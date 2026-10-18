"""storage_flows: where the 2026 battery storage plan went in EIA-860M, beside solar.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

plan_flows.py 0.1.0 followed the December 2025 report's 2026 solar book (43.65 GW) to the
August 2026 report (docs/plan-flows.md). EIA's Today in Energy of 20 February 2026 put planned
2026 battery additions at 24 GW from the same inventory. This reads batteries exactly as
plan_flows reads solar, with plan_flows 0.1.0's own functions unchanged, and asks one new
question: does a battery that shares a plant with a 2026 solar generator share its fate?

Paired: the battery's plant also has a solar generator in the December 2025 2026 book. The
plant's lead solar generator is its largest one in that book (ties by id); its August state is
compared with the battery's, in four groups: online_2026, planned_2026, planned_later, other.

Checks and predictions: docs/storage-flows-preregistration.md.

    python storage_flows.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import json
import os

import pandas as pd

import plan_flows as pf

VERSION = "0.1.0"
BATTERY = "batteries"
pf.TECH.setdefault(BATTERY, ("batteries",))  # plan_flows 0.1.0 reads solar and wind only
GROUPS = ("online_2026", "planned_2026", "planned_later", "other")
# EIA, Today in Energy 67205 (2026-02-20): "Developers plan to add 24 GW of utility-scale battery storage".
EIA_BATTERY_2026 = 24.0
# plan_flows-v1's December 2025 solar book in August 2026, GW (docs/plan-flows.md), for check K3.
SOLAR_V1 = {"base_book": 43.65, "online_2026": 12.58, "planned_2026": 20.71, "planned_later": 7.63,
            "not_listed": 2.29}
# Stated before the job ran (docs/storage-flows-preregistration.md).
K1_TOL, K2_TOL, K3_TOL, K4_TOL = 0.001, 0.01, 0.01, 0.15
B1_SLIP, B2_ONLINE, B4_EARLY, B4_BUILDING, B5_JOINED, B6_AGREE = 0.175, 0.35, 0.40, 0.10, 0.15, 0.75


def group(state):
    return state if state in GROUPS[:3] else "other"


def lead_states(sol_base, sol_latest):
    """Plant -> group, in the latest report, of the plant's largest solar generator in the base 2026 book."""
    sb = sol_base[sol_base["state"].isin(pf.IN_BOOK)]
    sb = sb.assign(k=sb.index).sort_values(["plant", "cap", "k"], ascending=[True, False, True], kind="mergesort")
    lead = sb.groupby("plant").head(1)
    return {p: group(sol_latest["state"].get(k, "not_listed")) for p, k in zip(lead["plant"], lead["k"])}


def paired(bat_base, bat_latest, sol_base, sol_latest):
    """The base battery book in the latest report, split by whether the plant has 2026 solar.

    matrix[battery group][lead solar group], GW at base capacity."""
    lead = lead_states(sol_base, sol_latest)
    bb = bat_base[bat_base["state"].isin(pf.IN_BOOK)]
    matrix = {b: {s: 0.0 for s in GROUPS} for b in GROUPS}
    alone = {s: 0.0 for s in GROUPS}
    units = {"paired": 0, "alone": 0}
    for k in bb.index:
        p, cap = bb.at[k, "plant"], float(bb.at[k, "cap"]) / 1000.0
        g = group(bat_latest["state"].get(k, "not_listed"))
        if p in lead:
            matrix[g][lead[p]] += cap
            units["paired"] += 1
        else:
            alone[g] += cap
            units["alone"] += 1
    total = sum(sum(r.values()) for r in matrix.values())
    agree = sum(matrix[s][s] for s in GROUPS)
    return {"matrix": matrix, "paired_gw": total, "agree_gw": agree, "agree_share": agree / total if total else 0.0,
            "alone": alone, "alone_gw": sum(alone.values()), "units": units}


def stage_shares(fate):
    """Shares of the base book's building (U, V, TS) and early (P, L) capacity by latest state."""
    st, out = fate["by_base_status"], {}
    for name, codes in (("building", pf.BUILDING), ("early", pf.EARLY)):
        rows = [st[c] for c in codes if c in st]
        base = sum(r["base_gw"] for r in rows)
        part = lambda *keys: sum(r[k] for r in rows for k in keys) / base if base else 0.0  # noqa: E731
        out[name] = {"base_gw": base, "online_share": part("online_2026"), "still_share": part("planned_2026"),
                     "later_share": part("planned_later"), "gone_share": part("not_listed", "other_status")}
    return out


def movers(gens, n=10):
    """The largest generators that were in the base book and are not in the latest one."""
    out = [g for g in gens if g["base_state"] in pf.IN_BOOK and g["latest_state"] not in pf.IN_BOOK]
    return sorted(out, key=lambda g: (-float(g["base_summer_mw"]), g["plant_id_eia"], g["generator_id"]))[:n]


def summarize(flows, fate, sfate, stages, pair):
    """Checks and the numbers each prediction needs; every verdict is re-read by hand."""
    s = {"version": VERSION, "checks": {}, "predictions": {}}
    worst = max((abs(f["residual"]) for f in flows), default=0.0)
    s["checks"]["K1"] = {"pairs": len(flows), "largest_residual_gw": round(worst, 6), "passed": worst <= K1_TOL}
    total = sum(fate["fate"].values())
    s["checks"]["K2"] = {"fate_sum_gw": round(total, 4), "base_book_gw": round(fate["base_book"], 4),
                         "passed": abs(total - fate["base_book"]) <= K2_TOL}
    got = {k: (sfate["base_book"] if k == "base_book" else sfate["fate"][k]) for k in SOLAR_V1}
    diffs = {k: round(got[k] - v, 4) for k, v in SOLAR_V1.items()}
    s["checks"]["K3"] = {"differences_gw": diffs, "passed": all(abs(d) <= K3_TOL for d in diffs.values())}
    off = (fate["base_book"] - EIA_BATTERY_2026) / EIA_BATTERY_2026
    s["checks"]["K4"] = {"base_book_gw": round(fate["base_book"], 3), "eia_gw": EIA_BATTERY_2026,
                         "relative_difference": round(off, 4), "passed": abs(off) <= K4_TOL}
    p, f, base = s["predictions"], fate["fate"], fate["base_book"]
    share = lambda x: x / base if base else 0.0  # noqa: E731
    p["B1"] = {"planned_later_gw": round(f["planned_later"], 3), "share": round(share(f["planned_later"]), 4),
               "held": share(f["planned_later"]) >= B1_SLIP}
    p["B2"] = {"online_gw": round(f["online_2026"], 3), "share": round(share(f["online_2026"]), 4),
               "held": share(f["online_2026"]) < B2_ONLINE}
    gone = f["other_status"] + f["not_listed"]
    p["B3"] = {"cancelled_or_unlisted_gw": round(gone, 3), "planned_later_gw": round(f["planned_later"], 3),
               "held": gone < f["planned_later"]}
    b, e = stages["building"], stages["early"]
    p["B4"] = {"building_later_share": round(b["later_share"], 4), "early_later_share": round(e["later_share"], 4),
               "held": e["later_share"] >= B4_EARLY and b["later_share"] <= B4_BUILDING}
    joined = fate["entries_total"] / fate["latest_book"] if fate["latest_book"] else 0.0
    p["B5"] = {"joined_gw": round(fate["entries_total"], 3), "latest_book_gw": round(fate["latest_book"], 3),
               "share": round(joined, 4), "held": joined >= B5_JOINED}
    p["B6"] = {"paired_gw": round(pair["paired_gw"], 3), "agree_gw": round(pair["agree_gw"], 3),
               "share": round(pair["agree_share"], 4), "held": pair["agree_share"] >= B6_AGREE}
    return s


def run(df):
    last = int(df["report_m"].max())
    latest_m = min(pf.TARGET_REPORT, last)
    reports = list(range(pf.FIRST_REPORT, last + 1))
    bst = {m: pf.states(df, m, BATTERY) for m in reports}
    book = {pf.month_str(m): round(pf.gw(bst[m].loc[bst[m]["state"].isin(pf.IN_BOOK), "cap"]), 4) for m in reports}
    flows = []
    for a, b in zip(reports, reports[1:]):
        f = pf.split(bst[a], bst[b])
        f["report"] = pf.month_str(b)
        flows.append(f)
    sol_base, sol_latest = pf.states(df, pf.BASE_REPORT), pf.states(df, latest_m)
    fate = pf.book_fate(bst[pf.BASE_REPORT], bst[latest_m])
    sfate = pf.book_fate(sol_base, sol_latest)
    stages = stage_shares(fate)
    pair = paired(bst[pf.BASE_REPORT], bst[latest_m], sol_base, sol_latest)
    s = summarize(flows, fate, sfate, stages, pair)
    s.update({"last_report": pf.month_str(last), "base_report": pf.month_str(pf.BASE_REPORT),
              "latest_report_used": pf.month_str(latest_m), "plan_flows_version": pf.VERSION})
    gens = pf.generator_rows(bst[pf.BASE_REPORT], bst[latest_m], pf.BASE_REPORT, latest_m)
    return flows, fate, stages, pair, s, gens, book, latest_m


def render(flows, fate, stages, pair, s, gens, census, base_m, latest_m):
    b, l = pf.month_str(base_m), pf.month_str(latest_m)  # noqa: E741
    md = ["# Where the 2026 battery storage plan went (storage_flows %s, plan_flows %s)" % (VERSION, pf.VERSION), "",
          "EIA-860M (PUDL changelog), technology 'Batteries', GW net summer capacity, read exactly as "
          "plan_flows reads solar. The 2026 book = online in 2026 by the report month + still planned for a "
          "2026 month. change = entries - exits + resize.", "",
          "Technology names containing 'batter' or 'stor' in the changelog (records): " + json.dumps(census), "",
          "## The %s battery book in %s" % (b, l), "",
          "%.2f GW in %s; %.2f GW in %s." % (fate["base_book"], b, fate["latest_book"], l), "",
          "| state in %s | GW (at %s capacity) | generators |" % (l, b), "|---|---:|---:|"]
    for st in pf.STATES:
        md.append("| %s | %.2f | %d |" % (st, fate["fate"][st], fate["fate_units"][st]))
    md += ["", "Joined the book since %s (GW at %s capacity, by state in %s): %s; total %.2f GW in %d generators, "
           "%.2f GW of it already online. Resize of generators in both books: %+.2f GW." % (
               b, l, b, ", ".join("%s %.2f" % (k, v) for k, v in fate["entries"].items()), fate["entries_total"],
               fate["entries_units"], fate["entries_online"], fate["resize"]),
           "", "Other statuses (GW): %s" % json.dumps({k: pf.r3(v) for k, v in fate["other_status_codes"].items()}),
           "", "By status in %s:" % b, "",
           "| status | GW | generators | " + " | ".join(pf.STATES) + " |", "|---|---:|---:|" + "---:|" * len(pf.STATES)]
    for code, row in fate["by_base_status"].items():
        md.append("| %s | %.2f | %d | " % (code, row["base_gw"], row["units"])
                  + " | ".join("%.2f" % row[st] for st in pf.STATES) + " |")
    md += ["", "| stage in %s | GW | online | still 2026 | 2027+ | not listed or other status |" % b,
           "|---|---:|---:|---:|---:|---:|"]
    for name, row in stages.items():
        md.append("| %s | %.2f | %.1f%% | %.1f%% | %.1f%% | %.1f%% |" % (
            name, row["base_gw"], 100 * row["online_share"], 100 * row["still_share"], 100 * row["later_share"],
            100 * row["gone_share"]))
    md += ["", "## Batteries beside 2026 solar", "",
           "Paired (plant also has solar in the %s 2026 book): %.2f GW in %d generators; alone: %.2f GW in %d. "
           "Same group as the plant's lead solar generator in %s: %.2f GW (%.1f%%)." % (
               b, pair["paired_gw"], pair["units"]["paired"], pair["alone_gw"], pair["units"]["alone"], l,
               pair["agree_gw"], 100 * pair["agree_share"]), "",
           "| battery in %s \\ lead solar in %s | " % (l, l) + " | ".join(GROUPS) + " |", "|---|" + "---:|" * len(GROUPS)]
    for g in GROUPS:
        md.append("| %s | " % g + " | ".join("%.2f" % pair["matrix"][g][x] for x in GROUPS) + " |")
    md += ["", "Alone, by group in %s (GW): %s" % (l, ", ".join("%s %.2f" % (k, v) for k, v in pair["alone"].items())),
           "", "## Month by month (batteries)", "",
           "| report | book | change | entries | from not listed | from 2027+ | exits | to 2027+ | to not listed | "
           "to other status | resize | came online |", "|---|" + "---:|" * 11]
    for f in flows:
        md.append("| %s | %.2f | %+.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %+.2f | %.2f |" % (
            f["report"], f["book_cur"], f["book_cur"] - f["book_prev"], f["entries"], f["in_not_listed"],
            f["in_planned_later"], f["exits"], f["out_planned_later"], f["out_not_listed"], f["out_other_status"],
            f["resize"], f["came_online"]))
    md += ["", "## Largest generators that left the %s book by %s" % (b, l), "",
           "| plant | generator | %s status | %s planned | MW | %s state | %s planned |" % (b, b, l, l),
           "|---|---|---|---|---:|---|---|"]
    for g in movers(gens):
        md.append("| %s | %s | %s | %s | %.1f | %s | %s |" % (
            g["plant_id_eia"], g["generator_id"], g["base_status"], g["base_planned"], float(g["base_summer_mw"]),
            g["latest_state"], g["latest_planned"]))
    md += ["", "## Checks and prediction aids (scored by hand against the pre-registration)", "", "```",
           json.dumps({"checks": s["checks"], "predictions": s["predictions"]}, indent=1), "```", ""]
    return "\n".join(md)


def tech_census(raw):
    t = raw["technology_description"].astype(str)
    hit = t[t.str.contains("batter|stor", case=False, regex=True)]
    return {k: int(v) for k, v in hit.value_counts().sort_index().items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    path = pf.find_parquet(a.data_dir)
    if not path:
        raise SystemExit("no changelog_generators parquet under %s" % a.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in pf.COLUMNS if c in names])
    census = tech_census(raw)
    df = pf.prepare(raw)
    flows, fate, stages, pair, s, gens, book, latest_m = run(df)
    s.update({"parquet": os.path.basename(path), "raw_records": int(len(raw)), "technology_census": census,
              "missing_columns": [c for c in pf.COLUMNS if c not in names]})
    with open(os.path.join(a.out_dir, "storage_flows.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": s, "book": book, "flows": flows, "fate": fate, "stages": stages, "paired": pair},
                  fh, indent=1)
    keys = [k for k in flows[0] if k not in ("out_other_status_codes", "report")] if flows else []
    with open(os.path.join(a.out_dir, "storage_flows.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["report"] + keys, extrasaction="ignore")
        w.writeheader()
        for f in flows:
            w.writerow({k: (pf.r3(v) if isinstance(v, float) else v) for k, v in f.items()})
    with open(os.path.join(a.out_dir, "storage_flows_generators.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gens[0].keys()) if gens else ["plant_id_eia"])
        w.writeheader()
        w.writerows(gens)
    md = render(flows, fate, stages, pair, s, gens, census, pf.BASE_REPORT, latest_m)
    with open(os.path.join(a.out_dir, "storage_flows.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
