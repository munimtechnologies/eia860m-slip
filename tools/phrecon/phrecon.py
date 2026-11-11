"""phrecon.py - do PUDL's PHMSA gas distribution Part B1 (material) totals agree with Part B4
(install decade) totals, by PHMSA's own consistency rule?

PHMSA's instructions for the annual gas distribution report (Form PHMSA F 7100.1-1) make Part B4,
decade of installation, the baseline for miles of main and number of services: values over 60 must
be within 0.5% of the baseline; values of 60 or less must be within 0.3 miles for mains, and
service counts must match exactly. PUDL's description of
core_phmsagas__yearly_distribution_by_install_decade says some operators reported negative values
"to reconcile totals across Parts B1 and B4", and PUDL sets those to zero. This tool compares, for
every report, the B1 'total' row of _core_phmsagas__yearly_distribution_by_material with the sum of
the B4 decade rows, applies PHMSA's rule, and counts what agrees. Pre-registration phrecon-1
(docs/phrecon-plan.md in munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library, plus polars inside main() to read the
nightly parquet files; the aggregation and scoring are pure Python and need no polars.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
import urllib.request
from collections import Counter

VERSION = "0.1.0"
B1_TABLE = "_core_phmsagas__yearly_distribution_by_material"
B4_TABLE = "core_phmsagas__yearly_distribution_by_install_decade"
BASE = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
UA = {"User-Agent": "mv2-phrecon/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
B1_NEED = ("report_id", "report_date", "operator_id_phmsa", "material", "mains_miles", "services")
B4_NEED = ("report_id", "report_date", "operator_id_phmsa", "commodity", "operating_state",
           "install_decade", "mains_miles", "services")
NULL = "<null>"
KINDS = ("mains", "services")
COLS = ("mains_miles", "services")
TOTAL = "total"
SKIP_MATERIALS = ("all_materials",)
B4_TOTAL = "total_decades"

# PHMSA's consistency rule (Part B4 is the baseline)
BIG = 60.0
SHARE_TOL = 0.005
SMALL_MAINS_TOL = 0.3
EPS = 1e-6
# "Exact" agreement: mains within 0.001 miles (PUDL's own mains tolerance), services equal
EXACT_MAINS_TOL = 0.001

# Windows: the scored years, and the years before PHMSA's 2010 form
LATE_FIRST = 2017
LATE_LAST = 2025
PRE_LAST = 2009

# Gates and bars (docs/phrecon-plan.md)
G2_MIN_LATE = 5000
G2_MIN_PER_YEAR = 300
P1_MIN = 0.97
P2_MIN = 0.90
P3_MIN = 0.60
P3_MIN_FAILS = 10
P4_MIN = 0.95
P5_GAP = 0.10
P5_MIN_PRE = 1000
P6_MIN_NEG = 1
P7_MIN = 0.97
FAIL_CAP = 3000
NEG_CAP = 2000


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def frac(a, b):
    return a / b if b else None


def share(a, b):
    return round(a / b, 6) if b else None


def key(value):
    """Key text: NULL for None or NaN, else str(value)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return NULL
    return str(value)


def num(value):
    """float, or None for None, NaN or text that is not a number."""
    if value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def r3(x):
    return None if x is None else round(x, 3)


def era(year):
    if year <= PRE_LAST:
        return "pre_2010"
    if year < LATE_FIRST:
        return "2010_2016"
    if year <= LATE_LAST:
        return "2017_2025"
    return "other"


def within(value, baseline, kind):
    """PHMSA's rule: over 60, within 0.5% of the baseline; 60 or less, within 0.3 miles for mains
    and exactly equal for services."""
    d = abs(value - baseline)
    if abs(baseline) > BIG:
        return d <= SHARE_TOL * abs(baseline) + EPS
    if kind == "mains":
        return d <= SMALL_MAINS_TOL + EPS
    return d <= EPS


def exact(value, baseline, kind):
    return abs(value - baseline) <= (EXACT_MAINS_TOL if kind == "mains" else EPS)


def agg_b1(rows):
    """rows: tuples (year, report_id, operator_id_phmsa, material, mains_miles, services).
    Returns ({(year, report_id, operator): {"t": [total mains, total services] (None if no
    non-null total), "s": [sum of non-total materials], "n": [non-null non-total values]}},
    info counts, negative non-total values (capped), materials by era)."""
    out = {}
    info = Counter()
    neg = []
    by_era = {}
    for y, rid, op, mat, m, s in rows:
        y = num(y)
        if y is None:
            info["rows_no_year"] += 1
            continue
        y = int(y)
        k = (y, key(rid), key(op))
        a = out.get(k)
        if a is None:
            a = out[k] = {"t": [None, None], "s": [0.0, 0.0], "n": [0, 0], "mats": set()}
        mat = key(mat)
        by_era.setdefault(era(y), Counter())[mat] += 1
        if mat in a["mats"]:
            info["duplicate_rows"] += 1
        a["mats"].add(mat)
        if mat in SKIP_MATERIALS:
            info["rows_skipped_material"] += 1
            continue
        for i, v in enumerate((num(m), num(s))):
            if v is None:
                continue
            if mat == TOTAL:
                a["t"][i] = (a["t"][i] or 0.0) + v
                if v < 0:
                    info["negative_total_values"] += 1
            else:
                a["s"][i] += v
                a["n"][i] += 1
                if v < 0:
                    info["negative_values"] += 1
                    info["negative_" + COLS[i]] += 1
                    if len(neg) < NEG_CAP:
                        neg.append((y, k[1], k[2], mat, COLS[i], v))
    for a in out.values():
        del a["mats"]
    return out, dict(info), neg, {e: dict(sorted(c.items())) for e, c in sorted(by_era.items())}


def agg_b4(rows):
    """rows: tuples (year, report_id, operator_id_phmsa, commodity, operating_state,
    install_decade, mains_miles, services). Returns ({(year, report_id, operator): {"s": [sum of
    decade mains, services], "n": [non-null values], "commodity", "state"}}, info counts)."""
    out = {}
    info = Counter()
    for y, rid, op, com, st, dec, m, s in rows:
        y = num(y)
        if y is None:
            info["rows_no_year"] += 1
            continue
        k = (int(y), key(rid), key(op))
        a = out.get(k)
        if a is None:
            a = out[k] = {"s": [0.0, 0.0], "n": [0, 0], "commodity": key(com), "state": key(st)}
        elif a["commodity"] != key(com) or a["state"] != key(st):
            info["rows_other_labels"] += 1
        if key(dec) == B4_TOTAL:
            info["total_rows"] += 1
            continue
        for i, v in enumerate((num(m), num(s))):
            if v is None:
                continue
            a["s"][i] += v
            a["n"][i] += 1
            if v < 0:
                info["negative_values"] += 1
    return out, dict(info)


def compare(b1, b4):
    """Per report in both tables: B1 total vs B4 decade sum (PHMSA's rule, B4 the baseline), and
    B1's material sum vs its own total and vs the B4 sum. Returns (records, {year: Counter})."""
    recs = []
    years = {}
    for k in sorted(set(b1) | set(b4)):
        c = years.setdefault(k[0], Counter())
        a, b = b1.get(k), b4.get(k)
        if a is None:
            c["b4_only"] += 1
            continue
        if b is None:
            c["b1_only"] += 1
            continue
        c["both"] += 1
        r = {"key": k, "commodity": b["commodity"], "state": b["state"]}
        for i, kind in enumerate(KINDS):
            t, s4, s1 = a["t"][i], b["s"][i], a["s"][i]
            has4, has1 = b["n"][i] > 0, a["n"][i] > 0
            r[kind] = None
            if t is not None and has4:
                p, e = within(t, s4, kind), exact(t, s4, kind)
                side = "equal" if e else ("b4_higher" if s4 > t else "b4_lower")
                r[kind] = {"b1": t, "b4": s4, "diff": s4 - t, "pass": p, "exact": e, "side": side}
                c[kind + "_comparable"] += 1
                c[kind + "_pass"] += int(p)
                c[kind + "_exact"] += int(e)
                if not p:
                    c[kind + "_fail_" + side] += 1
            elif t is None:
                c[kind + "_no_b1_total"] += 1
            else:
                c[kind + "_no_b4_values"] += 1
            r[kind + "_b1sum"] = None
            if t is not None and has1:
                p1 = within(s1, t, kind)
                r[kind + "_b1sum"] = {"sum": s1, "pass": p1}
                c[kind + "_b1sum_comparable"] += 1
                c[kind + "_b1sum_pass"] += int(p1)
            if has1 and has4:
                c[kind + "_s1s4_comparable"] += 1
                c[kind + "_s1s4_pass"] += int(within(s1, s4, kind))
        recs.append(r)
    return recs, years


def window(years, lo, hi):
    c = Counter()
    for y, v in years.items():
        if lo <= y <= hi:
            c.update(v)
    return c


def score(years, b1_info, p3_min_fails=P3_MIN_FAILS, p5_min_pre=P5_MIN_PRE):
    late = window(years, LATE_FIRST, LATE_LAST)
    pre = window(years, -10 ** 6, PRE_LAST)
    pm = frac(late["mains_pass"], late["mains_comparable"])
    ex = frac(late["mains_exact"], late["mains_comparable"])
    fails = late["mains_fail_b4_higher"] + late["mains_fail_b4_lower"]
    hi = frac(late["mains_fail_b4_higher"], fails) if fails >= p3_min_fails else None
    ps = frac(late["services_pass"], late["services_comparable"])
    pre_pm = (frac(pre["mains_pass"], pre["mains_comparable"])
              if pre["mains_comparable"] >= p5_min_pre else None)
    gap = pm - pre_pm if pm is not None and pre_pm is not None else None
    neg = b1_info.get("negative_values", 0)
    b1s = frac(late["mains_b1sum_pass"], late["mains_b1sum_comparable"])
    m = {"late": dict(sorted(late.items())), "pre_2010": dict(sorted(pre.items())),
         "late_mains_pass_share": share(late["mains_pass"], late["mains_comparable"]),
         "late_mains_exact_share": share(late["mains_exact"], late["mains_comparable"]),
         "late_mains_fails": fails,
         "late_fails_b4_higher_share": None if hi is None else round(hi, 6),
         "late_services_pass_share": share(late["services_pass"], late["services_comparable"]),
         "pre_mains_pass_share": share(pre["mains_pass"], pre["mains_comparable"]),
         "pass_gap_late_minus_pre": None if gap is None else round(gap, 6),
         "b1_negative_values": neg,
         "late_b1sum_mains_pass_share": share(late["mains_b1sum_pass"],
                                              late["mains_b1sum_comparable"])}
    scores = {"P1": pm is not None and pm >= P1_MIN,
              "P2": ex is not None and ex >= P2_MIN,
              "P3": hi is not None and hi >= P3_MIN,
              "P4": ps is not None and ps >= P4_MIN,
              "P5": gap is not None and gap >= P5_GAP,
              "P6": neg >= P6_MIN_NEG,
              "P7": b1s is not None and b1s >= P7_MIN}
    return m, scores


def gates(files, years):
    late = window(years, LATE_FIRST, LATE_LAST)
    per_year = {str(y): years.get(y, Counter())["mains_comparable"]
                for y in range(LATE_FIRST, LATE_LAST + 1)}
    years_ok = sum(1 for v in per_year.values() if v >= G2_MIN_PER_YEAR)
    g1 = all(f.get("bytes") and not f.get("missing_cols") for f in files)
    g2 = (late["mains_comparable"] >= G2_MIN_LATE
          and years_ok == LATE_LAST - LATE_FIRST + 1)
    return ({"G1": bool(g1), "G2": bool(g2)},
            {"late_mains_comparable": late["mains_comparable"],
             "mains_comparable_by_late_year": per_year, "late_years_with_enough": years_ok})


def fail_rows(recs, cap=FAIL_CAP):
    """Reports that fail PHMSA's rule on mains or services, by year then key."""
    out = []
    for r in recs:
        m, s = r["mains"], r["services"]
        if (m and not m["pass"]) or (s and not s["pass"]):
            b1m = r["mains_b1sum"]
            out.append([r["key"][0], r["key"][1], r["key"][2], r["commodity"], r["state"],
                        r3(m["b1"]) if m else None, r3(m["b4"]) if m else None,
                        r3(b1m["sum"]) if b1m else None, r3(m["diff"]) if m else None,
                        int(m["pass"]) if m else None,
                        r3(s["b1"]) if s else None, r3(s["b4"]) if s else None,
                        r3(s["diff"]) if s else None, int(s["pass"]) if s else None])
    return out[:cap], len(out)


def by_year_rows(years):
    cols = ("both", "b1_only", "b4_only", "mains_comparable", "mains_pass", "mains_exact",
            "mains_fail_b4_higher", "mains_fail_b4_lower", "mains_no_b1_total",
            "mains_no_b4_values", "services_comparable", "services_pass", "services_exact",
            "services_fail_b4_higher", "services_fail_b4_lower", "mains_b1sum_comparable",
            "mains_b1sum_pass", "mains_s1s4_comparable", "mains_s1s4_pass")
    return ["year"] + list(cols), [[y] + [years[y][c] for c in cols] for y in sorted(years)]


def download(url, tries=4, timeout=300):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # noqa: BLE001 - retried, then raised
            last = exc
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("%s: %s" % (url, last))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def load(pl, table, need, data_dir):
    """Downloads one nightly table; returns (info, polars frame with a 'year' column first)."""
    url = BASE % table
    raw, headers = download(url)
    path = os.path.join(data_dir, table + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    info = {"url": url, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "last_modified": headers.get("Last-Modified"), "saved_to": path}
    del raw
    schema = pl.scan_parquet(path).collect_schema()
    info["dtypes"] = {c: str(t) for c, t in schema.items()}
    info["missing_cols"] = [c for c in need if c not in schema]
    if info["missing_cols"]:
        return info, None
    df = pl.scan_parquet(path).select(list(need)).collect()
    info["rows"] = df.height
    for c in ("mains_miles", "services"):
        info["unparsed_" + c] = (df[c].cast(pl.Float64, strict=False).null_count()
                                 - df[c].null_count())
    if str(df.schema["report_date"]).startswith("Date"):
        yexpr = pl.col("report_date").dt.year()
    else:
        yexpr = pl.col("report_date").cast(pl.String).str.slice(0, 4).cast(pl.Int32, strict=False)
    cols = [yexpr.cast(pl.Int32).alias("year"),
            pl.col("report_id").cast(pl.String),
            pl.col("operator_id_phmsa").cast(pl.Int64, strict=False).cast(pl.String)]
    for c in need[3:]:
        if c in ("mains_miles", "services"):
            cols.append(pl.col(c).cast(pl.Float64, strict=False))
        else:
            cols.append(pl.col(c).cast(pl.String))
    out = df.select(cols)
    info["years"] = list(out.select(pl.col("year").min().alias("lo"),
                                    pl.col("year").max().alias("hi")).row(0))
    return info, out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phrecon-20261111")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phrecon.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now()}
    i1, d1 = load(pl, B1_TABLE, B1_NEED, a.data_dir)
    i4, d4 = load(pl, B4_TABLE, B4_NEED, a.data_dir)
    res["tables"] = {"b1": i1, "b4": i4}
    if d1 is None or d4 is None:
        b1, b1_info, neg, mats, b4, b4_info = {}, {}, [], {}, {}, {}
    else:
        b1, b1_info, neg, mats = agg_b1(d1.iter_rows())
        del d1
        b4, b4_info = agg_b4(d4.iter_rows())
        del d4
    res["b1_reports"], res["b4_reports"] = len(b1), len(b4)
    res["b1_info"], res["b4_info"], res["b1_materials_by_era"] = b1_info, b4_info, mats
    recs, years = compare(b1, b4)
    g, gm = gates([i1, i4], years)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    header, rows = by_year_rows(years)
    write_csv(os.path.join(a.out_dir, "phrecon-by-year.csv"), header, rows)
    fails, n_fails = fail_rows(recs)
    res["fail_rows_total"] = n_fails
    write_csv(os.path.join(a.out_dir, "phrecon-fails.csv"),
              ["year", "report_id", "operator_id_phmsa", "commodity", "operating_state",
               "b1_total_mains", "b4_sum_mains", "b1_material_sum_mains", "mains_b4_minus_b1",
               "mains_pass", "b1_total_services", "b4_sum_services", "services_b4_minus_b1",
               "services_pass"], fails)
    write_csv(os.path.join(a.out_dir, "phrecon-b1-negatives.csv"),
              ["year", "report_id", "operator_id_phmsa", "material", "column", "value"], neg)
    if all(g.values()):
        m, scores = score(years, b1_info)
        res["measures"], res["scores"] = m, dict(g, **scores)
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phrecon.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
