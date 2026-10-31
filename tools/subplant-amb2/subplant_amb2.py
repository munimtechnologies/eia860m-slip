"""Pre-registered test of a second rule for PUDL's ambiguous CEMS crosswalk rows: an unresolved
row of subplant-amb-1 whose EPA unit already has a boiler (from a crosswalk row with a boiler_id,
or inferred for another of its rows by subplant-amb-1's rule) is set aside as "unit".

Plan with every bar: docs/subplant-amb2-plan.md in munimtechnologies/eia860m-slip
(pre-registration id subplant-amb-2). This script:

  1. waits until the plan is live (no data is read before that);
  2. downloads the same four nightly PUDL tables through tools/subplant-gap/subplant_gap.py 0.1.0
     and runs tools/subplant-amb/subplant_amb.py 0.1.0's rule unchanged (classify, revise);
  3. moves each unresolved row whose EPA unit already has a boiler to the class "unit";
  4. re-counts the gap boilers with only the rows still unresolved marking a subplant ambiguous,
     and checks the gates (G0, G1) and Q1-Q4.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "subplant-amb"))
sys.path.append(os.path.join(HERE, "..", "subplant-gap"))

import pandas as pd  # noqa: E402

import subplant_amb as sa  # noqa: E402

sg = sa.sg

VERSION = "0.1.0"
SA_VERSION = "0.1.0"
SA_MD5 = "2dec70ebe46e81d6fb2a1500f0e7e632"
MAIN_YEAR = 2024
G1_UNRESOLVED = (400, 470)
G1_RESOLVED = (420, 465)
CLASSES = ("covered", "single", "name", "unit", "unresolved")


def md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ---- the second rule --------------------------------------------------------------------------

def unit_rule(xw, rows, year):
    """subplant-amb-1's rows with each unresolved row whose (plant, EPA unit) already has a boiler
    moved to the class "unit". A unit has a boiler if a year-Y crosswalk row names one for it, or
    if subplant-amb-1's rule inferred one for another of its rows."""
    xy = xw[(xw["report_year"] == year) & xw["emissions_unit_id_epa"].notna()]
    named = xy[xy["boiler_id"].notna()]
    has = set(zip(named["plant_id_eia"], named["emissions_unit_id_epa"]))
    inferred = rows[rows["boiler_id"].notna()]
    has |= set(zip(inferred["plant_id_eia"], inferred["emissions_unit_id_epa"]))
    out = rows.copy()
    hit = pd.Series([c == "unresolved" and k in has for c, k in
                     zip(out["class"], zip(out["plant_id_eia"], out["emissions_unit_id_epa"]))],
                    index=out.index, dtype=bool)
    out.loc[hit, "class"] = "unit"
    return out


def in_keys(df, keys):
    return pd.Series([k in keys for k in zip(df["plant_id_eia"], df["subplant_id"])],
                     index=df.index, dtype=bool)


def metrics(rows1, rows2, subs, subs1, subs2, b2):
    """Counts for one year. subs: subplant-gap-1; subs1: after rule 1; subs2 and b2: after both."""
    amb0 = sa.keys(subs[subs["ambiguous"].eq(True)])
    amb1 = sa.keys(subs1[subs1["ambiguous"].eq(True)])
    amb2 = sa.keys(subs2[subs2["ambiguous"].eq(True)])
    new = amb1 - amb2
    r = subs2[in_keys(subs2, new)]
    g = b2[in_keys(b2, new) & b2["gap"].astype(bool)]
    hrsg = pd.Series(["HRSG" in sa.norm(x) for x in g["boiler_id"]], index=g.index, dtype=bool)
    return {
        "rows": int(len(rows2)),
        "rows_by_class": {c: int((rows2["class"] == c).sum()) for c in CLASSES},
        "unresolved_rule1": int((rows1["class"] == "unresolved").sum()),
        "ambiguous_subplants": int(len(amb0)),
        "ambiguous_after_rule1": int(len(amb1)),
        "ambiguous_after_rule2": int(len(amb2)),
        "resolved_by_rule2": int(len(new)),
        "rule2_linked_mmbtu": float(r["total_mmbtu"].sum()),
        "rule2_gap_mmbtu": float(r["gap_mmbtu"].sum()),
        "rule2_gap_plants": int(r[r["gap_boilers"] > 0]["plant_id_eia"].nunique()),
        "rule2_gap_hrsg_mmbtu": float(g.loc[hrsg, "gap_mmbtu"].sum()),
    }


def gate_g1(m):
    resolved1 = m["ambiguous_subplants"] - m["ambiguous_after_rule1"]
    return bool(G1_UNRESOLVED[0] <= m["unresolved_rule1"] <= G1_UNRESOLVED[1]
                and G1_RESOLVED[0] <= resolved1 <= G1_RESOLVED[1])


def score(g0, g1, m):
    return {
        "G0": g0, "G1": g1,
        "Q1": m["unresolved_rule1"] > 0
        and m["rows_by_class"]["unit"] * 2 >= m["unresolved_rule1"],
        "Q2": m["ambiguous_after_rule2"] <= 100,
        "Q3": m["rule2_linked_mmbtu"] > 0
        and m["rule2_gap_mmbtu"] < 0.10 * m["rule2_linked_mmbtu"],
        "Q4": m["rule2_gap_mmbtu"] > 0
        and m["rule2_gap_hrsg_mmbtu"] * 2 >= m["rule2_gap_mmbtu"],
    }


def one_year(xw, sp, bga, bf, year):
    b, _ = sg.find_gaps(xw, sp, bga, bf, year)
    subs = sg.subplant_table(b)
    rows1, outside = sa.classify(xw, sp, bga, year)
    subs1 = sg.subplant_table(sa.revise(b, rows1))
    rows2 = unit_rule(xw, rows1, year)
    b2 = sa.revise(b, rows2)
    subs2 = sg.subplant_table(b2)
    m = metrics(rows1, rows2, subs, subs1, subs2, b2)
    m["rows_outside_subplants_with_boilers"] = outside
    rev = sg.summarize(b2, subs2, xw, sp, year)
    return m, rev, rows2, subs1, subs2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--wait-for")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=240)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, "subplant_amb2.json")
    res = {"version": VERSION, "started": sg.now(), "subplant_amb_version": sa.VERSION,
           "subplant_gap_version": sg.VERSION, "subplant_amb_md5": md5(sa.__file__),
           "subplant_gap_md5": md5(sg.__file__)}
    res["md5_match"] = res["subplant_amb_md5"] == SA_MD5 and res["subplant_gap_md5"] == sa.SG_MD5
    if args.wait_for:
        live, polls, at = sg.wait_for(args.wait_for, args.token, args.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live; no data read"
            json.dump(res, open(path, "w"), indent=1)
            print(res["stopped"])
            return

    g0 = sa.VERSION == SA_VERSION and sg.VERSION == sa.SG_VERSION and res["md5_match"]
    frames = {}
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
    if len(frames) < len(sg.TABLES):
        res["scores"] = {"G0": False}
        json.dump(res, open(path, "w"), indent=1, default=str)
        print(json.dumps(res, indent=1, default=str))
        return
    xw, sp, bga, bf = frames["xw"], frames["sp"], frames["bga"], frames["bf"]

    years, _ = sg.choose_years(xw, bga, bf)
    res["years"] = years
    g0 = g0 and MAIN_YEAR in years
    res["by_year"] = {}
    for year in years:
        m, rev, rows2, subs1, subs2 = one_year(xw, sp, bga, bf, year)
        res["by_year"][str(year)] = {"rules": m, "revised": {"ambiguous_subplants":
                                                             rev["ambiguous_subplants"],
                                                             "strict": rev["strict"]}}
        if year == MAIN_YEAR:
            rows2.to_csv(os.path.join(args.out_dir, "ambiguous_rows2_%d.csv" % year), index=False)
            subs2.to_csv(os.path.join(args.out_dir, "subplants_revised2_%d.csv" % year),
                         index=False)
            new = sa.keys(subs1[subs1["ambiguous"].eq(True)]) - sa.keys(
                subs2[subs2["ambiguous"].eq(True)])
            gaps = subs2[in_keys(subs2, new) & (subs2["gap_boilers"] > 0)]
            res["top_rule2_gap_subplants"] = (gaps.sort_values("gap_mmbtu", ascending=False)
                                              .head(40).to_dict("records"))
            res["unresolved_examples"] = rows2[rows2["class"] == "unresolved"].head(40).to_dict(
                "records")
        print(year, json.dumps(m), flush=True)
    if MAIN_YEAR in years:
        m = res["by_year"][str(MAIN_YEAR)]["rules"]
        res["G1"] = {"held": gate_g1(m), "unresolved_rule1": m["unresolved_rule1"],
                     "resolved_rule1": m["ambiguous_subplants"] - m["ambiguous_after_rule1"]}
        res["scores"] = score(g0, res["G1"]["held"], m)
    else:
        res["scores"] = {"G0": False}
    res["finished"] = sg.now()
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps(res["scores"]))


if __name__ == "__main__":
    main()
