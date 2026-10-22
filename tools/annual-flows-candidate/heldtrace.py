"""heldtrace: where do the disagreements the twenty-ninth test's simulation misses come from?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive follow-up to docs/history-revert.md (job history-v1: 4 of 5 predictions held; P5,
coverage of at least 0.80 in every year, failed in 2017, 2018 and 2019, where most misses are
of the "held before" kind). No prediction is tested. It replays the same 134 workbooks with
history.py 0.1.0's reader and simulation, and for every generator-month where the workbook and
PUDL's record in force disagree it records:

- what the workbook showed in the month PUDL's record in force was reported: "same" as that
  record, "differs", or "absent" (the generator was not in that month's workbook);
- for the "held before" kind, whether the simulation's value equals the workbook's (it took the
  returning value in) or is stale at another value, and whether an earlier PUDL record equals the
  workbook's value under the simulation's equality too (a missing field equals only a missing
  field), not only when a missing field is left uncompared;
- the plants with most "held before" generator-months;
- the months of the rebuilt changelog's "changed", "left" and "back" rows;
- for given generators, every month side by side, and PUDL's full rows (all columns).

    python heldtrace.py --data-dir /data --out-dir /out [--key 3075/11 ...]
"""

import argparse
import bisect
import collections
import json
import os
import time

import pandas as pd

import eia860m_slip as es
import history as hs
import layouts as ly
import revert as rv
import watchlist as wl

__version__ = "0.1.0"
KEYS = ("3075/11", "3075/12", "3075/7", "3082/2", "3925/1", "3655/1", "57299/1", "6175/2",
        "3921/3", "1134/5", "59485/PV2")
KINDS = ("predicted", "pudl_later", "held_before", "other")
WHERE = ("same", "differs", "absent")
EVENTS = ("first", "changed", "left", "back")
TOP = 25


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def at_month(hist, r):
    """A generator's workbook history [(month, projection or None)], one entry per change, ->
    its projection in month r (None when it was not listed then or not yet listed)."""
    i = bisect.bisect_right([m for m, _ in hist], r)
    return hist[i - 1][1] if i else None


def where_of(hist, p):
    """PUDL's record in force p = (projection, report month) -> what the workbook showed in
    the report month: 'same', 'differs' or 'absent'."""
    a = at_month(hist, p[1])
    return "absent" if a is None else "same" if rv.match(a, p[0]) else "differs"


def trace(df, frames, keys=()):
    """history.replay's loop with the extra counts. df: PUDL's records (history.prepare);
    frames: (month, workbook records or None) in month order -> dict."""
    recs = collections.defaultdict(list)
    for k, r, st, pm, mw in zip(df["key"], df["report_m"], df["status"], df["planned_m"],
                                df["cap_raw"]):
        recs[k].append((r, rv.proj(st, pm, mw)))
    want = set(keys)
    state, hist, last, prev = {}, collections.defaultdict(list), {}, set()
    kinds, where, held = collections.Counter(), collections.Counter(), collections.Counter()
    plants, events = collections.Counter(), collections.Counter()
    rows = collections.defaultdict(list)
    for month, wb in frames:
        if wb is None:
            continue
        r, yr = wl.parse_month(month), int(month[:4])
        wm = rv.w_map(wb)
        sheets = dict(zip(wb["key"], wb["sheet"]))
        pm = hs.p_map(df, r)
        for k in sorted(wm):
            w = wm[k]
            sim, was_held = hs.step(state.setdefault(k, [[], None]), w)
            v = (sheets[k], w[0], w[1], None if w[2] is None else round(w[2], 3))
            ev = ("first" if k not in last else "back" if k not in prev
                  else "changed" if v != last[k] else None)
            last[k] = v
            if ev:
                events[(month, ev)] += 1
            h = hist[k]
            if not h or h[-1][1] != w:
                h.append((r, w))
            p = pm.get(k)
            result = "no PUDL record" if p is None else "agree"
            if p is not None and not rv.match(w, p[0]):
                earlier = [x for rr, x in recs[k] if rr < p[1]]
                kind = rv.classify({"w": w, "p": p[0], "sim": sim},
                                   [x for rr, x in recs[k] if rr > r], earlier)
                at = where_of(h, p)
                kinds[(yr, kind)] += 1
                where[(yr, kind, at)] += 1
                if kind == "held_before":
                    simv = "equals workbook" if rv.match(sim, w) else "stale elsewhere"
                    strict = any(hs.sim_match(w, x) for x in earlier)
                    held[(yr, simv, strict, at)] += 1
                    plants[k.split("/", 1)[0]] += 1
                result = kind
            if k in want:
                rows[k].append({"month": month, "sheet": sheets[k], "workbook": rv.cell(w),
                                "simulated": rv.cell(sim), "seen_before": was_held,
                                "pudl": rv.cell(p[0]) if p else "",
                                "pudl_reported": es.month_str(p[1]) if p else "",
                                "result": result})
        for k in sorted(prev - set(wm)):
            events[(month, "left")] += 1
            hist[k].append((r, None))
            if k in want:
                rows[k].append({"month": month, "sheet": "", "workbook": "", "simulated": "",
                                "seen_before": False, "pudl": "", "pudl_reported": "",
                                "result": "left the workbook"})
        prev = set(wm)
    years = sorted({y for y, _ in kinds})
    return {
        "kinds": [dict({"year": y}, **{k: kinds[(y, k)] for k in KINDS}) for y in years],
        "where": [{"year": y, "kind": k, "at": a, "n": where[(y, k, a)]}
                  for y in years for k in KINDS for a in WHERE if where[(y, k, a)]],
        "held": [{"year": y, "simulated": s, "strict": st, "at": a, "n": c}
                 for (y, s, st, a), c in sorted(held.items(), key=lambda x: (x[0][0], -x[1], str(x[0])))],
        "plants": [{"plant": p, "n": c} for p, c in sorted(plants.items(), key=lambda x: (-x[1], x[0]))[:TOP]],
        "events": [dict({"month": m}, **{e: events[(m, e)] for e in EVENTS})
                   for m in sorted({m for m, _ in events})],
        "keys": {k: rows[k] for k in keys}}


def render(result):
    md = ["# heldtrace %s: where the twenty-ninth test's misses come from" % __version__, "",
          "Descriptive follow-up to docs/history-revert.md; no prediction is tested. MV2 of Munim, "
          "Inc. (made with AI agents).", ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    res = result["result"]
    md += ["PUDL file: %s bytes, file time %s, latest report %s. Workbook months read: %d." % (
        result["pudl"]["bytes"], result["pudl"]["mtime"], result["pudl"]["max_report"],
        result["months_read"]), "",
           "## Disagreements by kind (should equal history-v1's counts)", "",
           "| year | %s |" % " | ".join(KINDS), "|---|" + "---|" * len(KINDS)]
    for y in res["kinds"]:
        md.append("| %d | %s |" % (y["year"], " | ".join(str(y[k]) for k in KINDS)))
    md += ["", "## What the workbook showed in the month PUDL's record in force was reported", "",
           "| year | kind | workbook then | generator-months |", "|---|---|---|---|"]
    for x in res["where"]:
        md.append("| %d | %s | %s | %d |" % (x["year"], x["kind"], x["at"], x["n"]))
    md += ["", "## \"Held before\": the simulation's value and the earlier PUDL record", "",
           "strict: an earlier PUDL record equals the workbook's value also when a missing field "
           "equals only a missing field.", "",
           "| year | simulation | strict | workbook then | generator-months |", "|---|---|---|---|---|"]
    for x in res["held"]:
        md.append("| %d | %s | %s | %s | %d |" % (x["year"], x["simulated"], x["strict"], x["at"], x["n"]))
    md += ["", "## Plants with most \"held before\" generator-months (top %d)" % TOP, "",
           "| plant | generator-months |", "|---|---|"]
    for x in res["plants"]:
        md.append("| %s | %d |" % (x["plant"], x["n"]))
    md += ["", "## Rebuilt changelog rows by month", "",
           "| month | %s |" % " | ".join(EVENTS), "|---|" + "---|" * len(EVENTS)]
    for x in res["events"]:
        md.append("| %s | %s |" % (x["month"], " | ".join(str(x[e]) for e in EVENTS)))
    for k, rows in res["keys"].items():
        md += ["", "### %s" % k, "",
               "seen before: the workbook's value equals a value the simulation took in earlier "
               "(the value in force included).", "",
               "| month | sheet | workbook | simulation | seen before | PUDL in force | reported | result |",
               "|---|---|---|---|---|---|---|---|"]
        for x in rows:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                x["month"], x["sheet"], x["workbook"], x["simulated"], x["seen_before"], x["pudl"],
                x["pudl_reported"], x["result"]))
        if not rows:
            md.append("| not in any workbook | | | | | | | |")
    md += ["", "PUDL's full rows for these generators: heldtrace_pudl_rows.csv."]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--key", action="append", default=None, help="plant/generator (repeatable)")
    args = ap.parse_args(argv)
    keys = tuple(args.key or KEYS)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    result = {"version": __version__, "history": hs.__version__, "started_at": now(), "keys": keys}
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = hs.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    st = os.stat(path)
    result["pudl"] = {"bytes": st.st_size,
                      "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                      "max_report": es.month_str(df["report_m"].max())}
    zips, paths = [], []
    for year in ly.YEARS:
        p, z = ly.get_zip(year, args.data_dir, ly.ZIP_MD5.get(year), None)
        z.update(year=year, ok=p is not None)
        zips.append(z)
        if p is not None:
            paths.append((year, p))
    result["zips"] = zips
    if len(paths) != len(ly.YEARS):
        result["error"] = "zips with a listed md5: %d of %d" % (len(paths), len(ly.YEARS))
    else:
        months = []
        result["result"] = trace(df, hs.workbooks(paths, months), keys)
        result["months_read"] = len(months)
        result["months_unreadable"] = [m["month"] for m in months if not m["readable"]]
        full = pd.read_parquet(path)
        key = full["plant_id_eia"].astype(str) + "/" + full["generator_id"].astype(str)
        full[key.isin(keys)].assign(key=key[key.isin(keys)]).sort_values(
            ["key", "report_date"], kind="mergesort").to_csv(
            os.path.join(args.out_dir, "heldtrace_pudl_rows.csv"), index=False)
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "heldtrace.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "heldtrace.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
