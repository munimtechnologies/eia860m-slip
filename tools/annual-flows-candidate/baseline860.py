"""baseline860: the annual EIA-860's own plan for each year against January's EIA-860M plan.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

annual860.py (docs/annual-flows-eia860.md) kept January's EIA-860M plan fixed and changed only
the outcome; the annual operating dates did not raise the 2017 share. This tests the other
explanation its pre-registration named, the baseline. For each year Y 2017-2025 the annual plan
is every generator that the annual EIA-860 for Y - 1 (PUDL's out_eia__yearly_generators, EIA-860M
rows left out by data_maturity as in annual860 0.1.1) lists with an EIA-860M planned status code
and a current planned operating month in Y. Each gets annual860's annual class (from the earliest
operating date in an annual record that lists it as operating) and is marked `both` if January's
EIA-860M plan for Y (eia860m_slip 0.3.1's annual flows, rule R included) has the same key, else
`annual_only`; plan generators missing from the annual plan are `m_only`. Keys are plant id and
generator id, trimmed, any case.

Checks and predictions: docs/annual-flows-eia860-baseline-preregistration.md.

    python baseline860.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os
import urllib.request

import numpy as np
import pandas as pd

import annual860 as an
import eia860m_slip as es

__version__ = "0.1.0"

COLS = an.COLS_860 + ("current_planned_generator_operating_date", "technology_description",
                      "plant_name_eia")
YEARS = tuple(range(2017, 2026))
# Check D2: January's 2017 EIA-860M plan as docs/annual-flows.md states it.
PLAN_2017 = {"all": 26268.8, "wind_onshore": 6858.3}
BASELINE_2017 = (10000.0, 50000.0)  # check D4: a plausible size, not EIA's figure
EIA_2017_MW = 25100.0  # Today in Energy, 21 June 2018; prediction B1 only
TOP = 15
OVERLAP_COLS = ["year", "group", "baseline_mw", "share_in_year", "both_mw", "both_share_in_year",
                "annual_only_mw", "annual_only_share_in_year", "plan_860m_mw", "share_860m",
                "m_only_mw", "m_only_share_860m"]
ANNUAL_LIST = ["key", "plant", "group", "mw", "cls"]
M_LIST = ["key", "plant", "group", "mw", "state", "cls"]


def baseline(a, year):
    """The annual EIA-860's plan for `year`: one row per key (key, group, mw, plant) for each
    generator the report for year - 1 lists with an EIA-860M planned status code and a current
    planned operating month in the year."""
    rep = pd.to_datetime(a["report_date"], errors="coerce").dt.year.to_numpy()
    status = a["operational_status_code"].astype(str).str.strip().str.upper()
    planned = es.months(a["current_planned_generator_operating_date"])
    keep = ((rep == year - 1) & status.isin(es.PLANNED).to_numpy()
            & (planned >= year * 12) & (planned <= year * 12 + 11))
    f = a[keep]
    out = pd.DataFrame({
        "key": [an.norm_key(p, g) for p, g in zip(f["plant_id_eia"], f["generator_id"])],
        "group": [es.tech_group(x) for x in f["technology_description"]],
        "mw": pd.to_numeric(f["capacity_mw"], errors="coerce").fillna(0.0).to_numpy(dtype=float),
        "plant": [x if isinstance(x, str) else "" for x in f["plant_name_eia"]]})
    out = out[out["key"].notna()]
    return out.drop_duplicates("key").reset_index(drop=True)


def mark(base, plan, year, first, listed):
    """(annual side, EIA-860M side) for one year. The annual side is `base` with its annual class
    and overlap (both, annual_only); the EIA-860M side is January's plan for the year (key, group,
    mw, state, cls, plant) with its overlap (both, m_only). A plan generator re-keyed by rule R
    is in the annual plan if either of its keys is."""
    p = plan[plan["year"] == year]
    pkeys = {an.plan_key(k) for k in list(p["key"]) + list(p["lookup_key"])} - {None}
    b = base.copy()
    b["year"] = year
    b["cls"] = [an.annual_class(year, k, first, listed) for k in b["key"]]
    b["overlap"] = ["both" if k in pkeys else "annual_only" for k in b["key"]]
    bkeys = set(b["key"])
    m = p[["year", "key", "group", "mw", "state", "cls", "plant"]].copy().reset_index(drop=True)
    m["overlap"] = ["both" if an.plan_key(k) in bkeys or an.plan_key(lk) in bkeys else "m_only"
                    for k, lk in zip(p["key"], p["lookup_key"])]
    return b, m


def _sum(f, mask=None):
    return float(f["mw"].sum() if mask is None else f.loc[mask, "mw"].sum())


def _share(num, den):
    return round(num / den, 4) if den > 0 else None


def _row(label, b, m):
    bm, mm = _sum(b), _sum(m)
    parts = {c: _sum(b, b["cls"] == c) for c in an.CLASSES}
    row = dict(label, baseline_mw=round(bm, 1))
    row.update({c: round(v, 1) for c, v in parts.items()})
    row["share_in_year"] = _share(parts["in_year"], bm)
    for o in ("both", "annual_only"):
        s = b[b["overlap"] == o]
        row[o + "_mw"] = round(_sum(s), 1)
        row[o + "_share_in_year"] = _share(_sum(s, s["cls"] == "in_year"), _sum(s))
    delivered = _sum(m, m["state"].isin(an.DELIVERED))
    s = m[m["overlap"] == "m_only"]
    row["plan_860m_mw"] = round(mm, 1)
    row["delivered_860m_mw"] = round(delivered, 1)
    row["share_860m"] = _share(delivered, mm)
    row["m_only_mw"] = round(_sum(s), 1)
    row["m_only_share_860m"] = _share(_sum(s, s["state"].isin(an.DELIVERED)), _sum(s))
    row["adds_up"] = abs(sum(parts.values()) - bm) < 0.05
    return row


def summarize(sides):
    """One row per year and group ('all' and each group on either side)."""
    rows = []
    for year in sorted(sides):
        b, m = sides[year]
        for grp in ["all"] + sorted(set(b["group"]) | set(m["group"])):
            bg = b if grp == "all" else b[b["group"] == grp]
            mg = m if grp == "all" else m[m["group"] == grp]
            rows.append(_row({"year": int(year), "group": grp}, bg, mg))
    return rows


def checks(rows, missing_cols, report_years):
    r = {(x["year"], x["group"]): x for x in rows}
    got = {g: (r[(2017, g)]["plan_860m_mw"] if (2017, g) in r else None) for g in PLAN_2017}
    lacking = [y for y in range(min(YEARS) - 1, max(YEARS)) if y not in report_years]
    d1 = not missing_cols and not lacking
    d2 = all(got[g] is not None and abs(got[g] - v) <= 0.1 for g, v in PLAN_2017.items())
    bad = sum(not x["adds_up"] for x in rows)
    b17 = r[(2017, "all")]["baseline_mw"] if (2017, "all") in r else None
    lo, hi = BASELINE_2017
    d4 = b17 is not None and lo <= b17 <= hi
    return {"D1": {"missing_columns": list(missing_cols), "missing_report_years": lacking,
                   "pass": d1},
            "D2": {"got": got, "pass": d2},
            "D3": {"rows": len(rows), "not_adding_up": bad, "pass": bad == 0},
            "D4": {"baseline_2017_mw": b17, "range": list(BASELINE_2017), "pass": d4},
            "all_pass": bool(d1 and d2 and bad == 0 and d4)}


def _ratio(num, den):
    return num / den if den > 0 else None


def predictions(rows):
    """B1-B5. Shares are compared with their thresholds unrounded (from the rows' MW) and
    rounded only for display."""
    r = {(x["year"], x["group"]): x for x in rows}
    a, w = r.get((2017, "all")), r.get((2017, "wind_onshore"))
    out = {}
    off = None if a is None or not a["baseline_mw"] > 0 else \
        abs(a["baseline_mw"] - EIA_2017_MW) / EIA_2017_MW
    out["B1"] = {"baseline_mw": None if a is None else a["baseline_mw"], "eia_mw": EIA_2017_MW,
                 "off": None if off is None else round(off, 4), "max": 0.10,
                 "held": None if off is None else off <= 0.10}
    for name, x, floor in (("B2", a, 0.75), ("B3", w, 0.80)):
        s = None if x is None else _ratio(x["in_year"], x["baseline_mw"])
        out[name] = {"share_in_year": None if s is None else round(s, 4), "floor": floor,
                     "held": None if s is None else s >= floor}
    s = None if w is None else _ratio(w["both_mw"], w["baseline_mw"])
    out["B4"] = {"both_share": None if s is None else round(s, 4), "max": 0.80,
                 "held": None if s is None else s <= 0.80}
    years, above = [], []
    for y in range(2017, 2025):
        x = r.get((y, "all"))
        sa = None if x is None else _ratio(x["in_year"], x["baseline_mw"])
        sm = None if x is None else _ratio(x["delivered_860m_mw"], x["plan_860m_mw"])
        if sa is None or sm is None:
            continue
        years.append(y)
        if sa > sm:
            above.append(y)
    out["B5"] = {"years": years, "years_annual_above_860m": above, "min": 6,
                 "held": None if len(years) < 8 else len(above) >= 6}
    return out


def top(f, cols, n=TOP):
    """The n largest rows by MW (then key), with only `cols`, as plain values."""
    f = f.sort_values(["mw", "key"], ascending=[False, True], kind="mergesort").head(n)
    return [{c: (round(float(v), 1) if c == "mw" else es._text(v)) for c, v in zip(cols, rec)}
            for rec in f[cols].itertuples(index=False)]


def write_md(path, meta, rows, chk, pred, lists):
    md = ["# The annual EIA-860's own plan against January's EIA-860M plan", "",
          "baseline860 %s on eia860m-slip %s annual flows and annual860 %s; annual data %s "
          "(report years %s-%s). MV2 of Munim, Inc. (made with AI agents)." % (
              __version__, meta["eia860m_slip"], meta["annual860"], meta["annual_source"],
              meta["annual_report_years"][0], meta["annual_report_years"][-1]), "",
          "Annual plan for year Y: generators the annual EIA-860 for Y - 1 lists as planned "
          "(P, L, T, U, V, TS, OT) with a current planned operating month in Y. share_in_year: "
          "MW whose annual operating month is in Y / annual plan. both: also in January's "
          "EIA-860M plan for Y (same key). share_860m: (online_in_year + rekeyed_online) / "
          "January's EIA-860M plan, as in docs/annual-flows.md.", "",
          "Annual records by data_maturity before EIA-860M rows were left out: %s; kept %d." % (
              json.dumps(meta["annual_maturity_counts"]), meta["annual_rows_kept"]), ""]
    shown = [x for x in rows if x["group"] in an.SHOWN_GROUPS]
    md += ["## Every year: the two plans and their overlap (MW)", ""]
    md += es.table(shown, OVERLAP_COLS) + [""]
    md += ["## Every year: the annual plan by annual class (MW)", ""]
    md += es.table(shown, ["year", "group", "baseline_mw"] + list(an.CLASSES)) + [""]
    for grp in ("wind_onshore", "all"):
        md += ["## 2017, %s: largest in the annual plan only" % grp, ""]
        md += es.table(lists[grp]["annual_only"], ANNUAL_LIST) + [""]
        md += ["## 2017, %s: largest in January's EIA-860M plan only" % grp, ""]
        md += es.table(lists[grp]["m_only"], M_LIST) + [""]
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
    missing = [c for c in COLS if c not in a_names]
    a = pd.read_parquet(args.annual, columns=[c for c in COLS + an.OPTIONAL_860 if c in a_names])
    for c in missing:
        a[c] = np.nan
    a, maturity = an.annual_only(a)
    report_years = sorted({int(y) for y in
                           pd.to_datetime(a["report_date"], errors="coerce").dt.year.dropna()})
    plan = an._plan_rows(df, a)
    first, listed = an.annual_first(a)
    sides = {y: mark(baseline(a, y), plan, y, first, listed) for y in YEARS}
    rows = summarize(sides)
    chk = checks(rows, missing, report_years)
    pred = predictions(rows)
    b17, m17 = sides[2017]
    lists = {}
    for grp in ("wind_onshore", "all"):
        bg = b17 if grp == "all" else b17[b17["group"] == grp]
        mg = m17 if grp == "all" else m17[m17["group"] == grp]
        lists[grp] = {"annual_only": top(bg[bg["overlap"] == "annual_only"], ANNUAL_LIST),
                      "m_only": top(mg[mg["overlap"] == "m_only"], M_LIST)}
    meta = {"version": __version__, "eia860m_slip": es.__version__, "annual860": an.__version__,
            "source": os.path.basename(path), "report_max": es.month_str(df["report_m"].max()),
            "annual_source": os.path.basename(args.annual),
            "annual_bytes": os.path.getsize(args.annual),
            "annual_maturity_counts": maturity, "annual_rows_kept": int(len(a)),
            "annual_report_years": report_years, "eia_2017_mw": EIA_2017_MW}
    with open(os.path.join(args.out_dir, "baseline860.json"), "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "checks": chk, "predictions": pred, "rows": rows,
                   "lists_2017": lists}, fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "baseline860.md"), meta, rows, chk, pred, lists)
    pd.concat([sides[y][0] for y in YEARS], ignore_index=True).to_csv(
        os.path.join(args.out_dir, "baseline_860.csv"), index=False)
    pd.concat([sides[y][1] for y in YEARS], ignore_index=True).to_csv(
        os.path.join(args.out_dir, "plan_860m_overlap.csv"), index=False)
    print(json.dumps({"checks": chk, "predictions": pred}, indent=1))


if __name__ == "__main__":
    main()
