"""retiredentry: when did the 16 pre-2002 nuclear generators reach EIA-860M's "since 2002" Retired sheet?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Scores docs/retiredentry-plan.md (R1 to R4). Job sepretired-v1 found that the 16 generators that left
the Retired sheet of EIA's September 2026 EIA-860M workbook are all nuclear units that August's sheet
lists as retired before 2002, and that September's Retired sheet lists no generator retired before
2002. Job retiredscope-v1 found that March 2017's Retired sheet listed none either. This reads the
rebuilt changelog (data/eia860m_changelog_from_workbooks.csv.gz 0.1.1, pinned to commit a3ce085) for
every row of the 16 and finds the month each first reached the Retired sheet. It then reads that
month's workbook and the month before from PUDL's archive (md5-checked as layouts.py checks it), plus
July, August and September 2026 (September from EIA's own site), with retiredgap.py's sheet reader:
each generator's retirement year, technology and MW, and the Retired sheet's rows by retirement year.
In the same workbooks it lists every row on every sheet whose technology names nuclear, plant id or
not, so rows the sheet reader skips are counted too.

With --wait-plan it first polls the plan's address on GitHub every 10 minutes and computes nothing
until the plan is served, so the plan's commit time is before any number below exists.

    python retiredentry.py --wait-plan --deadline 2026-10-24T12:00 --data-dir /data --out-dir /out
"""

import argparse
import calendar
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
import zipfile

import pandas as pd

import layouts as ly
import retiredgap as rg
import retiredscope as rs

__version__ = "0.1.0"
SHA = "a3ce0851c47d820ba5f8a0556358b4abef960909"
LOG_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/%s/data/"
           "eia860m_changelog_from_workbooks.csv.gz" % SHA)
# the 0.1.1 file at that commit (GitHub contents API) and its row count (test_sep2026_doc.py)
LOG_BYTES, LOG_ROWS = 1054060, 117756
PLAN_URL = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/docs/retiredentry-plan.md"
PLAN_MARK = "Status: pre-registered, not yet scored."
FIRST, JUL, AUG, SEP = "2015-07", "2026-07", "2026-08", "2026-09"
SCAN = (JUL, AUG, SEP)
EIA = "https://www.eia.gov/electricity/data/eia860m/"
SEP_URLS = [EIA + "xls/september_generator2026.xlsx", EIA + "archive/xls/september_generator2026.xlsx"]
# the file monthcheck-sep2026-v1 and sepretired-v1 read on 23 October 2026
SEP_BYTES, SEP_MD5 = 14013970, "4c741eb77a5ccad5aca32ffe43f398af"
# sepretired-v1 (sepretired_rows.csv): retirement year on August 2026's Retired sheet
AUG_YEARS = {"1517/1": 1997, "1645/1": 1992, "1697/1": 1997, "1729/1": 1972, "246/3": 1985, "3166/1": 1975,
             "360/1": 1992, "4143/5": 1987, "558/1": 1996, "566/1": 1998, "6107/1": 1993, "6176/1": 1990,
             "8011/2": 1979, "869/1": 1985, "885/1": 1998, "885/2": 1998}
KEYS = tuple(sorted(AUG_YEARS))
# plants a third-party website names as newly listed in EIA-860M August 2026 (see the plan)
WATCH = ("shippingport", "vallecitos", "saxton", "piqua")
UA = "mv2-munim-retiredentry/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def deadline_ts(text):
    """'2026-10-24T12:00' (UTC) -> seconds since the epoch."""
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


def months(a=FIRST, b=SEP):
    """Every month from a to b, YYYY-MM."""
    out, y, m = [], int(a[:4]), int(a[5:])
    while "%04d-%02d" % (y, m) <= b:
        out.append("%04d-%02d" % (y, m))
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    return out


def load_log(data):
    """The changelog's .csv.gz bytes -> list of row dicts."""
    with gzip.open(io.BytesIO(data), "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def history(log, keys=KEYS):
    """{key: its changelog rows in month order} for the wanted keys."""
    out = {k: [] for k in keys}
    for r in log:
        if r["key"] in out:
            out[r["key"]].append(r)
    for rows in out.values():
        rows.sort(key=lambda r: r["report_month"])
    return out


def on_retired(r):
    return r["event"] != "left" and str(r.get("sheet") or "").strip().lower().startswith("retired")


def arrival(rows):
    """A generator's changelog rows -> its first row on the Retired sheet and where it was before
    ('never listed', 'no sheet' after a left row, or the sheet of its row before); None if never."""
    prior = "never listed"
    for r in rows:
        if on_retired(r):
            return {"month": r["report_month"], "event": r["event"], "from": prior}
        prior = "no sheet" if r["event"] == "left" else (r.get("sheet") or "no sheet")
    return None


def after_arrival(rows, a, end=AUG):
    """Rows after the arrival, up to the end month, that are not a change on the Retired sheet."""
    if a is None:
        return []
    return [r for r in rows if a["month"] < r["report_month"] <= end
            and not (r["event"] == "changed" and on_retired(r))]


def left_in(rows, month=SEP):
    return any(r["report_month"] == month and r["event"] == "left" for r in rows)


def state(rows, month):
    """The sheet a generator is on in a month by its changelog rows (None if not listed)."""
    s = None
    for r in rows:
        if r["report_month"] > month:
            break
        s = None if r["event"] == "left" else (r.get("sheet") or None)
    return s


def present(hist, month):
    """How many of the keys are on the Retired sheet in a month."""
    return sum(1 for rows in hist.values() if str(state(rows, month) or "").lower().startswith("retired"))


def runs(series):
    """[(month, n), ...] -> [[first month, last month, n], ...] for consecutive months with the same n."""
    out = []
    for m, n in series:
        if out and out[-1][2] == n:
            out[-1][1] = m
        else:
            out.append([m, m, n])
    return out


def nuclear_rows(name, raw):
    """One sheet read with header=None -> its rows whose technology names nuclear or whose plant name
    has a WATCH word, plant id or not."""
    rows = raw.values.tolist()
    h = rg.find_header(rows)
    if h is None:
        return []
    low = [str(c).strip().lower() if c is not None and c == c else "" for c in rows[h]]

    def col(text):
        return next((j for j, c in enumerate(low) if text in c), None)

    tj, nj, yj, mj = col("technology"), col("plant name"), col("retirement year"), col("nameplate capacity")
    pj, gj = low.index("plant id"), low.index("generator id")
    out = []
    for r in rows[h + 1:]:
        def cell(j):
            return None if j is None or j >= len(r) else rg.plain(r[j])
        tech, pname = cell(tj), cell(nj)
        if "nuclear" not in str(tech or "").lower() and not any(w in str(pname or "").lower() for w in WATCH):
            continue
        out.append({"sheet": str(name), "plant_id": rg.plain_id(r[pj]), "plant_name": pname,
                    "generator_id": rg.gen_id(r[gj]), "technology": tech, "retirement_year": rs.year_of(cell(yj)),
                    "nameplate_mw": cell(mj)})
    return out


def old_nuclear(scan):
    """Nuclear rows retired before 2002, or on a Retired sheet with no retirement year."""
    return [r for r in scan if "nuclear" in str(r["technology"] or "").lower() and (
        (r["retirement_year"] is not None and r["retirement_year"] < rs.SINCE) or
        (r["retirement_year"] is None and r["sheet"].strip().lower().startswith("retired")))]


def parse(data):
    """xlsx bytes -> (book as retiredgap.read_book gives it, nuclear rows of every sheet)."""
    sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    book, scan = [], []
    for n, raw in sheets.items():
        book.append(rg.book_sheet(n, raw))
        scan += nuclear_rows(n, raw)
    return book, scan


def read_month(month, data_dir, zips, get=None):
    """One month's workbook -> (file entry, book or None, nuclear rows or None). September 2026 comes
    from EIA's own site, every other month from PUDL's archive."""
    f = {"month": month, "errors": []}
    if month == SEP:
        data, url, errors = rg.download(SEP_URLS, get=get or _get)
        f.update(source=url, errors=list(errors))
    else:
        year = int(month[:4])
        if year not in zips:
            zips[year] = ly.get_zip(year, data_dir, ly.ZIP_MD5.get(year), None)
        path, z = zips[year]
        f["zip_md5_matches_page"] = bool(z.get("md5_matches_page"))
        data = None
        if path is None:
            f["errors"].append("zip not available")
        else:
            with zipfile.ZipFile(path) as zf:
                member = rg.member_for(zf.namelist(), month)
                data = zf.read(member) if member else None
            f["source"] = "PUDL archive: %s" % member
            if data is None:
                f["errors"].append("no workbook in the zip")
    if data is None:
        return f, None, None
    f.update(bytes=len(data), md5=rg.md5(data))
    if month == SEP:
        f["same_as_monthcheck"] = (f["bytes"], f["md5"]) == (SEP_BYTES, SEP_MD5)
    try:
        book, scan = parse(data)
    except Exception as e:  # recorded, not raised
        f["errors"].append("not read: %s: %s" % (type(e).__name__, e))
        return f, None, None
    return f, book, scan


def sheet_summary(book):
    """The Retired sheet of one book: generators, by retirement year, and those retired before 2002."""
    ret = rs.retired(book)
    before = "before %d" % rs.SINCE
    return {"retired": len(ret), "bins": rg.counts(rs.year_bin(f.get("retirement_year")) for f in ret.values()),
            "before": sorted(k for k, f in ret.items() if rs.year_bin(f.get("retirement_year")) == before)}


def entry(book, key):
    """What one month's book says about a generator on its Retired sheet."""
    f = rs.retired(book).get(key)
    if f is None:
        return {"on_retired": False, "where": rs.where(book, key)}
    return {"on_retired": True, "where": rs.where(book, key), "retirement_year": rs.year_of(f.get("retirement_year")),
            "retirement_month": rs.year_of(f.get("retirement_month")), "technology": f.get("technology"),
            "nameplate_mw": f.get("nameplate_mw")}


def score(arrivals, entries, stays, scan_aug, aug_years=AUG_YEARS):
    n = len(aug_years)
    got = {k: a for k, a in arrivals.items() if a}
    ms = sorted({a["month"] for a in got.values()})
    out = [{"id": "R1", "outcome": "held" if len(got) == n and len(ms) == 1 else "failed",
            "value": "%d of %d reach it; month(s): %s" % (len(got), n, ", ".join(ms) or "none"),
            "bar": "all %d first reach the Retired sheet in one workbook month" % n}]
    bar = "all %d have August 2026's retirement year in that month's workbook" % n
    if any(k in got and entries.get(k) is None for k in aug_years):
        out.append({"id": "R2", "outcome": "not scored", "value": "a workbook of an arrival month not read",
                    "bar": bar})
    else:
        same = sum(1 for k in aug_years if (entries.get(k) or {}).get("retirement_year") == aug_years[k])
        out.append({"id": "R2", "outcome": "held" if same == n else "failed", "value": "%d of %d" % (same, n),
                    "bar": bar})
    ok = sum(1 for k in aug_years if k in got and not stays.get(k))
    out.append({"id": "R3", "outcome": "held" if ok == n else "failed",
                "value": "%d of %d on it every month from arrival to %s" % (ok, n, AUG),
                "bar": "all %d on the Retired sheet every month from arrival to %s" % (n, AUG)})
    bar = ("exactly %d rows on all sheets of the %s workbook are nuclear and retired before %d "
           "(or on a Retired sheet with no year)" % (n, AUG, rs.SINCE))
    if scan_aug is None:
        out.append({"id": "R4", "outcome": "not scored", "value": "%s workbook not read" % AUG, "bar": bar})
    else:
        k = len(old_nuclear(scan_aug))
        out.append({"id": "R4", "outcome": "held" if k == n else "failed", "value": "%d rows" % k, "bar": bar})
    return out


_cell = rs._cell
_tally = rs._tally


def render(res):
    md = ["# retiredentry %s: when the %d pre-2002 nuclear generators reached EIA-860M's Retired sheet"
          % (__version__, len(KEYS)), "",
          "Scores docs/retiredentry-plan.md (R1 to R4). MV2 of Munim, Inc. (made with AI agents).", ""]
    if res.get("error"):
        return "\n".join(md + ["Not run: %s" % res["error"], ""])
    g = res["log"]
    md += ["## Files", "",
           "Changelog: %s (%d bytes, md5 %s; %d rows, %s to %s). Expected %d bytes and %d rows: %s." % (
               g["url"], g["bytes"], g["md5"], g["rows"], g["first"], g["last"], LOG_BYTES, LOG_ROWS,
               (g["bytes"], g["rows"]) == (LOG_BYTES, LOG_ROWS)), "",
           "| month | source | bytes | md5 | errors |", "|---|---|---|---|---|"]
    for f in res["files"]:
        md.append("| %s | %s | %s | %s | %s |" % (f["month"], _cell(f.get("source")), _cell(f.get("bytes")),
                                                  _cell(f.get("md5")), "; ".join(f["errors"]) or "none"))
    sep = next((f for f in res["files"] if f["month"] == SEP and "same_as_monthcheck" in f), None)
    if sep:
        md += ["", "September file is the one monthcheck-sep2026-v1 read (%d bytes, md5 %s): %s."
               % (SEP_BYTES, SEP_MD5, sep["same_as_monthcheck"])]
    md += ["", "## Predictions", "", "| id | outcome | value | bar |", "|---|---|---|---|"]
    for p in res["predictions"]:
        md.append("| %s | %s | %s | %s |" % (p["id"], p["outcome"], p["value"], p["bar"]))
    scored = [p for p in res["predictions"] if p["outcome"] in ("held", "failed")]
    md += ["", "Held: %d of %d scored." % (sum(1 for p in scored if p["outcome"] == "held"), len(scored))]
    md += ["", "## The %d" % len(res["keys"]), "",
           "| key | reached Retired | event | from | retirement year then | in %s | technology then | MW then "
           "| month before | other rows to %s | left in %s |" % (AUG, AUG, SEP),
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in res["keys"]:
        a, e = k["arrival"] or {}, k["entry"] or {}
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k["key"], _cell(a.get("month")), _cell(a.get("event")), _cell(a.get("from")),
            _cell(e.get("retirement_year")), AUG_YEARS[k["key"]], _cell(e.get("technology")),
            _cell(e.get("nameplate_mw")), k["where_before"],
            "; ".join("%s %s %s" % (r["report_month"], r["event"], r.get("sheet") or "-") for r in k["other_rows"])
            or "none", k["left_sep"]))
    md += ["", "## How many of the %d are on the Retired sheet, by the changelog" % len(res["keys"]), "",
           "| from | to | on the Retired sheet |", "|---|---|---|"]
    md += ["| %s | %s | %d |" % tuple(r) for r in res["runs"]]
    md += ["", "## The Retired sheet in the months read", "",
           "| month | generators | by retirement year | retired before %d | of those, not among the %d |"
           % (rs.SINCE, len(KEYS)), "|---|---|---|---|---|"]
    for m, s in sorted(res["sheets"].items()):
        others = [x for x in s["before"] if x not in AUG_YEARS]
        md.append("| %s | %d | %s | %d | %s |" % (m, s["retired"], _tally(s["bins"]), len(s["before"]),
                                                  ", ".join(others) or "none"))
    md += ["", "## Nuclear rows on every sheet, plant id or not", "",
           "| month | nuclear rows by sheet | retired before %d (or Retired with no year) |" % rs.SINCE,
           "|---|---|---|"]
    for m, scan in sorted(res["scans"].items()):
        nuc = [r for r in scan if "nuclear" in str(r["technology"] or "").lower()]
        md.append("| %s | %s | %d |" % (m, _tally(rg.counts(r["sheet"] for r in nuc)), len(old_nuclear(scan))))
    for m, scan in sorted(res["scans"].items()):
        old = old_nuclear(scan)
        md += ["", "### %s: nuclear rows retired before %d (or Retired with no year): %d" % (m, rs.SINCE, len(old)), "",
               "| sheet | plant id | plant | generator | retirement year | MW |", "|---|---|---|---|---|---|"]
        md += ["| %s | %s | %s | %s | %s | %s |" % (r["sheet"], _cell(r["plant_id"]), _cell(r["plant_name"]),
                                                    r["generator_id"], _cell(r["retirement_year"]),
                                                    _cell(r["nameplate_mw"])) for r in old]
        watch = [r for r in scan if any(w in str(r["plant_name"] or "").lower() for w in WATCH)]
        md += ["", "Rows whose plant name has %s: %s." % (" or ".join(WATCH), "; ".join(
            "%s %s %s/%s %s %s" % (r["sheet"], _cell(r["plant_name"]), _cell(r["plant_id"]), r["generator_id"],
                                   _cell(r["technology"]), _cell(r["retirement_year"])) for r in watch) or "none")]
    return "\n".join(md) + "\n"


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([_cell(r.get(c)) for c in cols])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-plan", action="store_true")
    ap.add_argument("--deadline", default="2026-10-24T12:00", help="UTC, YYYY-MM-DDTHH:MM")
    args = ap.parse_args(argv)
    if args.wait_plan and not wait_plan(deadline_ts(args.deadline)):
        return 3
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "retiredgap": rg.__version__, "retiredscope": rs.__version__, "user_agent": UA,
           "started_at": now()}
    try:
        data = _get(LOG_URL)
        log = load_log(data)
    except Exception as e:  # recorded, not raised
        res["error"] = "changelog not read: %s: %s" % (type(e).__name__, e)
        with open(os.path.join(args.out_dir, "retiredentry.md"), "w", encoding="utf-8") as fh:
            fh.write(render(res))
        return 2
    res["log"] = {"url": LOG_URL, "bytes": len(data), "md5": hashlib.md5(data).hexdigest(), "rows": len(log),
                  "first": min(r["report_month"] for r in log), "last": max(r["report_month"] for r in log)}
    print("changelog %d bytes, %d rows" % (len(data), len(log)), flush=True)
    hist = history(log)
    arrivals = {k: arrival(rows) for k, rows in hist.items()}
    want = set(SCAN)
    for a in arrivals.values():
        if a:
            want.add(a["month"])
            if a["month"] > FIRST:
                want.add(rs.prev_month(a["month"]))
    books, scans, files, zips = {}, {}, [], {}
    for m in sorted(want):
        f, book, scan = read_month(m, args.data_dir, zips)
        print("%s %s bytes %s errors %s" % (m, f.get("source"), f.get("bytes"), f["errors"]), flush=True)
        files.append(f)
        if book is not None:
            books[m], scans[m] = book, scan
    res["files"] = files
    entries, keys = {}, []
    for k in KEYS:
        a = arrivals[k]
        entries[k] = entry(books[a["month"]], k) if a and a["month"] in books else None
        p = rs.prev_month(a["month"]) if a and a["month"] > FIRST else None
        keys.append({"key": k, "arrival": a, "entry": entries[k],
                     "where_before": rs.where(books[p], k) if p in books else "not read",
                     "other_rows": after_arrival(hist[k], a), "left_sep": left_in(hist[k])})
    stays = {k["key"]: k["other_rows"] for k in keys}
    res["keys"] = keys
    res["runs"] = runs([(m, present(hist, m)) for m in months()])
    res["sheets"] = {m: sheet_summary(b) for m, b in books.items()}
    res["scans"] = scans
    res["predictions"] = score(arrivals, entries, stays, scans.get(AUG))
    res["finished_at"] = now()
    with open(os.path.join(args.out_dir, "retiredentry.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    write_csv(os.path.join(args.out_dir, "retiredentry_log_rows.csv"),
              ["report_month", "key", "event", "sheet", "status", "planned_month", "nameplate_mw"],
              [r for k in KEYS for r in hist[k]])
    write_csv(os.path.join(args.out_dir, "retiredentry_keys.csv"),
              ["key", "arrival_month", "arrival_event", "arrival_from", "retirement_year_then", "retirement_year_aug",
               "technology_then", "nameplate_mw_then", "where_before", "other_rows", "left_sep"],
              [{"key": k["key"], "arrival_month": (k["arrival"] or {}).get("month"),
                "arrival_event": (k["arrival"] or {}).get("event"), "arrival_from": (k["arrival"] or {}).get("from"),
                "retirement_year_then": (k["entry"] or {}).get("retirement_year"),
                "retirement_year_aug": AUG_YEARS[k["key"]], "technology_then": (k["entry"] or {}).get("technology"),
                "nameplate_mw_then": (k["entry"] or {}).get("nameplate_mw"), "where_before": k["where_before"],
                "other_rows": len(k["other_rows"]), "left_sep": k["left_sep"]} for k in keys])
    write_csv(os.path.join(args.out_dir, "retiredentry_nuclear.csv"),
              ["month", "sheet", "plant_id", "plant_name", "generator_id", "technology", "retirement_year",
               "nameplate_mw"],
              [dict(r, month=m) for m, scan in sorted(scans.items()) for r in scan])
    md = render(res)
    with open(os.path.join(args.out_dir, "retiredentry.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
