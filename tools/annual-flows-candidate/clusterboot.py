"""clusterboot: EIA-860M's next-month share by months since the last listing, with whole plants resampled.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/clusterboot-plan.md (C0 is a reproduction check; B1 to B5 are predictions). The fortieth
result (docs/plantw.md) found that weighting each plant once lifts every repeat-listing cell, so it
changes the question instead of answering it. Here the share stays the share of generator-months on
time, and rows of one plant are kept together: for each bar, the plants with rows in either compared
cell are resampled with replacement 2,000 times with a fixed seed, the difference of the two cells'
shares is recomputed from all rows of the drawn plants, and the bar is judged on the 95% interval of
those differences. The cells are those of gaptech.py 0.1.0 and plantw.py 0.1.0, written out again so
that the job needs no other file. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python clusterboot.py --wait-plan --deadline 2026-10-25T23:00 --out-dir /out
"""

import argparse
import csv
import hashlib
import io
import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timezone

__version__ = "0.1.0"
BASE = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/"
PLAN_URL = BASE + "main/docs/clusterboot-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
COHORT_URL = BASE + "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"
COHORT_ROWS = 14807
COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"
POOL = ("2016-01", "2025-12")
RECENT = ("2022-01", "2026-08")
PERIODS = (("2016-01", "2019-12"), ("2020-01", "2021-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
CELLS = ("first",) + tuple(x[2] for x in GAPS)
MIN_PLANTS = 30
RESAMPLES = 2000
SEED = 20261025
# docs/plantw-plan.md: generator-months (on time, rows) of the compared cells, as already published
KNOWN = {
    (POOL, "solar", "first"): (1474, 3568), (POOL, "solar", "1 month"): (1230, 2657),
    (POOL, "batteries", "first"): (205, 728), (POOL, "batteries", "1 month"): (297, 816),
    (POOL, "wind", "first"): (237, 497), (POOL, "wind", "1 month"): (191, 465),
    (POOL, "gas", "first"): (312, 687), (POOL, "gas", "1 month"): (206, 576),
    (RECENT, "solar", "1 month"): (639, 1636), (RECENT, "solar", "2-3 months"): (171, 644),
}
# (id, period, technology, cell, compared cell, sign, expect, bar). The difference is sign * (share of
# the cell - share of the compared cell). "above": the bar holds if the interval's lower end is above 0;
# "spans": it holds if the interval includes 0.
BARS = (
    ("B1", POOL, "solar", "1 month", "first", 1, "above", "2016-2025, solar: 1 month after the last listing minus "
                                                          "first listings; the 95% interval is above 0"),
    ("B2", POOL, "batteries", "1 month", "first", 1, "above", "2016-2025, batteries: 1 month after the last listing "
                                                              "minus first listings; the 95% interval is above 0"),
    ("B3", POOL, "wind", "1 month", "first", -1, "spans", "2016-2025, wind: first listings minus 1 month after the "
                                                          "last listing; the 95% interval includes 0"),
    ("B4", POOL, "gas", "1 month", "first", -1, "spans", "2016-2025, gas: first listings minus 1 month after the "
                                                         "last listing; the 95% interval includes 0"),
    ("B5", RECENT, "solar", "1 month", "2-3 months", 1, "above", "January 2022 to August 2026, solar: 1 month after "
                                                                 "the last listing minus 2-3 months after; the 95% "
                                                                 "interval is above 0"),
)
# Reported, not scored: (technology or None for all, cell, compared cell, sign) in every period
COMPARE = (("solar", "1 month", "first", 1), ("batteries", "1 month", "first", 1), ("wind", "1 month", "first", -1),
           ("gas", "1 month", "first", -1), ("solar", "1 month", "2-3 months", 1), (None, "1 month", "first", 1))
UA = "mv2-munim-clusterboot/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def deadline_ts(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).timestamp()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def wait_plan(deadline, get=None, sleep=time.sleep, clock=time.time, every=600):
    """Poll PLAN_URL until it serves the plan (True) or the deadline has passed (False)."""
    while True:
        try:
            text = (get or globals()["get"])(PLAN_URL).decode("utf-8", "replace")
        except Exception as e:  # recorded, not raised
            text = "%s: %s" % (type(e).__name__, e)
        if PLAN_MARK in text:
            print("%s plan served: %s" % (now(), PLAN_URL), flush=True)
            return True
        if clock() >= deadline:
            print("%s deadline passed; plan not served" % now(), flush=True)
            return False
        print("%s plan not served yet: %s" % (now(), text[:60]), flush=True)
        sleep(every)


def mi(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def cell_of(gap):
    if gap is None:
        return "first"
    for lo, hi, name in GAPS:
        if gap >= lo and (hi is None or gap <= hi):
            return name
    return None


def load(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


def annotate(rows):
    """Cohort rows -> rows with the cell, the plant and whether that month's workbook lists it as operating."""
    last, out = {}, []
    for r in sorted(rows, key=lambda r: (r["month"], r["key"])):
        k = r["key"]
        gap = None if k not in last else mi(r["month"]) - mi(last[k])
        out.append(dict(r, gap=gap, cell=cell_of(gap), plant=k.split("/")[0], ok=r["now"] == "Operating"))
        last[k] = r["month"]
    return out


def pick(a, period, group, name):
    return [r for r in a if period[0] <= r["month"] <= period[1] and (group is None or r["group"] == group)
            and r["cell"] == name]


def count(rows):
    return sum(1 for r in rows if r["ok"]), len(rows)


def clusters(a, period, group, x, y):
    """-> {plant: [on time in x, rows in x, on time in y, rows in y]} for the plants with rows in either cell."""
    by = {}
    for i, name in ((0, x), (2, y)):
        for r in pick(a, period, group, name):
            p = by.setdefault(r["plant"], [0, 0, 0, 0])
            p[i] += 1 if r["ok"] else 0
            p[i + 1] += 1
    return by


def diff(t, sign):
    """[on x, rows x, on y, rows y] -> sign * (share x - share y); 0.0 if either cell has no rows."""
    if not t[1] or not t[3]:
        return 0.0
    return sign * (t[0] / t[1] - t[2] / t[3])


def boot(by, sign, resamples=RESAMPLES, seed=SEED):
    """-> the sorted differences of `resamples` resamples of the plants, each drawn with replacement."""
    vals = [by[k] for k in sorted(by)]
    rng = random.Random(seed)
    n = len(vals)
    out = []
    for _ in range(resamples):
        t = [0, 0, 0, 0]
        for v in rng.choices(vals, k=n):
            t[0] += v[0]
            t[1] += v[1]
            t[2] += v[2]
            t[3] += v[3]
        out.append(diff(t, sign))
    return sorted(out)


def ends(d):
    """Sorted differences -> the 95% interval: positions n*25//1000 and n*975//1000-1 (51st and 1,950th of 2,000)."""
    n = len(d)
    return d[n * 25 // 1000], d[n * 975 // 1000 - 1]


def compare(a, period, group, x, y, sign, resamples=RESAMPLES):
    """-> the point difference, its interval (None if a cell has fewer than MIN_PLANTS plants) and the counts."""
    by = clusters(a, period, group, x, y)
    t = [sum(v[i] for v in by.values()) for i in range(4)]
    px, py = sum(1 for v in by.values() if v[1]), sum(1 for v in by.values() if v[3])
    lo = hi = None
    if px and py:
        lo, hi = ends(boot(by, sign, resamples))
    return {"point": diff(t, sign), "lo": lo, "hi": hi, "cells": t, "plants": (px, py, len(by))}


def score(a, n_rows, md5, known=None, rows_expected=COHORT_ROWS, md5_expected=COHORT_MD5, resamples=RESAMPLES):
    """-> the reproduction check C0 and predictions B1 to B5."""
    known = KNOWN if known is None else known
    got = {k: count(pick(a, k[0], k[1], k[2])) for k in known}
    same = sum(1 for k in known if got[k] == known[k])
    c0 = n_rows == rows_expected and md5 == md5_expected and same == len(known)
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows, md5 %s; %d of %d published cells reproduced" % (n_rows, md5, same, len(known)),
            "bar": "%d rows, md5 %s; %d of %d published cells reproduced" % (rows_expected, md5_expected, len(known),
                                                                              len(known))}]
    for pid, period, g, x, y, sign, expect, bar in BARS:
        r = compare(a, period, g, x, y, sign, resamples) if c0 else None
        if r is None or min(r["plants"][:2]) < MIN_PLANTS:
            o = "not scored"
        elif expect == "above":
            o = "held" if r["lo"] > 0 else "failed"
        else:
            o = "held" if r["lo"] <= 0 <= r["hi"] else "failed"
        out.append({"id": pid, "outcome": o, "value": fmt(r, x, y, sign) if r else "not computed", "bar": bar})
    return out


def label(x, y, sign):
    return "%s minus %s" % ((x, y) if sign > 0 else (y, x))


def fmt(r, x, y, sign):
    t, p = r["cells"], r["plants"]
    inter = "not computed" if r["lo"] is None else "%+.4f to %+.4f" % (r["lo"], r["hi"])
    return "%s: %+.4f, 95%% interval %s; %s: %d of %d at %d plants; %s: %d of %d at %d plants" % (
        label(x, y, sign), r["point"], inter, x, t[0], t[1], p[0], y, t[2], t[3], p[1])


def tables(a, resamples=RESAMPLES):
    """-> one row per period and comparison of COMPARE, reported, not scored."""
    t = []
    for period in PERIODS + (POOL, RECENT):
        for g, x, y, sign in COMPARE:
            r = compare(a, period, g, x, y, sign, resamples)
            t.append(dict(r, period=period, group=g or "all", label=label(x, y, sign)))
    return t


def render(res):
    md = ["# clusterboot %s: the next-month share by months since the last listing, whole plants resampled"
          % __version__, "", "Scores docs/clusterboot-plan.md (C0, B1 to B5). MV2 of Munim, Inc. (made with AI agents).",
          ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows). %d resamples, seed %d." % (
        res["source"], res["bytes"], res["md5"], res["rows"], res["resamples"], SEED),
        "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## Every period, reported, not scored", "",
           "| period | technology | difference | point | 95% interval | plants (cell, compared cell) |",
           "|---|---|---|---|---|---|"]
    for x in res["tables"]:
        inter = "not computed" if x["lo"] is None else "%+.4f to %+.4f" % (x["lo"], x["hi"])
        small = "" if min(x["plants"][:2]) >= MIN_PLANTS else " (under %d plants)" % MIN_PLANTS
        md.append("| %s to %s | %s | %s | %+.4f | %s | %d, %d%s |" % (
            x["period"][0], x["period"][1], x["group"], x["label"], x["point"], inter, x["plants"][0],
            x["plants"][1], small))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-25T23:00", help="UTC, YYYY-MM-DDTHH:MM")
    ap.add_argument("--resamples", type=int, default=RESAMPLES)
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "user_agent": UA, "started_at": now(), "source": args.cohort or COHORT_URL,
           "resamples": args.resamples, "seed": SEED}
    try:
        if args.cohort:
            with open(args.cohort, "rb") as fh:
                data = fh.read()
        else:
            data = get(COHORT_URL)
        rows = load(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "cohort file not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "clusterboot.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    a = annotate(rows)
    res["predictions"] = score(a, len(rows), res["md5"], resamples=args.resamples)
    res["tables"] = tables(a, args.resamples)
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "clusterboot.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "clusterboot.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
