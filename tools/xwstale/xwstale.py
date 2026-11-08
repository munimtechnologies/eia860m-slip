"""xwstale: pre-registered check xwstale-1 (plan: docs/xwstale-plan.md in
munimtechnologies/eia860m-slip).

xwgap-1 (docs/xwgap.md) found that 62 of the 75 CEMS units of report year 2024 that have a peak
load, no crosswalk row and nothing at their EIA plant to link to sit at EIA plants with no
EIA-860 generator row at all that year ("absent"), and 3 more at a plant with no operating
generator ("not_operating"). PUDL's yearly CEMS table uses a three-year trailing window, so a
unit at a plant that closed in an earlier year can still have a row. This script asks, for every
absent and not_operating gap unit of every report year in data/xwgap-units-2018-2024.csv: when
was its EIA plant last listed in EIA-860 (in that year or before), and had all of the plant's
combustion generators in that listing retired before the report year began?

Classes (one per unit):
- never_listed: the plant has no EIA-860 generator row in any year up to the report year;
- retired_before: in the plant's last listing up to the report year, it has combustion
  generators and every one has a retirement date before 1 January of the report year;
- retired_in_year: every one has a retirement date, the latest falls in the report year;
- other: anything else (a combustion generator with no retirement date, one retiring after the
  report year, or no combustion generator in the listing); the cause is recorded.

A generator's retirement date is the one on its row in that listing, or, if empty there, the
latest retirement date on any of its rows up to the report year.

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
GEN_TABLE = "core_eia860__scd_generators"
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "prime_mover_code",
            "operational_status_code", "generator_retirement_date"]
POP_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/"
           "data/xwgap-units-2018-2024.csv")
UA = {"User-Agent": "mv2-xwstale/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

COMB = ("CA", "CS", "CT", "GT", "IC", "ST")
REASONS_IN = ("absent", "not_operating")
CLASSES = ("never_listed", "retired_before", "retired_in_year", "other")

# Gates and bars (docs/xwstale-plan.md)
NEWEST = 2024
POP_ROWS = 317
POP_NEWEST = 65
ZIMMER = (2024, 6019, "1")
ZIMMER_YEAR = 2022
P1_SHARE = 0.6
P2_SHARE = 0.9
P3_MAX = 10
P4_PLANTS = (563, 2866, 55243)
P4_UNITS = 35
P4_YEAR = 2023
P5_YEARS = (2019, 2020, 2021, 2022, 2023)
P5_SHARE = 0.5


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


def iso(v):
    """A date (or datetime, or text) as 'YYYY-MM-DD'; None/NaN/'' -> None."""
    if v is None:
        return None
    if isinstance(v, float) and v != v:
        return None
    s = str(v).strip()
    if len(s) < 10 or not s[:4].isdigit():
        return None
    return s[:10]


def read_population(text):
    """xwgap-units CSV text. Returns (row count, list of units with reason absent or
    not_operating: dicts year, plant (EIA), plant_epa, unit, reason)."""
    n, out = 0, []
    for r in csv.DictReader(io.StringIO(text)):
        n += 1
        if r.get("reason") not in REASONS_IN:
            continue
        out.append({"year": pint(r["report_year"]), "plant": pint(r["plant_id_eia"]),
                    "plant_epa": pint(r["plant_id_epa"]), "unit": r["emissions_unit_id_epa"],
                    "reason": r["reason"]})
    return n, out


def index_gens(rows):
    """rows: dicts with GEN_COLS. Returns {plant: {year: {gen: {"pm", "status", "ret"}}}}; for a
    repeated (plant, gen, year) the first non-empty value of each field wins."""
    out = {}
    for r in rows:
        pi, gi = pint(r.get("plant_id_eia")), gid(r.get("generator_id"))
        d = iso(r.get("report_date"))
        if pi is None or not gi or d is None:
            continue
        y = int(d[:4])
        g = out.setdefault(pi, {}).setdefault(y, {}).setdefault(
            gi, {"pm": "", "status": "", "ret": None})
        if not g["pm"]:
            g["pm"] = gid(r.get("prime_mover_code"))
        if not g["status"]:
            g["status"] = gid(r.get("operational_status_code"))
        if g["ret"] is None:
            g["ret"] = iso(r.get("generator_retirement_date"))
    return out


def classify(unit, plant_years):
    """unit: dict with year; plant_years: {year: {gen: info}} for its EIA plant (or {}).
    Returns the unit with class, last_listed, listed_later, retired_year, combustion,
    undated, after_year added."""
    y = unit["year"]
    years = sorted(plant_years)
    upto = [yr for yr in years if yr <= y]
    res = dict(unit)
    res.update({"last_listed": upto[-1] if upto else None,
                "listed_later": any(yr > y for yr in years),
                "retired_year": None, "combustion": 0, "undated": 0, "after_year": 0,
                "cause": ""})
    if not upto:
        res["class"] = "never_listed"
        return res
    snap = plant_years[upto[-1]]
    comb = sorted(g for g, info in snap.items() if info["pm"] in COMB)
    res["combustion"] = len(comb)
    if not comb:
        res["class"] = "other"
        res["cause"] = "no_combustion"
        return res
    dates = []
    for g in comb:
        ret = snap[g]["ret"]
        if ret is None:
            older = [plant_years[yr][g]["ret"] for yr in upto
                     if g in plant_years[yr] and plant_years[yr][g]["ret"]]
            ret = max(older) if older else None
        dates.append(ret)
    undated = sum(1 for d in dates if d is None)
    start = "%04d-01-01" % y
    after = sum(1 for d in dates if d is not None and d[:4] > str(y))
    res["undated"], res["after_year"] = undated, after
    if undated:
        res["class"] = "other"
        res["cause"] = "undated"
        return res
    latest = max(dates)
    res["retired_year"] = int(latest[:4])
    if latest < start:
        res["class"] = "retired_before"
    elif latest[:4] == str(y):
        res["class"] = "retired_in_year"
    else:
        res["class"] = "other"
        res["cause"] = "after_year"
    return res


def summarize(units):
    c = {"n": len(units)}
    for k in CLASSES:
        c[k] = sum(1 for u in units if u["class"] == k)
    rb = [u for u in units if u["class"] == "retired_before"]
    c["retired_before_in_window"] = sum(1 for u in rb if u["retired_year"] >= u["year"] - 2)
    c["listed_later"] = sum(1 for u in units if u["listed_later"])
    c["plants"] = len({u["plant"] for u in units})
    return c


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and all(y in g1["years"]
                                                  for y in range(2018, NEWEST + 1)))
    if not s["G1"]:
        return s
    g2 = res.get("g2", {})
    s["G2"] = g2.get("rows") == POP_ROWS and g2.get("newest_units") == POP_NEWEST
    if not s["G2"]:
        return s
    z = res.get("g3", {})
    s["G3"] = z.get("class") == "retired_before" and z.get("retired_year") == ZIMMER_YEAR
    if not s["G3"]:
        return s
    c = res["summary"][str(NEWEST)]
    n = c["n"]
    s["P1"] = c["retired_before"] / n >= P1_SHARE
    s["P2"] = (c["retired_before"] > 0
               and c["retired_before_in_window"] / c["retired_before"] >= P2_SHARE)
    s["P3"] = c["never_listed"] <= P3_MAX
    p4 = res.get("p4_units", [])
    s["P4"] = (len(p4) == P4_UNITS
               and all(u["class"] == "retired_before" and u["retired_year"] == P4_YEAR
                       for u in p4))
    s["P5"] = all(res["summary"].get(str(y), {}).get("n", 0) > 0
                  and res["summary"][str(y)]["retired_before"] / res["summary"][str(y)]["n"]
                  >= P5_SHARE for y in P5_YEARS)
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


def write_csv(units, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
                    "xwgap_reason", "class", "cause", "last_listed_year", "listed_later",
                    "combustion_generators", "undated", "retiring_after_year",
                    "latest_retirement_year"])
        for u in units:
            w.writerow([u["year"], u["plant_epa"], u["unit"], u["plant"], u["reason"],
                        u["class"], u["cause"], "" if u["last_listed"] is None
                        else u["last_listed"], u["listed_later"], u["combustion"],
                        u["undated"], u["after_year"], "" if u["retired_year"] is None
                        else u["retired_year"]])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwstale.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    try:
        raw, _h = fetch(POP_URL, timeout=120)
        res["downloads"]["population"] = {"url": POP_URL, "bytes": len(raw),
                                          "md5": hashlib.md5(raw).hexdigest()}
        n_rows, pop = read_population(raw.decode("utf-8-sig"))
        res["g2"] = {"rows": n_rows,
                     "newest_units": sum(1 for u in pop if u["year"] == NEWEST)}
        plants = sorted({u["plant"] for u in pop if u["plant"] is not None})
        gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        gens_df = gens_df.with_columns(pl.col("report_date").cast(pl.String))
        res["g1"] = {"missing_cols": res["downloads"][GEN_TABLE]["missing_cols"],
                     "years": sorted({int(s[:4]) for s in gens_df.get_column("report_date")
                                      .drop_nulls().unique().to_list()})}
        gens_df = gens_df.filter(pl.col("plant_id_eia").cast(pl.Int64).is_in(plants))
        if "generator_retirement_date" in gens_df.columns:
            gens_df = gens_df.with_columns(pl.col("generator_retirement_date").cast(pl.String))
        gens = index_gens(gens_df.to_dicts())
        del gens_df
        units = [classify(u, gens.get(u["plant"], {})) for u in pop]
        by_year = {}
        for u in units:
            by_year.setdefault(str(u["year"]), []).append(u)
        res["summary"] = {y: summarize(v) for y, v in sorted(by_year.items())}
        z = [u for u in units if (u["year"], u["plant"], u["unit"]) == ZIMMER]
        res["g3"] = ({"class": z[0]["class"], "retired_year": z[0]["retired_year"]}
                     if len(z) == 1 else {"found": len(z)})
        res["p4_units"] = [u for u in units if u["year"] == NEWEST
                           and u["plant"] in P4_PLANTS and u["reason"] == "absent"]
        res["newest_units"] = by_year.get(str(NEWEST), [])
        write_csv(units, os.path.join(a.out_dir, "xwstale-units.csv"))
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "xwstale.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("newest_units", "p4_units")},
                     indent=1, default=str))
    for u in res.get("newest_units", []):
        print("UNIT", json.dumps(u, default=str))


if __name__ == "__main__":
    main()
