"""plan_path: the 2026 solar figure, month by month, in EIA-860M and in the STEO.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

The January 2026 Short-Term Energy Outlook put 2026 utility-scale solar additions at
32.1 GW, 26% below the 43.4 GW the developers planned (docs/steo-vs-plan.md, P5). This
follows both numbers through 2026:

- plan side: for each monthly EIA-860M report (PUDL's changelog) from November 2025 on,
  the solar photovoltaic capacity that came online in 2026 up to that report plus the
  capacity still planned for a 2026 month, which is what the inventory implies for 2026;
- STEO side: for each 2026 edition, the electric power sector "Solar photovoltaic" row of
  the capacity table (end of 2026 minus end of 2025), read from the page text that
  steo_text.py writes.

Wind is done the same way. Checks and predictions: docs/plan-path-preregistration.md.

    python plan_path.py --data-dir /data --steo-dir /out --out-dir /out
"""

import argparse
import csv
import glob
import json
import os
import re

import numpy as np
import pandas as pd

VERSION = "0.1.0"
COLUMNS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
           "summer_capacity_mw", "current_planned_generator_operating_date",
           "generator_operating_date", "operational_status_code", "technology_description")
PLANNED = frozenset({"P", "L", "T", "U", "V", "TS", "OT"})
OPERATING = frozenset({"OP", "SB", "OS", "OA"})
TECH = {"solar": ("solar photovoltaic",), "wind": ("onshore wind turbine", "offshore wind turbine")}
MEASURES = ("nameplate", "summer")
YEAR = 2026
FIRST_REPORT = 2025 * 12 + 10  # November 2025, the inventory behind the January 2026 STEO
PLAN_REPORT = 2025 * 12 + 11   # December 2025, the inventory behind EIA's 43.4 GW
PLAN_TIE = {"solar": 43.4, "wind": 11.8}  # GW, Today in Energy 67205 (20 February 2026)
EDITIONS = ("jan26", "feb26", "mar26", "apr26", "may26", "jun26", "jul26", "aug26", "sep26", "oct26")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
ROW = {"solar": re.compile(r"^\s*Solar photovoltaic\s*\.{2,}(.*)$", re.I),
       "wind": re.compile(r"^\s*Wind\s*\.{2,}(.*)$", re.I)}
# Stated before the job ran (docs/plan-path-preregistration.md).
C1_TOLERANCE = 0.05
C3_TOLERANCE = 0.5  # GW
JAN26 = {"solar": (139.2, 171.3), "wind": (160.4, 170.1)}
P1_DROP, P3_SHARE, P4_BAND, P5_SHARE = 4.0, 0.5, 4.0, 0.40


def months(values):
    """Months since year 0 (year * 12 + month - 1) as floats, NaN where missing."""
    d = pd.to_datetime(pd.Series(values), errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype(float).to_numpy()


def month_str(m):
    m = int(m)
    return "%04d-%02d" % (m // 12, m % 12 + 1)


def edition_month(ed):
    """Month index of a STEO edition name such as 'oct26'."""
    return (2000 + int(ed[3:5])) * 12 + MONTHS.index(ed[:3].lower())


def tech_of(desc):
    text = str(desc).strip().lower()
    for tech, names in TECH.items():
        if text in names:
            return tech
    return ""


# ---------------------------------------------------------------- STEO side

def steo_rows(text):
    """{tech: (end of 2025, end of 2026, end of 2027)} from an edition's page text.

    The capacity table's electric power sector block has a "Solar photovoltaic" row of 15
    numbers (12 quarters, then three year-end columns); wind is the first 15-number "Wind" row
    on the same page (the electric power block comes before the combined heat and power one).
    """
    for page in re.split(r"\n===== page \d+ =====\n", text):
        found = {}
        for line in page.splitlines():
            for tech, rx in ROW.items():
                m = rx.match(line)
                if not m or tech in found:
                    continue
                nums = [float(x) for x in NUM.findall(m.group(1))]
                if len(nums) >= 15:
                    found[tech] = tuple(nums[-3:])
        if "solar" in found:
            return found
    return {}


def read_steo(steo_dir, editions):
    out = []
    for ed in editions:
        entry = {"edition": ed, "pairs_with_report": month_str(edition_month(ed) - 2)}
        path = os.path.join(steo_dir, ed + ".txt")
        if not os.path.exists(path):
            entry["error"] = "no page text"
            out.append(entry)
            continue
        with open(path, encoding="utf-8") as fh:
            rows = steo_rows(fh.read())
        for tech in TECH:
            r = rows.get(tech)
            if r:
                entry[tech + "_end_2025"], entry[tech + "_end_2026"], entry[tech + "_end_2027"] = r
                entry[tech + "_2026"] = round(r[1] - r[0], 1)
        if "solar" not in rows:
            entry["error"] = "no capacity row found"
        out.append(entry)
    return out


# ---------------------------------------------------------------- plan side

def prepare(raw):
    df = raw.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["tech"] = [tech_of(x) for x in df["technology_description"]]
    df = df[df["tech"] != ""].copy()
    df["key"] = (pd.to_numeric(df["plant_id_eia"], errors="coerce").astype("Int64").astype(str) + "/"
                 + df["generator_id"].astype(str).str.strip())
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


def path_row(df, m, year=YEAR):
    """GW of each technology that came online in `year` by report month m, and GW still planned
    for a month of `year` (the inventory's implied total is their sum)."""
    jan, dec = year * 12, year * 12 + 11
    snap = snapshot(df, m)
    first = df[(df["report_m"] <= m) & df["status"].isin(OPERATING)].groupby("key")["report_m"].min()
    online = snap["op_m"].where(snap["op_m"].notna(), snap["key"].map(first))
    added = snap[snap["status"].isin(OPERATING) & (online >= jan) & (online <= min(m, dec))]
    planned = snap[snap["status"].isin(PLANNED) & (snap["planned_m"] >= jan) & (snap["planned_m"] <= dec)]
    row = {"report": month_str(m)}
    for tech in TECH:
        a, p = added[added["tech"] == tech], planned[planned["tech"] == tech]
        for ms in MEASURES:
            add, plan = float(a[ms].sum()) / 1000, float(p[ms].sum()) / 1000
            row["%s_added_%s" % (tech, ms)] = round(add, 2)
            row["%s_planned_%s" % (tech, ms)] = round(plan, 2)
            row["%s_implied_%s" % (tech, ms)] = round(add + plan, 2)
        row["%s_overdue_nameplate" % tech] = round(float(p.loc[p["planned_m"] < m, "nameplate"].sum()) / 1000, 2)
        row["%s_planned_units" % tech] = int(len(p))
    return row


# ---------------------------------------------------------------- scoring aids

def summarize(path_rows, steo):
    """Checks and the numbers each prediction needs; every verdict is re-read by hand."""
    by_report = {r["report"]: r for r in path_rows}
    s = {"version": VERSION, "checks": {}, "predictions": {}, "pairs": []}
    dec = by_report.get(month_str(PLAN_REPORT))
    measure = None
    if dec:
        diffs = {ms: (dec["solar_planned_" + ms] - PLAN_TIE["solar"]) / PLAN_TIE["solar"] for ms in MEASURES}
        measure = min(MEASURES, key=lambda ms: abs(diffs[ms]))
        s["checks"]["C1"] = {"planned_2026_solar_gw": {ms: dec["solar_planned_" + ms] for ms in MEASURES},
                             "relative_difference": {ms: round(diffs[ms], 4) for ms in MEASURES},
                             "measure": measure, "passed": abs(diffs[measure]) <= C1_TOLERANCE,
                             "wind_planned_2026_gw": {ms: dec["wind_planned_" + ms] for ms in MEASURES}}
    else:
        s["checks"]["C1"] = {"passed": False, "reason": "no December 2025 report"}
    s["measure"] = measure or "nameplate"
    ms = s["measure"]
    parsed = [e for e in steo if "solar_2026" in e]
    sane = [e for e in parsed if 130 <= e["solar_end_2025"] <= 150]
    jan = next((e for e in steo if e["edition"] == "jan26"), {})
    jan_ok = all(jan.get("%s_end_2025" % t) == JAN26[t][0] and jan.get("%s_end_2026" % t) == JAN26[t][1]
                 for t in JAN26)
    s["checks"]["C2"] = {"editions": len(steo), "parsed": len(parsed), "sane": len(sane),
                         "jan26_reproduced": jan_ok, "passed": len(sane) >= 8 and jan_ok}
    added = [(r["report"], r["solar_added_" + ms]) for r in path_rows]
    drops = [(b[0], round(a[1] - b[1], 2)) for a, b in zip(added, added[1:]) if a[1] - b[1] > 0]
    s["checks"]["C3"] = {"largest_drop_gw": max([d for _, d in drops], default=0.0), "drops": drops,
                         "passed": all(d <= C3_TOLERANCE for _, d in drops)}
    for e in parsed:
        r = by_report.get(e["pairs_with_report"])
        if r:
            s["pairs"].append({"edition": e["edition"], "report": r["report"], "steo_solar_2026": e["solar_2026"],
                               "implied_solar_2026": r["solar_implied_" + ms],
                               "gap_gw": round(r["solar_implied_" + ms] - e["solar_2026"], 2),
                               "steo_wind_2026": e.get("wind_2026"), "implied_wind_2026": r["wind_implied_" + ms]})
    last = path_rows[-1] if path_rows else None
    p = s["predictions"]
    if dec and last:
        drop = round(dec["solar_implied_" + ms] - last["solar_implied_" + ms], 2)
        p["P1"] = {"december_2025": dec["solar_implied_" + ms], "latest": last["solar_implied_" + ms],
                   "latest_report": last["report"], "drop_gw": drop, "held": drop >= P1_DROP}
    if s["pairs"]:
        p["P2"] = {"pairs": len(s["pairs"]), "pairs_with_plan_above": sum(1 for x in s["pairs"] if x["gap_gw"] > 0),
                   "held": all(x["gap_gw"] > 0 for x in s["pairs"])}
        feb = next((x for x in s["pairs"] if x["edition"] == "feb26"), None)
        latest = s["pairs"][-1]
        if feb and latest is not feb:
            p["P3"] = {"feb26_gap": feb["gap_gw"], "latest_edition": latest["edition"], "latest_gap": latest["gap_gw"],
                       "held": abs(latest["gap_gw"]) < P3_SHARE * abs(feb["gap_gw"])}
    if parsed and "solar_2026" in jan:
        newest = parsed[-1]
        move = round(newest["solar_2026"] - jan["solar_2026"], 1)
        p["P4"] = {"jan26": jan["solar_2026"], "latest_edition": newest["edition"], "latest": newest["solar_2026"],
                   "change_gw": move, "held": abs(move) <= P4_BAND}
    if last and last["solar_implied_" + ms] > 0:
        share = last["solar_added_" + ms] / last["solar_implied_" + ms]
        p["P5"] = {"latest_report": last["report"], "added": last["solar_added_" + ms],
                   "implied": last["solar_implied_" + ms], "share": round(share, 4), "held": share >= P5_SHARE}
    return s


# ---------------------------------------------------------------- output

def render(path_rows, steo, s):
    ms = s["measure"]
    md = ["# The 2026 solar figure, month by month (plan_path %s)" % VERSION, "",
          "Plan side: EIA-860M (PUDL changelog), GW %s capacity. Added = came online in 2026 by the report "
          "month; planned = still planned for a 2026 month; implied = added + planned; overdue = planned for a "
          "2026 month before the report month and not yet online (nameplate)." % ms, "",
          "| report | solar added | solar planned | solar implied | overdue | planned units | wind implied |"
          " solar implied (other measure) |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    other = [x for x in MEASURES if x != ms][0]
    for r in path_rows:
        md.append("| %s | %.2f | %.2f | %.2f | %.2f | %d | %.2f | %.2f |" % (
            r["report"], r["solar_added_" + ms], r["solar_planned_" + ms], r["solar_implied_" + ms],
            r["solar_overdue_nameplate"], r["solar_planned_units"], r["wind_implied_" + ms],
            r["solar_implied_" + other]))
    md += ["", "STEO side: capacity table, electric power sector, GW at end of period.", "",
           "| edition | pairs with report | solar end-2025 | solar end-2026 | solar 2026 | wind 2026 | note |",
           "|---|---|---:|---:|---:|---:|---|"]
    for e in steo:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            e["edition"], e["pairs_with_report"], e.get("solar_end_2025", "-"), e.get("solar_end_2026", "-"),
            e.get("solar_2026", "-"), e.get("wind_2026", "-"), e.get("error", "")))
    md += ["", "Pairs (edition with the EIA-860M report two months earlier):", "",
           "| edition | report | STEO solar 2026 | implied solar 2026 | gap | STEO wind 2026 | implied wind 2026 |",
           "|---|---|---:|---:|---:|---:|---:|"]
    for x in s["pairs"]:
        md.append("| %s | %s | %.1f | %.2f | %.2f | %s | %.2f |" % (
            x["edition"], x["report"], x["steo_solar_2026"], x["implied_solar_2026"], x["gap_gw"],
            x["steo_wind_2026"], x["implied_wind_2026"]))
    md += ["", "## Checks and prediction aids (scored by hand against the pre-registration)", "", "```",
           json.dumps({"checks": s["checks"], "predictions": s["predictions"]}, indent=1), "```", ""]
    return "\n".join(md)


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"), recursive=True))
    return hits[0] if hits else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--steo-dir", default="/out")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("editions", nargs="*", default=list(EDITIONS))
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    path = find_parquet(a.data_dir)
    if not path:
        raise SystemExit("no changelog_generators parquet under %s" % a.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in COLUMNS if c in names])
    df = prepare(raw)
    last = int(df["report_m"].max())
    path_rows = [path_row(df, m) for m in range(FIRST_REPORT, last + 1)]
    steo = read_steo(a.steo_dir, a.editions)
    s = summarize(path_rows, steo)
    s.update({"parquet": os.path.basename(path), "raw_records": int(len(raw)), "solar_wind_records": int(len(df)),
              "missing_columns": [c for c in COLUMNS if c not in names], "last_report": month_str(last)})
    with open(os.path.join(a.out_dir, "plan_path.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": s, "path": path_rows, "steo": steo}, fh, indent=1)
    with open(os.path.join(a.out_dir, "plan_path.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(path_rows[0].keys()) if path_rows else ["report"])
        w.writeheader()
        w.writerows(path_rows)
    md = render(path_rows, steo, s)
    with open(os.path.join(a.out_dir, "plan_path.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
