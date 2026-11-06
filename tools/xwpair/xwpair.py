"""xwpair: pre-registered census xwpair-1 (plan: docs/xwpair-plan.md in
munimtechnologies/eia860m-slip).

Some CEMS emissions units have no row at all in PUDL's run of EPA's CAMD-EIA crosswalk, so their
emissions and load cannot be tied to an EIA generator. This script counts them in every report
year shared by PUDL's crosswalk (core_epa__assn_eia_epacamd) and PUDL's yearly CEMS unit table
(out_epacems__yearly_operational_characteristics), and for each one looks at the same EIA plant
for an operating combustion generator that no crosswalk row links and whose nameplate is close to
the unit's CEMS peak gross load. A unit and a generator that are each other's only size match
form a "unique pair": a proposed crosswalk row for a person to check.

The proposals are then compared with an independent, partly hand-reviewed list: the 171 rows that
Open Grid Emissions pull request #476 adds to its manual crosswalk from EPA's CAMPD facility file
(notes "CAMPD Facility database mapping"), read at the PR's head commit pinned below.

Definitions, for one report year:
- CEMS unit: a (plant_id_epa, emissions_unit_id_epa) row of the yearly CEMS table; its EIA plant
  is the table's plant_id_eia (plant_id_epa when empty); its peak is max_gross_load_mw.
- unmatched unit: a CEMS unit with no crosswalk row of that year that names an EIA generator.
- candidate: an EIA-860 generator of that year at the unit's EIA plant, with status OP, a
  nameplate above zero, prime mover in COMB, and linked by no crosswalk row of that year.
- size match: peak / nameplate between LO and HI (inclusive).
- unique pair: the unit has exactly one size-matched candidate, and that candidate size-matches
  no other unmatched unit of the plant.
Unit ids are compared after trimming, upper-casing and removing leading zeros (as OGE does);
EIA generator ids after trimming and upper-casing.

PUDL's data (CC BY 4.0) and OGE's file (MIT) are downloaded at run time and not stored here.

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
OPS_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
            "max_gross_load_mw"]
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "capacity_mw", "prime_mover_code",
            "operational_status_code"]
OGE_SHA = "e6d1e3f487f338829108b348919eb9a37aa82616"
OGE_URL = ("https://raw.githubusercontent.com/singularity-energy/open-grid-emissions/%s/"
           "src/oge/reference_tables/epa_eia_crosswalk_manual.csv" % OGE_SHA)
OGE_NOTE = "CAMPD Facility database mapping"
UA = {"User-Agent": "mv2-xwpair/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

COMB = ("CA", "CS", "CT", "GT", "IC", "ST")
LO = 0.5
HI = 1.5
CLASSES = ("no_load", "no_candidate", "no_size_match", "ambiguous", "unique_pair")

# Gates and bars (docs/xwpair-plan.md)
MIN_NEWEST = 2023
MIN_UNITS = 2000
MIN_OGE_ROWS = 150
P1_LO = 0.02
P1_HI = 0.10
P2_SHARE = 0.3
P3_MIN = 25
P4_MIN_N = 20
P4_SHARE = 0.8
P5_MIN_N = 10
P5_SHARE = 0.6
P6_MIN_N = 5
P6_SHARE = 0.75
P7_MIN = 10


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


def uid(v):
    """A unit id for comparing: gid, then leading zeros removed ('01' -> '1', '0' -> '0')."""
    s = gid(v)
    if not s:
        return ""
    return s.lstrip("0") or "0"


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


def index_ops(rows):
    """rows: dicts with OPS_COLS. Returns {year: {(plant_id_epa, unit): {"pi", "peak"}}}; for a
    repeated key the largest peak and the first non-empty EIA plant win."""
    out = {}
    for r in rows:
        y, pe, ue = pint(r.get("report_year")), pint(r.get("plant_id_epa")), uid(
            r.get("emissions_unit_id_epa"))
        if y is None or pe is None or not ue:
            continue
        pi = pint(r.get("plant_id_eia"))
        peak = fnum(r.get("max_gross_load_mw"))
        d = out.setdefault(y, {})
        prev = d.get((pe, ue))
        if prev is None:
            d[(pe, ue)] = {"pi": pi if pi is not None else pe, "peak": peak}
            continue
        if pi is not None and prev["pi"] == pe and pi != pe:
            prev["pi"] = pi
        if peak is not None and (prev["peak"] is None or peak > prev["peak"]):
            prev["peak"] = peak
    return out


def index_xw(rows):
    """rows: dicts with XW_COLS. Returns {year: {"units": set of (plant_id_epa, unit) with a row
    naming an EIA generator, "linked": set of (EIA plant, EIA generator)}}."""
    out = {}
    for r in rows:
        y = pint(r.get("report_year"))
        if y is None:
            continue
        d = out.setdefault(y, {"units": set(), "linked": set()})
        pe, ue = pint(r.get("plant_id_epa")), uid(r.get("emissions_unit_id_epa"))
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        if not gi:
            continue
        if pe is not None and ue:
            d["units"].add((pe, ue))
        if pi is not None:
            d["linked"].add((pi, gi))
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


def is_candidate(info):
    return info["status"] == "OP" and info["pm"] in COMB and (info["cap"] or 0) > 0


def size_ok(peak, cap):
    return bool(peak and cap and peak > 0 and cap > 0 and LO <= peak / cap <= HI)


def year_pairs(ops_y, xw_y, gens_y):
    """The census for one report year (see the module docstring for the definitions)."""
    linked_units, linked = xw_y["units"], xw_y["linked"]
    cands = {}
    for (pi, gi), info in gens_y.items():
        if is_candidate(info) and (pi, gi) not in linked:
            cands.setdefault(pi, []).append((gi, info["cap"], info["pm"]))
    unmatched = sorted(k for k in ops_y if k not in linked_units)
    m_u, m_g = {}, {}
    for key in unmatched:
        d = ops_y[key]
        ms = sorted(gi for gi, cap, _pm in cands.get(d["pi"], []) if size_ok(d["peak"], cap))
        m_u[key] = ms
        for gi in ms:
            m_g.setdefault((d["pi"], gi), []).append(key)
    units = []
    for key in unmatched:
        d = ops_y[key]
        c = sorted(cands.get(d["pi"], []))
        ms = m_u[key]
        if not d["peak"] or d["peak"] <= 0:
            cls = "no_load"
        elif not c:
            cls = "no_candidate"
        elif not ms:
            cls = "no_size_match"
        elif len(ms) == 1 and len(m_g[(d["pi"], ms[0])]) == 1:
            cls = "unique_pair"
        else:
            cls = "ambiguous"
        units.append({"plant_id_epa": key[0], "unit": key[1], "plant_id_eia": d["pi"],
                      "peak": d["peak"], "class": cls,
                      "candidates": [{"generator": g, "cap": cap, "pm": pm}
                                     for g, cap, pm in c],
                      "size_matches": ms,
                      "pair": ms[0] if cls == "unique_pair" else None,
                      "same_id_matches": [g for g in ms if uid(g) == key[1]]})
    counts = {"cems_units": len(ops_y), "unmatched": len(unmatched),
              "with_candidate": sum(1 for u in units if u["candidates"])}
    for cls in CLASSES:
        counts[cls] = sum(1 for u in units if u["class"] == cls)
    return {"counts": counts, "units": units}


def parse_oge(text):
    """OGE's manual crosswalk CSV text. Returns (rows with the CAMPD note, {(plant_id_epa, unit):
    set of (EIA plant, EIA generator)})."""
    n, out = 0, {}
    for r in csv.DictReader(io.StringIO(text)):
        if (r.get("notes") or "").strip() != OGE_NOTE:
            continue
        pe, ue = pint(r.get("plant_id_epa")), uid(r.get("emissions_unit_id_epa"))
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        if pe is None or not ue or pi is None or not gi:
            continue
        n += 1
        out.setdefault((pe, ue), set()).add((pi, gi))
    return n, out


def validate(year_res, ops_y, oge):
    """Compare one year's census with OGE's CAMPD rows (see the plan's P4-P7)."""
    by_key = {(u["plant_id_epa"], u["unit"]): u for u in year_res["units"]}
    present = [k for k in sorted(oge) if k in ops_y]
    unm = [k for k in present if k in by_key]
    contained = []
    for k in unm:
        u = by_key[k]
        have = {(u["plant_id_eia"], c["generator"]) for c in u["candidates"]}
        if all(g in have for g in oge[k]):
            contained.append(k)
    pairs_in = [k for k in unm if by_key[k]["class"] == "unique_pair"]
    agree = [k for k in pairs_in if (by_key[k]["plant_id_eia"], by_key[k]["pair"]) in oge[k]]
    new_pairs = [(u["plant_id_epa"], u["unit"]) for u in year_res["units"]
                 if u["class"] == "unique_pair" and (u["plant_id_epa"], u["unit"]) not in oge]
    return {"oge_units": len(oge), "present": len(present), "unmatched": len(unm),
            "contained": len(contained), "pairs_in_oge": len(pairs_in),
            "pairs_agree": len(agree), "new_pairs": len(new_pairs),
            "present_matched": [list(k) for k in present if k not in by_key],
            "not_contained": [list(k) for k in unm if k not in contained],
            "pairs_disagree": [list(k) for k in pairs_in if k not in agree]}


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and g1["newest"] is not None
                   and g1["newest"] >= MIN_NEWEST and g1["cems_units"] >= MIN_UNITS)
    if not s["G1"]:
        return s
    c = res["by_year"][str(g1["newest"])]["counts"]
    share = c["unmatched"] / c["cems_units"]
    s["P1"] = P1_LO <= share <= P1_HI
    if c["unmatched"]:
        s["P2"] = c["with_candidate"] / c["unmatched"] >= P2_SHARE
    s["P3"] = c["unique_pair"] >= P3_MIN
    v = res.get("oge") or {}
    s["G2"] = res.get("oge_rows", 0) >= MIN_OGE_ROWS
    if not s["G2"]:
        return s
    if v["present"] >= P4_MIN_N:
        s["P4"] = v["unmatched"] / v["present"] >= P4_SHARE
    if v["unmatched"] >= P5_MIN_N:
        s["P5"] = v["contained"] / v["unmatched"] >= P5_SHARE
    if v["pairs_in_oge"] >= P6_MIN_N:
        s["P6"] = v["pairs_agree"] / v["pairs_in_oge"] >= P6_SHARE
    s["P7"] = v["new_pairs"] >= P7_MIN
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


def write_csvs(res, oge, out_dir):
    with open(os.path.join(out_dir, "xwpair-units.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
                    "max_gross_load_mw", "class", "proposed_generator_id",
                    "size_matched_generators", "same_id_matches", "candidates_id_pm_mw",
                    "in_oge_campd_rows", "oge_generators"])
        for y, yr in sorted(res.get("by_year", {}).items()):
            for u in yr["units"]:
                key = (u["plant_id_epa"], u["unit"])
                w.writerow([y, u["plant_id_epa"], u["unit"], u["plant_id_eia"], u["peak"],
                            u["class"], u["pair"] or "", ";".join(u["size_matches"]),
                            ";".join(u["same_id_matches"]),
                            ";".join("%s:%s:%s" % (c["generator"], c["pm"], c["cap"])
                                     for c in u["candidates"]),
                            key in oge,
                            ";".join("%s/%s" % g for g in sorted(oge.get(key, ())))])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwpair.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    oge = {}
    try:
        xw_df, res["downloads"][XW_TABLE] = load(XW_TABLE, XW_COLS, pl)
        xw = index_xw(xw_df.to_dicts())
        del xw_df
        ops_df, res["downloads"][OPS_TABLE] = load(OPS_TABLE, OPS_COLS, pl)
        ops_df = ops_df.filter(pl.col("report_year").cast(pl.Int64).is_in(sorted(xw)))
        ops = index_ops(ops_df.to_dicts())
        del ops_df
        years = sorted(set(ops) & set(xw))
        newest = years[-1] if years else None
        res["years"] = years
        plants = sorted({d["pi"] for y in years for d in ops[y].values()})
        gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        gens_df = gens_df.with_columns(pl.col("report_date").cast(pl.String))
        gens_df = gens_df.filter(
            pl.col("plant_id_eia").cast(pl.Int64).is_in(plants)
            & pl.col("report_date").str.slice(0, 4).cast(pl.Int64).is_in(years))
        gens = index_gens(gens_df.to_dicts())
        del gens_df
        res["by_year"] = {str(y): year_pairs(ops[y], xw[y], gens.get(y, {})) for y in years}
        res["summary"] = {y: v["counts"] for y, v in res["by_year"].items()}
        res["g1"] = {"missing_cols": (res["downloads"][XW_TABLE]["missing_cols"]
                                      + res["downloads"][OPS_TABLE]["missing_cols"]
                                      + res["downloads"][GEN_TABLE]["missing_cols"]),
                     "newest": newest,
                     "cems_units": len(ops[newest]) if newest else 0}
        try:
            raw, _h = fetch(OGE_URL, timeout=120)
            res["downloads"]["oge_manual_crosswalk"] = {
                "url": OGE_URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest()}
            res["oge_rows"], oge = parse_oge(raw.decode("utf-8-sig"))
            if newest:
                res["oge"] = validate(res["by_year"][str(newest)], ops[newest], oge)
        except Exception as exc:
            res["oge_error"] = "%s: %s" % (type(exc).__name__, exc)
        write_csvs(res, oge, a.out_dir)
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "xwpair.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("by_year",)}, indent=1,
                     default=str))
    if res.get("by_year") and res.get("g1", {}).get("newest"):
        for u in res["by_year"][str(res["g1"]["newest"])]["units"]:
            if u["class"] == "unique_pair":
                print("PAIR", json.dumps(u, default=str))


if __name__ == "__main__":
    main()
