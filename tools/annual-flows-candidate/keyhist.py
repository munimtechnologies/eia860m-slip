"""keyhist: EIA-860M's 2026 workbooks, month by month, against PUDL's changelog.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Job wbcheck-v2 found that PUDL's archived copies of EIA's July and August 2026 workbooks are the
files EIA serves today (same md5), yet the watchlist built from the workbook lists a change for
13 (July) and 11 (August) generators that PUDL's own edition does not; 8 keys differ in both
months with the same workbook values. This probe asks where such a disagreement starts and
whether PUDL's record follows an earlier month's workbook. It reads every 2026 monthly workbook
from PUDL's own archive copy (Zenodo record 22995197, eia860m-2026.zip, md5 checked) with
workbook.py's reader, compares each month with PUDL's records in force at that month
(xlsxprobe.compare), and shows each given generator month by month in both sources.

Descriptive only: no prediction is tested.

    python keyhist.py --data-dir /data --out-dir /out --key 68514/MC201 [--key ...]
"""

import argparse
import io
import json
import os
import time
import zipfile

import pandas as pd

import eia860m_slip as es
import rawcheck as rc
import watchlist as wl
import workbook as wk
import xlsxprobe as xp

__version__ = "0.1.0"
RECORD = "22995197"   # PUDL Raw EIA Form 860M, version 50.0.0, published 27 September 2026
ZIP = "eia860m-2026.zip"
ZIP_MD5 = "380a9824a20be96d182fea793c299e91"
YEAR = 2026
SKIP = ("_pr",)       # unlike workbook.py, the Canceled or Postponed sheet is read, so a
                      # generator that left the other sheets can be found there
MW_TOL = 0.05


def get_zip(data_dir):
    """PUDL's archive copy of eia860m-2026.zip -> (bytes or None, info). Kept in data_dir; a
    kept or downloaded copy is used only when its md5 is Zenodo's."""
    path = os.path.join(data_dir, "zenodo-%s-%s" % (RECORD, ZIP))
    info = {"path": path, "tried": [], "cached": False}
    if os.path.exists(path):
        with open(path, "rb") as fh:
            data = fh.read()
        if rc.md5(data) == ZIP_MD5:
            info["cached"] = True
            return data, info
    for url in rc.file_urls(RECORD, ZIP):
        data, err = rc.download(url)
        if data is not None and rc.md5(data) != ZIP_MD5:
            data, err = None, "md5 %s is not Zenodo's" % rc.md5(data)
        info["tried"].append({"url": url, "error": err})
        if data is not None:
            with open(path, "wb") as fh:
                fh.write(data)
            return data, info
    return None, info


def read_month(zf, month, skip=SKIP):
    """One month's workbook from the archive -> (workbook.py's records or None, info)."""
    member, hits = rc.member_for(zf.namelist(), month)
    if member is None:
        return None, {"member": None, "hits": hits}
    sheets = pd.read_excel(io.BytesIO(zf.read(member)), sheet_name=None, header=None, dtype=object)
    wb, sheet_info, dup = wk.workbook_frame(sheets, skip)
    return wb, {"member": member, "sheets": sheet_info, "duplicate_keys": dup}


def is_canceled(sheet):
    return sheet is not None and "cancel" in str(sheet).lower()


def for_compare(wb):
    """A month's records as xlsxprobe.compare reads them: the sheets workbook.py's self-check
    reads (no Canceled or Postponed sheet), technology under xlsxprobe's column name."""
    keep = [not is_canceled(s) for s in wb["sheet"]]
    return wb[keep].rename(columns={"technology_description": "technology"})


def row_of(wb, key):
    """A key's workbook row -> {sheet, status, planned, mw}, or None when it is not there."""
    hit = wb[wb["key"] == key]
    if hit.empty:
        return None
    x = hit.iloc[0]
    return {"sheet": x["sheet"], "status": x["status"], "planned": es.month_str(x["planned_m"]),
            "mw": xp._plain(x["capacity_mw"])}


def pudl_of(df, key, r):
    """A key's PUDL record in force at report month r -> {report, status, planned, mw}, or
    None when none is in force."""
    s = es.snapshot(df[df["key"] == key], r)
    if s.empty:
        return None
    x = s.iloc[-1]
    return {"report": es.month_str(x["report_m"]), "status": x["status"],
            "planned": es.month_str(x["planned_m"]), "mw": xp._plain(x["capacity_mw"])}


def same(w, p):
    """Do a workbook row and a PUDL record agree? A row on the Canceled or Postponed sheet
    counts as absent (PUDL's changelog has no such rows); planned months are compared only
    for a row on a Planned sheet; MW within MW_TOL."""
    if w is not None and is_canceled(w["sheet"]):
        w = None
    if w is None or p is None:
        return w is None and p is None
    if w["status"] != p["status"]:
        return False
    if "plan" in str(w["sheet"]).lower() and w["planned"] != p["planned"]:
        return False
    return abs(float(w["mw"] or 0.0) - float(p["mw"] or 0.0)) <= MW_TOL


def history(key, frames, df, months):
    """A key month by month: its workbook row, its PUDL record in force, whether they agree,
    and for a month where they do not, the earlier months whose workbook row PUDL's record
    matches."""
    rows = []
    for m in months:
        wb = frames.get(m)
        w = row_of(wb, key) if wb is not None else None
        p = pudl_of(df, key, wl.parse_month(m))
        rows.append({"month": m, "workbook": w, "pudl": p, "same": same(w, p)})
    for i, r in enumerate(rows):
        r["pudl_as_workbook_of"] = [] if r["same"] or r["pudl"] is None else [
            x["month"] for x in rows[:i] if x["workbook"] is not None and same(x["workbook"], r["pudl"])]
    first = next((r["month"] for r in rows if not r["same"]), None)
    return {"key": key, "first_differs": first,
            "months_differ": sum(1 for r in rows if not r["same"]), "months": rows}


def _cell(v, pudl=False):
    if v is None:
        return ""
    text = "%s, %s, %s MW" % (v["status"], v["planned"], v["mw"])
    return ("%s (from %s)" % (text, v["report"])) if pudl else ("%s: %s" % (v["sheet"], text))


def render(result):
    md = ["# keyhist %s: EIA-860M's 2026 workbooks against PUDL's changelog" % __version__, "",
          "Descriptive probe, no prediction tested. MV2 of Munim, Inc. (made with AI agents).", "",
          "PUDL file: %s, latest report %s. Workbooks from Zenodo record %s, %s (md5 %s; %s)." % (
              result["pudl_source"], result["pudl_max"], RECORD, ZIP, ZIP_MD5,
              "kept copy" if result["zip"].get("cached") else "downloaded"), ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    md += ["## Each month: workbook against PUDL's records in force", "",
           "| month | workbook keys | PUDL keys | both | workbook only | PUDL only | status agree "
           "| planned month agree | capacity agree |", "|---|---|---|---|---|---|---|---|---|"]
    for m in result["months"]:
        c = m.get("compare")
        if not c:
            md.append("| %s | not read | | | | | | | |" % m["month"])
            continue
        f = c["fields"]
        md.append("| %s | %d | %d | %d | %d | %d | %s | %s | %s |" % (
            m["month"], c["workbook_keys"], c["pudl_keys"], c["both"], c["workbook_only"],
            c["pudl_only"], *("%d of %d" % (f[k]["agree"], f[k]["compared"])
                              for k in ("status", "planned_month", "capacity"))))
    md += ["", "## Given generators, month by month", "",
           "| key | first month that differs | months that differ |", "|---|---|---|"]
    for h in result["keys"]:
        md.append("| %s | %s | %d of %d |" % (h["key"], h["first_differs"] or "none",
                                              h["months_differ"], len(h["months"])))
    for h in result["keys"]:
        md += ["", "### %s" % h["key"], "",
               "| month | workbook (sheet: status, planned, MW) | PUDL in force | same | PUDL "
               "equals the workbook of |", "|---|---|---|---|---|"]
        for r in h["months"]:
            md.append("| %s | %s | %s | %s | %s |" % (
                r["month"], _cell(r["workbook"]), _cell(r["pudl"], True), r["same"],
                ", ".join(r["pudl_as_workbook_of"])))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--key", action="append", default=None, help="plant/generator (repeatable)")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    last_m = int(df["report_m"].max())
    months = [m for m in ("%d-%02d" % (YEAR, k) for k in range(1, 13))
              if wl.parse_month(m) <= last_m]
    data, zinfo = get_zip(args.data_dir)
    result = {"version": __version__, "workbook": wk.__version__, "rawcheck": rc.__version__,
              "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "pudl_source": os.path.basename(path), "pudl_max": es.month_str(last_m),
              "zip": zinfo, "months": [], "keys": []}
    if data is None:
        result["error"] = "archive copy not downloaded"
    else:
        zf = zipfile.ZipFile(io.BytesIO(data))
        result["zip"]["members"] = sorted(zf.namelist())
        frames = {}
        for m in months:
            wb, info = read_month(zf, m)
            frames[m] = wb
            entry = dict(month=m, **info)
            if wb is not None:
                entry["compare"] = xp.compare(for_compare(wb), xp.pudl_records(df, wl.parse_month(m)))
            result["months"].append(entry)
        result["keys"] = [history(k, frames, df, months) for k in args.key or []]
    with open(os.path.join(args.out_dir, "keyhist.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "keyhist.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
