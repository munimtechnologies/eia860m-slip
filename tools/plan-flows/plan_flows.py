"""plan_flows: where the 2026 solar plan went, month by month, in EIA-860M.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

plan_path.py found that the inventory's implied 2026 solar total (online in 2026 plus still
planned for a 2026 month) stayed between 41.0 and 43.7 GW from December 2025 to August 2026
(docs/plan-path.md). A net total can hide flows both ways. This splits each month's change
into what entered the 2026 book, what left it and how much the generators that stayed were
resized, so the parts add up to the change exactly; and it follows every generator in the
December 2025 book to the August 2026 report.

Generator states in a report (its latest record by then, as plan_path.snapshot reads it):

    online_2026    operating, online in 2026 by the report month   } the 2026 book
    planned_2026   planned status, planned for a 2026 month        }
    planned_later  planned status, planned for 2027 or later
    planned_other  planned status, planned month blank or before 2026
    online_other   operating, online outside 2026
    other_status   any other status (cancelled, postponed, retired, ...)
    not_listed     no record valid at that report

Checks and predictions: docs/plan-flows-preregistration.md.

    python plan_flows.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import glob
import json
import os

import numpy as np
import pandas as pd

VERSION = "0.1.0"
COLUMNS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
           "summer_capacity_mw", "current_planned_generator_operating_date",
           "generator_operating_date", "operational_status_code", "technology_description")
PLANNED = frozenset({"P", "L", "T", "U", "V", "TS", "OT"})
OPERATING = frozenset({"OP", "SB", "OS", "OA"})
TECH = {"solar": ("solar photovoltaic",), "wind": ("onshore wind turbine", "offshore wind turbine")}
YEAR = 2026
FIRST_REPORT = 2025 * 12 + 10   # November 2025
BASE_REPORT = 2025 * 12 + 11    # December 2025, the inventory behind EIA's 43.4 GW
TARGET_REPORT = 2026 * 12 + 7   # August 2026, the latest report when this was written
IN_BOOK = ("online_2026", "planned_2026")
OUT_STATES = ("planned_later", "planned_other", "online_other", "other_status", "not_listed")
STATES = IN_BOOK + OUT_STATES
BUILDING = ("U", "V", "TS")
EARLY = ("P", "L")
# plan_path 0.1.0's implied 2026 solar totals, GW net summer (data/plan_path.csv), for check C2.
PLAN_PATH_V1 = {"2025-11": 41.37, "2025-12": 43.65, "2026-01": 42.48, "2026-02": 41.77, "2026-03": 43.21,
                "2026-04": 43.09, "2026-05": 42.81, "2026-06": 41.62, "2026-07": 41.00, "2026-08": 41.13}
# Stated before the job ran (docs/plan-flows-preregistration.md).
C1_TOL, C2_TOL, C3_TOL = 0.001, 0.01, 0.01  # GW
F1_LATER, F2_ENTRIES, F3_SHARE, F5_BUILDING, F5_EARLY = 8.0, 5.0, 0.30, 0.60, 0.20


def months(values):
    """Months since year 0 (year * 12 + month - 1) as floats, NaN where missing."""
    d = pd.to_datetime(pd.Series(values), errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype(float).to_numpy()


def month_str(m):
    if m is None or (isinstance(m, float) and np.isnan(m)):
        return ""
    m = int(m)
    return "%04d-%02d" % (m // 12, m % 12 + 1)


def tech_of(desc):
    text = str(desc).strip().lower()
    for tech, names in TECH.items():
        if text in names:
            return tech
    return ""


def prepare(raw):
    """The same preparation as plan_path.prepare: solar and wind records, months as numbers."""
    df = raw.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["tech"] = [tech_of(x) for x in df["technology_description"]]
    df = df[df["tech"] != ""].copy()
    df["plant"] = pd.to_numeric(df["plant_id_eia"], errors="coerce").astype("Int64").astype(str)
    df["gen"] = df["generator_id"].astype(str).str.strip()
    df["key"] = df["plant"] + "/" + df["gen"]
    df["report_m"] = months(df["report_date"])
    df["valid_m"] = months(df["valid_until_date"])
    df["planned_m"] = months(df["current_planned_generator_operating_date"])
    df["op_m"] = months(df["generator_operating_date"])
    df["status"] = df["operational_status_code"].astype(str).str.strip().str.upper()
    name = pd.to_numeric(df["capacity_mw"], errors="coerce")
    summer = pd.to_numeric(df["summer_capacity_mw"], errors="coerce")
    df["nameplate"] = name.fillna(0.0)
    df["summer"] = summer.where(summer > 0, name).fillna(0.0)
    return df[df["report_m"].notna()].reset_index(drop=True)


def snapshot(df, m):
    """Each generator's record as of report month m: its latest record reported by m, if still valid at m."""
    s = df[df["report_m"] <= m].sort_values(["key", "report_m"], kind="mergesort")
    s = s.groupby("key").tail(1)
    return s[s["valid_m"].isna() | (s["valid_m"] >= m)]


def states(df, m, tech="solar", year=YEAR):
    """One row per generator of `tech` listed at report month m: its state, net summer MW and status.

    Read exactly as plan_path.path_row reads a report, so the 2026 book's capacity here equals
    plan_path's added + planned."""
    jan, dec = year * 12, year * 12 + 11
    snap = snapshot(df, m)
    first = df[(df["report_m"] <= m) & df["status"].isin(OPERATING)].groupby("key")["report_m"].min()
    online = snap["op_m"].where(snap["op_m"].notna(), snap["key"].map(first))
    snap = snap.assign(online=online)
    snap = snap[snap["tech"] == tech].set_index("key")
    op = snap["status"].isin(OPERATING)
    pl = snap["status"].isin(PLANNED)
    on, pm = snap["online"], snap["planned_m"]
    state = np.select(
        [op & (on >= jan) & (on <= min(m, dec)), op,
         pl & (pm >= jan) & (pm <= dec), pl & (pm > dec), pl],
        ["online_2026", "online_other", "planned_2026", "planned_later", "planned_other"],
        default="other_status")
    return pd.DataFrame({"state": state, "cap": snap["summer"], "status": snap["status"], "planned_m": pm,
                         "online": on, "plant": snap["plant"], "gen": snap["gen"]}, index=snap.index)


def gw(values):
    return float(pd.to_numeric(pd.Series(values, dtype=float), errors="coerce").fillna(0.0).sum()) / 1000.0


def pick(frame, keys, col="cap"):
    return frame.loc[list(keys), col] if len(keys) else pd.Series([], dtype=float)


def split(prev, cur):
    """How the 2026 book changed from `prev` to `cur` (two states() frames).

    change = entries - exits + resize, exactly: an entry is counted at its capacity in `cur`, by
    its state in `prev`; an exit at its capacity in `prev`, by its state in `cur`; a generator in
    the book at both contributes its change in capacity."""
    pb = prev[prev["state"].isin(IN_BOOK)]
    cb = cur[cur["state"].isin(IN_BOOK)]
    exits, entries, stay = pb.index.difference(cb.index), cb.index.difference(pb.index), pb.index.intersection(cb.index)
    fate = cur["state"].reindex(exits).fillna("not_listed")
    origin = prev["state"].reindex(entries).fillna("not_listed")
    r = {"book_prev": gw(pb["cap"]), "book_cur": gw(cb["cap"])}
    for s in OUT_STATES:
        r["out_" + s] = gw(pick(pb, fate.index[fate.to_numpy() == s]))
        r["in_" + s] = gw(pick(cb, origin.index[origin.to_numpy() == s]))
    r["resize"] = gw(pick(cb, stay)) - gw(pick(pb, stay))
    r["entries"] = sum(r["in_" + s] for s in OUT_STATES)
    r["exits"] = sum(r["out_" + s] for s in OUT_STATES)
    r["entries_online"] = gw(pick(cb, [k for k in entries if cb.at[k, "state"] == "online_2026"]))
    r["came_online"] = gw(pick(cb, [k for k in stay if pb.at[k, "state"] == "planned_2026"
                                    and cb.at[k, "state"] == "online_2026"]))
    r["residual"] = r["book_cur"] - r["book_prev"] - r["entries"] + r["exits"] - r["resize"]
    codes = {}
    for k in fate.index[fate.to_numpy() == "other_status"]:
        c = str(cur.at[k, "status"])
        codes[c] = codes.get(c, 0.0) + float(pb.at[k, "cap"]) / 1000.0
    r["out_other_status_codes"] = {c: round(v, 3) for c, v in sorted(codes.items())}
    r["units_entered"], r["units_left"] = int(len(entries)), int(len(exits))
    return r


def book_fate(base, latest):
    """Where the `base` report's 2026 book is in `latest`, at base capacity, and what joined it since."""
    bb = base[base["state"].isin(IN_BOOK)]
    lb = latest[latest["state"].isin(IN_BOOK)]
    fate = latest["state"].reindex(bb.index).fillna("not_listed")
    entries = lb.index.difference(bb.index)
    origin = base["state"].reindex(entries).fillna("not_listed")
    stay = bb.index.intersection(lb.index)
    out = {"base_book": gw(bb["cap"]), "latest_book": gw(lb["cap"]),
           "fate": {s: gw(pick(bb, fate.index[fate.to_numpy() == s])) for s in STATES},
           "fate_units": {s: int((fate == s).sum()) for s in STATES},
           "entries": {s: gw(pick(lb, origin.index[origin.to_numpy() == s])) for s in OUT_STATES},
           "entries_units": int(len(entries)),
           "entries_online": gw(pick(lb, [k for k in entries if lb.at[k, "state"] == "online_2026"])),
           "resize": gw(pick(lb, stay)) - gw(pick(bb, stay)), "by_base_status": {}, "other_status_codes": {}}
    out["entries_total"] = sum(out["entries"].values())
    for code in sorted(set(bb["status"])):
        keys = bb.index[bb["status"].to_numpy() == code]
        f = fate.reindex(keys)
        out["by_base_status"][code] = {"base_gw": gw(pick(bb, keys)), "units": int(len(keys))}
        out["by_base_status"][code].update({s: gw(pick(bb, f.index[f.to_numpy() == s])) for s in STATES})
    for k in fate.index[fate.to_numpy() == "other_status"]:
        c = str(latest.at[k, "status"])
        out["other_status_codes"][c] = out["other_status_codes"].get(c, 0.0) + float(bb.at[k, "cap"]) / 1000.0
    return out


def generator_rows(base, latest, base_m, latest_m):
    """One row per generator in either report's 2026 book."""
    bb = base[base["state"].isin(IN_BOOK)]
    lb = latest[latest["state"].isin(IN_BOOK)]
    rows = []
    for k in sorted(bb.index.union(lb.index)):
        b = base.loc[k] if k in base.index else None
        l = latest.loc[k] if k in latest.index else None  # noqa: E741
        ref = b if b is not None else l
        rows.append({"plant_id_eia": ref["plant"], "generator_id": ref["gen"],
                     "base_report": month_str(base_m), "base_state": b["state"] if b is not None else "not_listed",
                     "base_status": b["status"] if b is not None else "",
                     "base_planned": month_str(b["planned_m"]) if b is not None else "",
                     "base_summer_mw": round(float(b["cap"]), 3) if b is not None else "",
                     "latest_report": month_str(latest_m),
                     "latest_state": l["state"] if l is not None else "not_listed",
                     "latest_status": l["status"] if l is not None else "",
                     "latest_planned": month_str(l["planned_m"]) if l is not None else "",
                     "latest_online": month_str(l["online"]) if l is not None else "",
                     "latest_summer_mw": round(float(l["cap"]), 3) if l is not None else ""})
    return rows


def summarize(flows, fate, book_by_report):
    """Checks and the numbers each prediction needs; every verdict is re-read by hand."""
    s = {"version": VERSION, "checks": {}, "predictions": {}}
    worst = max((abs(f["residual"]) for f in flows), default=0.0)
    s["checks"]["C1"] = {"pairs": len(flows), "largest_residual_gw": round(worst, 6), "passed": worst <= C1_TOL}
    diffs = {r: round(book_by_report[r] - v, 4) for r, v in PLAN_PATH_V1.items() if r in book_by_report}
    s["checks"]["C2"] = {"reports_compared": len(diffs), "differences_gw": diffs,
                         "passed": len(diffs) == len(PLAN_PATH_V1) and all(abs(d) <= C2_TOL for d in diffs.values())}
    total = sum(fate["fate"].values())
    s["checks"]["C3"] = {"fate_sum_gw": round(total, 4), "base_book_gw": round(fate["base_book"], 4),
                         "passed": abs(total - fate["base_book"]) <= C3_TOL}
    p, f, base = s["predictions"], fate["fate"], fate["base_book"]
    p["F1"] = {"planned_later_gw": round(f["planned_later"], 3), "held": f["planned_later"] >= F1_LATER}
    p["F2"] = {"entries_gw": round(fate["entries_total"], 3), "held": fate["entries_total"] >= F2_ENTRIES}
    share = f["online_2026"] / base if base else 0.0
    p["F3"] = {"online_gw": round(f["online_2026"], 3), "share": round(share, 4), "held": share < F3_SHARE}
    gone = f["other_status"] + f["not_listed"]
    p["F4"] = {"cancelled_or_unlisted_gw": round(gone, 3), "planned_later_gw": round(f["planned_later"], 3),
               "held": gone < f["planned_later"]}
    st = fate["by_base_status"]
    bld = sum(st[c]["base_gw"] for c in BUILDING if c in st)
    bld_on = sum(st[c]["online_2026"] for c in BUILDING if c in st)
    ear = sum(st[c]["base_gw"] for c in EARLY if c in st)
    ear_on = sum(st[c]["online_2026"] for c in EARLY if c in st)
    b_share = bld_on / bld if bld else 0.0
    e_share = ear_on / ear if ear else 0.0
    p["F5"] = {"building_gw": round(bld, 3), "building_online_share": round(b_share, 4),
               "early_gw": round(ear, 3), "early_online_share": round(e_share, 4),
               "held": b_share >= F5_BUILDING and e_share <= F5_EARLY}
    return s


def r3(x):
    return round(x, 3)


def render(flows, fate, s, wind_fate, base_m, latest_m):
    md = ["# Where the 2026 solar plan went (plan_flows %s)" % VERSION, "",
          "EIA-860M (PUDL changelog), GW net summer capacity. The 2026 book = online in 2026 by the report "
          "month + still planned for a 2026 month. Entries are counted at their new capacity, by where they "
          "were the report before; exits at their old capacity, by where they went. change = entries - exits "
          "+ resize.", "",
          "## Month by month (solar)", "",
          "| report | book | change | entries | from not listed | from 2027+ | from blank/pre-2026 | "
          "from online other | from other status | exits | to 2027+ | to blank/pre-2026 | to online other | "
          "to other status | to not listed | resize | came online | entered online |",
          "|---|" + "---:|" * 17]
    for f in flows:
        md.append("| %s | %.2f | %+.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | "
                  "%.2f | %.2f | %+.2f | %.2f | %.2f |" % (
                      f["report"], f["book_cur"], f["book_cur"] - f["book_prev"], f["entries"],
                      f["in_not_listed"], f["in_planned_later"], f["in_planned_other"], f["in_online_other"],
                      f["in_other_status"], f["exits"], f["out_planned_later"], f["out_planned_other"],
                      f["out_online_other"], f["out_other_status"], f["out_not_listed"], f["resize"],
                      f["came_online"], f["entries_online"]))
    md += ["", "Other statuses of exits, by report (GW): " + "; ".join(
        "%s %s" % (f["report"], json.dumps(f["out_other_status_codes"])) for f in flows if f["out_other_status_codes"]),
        "", "## The %s book in %s (solar)" % (month_str(base_m), month_str(latest_m)), "",
        "%.2f GW in %s; %.2f GW in %s." % (fate["base_book"], month_str(base_m), fate["latest_book"],
                                           month_str(latest_m)), "",
        "| state in %s | GW (at %s capacity) | generators |" % (month_str(latest_m), month_str(base_m)),
        "|---|---:|---:|"]
    for st in STATES:
        md.append("| %s | %.2f | %d |" % (st, fate["fate"][st], fate["fate_units"][st]))
    md += ["", "Joined the book since %s (GW at %s capacity, by state in %s): %s; total %.2f GW in %d "
           "generators, %.2f GW of it already online. Resize of generators in both books: %+.2f GW." % (
               month_str(base_m), month_str(latest_m), month_str(base_m),
               ", ".join("%s %.2f" % (k, v) for k, v in fate["entries"].items()), fate["entries_total"],
               fate["entries_units"], fate["entries_online"], fate["resize"]),
           "", "Other statuses (GW): %s" % json.dumps({k: r3(v) for k, v in fate["other_status_codes"].items()}),
           "", "By status in %s:" % month_str(base_m), "",
           "| status | GW | generators | " + " | ".join(STATES) + " |", "|---|---:|---:|" + "---:|" * len(STATES)]
    for code, row in fate["by_base_status"].items():
        md.append("| %s | %.2f | %d | " % (code, row["base_gw"], row["units"])
                  + " | ".join("%.2f" % row[st] for st in STATES) + " |")
    md += ["", "Wind, same reading: %.2f GW in %s; in %s: " % (wind_fate["base_book"], month_str(base_m),
                                                                month_str(latest_m))
           + ", ".join("%s %.2f" % (k, v) for k, v in wind_fate["fate"].items())
           + "; joined %.2f GW." % wind_fate["entries_total"],
           "", "## Checks and prediction aids (scored by hand against the pre-registration)", "", "```",
           json.dumps({"checks": s["checks"], "predictions": s["predictions"]}, indent=1), "```", ""]
    return "\n".join(md)


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"), recursive=True))
    return hits[0] if hits else None


def run(df):
    last = int(df["report_m"].max())
    reports = list(range(FIRST_REPORT, last + 1))
    st = {m: states(df, m) for m in reports}
    book = {month_str(m): round(gw(st[m].loc[st[m]["state"].isin(IN_BOOK), "cap"]), 4) for m in reports}
    flows = []
    for a, b in zip(reports, reports[1:]):
        f = split(st[a], st[b])
        f["report"] = month_str(b)
        flows.append(f)
    latest_m = min(TARGET_REPORT, last)
    fate = book_fate(st[BASE_REPORT], st[latest_m])
    wind_fate = book_fate(states(df, BASE_REPORT, "wind"), states(df, latest_m, "wind"))
    s = summarize(flows, fate, book)
    s.update({"last_report": month_str(last), "base_report": month_str(BASE_REPORT),
              "latest_report_used": month_str(latest_m)})
    gens = generator_rows(st[BASE_REPORT], st[latest_m], BASE_REPORT, latest_m)
    return flows, fate, wind_fate, s, gens, book, latest_m


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    path = find_parquet(a.data_dir)
    if not path:
        raise SystemExit("no changelog_generators parquet under %s" % a.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in COLUMNS if c in names])
    df = prepare(raw)
    flows, fate, wind_fate, s, gens, book, latest_m = run(df)
    s.update({"parquet": os.path.basename(path), "raw_records": int(len(raw)),
              "missing_columns": [c for c in COLUMNS if c not in names]})
    with open(os.path.join(a.out_dir, "plan_flows.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": s, "book": book, "flows": flows, "fate": fate, "wind_fate": wind_fate}, fh, indent=1)
    keys = [k for k in flows[0] if k != "out_other_status_codes"] if flows else ["report"]
    with open(os.path.join(a.out_dir, "plan_flows.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["report"] + [k for k in keys if k != "report"], extrasaction="ignore")
        w.writeheader()
        for f in flows:
            w.writerow({k: (r3(v) if isinstance(v, float) else v) for k, v in f.items()})
    with open(os.path.join(a.out_dir, "plan_flows_generators.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gens[0].keys()) if gens else ["plant_id_eia"])
        w.writeheader()
        w.writerows(gens)
    md = render(flows, fate, s, wind_fate, BASE_REPORT, latest_m)
    with open(os.path.join(a.out_dir, "plan_flows.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
