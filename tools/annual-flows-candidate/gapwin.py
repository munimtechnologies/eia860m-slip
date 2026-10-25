"""gapwin: EIA-860M's next-month share by months since the last listing, by technology, in 2020-2021.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/gapwin-plan.md (C0 is a reproduction check; W1 to W5 are predictions) on the next-month
groups of January 2020 to December 2021, which no earlier result split by first listing or months
since the last listing. The cells are gaptech.py 0.1.0's ("first", or the months since the generator's
last next-month listing: 1, 2-3, 4-12, more than 12), counted with nextcount.py 0.1.0's rules. Both are
used unchanged and must be in the same folder. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python gapwin.py --wait-plan --deadline 2026-10-25T18:00 --out-dir /out
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

import gaptech as gt
import nextcount as nc

__version__ = "0.1.0"
PLAN_URL = nc.BASE + "docs/gapwin-plan.md"
PLAN_MARK = nc.PLAN_MARK
WIN = ("2020-01", "2021-12")
# docs/nexttech.md, its table by year: (listed as operating, rows) of 2020 and 2021 added together
KNOWN = {"solar": (686, 1600), "batteries": (103, 344), "gas": (150, 375), "wind": (143, 373)}
# (id, technology, cell, compared cell, "above" or "below", bar)
BARS = (
    ("W1", "solar", "1 month", "first", "above", "2020-2021, solar: repeat listings 1 month after the last one are "
                                                 "on time more often than first listings"),
    ("W2", "solar", "1 month", "2-3 months", "above", "2020-2021, solar: repeat listings 1 month after the last one "
                                                      "are on time more often than those 2-3 months after"),
    ("W3", "batteries", "1 month", "first", "above", "2020-2021, batteries: repeat listings 1 month after the last "
                                                     "one are on time more often than first listings"),
    ("W4", "gas", "1 month", "first", "below", "2020-2021, gas: repeat listings 1 month after the last one are on "
                                               "time less often than first listings"),
    ("W5", "wind", "1 month", "first", "below", "2020-2021, wind: repeat listings 1 month after the last one are on "
                                                "time less often than first listings"),
)
UA = "mv2-munim-gapwin/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


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
            print("%s plan served: %s" % (nc.now(), PLAN_URL), flush=True)
            return True
        if clock() >= deadline:
            print("%s deadline passed; plan not served" % nc.now(), flush=True)
            return False
        print("%s plan not served yet: %s" % (nc.now(), text[:60]), flush=True)
        sleep(every)


def score(rows, known=None, n_rows=nc.COHORT_ROWS):
    """-> the reproduction check C0 and predictions W1 to W5."""
    known = KNOWN if known is None else known
    tot = {g: nc.frac([r for r in rows if nc.in_period(r["month"], WIN) and r["group"] == g]) for g in known}
    c0 = len(rows) == n_rows and tot == known
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows; 2020-2021: %s" % (len(rows), ", ".join("%s %s" % (g, nc._cell(tot[g])) for g in known)),
            "bar": "%d rows; 2020-2021: %s" % (n_rows, ", ".join("%s %s" % (g, nc._cell(known[g])) for g in known))}]
    a = nc.annotate(rows)
    s = nc.share
    for pid, g, x, y, way, bar in BARS:
        c = gt.cells(a, g, WIN)
        if way == "above":
            ok = lambda c=c, x=x, y=y: s(c[x]) > s(c[y])
        else:
            ok = lambda c=c, x=x, y=y: s(c[x]) < s(c[y])
        out.append({"id": pid, "outcome": nc.outcome(c0, (c[x], c[y]), ok),
                    "value": "%s: %s; %s: %s" % (x, nc._cell(c[x]), y, nc._cell(c[y])), "bar": bar})
    return out


def tables(a):
    """Annotated rows -> one row per group ("all" and each of nextcount.GROUPS) and cell, 2020-2021."""
    t = []
    for g in ("all",) + nc.GROUPS:
        extra = None if g == "all" else (lambda r, g=g: r["group"] == g)
        for x in nc.table(a, gt.cell_of, gt.CELLS, WIN, extra=extra):
            t.append(dict(x, group=g))
    return t


def render(res):
    md = ["# gapwin %s: the next-month share by months since the last listing, by technology, 2020-2021" % __version__,
          "", "Scores docs/gapwin-plan.md (C0, W1 to W5). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows)." % (res["source"], res["bytes"], res["md5"], res["rows"]),
           "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## By technology and months since the last listing (W1 to W5 compare some of these cells)", "",
           "| period | technology | cell | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|---|"]
    nc._rows(md, [x for x in res["tables"] if x["months"]], first="group")
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-25T18:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(nc.deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "gaptech": gt.__version__, "nextcount": nc.__version__, "user_agent": UA,
           "started_at": nc.now(), "source": args.cohort or nc.COHORT_URL}
    try:
        if args.cohort:
            with open(args.cohort, "rb") as fh:
                data = fh.read()
        else:
            data = get(nc.COHORT_URL)
        rows = nc.load(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "cohort file not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "gapwin.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    res["predictions"] = score(rows)
    res["tables"] = tables(nc.annotate(rows))
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "gapwin.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "gapwin.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
