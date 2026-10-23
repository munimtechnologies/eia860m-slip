"""sepretired: the 16 generators that left EIA-860M's Retired sheet in September 2026.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/sepretired-plan.md (S1 and S2; S3 waits for EIA's October 2026 workbook).
Job monthcheck-sep2026-v1 found that 16 generators on the August 2026 Retired sheet are on no sheet
the rebuilt changelog reads in EIA's September 2026 workbook (bar P3 of docs/sep2026-plan.md failed).
For each of them this reports what August's Retired sheet says (plant name, state, technology,
retirement month and year, nameplate MW), every sheet of the September workbook that lists it
(Canceled or Postponed and the *_PR sheets included), how many generators of its plant each sheet
lists in August and September, and where the annual EIA-860 2025 file lists it. It also compares the
two Retired sheets as wholes and repeats annual860's census (annual 2025 against the monthly
workbook) for August and September.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing
until the plan is served, so the plan's commit time is before any number below exists.

    python sepretired.py --wait-plan --deadline 2026-10-24T06:00 --data-dir /data --out-dir /out
"""

import argparse
import calendar
import csv
import io
import json
import os
import sys
import time
import urllib.request
import zipfile

import pandas as pd

import annual860 as an
import layouts as ly
import retiredgap as rg

__version__ = "0.1.0"
AUG, SEP, YEAR = "2026-08", "2026-09", 2025
SINCE = an.SINCE
# monthcheck-sep2026-v1 (gapcensus_left_events.csv): on the Retired sheet in 2026-08, on no read sheet in 2026-09
KEYS = ("1517/1", "1645/1", "1697/1", "1729/1", "246/3", "3166/1", "360/1", "4143/5", "558/1", "566/1",
        "6107/1", "6176/1", "8011/2", "869/1", "885/1", "885/2")
EIA = "https://www.eia.gov/electricity/data/eia860m/"
SEP_URLS = [EIA + "xls/september_generator2026.xlsx", EIA + "archive/xls/september_generator2026.xlsx"]
# the file monthcheck-sep2026-v1 read on 23 October 2026
SEP_BYTES, SEP_MD5 = 14013970, "4c741eb77a5ccad5aca32ffe43f398af"
PLAN_URL = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/sepretired-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
S2_MIN = 12
S3_MAX = 3
UA = "mv2-munim-sepretired/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def deadline_ts(text):
    """'2026-10-24T06:00' (UTC) -> seconds since the epoch."""
    return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M"))


def _get(url, timeout=300):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def wait_plan(deadline, get=None, sleep=time.sleep, clock=time.time, every=600):
    """Poll PLAN_URL until it serves the plan (True) or the deadline has passed (False)."""
    while True:
        try:
            text = (get or _get)(PLAN_URL).decode("utf-8", "replace")
        except Exception as e:  # recorded, not raised
            text = "%s: %s" % (type(e).__name__, e)
        if PLAN_MARK in text:
            print("%s plan served: %s" % (now(), PLAN_URL), flush=True)
            return True
        if clock() >= deadline:
            print("%s deadline passed; plan not served" % now(), flush=True)
            return False
        print("%s plan not served yet: %s" % (now(), text[:60]), flush=True)
        sleep(every)


def plant_names(raw, plants):
    """{plant id: plant name} for the wanted plants, from one sheet read with header=None."""
    rows = raw.values.tolist()
    h = an.find_header(rows)
    if h is None:
        return {}
    low = [str(c).strip().lower() if c is not None and c == c else "" for c in rows[h]]
    if "plant name" not in low:
        return {}
    pj = next(j for j, c in enumerate(low) if c in ("plant id", "plant code"))
    nj = low.index("plant name")
    out = {}
    for r in rows[h + 1:]:
        pid = rg.plain_id(r[pj])
        if pid in plants and rg.plain(r[nj]) is not None:
            out.setdefault(pid, str(rg.plain(r[nj])))
    return out


def read_named(data, plants):
    """xlsx bytes -> (book as retiredgap.read_book gives it, {plant id: name}, None) or (None, {}, error)."""
    try:
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    except Exception as e:  # recorded, not raised
        return None, {}, "%s: %s" % (type(e).__name__, e)
    book, names = [], {}
    for n, raw in sheets.items():
        book.append(rg.book_sheet(n, raw))
        for pid, name in plant_names(raw, plants).items():
            names.setdefault(pid, name)
    return book, names, None


def read_aug(data_dir, plants):
    """August 2026 from PUDL's archive (md5-checked as layouts.py checks it) -> (file entry, book, names)."""
    year = int(AUG[:4])
    f = {"name": "EIA-860M %s" % AUG, "errors": []}
    path, z = ly.get_zip(year, data_dir, ly.ZIP_MD5.get(year), None)
    f["zip_md5_matches_page"] = bool(z.get("md5_matches_page"))
    if path is None:
        f["errors"].append("zip not available")
        return f, None, {}
    with zipfile.ZipFile(path) as zf:
        member = rg.member_for(zf.namelist(), AUG)
        data = zf.read(member) if member else None
    f.update(source="PUDL archive: %s" % member, bytes=len(data) if data else None,
             md5=rg.md5(data) if data else None)
    if data is None:
        f["errors"].append("no workbook in the zip")
        return f, None, {}
    book, names, err = read_named(data, plants)
    if err:
        f["errors"].append("not read: %s" % err)
    return f, book, names


def read_sep(plants, get=None):
    """EIA's own September 2026 file -> (file entry, book, names)."""
    f = {"name": "EIA-860M %s" % SEP}
    data, url, errors = rg.download(SEP_URLS, get=get or _get)
    f.update(source=url, errors=list(errors))
    if data is None:
        return f, None, {}
    f.update(bytes=len(data), md5=rg.md5(data))
    f["same_as_monthcheck"] = (f["bytes"], f["md5"]) == (SEP_BYTES, SEP_MD5)
    book, names, err = read_named(data, plants)
    if err:
        f["errors"].append("not read: %s" % err)
    return f, book, names


def scope(v):
    """A retirement year -> 'before 2002', '2002-2025', 'after 2025' or 'missing'."""
    y = an.year_of(v)
    if y is None:
        return "missing"
    if y < SINCE:
        return "before %d" % SINCE
    return "%d-%d" % (SINCE, YEAR) if y <= YEAR else "after %d" % YEAR


def retired_keys(book):
    """{key: fields} on the Retired sheet(s) the changelog reads (not *_PR)."""
    out = {}
    for s in book:
        if an.is_retired_sheet(s["sheet"]) and rg.route(s["sheet"]):
            for k, f in s["keys"].items():
                out.setdefault(k, f)
    return out


def plant_sheets(book, plant):
    """'Operating 3; Retired 2': how many generators of a plant each sheet lists; 'none' if none."""
    c = [(s["sheet"], sum(1 for k in s["keys"] if k.split("/")[0] == plant)) for s in book]
    return "; ".join("%s %d" % (n, k) for n, k in c if k) or "none"


def leaver_rows(keys, aug, names, sep, annual):
    """One row per key: August's Retired-sheet fields, September's sheets, the annual 2025 file."""
    a_ret = an.annual_retired(annual, YEAR) if annual is not None else {}
    on_aug = retired_keys(aug) if aug is not None else {}
    rows = []
    for k in keys:
        plant = k.split("/")[0]
        f = on_aug.get(k)
        g = f or {}
        rows.append({"key": k, "plant_name": names.get(plant), "state": g.get("state"),
                     "technology": g.get("technology"), "retirement_month": an.year_of(g.get("retirement_month")),
                     "retirement_year": an.year_of(g.get("retirement_year")),
                     "scope": scope(g.get("retirement_year")) if f is not None else "not on August's Retired sheet",
                     "nameplate_mw": g.get("nameplate_mw"),
                     "where_sep": an.where(sep, k) if sep is not None else "not read",
                     "plant_aug": plant_sheets(aug, plant) if aug is not None else "not read",
                     "plant_sep": plant_sheets(sep, plant) if sep is not None else "not read",
                     "annual": an.annual_where(annual, k) if annual is not None else "not read",
                     "annual_retired": k in a_ret})
    return rows


def score(rows, sep_ok, annual_ok, s2_min=S2_MIN):
    n = len(rows)
    out = []
    bar1 = "all %d on no sheet (Canceled or Postponed and *_PR included)" % n
    if sep_ok:
        k = sum(1 for r in rows if r["where_sep"] == "not listed")
        out.append({"id": "S1", "outcome": "held" if k == n else "failed",
                    "value": "%d of %d on no sheet of the %s workbook" % (k, n, SEP), "bar": bar1})
    else:
        out.append({"id": "S1", "outcome": "not scored", "value": "September workbook not read", "bar": bar1})
    bar2 = "at least %d of %d" % (s2_min, n)
    if annual_ok:
        k = sum(1 for r in rows if r["annual_retired"])
        out.append({"id": "S2", "outcome": "held" if k >= s2_min else "failed",
                    "value": "%d of %d listed as retired (RE, %d-%d) by the annual EIA-860 %d" % (k, n, SINCE, YEAR,
                                                                                                  YEAR),
                    "bar": bar2})
    else:
        out.append({"id": "S2", "outcome": "not scored", "value": "annual file not read", "bar": bar2})
    out.append({"id": "S3", "outcome": "not scored yet", "value": "scored on EIA's October 2026 workbook",
                "bar": "at most %d of %d listed again on a sheet the changelog reads" % (S3_MAX, n)})
    return out


def compare(aug, sep):
    """The Retired sheets of the two months as wholes."""
    a, s = retired_keys(aug), retired_keys(sep)
    left = [k for k in a if k not in s]
    entered = [k for k in s if k not in a]
    by = lambda keys, src: rg.counts(scope(src[k].get("retirement_year")) for k in keys)
    mw = lambda keys, src: round(sum(rg.num(src[k].get("nameplate_mw")) for k in keys), 1)
    return {"aug": len(a), "sep": len(s), "aug_scope": by(a, a), "sep_scope": by(s, s),
            "left": len(left), "left_mw": mw(left, a), "left_scope": by(left, a),
            "left_where_sep": rg.counts(an.where(sep, k) for k in left),
            "entered": len(entered), "entered_mw": mw(entered, s), "entered_scope": by(entered, s),
            "entered_where_aug": rg.counts(an.where(aug, k) for k in entered)}


def census_summary(c):
    return {"annual_retired": c["annual_retired"]["n"], "annual_retired_mw": c["annual_retired"]["mw"],
            "where_in_monthly": c["where_in_monthly"], "not_in_monthly": c["not_in_monthly"]["n"],
            "not_in_monthly_mw": c["not_in_monthly"]["mw"], "monthly_retired": c["monthly_retired"],
            "monthly_retired_in_scope": c["monthly_retired_in_scope"], "both": c["both"],
            "monthly_not_annual": c["monthly_not_annual"]}


_cell = an._cell
_tally = an._tally


def render(res):
    rows = res["rows"]
    md = ["# sepretired %s: the %d generators that left EIA-860M's Retired sheet in September 2026"
          % (__version__, len(rows)), "",
          "Scores docs/sepretired-plan.md (S1 and S2; S3 waits for EIA's October 2026 workbook). "
          "MV2 of Munim, Inc. (made with AI agents).", ""]
    md += ["## Files", "", "| file | source | bytes | md5 | errors |", "|---|---|---|---|---|"]
    for f in res["files"]:
        md.append("| %s | %s | %s | %s | %s |" % (f["name"], _cell(f.get("source")), _cell(f.get("bytes")),
                                                  _cell(f.get("md5")), "; ".join(f.get("errors", [])) or "none"))
    if "same_as_monthcheck" in res.get("sep_file", {}):
        md += ["", "September file is the one monthcheck-sep2026-v1 read (%d bytes, md5 %s): %s."
               % (SEP_BYTES, SEP_MD5, res["sep_file"]["same_as_monthcheck"])]
    md += ["", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    for p in res["predictions"]:
        md.append("| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]))
    scored = [p for p in res["predictions"] if p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored." % (sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## The %d" % len(rows), "",
           "| key | plant | state | technology | retired (month/year) | MW | scope | September 2026 | plant in August "
           "| plant in September | annual EIA-860 2025 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| %s | %s | %s | %s | %s/%s | %s | %s | %s | %s | %s | %s |" % (
            r["key"], _cell(r["plant_name"]), _cell(r["state"]), _cell(r["technology"]), _cell(r["retirement_month"]),
            _cell(r["retirement_year"]), _cell(r["nameplate_mw"]), r["scope"], r["where_sep"], r["plant_aug"],
            r["plant_sep"], r["annual"]))
    md += ["", "Together: %s MW on August's Retired sheet, at %d plants. Scope: %s. Retirement years: %s. "
           "Technologies: %s. States: %s." % (
               res["leavers_mw"], len({r["key"].split("/")[0] for r in rows}), _tally(rg.counts(r["scope"] for r in rows)),
               _tally(sorted(rg.counts(r["retirement_year"] for r in rows), key=lambda x: x["value"])),
               _tally(rg.counts(r["technology"] for r in rows)), _tally(rg.counts(r["state"] for r in rows)))]
    c = res.get("compare")
    if c:
        md += ["", "## The Retired sheet, August against September", "",
               "Generators on the Retired sheet: %d in %s, %d in %s. By retirement year, %s: %s; %s: %s." % (
                   c["aug"], AUG, c["sep"], SEP, AUG, _tally(c["aug_scope"]), SEP, _tally(c["sep_scope"])), "",
               "Left the sheet: %d (%s MW). By retirement year: %s. Where September lists them: %s." % (
                   c["left"], c["left_mw"], _tally(c["left_scope"]), _tally(c["left_where_sep"])), "",
               "Entered the sheet: %d (%s MW). By retirement year: %s. Where August listed them: %s." % (
                   c["entered"], c["entered_mw"], _tally(c["entered_scope"]), _tally(c["entered_where_aug"]))]
    for m, s in sorted(res.get("census", {}).items()):
        md += ["", "## Census: annual EIA-860 %d against EIA-860M %s" % (YEAR, m), "",
               "Annual retired (status RE, retired %d to %d): %d (%s MW). Where the %s workbook lists them: %s. "
               "On no sheet of it: %d (%s MW)." % (SINCE, YEAR, s["annual_retired"], s["annual_retired_mw"], m,
                                                   _tally(s["where_in_monthly"]), s["not_in_monthly"],
                                                   s["not_in_monthly_mw"]), "",
               "Monthly Retired sheet: %d generators, %d retired %d to %d; of those, %d also annual retired and %d not."
               % (s["monthly_retired"], s["monthly_retired_in_scope"], SINCE, YEAR, s["both"],
                  s["monthly_not_annual"])]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-24T06:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    plants = sorted({k.split("/")[0] for k in KEYS})
    res = {"version": __version__, "annual860": an.__version__, "retiredgap": rg.__version__, "user_agent": UA,
           "started_at": now()}
    fa, aug, names_aug = read_aug(args.data_dir, plants)
    print("august %s errors %s" % (fa.get("source"), fa["errors"]), flush=True)
    fs, sep, names_sep = read_sep(plants)
    print("september %s bytes %s md5 %s errors %s" % (fs.get("source"), fs.get("bytes"), fs.get("md5"),
                                                      fs["errors"]), flush=True)
    fy, annual = an.read_annual(YEAR, args.data_dir)
    print("annual %d bytes %s errors %s" % (YEAR, fy.get("bytes"), fy["errors"]), flush=True)
    names = dict(names_sep)
    names.update(names_aug)
    fy = dict(fy, name="EIA-860 %d (%s)" % (YEAR, fy.get("member")), source=fy.get("url") or "cached in /data")
    res["files"], res["sep_file"], res["annual_file"] = [fa, fs, fy], fs, fy
    rows = leaver_rows(KEYS, aug, names, sep, annual)
    res["rows"] = rows
    res["leavers_mw"] = round(sum(rg.num(r["nameplate_mw"]) for r in rows), 1)
    res["predictions"] = score(rows, sep is not None, annual is not None)
    if aug is not None and sep is not None:
        res["compare"] = compare(aug, sep)
    if annual is not None:
        res["census"] = {m: census_summary(an.census(annual, b, YEAR)) for m, b in ((AUG, aug), (SEP, sep))
                         if b is not None}
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "sepretired.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    cols = ["key", "plant_name", "state", "technology", "retirement_month", "retirement_year", "scope", "nameplate_mw",
            "where_sep", "plant_aug", "plant_sep", "annual", "annual_retired"]
    with open(os.path.join(args.out_dir, "sepretired_rows.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([_cell(r[c]) for c in cols])
    md = render(res)
    with open(os.path.join(args.out_dir, "sepretired.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
