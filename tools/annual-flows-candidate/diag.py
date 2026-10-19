"""Diagnose the two checks that failed in eia860m-slip 0.3.0's first annual-flows run.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Compete job eia860m-slip-030-v1 (2026-10-18) failed K2 (377 operating exits, reference
379) and K3 (the January 2018 plan rose 3.6% over 0.2.0's; limit 1%). This job imports
eia860m_slip.py 0.3.0 unchanged and prints, on the same PUDL file:

1. Each year's January plan under 0.3.0's reading of validity dates and under 0.2.0's
   (every end exclusive), with the generators only one reading has and their records.
2. Each year's not_listed plan capacity and new_entry built capacity at the same plants
   (a test of whether a generator dropped from the plan came back under a new id).
3. Operating exits under the id check's rule (eia860m-slip-v3: last record operating,
   valid_until before the last report) and under 0.3.0's (the same, less generators with
   any retired record), with the generators that differ.
4. Raw records since November 2025 of four gas plants from the gas-flows result.

It changes nothing and scores nothing. 0.1.1 only frees the raw table once it is
prepared, so the job fits in 2 GB; the output is the same as 0.1.0's. 0.1.2 fixes
records(): under pandas 3, astype(str) keeps missing values as NaN (a float), which
crashed 0.1.0's run (flows-diag-v1) after sections 1-3 were computed.

    python diag.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860m_slip as es

__version__ = "0.1.2"

EXTRA = ("plant_name_eia",)
YEARS = tuple(range(2017, 2026))
# eia860m-slip 0.2.0's January plans (all technologies), as in checks.py.
REF_PLANNED_ALL = {2017: 26236.8, 2018: 34723.5, 2019: 24812.1, 2020: 42505.9, 2021: 42861.4,
                   2022: 46062.1, 2023: 52142.9, 2024: 59099.8, 2025: 60887.1}
# Plants behind the largest moves out of the 2025-12 gas book (docs/gas-flows-output.md).
GAS_PLANTS = (728, 3399, 67262, 160)
REC_COLS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
            "current_planned_generator_operating_date", "generator_operating_date",
            "operational_status_code", "technology_description", "plant_name_eia")
MAX_RECORDS = 400


def old_until(df):
    """0.2.0's reading: every record ends at its valid_until_date, exclusive."""
    last_m = df["report_m"].max()
    return (df["valid_m"] - 1).fillna(last_m).clip(upper=last_m)


def jan_plan(df, year):
    jan, dec = year * 12, year * 12 + 11
    snap = es.snapshot(df, jan)
    return snap[snap["status"].isin(es.PLANNED) & (snap["planned_m"] >= jan)
                & (snap["planned_m"] <= dec)].set_index("key")


def _name(r):
    v = r.get("plant_name_eia")
    return v if isinstance(v, str) else ""


def plan_diff(new, old, years=YEARS):
    """Per year: January plan MW under each reading, and the generators only one reading has."""
    last_rec = new.groupby("key")["report_m"].max()
    rows, gens = [], []
    for y in years:
        a, b = jan_plan(new, y), jan_plan(old, y)
        only_new = a.loc[a.index.difference(b.index)]
        only_old = b.loc[b.index.difference(a.index)]
        rows.append({"year": y, "planned_030": round(float(a["capacity_mw"].sum()), 1),
                     "planned_020_rule": round(float(b["capacity_mw"].sum()), 1),
                     "ref_020": REF_PLANNED_ALL.get(y),
                     "only_030_mw": round(float(only_new["capacity_mw"].sum()), 1),
                     "only_030_n": int(len(only_new)),
                     "only_020_mw": round(float(only_old["capacity_mw"].sum()), 1),
                     "only_020_n": int(len(only_old))})
        for kind, part in (("only_030", only_new), ("only_020", only_old)):
            for k, r in part.sort_values("capacity_mw", ascending=False).iterrows():
                gens.append({"year": y, "kind": kind, "key": k, "plant": _name(r),
                             "group": r["group"], "status": r["status"],
                             "planned": es.month_str(r["planned_m"]),
                             "mw": round(float(r["capacity_mw"]), 1),
                             "record_from": es.month_str(r["report_m"]),
                             "valid_until": es.month_str(r["valid_m"]),
                             "last_record": bool(r["report_m"] == last_rec.get(k)),
                             "one_month": bool(r["valid_m"] == r["report_m"] + 1)})
    return rows, gens


def _plant(key):
    return key.split("/")[0]


def rekey(df, years=YEARS, lag=es.LAG):
    """Per year: not_listed plan MW and new_entry built MW, and how much of each sits at a plant
    that has both (a dropped generator possibly back under a new id)."""
    online = es.online_months(df)
    latest = es._latest(df)
    rows, gens = [], []
    for y in years:
        f = es.plan_fates(df, y, lag, online)
        b = es.built_sources(df, y, online, latest)
        gone = f[f["fate"] == "not_listed"]
        new = b[b["source"] == "new_entry"]
        both = set(gone["key"].map(_plant)) & set(new["key"].map(_plant))
        g2 = gone[gone["key"].map(_plant).isin(both)]
        n2 = new[new["key"].map(_plant).isin(both)]
        rows.append({"year": y, "not_listed_mw": round(float(gone["mw"].sum()), 1),
                     "not_listed_at_shared_plant_mw": round(float(g2["mw"].sum()), 1),
                     "new_entry_mw": round(float(new["mw"].sum()), 1),
                     "new_entry_at_shared_plant_mw": round(float(n2["mw"].sum()), 1),
                     "shared_plants": len(both)})
        for kind, part in (("not_listed", g2), ("new_entry", n2)):
            for r in part.sort_values("mw", ascending=False).itertuples(index=False):
                gens.append({"year": y, "kind": kind, "key": r.key, "group": r.group,
                             "mw": round(float(r.mw), 1)})
    return rows, gens


def exits(df):
    """Operating exits by the id check's rule and by 0.3.0's detection count."""
    last_m = df["report_m"].max()
    last = es._latest(df)
    idcheck = set(last[last["status"].isin(es.OPERATING) & (last["valid_m"] < last_m)].index)
    v030 = set(es._operating_exits(df).index)
    retired = set(df.loc[es.is_retired(df), "key"])
    detected = v030 - retired
    return {"idcheck_rule": len(idcheck), "v030_exits": len(v030),
            "v030_without_retired_record": len(detected),
            "idcheck_not_v030": sorted(idcheck - detected),
            "v030_not_idcheck": sorted(detected - idcheck),
            "idcheck_with_retired_record": sorted(idcheck & retired)}


def _text(v):
    """A record value as text: blank when missing, dates without a midnight time."""
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return ""
    v = str(v)
    return "" if v in ("nan", "NaT", "None", "<NA>") else v.replace(" 00:00:00", "")


def records(df, keys=None, plants=None, since=None):
    """Raw records (as text) of the given generators or plants, by generator and report."""
    sel = df
    if keys is not None:
        sel = sel[sel["key"].isin(list(keys))]
    if plants is not None:
        sel = sel[pd.to_numeric(sel["plant_id_eia"], errors="coerce").isin(list(plants))]
    if since is not None:
        sel = sel[sel["until_m"] >= since]
    sel = sel.sort_values(["key", "report_m"], kind="mergesort").head(MAX_RECORDS)
    cols = [c for c in REC_COLS if c in sel.columns]
    return [{c: _text(v) for c, v in rec.items()} for rec in sel[cols].to_dict("records")]


def run(df, old):
    plan_rows, plan_gens = plan_diff(df, old)
    rk_rows, rk_gens = rekey(df)
    ex = exits(df)
    top18 = [g["key"] for g in plan_gens if g["year"] == 2018 and g["kind"] == "only_030"][:25]
    rk18 = [g["key"] for g in rk_gens if g["year"] == 2018 and g["group"] == "gas_cc"][:40]
    return {
        "version": "diag %s on eia860m_slip %s" % (__version__, es.__version__),
        "report_max": es.month_str(df["report_m"].max()),
        "plan_diff": plan_rows, "plan_diff_generators": plan_gens,
        "rekey": rk_rows, "rekey_generators": rk_gens,
        "exits": ex,
        "records_exit_diff": records(df, keys=ex["idcheck_not_v030"] + ex["v030_not_idcheck"]),
        "records_2018_only_030": records(df, keys=top18),
        "records_2018_gas_cc_shared_plants": records(df, keys=rk18),
        "records_gas_plants": records(df, plants=GAS_PLANTS, since=2025 * 12 + 10),
    }


def render(res):
    md = ["# Why checks K2 and K3 failed in eia860m-slip 0.3.0's first annual-flows run", "",
          "%s; PUDL EIA-860M changelog to %s. MV2 of Munim, Inc. (made with AI agents). "
          "Diagnosis only: nothing here is scored." % (res["version"], res["report_max"]), "",
          "## 1. January plans under 0.3.0's and 0.2.0's reading of validity dates", ""]
    md += es.table(res["plan_diff"], ["year", "planned_030", "planned_020_rule", "ref_020",
                                      "only_030_mw", "only_030_n", "only_020_mw", "only_020_n"])
    md += ["", "Generators in only one reading (largest first, up to 60):", ""]
    md += es.table(res["plan_diff_generators"][:60],
                   ["year", "kind", "key", "plant", "group", "status", "planned", "mw",
                    "record_from", "valid_until", "last_record", "one_month"])
    md += ["", "## 2. Dropped from the plan, new in the year, at the same plants", ""]
    md += es.table(res["rekey"], ["year", "not_listed_mw", "not_listed_at_shared_plant_mw",
                                  "new_entry_mw", "new_entry_at_shared_plant_mw",
                                  "shared_plants"])
    md += ["", "2018 generators at shared plants:", ""]
    md += es.table([g for g in res["rekey_generators"] if g["year"] == 2018],
                   ["year", "kind", "key", "group", "mw"])
    ex = res["exits"]
    md += ["", "## 3. Operating exits", "",
           "id check rule: %d; 0.3.0 exits: %d; 0.3.0 exits without any retired record (the "
           "count K2 compared): %d." % (ex["idcheck_rule"], ex["v030_exits"],
                                        ex["v030_without_retired_record"]), "",
           "In the id check's count only: %s" % ", ".join(ex["idcheck_not_v030"]),
           "In 0.3.0's count only: %s" % ", ".join(ex["v030_not_idcheck"]),
           "id check exits with a retired record: %s" % ", ".join(ex["idcheck_with_retired_record"]),
           ""]
    for title, key in (("Records: exits that differ", "records_exit_diff"),
                       ("Records: largest 2018 generators only 0.3.0 has", "records_2018_only_030"),
                       ("Records: 2018 gas_cc generators at shared plants",
                        "records_2018_gas_cc_shared_plants"),
                       ("Records since 2025-11: gas plants %s" % ", ".join(map(str, GAS_PLANTS)),
                        "records_gas_plants")):
        md += ["## " + title, ""] + es.table(res[key], list(REC_COLS)) + [""]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    path = es.find_parquet(args.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in es.COLUMNS + EXTRA if c in names])
    df = es.prepare(raw)
    del raw  # prepare() works on its own copy; keeping both would hold three tables
    old = df.copy()
    old["until_m"] = old_until(df)
    res = run(df, old)
    with open(os.path.join(args.out_dir, "diag.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    text = render(res)
    with open(os.path.join(args.out_dir, "diag.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
