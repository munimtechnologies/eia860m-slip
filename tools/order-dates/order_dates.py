"""order_dates: do EIA-860M planned retirement dates follow DOE's 202(c) orders?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

Since May 2025 DOE has kept a set of generators from retiring with Federal Power Act
202(c) orders that run about 90 days and are renewed shortly before they expire. For each
generator an order covers, this reads its record in every monthly EIA-860M report (PUDL's
changelog) from the month of the plant's first order on, and compares its planned
retirement month with the expiry month of the order in force on the last day of the
report month (the latest order for the plant issued on or before that day that has not
yet expired). Checks and predictions: docs/order-dates-preregistration.md.

    python order_dates.py --data-dir /data --out-dir /out
"""

import argparse
import calendar
import csv
import datetime as dt
import glob
import json
import os

import numpy as np
import pandas as pd

VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
OPERATING = frozenset({"OP", "SB", "OS", "OA"})
COAL_CODES = frozenset({"BIT", "SUB", "LIG", "ANT", "RC", "WC", "SGC"})
COLUMNS = ("report_date", "valid_until_date", "plant_id_eia", "plant_name_eia", "generator_id",
           "state", "capacity_mw", "summer_capacity_mw", "planned_generator_retirement_date",
           "generator_retirement_date", "operational_status_code", "energy_source_code_1")
SCORED = ("exact", "plus1", "minus1", "later", "earlier")
# Fallback unit set when no listed generator ID matches: generators at the plant that were
# operating with a planned retirement in 2025-2026 in the report before the first order.
FALLBACK_LO, FALLBACK_HI = 2025 * 12, 2026 * 12 + 11
# Stated before the job ran (docs/order-dates-preregistration.md).
EXPECTED_RECORDS = 224408
AUG_2026 = {"campbell": "2026-11", "schahfer": "2026-10", "culley": "2026-09", "craig": "2026-09"}
SEP_2026 = {"campbell": "2026-11", "schahfer": "2026-12", "culley": "2026-12", "craig": "2026-12"}


def months(values):
    """Months since year 0 (year * 12 + month - 1) as floats, NaN where missing."""
    d = pd.to_datetime(pd.Series(values), errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype(float).to_numpy()


def month_str(m):
    if m is None or m != m:
        return ""
    m = int(m)
    return "%04d-%02d" % (m // 12, m % 12 + 1)


def month_of(day):
    return day.year * 12 + day.month - 1


def month_end(m):
    y, mo = m // 12, m % 12 + 1
    return dt.date(y, mo, calendar.monthrange(y, mo)[1])


def read_orders(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [{"order": r["order"].strip(), "plant_key": r["plant_key"].strip(),
             "issued": dt.date.fromisoformat(r["issued"].strip()),
             "expires": dt.date.fromisoformat(r["expires"].strip())} for r in rows]


def read_units(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [{"plant_key": r["plant_key"].strip(), "plant": r["plant"].strip(),
             "state": r["state"].strip().upper(), "pattern": r["name_pattern"].strip(),
             "coal_plant": r["coal_plant"].strip().lower() == "yes",
             "ids": [x.strip().upper() for x in r["generator_ids"].split("|") if x.strip()],
             "expected_plant_id": r.get("expected_plant_id", "").strip()} for r in rows]


def in_force(orders, day):
    """The latest-issued order with issued <= day <= expires, else None."""
    live = [o for o in orders if o["issued"] <= day <= o["expires"]]
    return max(live, key=lambda o: (o["issued"], o["expires"])) if live else None


def prepare(raw):
    df = raw.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["generator_id"] = df["generator_id"].astype(str).str.strip()
    df["plant_id"] = pd.to_numeric(df["plant_id_eia"], errors="coerce").astype("Int64").astype(str)
    df["key"] = df["plant_id"] + "/" + df["generator_id"]
    df["report_m"] = months(df["report_date"])
    df["valid_m"] = months(df["valid_until_date"])
    df["plan_ret_m"] = months(df["planned_generator_retirement_date"])
    df["ret_m"] = months(df["generator_retirement_date"])
    df["status"] = df["operational_status_code"].astype(str).str.strip().str.upper()
    df["state"] = df["state"].astype(str).str.strip().str.upper()
    df["plant_name_eia"] = df["plant_name_eia"].astype(str)
    df["fuel"] = df["energy_source_code_1"].astype(str).str.strip().str.upper()
    summer = pd.to_numeric(df["summer_capacity_mw"], errors="coerce")
    name = pd.to_numeric(df["capacity_mw"], errors="coerce")
    df["mw"] = summer.where(summer > 0, name).fillna(0.0)
    return df[df["report_m"].notna()].reset_index(drop=True)


def snapshot(df, m):
    """Each generator's record as of report month m (latest record reported by m, if still
    valid at m)."""
    s = df[df["report_m"] <= m].sort_values(["key", "report_m"], kind="mergesort")
    s = s.groupby("key").tail(1)
    s = s[s["valid_m"].isna() | (s["valid_m"] >= m)]
    return s.set_index("key")


def plant_rows(df, unit):
    p = df[(df["state"] == unit["state"])
           & df["plant_name_eia"].str.contains(unit["pattern"], case=False, regex=True, na=False)]
    if unit["coal_plant"]:
        coal_ids = set(p.loc[p["fuel"].isin(COAL_CODES), "plant_id"])
        p = p[p["plant_id"].isin(coal_ids)]
    return p


def match(plant, unit, first_m):
    """(generator keys, method) for the units an order covers."""
    hit = sorted(set(plant.loc[plant["generator_id"].str.upper().isin(unit["ids"]), "key"]))
    if hit:
        return hit, "generator_ids"
    if plant.empty:
        return [], "none"
    snap = snapshot(plant, first_m - 1)
    fb = snap[snap["status"].isin(OPERATING) & (snap["plan_ret_m"] >= FALLBACK_LO)
              & (snap["plan_ret_m"] <= FALLBACK_HI)]
    return sorted(fb.index), "fallback" if len(fb) else "none"


def classify(rec, order):
    """Class of one generator-month: its record against the order in force."""
    if rec is None:
        return "not_listed"
    if rec["status"] == "RE" or rec["ret_m"] == rec["ret_m"]:
        return "retired"
    if order is None:
        return "no_order"
    if rec["status"] not in OPERATING:
        return "not_operating"
    if rec["plan_ret_m"] != rec["plan_ret_m"]:
        return "no_date"
    d = int(rec["plan_ret_m"]) - month_of(order["expires"])
    return {0: "exact", 1: "plus1", -1: "minus1"}.get(d, "later" if d > 1 else "earlier")


def changes(seq):
    """Times a sequence of planned months changes value (missing values skipped)."""
    vals = [v for v in seq if v]
    return sum(1 for a, b in zip(vals, vals[1:]) if a != b)


def analyse(df, orders, units):
    last_m = int(df["report_m"].max())
    rows, plants = [], []
    for unit in units:
        po = [o for o in orders if o["plant_key"] == unit["plant_key"]]
        if not po:
            continue
        first_m = month_of(min(o["issued"] for o in po))
        plant = plant_rows(df, unit)
        keys, method = match(plant, unit, first_m)
        before = snapshot(plant, first_m - 1) if len(plant) else None
        sub = plant[plant["key"].isin(keys)]
        prow = []
        for m in range(first_m, last_m + 1):
            snap = snapshot(sub, m)
            order = in_force(po, month_end(m))
            for k in keys:
                rec = snap.loc[k] if k in snap.index else None
                c = classify(rec, order)
                prow.append({"plant_key": unit["plant_key"], "plant": unit["plant"], "key": k,
                             "generator_id": k.split("/", 1)[1], "report": month_str(m),
                             "status": "" if rec is None else rec["status"],
                             "planned": "" if rec is None else month_str(rec["plan_ret_m"]),
                             "order": order["order"] if order else "",
                             "order_expires": order["expires"].isoformat() if order else "",
                             "class": c})
        rows += prow
        n = [r for r in prow if r["class"] in SCORED]
        per_gen = {k: changes([r["planned"] for r in prow if r["key"] == k]) for k in keys}
        latest = [r for r in prow if r["report"] == month_str(last_m)]
        plants.append({
            "plant_key": unit["plant_key"], "plant": unit["plant"], "state": unit["state"],
            "method": method, "generators": [k for k in keys],
            "plant_ids": sorted(set(plant["plant_id"])),
            "expected_plant_id": unit["expected_plant_id"],
            "mw": round(float(sum(snapshot(sub, first_m - 1)["mw"])) if len(sub) else 0.0, 1),
            "first_order": month_str(first_m), "orders": len(po),
            "planned_before": sorted({month_str(before.at[k, "plan_ret_m"]) for k in keys
                                      if before is not None and k in before.index}),
            "planned_latest": sorted({r["planned"] for r in latest}),
            "scored": len(n), "exact": sum(r["class"] == "exact" for r in n),
            "plus1": sum(r["class"] == "plus1" for r in n),
            "classes": {c: sum(r["class"] == c for r in prow) for c in sorted({r["class"] for r in prow})},
            "max_changes": max(per_gen.values()) if per_gen else 0})
    return {"report_max": month_str(last_m), "rows": rows, "plants": plants}


def planned_at(rows, plant_key, report):
    return sorted({r["planned"] for r in rows if r["plant_key"] == plant_key and r["report"] == report})


def score(res, records):
    rows, plants = res["rows"], res["plants"]
    s = [r for r in rows if r["class"] in SCORED]
    n = len(s)
    exact = sum(r["class"] == "exact" for r in s)
    near = sum(r["class"] in ("exact", "plus1") for r in s)
    retired_live = [r for r in rows if r["class"] == "retired" and r["order"]]
    ratchet = [p["plant_key"] for p in plants if p["max_changes"] >= 2]
    out = {"C1": {"text": "every plant matches at least one generator",
                  "unmatched": [p["plant_key"] for p in plants if not p["generators"]]},
           "C2": {"text": "August 2026 planned months reproduce coal_plan_2026_followup.csv",
                  "got": {k: planned_at(rows, k, "2026-08") for k in AUG_2026}, "want": AUG_2026},
           "C3": {"text": "same PUDL copy as coal-rows-v1", "records": records,
                  "want": EXPECTED_RECORDS},
           "P1": {"text": "exact share >= 0.50", "n": n, "exact": exact,
                  "share": round(exact / n, 4) if n else None},
           "P2": {"text": "exact or +1 share >= 0.75", "n": n, "near": near,
                  "share": round(near / n, 4) if n else None},
           "P3": {"text": "no covered generator reported retired with an order in force",
                  "count": len(retired_live)},
           "P4": {"text": ">= 6 of 8 plants have a generator whose planned month changes >= 2 times",
                  "plants": ratchet, "count": len(ratchet)}}
    out["C1"]["pass"] = not out["C1"]["unmatched"]
    out["C2"]["pass"] = all(out["C2"]["got"][k] == [v] for k, v in AUG_2026.items())
    out["C3"]["pass"] = records == EXPECTED_RECORDS
    out["P1"]["hit"] = bool(n) and exact / n >= 0.5
    out["P2"]["hit"] = bool(n) and near / n >= 0.75
    out["P3"]["hit"] = not retired_live
    out["P4"]["hit"] = len(ratchet) >= 6
    if res["report_max"] >= "2026-09":
        got = {k: planned_at(rows, k, "2026-09") for k in SEP_2026}
        hits = [k for k, v in SEP_2026.items() if got[k] == [v]]
        out["P5"] = {"text": ">= 3 of 4 plants exactly at the expiry month in the September 2026 report",
                     "got": got, "want": SEP_2026, "plants_exact": hits, "hit": len(hits) >= 3}
    else:
        out["P5"] = {"text": "September 2026 report", "hit": None,
                     "note": "not scorable: latest report is %s" % res["report_max"]}
    return out


def render(res, sc, diag):
    md = ["# EIA-860M planned retirement dates against DOE 202(c) orders", "",
          "MV2 of Munim, Inc. (made with AI agents). order_dates %s. EIA-860M via PUDL's changelog, "
          "latest report %s. A generator-month is compared with the order in force on the last day "
          "of the report month." % (VERSION, res["report_max"]), "",
          "| plant | state | generators | method | MW | first order | orders | planned before | "
          "planned latest | scored | exact | +1 | max changes | classes |",
          "|" + "---|" * 14]
    for p in res["plants"]:
        md.append("| %s | %s | %s | %s | %.1f | %s | %d | %s | %s | %d | %d | %d | %d | %s |" % (
            p["plant"], p["state"], ", ".join(p["generators"]), p["method"], p["mw"],
            p["first_order"], p["orders"], ", ".join(p["planned_before"]),
            ", ".join(p["planned_latest"]), p["scored"], p["exact"], p["plus1"], p["max_changes"],
            json.dumps(p["classes"])))
    md += ["", "## Checks and predictions", "", "```", json.dumps(sc, indent=1, default=str), "```",
           "", "## Month by month", ""]
    for p in res["plants"]:
        md += ["### %s" % p["plant"], "", "| report | generator | status | planned | order | expires | class |",
               "|---|---|---|---|---|---|---|"]
        md += ["| %(report)s | %(generator_id)s | %(status)s | %(planned)s | %(order)s | %(order_expires)s | "
               "%(class)s |" % r for r in res["rows"] if r["plant_key"] == p["plant_key"]]
        md.append("")
    md += ["## Diagnostics", "", "```", json.dumps(diag, indent=1, default=str), "```", ""]
    return "\n".join(md) + "\n"


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"),
                            recursive=True))
    return hits[0] if hits else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--orders", default=os.path.join(HERE, "orders.csv"))
    ap.add_argument("--units", default=os.path.join(HERE, "units.csv"))
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    path = find_parquet(a.data_dir)
    if not path:
        raise SystemExit("no changelog_generators parquet under %s" % a.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in COLUMNS if c in names])
    diag = {"version": VERSION, "parquet": os.path.basename(path), "raw_records": int(len(raw)),
            "missing_columns": [c for c in COLUMNS if c not in names]}
    df = prepare(raw)
    diag["records"] = int(len(df))
    orders, units = read_orders(a.orders), read_units(a.units)
    diag["orders"] = len(orders)
    res = analyse(df, orders, units)
    diag["plant_ids"] = {p["plant_key"]: {"found": p["plant_ids"], "expected": p["expected_plant_id"]}
                         for p in res["plants"]}
    sc = score(res, diag["records"])
    pd.DataFrame(res["rows"]).to_csv(os.path.join(a.out_dir, "order_dates.csv"), index=False)
    md = render(res, sc, diag)
    with open(os.path.join(a.out_dir, "order_dates.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(a.out_dir, "order_dates.json"), "w", encoding="utf-8") as fh:
        json.dump({"diagnostics": diag, "score": sc, **res}, fh, indent=1, default=str)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
