"""Look for generators that left a January plan under one id and came online under another.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

flows-diag-v3 (2026-10-19) showed that in 2018 no plant has both a generator dropped from
the January plan ("not_listed" in eia860m-slip 0.3.0's annual flows) and a generator that
came online unplanned ("new_entry"). So if the 3,141.5 MW of combined cycle on each side of
2018 is the same equipment under a new id, its plant id changed too. This job imports
eia860m_slip.py 0.3.0 unchanged and, for every closed year 2017-2025, pairs each not_listed
generator with a new_entry generator of the same technology group, in two passes:

  A (strict): capacity equal within 0.05 MW, first listed 0-3 months after the dropped
     generator's last listed month;
  B (loose):  capacity within 5%, first listed 0-6 months after, among what A left.

Each generator is used at most once (largest dropped capacity first; the closest capacity,
then the earliest listing, wins). It prints the matched capacity per year, every pair with
both plant names, and the raw records of the 2018 pairs. It changes nothing and scores
nothing.

    python rekey.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860m_slip as es

__version__ = "0.1.0"

YEARS = tuple(range(2017, 2026))
EXTRA = ("plant_name_eia",)
STRICT = {"name": "A", "mw_tol": 0.05, "rel_tol": 0.0, "gap": 3}
LOOSE = {"name": "B", "mw_tol": 0.0, "rel_tol": 0.05, "gap": 6}
REC_COLS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
            "current_planned_generator_operating_date", "generator_operating_date",
            "operational_status_code", "technology_description", "plant_name_eia")
MAX_RECORDS = 400
MAX_PAIRS = 120
YEAR_COLS = ("year", "not_listed_mw", "not_listed_n", "new_entry_mw", "new_entry_n",
             "strict_pairs", "strict_mw", "loose_pairs", "loose_mw", "loose_entry_mw",
             "matched_share", "cross_plant_pairs", "same_name_pairs")
PAIR_COLS = ("year", "pass", "dropped", "dropped_plant", "entry", "entry_plant", "group",
             "dropped_mw", "entry_mw", "last_listed", "first_listed", "months_apart",
             "same_plant", "same_name")


def _name(v):
    return v if isinstance(v, str) else ""


def _plant(key):
    return key.split("/")[0]


def listing(df):
    """Per generator: first report month, last listed month (0.3.0's reading) and the plant
    name in its last record."""
    s = df.sort_values(["key", "report_m"], kind="mergesort")
    g = s.groupby("key")
    return pd.DataFrame({"first_m": g["report_m"].min(), "last_m": g["until_m"].max(),
                         "name": g["plant_name_eia"].last().map(_name)})


def pairs(gone, new, info, rule, used, year):
    """Greedy one-to-one pairing of dropped generators with unplanned entries under `rule`."""
    out = []
    for g in gone.sort_values("mw", ascending=False).itertuples(index=False):
        if g.key in used:
            continue
        last = float(info.loc[g.key, "last_m"])
        best = None
        for n in new.itertuples(index=False):
            if n.key in used or n.group != g.group:
                continue
            gap = float(info.loc[n.key, "first_m"]) - last
            if gap < 0 or gap > rule["gap"]:
                continue
            d = abs(float(n.mw) - float(g.mw))
            if d > rule["mw_tol"] + rule["rel_tol"] * abs(float(g.mw)):
                continue
            cand = (d, gap, n.key)
            if best is None or cand < best[0]:
                best = (cand, n)
        if best is None:
            continue
        (d, gap, _), n = best
        used.add(g.key)
        used.add(n.key)
        gname, nname = info.loc[g.key, "name"], info.loc[n.key, "name"]
        out.append({"year": year, "pass": rule["name"], "dropped": g.key, "dropped_plant": gname,
                    "entry": n.key, "entry_plant": nname, "group": g.group,
                    "dropped_mw": round(float(g.mw), 1), "entry_mw": round(float(n.mw), 1),
                    "last_listed": es.month_str(last),
                    "first_listed": es.month_str(float(info.loc[n.key, "first_m"])),
                    "months_apart": int(gap), "same_plant": _plant(g.key) == _plant(n.key),
                    "same_name": bool(gname) and gname.casefold() == nname.casefold()})
    return out


def year_row(year, gone, new, pa, pb):
    nl = float(gone["mw"].sum())
    strict_mw = sum(p["dropped_mw"] for p in pa)
    loose_mw = sum(p["dropped_mw"] for p in pb)
    both = pa + pb
    return {"year": year, "not_listed_mw": round(nl, 1), "not_listed_n": int(len(gone)),
            "new_entry_mw": round(float(new["mw"].sum()), 1), "new_entry_n": int(len(new)),
            "strict_pairs": len(pa), "strict_mw": round(strict_mw, 1),
            "loose_pairs": len(pb), "loose_mw": round(loose_mw, 1),
            "loose_entry_mw": round(sum(p["entry_mw"] for p in pb), 1),
            "matched_share": round((strict_mw + loose_mw) / nl, 3) if nl else None,
            "cross_plant_pairs": sum(1 for p in both if not p["same_plant"]),
            "same_name_pairs": sum(1 for p in both if p["same_name"])}


def pooled(rows):
    tot = {"year": "all"}
    for c in YEAR_COLS[1:]:
        if c == "matched_share":
            continue
        tot[c] = round(sum(r[c] for r in rows), 1) if c.endswith("_mw") else sum(r[c] for r in rows)
    nl = tot["not_listed_mw"]
    tot["matched_share"] = round((tot["strict_mw"] + tot["loose_mw"]) / nl, 3) if nl else None
    return tot


def _text(v):
    """A record value as text: blank when missing, dates without a midnight time."""
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return ""
    v = str(v)
    return "" if v in ("nan", "NaT", "None", "<NA>") else v.replace(" 00:00:00", "")


def records(df, keys):
    """Raw records (as text) of the given generators, by generator and report."""
    sel = df[df["key"].isin(list(keys))]
    sel = sel.sort_values(["key", "report_m"], kind="mergesort").head(MAX_RECORDS)
    cols = [c for c in REC_COLS if c in sel.columns]
    return [{c: _text(v) for c, v in rec.items()} for rec in sel[cols].to_dict("records")]


def run(df, years=YEARS, record_year=2018):
    if "plant_name_eia" not in df.columns:
        df = df.assign(plant_name_eia="")
    online = es.online_months(df)
    latest = es._latest(df)
    info = listing(df)
    rows, allpairs = [], []
    for y in years:
        f = es.plan_fates(df, y, es.LAG, online)
        b = es.built_sources(df, y, online, latest)
        gone = f[f["fate"] == "not_listed"]
        new = b[b["source"] == "new_entry"]
        used = set()
        pa = pairs(gone, new, info, STRICT, used, y)
        pb = pairs(gone, new, info, LOOSE, used, y)
        rows.append(year_row(y, gone, new, pa, pb))
        allpairs += pa + pb
    keys = [p[k] for p in allpairs if p["year"] == record_year for k in ("dropped", "entry")]
    return {"version": "rekey %s on eia860m_slip %s" % (__version__, es.__version__),
            "report_max": es.month_str(df["report_m"].max()), "rules": [STRICT, LOOSE],
            "years": rows, "pooled": pooled(rows), "pairs": allpairs,
            "record_year": record_year, "records": records(df, keys)}


def render(res):
    md = ["# Re-keyed generators: dropped from a January plan under one id, online under another",
          "",
          "%s; PUDL EIA-860M changelog to %s. MV2 of Munim, Inc. (made with AI agents). "
          "Diagnosis only: nothing here is scored." % (res["version"], res["report_max"]), "",
          "Pass A: same technology group, capacity within 0.05 MW, first listed 0-3 months "
          "after the dropped generator's last listed month. Pass B: within 5%, 0-6 months, "
          "among what A left. MW are the dropped side unless named otherwise.", "",
          "## 1. Per year", ""]
    md += es.table(res["years"] + [res["pooled"]], list(YEAR_COLS))
    for name, title in (("A", "## 2. Pairs, pass A (strict)"), ("B", "## 3. Pairs, pass B (loose)")):
        part = [p for p in res["pairs"] if p["pass"] == name]
        md += ["", title, "", "%d pairs%s." % (len(part), "" if len(part) <= MAX_PAIRS
                                                  else "; the first %d by year" % MAX_PAIRS), ""]
        md += es.table(part[:MAX_PAIRS], list(PAIR_COLS))
    md += ["", "## 4. Raw records of the %s pairs" % res["record_year"], ""]
    md += es.table(res["records"], list(REC_COLS))
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
    del raw
    res = run(df)
    with open(os.path.join(args.out_dir, "rekey.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    text = render(res)
    with open(os.path.join(args.out_dir, "rekey.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
