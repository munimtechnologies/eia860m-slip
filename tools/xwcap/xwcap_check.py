"""Pre-registered census of EPA-EIA crosswalk groups whose CEMS load is far above the EIA
nameplate capacity of the generators they are linked to (pre-registration id xwcap-1; plan:
docs/xwcap-plan.md in munimtechnologies/eia860m-slip).

PUDL's EPA-EIA crosswalk (core_epa__assn_eia_epacamd) links EPA CEMS units to EIA generators.
This script joins the links of one year into connected groups (units and generators that share
a link, directly or through others), adds up the highest hourly gross load of each group's CEMS
units (max_gross_load_mw in out_epacems__yearly_operational_characteristics) and the nameplate
capacity of its generators (capacity_mw in core_eia860__scd_generators), and counts the groups
whose CEMS load is at least 1.5 times their capacity. Each such group is put in one class:
"cc" (a linked generator is part of a combined cycle), "candidate" (the same EIA plant has an
existing combustion generator that no CEMS unit is linked to and that is big enough to explain
the gap) or "other".

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
OPS_TABLE = "out_epacems__yearly_operational_characteristics"
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
PLANT_TABLE = "core_eia__entity_plants"
OPS_COLS = ["plant_id_epa", "emissions_unit_id_epa", "max_gross_load_mw", "report_year"]
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "prime_mover_code",
            "operational_status_code", "capacity_mw"]
PLANT_COLS = ["plant_id_eia", "plant_name_eia", "state"]
UNIT = ["plant_id_epa", "emissions_unit_id_epa"]
GEN = ["plant_id_eia", "generator_id"]
INT_COLS = ("plant_id_epa", "plant_id_eia", "report_year")
STR_COLS = ("emissions_unit_id_epa", "generator_id", "prime_mover_code",
            "operational_status_code", "state", "plant_name_eia")
CC_CODES = {"CT", "CA", "CS", "CC"}
COMBUSTION = {"GT", "ST", "IC", "CT", "CA", "CS", "CC"}
EXISTING = {"OP", "SB", "OS", "OA"}
CLASSES = ("cc", "candidate", "other")
OVER = 1.5
UNDER = 0.5
MIN_EXCESS_MW = 10.0
CAND_SHARE = 0.5
MIN_YEAR = 2022
WATCH_PLANT = 57865
UA = {"User-Agent": "mv2-xwcap-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---- small statistics, in plain Python ------------------------------------------------------

def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def quantiles(xs, qs=(0.1, 0.25, 0.5, 0.75, 0.9, 0.99)):
    s = sorted(xs)
    if not s:
        return {}
    return {str(q): s[int(round(q * (len(s) - 1)))] for q in qs}


# ---- groups ---------------------------------------------------------------------------------

def components(edges):
    """edges: (unit_key, gen_key) pairs. Returns [(set of unit keys, set of gen keys)], each
    group holding the units and generators joined by links, sorted by their smallest unit."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, g in edges:
        ru, rg = find(("U",) + tuple(u)), find(("G",) + tuple(g))
        if ru != rg:
            parent[ru] = rg
    groups = {}
    for u, g in edges:
        units, gens = groups.setdefault(find(("U",) + tuple(u)), (set(), set()))
        units.add(tuple(u))
        gens.add(tuple(g))
    return sorted(groups.values(), key=lambda c: min(c[0]))


def classify(gens, excess, gen_rows, by_plant, linked):
    """Class of an over group and the unlinked generators that could explain its gap."""
    pms = {gen_rows[g]["pm"] for g in gens if g in gen_rows}
    if pms & CC_CODES:
        return "cc", []
    cands = []
    for p in sorted({g[0] for g in gens}):
        for g in sorted(by_plant.get(p, [])):
            if g in linked:
                continue
            info = gen_rows[g]
            if (info["pm"] in COMBUSTION and info["status"] in EXISTING
                    and info["cap"] is not None and info["cap"] >= CAND_SHARE * excess):
                cands.append(g)
    return ("candidate" if cands else "other"), cands


def analyse(edges, ops_max, gen_rows):
    """edges: (unit_key, gen_key) links of one year; ops_max: unit_key -> max_gross_load_mw;
    gen_rows: gen_key -> {"pm", "status", "cap"} from EIA-860 rows of the same year."""
    linked = {tuple(g) for _, g in edges}
    by_plant = {}
    for g in gen_rows:
        by_plant.setdefault(g[0], []).append(g)
    out = []
    for units, gens in components(edges):
        pos = [ops_max[u] for u in units if ops_max.get(u) is not None and ops_max[u] > 0]
        cems = sum(pos)
        caps = [gen_rows[g]["cap"] if g in gen_rows else None for g in gens]
        all_cap = all(c is not None and c > 0 for c in caps)
        cap = sum(c for c in caps if c is not None and c > 0)
        rec = {"units": sorted(units), "gens": sorted(gens), "cems_max": cems, "eia_cap": cap,
               "n_units_max": len(pos)}
        rec["study"] = cems > 0 and all_cap
        rec["ratio"] = cems / cap if rec["study"] else None
        rec["over"] = bool(rec["study"] and rec["ratio"] >= OVER
                           and cems - cap >= MIN_EXCESS_MW)
        rec["under"] = bool(rec["study"] and rec["ratio"] < UNDER)
        rec["cls"], rec["candidates"] = None, []
        if rec["over"]:
            rec["cls"], rec["candidates"] = classify(gens, cems - cap, gen_rows, by_plant,
                                                     linked)
        out.append(rec)
    return out


def summary(recs):
    st = [r for r in recs if r["study"]]
    over = [r for r in st if r["over"]]
    ratios = [r["ratio"] for r in st]
    return {"groups": len(recs), "study": len(st), "over": len(over),
            "over_2x": sum(1 for r in over if r["ratio"] >= 2),
            "under": sum(1 for r in st if r["under"]),
            "median_ratio": median(ratios), "ratio_quantiles": quantiles(ratios),
            "over_by_class": {c: sum(1 for r in over if r["cls"] == c) for c in CLASSES},
            "over_units": sum(len(r["units"]) for r in over),
            "single_pair_study": sum(1 for r in st if len(r["units"]) == 1
                                     and len(r["gens"]) == 1)}


def persistence(cur, prev):
    over_cur = {u for r in cur if r["over"] for u in r["units"]}
    study_prev = {u for r in prev if r["study"] for u in r["units"]}
    over_prev = {u for r in prev if r["over"] for u in r["units"]}
    both = over_cur & study_prev
    return {"over_units": len(over_cur), "in_prev_study": len(both),
            "also_over_prev": len(both & over_prev)}


def plant_check(recs, plant, gen_rows, linked):
    mine = [r for r in recs if any(u[0] == plant for u in r["units"])]
    study = [r for r in mine if r["study"]]
    gens = sorted(g for g in gen_rows if g[0] == plant)
    return {"plant": plant, "groups": len(mine), "study": len(study),
            "over": sum(1 for r in study if r["over"]),
            "candidate": sum(1 for r in study if r["cls"] == "candidate"),
            "group_rows": [{k: r[k] for k in ("units", "gens", "cems_max", "eia_cap", "ratio",
                                              "cls", "candidates")} for r in mine],
            "eia_generators": [{"generator_id": g[1], "pm": gen_rows[g]["pm"],
                                "status": gen_rows[g]["status"], "cap": gen_rows[g]["cap"],
                                "linked": g in linked} for g in gens]}


# ---- scoring ----------------------------------------------------------------------------------

def score(r):
    s = {}
    g1 = r.get("g1")
    if g1 is not None:
        s["G1"] = (g1["missing_cols"] == [] and r.get("year") is not None
                   and r["year"] >= MIN_YEAR)
    m = r.get("main")
    if not m:
        return s
    s["G2"] = m["study"] >= 1500
    if m["study"] == 0:
        return s
    s["G3"] = 0.7 <= m["median_ratio"] <= 1.3
    if s.get("G1") and s["G2"] and s["G3"]:
        s["P1"] = m["over"] < 0.05 * m["study"]
        if m["over"] >= 10:
            s["P2"] = m["over_by_class"]["cc"] < 0.5 * m["over"]
            s["P3"] = m["over_by_class"]["candidate"] >= 0.20 * m["over"]
        pc = r.get("plant_check")
        if pc and pc["study"] >= 1:
            s["P4"] = pc["over"] == pc["study"] and pc["candidate"] == pc["study"]
        ps = r.get("persistence")
        if ps and ps["in_prev_study"] >= 10:
            s["P5"] = ps["also_over_prev"] >= 0.70 * ps["in_prev_study"]
    return s


# ---- the run ----------------------------------------------------------------------------------

def fetch(url, timeout=600):
    last = None
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # retried, then raised
            last = exc
            time.sleep(30)
    raise last


def clean(df, pl):
    casts = []
    for c, dt in df.schema.items():
        if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical:
            casts.append(pl.col(c).cast(pl.String))
    if casts:
        df = df.with_columns(casts)
    return df.with_columns([pl.col(c).cast(pl.Int64) for c in INT_COLS if c in df.columns]
                           + [pl.col(c).cast(pl.String) for c in STR_COLS if c in df.columns])


def load_table(name, cols, pl):
    raw, headers = fetch(NIGHTLY % name)
    df = clean(pl.read_parquet(io.BytesIO(raw), columns=cols), pl)
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified")}
    return df, info


def year_inputs(ops, xw, gens, year, pl):
    o = ops.filter(pl.col("report_year") == year).select(UNIT + ["max_gross_load_mw"])
    ops_max = {}
    for row in o.to_dicts():
        if row["plant_id_epa"] is None or row["emissions_unit_id_epa"] is None:
            continue
        u = (row["plant_id_epa"], row["emissions_unit_id_epa"])
        v = row["max_gross_load_mw"]
        if v is not None and (ops_max.get(u) is None or v > ops_max[u]):
            ops_max[u] = v
        else:
            ops_max.setdefault(u, v)
    x = (xw.filter((pl.col("report_year") == year)
                   & pl.col("emissions_unit_id_epa").is_not_null()
                   & pl.col("generator_id").is_not_null()
                   & pl.col("plant_id_eia").is_not_null()
                   & pl.col("plant_id_epa").is_not_null())
         .select(UNIT + GEN).unique().sort(UNIT + GEN))
    edges = [((r["plant_id_epa"], r["emissions_unit_id_epa"]),
              (r["plant_id_eia"], r["generator_id"])) for r in x.to_dicts()]
    g = (gens.filter(pl.col("report_date").dt.year() == year)
         .select(GEN + ["prime_mover_code", "operational_status_code", "capacity_mw"])
         .sort(GEN).unique(subset=GEN, keep="first", maintain_order=True))
    gen_rows = {(r["plant_id_eia"], r["generator_id"]):
                {"pm": r["prime_mover_code"], "status": r["operational_status_code"],
                 "cap": r["capacity_mw"]}
                for r in g.to_dicts() if r["plant_id_eia"] is not None
                and r["generator_id"] is not None}
    return edges, ops_max, gen_rows


def choose_year(ops, xw, gens, pl):
    oy = set(ops["report_year"].drop_nulls().unique().to_list())
    xy = set(xw["report_year"].drop_nulls().unique().to_list())
    gy = set(gens.filter(pl.col("capacity_mw").is_not_null())["report_date"]
             .dt.year().unique().to_list())
    both = oy & xy & gy
    return (max(both) if both else None), sorted(both)


def key_text(k):
    return "%s:%s" % (k[0], k[1])


def write_over_csv(path, recs, gen_rows, names):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["plant_id_eia", "plant_name_eia", "state", "units", "generators",
                     "cems_max_mw", "eia_capacity_mw", "ratio", "class", "candidates"])
        for r in recs:
            if not r["over"]:
                continue
            p = r["gens"][0][0]
            nm = names.get(p, {})
            w.writerow([p, nm.get("plant_name_eia"), nm.get("state"),
                        ";".join(key_text(u) for u in r["units"]),
                        ";".join("%s:%s:%s:%s" % (g[0], g[1], gen_rows[g]["pm"],
                                                  gen_rows[g]["cap"]) for g in r["gens"]),
                        round(r["cems_max"], 1), round(r["eia_cap"], 1),
                        round(r["ratio"], 3), r["cls"],
                        ";".join("%s:%s:%s:%s" % (g[0], g[1], gen_rows[g]["pm"],
                                                  gen_rows[g]["cap"])
                                 for g in r["candidates"])])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "xwcap_check.py " + VERSION, "python": sys.version.split()[0],
              "polars": pl.__version__, "started": now(), "downloads": {}}

    def save():
        result["scores"] = score(result)
        with open(os.path.join(a.out_dir, "xwcap_check.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    try:
        ops, result["downloads"][OPS_TABLE] = load_table(OPS_TABLE, None, pl)
        missing = [c for c in OPS_COLS if c not in ops.columns]
        xw, result["downloads"][XW_TABLE] = load_table(XW_TABLE, XW_COLS, pl)
        gens, result["downloads"][GEN_TABLE] = load_table(GEN_TABLE, GEN_COLS, pl)
        names = {}
        try:
            plants, result["downloads"][PLANT_TABLE] = load_table(PLANT_TABLE, PLANT_COLS, pl)
            names = {r["plant_id_eia"]: r for r in plants.to_dicts()}
        except Exception as exc:  # names are only labels
            result["plant_names_error"] = "%s: %s" % (type(exc).__name__, exc)
        year, years = choose_year(ops, xw, gens, pl)
        result["year"] = year
        result["common_years"] = years
        result["g1"] = {"missing_cols": missing, "ops_rows": ops.height}
        save()
        recs_by_year = {}
        if year is not None:
            edges, ops_max, gen_rows = year_inputs(ops, xw, gens, year, pl)
            recs = analyse(edges, ops_max, gen_rows)
            recs_by_year[year] = recs
            result["main"] = summary(recs)
            result["main"]["links"] = len(edges)
            linked = {g for _, g in edges}
            result["plant_check"] = plant_check(recs, WATCH_PLANT, gen_rows, linked)
            write_over_csv(os.path.join(a.out_dir, "xwcap_over_%d.csv" % year), recs,
                           gen_rows, names)
            save()
            if year - 1 in years:
                e1, o1, g1 = year_inputs(ops, xw, gens, year - 1, pl)
                recs_by_year[year - 1] = analyse(e1, o1, g1)
                result["persistence"] = persistence(recs, recs_by_year[year - 1])
            save()
            by_year = {}
            for y in years:
                if y not in recs_by_year:
                    ey, oy_, gy = year_inputs(ops, xw, gens, y, pl)
                    recs_by_year[y] = analyse(ey, oy_, gy)
                by_year[y] = summary(recs_by_year[y])
                recs_by_year[y] = recs_by_year[y] if y in (year, year - 1) else None
            result["by_year"] = by_year
    except Exception as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    result["finished"] = now()
    save()
    print(json.dumps({k: v for k, v in result.items() if k != "plant_check"}, indent=1,
                     default=str))
    print(json.dumps(result.get("plant_check"), indent=1, default=str))


if __name__ == "__main__":
    main()
