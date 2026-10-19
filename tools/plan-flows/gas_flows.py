"""gas_flows: where the 2026 natural gas plan went in EIA-860M, beside solar, wind and batteries.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

plan_flows.py 0.1.0 followed the December 2025 report's 2026 solar book to the August 2026
report (docs/plan-flows.md); storage_flows.py 0.1.0 did the same for batteries
(docs/storage-flows.md). EIA's Today in Energy of 20 February 2026 (article 67205) put planned
2026 natural gas additions at 6.3 GW from the same inventory (3.3 GW combined cycle, 2.8 GW
combustion turbine) and named Orange County Advanced Power Station (Texas, 1,158 MW) and
Trumbull Energy Center (Ohio, 900 MW) as the two largest. This reads natural gas generators
exactly as plan_flows reads solar, with plan_flows 0.1.0's own functions unchanged, splits
them by prime mover (combined cycle, combustion turbine, other), prints the raw records of the
two named plants, and puts the four technologies side by side.

Checks and predictions: docs/gas-flows-preregistration.md.

    python gas_flows.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import json
import os

import pandas as pd

import plan_flows as pf

VERSION = "0.1.0"
GAS = "gas"
BATTERY = "batteries"
# EIA technology descriptions; "Natural Gas with Compressed Air Storage" is storage, not read.
GAS_NAMES = ("natural gas fired combined cycle", "natural gas fired combustion turbine",
             "natural gas internal combustion engine", "natural gas steam turbine", "other natural gas")
SUBTYPE = {"natural gas fired combined cycle": "cc", "natural gas fired combustion turbine": "ct"}
SUBTYPES = ("cc", "ct", "other")
pf.TECH.setdefault(BATTERY, ("batteries",))  # plan_flows 0.1.0 reads solar and wind only
pf.TECH.setdefault(GAS, GAS_NAMES)
TECHS = ("solar", "wind", BATTERY, GAS)
# Plants EIA named (article 67205); matched on plant_name_eia, lower case.
NAMED = {"trumbull": "trumbull energy", "orange_county": "orange county advanced power"}
EIA_GAS_2026 = 6.3
# The December 2025 2026 books in August 2026, GW, as published (docs/plan-flows.md for solar and wind,
# docs/storage-flows.md for batteries), for check K3.
PRIOR = {"solar": {"base_book": 43.65, "online_2026": 12.58, "planned_2026": 20.71, "planned_later": 7.63,
                   "not_listed": 2.29},
         "wind": {"base_book": 12.12, "online_2026": 6.48, "planned_2026": 2.85, "planned_later": 2.39,
                  "not_listed": 0.0},
         BATTERY: {"base_book": 24.28, "online_2026": 9.57, "planned_2026": 8.69, "planned_later": 3.65,
                   "not_listed": 1.88}}
# Stated before the job ran (docs/gas-flows-preregistration.md).
K1_TOL, K2_TOL, K3_TOL, K4_TOL = 0.001, 0.01, 0.01, 0.20
G1_ONLINE, G2_LATER, G3_GONE, G5_EARLY, G5_BUILDING = 0.30, 0.175, 0.052, 0.40, 0.10


def subtypes(df):
    """Each gas generator's prime-mover group from its latest record: cc, ct or other."""
    g = df[df["tech"] == GAS].sort_values(["key", "report_m"], kind="mergesort").groupby("key").tail(1)
    text = g["technology_description"].astype(str).str.strip().str.lower()
    return {k: SUBTYPE.get(t, "other") for k, t in zip(g["key"], text)}


def sub_frame(frame, sub, code):
    return frame.loc[[k for k in frame.index if sub.get(k) == code]]


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


def plant_ids(raw):
    return pd.to_numeric(raw["plant_id_eia"], errors="coerce").astype("Int64").astype(str)


def plant_names(raw):
    """Plant id (as plan_flows writes it) -> plant_name_eia, last record wins; empty without the column."""
    if "plant_name_eia" not in raw.columns:
        return {}
    return dict(zip(plant_ids(raw), raw["plant_name_eia"].astype(str)))


def named(names, gens):
    """The named plants' generators in either 2026 gas book, by their generator_rows."""
    out = {}
    for label, pattern in NAMED.items():
        plants = {p: n for p, n in names.items() if pattern in n.lower()}
        out[label] = {"pattern": pattern, "plants": plants,
                      "generators": [g for g in gens if g["plant_id_eia"] in plants]}
    return out


def named_records(raw, named_out):
    """Every raw changelog record of the named plants, as text, sorted by plant, generator and report."""
    cols = [c for c in pf.COLUMNS if c in raw.columns] + (["plant_name_eia"] if "plant_name_eia" in raw.columns else [])
    pid = plant_ids(raw)
    for label, item in named_out.items():
        rows = raw.loc[pid.isin(list(item["plants"])), cols].copy()
        rows["plant_id_eia"] = pid[rows.index]
        rows = rows.sort_values(["plant_id_eia", "generator_id", "report_date"], kind="mergesort")
        item["records"] = [{c: ("" if pd.isna(v) else str(v)[:10] if "date" in c else str(v)) for c, v in r.items()}
                           for r in rows.to_dict("records")]


def summarize(flows, fate, cross, stages, subs, named_out):
    """Checks and the numbers each prediction needs; every verdict is re-read by hand."""
    s = {"version": VERSION, "checks": {}, "predictions": {}}
    worst = max((abs(f["residual"]) for f in flows), default=0.0)
    s["checks"]["K1"] = {"pairs": len(flows), "largest_residual_gw": round(worst, 6), "passed": worst <= K1_TOL}
    total = sum(fate["fate"].values())
    s["checks"]["K2"] = {"fate_sum_gw": round(total, 4), "base_book_gw": round(fate["base_book"], 4),
                         "passed": abs(total - fate["base_book"]) <= K2_TOL}
    diffs = {}
    for tech, prior in PRIOR.items():
        got = {k: (cross[tech]["base_book"] if k == "base_book" else cross[tech]["fate"][k]) for k in prior}
        diffs[tech] = {k: round(got[k] - v, 4) for k, v in prior.items()}
    s["checks"]["K3"] = {"differences_gw": diffs,
                         "passed": all(abs(d) <= K3_TOL for t in diffs.values() for d in t.values())}
    off = (fate["base_book"] - EIA_GAS_2026) / EIA_GAS_2026
    s["checks"]["K4"] = {"base_book_gw": round(fate["base_book"], 3), "eia_gw": EIA_GAS_2026,
                         "relative_difference": round(off, 4), "passed": abs(off) <= K4_TOL}
    p, f, base = s["predictions"], fate["fate"], fate["base_book"]
    share = lambda x: x / base if base else 0.0  # noqa: E731
    p["G1"] = {"online_gw": round(f["online_2026"], 3), "share": round(share(f["online_2026"]), 4),
               "held": share(f["online_2026"]) >= G1_ONLINE}
    p["G2"] = {"planned_later_gw": round(f["planned_later"], 3), "share": round(share(f["planned_later"]), 4),
               "held": share(f["planned_later"]) <= G2_LATER}
    gone = f["other_status"] + f["not_listed"]
    p["G3"] = {"cancelled_or_unlisted_gw": round(gone, 3), "share": round(share(gone), 4),
               "held": share(gone) < G3_GONE}
    sub_share = {c: (subs[c]["fate"]["online_2026"] / subs[c]["base_book"] if subs[c]["base_book"] else 0.0)
                 for c in ("cc", "ct")}
    p["G4"] = {"cc_base_gw": round(subs["cc"]["base_book"], 3), "cc_online_share": round(sub_share["cc"], 4),
               "ct_base_gw": round(subs["ct"]["base_book"], 3), "ct_online_share": round(sub_share["ct"], 4),
               "held": sub_share["cc"] >= sub_share["ct"]}
    b, e = stages["building"], stages["early"]
    p["G5"] = {"early_left_share": round(e["later_share"] + e["gone_share"], 4),
               "building_later_share": round(b["later_share"], 4),
               "held": e["later_share"] + e["gone_share"] >= G5_EARLY and b["later_share"] <= G5_BUILDING}
    tr = named_out["trumbull"]["generators"]
    oc = named_out["orange_county"]["generators"]
    p["G6"] = {"trumbull": [(g["generator_id"], g["latest_state"], g["latest_online"]) for g in tr],
               "orange_county": [(g["generator_id"], g["latest_state"], g["latest_planned"]) for g in oc],
               "held": bool(tr) and bool(oc)
               and all(g["latest_state"] == "online_2026" and g["latest_online"].startswith("2026") for g in tr)
               and all(g["latest_state"] == "planned_2026" for g in oc)}
    return s


def run(df, names):
    last = int(df["report_m"].max())
    latest_m = min(pf.TARGET_REPORT, last)
    reports = list(range(pf.FIRST_REPORT, last + 1))
    gst = {m: pf.states(df, m, GAS) for m in reports}
    book = {pf.month_str(m): round(pf.gw(gst[m].loc[gst[m]["state"].isin(pf.IN_BOOK), "cap"]), 4) for m in reports}
    flows = []
    for a, b in zip(reports, reports[1:]):
        f = pf.split(gst[a], gst[b])
        f["report"] = pf.month_str(b)
        flows.append(f)
    cross = {}
    for tech in TECHS:
        base = gst[pf.BASE_REPORT] if tech == GAS else pf.states(df, pf.BASE_REPORT, tech)
        latest = gst[latest_m] if tech == GAS else pf.states(df, latest_m, tech)
        cross[tech] = pf.book_fate(base, latest)
    fate = cross[GAS]
    stages = stage_shares(fate)
    sub = subtypes(df)
    subs = {c: pf.book_fate(sub_frame(gst[pf.BASE_REPORT], sub, c), sub_frame(gst[latest_m], sub, c))
            for c in SUBTYPES}
    gens = pf.generator_rows(gst[pf.BASE_REPORT], gst[latest_m], pf.BASE_REPORT, latest_m)
    for g in gens:
        g["subtype"] = sub.get(g["plant_id_eia"] + "/" + g["generator_id"], "")
    named_out = named(names, gens)
    s = summarize(flows, fate, cross, stages, subs, named_out)
    s.update({"last_report": pf.month_str(last), "base_report": pf.month_str(pf.BASE_REPORT),
              "latest_report_used": pf.month_str(latest_m), "plan_flows_version": pf.VERSION})
    return flows, fate, cross, stages, subs, named_out, s, gens, book, latest_m


def left_share(f):
    out = sum(f["fate"][s] for s in pf.OUT_STATES)
    return out / f["base_book"] if f["base_book"] else 0.0


def render(flows, fate, cross, stages, subs, named_out, s, gens, census, base_m, latest_m):
    b, l = pf.month_str(base_m), pf.month_str(latest_m)  # noqa: E741
    md = ["# Where the 2026 natural gas plan went (gas_flows %s, plan_flows %s)" % (VERSION, pf.VERSION), "",
          "EIA-860M (PUDL changelog), GW net summer capacity, read exactly as plan_flows reads solar. "
          "Natural gas = " + ", ".join(GAS_NAMES) + ". The 2026 book = online in 2026 by the report month "
          "+ still planned for a 2026 month. change = entries - exits + resize.", "",
          "Technology names containing 'natural gas' in the changelog (records): " + json.dumps(census), "",
          "## Four technologies: the %s 2026 book in %s" % (b, l), "",
          "| technology | %s book | online 2026 | still 2026 | 2027+ | blank/pre-2026 | online outside 2026 | "
          "other status | not listed | left the year | joined since | %s book |" % (b, l),
          "|---|" + "---:|" * 11]
    for tech in TECHS:
        f = cross[tech]
        md.append("| %s | %.2f | " % (tech, f["base_book"]) + " | ".join("%.2f" % f["fate"][st] for st in pf.STATES)
                  + " | %.1f%% | %.2f | %.2f |" % (100 * left_share(f), f["entries_total"], f["latest_book"]))
    md += ["", "Sum of the four %s books: %.2f GW." % (b, sum(cross[t]["base_book"] for t in TECHS)), "",
           "## The %s natural gas book in %s" % (b, l), "",
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
    md += ["", "## By prime mover (cc = combined cycle, ct = combustion turbine, other = engines, steam, other)", "",
           "| group | %s book | generators | online 2026 | still 2026 | 2027+ | online outside 2026 | not listed | "
           "other status | joined since | %s book |" % (b, l), "|---|" + "---:|" * 10]
    for c in SUBTYPES:
        f = subs[c]
        md.append("| %s | %.2f | %d | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f |" % (
            c, f["base_book"], sum(f["fate_units"].values()), f["fate"]["online_2026"], f["fate"]["planned_2026"],
            f["fate"]["planned_later"], f["fate"]["online_other"], f["fate"]["not_listed"], f["fate"]["other_status"],
            f["entries_total"], f["latest_book"]))
    md += ["", "## Month by month (natural gas)", "",
           "| report | book | change | entries | from not listed | from 2027+ | exits | to 2027+ | to not listed | "
           "to other status | resize | came online |", "|---|" + "---:|" * 11]
    for f in flows:
        md.append("| %s | %.2f | %+.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %+.2f | %.2f |" % (
            f["report"], f["book_cur"], f["book_cur"] - f["book_prev"], f["entries"], f["in_not_listed"],
            f["in_planned_later"], f["exits"], f["out_planned_later"], f["out_not_listed"], f["out_other_status"],
            f["resize"], f["came_online"]))
    md += ["", "## Largest generators that left the %s book by %s" % (b, l), "",
           "| plant | generator | group | %s status | %s planned | MW | %s state | %s planned |" % (b, b, l, l),
           "|---|---|---|---|---|---:|---|---|"]
    for g in movers(gens):
        md.append("| %s | %s | %s | %s | %s | %.1f | %s | %s |" % (
            g["plant_id_eia"], g["generator_id"], g.get("subtype", ""), g["base_status"], g["base_planned"],
            float(g["base_summer_mw"]), g["latest_state"], g["latest_planned"]))
    md += ["", "## The two plants EIA named, by raw record", ""]
    for label, item in named_out.items():
        md += ["### %s (plant_name_eia contains '%s'): plants %s" % (label, item["pattern"], json.dumps(item["plants"])),
               "", "| plant | generator | group | %s state | %s status | %s planned | MW | %s state | %s status | "
               "%s planned | %s online |" % (b, b, b, l, l, l, l), "|---|---|---|---|---|---|---:|---|---|---|---|"]
        for g in item["generators"]:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                g["plant_id_eia"], g["generator_id"], g.get("subtype", ""), g["base_state"], g["base_status"],
                g["base_planned"], g["base_summer_mw"], g["latest_state"], g["latest_status"], g["latest_planned"],
                g["latest_online"]))
        recs = item.get("records", [])
        if recs:
            cols = list(recs[0].keys())
            md += ["", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
            md += ["| " + " | ".join(r[c] for c in cols) + " |" for r in recs]
        md.append("")
    md += ["## Checks and prediction aids (scored by hand against the pre-registration)", "", "```",
           json.dumps({"checks": s["checks"], "predictions": s["predictions"]}, indent=1), "```", ""]
    return "\n".join(md)


def tech_census(raw):
    t = raw["technology_description"].astype(str)
    hit = t[t.str.contains("natural gas", case=False, regex=False)]
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
    cols = [c for c in pf.COLUMNS if c in names] + (["plant_name_eia"] if "plant_name_eia" in names else [])
    raw = pd.read_parquet(path, columns=cols)
    census = tech_census(raw)
    pnames = plant_names(raw)
    df = pf.prepare(raw)
    flows, fate, cross, stages, subs, named_out, s, gens, book, latest_m = run(df, pnames)
    named_records(raw, named_out)
    s.update({"parquet": os.path.basename(path), "raw_records": int(len(raw)), "technology_census": census,
              "missing_columns": [c for c in pf.COLUMNS if c not in names]})
    with open(os.path.join(a.out_dir, "gas_flows.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": s, "book": book, "flows": flows, "fate": fate, "cross": cross, "stages": stages,
                   "subtypes": subs, "named": named_out}, fh, indent=1)
    keys = [k for k in flows[0] if k not in ("out_other_status_codes", "report")] if flows else []
    with open(os.path.join(a.out_dir, "gas_flows.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["report"] + keys, extrasaction="ignore")
        w.writeheader()
        for f in flows:
            w.writerow({k: (pf.r3(v) if isinstance(v, float) else v) for k, v in f.items()})
    with open(os.path.join(a.out_dir, "gas_flows_generators.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gens[0].keys()) if gens else ["plant_id_eia"])
        w.writeheader()
        w.writerows(gens)
    md = render(flows, fate, cross, stages, subs, named_out, s, gens, census, pf.BASE_REPORT, latest_m)
    with open(os.path.join(a.out_dir, "gas_flows.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
