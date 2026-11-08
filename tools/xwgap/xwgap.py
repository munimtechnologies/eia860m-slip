"""xwgap: pre-registered check xwgap-1 (plan: docs/xwgap-plan.md in
munimtechnologies/eia860m-slip).

xwpair-1 (docs/xwpair.md) counted the CEMS units that have no row in PUDL's run of EPA's CAMD-EIA
crosswalk (core_epa__assn_eia_epacamd). In report year 2024, 75 of them had a CEMS peak load above
zero but no "candidate" at their EIA plant: no operating, unlinked combustion generator that a new
row could point to. The size rule could say nothing about them. This script sorts every such unit
of every report year by reason:

- absent: the unit's EIA plant has no EIA-860 generator row at all that year;
- not_operating: the plant has generator rows, but none is an operating combustion generator with
  a nameplate above zero;
- all_linked: the plant has operating combustion generators and every one of them is already
  linked by some crosswalk row that year (to other CEMS units).

For each unit it also records the plant's linked operating combustion generators whose nameplate
fits the unit's CEMS peak (0.5 to 1.5 times), any generator at the plant whose id equals the unit
id, other EIA plants that the same EPA plant links to that year, the EIA status codes at the plant,
whether Open Grid Emissions' manual crosswalk (pinned commit) has a row for the unit, and whether
the unit was also unmatched the year before.

Definitions follow xwpair.py 0.1.0. Unit ids are compared after trimming, upper-casing and removing
leading zeros (as OGE does); EIA generator ids after trimming and upper-casing.

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
UA = {"User-Agent": "mv2-xwgap/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

COMB = ("CA", "CS", "CT", "GT", "IC", "ST")
LO = 0.5
HI = 1.5
REASONS = ("absent", "not_operating", "all_linked")

# Gates and bars (docs/xwgap-plan.md)
MIN_NEWEST = 2023
MIN_UNITS = 2000
MIN_GAP = 40
MIN_OGE_ROWS = 150
P2_SHARE = 0.2
P3_MIN_N = 10
P3_SHARE = 0.5
P4_MIN = 10
P5_SHARE = 0.25
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
    repeated key the largest peak and the first non-empty EIA plant win (as xwpair.py)."""
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
    naming an EIA generator, "linked": set of (EIA plant, EIA generator), "gen_units":
    {(EIA plant, EIA generator): set of (plant_id_epa, unit)}, "epa_to_eia": {plant_id_epa: set
    of EIA plants}}}."""
    out = {}
    for r in rows:
        y = pint(r.get("report_year"))
        if y is None:
            continue
        d = out.setdefault(y, {"units": set(), "linked": set(), "gen_units": {},
                               "epa_to_eia": {}})
        pe, ue = pint(r.get("plant_id_epa")), uid(r.get("emissions_unit_id_epa"))
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        if not gi:
            continue
        if pe is not None and ue:
            d["units"].add((pe, ue))
        if pi is not None:
            d["linked"].add((pi, gi))
            if pe is not None:
                d["epa_to_eia"].setdefault(pe, set()).add(pi)
                if ue:
                    d["gen_units"].setdefault((pi, gi), set()).add((pe, ue))
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


def is_comb_op(info):
    return info["status"] == "OP" and info["pm"] in COMB and (info["cap"] or 0) > 0


def size_ok(peak, cap):
    return bool(peak and cap and peak > 0 and cap > 0 and LO <= peak / cap <= HI)


def unmatched_keys(ops_y, xw_y):
    return {k for k in ops_y if k not in xw_y["units"]}


def year_gaps(ops_y, xw_y, gens_y, oge_units, prev_unmatched):
    """Every unmatched CEMS unit of one year with a peak above zero and no candidate, with its
    reason and leads. prev_unmatched: set of unmatched keys the year before, or None."""
    linked = xw_y["linked"]
    by_plant = {}
    for (pi, gi), info in gens_y.items():
        by_plant.setdefault(pi, []).append((gi, info))
    out = []
    for key in sorted(unmatched_keys(ops_y, xw_y)):
        d = ops_y[key]
        if not d["peak"] or d["peak"] <= 0:
            continue
        pi = d["pi"]
        gl = sorted(by_plant.get(pi, []), key=lambda g: g[0])
        comb = [(gi, info) for gi, info in gl if is_comb_op(info)]
        if any((pi, gi) not in linked for gi, _info in comb):
            continue  # has a candidate: xwpair-1's classes cover it
        if not gl:
            reason = "absent"
        elif not comb:
            reason = "not_operating"
        else:
            reason = "all_linked"
        fits = [gi for gi, info in comb if size_ok(d["peak"], info["cap"])]
        fit_units = sorted({"%s/%s" % u for gi in fits
                            for u in xw_y["gen_units"].get((pi, gi), set())})
        out.append({
            "plant_id_epa": key[0], "unit": key[1], "plant_id_eia": pi, "peak": d["peak"],
            "reason": reason,
            "generators": len(gl),
            "statuses": sorted({info["status"] or "?" for _gi, info in gl}),
            "linked_fits": fits,
            "linked_fit_units": fit_units,
            "same_id": [gi for gi, _info in gl if uid(gi) == key[1]],
            "other_eia_plants": sorted(p for p in xw_y["epa_to_eia"].get(key[0], set())
                                       if p != pi),
            "in_oge": key in oge_units,
            "unmatched_prev": None if prev_unmatched is None else key in prev_unmatched,
        })
    return out


def summarize(units):
    n = len(units)
    c = {"n": n}
    for r in REASONS:
        c[r] = sum(1 for u in units if u["reason"] == r)
    al = [u for u in units if u["reason"] == "all_linked"]
    c["all_linked_with_fit"] = sum(1 for u in al if u["linked_fits"])
    c["same_id"] = sum(1 for u in units if u["same_id"])
    c["other_eia_plant"] = sum(1 for u in units if u["other_eia_plants"])
    c["in_oge"] = sum(1 for u in units if u["in_oge"])
    prev = [u for u in units if u["unmatched_prev"] is not None]
    c["with_prev_year"] = len(prev)
    c["unmatched_prev"] = sum(1 for u in prev if u["unmatched_prev"])
    c["plants"] = len({u["plant_id_eia"] for u in units})
    return c


def parse_oge(text):
    """OGE's manual crosswalk CSV text (every row, any note). Returns (row count, set of
    (plant_id_epa, unit))."""
    n, out = 0, set()
    for r in csv.DictReader(io.StringIO(text)):
        pe, ue = pint(r.get("plant_id_epa")), uid(r.get("emissions_unit_id_epa"))
        if pe is None or not ue:
            continue
        n += 1
        out.add((pe, ue))
    return n, out


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and g1["newest"] is not None
                   and g1["newest"] >= MIN_NEWEST and g1["cems_units"] >= MIN_UNITS)
    if not s["G1"]:
        return s
    c = res["summary"][str(g1["newest"])]
    s["G2"] = c["n"] >= MIN_GAP
    if not s["G2"]:
        return s
    n = c["n"]
    s["P1"] = c["all_linked"] > c["absent"] and c["all_linked"] > c["not_operating"]
    s["P2"] = c["absent"] / n >= P2_SHARE
    if c["all_linked"] >= P3_MIN_N:
        s["P3"] = c["all_linked_with_fit"] / c["all_linked"] >= P3_SHARE
    s["P4"] = c["same_id"] >= P4_MIN
    s["G3"] = res.get("oge_rows", 0) >= MIN_OGE_ROWS
    if s["G3"]:
        s["P5"] = c["in_oge"] / n >= P5_SHARE
    if c["with_prev_year"] == n:
        s["P6"] = c["unmatched_prev"] / n >= P6_SHARE
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


def write_csv(by_year, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
                    "max_gross_load_mw", "reason", "eia_generators_at_plant", "eia_statuses",
                    "linked_generators_that_fit", "units_linked_to_those", "same_id_generators",
                    "other_eia_plants_of_epa_plant", "in_oge_manual", "unmatched_prev_year"])
        for y in sorted(by_year):
            for u in by_year[y]:
                w.writerow([y, u["plant_id_epa"], u["unit"], u["plant_id_eia"], u["peak"],
                            u["reason"], u["generators"], ";".join(u["statuses"]),
                            ";".join(u["linked_fits"]), ";".join(u["linked_fit_units"]),
                            ";".join(u["same_id"]), ";".join(map(str, u["other_eia_plants"])),
                            u["in_oge"], "" if u["unmatched_prev"] is None
                            else u["unmatched_prev"]])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwgap.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
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
        plants = sorted({ops[y][k]["pi"] for y in years for k in unmatched_keys(ops[y], xw[y])})
        gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        gens_df = gens_df.with_columns(pl.col("report_date").cast(pl.String))
        gens_df = gens_df.filter(
            pl.col("plant_id_eia").cast(pl.Int64).is_in(plants)
            & pl.col("report_date").str.slice(0, 4).cast(pl.Int64).is_in(years))
        gens = index_gens(gens_df.to_dicts())
        del gens_df
        oge = set()
        try:
            raw, _h = fetch(OGE_URL, timeout=120)
            res["downloads"]["oge_manual_crosswalk"] = {
                "url": OGE_URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest()}
            res["oge_rows"], oge = parse_oge(raw.decode("utf-8-sig"))
        except Exception as exc:
            res["oge_error"] = "%s: %s" % (type(exc).__name__, exc)
        by_year = {}
        for y in years:
            prev = unmatched_keys(ops[y - 1], xw[y - 1]) if (y - 1) in years else None
            by_year[str(y)] = year_gaps(ops[y], xw[y], gens.get(y, {}), oge, prev)
        res["summary"] = {y: summarize(v) for y, v in by_year.items()}
        res["g1"] = {"missing_cols": (res["downloads"][XW_TABLE]["missing_cols"]
                                      + res["downloads"][OPS_TABLE]["missing_cols"]
                                      + res["downloads"][GEN_TABLE]["missing_cols"]),
                     "newest": newest,
                     "cems_units": len(ops[newest]) if newest else 0}
        res["newest_units"] = by_year.get(str(newest), []) if newest else []
        write_csv(by_year, os.path.join(a.out_dir, "xwgap-units.csv"))
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "xwgap.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "newest_units"}, indent=1,
                     default=str))
    for u in res.get("newest_units", []):
        print("GAP", json.dumps(u, default=str))


if __name__ == "__main__":
    main()
