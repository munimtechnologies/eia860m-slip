"""leadtime: does lead time matter less for a generator that is already being built? Stage by
lead time in EIA-860M planned operating months.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Every EIA-860M report lists each planned generator with a status code and a planned operating
month. eia860m_slip.py scores every (generator, report) pair whose planned month is 0-12 months
ahead for whether the generator was online by that month (on time), 1-12 months after it (late)
or not within 12 months of it (not online), capacity-weighted, and reports the shares by stage
and, separately, by lead time. This tool crosses the two. It reads the same cohort rows with a
24-month horizon and gives, for each cell of stage group (early = P, L; approved = T; U; V;
also TS and OT) by lead band (0-3, 4-6, 7-12, 13-24 months), the MW and the on-time, late and
not-online shares. Rows are kept for report months from January 2016 to the last month for
which a 24-month lead has a closed outcome window (last report - 24 - 12 - 2 months), so every
band is read over the same report months.

Checks and predictions: docs/stage-leadtime-preregistration.md.

    python leadtime.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860m_slip as es

__version__ = "0.1.0"

HORIZON = 24                  # months ahead a planned month may be
START_M = 2016 * 12           # first report month: January 2016 (PUDL's capacities start then)
BANDS = (("00-03", 0, 3), ("04-06", 4, 6), ("07-12", 7, 12), ("13-24", 13, 24))
BAND_NAMES = tuple(b[0] for b in BANDS)
STAGES = {"P": "early", "L": "early", "T": "approved", "U": "U", "V": "V", "TS": "TS", "OT": "OT"}
STAGE_ORDER = ("early", "approved", "U", "V", "TS", "OT")
GRID = ("early", "approved", "U", "V")   # the stage groups the predictions are about
GROUPS = ("all", "solar", "battery", "wind_onshore", "gas_cc", "gas_ct")
MIN_GENERATORS = 20           # check C2: distinct generators in every prediction cell
SAMPLE = (2017 * 12, 2019 * 12, 2021 * 12)  # check C1: January 2017, 2019 and 2021
LATE = ("late_1_3", "late_4_6", "late_7_12")
CELL_COLS = ["stage", "band", "rows", "generators", "mw", "on_time_share", "late_share",
             "not_online_share", "on_time_count_share"]
GRID_COLS = ["group", "stage"] + list(BAND_NAMES)


def band(lead):
    """The lead band of a lead time in months, or None outside 0-24."""
    for name, lo, hi in BANDS:
        if lo <= lead <= hi:
            return name
    return None


def end_month(last_m):
    """Last report month whose 24-month lead has a closed outcome window."""
    return int(last_m) - (HORIZON + es.RESOLVE + es.LAG)


def rows(df, last_m=None):
    """eia860m_slip's cohort rows with a 24-month horizon, report months START_M..end_month,
    plus the stage group and lead band of each row."""
    if last_m is None:
        last_m = int(df["report_m"].max())
    c = es.cohorts(df, last_m, horizon=HORIZON)
    c = c[(c["report_m"] >= START_M) & (c["report_m"] <= end_month(last_m))].copy()
    c["stage_group"] = [STAGES.get(s, "OT") for s in c["status"]]
    c["band"] = [band(x) for x in c["lead"]]
    return c.reset_index(drop=True)


def _share(num, den):
    return round(num / den, 4) if den > 0 else None


def _ratio(num, den):
    return num / den if den > 0 else None


def _r4(x):
    return None if x is None else round(x, 4)


def _mw(f, mask=None):
    return float(f["mw"].sum() if mask is None else f.loc[mask, "mw"].sum())


def cell(f):
    """Rows, generators, MW and the on-time, late and not-online MW shares of some rows."""
    mw = _mw(f)
    on = _mw(f, f["outcome"] == "on_time")
    late = _mw(f, f["outcome"].isin(LATE))
    off = _mw(f, f["outcome"] == "not_online_12")
    return {"rows": int(len(f)), "generators": int(f["key"].nunique()), "mw": round(mw, 1),
            "on_time_share": _share(on, mw), "late_share": _share(late, mw),
            "not_online_share": _share(off, mw),
            "on_time_count_share": _share(float((f["outcome"] == "on_time").sum()),
                                          float(len(f))),
            "adds_up": bool(abs(on + late + off - mw) < 0.05)}


def cells(c, stages=STAGE_ORDER):
    """One row per stage group and lead band (empty cells included)."""
    out = []
    for st in stages:
        for b in BAND_NAMES:
            f = c[(c["stage_group"] == st) & (c["band"] == b)]
            out.append(dict(stage=st, band=b, **cell(f)))
    return out


def on_time(c, st, b, outcome="on_time"):
    """Unrounded MW share of an outcome in one cell, or None for an empty cell."""
    f = c[(c["stage_group"] == st) & (c["band"] == b)]
    return _ratio(_mw(f, f["outcome"] == outcome), _mw(f))


def grids(c):
    """On-time share by stage group and lead band, for all generators and by technology group."""
    out = []
    for grp in GROUPS:
        g = c if grp == "all" else c[c["group"] == grp]
        for st in GRID:
            row = {"group": grp, "stage": st}
            for b in BAND_NAMES:
                row[b] = _r4(on_time(g, st, b))
            out.append(row)
    return out


def sample_check(df, c, months, last_m):
    """Check C1: for each sample month, the rows equal an independent reading of es.snapshot:
    planned records with a planned month 0-24 months ahead and a closed outcome window."""
    out = {}
    for m in months:
        s = es.snapshot(df, m)
        s = s[s["status"].isin(list(es.PLANNED)) & s["planned_m"].notna()]
        lead = s["planned_m"] - m
        s = s[(lead >= 0) & (lead <= HORIZON) & (s["planned_m"] + es.RESOLVE + es.LAG <= last_m)]
        got = c[c["report_m"] == m]
        out[es.month_str(m)] = {"expected_mw": round(float(s["capacity_mw"].sum()), 1),
                                "expected_n": int(len(s)), "got_mw": round(_mw(got), 1),
                                "got_n": int(len(got))}
    ok = bool(out) and all(abs(v["expected_mw"] - v["got_mw"]) <= 0.1
                           and v["expected_n"] == v["got_n"] for v in out.values())
    return {"months": out, "pass": ok}


def checks(c, cell_rows, sample, last_m):
    thin = ["%s %s" % (r["stage"], r["band"]) for r in cell_rows
            if r["stage"] in GRID and r["generators"] < MIN_GENERATORS]
    bad = sum(not r["adds_up"] for r in cell_rows)
    cell_total = sum(r["rows"] for r in cell_rows)
    dup = int(c.duplicated(["key", "report_m"]).sum())
    end = end_month(last_m)
    outside = int(((c["report_m"] < START_M) | (c["report_m"] > end) | (c["lead"] < 0)
                   | (c["lead"] > HORIZON)).sum())
    c2 = not thin
    c3 = bad == 0 and cell_total == len(c)
    c4 = dup == 0 and outside == 0
    return {"C1": sample,
            "C2": {"min_generators": MIN_GENERATORS, "thin_cells": thin, "pass": c2},
            "C3": {"cells": len(cell_rows), "not_adding_up": bad, "rows": int(len(c)),
                   "cell_rows": cell_total, "pass": c3},
            "C4": {"duplicate_key_months": dup, "rows_outside_window": outside,
                   "first_month": es.month_str(START_M), "last_month": es.month_str(end),
                   "pass": c4},
            "all_pass": bool(sample["pass"] and c2 and c3 and c4)}


def _mono(seq):
    """True if every consecutive pair of the values present is non-increasing; None if fewer
    than two cells have a value."""
    v = [x for x in seq if x is not None]
    if len(v) < 2:
        return None
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1))


def _diff(a, b):
    return None if a is None or b is None else a - b


def predictions(c):
    """L1-L6. Shares are compared with their thresholds unrounded and rounded for display."""
    d = {(st, b): on_time(c, st, b) for st in GRID for b in BAND_NAMES}
    mono = {st: _mono([d[(st, b)] for b in BAND_NAMES]) for st in ("U", "V")}
    out = {"L1": {"on_time_by_band": {st: {b: _r4(d[(st, b)]) for b in BAND_NAMES}
                                      for st in ("U", "V")},
                  "non_increasing": mono,
                  "held": None if any(v is None for v in mono.values()) else all(mono.values())}}
    fv = _diff(d[("V", "00-03")], d[("V", "13-24")])
    fe = _diff(d[("early", "00-03")], d[("early", "13-24")])
    out["L2"] = {"fall_V": _r4(fv), "fall_early": _r4(fe),
                 "held": None if fv is None or fe is None else fv > fe}
    x = d[("V", "00-03")]
    out["L3"] = {"V_00_03_on_time": _r4(x), "floor": 0.45, "held": None if x is None else x >= 0.45}
    x = d[("early", "13-24")]
    out["L4"] = {"early_13_24_on_time": _r4(x), "ceiling": 0.20,
                 "held": None if x is None else x <= 0.20}
    a, b = d[("V", "07-12")], d[("early", "00-03")]
    out["L5"] = {"V_07_12_on_time": _r4(a), "early_00_03_on_time": _r4(b),
                 "held": None if a is None or b is None else a > b}
    x = on_time(c, "early", "13-24", "not_online_12")
    out["L6"] = {"early_13_24_not_online": _r4(x), "floor": 0.50,
                 "held": None if x is None else x >= 0.50}
    return out


def write_md(path, meta, res):
    md = ["# EIA-860M planned operating months: on-time share by stage and lead time", "",
          "leadtime %s on eia860m-slip %s; data %s (reports to %s; rows for report months %s to "
          "%s). MV2 of Munim, Inc. (made with AI agents)." % (
              meta["version"], meta["eia860m_slip"], meta["source"], meta["report_max"],
              meta["first_month"], meta["last_month"]), "",
          "A row: a generator listed as planned (P, L, T, U, V, TS, OT) in a report with a planned "
          "operating month 0-24 months ahead, scored once its outcome window has closed (planned "
          "month + 12 + 2 months at or before the last report): on time = online by the planned "
          "month; late = online 1-12 months after it; not online = not within 12 months of it. "
          "Shares are of MW. Stage groups: early = P, L; approved = T; U; V; TS; OT. Lead = "
          "planned month minus report month. Report months end %d months before the last "
          "report, so every lead band covers the same months." % (HORIZON + es.RESOLVE + es.LAG),
          ""]
    md += ["## On-time share by stage group and lead band (MW), all generators", ""]
    md += es.table([r for r in res["grids"] if r["group"] == "all"], GRID_COLS) + [""]
    md += ["## On-time share by stage group and lead band (MW), by technology group", ""]
    md += es.table(res["grids"], GRID_COLS) + [""]
    md += ["## Every cell", ""]
    md += es.table(res["cells"], CELL_COLS) + [""]
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
    last_m = int(df["report_m"].max())
    c = rows(df, last_m)
    cell_rows = cells(c)
    res = {"cells": cell_rows, "grids": grids(c),
           "checks": checks(c, cell_rows, sample_check(df, c, SAMPLE, last_m), last_m),
           "predictions": predictions(c)}
    meta = {"version": __version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "report_max": es.month_str(last_m),
            "first_month": es.month_str(START_M), "last_month": es.month_str(end_month(last_m)),
            "horizon": HORIZON, "rows": int(len(c)), "generators": int(c["key"].nunique()),
            "mw": round(_mw(c), 1)}
    with open(os.path.join(args.out_dir, "leadtime.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "leadtime.md"), meta, res)
    pd.DataFrame(cell_rows).to_csv(os.path.join(args.out_dir, "leadtime_cells.csv"), index=False)
    c.to_csv(os.path.join(args.out_dir, "leadtime_rows.csv.gz"), index=False, compression="gzip")
    print(json.dumps({"meta": meta, "checks": res["checks"], "predictions": res["predictions"]},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
