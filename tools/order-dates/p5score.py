"""p5score: score bar P5 of docs/order-dates-preregistration.md on EIA's own September 2026 workbook.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

P5 (fixed on 2026-10-17, before EIA published its September 2026 workbook on 2026-10-23): at least 3
of these 4 plants are dated exactly to the expiry of the order in force on 30 September: Campbell
2026-11 (order 202-26-39), Schahfer 2026-12 (202-26-46), Culley 2026-12 (202-26-47) and Craig 2026-12
(202-26-49).

The pre-registration read PUDL's EIA-860M changelog, which has not yet taken in September 2026, so
this reads EIA's own workbook instead. Check W1 first reads EIA's August 2026 workbook the same way; it
must give the August months that docs/order-dates.md took from PUDL (its check C2: Campbell 2026-11,
Schahfer 2026-10, Culley 2026-09, Craig 2026-09). If it does not, P5 is not scored.

A plant counts as exact when at least one of its units is on the Operating sheet with a planned
retirement month and every such unit is dated to the target month. This rule was written on
2026-10-27, before this code read the September workbook's rows for these units.

The other four plants under orders (Eddystone, Wagner, Centralia, Stanton) are reported against
their own orders' expiry months, not scored.

    python p5score.py --out-dir /out
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import urllib.request

__version__ = "0.1.0"

BASE = "https://www.eia.gov/electricity/data/eia860m/"
AGENT = "mv2-munim-p5score/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
ACCEPT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*"
XLSX_MAGIC = b"PK\x03\x04"
GZIP_MAGIC = b"\x1f\x8b"

# Units as matched by docs/order-dates.md (second run): plant ID and the generator IDs accepted.
UNITS = {
    "campbell": ("1710", ("1", "2", "3")),
    "eddystone": ("3161", ("3", "4")),
    "wagner": ("1554", ("4", "ST4")),
    "centralia": ("3845", ("2", "BW22", "22")),
    "schahfer": ("6085", ("17", "18")),
    "culley": ("1012", ("2",)),
    "craig": ("6021", ("1", "C1")),
    "stanton": ("564", ("1",)),
}
WANTED = {(pid, g.upper()): plant for plant, (pid, gens) in UNITS.items() for g in gens}

P5_TARGETS = {"campbell": "2026-11", "schahfer": "2026-12", "culley": "2026-12", "craig": "2026-12"}
P5_NEED = 3
W1_TARGETS = {"campbell": "2026-11", "schahfer": "2026-10", "culley": "2026-09", "craig": "2026-09"}
# Expiry month of each other plant's order in force on 30 September 2026 (data/doe_202c_unit_orders.csv):
# Eddystone 202-26-40 (2026-11-20), Wagner 202-26-25A (2026-11-17), Centralia 202-26-44 (2026-12-11),
# Stanton 202-26-42 (2026-11-30).
OTHER_EXPIRY = {"eddystone": "2026-11", "wagner": "2026-11", "centralia": "2026-12", "stanton": "2026-11"}

SEPT = ("september_generator2026.xlsx", "4c741eb77a5ccad5aca32ffe43f398af", 14013970)
AUG = ("august_generator2026.xlsx", "9727ac86", None)   # md5 prefix as recorded in earlier jobs


def norm_id(value):
    """Plant or generator id as text: stripped, a trailing '.0' of a whole number removed."""
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:
            return ""
        if value.is_integer():
            return str(int(value))
    text = str(value).strip()
    return text[:-2] if re.fullmatch(r"\d+\.0", text) else text


def to_int(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def ym(year, month):
    """'YYYY-MM' from a year and a month cell, '' if either is missing or out of range."""
    y, m = to_int(year), to_int(month)
    if y is None or m is None or not 1 <= m <= 12:
        return ""
    return "%04d-%02d" % (y, m)


def find_header(rows, limit=15):
    """Index of the first row with cells 'Plant ID' and 'Generator ID', else None."""
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip().lower() for c in row if c is not None}
        if "plant id" in cells and "generator id" in cells:
            return i
    return None


def find_col(columns, *needles, exclude=()):
    """Index of the first column whose lower-case name contains every needle and no excluded word."""
    for j, c in enumerate(columns):
        low = str(c).strip().lower()
        if all(n in low for n in needles) and not any(x in low for x in exclude):
            return j
    return None


def is_operating(sheet):
    return sheet.strip().lower().startswith("operating")


def match_rows(sheet, rows):
    """One sheet's rows (lists of cell values) -> (records of the wanted units, header info or None)."""
    h = find_header(rows)
    if h is None:
        return [], None
    cols = ["" if c is None else str(c).strip() for c in rows[h]]
    j_pid, j_gid = find_col(cols, "plant id"), find_col(cols, "generator id")
    j_rm, j_ry = find_col(cols, "retirement", "month"), find_col(cols, "retirement", "year")
    j_st, j_mw, j_name = find_col(cols, "status"), find_col(cols, "nameplate"), find_col(cols, "plant name")

    def cell(row, j):
        return row[j] if j is not None and j < len(row) else None

    out = []
    for row in rows[h + 1:]:
        pid, gid = norm_id(cell(row, j_pid)), norm_id(cell(row, j_gid))
        plant = WANTED.get((pid, gid.upper()))
        if plant is None:
            continue
        mw = cell(row, j_mw)
        out.append({"plant": plant, "sheet": sheet, "key": "%s/%s" % (pid, gid),
                    "plant_name": str(cell(row, j_name) or "").strip(),
                    "status": str(cell(row, j_st) or "").strip(),
                    "retirement_ym": ym(cell(row, j_ry), cell(row, j_rm)),
                    "mw": float(mw) if isinstance(mw, (int, float)) else None})
    info = {"header_row": h, "retirement_columns": [cols[j] for j in (j_ry, j_rm) if j is not None],
            "rows": len(rows) - h - 1}
    return out, info


def judge(records, target):
    """One plant's records -> (class, sorted Operating-sheet months). 'exact': at least one unit on the
    Operating sheet with a planned retirement month, and every such unit dated to target. 'no month':
    no unit on the Operating sheet with a month. 'other': otherwise."""
    months = sorted({r["retirement_ym"] for r in records if is_operating(r["sheet"]) and r["retirement_ym"]})
    if not months:
        return "no month", months
    return ("exact" if months == [target] else "other"), months


def score(sep_recs, aug_recs):
    def of(recs, plant):
        return [r for r in recs if r["plant"] == plant]

    w1 = {p: judge(of(aug_recs, p), t) for p, t in W1_TARGETS.items()}
    w1_ok = all(c == "exact" for c, _ in w1.values())
    p5 = {p: judge(of(sep_recs, p), t) for p, t in P5_TARGETS.items()}
    n_exact = sum(1 for c, _ in p5.values() if c == "exact")
    if not w1_ok:
        verdict = "not scored (W1 failed)"
    else:
        verdict = "held" if n_exact >= P5_NEED else "failed"
    other = {p: judge(of(sep_recs, p), t) for p, t in OTHER_EXPIRY.items()}
    return {"w1": {p: {"target": W1_TARGETS[p], "class": c, "months": m} for p, (c, m) in w1.items()},
            "w1_held": w1_ok,
            "p5": {p: {"target": P5_TARGETS[p], "class": c, "months": m} for p, (c, m) in p5.items()},
            "p5_exact": n_exact, "p5_need": P5_NEED, "p5_verdict": verdict,
            "other": {p: {"expiry_month": OTHER_EXPIRY[p], "class": c, "months": m} for p, (c, m) in other.items()}}


def fetch(name, dest, archive_first):
    """Download EIA's workbook `name` to dest -> (url, size, md5, errors). Tries the current and the
    archive address; a download counts only if it is an xlsx file."""
    urls = [BASE + "xls/" + name, BASE + "archive/xls/" + name]
    if archive_first:
        urls.reverse()
    errors = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": ACCEPT})
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
        except Exception as exc:  # record every failed address, try the next
            errors.append("%s: %s" % (url, exc))
            continue
        if body[:2] == GZIP_MAGIC:
            body = gzip.decompress(body)
        if body[:4] != XLSX_MAGIC:
            errors.append("%s: not an xlsx file (%d bytes, starts %r)" % (url, len(body), body[:80]))
            continue
        with open(dest, "wb") as fh:
            fh.write(body)
        return url, len(body), hashlib.md5(body).hexdigest(), errors
    return None, 0, "", errors


def read_workbook(path):
    """All sheets -> (records of the wanted units, {sheet: header info or None})."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    recs, info = [], {}
    for ws in wb.worksheets:
        try:
            ws.reset_dimensions()
        except AttributeError:
            pass
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        found, inf = match_rows(ws.title, rows)
        recs += found
        info[ws.title] = inf
    wb.close()
    return recs, info


def render(result):
    md = ["# P5 of order-dates, scored on EIA's own September 2026 workbook (p5score %s)" % __version__, ""]
    for label, f in (("September 2026", result["files"]["september"]), ("August 2026", result["files"]["august"])):
        md.append("- %s: %s, %s bytes, md5 %s (same as recorded earlier: %s)" % (
            label, f["url"], "{:,}".format(f["size"]), f["md5"], f["same_as_recorded"]))
    md += ["", "W1 (August 2026 workbook reproduces order-dates' C2 months): **%s**" % (
        "held" if result["w1_held"] else "FAILED"), "",
        "| plant | August target | class | Operating-sheet months |", "|---|---|---|---|"]
    for p, r in result["w1"].items():
        md.append("| %s | %s | %s | %s |" % (p, r["target"], r["class"], ", ".join(r["months"]) or "-"))
    md += ["", "P5: %d of 4 exact (needs %d): **%s**" % (result["p5_exact"], result["p5_need"], result["p5_verdict"]), "",
           "| plant | target (order in force on 30 Sep 2026) | class | Operating-sheet months |", "|---|---|---|---|"]
    for p, r in result["p5"].items():
        md.append("| %s | %s | %s | %s |" % (p, r["target"], r["class"], ", ".join(r["months"]) or "-"))
    md += ["", "Reported, not scored: the other plants under orders, September 2026 workbook.", "",
           "| plant | expiry month of order in force on 30 Sep 2026 | class | Operating-sheet months |",
           "|---|---|---|---|"]
    for p, r in result["other"].items():
        md.append("| %s | %s | %s | %s |" % (p, r["expiry_month"], r["class"], ", ".join(r["months"]) or "-"))
    for label in ("september", "august"):
        md += ["", "## Every matched row, %s 2026 workbook" % label.capitalize(), "",
               "| plant | key | sheet | plant name | status | retirement month | MW |", "|---|---|---|---|---|---|---|"]
        for r in result["rows"][label]:
            md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["plant"], r["key"], r["sheet"], r["plant_name"], r["status"], r["retirement_ym"] or "-",
                "-" if r["mw"] is None else "%.1f" % r["mw"]))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--work-dir", default=".")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"version": __version__, "files": {}, "rows": {}, "sheets": {}}
    recs = {}
    for label, (name, known_md5, known_size), archive_first in (("september", SEPT, False), ("august", AUG, True)):
        dest = os.path.join(a.work_dir, name)
        url, size, md5, errors = fetch(name, dest, archive_first)
        if url is None:
            raise SystemExit("could not download %s: %s" % (name, errors))
        same = md5.startswith(known_md5) and (known_size is None or size == known_size)
        result["files"][label] = {"url": url, "size": size, "md5": md5, "same_as_recorded": same,
                                  "errors": errors}
        print("%s: %s %d bytes md5 %s (same as recorded: %s)" % (label, url, size, md5, same), flush=True)
        recs[label], result["sheets"][label] = read_workbook(dest)
        result["rows"][label] = sorted(recs[label], key=lambda r: (r["plant"], r["key"], r["sheet"]))
        print("%s: %d matched rows" % (label, len(recs[label])), flush=True)
    result.update(score(recs["september"], recs["august"]))
    with open(os.path.join(a.out_dir, "p5score.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    md = render(result)
    with open(os.path.join(a.out_dir, "p5score.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
