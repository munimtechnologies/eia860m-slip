"""retiredgap: were the generators missing from November 2024's EIA-860M workbook missing from EIA's own file?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive check for docs/heldtrace.md; no prediction is tested. heldtrace-v2 found that 282
generators listed in October 2024's workbook were not in November 2024's and that most came back
in December, and layouts-v1 found the Retired sheet of PUDL's archived November 2024 copy about
270 rows shorter than October's and December's. This reads the October, November and December
2024 workbooks from PUDL's archive (eia860m-2024.zip of Zenodo record 22995197, the copy kept
for job layouts-v1) and from EIA's site, compares each pair by md5, and in each source lists the
generators listed in October and December but not November: their sheets, retirement years,
states, technologies and nameplate MW. Canceled or Postponed and *_PR sheets are left out, as in
history.py. Honest User-Agent; three downloads from EIA, two seconds apart.

    python retiredgap.py --data-dir /data --out-dir /out
"""

import argparse
import collections
import glob
import hashlib
import io
import json
import os
import re
import time
import urllib.request
import zipfile

import pandas as pd

__version__ = "0.1.0"
MONTHS = ("2024-10", "2024-11", "2024-12")
NAMES = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
         "october", "november", "december")
BASE = "https://www.eia.gov/electricity/data/eia860m/"
UA = "mv2-munim-retiredgap/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
MAGIC = b"PK\x03\x04"   # an xlsx file is a zip archive
FIELDS = {"status": ("status",), "retirement_year": ("retirement year",),
          "retirement_month": ("retirement month",), "technology": ("technology",),
          "state": ("state",), "nameplate_mw": ("nameplate capacity",)}
TOP = 15
SAMPLE = 20


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def md5(data):
    return hashlib.md5(data).hexdigest()


def eia_urls(month):
    """Archive and current URLs of EIA's workbook for report month YYYY-MM."""
    year, mm = month.split("-")
    name = "%s_generator%s.xlsx" % (NAMES[int(mm) - 1], year)
    return [BASE + "archive/xls/" + name, BASE + "xls/" + name]


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def download(urls, get=None):
    """The first URL that gives an xlsx file -> (bytes, url, errors); (None, None, errors) when
    none does. Never raises."""
    errors = []
    for url in urls:
        try:
            data = (get or _get)(url)
        except Exception as e:  # recorded, not raised
            errors.append("%s: %s: %s" % (url, type(e).__name__, e))
            continue
        if data[:4] != MAGIC:
            errors.append("%s: not an xlsx file (first bytes %r)" % (url, data[:16]))
            continue
        return data, url, errors
    return None, None, errors


def member_for(names, month):
    """The zip member holding report month YYYY-MM's workbook (as rawcheck.member_for)."""
    year, mm = month.split("-")
    word = NAMES[int(mm) - 1]
    pat = re.compile(r"%s[-_]?%s(?!\d)" % (year, mm))
    hits = [n for n in names if n.lower().endswith((".xlsx", ".xls")) and
            ((word in n.lower() and year in n) or pat.search(n.rsplit("/", 1)[-1]))]
    hits.sort(key=lambda n: (len(n), n))
    return hits[0] if hits else None


def plain(v):
    """A cell as JSON-friendly value: None when missing, int for a whole float, text stripped."""
    if v is None or (isinstance(v, float) and v != v):
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    return s or None


def plain_id(v):
    """A plant id as text without leading zeros ('00002', 2, 2.0 -> '2'); None when missing."""
    p = plain(v)
    if p is None:
        return None
    s = str(p)
    return str(int(s)) if s.isdigit() else s


def gen_id(v):
    p = plain(v)
    return "" if p is None else str(p)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def find_header(rows, limit=15):
    """Index of the first row with cells 'Plant ID' and 'Generator ID', else None."""
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip().lower() for c in row if c is not None and c == c}
        if "plant id" in cells and "generator id" in cells:
            return i
    return None


def route(name):
    """Does history.py's route read this sheet (all but Canceled or Postponed and *_PR)?"""
    low = str(name).lower()
    return not ("cancel" in low or low.endswith("_pr"))


def book_sheet(name, raw):
    """One sheet read with header=None -> {sheet, route, header_row, rows, keys: {key: fields}};
    only rows with a whole-number plant id count."""
    rows = raw.values.tolist()
    h = find_header(rows)
    entry = {"sheet": str(name), "route": route(name), "header_row": h, "rows": 0, "keys": {}}
    if h is None:
        return entry
    low = [str(c).strip().lower() if c is not None and c == c else "" for c in rows[h]]
    pick = {f: next((j for j, c in enumerate(low) if all(w in c for w in ws)), None)
            for f, ws in FIELDS.items()}
    pj, gj = low.index("plant id"), low.index("generator id")
    for r in rows[h + 1:]:
        pid = plain_id(r[pj])
        if pid is None or not pid.isdigit():
            continue
        entry["rows"] += 1
        key = "%s/%s" % (pid, gen_id(r[gj]))
        entry["keys"].setdefault(key, {f: None if j is None else plain(r[j]) for f, j in pick.items()})
    return entry


def read_book(data):
    """xlsx bytes -> (list of book_sheet entries, None) or (None, error)."""
    try:
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    except Exception as e:  # recorded, not raised
        return None, "%s: %s" % (type(e).__name__, e)
    return [book_sheet(n, raw) for n, raw in sheets.items()], None


def keyset(book):
    """{key: (sheet, fields)} over the route's sheets; the first sheet listing a key wins."""
    out = {}
    for s in book:
        if s["route"]:
            for k, v in s["keys"].items():
                out.setdefault(k, (s["sheet"], v))
    return out


def counts(values, top=None):
    c = collections.Counter("-" if v is None else str(v) for v in values)
    return [{"value": v, "n": n} for v, n in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:top]]


def gap(books):
    """{month: book} for MONTHS -> the generators listed in the first and last month's workbook
    but not in the middle one's, described from the last month's rows."""
    a, b, c = (keyset(books[m]) for m in MONTHS)
    left = sorted(set(a) - set(b))
    back = [k for k in left if k in c]
    return {"keys": [len(a), len(b), len(c)], "left": len(left), "back": len(back),
            "sheet_before": counts(a[k][0] for k in back),
            "sheet_after": counts(c[k][0] for k in back),
            "retirement_year": counts(c[k][1]["retirement_year"] for k in back),
            "state": counts((c[k][1]["state"] for k in back), TOP),
            "technology": counts((c[k][1]["technology"] for k in back), TOP),
            "mw": round(sum(num(c[k][1]["nameplate_mw"]) for k in back), 1),
            "back_keys": back}


def report(sources):
    """{source: {month: book}} -> gaps for each source with all three months, and how many of
    the archive's gap generators EIA's own middle-month file lists."""
    out = {"gaps": {s: gap(b) for s, b in sources.items() if all(m in b for m in MONTHS)}}
    g, eia = out["gaps"].get("archive"), sources.get("eia", {})
    if g is not None and MONTHS[1] in eia:
        mid = keyset(eia[MONTHS[1]])
        out["archive_gap_in_eia_middle"] = sum(1 for k in g["back_keys"] if k in mid)
    return out


def render(result):
    md = ["# retiredgap %s: generators missing from November 2024's EIA-860M workbook" % __version__,
          "", "Descriptive check for docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. "
          "(made with AI agents).", ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    md += ["PUDL archive: %s." % result["zip"], "", "## Files", "",
           "| month | archive member | archive bytes | archive md5 | EIA URL | EIA bytes | EIA md5 | "
           "same file |", "|---|---|---|---|---|---|---|---|"]
    for f in result["files"]:
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            f["month"], f["member"], f["archive_bytes"], f["archive_md5"], f["eia_url"],
            f["eia_bytes"], f["eia_md5"], f["same_file"]))
    errs = ["%s %s" % (f["month"], e) for f in result["files"] for e in f["errors"]]
    md += ["", "Errors: %s." % ("; ".join(errs) or "none"), "",
           "## Sheets (rows with a plant id; - not read by the route)", "",
           "| month | source | sheets |", "|---|---|---|"]
    for f in result["files"]:
        for src, sheets in f["sheets"].items():
            md.append("| %s | %s | %s |" % (f["month"], src, "; ".join(
                "%s %d%s" % (s["sheet"], s["rows"], "" if s["route"] else " -") for s in sheets) or "not read"))
    md += ["", "## Listed in %s and %s but not in %s" % (MONTHS[0], MONTHS[2], MONTHS[1]), "",
           "| source | keys %s | keys %s | keys %s | left in %s | back in %s | nameplate MW of those back |"
           % (MONTHS + (MONTHS[1], MONTHS[2])), "|---|---|---|---|---|---|---|"]
    for src, g in result["gaps"].items():
        md.append("| %s | %d | %d | %d | %d | %d | %s |" % ((src,) + tuple(g["keys"]) + (
            g["left"], g["back"], g["mw"])))
    if "archive_gap_in_eia_middle" in result:
        md += ["", "Of the archive's %d, listed in EIA's own %s file: %d." % (
            result["gaps"]["archive"]["back"], MONTHS[1], result["archive_gap_in_eia_middle"])]
    for src, g in result["gaps"].items():
        for title, field in (("sheet in %s" % MONTHS[0], "sheet_before"), ("sheet in %s" % MONTHS[2], "sheet_after"),
                             ("retirement year", "retirement_year"), ("state (top %d)" % TOP, "state"),
                             ("technology (top %d)" % TOP, "technology")):
            md += ["", "### %s: %s" % (src, title), "", "| value | generators |", "|---|---|"]
            md += ["| %s | %d |" % (x["value"], x["n"]) for x in g[field]]
        md += ["", "First %d of %s's: %s" % (SAMPLE, src, ", ".join(g["back_keys"][:SAMPLE]) or "none")]
    return "\n".join(md) + "\n"


def find_zip(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*eia860m-2024.zip"), recursive=True))
    return hits[0] if hits else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "user_agent": UA, "started_at": now(), "months": MONTHS}
    path = find_zip(args.data_dir)
    if path is None:
        result["error"] = "no *eia860m-2024.zip under %s" % args.data_dir
    else:
        result["zip"] = "%s (%d bytes, md5 %s)" % (os.path.basename(path), os.path.getsize(path),
                                                   md5(open(path, "rb").read()))
        sources, files = {"archive": {}, "eia": {}}, []
        with zipfile.ZipFile(path) as zf:
            for i, m in enumerate(MONTHS):
                if i:
                    time.sleep(2)
                member = member_for(zf.namelist(), m)
                got = {"archive": zf.read(member) if member else None}
                got["eia"], url, errors = download(eia_urls(m))
                f = {"month": m, "member": member, "eia_url": url, "errors": errors, "sheets": {}}
                for src, data in got.items():
                    f["%s_bytes" % src] = len(data) if data else None
                    f["%s_md5" % src] = md5(data) if data else None
                    if data is None:
                        continue
                    book, err = read_book(data)
                    if err:
                        f["errors"].append("%s not read: %s" % (src, err))
                        continue
                    sources[src][m] = book
                    f["sheets"][src] = [{"sheet": s["sheet"], "rows": s["rows"], "route": s["route"]}
                                        for s in book]
                f["same_file"] = bool(got["archive"] and got["eia"]) and f["archive_md5"] == f["eia_md5"]
                print("%s member %s same file %s errors %s" % (m, member, f["same_file"], errors), flush=True)
                files.append(f)
        result["files"] = files
        result.update(report(sources))
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "retiredgap.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "retiredgap.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
