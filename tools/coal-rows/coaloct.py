"""coaloct: EIA's October 2026 EIA-860M workbook, read for coal: 2026 retirements and the dates ahead.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The code of coalsep.py 0.1.0 with the workbooks, the gate and the bars changed, as docs/coaloct-plan.md
says. It was published before EIA posted the October 2026 workbook. The predictions it scores (O1-O3)
are in docs/coaloct-plan.md.

Gate G2: EIA's September 2026 workbook, downloaded again, must give what job coalsep-v1 recorded: (a) no
coal row on the Retired sheet with retirement year 2026, and (b) the same 9 operating coal units dated
2026-10 to 2026-12, with the same months, 3,584.5 MW in all. The file's size and md5 are reported, not
required. If G2 fails, nothing is scored.

A row is coal when its energy source code is a coal code, or, with no code, its technology names coal.
Capacity is net summer, nameplate where summer is blank or zero (as coal_rows.py).

    python coaloct.py --out-dir /out --work-dir .
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import urllib.request

__version__ = "0.2.0"

BASE = "https://www.eia.gov/electricity/data/eia860m/"
AGENT = "mv2-munim-coaloct/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
ACCEPT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*"
XLSX_MAGIC = b"PK\x03\x04"
GZIP_MAGIC = b"\x1f\x8b"

# October's size and md5 are not known in advance: they are recorded, not compared.
OCT = ("october_generator2026.xlsx", None, None)
SEPT = ("september_generator2026.xlsx", "4c741eb77a5ccad5aca32ffe43f398af", 14013970)

COAL_CODES = frozenset({"BIT", "SUB", "LIG", "ANT", "RC", "WC", "SGC"})

# Plants under DOE 202(c) plant orders (data/doe_202c_orders.csv), by EIA plant ID.
ORDER_PLANTS = {"1710": "J.H. Campbell", "3161": "Eddystone", "1554": "H.A. Wagner", "3845": "Centralia",
                "6085": "R.M. Schahfer", "1012": "F.B. Culley", "6021": "Craig", "564": "Stanton"}

# EIA's December 2025 coal plan for 2026 (data/coal_plan_2026_followup.csv): key -> (MW, PUDL's month).
PLAN = {
    "1012/2": (90.0, "2026-09"), "165/2": (478.9, ""), "1710/1": (260.0, "2026-11"),
    "1710/2": (279.8, "2026-11"), "1710/3": (790.7, "2026-11"), "3399/2": (1231.0, "2034-12"),
    "3407/7": (147.0, "2034-12"), "3407/8": (150.0, "2034-12"), "3407/9": (147.0, "2034-12"),
    "4041/7": (306.5, "2027-12"), "4041/8": (309.5, "2027-12"), "470/2": (335.0, "2026-12"),
    "6021/1": (427.0, "2026-09"), "6085/17": (361.0, "2026-10"), "6085/18": (361.0, "2026-10"),
    "6090/1": (680.0, "2026-12"),
}

# What job coalsep-v1 recorded from the September workbook (data/coalsep_2026-09.json): operating coal
# dated 2026-10 to 2026-12, key -> planned month, and its MW.
G2_UNITS = {"1710/1": "2026-11", "1710/2": "2026-11", "1710/3": "2026-11", "6085/17": "2026-12",
            "6085/18": "2026-12", "6090/1": "2026-12", "6021/1": "2026-12", "470/2": "2026-12",
            "1012/2": "2026-12"}
G2_MW = 3584.5
G2_WINDOW = ("2026-10", "2026-12")
O2_BEFORE = "2026-11"
O3_STILL_2026 = {"6090/1": "2026-12", "470/2": "2026-12"}   # Sherburne County 1, Comanche 2
CAMPBELL = ("1710/1", "1710/2", "1710/3")
AHEAD = ("2026-11", "2027-12")
RECENT_FROM = "2025-01"


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


def window_rows(recs, lo, hi):
    return [r for r in recs if r["kind"] == "operating" and r["ym"] and lo <= r["ym"] <= hi]


def gate(sep):
    """G2 on the September records: no 2026 coal retirement, and the 9 recorded units, months and MW."""
    win = window_rows(sep, *G2_WINDOW)
    got = {}
    for r in win:
        got.setdefault(r["key"], r["ym"])
    rows = []
    for k in sorted(set(G2_UNITS) | set(got)):
        want, have = G2_UNITS.get(k, "(not recorded)"), got.get(k, "(not dated 2026-10 to 2026-12)")
        rows.append({"key": k, "recorded": want, "september": have, "match": want == have})
    ret26 = retired_in(sep, "2026")
    total = round(sum(r["mw"] for r in win), 1)
    same_mw = abs(total - G2_MW) < 0.05
    return {"retired_2026": ret26, "unit_rows": rows, "units": len(win), "mw": total, "need_mw": G2_MW,
            "units_match": all(r["match"] for r in rows) and len(win) == len(G2_UNITS), "mw_match": same_mw,
            "held": not ret26 and all(r["match"] for r in rows) and len(win) == len(G2_UNITS) and same_mw}


def overdue(recs, before=O2_BEFORE):
    """Operating coal units whose planned month is before `before`."""
    return sorted((r for r in recs if r["kind"] == "operating" and r["ym"] and r["ym"] < before),
                  key=lambda r: (r["ym"], r["key"]))


def predictions(octo):
    op, ret = index(octo, "operating"), index(octo, "retired")
    o1_rows = retired_in(octo, "2026")
    o2_rows = overdue(octo)
    plan_retired = sorted(k for k in PLAN if k in ret)
    still = {k: (op[k]["ym"] if k in op else "(not on Operating sheet)") for k in O3_STILL_2026}
    o3 = not plan_retired and all(still[k] == v for k, v in O3_STILL_2026.items())
    return {"O1": {"held": not o1_rows, "retired_2026": o1_rows},
            "O2": {"held": not o2_rows, "overdue": o2_rows},
            "O3": {"held": o3, "plan_retired": plan_retired, "still": still}}


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


def state_of(recs):
    """{key: 'retired YYYY-MM' or 'operating YYYY-MM|no date'}; a Retired row wins over an Operating one."""
    out = {}
    for r in recs:
        s = "%s %s" % (r["kind"], r["ym"] or "no date")
        if r["kind"] == "retired" or r["key"] not in out:
            out[r["key"]] = s
    return out


def changes(sep, octo):
    """Coal units whose state differs between the two workbooks (Retired rows before 2026 ignored)."""
    a, s = state_of(sep), state_of(octo)
    names = {}
    for r in sep + octo:
        names[r["key"]] = (r["plant_name"], r["state"], r["mw"])
    out = []
    for k in sorted(set(a) | set(s)):
        before, after = a.get(k, "absent"), s.get(k, "absent")
        if before == after:
            continue
        if all(x == "absent" or (x.startswith("retired") and x[8:12] < "2026") for x in (before, after)):
            continue
        n = names[k]
        out.append({"key": k, "plant": n[0], "state": n[1], "mw": round(n[2], 1), "september": before,
                    "october": after})
    return out


def recent(recs, start=RECENT_FROM):
    return sorted((r for r in recs if r["kind"] == "retired" and r["ym"] >= start),
                  key=lambda r: (r["ym"], r["key"]))


def campbell(recs):
    st = state_of(recs)
    return {k: st.get(k, "absent") for k in CAMPBELL}


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
        return "not scored (G2 failed)"
    return "held" if held else "failed"


def mwf(x):
    return "{:,.1f}".format(x)


def same_text(same):
    return "not recorded in advance" if same is None else str(same)


def render(res):
    g, p = res["gate"], res["predictions"]
    md = ["# Coal in EIA's October 2026 EIA-860M workbook (coaloct %s)" % __version__, ""]
    for label in ("october", "september"):
        f = res["files"][label]
        md.append("- %s 2026: %s, %s bytes, md5 %s (same as recorded earlier: %s)" % (
            label.capitalize(), f["url"], "{:,}".format(f["size"]), f["md5"], same_text(f["same_as_recorded"])))
    md += ["", "Coal rows read: October %s, September %s." % ("{:,}".format(res["counts"]["october"]),
                                                           "{:,}".format(res["counts"]["september"])),
           "", "## Gate G2: the September workbook reproduces job coalsep-v1", "",
           "- Coal rows on September's Retired sheet with retirement year 2026: %d" % len(g["retired_2026"]),
           "- Operating coal dated 2026-10 to 2026-12: %d units, %s MW (recorded: %d units, %s MW)" % (
               g["units"], mwf(g["mw"]), len(G2_UNITS), mwf(g["need_mw"])),
           "- G2: **%s**" % ("held" if g["held"] else "FAILED"), "",
           "| key | coalsep-v1 | September workbook now | match |", "|---|---|---|---|"]
    for r in g["unit_rows"]:
        md.append("| %s | %s | %s | %s |" % (r["key"], r["recorded"], r["september"], "yes" if r["match"] else "no"))
    for r in g["retired_2026"]:
        md.append("")
        md.append("September Retired-sheet coal row in 2026: %s %s (%s), %s, %s MW" % (
            r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"])))
    o1, o2, o3 = p["O1"], p["O2"], p["O3"]
    md += ["", "## Predictions (docs/coaloct-plan.md), October 2026 workbook", "",
           "| # | prediction | result | verdict |", "|---|---|---|---|",
           "| O1 | no coal row on the Retired sheet has retirement year 2026 | %d rows | %s |" % (
               len(o1["retired_2026"]), verdict(o1["held"], g["held"])),
           "| O2 | no coal unit on the Operating sheet is dated before %s | %d units | %s |" % (
               O2_BEFORE, len(o2["overdue"]), verdict(o2["held"], g["held"])),
           "| O3 | none of the 16 plan generators retired; Sherburne County 1 and Comanche 2 still dated 2026-12 "
           "| retired: %s; 6090/1: %s; 470/2: %s | %s |" % (
               ", ".join(o3["plan_retired"]) or "none", o3["still"]["6090/1"], o3["still"]["470/2"],
               verdict(o3["held"], g["held"]))]
    if o1["retired_2026"]:
        md += ["", "### October Retired-sheet coal rows in 2026", "",
               "| key | plant | state | retired | MW |", "|---|---|---|---|---|"]
        md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
               for r in o1["retired_2026"]]
    md += ["", "### Operating coal dated before %s (past its planned month), October 2026 workbook" % O2_BEFORE, "",
           "| key | plant | state | planned | MW |", "|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
           for r in o2["overdue"]] or ["| none | | | | |"]
    md += ["", "## Described, not scored", "",
           "### J.H. Campbell 1-3 in the October 2026 workbook (beside forecast R3; not a test of it)", "",
           "| key | October workbook |", "|---|---|"]
    md += ["| %s | %s |" % (k, v) for k, v in sorted(res["campbell"].items())]
    md += ["", "### Operating coal dated to retire %s to %s, by plant (October 2026 workbook)" % AHEAD, "",
           "| plant | state | plant ID | units | MW | months | DOE 202(c) order |", "|---|---|---|---|---|---|---|"]
    rows = res["ahead"]
    md += ["| %s | %s | %s | %s | %s | %s | %s |" % (a["plant"], a["state"], a["plant_id"], a["units"], mwf(a["mw"]),
                                                    a["months"], a["doe_order"]) for a in rows]
    md += ["", "%d plants, %s MW; %s MW at plants under DOE orders." % (
        len(rows), mwf(sum(a["mw"] for a in rows)), mwf(sum(a["mw"] for a in rows if a["doe_order"] == "yes")))]
    md += ["", "### Coal units whose record changed from September to October 2026", "",
           "| key | plant | state | MW | September | October |", "|---|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s | %s |" % (c["key"], c["plant"], c["state"], mwf(c["mw"]), c["september"],
                                               c["october"]) for c in res["changes"]] or ["| none | | | | | |"]
    md += ["", "### Coal on the October Retired sheet with retirement year 2025 or later", "",
           "| key | plant | state | retired | MW |", "|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | %s |" % (r["key"], r["plant_name"], r["state"], r["ym"], mwf(r["mw"]))
           for r in res["retired_recent"]] or ["| none | | | | |"]
    md += ["", "October: %d rows; September: %d rows." % (len(res["retired_recent"]), res["retired_recent_september"])]
    md += ["", "### Sheets read", ""]
    for label in ("october", "september"):
        for sheet, inf in sorted(res["sheets"][label].items()):
            if inf is None:
                md.append("- %s / %s: not read" % (label, sheet))
            else:
                md.append("- %s / %s: header row %d, %s rows, %s coal; columns missing: %s" % (
                    label, sheet, inf["header_row"], "{:,}".format(inf["rows"]), "{:,}".format(inf["coal_rows"]),
                    ", ".join(inf["columns_missing"]) or "none"))
    return "\n".join(md) + "\n"


def analyse(octo, sep):
    return {"gate": gate(sep), "predictions": predictions(octo), "campbell": campbell(octo), "ahead": ahead(octo),
            "changes": changes(sep, octo), "retired_recent": recent(octo),
            "retired_recent_september": len(recent(sep))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--work-dir", default=".")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"version": __version__, "files": {}, "sheets": {}, "counts": {}}
    recs = {}
    for label, (name, known_md5, known_size), archive_first in (("october", OCT, False), ("september", SEPT, True)):
        dest = os.path.join(a.work_dir, name)
        url, size, md5, errors = fetch(name, dest, archive_first)
        if url is None:
            raise SystemExit("could not download %s: %s" % (name, errors))
        same = None if known_md5 is None else (md5 == known_md5 and size == known_size)
        res["files"][label] = {"url": url, "size": size, "md5": md5, "same_as_recorded": same, "errors": errors}
        print("%s: %s %d bytes md5 %s (same as recorded: %s)" % (label, url, size, md5, same_text(same)), flush=True)
        recs[label], res["sheets"][label] = read_workbook(dest)
        res["counts"][label] = len(recs[label])
        print("%s: %d coal rows" % (label, len(recs[label])), flush=True)
    res.update(analyse(recs["october"], recs["september"]))
    with open(os.path.join(a.out_dir, "coaloct.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    md = render(res)
    with open(os.path.join(a.out_dir, "coaloct.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
