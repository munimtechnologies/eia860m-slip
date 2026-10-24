"""nextcount: EIA-860M's next-month share by how often a generator was planned for the next month before.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/nextcount-plan.md (C0 is a reproduction check; K1 to K3 are predictions).
A generator in a month's next-month cohort (listed the month before as planned to start in that
month) is counted with its number of earlier cohort months, from August 2015: 0, 1, 2, or 3 or more.
It is on time if that month's workbook lists it as operating. This reads data/nexttech_cohort.csv
(job nexttech-v1) at commit ea63c15. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python nextcount.py --wait-plan --deadline 2026-10-26T12:00 --out-dir /out
"""

import argparse
import calendar
import collections
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

__version__ = "0.1.0"
BASE = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/"
PLAN_URL = BASE + "docs/nextcount-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
COHORT_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/"
              "ea63c150a8ed41cc1fcad901ccab51686c924d46/data/nexttech_cohort.csv")
COHORT_ROWS = 14807
GROUPS = ("solar", "batteries", "gas", "wind", "other")
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
# docs/nexttech.md, T0: (listed as operating, cohort) in generator-months
KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}
BINS = ("0", "1", "2", "3+")
FINE = ((0, 0, "0"), (1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 4, "4"), (5, 9, "5-9"), (10, None, "10+"))
GAPS = ((1, 1, "1 month"), (2, 3, "2-3 months"), (4, 12, "4-12 months"), (13, None, "more than 12 months"))
MIN_COHORT = 30   # K1-K3: every cell a prediction compares needs at least 30 generator-months
GAS_PLANT = "60264"   # docs/nexttech.md: 102 of the 743 gas generator-months of 2016-2019
UA = "mv2-munim-nextcount/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def deadline_ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M"))


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


def load(data):
    """The cohort file's bytes -> a list of row dicts (month, key, technology, group, now, ...)."""
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"), newline="")))


def in_period(month, period):
    return period[0] <= month <= period[1]


def m_index(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def annotate(rows):
    """Cohort rows -> the same rows in month order, each with prior (its generator's earlier cohort
    months) and gap (months since its generator's last earlier cohort month; None for the first)."""
    last, count, out = {}, collections.Counter(), []
    for r in sorted(rows, key=lambda r: (r["month"], r["key"])):
        k = r["key"]
        out.append(dict(r, prior=count[k], gap=None if k not in last else m_index(r["month"]) - m_index(last[k])))
        count[k] += 1
        last[k] = r["month"]
    return out


def bin_of(prior):
    return "3+" if prior >= 3 else str(prior)


def label(value, bins):
    """A number -> the label of the (low, high, label) bin holding it; high None is open."""
    for lo, hi, name in bins:
        if value >= lo and (hi is None or value <= hi):
            return name
    return None


def frac(rows):
    """(listed as operating, rows)."""
    return sum(1 for r in rows if r["now"] == "Operating"), len(rows)


def share(op_n):
    op, n = op_n
    return None if n == 0 else op / n


def by_bin(rows, period):
    """Annotated rows -> {bin: (operating, generator-months)} for one period."""
    sel = [r for r in rows if in_period(r["month"], period)]
    return {b: frac([r for r in sel if bin_of(r["prior"]) == b]) for b in BINS}


def outcome(c0, cells, ok):
    if not c0:
        return "not scored"
    if min(c[1] for c in cells) < MIN_COHORT:
        return "not scored"
    return "held" if ok() else "failed"


def _cell(c):
    return "%d of %d" % c


def score(rows, known=None, n_rows=COHORT_ROWS):
    """-> the reproduction check C0 and predictions K1 to K3."""
    known = KNOWN if known is None else known
    gm = {p: frac([r for r in rows if in_period(r["month"], p)]) for p in (EARLY, LATE)}
    c0 = len(rows) == n_rows and gm == known
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows; generator-months %d of %d and %d of %d" % (
                len(rows), gm[EARLY][0], gm[EARLY][1], gm[LATE][0], gm[LATE][1]),
            "bar": "%d rows that reproduce %d of %d and %d of %d generator-months" % (
                n_rows, known[EARLY][0], known[EARLY][1], known[LATE][0], known[LATE][1])}]
    a = annotate(rows)
    e, l = by_bin(a, EARLY), by_bin(a, LATE)
    s = {p: {b: share(c[b]) for b in BINS} for p, c in ((EARLY, e), (LATE, l))}
    out.append({"id": "K1", "outcome": outcome(c0, (l["0"], l["3+"]), lambda: s[LATE]["0"] > s[LATE]["3+"]),
                "value": "0: %s; 3+: %s" % (_cell(l["0"]), _cell(l["3+"])),
                "bar": "2022-2025: the share with no earlier next-month listing is above the share with 3 or more"})
    out.append({"id": "K2", "outcome": outcome(c0, [l[b] for b in BINS], lambda: all(
                    s[LATE][BINS[i]] >= s[LATE][BINS[i + 1]] for i in range(len(BINS) - 1))),
                "value": "; ".join("%s: %s" % (b, _cell(l[b])) for b in BINS),
                "bar": "2022-2025: the share does not rise from 0 to 1 to 2 to 3 or more earlier listings"})
    out.append({"id": "K3", "outcome": outcome(c0, (e["0"], e["3+"], l["0"], l["3+"]), lambda: (
                    s[EARLY]["0"] - s[EARLY]["3+"]) < (s[LATE]["0"] - s[LATE]["3+"])),
                "value": "2016-2019 0: %s, 3+: %s; 2022-2025 0: %s, 3+: %s" % (
                    _cell(e["0"]), _cell(e["3+"]), _cell(l["0"]), _cell(l["3+"])),
                "bar": "the share with no earlier listing minus the share with 3 or more is smaller in 2016-2019 "
                       "than in 2022-2025"})
    return out


def table(rows, key, names, period, extra=None):
    """Annotated rows of a period -> one row per name of key(r): generator-months, on time, share,
    generators and plants."""
    sel = [r for r in rows if in_period(r["month"], period) and (extra is None or extra(r))]
    out = []
    for name in names:
        g = [r for r in sel if key(r) == name]
        op, n = frac(g)
        out.append({"period": "%s to %s" % period, "cell": name, "months": n, "operating": op,
                    "share": share((op, n)), "generators": len(set(r["key"] for r in g)),
                    "plants": len(set(r["key"].split("/")[0] for r in g))})
    return out


def tables(a):
    """Annotated rows -> the report's tables (reported, not scored)."""
    fine = [x[2] for x in FINE]
    gaps = [x[2] for x in GAPS]
    t = {"bins": [], "fine": [], "gaps": [], "tech": [], "without_gas_plant": []}
    for per in (EARLY, LATE):
        t["bins"] += table(a, lambda r: bin_of(r["prior"]), BINS, per)
        t["fine"] += table(a, lambda r: label(r["prior"], FINE), fine, per)
        t["gaps"] += table(a, lambda r: label(r["gap"], GAPS), gaps, per, extra=lambda r: r["gap"] is not None)
        t["without_gas_plant"] += table(a, lambda r: bin_of(r["prior"]), BINS, per,
                                        extra=lambda r: r["key"].split("/")[0] != GAS_PLANT)
        for g in GROUPS:
            for x in table(a, lambda r: bin_of(r["prior"]), BINS, per, extra=lambda r, g=g: r["group"] == g):
                t["tech"].append(dict(x, group=g))
    return t


def _f(v):
    return "-" if v is None else "%.4f" % v


def _rows(md, rows, first=None):
    for x in rows:
        md.append("| %s%s | %s | %d | %d | %s | %d | %d |" % (
            x["period"], "" if first is None else " | " + x[first], x["cell"], x["months"], x["operating"],
            _f(x["share"]), x["generators"], x["plants"]))


def render(res):
    md = ["# nextcount %s: the next-month share by earlier next-month listings" % __version__, "",
          "Scores docs/nextcount-plan.md (C0, K1 to K3). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows; repeated generator and month rows: %d)." % (
        res["source"], res["bytes"], res["md5"], res["rows"], res["duplicates"]),
        "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    head = ["| period | earlier listings | generator-months | on time | share | generators | plants |",
            "|---|---|---|---|---|---|---|"]
    t = res["tables"]
    md += ["", "## By earlier next-month listings", ""] + head
    _rows(md, t["bins"])
    md += ["", "## Finer (reported, not scored)", ""] + head
    _rows(md, t["fine"])
    md += ["", "## Repeat listings by months since the last one (reported, not scored)", "",
           "| period | months since | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|"]
    _rows(md, t["gaps"])
    md += ["", "## Without plant %s (reported, not scored)" % GAS_PLANT, ""] + head
    _rows(md, t["without_gas_plant"])
    md += ["", "## By technology (reported, not scored)", "",
           "| period | technology | earlier listings | generator-months | on time | share | generators | plants |",
           "|---|---|---|---|---|---|---|---|"]
    _rows(md, [x for x in t["tech"] if x["months"]], first="group")
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-26T12:00", help="UTC, YYYY-MM-DDTHH:MM")
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
        with open(os.path.join(args.out_dir, "nextcount.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    pairs = collections.Counter((r["month"], r["key"]) for r in rows)
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows),
                "duplicates": sum(n - 1 for n in pairs.values() if n > 1)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    res["predictions"] = score(rows)
    a = annotate(rows)
    res["tables"] = tables(a)
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "nextcount.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "nextcount_rows.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["month", "key", "group", "now", "prior", "gap"], extrasaction="ignore")
        w.writeheader()
        w.writerows(dict(r, gap="" if r["gap"] is None else r["gap"]) for r in a)
    md = render(res)
    with open(os.path.join(args.out_dir, "nextcount.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
