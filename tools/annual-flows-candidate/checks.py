"""Pre-registered checks K2-K4 and L1-L3 for eia860m-slip 0.3.1
(docs/annual-flows-preregistration-v2.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. Standard library only.
Reads profile.json, slip.json, retire.json and flows.json from --out-dir and writes checks.json.
Run 1's figures below are from job eia860m-slip-030-v1 (eia860m-slip 0.3.0, 2026-10-18; its
flows.md and checks.json), as the pre-registration lists them. "To 0.1 MW" is read as a
difference of at most 0.1 MW, since sums of values rounded to 0.1 MW can differ by one step.

    python checks.py --out-dir /out
"""

import argparse
import json
import os

__version__ = "0.2.0"

REF_EXITS = 377
REF_ON_TIME, REF_NOT_ONLINE, SHARE_TOL = 0.3247, 0.1916, 0.0005
MW_TOL = 0.1 + 1e-6
YEARS = list(range(2016, 2026))
K3_YEARS = range(2017, 2026)
# Run 1, all technologies: January plan, built, not_listed and new_entry per year.
REF_PLAN = {2016: 0.0, 2017: 26268.8, 2018: 35982.4, 2019: 24826.1, 2020: 42753.9,
            2021: 43181.4, 2022: 46461.4, 2023: 52145.7, 2024: 59102.8, 2025: 60890.9}
REF_BUILT = {2016: 28779.3, 2017: 23644.6, 2018: 34720.3, 2019: 23896.4, 2020: 34513.1,
             2021: 39193.5, 2022: 34386.9, 2023: 45512.8, 2024: 51328.6, 2025: 58070.9}
REF_NOT_LISTED = {2016: 0.0, 2017: 425.3, 2018: 3500.3, 2019: 799.0, 2020: 1325.4,
                  2021: 763.3, 2022: 1104.8, 2023: 302.7, 2024: 1451.1, 2025: 1482.6}
REF_NEW_ENTRY = {2016: 9824.8, 2017: 4626.7, 2018: 9277.4, 2019: 4027.4, 2020: 8355.6,
                 2021: 6384.5, 2022: 8535.6, 2023: 12233.5, 2024: 11118.1, 2025: 13300.1}
# L1: the 2018 links, (old plant id, new plant id, generator id).
L1_LINKS = sorted([("60671", "3393", g) for g in ("CTG1", "CTG2", "STG1")]
                  + [("60138", "628", g) for g in ("1GTA", "1GTB", "2GTA", "2GTB",
                                                    "CC1ST", "CC2ST")])
L1_MW = 3141.5
# L2: two more links that must be found, (year, plan key, entry key, MW).
L2_LINKS = [(2019, "57567/VISTA", "62467/VISTA", 10.0), (2022, "64845/AREXP", "56336/AREXP", 145.0)]


def _split(key):
    plant, _, gen = key.partition("/")
    return plant, gen


def _same_gen(link):
    return (_split(link["plan_key"])[1].strip().casefold()
            == _split(link["entry_key"])[1].strip().casefold())


def _all_rows(flows):
    return {r["year"]: r for r in flows["by_group"] if r["group"] == "all"}


def evaluate(profile, slip, retire, flows):
    out = {}
    exits = retire["detection"]["operating_exits_without_retired_record"]
    out["K2"] = {"report_max": profile["report_max"], "operating_exits": exits,
                 "pass": profile["report_max"] == "2026-08" and exits == REF_EXITS}

    overall = slip["overall"][0]
    slip_plan = {r["year"]: r["planned_mw"] for r in slip["annual"] if r["group"] == "all"}
    flow_plan = {y: r["planned_mw"] for y, r in _all_rows(flows).items()}
    diffs = [abs(src.get(y, float("inf")) - REF_PLAN[y])
             for src in (slip_plan, flow_plan) for y in K3_YEARS]
    worst = max(diffs)
    out["K3"] = {"on_time": overall["on_time"], "not_online_12": overall["not_online_12"],
                 "max_planned_mw_diff": round(worst, 3) if worst != float("inf") else None,
                 "pass": (abs(overall["on_time"] - REF_ON_TIME) <= SHARE_TOL + 1e-9
                          and abs(overall["not_online_12"] - REF_NOT_ONLINE) <= SHARE_TOL + 1e-9
                          and worst <= MW_TOL)}

    rows = flows["by_group"] + flows["by_band"] + flows["pooled"]
    bad = [r for r in rows if not r["plan_identity_ok"] or not r.get("built_identity_ok", True)]
    out["K4"] = {"rows": len(rows), "rows_not_adding_up": len(bad),
                 "years": flows["years"],
                 "pass": not bad and flows["years"] == YEARS}

    links = flows["links"]
    l18 = [x for x in links if x["year"] == 2018]
    found = sorted((_split(x["plan_key"])[0], _split(x["entry_key"])[0],
                    _split(x["plan_key"])[1]) for x in l18)
    mw18 = sum(x["plan_mw"] for x in l18)
    out["L1"] = {"links_2018": len(l18), "mw_2018": round(mw18, 1),
                 "unexpected": [x for x in found if x not in L1_LINKS],
                 "pass": (len(l18) == 9 and found == L1_LINKS and all(_same_gen(x) for x in l18)
                          and abs(mw18 - L1_MW) <= MW_TOL)}

    def is_l2(x, ref):
        return ((x["year"], x["plan_key"], x["entry_key"]) == ref[:3]
                and abs(x["plan_mw"] - ref[3]) <= MW_TOL)

    missing = [list(ref) for ref in L2_LINKS if not any(is_l2(x, ref) for x in links)]
    known = set((2018, old + "/" + gen) for old, _, gen in L1_LINKS)
    known |= set((ref[0], ref[1]) for ref in L2_LINKS)
    extra = [x for x in links if (x["year"], x["plan_key"]) not in known]
    out["L2"] = {"links": len(links), "missing": missing, "extra_links": extra,
                 "pass": not missing}

    allrows = _all_rows(flows)
    bad_years = []
    for y in YEARS:
        r = allrows.get(y)
        if r is None:
            bad_years.append({"year": y, "missing": True})
            continue
        got = {"plan": r["planned_mw"], "built": r["built_mw"],
               "not_listed": r["not_listed"] + r["rekeyed_online"],
               "new_entry": r["new_entry"] + r["rekeyed"]}
        ref = {"plan": REF_PLAN[y], "built": REF_BUILT[y], "not_listed": REF_NOT_LISTED[y],
               "new_entry": REF_NEW_ENTRY[y]}
        off = {k: round(got[k] - ref[k], 1) for k in ref if abs(got[k] - ref[k]) > MW_TOL}
        if off:
            bad_years.append({"year": y, "off_by": off})
    out["L3"] = {"years_checked": len(YEARS), "years_off": bad_years, "pass": not bad_years}

    out["all_pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
    out["version"] = __version__
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    docs = {}
    for name in ("profile", "slip", "retire", "flows"):
        with open(os.path.join(args.out_dir, name + ".json"), encoding="utf-8") as fh:
            docs[name] = json.load(fh)
    result = evaluate(docs["profile"], docs["slip"], docs["retire"], docs["flows"])
    with open(os.path.join(args.out_dir, "checks.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
