"""nexttech: the next-month share of EIA-860M split by technology, and how much of its fall is within technologies.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/nexttech-plan.md (T0 is a reproduction check; T1 to T4 are predictions). docs/nextmonth-share.md
found that of the generators EIA-860M listed as planned for the next month, the share listed as operating
in it fell from 0.469 (1,980 of 4,223) in 2016-2019 to 0.349 (2,110 of 6,047) in 2022-2025, by count. It
did not split by technology. This replays the rebuilt changelog (data/eia860m_changelog_from_workbooks.csv.gz
0.1.1, pinned to commit a3ce085) with monthcheck.replay 0.1.0 unchanged, keeping every month's next-month
cohort, and takes each cohort generator's technology from the workbook of the month before (the month that
listed it as planned for this one), read from PUDL's archive by retiredentry.read_month 0.1.0 and
retiredgap.keyset.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing until
the plan is served, so the plan's commit time is before any number below exists.

    python nexttech.py --wait-plan --deadline 2026-10-25T12:00 --data-dir /data --out-dir /out
"""

import argparse
import collections
import csv
import hashlib
import json
import os
import sys
import time

import monthcheck as mc
import retiredentry as ren
import retiredgap as rg
import retiredscope as rs

__version__ = "0.1.0"
PLAN_URL = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/nexttech-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
GROUPS = ("solar", "batteries", "gas", "wind", "other")
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
# docs/nextmonth-share.md (job monthcheck-dry-v1): (listed as operating, cohort) by count
KNOWN = {EARLY: (1980, 4223), LATE: (2110, 6047)}
MISSING_MAX = 0.01  # T0: at most 1% of each period's cohort without a technology
MIN_COHORT = 30     # T1-T3: a technology needs at least 30 in each period to be scored
UA = "mv2-munim-nexttech/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def wait_plan(deadline, get=None, sleep=time.sleep, clock=time.time, every=600):
    """Poll PLAN_URL until it serves the plan (True) or the deadline has passed (False)."""
    while True:
        try:
            text = (get or ren._get)(PLAN_URL).decode("utf-8", "replace")
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


def tech_group(tech):
    """An EIA-860M technology name -> solar, batteries, gas, wind or other (other when missing)."""
    t = str(tech or "").strip().lower()
    if t == "solar photovoltaic":
        return "solar"
    if t == "batteries":
        return "batteries"
    if t.startswith("natural gas") or t == "other natural gas":
        return "gas"
    if "wind" in t:
        return "wind"
    return "other"


class _Every(object):
    """Equal to every month, so monthcheck.replay keeps the cohort detail of every month."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = None


def cohorts(rows):
    """Changelog rows -> {month: [(key, where now, nameplate MW in the month before), ...]} for every
    month with a next-month cohort, from monthcheck.replay unchanged."""
    out = {}
    for x in mc.replay(rows, detail_for=_Every()):
        if x["cohort"]:
            out[x["month"]] = [(d["key"], d["now"], mc.mw(d["nameplate_mw"])) for d in x["detail"]]
    return out


def in_period(month, period):
    return period[0] <= month <= period[1]


def tally(rows):
    """[(month, group, now, mw), ...] -> {(year, group): [cohort, operating, mw, mw operating]}."""
    t = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    for month, group, where, mw in rows:
        c = t[(month[:4], group)]
        c[0] += 1
        c[2] += mw
        if where == "Operating":
            c[1] += 1
            c[3] += mw
    return dict(t)


def period_sum(rows, period, group=None):
    """(operating, cohort) for one period, one group or all."""
    sel = [r for r in rows if in_period(r[0], period) and (group is None or r[1] == group)]
    return sum(1 for r in sel if r[2] == "Operating"), len(sel)


def share(op_n):
    op, n = op_n
    return None if n == 0 else op / n


def standardized(rows):
    """The late period's technology shares weighted by the early period's technology mix, or None if a
    technology of the early mix has no late cohort."""
    _, n_early = period_sum(rows, EARLY)
    total = 0.0
    for g in GROUPS:
        _, ne = period_sum(rows, EARLY, g)
        if ne == 0:
            continue
        s = share(period_sum(rows, LATE, g))
        if s is None:
            return None
        total += ne / n_early * s
    return total


def score(rows, missing):
    """rows: [(month, group, now, mw)]; missing: {period: cohort generators without a technology}.
    -> the reproduction check T0 and predictions T1 to T4."""
    got = {p: period_sum(rows, p) for p in (EARLY, LATE)}
    miss_ok = all(missing.get(p, 0) <= MISSING_MAX * got[p][1] for p in (EARLY, LATE))
    t0 = got == KNOWN and miss_ok
    out = [{"id": "T0", "outcome": "held" if t0 else "failed",
            "value": "2016-2019 %d of %d; 2022-2025 %d of %d; without a technology %d and %d" % (
                got[EARLY][0], got[EARLY][1], got[LATE][0], got[LATE][1], missing.get(EARLY, 0),
                missing.get(LATE, 0)),
            "bar": "reproduces 1980 of 4223 and 2110 of 6047, with at most 1% of each period's cohort "
                   "without a technology"}]
    for pid, g in (("T1", "solar"), ("T2", "gas"), ("T3", "batteries")):
        e, l = period_sum(rows, EARLY, g), period_sum(rows, LATE, g)
        bar = "%s share lower in 2022-2025 than in 2016-2019 (at least %d in each)" % (g, MIN_COHORT)
        value = "%d of %d to %d of %d" % (e[0], e[1], l[0], l[1])
        if not t0:
            out.append({"id": pid, "outcome": "not scored", "value": "T0 failed; " + value, "bar": bar})
        elif min(e[1], l[1]) < MIN_COHORT:
            out.append({"id": pid, "outcome": "not scored", "value": "too few; " + value, "bar": bar})
        else:
            out.append({"id": pid, "outcome": "held" if share(l) < share(e) else "failed",
                        "value": "%.4f to %.4f (%s)" % (share(e), share(l), value), "bar": bar})
    bar = "within-technology fall (2016-2019 share minus mix-standardized 2022-2025 share) at least half the total fall"
    s_e, s_l, s_std = share(got[EARLY]), share(got[LATE]), standardized(rows)
    if not t0 or s_std is None:
        out.append({"id": "T4", "outcome": "not scored",
                    "value": "T0 failed" if not t0 else "a technology has no 2022-2025 cohort", "bar": bar})
    else:
        within, total = s_e - s_std, s_e - s_l
        out.append({"id": "T4", "outcome": "held" if within >= total / 2 else "failed",
                    "value": "within %.4f of total %.4f (standardized %.4f)" % (within, total, s_std), "bar": bar})
    return out


def render(res):
    md = ["# nexttech %s: the next-month share of EIA-860M by technology" % __version__, "",
          "Scores docs/nexttech-plan.md (T0 to T4). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    g = res["log"]
    md += ["## Files", "",
           "Changelog: %s (%d bytes, md5 %s; %d rows). Expected %d bytes and %d rows: %s." % (
               g["url"], g["bytes"], g["md5"], g["rows"], ren.LOG_BYTES, ren.LOG_ROWS,
               (g["bytes"], g["rows"]) == (ren.LOG_BYTES, ren.LOG_ROWS)), "",
           "Workbooks read: %d. With errors: %s." % (len(res["files"]), "; ".join(
               "%s %s" % (f["month"], ", ".join(f["errors"])) for f in res["files"] if f["errors"]) or "none"), "",
           "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]) for p in res["predictions"]]
    scored = [p for p in res["predictions"] if p["id"] != "T0" and p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored (T0 is a check, not counted)." % (
        sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## By period and technology", "",
           "| period | technology | cohort | operating | share | MW | MW operating | MW share |",
           "|---|---|---|---|---|---|---|---|"]
    for p in res["periods"]:
        md.append("| %s | %s | %d | %d | %s | %.1f | %.1f | %s |" % (
            p["period"], p["group"], p["cohort"], p["operating"], _f(p["share"]), p["mw"], p["mw_operating"],
            _f(p["mw_share"])))
    md += ["", "## By year and technology", "", "| year | technology | cohort | operating | share |",
           "|---|---|---|---|---|"]
    for y in res["years"]:
        md.append("| %s | %s | %d | %d | %s |" % (y["year"], y["group"], y["cohort"], y["operating"], _f(y["share"])))
    md += ["", "Cohort generators without a technology, by month: %s." % (
        "; ".join("%s %d" % (m, n) for m, n in sorted(res["missing_by_month"].items()) if n) or "none")]
    return "\n".join(md) + "\n"


def _f(v):
    return "-" if v is None else "%.4f" % v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-25T12:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(ren.deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "monthcheck": mc.__version__, "retiredentry": ren.__version__,
           "retiredgap": rg.__version__, "user_agent": UA, "started_at": now()}
    try:
        data = ren._get(ren.LOG_URL)
        log = ren.load_log(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "changelog not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "nexttech.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res["log"] = {"url": ren.LOG_URL, "bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(log)}
    print("changelog %d bytes, %d rows" % (len(data), len(log)), flush=True)
    co = cohorts(log)
    del log
    print("cohort months %d, generators %d" % (len(co), sum(len(v) for v in co.values())), flush=True)
    files, zips, out_rows, detail, missing_by_month = [], {}, [], [], {}
    for m in sorted(co):
        p = rs.prev_month(m)
        f, book, _ = ren.read_month(p, args.data_dir, zips)
        files.append(f)
        ks = rg.keyset(book) if book is not None else {}
        miss = 0
        for key, where, mw in co[m]:
            hit = ks.get(key)
            tech = hit[1].get("technology") if hit else None
            if not hit:
                miss += 1
            grp = tech_group(tech)
            out_rows.append((m, grp, where, mw))
            detail.append({"month": m, "key": key, "technology": tech, "group": grp, "now": where,
                           "nameplate_mw": mw, "found": bool(hit)})
        missing_by_month[m] = miss
        print("%s (workbook %s, %s bytes, errors %s): cohort %d, without a technology %d" % (
            m, p, f.get("bytes"), f["errors"], len(co[m]), miss), flush=True)
        del book, ks
    res["files"] = files
    res["missing_by_month"] = missing_by_month
    missing = {per: sum(n for m, n in missing_by_month.items() if in_period(m, per)) for per in (EARLY, LATE)}
    res["predictions"] = score(out_rows, missing)
    res["periods"] = []
    for per in (EARLY, LATE):
        for grp in GROUPS + (None,):
            sel = [r for r in out_rows if in_period(r[0], per) and (grp is None or r[1] == grp)]
            n, op = len(sel), sum(1 for r in sel if r[2] == "Operating")
            mw = sum(r[3] for r in sel)
            mwo = sum(r[3] for r in sel if r[2] == "Operating")
            res["periods"].append({"period": "%s to %s" % per, "group": grp or "all", "cohort": n, "operating": op,
                                   "share": None if n == 0 else op / n, "mw": round(mw, 1),
                                   "mw_operating": round(mwo, 1), "mw_share": None if mw == 0 else mwo / mw})
    res["years"] = [{"year": y, "group": grp, "cohort": c[0], "operating": c[1],
                     "share": None if c[0] == 0 else c[1] / c[0], "mw": round(c[2], 1), "mw_operating": round(c[3], 1)}
                    for (y, grp), c in sorted(tally(out_rows).items())]
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "nexttech.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "nexttech_cohort.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["month", "key", "technology", "group", "now", "nameplate_mw", "found"])
        w.writeheader()
        w.writerows(detail)
    with open(os.path.join(args.out_dir, "nexttech_years.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["year", "group", "cohort", "operating", "share", "mw", "mw_operating"])
        w.writeheader()
        w.writerows(res["years"])
    md = render(res)
    with open(os.path.join(args.out_dir, "nexttech.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
