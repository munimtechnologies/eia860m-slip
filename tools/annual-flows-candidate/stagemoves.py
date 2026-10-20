"""stagemoves: how do planned generators move between stages from one EIA-860M report to the next?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Every EIA-860M report gives each planned generator a status code. The repo's earlier results
read a generator's stage at one report; this reads how the stage moves between consecutive
reports. A "step" is one generator that is planned in report m with an ordered band (early =
P, L; approved = T; building = U, V, TS) and has a record in force in report m + 1. Its move:

    forward        to a later planned band (early -> approved -> building)
    held           the same band
    backward       to an earlier planned band
    to_operating   listed as operating (OP, SB, OS, OA) in report m + 1
    exit_other     any other status in report m + 1 (OT, IP, CN, RE, ...)

A generator planned in m with no record in force in m + 1 is not a step; it is counted as
"left". Re-keyed plants (rule R, eia860m_slip 0.3.1) are one generator: each entry key is
renamed to its plan key before anything is read. Steps start in January 2016, when PUDL's
EIA-860M capacities start. A step at m is scored for whether the generator is listed as
operating in any report m + 1 to m + 12, only when m + 12 is at or before the last report.

Checks and predictions: docs/stage-moves-preregistration.md.

    python stagemoves.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

import eia860m_slip as es

__version__ = "0.1.0"

BANDS = ("early", "approved", "building")  # the ordered planned bands, earliest first
ORDER = {b: i for i, b in enumerate(BANDS)}
TO = BANDS + ("operating", "other")
MOVES = ("forward", "held", "backward", "to_operating", "exit_other")
START_M = 2016 * 12           # first step month: January 2016
POOL_END = 2025 * 12 + 11     # steps pooled for M1 and the tables: m in 2016-2025
WINDOW = 12                   # reports after a step in which an operating listing is looked for
FLICKER = 6                   # reports after a backward move in which a return is looked for
SAMPLE = (2017 * 12, 2020 * 12, 2024 * 12)  # check S1: January 2017, 2020 and 2024
REKEYS = 11                   # check S3: rule R links, docs/annual-flows-rekey.md
GROUPS = ("all", "solar", "wind_onshore", "battery", "gas_cc", "gas_ct")
TOP = 15
YEAR_COLS = (["year", "band", "steps", "step_mw"] + [x + "_mw" for x in MOVES]
             + ["left_mw", "backward_share"])
POOL_COLS = ["band", "steps", "step_mw"] + [x + "_mw" for x in TO] + ["left_mw"]
GROUP_COLS = ["group", "building_step_mw", "building_backward_mw", "building_backward_share",
              "approved_step_mw", "approved_backward_mw", "approved_backward_share"]
OUT_COLS = ["band", "move", "steps", "scored_mw", "online_mw", "online_share"]
TOP_COLS = ["key", "plant", "group", "mw", "moved_in", "from_status", "to_status", "online_12"]


def band(status):
    """early, approved, building, operating or other, as entry860.band."""
    if status in es.OPERATING:
        return "operating"
    b = es.STAGE_BANDS.get(status)
    return b if b in BANDS else "other"


def move(b0, b1):
    """The move of a step from planned band b0 to band b1."""
    if b1 == "operating":
        return "to_operating"
    if b1 not in ORDER:
        return "exit_other"
    d = ORDER[b1] - ORDER[b0]
    return "forward" if d > 0 else "held" if d == 0 else "backward"


def rekeyed(df, links):
    """df with each rule R entry key renamed to its plan key, so a re-keyed plant is one key."""
    names = {x["entry_key"]: x["plan_key"] for x in links}
    out = df.copy()
    out["key"] = [names.get(k, k) for k in out["key"]]
    return out


def timeline(df, first_m, last_m):
    """One row per report month first_m..last_m and generator ever listed as planned that has a
    record in force then: key, status, band, MW, technology group and plant name."""
    planned = set(df.loc[df["status"].isin(list(es.PLANNED)), "key"])
    sub = df[df["key"].isin(planned)]
    parts = []
    for r in range(int(first_m), int(last_m) + 1):
        s = es.snapshot(sub, r)
        parts.append(pd.DataFrame({"m": np.full(len(s), r, dtype=np.int64),
                                   "key": s["key"].to_numpy(),
                                   "status": s["status"].to_numpy(),
                                   "mw": s["capacity_mw"].to_numpy(dtype=float),
                                   "group": s["group"].to_numpy(),
                                   "plant": s["plant_name_eia"].to_numpy()}))
    t = pd.concat(parts, ignore_index=True)
    t["band"] = [band(x) for x in t["status"]]
    return t


def online_within(t, s, last_m):
    """1.0 if the step's generator is listed as operating in a report m + 1 to m + WINDOW, else
    0.0; NaN when m + WINDOW is after the last report."""
    op = {k: np.sort(g.to_numpy(dtype=float))
          for k, g in t.loc[t["band"] == "operating"].groupby("key")["m"]}
    out = []
    for k, m in zip(s["key"], s["m"]):
        if m + WINDOW > last_m:
            out.append(np.nan)
            continue
        a = op.get(k)
        i = 0 if a is None else int(np.searchsorted(a, m, side="right"))
        out.append(1.0 if a is not None and i < len(a) and a[i] <= m + WINDOW else 0.0)
    return np.array(out, dtype=float)


def steps(t, last_m):
    """(steps, left): one row per step, and one row per generator planned in an ordered band in
    report m (m before the last report) with no record in force in m + 1."""
    a = t[t["band"].isin(list(BANDS)) & (t["m"] < last_m)]
    nxt = t[["m", "key", "band", "status"]].rename(columns={"band": "band1", "status": "status1"})
    nxt = nxt.assign(m=nxt["m"] - 1)
    j = a.merge(nxt, on=["m", "key"], how="left", indicator=True)
    left = j[j["_merge"] == "left_only"].drop(columns=["band1", "status1", "_merge"])
    s = j[j["_merge"] == "both"].drop(columns=["_merge"]).reset_index(drop=True)
    s["move"] = [move(x, y) for x, y in zip(s["band"], s["band1"])]
    s["online_12"] = online_within(t, s, last_m)
    s["year"] = (s["m"] // 12).astype(int)
    left = left.assign(year=(left["m"] // 12).astype(int)).reset_index(drop=True)
    return s, left


def _mw(f, mask=None):
    return float(f["mw"].sum() if mask is None else f.loc[mask, "mw"].sum())


def _share(num, den):
    return round(num / den, 4) if den > 0 else None


def _ratio(num, den):
    return num / den if den > 0 else None


def matrix(s, left, label):
    """One row per starting band: steps, MW by move and left, and the backward share."""
    rows = []
    for b0 in BANDS:
        f, lf = s[s["band"] == b0], left[left["band"] == b0]
        row = dict(label, band=b0, steps=int(len(f)), step_mw=round(_mw(f), 1))
        parts, count = 0.0, 0
        for mv in MOVES:
            hit = f["move"] == mv
            row[mv + "_mw"] = round(_mw(f, hit), 1)
            row[mv + "_n"] = int(hit.sum())
            parts += _mw(f, hit)
            count += int(hit.sum())
        row["left_mw"] = round(_mw(lf), 1)
        row["left_n"] = int(len(lf))
        row["backward_share"] = _share(_mw(f, f["move"] == "backward"), _mw(f))
        row["adds_up"] = bool(abs(parts - _mw(f)) < 0.05 and count == len(f))
        rows.append(row)
    return rows


def pooled(s, left):
    """2016-2025: one row per starting band, MW by the band in report m + 1, and left."""
    p, lp = s[s["m"] <= POOL_END], left[left["m"] <= POOL_END]
    rows = []
    for b0 in BANDS:
        f = p[p["band"] == b0]
        row = {"band": b0, "steps": int(len(f)), "step_mw": round(_mw(f), 1)}
        for b1 in TO:
            row[b1 + "_mw"] = round(_mw(f, f["band1"] == b1), 1)
        row["left_mw"] = round(_mw(lp[lp["band"] == b0]), 1)
        rows.append(row)
    return rows


def by_group(s):
    """2016-2025: backward share of building and approved steps, by technology group."""
    p = s[s["m"] <= POOL_END]
    rows = []
    for grp in GROUPS:
        g = p if grp == "all" else p[p["group"] == grp]
        row = {"group": grp}
        for b0 in ("building", "approved"):
            f = g[g["band"] == b0]
            back = _mw(f, f["move"] == "backward")
            row[b0 + "_step_mw"] = round(_mw(f), 1)
            row[b0 + "_backward_mw"] = round(back, 1)
            row[b0 + "_backward_share"] = _share(back, _mw(f))
        rows.append(row)
    return rows


def outcomes(s):
    """Steps whose window is closed: MW listed as operating within WINDOW reports, by starting
    band and move."""
    c = s[s["online_12"].notna()]
    rows = []
    for b0 in BANDS:
        for mv in MOVES:
            f = c[(c["band"] == b0) & (c["move"] == mv)]
            on = _mw(f, f["online_12"] == 1.0)
            rows.append({"band": b0, "move": mv, "steps": int(len(f)),
                         "scored_mw": round(_mw(f), 1), "online_mw": round(on, 1),
                         "online_share": _share(on, _mw(f))})
    return rows


def flicker(t, s, last_m):
    """Generators whose first backward step from building leaves FLICKER reports to look in:
    how many are listed as building or operating again in reports m + 2 to m + 1 + FLICKER."""
    back = s[(s["band"] == "building") & (s["move"] == "backward")
             & (s["m"] + 1 + FLICKER <= last_m)]
    back = back.sort_values(["key", "m"], kind="mergesort").drop_duplicates("key")
    sub = t[t["key"].isin(set(back["key"]))]
    bands = {k: dict(zip(g["m"], g["band"])) for k, g in sub.groupby("key")}
    returned = 0
    for k, m in zip(back["key"], back["m"]):
        seen = bands.get(k, {})
        if any(seen.get(m + 1 + j) in ("building", "operating") for j in range(1, FLICKER + 1)):
            returned += 1
    return {"generators": int(len(back)), "returned": returned,
            "mw": round(_mw(back), 1), "share": _share(returned, len(back))}


def paths(t):
    """Generators first in force after January 2016 with an early band that later reach
    building: how many, and how much MW (at the first building report), were listed as
    approved in between."""
    first = t.groupby("key")["m"].min()
    new = set(first[first > START_M].index)
    f = t[t["key"].isin(new)].sort_values(["key", "m"], kind="mergesort")
    total = through = 0.0
    n = n_t = 0
    for _, g in f.groupby("key", sort=True):
        b = list(g["band"])
        if b[0] != "early" or "building" not in b:
            continue
        i = b.index("building")
        mw = float(g["mw"].iloc[i])
        total += mw
        n += 1
        if "approved" in b[:i]:
            through += mw
            n_t += 1
    return {"generators": n, "mw": round(total, 1), "through_approved_n": n_t,
            "through_approved_mw": round(through, 1), "share": _share(through, total)}


def _plant(v):
    return v if isinstance(v, str) else None


def top_backward(s):
    """The largest backward steps from building (all months), largest MW first."""
    f = s[(s["band"] == "building") & (s["move"] == "backward")]
    f = f.sort_values(["mw", "key", "m"], ascending=[False, True, True], kind="mergesort")
    out = []
    for r in f.head(TOP).itertuples(index=False):
        out.append({"key": r.key, "plant": _plant(r.plant), "group": r.group,
                    "mw": round(float(r.mw), 1), "moved_in": es.month_str(r.m + 1),
                    "from_status": r.status, "to_status": r.status1,
                    "online_12": None if r.online_12 != r.online_12 else
                    ("yes" if r.online_12 == 1.0 else "no")})
    return out


def sample_check(df, s, months):
    """Check S1: for each sample month, the steps equal an independent reading of es.snapshot at
    m and m + 1 on the whole (re-keyed) changelog."""
    out = {}
    for m in months:
        a, b = es.snapshot(df, m), es.snapshot(df, m + 1)
        a = a[np.array([band(x) in ORDER for x in a["status"]], dtype=bool)]
        a = a[a["key"].isin(set(b["key"]))]
        got = s[s["m"] == m]
        out[es.month_str(m)] = {"expected_mw": round(float(a["capacity_mw"].sum()), 1),
                                "expected_n": int(len(a)), "got_mw": round(_mw(got), 1),
                                "got_n": int(len(got))}
    ok = bool(out) and all(abs(v["expected_mw"] - v["got_mw"]) <= 0.1
                           and v["expected_n"] == v["got_n"] for v in out.values())
    return {"months": out, "pass": ok}


def checks(t, s_check, rows, links, first_m, last_m):
    dup = int(t.duplicated(["m", "key"]).sum())
    have = {int(x) for x in set(t["m"])}
    missing = [es.month_str(m) for m in range(int(first_m), int(last_m) + 1) if m not in have]
    bad = sum(not x["adds_up"] for x in rows)
    return {"S1": s_check,
            "S2": {"rows": len(rows), "not_adding_up": bad, "pass": bad == 0},
            "S3": {"links": len(links), "expected": REKEYS, "pass": len(links) == REKEYS},
            "S4": {"duplicate_key_months": dup, "missing_months": missing,
                   "pass": dup == 0 and not missing},
            "all_pass": bool(s_check["pass"] and bad == 0 and len(links) == REKEYS
                             and dup == 0 and not missing)}


def _r4(x):
    return None if x is None else round(x, 4)


def predictions(s, flick, path):
    """M1-M4. Shares are compared with their thresholds unrounded and rounded for display."""
    p = s[(s["m"] <= POOL_END) & (s["band"] == "building")]
    r = _ratio(_mw(p, p["move"] == "backward"), _mw(p))
    out = {"M1": {"building_backward_share": _r4(r), "below": 0.02,
                  "held": None if r is None else r < 0.02}}
    r = _ratio(flick["returned"], flick["generators"])
    out["M2"] = {"returned_share": _r4(r), "floor": 0.25, "held": None if r is None else r >= 0.25}
    c = s[s["online_12"].notna() & (s["band"] == "building")]
    held, back = c[c["move"] == "held"], c[c["move"] == "backward"]
    h = _ratio(_mw(held, held["online_12"] == 1.0), _mw(held))
    b = _ratio(_mw(back, back["online_12"] == 1.0), _mw(back))
    gap = None if h is None or b is None else h - b
    out["M3"] = {"held_online_share": _r4(h), "backward_online_share": _r4(b),
                 "gap": _r4(gap), "floor": 0.20, "held": None if gap is None else gap >= 0.20}
    r = _ratio(path["through_approved_mw"], path["mw"])
    out["M4"] = {"through_approved_share": _r4(r), "below": 0.50,
                 "held": None if r is None else r < 0.50}
    return out


def write_md(path, meta, res):
    md = ["# How planned generators move between stages in EIA-860M", "",
          "stagemoves %s on eia860m-slip %s; data %s (reports %s to %s). MV2 of Munim, Inc. "
          "(made with AI agents)." % (meta["version"], meta["eia860m_slip"], meta["source"],
                                      meta["first_step"], meta["report_max"]), "",
          "A step: a generator planned in report m with band early (P, L), approved (T) or "
          "building (U, V, TS) that has a record in force in report m + 1. Moves: forward, held, "
          "backward (to an earlier band), to_operating, exit_other (any other status). left: "
          "planned in m, no record in force in m + 1 (not a step). Rule R re-keys are one "
          "generator. MW is the capacity in report m. online_12: listed as operating in a "
          "report m + 1 to m + 12, scored only when m + 12 is at or before the last report.", ""]
    md += ["## Pooled 2016-2025: the band in the next report (MW)", ""]
    md += es.table(res["pooled"], POOL_COLS) + [""]
    md += ["## Every year: steps by starting band and move (MW)", ""]
    md += es.table(res["matrix"], YEAR_COLS) + [""]
    md += ["## Pooled 2016-2025: backward share by technology group", ""]
    md += es.table(res["groups"], GROUP_COLS) + [""]
    md += ["## Listed as operating within 12 reports, by starting band and move (closed windows)",
           ""]
    md += es.table(res["outcomes"], OUT_COLS) + [""]
    md += ["## Largest backward steps from building", ""]
    md += es.table(res["top_backward"], TOP_COLS) + [""]
    md += ["## Back in building or operating within %d reports of a backward move (M2)" % FLICKER,
           "", "```", json.dumps(res["flicker"], indent=1), "```", "",
           "## From early to building: through approved? (M4)", "", "```",
           json.dumps(res["paths"], indent=1), "```", "",
           "## Checks", "", "```", json.dumps(res["checks"], indent=1), "```", "",
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
    df = rekeyed(df, links)
    last_m = int(df["report_m"].max())
    t = timeline(df, START_M, last_m)
    s, left = steps(t, last_m)
    rows = []
    for y in sorted(set(s["year"])):
        rows += matrix(s[s["year"] == y], left[left["year"] == y], {"year": int(y)})
    flick = flicker(t, s, last_m)
    path_res = paths(t)
    res = {"matrix": rows, "pooled": pooled(s, left), "groups": by_group(s),
           "outcomes": outcomes(s), "top_backward": top_backward(s), "flicker": flick,
           "paths": path_res,
           "checks": checks(t, sample_check(df, s, SAMPLE), rows, links, START_M, last_m),
           "predictions": predictions(s, flick, path_res)}
    meta = {"version": __version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "first_step": es.month_str(START_M),
            "report_max": es.month_str(last_m), "steps": int(len(s)), "left": int(len(left)),
            "generators": int(t["key"].nunique()), "links": links}
    with open(os.path.join(args.out_dir, "stagemoves.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "stagemoves.md"), meta, res)
    s[s["move"] == "backward"].to_csv(os.path.join(args.out_dir, "backward_steps.csv"),
                                      index=False)
    print(json.dumps({"checks": res["checks"], "predictions": res["predictions"]}, indent=1,
                     default=str))


if __name__ == "__main__":
    main()
