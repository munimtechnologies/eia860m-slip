"""coal_rows: which coal retirements were in EIA's start-of-year plan? A row-level check.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check on eia860m-slip
docs/coal-plan-misses.md, which inferred plan membership from EIA's articles.

For each year Y, the plan is every operating coal generator whose planned retirement
date falls in Y in the EIA-860M inventory of October and of December of Y-1 (EIA's
start-of-year articles use one or the other). Each coal generator that retired in Y is
then classed by what that inventory said about it: planned for Y, planned for a later
year, planned for an earlier year, no planned date, not operating, or not listed. The
retirement month is the latest generator_retirement_date reported for the generator.
Capacity is net summer (summer_capacity_mw) from its last operating record, else
nameplate. The last year in the data also gets a follow-up: where each generator of its
December plan stands in the latest report.

    python coal_rows.py --data-dir /data --out-dir /out
"""

import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

OPERATING = frozenset({"OP", "SB", "OS", "OA"})
COAL_CODES = frozenset({"BIT", "SUB", "LIG", "ANT", "RC", "WC", "SGC"})
COLUMNS = ("report_date", "valid_until_date", "plant_id_eia", "plant_name_eia", "generator_id",
           "utility_name_eia", "state", "capacity_mw", "summer_capacity_mw",
           "planned_generator_retirement_date", "generator_retirement_date",
           "operational_status_code", "technology_description", "energy_source_code_1")
CLASSES = ("planned_same_year", "planned_later", "planned_earlier", "no_date", "not_operating",
           "not_listed")
INVENTORIES = (("oct", 9), ("dec", 11))
# EIA's start-of-year coal plan, final Table 4.6 count and first count (GW, net summer),
# copied from eia860m-slip data/eia_headline_retirements.csv.
EIA_PLAN = {2018: 13.0, 2019: 4.5, 2020: 5.8, 2021: 2.7, 2022: 12.6, 2023: 8.9, 2024: 2.3,
            2025: 8.1, 2026: 6.4}
EIA_FINAL = {2018: 13.3042, 2019: 12.8951, 2020: 10.4567, 2021: 5.5618, 2022: 13.6798,
             2023: 9.2249, 2024: 3.9586}
EIA_FIRST = {2025: 2.6}
TOP = 12


def months(values):
    """Months since year 0 (year * 12 + month - 1) as floats, NaN where missing."""
    d = pd.to_datetime(pd.Series(values), errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype(float).to_numpy()


def month_str(m):
    if m is None or m != m:
        return ""
    m = int(m)
    return "%04d-%02d" % (m // 12, m % 12 + 1)


def is_coal(code, tech):
    if isinstance(code, str) and code.strip():
        return code.strip().upper() in COAL_CODES
    return isinstance(tech, str) and "coal" in tech.lower()


def prepare(raw):
    df = raw.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["key"] = df["plant_id_eia"].astype(str) + "/" + df["generator_id"].astype(str)
    df["report_m"] = months(df["report_date"])
    df["valid_m"] = months(df["valid_until_date"])
    df["plan_ret_m"] = months(df["planned_generator_retirement_date"])
    df["ret_m"] = months(df["generator_retirement_date"])
    df["status"] = df["operational_status_code"].astype(str).str.strip().str.upper()
    df["coal"] = [is_coal(a, b) for a, b in zip(df["energy_source_code_1"],
                                                df["technology_description"])]
    summer = pd.to_numeric(df["summer_capacity_mw"], errors="coerce")
    name = pd.to_numeric(df["capacity_mw"], errors="coerce")
    df["mw"] = summer.where(summer > 0, name).fillna(0.0)
    return df[df["report_m"].notna()].reset_index(drop=True)


def generators(df):
    """One row per generator: identity from its last record, coal flag and MW from its last
    operating record, latest reported retirement month, latest status and planned date."""
    s = df.sort_values(["key", "report_m"], kind="mergesort")
    last = s.groupby("key").tail(1).set_index("key")
    op = s[s["status"].isin(OPERATING)].groupby("key").tail(1).set_index("key")
    t = last[["plant_id_eia", "plant_name_eia", "generator_id", "state", "utility_name_eia"]].copy()
    t["last_status"] = last["status"]
    t["last_plan_ret_m"] = last["plan_ret_m"]
    t["last_m"] = last["report_m"]
    t["coal"] = op["coal"].reindex(t.index).fillna(last["coal"]).astype(bool)
    t["mw"] = op["mw"].reindex(t.index).fillna(last["mw"]).astype(float)
    dated = s[s["ret_m"].notna()]
    t["ret_m"] = dated.groupby("key")["ret_m"].last().reindex(t.index)
    return t


def snapshot(df, m):
    """Each generator's record as of report month m (latest record reported by m, if still
    valid at m)."""
    s = df[df["report_m"] <= m].sort_values(["key", "report_m"], kind="mergesort")
    s = s.groupby("key").tail(1)
    s = s[s["valid_m"].isna() | (s["valid_m"] >= m)]
    return s.set_index("key")


def plan_rows(snap, year):
    lo, hi = year * 12, year * 12 + 11
    return snap[snap["coal"] & snap["status"].isin(OPERATING) & (snap["plan_ret_m"] >= lo)
                & (snap["plan_ret_m"] <= hi)]


def classify(rec, year):
    if rec is None:
        return "not_listed"
    if rec["status"] not in OPERATING:
        return "not_operating"
    p = rec["plan_ret_m"]
    if p != p:
        return "no_date"
    py = int(p // 12)
    if py == year:
        return "planned_same_year"
    return "planned_later" if py > year else "planned_earlier"


def first_dated(df, keys, year):
    """First report month in which a generator carries a planned or actual retirement in year."""
    lo, hi = year * 12, year * 12 + 11
    d = df[df["key"].isin(keys)]
    hit = d[((d["plan_ret_m"] >= lo) & (d["plan_ret_m"] <= hi))
            | ((d["ret_m"] >= lo) & (d["ret_m"] <= hi))]
    return hit.groupby("key")["report_m"].min()


def followup(df, t, year):
    """Where each generator of year's December plan stands in its latest record."""
    hi = year * 12 + 11
    plan = plan_rows(snapshot(df, (year - 1) * 12 + 11), year)
    rows = []
    for k, r in plan.iterrows():
        g = t.loc[k]
        if g["ret_m"] == g["ret_m"]:
            now = "retired"
        elif g["last_status"] not in OPERATING:
            now = "status_" + str(g["last_status"])
        elif g["last_plan_ret_m"] != g["last_plan_ret_m"]:
            now = "no_date_now"
        elif g["last_plan_ret_m"] > hi:
            now = "dated_later"
        else:
            now = "still_dated_this_year"
        rows.append({"key": k, "plant": g["plant_name_eia"], "state": g["state"],
                     "generator_id": g["generator_id"], "mw": round(float(r["mw"]), 1),
                     "planned_at_dec": month_str(r["plan_ret_m"]), "now": now,
                     "planned_now": month_str(g["last_plan_ret_m"]),
                     "retired": month_str(g["ret_m"]), "last_report": month_str(g["last_m"])})
    status = {}
    for row in rows:
        status[row["now"]] = round(status.get(row["now"], 0.0) + row["mw"], 1)
    return {"year": year, "inventory": month_str((year - 1) * 12 + 11), "plan_n": len(rows),
            "plan_mw": round(sum(r["mw"] for r in rows), 1), "mw_by_status": status, "rows": rows}


def analyse(df):
    t = generators(df)
    first_m, last_m = df["report_m"].min(), df["report_m"].max()
    coal = t[t["coal"]]
    years, gens = [], []
    for year in range(int(first_m // 12) + 1, int(last_m // 12) + 1):
        if (year - 1) * 12 + INVENTORIES[0][1] < first_m:
            continue
        lo, hi = year * 12, year * 12 + 11
        retired = coal[(coal["ret_m"] >= lo) & (coal["ret_m"] <= hi)]
        retired_mw = float(retired["mw"].sum())
        fd = first_dated(df, set(retired.index), year)
        in_year = [k for k in retired.index if fd.get(k, np.nan) >= lo]
        entry = {"year": year, "partial": bool(hi + 2 > last_m), "retired_n": int(len(retired)),
                 "retired_mw": round(retired_mw, 1),
                 "decided_in_year_mw": round(float(retired.loc[in_year, "mw"].sum()), 1),
                 "eia_plan_gw": EIA_PLAN.get(year), "eia_final_gw": EIA_FINAL.get(year),
                 "eia_first_gw": EIA_FIRST.get(year), "inventories": {}}
        cls_by_inv = {}
        for name, month in INVENTORIES:
            m = (year - 1) * 12 + month
            if m < first_m:
                continue
            snap = snapshot(df, m)
            plan = plan_rows(snap, year)
            plan_mw = float(plan["mw"].sum())
            pr = t["ret_m"].reindex(plan.index)
            outcome = {"retired_in_year": float(plan.loc[(pr >= lo) & (pr <= hi), "mw"].sum()),
                       "retired_earlier": float(plan.loc[pr < lo, "mw"].sum()),
                       "retired_later": float(plan.loc[pr > hi, "mw"].sum()),
                       "not_retired": float(plan.loc[pr.isna(), "mw"].sum())}
            by = {c: 0.0 for c in CLASSES}
            cls = {}
            for k in retired.index:
                c = classify(snap.loc[k] if k in snap.index else None, year)
                cls[k] = (c, snap.at[k, "plan_ret_m"] if k in snap.index else np.nan)
                by[c] += float(retired.at[k, "mw"])
            cls_by_inv[name] = cls
            entry["inventories"][name] = {
                "month": month_str(m), "plan_n": int(len(plan)), "plan_mw": round(plan_mw, 1),
                "plan_outcome": {k: round(v, 1) for k, v in outcome.items()},
                "plan_delivery": round(outcome["retired_in_year"] / plan_mw, 4) if plan_mw > 0 else None,
                "retired_by_class": {k: round(v, 1) for k, v in by.items()},
                "unplanned_share": (round(1 - by["planned_same_year"] / retired_mw, 4)
                                    if retired_mw > 0 else None)}
        years.append(entry)
        for k, g in retired.iterrows():
            row = {"year": year, "key": k, "plant": g["plant_name_eia"], "state": g["state"],
                   "utility": g["utility_name_eia"], "generator_id": g["generator_id"],
                   "mw": round(float(g["mw"]), 1), "retired": month_str(g["ret_m"]),
                   "first_dated": month_str(fd.get(k, np.nan))}
            for name, _ in INVENTORIES:
                c, p = cls_by_inv.get(name, {}).get(k, ("", np.nan))
                row["class_" + name] = c
                row["planned_at_" + name] = month_str(p)
            gens.append(row)
    return {"report_min": month_str(first_m), "report_max": month_str(last_m), "years": years,
            "generators": gens, "followup": followup(df, t, int(last_m // 12))}


def top_unplanned(gens, year):
    """Plants whose retired coal MW in year was not planned for year in December (else October)."""
    agg = {}
    for g in gens:
        if g["year"] != year:
            continue
        c = g["class_dec"] or g["class_oct"]
        if c == "planned_same_year":
            continue
        a = agg.setdefault((str(g["plant"]), str(g["state"])), {"mw": 0.0, "units": 0, "classes": set(),
                                                                  "retired": set(), "first": set()})
        a["mw"] += g["mw"]
        a["units"] += 1
        a["classes"].add(c)
        a["retired"].add(g["retired"])
        a["first"].add(g["first_dated"])
    out = sorted(agg.items(), key=lambda kv: -kv[1]["mw"])
    return [{"plant": p, "state": s, "mw": round(a["mw"], 1), "units": a["units"],
             "classes": ",".join(sorted(a["classes"])), "retired": ",".join(sorted(a["retired"])),
             "first_dated": ",".join(sorted(x for x in a["first"] if x))} for (p, s), a in out]


def gw(x):
    return "" if x is None else "%.2f" % (x / 1000.0)


def render(res, diag):
    md = ["# Coal retirements against EIA's start-of-year plan, row by row", "",
          "MV2 of Munim, Inc. (made with AI agents). EIA-860M via PUDL's changelog, reports %s to %s."
          % (res["report_min"], res["report_max"]), "",
          "GW net summer. 'plan' = operating coal generators dated to retire in the year in the "
          "inventory named. Classes describe that inventory's record of each generator that retired.", "",
          "| year | inv | EIA plan | plan (rows) | plan retired in year | retired (rows) | EIA final | "
          "planned same year | planned later | planned earlier | no date | not operating | not listed | "
          "unplanned share | decided in year |",
          "|" + "---|" * 15]
    for y in res["years"]:
        for name, _ in INVENTORIES:
            inv = y["inventories"].get(name)
            if not inv:
                continue
            b = inv["retired_by_class"]
            md.append("| %d%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                y["year"], " (partial)" if y["partial"] else "", inv["month"],
                "" if y["eia_plan_gw"] is None else y["eia_plan_gw"], gw(inv["plan_mw"]),
                gw(inv["plan_outcome"]["retired_in_year"]), gw(y["retired_mw"]),
                y["eia_final_gw"] or (y["eia_first_gw"] and "%s first" % y["eia_first_gw"]) or "",
                gw(b["planned_same_year"]), gw(b["planned_later"]), gw(b["planned_earlier"]),
                gw(b["no_date"]), gw(b["not_operating"]), gw(b["not_listed"]),
                "" if inv["unplanned_share"] is None else "%.3f" % inv["unplanned_share"],
                gw(y["decided_in_year_mw"])))
    md.append("")
    for y in res["years"]:
        rows = top_unplanned(res["generators"], y["year"])[:TOP]
        if not rows:
            continue
        md += ["## %d: largest retirements not planned for the year" % y["year"], "",
               "| plant | state | MW | units | class | retired | first dated |", "|---|---|---|---|---|---|---|"]
        md += ["| %(plant)s | %(state)s | %(mw).1f | %(units)d | %(classes)s | %(retired)s | %(first_dated)s |"
               % r for r in rows]
        md.append("")
    f = res["followup"]
    md += ["## %d plan (inventory %s) as of the latest report" % (f["year"], f["inventory"]), "",
           "%d generators, %.1f MW. MW by status now: %s." % (f["plan_n"], f["plan_mw"],
                                                            json.dumps(f["mw_by_status"])), "",
           "| plant | state | gen | MW | planned at Dec | now | planned now | retired |",
           "|---|---|---|---|---|---|---|---|"]
    for r in sorted(f["rows"], key=lambda r: (str(r["plant"]), str(r["generator_id"]))):
        md.append("| %(plant)s | %(state)s | %(generator_id)s | %(mw).1f | %(planned_at_dec)s | %(now)s | "
                  "%(planned_now)s | %(retired)s |" % r)
    md += ["", "## Diagnostics", "", "```", json.dumps(diag, indent=1, default=str), "```", ""]
    return "\n".join(md) + "\n"


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"),
                            recursive=True))
    return hits[0] if hits else None


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
    diag = {"parquet": os.path.basename(path), "schema": names,
            "missing_columns": [c for c in COLUMNS if c not in names]}
    df = prepare(pd.read_parquet(path, columns=[c for c in COLUMNS if c in names]))
    diag["records"] = int(len(df))
    diag["status_counts"] = {str(k): int(v) for k, v in df["status"].value_counts().items()}
    diag["records_with_retirement_date"] = int(df["ret_m"].notna().sum())
    diag["records_with_planned_retirement"] = int(df["plan_ret_m"].notna().sum())
    res = analyse(df)
    pd.DataFrame(res["generators"]).to_csv(os.path.join(a.out_dir, "coal_retired_generators.csv"),
                                           index=False)
    pd.DataFrame(res["followup"]["rows"]).to_csv(
        os.path.join(a.out_dir, "coal_plan_%d_followup.csv" % res["followup"]["year"]), index=False)
    md = render(res, diag)
    with open(os.path.join(a.out_dir, "coal_rows.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(a.out_dir, "coal_rows.json"), "w", encoding="utf-8") as fh:
        json.dump({"diagnostics": diag, **res}, fh, indent=1, default=str)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
