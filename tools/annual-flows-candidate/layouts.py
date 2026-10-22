"""layouts: can workbook.py read every EIA-860M monthly workbook in PUDL's archive, 2015-2026?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The twenty-eighth test found that PUDL's EIA-860M changelog drops a generator's value when it
changes and later comes back, using EIA's 2026 workbooks. The twenty-ninth will rebuild a
consecutive-record changelog from EIA's own monthly workbooks for every year PUDL archives and
compare it with PUDL's changelog. Before its predictions are fixed, this probe checks only that
the reader works on the older layouts. It downloads each eia860m-YYYY.zip of Zenodo record
22995197 (PUDL Raw EIA Form 860M, version 50.0.0), checks it against the md5 on the record page
and in the record's datapackage.json, finds each month's workbook with rawcheck.member_for and
reads every sheet with workbook.py's reader (workbook.sheet_rows). It reports structure and
reader health only: sheet names, header rows, the columns the reader picks, rows and keys,
duplicate keys, and how many rows lack a status code or (Planned sheets) a planned month.

Descriptive only: no prediction is tested, no workbook is compared with PUDL, and nothing the
twenty-ninth test will score is computed. Set before the first run: a workbook is readable when
every sheet the workbook route reads (all but Canceled or Postponed and *_PR) has a header row
(or is not a generator sheet), the reader finds a capacity column, a status column (all but
Retired) and planned month and year columns (Planned), at most 1% of a sheet's rows lack a
status code or planned month, and an Operating sheet has rows.

    python layouts.py --data-dir /data --out-dir /out [--year 2015 ...] \
        [--compare-base URL --minutes 60]
"""

import argparse
import collections
import hashlib
import io
import json
import os
import time
import urllib.request
import zipfile

import pandas as pd

import rawcheck as rc
import workbook as wk
import xlsxprobe as xp

__version__ = "0.1.0"
RECORD = "22995197"   # PUDL Raw EIA Form 860M, version 50.0.0, published 27 September 2026
ZIP_MD5 = {           # as the Zenodo record page lists them (read 22 October 2026)
    2015: "bc6a0c5b0aaefd81f5b4cca847bccff0",
    2016: "3953d510a43dcf661a799c971c1014b0",
    2017: "2443c5384580ddd71c81dfb056916a11",
    2018: "acab1ebfa45b61d7822df1bae8169a0a",
    2019: "b3a075a025dde6962458af9de2f5acd3",
    2020: "c70b432d6fcb8bd8faaf0d32e6571cda",
    2021: "e884f2fdffe9a962fa35bb82f7ea4145",
    2022: "b7ac26d1a77f5731d75d95df3460182b",
    2023: "de66d1e408ef7ca8cca5f7c2d044b792",
    2024: "55592d39081c290b755b36f78e123be2",
    2025: "b597d05e22b8631da27754957d7c9f8c",
    2026: "380a9824a20be96d182fea793c299e91",
}
YEARS = tuple(sorted(ZIP_MD5))
BLANK = 0.01          # at most this share of a sheet's rows may lack a status or planned month
TOP_ROWS = 15
TOP_CELLS = 10
UA = "mv2-munim-layouts/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
FILES = ("layouts.py", "test_layouts.py")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def kind(name):
    """A sheet's kind from its name: canceled, retired, planned, operating or other."""
    low = str(name).lower()
    for word, k in (("cancel", "canceled"), ("retire", "retired"), ("plan", "planned"),
                    ("operat", "operating")):
        if word in low:
            return k
    return "other"


def left_out(name):
    """Does the workbook route leave this sheet out (workbook.SKIP)?"""
    return any(w in str(name).lower() for w in wk.SKIP)


def picks(cols):
    """The column workbook.sheet_rows uses for each field (None when it finds none)."""
    return {"plant_id": xp.find_col(cols, "plant id"),
            "generator_id": xp.find_col(cols, "generator id"),
            "capacity": wk._pick(cols, (("nameplate capacity",), ()), (("capacity",), ())),
            "status": xp.find_col(cols, "status"),
            "planned_month": wk._pick(cols, (("planned", "operation", "month"), ()),
                                      (("planned", "month"), ("retire",))),
            "planned_year": wk._pick(cols, (("planned", "operation", "year"), ()),
                                     (("planned", "year"), ("retire",))),
            "technology": xp.find_col(cols, "technology"),
            "state": xp.find_col(cols, "state"),
            "plant_name": xp.find_col(cols, "plant name")}


def top_cells(rows, n=TOP_ROWS, width=TOP_CELLS):
    """The non-empty cells of a sheet's first n rows (at most width per row, 40 characters
    each), to show a layout the reader does not know."""
    out = []
    for row in rows[:n]:
        cells = [str(c).strip()[:40] for c in row if c is not None and c == c and str(c).strip()]
        if cells:
            out.append(cells[:width])
    return out


def health(rec, k):
    """Reader health of one sheet's records (workbook.sheet_rows)."""
    return {"rows": int(len(rec)), "keys": int(rec["key"].nunique()),
            "status_blank": int((rec["status"] == "").sum()),
            "capacity_zero": int((rec["capacity_mw"] <= 0).sum()),
            "planned_missing": int(rec["planned_m"].isna().sum()) if k == "planned" else None,
            "generator_id_missing": int((rec["generator_id"] == "nan").sum()),
            "statuses": sorted({s for s in rec["status"] if s})}


def problems(info):
    """Reader problems on a sheet the route reads ([] for a sheet it leaves out, and for a sheet
    with no header row that is not named as a generator sheet)."""
    if info["left_out"]:
        return []
    if info.get("error"):
        return ["error: %s" % info["error"]]
    k = info["kind"]
    if info["header_row"] is None:
        return [] if k == "other" else ["no header row"]
    p, out = info["picks"], []
    if p["capacity"] is None:
        out.append("no capacity column")
    if k != "retired" and p["status"] is None:
        out.append("no status column")
    plan_cols = p["planned_month"] is not None and p["planned_year"] is not None
    if k == "planned" and not plan_cols:
        out.append("no planned month or year column")
    n = info["rows"]
    if n == 0:
        out.append("no rows")
    elif k != "retired" and p["status"] is not None and info["status_blank"] > BLANK * n:
        out.append("status blank in %d of %d rows" % (info["status_blank"], n))
    if k == "planned" and n and plan_cols and info["planned_missing"] > BLANK * n:
        out.append("planned month missing in %d of %d rows" % (info["planned_missing"], n))
    return out


def sheet_info(name, raw):
    """One sheet read with header=None -> (its layout and reader health, its records or None)."""
    info = {"sheet": str(name), "kind": kind(name), "left_out": left_out(name),
            "shape": [int(x) for x in raw.shape], "header_row": None}
    rec = None
    try:
        rows = raw.values.tolist()
        info["header_row"] = xp.find_header(rows)
        if info["header_row"] is None:
            info["top"] = top_cells(rows)
        else:
            df, _ = xp.sheet_frame(raw)
            cols = list(df.columns)
            info["columns"] = [str(c) for c in cols]
            info["picks"] = picks(cols)
            rec = wk.sheet_rows(name, raw)
            info.update(health(rec, info["kind"]))
    except Exception as e:  # recorded, not raised: the other sheets and months still run
        info["error"] = "%s: %s" % (type(e).__name__, e)
        rec = None
    info["problems"] = problems(info)
    return info, rec


def month_info(month, sheets):
    """A month's sheets ({name: raw frame}) -> its sheets' layouts, the route's keys and
    duplicate keys (as workbook.workbook_frame counts them) and whether it is readable."""
    infos, recs = [], []
    for name, raw in sheets.items():
        info, rec = sheet_info(name, raw)
        infos.append(info)
        if rec is not None and not info["left_out"]:
            recs.append(rec)
    wb = pd.concat(recs, ignore_index=True) if recs else None
    probs = ["%s: %s" % (i["sheet"], p) for i in infos for p in i["problems"]]
    if not any(i["kind"] == "operating" and not i["left_out"] and i.get("rows", 0) > 0
               for i in infos):
        probs.append("no Operating sheet with rows")
    return {"month": month, "sheets": infos,
            "rows": 0 if wb is None else int(len(wb)),
            "keys": 0 if wb is None else int(wb["key"].nunique()),
            "duplicate_keys": 0 if wb is None else int(wb["key"].duplicated().sum()),
            "problems": probs, "readable": not probs}


def read_month(zf, month):
    """One month's workbook from a zip -> month_info, plus its member, bytes, md5 and seconds;
    {month, member: None} when the zip has no workbook for it."""
    t0 = time.time()
    member, hits = rc.member_for(zf.namelist(), month)
    if member is None:
        return {"month": month, "member": None, "hits": hits, "readable": False, "problems": []}
    data = zf.read(member)
    head = {"member": member, "hits": hits, "bytes": len(data), "md5": rc.md5(data)}
    try:
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    except Exception as e:  # recorded, not raised
        return dict(month=month, readable=False, problems=["not read: %s: %s" % (type(e).__name__, e)],
                    seconds=round(time.time() - t0, 1), **head)
    entry = month_info(month, sheets)
    entry.update(head)
    entry["seconds"] = round(time.time() - t0, 1)
    return entry


def listed_md5(text):
    """datapackage.json's text -> {file name: md5} from each resource's name, path and hash."""
    out = {}
    try:
        pkg = json.loads(text)
    except (TypeError, ValueError):
        return out
    for r in pkg.get("resources", []) if isinstance(pkg, dict) else []:
        h = str(r.get("hash") or "").strip().lower()
        h = h.split(":", 1)[1] if ":" in h else h
        if not h:
            continue
        for n in (r.get("name"), str(r.get("path") or "").split("?")[0].rsplit("/", 1)[-1]):
            if n:
                out[str(n)] = h
    return out


def file_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_zip(year, data_dir, page_md5, pkg_md5, download=rc.download):
    """eia860m-YYYY.zip -> (path or None, info). A copy kept in data_dir (keyhist's file name)
    is used when its md5 is the record page's or datapackage.json's; otherwise it is downloaded
    and kept only on such a match."""
    name = "eia860m-%d.zip" % year
    path = os.path.join(data_dir, "zenodo-%s-%s" % (RECORD, name))
    want = {m for m in (page_md5, pkg_md5) if m}
    info = {"file": name, "md5_page": page_md5, "md5_datapackage": pkg_md5, "cached": False,
            "tried": []}
    got = None
    if os.path.exists(path):
        got = file_md5(path)
        if got in want:
            info.update(cached=True, bytes=os.path.getsize(path))
    if not info["cached"]:
        got = None
        for url in rc.file_urls(RECORD, name):
            data, err = download(url)
            if data is not None and rc.md5(data) not in want:
                data, err = None, "md5 %s matches neither listed md5" % rc.md5(data)
            info["tried"].append({"url": url, "error": err})
            if data is not None:
                got = rc.md5(data)
                with open(path, "wb") as fh:
                    fh.write(data)
                info["bytes"] = len(data)
                break
    if got is None:
        return None, info
    info.update(md5=got, md5_matches_page=got == page_md5, md5_matches_datapackage=got == pkg_md5)
    return path, info


def read_year(year, path):
    """Every month of one year's zip -> (month entries, spreadsheet members no month claimed,
    error)."""
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as e:
        return [], [], "not a zip: %s" % e
    months, claimed = [], set()
    with zf:
        for k in range(1, 13):
            m = "%d-%02d" % (year, k)
            e = read_month(zf, m)
            if e.get("member"):
                claimed.add(e["member"])
                print("%s %s %s rows, readable %s, %ss" % (m, e["member"], e.get("rows"),
                                                         e["readable"], e.get("seconds")), flush=True)
            months.append(e)
        names = zf.namelist()
    unclaimed = sorted(n for n in names if n.lower().endswith((".xlsx", ".xls")) and n not in claimed)
    return months, unclaimed, None


def layouts(years):
    """Months grouped by each route sheet's layout (kind, header row, picked columns)."""
    groups = collections.OrderedDict()
    for y in years:
        for m in y["months"]:
            for s in m.get("sheets", []):
                if s["left_out"] or "picks" not in s:
                    continue
                p = s["picks"]
                sig = (s["kind"], s["header_row"], p["capacity"], p["status"],
                       p["planned_month"], p["planned_year"])
                groups.setdefault(sig, []).append(m["month"])
    return [{"kind": k[0], "header_row": k[1], "capacity": k[2], "status": k[3],
             "planned_month": k[4], "planned_year": k[5], "months": len(v), "first": min(v),
             "last": max(v)} for k, v in groups.items()]


def sheet_sets(years):
    """Months grouped by their tuple of sheet names."""
    groups = collections.OrderedDict()
    for y in years:
        for m in y["months"]:
            if m.get("sheets"):
                groups.setdefault(tuple(s["sheet"] for s in m["sheets"]), []).append(m["month"])
    return [{"sheets": list(k), "months": len(v), "first": min(v), "last": max(v)}
            for k, v in groups.items()]


def totals(years):
    found = [m for y in years for m in y["months"] if m.get("member")]
    return {"years": len(years), "workbooks_found": len(found),
            "readable": sum(1 for m in found if m["readable"]),
            "not_readable": [m["month"] for m in found if not m["readable"]],
            "first_month": min((m["month"] for m in found), default=None),
            "last_month": max((m["month"] for m in found), default=None),
            "seconds": round(sum(m.get("seconds") or 0 for m in found), 1)}


def _get_bytes(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def same_as_published(base, names, minutes, here=".", fetch=_get_bytes, clock=time.time,
                      pause=time.sleep, sleep=120):
    """Poll base + name until every published copy equals the run copy, for at most minutes ->
    {checks, same, files: {name: {md5, same, error}}}."""
    deadline = clock() + minutes * 60
    checks = 0
    while True:
        checks += 1
        files = {}
        for n in names:
            with open(os.path.join(here, n), "rb") as fh:
                mine = fh.read()
            entry = {"md5": hashlib.md5(mine).hexdigest(), "same": False, "error": None}
            try:
                entry["same"] = fetch(base + n) == mine
            except Exception as e:  # a failed poll is retried until the deadline
                entry["error"] = "%s: %s" % (type(e).__name__, e)
            files[n] = entry
        same = all(f["same"] for f in files.values())
        if same or clock() >= deadline:
            return {"checks": checks, "same": same, "files": files, "at": now()}
        pause(sleep)


def _rows(e):
    parts = []
    for s in e.get("sheets", []):
        if s["left_out"]:
            parts.append("%s -" % s["sheet"])
        elif s.get("error"):
            parts.append("%s (error)" % s["sheet"])
        elif "rows" in s:
            parts.append("%s %d" % (s["sheet"], s["rows"]))
        else:
            parts.append("%s (no header)" % s["sheet"])
    return "; ".join(parts)


def render(result):
    t = result["totals"]
    md = ["# layouts %s: can workbook.py read every EIA-860M workbook in PUDL's archive?" % __version__,
          "", "Structure check before the twenty-ninth test. No workbook is compared with PUDL and "
          "nothing the test will score is computed. MV2 of Munim, Inc. (made with AI agents).", "",
          "Zenodo record %s; datapackage.json read: %s (%d files listed). Reader: workbook %s, "
          "xlsxprobe %s, rawcheck %s." % (RECORD, result["datapackage"]["read"],
                                          len(result["datapackage"]["md5"]), wk.__version__,
                                          xp.__version__, rc.__version__), "",
          "Readable: %d of %d workbooks found (%s to %s, %d years); not readable: %s. Reading took "
          "%s s." % (t["readable"], t["workbooks_found"], t["first_month"], t["last_month"],
                     t["years"], ", ".join(t["not_readable"]) or "none", t["seconds"]), "",
          "## Zips", "",
          "| year | md5 = record page | md5 = datapackage.json | bytes | kept copy | workbooks | "
          "readable | unclaimed spreadsheets | error |", "|---|---|---|---|---|---|---|---|---|"]
    for y in result["years"]:
        z = y["zip"]
        found = [m for m in y["months"] if m.get("member")]
        errs = "; ".join(x["error"] for x in z.get("tried", []) if x["error"])
        md.append("| %d | %s | %s | %s | %s | %d | %d | %d | %s |" % (
            y["year"], z.get("md5_matches_page"), z.get("md5_matches_datapackage"), z.get("bytes"),
            z.get("cached"), len(found), sum(1 for m in found if m["readable"]),
            len(y.get("unclaimed", [])), y.get("error") or errs))
    md += ["", "## Months", "",
           "| month | member | sheets (rows read; - left out) | keys | duplicate keys | seconds | "
           "readable | problems |", "|---|---|---|---|---|---|---|---|"]
    for y in result["years"]:
        for m in y["months"]:
            if not m.get("member"):
                continue
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                m["month"], m["member"], _rows(m), m.get("keys"), m.get("duplicate_keys"),
                m.get("seconds"), m["readable"], "; ".join(m["problems"])))
    md += ["", "## Layouts of the sheets the route reads", "",
           "| kind | header row | capacity | status | planned month | planned year | months | "
           "first | last |", "|---|---|---|---|---|---|---|---|---|"]
    for x in result["layouts"]:
        md.append("| %s | %s | %s | %s | %s | %s | %d | %s | %s |" % (
            x["kind"], x["header_row"], x["capacity"], x["status"], x["planned_month"],
            x["planned_year"], x["months"], x["first"], x["last"]))
    md += ["", "## Sheet-name sets", "", "| sheets | months | first | last |", "|---|---|---|---|"]
    for x in result["sheet_sets"]:
        md.append("| %s | %d | %s | %s |" % (", ".join(x["sheets"]), x["months"], x["first"], x["last"]))
    odd = [(m["month"], s) for y in result["years"] for m in y["months"] for s in m.get("sheets", [])
           if s.get("problems") or (s["header_row"] is None and s["kind"] != "other")]
    md += ["", "## Sheets with a problem (first rows shown when no header was found)", ""]
    if not odd:
        md.append("None.")
    for month, s in odd[:40]:
        md.append("- %s %s: %s" % (month, s["sheet"], "; ".join(s["problems"]) or "left out"))
        for row in s.get("top", [])[:TOP_ROWS]:
            md.append("  - %s" % " | ".join(row))
    unclaimed = [(y["year"], n) for y in result["years"] for n in y.get("unclaimed", [])]
    md += ["", "## Spreadsheets in a zip that no month claimed", ""]
    md += ["- %d: %s" % (y, n) for y, n in unclaimed] or ["None."]
    pub = result.get("published")
    if pub:
        md += ["", "Published copies same as run copies: %s (%s)." % (pub["same"], ", ".join(
            "%s %s %s" % (n, f["same"], f["md5"]) for n, f in pub["files"].items()))]
    return "\n".join(md) + "\n"


def sheet_table(years):
    """One row per month and sheet, for layouts_sheets.csv."""
    rows = []
    for y in years:
        for m in y["months"]:
            for s in m.get("sheets", []):
                rows.append({"month": m["month"], "sheet": s["sheet"], "kind": s["kind"],
                             "left_out": s["left_out"], "header_row": s["header_row"],
                             "rows": s.get("rows"), "keys": s.get("keys"),
                             "status_blank": s.get("status_blank"),
                             "capacity_zero": s.get("capacity_zero"),
                             "planned_missing": s.get("planned_missing"),
                             "generator_id_missing": s.get("generator_id_missing"),
                             "problems": "; ".join(s["problems"])})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--year", action="append", type=int, default=None)
    ap.add_argument("--compare-base", default=None, help="raw URL folder of the published copies")
    ap.add_argument("--minutes", type=float, default=60.0)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    result = {"version": __version__, "workbook": wk.__version__, "started_at": now(),
              "record": RECORD, "years": []}
    pkg = {"read": False, "tried": [], "md5": {}}
    for url in rc.file_urls(RECORD, "datapackage.json"):
        data, err = rc.download(url, timeout=120)
        pkg["tried"].append({"url": url, "error": err})
        if data is not None:
            pkg["md5"] = listed_md5(data.decode("utf-8", "replace"))
            pkg["read"] = True
            break
    result["datapackage"] = pkg
    for year in args.year or YEARS:
        name = "eia860m-%d.zip" % year
        path, zinfo = get_zip(year, args.data_dir, ZIP_MD5.get(year), pkg["md5"].get(name))
        entry = {"year": year, "zip": zinfo, "months": [], "unclaimed": [], "error": None}
        if path is None:
            entry["error"] = "zip not downloaded with a listed md5"
        else:
            entry["months"], entry["unclaimed"], entry["error"] = read_year(year, path)
        result["years"].append(entry)
    result["totals"] = totals(result["years"])
    result["layouts"] = layouts(result["years"])
    result["sheet_sets"] = sheet_sets(result["years"])
    result["finished_at"] = now()
    if args.compare_base:
        result["published"] = same_as_published(args.compare_base, FILES, args.minutes)
    with open(os.path.join(args.out_dir, "layouts.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    sheet_table(result["years"]).to_csv(os.path.join(args.out_dir, "layouts_sheets.csv"), index=False)
    md = render(result)
    with open(os.path.join(args.out_dir, "layouts.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
