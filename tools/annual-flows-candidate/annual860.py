"""annual860: January's EIA-860M plan against the operating dates of the annual EIA-860.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

For each closed year, every generator in the January EIA-860M plan (eia860m_slip 0.3.1's
annual flows, unchanged, rule R included) is looked up by plant id and generator id
(trimmed, any case) in PUDL's out_eia__yearly_generators, the annual EIA-860 with each
generator's harvested generator_operating_date. Records PUDL took from EIA-860M (data_maturity
incremental_ytd or monthly_update) are left out. Its annual operating month is the earliest
generator_operating_date in an annual record that lists it as operating (OP, SB, OS, OA).
A generator re-keyed by rule R is looked up under its new key. Each plan generator gets one
annual class:

    before / in_year / next_year / later   annual operating month before, in, the year after,
                                           or later than the plan year
    undated      listed as operating in the annual data, never with an operating date
    never        in the annual data, never listed as operating
    not_in_860   no annual record under its key

Checks and predictions: docs/annual-flows-eia860-preregistration.md and its amendment 1
(docs/annual-flows-eia860-amendment-1.md: 0.1.0 read core_eia860__scd_generators, which has
no operating date).

    python annual860.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os
import urllib.request

import numpy as np
import pandas as pd

import eia860m_slip as es

__version__ = "0.1.1"

URL_860 = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
           "out_eia__yearly_generators.parquet")
COLS_860 = ("plant_id_eia", "generator_id", "report_date", "operational_status_code",
            "generator_operating_date", "capacity_mw")
OPTIONAL_860 = ("data_maturity",)
NOT_ANNUAL = frozenset({"incremental_ytd", "monthly_update"})
CLASSES = ("before", "in_year", "next_year", "later", "undated", "never", "not_in_860")
DELIVERED = ("online_in_year", "rekeyed_online")
SHOWN_GROUPS = ("all", "wind_onshore", "solar", "gas_cc", "battery", "gas_ct")
# The January 2017 plan as docs/annual-flows.md states it (check C1).
EXPECTED_2017 = {("all", "all"): 26268.8, ("wind_onshore", "all"): 6858.3,
                 ("all", "online_in_year"): 16750.8, ("wind_onshore", "online_in_year"): 4283.6,
                 ("wind_onshore", "slipped"): 2236.3}
UNDATED_MAX = 0.10  # check C4 (amendment 1): undated share of the 2017 plan


def norm_key(plant, gen):
    """'plant/GEN' with the plant id as an integer and the generator id trimmed and upper-cased;
    None if either is missing."""
    try:
        p = int(float(plant))
    except (TypeError, ValueError):
        return None
    if not isinstance(gen, str) or not gen.strip():
        return None
    return "%d/%s" % (p, gen.strip().upper())


def plan_key(key):
    plant, _, gen = str(key).partition("/")
    return norm_key(plant, gen)


def annual_only(a):
    """The annual records only: rows whose data_maturity marks them as EIA-860M updates are left
    out. Returns (kept, counts of every data_maturity value before the cut)."""
    if "data_maturity" not in a.columns:
        return a, {}
    dm = a["data_maturity"].astype(str).str.strip().str.lower()
    counts = {str(k): int(v) for k, v in dm.value_counts().sort_index().items()}
    return a[~dm.isin(NOT_ANNUAL)], counts


def annual_first(a):
    """(first, listed): each key's earliest operating month (months since year 0) in the annual
    records that list it as operating, NaN if none of them is dated; and every key listed."""
    keys = [norm_key(p, g) for p, g in zip(a["plant_id_eia"], a["generator_id"])]
    status = a["operational_status_code"].astype(str).str.strip().str.upper().to_numpy()
    f = pd.DataFrame({"key": keys, "status": status,
                      "op_m": es.months(a["generator_operating_date"])})
    f = f[f["key"].notna()]
    op = f[f["status"].isin(es.OPERATING)]
    return op.groupby("key")["op_m"].min(), set(f["key"])


def annual_class(year, key, first, listed):
    k = plan_key(key)
    if k is not None and k in first.index:
        m = first[k]
        if m != m:
            return "undated"
        y = int(m // 12)
        if y < year:
            return "before"
        if y == year:
            return "in_year"
        return "next_year" if y == year + 1 else "later"
    return "never" if k in listed else "not_in_860"


def _row(label, f):
    mw = float(f["mw"].sum())
    row = dict(label, planned_mw=round(mw, 1))
    parts = {c: float(f.loc[f["cls"] == c, "mw"].sum()) for c in CLASSES}
    row.update({c: round(v, 1) for c, v in parts.items()})
    delivered = float(f.loc[f["state"].isin(DELIVERED), "mw"].sum())
    row["delivered_860m_mw"] = round(delivered, 1)
    row["share_860m"] = round(delivered / mw, 3) if mw > 0 else None
    row["share_860"] = round(parts["in_year"] / mw, 3) if mw > 0 else None
    row["adds_up"] = abs(sum(parts.values()) - mw) < 0.05
    return row


def summarize(plan):
    """Rows per year and group ('all' and each group), for all states and for each EIA-860M
    state, with MW by annual class."""
    rows = []
    for year, f in plan.groupby("year"):
        for grp in ["all"] + sorted(set(f["group"])):
            g = f if grp == "all" else f[f["group"] == grp]
            rows.append(_row({"year": int(year), "group": grp, "state": "all"}, g))
            for st in sorted(set(g["state"])):
                rows.append(_row({"year": int(year), "group": grp, "state": st},
                                 g[g["state"] == st]))
    return rows


def checks(rows, missing_cols, report_years):
    r = {(x["year"], x["group"], x["state"]): x for x in rows}
    got = {"%s/%s" % gs: (r[(2017,) + gs]["planned_mw"] if (2017,) + gs in r else None)
           for gs in EXPECTED_2017}
    c1 = all(got["%s/%s" % gs] is not None and abs(got["%s/%s" % gs] - v) <= 0.1
             for gs, v in EXPECTED_2017.items())
    years_ok = 2017 in report_years and 2018 in report_years
    c2 = not missing_cols and years_ok
    bad = sum(not x["adds_up"] for x in rows)
    a17 = r.get((2017, "all", "all"))
    undated = (a17["undated"] / a17["planned_mw"]
               if a17 is not None and a17["planned_mw"] > 0 else None)
    c4 = undated is not None and undated < UNDATED_MAX
    return {"C1": {"got": got, "pass": c1},
            "C2": {"missing_columns": list(missing_cols), "has_2017_and_2018": years_ok,
                   "pass": c2},
            "C3": {"rows": len(rows), "not_adding_up": bad, "pass": bad == 0},
            "C4": {"undated_share_2017": None if undated is None else round(undated, 4),
                   "max": UNDATED_MAX, "pass": c4},
            "all_pass": bool(c1 and c2 and bad == 0 and c4)}


def _share(row):
    if row is None or not row["planned_mw"] > 0:
        return None
    return round(row["in_year"] / row["planned_mw"], 4)


def predictions(rows):
    r = {(x["year"], x["group"], x["state"]): x for x in rows}
    out = {}
    for name, gs, floor in (("W1", ("wind_onshore", "all"), 0.75),
                            ("W2", ("wind_onshore", "slipped"), 0.50),
                            ("W3", ("all", "all"), 0.70)):
        s = _share(r.get((2017,) + gs))
        out[name] = {"share_860": s, "floor": floor, "held": None if s is None else s >= floor}
    years = [y for y in range(2017, 2025) if (y, "all", "all") in r]
    above = [y for y in years if r[(y, "all", "all")]["in_year"]
             > r[(y, "all", "all")]["delivered_860m_mw"]]
    out["W4"] = {"years": years, "years_860_above_860m": above,
                 "held": None if len(years) < 8 else len(above) >= 7}
    return out


def _plan_rows(df, a):
    """Plan-side generators of the annual flows with their annual class and both online months."""
    result, gens = es.annual_flows(df)
    plan = gens[gens["kind"] == "plan"].copy().reset_index(drop=True)
    first, listed = annual_first(a)
    links = {x["plan_key"]: x["entry_key"] for x in result["links"]}
    look = [links.get(k, k) for k in plan["key"]]
    online = es.online_months(df)
    latest = es._latest(df)
    plan["lookup_key"] = look
    plan["cls"] = [annual_class(int(y), k, first, listed) for y, k in zip(plan["year"], look)]
    plan["online_860m"] = [es.month_str(online.get(k, np.nan)) for k in plan["key"]]
    plan["online_860"] = [es.month_str(first.get(plan_key(k), np.nan)) for k in look]
    plan["plant"] = [latest["plant_name_eia"].get(k) for k in plan["key"]]
    return plan


def write_md(path, meta, rows, chk, pred, gaps):
    md = ["# January's EIA-860M plan against annual EIA-860 operating dates", "",
          "eia860m-slip %s annual flows; annual data %s (report years %s-%s). annual860 %s, "
          "MV2 of Munim, Inc. (made with AI agents)." % (
              meta["eia860m_slip"], meta["annual_source"], meta["annual_report_years"][0],
              meta["annual_report_years"][-1], __version__), "",
          "share_860m: (online_in_year + rekeyed_online) / planned, as in docs/annual-flows.md. "
          "share_860: in_year / planned, from the annual operating month.", "",
          "Annual records by data_maturity before EIA-860M rows were left out: %s; kept %d." % (
              json.dumps(meta["annual_maturity_counts"]), meta["annual_rows_kept"]), ""]
    cols = ["year", "group", "planned_mw", "share_860m", "share_860"] + list(CLASSES)
    md += ["## Every year, main groups", ""]
    md += es.table([x for x in rows if x["state"] == "all" and x["group"] in SHOWN_GROUPS],
                   cols) + [""]
    md += ["## 2017 by EIA-860M state", ""]
    md += es.table([x for x in rows if x["year"] == 2017 and x["group"] in SHOWN_GROUPS],
                   ["group", "state", "planned_mw"] + list(CLASSES)) + [""]
    md += ["## 2017 onshore wind not delivered in EIA-860M but in_year in EIA-860", ""]
    md += es.table(gaps, ["key", "plant", "mw", "state", "online_860m", "online_860"]) + [""]
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
        urllib.request.urlretrieve(URL_860, args.annual)
    a_names = pq.read_schema(args.annual).names
    missing = [c for c in COLS_860 if c not in a_names]
    a = pd.read_parquet(args.annual,
                        columns=[c for c in COLS_860 + OPTIONAL_860 if c in a_names])
    for c in missing:
        a[c] = np.nan
    a, maturity = annual_only(a)
    report_years = sorted({int(y) for y in
                           pd.to_datetime(a["report_date"], errors="coerce").dt.year.dropna()})
    plan = _plan_rows(df, a)
    rows = summarize(plan)
    chk = checks(rows, missing, report_years)
    pred = predictions(rows)
    w = plan[(plan["year"] == 2017) & (plan["group"] == "wind_onshore")
             & ~plan["state"].isin(DELIVERED) & (plan["cls"] == "in_year")]
    gaps = [{"key": k, "plant": p, "mw": float(m), "state": s, "online_860m": o1, "online_860": o2}
            for k, p, m, s, o1, o2 in sorted(zip(w["key"], w["plant"], w["mw"], w["state"],
                                                 w["online_860m"], w["online_860"]),
                                             key=lambda t: (-t[2], t[0]))]
    meta = {"version": __version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "report_max": es.month_str(df["report_m"].max()),
            "annual_source": os.path.basename(args.annual),
            "annual_bytes": os.path.getsize(args.annual), "annual_columns": a_names,
            "annual_maturity_counts": maturity, "annual_rows_kept": int(len(a)),
            "annual_report_years": report_years}
    with open(os.path.join(args.out_dir, "annual860.json"), "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "checks": chk, "predictions": pred, "rows": rows,
                   "wind_2017_gaps": gaps}, fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "annual860.md"), meta, rows, chk, pred, gaps)
    plan.drop(columns=["kind"]).to_csv(os.path.join(args.out_dir, "plan_860.csv"), index=False)
    print(json.dumps({"checks": chk, "predictions": pred}, indent=1))


if __name__ == "__main__":
    main()
