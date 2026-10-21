"""revert: does PUDL's EIA-860M changelog drop a value that comes back? (twenty-eighth test)

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Pre-registered in docs/changelog-revert-preregistration.md before any of its numbers were
computed; the job waits until that file is live on GitHub before it reads any data.

PUDL builds core_eia860m__changelog_generators with pudl.helpers.make_changelog, which sorts a
generator's monthly records by report_date and calls drop_duplicates(keep="first") on every
column but report_date. A monthly record is so kept only if no EARLIER record of the generator
has the same values, not only the record before it: a value that changes and later comes back
(A, B, A) loses its second A, and PUDL's record in force stays B. Four predictions:

P1  no generator in the changelog has two records equal in every column but report_date and
    valid_until_date (the published file follows that rule);
P2  of the 2026 generator-months in which EIA's workbook and PUDL's record in force disagree,
    at least 0.90 are predicted by that rule simulated on three fields (status, planned month,
    MW), started from PUDL's records before 2026 and fed the 2026 workbooks;
P3  of the generator-months in which the simulation keeps a value the workbook no longer has,
    PUDL's record in force is that value in at least 0.50;
P4  69338/LEAKY's August 2026 and 69372/KNOXS's July 2026 workbook rows each match, on the three
    fields, a PUDL record of that generator reported before 2026.

    python revert.py --data-dir /data --out-dir /out \
        [--wait-for URL --token TEXT --minutes 100]
"""

import argparse
import collections
import io
import json
import os
import time
import urllib.request
import zipfile

import numpy as np
import pandas as pd

import eia860m_slip as es
import keyhist as kh
import watchlist as wl

__version__ = "0.1.0"
MONTHS = tuple("2026-%02d" % k for k in range(1, 9))
START = "2026-01"
LAST = "2026-08"
MW_TOL = 0.05
COVERAGE = 0.90     # P2
PRECISION = 0.50    # P3
MIN_UNITS = 100     # C3: the rule must link at least this many generator-months both ways
NAMED = (("69338/LEAKY", "2026-08"), ("69372/KNOXS", "2026-07"))   # P4
DATE_COLS = ("report_date", "valid_until_date", "report_date_max")
AGENT = "mv2-munim-eia860m-probe/0.1 (MV2 of Munim, Inc.; mv2@munimtech.com)"
COMMITS = ("https://api.github.com/repos/munimtechnologies/eia860m-slip/commits"
           "?path=docs/changelog-revert-preregistration.md&per_page=1")
SAMPLE = 30
FIELDS = ("status", "planned month", "MW")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def wait_for(url, token, minutes, sleep=120, fetch=_get, clock=time.time, pause=time.sleep):
    """Poll url until its text contains token, for at most `minutes` -> {live, checks, at,
    error}. No data is read before this returns live."""
    deadline = clock() + minutes * 60
    checks, err = 0, None
    while True:
        checks += 1
        try:
            if token in fetch(url):
                return {"live": True, "checks": checks, "at": now(), "error": None}
        except Exception as e:  # a failed poll is retried until the deadline
            err = "%s: %s" % (type(e).__name__, e)
        if clock() >= deadline:
            return {"live": False, "checks": checks, "at": now(), "error": err}
        pause(sleep)


def commit_of(fetch=_get):
    """The commit that last changed the pre-registration on GitHub -> {sha, date} or {error}."""
    try:
        c = json.loads(fetch(COMMITS))[0]
        return {"sha": c["sha"], "date": c["commit"]["committer"]["date"]}
    except Exception as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return None if v != v else v


def proj(status, planned, mw):
    """The three fields compared here: status code, planned month (only for a planned status),
    MW."""
    s = "" if status is None or status != status else str(status).strip().upper()
    if s == "NAN" or s == "NONE":
        s = ""
    p = _num(planned) if s in es.PLANNED else None
    return (s, None if p is None else int(p), _num(mw))


def w_proj(status, sheet, planned, mw):
    """A workbook row -> proj. The Retired sheet has no status column; its rows read RE, as
    PUDL codes them."""
    blank = status is None or status != status or not str(status).strip()
    if blank and "retire" in str(sheet).lower():
        status = "RE"
    return proj(status, planned, mw)


def match(a, b):
    """Do two projections agree? A field missing on either side is not compared."""
    if a[0] and b[0] and a[0] != b[0]:
        return False
    if a[1] is not None and b[1] is not None and a[1] != b[1]:
        return False
    if a[2] is not None and b[2] is not None and abs(a[2] - b[2]) > MW_TOL:
        return False
    return True


def differs(w, p):
    """The fields on which a workbook projection and a PUDL projection disagree."""
    out = []
    if w[0] and p[0] and w[0] != p[0]:
        out.append("status")
    if w[1] is not None and p[1] is not None and w[1] != p[1]:
        out.append("planned month")
    if w[2] is not None and p[2] is not None and abs(w[2] - p[2]) > MW_TOL:
        out.append("MW")
    return out


def simulate(seen, start, rows):
    """make_changelog's rule on projections: a workbook value is taken in only when no earlier
    value of the generator matches it. seen: projections of its PUDL records before the first
    month; start: the projection in force the month before (None if none); rows: its workbook
    projection each month (None where it is not in the workbook) -> the projection in force
    each month."""
    seen, cur, out = list(seen), start, []
    for w in rows:
        if w is not None and (cur is None or not match(w, cur)):
            if not any(match(w, h) for h in seen):
                cur = w
                seen.append(w)
        out.append(cur)
    return out


def classify(u, later, earlier):
    """A disagreeing generator-month -> 'predicted' (the simulation gives PUDL's value),
    'pudl_later' (a later PUDL record has the workbook's value), 'held_before' (an earlier PUDL
    record has it) or 'other'."""
    if is_hit(u):
        return "predicted"
    if any(match(u["w"], x) for x in later):
        return "pudl_later"
    if any(match(u["w"], x) for x in earlier):
        return "held_before"
    return "other"


def is_hit(u):
    s = u["sim"]
    return (s is not None and not match(s, u["w"]) and match(s, u["p"])
            and not match(u["p"], u["w"]))


def score(units):
    """Generator-months in both sources (dicts with w, p, sim) -> the counts P2 and P3 use."""
    d = sum(1 for u in units if not match(u["w"], u["p"]))
    s = sum(1 for u in units if u["sim"] is not None and not match(u["sim"], u["w"]))
    hits = sum(1 for u in units if is_hit(u))
    return {"units": len(units), "disagree": d, "sim_stale": s, "hits": hits,
            "coverage": round(hits / d, 4) if d else None,
            "precision": round(hits / s, 4) if s else None}


def repeat_count(path):
    """Records equal in every column but the date columns to another record of the same
    generator, found by hashing each row's other columns one column at a time."""
    import pyarrow.parquet as pq
    names = [c for c in pq.read_schema(path).names if c not in DATE_COLS]
    h = None
    for c in names:
        col = pq.read_table(path, columns=[c]).to_pandas()[c]
        ch = pd.util.hash_pandas_object(col, index=False).to_numpy(dtype=np.uint64)
        h = ch if h is None else (h * np.uint64(1099511628211)) ^ ch
    ids = pq.read_table(path, columns=["plant_id_eia", "generator_id", "report_date"]).to_pandas()
    frame = pd.DataFrame({"key": ids["plant_id_eia"].astype(str) + "/" + ids["generator_id"].astype(str),
                          "h": h, "report": es.months(ids["report_date"])})
    dup = frame.duplicated(["key", "h"], keep="first")
    sample = [{"key": k, "report": es.month_str(r)} for k, r in
              zip(frame.loc[dup, "key"].head(SAMPLE), frame.loc[dup, "report"].head(SAMPLE))]
    return {"columns": len(names), "column_names": names, "rows": int(len(frame)),
            "repeats": int(dup.sum()), "generators_with_repeats": int(frame.loc[dup, "key"].nunique()),
            "sample": sample}


def w_map(wb):
    return {k: w_proj(s, sh, pm, mw) for k, s, sh, pm, mw in
            zip(wb["key"], wb["status"], wb["sheet"], wb["planned_m"], wb["capacity_mw"])}


def p_map(df, r):
    s = es.snapshot(df, r)
    return {k: (proj(st, pm, mw), rep) for k, st, pm, mw, rep in
            zip(s["key"], s["status"], s["planned_m"], s["capacity_mw"], s["report_m"])}


def cell(p):
    if p is None:
        return ""
    return "%s, %s, %s MW" % (p[0] or "-", es.month_str(p[1]) or "-",
                              "-" if p[2] is None else "%.1f" % p[2])


def named(key, month, wmaps, recs):
    """P4 for one generator: its workbook row in month and the PUDL records before START that
    match it on the three fields."""
    w = wmaps.get(month, {}).get(key)
    before = [(r, p) for r, p in recs.get(key, []) if r < wl.parse_month(START)]
    hits = [es.month_str(r) for r, p in before if w is not None and match(w, p)]
    return {"key": key, "month": month, "workbook": cell(w), "records_before": len(before),
            "matching_reports": hits, "held": bool(hits)}


def run(df, frames, repeats):
    """The scored part, given prepared PUDL records, workbook frames by month (for_compare'd)
    and repeat_count's result."""
    wmaps = {m: w_map(frames[m]) for m in MONTHS}
    pmaps = {m: p_map(df, wl.parse_month(m)) for m in MONTHS}
    start = p_map(df, wl.parse_month(START) - 1)
    recs = collections.defaultdict(list)
    for k, r, st, pm, mw in zip(df["key"], df["report_m"], df["status"], df["planned_m"],
                                df["capacity_mw"]):
        recs[k].append((r, proj(st, pm, mw)))
    first = wl.parse_month(START)
    units, kinds, pairs, by_month = [], collections.Counter(), collections.Counter(), {}
    rows_out = []
    keys = sorted(set().union(*[set(wmaps[m]) for m in MONTHS]))
    for k in keys:
        rows = [wmaps[m].get(k) for m in MONTHS]
        seen = [p for r, p in recs.get(k, []) if r < first]
        st = start.get(k)
        sim = simulate(seen, st[0] if st else None, rows)
        run_start = None
        for i, m in enumerate(MONTHS):
            w, pr = rows[i], pmaps[m].get(k)
            if w is None or pr is None:
                run_start = None
                continue
            u = {"key": k, "month": m, "w": w, "p": pr[0], "p_report": pr[1], "sim": sim[i]}
            units.append(u)
            if match(w, pr[0]):
                run_start = None
                continue
            run_start = run_start or m
            r = wl.parse_month(m)
            later = [p for rr, p in recs[k] if rr > r]
            earlier = [p for rr, p in recs[k] if rr < pr[1]]
            kind = classify(u, later, earlier)
            kinds[(m, kind)] += 1
            if kind == "predicted":
                f = differs(w, pr[0])
                pairs[(f[0] if f else "-", w[0], pr[0][0])] += 1
                if m == LAST:
                    rows_out.append({"key": k, "fields": "; ".join(f), "workbook": cell(w),
                                     "pudl": cell(pr[0]), "pudl_reported": es.month_str(pr[1]),
                                     "differs_since": run_start, "workbook_mw": w[2]})
    sc = score(units)
    for m in MONTHS:
        by_month[m] = {"units": sum(1 for u in units if u["month"] == m),
                       **{c: kinds[(m, c)] for c in ("predicted", "pudl_later", "held_before", "other")}}
    p4 = [named(k, m, wmaps, recs) for k, m in NAMED]
    gone = sorted(set(wmaps[LAST]) - set(pmaps[LAST]))
    trace = [{"key": k, "sheet_status": cell(wmaps[LAST][k]),
              "in_workbook": [m for m in MONTHS if k in wmaps[m]],
              "pudl_records": [{"report": es.month_str(r), "value": cell(p)} for r, p in
                               sorted(recs.get(k, []), key=lambda x: x[0])][-6:]}
             for k in gone[:SAMPLE]]
    return {"score": sc, "by_month": by_month,
            "pairs": [{"field": a, "workbook": b, "pudl": c, "n": n}
                      for (a, b, c), n in pairs.most_common()],
            "august": sorted(rows_out, key=lambda x: (-(x["workbook_mw"] or 0), x["key"])),
            "named": p4, "repeats": repeats, "august_workbook_only": len(gone),
            "august_workbook_only_trace": trace}


def verdict(res, checks):
    """Checks first: any failed check means not scored. Then P1-P4 against the bars set before."""
    if not all(c["ok"] for c in checks.values()):
        return {"scored": False, "held": None, "predictions": {}}
    sc = res["score"]
    p = {"P1": res["repeats"]["repeats"] == 0,
         "P2": sc["hits"] >= COVERAGE * sc["disagree"],
         "P3": sc["hits"] >= PRECISION * sc["sim_stale"],
         "P4": all(x["held"] for x in res["named"])}
    return {"scored": True, "held": sum(p.values()), "predictions": p}


def render(result):
    md = ["# revert %s: does PUDL's EIA-860M changelog drop a value that comes back?" % __version__,
          "", "Twenty-eighth test, pre-registered in docs/changelog-revert-preregistration.md. "
          "MV2 of Munim, Inc. (made with AI agents).", ""]
    g = result.get("gate", {})
    md.append("Pre-registration live: %s (checks %s, at %s; commit %s)." % (
        g.get("live"), g.get("checks"), g.get("at"), result.get("prereg_commit", {}).get("sha")))
    md.append("")
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    v = result["verdict"]
    md += ["## Checks", "", "| check | ok | detail |", "|---|---|---|"]
    for name, c in result["checks"].items():
        md.append("| %s | %s | %s |" % (name, c["ok"], c["detail"]))
    md.append("")
    if not v["scored"]:
        return "\n".join(md + ["Not scored: a check failed.", ""])
    r = result["result"]
    sc = r["score"]
    md += ["## Predictions", "", "Scored: %d of 4 predictions held." % v["held"], "",
           "| prediction | bar | value | held |", "|---|---|---|---|",
           "| P1 repeats in the changelog | 0 | %d | %s |" % (r["repeats"]["repeats"], v["predictions"]["P1"]),
           "| P2 coverage | %.2f | %s (%d of %d) | %s |" % (COVERAGE, sc["coverage"], sc["hits"], sc["disagree"], v["predictions"]["P2"]),
           "| P3 precision | %.2f | %s (%d of %d) | %s |" % (PRECISION, sc["precision"], sc["hits"], sc["sim_stale"], v["predictions"]["P3"]),
           "| P4 named generators | both | %s | %s |" % (
               ", ".join("%s %s" % (x["key"], x["held"]) for x in r["named"]), v["predictions"]["P4"]),
           "", "Generator-months in both sources: %d." % sc["units"], "",
           "## Disagreements by month", "",
           "| month | in both | predicted | PUDL takes it later | PUDL held it before | other |",
           "|---|---|---|---|---|---|"]
    for m, b in r["by_month"].items():
        md.append("| %s | %d | %d | %d | %d | %d |" % (m, b["units"], b["predicted"], b["pudl_later"],
                                                     b["held_before"], b["other"]))
    md += ["", "## Predicted disagreements by first differing field and value", "",
           "| field | workbook | PUDL | generator-months |", "|---|---|---|---|"]
    for x in r["pairs"][:40]:
        md.append("| %s | %s | %s | %d |" % (x["field"], x["workbook"] or "-", x["pudl"] or "-", x["n"]))
    md += ["", "## P4", "", "| generator | month | workbook | PUDL records before 2026 | matching |",
           "|---|---|---|---|---|"]
    for x in r["named"]:
        md.append("| %s | %s | %s | %d | %s |" % (x["key"], x["month"], x["workbook"],
                                                 x["records_before"], ", ".join(x["matching_reports"])))
    rp = r["repeats"]
    md += ["", "## P1", "", "%d rows, %d columns hashed (all but %s); %d repeats at %d generators." % (
        rp["rows"], rp["columns"], ", ".join(DATE_COLS), rp["repeats"], rp["generators_with_repeats"]),
        "", "## August 2026: generators the simulation predicts PUDL shows a stale value for", "",
        "%d generators, %.1f MW by the workbook." % (len(r["august"]), sum(x["workbook_mw"] or 0 for x in r["august"])),
        "", "| generator | fields | workbook | PUDL | PUDL reported | differs since |",
        "|---|---|---|---|---|---|"]
    for x in r["august"][:60]:
        md.append("| %s | %s | %s | %s | %s | %s |" % (x["key"], x["fields"], x["workbook"], x["pudl"],
                                                     x["pudl_reported"], x["differs_since"]))
    md += ["", "## August 2026 workbook generators with no PUDL record in force (descriptive)", "",
           "%d generators; first %d traced (last six PUDL records each)." % (
               r["august_workbook_only"], len(r["august_workbook_only_trace"])), "",
           "| generator | workbook August | 2026 workbooks listing it | last PUDL records |", "|---|---|---|---|"]
    for x in r["august_workbook_only_trace"]:
        md.append("| %s | %s | %s | %s |" % (x["key"], x["sheet_status"], ", ".join(x["in_workbook"]),
                                            "; ".join("%s: %s" % (y["report"], y["value"]) for y in x["pudl_records"])))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-for", default=None, help="URL of the live pre-registration")
    ap.add_argument("--token", default=None, help="text the live pre-registration contains")
    ap.add_argument("--minutes", type=float, default=100.0)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    result = {"version": __version__, "started_at": now()}
    if args.wait_for:
        result["gate"] = wait_for(args.wait_for, args.token or "", args.minutes)
        result["prereg_commit"] = commit_of()
        if not result["gate"]["live"]:
            result["error"] = "pre-registration not live after %s minutes" % args.minutes
    if not result.get("error"):
        import pyarrow.parquet as pq
        path = es.find_parquet(args.data_dir)
        names = pq.read_schema(path).names
        df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
        last_m = int(df["report_m"].max())
        st = os.stat(path)
        result["pudl"] = {"file": os.path.basename(path), "bytes": st.st_size,
                          "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                          "max_report": es.month_str(last_m), "rows": int(len(df))}
        data, zinfo = kh.get_zip(args.data_dir)
        result["zip"] = {k: v for k, v in zinfo.items() if k != "path"}
        frames = {}
        if data is not None:
            zf = zipfile.ZipFile(io.BytesIO(data))
            for m in MONTHS:
                wb, _ = kh.read_month(zf, m)
                frames[m] = None if wb is None else kh.for_compare(wb)
        checks = {
            "C1 workbooks": {"ok": data is not None and all(frames.get(m) is not None for m in MONTHS),
                             "detail": "zip md5 %s; months read %d of %d" % (
                                 kh.ZIP_MD5, sum(1 for m in MONTHS if frames.get(m) is not None), len(MONTHS))},
            "C2 PUDL through August": {"ok": last_m >= wl.parse_month(LAST),
                                       "detail": "latest report %s" % es.month_str(last_m)}}
        if checks["C1 workbooks"]["ok"]:
            res = run(df, frames, repeat_count(path))
            sc = res["score"]
            checks["C3 links"] = {"ok": sc["disagree"] >= MIN_UNITS and sc["sim_stale"] >= MIN_UNITS,
                                  "detail": "disagree %d, simulation stale %d (each at least %d)" % (
                                      sc["disagree"], sc["sim_stale"], MIN_UNITS)}
            result["result"] = res
        result["checks"] = checks
        result["verdict"] = verdict(result.get("result", {}), checks)
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "revert.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    if result.get("result"):
        pd.DataFrame(result["result"]["august"]).to_csv(
            os.path.join(args.out_dir, "revert_august.csv"), index=False)
    md = render(result)
    with open(os.path.join(args.out_dir, "revert.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
