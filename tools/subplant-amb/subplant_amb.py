"""Pre-registered test of whether PUDL's ambiguous CEMS subplants can be resolved: crosswalk rows
of core_epa__assn_eia_epacamd that tie an EPA unit to an EIA generator with a blank boiler_id
(the "ambiguous" subplants of subplant-gap-1, 602 of 1,328 CEMS subplants with boilers in 2024).

Plan with every bar: docs/subplant-amb-plan.md in munimtechnologies/eia860m-slip
(pre-registration id subplant-amb-1). This script:

  1. waits until the plan is live (no data is read before that);
  2. downloads the same four nightly PUDL tables as tools/subplant-gap/subplant_gap.py 0.1.0,
     whose functions it reuses unchanged (fetch, load, find_gaps, subplant_table, summarize);
  3. gives each ambiguous crosswalk row one class (covered, single, name or unresolved) and,
     where the class names a boiler, infers that boiler for the EPA unit;
  4. re-counts the gap boilers with the inferred boilers counted as matched and the resolved
     subplants moved into the strict count, and checks the gates (G0, G1) and P1-P4.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "subplant-gap"))

import pandas as pd  # noqa: E402

import subplant_gap as sg  # noqa: E402

VERSION = "0.1.0"
SG_VERSION = "0.1.0"
SG_MD5 = "276817f5826157f3f2dc6a94f94c730f"
MAIN_YEAR = 2024
G1_AMBIGUOUS = (580, 625)
G1_GAP_PLANTS = (6, 10)
CLASSES = ("covered", "single", "name", "unresolved")
ROW_COLS = ["plant_id_eia", "subplant_id", "emissions_unit_id_epa", "generator_id", "source",
            "candidates", "class", "boiler_id"]


def norm(x):
    """Upper case, letters and digits only, leading zeros dropped: 'ct-01' -> 'CT01', '01' -> '1'."""
    s = re.sub(r"[^A-Z0-9]", "", str(x).upper()).lstrip("0")
    return s or "0"


# ---- the rule ---------------------------------------------------------------------------------

def classify(xw, sp, bga, year):
    """One row per ambiguous crosswalk row (plant, EPA unit, generator) in a CEMS subplant with
    linked boilers, with its class and inferred boiler. Also returns how many ambiguous rows sit
    in subplants without linked boilers (left out, as in subplant-gap-1)."""
    xy = xw[(xw["report_year"] == year) & xw["emissions_unit_id_epa"].notna()]
    units = xy[["plant_id_epa", "emissions_unit_id_epa"]].drop_duplicates()
    cems_sub = sp.merge(units, on=["plant_id_epa", "emissions_unit_id_epa"])[sg.SB].drop_duplicates()
    gens = (sp[sp["generator_id"].notna()].merge(cems_sub, on=sg.SB)[sg.SB + ["generator_id"]]
            .drop_duplicates())
    by = (bga[bga["report_date"].dt.year == year][sg.PG + ["boiler_id"]]
          .dropna().drop_duplicates())
    linked = gens.merge(by, on=sg.PG).drop_duplicates()
    own = {k: sorted(set(g["boiler_id"])) for k, g in linked.groupby(sg.PG)}
    sub = {k: sorted(set(g["boiler_id"])) for k, g in linked.groupby(sg.SB)}
    covered = set(zip(xy[xy["boiler_id"].notna()]["plant_id_eia"],
                      xy[xy["boiler_id"].notna()]["boiler_id"]))
    amb = (xy[xy["boiler_id"].isna() & xy["generator_id"].notna()]
           [["plant_id_eia", "emissions_unit_id_epa", "generator_id"]].drop_duplicates()
           .merge(gens, on=sg.PG))

    rows, outside = [], 0
    for r in amb.itertuples(index=False):
        key = (r.plant_id_eia, r.subplant_id)
        if key not in sub:
            outside += 1
            continue
        mine = own.get((r.plant_id_eia, r.generator_id), [])
        source = "generator" if mine else "subplant"
        cands = [c for c in (mine or sub[key]) if (r.plant_id_eia, c) not in covered]
        targets = {norm(r.emissions_unit_id_epa), norm(r.generator_id)}
        named = [c for c in cands if norm(c) in targets]
        if not cands:
            cls, boiler = "covered", None
        elif len(cands) == 1:
            cls, boiler = "single", cands[0]
        elif len(named) == 1:
            cls, boiler = "name", named[0]
        else:
            cls, boiler = "unresolved", None
        rows.append({"plant_id_eia": r.plant_id_eia, "subplant_id": r.subplant_id,
                     "emissions_unit_id_epa": r.emissions_unit_id_epa,
                     "generator_id": r.generator_id, "source": source,
                     "candidates": ";".join(cands), "class": cls, "boiler_id": boiler})
    return pd.DataFrame(rows, columns=ROW_COLS), outside


def revise(b, rows):
    """find_gaps output with the inferred boilers counted as matched and only the subplants that
    still hold an unresolved row marked ambiguous."""
    inferred = set(zip(rows[rows["boiler_id"].notna()]["plant_id_eia"],
                       rows[rows["boiler_id"].notna()]["boiler_id"]))
    unresolved = set(zip(rows[rows["class"] == "unresolved"]["plant_id_eia"],
                         rows[rows["class"] == "unresolved"]["subplant_id"]))
    b2 = b.copy()
    b2["inferred"] = [k in inferred for k in zip(b2["plant_id_eia"], b2["boiler_id"])]
    b2["covered"] = b2["covered"] | b2["inferred"]
    b2["ambiguous"] = [k in unresolved for k in zip(b2["plant_id_eia"], b2["subplant_id"])]
    b2["gap"] = ~b2["covered"] & (b2["mmbtu"] > 0)
    b2["gap_mmbtu"] = b2["mmbtu"].where(b2["gap"], 0.0)
    return b2


def keys(subs):
    return set(zip(subs["plant_id_eia"], subs["subplant_id"]))


def metrics(rows, subs, subs2):
    amb = keys(subs[subs["ambiguous"].eq(True)])
    resolved = amb - keys(subs2[subs2["ambiguous"].eq(True)])
    r = subs2[[k in resolved for k in zip(subs2["plant_id_eia"], subs2["subplant_id"])]]
    return {
        "rows": int(len(rows)),
        "rows_by_class": {c: int((rows["class"] == c).sum()) for c in CLASSES},
        "rows_generator_without_boiler": int((rows["source"] == "subplant").sum()),
        "ambiguous_subplants": int(len(amb)),
        "ambiguous_subplants_with_a_row": int(len(keys(rows))),
        "resolved_subplants": int(len(resolved)),
        "resolved_linked_mmbtu": float(r["total_mmbtu"].sum()),
        "resolved_gap_mmbtu": float(r["gap_mmbtu"].sum()),
        "resolved_gap_plants": int(r[r["gap_boilers"] > 0]["plant_id_eia"].nunique()),
    }


def gate_g1(orig):
    return bool(G1_AMBIGUOUS[0] <= orig["ambiguous_subplants"] <= G1_AMBIGUOUS[1]
                and G1_GAP_PLANTS[0] <= orig["strict"]["gap_plants"] <= G1_GAP_PLANTS[1])


def score(g0, g1, m):
    return {
        "G0": g0, "G1": g1,
        "P1": m["ambiguous_subplants"] > 0 and m["resolved_subplants"] * 2 >= m["ambiguous_subplants"],
        "P2": m["rows"] > 0 and m["rows_generator_without_boiler"] >= 0.6 * m["rows"],
        "P3": m["resolved_linked_mmbtu"] > 0
        and m["resolved_gap_mmbtu"] < 0.01 * m["resolved_linked_mmbtu"],
        "P4": m["rows_by_class"]["name"] >= 100,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--wait-for")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=240)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, "subplant_amb.json")
    res = {"version": VERSION, "started": sg.now(), "subplant_gap_version": sg.VERSION,
           "subplant_gap_md5": hashlib.md5(open(sg.__file__, "rb").read()).hexdigest()}
    res["subplant_gap_md5_matches"] = res["subplant_gap_md5"] == SG_MD5
    if args.wait_for:
        live, polls, at = sg.wait_for(args.wait_for, args.token, args.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live; no data read"
            json.dump(res, open(path, "w"), indent=1)
            print(res["stopped"])
            return

    frames, g0 = {}, sg.VERSION == SG_VERSION
    res["downloads"] = {}
    for key, table in sg.TABLES.items():
        for attempt in range(3):
            try:
                raw, headers = sg.fetch(sg.NIGHTLY % table)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(30)
        res["downloads"][table] = {"bytes": len(raw), "last_modified": headers.get("Last-Modified"),
                                   "etag": headers.get("ETag")}
        try:
            frames[key] = sg.load(key, raw)
            res["downloads"][table]["rows"] = int(len(frames[key]))
        except Exception as exc:  # a missing column fails G0
            g0 = False
            res["downloads"][table]["error"] = repr(exc)[:400]
    if not g0:
        res["scores"] = {"G0": False}
        json.dump(res, open(path, "w"), indent=1, default=str)
        print(json.dumps(res, indent=1, default=str))
        return
    xw, sp, bga, bf = frames["xw"], frames["sp"], frames["bga"], frames["bf"]

    years, _ = sg.choose_years(xw, bga, bf)
    res["years"] = years
    g0 = MAIN_YEAR in years
    res["by_year"] = {}
    for year in years:
        b, _ = sg.find_gaps(xw, sp, bga, bf, year)
        subs = sg.subplant_table(b)
        orig = sg.summarize(b, subs, xw, sp, year)
        rows, outside = classify(xw, sp, bga, year)
        b2 = revise(b, rows)
        subs2 = sg.subplant_table(b2)
        rev = sg.summarize(b2, subs2, xw, sp, year)
        m = metrics(rows, subs, subs2)
        m["rows_outside_subplants_with_boilers"] = outside
        res["by_year"][str(year)] = {"subplant_gap": {"ambiguous_subplants":
                                                      orig["ambiguous_subplants"],
                                                      "strict": orig["strict"]},
                                     "rule": m, "revised": {"ambiguous_subplants":
                                                            rev["ambiguous_subplants"],
                                                            "strict": rev["strict"]}}
        if year == MAIN_YEAR:
            res["G1"] = {"held": gate_g1(orig), "ambiguous_subplants": orig["ambiguous_subplants"],
                         "strict_gap_plants": orig["strict"]["gap_plants"]}
            rows.to_csv(os.path.join(args.out_dir, "ambiguous_rows_%d.csv" % year), index=False)
            subs2.to_csv(os.path.join(args.out_dir, "subplants_revised_%d.csv" % year), index=False)
            gaps = subs2[(subs2["gap_boilers"] > 0) & subs2["ambiguous"].eq(False)]
            res["top_revised_gap_subplants"] = (gaps.sort_values("gap_mmbtu", ascending=False)
                                                .head(40).to_dict("records"))
            res["unresolved_examples"] = rows[rows["class"] == "unresolved"].head(40).to_dict(
                "records")
        print(year, json.dumps(m), flush=True)
    if MAIN_YEAR in years:
        res["scores"] = score(g0, res["G1"]["held"], res["by_year"][str(MAIN_YEAR)]["rule"])
    else:
        res["scores"] = {"G0": False}
    res["finished"] = sg.now()
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res["scores"]))


if __name__ == "__main__":
    main()
