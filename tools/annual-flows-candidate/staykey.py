"""staykey: how much EIA-860M capacity scored "not online" belongs to planned keys still listed
beside a built replacement at the same plant? The second bound on key-following in every
eia860m-slip delivery rate, after splitkey's rule S.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

eia860m_slip.py follows each generator by its key (plant id / generator id). splitkey's rule S
links plans that LEFT EIA-860M to new generator ids at the same plant. It skips plans still
listed in the last report, so a stale planned key kept beside the generators that built it
stays "not online". This tool splits the not-online capacity by what became of each key
(came online later, still listed as planned, left the list, other), finds stale keys with rule
T and re-scores the cohort rows (0-12 months) and the stage-by-lead rows (0-24 months) with the
month the replacements came online, alone and together with rule S.

Rule T (docs/stale-keys-preregistration.md):

1. A stayer is a generator with a planned record, no operating month under its key, a record
   in force in the last report that lists it as planned, and capacity above 0 in that record.
2. Stayers at the same plant id and fuel family (splitkey.family) form one group.
3. A group's twins: generators at the same plant id and fuel family that have a planned record,
   came online, and were first listed after the group's earliest first listing.
4. A group is linked when it has twins and their summed capacity (each in its first record with
   capacity above 0) is within MW_TOL of the group's (each stayer's last record).
5. A linked group's replacement month is the latest operating month of its twins. Its stayers
   are re-scored as if online in that month.

Bound B: a group is possible when any generator at the same plant id and fuel family that was
first listed after the group's earliest first listing came online. Every replaced stayer is in
a possible group, so B bounds rule T from above.

    python staykey.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

import eia860m_slip as es
import leadtime as lt
import splitkey as sk

__version__ = "0.1.0"

MW_TOL = 0.20        # largest capacity difference, as a share of the group's capacity
TOLERANCES = (0.05, 0.10, 0.20, 0.30)
GROUPS = ("solar", "wind_onshore", "gas_cc", "battery", "gas_ct")
FATES = ("online_later", "stayer", "leaver", "other")
HAND_READ = 10       # linked groups whose raw records are written out for reading by hand
RANK = {"P": 0, "L": 0, "T": 1, "U": 2, "V": 3, "TS": 4}   # stage order; OT has none
# Predictions (docs/stale-keys-preregistration.md), compared unrounded.
STAYER_RANGE = (0.10, 0.40)   # T1
S_SHARE = 0.0235              # T2: rule S's published replaced share
RISE_CEILING = 0.01           # T3
NOT_ONLINE_FLOOR = 0.17       # T4
PART_COLS = ["part", "rows", "mw", "not_online_mw", "online_later_share", "stayer_share",
             "leaver_share", "other_share", "replaced_mw", "possible_mw", "replaced_share",
             "possible_share", "on_time_before", "on_time_after", "not_online_before",
             "not_online_after", "on_time_both", "not_online_both"]
LINK_COLS = ["plant", "name", "state", "family", "stayers", "stayer_mw", "twins", "twin_mw",
             "first_listed", "twins_listed", "planned_at_arrival", "twins_planned", "a_months",
             "online_all", "stayer_planned_last", "b_advanced", "not_online_mw_rows",
             "lt_not_online_mw_rows"]


def last_status(df):
    """Status code of each generator's last record."""
    s = df.sort_values(["key", "report_m"], kind="mergesort")
    return s.groupby("key")["status"].last()


def stayers(info, status, last_report):
    """Rule T step 1."""
    st = status.reindex(info.index)
    return info[info["planned"] & ~info["online"] & (info["last_m"] >= last_report)
                & st.isin(list(es.PLANNED)) & (info["mw_last"] > 0)]


def groups(stay):
    """Rule T step 2: one dict per plant id and family (stayers, earliest first listing, summed
    last-record MW), in order of plant id and family."""
    out = []
    for (p, f), h in stay.sort_index().groupby(["plant", "family"], sort=True):
        out.append({"plant": p, "family": f, "stayers": list(h.index),
                    "first": float(h["first_m"].min()), "mw": float(h["mw_last"].sum())})
    return out


def link(info, gr, tol=MW_TOL):
    """Rule T steps 3-5: the linked groups, each with its twins, their summed MW and the
    replacement month."""
    by = dict(tuple(info.groupby(["plant", "family"])))
    out = []
    for x in gr:
        h = by[(x["plant"], x["family"])]
        cand = h[h["online"] & h["planned"] & (h["first_m"] > x["first"])
                 & ~h.index.isin(x["stayers"])]
        tw = sorted(cand.index)
        if not tw:
            continue
        mw = float(info.loc[tw, "mw_first"].sum())
        if abs(mw - x["mw"]) <= tol * x["mw"]:
            out.append(dict(x, twins=tw, twins_mw=mw,
                            month=float(info.loc[tw, "online_m"].max())))
    return out


def credit(links):
    """Stayer key -> replacement month."""
    return {k: x["month"] for x in links for k in x["stayers"]}


def possible_keys(info, gr):
    """Bound B: stayers of groups at whose plant and family a generator first listed after the
    group's earliest first listing came online."""
    on = info[info["online"]].groupby(["plant", "family"])["first_m"].max()
    out = set()
    for x in gr:
        m = on.get((x["plant"], x["family"]), np.nan)
        if m == m and m > x["first"]:
            out.update(x["stayers"])
    return out


def fates(c, online_keys, stay, leave):
    """Not-online MW of some rows split by what became of each key: came online later than 12
    months, still listed as planned (stayer), left EIA-860M (splitkey's leaver), other."""
    off = c[c["outcome"] == "not_online_12"]
    n = float(off["mw"].sum())
    k = off["key"]
    on = k.isin(list(online_keys)).to_numpy()
    st = k.isin(list(stay)).to_numpy() & ~on
    lv = k.isin(list(leave)).to_numpy() & ~on & ~st
    masks = {"online_later": on, "stayer": st, "leaver": lv, "other": ~(on | st | lv)}
    out = {"not_online_mw": n}
    for name in FATES:
        mw = float(off.loc[masks[name], "mw"].sum())
        out[name + "_mw"] = mw
        out[name + "_share"] = lt._ratio(mw, n)
    return out


def measure(c, c2, c3, online_keys, stay, leave, linked, months, possible):
    """Unrounded: sk.bias for rule T (c2), the not-online split, and the on-time and not-online
    shares after rules S and T together (c3)."""
    out = sk.bias(c, c2, linked, months, possible)
    out.update(fates(c, online_keys, stay, leave))
    both = sk.bias(c, c3, linked, months, possible)
    out["on_time_both"] = both["on_time_after"]
    out["not_online_both"] = both["not_online_after"]
    return out


def k2(info, status, links, months, possible, last_report, tol=MW_TOL):
    """K2: every link obeys rule T and every replaced stayer is inside bound B."""
    st = [k for x in links for k in x["stayers"]]
    tw = [k for x in links for k in x["twins"]]
    out = {"stayers_not_staying": sum(1 for k in st if info.at[k, "online"]
                                      or info.at[k, "last_m"] < last_report
                                      or status.get(k) not in es.PLANNED),
           "twins_not_built": sum(1 for k in tw if not info.at[k, "online"]
                                  or not info.at[k, "planned"]),
           "wrong_plant_or_family": sum(1 for x in links for k in x["stayers"] + x["twins"]
                                        if info.at[k, "plant"] != x["plant"]
                                        or info.at[k, "family"] != x["family"]),
           "twin_listed_too_early": sum(1 for x in links for k in x["twins"]
                                        if info.at[k, "first_m"] <= x["first"]),
           "twins_reused": len(tw) - len(set(tw)),
           "outside_tolerance": sum(1 for x in links
                                    if abs(x["twins_mw"] - x["mw"]) > tol * x["mw"]),
           "replaced_outside_bound": len(set(months) - set(possible))}
    out["pass"] = all(v == 0 for v in out.values())
    return out


def predictions(cohort, l_before, l_both):
    """T1-T5 from unrounded measures (cohort: the 0-12-month rows; l_before / l_both:
    leadtime.predictions before and after rules S and T together)."""
    s = cohort["stayer_share"]
    out = {"T1": {"stayer_share": lt._r4(s), "range": list(STAYER_RANGE),
                  "held": None if s is None else STAYER_RANGE[0] <= s <= STAYER_RANGE[1]}}
    r = cohort["replaced_share"]
    out["T2"] = {"replaced_share": lt._r4(r), "rule_s_share": S_SHARE,
                 "held": None if r is None else r < S_SHARE}
    a, b = cohort["on_time_before"], cohort["on_time_after"]
    rise = None if a is None or b is None else b - a
    out["T3"] = {"on_time_before": lt._r4(a), "on_time_after": lt._r4(b), "rise": lt._r4(rise),
                 "ceiling": RISE_CEILING, "held": None if rise is None else rise < RISE_CEILING}
    x = cohort["not_online_both"]
    out["T4"] = {"not_online_before": lt._r4(cohort["not_online_before"]),
                 "not_online_both": lt._r4(x), "floor": NOT_ONLINE_FLOOR,
                 "held": None if x is None else x >= NOT_ONLINE_FLOOR}
    same = {k: l_before[k]["held"] == l_both[k]["held"] for k in sorted(l_before)}
    out["T5"] = {"before": {k: l_before[k]["held"] for k in sorted(l_before)},
                 "both": {k: l_both[k]["held"] for k in sorted(l_both)},
                 "unchanged": same, "held": all(same.values())}
    return out


def planned_at(sub, keys, before):
    """Latest planned month among the stayers' records reported before a month (NaN if none)."""
    s = sub[sub["key"].isin(keys) & (sub["report_m"] < before)
            & sub["status"].isin(list(es.PLANNED)) & sub["planned_m"].notna()]
    if s.empty:
        return np.nan
    s = s.sort_values(["key", "report_m"], kind="mergesort")
    return float(s.groupby("key")["planned_m"].last().max())


def advanced(sub, key, month):
    """True if a record reported after a month lists the generator at a later stage than the
    record in force at that month (its first record if none was reported yet)."""
    s = sub[sub["key"] == key].sort_values("report_m", kind="mergesort")
    if s.empty:
        return False
    before = s[s["report_m"] <= month]
    base = RANK.get((before if len(before) else s.head(1))["status"].iloc[-1])
    after = [RANK.get(v) for v in s.loc[s["report_m"] > month, "status"]]
    return base is not None and any(a is not None and a > base for a in after)


def link_table(links, info, df, c, r):
    """One row per linked group, most not-online MW (0-12-month rows) first, with the two
    counts the hand-reading uses: (a) the largest gap in months between a twin's first planned
    month and the stayers' planned month just before the first twin was listed, and (b) how
    many stayers moved to a later stage after the replacement month."""
    off = c[c["outcome"] == "not_online_12"].groupby("key")["mw"].sum()
    offr = r[r["outcome"] == "not_online_12"].groupby("key")["mw"].sum()
    keys = [k for x in links for k in x["stayers"]]
    sub = df[df["key"].isin(keys)]
    rows = []
    for x in links:
        st, tw = x["stayers"], x["twins"]
        arrived = float(info.loc[tw, "first_m"].min())
        pa = planned_at(sub, st, arrived)
        if pa != pa:
            got = [v for v in info.loc[st, "planned_first"] if v == v]
            pa = max(got) if got else np.nan
        tp = list(info.loc[tw, "planned_first"])
        gaps = [abs(v - pa) for v in tp]
        last = [v for v in info.loc[st, "planned_last"] if v == v]
        rows.append({"plant": x["plant"], "name": info.at[st[0], "name"],
                     "state": info.at[st[0], "state"], "family": x["family"],
                     "stayers": "; ".join(st), "stayer_mw": round(x["mw"], 1),
                     "twins": "; ".join(tw), "twin_mw": round(x["twins_mw"], 1),
                     "first_listed": es.month_str(x["first"]),
                     "twins_listed": es.month_str(arrived),
                     "planned_at_arrival": es.month_str(pa),
                     "twins_planned": sk._months_text(tp),
                     "a_months": None if any(g != g for g in gaps) else int(max(gaps)),
                     "online_all": es.month_str(x["month"]),
                     "stayer_planned_last": es.month_str(max(last)) if last else None,
                     "b_advanced": sum(1 for k in st if advanced(sub, k, x["month"])),
                     "not_online_mw_rows": round(float(off.reindex(st).fillna(0.0).sum()), 1),
                     "lt_not_online_mw_rows": round(float(offr.reindex(st).fillna(0.0).sum()),
                                                    1)})
    rows.sort(key=lambda d: (-d["not_online_mw_rows"], -d["lt_not_online_mw_rows"], d["plant"],
                             d["stayers"]))
    return rows


def counts(info, stay, gr, links, possible, s_months):
    linked = [k for x in links for k in x["stayers"]]
    tw = [k for x in links for k in x["twins"]]
    pos = sorted(possible)
    return {"stayers": int(len(stay)), "stayer_mw": round(float(stay["mw_last"].sum()), 1),
            "groups": len(gr), "linked_groups": len(links), "linked_stayers": len(linked),
            "linked_stayer_mw": round(float(info.loc[linked, "mw_last"].sum()), 1),
            "twins": len(tw), "twin_mw": round(float(info.loc[tw, "mw_first"].sum()), 1),
            "possible_stayers": len(pos),
            "possible_stayer_mw": round(float(info.loc[pos, "mw_last"].sum()), 1),
            "rule_s_replaced_leavers": len(s_months)}


def run(df, last_m=None):
    """Everything the job reports, as one dict (plus the hand-read keys)."""
    if last_m is None:
        last_m = int(df["report_m"].max())
    online = es.online_months(df)
    info = sk.generators(df, online)
    status = last_status(df)
    stay = stayers(info, status, last_m)
    gr = groups(stay)
    links = link(info, gr)
    months = credit(links)
    linked = {k for x in links for k in x["stayers"]}
    possible = possible_keys(info, gr)
    leave = set(sk.leavers(info, last_m).index)
    sl = sk.link(info, sk.clusters(info, last_m))
    s_months = sk.credit(sl, sk.replacement(sl, online)[0])
    s_arrivals = {k for x in sl for k in x["arrivals"]}
    both = dict(s_months)
    both.update(months)
    online_keys = set(info.index[info["online"]])
    st = set(stay.index)
    c = es.cohorts(df, last_m)
    c2, c3 = sk.rescore(c, months), sk.rescore(c, both)
    r = lt.rows(df, last_m)
    r2, r3 = sk.rescore(r, months), sk.rescore(r, both)

    def m(a, a2, a3):
        return measure(a, a2, a3, online_keys, st, leave, linked, months, possible)

    cohort = m(c, c2, c3)
    by_group = {g: m(c[c["group"] == g], c2[c2["group"] == g], c3[c3["group"] == g])
                for g in GROUPS}
    by_stage = {s: m(c[c["stage"] == s], c2[c2["stage"] == s], c3[c3["stage"] == s])
                for s in sorted(set(c["stage"]))}
    cells = {}
    for sg in lt.GRID:
        for b in lt.BAND_NAMES:
            k = (r["stage_group"] == sg) & (r["band"] == b)
            cells["%s %s" % (sg, b)] = m(r[k], r2[k], r3[k])
    l_before, l_both = lt.predictions(r), lt.predictions(r3)
    sens = []
    for tol in TOLERANCES:
        lk = link(info, gr, tol)
        mt = credit(lk)
        b = sk.bias(c, sk.rescore(c, mt), set(mt), mt, possible)
        sens.append({"tolerance": tol, "linked_groups": len(lk), "replaced_stayers": len(mt),
                     "replaced_share": lt._r4(b["replaced_share"]),
                     "on_time_after": lt._r4(b["on_time_after"]),
                     "not_online_after": lt._r4(b["not_online_after"])})
    table = link_table(links, info, df, c, r)
    res = {"counts": dict(counts(info, stay, gr, links, possible, s_months),
                          twins_also_rule_s_arrivals=len({k for x in links for k in x["twins"]}
                                                         & s_arrivals)),
           "checks": {"K1": sk.k1(c, r), "K2": k2(info, status, links, months, possible, last_m),
                      "K3": {"cohort": sk.k3(c, c2, months), "leadtime": sk.k3(r, r2, months),
                             "cohort_both": sk.k3(c, c3, both)}},
           "predictions": predictions(cohort, l_before, l_both),
           "cohort": sk.rounded(cohort),
           "by_group": [dict(part=g, **sk.rounded(v)) for g, v in by_group.items()],
           "by_stage": [dict(part=s, **sk.rounded(v)) for s, v in by_stage.items()],
           "cells": [dict(part=k, **sk.rounded(v)) for k, v in cells.items()],
           "leadtime_predictions": {"before": l_before, "both": l_both},
           "sensitivity_tolerance": sens,
           "links": table}
    k = res["checks"]
    k["all_pass"] = bool(k["K1"]["pass"] and k["K2"]["pass"] and k["K3"]["cohort"]["pass"]
                         and k["K3"]["leadtime"]["pass"] and k["K3"]["cohort_both"]["pass"])
    hand = [key for row in table[:HAND_READ]
            for key in row["stayers"].split("; ") + row["twins"].split("; ")]
    return res, hand


def write_md(path, meta, res):
    rule = ("Rule T: stayers (planned, never operating under their key, still listed as planned "
            "in the last report) at one plant and fuel family form a group; its twins are the "
            "plant's generators of that family that were planned, came online and were first "
            "listed after the group's first listing; it is linked when the twins' capacity is "
            "within %.2f of the group's, and re-scored with the month the last twin came "
            "online." % MW_TOL)
    md = ["# Planned keys still listed beside a built replacement (rule T)", "",
          "staykey %s on eia860m-slip %s, leadtime %s and splitkey %s; data %s (reports to %s). "
          "MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0." % (
              meta["version"], meta["eia860m_slip"], meta["leadtime"], meta["splitkey"],
              meta["source"], meta["report_max"]), "", rule, "",
          "## Counts", "", "```", json.dumps(res["counts"], indent=1), "```", "",
          "## Checks", "", "```", json.dumps(res["checks"], indent=1), "```", "",
          "## Predictions", "", "```", json.dumps(res["predictions"], indent=1), "```", "",
          "## 0-12-month cohort rows", ""]
    md += es.table([dict(part="all", **res["cohort"])], PART_COLS) + [""]
    md += ["## By technology group", ""] + es.table(res["by_group"], PART_COLS) + [""]
    md += ["## By stage at the report", ""] + es.table(res["by_stage"], PART_COLS) + [""]
    md += ["## Stage-by-lead cells (0-24-month rows)", ""] + es.table(res["cells"], PART_COLS)
    md += ["", "## Capacity tolerance", ""]
    md += es.table(res["sensitivity_tolerance"], ["tolerance", "linked_groups",
                                                  "replaced_stayers", "replaced_share",
                                                  "on_time_after", "not_online_after"])
    md += ["", "## Every linked group", "", "%d links." % len(res["links"]), ""]
    md += es.table(res["links"], LINK_COLS) + [""]
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
    cols = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in cols]))
    last_m = int(df["report_m"].max())
    res, hand = run(df, last_m)
    meta = {"version": __version__, "eia860m_slip": es.__version__, "leadtime": lt.__version__,
            "splitkey": sk.__version__, "source": os.path.basename(path),
            "report_max": es.month_str(last_m), "rule": {"mw_tolerance": MW_TOL}}
    with open(os.path.join(args.out_dir, "staykey.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "staykey.md"), meta, res)
    cols = [c for c in es.RECORD_COLS if c in df.columns] + ["state"]
    sel = df[df["key"].isin(hand)].sort_values(["key", "report_m"], kind="mergesort")
    sel[["key"] + cols].to_csv(os.path.join(args.out_dir, "handread_records.csv"), index=False)
    print(json.dumps({"meta": meta, "counts": res["counts"], "checks": res["checks"],
                      "predictions": res["predictions"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
