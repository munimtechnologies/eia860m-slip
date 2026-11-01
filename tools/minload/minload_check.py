"""Pre-registered comparison of PUDL's CEMS-derived minimum stable load with the minimum load
generators report on EIA-860 (pre-registration id minload-1; plan: docs/minload-plan.md in
munimtechnologies/eia860m-slip).

PUDL's out_epacems__yearly_operational_characteristics gives each EPA CEMS unit a
min_stable_load_factor: a share of the unit's highest observed hourly gross load. Times that
highest load (max_gross_load_mw) it is a minimum stable load in MW. EIA-860 asks each
generator for its minimum load in MW, which PUDL carries as minimum_load_mw in
core_eia860__scd_generators. This script matches CEMS units to EIA generators one to one
through PUDL's EPA-EIA crosswalk (core_epa__assn_eia_epacamd) and compares the two.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import io
import json
import math
import os
import sys
import time
import urllib.request

import polars as pl

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
OPS_TABLE = "out_epacems__yearly_operational_characteristics"
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
OPS_COLS = ["plant_id_epa", "emissions_unit_id_epa", "plant_id_eia", "state",
            "max_gross_load_mw", "min_stable_load_factor", "min_up_time_hours",
            "min_down_time_hours", "heat_rate_at_max_load_factor_mmbtu_per_mwh",
            "heat_rate_at_min_stable_load_factor_mmbtu_per_mwh", "ramp_up_rate_per_min",
            "ramp_down_rate_per_min", "report_year"]
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "prime_mover_code",
            "operational_status_code", "capacity_mw", "minimum_load_mw"]
UNIT = ["plant_id_epa", "emissions_unit_id_epa"]
GEN = ["plant_id_eia", "generator_id"]
INT_COLS = ("plant_id_epa", "plant_id_eia", "report_year")
STR_COLS = ("emissions_unit_id_epa", "generator_id", "prime_mover_code",
            "operational_status_code", "state")
CC_CODES = {"CT", "CA", "CS", "CC"}
CLASSES = ("GT", "CC", "ST", "IC", "other")
MIN_YEAR = 2022
AGREE = 0.20
LOW = 0.80
UA = {"User-Agent": "mv2-minload-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---- small statistics, in plain Python so the tests need nothing else -----------------------

def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def quantiles(xs, qs=(0.1, 0.25, 0.5, 0.75, 0.9)):
    s = sorted(xs)
    if not s:
        return {}
    return {str(q): s[int(round(q * (len(s) - 1)))] for q in qs}


def avg_ranks(xs):
    """Ranks from 1, ties sharing their average rank."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sa * sb)


def spearman(a, b):
    return pearson(avg_ranks(a), avg_ranks(b))


# ---- matching -------------------------------------------------------------------------------

def clean(df):
    casts = []
    for c, dt in df.schema.items():
        if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical:
            casts.append(pl.col(c).cast(pl.String))
    if casts:
        df = df.with_columns(casts)
    return df.with_columns([pl.col(c).cast(pl.Int64) for c in INT_COLS if c in df.columns]
                           + [pl.col(c).cast(pl.String) for c in STR_COLS if c in df.columns])


def one_to_one(xw, year):
    """Crosswalk pairs of the year where the CEMS unit has exactly one EIA generator and that
    generator has exactly one CEMS unit."""
    x = (xw.filter((pl.col("report_year") == year)
                   & pl.col("emissions_unit_id_epa").is_not_null()
                   & pl.col("generator_id").is_not_null()
                   & pl.col("plant_id_eia").is_not_null()
                   & pl.col("plant_id_epa").is_not_null())
         .select(UNIT + GEN).unique())
    x = x.with_columns(pl.col("generator_id").count().over(UNIT).alias("_g_per_u"),
                       pl.col("emissions_unit_id_epa").count().over(GEN).alias("_u_per_g"))
    return (x.filter((pl.col("_g_per_u") == 1) & (pl.col("_u_per_g") == 1))
            .drop(["_g_per_u", "_u_per_g"]).sort(UNIT))


def gens_year(gens, year):
    return (gens.filter(pl.col("report_date").dt.year() == year)
            .select(GEN + ["prime_mover_code", "operational_status_code", "capacity_mw",
                           "minimum_load_mw"])
            .sort(GEN).unique(subset=GEN, keep="first", maintain_order=True))


def pm_class_expr():
    pm = pl.col("prime_mover_code")
    return (pl.when(pm.is_in(sorted(CC_CODES))).then(pl.lit("CC"))
            .when(pm.is_in(["GT", "ST", "IC"])).then(pm)
            .otherwise(pl.lit("other")).alias("pm_class"))


def build(ops, xw, gens, year):
    """One row per one-to-one pair with an operational-characteristics row and an EIA-860
    generator row in the year."""
    o = (ops.filter(pl.col("report_year") == year)
         .select(UNIT + ["max_gross_load_mw", "min_stable_load_factor"]))
    m = (one_to_one(xw, year).join(o, on=UNIT, how="inner")
         .join(gens_year(gens, year), on=GEN, how="inner"))
    return m.with_columns(
        pm_class_expr(),
        (pl.col("min_stable_load_factor") * pl.col("max_gross_load_mw")).alias("pudl_min_mw"),
    ).sort(UNIT)


def comparable(m):
    """The comparison set: both minimums present and positive capacities."""
    keep = (pl.col("min_stable_load_factor").is_not_null() & (pl.col("max_gross_load_mw") > 0)
            & (pl.col("minimum_load_mw") > 0) & (pl.col("capacity_mw") > 0))
    return m.filter(keep).with_columns(
        (pl.col("pudl_min_mw") / pl.col("minimum_load_mw")).alias("ratio"),
        (pl.col("pudl_min_mw") / pl.col("capacity_mw")).alias("pudl_frac"),
        (pl.col("minimum_load_mw") / pl.col("capacity_mw")).alias("eia_frac"),
        (pl.col("max_gross_load_mw") / pl.col("capacity_mw")).alias("max_frac"),
    )


def compare_summary(c):
    n = c.height
    out = {"n": n}
    if n == 0:
        return out
    ratio = c["ratio"].to_list()
    out.update({
        "above": sum(1 for r in ratio if r > 1),
        "below": sum(1 for r in ratio if r < 1),
        "within_20": sum(1 for r in ratio if abs(r - 1) <= AGREE),
        "below_80": sum(1 for r in ratio if r < LOW),
        "median_ratio": median(ratio),
        "ratio_quantiles": quantiles(ratio),
        "median_max_frac": median(c["max_frac"].to_list()),
        "median_pudl_frac": median(c["pudl_frac"].to_list()),
        "median_eia_frac": median(c["eia_frac"].to_list()),
        "spearman_mw": spearman(c["pudl_min_mw"].to_list(), c["minimum_load_mw"].to_list()),
        "spearman_frac": spearman(c["pudl_frac"].to_list(), c["eia_frac"].to_list()),
    })
    return out


def null_by_class(m):
    res = {}
    for cl in CLASSES:
        g = m.filter(pl.col("pm_class") == cl)
        res[cl] = {"units": g.height,
                   "null_factor": g.filter(pl.col("min_stable_load_factor").is_null()).height,
                   "eia_min_reported": g.filter(pl.col("minimum_load_mw") > 0).height}
    return res


def choose_year(ops, xw, gens):
    """Latest year present in the operational-characteristics table and the crosswalk, with at
    least one EIA-860 generator reporting a minimum load."""
    oy = set(ops["report_year"].drop_nulls().unique().to_list())
    xy = set(xw["report_year"].drop_nulls().unique().to_list())
    gy = set(gens.filter(pl.col("minimum_load_mw").is_not_null())["report_date"]
             .dt.year().unique().to_list())
    both = oy & xy & gy
    return (max(both) if both else None), sorted(both)


def coverage(gens):
    g = gens.with_columns(pl.col("report_date").dt.year().alias("year"))
    t = g.group_by("year").agg(pl.len().alias("gens"),
                               pl.col("minimum_load_mw").is_not_null().sum().alias("with_min"),
                               (pl.col("minimum_load_mw") > 0).sum().alias("positive_min"))
    return {int(r["year"]): {"gens": int(r["gens"]), "with_min": int(r["with_min"]),
                             "positive_min": int(r["positive_min"] or 0)}
            for r in t.sort("year").to_dicts() if r["year"] is not None}


# ---- scoring ----------------------------------------------------------------------------------

def score(r):
    s = {}
    g1 = r.get("g1")
    if g1 is not None:
        s["G1"] = (g1["missing_cols"] == [] and g1["rows_year"] > 0
                   and r.get("year") is not None and r["year"] >= MIN_YEAR)
    c = r.get("compare")
    if not c:
        return s
    s["G2"] = c["n"] >= 300
    if c["n"] == 0:
        return s
    s["G3"] = 0.7 <= c["median_max_frac"] <= 1.3
    if s.get("G1") and s["G2"]:
        if s["G3"]:
            s["P1"] = c["above"] >= 0.5 * c["n"]
            s["P2"] = c["within_20"] < 0.40 * c["n"]
            s["P6"] = c["below_80"] >= 0.15 * c["n"]
        if c["spearman_mw"] is not None:
            s["P3"] = c["spearman_mw"] >= 0.80
        if c["spearman_frac"] is not None:
            s["P4"] = c["spearman_frac"] < 0.50
    nb = r.get("null_by_class")
    if nb and s.get("G1"):
        gt, st = nb["GT"], nb["ST"]
        if gt["units"] >= 20 and st["units"] >= 20:
            s["P5"] = (gt["null_factor"] / gt["units"]
                       >= st["null_factor"] / st["units"] + 0.15)
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


def load_table(name, cols):
    raw, headers = fetch(NIGHTLY % name)
    df = clean(pl.read_parquet(io.BytesIO(raw), columns=cols))
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified")}
    return df, info


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "minload_check.py " + VERSION, "python": sys.version.split()[0],
              "polars": pl.__version__, "started": now(), "downloads": {}}

    def save():
        result["scores"] = score(result)
        with open(os.path.join(a.out_dir, "minload_check.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)

    try:
        ops, result["downloads"][OPS_TABLE] = load_table(OPS_TABLE, None)
        missing = [c for c in OPS_COLS if c not in ops.columns]
        xw, result["downloads"][XW_TABLE] = load_table(XW_TABLE, XW_COLS)
        gens, result["downloads"][GEN_TABLE] = load_table(GEN_TABLE, GEN_COLS)
        year, years = choose_year(ops, xw, gens)
        result["year"] = year
        result["common_years"] = years
        result["g1"] = {"missing_cols": missing, "ops_rows": ops.height,
                        "rows_year": (ops.filter(pl.col("report_year") == year).height
                                      if year is not None else 0)}
        result["coverage"] = coverage(gens)
        save()
        if year is not None:
            m = build(ops, xw, gens, year)
            result["matched"] = {"one_to_one_pairs": one_to_one(xw, year).height,
                                 "with_ops_and_gen": m.height}
            result["null_by_class"] = null_by_class(m)
            c = comparable(m)
            result["compare"] = compare_summary(c)
            result["compare_by_class"] = {
                cl: compare_summary(c.filter(pl.col("pm_class") == cl)) for cl in CLASSES}
            c.write_csv(os.path.join(a.out_dir, "minload_compare_%d.csv" % year))
            m.write_csv(os.path.join(a.out_dir, "minload_matched_%d.csv" % year))
            save()
            by_year = {}
            for y in years:
                cy = comparable(build(ops, xw, gens, y))
                s = compare_summary(cy)
                by_year[y] = {k: s.get(k) for k in ("n", "above", "within_20", "below_80",
                                                     "median_ratio", "spearman_mw",
                                                     "spearman_frac", "median_max_frac")}
            result["by_year"] = by_year
    except Exception as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    result["finished"] = now()
    save()
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
