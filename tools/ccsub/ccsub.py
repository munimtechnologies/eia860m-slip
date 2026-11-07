"""ccsub: pre-registered check ccsub-1 (plan: docs/ccsub-plan.md in
munimtechnologies/eia860m-slip).

ccsplit-1 (docs/ccsplit.md) found 10 operating steam (prime mover CA) generators at 9 combined-
cycle plants that no row of PUDL's 2024 crosswalk (core_epa__assn_eia_epacamd) links, 3 of them
at "collapsed" combined cycles. PUDL's subplant table (core_epa__assn_eia_epacamd_subplant_ids)
also adds every EIA-860 generator and joins generators that share a PUDL unit (unit_id_pudl, from
EIA's boiler-generator associations). This script asks, for each of the 10, whether the subplant
table already puts it in the same subplant as at least one of its plant's crosswalk-linked CT
generators ("joined"), puts it in a subplant of its own or with others ("apart"), or leaves it out
("absent"). As a base rate it does the same for the steam generators the newest crosswalk year
does link.

Ids are compared after trimming and upper-casing. PUDL's data (CC BY 4.0) is downloaded at run time
and not stored here.

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
SUB_TABLE = "core_epa__assn_eia_epacamd_subplant_ids"
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
SUB_COLS = ["plant_id_eia", "plant_id_epa", "subplant_id", "unit_id_pudl",
            "emissions_unit_id_epa", "generator_id"]
SUB_NEED = ["plant_id_eia", "generator_id", "subplant_id", "unit_id_pudl"]
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "capacity_mw", "prime_mover_code",
            "operational_status_code"]
UA = {"User-Agent": "mv2-ccsub/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

# The 2024 orphan-CA plants of ccsplit-1 (docs/ccsplit.md; data/ccsplit-orphans-2018-2024.csv):
# EIA plant -> (crosswalk-linked CT generators, unlinked operating CA generators).
ORPHANS = {
    422: (("GT5",), ("ST1",)),
    7242: (("1CT", "2", "3", "4", "5"), ("1CA",)),
    7307: (("5", "6"), ("4",)),
    10682: (("GT4", "GT5"), ("ST2",)),
    52176: (("GEN1", "GEN2"), ("GEN3",)),
    55419: (("G500", "G600", "G700", "G800"), ("ST6", "ST7")),
    55524: (("CTG1", "CTG2", "CTG3"), ("STG2",)),
    58478: (("LEPA1",), ("LEPA2",)),
    60589: (("GEN1", "GEN2"), ("GEN3",)),
}
HIT_PLANTS = (422, 58478, 60589)

# Gate and bars (docs/ccsub-plan.md)
MIN_ROWS = 20000
P2_MIN = 7
P3_MIN = 2
P4_MIN_N = 3
P5_MIN_N = 200
P5_SHARE = 0.95


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


def index_sub(rows):
    """rows: dicts with SUB_COLS. Returns {"present": set of (plant, gen) with any row,
    "gen_subs": {(plant, gen): set of subplant ids}, "gen_units": {(plant, gen): set of
    unit_id_pudl}, "sub_cems": {(plant, subplant): set of emissions unit ids},
    "sub_gens": {(plant, subplant): set of generator ids}}."""
    out = {"present": set(), "gen_subs": {}, "gen_units": {}, "sub_cems": {}, "sub_gens": {}}
    for r in rows:
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        sid, unit = pint(r.get("subplant_id")), gid(r.get("unit_id_pudl"))
        eu = gid(r.get("emissions_unit_id_epa"))
        if pi is None:
            continue
        if sid is not None and eu:
            out["sub_cems"].setdefault((pi, sid), set()).add(eu)
        if not gi:
            continue
        out["present"].add((pi, gi))
        if sid is not None:
            out["gen_subs"].setdefault((pi, gi), set()).add(sid)
            out["sub_gens"].setdefault((pi, sid), set()).add(gi)
        if unit:
            out["gen_units"].setdefault((pi, gi), set()).add(unit)
    return out


def classify(pi, ca, cts, idx):
    """One steam generator against its plant's linked CT generators."""
    subs = idx["gen_subs"].get((pi, ca), set())
    ct_subs = set()
    ct_units = set()
    for c in cts:
        ct_subs |= idx["gen_subs"].get((pi, c), set())
        ct_units |= idx["gen_units"].get((pi, c), set())
    units = idx["gen_units"].get((pi, ca), set())
    present = (pi, ca) in idx["present"]
    joined = bool(subs & ct_subs)
    cls = "absent" if not present else ("joined" if joined else "apart")
    gens, cems = set(), set()
    for s in subs:
        gens |= idx["sub_gens"].get((pi, s), set())
        cems |= idx["sub_cems"].get((pi, s), set())
    return {"plant": pi, "generator": ca, "cts": list(cts), "class": cls,
            "shared_unit": bool(units & ct_units),
            "subplants": sorted(subs), "ct_subplants": sorted(ct_subs),
            "units": sorted(units), "ct_units": sorted(ct_units),
            "subplant_generators": sorted(gens), "subplant_cems_units": sorted(cems)}


def check_orphans(idx, orphans=ORPHANS):
    out = []
    for pi in sorted(orphans):
        cts, cas = orphans[pi]
        for ca in cas:
            out.append(classify(pi, ca, cts, idx))
    return out


def cts_missing(idx, orphans=ORPHANS):
    return ["%s/%s" % (pi, c) for pi in sorted(orphans) for c in orphans[pi][0]
            if (pi, c) not in idx["present"]]


def index_linked(rows):
    """Crosswalk rows (XW_COLS). Returns {year: set of linked (EIA plant, EIA generator)}."""
    out = {}
    for r in rows:
        y, pi, gi = pint(r.get("report_year")), pint(r.get("plant_id_eia")), gid(
            r.get("generator_id"))
        if y is None or pi is None or not gi:
            continue
        out.setdefault(y, set()).add((pi, gi))
    return out


def index_gens(rows):
    """rows: dicts with GEN_COLS. Returns {(plant, gen): {"cap", "pm", "status"}}; for a
    repeated key the first row with a capacity wins."""
    out = {}
    for r in rows:
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        if pi is None or not gi:
            continue
        cap = fnum(r.get("capacity_mw"))
        prev = out.get((pi, gi))
        if prev is None or (prev["cap"] is None and cap is not None):
            out[(pi, gi)] = {"cap": cap, "pm": gid(r.get("prime_mover_code")),
                             "status": gid(r.get("operational_status_code"))}
    return out


def base_rate(linked, gens, idx):
    """ccsplit-1's definitions for one year: CC plant = an EIA plant with a linked CT generator
    and an operating CA generator (status OP, nameplate above zero). For every linked operating
    CA at a CC plant: is it joined with a linked CT of its plant?"""
    ct_linked, cas = {}, {}
    for (pi, gi) in linked:
        if gens.get((pi, gi), {}).get("pm") == "CT":
            ct_linked.setdefault(pi, []).append(gi)
    for (pi, gi), info in gens.items():
        if info["pm"] == "CA" and info["status"] == "OP" and (info["cap"] or 0) > 0:
            cas.setdefault(pi, []).append(gi)
    res = []
    for pi in sorted(set(ct_linked) & set(cas)):
        for ca in sorted(cas[pi]):
            if (pi, ca) in linked:
                res.append(classify(pi, ca, sorted(ct_linked[pi]), idx))
    n = len(res)
    j = sum(1 for r in res if r["class"] == "joined")
    return {"n": n, "joined": j, "share": round(j / n, 4) if n else None,
            "not_joined": [{k: r[k] for k in ("plant", "generator", "class", "subplants",
                                              "ct_subplants")}
                           for r in res if r["class"] != "joined"]}


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and g1["rows"] >= MIN_ROWS
                   and not g1["cts_missing"])
    if not s["G1"]:
        return s
    o = res.get("orphans") or []
    joined = [r for r in o if r["class"] == "joined"]
    s["P1"] = bool(o) and all(r["class"] != "absent" for r in o)
    s["P2"] = len(joined) >= P2_MIN
    s["P3"] = sum(1 for r in joined if r["plant"] in HIT_PLANTS) >= P3_MIN
    if len(joined) >= P4_MIN_N:
        s["P4"] = all(r["shared_unit"] for r in joined)
    b = res.get("base") or {}
    if b.get("n", 0) >= P5_MIN_N:
        s["P5"] = b["joined"] / b["n"] >= P5_SHARE
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
        schema = list(pl.read_parquet_schema(io.BytesIO(raw)))
    except Exception:
        try:
            schema = list(pl.scan_parquet(io.BytesIO(raw)).collect_schema().names())
        except Exception:
            schema = pl.read_parquet(io.BytesIO(raw), n_rows=1).columns
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


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["plant_id_eia", "generator_id", "class", "shared_unit_id_pudl",
                    "subplant_ids", "linked_ct_generators", "ct_subplant_ids", "unit_id_pudl",
                    "ct_unit_id_pudl", "subplant_generators", "subplant_cems_units"])
        for r in rows:
            w.writerow([r["plant"], r["generator"], r["class"], r["shared_unit"],
                        ";".join(map(str, r["subplants"])), ";".join(r["cts"]),
                        ";".join(map(str, r["ct_subplants"])), ";".join(r["units"]),
                        ";".join(r["ct_units"]), ";".join(r["subplant_generators"]),
                        ";".join(r["subplant_cems_units"])])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "ccsub.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    try:
        sub_df, res["downloads"][SUB_TABLE] = load(SUB_TABLE, SUB_COLS, pl)
        idx = index_sub(sub_df.to_dicts())
        nrows = sub_df.height
        del sub_df
        res["g1"] = {"missing_cols": [c for c in SUB_NEED
                                      if c in res["downloads"][SUB_TABLE]["missing_cols"]],
                     "rows": nrows, "cts_missing": cts_missing(idx)}
        res["orphans"] = check_orphans(idx)
        write_csv(res["orphans"], os.path.join(a.out_dir, "ccsub-orphans.csv"))
        xw_df, res["downloads"][XW_TABLE] = load(XW_TABLE, XW_COLS, pl)
        linked = index_linked(xw_df.to_dicts())
        del xw_df
        newest = max(linked) if linked else None
        res["base_year"] = newest
        if newest is not None:
            gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
            gens_df = gens_df.with_columns(pl.col("report_date").cast(pl.String))
            gens_df = gens_df.filter(pl.col("report_date").str.slice(0, 4) == str(newest))
            gens = index_gens(gens_df.to_dicts())
            del gens_df
            res["base"] = base_rate(linked[newest], gens, idx)
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "ccsub.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
