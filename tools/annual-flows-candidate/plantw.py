"""plantw: EIA-860M's next-month share by months since the last listing, with each plant weighted once.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/plantw-plan.md (C0 is a reproduction check; P1 to P5 are predictions). Earlier results
counted generator-months, so a plant with many generators, or a generator planned for the next month
again and again, weighs more than a plant with one. Here each plant's share of on-time rows within a
cell is computed first, and the cell's share is the mean over its plants. The cells are gaptech.py
0.1.0's ("first", or the months since the generator's last next-month listing: 1, 2-3, 4-12, more
than 12), with each generator's history counted from August 2015. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python plantw.py --wait-plan --deadline 2026-10-25T20:00 --out-dir /out
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

__version__ = "0.1.0"
BASE = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/"
PLAN_URL = BASE + "main/docs/plantw-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
COHORT_URL = BASE + "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv"
COHORT_ROWS = 14807
COHORT_MD5 = "1681df9fdee9878ca2c359d1239c6467"
POOL = ("2016-01", "2025-12")
RECENT = ("2022-01", "2026-08")
PERIODS = (("2016-01", "2019-12"), ("2020-01", "2021-12"), ("2022-01", "2025-12"), ("2026-01", "2026-08"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
CELLS = ("first",) + tuple(x[2] for x in GAPS)
GROUPS = ("solar", "batteries", "gas", "wind", "other")
MIN_PLANTS = 30
# docs/nextgaptech.md and docs/gapwin.md: generator-months (on time, rows) of 2016-2019, 2020-2021 and 2022-2025 added
KNOWN = {("solar", "first"): (1474, 3568), ("solar", "1 month"): (1230, 2657)}
# (id, period, technology, cell, compared cell, "above" or "below", bar)
BARS = (
    ("P1", POOL, "solar", "1 month", "first", "above", "2016-2025, solar, each plant weighted once: repeat listings "
                                                       "1 month after the last one are on time more often than first "
                                                       "listings"),
    ("P2", POOL, "batteries", "1 month", "first", "above", "2016-2025, batteries, each plant weighted once: repeat "
                                                           "listings 1 month after the last one are on time more often "
                                                           "than first listings"),
    ("P3", POOL, "wind", "1 month", "first", "below", "2016-2025, wind, each plant weighted once: repeat listings 1 "
                                                      "month after the last one are on time less often than first "
                                                      "listings"),
    ("P4", POOL, "gas", "1 month", "first", "below", "2016-2025, gas, each plant weighted once: repeat listings 1 "
                                                     "month after the last one are on time less often than first "
                                                     "listings"),
    ("P5", RECENT, "solar", "1 month", "2-3 months", "above", "January 2022 to August 2026, solar, each plant weighted "
                                                              "once: repeat listings 1 month after the last one are on "
                                                              "time more often than those 2-3 months after"),
)
UA = "mv2-munim-plantw/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


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


def cell(rows):
    """-> generator-months on time and in all, the number of plants and the mean of the plants' shares."""
    by = {}
    for r in rows:
        p = by.setdefault(r["plant"], [0, 0])
        p[0] += 1 if r["ok"] else 0
        p[1] += 1
    pw = sum(v[0] / v[1] for v in by.values()) / len(by) if by else None
    return {"on": sum(v[0] for v in by.values()), "rows": sum(v[1] for v in by.values()), "plants": len(by), "pw": pw}


def fmt(c):
    if not c["plants"]:
        return "no rows"
    return "%.4f over %d plants (generator-months %d of %d)" % (c["pw"], c["plants"], c["on"], c["rows"])


def score(a, n_rows, md5, known=None, rows_expected=COHORT_ROWS, md5_expected=COHORT_MD5):
    """-> the reproduction check C0 and predictions P1 to P5."""
    known = KNOWN if known is None else known
    got = {}
    for k in known:
        c = cell(pick(a, POOL, k[0], k[1]))
        got[k] = (c["on"], c["rows"])
    c0 = n_rows == rows_expected and md5 == md5_expected and got == known
    show = lambda d: "; ".join("%s %s %d of %d" % (k[0], k[1], v[0], v[1]) for k, v in d.items())
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows, md5 %s; 2016-2025: %s" % (n_rows, md5, show(got)),
            "bar": "%d rows, md5 %s; 2016-2025: %s" % (rows_expected, md5_expected, show(known))}]
    for pid, period, g, x, y, way, bar in BARS:
        cx, cy = cell(pick(a, period, g, x)), cell(pick(a, period, g, y))
        if not c0 or min(cx["plants"], cy["plants"]) < MIN_PLANTS:
            o = "not scored"
        elif way == "above":
            o = "held" if cx["pw"] > cy["pw"] else "failed"
        else:
            o = "held" if cx["pw"] < cy["pw"] else "failed"
        out.append({"id": pid, "outcome": o, "value": "%s: %s; %s: %s" % (x, fmt(cx), y, fmt(cy)), "bar": bar})
    return out


def tables(a):
    """Annotated rows -> one row per period, group ("all" and each of GROUPS) and cell that has rows."""
    t = []
    for period in PERIODS + (POOL, RECENT):
        for g in (None,) + GROUPS:
            for name in CELLS:
                c = cell(pick(a, period, g, name))
                if c["plants"]:
                    t.append(dict(c, period=period, group=g or "all", cell=name))
    return t


def render(res):
    md = ["# plantw %s: the next-month share by months since the last listing, each plant weighted once" % __version__,
          "", "Scores docs/plantw-plan.md (C0, P1 to P5). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows)." % (res["source"], res["bytes"], res["md5"], res["rows"]),
           "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## Each plant weighted once, and generator-months, by period, technology and cell", "",
           "| period | technology | cell | generator-months | on time | share | plants | plant-weighted share |",
           "|---|---|---|---|---|---|---|---|"]
    for x in res["tables"]:
        md.append("| %s to %s | %s | %s | %d | %d | %.4f | %d | %.4f |" % (
            x["period"][0], x["period"][1], x["group"], x["cell"], x["rows"], x["on"], x["on"] / x["rows"],
            x["plants"], x["pw"]))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-25T20:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "user_agent": UA, "started_at": now(), "source": args.cohort or COHORT_URL}
    try:
        if args.cohort:
            with open(args.cohort, "rb") as fh:
                data = fh.read()
        else:
            data = get(COHORT_URL)
        rows = load(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "cohort file not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "plantw.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    a = annotate(rows)
    res["predictions"] = score(a, len(rows), res["md5"])
    res["tables"] = tables(a)
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "plantw.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "plantw.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
