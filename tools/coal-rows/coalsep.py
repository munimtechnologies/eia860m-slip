"""coalsep: EIA's September 2026 EIA-860M workbook, read for coal: 2026 retirements and the dates ahead.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

docs/coal-rows.md found, on PUDL's EIA-860M changelog (reports to August 2026), that no coal generator
retired from January to August 2026, and followed the 16 generators of EIA's December 2025 plan. PUDL
has not yet taken in September 2026, so this reads EIA's own workbooks, as p5score.py did. The
predictions it scores (S1-S3) are in docs/coalsep-plan.md, written before this code read the September
workbook's coal rows.

Gate G1: EIA's August 2026 workbook must reproduce what coal-rows took from PUDL: (a) no coal row on the
Retired sheet with retirement year 2026, and (b) at least 15 of the 16 plan generators on the Operating
sheet with the planned month PUDL gave (blank where PUDL had none). If G1 fails, nothing is scored.

A row is coal when its energy source code is a coal code, or, with no code, its technology names coal.
Capacity is net summer, nameplate where summer is blank or zero (as coal_rows.py).

    python coalsep.py --out-dir /out --work-dir .
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
AGENT = "mv2-munim-coalsep/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
ACCEPT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*"
XLSX_MAGIC = b"PK\x03\x04"
GZIP_MAGIC = b"\x1f\x8b"

SEPT = ("september_generator2026.xlsx", "4c741eb77a5ccad5aca32ffe43f398af", 14013970)
AUG = ("august_generator2026.xlsx", "9727ac867236faab7d5503175dacdf38", 13955142)

COAL_CODES = frozenset({"BIT", "SUB", "LIG", "ANT", "RC", "WC", "SGC"})

# Plants under DOE 202(c) plant orders (data/doe_202c_orders.csv), by EIA plant ID.
ORDER_PLANTS = {"1710": "J.H. Campbell", "3161": "Eddystone", "1554": "H.A. Wagner", "3845": "Centralia",
                "6085": "R.M. Schahfer", "1012": "F.B. Culley", "6021": "Craig", "564": "Stanton"}

# EIA's December 2025 coal plan for 2026 and the planned month PUDL gave in its latest report (to
# August 2026), from data/coal_plan_2026_followup.csv: key -> (MW, planned month, '' for no date).
PLAN = {
    "1012/2": (90.0, "2026-09"), "165/2": (478.9, ""), "1710/1": (260.0, "2026-11"),
    "1710/2": (279.8, "2026-11"), "1710/3": (790.7, "2026-11"), "3399/2": (1231.0, "2034-12"),
    "3407/7": (147.0, "2034-12"), "3407/8": (150.0, "2034-12"), "3407/9": (147.0, "2034-12"),
    "4041/7": (306.5, "2027-12"), "4041/8": (309.5, "2027-12"), "470/2": (335.0, "2026-12"),
    "6021/1": (427.0, "2026-09"), "6085/17": (361.0, "2026-10"), "6085/18": (361.0, "2026-10"),
    "6090/1": (680.0, "2026-12"),
}
G1_NEED = 15
S2_STILL_2026 = {"6090/1": "2026-12", "470/2": "2026-12"}   # Sherburne County 1, Comanche 2
WINDOW = ("2026-10", "2026-12")
S3_RANGE = (3000.0, 4500.0)
S3_SHARE = 0.60
AHEAD = ("2026-10", "2027-12")


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


def to_float(value):
    try:
        x = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return None if x != x else x


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


def find_col(columns, *needles):
    """Index of the first column whose lower-case name contains every needle, else None."""
    for j, c in enumerate(columns):
        low = str(c).strip().lower()
        if all(n in low for n in needles):
            return j
    return None


def sheet_kind(title):
    low = title.strip().lower()
    if low.startswith("operating"):
        return "operating"
    if low.startswith("retired"):
        return "retired"
    return None


def is_coal(code, tech):
    if isinstance(code, str) and code.strip():
        return code.strip().upper() in COAL_CODES
    return isinstance(tech, str) and "coal" in tech.lower()


def coal_rows(sheet, rows):
    """One sheet's rows (lists of cell values) -> (coal records, header info or None). Only Operating
    and Retired sheets are read; 'ym' is the planned retirement month on Operating sheets and the
    retirement month on Retired sheets."""
    kind = sheet_kind(sheet)
    h = find_header(rows) if kind else None
    if h is None:
        return [], None
    cols = ["" if c is None else str(c).strip() for c in rows[h]]
    j = {"pid": find_col(cols, "plant id"), "gid": find_col(cols, "generator id"),
         "name": find_col(cols, "plant name"), "state": find_col(cols, "plant state"),
         "status": find_col(cols, "status"), "nameplate": find_col(cols, "nameplate"),
         "summer": find_col(cols, "summer"), "esc": find_col(cols, "energy source"),
         "tech": find_col(cols, "technology"), "rm": find_col(cols, "retirement", "month"),
         "ry": find_col(cols, "retirement", "year")}

    def cell(row, key):
        k = j[key]
        return row[k] if k is not None and k < len(row) else None

    out = []
    for row in rows[h + 1:]:
        pid, gid = norm_id(cell(row, "pid")), norm_id(cell(row, "gid"))
        if not pid or not gid:
            continue
        esc, tech = cell(row, "esc"), cell(row, "tech")
        if not is_coal(esc, tech):
            continue
        summer, name = to_float(cell(row, "summer")), to_float(cell(row, "nameplate"))
        mw = summer if summer is not None and summer > 0 else (name or 0.0)
        out.append({"sheet": sheet, "kind": kind, "key": "%s/%s" % (pid, gid), "plant_id": pid,
                    "plant_name": str(cell(row, "name") or "").strip(),
                    "state": str(cell(row, "state") or "").strip(),
                    "status": str(cell(row, "status") or "").strip(),
                    "esc": str(esc or "").strip(), "ym": ym(cell(row, "ry"), cell(row, "rm")),
                    "mw": float(mw)})
    info = {"header_row": h, "rows": len(rows) - h - 1, "coal_rows": len(out),
            "columns_found": sorted(k for k, v in j.items() if v is not None),
            "columns_missing": sorted(k for k, v in j.items() if v is None)}
    return out, info


def index(recs, kind):
    """{key: first record of that kind}."""
    out = {}
    for r in recs:
        if r["kind"] == kind and r["key"] not in out:
            out[r["key"]] = r
    return out


def retired_in(recs, year):
    return sorted((r for r in recs if r["kind"] == "retired" and r["ym"][:4] == year),
                  key=lambda r: (r["ym"], r["key"]))


def gate(aug):
    op = index(aug, "operating")
    rows = []
    for k, (mw, want) in sorted(PLAN.items()):
        got = op[k]["ym"] if k in op else None
        rows.append({"key": k, "pudl": want, "august": "(not on Operating sheet)" if got is None else got,
                     "match": got == want})
    ret26 = retired_in(aug, "2026")
    n = sum(1 for r in rows if r["match"])
    return {"retired_2026": ret26, "plan_rows": rows, "plan_match": n, "need": G1_NEED,
            "held": not ret26 and n >= G1_NEED}


def window_rows(recs, lo, hi):
    return [r for r in recs if r["kind"] == "operating" and r["ym"] and lo <= r["ym"] <= hi]


def predictions(sep):
    op, ret = index(sep, "operating"), index(sep, "retired")
    s1_rows = retired_in(sep, "2026")
    plan_retired = sorted(k for k in PLAN if k in ret)
    still = {k: (op[k]["ym"] if k in op else "(not on Operating sheet)") for k in S2_STILL_2026}
    s2 = not plan_retired and all(still[k] == v for k, v in S2_STILL_2026.items())
    win = window_rows(sep, *WINDOW)
    total = sum(r["mw"] for r in win)
    ordered = sum(r["mw"] for r in win if r["plant_id"] in ORDER_PLANTS)
    share = ordered / total if total > 0 else None
    s3 = S3_RANGE[0] <= total <= S3_RANGE[1] and share is not None and share >= S3_SHARE
    return {"S1": {"held": not s1_rows, "retired_2026": s1_rows},
            "S2": {"held": s2, "plan_retired": plan_retired, "still": still},
            "S3": {"held": s3, "mw": round(total, 1), "mw_under_orders": round(ordered, 1),
                   "share": None if share is None else round(share, 4), "units": len(win)}}


def ahead(recs, lo=AHEAD[0], hi=AHEAD[1]):
    """Operating coal units dated lo..hi, by plant."""
    agg = {}
    for r in window_rows(recs, lo, hi):
        a = agg.setdefault(r["plant_id"], {"plant_id": r["plant_id"], "plant": r["plant_name"],
                                           "state": r["state"], "units": [], "mw": 0.0, "months": set()})
        a["units"].append(r["key"].split("/", 1)[1])
        a["mw"] += r["mw"]
        a["months"].add(r["ym"])
    out = []
    for a in agg.values():
        out.append({"plant_id": a["plant_id"], "plant": a["plant"], "state": a["state"],
                    "units": ", ".join(sorted(a["units"])), "mw": round(a["mw"], 1),
                    "months": ", ".join(sorted(a["months"])), "first": min(a["months"]),
                    "doe_order": "yes" if a["plant_id"] in ORDER_PLANTS else "no"})
    return sorted(out, key=lambda a: (a["first"], -a["mw"], a["plant"]))


def overdue(recs, before=WINDOW[0]):
    """Operating coal units whose planned month is before `before`."""
    return sorted((r for r in recs if r["kind"] == "operating" and r["ym"] and r["ym"] < before),
                  key=lambda r: (r["ym"], r["key"]))


def state_of(recs):
    """{key: 'retired YYYY-MM' or 'operating YYYY-MM|no date'}; a Retired row wins over an Operating one."""
    out = {}
    for r in recs:
        s = "%s %s" % (r["kind"], r["ym"] or "no date")
        if r["kind"] == "retired" or r["key"] not in out:
            out[r["key"]] = s
    return out


def changes(aug, sep):
    """Coal units whose state differs between the two workbooks (Retired rows before 2026 ignored)."""
    a, s = state_of(aug), state_of(sep)
    names = {}
    for r in aug + sep:
        names[r["key"]] = (r["plant_name"], r["state"], r["mw"])
    out = []
    for k in sorted(set(a) | set(s)):
        before, after = a.get(k, "absent"), s.get(k, "absent")
        if before == after:
            continue
        if all(x == "absent" or (x.startswith("retired") and x[8:12] < "2026") for x in (before, after)):
            continue
        n = names[k]
        out.append({"key": k, "plant": n[0], "state": n[1], "mw": round(n[2], 1), "august": before,
                    "september": after})
    return out


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
    """All sheets -> (coal records, {sheet: header info or None})."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    recs, info = [], {}
    for ws in wb.worksheets:
        if sheet_kind(ws.title) is None:
            info[ws.title] = None
            continue
        try:
            ws.reset_dimensions()
        except AttributeError:
            pass
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        found, inf = coal_rows(ws.title, rows)
        del rows
        recs += found
        info[ws.title] = inf
    wb.close()
    return recs, info


def verdict(held, gate_held):
    if not gate_held:
        return "not scored (G1 failed)"
    return "held" if held else "failed"


def mwf(x):
    return "{:,.1f}".format(x)


def render(res):
    g, p = res["gate"], res["predictions"]
    md = ["# Coal in EIA's September 2026 EIA-860M workbook (coalsep %s)" % __version__, ""]
    for label in ("september", "august"):
        f = res["files"][label]
        md.append("- %s 2026: %s, %s bytes, md5 %s (same as recorded earlier: %s)" % (
            label.capitalize(), f["url"], "{:,}".format(f["size"]), f["md5"], f["same_as_recorded"]))
    md += ["", "Coal rows read: August %s, September %s." % ("{:,}".format(res["counts"]["august"]),
                                                          "{:,}".format(res["counts"]["september"])),
           "", "## Gate G1: the August workbook reproduces coal-rows (PUDL, to August 2026)", "",
           "- Coal rows on August's Retired sheet with retirement year 2026: %d" % len(g["retired_2026"]),
           "- Plan generators whose August planned month equals PUDL's: %d of %d (needs %d)" % (
               g["plan_match"], len(g["plan_rows"]), g["need"]),
           "- G1: **%s**" % ("held" if g["held"] else "FAILED"), "",
           "| key | PUDL (to Aug 2026) | August workbook | match |", "|---|---|---|---|"]
    for r in g["plan_rows"]:
        md.append("| %s | %s | %s | %s |" % (r["key"], r["pudl"] or "no date", r["august"] or "no date",
                                             "yes" if r["match"] else "no"))
    for r in g["retired_2026"]:
        md.append("")
        md.append("August Retired-sheet coal row in 2026: %s %s (%s), %s, %s MW" % (
            r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"])))
    s1, s2, s3 = p["S1"], p["S2"], p["S3"]
    md += ["", "## Predictions (docs/coalsep-plan.md), September 2026 workbook", "",
           "| # | prediction | result | verdict |", "|---|---|---|---|",
           "| S1 | no coal row on the Retired sheet with retirement year 2026 | %d rows | %s |" % (
               len(s1["retired_2026"]), verdict(s1["held"], g["held"])),
           "| S2 | none of the 16 plan generators retired; Sherburne County 1 and Comanche 2 still dated 2026-12 "
           "| retired: %s; 6090/1: %s; 470/2: %s | %s |" % (
               ", ".join(s2["plan_retired"]) or "none", s2["still"]["6090/1"], s2["still"]["470/2"],
               verdict(s2["held"], g["held"])),
           "| S3 | operating coal dated 2026-10 to 2026-12 is 3,000-4,500 MW, at least 60%% of it at plants under "
           "DOE orders | %s MW in %d units; %s MW under orders (share %s) | %s |" % (
               mwf(s3["mw"]), s3["units"], mwf(s3["mw_under_orders"]),
               "-" if s3["share"] is None else "%.4f" % s3["share"], verdict(s3["held"], g["held"]))]
    if s1["retired_2026"]:
        md += ["", "### September Retired-sheet coal rows in 2026", "",
               "| key | plant | state | retired | MW |", "|---|---|---|---|---|"]
        md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
               for r in s1["retired_2026"]]
    md += ["", "## Described, not scored", "",
           "### Operating coal dated to retire %s to %s, by plant (September 2026 workbook)" % AHEAD, "",
           "| plant | state | plant ID | units | MW | months | DOE 202(c) order |", "|---|---|---|---|---|---|---|"]
    rows = res["ahead"]
    md += ["| %s | %s | %s | %s | %s | %s | %s |" % (a["plant"], a["state"], a["plant_id"], a["units"], mwf(a["mw"]),
                                                    a["months"], a["doe_order"]) for a in rows]
    md += ["", "%d plants, %s MW; %s MW at plants under DOE orders." % (
        len(rows), mwf(sum(a["mw"] for a in rows)), mwf(sum(a["mw"] for a in rows if a["doe_order"] == "yes")))]
    md += ["", "### Operating coal dated before %s (past its planned month), September 2026 workbook" % WINDOW[0], "",
           "| key | plant | state | planned | MW |", "|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
           for r in res["overdue"]] or ["| none | | | | |"]
    md += ["", "### Coal units whose record changed from August to September 2026", "",
           "| key | plant | state | MW | August | September |", "|---|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s | %s |" % (c["key"], c["plant"], c["state"], mwf(c["mw"]), c["august"],
                                               c["september"]) for c in res["changes"]] or ["| none | | | | | |"]
    md += ["", "### Coal on the September Retired sheet with retirement year 2025 or later", "",
           "| key | plant | state | retired | MW |", "|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
           for r in res["retired_recent"]] or ["| none | | | | |"]
    md += ["", "### Sheets read", ""]
    for label in ("september", "august"):
        for sheet, inf in sorted(res["sheets"][label].items()):
            if inf is None:
                md.append("- %s / %s: not read" % (label, sheet))
            else:
                md.append("- %s / %s: header row %d, %s rows, %s coal; columns missing: %s" % (
                    label, sheet, inf["header_row"], "{:,}".format(inf["rows"]), "{:,}".format(inf["coal_rows"]),
                    ", ".join(inf["columns_missing"]) or "none"))
    return "\n".join(md) + "\n"


def analyse(sep, aug):
    g = gate(aug)
    return {"gate": g, "predictions": predictions(sep), "ahead": ahead(sep), "overdue": overdue(sep),
            "changes": changes(aug, sep),
            "retired_recent": sorted((r for r in sep if r["kind"] == "retired" and r["ym"] >= "2025-01"),
                                     key=lambda r: (r["ym"], r["key"]))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--work-dir", default=".")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"version": __version__, "files": {}, "sheets": {}, "counts": {}}
    recs = {}
    for label, (name, known_md5, known_size), archive_first in (("september", SEPT, False), ("august", AUG, True)):
        dest = os.path.join(a.work_dir, name)
        url, size, md5, errors = fetch(name, dest, archive_first)
        if url is None:
            raise SystemExit("could not download %s: %s" % (name, errors))
        same = md5 == known_md5 and size == known_size
        res["files"][label] = {"url": url, "size": size, "md5": md5, "same_as_recorded": same, "errors": errors}
        print("%s: %s %d bytes md5 %s (same as recorded: %s)" % (label, url, size, md5, same), flush=True)
        recs[label], res["sheets"][label] = read_workbook(dest)
        res["counts"][label] = len(recs[label])
        print("%s: %d coal rows" % (label, len(recs[label])), flush=True)
    res.update(analyse(recs["september"], recs["august"]))
    with open(os.path.join(a.out_dir, "coalsep.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    md = render(res)
    with open(os.path.join(a.out_dir, "coalsep.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
