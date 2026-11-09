"""xwback: pre-registered check xwback-1 (plan: docs/xwback-plan.md in
munimtechnologies/eia860m-slip).

xwstale-1 (docs/xwstale.md) found 14 EIA plants with crosswalk gap units in report year 2024
that are missing from PUDL's EIA-860 generator table in some years after they retired and are
listed again in a later year (2025 or 2026). EIA says the annual EIA-860 retired tab "only
includes those retired generators which were reported in the most current data cycle", while
the EIA-860M Retired tab lists generators retired since 2002, and PUDL adds the latest EIA-860M
to its EIA-860 tables with data_maturity "monthly_update". This script asks whether that
explains the return, for the 14 plants and for every fully retired plant in the table.

Population A: the EIA plants of the 2024 rows of data/xwstale-units-2018-2024.csv whose
listed_later is True.
Population C: every EIA plant whose first annual report year (2024 or earlier) in which all of
its generator rows have operational_status_code RE falls in 2002-2021, and that has no
non-RE generator row in a later annual year up to 2024.

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
GEN_TABLE = "core_eia860__scd_generators"
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "operational_status_code",
            "generator_retirement_date", "data_maturity", "prime_mover_code"]
POP_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/"
           "data/xwstale-units-2018-2024.csv")
UA = {"User-Agent": "mv2-xwback/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

COMB = ("CA", "CS", "CT", "GT", "IC", "ST")
RETIRED = "RE"

# Gates and bars (docs/xwback-plan.md)
NEWEST_ANNUAL = 2024
LATER_YEARS = (2025, 2026)
G1_YEARS = tuple(range(2018, 2027))
POP_PLANTS = 14
POP_UNITS = 57
P1_MIN_PLANTS = 13
P1_MATURITY = "monthly_update"
P2_SHARE = 0.95
C_FIRST = 2002
C_LAST = 2021
P3_GAP = 3
P3_MAX_SHARE = 0.10
P4_SHARE = 0.80
P5_MAX_SHARE = 0.10
ASTORIA = 55243
ASTORIA_YEAR = 2023


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def gid(v):
    """An id or code for comparing: strip and upper-case; 1.0 -> '1'; None/NaN -> ''."""
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


def mat(v):
    """data_maturity as lower-case text; None -> ''."""
    return "" if v is None else str(v).strip().lower()


def read_population(text):
    """xwstale-units CSV text. Returns (units, plants): the 2024 rows whose listed_later is True,
    and their EIA plant ids."""
    units = []
    for r in csv.DictReader(io.StringIO(text)):
        if r.get("report_year") == str(NEWEST_ANNUAL) and r.get("listed_later") == "True":
            units.append((pint(r["plant_id_eia"]), r["emissions_unit_id_epa"]))
    return units, sorted({p for p, _ in units if p is not None})


def aggregate(rows, detail_plants):
    """rows: tuples in GEN_COLS order. Returns (plants, detail, maturity):
    plants = {plant: {year: {"gens": set, "re": set}}};
    detail = {plant: [row dicts]} for plants in detail_plants;
    maturity = Counter of (year, data_maturity) over all rows."""
    detail_plants = set(detail_plants)
    plants, detail, maturity = {}, {p: [] for p in detail_plants}, Counter()
    for t in rows:
        pi, gi = pint(t[0]), gid(t[1])
        d = iso(t[2])
        if pi is None or not gi or d is None:
            continue
        y = int(d[:4])
        status, m = gid(t[3]), mat(t[5])
        maturity[(y, m)] += 1
        py = plants.setdefault(pi, {}).setdefault(y, {"gens": set(), "re": set()})
        py["gens"].add(gi)
        if status == RETIRED:
            py["re"].add(gi)
        if pi in detail_plants:
            detail[pi].append({"gen": gi, "year": y, "status": status, "ret": iso(t[4]),
                               "maturity": m, "pm": gid(t[6])})
    return plants, detail, maturity


def fully_retired(info):
    return bool(info["gens"]) and info["re"] == info["gens"]


def population_c(plants):
    """Plants whose first annual year with every generator row RE is in C_FIRST..C_LAST and that
    have no non-RE row in a later annual year. One dict per plant."""
    out = []
    for p in sorted(plants):
        years = plants[p]
        annual = sorted(y for y in years if y <= NEWEST_ANNUAL)
        first = next((y for y in annual if fully_retired(years[y])), None)
        if first is None or not C_FIRST <= first <= C_LAST:
            continue
        if any(not fully_retired(years[y]) for y in annual if y > first):
            continue
        out.append({"plant": p, "first_retired_year": first, "last_annual": annual[-1],
                    "annual_years": len(annual),
                    "persist": any(y in years for y in range(first + P3_GAP, NEWEST_ANNUAL + 1)),
                    "in_2025": 2025 in years, "in_2026": 2026 in years})
    return out


def summarize_c(cs):
    n = len(cs)
    s = {"n": n, "persist": sum(c["persist"] for c in cs),
         "in_2025": sum(c["in_2025"] for c in cs), "in_2026": sum(c["in_2026"] for c in cs),
         "by_first_year": {}}
    for c in cs:
        b = s["by_first_year"].setdefault(str(c["first_retired_year"]),
                                          {"n": 0, "persist": 0, "in_2025": 0, "in_2026": 0})
        b["n"] += 1
        for k in ("persist", "in_2025", "in_2026"):
            b[k] += c[k]
    return s


def population_a(pop_plants, units, plants, detail):
    """One dict per population-A plant."""
    n_units = Counter(p for p, _ in units)
    out = []
    for p in pop_plants:
        years = sorted(plants.get(p, {}))
        rows = detail.get(p, [])
        later = [r for r in rows if r["year"] > NEWEST_ANNUAL]
        r26 = [r for r in rows if r["year"] == 2026]
        out.append({
            "plant": p, "units_2024": n_units[p], "years": years,
            "last_annual": max([y for y in years if y <= NEWEST_ANNUAL], default=None),
            "rows_2025": sum(1 for r in rows if r["year"] == 2025),
            "rows_2026": len(r26),
            "maturity_2025": dict(Counter(r["maturity"] for r in rows if r["year"] == 2025)),
            "maturity_2026": dict(Counter(r["maturity"] for r in r26)),
            "later_rows": len(later),
            "later_re": sum(1 for r in later if r["status"] == RETIRED),
            "later_status": dict(Counter(r["status"] for r in later)),
            "p1_ok": bool(r26) and all(r["maturity"] == P1_MATURITY for r in r26)})
    return out


def astoria_undated(rows):
    """Combustion generators in Astoria's ASTORIA_YEAR rows with no retirement date on any row up
    to that year, and every row of each (all years)."""
    upto = [r for r in rows if r["year"] <= ASTORIA_YEAR]
    snap = sorted({r["gen"] for r in upto if r["year"] == ASTORIA_YEAR and r["pm"] in COMB})
    undated = [g for g in snap if not any(r["ret"] for r in upto if r["gen"] == g)]
    return {g: sorted(({k: r[k] for k in ("year", "status", "ret", "maturity", "pm")}
                       for r in rows if r["gen"] == g), key=lambda r: (r["year"], r["maturity"]))
            for g in undated}


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and all(y in g1["years"] for y in G1_YEARS))
    if not s["G1"]:
        return s
    g2 = res.get("g2", {})
    s["G2"] = g2.get("plants") == POP_PLANTS and g2.get("units") == POP_UNITS
    if not s["G2"]:
        return s
    a = res.get("pop_a", [])
    s["G3"] = len(a) == POP_PLANTS and all(any(y > NEWEST_ANNUAL for y in p["years"]) for p in a)
    if not s["G3"]:
        return s
    s["P1"] = sum(1 for p in a if p["p1_ok"]) >= P1_MIN_PLANTS
    later = sum(p["later_rows"] for p in a)
    s["P2"] = later > 0 and sum(p["later_re"] for p in a) / later >= P2_SHARE
    c = res.get("pop_c_summary", {})
    n = c.get("n", 0)
    s["P3"] = n > 0 and c["persist"] / n <= P3_MAX_SHARE
    s["P4"] = n > 0 and c["in_2026"] / n >= P4_SHARE
    s["P5"] = n > 0 and c["in_2025"] / n <= P5_MAX_SHARE
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
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified"),
            "missing_cols": [c for c in cols if c not in schema]}
    del raw
    df = df.with_columns([pl.col(c).cast(pl.String) for c in df.columns])
    return df, info


def write_csvs(res, out_dir):
    with open(os.path.join(out_dir, "xwback-plants.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["plant_id_eia", "units_2024", "years_listed", "last_annual_year", "rows_2025",
                    "rows_2026", "maturity_2025", "maturity_2026", "later_rows", "later_rows_RE"])
        for p in res.get("pop_a", []):
            w.writerow([p["plant"], p["units_2024"], "|".join(str(y) for y in p["years"]),
                        "" if p["last_annual"] is None else p["last_annual"], p["rows_2025"],
                        p["rows_2026"], json.dumps(p["maturity_2025"], sort_keys=True),
                        json.dumps(p["maturity_2026"], sort_keys=True), p["later_rows"],
                        p["later_re"]])
    with open(os.path.join(out_dir, "xwback-retired-plants.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["plant_id_eia", "first_retired_year", "last_annual_year", "annual_years",
                    "listed_3plus_years_later", "in_2025", "in_2026"])
        for c in res.get("pop_c", []):
            w.writerow([c["plant"], c["first_retired_year"], c["last_annual"], c["annual_years"],
                        c["persist"], c["in_2025"], c["in_2026"]])


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwback.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}
    try:
        raw, _h = fetch(POP_URL, timeout=120)
        res["downloads"]["population"] = {"url": POP_URL, "bytes": len(raw),
                                          "md5": hashlib.md5(raw).hexdigest()}
        units, pop_plants = read_population(raw.decode("utf-8-sig"))
        res["g2"] = {"plants": len(pop_plants), "units": len(units)}
        df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        missing = res["downloads"][GEN_TABLE]["missing_cols"]
        years = sorted({int(s[:4]) for s in df.get_column("report_date").drop_nulls().to_list()
                        if s[:4].isdigit()}) if "report_date" in df.columns else []
        res["g1"] = {"missing_cols": missing, "years": years}
        if missing:
            raise RuntimeError("missing columns %s" % missing)
        plants, detail, maturity = aggregate(df.select(GEN_COLS).iter_rows(),
                                             set(pop_plants) | {ASTORIA})
        del df
        res["maturity_by_year"] = {"%d %s" % k: v for k, v in sorted(maturity.items())
                                   if k[0] >= 2018}
        res["pop_a"] = population_a(pop_plants, units, plants, detail)
        cs = population_c(plants)
        res["pop_c"] = cs
        res["pop_c_summary"] = summarize_c(cs)
        res["astoria_undated"] = astoria_undated(detail.get(ASTORIA, []))
        write_csvs(res, a.out_dir)
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "xwback.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "pop_c"}, indent=1, default=str))


if __name__ == "__main__":
    main()
