"""ccsplit: pre-registered census ccsplit-1 (plan: docs/ccsplit-plan.md in
munimtechnologies/eia860m-slip).

A combined cycle has a combustion turbine part (EIA prime mover CT) and a steam part (CA). In
xwpudl.md two plants (Glenarm, EIA 422, and LEPA Unit No. 1, EIA 58478) showed one shape of
crosswalk error: a CAMD unit's two generators (the turbine and the steam generator) are both linked
to the one EIA CT generator, and the plant's operating CA generator is linked by no crosswalk row.
This script counts that shape ("collapsed combined cycle") in every report year of PUDL's run of
EPA's crosswalk (core_epa__assn_eia_epacamd), using PUDL's EIA-860 generator table
(core_eia860__scd_generators) for prime movers, status and nameplate, and scores the plan's gates
and predictions.

Definitions, for one report year:
- linked: an EIA (plant, generator) pair that at least one crosswalk row of that year links.
- operating CA: an EIA-860 generator of that year with prime mover CA, status code OP and a
  nameplate above zero.
- orphan CA: an operating CA that is not linked.
- CC plant: an EIA plant with at least one linked CT generator and at least one operating CA.
- orphan-CA plant: a CC plant with at least one orphan CA.
- hit: a CAMD unit (plant_id_epa, emissions_unit_id_epa) with two or more distinct CAMD generator
  ids linked to the same EIA generator, where that EIA generator's prime mover is CT and its EIA
  plant has at least one orphan CA. A hit plant is an EIA plant with at least one hit.

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
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "generator_id_epa",
           "plant_id_eia", "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "capacity_mw", "prime_mover_code",
            "operational_status_code"]
UA = {"User-Agent": "mv2-ccsplit/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

# Gates and bars (docs/ccsplit-plan.md)
MIN_NEWEST = 2023
MIN_PM_SHARE = 0.95
MIN_CC_PLANTS = 200
KNOWN = (422, 58478)
P1_MIN = 5
P2_MAX = 50
P3_FACTOR = 2
P4_YEAR = 2019
P4_MIN_N = 3
P4_SHARE = 0.7
P5_SHARE = 0.6
P6_LO = 0.1
P6_HI = 1.2
P6_SHARE = 0.7


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def gid(v):
    """An id for comparing: strip and upper-case; 1.0 -> '1'; None/NaN -> ''."""
    if v is None:
        return ""
    if isinstance(v, float):
        if v != v:
            return ""
        if v.is_integer():
            v = int(v)
    return str(v).strip().upper()


def pint(v):
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None


def fnum(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def index_links(rows):
    """rows: dicts with XW_COLS. Returns {year: {"units": {(epa plant, epa unit): {(eia plant,
    eia gen): set of epa gens}}, "linked": set of (eia plant, eia gen), "eia_plants": set}}."""
    out = {}
    for r in rows:
        y = pint(r.get("report_year"))
        if y is None:
            continue
        d = out.setdefault(y, {"units": {}, "linked": set(), "eia_plants": set()})
        pe, pi = pint(r.get("plant_id_epa")), pint(r.get("plant_id_eia"))
        ue, ge, gi = (gid(r.get("emissions_unit_id_epa")), gid(r.get("generator_id_epa")),
                      gid(r.get("generator_id")))
        if pi is not None:
            d["eia_plants"].add(pi)
        if pi is None or not gi:
            continue
        d["linked"].add((pi, gi))
        if pe is None or not ue or not ge:
            continue
        d["units"].setdefault((pe, ue), {}).setdefault((pi, gi), set()).add(ge)
    return out


def index_gens(rows):
    """rows: dicts with GEN_COLS (report_date a date or 'YYYY-MM-DD' text). Returns
    {year: {(plant, gen): {"cap", "pm", "status"}}}; for a repeated key the first row with a
    capacity wins."""
    out = {}
    for r in rows:
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        d = r.get("report_date")
        y = pint(str(d)[:4]) if d is not None else None
        if pi is None or not gi or y is None:
            continue
        cap = fnum(r.get("capacity_mw"))
        ydict = out.setdefault(y, {})
        prev = ydict.get((pi, gi))
        if prev is None or (prev["cap"] is None and cap is not None):
            ydict[(pi, gi)] = {"cap": cap, "pm": gid(r.get("prime_mover_code")),
                               "status": gid(r.get("operational_status_code"))}
    return out


def is_op_ca(info):
    return info["pm"] == "CA" and info["status"] == "OP" and (info["cap"] or 0) > 0


def pm_share(gens_y, plants):
    """Share of EIA-860 generators of the year, at the given plants, with a prime mover."""
    n = have = 0
    for (pi, _gi), info in gens_y.items():
        if pi in plants:
            n += 1
            have += bool(info["pm"])
    return round(have / n, 4) if n else None


def year_lint(links_y, gens_y):
    """The census for one report year (see the module docstring for the definitions)."""
    linked = links_y["linked"]
    ca_by_plant = {}
    for (pi, gi), info in gens_y.items():
        if is_op_ca(info):
            ca_by_plant.setdefault(pi, []).append((gi, info["cap"], (pi, gi) in linked))
    orphans = {}
    for pi, cas in ca_by_plant.items():
        o = sorted((g, c) for g, c, is_linked in cas if not is_linked)
        if o:
            orphans[pi] = o
    ct_linked = {}
    for (pi, gi) in linked:
        if gens_y.get((pi, gi), {}).get("pm") == "CT":
            ct_linked.setdefault(pi, set()).add(gi)
    cc_plants = set(ct_linked) & set(ca_by_plant)
    orphan_plants = cc_plants & set(orphans)
    hits = []
    for (pe, ue), targets in sorted(links_y["units"].items()):
        for (pi, gi), ges in sorted(targets.items()):
            info = gens_y.get((pi, gi))
            if len(ges) >= 2 and info and info["pm"] == "CT" and pi in orphans:
                hits.append({"camd_plant": pe, "camd_unit": ue, "camd_generators": sorted(ges),
                             "eia_plant": pi, "eia_generator": gi, "eia_cap": info["cap"],
                             "orphan_cas": [{"generator": g, "cap": c} for g, c in orphans[pi]],
                             "st_in_camd_ids": any("ST" in g for g in ges)})
    hit_plants = sorted({h["eia_plant"] for h in hits})
    detail = [{"eia_plant": pi, "linked_cts": sorted(ct_linked[pi]),
               "orphan_cas": [{"generator": g, "cap": c} for g, c in orphans[pi]],
               "hit": pi in hit_plants} for pi in sorted(orphan_plants)]
    return {"cc_plants": len(cc_plants), "orphan_ca_plants": sorted(orphan_plants),
            "hit_plants": hit_plants, "hits": hits, "orphan_detail": detail}


def p4_persist(lints, links, newest, year=P4_YEAR):
    """Of the newest year's hit plants that have a crosswalk row in `year`, how many are hit
    plants in `year` too."""
    if year not in links or str(year) not in lints or str(newest) not in lints:
        return None
    present = [p for p in lints[str(newest)]["hit_plants"] if p in links[year]["eia_plants"]]
    also = [p for p in present if p in lints[str(year)]["hit_plants"]]
    return {"year": year, "n": len(present), "also": len(also), "plants": present,
            "also_plants": also}


def p6_ratios(lint_y):
    """Per hit plant: total orphan CA nameplate / total nameplate of the CT generators its hits
    are linked to."""
    by_plant = {}
    for h in lint_y["hits"]:
        d = by_plant.setdefault(h["eia_plant"], {"ct": {}, "ca": {}})
        d["ct"][h["eia_generator"]] = h["eia_cap"]
        for o in h["orphan_cas"]:
            d["ca"][o["generator"]] = o["cap"]
    out = {}
    for pi, d in sorted(by_plant.items()):
        ct = sum(c for c in d["ct"].values() if c)
        ca = sum(c for c in d["ca"].values() if c)
        if ct > 0:
            out[str(pi)] = round(ca / ct, 4)
    return out


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and g1["newest"] is not None
                   and g1["newest"] >= MIN_NEWEST and g1["pm_share"] is not None
                   and g1["pm_share"] >= MIN_PM_SHARE and g1["cc_plants"] >= MIN_CC_PLANTS)
    if not s["G1"]:
        return s
    newest = res["by_year"][str(g1["newest"])]
    s["G2"] = all(p in newest["hit_plants"] for p in KNOWN)
    if not s["G2"]:
        return s
    n = len(newest["hit_plants"])
    s["P1"] = n >= P1_MIN
    s["P2"] = n <= P2_MAX
    s["P3"] = len(newest["orphan_ca_plants"]) >= P3_FACTOR * n
    p4 = res.get("p4")
    if p4 and p4["n"] >= P4_MIN_N:
        s["P4"] = p4["also"] / p4["n"] >= P4_SHARE
    hits = newest["hits"]
    if hits:
        s["P5"] = sum(1 for h in hits if h["st_in_camd_ids"]) / len(hits) >= P5_SHARE
    r = res.get("p6_ratios") or {}
    if r:
        s["P6"] = sum(1 for v in r.values() if P6_LO <= v <= P6_HI) / len(r) >= P6_SHARE
    return s


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


def load(name, cols, pl):
    raw, headers = fetch(NIGHTLY % name)
    try:
        schema = dict(pl.read_parquet_schema(io.BytesIO(raw)))
    except AttributeError:
        schema = dict(pl.scan_parquet(io.BytesIO(raw)).collect_schema())
    have = [c for c in cols if c in schema]
    df = pl.read_parquet(io.BytesIO(raw), columns=have)
    casts = [pl.col(c).cast(pl.String) for c, dt in df.schema.items()
             if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical]
    if casts:
        df = df.with_columns(casts)
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified"),
            "missing_cols": [c for c in cols if c not in schema]}
    return df, info


def write_csvs(res, out_dir):
    with open(os.path.join(out_dir, "ccsplit-hits.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_epa", "emissions_unit_id_epa", "generator_ids_epa",
                    "plant_id_eia", "generator_id_eia_ct", "ct_capacity_mw",
                    "orphan_ca_generators", "orphan_ca_capacity_mw"])
        for y, lint in sorted(res.get("by_year", {}).items()):
            for h in lint["hits"]:
                w.writerow([y, h["camd_plant"], h["camd_unit"], ";".join(h["camd_generators"]),
                            h["eia_plant"], h["eia_generator"], h["eia_cap"],
                            ";".join(o["generator"] for o in h["orphan_cas"]),
                            ";".join(str(o["cap"]) for o in h["orphan_cas"])])
    with open(os.path.join(out_dir, "ccsplit-orphans.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_eia", "linked_ct_generators", "orphan_ca_generators",
                    "orphan_ca_capacity_mw", "hit"])
        for y, lint in sorted(res.get("by_year", {}).items()):
            for d in lint["orphan_detail"]:
                w.writerow([y, d["eia_plant"], ";".join(d["linked_cts"]),
                            ";".join(o["generator"] for o in d["orphan_cas"]),
                            ";".join(str(o["cap"]) for o in d["orphan_cas"]), d["hit"]])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "ccsplit.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    try:
        xw, res["downloads"][XW_TABLE] = load(XW_TABLE, XW_COLS, pl)
        links = index_links(xw.to_dicts())
        del xw
        years = sorted(links)
        newest = years[-1] if years else None
        res["years"] = years
        all_plants = sorted(set().union(*(links[y]["eia_plants"] for y in years))) if years else []
        gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        gens_df = gens_df.with_columns(pl.col("report_date").cast(pl.String))
        gens_df = gens_df.filter(
            pl.col("plant_id_eia").cast(pl.Int64).is_in(all_plants)
            & pl.col("report_date").str.slice(0, 4).cast(pl.Int64).is_in(years))
        gens = index_gens(gens_df.to_dicts())
        del gens_df
        res["by_year"] = {str(y): year_lint(links[y], gens.get(y, {})) for y in years}
        res["summary"] = {y: {"cc_plants": v["cc_plants"],
                              "orphan_ca_plants": len(v["orphan_ca_plants"]),
                              "hit_plants": len(v["hit_plants"]), "hits": len(v["hits"])}
                          for y, v in res["by_year"].items()}
        res["g1"] = {"missing_cols": (res["downloads"][XW_TABLE]["missing_cols"]
                                      + res["downloads"][GEN_TABLE]["missing_cols"]),
                     "newest": newest,
                     "pm_share": pm_share(gens.get(newest, {}),
                                          links[newest]["eia_plants"]) if newest else None,
                     "cc_plants": res["by_year"][str(newest)]["cc_plants"] if newest else 0}
        res["p4"] = p4_persist(res["by_year"], links, newest) if newest else None
        res["p6_ratios"] = p6_ratios(res["by_year"][str(newest)]) if newest else {}
        write_csvs(res, a.out_dir)
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "ccsplit.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("by_year",)}, indent=1,
                     default=str))
    if res.get("by_year") and res.get("g1", {}).get("newest"):
        for h in res["by_year"][str(res["g1"]["newest"])]["hits"]:
            print("HIT", json.dumps(h, default=str))


if __name__ == "__main__":
    main()
