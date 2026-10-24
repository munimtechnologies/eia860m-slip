"""nextheld: the thirty-sixth result's pattern, checked on EIA-860M's next-month groups of January to August 2026.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/nextheld-plan.md (C1 is a reproduction check; H1 to H3 are predictions). It counts the
cohort months January to August 2026 of data/nexttech_cohort.csv at commit ea63c15 with nextcount.py's
rules: a row's earlier next-month listings from August 2015 (0, 1, 2, 3 or more) and, for a repeat
listing, the months since the generator's last one. docs/nextcount.md (the thirty-sixth result) counted
2016-2019 and 2022-2025 only. Needs nextcount.py 0.1.0 in the same folder. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python nextheld.py --wait-plan --deadline 2026-10-25T14:00 --out-dir /out
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

import nextcount as nc

__version__ = "0.1.0"
PLAN_URL = nc.BASE + "docs/nextheld-plan.md"
PLAN_MARK = nc.PLAN_MARK
HELD = ("2026-01", "2026-08")
# data/monthcheck_months_2026-09.csv: (cohort_operating, cohort) of each month
KNOWN_MONTHS = {"2026-01": (46, 136), "2026-02": (20, 114), "2026-03": (38, 156), "2026-04": (71, 168),
                "2026-05": (35, 140), "2026-06": (70, 216), "2026-07": (47, 140), "2026-08": (39, 124)}
UA = "mv2-munim-nextheld/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


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


def months_of(rows, period=HELD):
    """Cohort rows -> {month: (listed as operating, rows)} for the months of a period."""
    out = {}
    for r in rows:
        if nc.in_period(r["month"], period):
            op, n = out.get(r["month"], (0, 0))
            out[r["month"]] = (op + (r["now"] == "Operating"), n + 1)
    return out


def gap_cell(a, name, period=HELD):
    """Annotated rows -> (operating, rows) of a period's repeat listings whose months since the last
    listing fall in the nextcount.GAPS bin with this label."""
    return nc.frac([r for r in a if nc.in_period(r["month"], period) and r["gap"] is not None
                    and nc.label(r["gap"], nc.GAPS) == name])


def _total(months):
    return sum(v[0] for v in months.values()), sum(v[1] for v in months.values()), len(months)


def score(rows, known=None):
    """-> the reproduction check C1 and predictions H1 to H3."""
    known = KNOWN_MONTHS if known is None else known
    got = months_of(rows)
    c1 = got == known
    out = [{"id": "C1", "outcome": "held" if c1 else "failed",
            "value": "%d of %d generator-months in %d months" % _total(got),
            "bar": "each month's rows and operating rows as in data/monthcheck_months_2026-09.csv: "
                   "%d of %d in %d months" % _total(known)}]
    a = nc.annotate(rows)
    b = nc.by_bin(a, HELD)
    one, two = gap_cell(a, "1 month"), gap_cell(a, "2-3 months")
    s = nc.share
    out.append({"id": "H1", "outcome": nc.outcome(c1, (b["0"], b["3+"]), lambda: s(b["3+"]) < s(b["0"])),
                "value": "0: %s; 3+: %s" % (nc._cell(b["0"]), nc._cell(b["3+"])),
                "bar": "the share with 3 or more earlier next-month listings is below the share with none"})
    out.append({"id": "H2", "outcome": nc.outcome(c1, (one, two), lambda: s(one) > s(two)),
                "value": "1 month: %s; 2-3 months: %s" % (nc._cell(one), nc._cell(two)),
                "bar": "repeat listings 1 month after the last one are on time more often than those 2-3 months after"})
    out.append({"id": "H3", "outcome": nc.outcome(c1, (one, b["0"]), lambda: s(one) > s(b["0"])),
                "value": "1 month: %s; 0: %s" % (nc._cell(one), nc._cell(b["0"])),
                "bar": "repeat listings 1 month after the last one are on time more often than first listings"})
    return out


def tables(a):
    """Annotated rows -> the report's tables for January to August 2026 (reported, not scored)."""
    t = {"bins": nc.table(a, lambda r: nc.bin_of(r["prior"]), nc.BINS, HELD),
         "fine": nc.table(a, lambda r: nc.label(r["prior"], nc.FINE), [x[2] for x in nc.FINE], HELD),
         "gaps": nc.table(a, lambda r: nc.label(r["gap"], nc.GAPS), [x[2] for x in nc.GAPS], HELD,
                          extra=lambda r: r["gap"] is not None),
         "tech": []}
    for g in nc.GROUPS:
        for x in nc.table(a, lambda r: nc.bin_of(r["prior"]), nc.BINS, HELD, extra=lambda r, g=g: r["group"] == g):
            t["tech"].append(dict(x, group=g))
    return t


def render(res):
    md = ["# nextheld %s: the next-month share by earlier listings, January to August 2026" % __version__, "",
          "Scores docs/nextheld-plan.md (C1, H1 to H3). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows)." % (res["source"], res["bytes"], res["md5"], res["rows"]),
           "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C1" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C1 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## Months", "", "| month | on time | generator-months |", "|---|---|---|"]
    md += ["| %s | %d | %d |" % (m, c[0], c[1]) for m, c in sorted(res["months"].items())]
    head = ["| period | earlier listings | generator-months | on time | share | generators | plants |",
            "|---|---|---|---|---|---|---|"]
    t = res["tables"]
    md += ["", "## By earlier next-month listings", ""] + head
    nc._rows(md, t["bins"])
    md += ["", "## Finer (reported, not scored)", ""] + head
    nc._rows(md, t["fine"])
    md += ["", "## Repeat listings by months since the last one", "",
           "| period | months since | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|"]
    nc._rows(md, t["gaps"])
    md += ["", "## By technology (reported, not scored)", "",
           "| period | technology | earlier listings | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|---|"]
    nc._rows(md, [x for x in t["tech"] if x["months"]], first="group")
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-25T14:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(nc.deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "nextcount": nc.__version__, "user_agent": UA, "started_at": nc.now(),
           "source": args.cohort or nc.COHORT_URL}
    try:
        if args.cohort:
            with open(args.cohort, "rb") as fh:
                data = fh.read()
        else:
            data = get(nc.COHORT_URL)
        rows = nc.load(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "cohort file not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "nextheld.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    res["predictions"] = score(rows)
    res["months"] = months_of(rows)
    res["tables"] = tables(nc.annotate(rows))
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "nextheld.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "nextheld.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
