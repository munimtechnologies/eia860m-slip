"""nexttechonce: the next-month share of EIA-860M by technology, counting each generator once per period.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/nexttechonce-plan.md (C0 is a reproduction check; O1 to O4 are predictions).
docs/nexttech.md counted generator-months: a generator planned for the next month in many months
counted once in each, and one gas plant (60264, 102 generator-months) moved gas's 2016-2019 share.
This reads data/nexttech_cohort.csv (job nexttech-v1) and keeps, for each generator and period, only
its first next-month cohort month in that period. Standard library only.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python nexttechonce.py --wait-plan --deadline 2026-10-26T12:00 --out-dir /out
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
PLAN_URL = BASE + "docs/nexttechonce-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
COHORT_URL = BASE + "data/nexttech_cohort.csv"
COHORT_ROWS = 14807
GROUPS = ("solar", "batteries", "gas", "wind", "other")
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
# docs/nexttech.md, T0: (listed as operating, cohort) in generator-months
KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}
MIN_COHORT = 30   # O1-O3: a group needs at least 30 generators in each period to be scored
GAS_BAND = 0.05   # O3: gas's two shares within 0.05 of each other
UA = "mv2-munim-nexttechonce/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


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


def first_rows(rows, period):
    """Each generator's first cohort row in a period (its earliest cohort month)."""
    seen = {}
    for r in sorted((r for r in rows if in_period(r["month"], period)), key=lambda r: r["month"]):
        seen.setdefault(r["key"], r)
    return list(seen.values())


def frac(rows, group=None):
    """(listed as operating, rows) for one group or all."""
    sel = [r for r in rows if group is None or r["group"] == group]
    return sum(1 for r in sel if r["now"] == "Operating"), len(sel)


def share(op_n):
    op, n = op_n
    return None if n == 0 else op / n


def standardized(early, late):
    """The late shares of each group weighted by the early mix, or None if a group of the early mix has
    no late rows."""
    total = 0.0
    for g in GROUPS:
        ne = frac(early, g)[1]
        if ne == 0:
            continue
        s = share(frac(late, g))
        if s is None:
            return None
        total += ne / len(early) * s
    return total


def top_plant(rows, group):
    """(plant id, rows) of the plant with the most rows in a group, or (None, 0)."""
    c = collections.Counter(r["key"].split("/")[0] for r in rows if r["group"] == group)
    return c.most_common(1)[0] if c else (None, 0)


def score(rows, known=None, n_rows=COHORT_ROWS):
    """-> the reproduction check C0 and predictions O1 to O4."""
    known = KNOWN if known is None else known
    gm = {p: frac([r for r in rows if in_period(r["month"], p)]) for p in (EARLY, LATE)}
    c0 = len(rows) == n_rows and gm == known
    out = [{"id": "C0", "outcome": "held" if c0 else "failed",
            "value": "%d rows; generator-months %d of %d and %d of %d" % (
                len(rows), gm[EARLY][0], gm[EARLY][1], gm[LATE][0], gm[LATE][1]),
            "bar": "%d rows that reproduce %d of %d and %d of %d generator-months" % (
                n_rows, known[EARLY][0], known[EARLY][1], known[LATE][0], known[LATE][1])}]
    e, l = first_rows(rows, EARLY), first_rows(rows, LATE)
    for pid, g in (("O1", "solar"), ("O2", "batteries"), ("O3", "gas")):
        a, b = frac(e, g), frac(l, g)
        if pid == "O3":
            bar = "gas share, each generator once, within %.2f of its 2016-2019 share in 2022-2025 (at least %d in each)" % (
                GAS_BAND, MIN_COHORT)
        else:
            bar = "%s share, each generator once, lower in 2022-2025 than in 2016-2019 (at least %d in each)" % (
                g, MIN_COHORT)
        value = "%d of %d to %d of %d" % (a + b)
        if not c0:
            out.append({"id": pid, "outcome": "not scored", "value": "C0 failed; " + value, "bar": bar})
        elif min(a[1], b[1]) < MIN_COHORT:
            out.append({"id": pid, "outcome": "not scored", "value": "too few; " + value, "bar": bar})
        else:
            sa, sb = share(a), share(b)
            ok = abs(sb - sa) < GAS_BAND if pid == "O3" else sb < sa
            out.append({"id": pid, "outcome": "held" if ok else "failed",
                        "value": "%.4f to %.4f (%s)" % (sa, sb, value), "bar": bar})
    bar = ("all-technology share, each generator once, falls, and the within-technology fall is at least half "
           "the total fall")
    s_e, s_l, s_std = share(frac(e)), share(frac(l)), standardized(e, l) if e else None
    if not c0 or s_std is None or s_e is None or s_l is None:
        out.append({"id": "O4", "outcome": "not scored",
                    "value": "C0 failed" if not c0 else "a group has no 2022-2025 generators", "bar": bar})
    else:
        within, total = s_e - s_std, s_e - s_l
        out.append({"id": "O4", "outcome": "held" if total > 0 and within >= total / 2 else "failed",
                    "value": "within %.4f of total %.4f (shares %.4f to %.4f; standardized %.4f)" % (
                        within, total, s_e, s_l, s_std), "bar": bar})
    return out


def tables(rows):
    """-> (period rows, top plants, first rows) for the report."""
    periods, tops, firsts = [], [], []
    for per in (EARLY, LATE):
        name = "%s to %s" % per
        gm_rows = [r for r in rows if in_period(r["month"], per)]
        first = first_rows(rows, per)
        for grp in GROUPS + (None,):
            o, m = frac(first, grp), frac(gm_rows, grp)
            periods.append({"period": name, "group": grp or "all", "generators": o[1], "operating": o[0],
                            "share": share(o), "months": m[1], "months_operating": m[0], "months_share": share(m)})
        for grp in GROUPS:
            plant, k = top_plant(gm_rows, grp)
            rest = [r for r in gm_rows if r["group"] == grp and r["key"].split("/")[0] != plant]
            tops.append({"period": name, "group": grp, "plant": plant, "months": k,
                         "share_without": share(frac(rest))})
        firsts += [{"period": name, "month": r["month"], "key": r["key"], "group": r["group"], "now": r["now"]}
                   for r in first]
    return periods, tops, firsts


def _f(v):
    return "-" if v is None else "%.4f" % v


def render(res):
    md = ["# nexttechonce %s: the next-month share by technology, each generator once per period" % __version__,
          "", "Scores docs/nexttechonce-plan.md (C0, O1 to O4). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    md += ["Cohort file: %s (%d bytes, md5 %s; %d rows)." % (res["source"], res["bytes"], res["md5"], res["rows"]),
           "", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "C0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (C0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## By period and technology", "",
           "| period | technology | generators | on time | share | generator-months | on time | share |",
           "|---|---|---|---|---|---|---|---|"]
    for p in res["periods"]:
        md.append("| %s | %s | %d | %d | %s | %d | %d | %s |" % (
            p["period"], p["group"], p["generators"], p["operating"], _f(p["share"]), p["months"],
            p["months_operating"], _f(p["months_share"])))
    md += ["", "## The plant with the most generator-months in each group (reported, not scored)", "",
           "| period | technology | plant | generator-months | share without it |", "|---|---|---|---|---|"]
    for t in res["top_plants"]:
        md.append("| %s | %s | %s | %d | %s |" % (t["period"], t["group"], t["plant"] or "-", t["months"],
                                                 _f(t["share_without"])))
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
        with open(os.path.join(args.out_dir, "nexttechonce.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res.update({"bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(rows)})
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), res["md5"], len(rows)), flush=True)
    res["predictions"] = score(rows)
    res["periods"], res["top_plants"], firsts = tables(rows)
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "nexttechonce.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "nexttechonce_first.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["period", "month", "key", "group", "now"])
        w.writeheader()
        w.writerows(firsts)
    md = render(res)
    with open(os.path.join(args.out_dir, "nexttechonce.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
