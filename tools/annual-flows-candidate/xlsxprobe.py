"""xlsxprobe: does EIA's own monthly EIA-860M workbook give the same generators as PUDL?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The EIA-860M watchlist (watchlist.py) reads Catalyst Cooperative's PUDL changelog, which takes
in a new EIA-860M month some days or weeks after EIA releases it. EIA's own workbook
(eia.gov/electricity/data/eia860m/) is out on release day. Before a watchlist edition is built
from the workbook, this probe measures how closely a workbook month matches PUDL's records in
force for the same report month: which sheets and columns the workbook has, which generator
keys (plant id / generator id) are in one source and not the other, and for keys in both how
often capacity, status code, planned operating month, technology and state agree.

Descriptive only: no prediction is tested. The probe checks itself (PUDL holds the month, the
workbook has a sheet with plant and generator ids, both snapshots are non-empty).

0.1.1: a download counts only if it is an xlsx file (a zip archive); anything else (an HTML
page, say) is recorded with its HTTP status, headers and first bytes, and the next URL is
tried. A workbook that cannot be read is recorded, not raised.

    python xlsxprobe.py --data-dir /data --out-dir /out --report 2026-08 --report 2026-07
"""

import argparse
import gzip
import json
import os
import re
import urllib.request

import pandas as pd

import eia860m_slip as es

__version__ = "0.1.1"

BASE = "https://www.eia.gov/electricity/data/eia860m/"
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december")
AGENT = "mv2-munim-eia860m-probe/0.1 (MV2 of Munim, Inc.; mv2@munimtech.com)"
ACCEPT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*"
XLSX_MAGIC = b"PK\x03\x04"   # an xlsx file is a zip archive
GZIP_MAGIC = b"\x1f\x8b"
HEAD_BYTES = 160
MW_TOL = 0.05
SAMPLE = 20
FIELDS = ("capacity", "status", "planned_month", "technology", "state")


def workbook_urls(report):
    """Current and archive URLs of EIA's workbook for report month YYYY-MM."""
    year, month = report.split("-")
    name = "%s_generator%s.xlsx" % (MONTHS[int(month) - 1], year)
    return [BASE + "xls/" + name, BASE + "archive/xls/" + name]


def unpack(body):
    """The bytes of a download, gunzipped if the server sent them gzip-compressed."""
    if body[:2] == GZIP_MAGIC:
        try:
            return gzip.decompress(body)
        except (OSError, EOFError):
            return body
    return body


def describe(body, info):
    """One line on a download that is not an xlsx file: status, headers, size, first bytes."""
    return ("not an xlsx file: status %s, final URL %s, Content-Type %s, Content-Encoding %s, "
            "%d bytes, starts %r" % (info.get("status"), info.get("final_url"),
                                     info.get("content_type"), info.get("content_encoding"),
                                     len(body), body[:HEAD_BYTES]))


def fetch(urls, dest):
    """Download the first URL that gives an xlsx file to dest -> (url, errors), or (None,
    errors) when none does. Every failed URL adds one line to errors."""
    errors = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": ACCEPT})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                info = {"status": r.getcode(), "final_url": r.geturl(),
                        "content_type": r.headers.get("Content-Type"),
                        "content_encoding": r.headers.get("Content-Encoding")}
        except Exception as exc:  # report every failed URL, try the next
            errors.append("%s: %s" % (url, exc))
            continue
        body = unpack(body)
        if body[:4] != XLSX_MAGIC:
            errors.append("%s: %s" % (url, describe(body, info)))
            continue
        with open(dest, "wb") as fh:
            fh.write(body)
        return url, errors
    return None, errors


def norm_id(value):
    """Plant or generator id as text: stripped, a trailing '.0' of a whole number removed."""
    if value is None or value != value:
        return ""
    text = str(value).strip()
    return text[:-2] if re.fullmatch(r"\d+\.0", text) else text


def status_code(text):
    """'(V) Under construction, more than 50 percent complete' -> 'V'; plain codes pass."""
    if text is None or text != text:
        return ""
    text = str(text).strip()
    m = re.match(r"\(([A-Za-z]+)\)", text)
    if m:
        return m.group(1).upper()
    return text.upper() if re.fullmatch(r"[A-Za-z]{1,3}", text) else ""


def to_int(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def month_index(year, month):
    """Months since year 0 (as eia860m_slip.months), None if either part is missing."""
    y, m = to_int(year), to_int(month)
    if y is None or m is None or not 1 <= m <= 12:
        return None
    return y * 12 + m - 1


def find_header(rows, limit=15):
    """Index of the first row with cells 'Plant ID' and 'Generator ID', else None."""
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip().lower() for c in row if c is not None and c == c}
        if "plant id" in cells and "generator id" in cells:
            return i
    return None


def find_col(columns, *needles, exclude=()):
    """First column whose lower-case name contains every needle and no excluded word."""
    for c in columns:
        low = str(c).strip().lower()
        if all(n in low for n in needles) and not any(x in low for x in exclude):
            return c
    return None


def sheet_frame(raw):
    """A sheet read with header=None -> (frame with named columns, header row) or (None, None).

    Rows whose plant id is not a whole number (titles, notes, totals) are dropped."""
    rows = raw.values.tolist()
    h = find_header(rows)
    if h is None:
        return None, None
    cols = [str(c).strip() if c is not None and c == c else "col%d" % j
            for j, c in enumerate(rows[h])]
    df = pd.DataFrame(rows[h + 1:], columns=cols)
    pid = df[find_col(cols, "plant id")].map(norm_id)
    return df[pid.str.fullmatch(r"\d+")].reset_index(drop=True), h


def workbook_records(sheets):
    """All sheets with plant and generator ids -> one frame of normalised fields, and a
    description of each sheet (header row, columns, rows, MW)."""
    out, info = [], {}
    for name, raw in sheets.items():
        df, h = sheet_frame(raw)
        if df is None:
            info[name] = {"generator_sheet": False, "shape": list(raw.shape)}
            continue
        cols = list(df.columns)
        c_cap = find_col(cols, "nameplate capacity") or find_col(cols, "capacity")
        c_stat = find_col(cols, "status")
        c_pm = (find_col(cols, "planned", "operation", "month")
                or find_col(cols, "planned", "month", exclude=("retire",)))
        c_py = (find_col(cols, "planned", "operation", "year")
                or find_col(cols, "planned", "year", exclude=("retire",)))
        c_tech = find_col(cols, "technology")
        c_state = find_col(cols, "state")
        rec = pd.DataFrame({
            "sheet": name,
            "key": df[find_col(cols, "plant id")].map(norm_id) + "/"
            + df[find_col(cols, "generator id")].map(norm_id),
            "capacity_mw": pd.to_numeric(df[c_cap], errors="coerce") if c_cap else float("nan"),
            "status": df[c_stat].map(status_code) if c_stat else "",
            "planned_m": ([month_index(y, m) for y, m in zip(df[c_py], df[c_pm])]
                          if c_pm and c_py else None),
            "technology": df[c_tech].astype(str).str.strip() if c_tech else "",
            "state": df[c_state].astype(str).str.strip() if c_state else "",
        })
        info[name] = {"generator_sheet": True, "header_row": h, "columns": cols,
                      "rows": len(rec), "mw": round(float(rec["capacity_mw"].sum()), 1),
                      "used": {"capacity": c_cap, "status": c_stat, "planned_month": c_pm,
                               "planned_year": c_py, "technology": c_tech, "state": c_state},
                      "status_counts": {k: int(v) for k, v in
                                        rec["status"].value_counts().head(25).items()}}
        out.append(rec)
    recs = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    return recs, info


def pudl_records(df, r):
    """PUDL records in force at report month r, in the workbook's normalised fields."""
    s = es.snapshot(df, r)
    return pd.DataFrame({
        "key": s["key"].to_numpy(),
        "capacity_mw": s["capacity_mw"].to_numpy(),
        "status": s["status"].to_numpy(),
        "planned_m": s["planned_m"].to_numpy(),
        "technology": s["technology_description"].astype(str).str.strip().to_numpy(),
        "state": s["state"].astype(str).str.strip().to_numpy(),
    })


def agree(field, a, b):
    """Do a workbook value a and a PUDL value b agree? None when the field cannot be
    compared (missing on either side, or a planned month on a non-planned record)."""
    if field == "capacity":
        if a != a or b != b:
            return None
        return abs(float(a) - float(b)) <= MW_TOL
    if field == "planned_month":
        if a is None or a != a or b is None or b != b:
            return None
        return int(a) == int(b)
    a, b = ("" if a != a else str(a)), ("" if b != b else str(b))
    if not a or not b or a.lower() == "nan" or b.lower() == "nan":
        return None
    return a == b


def compare(wb, pu):
    """Key overlap and field agreement between a workbook month and PUDL's snapshot."""
    dup = int(wb["key"].duplicated().sum())
    w = wb.drop_duplicates("key", keep="first").set_index("key")
    p = pu.drop_duplicates("key", keep="first").set_index("key")
    both = w.index.intersection(p.index)
    only_w, only_p = w.index.difference(p.index), p.index.difference(w.index)
    res = {"workbook_keys": int(len(w)), "workbook_duplicate_keys": dup,
           "pudl_keys": int(len(p)), "both": int(len(both)),
           "workbook_only": int(len(only_w)), "pudl_only": int(len(only_p)),
           "workbook_only_by_sheet": {k: int(v) for k, v in
                                      w.loc[only_w, "sheet"].value_counts().items()},
           "workbook_only_mw_by_sheet": {k: round(float(v), 1) for k, v in
                                         w.loc[only_w].groupby("sheet")["capacity_mw"].sum().items()},
           "pudl_only_by_status": {k: int(v) for k, v in
                                   p.loc[only_p, "status"].value_counts().items()},
           "pudl_only_mw": round(float(p.loc[only_p, "capacity_mw"].sum()), 1),
           "sheet_by_pudl_status": {}, "fields": {}, "mismatch_samples": {},
           "workbook_only_sample": [{"key": k, **{c: _plain(w.loc[k, c]) for c in
                                                  ("sheet", "capacity_mw", "status")}}
                                    for k in list(only_w[:SAMPLE])],
           "pudl_only_sample": [{"key": k, **{c: _plain(p.loc[k, c]) for c in
                                              ("capacity_mw", "status", "technology")}}
                                for k in list(only_p[:SAMPLE])]}
    for sheet, g in w.loc[both].groupby("sheet"):
        res["sheet_by_pudl_status"][sheet] = {k: int(v) for k, v in
                                              p.loc[g.index, "status"].value_counts().items()}
    cols = {"capacity": "capacity_mw", "status": "status", "planned_month": "planned_m",
            "technology": "technology", "state": "state"}
    for field in FIELDS:
        c = cols[field]
        n = same = 0
        bad = []
        for k in both:
            a, b = w.at[k, c], p.at[k, c]
            if field == "planned_month" and p.at[k, "status"] not in es.PLANNED:
                continue
            ok = agree(field, a, b)
            if ok is None:
                continue
            n += 1
            if ok:
                same += 1
            elif len(bad) < SAMPLE:
                bad.append({"key": k, "sheet": w.at[k, "sheet"], "workbook": _plain(a),
                            "pudl": _plain(b)})
        res["fields"][field] = {"compared": n, "agree": same,
                                "agree_share": round(same / n, 4) if n else None}
        res["mismatch_samples"][field] = bad
    return res


def _plain(v):
    if v is None or v != v:
        return None
    if hasattr(v, "item"):
        v = v.item()
    return round(v, 3) if isinstance(v, float) else v


def render(result):
    md = ["# EIA-860M workbook against PUDL (xlsxprobe %s)" % __version__, "",
          "Descriptive probe, no prediction tested. MV2 of Munim, Inc. (made with AI agents).",
          "", "PUDL file: %s, reports %s to %s." % (result["pudl_source"], result["pudl_min"],
                                                     result["pudl_max"]), ""]
    for rep in result["reports"]:
        md += ["## Report %s" % rep["report"], ""]
        if rep.get("error"):
            md += ["Not compared: %s" % rep["error"], ""]
            md += ["- %s" % e for e in rep.get("fetch_errors", [])]
            md += [""] if rep.get("fetch_errors") else []
            continue
        md += ["Workbook: %s" % rep["url"], ""]
        md += ["| sheet | header row | rows | MW |", "|---|---|---|---|"]
        for name, s in rep["sheets"].items():
            if s["generator_sheet"]:
                md.append("| %s | %d | %d | %.1f |" % (name, s["header_row"], s["rows"], s["mw"]))
            else:
                md.append("| %s (no generator ids) | | | |" % name)
        c = rep["compare"]
        md += ["", "Keys: workbook %d (duplicates %d), PUDL in force %d, both %d, workbook only "
               "%d, PUDL only %d." % (c["workbook_keys"], c["workbook_duplicate_keys"],
                                      c["pudl_keys"], c["both"], c["workbook_only"],
                                      c["pudl_only"]), "",
               "| field | compared | agree | share |", "|---|---|---|---|"]
        for f in FIELDS:
            x = c["fields"][f]
            md.append("| %s | %d | %d | %s |" % (f, x["compared"], x["agree"], x["agree_share"]))
        md += ["", "Checks: " + ", ".join("%s %s" % (k, "pass" if v else "FAIL")
                                          for k, v in rep["checks"].items()), ""]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--report", action="append", default=None, help="YYYY-MM (repeatable)")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    path = es.find_parquet(args.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    result = {"version": __version__, "eia860m_slip": es.__version__,
              "pudl_source": os.path.basename(path),
              "pudl_min": es.month_str(df["report_m"].min()),
              "pudl_max": es.month_str(df["report_m"].max()), "reports": []}
    for report in args.report or ["2026-08"]:
        rep = {"report": report}
        dest = "workbook_%s.xlsx" % report
        url, errors = fetch(workbook_urls(report), dest)
        rep["fetch_errors"] = errors
        if url is None:
            rep["error"] = "workbook not downloaded"
            result["reports"].append(rep)
            continue
        rep["url"] = url
        rep["bytes"] = os.path.getsize(dest)
        try:
            sheets = pd.read_excel(dest, sheet_name=None, header=None, dtype=object)
        except Exception as exc:  # recorded, not raised: the other months still run
            with open(dest, "rb") as fh:
                head = fh.read(HEAD_BYTES)
            rep["error"] = "workbook not readable: %s (%d bytes, starts %r)" % (
                exc, rep["bytes"], head)
            result["reports"].append(rep)
            continue
        wb, info = workbook_records(sheets)
        rep["sheets"] = info
        r = es.months([report + "-01"])[0]
        pu = pudl_records(df, r)
        rep["checks"] = {"pudl_holds_month": bool((df["report_m"] == r).any()),
                         "workbook_has_generator_sheet": len(wb) > 0,
                         "pudl_snapshot_nonempty": len(pu) > 0}
        if len(wb) and len(pu):
            rep["compare"] = compare(wb, pu)
        else:
            rep["error"] = "an empty snapshot"
        result["reports"].append(rep)
    with open(os.path.join(args.out_dir, "xlsxprobe.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "xlsxprobe.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
