"""workbook: an EIA-860M watchlist edition from EIA's own workbook, on EIA's release day.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

watchlist.py reads Catalyst Cooperative's PUDL changelog, which takes in a new EIA-860M month
some weeks after EIA publishes its workbook. Here PUDL's records through report r - 1 are
extended with report r read from EIA's workbook: every generator in the workbook gets a record
reported in r, and a generator in force in r - 1 that is not in the workbook ends at r - 1.
watchlist 0.1.0's own functions then build the edition for report r.

Self-check (--check YYYY-MM, a month PUDL already holds): the edition built from PUDL through
the month before plus that month's workbook is compared generator by generator with the edition
built from PUDL alone. Set before the first run: the workbook route is usable when at least
0.98 of the generators listed in either edition have the same change in both.

0.1.1 (after job xlsxprobe-v3, whose August self-check gave 0.9565, every difference a row the
workbook route listed and PUDL's edition did not): generator ids are keyed as PUDL keys them
(a whole-number id loses its leading zeros, '0011' -> '11'; a missing id reads 'nan'), the
Puerto Rico sheets (*_PR) are left out as PUDL has none, --check can be given more than once,
and each self-check lists every differing generator's PUDL records and workbook row. These
changes were read off August's differences, so August's self-check is no longer a fresh test;
the 0.98 threshold is unchanged.

    python workbook.py --data-dir /data --out-dir /out --check 2026-08 --check 2026-07 \
        [--report 2026-09]
"""

import argparse
import collections
import json
import os
import re

import pandas as pd

import eia860m_slip as es
import stagemoves as sm
import watchlist as wl
import xlsxprobe as xp

__version__ = "0.1.1"

SKIP = ("cancel", "_pr")  # sheets left out: PUDL's changelog has no CN or IP rows and no
                          # Puerto Rico sheets (xlsxprobe-v3: all 243 *_PR rows workbook-only)
USABLE = 0.98
SAMPLE = 60
MW_TOL = 0.05
NEW_COLS = ("key", "plant_id_eia", "generator_id", "plant_name_eia", "state",
            "technology_description", "status", "capacity_mw", "planned_m")


def _clean(v):
    """A cell as stripped text, None when blank or missing."""
    if v is None or v != v:
        return None
    text = str(v).strip()
    return text or None


def gen_id(value):
    """A generator id as PUDL keys it: xlsxprobe.norm_id, then a whole-number id without its
    leading zeros ('0011' -> '11', '06' -> '6', '0' stays '0'), and a missing id as 'nan'."""
    text = xp.norm_id(value)
    if not text:
        return "nan"
    return re.sub(r"^0+(?=\d)", "", text) if text.isdigit() else text


def _pick(cols, *choices):
    """The first column found by xlsxprobe.find_col for each (needles, exclude) choice in turn."""
    for needles, exclude in choices:
        c = xp.find_col(cols, *needles, exclude=exclude)
        if c is not None:
            return c
    return None


def sheet_rows(name, raw):
    """One sheet read with header=None -> its generators in PUDL's column names, or None when
    the sheet has no plant and generator ids. A row without a generator id is keyed
    '<plant>/nan', as PUDL keys it."""
    df, _ = xp.sheet_frame(raw)
    if df is None:
        return None
    cols = list(df.columns)
    blank = pd.Series([None] * len(df), index=df.index, dtype=object)

    def col(c):
        return blank if c is None else df[c]

    pid = df[xp.find_col(cols, "plant id")].map(xp.norm_id)
    gid = df[xp.find_col(cols, "generator id")].map(gen_id)
    c_cap = _pick(cols, (("nameplate capacity",), ()), (("capacity",), ()))
    c_pm = _pick(cols, (("planned", "operation", "month"), ()),
                 (("planned", "month"), ("retire",)))
    c_py = _pick(cols, (("planned", "operation", "year"), ()),
                 (("planned", "year"), ("retire",)))
    planned = [xp.month_index(y, m) for y, m in zip(col(c_py), col(c_pm))]
    out = pd.DataFrame({
        "sheet": str(name),
        "key": pid + "/" + gid,
        "plant_id_eia": pid.astype(int),
        "generator_id": gid,
        "plant_name_eia": col(xp.find_col(cols, "plant name")).map(_clean),
        "state": col(xp.find_col(cols, "state")).map(_clean),
        "technology_description": col(xp.find_col(cols, "technology")).map(_clean),
        "status": col(xp.find_col(cols, "status")).map(xp.status_code),
        "capacity_mw": pd.to_numeric(col(c_cap), errors="coerce").fillna(0.0),
        "planned_m": pd.Series(planned, index=df.index, dtype=float),
    })
    return out.reset_index(drop=True)


def workbook_frame(sheets, skip=SKIP):
    """All generator sheets except those whose name contains a skip word -> (records, rows read
    per sheet, duplicate keys). A key on more than one row keeps its first row (sheets in
    workbook order)."""
    parts, info = [], {}
    for name, raw in sheets.items():
        if any(w in str(name).lower() for w in skip):
            info[str(name)] = "skipped"
            continue
        rec = sheet_rows(name, raw)
        if rec is None:
            info[str(name)] = "no generator ids"
            continue
        info[str(name)] = int(len(rec))
        parts.append(rec)
    if not parts:
        return pd.DataFrame(columns=["sheet"] + list(NEW_COLS)), info, 0
    wb = pd.concat(parts, ignore_index=True)
    dup = int(wb["key"].duplicated().sum())
    return wb.drop_duplicates("key", keep="first").reset_index(drop=True), info, dup


def extend(df, wb, r):
    """Prepared PUDL records (es.prepare) cut to reports before r, each record's last month in
    force capped at r - 1, plus one record reported in r (and in force in r) for every workbook
    generator. A generator in force in r - 1 that is not in the workbook so ends at r - 1."""
    old = df[df["report_m"] < r].copy()
    old["until_m"] = old["until_m"].clip(upper=r - 1)
    new = pd.DataFrame({c: wb[c].to_numpy() for c in NEW_COLS})
    new["report_m"] = float(r)
    new["until_m"] = float(r)
    new["group"] = [es.tech_group(x) for x in new["technology_description"]]
    return pd.concat([old, new], ignore_index=True)


def edition(df, r, source):
    """watchlist 0.1.0's rows, tables and meta for report r of prepared records df, as
    watchlist.main builds them."""
    lo = max(sm.START_M, r - 1 - wl.HISTORY)
    t = sm.timeline(df, lo, r)
    s, left = sm.steps(t, r)
    a, b = wl.records(es.snapshot(df, r - 1)), wl.records(es.snapshot(df, r))
    rows = wl.changes(a, b, wl.backward_before(s, lo, r))
    pairs = wl.flag_rekeys(rows)
    hist = wl.history(t, s, left, lo, r)
    part = wl.partition(a, b)
    res = {"summary": wl.summary(rows, hist),
           "top_backward": [wl._out(x) for x in wl.top(rows, ("backward",))],
           "top_exits": [wl._out(x) for x in wl.top(rows, ("exit_other", "left"))],
           "top_delayed": [wl._out(x) for x in wl.top(rows, ("delayed",))],
           "top_new": [wl._out(x) for x in wl.top(rows, ("new",))],
           "outcomes": sm.outcomes(s[s["m"] < r - 1]),
           "partition": {k: {"n": v["n"], "mw": round(v["mw"], 1)} for k, v in part.items()},
           "checks": wl.checks(rows, part, a, s, left, r)}
    meta = {"version": wl.__version__, "stagemoves": sm.__version__,
            "eia860m_slip": es.__version__, "workbook": __version__, "source": source,
            "report": es.month_str(r), "previous": es.month_str(r - 1),
            "report_max": es.month_str(r), "pairs": len(hist),
            "history_from": es.month_str(lo), "history_to": es.month_str(r - 1),
            "outcomes_to": es.month_str(r - 12), "rows": len(rows), "rekey_pairs": pairs}
    return rows, res, meta


def compare_editions(ref, got):
    """Generator-by-generator agreement of two editions' rows (ref: PUDL alone; got: workbook
    route). A generator missing from one edition reads 'none' there."""
    a = {x["key"]: x for x in ref}
    b = {x["key"]: x for x in got}
    keys = sorted(set(a) | set(b))
    ca = {k: a[k]["change"] if k in a else "none" for k in keys}
    cb = {k: b[k]["change"] if k in b else "none" for k in keys}
    same = [k for k in keys if ca[k] == cb[k]]
    mw = [k for k in same if abs(a[k]["mw"] - b[k]["mw"]) > MW_TOL]
    diff = collections.Counter("%s -> %s" % (ca[k], cb[k]) for k in keys if ca[k] != cb[k])
    return {"pudl_rows": len(a), "workbook_rows": len(b), "union": len(keys),
            "same_change": len(same),
            "same_share": round(len(same) / len(keys), 4) if keys else None,
            "usable": bool(keys) and len(same) >= USABLE * len(keys),
            # Added in 0.1.1, after xlsxprobe-v3: the share of PUDL's own rows the workbook
            # route gives the same change (descriptive; not the pre-set usability test).
            "pudl_rows_same_share": round(len(same) / len(a), 4) if a else None,
            "same_change_mw_differs": len(mw),
            "by_change": {c: [sum(1 for v in a.values() if v["change"] == c),
                              sum(1 for v in b.values() if v["change"] == c)]
                          for c in wl.CHANGES},
            "differences": dict(sorted(diff.items(), key=lambda kv: (-kv[1], kv[0]))),
            "difference_sample": [{"key": k, "pudl": ca[k], "workbook": cb[k]}
                                  for k in keys if ca[k] != cb[k]][:SAMPLE],
            "mw_sample": [{"key": k, "pudl": round(a[k]["mw"], 3), "workbook": round(b[k]["mw"], 3)}
                          for k in mw[:SAMPLE]]}


def detail(df, wb, keys, r):
    """Each key's PUDL records reported r - 3 to r (prepared, before extend) and its row in
    report r's workbook: tells a key mismatch from a value disagreement."""
    w = wb.drop_duplicates("key").set_index("key")
    out = []
    for k in keys:
        recs = df[(df["key"] == k) & (df["report_m"] >= r - 3) & (df["report_m"] <= r)]
        recs = recs.sort_values("report_m", kind="mergesort")
        pudl = [{"report": es.month_str(x.report_m), "valid_until": es.month_str(x.valid_m),
                 "until": es.month_str(x.until_m), "status": x.status,
                 "planned": es.month_str(x.planned_m), "mw": round(float(x.capacity_mw), 3)}
                for x in recs.itertuples()]
        row = None
        if k in w.index:
            x = w.loc[k]
            row = {"sheet": x.get("sheet"), "status": x["status"],
                   "planned": es.month_str(x["planned_m"]),
                   "mw": round(float(x["capacity_mw"]), 3)}
        out.append({"key": k, "pudl": pudl, "workbook": row})
    return out


def write(out_dir, tag, rows, res, meta):
    """watchlist's CSV, JSON and Markdown for one edition, file names ending in tag."""
    out = pd.DataFrame([wl._out(x) for x in rows], columns=wl.ROW_COLS)
    for c in ("plant_id_eia", "shift_months"):
        out[c] = out[c].astype("Int64")
    out.to_csv(os.path.join(out_dir, "watchlist_%s.csv" % tag), index=False)
    with open(os.path.join(out_dir, "watchlist_%s.json" % tag), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    wl.write_md(os.path.join(out_dir, "watchlist_%s.md" % tag), meta, res)


def run_month(df, last_m, month, out_dir, skip, check):
    """One workbook month: fetch, read, extend PUDL, build the edition and (check) compare it
    with PUDL's own edition of that month."""
    r = wl.parse_month(month)
    entry = {"report": month, "mode": "check" if check else "report"}
    need = r if check else r - 1
    if need > last_m:
        entry["error"] = "PUDL does not hold report %s" % es.month_str(need)
        return entry
    url, errors = xp.fetch(xp.workbook_urls(month), "workbook_%s.xlsx" % month)
    entry["fetch_errors"] = errors
    if url is None:
        entry["error"] = "workbook not downloaded (not released yet?)"
        return entry
    sheets = pd.read_excel("workbook_%s.xlsx" % month, sheet_name=None, header=None, dtype=object)
    wb, info, dup = workbook_frame(sheets, skip)
    entry.update({"url": url, "sheets": info, "workbook_keys": int(len(wb)),
                  "duplicate_keys": dup,
                  "statuses": {k: int(v) for k, v in wb["status"].value_counts().items()}})
    source = "PUDL %s through %s + EIA workbook %s" % (
        "changelog", es.month_str(r - 1), url.rsplit("/", 1)[-1])
    rows, res, meta = edition(extend(df, wb, r), r, source)
    write(out_dir, month + "_workbook", rows, res, meta)
    entry.update({"rows": len(rows), "rekey_pairs": meta["rekey_pairs"],
                  "checks": res["checks"], "summary": res["summary"]})
    if check:
        ref, _, _ = edition(df, r, "PUDL")
        entry["self_check"] = compare_editions(ref, rows)
        keys = [d["key"] for d in entry["self_check"]["difference_sample"]]
        entry["difference_detail"] = detail(df, wb, keys, r)
    return entry


def render(result):
    """A short Markdown summary of each month's self-check and its differing generators."""
    md = ["# EIA-860M workbook route, self-check (workbook %s)" % __version__, "",
          "MV2 of Munim, Inc. (made with AI agents). PUDL %s, latest report %s. Usable when "
          "same_share >= %s (set before the first run)." % (
              result["pudl_source"], result["pudl_max"], result["usable_threshold"]), ""]
    for m in result["months"]:
        md += ["## %s (%s)" % (m["report"], m["mode"]), ""]
        if m.get("error"):
            md += ["Not built: %s" % m["error"], ""]
            continue
        md += ["Sheets: %s" % json.dumps(m["sheets"]), ""]
        c = m.get("self_check")
        if not c:
            md += ["Edition rows: %d (no self-check in report mode)." % m["rows"], ""]
            continue
        md += ["PUDL rows %d, workbook rows %d, union %d, same change %d: same_share %s, "
               "usable %s; share of PUDL's rows reproduced %s." % (
                   c["pudl_rows"], c["workbook_rows"], c["union"], c["same_change"],
                   c["same_share"], c["usable"], c["pudl_rows_same_share"]), "",
               "Differences: %s" % json.dumps(c["differences"]), "",
               "| key | pudl | workbook | PUDL records (report: status, planned, until) "
               "| workbook row (sheet: status, planned) |", "|---|---|---|---|---|"]
        changes = {d["key"]: d for d in c["difference_sample"]}
        for d in m.get("difference_detail", []):
            recs = "; ".join("%s: %s, %s, %s" % (x["report"], x["status"], x["planned"],
                                                 x["until"]) for x in d["pudl"])
            w = d["workbook"]
            row = "%s: %s, %s" % (w["sheet"], w["status"], w["planned"]) if w else ""
            md.append("| %s | %s | %s | %s | %s |" % (d["key"], changes[d["key"]]["pudl"],
                                                      changes[d["key"]]["workbook"], recs, row))
        md.append("")
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--check", action="append", default=None,
                    help="YYYY-MM that PUDL already holds (repeatable)")
    ap.add_argument("--report", default=None, help="YYYY-MM after PUDL's last report")
    ap.add_argument("--skip", action="append", default=None, help="sheet-name word to leave out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    last_m = int(df["report_m"].max())
    skip = tuple(args.skip) if args.skip else SKIP
    result = {"version": __version__, "watchlist": wl.__version__,
              "pudl_source": os.path.basename(path), "pudl_max": es.month_str(last_m),
              "skip": list(skip), "usable_threshold": USABLE, "months": []}
    todo = [(m, True) for m in args.check or []] + ([(args.report, False)] if args.report else [])
    for month, check in todo:
        result["months"].append(run_month(df, last_m, month, args.out_dir, skip, check))
    with open(os.path.join(args.out_dir, "workbook.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "workbook.md"), "w", encoding="utf-8") as fh:
        fh.write(render(result))
    print(json.dumps(result, indent=1, default=str))
    return result


if __name__ == "__main__":
    main()
