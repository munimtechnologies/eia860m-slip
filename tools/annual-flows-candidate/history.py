"""history: how far back does PUDL's EIA-860M changelog keep stale values? (twenty-ninth test)

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Predictions fixed in docs/history-revert-predictions.md (commit 04fb92c, 22 October 2026) and
pre-registered in docs/history-revert-preregistration.md before any workbook was compared with
PUDL; the job waits until that file is live on GitHub before it reads any data.

Every monthly EIA-860M workbook in PUDL's raw archive (Zenodo record 22995197, eia860m-2015.zip
to eia860m-2026.zip, md5-checked as layouts.py 0.1.0 checks them) is read with layouts.py's
sheet reader and compared with PUDL's changelog record in force that month on three fields
(revert.py 0.1.0's proj and match: status, planned month for a planned status, MW within
0.05). make_changelog's rule is simulated from the first workbook month, fed only the workbooks.

Two readings differ from revert.py, both set from the structure check (job layouts-v1) and
PUDL's EIA-860M column map before any comparison: MW is read only from a Nameplate Capacity
column (the sheets of 2015-07 to 2016-03 have none, only Net Summer Capacity, and PUDL's
capacity_mw is blank for those months), and PUDL's missing capacity is missing, not 0 MW. A
field missing on either side is not compared (revert.match). In the simulation a missing field
equals only a missing field, as pandas' drop_duplicates treats NaN.

Also written: a consecutive changelog of every generator built from the workbooks themselves
(a row when a generator is first listed, changes, leaves or comes back) and every hit
generator-month with PUDL's stale value.

    python history.py --data-dir /data --out-dir /out \
        [--wait-for URL --token TEXT --minutes 100] [--compare-base URL --minutes-same 20]
"""

import argparse
import collections
import csv
import gzip
import io
import json
import os
import time
import zipfile

import pandas as pd

import eia860m_slip as es
import layouts as ly
import rawcheck as rc
import revert as rv
import watchlist as wl

__version__ = "0.1.0"
SCORED = tuple(range(2016, 2026))   # P1 and P5
P1_MIN = 50                         # P1: hit generator-months in each scored year
COVERAGE = 0.90                     # P2
PRECISION = 0.50                    # P3
P4_YEARS = (2017, 2025)             # P4: mean hits per month, later year above earlier
YEAR_COVERAGE = 0.80                # P5
KEYS_MIN = 0.95                     # C3
MIN_UNITS = 100                     # C4
LAST = "2026-08"                    # C2
SAMPLE = 10
PREREG = "docs/history-revert-preregistration.md"
COMMITS = ("https://api.github.com/repos/munimtechnologies/eia860m-slip/commits"
           "?path=%s&per_page=1" % PREREG)
FILES = ("history.py", "test_history.py")
KINDS = ("predicted", "pudl_later", "held_before", "other")
EVENTS = ("first", "changed", "left", "back")
LOG_COLS = ("report_month", "key", "plant_id_eia", "generator_id", "event", "sheet", "status",
            "planned_month", "nameplate_mw")
HIT_COLS = ("month", "key", "fields", "workbook", "pudl", "pudl_reported", "simulated",
            "differs_since")
LOG_FILE = "eia860m_changelog_from_workbooks.csv.gz"
HIT_FILE = "history_hits.csv"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def commit_of(fetch=rv._get):
    """The commit that last changed the pre-registration on GitHub -> {sha, date} or {error}."""
    try:
        c = json.loads(fetch(COMMITS))[0]
        return {"sha": c["sha"], "date": c["commit"]["committer"]["date"]}
    except Exception as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}


def prepare(raw):
    """PUDL's changelog columns -> eia860m_slip.prepare's records plus cap_raw, the capacity
    with a missing value left missing (prepare fills it with 0)."""
    raw = raw.copy()
    raw["cap_raw"] = pd.to_numeric(raw["capacity_mw"], errors="coerce")
    return es.prepare(raw)


def _missing(p):
    return (not p[0], p[1] is None, p[2] is None)


def sim_match(a, b):
    """make_changelog's equality on two projections: revert.match, and a field missing on one
    side equals only a field missing on the other."""
    return _missing(a) == _missing(b) and rv.match(a, b)


def step(state, w):
    """One month of make_changelog's rule for one generator. state: [values taken in so far,
    value in force]; w: its workbook projection (None when not listed) -> (value in force,
    whether w matches a value taken in before this month)."""
    seen, cur = state
    held = w is not None and any(sim_match(w, h) for h in seen)
    if w is not None and (cur is None or not sim_match(w, cur)) and not held:
        state[1] = w
        seen.append(w)
    return state[1], held


def month_frame(month, sheets):
    """A month's sheets ({name: raw frame}) -> (the route's records, one row per key, MW missing
    on a sheet with no Nameplate Capacity column; month info with layouts.py's readability)."""
    infos, recs = [], []
    for name, raw in sheets.items():
        info, rec = ly.sheet_info(name, raw)
        infos.append(info)
        if rec is None or info["left_out"]:
            continue
        cap = info["picks"]["capacity"]
        info["nameplate"] = cap is not None and "nameplate" in str(cap).lower()
        if not info["nameplate"]:
            rec = rec.assign(capacity_mw=float("nan"))
        recs.append(rec)
    probs = ["%s: %s" % (i["sheet"], p) for i in infos for p in i["problems"]]
    if not any(i["kind"] == "operating" and not i["left_out"] and i.get("rows", 0) > 0
               for i in infos):
        probs.append("no Operating sheet with rows")
    wb = pd.concat(recs, ignore_index=True) if recs else None
    dup = 0 if wb is None else int(wb["key"].duplicated().sum())
    if wb is not None:
        wb = wb.drop_duplicates("key", keep="first").reset_index(drop=True)
    return wb, {"month": month, "readable": not probs, "problems": probs, "duplicate_keys": dup,
                "keys": 0 if wb is None else int(len(wb)),
                "nameplate_sheets": [i["sheet"] for i in infos if i.get("nameplate")],
                "other_capacity_sheets": [i["sheet"] for i in infos if i.get("nameplate") is False]}


def p_map(df, r):
    """PUDL's records in force at report month r -> {key: (projection, report month)}."""
    s = es.snapshot(df, r)
    return {k: (rv.proj(st, pm, mw), rep) for k, st, pm, mw, rep in
            zip(s["key"], s["status"], s["planned_m"], s["cap_raw"], s["report_m"])}


def log_row(month, key, event, v):
    """One row of the consecutive changelog; v = (sheet, status, planned month, MW) or None."""
    pid, gid = key.split("/", 1)
    sheet, status, planned, mw = v if v else (None, None, None, None)
    return {"report_month": month, "key": key, "plant_id_eia": pid, "generator_id": gid,
            "event": event, "sheet": sheet or "", "status": status or "",
            "planned_month": es.month_str(planned) or "", "nameplate_mw": "" if mw is None else mw}


def blank_year():
    return dict({"months": 0, "workbook": 0, "with_pudl": 0, "units": 0, "disagree": 0,
                 "sim_stale": 0, "hits": 0, "workbook_only": 0, "workbook_only_held": 0},
                **{k: 0 for k in KINDS if k != "predicted"})


def finish(y):
    """Shares of one year's (or the total's) counts; unrounded comparisons are in verdict."""
    y["coverage"] = round(y["hits"] / y["disagree"], 4) if y["disagree"] else None
    y["precision"] = round(y["hits"] / y["sim_stale"], 4) if y["sim_stale"] else None
    y["keys_share"] = round(y["with_pudl"] / y["workbook"], 4) if y["workbook"] else None
    y["hits_per_month"] = round(y["hits"] / y["months"], 2) if y["months"] else None
    return y


def replay(df, frames, log=None, hits_out=None):
    """The scored part. df: PUDL's records (prepare); frames: (month, workbook records or None)
    in month order; log, hits_out: callables taking one row of the changelog and of the hits ->
    counts by year and month, disagreements by kind, field and status, event counts, samples."""
    recs = collections.defaultdict(list)
    for k, r, st, pm, mw in zip(df["key"], df["report_m"], df["status"], df["planned_m"],
                                df["cap_raw"]):
        recs[k].append((r, rv.proj(st, pm, mw)))
    state, last, since, prev = {}, {}, {}, set()
    years, by_month = collections.OrderedDict(), []
    pairs, events = collections.Counter(), collections.Counter()
    samples = collections.defaultdict(list)
    for month, wb in frames:
        if wb is None:
            continue
        r, yr = wl.parse_month(month), int(month[:4])
        y = years.setdefault(yr, blank_year())
        y["months"] += 1
        wm = rv.w_map(wb)
        sheets = dict(zip(wb["key"], wb["sheet"]))
        pm = p_map(df, r)
        mu = md = mh = 0
        for k in sorted(wm):
            w = wm[k]
            sim, held = step(state.setdefault(k, [[], None]), w)
            v = (sheets[k], w[0], w[1], None if w[2] is None else round(w[2], 3))
            ev = ("first" if k not in last else "back" if k not in prev
                  else "changed" if v != last[k] else None)
            last[k] = v
            if ev:
                events[(yr, ev)] += 1
                if log:
                    log(log_row(month, k, ev, v))
            y["workbook"] += 1
            p = pm.get(k)
            if p is None:
                y["workbook_only"] += 1
                y["workbook_only_held"] += int(held)
                since.pop(k, None)
                continue
            y["with_pudl"] += 1
            y["units"] += 1
            mu += 1
            u = {"w": w, "p": p[0], "sim": sim}
            if sim is not None and not rv.match(sim, w):
                y["sim_stale"] += 1
            if rv.match(w, p[0]):
                since.pop(k, None)
                continue
            y["disagree"] += 1
            md += 1
            first = since.setdefault(k, month)
            kind = rv.classify(u, [x for rr, x in recs[k] if rr > r],
                               [x for rr, x in recs[k] if rr < p[1]])
            f = rv.differs(w, p[0])
            pairs[(kind, f[0] if f else "-", w[0], p[0][0])] += 1
            if kind == "predicted":
                y["hits"] += 1
                mh += 1
                if hits_out:
                    hits_out({"month": month, "key": k, "fields": "; ".join(f),
                              "workbook": rv.cell(w), "pudl": rv.cell(p[0]),
                              "pudl_reported": es.month_str(p[1]), "simulated": rv.cell(sim),
                              "differs_since": first})
            else:
                y[kind] += 1
                if len(samples[(yr, kind)]) < SAMPLE:
                    samples[(yr, kind)].append({"key": k, "month": month, "workbook": rv.cell(w),
                                                "pudl": rv.cell(p[0]),
                                                "pudl_reported": es.month_str(p[1])})
        for k in sorted(prev - set(wm)):
            events[(yr, "left")] += 1
            since.pop(k, None)
            if log:
                log(log_row(month, k, "left", None))
        prev = set(wm)
        by_month.append({"month": month, "units": mu, "disagree": md, "hits": mh})
    total = blank_year()
    for y in years.values():
        finish(y)
        for c in total:
            total[c] += y[c]
    return {"years": years, "total": finish(total), "by_month": by_month,
            "pairs": [{"kind": a, "field": b, "workbook": c, "pudl": d, "n": n}
                      for (a, b, c, d), n in pairs.most_common()],
            "events": {yr: {e: events[(yr, e)] for e in EVENTS} for yr in years},
            "samples": [{"year": yr, "kind": kd, "rows": rows}
                        for (yr, kd), rows in sorted(samples.items())]}


def checks_for(zips, months, res, last_m, want_years):
    """C1 to C4 (C3 and C4 only once the workbooks are read)."""
    got = sorted({int(m["month"][:4]) for m in months})
    bad = [m["month"] for m in months if not m["readable"]]
    c = {"C1 workbooks": {
        "ok": all(z["ok"] for z in zips) and got == sorted(want_years) and not bad,
        "detail": "zips with a listed md5 %d of %d; years read %s; months read %d; not readable: %s" % (
            sum(1 for z in zips if z["ok"]), len(zips), ", ".join(map(str, got)) or "none",
            len(months), ", ".join(bad) or "none")},
        "C2 PUDL through %s" % LAST: {"ok": last_m >= wl.parse_month(LAST),
                                      "detail": "latest report %s" % es.month_str(last_m)}}
    if res:
        ys, t = res["years"], res["total"]
        low = ["%d %s" % (yr, y["keys_share"]) for yr, y in ys.items()
               if y["with_pudl"] < KEYS_MIN * y["workbook"]]
        c["C3 keys"] = {"ok": bool(ys) and not low,
                        "detail": "years below %.2f: %s; lowest share %s" % (
                            KEYS_MIN, ", ".join(low) or "none",
                            min((y["keys_share"] for y in ys.values() if y["keys_share"] is not None),
                                default=None))}
        c["C4 links"] = {"ok": t["disagree"] >= MIN_UNITS and t["sim_stale"] >= MIN_UNITS,
                         "detail": "disagree %d, simulation stale %d (each at least %d)" % (
                             t["disagree"], t["sim_stale"], MIN_UNITS)}
    return c


def verdict(res, checks):
    """Checks first: any failed check means not scored. Then P1-P5 against the bars fixed in
    docs/history-revert-predictions.md, compared unrounded."""
    ys = (res or {}).get("years", {})
    if (not checks or not all(c["ok"] for c in checks.values())
            or any(n not in ys for n in SCORED + P4_YEARS)):
        return {"scored": False, "held": None, "predictions": {}}
    t = res["total"]
    a, b = ys[P4_YEARS[0]], ys[P4_YEARS[1]]
    p = {"P1": all(ys[n]["hits"] >= P1_MIN for n in SCORED),
         "P2": t["hits"] >= COVERAGE * t["disagree"],
         "P3": t["hits"] >= PRECISION * t["sim_stale"],
         "P4": b["hits"] * a["months"] > a["hits"] * b["months"],
         "P5": all(ys[n]["hits"] >= YEAR_COVERAGE * ys[n]["disagree"] for n in SCORED)}
    return {"scored": True, "held": sum(p.values()), "predictions": p}


def workbooks(paths, infos):
    """(year, zip path) pairs -> (month, records or None when not readable) for every month the
    zips hold, in order; each month's info is appended to infos."""
    for year, path in paths:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            for k in range(1, 13):
                month = "%d-%02d" % (year, k)
                member, _ = rc.member_for(names, month)
                if member is None:
                    continue
                t0 = time.time()
                data = zf.read(member)
                sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
                wb, info = month_frame(month, sheets)
                info.update(member=member, md5=rc.md5(data), seconds=round(time.time() - t0, 1))
                infos.append(info)
                print("%s %s keys %d readable %s %ss" % (month, member, info["keys"],
                                                       info["readable"], info["seconds"]), flush=True)
                yield month, (wb if info["readable"] else None)


def listed_md5(download=rc.download):
    """The record's datapackage.json -> {read, tried, md5: {file name: md5}}."""
    pkg = {"read": False, "tried": [], "md5": {}}
    for url in rc.file_urls(ly.RECORD, "datapackage.json"):
        data, err = download(url, timeout=120)
        pkg["tried"].append({"url": url, "error": err})
        if data is not None:
            pkg["md5"] = ly.listed_md5(data.decode("utf-8", "replace"))
            pkg["read"] = True
            break
    return pkg


def _share(x):
    return "-" if x is None else "%.4f" % x


def render(result):
    md = ["# history %s: how far back does PUDL's EIA-860M changelog keep stale values?" % __version__,
          "", "Twenty-ninth test. Predictions fixed in docs/history-revert-predictions.md, method "
          "pre-registered in %s. MV2 of Munim, Inc. (made with AI agents)." % PREREG, ""]
    g = result.get("gate", {})
    md += ["Pre-registration live: %s (checks %s, at %s; commit %s)." % (
        g.get("live"), g.get("checks"), g.get("at"), result.get("prereg_commit", {}).get("sha")), ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    v = result["verdict"]
    md += ["## Checks", "", "| check | ok | detail |", "|---|---|---|"]
    for name, c in result["checks"].items():
        md.append("| %s | %s | %s |" % (name, c["ok"], c["detail"]))
    md.append("")
    res = result.get("result")
    if v["scored"]:
        ys, t, p = res["years"], res["total"], v["predictions"]
        a, b = ys[P4_YEARS[0]], ys[P4_YEARS[1]]
        md += ["## Predictions", "", "Scored: %d of 5 predictions held." % v["held"], "",
               "| prediction | bar | value | held |", "|---|---|---|---|",
               "| P1 hits in each year %d-%d | at least %d | lowest %d (%d) | %s |" % (
                   SCORED[0], SCORED[-1], P1_MIN, min(ys[n]["hits"] for n in SCORED),
                   min(SCORED, key=lambda n: (ys[n]["hits"], n)), p["P1"]),
               "| P2 coverage, all months | %.2f | %s (%d of %d) | %s |" % (
                   COVERAGE, _share(t["coverage"]), t["hits"], t["disagree"], p["P2"]),
               "| P3 precision, all months | %.2f | %s (%d of %d) | %s |" % (
                   PRECISION, _share(t["precision"]), t["hits"], t["sim_stale"], p["P3"]),
               "| P4 hits per month, %d above %d | greater | %s against %s | %s |" % (
                   P4_YEARS[1], P4_YEARS[0], b["hits_per_month"], a["hits_per_month"], p["P4"]),
               "| P5 coverage in each year %d-%d | %.2f | lowest %s (%d) | %s |" % (
                   SCORED[0], SCORED[-1], YEAR_COVERAGE,
                   _share(min((ys[n]["coverage"] for n in SCORED if ys[n]["coverage"] is not None),
                              default=None)),
                   min(SCORED, key=lambda n: (ys[n]["coverage"] if ys[n]["coverage"] is not None else 2, n)),
                   p["P5"]), ""]
    else:
        md += ["Not scored: a check failed or a scored year was not read.", ""]
    if not res:
        return "\n".join(md)
    md += ["## By year", "",
           "| year | months | workbook generator-months | with a PUDL record | share | in both | "
           "disagree | hits | simulation stale | coverage | precision | hits per month | PUDL "
           "later | PUDL held before | other | workbook only | of which held before |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = list(res["years"].items()) + [("all", res["total"])]
    for yr, y in rows:
        md.append("| %s | %d | %d | %d | %s | %d | %d | %d | %d | %s | %s | %s | %d | %d | %d | %d | %d |" % (
            yr, y["months"], y["workbook"], y["with_pudl"], _share(y["keys_share"]), y["units"],
            y["disagree"], y["hits"], y["sim_stale"], _share(y["coverage"]), _share(y["precision"]),
            y["hits_per_month"], y["pudl_later"], y["held_before"], y["other"], y["workbook_only"],
            y["workbook_only_held"]))
    md += ["", "## Changelog rebuilt from the workbooks: rows by year and event", "",
           "| year | %s |" % " | ".join(EVENTS), "|---|" + "---|" * len(EVENTS)]
    for yr, e in res["events"].items():
        md.append("| %s | %s |" % (yr, " | ".join(str(e[x]) for x in EVENTS)))
    md += ["", "## Disagreements by kind, first differing field and status (top 40)", "",
           "| kind | field | workbook | PUDL | generator-months |", "|---|---|---|---|---|"]
    for x in res["pairs"][:40]:
        md.append("| %s | %s | %s | %s | %d |" % (x["kind"], x["field"], x["workbook"] or "-",
                                                 x["pudl"] or "-", x["n"]))
    md += ["", "## Disagreements the rule does not predict (first %d per year and kind, in month "
           "and key order; not a random draw)" % SAMPLE, ""]
    for s in res["samples"]:
        md.append("- %s %s: %s" % (s["year"], s["kind"], "; ".join(
            "%s %s workbook %s, PUDL %s (from %s)" % (x["month"], x["key"], x["workbook"], x["pudl"],
                                                   x["pudl_reported"]) for x in s["rows"])))
    if not res["samples"]:
        md.append("None.")
    md += ["", "## By month", "", "| month | in both | disagree | hits |", "|---|---|---|---|"]
    for m in res["by_month"]:
        md.append("| %s | %d | %d | %d |" % (m["month"], m["units"], m["disagree"], m["hits"]))
    other = [m["month"] for m in result.get("months", []) if m.get("other_capacity_sheets")]
    md += ["", "Months whose sheets have no Nameplate Capacity column (MW not compared): %s." % (
        ", ".join(other) or "none")]
    pub = result.get("published")
    if pub:
        md += ["", "Published copies same as run copies: %s (%s)." % (pub["same"], ", ".join(
            "%s %s %s" % (n, f["same"], f["md5"]) for n, f in pub["files"].items()))]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--year", action="append", type=int, default=None)
    ap.add_argument("--wait-for", default=None, help="raw URL of the live pre-registration")
    ap.add_argument("--token", default=None, help="text the live pre-registration contains")
    ap.add_argument("--minutes", type=float, default=100.0)
    ap.add_argument("--compare-base", default=None, help="raw URL folder of the published copies")
    ap.add_argument("--minutes-same", type=float, default=20.0)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    result = {"version": __version__, "layouts": ly.__version__, "revert": rv.__version__,
              "started_at": now()}
    if args.wait_for:
        result["gate"] = rv.wait_for(args.wait_for, args.token or "", args.minutes)
        result["prereg_commit"] = commit_of()
        if not result["gate"]["live"]:
            result["error"] = "pre-registration not live after %s minutes" % args.minutes
    if not result.get("error"):
        import pyarrow.parquet as pq
        path = es.find_parquet(args.data_dir)
        names = pq.read_schema(path).names
        df = prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
        last_m = int(df["report_m"].max())
        st = os.stat(path)
        result["pudl"] = {"file": os.path.basename(path), "bytes": st.st_size,
                          "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                          "max_report": es.month_str(last_m), "rows": int(len(df))}
        pkg = listed_md5()
        result["datapackage"] = {"read": pkg["read"], "tried": pkg["tried"], "files": len(pkg["md5"])}
        want = list(args.year or ly.YEARS)
        zips, paths = [], []
        for year in want:
            name = "eia860m-%d.zip" % year
            p, z = ly.get_zip(year, args.data_dir, ly.ZIP_MD5.get(year), pkg["md5"].get(name))
            z.update(year=year, ok=p is not None)
            zips.append(z)
            if p is not None:
                paths.append((year, p))
        result["zips"] = zips
        months = []
        with gzip.open(os.path.join(args.out_dir, LOG_FILE), "wt", newline="", encoding="utf-8") as lf, \
                open(os.path.join(args.out_dir, HIT_FILE), "w", newline="", encoding="utf-8") as hf:
            lw, hw = csv.DictWriter(lf, LOG_COLS), csv.DictWriter(hf, HIT_COLS)
            lw.writeheader()
            hw.writeheader()
            res = replay(df, workbooks(paths, months), lw.writerow, hw.writerow)
        result["months"] = months
        result["result"] = res
        result["checks"] = checks_for(zips, months, res, last_m, want)
        result["verdict"] = verdict(res, result["checks"])
        pd.DataFrame([dict(year=yr, **y) for yr, y in res["years"].items()]).to_csv(
            os.path.join(args.out_dir, "history_years.csv"), index=False)
        pd.DataFrame(res["by_month"]).to_csv(os.path.join(args.out_dir, "history_months.csv"),
                                             index=False)
    result["finished_at"] = now()
    if args.compare_base:
        result["published"] = ly.same_as_published(args.compare_base, FILES, args.minutes_same)
    with open(os.path.join(args.out_dir, "history.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "history.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
