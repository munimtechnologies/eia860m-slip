"""splitkey: how much EIA-860M capacity that never came online was re-filed at the same plant
under new generator ids? A bound on one bias in every eia860m-slip delivery rate.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

eia860m_slip.py follows each generator by its key (plant id / generator id). Rule R (0.3.1)
links a plan that left EIA-860M to the same equipment filed under another plant id. It cannot
link a plan re-filed at the same plant under new generator ids (a combined-cycle block split
into its turbines, a wind farm split into phases, a generator renumbered): such a plan reads as
never online. This tool finds them with rule S and re-scores the cohort rows (0-12 months, as
eia860m_slip scores them) and the stage-by-lead rows (0-24 months, as leadtime.py reads them)
with the month the replacements came online.

Rule S (docs/split-rekey-preregistration.md):

1. A leaver is a generator with a planned record, no operating month under its key, no record
   in force in the last report (it left EIA-860M) and capacity above 0 in its last record.
2. Leavers at the same plant id and fuel family (all natural-gas groups are one family; any
   other technology group is its own; "other" is split by technology) whose last listed months
   are at most CLUSTER_GAP months apart, in order of last listed month, form one cluster.
3. A cluster's arrivals: generators at the same plant id and fuel family, not in the cluster,
   first listed after the cluster's earliest first listing, and from ARRIVE_BEFORE months
   before the cluster's earliest last listed month to ARRIVE_AFTER months after its latest.
   Clusters are taken in order of latest last listed month (then plant id, family, first key);
   an arrival taken by a linked cluster is not offered to a later one.
4. A cluster is linked when it has arrivals and their summed capacity (each in its first
   record with capacity above 0) is within MW_TOL of the cluster's (each leaver's last record).
5. A linked cluster's replacement month is the latest operating month of its arrivals, when
   every arrival has one; an arrival with none that is itself a leaver of a linked cluster
   takes that cluster's replacement month (chains are followed). Its leavers are re-scored as
   if online in that month.

Bound B: a cluster is possible when any generator at the same plant id and fuel family that
was first listed after the cluster's earliest first listing came online. Every replaced leaver
is in a possible cluster, so B bounds rule S from above.

    python splitkey.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

import eia860m_slip as es
import leadtime as lt

__version__ = "0.1.0"

CLUSTER_GAP = 3      # months between consecutive leavers' last listed months in one cluster
ARRIVE_BEFORE = 6    # months an arrival may be first listed before the cluster's first exit
ARRIVE_AFTER = 6     # months an arrival may be first listed after the cluster's last exit
MW_TOL = 0.20        # largest capacity difference, as a share of the cluster's capacity
TOLERANCES = (0.05, 0.10, 0.20, 0.30)
GROUPS = ("solar", "wind_onshore", "gas_cc", "battery", "gas_ct")
HAND_READ = 10       # linked clusters whose raw records are written out for reading by hand
# K1: the published 0-12-month cohort (docs/annual-flows-run1-slip.md, "Overall": rows, MW,
# on-time and not-online shares as printed to 3 dp) and the published stage-by-lead cells
# (docs/stage-leadtime.md: rows, generators, MW, on-time share).
PUBLISHED_COHORT = (78646, 4550498.4, 0.325, 0.192)
PUBLISHED_CELLS = {("U", "13-24"): (4138, 506, 636740.1, 0.2457),
                   ("V", "13-24"): (315, 79, 57078.8, 0.1389),
                   ("U", "00-03"): (5131, 1774, 190762.7, 0.3017),
                   ("V", "00-03"): (11795, 3421, 627147.3, 0.4088)}
SHARE_TOL = 0.00051  # a 3-dp printed share matches a value within half a unit (and float slack)
LINK_COLS = ["plant", "name", "state", "family", "leavers", "leaver_mw", "arrivals", "arrival_mw",
             "last_listed", "arrived", "planned_was", "planned_new", "online_all", "online_first",
             "not_online_mw_rows", "lt_not_online_mw_rows"]
BIAS_COLS = ["part", "rows", "mw", "not_online_mw", "linked_mw", "replaced_mw", "possible_mw",
             "replaced_share", "possible_share", "on_time_before", "on_time_after",
             "not_online_before", "not_online_after"]


def family(group, technology):
    """Fuel family of a technology group: natural gas is one family; "other" is split by
    technology description; any other group is its own family."""
    if isinstance(group, str) and group.startswith("gas_"):
        return "gas"
    if group == "other" or not isinstance(group, str):
        return "other:" + (technology.strip().lower() if isinstance(technology, str) else "")
    return group


def generators(df, online=None):
    """Per generator (index: key): plant id, fuel family, state and plant name (last record),
    first report month, last listed month, capacity in its first record with capacity above 0
    and in its last record, whether it was ever listed as planned, its first and last planned
    months, and its operating month."""
    if online is None:
        online = es.online_months(df)
    s = df.sort_values(["key", "report_m"], kind="mergesort")
    g = s.groupby("key")
    last = g.tail(1).set_index("key")
    keys = last.index
    pos = s[s["capacity_mw"] > 0].groupby("key")["capacity_mw"].first()
    plan = s[s["status"].isin(list(es.PLANNED)) & s["planned_m"].notna()].groupby("key")["planned_m"]
    planned = set(s.loc[s["status"].isin(list(es.PLANNED)), "key"])
    info = pd.DataFrame(index=keys)
    info["plant"] = [k.split("/", 1)[0] for k in keys]
    info["family"] = [family(gr, t) for gr, t in zip(last["group"], last["technology_description"])]
    info["state"] = last["state"].map(es._name)
    info["name"] = last["plant_name_eia"].map(es._name)
    info["first_m"] = g["report_m"].min()
    info["last_m"] = g["until_m"].max()
    info["mw_first"] = pos.reindex(keys).fillna(0.0)
    info["mw_last"] = last["capacity_mw"].astype(float)
    info["planned"] = [k in planned for k in keys]
    info["planned_first"] = plan.first().reindex(keys)
    info["planned_last"] = plan.last().reindex(keys)
    info["online_m"] = online.reindex(keys).astype(float)
    info["online"] = info["online_m"].notna()
    return info


def leavers(info, last_report):
    """Rule S step 1."""
    return info[info["planned"] & ~info["online"] & (info["last_m"] < last_report)
                & (info["mw_last"] > 0)]


def clusters(info, last_report):
    """Rule S step 2: one dict per cluster (plant, family, leavers, earliest and latest last
    listed month lo and hi, earliest first listing, summed last-record MW)."""
    lv = leavers(info, last_report).sort_index()
    out = []
    for (p, f), h in lv.groupby(["plant", "family"], sort=True):
        h = h.sort_values("last_m", kind="mergesort")
        groups, prev = [], None
        for k, v in zip(h.index, h["last_m"]):
            if prev is None or v - prev > CLUSTER_GAP:
                groups.append([])
            groups[-1].append(k)
            prev = v
        for ks in groups:
            out.append({"plant": p, "family": f, "leavers": ks,
                        "lo": float(h.loc[ks, "last_m"].min()),
                        "hi": float(h.loc[ks, "last_m"].max()),
                        "first": float(h.loc[ks, "first_m"].min()),
                        "mw": float(h.loc[ks, "mw_last"].sum())})
    return out


def link(info, cl, tol=MW_TOL):
    """Rule S steps 3-4: the linked clusters, each with its arrivals and their summed MW, in the
    order they were taken."""
    by = dict(tuple(info.groupby(["plant", "family"])))
    used, out = set(), []
    for x in sorted(cl, key=lambda x: (x["hi"], x["plant"], x["family"], x["leavers"][0])):
        h = by[(x["plant"], x["family"])]
        f = h["first_m"].to_numpy()
        cand = h[~h.index.isin(x["leavers"]) & (f > x["first"]) & (f >= x["lo"] - ARRIVE_BEFORE)
                 & (f <= x["hi"] + ARRIVE_AFTER)]
        arr = sorted(k for k in cand.index if k not in used)
        if not arr:
            continue
        mw = float(info.loc[arr, "mw_first"].sum())
        if abs(mw - x["mw"]) <= tol * x["mw"]:
            used.update(arr)
            out.append(dict(x, arrivals=arr, arrivals_mw=mw))
    return out


def _same(a, b):
    return (a != a and b != b) or a == b


def replacement(links, online):
    """Rule S step 5: for each link, the month all its arrivals were online (NaN if one never
    was) and, for the sensitivity, the month the first was; chains are followed."""
    member = {k: i for i, x in enumerate(links) for k in x["leavers"]}
    last = [np.nan] * len(links)
    first = [np.nan] * len(links)
    for _ in range(len(links) + 1):
        changed = False
        for i, x in enumerate(links):
            vl, vf = [], []
            for n in x["arrivals"]:
                v = float(online.get(n, np.nan))
                if v == v:
                    vl.append(v)
                    vf.append(v)
                elif n in member:
                    vl.append(last[member[n]])
                    vf.append(first[member[n]])
                else:
                    vl.append(np.nan)
                    vf.append(np.nan)
            nl = max(vl) if vl and all(v == v for v in vl) else np.nan
            got = [v for v in vf if v == v]
            nf = min(got) if got else np.nan
            if not _same(nl, last[i]) or not _same(nf, first[i]):
                last[i], first[i] = nl, nf
                changed = True
        if not changed:
            break
    return last, first


def credit(links, months):
    """Leaver key -> replacement month, for links that have one."""
    return {k: m for x, m in zip(links, months) if m == m for k in x["leavers"]}


def possible_keys(info, cl):
    """Bound B: leavers of clusters at whose plant and family a generator first listed after
    the cluster's earliest first listing came online."""
    on = info[info["online"]].groupby(["plant", "family"])["first_m"].max()
    out = set()
    for x in cl:
        m = on.get((x["plant"], x["family"]), np.nan)
        if m == m and m > x["first"]:
            out.update(x["leavers"])
    return out


def rescore(c, months):
    """Cohort rows with each credited leaver's rows scored against its replacement month."""
    c = c.copy()
    hit = c["key"].map(months).astype(float)
    on = hit.notna() & c["online_m"].isna()
    c.loc[on, "online_m"] = hit[on]
    c["slip"] = c["online_m"] - c["planned_m"]
    c["outcome"] = [es.outcome(s) for s in c["slip"]]
    return c


def _mw(f):
    return float(f["mw"].sum())


def bias(c, c2, linked, replaced, possible):
    """Unrounded: rows, MW, not-online MW, how much of it belongs to linked, replaced and
    possible leavers, and the on-time and not-online shares before and after re-scoring."""
    off = c[c["outcome"] == "not_online_12"]
    n = _mw(off)
    mw = _mw(c)

    def part(keys):
        return _mw(off[off["key"].isin(list(keys))])

    rep, pos = part(replaced), part(possible)
    return {"rows": int(len(c)), "mw": mw, "not_online_mw": n, "linked_mw": part(linked),
            "replaced_mw": rep, "possible_mw": pos,
            "replaced_share": lt._ratio(rep, n), "possible_share": lt._ratio(pos, n),
            "on_time_before": lt._ratio(_mw(c[c["outcome"] == "on_time"]), mw),
            "on_time_after": lt._ratio(_mw(c2[c2["outcome"] == "on_time"]), mw),
            "not_online_before": lt._ratio(n, mw),
            "not_online_after": lt._ratio(_mw(c2[c2["outcome"] == "not_online_12"]), mw)}


def rounded(b):
    """MW to 0.1, shares to 4 dp, for display."""
    out = {}
    for k, v in b.items():
        if isinstance(v, float):
            v = round(v, 1) if k == "mw" or k.endswith("_mw") else round(v, 4)
        out[k] = v
    return out


def k1(c, r, cohort=PUBLISHED_COHORT, cells=PUBLISHED_CELLS):
    """K1: the rebuilt rows are the published ones."""
    mw = _mw(c)
    on = lt._ratio(_mw(c[c["outcome"] == "on_time"]), mw)
    off = lt._ratio(_mw(c[c["outcome"] == "not_online_12"]), mw)
    ok_c = (int(len(c)) == cohort[0] and abs(mw - cohort[1]) <= 0.05 and on is not None
            and abs(on - cohort[2]) <= SHARE_TOL and abs(off - cohort[3]) <= SHARE_TOL)
    out = {"cohort": {"got": [int(len(c)), round(mw, 1), lt._r4(on), lt._r4(off)],
                      "published": list(cohort), "pass": bool(ok_c)}, "cells": {}}
    ok = ok_c
    for (st, b), want in sorted(cells.items()):
        got = lt.cell(r[(r["stage_group"] == st) & (r["band"] == b)])
        g = (got["rows"], got["generators"], got["mw"], got["on_time_share"])
        same = (g[0] == want[0] and g[1] == want[1] and abs(g[2] - want[2]) <= 0.05
                and g[3] == want[3])
        out["cells"]["%s %s" % (st, b)] = {"got": list(g), "published": list(want),
                                           "pass": bool(same)}
        ok = ok and same
    out["pass"] = bool(ok)
    return out


def k2(info, links, months, possible, last_report, tol=MW_TOL):
    """K2: every link obeys rule S and every replaced leaver is inside bound B."""
    lv = [k for x in links for k in x["leavers"]]
    arr = [k for x in links for k in x["arrivals"]]
    bad = sum(1 for k in lv if info.at[k, "online"] or info.at[k, "last_m"] >= last_report)
    wrong = sum(1 for x in links for k in x["leavers"] + x["arrivals"]
                if info.at[k, "plant"] != x["plant"] or info.at[k, "family"] != x["family"])
    out = {"leavers_not_leaving": int(bad), "wrong_plant_or_family": int(wrong),
           "arrivals_reused": len(arr) - len(set(arr)),
           "leaver_is_own_arrival": sum(1 for x in links if set(x["leavers"]) & set(x["arrivals"])),
           "outside_tolerance": sum(1 for x in links
                                    if abs(x["arrivals_mw"] - x["mw"]) > tol * x["mw"]),
           "replaced_outside_bound": len(set(months) - set(possible))}
    out["pass"] = all(v == 0 for v in out.values())
    return out


def k3(c, c2, months):
    """K3: re-scoring keeps the rows and MW, its outcomes add up, and only credited leavers'
    rows change."""
    parts = sum(_mw(c2[c2["outcome"] == o]) for o in es.OUTCOMES)
    changed = c["outcome"].to_numpy() != c2["outcome"].to_numpy()
    stray = int((changed & ~c2["key"].isin(list(months)).to_numpy()).sum())
    out = {"rows": [int(len(c)), int(len(c2))], "mw": [round(_mw(c), 1), round(_mw(c2), 1)],
           "adds_up": bool(abs(parts - _mw(c2)) < 0.05), "rows_changed": int(changed.sum()),
           "stray_changes": stray}
    out["pass"] = bool(len(c) == len(c2) and abs(_mw(c) - _mw(c2)) < 0.05 and out["adds_up"]
                       and stray == 0)
    return out


def predictions(cohort, groups, u13, l_before, l_after):
    """S1-S5 from unrounded measures (cohort: the 0-12-month rows; groups: by technology group;
    u13: the U 13-24 cell; l_before / l_after: leadtime.predictions before and after)."""
    s1 = cohort["replaced_share"]
    out = {"S1": {"replaced_share": lt._r4(s1), "range": [0.03, 0.20],
                  "held": None if s1 is None else 0.03 <= s1 <= 0.20}}
    a, b = cohort["on_time_before"], cohort["on_time_after"]
    rise = None if a is None or b is None else b - a
    out["S2"] = {"on_time_before": lt._r4(a), "on_time_after": lt._r4(b), "rise": lt._r4(rise),
                 "ceiling": 0.02, "held": None if rise is None else rise < 0.02}
    u, w = u13["replaced_share"], cohort["replaced_share"]
    out["S3"] = {"U_13_24": lt._r4(u), "cohort": lt._r4(w),
                 "held": None if u is None or w is None else u > w}
    g = {k: groups[k]["replaced_share"] for k in ("gas_cc", "solar", "wind_onshore", "battery")}
    out["S4"] = {"replaced_share": {k: lt._r4(v) for k, v in g.items()},
                 "held": None if any(v is None for v in g.values())
                 else all(g["gas_cc"] > g[k] for k in ("solar", "wind_onshore", "battery"))}
    same = {k: l_before[k]["held"] == l_after[k]["held"] for k in sorted(l_before)}
    out["S5"] = {"before": {k: l_before[k]["held"] for k in sorted(l_before)},
                 "after": {k: l_after[k]["held"] for k in sorted(l_after)},
                 "unchanged": same, "held": all(same.values())}
    return out


def _months_text(vals):
    got = [v for v in vals if v == v]
    return es.month_str(min(got)) if got else None


def link_table(links, last, first, info, c, r):
    """One row per linked cluster, most not-online MW (0-12-month rows) first."""
    off = c[c["outcome"] == "not_online_12"].groupby("key")["mw"].sum()
    offr = r[r["outcome"] == "not_online_12"].groupby("key")["mw"].sum()
    rows = []
    for x, ml, mf in zip(links, last, first):
        lv, ar = x["leavers"], x["arrivals"]
        was = [v for v in info.loc[lv, "planned_last"] if v == v]
        rows.append({"plant": x["plant"], "name": info.at[lv[0], "name"],
                     "state": info.at[lv[0], "state"], "family": x["family"],
                     "leavers": "; ".join(lv), "leaver_mw": round(x["mw"], 1),
                     "arrivals": "; ".join(ar), "arrival_mw": round(x["arrivals_mw"], 1),
                     "last_listed": es.month_str(x["hi"]),
                     "arrived": _months_text(info.loc[ar, "first_m"]),
                     "planned_was": es.month_str(max(was)) if was else None,
                     "planned_new": _months_text(info.loc[ar, "planned_first"]),
                     "online_all": es.month_str(ml), "online_first": es.month_str(mf),
                     "not_online_mw_rows": round(float(off.reindex(lv).fillna(0.0).sum()), 1),
                     "lt_not_online_mw_rows": round(float(offr.reindex(lv).fillna(0.0).sum()), 1)})
    rows.sort(key=lambda d: (-d["not_online_mw_rows"], -d["lt_not_online_mw_rows"], d["plant"],
                             d["leavers"]))
    return rows


def counts(info, cl, links, months, possible, last_report):
    lv = leavers(info, last_report)
    linked = [k for x in links for k in x["leavers"]]
    return {"leavers": int(len(lv)), "leaver_mw": round(float(lv["mw_last"].sum()), 1),
            "clusters": len(cl), "linked_clusters": len(links), "linked_leavers": len(linked),
            "linked_leaver_mw": round(float(info.loc[linked, "mw_last"].sum()), 1),
            "replaced_leavers": len(months),
            "replaced_leaver_mw": round(float(info.loc[list(months), "mw_last"].sum()), 1),
            "possible_leavers": len(possible),
            "possible_leaver_mw": round(float(info.loc[list(possible), "mw_last"].sum()), 1)}


def run(df, last_m=None):
    """Everything the job reports, as one dict (plus the hand-read keys)."""
    if last_m is None:
        last_m = int(df["report_m"].max())
    online = es.online_months(df)
    info = generators(df, online)
    cl = clusters(info, last_m)
    links = link(info, cl)
    last, first = replacement(links, online)
    months = credit(links, last)
    linked = {k for x in links for k in x["leavers"]}
    possible = possible_keys(info, cl)
    c = es.cohorts(df, last_m)
    c2 = rescore(c, months)
    r = lt.rows(df, last_m)
    r2 = rescore(r, months)
    cohort = bias(c, c2, linked, months, possible)
    groups = {g: bias(c[c["group"] == g], c2[c2["group"] == g], linked, months, possible)
              for g in GROUPS}
    stages = {s: bias(c[c["stage"] == s], c2[c2["stage"] == s], linked, months, possible)
              for s in sorted(set(c["stage"]))}
    cells = {}
    for st in lt.GRID:
        for b in lt.BAND_NAMES:
            m = (r["stage_group"] == st) & (r["band"] == b)
            cells["%s %s" % (st, b)] = bias(r[m], r2[m], linked, months, possible)
    l_before, l_after = lt.predictions(r), lt.predictions(r2)
    sens = []
    for tol in TOLERANCES:
        lk = link(info, cl, tol)
        mt = credit(lk, replacement(lk, online)[0])
        b = bias(c, rescore(c, mt), {k for x in lk for k in x["leavers"]}, mt, possible)
        sens.append({"tolerance": tol, "linked_clusters": len(lk), "replaced_leavers": len(mt),
                     "replaced_share": lt._r4(b["replaced_share"]),
                     "on_time_after": lt._r4(b["on_time_after"]),
                     "not_online_after": lt._r4(b["not_online_after"])})
    mf = credit(links, first)
    bf = bias(c, rescore(c, mf), linked, mf, possible)
    table = link_table(links, last, first, info, c, r)
    res = {"counts": counts(info, cl, links, months, possible, last_m),
           "checks": {"K1": k1(c, r), "K2": k2(info, links, months, possible, last_m),
                      "K3": {"cohort": k3(c, c2, months), "leadtime": k3(r, r2, months)}},
           "predictions": predictions(cohort, groups, cells["U 13-24"], l_before, l_after),
           "cohort": rounded(cohort),
           "by_group": [dict(part=g, **rounded(v)) for g, v in groups.items()],
           "by_stage": [dict(part=s, **rounded(v)) for s, v in stages.items()],
           "cells": [dict(part=k, **rounded(v)) for k, v in cells.items()],
           "leadtime_predictions": {"before": l_before, "after": l_after},
           "sensitivity_tolerance": sens,
           "sensitivity_first_online": {"on_time_after": lt._r4(bf["on_time_after"]),
                                        "not_online_after": lt._r4(bf["not_online_after"])},
           "links": table}
    k = res["checks"]
    k["all_pass"] = bool(k["K1"]["pass"] and k["K2"]["pass"] and k["K3"]["cohort"]["pass"]
                         and k["K3"]["leadtime"]["pass"])
    hand = [key for row in table[:HAND_READ]
            for key in row["leavers"].split("; ") + row["arrivals"].split("; ")]
    return res, hand


def write_md(path, meta, res):
    rule = ("Rule S: leavers (planned, never operating under their key, gone from EIA-860M) at "
            "one plant and fuel family whose exits are at most %d months apart form a cluster; "
            "its arrivals are the plant's generators of that family first listed after the "
            "cluster's first listing and from %d months before its first exit to %d months "
            "after its last; it is linked when the arrivals' capacity is within %.2f of the "
            "cluster's, and re-scored with the month the last arrival came online."
            % (CLUSTER_GAP, ARRIVE_BEFORE, ARRIVE_AFTER, MW_TOL))
    md = ["# Plans re-filed at the same plant under new generator ids (rule S)", "",
          "splitkey %s on eia860m-slip %s and leadtime %s; data %s (reports to %s). MV2 of "
          "Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0." % (
              meta["version"], meta["eia860m_slip"], meta["leadtime"], meta["source"],
              meta["report_max"]), "", rule, "",
          "## Counts", "", "```", json.dumps(res["counts"], indent=1), "```", "",
          "## Checks", "", "```", json.dumps(res["checks"], indent=1), "```", "",
          "## Predictions", "", "```", json.dumps(res["predictions"], indent=1), "```", "",
          "## 0-12-month cohort rows", ""]
    md += es.table([dict(part="all", **res["cohort"])], BIAS_COLS) + [""]
    md += ["## By technology group", ""] + es.table(res["by_group"], BIAS_COLS) + [""]
    md += ["## By stage at the report", ""] + es.table(res["by_stage"], BIAS_COLS) + [""]
    md += ["## Stage-by-lead cells (0-24-month rows)", ""] + es.table(res["cells"], BIAS_COLS)
    md += ["", "## Capacity tolerance", ""]
    md += es.table(res["sensitivity_tolerance"], ["tolerance", "linked_clusters",
                                                  "replaced_leavers", "replaced_share",
                                                  "on_time_after", "not_online_after"])
    md += ["", "Crediting the first arrival's month instead of the last: %s" %
           json.dumps(res["sensitivity_first_online"]), "",
           "## Every linked cluster", "", "%d links." % len(res["links"]), ""]
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
            "source": os.path.basename(path), "report_max": es.month_str(last_m),
            "rule": {"cluster_gap": CLUSTER_GAP, "arrive_before": ARRIVE_BEFORE,
                     "arrive_after": ARRIVE_AFTER, "mw_tolerance": MW_TOL}}
    with open(os.path.join(args.out_dir, "splitkey.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "splitkey.md"), meta, res)
    cols = [c for c in es.RECORD_COLS if c in df.columns] + ["state"]
    sel = df[df["key"].isin(hand)].sort_values(["key", "report_m"], kind="mergesort")
    sel[["key"] + cols].to_csv(os.path.join(args.out_dir, "handread_records.csv"), index=False)
    print(json.dumps({"meta": meta, "counts": res["counts"], "checks": res["checks"],
                      "predictions": res["predictions"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
