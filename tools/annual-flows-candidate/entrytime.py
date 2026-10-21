"""entrytime: in which month of the year do the annual EIA-860's plan-only projects enter EIA-860M?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

entry860 (docs/annual-flows-eia860-entry.md) found that most of the annual EIA-860's 2017
annual-only capacity was first listed in EIA-860M during 2017, after January. Its 20 October
correction left two readings open: R1 (lag), the annual filing (due early in the year) held
these projects and EIA-860M listed them only after EIA took the filing in; R2 (revision), the
annual records were added or revised during the year, after the projects appeared elsewhere.
This splits, for each year Y 2017-2025, three sets of generators by the month of their first
EIA-860M report:

    A        annual_only generators of Y first listed after January (entry860's
             entered_after_january), as entry860 0.1.0 classifies them
    A_built  the year's EIA-860M new entries (came online in Y, not listed in January;
             eia860m_slip's new_entry after rule R) that are in Y's annual plan
    B        the year's EIA-860M new entries that are not in Y's annual plan (the control)

Under R1, A and A_built should bunch in the March-June reports, more than B. A_built and B
both came online in Y, so their contrast is not driven by how close to operation a project was.

Checks and predictions: docs/entry-timing-preregistration.md.

    python entrytime.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os
import urllib.request

import numpy as np
import pandas as pd

import entry860 as en

an, bn, es = en.an, en.bn, en.es

__version__ = "0.1.0"

SETS = ("A", "A_built", "B")
MONTHS = tuple("m%02d" % i for i in range(1, 13))
BUCKETS = ("before",) + MONTHS + ("after", "unlisted")
FEB_DEC = MONTHS[1:]
MAR_JUN = ("m03", "m04", "m05", "m06")
OCT_DEC = ("m10", "m11", "m12")
YEARS = bn.YEARS
SCORED = tuple(range(2018, 2026))
POOLED = "2018-2025"
# Check U1: per year, entry860-v1's entered_after_january, new_entry_mw and
# new_entry_in_annual_plan_mw for group "all", as docs/annual-flows-eia860-entry.md states them.
PUBLISHED = {2017: (3530.1, 4626.7, 2871.8), 2018: (4666.4, 6135.9, 3828.4),
             2019: (3067.2, 4017.4, 1873.7), 2020: (7158.8, 8355.6, 4266.4),
             2021: (5337.3, 6384.5, 2815.2), 2022: (7141.9, 8390.6, 3815.9),
             2023: (9565.0, 12233.5, 6765.5), 2024: (11032.0, 11118.1, 7662.0),
             2025: (7294.9, 13300.1, 5971.3)}
TOL = {"A": 0.1, "A_built": 0.1, "B": 0.15}  # B is a difference of two published figures
ROW_COLS = (["year", "set", "group", "total_mw", "before"] + list(MONTHS)
            + ["after", "unlisted", "mar_jun_share", "oct_dec_share"])
SET_COLS = ["year", "set", "key", "group", "mw", "first_listed", "bucket"]


def bucket(m, year):
    """The month of `year` in which a first EIA-860M report falls (m01-m12), or before, after
    or unlisted."""
    if m is None or m != m:
        return "unlisted"
    m, lo = int(m), year * 12
    if m < lo:
        return "before"
    if m > lo + 11:
        return "after"
    return "m%02d" % (m - lo + 1)


def first_month(keys, first):
    """The first EIA-860M report month (entry860.entries) of each key, NaN where none."""
    return [float(first.at[k, "first_m"]) if isinstance(k, str) and k in first.index else np.nan
            for k in keys]


def sets(b, f, new, first):
    """The three sets of one year as frames (key, group, mw, first_m): b is the year's annual
    plan, f its classified annual_only rows (entry860.classify), new its EIA-860M new entries
    with nkey; the A_built / B split is entry860's in_annual_plan test."""
    a = f[f["entry"] == "entered_after_january"]
    inside = new["nkey"].isin(set(b["key"]))
    out = {"A": pd.DataFrame({"key": a["key"].to_numpy(), "group": a["group"].to_numpy(),
                              "mw": a["mw"].to_numpy(dtype=float),
                              "first_m": a["first_m"].to_numpy(dtype=float)})}
    for name, part in (("A_built", new[inside]), ("B", new[~inside])):
        out[name] = pd.DataFrame({"key": part["nkey"].to_numpy(),
                                  "group": part["group"].to_numpy(),
                                  "mw": part["mw"].to_numpy(dtype=float),
                                  "first_m": first_month(part["nkey"], first)})
    return out


def timing(s, year):
    """MW of a set by the bucket of its first EIA-860M report."""
    out = {k: 0.0 for k in BUCKETS}
    for m, mw in zip(s["first_m"], s["mw"]):
        out[bucket(m, year)] += float(mw)
    return out


def _ratio(num, den):
    return num / den if den > 0 else None


def _r4(x):
    return None if x is None else round(x, 4)


def part_share(x, cols):
    """Share of a row's February-December MW in `cols`, from the row's (rounded) MW."""
    if x is None:
        return None
    return _ratio(sum(x[k] for k in cols), sum(x[k] for k in FEB_DEC))


def _row(label, t):
    row = dict(label)
    row.update({k: round(v, 1) for k, v in t.items()})
    row["total_mw"] = round(sum(t.values()), 1)
    row["mar_jun_share"] = _r4(part_share(row, MAR_JUN))
    row["oct_dec_share"] = _r4(part_share(row, OCT_DEC))
    return row


def summarize(by_year):
    """One row per year, set and group ('all' and each group), then the pooled 2018-2025 rows."""
    rows, pooled = [], {}
    for year in sorted(by_year):
        for name in SETS:
            s = by_year[year][name]
            for grp in ["all"] + sorted(set(s["group"].dropna())):
                t = timing(s if grp == "all" else s[s["group"] == grp], year)
                rows.append(_row({"year": int(year), "set": name, "group": grp}, t))
                if year in SCORED:
                    acc = pooled.setdefault((name, grp), {k: 0.0 for k in BUCKETS})
                    for k, v in t.items():
                        acc[k] += v
    for name, grp in sorted(pooled, key=lambda x: (SETS.index(x[0]), x[1] != "all", x[1])):
        rows.append(_row({"year": POOLED, "set": name, "group": grp}, pooled[(name, grp)]))
    return rows


def checks(rows):
    r = {(x["year"], x["set"], x["group"]): x for x in rows}
    got, u1 = {}, True
    for y, (ea, ne, nin) in PUBLISHED.items():
        want = {"A": ea, "A_built": nin, "B": round(ne - nin, 1)}
        got[y] = {s: (r[(y, s, "all")]["total_mw"] if (y, s, "all") in r else None) for s in SETS}
        u1 = u1 and all(got[y][s] is not None and abs(got[y][s] - want[s]) <= TOL[s] + 1e-9
                        for s in SETS)
    bad = []
    for (y, s, g), x in r.items():
        if g != "all":
            continue
        parts = [v["total_mw"] for (y2, s2, g2), v in r.items()
                 if y2 == y and s2 == s and g2 != "all"]
        if abs(sum(parts) - x["total_mw"]) > 0.05 * (len(parts) + 1):
            bad.append("%s %s" % (y, s))
    stray = {}
    for (y, s, g), x in r.items():
        if g != "all" or y == POOLED:
            continue
        # A is first listed after January by definition; a new entry was not listed in
        # January, but its normal-form key can match another raw key's record (allowed: 1%).
        cols = ("before", "m01", "unlisted") if s == "A" else ("m01", "unlisted")
        limit = 0.05 if s == "A" else max(0.05, 0.01 * x["total_mw"])
        v = round(sum(x[k] for k in cols), 1)
        if v > limit:
            stray["%s %s" % (y, s)] = v
    return {"U1": {"got": got, "expected": {y: list(v) for y, v in PUBLISHED.items()},
                   "pass": u1},
            "U2": {"groups_not_adding_up": bad, "pass": not bad},
            "U3": {"stray_mw": stray, "pass": not stray},
            "all_pass": bool(u1 and not bad and not stray)}


def predictions(rows):
    """P1-P5 on the 'all' rows. Shares are compared with their thresholds unrounded (from the
    rows' MW) and rounded only for display."""
    r = {(x["year"], x["set"], x["group"]): x for x in rows}

    def share(year, s, cols):
        return part_share(r.get((year, s, "all")), cols)

    a, ab, b = (share(POOLED, s, MAR_JUN) for s in SETS)
    out = {"P1": {"A_mar_jun_share": _r4(a), "floor": 0.50,
                  "held": None if a is None else a >= 0.50}}
    d = None if a is None or b is None else a - b
    out["P2"] = {"A_mar_jun_share": _r4(a), "B_mar_jun_share": _r4(b), "difference": _r4(d),
                 "floor": 0.10, "held": None if d is None else d >= 0.10}
    years, above = [], []
    for y in SCORED:
        sa, sb = share(y, "A", MAR_JUN), share(y, "B", MAR_JUN)
        if sa is None or sb is None:
            continue
        years.append(y)
        if sa > sb:
            above.append(y)
    out["P3"] = {"years": years, "years_A_above_B": above, "min": 6,
                 "held": None if len(years) < len(SCORED) else len(above) >= 6}
    d = None if ab is None or b is None else ab - b
    out["P4"] = {"A_built_mar_jun_share": _r4(ab), "B_mar_jun_share": _r4(b),
                 "difference": _r4(d), "floor": 0.10, "held": None if d is None else d >= 0.10}
    late = share(POOLED, "A", OCT_DEC)
    out["P5"] = {"A_oct_dec_share": _r4(late), "ceiling": 0.10,
                 "held": None if late is None else late <= 0.10}
    return out


def write_md(path, meta, rows, chk, pred):
    md = ["# When in the year the annual EIA-860's plan-only projects enter EIA-860M", "",
          "entrytime %s on entry860 %s, baseline860 %s, annual860 %s and eia860m-slip %s; "
          "annual data %s (report years %s-%s); EIA-860M reports to %s. MV2 of Munim, Inc. "
          "(made with AI agents)." % (
              __version__, meta["entry860"], meta["baseline860"], meta["annual860"],
              meta["eia860m_slip"], meta["annual_source"], meta["annual_report_years"][0],
              meta["annual_report_years"][-1], meta["report_max"]), "",
          "A: annual_only generators of Y first listed in EIA-860M after January "
          "(entered_after_january). A_built: Y's EIA-860M new entries (came online in Y, not "
          "listed in January, rule R applied) in Y's annual plan. B: Y's new entries not in "
          "Y's annual plan. m01-m12: MW by the month of Y of the first EIA-860M report (a "
          "report month, not a release date); before / after: first listed before or after "
          "Y. mar_jun_share and oct_dec_share are shares of the February-December MW.", "",
          "Annual records by data_maturity before EIA-860M rows were left out: %s; kept %d." % (
              json.dumps(meta["annual_maturity_counts"]), meta["annual_rows_kept"]), ""]
    md += ["## Every year and pooled, all groups (MW)", ""]
    md += es.table([x for x in rows if x["group"] == "all"], ROW_COLS) + [""]
    md += ["## Pooled 2018-2025, main groups (MW)", ""]
    md += es.table([x for x in rows if x["year"] == POOLED and x["group"] in an.SHOWN_GROUPS
                    and x["group"] != "all"], ROW_COLS) + [""]
    md += ["## Checks", "", "```", json.dumps(chk, indent=1), "```", "",
           "## Predictions", "", "```", json.dumps(pred, indent=1), "```", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--annual", default="/tmp/eia860/out_eia__yearly_generators.parquet")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    import pyarrow.parquet as pq
    # The same steps as entry860.main, so A, A_built and B are entry860-v1's sets.
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    if not os.path.exists(args.annual):
        os.makedirs(os.path.dirname(args.annual), exist_ok=True)
        urllib.request.urlretrieve(an.URL_860, args.annual)
    a_names = pq.read_schema(args.annual).names
    missing = [c for c in bn.COLS if c not in a_names]
    a = pd.read_parquet(args.annual, columns=[c for c in bn.COLS + an.OPTIONAL_860 if c in a_names])
    for c in missing:
        a[c] = np.nan
    a, maturity = an.annual_only(a)
    report_years = sorted({int(y) for y in
                           pd.to_datetime(a["report_date"], errors="coerce").dt.year.dropna()})
    plan = an._plan_rows(df, a)
    op_first, listed = an.annual_first(a)
    bases = {y: bn.mark(bn.baseline(a, y), plan, y, op_first, listed)[0] for y in YEARS}
    _, gens = es.annual_flows(df)
    built = gens[(gens["kind"] == "built") & (gens["state"] == "new_entry")].copy()
    built["nkey"] = [an.plan_key(k) for k in built["key"]]
    first = en.entries(df)
    by_year = {}
    for y in YEARS:
        f = en.classify(bases[y], y, en.january(df, y), first, op_first)
        by_year[y] = sets(bases[y], f, built[built["year"] == y], first)
    rows = summarize(by_year)
    chk = checks(rows)
    pred = predictions(rows)
    meta = {"version": __version__, "entry860": en.__version__, "baseline860": bn.__version__,
            "annual860": an.__version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "report_max": es.month_str(df["report_m"].max()),
            "annual_source": os.path.basename(args.annual),
            "annual_bytes": os.path.getsize(args.annual), "missing_columns": missing,
            "annual_maturity_counts": maturity, "annual_rows_kept": int(len(a)),
            "annual_report_years": report_years}
    with open(os.path.join(args.out_dir, "entrytime.json"), "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "checks": chk, "predictions": pred, "rows": rows}, fh,
                  indent=1, default=str)
    write_md(os.path.join(args.out_dir, "entrytime.md"), meta, rows, chk, pred)
    recs = []
    for y in YEARS:
        for name in SETS:
            s = by_year[y][name]
            recs.append(pd.DataFrame({"year": y, "set": name, "key": s["key"].to_numpy(),
                                      "group": s["group"].to_numpy(),
                                      "mw": s["mw"].round(1).to_numpy(),
                                      "first_listed": [es.month_str(m) for m in s["first_m"]],
                                      "bucket": [bucket(m, y) for m in s["first_m"]]}))
    pd.concat(recs, ignore_index=True)[SET_COLS].to_csv(
        os.path.join(args.out_dir, "entrytime_sets.csv"), index=False)
    print(json.dumps({"checks": chk, "predictions": pred}, indent=1))


if __name__ == "__main__":
    main()
