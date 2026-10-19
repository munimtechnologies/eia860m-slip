"""entry860: where did the projects only the annual EIA-860 plans for a year stand in EIA-860M?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

baseline860 (docs/annual-flows-eia860-baseline.md) found that about a fifth of the annual
EIA-860's plan for a year is generators that January's EIA-860M plan for the year does not
hold (`annual_only`), and that they came online in the year far more often than any January
plan. This asks where those generators stood in EIA-860M. For each year Y 2017-2025 the annual
plan is rebuilt with baseline860 0.1.0 unchanged, and each annual_only generator (plant id and
generator id, trimmed, any case) gets one entry class from PUDL's EIA-860M changelog:

    in_january_not_planned        in force in January's report of Y, status not planned
    in_january_other_month        in force in January, planned for a month outside Y or undated
    in_january_planned_in_year    in force in January, planned for a month in Y (expected none:
                                  those are January's plan; check E3)
    entered_after_january         first listed in a report after January of Y
    listed_before_not_in_january  first listed before January of Y, no record in force then
    never_in_860m                 never listed in EIA-860M

and the band of its first EIA-860M record (operating; building = U, V, TS; approved = T;
early = P, L; other). The year's EIA-860M additions that were not listed in January
(eia860m_slip's new_entry, after rule R) are looked up in the year's annual plan the same way.

Checks and predictions: docs/annual-flows-eia860-entry-preregistration.md.

    python entry860.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os
import urllib.request

import numpy as np
import pandas as pd

import annual860 as an
import baseline860 as bn
import eia860m_slip as es

__version__ = "0.1.0"

ENTRY = ("in_january_not_planned", "in_january_other_month", "in_january_planned_in_year",
         "entered_after_january", "listed_before_not_in_january", "never_in_860m")
BANDS = ("operating", "building", "approved", "early", "other")
YEARS = bn.YEARS
# Check E1: annual plan and annual-only MW, all technologies, as docs/annual-flows-eia860-baseline.md
# states them.
PUBLISHED = {2017: (26808.6, 5627.2), 2018: (37113.4, 6779.5), 2019: (27422.9, 5229.2),
             2020: (45840.9, 10329.7), 2021: (45495.2, 8195.4), 2022: (44620.7, 9757.1),
             2023: (52775.4, 11913.6), 2024: (64633.7, 16444.9), 2025: (65101.5, 12503.2)}
NEW_ENTRY_2017 = 4626.7  # check E4: 2017 additions not listed in January, docs/annual-flows.md
TOP = 15
ROW_COLS = ["year", "group", "baseline_mw", "annual_only_mw"] + list(ENTRY) + ["after_share"]
BAND_COLS = (["year", "group", "entered_after_january"] + ["after_" + b for b in BANDS]
             + ["after_op_or_building_share", "after_in_year_share"])
NEW_COLS = ["year", "group", "new_entry_mw", "new_entry_in_annual_plan_mw",
            "new_entry_in_annual_plan_share"]
LIST_COLS = ["key", "plant", "group", "mw", "entry", "first_listed", "first_band", "cls",
             "online_860"]
NEW_LIST = ["key", "group", "mw"]


def band(status):
    """The band of an EIA-860M status code."""
    if status in es.OPERATING:
        return "operating"
    b = es.STAGE_BANDS.get(status)
    return b if b in BANDS else "other"


def entries(df):
    """Per generator key (trimmed, any case): the first report month that lists it and the status
    in that record, from the earliest record of any EIA-860M key with that normal form."""
    f = df.sort_values(["report_m", "key"], kind="mergesort").groupby("key", sort=False).head(1)
    f = f.assign(nkey=[an.plan_key(k) for k in f["key"]])
    f = f[f["nkey"].notna()].sort_values(["report_m", "key"], kind="mergesort")
    f = f.drop_duplicates("nkey")
    return pd.DataFrame({"first_m": f["report_m"].to_numpy(dtype=float),
                         "first_status": f["status"].to_numpy()}, index=f["nkey"].to_numpy())


def january(df, year):
    """January's report of `year`: per generator key (trimmed, any case), the status and planned
    month of the record in force."""
    s = es.snapshot(df, year * 12)
    s = s.assign(nkey=[an.plan_key(k) for k in s["key"]])
    s = s[s["nkey"].notna()].sort_values("key", kind="mergesort").drop_duplicates("nkey")
    return pd.DataFrame({"status": s["status"].to_numpy(),
                         "planned_m": s["planned_m"].to_numpy(dtype=float)},
                        index=s["nkey"].to_numpy())


def entry_class(year, key, jan, first):
    lo, hi = year * 12, year * 12 + 11
    if key in jan.index:
        status, planned = jan.at[key, "status"], jan.at[key, "planned_m"]
        if status not in es.PLANNED:
            return "in_january_not_planned"
        return "in_january_planned_in_year" if lo <= planned <= hi else "in_january_other_month"
    if key not in first.index:
        return "never_in_860m"
    if first.at[key, "first_m"] > lo:
        return "entered_after_january"
    return "listed_before_not_in_january"


def classify(b, year, jan, first, op_first):
    """The annual_only rows of one year's annual side (baseline860.mark) with their entry class,
    first EIA-860M listing (month and band) and annual operating month."""
    f = b[b["overlap"] == "annual_only"].copy().reset_index(drop=True)
    seen = [k in first.index for k in f["key"]]
    f["entry"] = [entry_class(year, k, jan, first) for k in f["key"]]
    f["first_m"] = [float(first.at[k, "first_m"]) if s else np.nan for k, s in zip(f["key"], seen)]
    f["first_listed"] = [es.month_str(m) for m in f["first_m"]]
    f["first_band"] = [band(first.at[k, "first_status"]) if s else None
                       for k, s in zip(f["key"], seen)]
    f["online_860"] = [es.month_str(op_first.get(k, np.nan)) for k in f["key"]]
    return f


def _sum(f, mask=None):
    return float(f["mw"].sum() if mask is None else f.loc[mask, "mw"].sum())


def _share(num, den):
    return round(num / den, 4) if den > 0 else None


def _row(label, b, f, new, akeys):
    """One summary row: the annual plan (b), its annual_only part by entry class (f), and the
    year's EIA-860M new entries (new) looked up in the year's annual plan (akeys)."""
    mw = _sum(f)
    row = dict(label, baseline_mw=round(_sum(b), 1), annual_only_mw=round(mw, 1))
    parts = {c: _sum(f, f["entry"] == c) for c in ENTRY}
    row.update({c: round(v, 1) for c, v in parts.items()})
    a_mw = parts["entered_after_january"]
    row["after_share"] = _share(a_mw, mw)
    after = f[f["entry"] == "entered_after_january"]
    for x in BANDS:
        row["after_" + x] = round(_sum(after, after["first_band"] == x), 1)
    row["after_op_or_building_share"] = _share(
        _sum(after, after["first_band"].isin(["operating", "building"])), a_mw)
    row["after_in_year_share"] = _share(_sum(after, after["cls"] == "in_year"), a_mw)
    inside = new["nkey"].isin(akeys)
    row["new_entry_mw"] = round(_sum(new), 1)
    row["new_entry_in_annual_plan_mw"] = round(_sum(new, inside), 1)
    row["new_entry_in_annual_plan_share"] = _share(_sum(new, inside), _sum(new))
    row["adds_up"] = abs(sum(parts.values()) - mw) < 0.05
    return row


def _pick(f, grp):
    return f if grp == "all" else f[f["group"] == grp]


def summarize(bases, classified, news):
    """One row per year and group ('all' and each group of the annual plan or the new entries)."""
    rows = []
    for year in sorted(classified):
        b, f, new = bases[year], classified[year], news[year]
        akeys = set(b["key"])
        for grp in ["all"] + sorted(set(b["group"]) | set(new["group"])):
            rows.append(_row({"year": int(year), "group": grp}, _pick(b, grp), _pick(f, grp),
                             _pick(new, grp), akeys))
    return rows


def entry_timing(f, year):
    """MW that entered after January, by the quarter of its first report (Q1 is February and
    March) or after the year."""
    a = f[f["entry"] == "entered_after_january"]
    out = {"%d-Q%d" % (year, i): 0.0 for i in range(1, 5)}
    out["after_%d" % year] = 0.0
    for m, mw in zip(a["first_m"], a["mw"]):
        label = ("%d-Q%d" % (year, int(m - year * 12) // 3 + 1) if m <= year * 12 + 11
                 else "after_%d" % year)
        out[label] += float(mw)
    return {k: round(v, 1) for k, v in out.items()}


def checks(rows, missing_cols):
    r = {(x["year"], x["group"]): x for x in rows}
    got = {y: ([r[(y, "all")]["baseline_mw"], r[(y, "all")]["annual_only_mw"]]
               if (y, "all") in r else None) for y in PUBLISHED}
    e1 = not missing_cols and all(
        got[y] is not None and abs(got[y][0] - v[0]) <= 0.1 and abs(got[y][1] - v[1]) <= 0.1
        for y, v in PUBLISHED.items())
    bad = sum(not x["adds_up"] for x in rows)
    stray = {y: r[(y, "all")]["in_january_planned_in_year"] for y in YEARS if (y, "all") in r}
    e3 = len(stray) == len(YEARS) and all(v <= 0.05 for v in stray.values())
    n17 = r[(2017, "all")]["new_entry_mw"] if (2017, "all") in r else None
    e4 = n17 is not None and abs(n17 - NEW_ENTRY_2017) <= 0.1
    return {"E1": {"missing_columns": list(missing_cols), "got": got,
                   "expected": {y: list(v) for y, v in PUBLISHED.items()}, "pass": e1},
            "E2": {"rows": len(rows), "not_adding_up": bad, "pass": bad == 0},
            "E3": {"in_january_planned_in_year_mw": stray, "pass": e3},
            "E4": {"new_entry_2017_mw": n17, "expected": NEW_ENTRY_2017, "pass": e4},
            "all_pass": bool(e1 and bad == 0 and e3 and e4)}


def _ratio(num, den):
    return num / den if den > 0 else None


def _r4(x):
    return None if x is None else round(x, 4)


def predictions(rows):
    """A1-A4. Shares are compared with their thresholds unrounded (from the rows' MW) and
    rounded only for display."""
    r = {(x["year"], x["group"]): x for x in rows}
    a = r.get((2017, "all"))
    out = {}
    s = None if a is None else _ratio(a["entered_after_january"], a["annual_only_mw"])
    out["A1"] = {"after_share": _r4(s), "floor": 0.60, "held": None if s is None else s >= 0.60}
    s = None if a is None else _ratio(a["after_operating"] + a["after_building"],
                                      a["entered_after_january"])
    out["A2"] = {"op_or_building_share": _r4(s), "floor": 0.80,
                 "held": None if s is None else s >= 0.80}
    years, half = [], []
    for y in range(2017, 2025):
        x = r.get((y, "all"))
        s = None if x is None else _ratio(x["entered_after_january"], x["annual_only_mw"])
        if s is None:
            continue
        years.append(y)
        if s >= 0.50:
            half.append(y)
    out["A3"] = {"years": years, "years_after_share_at_least_half": half, "min": 6,
                 "held": None if len(years) < 8 else len(half) >= 6}
    s = None if a is None else _ratio(a["new_entry_in_annual_plan_mw"], a["new_entry_mw"])
    out["A4"] = {"new_entry_in_annual_plan_share": _r4(s), "floor": 0.50,
                 "held": None if s is None else s >= 0.50}
    return out


def write_md(path, meta, rows, chk, pred, timing, lists):
    md = ["# Where the annual EIA-860's plan-only projects stood in EIA-860M", "",
          "entry860 %s on baseline860 %s, annual860 %s and eia860m-slip %s; annual data %s "
          "(report years %s-%s). MV2 of Munim, Inc. (made with AI agents)." % (
              __version__, meta["baseline860"], meta["annual860"], meta["eia860m_slip"],
              meta["annual_source"], meta["annual_report_years"][0],
              meta["annual_report_years"][-1]), "",
          "annual_only: generators in the annual EIA-860's plan for Y (report year Y - 1, planned "
          "for a month in Y) that January's EIA-860M plan for Y does not hold, as in "
          "docs/annual-flows-eia860-baseline.md. Entry classes are read from the EIA-860M "
          "changelog (January = the report for January of Y). after_share: "
          "entered_after_january / annual_only. Bands are of the first EIA-860M record "
          "(building = U, V, TS). new_entry: the year's EIA-860M additions not listed in "
          "January (eia860m_slip 0.3.1, rule R applied); in_annual_plan: in the year's annual "
          "plan, any group.", "",
          "Annual records by data_maturity before EIA-860M rows were left out: %s; kept %d." % (
              json.dumps(meta["annual_maturity_counts"]), meta["annual_rows_kept"]), ""]
    shown = [x for x in rows if x["group"] in an.SHOWN_GROUPS]
    md += ["## Every year: the annual-only part by entry class (MW)", ""]
    md += es.table(shown, ROW_COLS) + [""]
    md += ["## Every year: what entered after January, by its first band (MW)", ""]
    md += es.table(shown, BAND_COLS) + [""]
    md += ["## Every year: EIA-860M new entries found in the annual plan (MW)", ""]
    md += es.table(shown, NEW_COLS) + [""]
    md += ["## 2017: entered after January, by quarter of first report (MW)", "", "```",
           json.dumps(timing, indent=1), "```", ""]
    for grp in ("wind_onshore", "all"):
        md += ["## 2017, %s: largest annual-only generators" % grp, ""]
        md += es.table(lists[grp]["annual_only"], LIST_COLS) + [""]
        md += ["## 2017, %s: largest new entries not in the annual plan" % grp, ""]
        md += es.table(lists[grp]["new_not_in_annual"], NEW_LIST) + [""]
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
    first = entries(df)
    classified = {y: classify(bases[y], y, january(df, y), first, op_first) for y in YEARS}
    news = {y: built[built["year"] == y] for y in YEARS}
    rows = summarize(bases, classified, news)
    chk = checks(rows, missing)
    pred = predictions(rows)
    timing = {g: entry_timing(_pick(classified[2017], g), 2017) for g in ("all", "wind_onshore")}
    lists = {}
    for grp in ("wind_onshore", "all"):
        f, n = _pick(classified[2017], grp), _pick(news[2017], grp)
        lists[grp] = {"annual_only": bn.top(f, LIST_COLS),
                      "new_not_in_annual": bn.top(n[~n["nkey"].isin(set(bases[2017]["key"]))],
                                                  NEW_LIST)}
    meta = {"version": __version__, "baseline860": bn.__version__, "annual860": an.__version__,
            "eia860m_slip": es.__version__, "source": os.path.basename(path),
            "report_max": es.month_str(df["report_m"].max()),
            "annual_source": os.path.basename(args.annual),
            "annual_bytes": os.path.getsize(args.annual),
            "annual_maturity_counts": maturity, "annual_rows_kept": int(len(a)),
            "annual_report_years": report_years}
    with open(os.path.join(args.out_dir, "entry860.json"), "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "checks": chk, "predictions": pred, "rows": rows,
                   "timing_2017": timing, "lists_2017": lists}, fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "entry860.md"), meta, rows, chk, pred, timing, lists)
    pd.concat([classified[y] for y in YEARS], ignore_index=True).to_csv(
        os.path.join(args.out_dir, "annual_only_entry.csv"), index=False)
    print(json.dumps({"checks": chk, "predictions": pred}, indent=1))


if __name__ == "__main__":
    main()
