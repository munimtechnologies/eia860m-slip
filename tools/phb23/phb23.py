"""phb23.py - do the Part B2/B3 (material and size) totals in PUDL's PHMSA gas distribution data
agree with Part B1 (material) and Part B4 (install decade), and is PUDL's 2017+ 'pvc' label right?

PHMSA's annual gas distribution report (Form PHMSA F 7100.1-1) gives each operator's miles of main
and number of services by material (Part B1), by material and size (Part B2 for mains, Part B3 for
services) and by install decade (Part B4). PHMSA's instructions make Part B4 the baseline the other
parts must match (over 60: within 0.5%; 60 or less: within 0.3 miles for mains, exactly for
services). PUDL publishes Parts B2/B3 as _core_phmsagas__yearly_distribution_by_material_and_size.
This tool takes, for every report, the Part B2/B3 grand total (material all_materials, size total),
the sum of its material-by-size cells, and each material's total, and compares them with the Part
B1 total, the Part B1 material values and the Part B4 decade sum. It also checks PUDL's column map,
which files PHMSA's raw mmiles_plastic_* size fields under 'pvc' (2017 form): if that is right,
Part B1's plastic miles should match pvc + pe + abs + other_plastic, not pvc alone.
Pre-registration phb23-1 (docs/phb23-plan.md in munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library, plus polars inside main() / read_slices()
to read the nightly parquet files in slices; the aggregation and scoring are pure Python.

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
B2_TABLE = "_core_phmsagas__yearly_distribution_by_material_and_size"
B4_TABLE = "core_phmsagas__yearly_distribution_by_install_decade"
BASE = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
UA = {"User-Agent": "mv2-phb23/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
B1_NEED = ("report_id", "report_date", "operator_id_phmsa", "material", "mains_miles", "services")
B2_NEED = ("report_id", "report_date", "operator_id_phmsa", "material", "main_size",
           "mains_miles", "services")
B4_NEED = ("report_id", "report_date", "operator_id_phmsa", "install_decade", "mains_miles",
           "services")
VALUE_COLS = ("mains_miles", "services")
NULL = "<null>"
KINDS = ("mains", "services")

GRAND = "all_materials"
MAT_TOTAL = "total"
SIZE_TOTAL = "total"
B4_TOTAL = "total_decades"
PVC = "pvc"
PLASTIC_OTHERS = ("pe", "abs", "other_plastic")
STEEL = ("unprotected_steel_bare", "unprotected_steel_coated",
         "cathodically_protected_steel_bare", "cathodically_protected_steel_coated", "steel")
PLASTIC = ("pvc", "pe", "abs", "other_plastic", "plastic")
OTHER = ("other", "other_alt", "other_material")

# PHMSA's consistency rule (the second argument is the baseline)
BIG = 60.0
SHARE_TOL = 0.005
SMALL_MAINS_TOL = 0.3
EPS = 1e-6

# Scored window
LATE_FIRST = 2017
LATE_LAST = 2025
PRE_LAST = 2009

# Gates and bars (docs/phb23-plan.md)
G2_MIN_LATE = 5000
G2_MIN_PER_YEAR = 300
G2_MIN_YEARS = 7
P1_MIN = 0.97
P2_MIN = 0.97
P3_MIN = 0.97
P4_MIN = 0.95
P5_MIN = 0.90
P5_MIN_N = 100
P6_MAX = 0.10
P7_MIN = 0.95
P8_MIN = 0.60
P8_MIN_FAILS = 10
FAIL_CAP = 3000
PLASTIC_CAP = 3000
SLICE_ROWS = 1000000

PARTS = ("g4_comparable", "g4_pass", "g4_fail_with_b1", "g4_fail_g1_pass", "g1_comparable",
         "g1_pass", "cg_comparable", "cg_pass", "c4_comparable", "c4_pass", "pl_comparable",
         "pl_disc", "pl_group_pass", "pl_pvc_pass")


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


def flag(x):
    return "" if x is None else int(x)


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


def add(acc, i, v):
    """Adds v to acc[i]; a blank value is left out, so acc[i] stays None until a value comes."""
    if v is not None:
        acc[i] = v if acc[i] is None else acc[i] + v


def group(material):
    """Material group used to line Part B1 up with Parts B2/B3."""
    if material in STEEL:
        return "steel"
    if material in PLASTIC:
        return "plastic"
    if material in OTHER:
        return "other"
    return material


def report_key(y, rid, op):
    return (int(y), key(rid), key(op))


def agg_b1(rows, out=None, info=None):
    """rows: (year, report_id, operator_id_phmsa, material, mains_miles, services). Per report:
    "t" = the 'total' material row; "g" = {material group: [mains, services]}; all_materials rows
    are left out (counted)."""
    out = {} if out is None else out
    info = Counter() if info is None else info
    for y, rid, op, mat, m, s in rows:
        y = num(y)
        if y is None:
            info["b1_rows_no_year"] += 1
            continue
        k = report_key(y, rid, op)
        a = out.get(k)
        if a is None:
            a = out[k] = {"t": [None, None], "g": {}}
        mat = key(mat)
        if mat == GRAND:
            info["b1_rows_all_materials"] += 1
            continue
        if mat == MAT_TOTAL:
            tgt = a["t"]
        else:
            tgt = a["g"].setdefault(group(mat), [None, None])
        for i, v in enumerate((num(m), num(s))):
            add(tgt, i, v)
    return out, info


def new_b2():
    return {"G": [None, None], "C": [None, None], "M": {}, "pvc": [None, None],
            "plo": [None, None]}


def agg_b2(rows, out=None, info=None):
    """rows: (year, report_id, operator_id_phmsa, material, main_size, mains_miles, services).
    Per report: "G" = grand total (all_materials, size total); "C" = sum of the cells (a material
    other than all_materials/total, a size other than total or blank); "M" = {material group:
    [mains, services]} from each material's size-total row; "pvc" = the pvc size-total row; "plo" =
    the pe, abs and other_plastic size-total rows. Can be called again on more rows (slices)."""
    out = {} if out is None else out
    info = Counter() if info is None else info
    for y, rid, op, mat, size, m, s in rows:
        y = num(y)
        if y is None:
            info["b2_rows_no_year"] += 1
            continue
        k = report_key(y, rid, op)
        a = out.get(k)
        if a is None:
            a = out[k] = new_b2()
        mat, size = key(mat), key(size)
        vals = (num(m), num(s))
        has = vals[0] is not None or vals[1] is not None
        if mat == GRAND:
            if size != SIZE_TOTAL:
                info["b2_rows_all_materials_by_size"] += 1
                continue
            tgts = [a["G"]]
        elif mat == MAT_TOTAL:
            info["b2_rows_material_total"] += 1
            continue
        elif size == SIZE_TOTAL:
            tgts = [a["M"].setdefault(group(mat), [None, None])]
            if mat == PVC:
                tgts.append(a["pvc"])
            elif mat in PLASTIC_OTHERS:
                tgts.append(a["plo"])
            elif mat == "plastic" and has:
                info["b2_plastic_total_rows_" + era(k[0])] += 1
        elif size == NULL:
            if has:
                info["b2_null_size_rows_with_value_" + era(k[0])] += 1
            continue
        else:
            tgts = [a["C"]]
        for tgt in tgts:
            for i, v in enumerate(vals):
                add(tgt, i, v)
    return out, info


def agg_b4(rows, out=None, info=None):
    """rows: (year, report_id, operator_id_phmsa, install_decade, mains_miles, services). Per
    report: "s" = sum of the decade rows (total_decades rows left out, counted)."""
    out = {} if out is None else out
    info = Counter() if info is None else info
    for y, rid, op, dec, m, s in rows:
        y = num(y)
        if y is None:
            info["b4_rows_no_year"] += 1
            continue
        k = report_key(y, rid, op)
        a = out.get(k)
        if a is None:
            a = out[k] = {"s": [None, None]}
        if key(dec) == B4_TOTAL:
            info["b4_total_rows"] += 1
            continue
        for i, v in enumerate((num(m), num(s))):
            add(a["s"], i, v)
    return out, info


def compare(b1, b2, b4):
    """Per report with Parts B2/B3: grand total vs B4 sum (g4, B4 the baseline), vs B1 total (g1,
    B1 the baseline), cells vs grand total (cg), cells vs B4 sum (c4); B1 material groups vs B2
    material totals; and the plastic test. Returns (records, {year: Counter}, {(era, group, kind):
    Counter})."""
    recs, years, grp = [], {}, {}
    for k in sorted(set(b1) | set(b2) | set(b4)):
        c = years.setdefault(k[0], Counter())
        a1, a2, a4 = b1.get(k), b2.get(k), b4.get(k)
        c["b1"] += int(a1 is not None)
        c["b2"] += int(a2 is not None)
        c["b4"] += int(a4 is not None)
        if a2 is None:
            continue
        r = {"key": k}
        for i, kind in enumerate(KINDS):
            g, cells = a2["G"][i], a2["C"][i]
            t = a1["t"][i] if a1 else None
            f = a4["s"][i] if a4 else None
            res = {"g": g, "c": cells, "t": t, "f": f, "g4": None, "g1": None, "cg": None,
                   "pl": None}
            if g is not None and f is not None:
                p = within(g, f, kind)
                res["g4"] = p
                c[kind + "_g4_comparable"] += 1
                c[kind + "_g4_pass"] += int(p)
                if not p and t is not None:
                    c[kind + "_g4_fail_with_b1"] += 1
                    c[kind + "_g4_fail_g1_pass"] += int(within(g, t, kind))
            if g is not None and t is not None:
                p = within(g, t, kind)
                res["g1"] = p
                c[kind + "_g1_comparable"] += 1
                c[kind + "_g1_pass"] += int(p)
            if cells is not None and g is not None:
                p = within(cells, g, kind)
                res["cg"] = p
                c[kind + "_cg_comparable"] += 1
                c[kind + "_cg_pass"] += int(p)
            if cells is not None and f is not None:
                c[kind + "_c4_comparable"] += 1
                c[kind + "_c4_pass"] += int(within(cells, f, kind))
            if a1:
                for name, v2 in a2["M"].items():
                    v1 = a1["g"].get(name)
                    if v1 is None or v1[i] is None or v2[i] is None:
                        continue
                    gc = grp.setdefault((era(k[0]), name, kind), Counter())
                    gc["comparable"] += 1
                    gc["pass"] += int(within(v2[i], v1[i], kind))
                v1 = a1["g"].get("plastic")
                pg = a2["M"].get("plastic")
                pv = a2["pvc"][i]
                if v1 and v1[i] is not None and pg and pg[i] is not None and pv is not None:
                    gp, vp = within(pg[i], v1[i], kind), within(pv, v1[i], kind)
                    c[kind + "_pl_comparable"] += 1
                    if not (gp and vp):
                        c[kind + "_pl_disc"] += 1
                        c[kind + "_pl_group_pass"] += int(gp)
                        c[kind + "_pl_pvc_pass"] += int(vp)
                        res["pl"] = (v1[i], pv, a2["plo"][i], pg[i], gp, vp)
            r[kind] = res
        recs.append(r)
    return recs, years, grp


def window(years, lo, hi):
    c = Counter()
    for y, v in years.items():
        if lo <= y <= hi:
            c.update(v)
    return c


def group_window(grp, era_name, name, kind):
    return grp.get((era_name, name, kind), Counter())


def score(years, grp, p5_min_n=P5_MIN_N, p8_min_fails=P8_MIN_FAILS):
    late = window(years, LATE_FIRST, LATE_LAST)
    p1 = frac(late["mains_g4_pass"], late["mains_g4_comparable"])
    p2 = frac(late["mains_g1_pass"], late["mains_g1_comparable"])
    p3 = frac(late["mains_cg_pass"], late["mains_cg_comparable"])
    p4 = frac(late["services_g4_pass"], late["services_g4_comparable"])
    disc = late["mains_pl_disc"]
    p5 = frac(late["mains_pl_group_pass"], disc) if disc >= p5_min_n else None
    p6 = frac(late["mains_pl_pvc_pass"], disc) if disc >= p5_min_n else None
    st = group_window(grp, "2017_2025", "steel", "mains")
    p7 = frac(st["pass"], st["comparable"])
    fails = late["mains_g4_fail_with_b1"]
    p8 = frac(late["mains_g4_fail_g1_pass"], fails) if fails >= p8_min_fails else None
    m = {"late": dict(sorted(late.items())),
         "late_mains_g4_pass_share": share(late["mains_g4_pass"], late["mains_g4_comparable"]),
         "late_mains_g1_pass_share": share(late["mains_g1_pass"], late["mains_g1_comparable"]),
         "late_mains_cg_pass_share": share(late["mains_cg_pass"], late["mains_cg_comparable"]),
         "late_mains_c4_pass_share": share(late["mains_c4_pass"], late["mains_c4_comparable"]),
         "late_services_g4_pass_share": share(late["services_g4_pass"],
                                              late["services_g4_comparable"]),
         "late_services_g1_pass_share": share(late["services_g1_pass"],
                                              late["services_g1_comparable"]),
         "late_services_cg_pass_share": share(late["services_cg_pass"],
                                              late["services_cg_comparable"]),
         "late_mains_plastic_discriminating": disc,
         "late_mains_plastic_group_pass_share": share(late["mains_pl_group_pass"], disc),
         "late_mains_plastic_pvc_pass_share": share(late["mains_pl_pvc_pass"], disc),
         "late_services_plastic_discriminating": late["services_pl_disc"],
         "late_services_plastic_group_pass_share": share(late["services_pl_group_pass"],
                                                         late["services_pl_disc"]),
         "late_services_plastic_pvc_pass_share": share(late["services_pl_pvc_pass"],
                                                       late["services_pl_disc"]),
         "late_steel_mains_comparable": st["comparable"],
         "late_steel_mains_pass_share": share(st["pass"], st["comparable"]),
         "late_mains_g4_fails_with_b1": fails,
         "late_mains_g4_fails_g1_pass_share": None if p8 is None else round(p8, 6)}
    scores = {"P1": p1 is not None and p1 >= P1_MIN,
              "P2": p2 is not None and p2 >= P2_MIN,
              "P3": p3 is not None and p3 >= P3_MIN,
              "P4": p4 is not None and p4 >= P4_MIN,
              "P5": p5 is not None and p5 >= P5_MIN,
              "P6": p6 is not None and p6 <= P6_MAX,
              "P7": p7 is not None and p7 >= P7_MIN,
              "P8": p8 is not None and p8 >= P8_MIN}
    return m, scores


def gates(files, years):
    per_year = {str(y): years.get(y, Counter())["mains_g4_comparable"]
                for y in range(LATE_FIRST, LATE_LAST + 1)}
    years_ok = sum(1 for v in per_year.values() if v >= G2_MIN_PER_YEAR)
    late = sum(per_year.values())
    g1 = all(f.get("bytes") and not f.get("missing_cols") for f in files)
    g2 = late >= G2_MIN_LATE and years_ok >= G2_MIN_YEARS
    return ({"G1": bool(g1), "G2": bool(g2)},
            {"late_mains_g4_comparable": late, "mains_g4_comparable_by_late_year": per_year,
             "late_years_with_enough": years_ok})


def fail_rows(recs, cap=FAIL_CAP):
    """One row per report and kind that fails g4, g1 or cg."""
    out = []
    for r in recs:
        for kind in KINDS:
            x = r[kind]
            if False in (x["g4"], x["g1"], x["cg"]):
                out.append([r["key"][0], r["key"][1], r["key"][2], kind, r3(x["g"]), r3(x["c"]),
                            r3(x["t"]), r3(x["f"]), flag(x["g4"]), flag(x["g1"]),
                            flag(x["cg"])])
    return out[:cap], len(out)


def plastic_rows(recs, cap=PLASTIC_CAP):
    """Every discriminating report of the plastic test."""
    out = []
    for r in recs:
        for kind in KINDS:
            p = r[kind]["pl"]
            if p:
                out.append([r["key"][0], r["key"][1], r["key"][2], kind, r3(p[0]), r3(p[1]),
                            r3(p[2]), r3(p[3]), int(p[4]), int(p[5])])
    return out[:cap], len(out)


def group_rows(grp):
    return [[e, g, k, c["comparable"], c["pass"]] for (e, g, k), c in sorted(grp.items())]


def by_year_rows(years):
    cols = ["b1", "b2", "b4"] + [k + "_" + p for k in KINDS for p in PARTS]
    return ["year"] + cols, [[y] + [years[y][c] for c in cols] for y in sorted(years)]


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


def read_slices(pl, path, need, feed, slice_rows=SLICE_ROWS):
    """Reads a parquet file in slices of slice_rows rows and passes each slice's rows, as tuples
    (year, report_id, operator_id_phmsa, <need[3:]>...), to feed. Returns info."""
    lf = pl.scan_parquet(path)
    schema = lf.collect_schema()
    info = {"dtypes": {c: str(t) for c, t in schema.items()},
            "missing_cols": [c for c in need if c not in schema]}
    if info["missing_cols"]:
        return info
    if str(schema["report_date"]).startswith("Date"):
        yexpr = pl.col("report_date").dt.year()
    else:
        yexpr = pl.col("report_date").cast(pl.String).str.slice(0, 4).cast(pl.Int32, strict=False)
    cols = [yexpr.cast(pl.Int32).alias("year"),
            pl.col("report_id").cast(pl.String),
            pl.col("operator_id_phmsa").cast(pl.Int64, strict=False).cast(pl.String)]
    for c in need[3:]:
        if c in VALUE_COLS:
            cols.append(pl.col(c).cast(pl.Float64, strict=False))
        else:
            cols.append(pl.col(c).cast(pl.String))
    n = lf.select(pl.len()).collect().item()
    info["rows"] = n
    lo, hi, slices = None, None, 0
    for off in range(0, n, slice_rows):
        df = lf.slice(off, slice_rows).select(cols).collect()
        slices += 1
        ys = [y for y in df.get_column("year").to_list() if y is not None]
        if ys:
            lo = min(ys) if lo is None else min(lo, min(ys))
            hi = max(ys) if hi is None else max(hi, max(ys))
        feed(df.iter_rows())
        del df
    info["years"], info["slices"] = [lo, hi], slices
    return info


def fetch(table, data_dir):
    url = BASE % table
    raw, headers = download(url)
    path = os.path.join(data_dir, table + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    info = {"url": url, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "last_modified": headers.get("Last-Modified"), "saved_to": path}
    return info, path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phb23-20261111")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phb23.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "tables": {}}
    b1, b2, b4, info = {}, {}, {}, Counter()
    plan = ((B1_TABLE, B1_NEED, lambda rows: agg_b1(rows, b1, info)),
            (B2_TABLE, B2_NEED, lambda rows: agg_b2(rows, b2, info)),
            (B4_TABLE, B4_NEED, lambda rows: agg_b4(rows, b4, info)))
    files = []
    for table, need, feed in plan:
        fi, path = fetch(table, a.data_dir)
        fi.update(read_slices(pl, path, need, feed))
        res["tables"][table] = fi
        files.append(fi)
        print(table, fi.get("rows"), fi.get("years"), fi.get("missing_cols"), now())
    res["reports"] = {"b1": len(b1), "b2": len(b2), "b4": len(b4)}
    res["info"] = dict(sorted(info.items()))
    recs, years, grp = compare(b1, b2, b4)
    g, gm = gates(files, years)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    header, rows = by_year_rows(years)
    write_csv(os.path.join(a.out_dir, "phb23-by-year.csv"), header, rows)
    write_csv(os.path.join(a.out_dir, "phb23-groups.csv"),
              ["era", "group", "kind", "comparable", "pass"], group_rows(grp))
    fails, n_fails = fail_rows(recs)
    res["fail_rows_total"] = n_fails
    write_csv(os.path.join(a.out_dir, "phb23-fails.csv"),
              ["year", "report_id", "operator_id_phmsa", "kind", "b2_grand_total",
               "b2_cell_sum", "b1_total", "b4_decade_sum", "grand_vs_b4_pass",
               "grand_vs_b1_pass", "cells_vs_grand_pass"], fails)
    pls, n_pls = plastic_rows(recs)
    res["plastic_rows_total"] = n_pls
    write_csv(os.path.join(a.out_dir, "phb23-plastic.csv"),
              ["year", "report_id", "operator_id_phmsa", "kind", "b1_plastic", "b2_pvc_total",
               "b2_pe_abs_other_plastic_total", "b2_plastic_group_total", "group_pass",
               "pvc_alone_pass"], pls)
    if all(g.values()):
        m, scores = score(years, grp)
        res["measures"], res["scores"] = m, dict(g, **scores)
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phb23.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
