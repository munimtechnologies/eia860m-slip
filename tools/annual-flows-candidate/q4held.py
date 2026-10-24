"""q4held: EIA-860M's next-month share by months since the last listing, October to December 2026.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/q4held-plan.md (C1 and C2 are checks; Q1 to Q3 are predictions) on months whose
workbooks did not exist when the plan was fixed. The base is data/nexttech_cohort.csv at commit
ea63c15 (next-month groups from August 2015 to September 2026). Each scored month's group is the
monthrun_cohort.csv that monthrun.py 0.1.0 writes for that month (--target), appended in month
order; nextcount.annotate then counts each row's earlier listings and months since the last one.
Standard library only; needs nextcount.py 0.1.0 beside it.

    python q4held.py --month-file 2026-10=oct/monthrun_cohort.csv --month-file 2026-11=... \\
        --month-file 2026-12=... --months dec/monthrun_months.csv --out-dir /out

Practice on a month whose answer is published: --scored 2026-09 with the practice run's files. The
cohort rows of a scored month are then replaced by the appended ones, and both are compared.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys

import nextcount as nc

__version__ = "0.1.0"
COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"
SCORED = ("2026-10", "2026-11", "2026-12")
PLAN_URL = nc.BASE + "docs/q4held-plan.md"
CELLS = (
    ("first", lambda r: r["prior"] == 0),
    ("1 month", lambda r: r["gap"] == 1),
    ("2-3 months", lambda r: r["gap"] is not None and 2 <= r["gap"] <= 3),
    ("4-12 months", lambda r: r["gap"] is not None and 4 <= r["gap"] <= 12),
    ("more than 12 months", lambda r: r["gap"] is not None and r["gap"] > 12),
    ("5 or more earlier", lambda r: r["prior"] >= 5),
)
TECH_CELLS = ("first", "1 month", "2-3 months")


def month_rows(month, data):
    """A monthrun_cohort.csv's bytes -> cohort-like rows for that month (month, key, group, now, listing)."""
    rows = []
    for x in csv.DictReader(io.StringIO(data.decode("utf-8"), newline="")):
        rows.append({"month": month, "key": x["key"], "group": x["group"], "now": x["now"],
                     "technology": x["technology"], "listing": x["listing"]})
    return rows


def known_months(data):
    """A monthrun_months.csv (or monthcheck_months) -> {month: (cohort operating, cohort)}."""
    return {r["month"]: (int(r["cohort_operating"]), int(r["cohort"]))
            for r in csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))}


def build(cohort, appended, scored):
    """Cohort rows before the first scored month + the appended rows -> (annotated rows, identity).
    identity compares the appended rows of a scored month with the cohort's own rows of that month,
    where the cohort has them (practice only)."""
    first = min(scored)
    base = [r for r in cohort if r["month"] < first]
    identity = {}
    for m in scored:
        old = sorted((r["key"], r["now"]) for r in cohort if r["month"] == m)
        if old:
            new = sorted((r["key"], r["now"]) for r in appended if r["month"] == m)
            groups_old = {r["key"]: r["group"] for r in cohort if r["month"] == m}
            identity[m] = {"rows_equal": old == new, "cohort_rows": len(old), "appended_rows": len(new),
                           "group_differs": sum(1 for r in appended if r["month"] == m
                                                and groups_old.get(r["key"], r["group"]) != r["group"])}
    return nc.annotate(base + appended), identity


def checks(rows, scored, known):
    """-> (C1, C2) dicts. C1: each scored month's (operating, rows) equals monthrun's own numbers.
    C2: monthrun's listing column says first exactly when the row has no earlier listing."""
    c1 = {"months": {}}
    for m in scored:
        got = nc.frac([r for r in rows if r["month"] == m])
        c1["months"][m] = {"got": got, "known": known.get(m)}
    c1["held"] = all(v["known"] is not None and tuple(v["got"]) == tuple(v["known"]) for v in c1["months"].values())
    sel = [r for r in rows if r["month"] in scored]
    bad = [r["key"] + " " + r["month"] for r in sel if (r.get("listing") == "first") != (r["prior"] == 0)]
    c2 = {"rows": len(sel), "disagree": len(bad), "examples": bad[:10], "held": bool(sel) and not bad}
    return c1, c2


def cells(rows):
    return {name: nc.frac([r for r in rows if test(r)]) for name, test in CELLS}


def pred(pid, ok_checks, a, b, better, bar, min_cell):
    """better: 'a above b' or 'a below b'."""
    if not ok_checks or min(a[1], b[1]) < min_cell:
        out = "not scored"
    else:
        sa, sb = nc.share(a), nc.share(b)
        out = "held" if (sa > sb if better == "above" else sa < sb) else "failed"
    return {"id": pid, "outcome": out, "a": a, "b": b, "bar": bar}


def score(rows, scored, known, min_cell=nc.MIN_COHORT):
    c1, c2 = checks(rows, scored, known)
    pooled = [r for r in rows if r["month"] in scored]
    c = cells(pooled)
    ok = c1["held"] and c2["held"]
    preds = [
        pred("Q1", ok, c["1 month"], c["2-3 months"], "above",
             "repeat listings 1 month after the last one are on time more often than those 2-3 months after", min_cell),
        pred("Q2", ok, c["1 month"], c["first"], "above",
             "repeat listings 1 month after the last one are on time more often than first listings", min_cell),
        pred("Q3", ok, c["5 or more earlier"], c["first"], "below",
             "rows with 5 or more earlier listings are on time less often than first listings", min_cell),
    ]
    scored_n = [p for p in preds if p["outcome"] != "not scored"]
    return {"c1": c1, "c2": c2, "cells": c, "predictions": preds,
            "held": sum(p["outcome"] == "held" for p in scored_n), "scored": len(scored_n)}


def tables(rows, scored):
    out = {"months": [], "tech": []}
    for m in list(scored) + ["pooled"]:
        sel = [r for r in rows if (r["month"] in scored if m == "pooled" else r["month"] == m)]
        for name, c in cells(sel).items():
            out["months"].append({"month": m, "cell": name, "rows": c[1], "on_time": c[0], "share": nc.share(c)})
    pooled = [r for r in rows if r["month"] in scored]
    for g in nc.GROUPS:
        sel = [r for r in pooled if r["group"] == g]
        c = cells(sel)
        for name in TECH_CELLS:
            out["tech"].append({"group": g, "cell": name, "rows": c[name][1], "on_time": c[name][0],
                                "share": nc.share(c[name])})
    return out


def _f(v):
    return "" if v is None else "%.4f" % v


def render(res):
    s = res.get("score")
    md = ["# q4held %s: the next-month share by months since the last listing, %s" % (
        res["version"], " to ".join(sorted(set([res["scored"][0], res["scored"][-1]])))), "",
        "Scores docs/q4held-plan.md (C1, C2, Q1 to Q3). MV2 of Munim, Inc. (made with AI agents).", "",
        "Cohort file: %s (%s bytes, md5 %s; %s rows)." % (res["cohort"]["source"], res["cohort"]["bytes"],
                                                          res["cohort"]["md5"], res["cohort"]["rows"]), ""]
    for m, f in sorted(res["month_files"].items()):
        md.append("Month file %s: %s (%s bytes, md5 %s; %s rows)." % (m, f["path"], f["bytes"], f["md5"], f["rows"]))
    md.append("")
    if res.get("error"):
        return "\n".join(md + ["Error: %s" % res["error"], ""])
    md += ["## Checks and predictions", "", "| id | outcome | value |", "|---|---|---|"]
    c1 = s["c1"]
    md.append("| C1 | %s | %s |" % ("held" if c1["held"] else "failed", "; ".join(
        "%s: %s against %s" % (m, nc._cell(tuple(v["got"])), "missing" if v["known"] is None else nc._cell(tuple(v["known"])))
        for m, v in sorted(c1["months"].items()))))
    md.append("| C2 | %s | %d rows, %d disagree |" % ("held" if s["c2"]["held"] else "failed", s["c2"]["rows"],
                                                      s["c2"]["disagree"]))
    for p in s["predictions"]:
        md.append("| %s | %s | %s against %s |" % (p["id"], p["outcome"], nc._cell(tuple(p["a"])), nc._cell(tuple(p["b"]))))
    md += ["", "Held: %d of %d scored (C1 and C2 are checks, not counted)." % (s["held"], s["scored"]), ""]
    if res.get("identity"):
        md += ["## Practice: appended rows against the cohort's own rows", "",
               "| month | rows equal | cohort rows | appended rows | group differs |", "|---|---|---|---|---|"]
        for m, v in sorted(res["identity"].items()):
            md.append("| %s | %s | %d | %d | %d |" % (m, v["rows_equal"], v["cohort_rows"], v["appended_rows"],
                                                     v["group_differs"]))
        md.append("")
    md += ["## By month and cell", "", "| month | cell | generator-months | on time | share |", "|---|---|---|---|---|"]
    for t in res["tables"]["months"]:
        md.append("| %s | %s | %d | %d | %s |" % (t["month"], t["cell"], t["rows"], t["on_time"], _f(t["share"])))
    md += ["", "## By technology, pooled (reported, not scored)", "",
           "| technology | cell | generator-months | on time | share |", "|---|---|---|---|---|"]
    for t in res["tables"]["tech"]:
        md.append("| %s | %s | %d | %d | %s |" % (t["group"], t["cell"], t["rows"], t["on_time"], _f(t["share"])))
    return "\n".join(md + [""])


def plan_served(get=None):
    try:
        text = (get or nc.get)(PLAN_URL).decode("utf-8", "replace")
    except Exception as e:  # recorded, not raised
        return False, "%s: %s" % (type(e).__name__, e)
    return nc.PLAN_MARK in text, "served" if nc.PLAN_MARK in text else "no pre-registration mark"


def main(argv=None, get=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--month-file", action="append", default=[], help="YYYY-MM=path to that month's monthrun_cohort.csv")
    ap.add_argument("--months", required=True, help="monthrun_months.csv (or monthcheck_months) holding every scored month")
    ap.add_argument("--scored", default=",".join(SCORED))
    ap.add_argument("--require-plan", action="store_true", help="exit 3 unless docs/q4held-plan.md is served")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    scored = tuple(sorted(args.scored.split(",")))
    res = {"version": __version__, "nextcount": nc.__version__, "started_at": nc.now(), "scored": scored,
           "month_files": {}}
    if args.require_plan:
        ok, why = plan_served(get)
        print("%s plan %s: %s" % (nc.now(), PLAN_URL, why), flush=True)
        if not ok:
            return 3
    if args.cohort:
        with open(args.cohort, "rb") as fh:
            data = fh.read()
        src = args.cohort
    else:
        data, src = (get or nc.get)(nc.COHORT_URL), nc.COHORT_URL
    cohort = nc.load(data)
    res["cohort"] = {"source": src, "bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(cohort)}
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["cohort"]["md5"], len(cohort)), flush=True)
    files = dict(x.split("=", 1) for x in args.month_file)
    if res["cohort"]["md5"] != COHORT_MD5 or len(cohort) != nc.COHORT_ROWS:
        res["error"] = "cohort file is not the one at commit ea63c15 (md5 %s, %d rows)" % (COHORT_MD5, nc.COHORT_ROWS)
    elif sorted(files) != list(scored):
        res["error"] = "month files %s do not match the scored months %s" % (sorted(files), list(scored))
    appended = []
    if not res.get("error"):
        for m in scored:
            with open(files[m], "rb") as fh:
                b = fh.read()
            rows = month_rows(m, b)
            res["month_files"][m] = {"path": files[m], "bytes": len(b), "md5": hashlib.md5(b).hexdigest(), "rows": len(rows)}
            if len(set(r["key"] for r in rows)) != len(rows):
                res["error"] = "%s: a key is listed twice" % m
            appended += rows
    if not res.get("error"):
        with open(args.months, "rb") as fh:
            known = known_months(fh.read())
        rows, res["identity"] = build(cohort, appended, scored)
        res["score"] = score(rows, scored, known)
        res["tables"] = tables(rows, scored)
        with open(os.path.join(args.out_dir, "q4held_rows.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["month", "key", "group", "now", "listing", "prior", "gap"])
            for r in rows:
                if r["month"] in scored:
                    w.writerow([r["month"], r["key"], r["group"], r["now"], r.get("listing", ""), r["prior"],
                                "" if r["gap"] is None else r["gap"]])
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "q4held.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    md = render(res)
    with open(os.path.join(args.out_dir, "q4held.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 2 if res.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
