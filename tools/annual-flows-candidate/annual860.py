"""annual860: does EIA's annual EIA-860 list the generators that left EIA-860M's Retired sheet?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive follow-up to retiredscope-v1 (docs/heldtrace.md); no prediction is tested.
retiredscope-v1 found 41 generators, all retired in 2002 or later by EIA-860M's own Retired sheet,
that left that sheet after March 2017 and were not listed again on any sheet the changelog reads by
August 2026, although EIA's page says the tab is "a comprehensive list of generators which retired
since 2002". This downloads EIA's annual EIA-860 files for 2020 to 2025 (eia860YYYY.zip; honest
User-Agent, two seconds apart), reads each generator workbook (3_1_Generator_YYYY) and reports:

- for each of the 41 (LEAVERS) and each year, every sheet that lists it with its status code,
  retirement year and nameplate MW, and how many generators of its plant each sheet lists;
- for CENSUS_YEAR, a census against EIA-860M's December 2025 and August 2026 workbooks (PUDL's
  archive, Zenodo record 22995197, md5-checked as layouts.py 0.1.0 checks it): the annual file's
  retired generators (status RE, retired 2002 to CENSUS_YEAR) that the monthly workbook lists on no
  sheet at all, and the monthly Retired sheet's generators retired in those years that the annual
  file does not list as retired.

    python annual860.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import io
import json
import os
import re
import time
import urllib.request
import zipfile

import pandas as pd

import layouts as ly
import retiredgap as rg

__version__ = "0.1.0"
SINCE = 2002
YEARS = (2020, 2021, 2022, 2023, 2024, 2025)
CENSUS_YEAR = 2025
MONTHLY = ("2025-12", "2026-08")
BASE = "https://www.eia.gov/electricity/data/eia860/"
UA = "mv2-munim-annual860/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
# exact header cells (lower case); exact so that "Planned Retirement Year" is never read as retirement year
FIELDS = {"status": ("status",), "retirement_year": ("retirement year",), "technology": ("technology",),
          "state": ("state", "plant state"), "nameplate_mw": ("nameplate capacity (mw)", "nameplate capacity")}
TOP = 10
# retiredscope-v1 (retiredscope_leavers.csv): left the Retired sheet after March 2017, not back by 2026-08
LEAVERS = (
    ("2020-02", "55526/GEN5"), ("2020-12", "57693/ALSTO"), ("2021-01", "57692/ALSTO"),
    ("2021-12", "1571/ST1"), ("2021-12", "1571/ST2"), ("2021-12", "1572/2"), ("2021-12", "1572/3"),
    ("2021-12", "1572/ST1"), ("2023-01", "7922/6"), ("2023-05", "59196/IC1"), ("2023-09", "64756/EQX05"),
    ("2024-01", "1439/10A"), ("2024-01", "1439/10B"), ("2024-01", "1439/11A"), ("2024-01", "1439/11B"),
    ("2024-01", "1439/12A"), ("2024-01", "1439/12B"), ("2024-01", "1439/1A"), ("2024-01", "1439/1B"),
    ("2024-01", "1439/2A"), ("2024-01", "1439/2B"), ("2024-01", "1439/3A"), ("2024-01", "1439/3B"),
    ("2024-01", "1439/4A"), ("2024-01", "1439/4B"), ("2024-01", "1439/5A"), ("2024-01", "1439/6A"),
    ("2024-01", "1439/6B"), ("2024-01", "1439/7A"), ("2024-01", "1439/7B"), ("2024-01", "1439/8A"),
    ("2024-01", "1439/8B"), ("2024-01", "1439/9A"), ("2024-01", "1439/9B"), ("2025-03", "955/3"),
    ("2025-03", "955/4"), ("2025-03", "955/IC1"), ("2025-03", "955/IC2"), ("2025-03", "955/IC3"),
    ("2025-04", "63740/ONT6"), ("2026-06", "423/3A"),
)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def urls(year):
    """Current and archive URLs of EIA's annual EIA-860 zip for a data year."""
    name = "eia860%d.zip" % year
    return [BASE + "xls/" + name, BASE + "archive/xls/" + name]


def _get(url, timeout=300):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_annual(year, data_dir, get=None):
    """eia860YYYY.zip -> (path or None, info). A copy kept in data_dir is used when it is a zip file."""
    folder = os.path.join(data_dir, "eia860-annual")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "eia860%d.zip" % year)
    info = {"year": year, "file": os.path.basename(path), "cached": False, "url": None, "errors": []}
    if os.path.exists(path) and zipfile.is_zipfile(path):
        info["cached"] = True
    else:
        data, url, errors = rg.download(urls(year), get=get or _get)
        info.update(url=url, errors=errors)
        if data is None:
            return None, info
        with open(path, "wb") as fh:
            fh.write(data)
    with open(path, "rb") as fh:
        data = fh.read()
    info.update(bytes=len(data), md5=rg.md5(data))
    return path, info


def member_3_1(names, year):
    """The zip member holding the year's generator workbook (3_1_Generator_YYYY.xlsx)."""
    base = lambda n: n.rsplit("/", 1)[-1].lower()
    hits = [n for n in names if re.search(r"^3_1_generator_y%d\.xlsx?$" % year, base(n))]
    if not hits:
        hits = [n for n in names if base(n).startswith("3_1_generator")]
    hits.sort(key=lambda n: (len(n), n))
    return hits[0] if hits else None


def year_of(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def year_bin(v):
    y = year_of(v)
    return "missing" if y is None else "before %d" % SINCE if y < SINCE else "%d or later" % SINCE


def code(v):
    """A status cell -> its code ('RE', '(RE) Retired' -> 'RE'); None when missing."""
    p = rg.plain(v)
    if p is None:
        return None
    m = re.match(r"\(?([A-Za-z]+)\)?", str(p))
    return m.group(1).upper() if m else str(p)


def find_header(rows, limit=15):
    """Index of the first row with cells 'Plant Code' (or 'Plant ID') and 'Generator ID', else None."""
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip().lower() for c in row if c is not None and c == c}
        if ("plant code" in cells or "plant id" in cells) and "generator id" in cells:
            return i
    return None


def annual_sheet(name, raw):
    """One sheet of the annual workbook read with header=None -> {sheet, header_row, rows,
    keys: {key: fields}}; only rows with a whole-number plant code count."""
    rows = raw.values.tolist()
    h = find_header(rows)
    entry = {"sheet": str(name), "header_row": h, "rows": 0, "keys": {}}
    if h is None:
        return entry
    low = [str(c).strip().lower() if c is not None and c == c else "" for c in rows[h]]
    pj = next(j for j, c in enumerate(low) if c in ("plant code", "plant id"))
    gj = low.index("generator id")
    pick = {f: next((j for j, c in enumerate(low) if c in names), None) for f, names in FIELDS.items()}
    for r in rows[h + 1:]:
        pid = rg.plain_id(r[pj])
        if pid is None or not pid.isdigit():
            continue
        entry["rows"] += 1
        key = "%s/%s" % (pid, rg.gen_id(r[gj]))
        entry["keys"].setdefault(key, {f: None if j is None else rg.plain(r[j]) for f, j in pick.items()})
    return entry


def is_retired_sheet(name):
    return str(name).strip().lower().startswith("retired")


def annual_where(book, key):
    """Every sheet of an annual book that lists the key, with its status code, joined with '+'."""
    return "+".join("%s %s" % (s["sheet"], code(s["keys"][key].get("status")) or "-")
                    for s in book if key in s["keys"]) or "not listed"


def where(book, key):
    """Every sheet of a monthly book that lists the key (the left-out ones included), joined with '+'."""
    return "+".join(s["sheet"] for s in book if key in s["keys"]) or "not listed"


def annual_retired(book, year):
    """{key: fields} the annual file lists as retired (status RE on a Retired sheet), retired SINCE..year."""
    out = {}
    for s in book:
        if is_retired_sheet(s["sheet"]):
            for k, f in s["keys"].items():
                y = year_of(f.get("retirement_year"))
                if code(f.get("status")) == "RE" and y is not None and SINCE <= y <= year:
                    out.setdefault(k, f)
    return out


def retired_sheet_tallies(book):
    """Status codes on the annual Retired sheet(s), and retirement-year bins of the RE rows."""
    fields = [f for s in book if is_retired_sheet(s["sheet"]) for f in s["keys"].values()]
    return {"status": rg.counts(code(f.get("status")) for f in fields),
            "re_bins": rg.counts(year_bin(f.get("retirement_year")) for f in fields
                                 if code(f.get("status")) == "RE")}


def summary(fields):
    fields = list(fields)
    return {"n": len(fields),
            "bins": rg.counts(year_bin(f.get("retirement_year")) for f in fields),
            "years": rg.counts(year_of(f.get("retirement_year")) for f in fields),
            "mw": round(sum(rg.num(f.get("nameplate_mw")) for f in fields), 1),
            "technology": rg.counts((f.get("technology") for f in fields), TOP),
            "state": rg.counts((f.get("state") for f in fields), TOP)}


def census(annual, monthly, year):
    """The annual book of a data year against one monthly book."""
    a_ret = annual_retired(annual, year)
    m_ret = {}
    for s in monthly:
        if is_retired_sheet(s["sheet"]) and rg.route(s["sheet"]):
            for k, f in s["keys"].items():
                m_ret.setdefault(k, f)
    m_old = {k: f for k, f in m_ret.items()
             if year_of(f.get("retirement_year")) is not None and SINCE <= year_of(f.get("retirement_year")) <= year}
    where_m = {k: where(monthly, k) for k in a_ret}
    missing = sorted(k for k, w in where_m.items() if w == "not listed")
    a_where = {k: annual_where(annual, k) for k in m_old if k not in a_ret}
    both = [k for k in a_ret if k in m_old]
    return {"annual_retired": summary(a_ret.values()),
            "monthly_retired": len(m_ret), "monthly_retired_in_scope": len(m_old),
            "where_in_monthly": rg.counts(where_m.values()),
            "not_in_monthly": summary(a_ret[k] for k in missing),
            "not_in_monthly_rows": [dict({"key": k}, **a_ret[k]) for k in missing],
            "monthly_not_annual": len(a_where),
            "monthly_not_annual_where": rg.counts(a_where.values()),
            "monthly_not_annual_rows": [{"key": k, "where_annual": a_where[k],
                                         "retirement_year": year_of(m_old[k].get("retirement_year")),
                                         "nameplate_mw": m_old[k].get("nameplate_mw")} for k in sorted(a_where)],
            "both": len(both),
            "same_year": sum(1 for k in both if year_of(a_ret[k].get("retirement_year")) ==
                             year_of(m_old[k].get("retirement_year")))}


def leaver_row(book, year, key):
    """What one year's annual book says about one generator and its plant."""
    plant = key.split("/")[0]
    hit = [s["keys"][key] for s in book if key in s["keys"]]
    f = hit[0] if hit else {}
    return {"year": year, "where": annual_where(book, key), "retirement_year": year_of(f.get("retirement_year")),
            "nameplate_mw": f.get("nameplate_mw"),
            "plant": {s["sheet"]: sum(1 for k in s["keys"] if k.split("/")[0] == plant) for s in book}}


def _cell(v):
    return "-" if v is None else str(v)


def _tally(entries):
    return "; ".join("%s %d" % (x["value"], x["n"]) for x in entries) or "none"


def render(result):
    md = ["# annual860 %s: EIA's annual EIA-860 and the generators that left EIA-860M's Retired sheet" % __version__,
          "", "Descriptive follow-up to retiredscope-v1; no prediction is tested. MV2 of Munim, Inc. "
          "(made with AI agents).", ""]
    md += ["## Annual files", "", "| year | url | cached | bytes | md5 | member | sheets (rows) | errors |",
           "|---|---|---|---|---|---|---|---|"]
    for f in result["files"]:
        md.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (
            f["year"], _cell(f.get("url")), f.get("cached"), _cell(f.get("bytes")), _cell(f.get("md5")),
            _cell(f.get("member")), "; ".join("%s %d" % (s["sheet"], s["rows"]) for s in f.get("sheets", []))
            or "not read", "; ".join(f.get("errors", [])) or "none"))
    md += ["", "## Retired sheets of the annual files", "", "| year | status codes | retirement years of RE rows |",
           "|---|---|---|"]
    for f in result["files"]:
        t = f.get("retired_sheet")
        if t:
            md.append("| %d | %s | %s |" % (f["year"], _tally(t["status"]), _tally(t["re_bins"])))
    md += ["", "## Monthly files", "", "| month | member | bytes | md5 | errors |", "|---|---|---|---|---|"]
    for f in result["monthly_files"]:
        md.append("| %s | %s | %s | %s | %s |" % (f["month"], _cell(f.get("member")), _cell(f.get("bytes")),
                                                   _cell(f.get("md5")), "; ".join(f["errors"]) or "none"))
    years = [f["year"] for f in result["files"]]
    md += ["", "## The %d later leavers in the annual files" % len(result["leavers"]), "",
           "| key | left 860M | " + " | ".join(str(y) for y in years) + " |", "|---|---|" + "---|" * len(years)]
    for e in result["leavers"]:
        by = {r["year"]: r for r in e["years"]}
        md.append("| %s | %s | %s |" % (e["key"], e["month"], " | ".join(
            ("not listed" if by[y]["where"] == "not listed" else "%s (%s, %s MW)" % (
                by[y]["where"], _cell(by[y]["retirement_year"]), _cell(by[y]["nameplate_mw"])))
            if y in by else "not read" for y in years)))
    for m, c in sorted(result.get("census", {}).items()):
        y = result["census_year"]
        md += ["", "## Census: annual %d against EIA-860M %s" % (y, m), "",
               "Annual retired (status RE, retired %d to %d): %d (%s MW)." % (
                   SINCE, y, c["annual_retired"]["n"], c["annual_retired"]["mw"]), "",
               "Where the %s workbook lists them: %s." % (m, _tally(c["where_in_monthly"])), "",
               "On no sheet of the %s workbook: %d (%s MW). Retirement years: %s. Technologies (top %d): %s. "
               "States (top %d): %s." % (
                   m, c["not_in_monthly"]["n"], c["not_in_monthly"]["mw"],
                   _tally(sorted(c["not_in_monthly"]["years"], key=lambda x: x["value"])),
                   TOP, _tally(c["not_in_monthly"]["technology"]), TOP, _tally(c["not_in_monthly"]["state"])), "",
               "Monthly Retired sheet: %d generators, %d retired %d to %d; of those, %d also annual retired "
               "(same retirement year: %d) and %d not. Where the annual file lists those %d: %s." % (
                   c["monthly_retired"], c["monthly_retired_in_scope"], SINCE, y, c["both"], c["same_year"],
                   c["monthly_not_annual"], c["monthly_not_annual"], _tally(c["monthly_not_annual_where"]))]
    return "\n".join(md) + "\n"


def read_annual(year, data_dir):
    """One data year -> (file entry, book or None)."""
    path, f = get_annual(year, data_dir)
    if path is None:
        return f, None
    try:
        with zipfile.ZipFile(path) as zf:
            f["member"] = member_3_1(zf.namelist(), year)
            data = zf.read(f["member"]) if f["member"] else None
        if data is None:
            f["errors"].append("no 3_1_Generator workbook in the zip")
            return f, None
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
        book = [annual_sheet(n, raw) for n, raw in sheets.items()]
    except Exception as ex:  # recorded, not raised
        f["errors"].append("not read: %s: %s" % (type(ex).__name__, ex))
        return f, None
    f["sheets"] = [{"sheet": s["sheet"], "header_row": s["header_row"], "rows": s["rows"]} for s in book]
    f["retired_sheet"] = retired_sheet_tallies(book)
    return f, book


def read_monthly(month, data_dir):
    """One EIA-860M month from PUDL's archive -> (file entry, book or None)."""
    year = int(month[:4])
    f = {"month": month, "errors": []}
    path, z = ly.get_zip(year, data_dir, ly.ZIP_MD5.get(year), None)
    f["zip_md5_matches_page"] = bool(z.get("md5_matches_page"))
    if path is None:
        f["errors"].append("zip not available")
        return f, None
    with zipfile.ZipFile(path) as zf:
        member = rg.member_for(zf.namelist(), month)
        data = zf.read(member) if member else None
    f.update(member=member, bytes=len(data) if data else None, md5=rg.md5(data) if data else None)
    if data is None:
        f["errors"].append("no workbook in the zip")
        return f, None
    book, err = rg.read_book(data)
    if err:
        f["errors"].append("not read: %s" % err)
    return f, book


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "retiredgap": rg.__version__, "user_agent": UA, "started_at": now(),
              "census_year": CENSUS_YEAR}
    files, rows, annual = [], {k: [] for _, k in LEAVERS}, None
    for i, year in enumerate(YEARS):
        if i:
            time.sleep(2)
        f, book = read_annual(year, args.data_dir)
        if book is not None:
            for _, k in LEAVERS:
                rows[k].append(leaver_row(book, year, k))
            if year == CENSUS_YEAR:
                annual = book
        print("annual %d url %s bytes %s errors %s" % (year, f.get("url"), f.get("bytes"), f["errors"]), flush=True)
        files.append(f)
    result["files"] = files
    result["leavers"] = [{"month": m, "key": k, "years": rows[k]} for m, k in LEAVERS]
    mfiles, cen = [], {}
    for m in MONTHLY:
        f, book = read_monthly(m, args.data_dir)
        if book is not None and annual is not None:
            cen[m] = census(annual, book, CENSUS_YEAR)
        print("monthly %s member %s errors %s" % (m, f.get("member"), f["errors"]), flush=True)
        mfiles.append(f)
    result["monthly_files"], result["census"] = mfiles, cen
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "annual860.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "annual860_leavers.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month_left", "key", "year", "where_annual", "retirement_year", "nameplate_mw"])
        for e in result["leavers"]:
            for r in e["years"]:
                w.writerow([e["month"], e["key"], r["year"], r["where"], _cell(r["retirement_year"]),
                            _cell(r["nameplate_mw"])])
    with open(os.path.join(args.out_dir, "annual860_not_in_monthly.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "key", "retirement_year", "technology", "state", "nameplate_mw"])
        for m, c in sorted(cen.items()):
            for r in c["not_in_monthly_rows"]:
                w.writerow([m, r["key"], _cell(year_of(r.get("retirement_year"))), _cell(r.get("technology")),
                            _cell(r.get("state")), _cell(r.get("nameplate_mw"))])
    with open(os.path.join(args.out_dir, "annual860_monthly_not_annual.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "key", "where_annual", "retirement_year", "nameplate_mw"])
        for m, c in sorted(cen.items()):
            for r in c["monthly_not_annual_rows"]:
                w.writerow([m, r["key"], r["where_annual"], _cell(r["retirement_year"]), _cell(r["nameplate_mw"])])
    md = render(result)
    with open(os.path.join(args.out_dir, "annual860.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
