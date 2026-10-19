"""gen_202c: how much electricity did the plants under DOE 202(c) orders actually make?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A check for eia860m-slip.

DOE's plant orders keep units available; they do not say how much the units must run.
This reads EIA-923 monthly net generation (PUDL's core_eia923__monthly_generation, one
row per generator and month) for the units each order covers (data/doe_202c_plant_mw.csv)
and compares every full calendar month under order with the same calendar month in
2021-2024, before any order. Days under order come from data/doe_202c_orders.csv through
orders_202c.plant_dates. Checks and predictions: docs/gen-202c-preregistration.md.

A plant-month is the sum of the covered generators' net generation; it is missing if any
covered generator has no value that month. Its baseline is the mean of the same calendar
month over the reported years of 2021-2024 (at least two needed). A plant's ratio is its
net generation over the sum of baselines, both over the included months: full months under
order, reported, with a baseline.

    python gen_202c.py --data-dir /data --out-dir /out
"""

import argparse
import calendar
import csv
import datetime as dt
import glob
import json
import os

import orders_202c

__version__ = "0.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_YEARS = (2021, 2022, 2023, 2024)
MIN_BASE_YEARS = 2
WINDOW_START = "2026-01"
# Utility Dive (23 June 2026) put five plants' first-quarter output at 1.5 million MWh in
# 2026 against 4.3 million in 2025; compared, not scored (its exact definition is unknown).
UD_PLANTS = ("campbell", "centralia", "craig", "culley", "schahfer")
UD_Q1 = {"2026": 1.5e6, "2025": 4.3e6}


def load_units(path=None):
    """Covered units by plant_key: plant id, generator ids, summer MW."""
    path = path or os.path.join(HERE, "data", "doe_202c_plant_mw.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["plant_key"].strip(): {
            "plant": r["plant"].strip(), "plant_id": str(int(r["plant_id_eia"])),
            "gens": sorted(g.strip().upper() for g in r["generators"].split("|") if g.strip()),
            "mw": float(r["summer_mw"])} for r in csv.DictReader(fh)}


def month_key(year, month):
    return "%04d-%02d" % (year, month)


def month_days(m):
    y, mo = int(m[:4]), int(m[5:])
    return calendar.monthrange(y, mo)[1]


def month_range(first, last):
    y, mo = int(first[:4]), int(first[5:])
    out = []
    while month_key(y, mo) <= last:
        out.append(month_key(y, mo))
        y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
    return out


def order_days(orders, key, m):
    """Days of month m with an order for the plant in force."""
    y, mo = int(m[:4]), int(m[5:])
    first, last = dt.date(y, mo, 1), dt.date(y, mo, month_days(m))
    return sum(1 for d in orders_202c.plant_dates(orders, key, last) if first <= d <= last)


def plant_month(values, unit, m):
    """Sum of the covered generators' net MWh in month m, or None if any is missing."""
    got = [values.get((unit["plant_id"], g, m)) for g in unit["gens"]]
    return None if any(v is None for v in got) else round(sum(got), 3)


def baseline(values, unit, m):
    """(mean over reported base years of the same calendar month, years used) or (None, n)."""
    vals = [plant_month(values, unit, month_key(y, int(m[5:]))) for y in BASE_YEARS]
    vals = [v for v in vals if v is not None]
    if len(vals) < MIN_BASE_YEARS:
        return None, len(vals)
    return round(sum(vals) / len(vals), 3), len(vals)


def analyse(values, units, orders, last):
    """Month rows and per-plant totals up to month `last` (inclusive)."""
    rows, plants = [], []
    for key in sorted(units):
        unit = units[key]
        cover = orders_202c.plant_dates(orders, key, dt.date(int(last[:4]), int(last[5:]),
                                                             month_days(last)))
        if not cover:
            continue
        first = min(cover)
        prow = []
        for m in month_range(month_key(first.year, first.month), last):
            od = order_days(orders, key, m)
            v = plant_month(values, unit, m)
            b, nb = baseline(values, unit, m)
            full = od == month_days(m)
            prow.append({"plant_key": key, "month": m, "order_days": od, "full": full,
                         "mwh": v, "baseline_mwh": b, "base_years": nb,
                         "y2025_mwh": plant_month(values, unit, "2025" + m[4:]),
                         "included": full and v is not None and b is not None})
        rows += prow
        plants.append({"plant_key": key, "plant": unit["plant"], "mw": unit["mw"],
                       "first_order_day": first.isoformat(),
                       "all": totals(prow, unit["mw"]),
                       "w26": totals([r for r in prow if r["month"] >= WINDOW_START], unit["mw"]),
                       "missing_full_months": [r["month"] for r in prow
                                               if r["full"] and r["mwh"] is None]})
    return {"last": last, "rows": rows, "plants": plants,
            "combined_w26": totals([r for r in rows if r["month"] >= WINDOW_START],
                                   None, units)}


def totals(prow, mw, units=None):
    inc = [r for r in prow if r["included"]]
    gen = round(sum(r["mwh"] for r in inc), 1)
    base = round(sum(r["baseline_mwh"] for r in inc), 1)
    if units is None:
        mwh_cap = sum(mw * 24 * month_days(r["month"]) for r in inc)
    else:
        mwh_cap = sum(units[r["plant_key"]]["mw"] * 24 * month_days(r["month"]) for r in inc)
    return {"months": len(inc), "mwh": gen, "baseline_mwh": base,
            "ratio": round(gen / base, 4) if base > 0 else None,
            "cf": round(gen / mwh_cap, 4) if mwh_cap else None,
            "cf_baseline": round(base / mwh_cap, 4) if mwh_cap else None,
            "idle_months": sum(1 for r in inc if r["mwh"] <= 0)}


def quarter(values, units, keys, year):
    """First-quarter net MWh of the plants, or None if any plant-month is missing."""
    got = [plant_month(values, units[k], month_key(year, mo)) for k in keys for mo in (1, 2, 3)]
    return None if any(v is None for v in got) else round(sum(got), 1)


def score(res, values, units, coverage):
    p = {x["plant_key"]: x for x in res["plants"]}
    c = res["combined_w26"]
    out = {"C1": {"text": "data reach 2026-03 and every covered generator has a 2021-2024 value",
                  "last": res["last"], "no_base": coverage["no_base"]},
           "C2": {"text": "at least 6 of 8 plants have an included 2026 month",
                  "plants": sorted(k for k, x in p.items() if x["w26"]["months"])}}
    out["C1"]["pass"] = res["last"] >= "2026-03" and not coverage["no_base"]
    out["C2"]["pass"] = len(out["C2"]["plants"]) >= 6
    out["G1"] = {"text": "combined 2026 ratio below 0.50", "ratio": c["ratio"],
                 "hit": c["ratio"] is not None and c["ratio"] < 0.5}
    cen = [r for r in res["rows"] if r["plant_key"] == "centralia"
           and r["month"] >= WINDOW_START and r["mwh"] is not None]
    out["G2"] = {"text": "Centralia 2: net generation <= 0 in every reported 2026 month (>= 3 months)",
                 "months": {r["month"]: r["mwh"] for r in cen},
                 "hit": len(cen) >= 3 and all(r["mwh"] <= 0 for r in cen)}
    cam = p.get("campbell", {}).get("all", {}).get("ratio")
    out["G3"] = {"text": "Campbell ratio over all full order months between 0.55 and 0.85",
                 "ratio": cam, "hit": cam is not None and 0.55 <= cam <= 0.85}
    rated = {k: x["w26"]["ratio"] for k, x in p.items() if x["w26"]["ratio"] is not None}
    low = sorted(k for k, r in rated.items() if r < 0.75)
    out["G4"] = {"text": "at least 5 plants have a 2026 ratio below 0.75", "ratios": rated,
                 "below": low, "hit": len(low) >= 5}
    st = p.get("stanton", {}).get("w26", {})
    out["G5"] = {"text": "Stanton 1 ratio over its full 2026 order months below 0.50",
                 "months": st.get("months", 0), "ratio": st.get("ratio"),
                 "hit": None if not st.get("months") else st["ratio"] is not None and st["ratio"] < 0.5}
    out["X1"] = {"text": "compared, not scored: Utility Dive's five-plant first quarter",
                 "q1_2026": quarter(values, units, UD_PLANTS, 2026),
                 "q1_2025": quarter(values, units, UD_PLANTS, 2025), "utility_dive": UD_Q1}
    return out


def coverage_of(values, units, all_gens):
    no_base = []
    for key, u in sorted(units.items()):
        for g in u["gens"]:
            if not any((u["plant_id"], g, month_key(y, mo)) in values
                       for y in BASE_YEARS for mo in range(1, 13)):
                no_base.append("%s/%s" % (u["plant_id"], g))
    return {"no_base": no_base, "generators_at_plants": all_gens}


def fmt(v, pct=False):
    if v is None:
        return ""
    return "%.1f%%" % (100 * v) if pct else "{:,.0f}".format(v)


def render(res, sc, diag):
    md = ["# Net generation of the plants under DOE 202(c) orders", "",
          "MV2 of Munim, Inc. (made with AI agents). gen_202c %s. EIA-923 monthly net generation "
          "via PUDL, last month with data %s. Baseline: same calendar month, 2021-2024 mean." % (
              __version__, res["last"]), "",
          "| plant | MW | window | months | net MWh | baseline MWh | ratio | CF | CF baseline | "
          "idle months |", "|" + "---|" * 10]
    for x in res["plants"]:
        for w in ("w26", "all"):
            t = x[w]
            md.append("| %s | %.1f | %s | %d | %s | %s | %s | %s | %s | %d |" % (
                x["plant"], x["mw"], "2026" if w == "w26" else "since first order", t["months"],
                fmt(t["mwh"]), fmt(t["baseline_mwh"]), "" if t["ratio"] is None else "%.3f" % t["ratio"],
                fmt(t["cf"], True), fmt(t["cf_baseline"], True), t["idle_months"]))
    c = res["combined_w26"]
    md += ["", "Combined, 2026 months: %d plant-months, %s MWh against a baseline of %s MWh "
           "(ratio %s)." % (c["months"], fmt(c["mwh"]), fmt(c["baseline_mwh"]),
                            "" if c["ratio"] is None else "%.3f" % c["ratio"]), "",
           "## Checks and predictions", "", "```", json.dumps(sc, indent=1, default=str), "```",
           "", "## Month by month", "",
           "| plant | month | order days | full | net MWh | baseline MWh | base years | 2025 MWh | "
           "included |", "|" + "---|" * 9]
    for r in res["rows"]:
        md.append("| %s | %s | %d | %s | %s | %s | %d | %s | %s |" % (
            r["plant_key"], r["month"], r["order_days"], "yes" if r["full"] else "no",
            fmt(r["mwh"]), fmt(r["baseline_mwh"]), r["base_years"], fmt(r["y2025_mwh"]),
            "yes" if r["included"] else "no"))
    md += ["", "## Diagnostics", "", "```", json.dumps(diag, indent=1, default=str), "```", ""]
    return "\n".join(md) + "\n"


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*eia923__monthly_generation.parquet"),
                            recursive=True))
    return hits[0] if hits else None


def read_values(path, plant_ids):
    """({(plant_id, generator_id, 'YYYY-MM'): net MWh}, latest month with any value in the
    table, every generator listed at the plants with its months, maturity by month)."""
    import pandas as pd
    df = pd.read_parquet(path)
    gen = pd.to_numeric(df["net_generation_mwh"], errors="coerce")
    month = pd.to_datetime(df["report_date"], errors="coerce").dt.strftime("%Y-%m").fillna("")
    last = str(month[gen.notna() & (month != "")].max())
    pid = pd.to_numeric(df["plant_id_eia"], errors="coerce")
    sel = pid.isin([int(p) for p in plant_ids]) & gen.notna() & (month != "")
    sub = pd.DataFrame({"plant_id": pid[sel].astype(int).astype(str),
                        "gen": df.loc[sel, "generator_id"].astype(str).str.strip().str.upper(),
                        "month": month[sel], "mwh": gen[sel].astype(float)})
    sub = sub.groupby(["plant_id", "gen", "month"], as_index=False)["mwh"].sum()
    values = {(r.plant_id, r.gen, r.month): float(r.mwh) for r in sub.itertuples()}
    listed = {}
    for (p, g), grp in sub.groupby(["plant_id", "gen"]):
        listed["%s/%s" % (p, g)] = {"first": grp["month"].min(), "last": grp["month"].max(),
                                    "months": int(len(grp))}
    maturity = {}
    if "data_maturity" in df.columns:
        recent = df[gen.notna() & (month >= "2025-07")]
        m2 = month[recent.index]
        maturity = {m: sorted(set(recent.loc[m2 == m, "data_maturity"].astype(str)))
                    for m in sorted(set(m2))}
    return values, last, listed, maturity, {"records": int(len(df)), "columns": list(df.columns)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--orders", default=orders_202c.CSV)
    ap.add_argument("--units", default=os.path.join(HERE, "data", "doe_202c_plant_mw.csv"))
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    path = find_parquet(a.data_dir)
    if not path:
        raise SystemExit("no eia923 monthly_generation parquet under %s" % a.data_dir)
    units, orders = load_units(a.units), orders_202c.load(a.orders)
    values, last, listed, maturity, info = read_values(path, [u["plant_id"] for u in units.values()])
    res = analyse(values, units, orders, last)
    cov = coverage_of(values, units, listed)
    sc = score(res, values, units, cov)
    diag = {"version": __version__, "parquet": os.path.basename(path), **info,
            "maturity_by_month": maturity, "coverage": cov}
    with open(os.path.join(a.out_dir, "gen_202c_months.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res["rows"][0]))
        w.writeheader()
        w.writerows(res["rows"])
    md = render(res, sc, diag)
    with open(os.path.join(a.out_dir, "gen_202c.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(a.out_dir, "gen_202c.json"), "w", encoding="utf-8") as fh:
        json.dump({"diagnostics": diag, "score": sc, **res}, fh, indent=1, default=str)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
