"""retiredscope: which generators leave EIA-860M's Retired sheet and never come back, and why?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive follow-up to gapcensus-v1 (docs/gapcensus-v1-output.md); no prediction is tested.
gapcensus-v1 found 279 generators that left the Retired sheet of EIA's monthly EIA-860M workbook
and were not listed again on any sheet by August 2026: 238 in March 2017 and 41 later. EIA's
EIA-860M page says that "starting with March 2017 data" the Retired tab "includes a comprehensive
list of generators which retired since 2002". This reads, from PUDL's archive (Zenodo record
22995197, md5-checked as layouts.py 0.1.0 checks it) with retiredgap.py 0.1.0's sheet reader:

- February and March 2017: the Retired sheet's rows and retirement years in each month, the
  generators that left it (their retirement years, MW, technologies and where March lists them)
  and those that entered it from no sheet, plus the text above each Retired sheet's header row;
- for each of the 41 later leavers (LEAVERS, from gapcensus-v1's gapcensus_left_events.csv), the
  workbook of the month before and of the month it left: its retirement year, MW, technology and
  state, every sheet of the later workbook that lists it (Canceled or Postponed and *_PR
  included), and the plant's generators listed in the later month but not the month before
  (possible renamed generators);
- for COMPARE months, EIA's own file (honest User-Agent, two seconds apart): bytes and md5
  against the archive's copy.

    python retiredscope.py --data-dir /data --out-dir /out
"""

import argparse
import collections
import csv
import io
import json
import os
import time
import urllib.request
import zipfile

import pandas as pd

import layouts as ly
import retiredgap as rg

__version__ = "0.1.0"
SINCE = 2002
SCOPE = ("2017-02", "2017-03")
COMPARE = ("2017-02", "2017-03", "2023-12", "2024-01")
TOP = 10
UA = "mv2-munim-retiredscope/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
# gapcensus-v1 (gapcensus_left_events.csv): left the Retired sheet after March 2017, not back by 2026-08
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


def prev_month(month):
    y, m = (int(x) for x in month.split("-"))
    return "%04d-%02d" % ((y, m - 1) if m > 1 else (y - 1, 12))


def months_needed():
    want = set(SCOPE)
    for m, _ in LEAVERS:
        want.update((prev_month(m), m))
    return sorted(want)


def year_of(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def year_bin(v):
    y = year_of(v)
    return "missing" if y is None else "before %d" % SINCE if y < SINCE else "%d or later" % SINCE


def is_retired(name):
    return str(name).strip().lower().startswith("retired") and rg.route(name)


def title_cells(raw):
    """Text cells above a sheet's header row (all of the first 15 rows when it has none)."""
    rows = raw.values.tolist()
    h = rg.find_header(rows)
    out = []
    for row in rows[:15 if h is None else h]:
        out += [str(c).strip() for c in row if c is not None and c == c and str(c).strip()]
    return out


def book_from_sheets(sheets):
    """{sheet name: DataFrame read with header=None} -> (book as retiredgap.read_book gives it,
    {sheet name: title cells})."""
    return ([rg.book_sheet(n, raw) for n, raw in sheets.items()],
            {str(n): title_cells(raw) for n, raw in sheets.items()})


def retired(book):
    """{key: fields} over the Retired sheet(s) the route reads; the first sheet listing a key wins."""
    out = {}
    for s in book:
        if is_retired(s["sheet"]):
            for k, v in s["keys"].items():
                out.setdefault(k, v)
    return out


def where(book, key):
    """Every sheet of a book that lists the key (the left-out ones included), joined with '+'."""
    return "+".join(s["sheet"] for s in book if key in s["keys"]) or "not listed"


def summary(fields):
    fields = list(fields)
    return {"n": len(fields),
            "bins": rg.counts(year_bin(f.get("retirement_year")) for f in fields),
            "years": rg.counts(year_of(f.get("retirement_year")) for f in fields),
            "mw": round(sum(rg.num(f.get("nameplate_mw")) for f in fields), 1),
            "technology": rg.counts((f.get("technology") for f in fields), TOP),
            "state": rg.counts((f.get("state") for f in fields), TOP)}


def scope(before, after):
    """Two months' books -> how the Retired sheet changed between them."""
    b_ret, a_ret = retired(before), retired(after)
    b_all, a_all = rg.keyset(before), rg.keyset(after)
    left = sorted(k for k in b_ret if k not in a_all)
    entered = sorted(k for k in a_ret if k not in b_all)
    moved_in = sorted(k for k in a_ret if k in b_all and k not in b_ret)
    return {"retired_rows": [sum(s["rows"] for s in b if is_retired(s["sheet"])) for b in (before, after)],
            "retired_keys": [len(b_ret), len(a_ret)],
            "retired_bins": [rg.counts(year_bin(f.get("retirement_year")) for f in r.values())
                             for r in (b_ret, a_ret)],
            "left": summary(b_ret[k] for k in left),
            "left_where": rg.counts(where(after, k) for k in left),
            "entered": summary(a_ret[k] for k in entered),
            "moved_in": len(moved_in),
            "left_keys": left}


def leaver(before, after, key):
    """One generator that left between two months' books -> what the books say about it."""
    b_all, a_all = rg.keyset(before), rg.keyset(after)
    sheet, f = b_all.get(key, (None, {}))
    plant = key.split("/")[0]
    new = sorted(k for k in a_all if k.split("/")[0] == plant and k not in b_all)
    return {"key": key, "sheet_before": sheet, "retirement_year": year_of(f.get("retirement_year")),
            "retirement_month": year_of(f.get("retirement_month")), "technology": f.get("technology"),
            "state": f.get("state"), "nameplate_mw": f.get("nameplate_mw"),
            "listed_after": key in a_all, "where_after": where(after, key),
            "plant_keys": [sum(1 for k in d if k.split("/")[0] == plant) for d in (b_all, a_all)],
            "new_at_plant": [{"key": k, "sheet": a_all[k][0],
                              "retirement_year": year_of(a_all[k][1].get("retirement_year")),
                              "technology": a_all[k][1].get("technology"),
                              "nameplate_mw": a_all[k][1].get("nameplate_mw")} for k in new]}


def consistent(e):
    """Does the book agree with gapcensus-v1: on the Retired sheet before, on no routed sheet after?"""
    return bool(e["sheet_before"]) and is_retired(e["sheet_before"]) and not e["listed_after"]


def _get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _cell(v):
    return "-" if v is None else str(v)


def _tally(entries):
    return "; ".join("%s %d" % (x["value"], x["n"]) for x in entries) or "none"


def render(result):
    md = ["# retiredscope %s: generators that leave EIA-860M's Retired sheet for good" % __version__, "",
          "Descriptive follow-up to gapcensus-v1; no prediction is tested. MV2 of Munim, Inc. "
          "(made with AI agents).", ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    md += ["## Files", "", "| month | archive member | archive bytes | archive md5 | EIA bytes | EIA md5 | same file |",
           "|---|---|---|---|---|---|---|"]
    for f in result["files"]:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            f["month"], f.get("member"), f.get("bytes"), f.get("md5"), _cell(f.get("eia_bytes")),
            _cell(f.get("eia_md5")), _cell(f.get("same_file"))))
    errs = ["%s %s" % (f["month"], e) for f in result["files"] for e in f.get("errors", [])]
    md += ["", "Errors: %s." % ("; ".join(errs) or "none"), ""]
    s = result.get("scope")
    if s:
        a, b = SCOPE
        md += ["## The Retired sheet, %s to %s" % (a, b), "",
               "Retired sheet rows: %s %d, %s %d. Keys: %d, %d." % (
                   a, s["retired_rows"][0], b, s["retired_rows"][1], s["retired_keys"][0], s["retired_keys"][1]), "",
               "Retirement years on the sheet, %s: %s." % (a, _tally(s["retired_bins"][0])), "",
               "Retirement years on the sheet, %s: %s." % (b, _tally(s["retired_bins"][1])), "",
               "Left the Retired sheet and listed on no sheet the route reads in %s: %d (%s MW). "
               "Retirement years: %s." % (b, s["left"]["n"], s["left"]["mw"], _tally(s["left"]["bins"])), "",
               "Where %s lists them: %s." % (b, _tally(s["left_where"])), "",
               "Their retirement years, all: %s." % _tally(sorted(s["left"]["years"], key=lambda x: x["value"])), "",
               "Their technologies (top %d): %s." % (TOP, _tally(s["left"]["technology"])), "",
               "Their states (top %d): %s." % (TOP, _tally(s["left"]["state"])), "",
               "Entered the Retired sheet in %s from no sheet: %d (%s MW). Retirement years: %s." % (
                   b, s["entered"]["n"], s["entered"]["mw"], _tally(s["entered"]["bins"])), "",
               "Moved to the Retired sheet from another sheet: %d." % s["moved_in"], ""]
        for m in SCOPE:
            md += ["Text above the Retired sheet's header, %s: %s" % (
                m, " / ".join(result["titles"].get(m, [])) or "none"), ""]
    md += ["## Later leavers (%d, from gapcensus-v1)" % len(result["leavers"]), "",
           "Consistent with gapcensus-v1 (Retired the month before, on no routed sheet the month it left): %d of %d." % (
               sum(1 for e in result["leavers"] if e["consistent"]), len(result["leavers"])), "",
           "Retirement years: %s." % _tally(rg.counts(year_bin(e["retirement_year"]) for e in result["leavers"])), "",
           "| left | key | retirement | technology | state | MW | where listed after | plant keys before, after "
           "| new keys at the plant |", "|---|---|---|---|---|---|---|---|---|"]
    for e in result["leavers"]:
        md.append("| %s | %s | %s-%s | %s | %s | %s | %s | %d, %d | %s |" % (
            e["month"], e["key"], _cell(e["retirement_year"]), _cell(e["retirement_month"]), _cell(e["technology"]),
            _cell(e["state"]), _cell(e["nameplate_mw"]), e["where_after"], e["plant_keys"][0], e["plant_keys"][1],
            ", ".join("%s (%s, %s, %s MW)" % (x["key"], x["sheet"], _cell(x["retirement_year"]), _cell(x["nameplate_mw"]))
                      for x in e["new_at_plant"]) or "none"))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "retiredgap": rg.__version__, "user_agent": UA, "started_at": now()}
    books, titles, files, zips = {}, {}, [], {}
    fetched = 0
    for m in months_needed():
        year = int(m[:4])
        f = {"month": m, "errors": []}
        if year not in zips:
            zips[year] = ly.get_zip(year, args.data_dir, ly.ZIP_MD5.get(year), None)
        path, z = zips[year]
        f["zip_md5_matches_page"] = bool(z.get("md5_matches_page"))
        if path is None:
            f["errors"].append("zip not available")
            files.append(f)
            continue
        with zipfile.ZipFile(path) as zf:
            member = rg.member_for(zf.namelist(), m)
            data = zf.read(member) if member else None
        f.update(member=member, bytes=len(data) if data else None, md5=rg.md5(data) if data else None)
        if data is None:
            f["errors"].append("no workbook in the zip")
            files.append(f)
            continue
        try:
            sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
            books[m], notes = book_from_sheets(sheets)
            titles[m] = next((v for n, v in notes.items() if is_retired(n)), [])
            f["sheets"] = [{"sheet": s["sheet"], "rows": s["rows"], "route": s["route"]} for s in books[m]]
        except Exception as ex:  # recorded, not raised
            f["errors"].append("not read: %s: %s" % (type(ex).__name__, ex))
        if m in COMPARE:
            if fetched:
                time.sleep(2)
            fetched += 1
            eia, url, errors = rg.download(rg.eia_urls(m), get=_get)
            f["errors"] += errors
            f.update(eia_url=url, eia_bytes=len(eia) if eia else None, eia_md5=rg.md5(eia) if eia else None,
                     same_file=bool(eia) and rg.md5(eia) == f["md5"])
        print("%s member %s bytes %s errors %s" % (m, member, f["bytes"], f["errors"]), flush=True)
        files.append(f)
    result["files"], result["titles"] = files, titles
    if all(m in books for m in SCOPE):
        result["scope"] = scope(books[SCOPE[0]], books[SCOPE[1]])
    out = []
    for m, k in LEAVERS:
        p = prev_month(m)
        if p in books and m in books:
            e = dict({"month": m}, **leaver(books[p], books[m], k))
            e["consistent"] = consistent(e)
            out.append(e)
    result["leavers"] = out
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "retiredscope.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "retiredscope_leavers.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month_left", "key", "retirement_year", "retirement_month", "technology", "state",
                    "nameplate_mw", "where_listed_after", "plant_keys_before", "plant_keys_after", "new_keys_at_plant"])
        for e in out:
            w.writerow([e["month"], e["key"], _cell(e["retirement_year"]), _cell(e["retirement_month"]),
                        _cell(e["technology"]), _cell(e["state"]), _cell(e["nameplate_mw"]), e["where_after"],
                        e["plant_keys"][0], e["plant_keys"][1], " ".join(x["key"] for x in e["new_at_plant"])])
    if "scope" in result:
        s, ret = result["scope"], retired(books[SCOPE[0]])
        with open(os.path.join(args.out_dir, "retiredscope_2017_03_left.csv"), "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "retirement_year", "where_listed_2017_03"])
            for k in s["left_keys"]:
                w.writerow([k, _cell(year_of(ret[k].get("retirement_year"))), where(books[SCOPE[1]], k)])
    md = render(result)
    with open(os.path.join(args.out_dir, "retiredscope.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
