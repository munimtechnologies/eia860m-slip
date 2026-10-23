"""monthcheck: score EIA's newest EIA-860M month against bars fixed before EIA released it.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Pre-registration: docs/sep2026-plan.md, committed before EIA published its September 2026
workbook. The job runs gapcensus.py 0.1.0 unchanged (it replays the 134 archived workbooks with
history.py 0.1.0's reader and, with --eia-month, appends EIA's own file for the month after the
archive's last to the rebuilt changelog), then replays that changelog once more and counts, for
every month:

- events (first, changed, left, back) and the sheet group each "left" generator was on before;
- generators listed at the end of the month;
- the next-month cohort: generators that the month before listed on the Planned sheet with a
  planned operating month equal to this month, and where this month lists them (Operating,
  Planned, Retired, another sheet, or absent), by count and by nameplate MW. "absent" includes
  moves to the Canceled or Postponed sheet, which the changelog does not read.

The four predictions are scored for the target month; the months before it are the record they
are scored against. A target month that was already in the archive is a practice run.

    python monthcheck.py --data-dir /data --out-dir /out --eia-month 2026-09
"""

import argparse
import collections
import csv
import gzip
import json
import math
import os

import gapcensus as gc
import history as hs

__version__ = "0.1.0"
PLAN = "docs/sep2026-plan.md"
GROUPS = ("Operating", "Planned", "Retired", "other", "absent")
KEYS_TOL = 0.03          # P1: generators listed within 3% of the month before
LEFT_MAX = 50            # P2: at most 50 "left" events
RETIRED_LEFT_BELOW = 10  # P3: fewer than 10 of them from the Retired sheet
BAND_MONTHS = 24         # P4: the 24 months before the target set the band


def read_log(path):
    """The rebuilt changelog (csv.gz) -> its rows as dicts of strings."""
    with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def mw(x):
    """A nameplate_mw cell -> float; 0.0 when blank or not a number (NaN too)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if math.isnan(v) else v


def replay(rows, detail_for=None):
    """Changelog rows -> one dict per report month, in month order. The month named by
    detail_for also gets "detail": one row per generator of its next-month cohort."""
    by_month = collections.OrderedDict()
    for r in rows:
        by_month.setdefault(r["report_month"], []).append(r)
    state, out = {}, []
    for m in sorted(by_month):
        cohort = {k: v for k, v in state.items()
                  if gc.sheet_group(v["sheet"]) == "Planned" and v["planned_month"] == m}
        ev, left = collections.Counter(), collections.Counter()
        for r in by_month[m]:
            ev[r["event"]] += 1
            if r["event"] == "left":
                before = state.pop(r["key"], None)
                left[gc.sheet_group(before["sheet"]) if before else "other"] += 1
            else:
                state[r["key"]] = r
        n_by, mw_by, later, detail = collections.Counter(), collections.Counter(), 0, []
        for k in sorted(cohort):
            v, now = cohort[k], state.get(k)
            g = "absent" if now is None else gc.sheet_group(now["sheet"])
            n_by[g] += 1
            mw_by[g] += mw(v["nameplate_mw"])
            if g == "Planned" and now["planned_month"] > m:
                later += 1
            if m == detail_for:
                detail.append({"key": k, "status_before": v["status"], "nameplate_mw": v["nameplate_mw"],
                               "now": g, "status_now": now["status"] if now else "",
                               "planned_month_now": now["planned_month"] if now else ""})
        n = len(cohort)
        x = {"month": m, "listed": len(state), "events": dict(ev), "left_by_sheet": dict(left),
             "cohort": n, "cohort_by": {g: n_by[g] for g in GROUPS},
             "cohort_mw": round(sum(mw_by.values()), 1),
             "cohort_mw_by": {g: round(mw_by[g], 1) for g in GROUPS},
             "planned_later": later, "share_operating": None if n == 0 else n_by["Operating"] / n}
        if m == detail_for:
            x["detail"] = detail
        out.append(x)
    return out


def band(values):
    """The prior months' shares -> (second lowest, second highest), or None for fewer than 3."""
    s = sorted(values)
    return (s[1], s[-2]) if len(s) >= 3 else None


def pred(pid, held, value, bar):
    return {"id": pid, "held": held, "value": value, "bar": bar}


def score(stats, target, eia=None):
    """Per-month stats, the target month and gapcensus's record of EIA's file -> the four
    predictions (held True, False, or None when not scored)."""
    by = {s["month"]: s for s in stats}
    t = by.get(target)
    bars = ("readable; listed within 3% of the month before",
            "at most %d" % LEFT_MAX, "fewer than %d" % RETIRED_LEFT_BELOW,
            "second lowest to second highest of the %d months before" % BAND_MONTHS)
    if t is None:
        got = bool(eia and eia.get("md5"))
        why = ("EIA's file was downloaded but not read" if got
               else "EIA's file for %s was not available" % target)
        preds = [pred("P1", False if got else None, why, bars[0])]
        preds += [pred(p, None, "not in the changelog", b) for p, b in zip(("P2", "P3", "P4"), bars[1:])]
        return finish({"target": target, "error": why, "predictions": preds})
    prior = [s for s in stats if s["month"] < target]
    p = prior[-1] if prior else None
    read_ok = eia is None or eia.get("plan") == "compare" or eia.get("readable") is True
    if p is None or not p["listed"]:
        preds = [pred("P1", None, "no month before the target", bars[0])]
    else:
        d = (t["listed"] - p["listed"]) / p["listed"]
        preds = [pred("P1", bool(read_ok and abs(d) <= KEYS_TOL),
                      "listed %d vs %d in %s (%+.2f%%); readable %s" % (
                          t["listed"], p["listed"], p["month"], 100 * d, read_ok), bars[0])]
    nl, nr = t["events"].get("left", 0), t["left_by_sheet"].get("Retired", 0)
    preds.append(pred("P2", nl <= LEFT_MAX, "%d left" % nl, bars[1]))
    preds.append(pred("P3", nr < RETIRED_LEFT_BELOW, "%d left from Retired" % nr, bars[2]))
    shares = [(s["month"], s["share_operating"]) for s in prior if s["share_operating"] is not None]
    shares = shares[-BAND_MONTHS:]
    b = band([v for _, v in shares]) if len(shares) == BAND_MONTHS else None
    ts = t["share_operating"]
    res = {"target": target, "band": b, "band_months": [shares[0][0], shares[-1][0]] if shares else None}
    if b is None or ts is None:
        preds.append(pred("P4", None, "cohort %d; prior months with a cohort %d" % (t["cohort"], len(shares)),
                          bars[3]))
    else:
        preds.append(pred("P4", b[0] <= ts <= b[1], "%.4f (%d of %d)" % (
            ts, t["cohort_by"]["Operating"], t["cohort"]), "%.4f to %.4f (%s to %s)" % (
            b[0], b[1], shares[0][0], shares[-1][0])))
    res["predictions"] = preds
    return finish(res)


def finish(res):
    res["scored"] = sum(1 for p in res["predictions"] if p["held"] is not None)
    res["held"] = sum(1 for p in res["predictions"] if p["held"])
    return res


def render(r):
    md = ["# monthcheck %s: EIA-860M %s against bars fixed in advance" % (__version__, r.get("target")), "",
          "Pre-registration: %s. Mode: %s. MV2 of Munim, Inc. (made with AI agents)." % (
              PLAN, r.get("mode")), ""]
    if r.get("error"):
        return "\n".join(md + ["Not run: %s" % r["error"], ""])
    s = r["score"]
    md += ["## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    names = {True: "held", False: "failed", None: "not scored"}
    md += ["| %s | %s | %s | %s |" % (p["id"], names[p["held"]], p["value"], p["bar"]) for p in s["predictions"]]
    md += ["", "Held: %d of %d scored." % (s["held"], s["scored"]), ""]
    if s.get("error"):
        md += ["Note: %s" % s["error"], ""]
    t = r.get("target_stats")
    if t:
        md += ["## The %s next-month cohort" % t["month"], "",
               "Generators that the month before listed on the Planned sheet with planned operating month "
               "%s: %d (%.1f MW). Where %s lists them:" % (t["month"], t["cohort"], t["cohort_mw"], t["month"]), "",
               "| where now | generators | MW |", "|---|---|---|"]
        md += ["| %s | %d | %.1f |" % (g, t["cohort_by"][g], t["cohort_mw_by"][g]) for g in GROUPS]
        md += ["", "Still on the Planned sheet with a later planned month: %d." % t["planned_later"], ""]
    md += ["## Month by month (last 25 months)", "",
           "| month | listed | first | changed | left | back | left from Retired | cohort | to Operating | share |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for x in r["months"][-25:]:
        e = x["events"]
        md.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %s |" % (
            x["month"], x["listed"], e.get("first", 0), e.get("changed", 0), e.get("left", 0), e.get("back", 0),
            x["left_by_sheet"].get("Retired", 0), x["cohort"], x["cohort_by"]["Operating"],
            "-" if x["share_operating"] is None else "%.4f" % x["share_operating"]))
    return "\n".join(md) + "\n"


def write_months(path, stats):
    cols = ["month", "listed", "first", "changed", "left", "back", "left_operating", "left_planned",
            "left_retired", "cohort", "cohort_mw"] + ["cohort_%s" % g.lower() for g in GROUPS] + [
            "cohort_mw_%s" % g.lower() for g in GROUPS] + ["planned_later", "share_operating"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for x in stats:
            e, lb = x["events"], x["left_by_sheet"]
            w.writerow([x["month"], x["listed"], e.get("first", 0), e.get("changed", 0), e.get("left", 0),
                        e.get("back", 0), lb.get("Operating", 0), lb.get("Planned", 0), lb.get("Retired", 0),
                        x["cohort"], x["cohort_mw"]] + [x["cohort_by"][g] for g in GROUPS] +
                       [x["cohort_mw_by"][g] for g in GROUPS] +
                       [x["planned_later"], "" if x["share_operating"] is None else round(x["share_operating"], 6)])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--eia-month", required=True, help="YYYY-MM: EIA's own file to append (or compare)")
    ap.add_argument("--target", default=None, help="month to score (default: --eia-month)")
    args = ap.parse_args(argv)
    target = args.target or args.eia_month
    os.makedirs(args.out_dir, exist_ok=True)
    r = {"version": __version__, "gapcensus": gc.__version__, "target": target, "started_at": gc.now()}
    g = gc.main(["--data-dir", args.data_dir, "--out-dir", args.out_dir, "--eia-month", args.eia_month])
    e = g.get("eia") or {}
    r["eia"] = e
    r["mode"] = ("scored (EIA's own file, appended)" if e.get("plan") == "append"
                 else "practice (the month was already in the archive)")
    if g.get("error"):
        r["error"] = "gapcensus: %s" % g["error"]
    else:
        stats = replay(read_log(os.path.join(args.out_dir, hs.LOG_FILE)), detail_for=target)
        r["months"] = [{k: v for k, v in x.items() if k != "detail"} for x in stats]
        r["score"] = score(stats, target, e)
        t = next((x for x in stats if x["month"] == target), None)
        if t:
            r["target_stats"] = {k: v for k, v in t.items() if k != "detail"}
            with open(os.path.join(args.out_dir, "monthcheck_cohort.csv"), "w", newline="",
                      encoding="utf-8") as fh:
                w = csv.DictWriter(fh, ["key", "status_before", "nameplate_mw", "now", "status_now",
                                        "planned_month_now"])
                w.writeheader()
                w.writerows(t.get("detail", []))
        write_months(os.path.join(args.out_dir, "monthcheck_months.csv"), stats)
    r["finished_at"] = gc.now()
    with open(os.path.join(args.out_dir, "monthcheck.json"), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, default=str)
    md = render(r)
    with open(os.path.join(args.out_dir, "monthcheck.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return r


if __name__ == "__main__":
    main()
