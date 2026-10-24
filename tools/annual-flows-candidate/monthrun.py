"""monthrun: score a new EIA-860M month when EIA's own site must supply more than one month.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

gapcensus.py 0.1.0 appends EIA's own file for one month only, the month after the last one in PUDL's
raw archive (August 2026). Scoring October 2026 (docs/oct2026-plan.md) needs September and October
from EIA's site. This runs the same steps with the gapcensus, history, monthcheck, retiredentry and
nexttech code unchanged:

- replays the archived workbooks (md5-checked zips, history.py 0.1.0's reader, gapcensus.Census's
  event rule) through --archive-through, then appends EIA's own file for each month of --eia-months
  in order (honest User-Agent; size and md5 recorded, and compared with the archive's copy when the
  archive has the month too);
- C0: compares the rebuilt changelog's text through September 2026 with the published dataset 0.1.1
  (commit a3ce085), the copy docs/sep2026.md scored;
- scores P1 to P4 with monthcheck.score 0.1.0 unchanged, and checks P4's band against the plan's;
- P5: scans every row of every sheet of the target month's file with retiredentry.parse (plant id or
  not) for rows whose technology is nuclear and whose retirement year is before 2002; the month
  before is scanned too, for comparison;
- S3 of docs/sepretired-plan.md: how many of the 16 generators that left the Retired sheet in
  September 2026 the target month lists again, on any sheet the changelog reads;
- reports, not scored, the target month's next-month cohort by technology group (nexttech.tech_group,
  the technology from the month before's file) and split into generators in a next-month cohort for
  the first time since July 2015 and those listed again.

A practice run takes August and September 2026 from EIA's site instead of the archive and must
reproduce the published changelog and every number of docs/sep2026.md:

    python monthrun.py --data-dir /data --out-dir /out --archive-through 2026-07 \
        --eia-months 2026-08,2026-09 --target 2026-09

The October run, after wait_eia.py has seen EIA's October file:

    python monthrun.py --data-dir /data --out-dir /out --archive-through 2026-08 \
        --eia-months 2026-09,2026-10 --target 2026-10
"""

import argparse
import collections
import csv
import gzip
import io
import json
import os
import sys
import urllib.request
import zipfile

import pandas as pd

import gapcensus as gc
import history as hs
import layouts as ly
import monthcheck as mc
import nexttech as nt
import retiredentry as ren
import retiredgap as rg
import revert as rv

__version__ = "0.1.0"
PLAN = "docs/oct2026-plan.md"
PUBLISHED = ren.LOG_URL     # dataset 0.1.1 at commit a3ce085: July 2015 to September 2026
PUBLISHED_LAST = "2026-09"
# P4's band as docs/oct2026-plan.md gives it (from data/monthcheck_months_2026-09.csv, 6 decimals)
PLAN_BAND = {"2026-10": (0.219512, 0.473958)}
BAND_TOL = 1e-6
NUCLEAR_BEFORE = 2002       # P5
S3_KEYS = ren.KEYS          # the 16 generators that left the Retired sheet in September 2026
S3_MAX = 3
# what a practice run on September 2026 must reproduce (docs/sep2026.md, docs/retiredentry.md)
EXPECT = {"2026-09": {"listed": 38162, "listed_before": 38011, "left": 20, "left_retired": 16, "cohort": 170,
                      "operating": 57, "held": [True, True, False, True], "p5": 0, "p5_before": 28, "s3": 0}}
LISTINGS = ("first", "repeat", "all")
UA = "mv2-munim-monthrun/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def _get(url, timeout=300):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def check_months(last, months):
    """The archive's last month fed and the EIA months -> None if each follows the one before with no
    gap, else what is wrong."""
    if not months:
        return "no EIA month given"
    want = last
    for m in months:
        want = gc.next_month(want)
        if m != want:
            return "%s given where %s was expected" % (m, want)
    return None


def p5_rows(scan):
    """Rows of every sheet (retiredentry.parse) -> those whose technology is nuclear and whose retirement
    year is before 2002 (rows with no year are not counted here)."""
    return [r for r in scan if "nuclear" in str(r.get("technology") or "").lower()
            and r.get("retirement_year") is not None and r["retirement_year"] < NUCLEAR_BEFORE]


def s3_back(rows, month, keys=S3_KEYS):
    """Changelog rows -> the keys listed in that month, on any sheet the changelog reads."""
    hist = ren.history(rows, keys)
    return sorted(k for k in keys if ren.state(hist[k], month))


def first_listing(stats, target):
    """Per-month stats with cohort detail -> {key: True if no month before the target had it in its
    next-month cohort} for the target month's cohort."""
    seen, t = set(), None
    for x in stats:
        if x["month"] < target:
            seen.update(d["key"] for d in x.get("detail", []))
        elif x["month"] == target:
            t = x
    return {} if t is None else {d["key"]: d["key"] not in seen for d in t.get("detail", [])}


def by_tech(detail, techs, first):
    """The target cohort's detail rows, {key: technology} and {key: first listing?} -> one row per
    technology group and listing with at least one generator."""
    c = collections.Counter()
    for d in detail:
        g = nt.tech_group(techs.get(d["key"]))
        lst = "first" if first.get(d["key"]) else "repeat"
        for grp in (g, "all"):
            for l in (lst, "all"):
                c[(grp, l)] += 1
                if d["now"] == "Operating":
                    c[(grp, l, "op")] += 1
    out = []
    for grp in nt.GROUPS + ("all",):
        for l in LISTINGS:
            n = c[(grp, l)]
            if n:
                out.append({"group": grp, "listing": l, "cohort": n, "operating": c[(grp, l, "op")],
                            "share": c[(grp, l, "op")] / n})
    return out


def band_check(score, target):
    """monthcheck's band against the plan's -> {plan, job, same} or None when the plan gives none."""
    want = PLAN_BAND.get(target)
    if want is None:
        return None
    got = score.get("band")
    same = got is not None and all(abs(a - b) <= BAND_TOL for a, b in zip(got, want))
    return {"plan": list(want), "job": None if got is None else list(got), "same": same}


def expect_check(target, t, before, score, p5, p5_before, s3):
    """A practice month's numbers against EXPECT -> {item: [expected, got, same]} or None."""
    e = EXPECT.get(target)
    if e is None:
        return None
    held = [p["held"] for p in score["predictions"] if p["id"] in ("P1", "P2", "P3", "P4")]
    got = {"listed": t and t["listed"], "listed_before": before and before["listed"],
           "left": t and t["events"].get("left", 0), "left_retired": t and t["left_by_sheet"].get("Retired", 0),
           "cohort": t and t["cohort"], "operating": t and t["cohort_by"]["Operating"], "held": held,
           "p5": p5, "p5_before": p5_before, "s3": s3}
    return {k: [e[k], got[k], e[k] == got[k]] for k in e}


def month_bytes(month, raw, paths):
    """A month's workbook bytes and where they came from: EIA's site if this run fetched it, else the
    archive's zip; (None, reason) when neither has it."""
    if month in raw:
        return raw[month], "EIA's site"
    p = dict(paths).get(int(month[:4]))
    if p is None:
        return None, "no zip"
    with zipfile.ZipFile(p) as zf:
        member = rg.member_for(zf.namelist(), month)
        return (zf.read(member), "PUDL archive: %s" % member) if member else (None, "not in the zip")


def scan_month(data):
    """xlsx bytes -> (book, every-sheet rows of retiredentry.parse, error)."""
    try:
        book, scan = ren.parse(data)
        return book, scan, None
    except Exception as e:  # recorded, not raised
        return None, None, "%s: %s" % (type(e).__name__, e)


def _f(v):
    return "-" if v is None else "%.4f" % v


def render(r):
    md = ["# monthrun %s: EIA-860M %s" % (__version__, r.get("target")), "",
          "Pre-registration: %s. Mode: %s. MV2 of Munim, Inc. (made with AI agents)." % (PLAN, r.get("mode")), ""]
    if r.get("error"):
        md += ["Stopped: %s" % r["error"], ""]
    md += ["## Files", "", "Archive replayed through %s (%d months; not readable: %s)." % (
        r.get("archive_through"), len(r.get("archive_months", [])), ", ".join(r.get("archive_unreadable", [])) or "none"),
        "", "| month | url | bytes | md5 | archive md5 | same as archive | readable | keys | rows appended | events "
        "| errors and problems |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in r.get("eia", []):
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            e["month"], e.get("url") or "-", e.get("bytes", "-"), e.get("md5", "-"), e.get("archive_md5", "-"),
            e.get("same_as_archive", "-"), e.get("readable", "-"), e.get("keys", "-"), e.get("rows_appended", "-"),
            ", ".join("%s %d" % kv for kv in sorted(e.get("events", {}).items())) or "-",
            "; ".join(e.get("errors", []) + e.get("problems", [])) or "none"))
    c = r.get("published")
    if c:
        md += ["", "## C0: rebuilt changelog against the published copy", ""]
        if c.get("error"):
            md += ["Not compared: %s" % c["error"]]
        else:
            md += ["Published: %s (%d bytes, md5 %s). Same text through %s: %s. Lines: published %d, rebuilt %d. "
                   "First difference: %s." % (c["url"], c["bytes"], c["md5"], PUBLISHED_LAST, c["same"],
                                              c["lines_published"], c["lines_rebuilt"], c["first_difference"] or "none")]
            if c["first_difference"]:
                md += ["", "Published line: `%s`" % c["published_line"], "", "Rebuilt line: `%s`" % c["rebuilt_line"]]
        md += ["", "Rebuilt rows, all months: %s (%s)." % (r.get("log_rows"), hs.LOG_FILE)]
    s = r.get("score")
    if s:
        names = {True: "held", False: "failed", None: "not scored"}
        md += ["", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
        md += ["| %s | %s | %s | %s |" % (p["id"], names[p["held"]], p["value"], p["bar"]) for p in s["predictions"]]
        md += ["", "Held: %d of %d scored." % (s["held"], s["scored"])]
        b = r.get("band_check")
        if b:
            md += ["", "P4's band, plan %s, job %s: same %s." % (b["plan"], b["job"], b["same"])]
    x = r.get("s3")
    if x:
        md += ["", "## S3 (docs/sepretired-plan.md)", "",
               "Of the %d generators that left the Retired sheet in September 2026, listed in %s: %d (%s). "
               "Bar: at most %d. %s." % (len(S3_KEYS), r["target"], len(x["back"]), ", ".join(x["back"]) or "none",
                                         S3_MAX, names_of(x["held"]))]
    nuc = r.get("nuclear")
    if nuc:
        md += ["", "## Nuclear rows retired before %d, every sheet, plant id or not" % NUCLEAR_BEFORE, "",
               "| month | source | nuclear rows | retired before %d | also on a Retired sheet with no year |"
               % NUCLEAR_BEFORE, "|---|---|---|---|---|"]
        for m in sorted(nuc):
            n = nuc[m]
            md.append("| %s | %s | %s | %s | %s |" % (m, n["source"], n.get("nuclear", "-"), n.get("before", "-"),
                                                     n.get("no_year_retired", "-")))
            if n.get("error"):
                md.append("| %s | not read: %s | | | |" % (m, n["error"]))
    t = r.get("target_stats")
    if t:
        md += ["", "## The %s next-month cohort" % t["month"], "",
               "Generators that the month before listed on the Planned sheet with planned operating month %s: %d "
               "(%.1f MW); listed as operating in %s: %d. Still planned for a later month: %d." % (
                   t["month"], t["cohort"], t["cohort_mw"], t["month"], t["cohort_by"]["Operating"], t["planned_later"]),
               "", "| where now | generators | MW |", "|---|---|---|"]
        md += ["| %s | %d | %.1f |" % (g, t["cohort_by"][g], t["cohort_mw_by"][g]) for g in mc.GROUPS]
    bt = r.get("by_tech")
    if bt is not None:
        md += ["", "### By technology group and listing (reported, not scored)", "",
               "Technology from %s; cohort generators it does not list: %d. first: in a next-month cohort for the "
               "first time since July 2015; repeat: in an earlier month's cohort too." % (
                   r.get("tech_source"), r.get("tech_missing", 0)), "",
               "| technology | listing | cohort | operating | share |", "|---|---|---|---|---|"]
        md += ["| %s | %s | %d | %d | %s |" % (x["group"], x["listing"], x["cohort"], x["operating"], _f(x["share"]))
               for x in bt]
    ex = r.get("expect")
    if ex:
        md += ["", "## Practice check against the published numbers", "", "| item | expected | got | same |",
               "|---|---|---|---|"]
        md += ["| %s | %s | %s | %s |" % (k, v[0], v[1], v[2]) for k, v in ex.items()]
        md += ["", "All the same: %s." % all(v[2] for v in ex.values())]
    return "\n".join(md) + "\n"


def names_of(held):
    return {True: "held", False: "failed", None: "not scored"}[held]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--archive-through", required=True, help="YYYY-MM: last archived month to replay")
    ap.add_argument("--eia-months", required=True, help="YYYY-MM,YYYY-MM: EIA's own files to append, in order")
    ap.add_argument("--target", required=True, help="YYYY-MM: the month to score")
    ap.add_argument("--published", default=PUBLISHED)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    months = [m.strip() for m in args.eia_months.split(",") if m.strip()]
    r = {"version": __version__, "gapcensus": gc.__version__, "history": hs.__version__, "monthcheck": mc.__version__,
         "retiredentry": ren.__version__, "nexttech": nt.__version__, "user_agent": UA, "target": args.target,
         "archive_through": args.archive_through, "eia_months": months, "started_at": gc.now(),
         "mode": "practice (the month is in the published changelog)" if args.target <= PUBLISHED_LAST
         else "scored (EIA's own files, appended)"}
    zips, paths = [], []
    for year in ly.YEARS:
        p, z = ly.get_zip(year, args.data_dir, ly.ZIP_MD5.get(year), None)
        z.update(year=year, ok=p is not None)
        zips.append(z)
        if p is not None:
            paths.append((year, p))
    r["zips"] = zips
    err = None if len(paths) == len(ly.YEARS) else "zips with a listed md5: %d of %d" % (len(paths), len(ly.YEARS))
    census, rows, infos = gc.Census(), [], []

    def feed(month, wb):
        for k, ev, v in census.feed(month, rv.w_map(wb), dict(zip(wb["key"], wb["sheet"]))):
            rows.append(hs.log_row(month, k, ev, v))

    if err is None:
        for month, wb in hs.workbooks(paths, infos):
            if wb is not None and month <= args.archive_through:
                feed(month, wb)
        r["archive_months"] = [i["month"] for i in infos if i["month"] <= args.archive_through]
        r["archive_unreadable"] = [i["month"] for i in infos if not i["readable"] and i["month"] <= args.archive_through]
        if not r["archive_months"] or r["archive_months"][-1] != args.archive_through:
            err = "the archive does not end its replay at %s" % args.archive_through
        else:
            err = check_months(args.archive_through, months)
    arch = {i["month"]: i for i in infos}
    raw, files = {}, []
    if err is None:
        for m in months:
            e = {"month": m, "plan": "append"}
            files.append(e)
            data, e["url"], e["errors"] = rg.download(rg.eia_urls(m), get=_get)
            if data is None:
                print("%s %s: not served" % (gc.now(), m), flush=True)
                break
            e.update(bytes=len(data), md5=rg.md5(data))
            if m in arch:
                e.update(archive_md5=arch[m]["md5"], same_as_archive=arch[m]["md5"] == e["md5"])
            try:
                sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
                wb, info = hs.month_frame(m, sheets)
                del sheets
            except Exception as ex:  # recorded, not raised
                e.update(readable=False, problems=["not read: %s: %s" % (type(ex).__name__, ex)], keys=0)
                break
            e.update(readable=info["readable"], problems=info["problems"], keys=info["keys"])
            raw[m] = data
            if not info["readable"]:
                break
            n0 = len(rows)
            feed(m, wb)
            e["rows_appended"] = len(rows) - n0
            e["events"] = dict(collections.Counter(x["event"] for x in rows[n0:]))
            print("%s %s: %d bytes, md5 %s, keys %d, rows appended %d" % (
                gc.now(), m, e["bytes"], e["md5"], e["keys"], e["rows_appended"]), flush=True)
    r["eia"] = files
    if err:
        r["error"] = err
    else:
        with gzip.open(os.path.join(args.out_dir, hs.LOG_FILE), "wt", newline="", encoding="utf-8") as fh:
            fh.write(gc.log_text(rows))
        r["log_rows"] = len(rows)
        try:
            data = _get(args.published)
            pub = gzip.decompress(data).decode("utf-8")
            c = gc.compare_text(pub, gc.log_text([x for x in rows if x["report_month"] <= PUBLISHED_LAST]))
            c.update(url=args.published, bytes=len(data), md5=rg.md5(data))
        except Exception as ex:  # recorded, not raised
            c = {"error": "%s: %s" % (type(ex).__name__, ex)}
        r["published"] = c
        stats = mc.replay(rows, detail_for=nt._Every())
        e_t = next((e for e in files if e["month"] == args.target), {"month": args.target, "plan": "append"})
        r["score"] = mc.score(stats, args.target, e_t)
        r["band_check"] = band_check(r["score"], args.target)
        by = {x["month"]: x for x in stats}
        t = by.get(args.target)
        before = by.get(gc.m_str(gc.m_index(args.target) - 1))
        nuc, counts = {}, {}
        for m in (gc.m_str(gc.m_index(args.target) - 1), args.target):
            data, src = month_bytes(m, raw, paths)
            if data is None:
                nuc[m] = {"source": src, "error": "no file"}
                continue
            book, scan, why = scan_month(data)
            if why:
                nuc[m] = {"source": src, "error": why}
                continue
            hits = p5_rows(scan)
            counts[m] = len(hits)
            nuc[m] = {"source": src, "nuclear": sum(1 for x in scan if "nuclear" in str(x["technology"] or "").lower()),
                      "before": len(hits), "no_year_retired": len(ren.old_nuclear(scan)) - len(hits),
                      "rows": [dict(x, month=m) for x in hits]}
            if m != args.target:
                r["tech_source"] = "%s's file (%s)" % (m, src)
                techs = {k: v[1].get("technology") for k, v in rg.keyset(book).items()}
            del book, scan
        r["nuclear"] = {m: {k: v for k, v in n.items() if k != "rows"} for m, n in nuc.items()}
        p5 = counts.get(args.target)
        r["score"]["predictions"].append(mc.pred(
            "P5", None if p5 is None else p5 == 0, "not read" if p5 is None else "%d rows" % p5,
            "no row on any sheet, plant id or not, nuclear and retired before %d" % NUCLEAR_BEFORE))
        mc.finish(r["score"])
        if t is not None:
            back = s3_back(rows, args.target)
            r["s3"] = {"back": back, "held": len(back) <= S3_MAX}
            r["target_stats"] = {k: v for k, v in t.items() if k != "detail"}
            first = first_listing(stats, args.target)
            tk = techs if "tech_source" in r else {}
            r["tech_missing"] = sum(1 for d in t["detail"] if d["key"] not in tk)
            r["by_tech"] = by_tech(t["detail"], tk, first)
            with open(os.path.join(args.out_dir, "monthrun_cohort.csv"), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, ["key", "status_before", "nameplate_mw", "now", "status_now", "planned_month_now",
                                        "technology", "group", "listing"])
                w.writeheader()
                for d in t["detail"]:
                    w.writerow(dict(d, technology=tk.get(d["key"]) or "", group=nt.tech_group(tk.get(d["key"])),
                                    listing="first" if first.get(d["key"]) else "repeat"))
        r["expect"] = expect_check(args.target, t, before, r["score"], p5,
                                   counts.get(gc.m_str(gc.m_index(args.target) - 1)),
                                   len(r["s3"]["back"]) if "s3" in r else None)
        r["months"] = [{k: v for k, v in x.items() if k != "detail"} for x in stats]
        mc.write_months(os.path.join(args.out_dir, "monthrun_months.csv"), stats)
        with open(os.path.join(args.out_dir, "monthrun_nuclear.csv"), "w", newline="", encoding="utf-8") as fh:
            cols = ["month", "sheet", "plant_id", "plant_name", "generator_id", "technology", "retirement_year",
                    "nameplate_mw"]
            w = csv.writer(fh)
            w.writerow(cols)
            for m in sorted(nuc):
                for x in nuc[m].get("rows", []):
                    w.writerow([ren._cell(x.get(c)) for c in cols])
    r["finished_at"] = gc.now()
    with open(os.path.join(args.out_dir, "monthrun.json"), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, default=str)
    md = render(r)
    with open(os.path.join(args.out_dir, "monthrun.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 2 if r.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
