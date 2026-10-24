"""gaptech: EIA-860M's next-month share by months since the last next-month listing, within solar and batteries.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/nextgaptech-plan.md (C0 is a reproduction check; G1 to G4 are predictions). Each row of
data/nexttech_cohort.csv at commit ea63c15 is annotated with nextcount.py's rules and put in one cell:
"first" (no earlier next-month listing since August 2015) or the months since the generator's last
one (1, 2-3, 4-12, more than 12). The thirty-sixth and thirty-seventh results counted these cells for
all technologies together; this splits them by technology group. Needs nextcount.py 0.1.0 in the
same folder. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python gaptech.py --wait-plan --deadline 2026-10-24T18:00 --out-dir /out
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
PLAN_URL = nc.BASE + "docs/nextgaptech-plan.md"
PLAN_MARK = nc.PLAN_MARK
HELD = ("2026-01", "2026-08")
PERIODS = (nc.EARLY, nc.LATE, HELD)
CELLS = ("first",) + tuple(x[2] for x in nc.GAPS)
# docs/nexttech.md (T0) and docs/nextheld.md (C1): (listed as operating, cohort) in generator-months
KNOWN = {nc.EARLY: (1980, 4223), nc.LATE: (2110, 6047), HELD: (366, 1194)}
# docs/nextcount.md: first listings of 2022-2025, (listed as operating, rows)
KNOWN_FIRST = {"solar": (536, 1483), "batteries": (143, 514)}
UA = "mv2-munim-gaptech/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


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


def cell_of(r):
    """An annotated row -> "first" or the label of its months since the last listing."""
    return "first" if r["gap"] is None else nc.label(r["gap"], nc.GAPS)


def cells(a, group, period):
    """Annotated rows -> {cell: (operating, rows)} for one technology group and period."""
    sel = [r for r in a if nc.in_period(r["month"], period) and r["group"] == group]
    return {c: nc.frac([r for r in sel if cell_of(r) == c]) for c in CELLS}


def score(rows, known=None, first=None, n_rows=nc.COHORT_ROWS):
    """-> the reproduction check C0 and predictions G1 to G4."""
    known = KNOWN if known is None else known
    first = KNOWN_FIRST if first is None else first
    a = nc.annotate(rows)
    gm = {p: nc.frac([r for r in rows if nc.in_period(r["month"], p)]) for p in PERIODS}
    sl, bl, s26 = cells(a, "solar", nc.LATE), cells(a, "batteries", nc.LATE), cells(a, "solar", HELD)
    got_first = {"solar": sl["first"], "batteries": bl["first"]}
    c0 = len(rows) == n_rows and gm == known and got_first == first
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows; %s; first listings 2022-2025: solar %s, batteries %s" % (
                len(rows), ", ".join(nc._cell(gm[p]) for p in PERIODS), nc._cell(sl["first"]), nc._cell(bl["first"])),
            "bar": "%d rows; %s; first listings 2022-2025: solar %s, batteries %s" % (
                n_rows, ", ".join(nc._cell(known[p]) for p in PERIODS), nc._cell(first["solar"]),
                nc._cell(first["batteries"]))}]
    s = nc.share
    for pid, c, x, y, bar in (
            ("G1", sl, "1 month", "first", "2022-2025, solar: repeat listings 1 month after the last one are on time "
                                           "more often than first listings"),
            ("G2", sl, "1 month", "2-3 months", "2022-2025, solar: repeat listings 1 month after the last one are on "
                                                "time more often than those 2-3 months after"),
            ("G3", s26, "1 month", "2-3 months", "January-August 2026, solar: repeat listings 1 month after the last "
                                                 "one are on time more often than those 2-3 months after"),
            ("G4", bl, "1 month", "first", "2022-2025, batteries: repeat listings 1 month after the last one are on "
                                           "time more often than first listings")):
        out.append({"id": pid, "outcome": nc.outcome(c0, (c[x], c[y]), lambda c=c, x=x, y=y: s(c[x]) > s(c[y])),
                    "value": "%s: %s; %s: %s" % (x, nc._cell(c[x]), y, nc._cell(c[y])), "bar": bar})
    return out


def tables(a):
    """Annotated rows -> one row per period, group ("all" and each of nextcount.GROUPS) and cell."""
    t = []
    for per in PERIODS:
        for g in ("all",) + nc.GROUPS:
            extra = None if g == "all" else (lambda r, g=g: r["group"] == g)
            for x in nc.table(a, cell_of, CELLS, per, extra=extra):
                t.append(dict(x, group=g))
    return t


def render(res):
    md = ["# gaptech %s: the next-month share by months since the last listing, by technology" % __version__, "",
          "Scores docs/nextgaptech-plan.md (C0, G1 to G4). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows)." % (res["source"], res["bytes"], res["md5"], res["rows"]),
           "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## By technology and months since the last listing (G1 to G4 compare some of these cells)", "",
           "| period | technology | cell | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|---|"]
    nc._rows(md, [x for x in res["tables"] if x["months"]], first="group")
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-24T18:00", help="UTC, YYYY-MM-DDTHH:MM")
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
        with open(os.path.join(args.out_dir, "gaptech.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    res["predictions"] = score(rows)
    res["tables"] = tables(nc.annotate(rows))
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "gaptech.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "gaptech.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
