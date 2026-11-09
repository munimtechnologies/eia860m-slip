"""xwtz: pre-registered check xwtz-1 (plan: docs/xwtz-plan.md in
munimtechnologies/eia860m-slip).

PUDL's CEMS transform (src/pudl/transform/epacems.py) gives each CEMS unit a plant_id_eia by a
left join to the EPA-EIA crosswalk (core_epa__assn_eia_epacamd, all report years, deduplicated)
on plant_id_epa and emissions_unit_id_epa; a unit with no crosswalk row gets plant_id_epa as its
plant_id_eia (fill_null). convert_to_utc then looks up a UTC offset by plant_id_eia from the
timezones in core_eia__entity_plants (null timezones dropped, left join): a plant_id_eia with no
timezone gives a null operating_datetime_utc, and a fallback id that belongs to a different EIA
plant gives that plant's offset. PUDL issue #5162 asks for a validation of CEMS plants missing
from EIA data. This script counts, for the CEMS units in out_epacems__yearly_operational_
characteristics (report years 2018-2024), which ones the documented rule leaves without a
timezone or with a fallback id at an EPA plant that the crosswalk maps elsewhere.

With --verify it reads its own xwtz.json and counts null operating_datetime_utc rows in
core_epacems__hourly_emissions (years 2018+) for the flagged plants and three control plants.

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
from collections import Counter

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
OPS_TABLE = "out_epacems__yearly_operational_characteristics"
OPS_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia"]
XW_TABLE = "core_epa__assn_eia_epacamd"
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia"]
PL_TABLE = "core_eia__entity_plants"
PL_COLS = ["plant_id_eia", "timezone", "state", "plant_name_eia"]
PL_REQUIRED = ("plant_id_eia", "timezone")
HOURLY_TABLE = "core_epacems__hourly_emissions"
UA = {"User-Agent": "mv2-xwtz/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

# Gates and bars (docs/xwtz-plan.md)
YEARS = tuple(range(2018, 2025))
FOCUS = 2024
G2_MIN = 4100
G2_MAX = 4300
G3_UNIQUE = 0.99
P1_MAX = 0
P2_MAX_UNITS = 5
P3_MAX_PLANTS = 10
P4_MIN_UNITS = 1
P5_MIN_UNITS = 1
VERIFY_MAX_PLANTS = 40
VERIFY_FROM_YEAR = 2018
CONTROLS = 3


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def pint(v):
    """A plant id or year as int; None/NaN/'' -> None."""
    if v is None:
        return None
    if isinstance(v, float):
        if v != v:
            return None
        return int(v)
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None


def uid(v):
    """A unit id as PUDL joins it: the text, stripped of surrounding spaces; case kept.
    None/NaN -> ''."""
    if v is None:
        return ""
    if isinstance(v, float):
        if v != v:
            return ""
        if v.is_integer():
            v = int(v)
    return str(v).strip()


def tzv(v):
    """A timezone name, or None when missing/blank/NaN."""
    if v is None or (isinstance(v, float) and v != v):
        return None
    s = str(v).strip()
    return s or None


def build_xw(rows):
    """rows: (report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia).
    Returns (unit_map, plant_map, info): unit_map {(pe, u): set of plant_id_eia} over all years
    (as the CEMS transform uses it), plant_map {pe: set of plant_id_eia}, and counts."""
    unit_map, plant_map = {}, {}
    rows_used = skipped = 0
    for t in rows:
        pe, u, pi = pint(t[1]), uid(t[2]), pint(t[3])
        if pe is None or not u or pi is None:
            skipped += 1
            continue
        rows_used += 1
        unit_map.setdefault((pe, u), set()).add(pi)
        plant_map.setdefault(pe, set()).add(pi)
    keys = len(unit_map)
    multi = sum(1 for v in unit_map.values() if len(v) > 1)
    lz = sum(1 for (_pe, u) in unit_map if u.isdigit() and len(u) > 1 and u[0] == "0")
    info = {"rows_used": rows_used, "rows_skipped": skipped, "unit_keys": keys,
            "multi_keys": multi, "unique_share": (keys - multi) / keys if keys else 0.0,
            "leading_zero_keys": lz,
            "renumbered_plants": sum(1 for pe, v in plant_map.items() if v != {pe})}
    return unit_map, plant_map, info


def build_plants(rows):
    """rows: (plant_id_eia, timezone, state, plant_name_eia). Returns {pi: {...}}; the first
    non-null timezone wins if an id repeats."""
    out = {}
    for t in rows:
        pi = pint(t[0])
        if pi is None:
            continue
        rec = out.setdefault(pi, {"tz": None, "state": "", "name": ""})
        if rec["tz"] is None:
            rec["tz"] = tzv(t[1])
        if not rec["state"] and len(t) > 2 and t[2] is not None:
            rec["state"] = str(t[2]).strip()
        if not rec["name"] and len(t) > 3 and t[3] is not None:
            rec["name"] = str(t[3]).strip()
    return out


def classify(ops_rows, unit_map, plant_map, plants):
    """ops_rows: (report_year, plant_id_epa, emissions_unit_id_epa, plant_id_eia).
    One dict per unit-year in YEARS (duplicates of a unit-year are counted once)."""
    seen, out = set(), []
    for t in ops_rows:
        y, pe, u, pi = pint(t[0]), pint(t[1]), uid(t[2]), pint(t[3])
        if y not in YEARS or pe is None or not u:
            continue
        if (y, pe, u) in seen:
            continue
        seen.add((y, pe, u))
        xw = unit_map.get((pe, u), set())
        fallback = not xw
        if fallback:
            expected = pe
        elif len(xw) == 1:
            expected = next(iter(xw))
        else:
            expected = None
        tz = plants.get(pi, {}).get("tz") if pi is not None else None
        alt = sorted(plant_map.get(pe, set()) - {pe}) if fallback else []
        alt_tz = [plants.get(a, {}).get("tz") for a in alt]
        out.append({
            "year": y, "plant_id_epa": pe, "unit": u, "plant_id_eia": pi,
            "fallback": fallback, "multi": expected is None,
            "inconsistent": expected is not None and pi != expected,
            "in_entity": pi in plants, "tz": tz, "no_tz": tz is None,
            "alt": alt, "alt_tz": alt_tz,
            "suspicious": fallback and bool(alt),
            "tz_diff": fallback and tz is not None and any(a is not None and a != tz
                                                           for a in alt_tz),
            "renumbered": pi is not None and pi != pe})
    return out


def summarize(units):
    """Counts by year and over all years."""
    keys = ("fallback", "multi", "inconsistent", "no_tz", "suspicious", "tz_diff", "renumbered")
    by_year = {}
    for y in YEARS:
        us = [x for x in units if x["year"] == y]
        s = {"units": len(us), "plants": len({x["plant_id_epa"] for x in us}),
             "not_in_entity": sum(1 for x in us if not x["in_entity"])}
        for k in keys:
            s[k] = sum(1 for x in us if x[k])
            s[k + "_plants"] = len({x["plant_id_epa"] for x in us if x[k]})
        by_year[str(y)] = s
    allyears = {k + "_plants": len({x["plant_id_epa"] for x in units if x[k]}) for k in keys}
    allyears.update({k + "_units": len({(x["plant_id_epa"], x["unit"]) for x in units if x[k]})
                     for k in keys})
    allyears["unit_years"] = len(units)
    return {"by_year": by_year, "all_years": allyears}


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1.get("missing_required") and all(y in g1.get("years", [])
                                                          for y in YEARS))
    if not s["G1"]:
        return s
    f = res.get("summary", {}).get("by_year", {}).get(str(FOCUS), {})
    s["G2"] = G2_MIN <= f.get("units", 0) <= G2_MAX
    if not s["G2"]:
        return s
    s["G3"] = res.get("xw_info", {}).get("unique_share", 0.0) >= G3_UNIQUE
    if not s["G3"]:
        return s
    a = res["summary"]["all_years"]
    s["P1"] = f["inconsistent"] <= P1_MAX
    s["P2"] = f["no_tz"] <= P2_MAX_UNITS
    s["P3"] = a["no_tz_plants"] <= P3_MAX_PLANTS
    s["P4"] = f["suspicious"] >= P4_MIN_UNITS
    s["P5"] = sum(res["summary"]["by_year"][str(y)]["tz_diff"] for y in YEARS) >= P5_MIN_UNITS
    return s


def flagged_plants(units):
    """EPA plant ids to verify in the hourly table: plants with a unit-year lacking a timezone
    or with a different-timezone fallback, at most VERIFY_MAX_PLANTS (smallest ids first)."""
    ids = sorted({x["plant_id_epa"] for x in units if x["no_tz"] or x["tz_diff"]})
    return ids[:VERIFY_MAX_PLANTS], len(ids)


def control_plants(units, exclude):
    """The CONTROLS smallest EPA plant ids of FOCUS-year units with a timezone, not flagged."""
    ids = sorted({x["plant_id_epa"] for x in units
                  if x["year"] == FOCUS and not x["no_tz"] and not x["fallback"]
                  and x["plant_id_epa"] not in exclude})
    return ids[:CONTROLS]


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
        schema = list(pl.scan_parquet(io.BytesIO(raw)).collect_schema().names())
    have = [c for c in cols if c in schema]
    df = pl.read_parquet(io.BytesIO(raw), columns=have)
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified"),
            "missing_cols": [c for c in cols if c not in schema]}
    del raw
    return df, info


def rows_of(df, cols):
    """Tuples in cols order; a missing column gives None."""
    present = [c for c in cols if c in df.columns]
    idx = {c: i for i, c in enumerate(present)}
    for t in df.select(present).iter_rows():
        yield tuple(t[idx[c]] if c in idx else None for c in cols)


def write_csv(units, plants, out_dir):
    path = os.path.join(out_dir, "xwtz-flagged-units.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
                    "fallback", "in_entity_plants", "timezone", "eia_state", "eia_plant_name",
                    "crosswalk_other_plant_ids", "other_timezones", "other_names", "flags"])
        for x in units:
            flags = [k for k in ("no_tz", "suspicious", "tz_diff", "inconsistent", "multi")
                     if x[k]]
            if not flags:
                continue
            p = plants.get(x["plant_id_eia"], {})
            w.writerow([x["year"], x["plant_id_epa"], x["unit"],
                        "" if x["plant_id_eia"] is None else x["plant_id_eia"], x["fallback"],
                        x["in_entity"], x["tz"] or "", p.get("state", ""), p.get("name", ""),
                        "|".join(str(a) for a in x["alt"]),
                        "|".join(t or "" for t in x["alt_tz"]),
                        "|".join(plants.get(a, {}).get("name", "") for a in x["alt"]),
                        "|".join(flags)])


def main_census(out_dir):
    import polars as pl
    res = {"tool": "xwtz.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    try:
        ops, res["downloads"][OPS_TABLE] = load(OPS_TABLE, OPS_COLS, pl)
        xw, res["downloads"][XW_TABLE] = load(XW_TABLE, XW_COLS, pl)
        pdf, res["downloads"][PL_TABLE] = load(PL_TABLE, PL_COLS, pl)
        missing = (res["downloads"][OPS_TABLE]["missing_cols"]
                   + res["downloads"][XW_TABLE]["missing_cols"]
                   + [c for c in res["downloads"][PL_TABLE]["missing_cols"] if c in PL_REQUIRED])
        years = sorted({y for y in (pint(v) for v in ops.get_column("report_year").to_list())
                        if y is not None}) if "report_year" in ops.columns else []
        res["g1"] = {"missing_required": missing, "years": years}
        if missing:
            raise RuntimeError("missing columns %s" % missing)
        unit_map, plant_map, res["xw_info"] = build_xw(rows_of(xw, XW_COLS))
        plants = build_plants(rows_of(pdf, PL_COLS))
        res["entity_plants"] = {"plants": len(plants),
                                "with_timezone": sum(1 for p in plants.values() if p["tz"]),
                                "timezones": dict(Counter(p["tz"] or "" for p in
                                                          plants.values()).most_common())}
        units = classify(rows_of(ops, OPS_COLS), unit_map, plant_map, plants)
        del ops, xw, pdf
        res["summary"] = summarize(units)
        flagged, n_flagged = flagged_plants(units)
        res["verify_plan"] = {"flagged_plants": flagged, "flagged_total": n_flagged,
                              "controls": control_plants(units, set(flagged))}
        write_csv(units, plants, out_dir)
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(out_dir, "xwtz.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


def main_verify(out_dir):
    """Null operating_datetime_utc rows by plant and year in the hourly table (years 2018+)."""
    import polars as pl
    with open(os.path.join(out_dir, "xwtz.json"), encoding="utf-8") as fh:
        plan = json.load(fh).get("verify_plan", {})
    flagged, controls = plan.get("flagged_plants", []), plan.get("controls", [])
    ids = sorted(set(flagged) | set(controls))
    res = {"tool": "xwtz.py " + VERSION + " --verify", "polars": pl.__version__,
           "started": now(), "plants": ids, "controls": controls}
    try:
        if not ids:
            raise RuntimeError("nothing to verify")
        lf = pl.scan_parquet(NIGHTLY % HOURLY_TABLE)
        names = lf.collect_schema().names()
        res["columns_seen"] = [c for c in ("year", "plant_id_epa", "plant_id_eia",
                                           "emissions_unit_id_epa", "operating_datetime_utc")
                               if c in names]
        q = (lf.filter((pl.col("year") >= VERIFY_FROM_YEAR) & pl.col("plant_id_epa").is_in(ids))
             .group_by(["plant_id_epa", "plant_id_eia", "year"])
             .agg(pl.len().alias("rows"),
                  pl.col("operating_datetime_utc").is_null().sum().alias("null_utc"),
                  pl.col("emissions_unit_id_epa").n_unique().alias("units")))
        try:
            df = q.collect(engine="streaming")
        except TypeError:
            df = q.collect(streaming=True)
        res["rows"] = sorted(df.to_dicts(), key=lambda r: (r["plant_id_epa"], r["year"]))
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    with open(os.path.join(out_dir, "xwtz-verify.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.verify:
        main_verify(a.out_dir)
    else:
        main_census(a.out_dir)


if __name__ == "__main__":
    main()
