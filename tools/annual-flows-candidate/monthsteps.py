"""monthsteps: are EIA-860M stage moves bunched in the report months around the annual survey?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

stagemoves 0.1.0 counts how planned generators move between stages from one EIA-860M report to
the next. This reads the same steps by the calendar month of the report in which the move shows
(report m + 1). The annual EIA-860 asks for each generator's status at the end of the year and
is due between January and the end of February; if annual filings and year-end reviews correct
stale monthly statuses, moves should be more frequent in the reports for December to March (the
window) than in the other eight months. Steps are pooled for m in 2016-2025, as in stagemoves, so
each calendar month is ten reports. Rates count generators (one per step) and are compared
inside and outside the window; the same rates in MW are reported too.

    kind               starting bands        moves counted
    backward           approved, building    backward
    backward_building  building              backward
    forward            early, approved       forward
    exit_other         all three             exit_other
    to_operating       all three             to_operating

Checks and predictions: docs/report-months-preregistration.md.

    python monthsteps.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860m_slip as es
import stagemoves as sm

__version__ = "0.1.0"

WINDOW = (12, 1, 2, 3)            # report months around the annual EIA-860 (due January-February)
YEARS = tuple(range(2016, 2026))  # W3: years of m
REPORTS = 10                      # check C2: reports per calendar month, m in 2016-2025
KINDS = {"backward": (("approved", "building"), ("backward",)),
         "backward_building": (("building",), ("backward",)),
         "forward": (("early", "approved"), ("forward",)),
         "exit_other": (sm.BANDS, ("exit_other",)),
         "to_operating": (sm.BANDS, ("to_operating",))}
MONTH_COLS = (["month", "window", "reports", "steps", "step_mw"]
              + [k + x for k in KINDS for x in ("_n", "_rate")])
CMP_COLS = ["kind", "in_n", "in_steps", "in_rate", "out_n", "out_steps", "out_rate", "ratio",
            "in_mw_rate", "out_mw_rate", "mw_ratio"]
YEAR_COLS = ["year", "in_rate", "out_rate", "higher"]


def report_month(m):
    """Calendar month (1-12) of report m + 1, the report in which a step's move shows."""
    return (m + 1) % 12 + 1


def pooled_steps(s):
    """Steps with m in 2016-2025, with the calendar month of report m + 1."""
    p = s[s["m"] <= sm.POOL_END].copy()
    p["month"] = report_month(p["m"])
    return p


def _count(f, kind):
    """(moves, eligible steps, MW of moves, MW of eligible steps) of one kind in f."""
    bands, mvs = KINDS[kind]
    e = f[f["band"].isin(list(bands))]
    hit = e["move"].isin(list(mvs))
    return int(hit.sum()), int(len(e)), float(e.loc[hit, "mw"].sum()), float(e["mw"].sum())


def _div(a, b):
    return None if a is None or b is None or b == 0 else a / b


def rates(p, kind):
    """Unrounded rates inside and outside the window: (in, out, in MW, out MW)."""
    inside = p["month"].isin(list(WINDOW))
    a, b = _count(p[inside], kind), _count(p[~inside], kind)
    return (sm._ratio(a[0], a[1]), sm._ratio(b[0], b[1]),
            sm._ratio(a[2], a[3]), sm._ratio(b[2], b[3]))


def by_month(p):
    """One row per calendar month of report m + 1: reports, steps, and each kind's count, rate
    (moves / eligible steps) and MW."""
    rows = []
    for mo in range(1, 13):
        f = p[p["month"] == mo]
        row = {"month": mo, "window": "yes" if mo in WINDOW else "no",
               "reports": int(f["m"].nunique()), "steps": int(len(f)),
               "step_mw": round(sm._mw(f), 1)}
        for k in KINDS:
            n, d, mw, _ = _count(f, k)
            row[k + "_n"] = n
            row[k + "_rate"] = sm._share(n, d)
            row[k + "_mw"] = round(mw, 1)
        rows.append(row)
    return rows


def compare(p):
    """One row per kind: counts and rates inside and outside the window, and their ratios."""
    inside = p["month"].isin(list(WINDOW))
    rows = []
    for k in KINDS:
        a, b = _count(p[inside], k), _count(p[~inside], k)
        ri, ro, mi, mo = rates(p, k)
        rows.append({"kind": k, "in_n": a[0], "in_steps": a[1], "in_rate": sm._r4(ri),
                     "out_n": b[0], "out_steps": b[1], "out_rate": sm._r4(ro),
                     "ratio": sm._r4(_div(ri, ro)), "in_mw_rate": sm._r4(mi),
                     "out_mw_rate": sm._r4(mo), "mw_ratio": sm._r4(_div(mi, mo))})
    return rows


def per_year(p, kind):
    """For each year of m in YEARS: the kind's rate inside and outside the window, and whether
    the inside rate is higher (False when either rate is missing)."""
    rows = []
    for y in YEARS:
        ri, ro = rates(p[p["year"] == y], kind)[:2]
        rows.append({"year": y, "in_rate": sm._r4(ri), "out_rate": sm._r4(ro),
                     "higher": bool(ri is not None and ro is not None and ri > ro)})
    return rows


def checks(rows, pooled_rows, base):
    """C1: the months add up to stagemoves' pooled table (steps exactly, MW to 1.0, because each
    month's MW is rounded to 0.1); C2: every calendar month has REPORTS reports; C3: stagemoves'
    checks S1-S4."""
    n, mw = sum(r["steps"] for r in rows), sum(r["step_mw"] for r in rows)
    pn, pmw = sum(r["steps"] for r in pooled_rows), sum(r["step_mw"] for r in pooled_rows)
    b = {r["band"]: r for r in pooled_rows}["building"]
    back, pback = sum(r["backward_building_mw"] for r in rows), b["early_mw"] + b["approved_mw"]
    c1 = bool(n == pn and abs(mw - pmw) <= 1.0 and abs(back - pback) <= 1.0)
    short = [r["month"] for r in rows if r["reports"] != REPORTS]
    out = {"C1": {"steps": n, "pooled_steps": pn, "step_mw": round(mw, 1),
                  "pooled_step_mw": round(pmw, 1), "backward_building_mw": round(back, 1),
                  "pooled_backward_building_mw": round(pback, 1), "pass": c1},
           "C2": {"months_without_%d_reports" % REPORTS: short, "pass": not short},
           "C3": {"stagemoves_all_pass": bool(base["all_pass"]), "pass": bool(base["all_pass"])}}
    out["all_pass"] = bool(out["C1"]["pass"] and out["C2"]["pass"] and out["C3"]["pass"])
    return out


def predictions(p, years):
    """W1-W4 on generator counts. Ratios are compared with their floors unrounded."""
    out = {}
    for name, k, floor in (("W1", "backward", 1.5), ("W2", "forward", 1.25)):
        ri, ro = rates(p, k)[:2]
        q = _div(ri, ro)
        out[name] = {"kind": k, "ratio": sm._r4(q), "floor": floor,
                     "held": None if q is None else q >= floor}
    hi = sum(1 for x in years if x["higher"])
    out["W3"] = {"kind": "backward", "years_higher": hi, "years": len(years), "floor": 7,
                 "held": hi >= 7}
    ri, ro = rates(p, "exit_other")[:2]
    q = _div(ri, ro)
    out["W4"] = {"kind": "exit_other", "ratio": sm._r4(q), "floor": 1.5,
                 "held": None if q is None else q >= 1.5}
    return out


def write_md(path, meta, res):
    md = ["# EIA-860M stage moves by report month", "",
          "monthsteps %s on stagemoves %s and eia860m-slip %s; data %s (reports %s to %s). "
          "MV2 of Munim, Inc. (made with AI agents)." % (
              meta["version"], meta["stagemoves"], meta["eia860m_slip"], meta["source"],
              meta["first_step"], meta["report_max"]), "",
          "Steps as in stagemoves, m in 2016-2025, by the calendar month of report m + 1. "
          "Window: reports for months %s. Rates: moves / eligible steps (generator counts); "
          "ratio: inside rate / outside rate." % ", ".join(str(x) for x in WINDOW), ""]
    md += ["## Inside and outside the window", ""]
    md += es.table(res["compare"], CMP_COLS) + [""]
    md += ["## By calendar month of report m + 1", ""]
    md += es.table(res["months"], MONTH_COLS) + [""]
    md += ["## Backward rate inside and outside the window, by year of m (W3)", ""]
    md += es.table(res["years"], YEAR_COLS) + [""]
    md += ["## Checks", "", "```", json.dumps(res["checks"], indent=1), "```", "",
           "## Predictions", "", "```", json.dumps(res["predictions"], indent=1), "```", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    links = es.annual_flows(df)[0]["links"]
    df = sm.rekeyed(df, links)
    last_m = int(df["report_m"].max())
    t = sm.timeline(df, sm.START_M, last_m)
    s, left = sm.steps(t, last_m)
    mrows = []
    for y in sorted(set(s["year"])):
        mrows += sm.matrix(s[s["year"] == y], left[left["year"] == y], {"year": int(y)})
    base = sm.checks(t, sm.sample_check(df, s, sm.SAMPLE), mrows, links, sm.START_M, last_m)
    p = pooled_steps(s)
    months = by_month(p)
    years = per_year(p, "backward")
    res = {"compare": compare(p), "months": months, "years": years,
           "checks": checks(months, sm.pooled(s, left), base),
           "predictions": predictions(p, years)}
    meta = {"version": __version__, "stagemoves": sm.__version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "first_step": es.month_str(sm.START_M),
            "report_max": es.month_str(last_m), "pooled_steps": int(len(p)),
            "window": list(WINDOW), "stagemoves_checks": base}
    with open(os.path.join(args.out_dir, "monthsteps.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "monthsteps.md"), meta, res)
    print(json.dumps({"checks": res["checks"], "predictions": res["predictions"]}, indent=1,
                     default=str))


if __name__ == "__main__":
    main()
