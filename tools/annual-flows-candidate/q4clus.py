"""q4clus: EIA-860M's next-month share for solar and batteries, October to December 2026, whole plants resampled.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/q4clus-plan.md (C1 and C2 are checks; R1 to R3 are direction bars; K1 to K3 are
consistency bars) on months whose workbooks did not exist when the plan was fixed. The rows are
those of q4held.py 0.1.0 (the cohort file at commit ea63c15 up to the month before the first scored
month, then each scored month's monthrun_cohort.csv), with C1 and C2 as q4held.checks counts them.
The cells and the plant resampling are those of clusterboot.py 0.1.0 (plant = the key before "/",
2,000 resamples, seed 20261025), used unchanged. Standard library only; needs nextcount.py,
q4held.py and clusterboot.py beside it.

    python q4clus.py --require-plan --month-file 2026-10=oct/monthrun_cohort.csv \\
        --month-file 2026-11=... --month-file 2026-12=... --months dec/monthrun_months.csv --out-dir /out

Practice on a month whose answer is published: --scored 2026-09 with the practice run's files.
"""

import argparse
import hashlib
import json
import math
import os
import sys

import clusterboot as cb
import nextcount as nc
import q4held as q4

__version__ = "0.1.0"
PLAN_URL = nc.BASE + "docs/q4clus-plan.md"
MIN_ROWS = 30     # every cell a bar compares needs at least 30 generator-months
MIN_PLANTS = 10   # and a consistency bar at least 10 plants in each cell
# Published generator-month cells (on time, rows) of the forty-first result (docs/clusterboot.md)
HISTORY = {
    "R1": ((1230, 2657), (1474, 3568)),   # B1: solar, 2016-2025, 1 month after minus first listings
    "R2": ((297, 816), (205, 728)),       # B2: batteries, 2016-2025, the same
    "R3": ((639, 1636), (171, 644)),      # B5: solar, January 2022 to August 2026, 1 month minus 2-3 months
}
# (id, technology, cell, compared cell, bar)
DIRECTION = (
    ("R1", "solar", "1 month", "first", "Solar: 1 month after the last listing minus first listings is above 0"),
    ("R2", "batteries", "1 month", "first", "Batteries: 1 month after the last listing minus first listings is "
                                            "above 0"),
    ("R3", "solar", "1 month", "2-3 months", "Solar: 1 month after the last listing minus 2-3 months after is "
                                             "above 0"),
)
# (id, direction bar whose interval is used, bar)
CONSISTENCY = (
    ("K1", "R1", "R1's 95% interval contains the forty-first result's B1 difference"),
    ("K2", "R2", "R2's 95% interval contains the forty-first result's B2 difference"),
    ("K3", "R3", "R3's 95% interval contains the forty-first result's B5 difference"),
)
# September 2026 cells (rows) from the q4held practice run; the expected size of three months is three times these
SEPTEMBER_ROWS = {("solar", "first"): 41, ("solar", "1 month"): 35, ("solar", "2-3 months"): 24,
                  ("batteries", "first"): 16, ("batteries", "1 month"): 11, ("batteries", "2-3 months"): 10}
DESIGN = 1.2      # the forty-first result's intervals were 1.07 to 1.22 times as wide as row-independent ones
REPORT = (("solar", "1 month", "first"), ("batteries", "1 month", "first"), ("solar", "1 month", "2-3 months"),
          ("wind", "1 month", "first"), ("gas", "1 month", "first"), (None, "1 month", "first"))


def history(pid):
    (a, b), (c, d) = HISTORY[pid]
    return a / b - c / d


def chance(pid, rows_x, rows_y, design=DESIGN):
    """Normal approximation of the chance that the point difference is above 0, if the scored months
    have the historical shares, the given cell sizes and intervals `design` times as wide."""
    (a, b), (c, d) = HISTORY[pid]
    px, py = a / b, c / d
    se = design * math.sqrt(px * (1 - px) / rows_x + py * (1 - py) / rows_y)
    return 0.5 * (1 + math.erf((px - py) / se / math.sqrt(2)))


def expected():
    """-> {bar id: (expected rows in the cell, in the compared cell, chance the bar holds)}."""
    out = {}
    for pid, g, x, y, _ in DIRECTION:
        rx, ry = 3 * SEPTEMBER_ROWS[(g, x)], 3 * SEPTEMBER_ROWS[(g, y)]
        out[pid] = (rx, ry, chance(pid, rx, ry))
    return out


def prepare(rows):
    """q4held rows (with prior and gap) -> the same rows with clusterboot's cell, plant and on-time flag."""
    return [dict(r, cell=cb.cell_of(r["gap"]), plant=r["key"].split("/")[0], ok=r["now"] == "Operating")
            for r in rows]


def score(a, scored, c1, c2, resamples=cb.RESAMPLES, min_rows=MIN_ROWS, min_plants=MIN_PLANTS):
    period = (min(scored), max(scored))
    ok = c1["held"] and c2["held"]
    direction, consistency, comp = [], [], {}
    for pid, g, x, y, bar in DIRECTION:
        r = cb.compare(a, period, g, x, y, 1, resamples)
        comp[pid] = r
        t = r["cells"]
        if not ok or min(t[1], t[3]) < min_rows:
            o = "not scored"
        else:
            o = "held" if r["point"] > 0 else "failed"
        direction.append({"id": pid, "outcome": o, "value": cb.fmt(r, x, y, 1), "bar": bar})
    for kid, pid, bar in CONSISTENCY:
        r, h = comp[pid], history(pid)
        t, p = r["cells"], r["plants"]
        if not ok or min(t[1], t[3]) < min_rows or min(p[:2]) < min_plants or r["lo"] is None:
            o = "not scored"
        else:
            o = "held" if r["lo"] <= h <= r["hi"] else "failed"
        inter = "not computed" if r["lo"] is None else "%+.4f to %+.4f" % (r["lo"], r["hi"])
        consistency.append({"id": kid, "outcome": o, "value": "%s against %+.4f" % (inter, h), "bar": bar})
    count = lambda ps: (sum(p["outcome"] == "held" for p in ps), sum(p["outcome"] != "not scored" for p in ps))
    return {"c1": c1, "c2": c2, "direction": direction, "consistency": consistency,
            "direction_held": count(direction), "consistency_held": count(consistency)}


def tables(a, scored, resamples=cb.RESAMPLES):
    """-> each scored month and the pooled months, every comparison of REPORT (reported, not scored)."""
    out = []
    for m in list(scored) + ["pooled"]:
        period = (min(scored), max(scored)) if m == "pooled" else (m, m)
        for g, x, y in REPORT:
            r = cb.compare(a, period, g, x, y, 1, resamples)
            out.append(dict(r, month=m, group=g or "all", label=cb.label(x, y, 1)))
    return out


def _bar_rows(ps):
    return ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in ps]


def render(res):
    md = ["# q4clus %s: solar and batteries by months since the last listing, %s, whole plants resampled" % (
        res["version"], " to ".join(sorted(set([res["scored"][0], res["scored"][-1]])))), "",
        "Scores docs/q4clus-plan.md (C1, C2, R1 to R3, K1 to K3). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("cohort"):
        md += ["Cohort file: %s (%s bytes, md5 %s; %s rows)." % (res["cohort"]["source"], res["cohort"]["bytes"],
                                                                res["cohort"]["md5"], res["cohort"]["rows"]), ""]
    for m, f in sorted(res["month_files"].items()):
        md.append("Month file %s: %s (%s bytes, md5 %s; %s rows)." % (m, f["path"], f["bytes"], f["md5"], f["rows"]))
    md.append("")
    if res.get("error"):
        return "\n".join(md + ["Error: %s" % res["error"], ""])
    s = res["score"]
    c1 = s["c1"]
    md += ["## Checks", "", "| id | outcome | value |", "|---|---|---|",
           "| C1 | %s | %s |" % ("held" if c1["held"] else "failed", "; ".join(
               "%s: %s against %s" % (m, nc._cell(tuple(v["got"])),
                                      "missing" if v["known"] is None else nc._cell(tuple(v["known"])))
               for m, v in sorted(c1["months"].items()))),
           "| C2 | %s | %d rows, %d disagree |" % ("held" if s["c2"]["held"] else "failed", s["c2"]["rows"],
                                                   s["c2"]["disagree"]),
           "", "## Direction bars", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += _bar_rows(s["direction"])
    md += ["", "Direction bars held: %d of %d scored." % s["direction_held"], "",
           "## Consistency bars", "", "| id | outcome | interval against the earlier difference | bar |",
           "|---|---|---|---|"]
    md += _bar_rows(s["consistency"])
    md += ["", "Consistency bars held: %d of %d scored. %d resamples, seed %d." % (
        s["consistency_held"] + (res["resamples"], cb.SEED)), ""]
    if res.get("identity"):
        md += ["## Practice: appended rows against the cohort's own rows", "",
               "| month | rows equal | cohort rows | appended rows | group differs |", "|---|---|---|---|---|"]
        for m, v in sorted(res["identity"].items()):
            md.append("| %s | %s | %d | %d | %d |" % (m, v["rows_equal"], v["cohort_rows"], v["appended_rows"],
                                                     v["group_differs"]))
        md.append("")
    md += ["## Every month, reported, not scored", "",
           "| month | technology | difference | point | 95% interval | cells (on time of rows, plants) |",
           "|---|---|---|---|---|---|"]
    for x in res["tables"]:
        t, p = x["cells"], x["plants"]
        inter = "not computed" if x["lo"] is None else "%+.4f to %+.4f" % (x["lo"], x["hi"])
        md.append("| %s | %s | %s | %+.4f | %s | %d of %d at %d plants; %d of %d at %d plants |" % (
            x["month"], x["group"], x["label"], x["point"], inter, t[0], t[1], p[0], t[2], t[3], p[1]))
    md += ["", "## Expected size and chance of each direction bar (fixed before scoring)", "",
           "| id | expected rows (cell, compared cell) | earlier difference | chance the point is above 0 |",
           "|---|---|---|---|"]
    for pid, (rx, ry, c) in sorted(res["expected"].items()):
        md.append("| %s | %d, %d | %+.4f | %.2f |" % (pid, rx, ry, history(pid), c))
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
    ap.add_argument("--scored", default=",".join(q4.SCORED))
    ap.add_argument("--resamples", type=int, default=cb.RESAMPLES)
    ap.add_argument("--require-plan", action="store_true", help="exit 3 unless docs/q4clus-plan.md is served")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    scored = tuple(sorted(args.scored.split(",")))
    res = {"version": __version__, "q4held": q4.__version__, "clusterboot": cb.__version__, "started_at": nc.now(),
           "scored": scored, "month_files": {}, "resamples": args.resamples, "seed": cb.SEED, "expected": expected()}
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
    if res["cohort"]["md5"] != q4.COHORT_MD5 or len(cohort) != nc.COHORT_ROWS:
        res["error"] = "cohort file is not the one at commit ea63c15 (md5 %s, %d rows)" % (q4.COHORT_MD5, nc.COHORT_ROWS)
    elif sorted(files) != list(scored):
        res["error"] = "month files %s do not match the scored months %s" % (sorted(files), list(scored))
    appended = []
    if not res.get("error"):
        for m in scored:
            with open(files[m], "rb") as fh:
                b = fh.read()
            rows = q4.month_rows(m, b)
            res["month_files"][m] = {"path": files[m], "bytes": len(b), "md5": hashlib.md5(b).hexdigest(), "rows": len(rows)}
            if len(set(r["key"] for r in rows)) != len(rows):
                res["error"] = "%s: a key is listed twice" % m
            appended += rows
    if not res.get("error"):
        with open(args.months, "rb") as fh:
            known = q4.known_months(fh.read())
        rows, res["identity"] = q4.build(cohort, appended, scored)
        c1, c2 = q4.checks(rows, scored, known)
        a = prepare(rows)
        res["score"] = score(a, scored, c1, c2, args.resamples)
        res["tables"] = tables(a, scored, args.resamples)
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "q4clus.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "q4clus.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 2 if res.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
