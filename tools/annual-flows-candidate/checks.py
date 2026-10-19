"""Pre-registered checks K2-K4 for eia860m-slip 0.3.0 (docs/annual-flows-preregistration.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. Standard library only.
Reads profile.json, slip.json, retire.json and flows.json from --out-dir and writes checks.json.

    python checks.py --out-dir /out
"""

import argparse
import json
import os

# eia860m-slip 0.2.0 on the same PUDL file (compete job eia860m-slip-v2, 2026-10-15).
REF_ON_TIME, REF_NOT_ONLINE = 0.326, 0.188
REF_PLANNED_ALL = {2017: 26236.8, 2018: 34723.5, 2019: 24812.1, 2020: 42505.9, 2021: 42861.4,
                   2022: 46062.1, 2023: 52142.9, 2024: 59099.8, 2025: 60887.1}
# Operating generators whose last record ends before the last report (id check, eia860m-slip-v3).
REF_EXITS = 379


def evaluate(profile, slip, retire, flows):
    out = {}
    exits = retire["detection"]["operating_exits_without_retired_record"]
    out["K2"] = {"report_max": profile["report_max"], "operating_exits": exits,
                 "pass": profile["report_max"] == "2026-08" and exits == REF_EXITS}
    overall = slip["overall"][0]
    planned = {r["year"]: r["planned_mw"] for r in slip["annual"] if r["group"] == "all"}
    worst = max((abs(planned.get(y, 0.0) - v) / v for y, v in REF_PLANNED_ALL.items()),
                default=0.0)
    out["K3"] = {"on_time": overall["on_time"], "not_online_12": overall["not_online_12"],
                 "max_planned_mw_change": round(worst, 4),
                 "pass": (abs(overall["on_time"] - REF_ON_TIME) <= 0.005
                          and abs(overall["not_online_12"] - REF_NOT_ONLINE) <= 0.005
                          and worst <= 0.01)}
    rows = flows["by_group"] + flows["by_band"] + flows["pooled"]
    bad = [r for r in rows if not r["plan_identity_ok"] or not r.get("built_identity_ok", True)]
    out["K4"] = {"rows": len(rows), "rows_not_adding_up": len(bad),
                 "years": flows["years"],
                 "pass": not bad and flows["years"] == list(range(2016, 2026))}
    out["all_pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
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
