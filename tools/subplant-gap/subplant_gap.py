"""Pre-registered count of EIA boilers that burn fuel inside a CEMS subplant of PUDL's
core_epa__assn_eia_epacamd_subplant_ids but are not matched to any EPA unit (the pattern of
PUDL issue #5681, Covanta Niagara, plant 50472).

Plan with every bar: docs/subplant-gap-plan.md in munimtechnologies/eia860m-slip
(pre-registration id subplant-gap-1). This script:

  1. waits until the plan is live (no data is read before that);
  2. downloads four of PUDL's nightly tables (the EPA-EIA crosswalk, the subplant crosswalk,
     the EIA-860 boiler-generator associations and EIA-923 monthly boiler fuel);
  3. for each year, finds the subplants with at least one EPA unit matched in that year's
     crosswalk, the EIA boilers linked to their generators, and which of those boilers burned
     fuel without being matched to an EPA unit (a "gap boiler");
  4. checks the gate (G0, G1) and the predictions (P1-P4) for the main year.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import io
import json
import os
import time
import urllib.request

import pandas as pd

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
TABLES = {
    "xw": "core_epa__assn_eia_epacamd",
    "sp": "core_epa__assn_eia_epacamd_subplant_ids",
    "bga": "core_eia860__assn_boiler_generator",
    "bf": "core_eia923__monthly_boiler_fuel",
}
COLUMNS = {
    "xw": ["report_year", "plant_id_epa", "emissions_unit_id_epa", "plant_id_eia",
           "boiler_id", "generator_id"],
    "sp": ["plant_id_eia", "plant_id_epa", "subplant_id", "emissions_unit_id_epa",
           "generator_id"],
    "bga": ["plant_id_eia", "report_date", "generator_id", "boiler_id"],
    "bf": ["plant_id_eia", "boiler_id", "energy_source_code", "report_date",
           "fuel_consumed_units", "fuel_mmbtu_per_unit"],
}
MAIN_YEAR = 2024
GATE_YEAR = 2023
GATE_PLANT = 50472
GATE_GAP = ("BLR3", "BLR4")
GATE_COVERED = ("BLR1", "BLR2")
GATE_HEAT = (7_000_000, 9_500_000)
MSW_CODES = ("MSW", "MSB", "MSN")
UA = {"User-Agent": "mv2-subplant-gap/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
SB = ["plant_id_eia", "subplant_id"]
PB = ["plant_id_eia", "boiler_id"]
PG = ["plant_id_eia", "generator_id"]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(url, timeout=300):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers)


def wait_for(url, token, minutes):
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url, 60)[0].decode("utf-8", "replace"):
                return True, polls, now()
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, now()
        time.sleep(60)


def load(key, raw):
    df = pd.read_parquet(io.BytesIO(raw), columns=COLUMNS[key])
    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(df["report_date"])
    if "report_year" in df.columns:
        df = df[df["report_year"].notna()].copy()
        df["report_year"] = df["report_year"].astype(int)
    for col in ("boiler_id", "generator_id", "emissions_unit_id_epa", "energy_source_code"):
        if col in df.columns:
            df[col] = df[col].astype("object").where(df[col].notna(), None)
    return df


# ---- the rule ---------------------------------------------------------------------------------

def boiler_heat(bf, year):
    """Annual EIA-923 heat input (MMBtu) of each boiler and the fuel it burned most of."""
    d = bf[bf["report_date"].dt.year == year].copy()
    d["mmbtu"] = d["fuel_consumed_units"].fillna(0) * d["fuel_mmbtu_per_unit"].fillna(0)
    by_fuel = d.groupby(PB + ["energy_source_code"], as_index=False, dropna=False)["mmbtu"].sum()
    top = (by_fuel.sort_values(["mmbtu", "energy_source_code"], ascending=[False, True])
           .drop_duplicates(PB)[PB + ["energy_source_code"]]
           .rename(columns={"energy_source_code": "top_fuel"}))
    heat = by_fuel.groupby(PB, as_index=False)["mmbtu"].sum()
    return heat.merge(top, on=PB, how="left")


def find_gaps(xw, sp, bga, bf, year):
    """One row per (plant, CEMS subplant, linked EIA boiler) for one year."""
    xy = xw[(xw["report_year"] == year) & xw["emissions_unit_id_epa"].notna()]
    units = xy[["plant_id_epa", "emissions_unit_id_epa"]].drop_duplicates()
    cems_sub = sp.merge(units, on=["plant_id_epa", "emissions_unit_id_epa"])[SB].drop_duplicates()
    gens = (sp[sp["generator_id"].notna()].merge(cems_sub, on=SB)[SB + ["generator_id"]]
            .drop_duplicates())
    by = (bga[bga["report_date"].dt.year == year][PG + ["boiler_id"]]
          .dropna().drop_duplicates())
    b = gens.merge(by, on=PG)[SB + ["boiler_id"]].drop_duplicates()

    covered = xy[xy["boiler_id"].notna()][PB].drop_duplicates().assign(covered=True)
    amb_gens = xy[xy["boiler_id"].isna() & xy["generator_id"].notna()][PG].drop_duplicates()
    amb_sub = gens.merge(amb_gens, on=PG)[SB].drop_duplicates().assign(ambiguous=True)

    b = b.merge(boiler_heat(bf, year), on=PB, how="left")
    b["mmbtu"] = b["mmbtu"].fillna(0.0)
    b = b.merge(covered, on=PB, how="left").merge(amb_sub, on=SB, how="left")
    b["covered"] = b["covered"].eq(True)
    b["ambiguous"] = b["ambiguous"].eq(True)
    b["gap"] = ~b["covered"] & (b["mmbtu"] > 0)
    b["gap_mmbtu"] = b["mmbtu"].where(b["gap"], 0.0)
    return b.sort_values(SB + ["boiler_id"]).reset_index(drop=True), len(cems_sub)


SUB_COLS = ["plant_id_eia", "subplant_id", "ambiguous", "boilers", "gap_boilers", "total_mmbtu",
            "gap_mmbtu", "gap_share", "gap_top_fuel", "gap_boiler_ids"]


def subplant_table(b):
    rows = []
    for (plant, sub), g in b.groupby(SB, sort=True):
        gaps = g[g["gap"]].sort_values(["gap_mmbtu", "boiler_id"], ascending=[False, True])
        total = float(g["mmbtu"].sum())
        gap = float(g["gap_mmbtu"].sum())
        rows.append({"plant_id_eia": int(plant), "subplant_id": int(sub),
                     "ambiguous": bool(g["ambiguous"].any()), "boilers": int(len(g)),
                     "gap_boilers": int(len(gaps)), "total_mmbtu": total, "gap_mmbtu": gap,
                     "gap_share": gap / total if total > 0 else float("nan"),
                     "gap_top_fuel": gaps["top_fuel"].iloc[0] if len(gaps) else None,
                     "gap_boiler_ids": ";".join(str(x) for x in gaps["boiler_id"])})
    return pd.DataFrame(rows, columns=SUB_COLS)


def summarize(b, subs, xw, sp, year):
    out = {}
    for name, keep in (("strict", ~b["ambiguous"]), ("all", pd.Series(True, index=b.index))):
        bb = b[keep]
        ss = subs[subs["ambiguous"].eq(False)] if name == "strict" else subs
        gap = bb[bb["gap"]].drop_duplicates(PB)
        uniq = bb.drop_duplicates(PB)
        half = ss[ss["gap_share"].notna() & (ss["gap_share"] > 0.5)]
        non_msw = half[~half["gap_top_fuel"].isin(MSW_CODES)]
        other_years = xw[(xw["report_year"] != year) & xw["emissions_unit_id_epa"].notna()
                         & xw["boiler_id"].notna()][PB].drop_duplicates()
        seen = gap.merge(other_years, on=PB)
        gap_plants = set(gap["plant_id_eia"])
        unmatched = sp[sp["generator_id"].isna() & sp["emissions_unit_id_epa"].notna()]
        out[name] = {
            "cems_subplants_with_boilers": int(len(ss)),
            "gap_boilers": int(len(gap)),
            "gap_plants": int(len(gap_plants)),
            "gap_mmbtu": float(gap["mmbtu"].sum()),
            "total_mmbtu_linked_boilers": float(uniq["mmbtu"].sum()),
            "subplants_gap_share_over_half": int(len(half)),
            "subplants_gap_share_over_half_not_msw": int(len(non_msw)),
            "gap_boilers_matched_in_another_year": int(len(seen)),
            "gap_plants_with_an_unmatched_epa_unit":
                int(len(gap_plants & set(unmatched["plant_id_eia"].dropna().astype(int)))),
            "gap_mmbtu_by_top_fuel": {str(k): float(v) for k, v in
                                      gap.groupby(gap["top_fuel"].fillna("none"))["mmbtu"]
                                      .sum().sort_values(ascending=False).items()},
        }
    out["ambiguous_subplants"] = int(subs["ambiguous"].sum()) if len(subs) else 0
    return out


def gate_g1(b):
    p = b[b["plant_id_eia"] == GATE_PLANT]
    rows = p[["subplant_id", "boiler_id", "mmbtu", "covered", "gap", "ambiguous"]].to_dict("records")
    gap_ids = set(p[p["gap"]]["boiler_id"])
    cov_ids = set(p[p["covered"]]["boiler_id"])
    heat = float(p.drop_duplicates("boiler_id")["gap_mmbtu"].sum())
    ok = (set(GATE_GAP) <= gap_ids and set(GATE_COVERED) <= cov_ids
          and GATE_HEAT[0] <= heat <= GATE_HEAT[1])
    return {"held": bool(ok), "gap_ids": sorted(gap_ids), "covered_ids": sorted(cov_ids),
            "gap_mmbtu": heat, "rows": rows}


def choose_years(xw, bga, bf):
    months = bf.groupby(bf["report_date"].dt.year)["report_date"].apply(
        lambda s: s.dt.month.nunique())
    full = {int(y) for y, m in months.items() if m == 12}
    years = (set(int(y) for y in xw["report_year"].dropna().unique())
             & set(int(y) for y in bga["report_date"].dt.year.unique()) & full)
    main = MAIN_YEAR if MAIN_YEAR in years else (max(years) if years else None)
    return sorted(years), main


def score(g0, g1, main):
    s = main["strict"]
    return {
        "G0": g0, "G1": g1,
        "P1": s["gap_plants"] >= 20,
        "P2": s["gap_mmbtu"] >= 25_000_000,
        "P3": s["subplants_gap_share_over_half"] >= 10,
        "P4": s["subplants_gap_share_over_half_not_msw"] >= 3,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--wait-for")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=150)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": VERSION, "started": now()}
    if args.wait_for:
        live, polls, at = wait_for(args.wait_for, args.token, args.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live; no data read"
            json.dump(res, open(os.path.join(args.out_dir, "subplant_gap.json"), "w"), indent=1)
            print(res["stopped"])
            return

    frames, g0 = {}, True
    res["downloads"] = {}
    for key, table in TABLES.items():
        for attempt in range(3):
            try:
                raw, headers = fetch(NIGHTLY % table)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(30)
        res["downloads"][table] = {"bytes": len(raw), "last_modified": headers.get("Last-Modified"),
                                   "etag": headers.get("ETag")}
        try:
            frames[key] = load(key, raw)
            res["downloads"][table]["rows"] = int(len(frames[key]))
        except Exception as exc:  # a missing column fails G0
            g0 = False
            res["downloads"][table]["error"] = repr(exc)[:400]
    if not g0:
        res["scores"] = {"G0": False}
        json.dump(res, open(os.path.join(args.out_dir, "subplant_gap.json"), "w"), indent=1)
        print(json.dumps(res, indent=1))
        return
    xw, sp, bga, bf = frames["xw"], frames["sp"], frames["bga"], frames["bf"]

    years, main_year = choose_years(xw, bga, bf)
    res["years"] = years
    res["main_year"] = main_year
    g0 = GATE_YEAR in years and main_year is not None
    res["by_year"] = {}
    for year in years:
        t0 = time.time()
        b, n_cems = find_gaps(xw, sp, bga, bf, year)
        subs = subplant_table(b)
        summ = summarize(b, subs, xw, sp, year)
        summ["cems_subplants"] = n_cems
        summ["seconds"] = round(time.time() - t0, 2)
        res["by_year"][str(year)] = summ
        if year == GATE_YEAR:
            res["G1"] = gate_g1(b)
        if year == main_year:
            b.to_csv(os.path.join(args.out_dir, "boilers_%d.csv" % year), index=False)
            subs.to_csv(os.path.join(args.out_dir, "subplants_%d.csv" % year), index=False)
            gaps = subs[subs["gap_boilers"] > 0].sort_values("gap_mmbtu", ascending=False)
            res["top_gap_subplants"] = gaps.head(40).to_dict("records")
        print(year, json.dumps(summ["strict"]), flush=True)
    g1 = bool(res.get("G1", {}).get("held"))
    if main_year is not None:
        res["scores"] = score(g0, g1, res["by_year"][str(main_year)])
    else:
        res["scores"] = {"G0": False}
    res["finished"] = now()
    with open(os.path.join(args.out_dir, "subplant_gap.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res["scores"]))


if __name__ == "__main__":
    main()
