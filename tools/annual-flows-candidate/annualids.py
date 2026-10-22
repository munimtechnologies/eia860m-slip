"""annualids: the plants of the 41, the late monthly retirements and the monthly-only retired generators.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Follow-up to annual860-v1 (docs/heldtrace.md, update of 22 October 2026, late night). It reads EIA's annual
EIA-860 files for 2016 to 2025 with annual860.py 0.1.0's reader (2020 to 2025 are kept in /data from
annual860-v1; 2016 to 2019 are downloaded with an honest User-Agent, two seconds apart) and EIA-860M workbooks
from PUDL's archive (Zenodo record 22995197, md5-checked as layouts.py 0.1.0 checks it), and reports:

- for each of the 41 and each year from 2016, where the annual file lists it (annual860's leaver rows);
- for the plants in FOCUS, every row the annual files and the monthly workbooks give at the plant
  (the month before its generators left, December 2025 and August 2026), so generator IDs can be compared;
- the generators the annual 2025 file lists as retired (RE, 2002 to 2025) that EIA-860M's December 2025
  workbook lists on its Operating sheet: their retirement years by the annual file, and the status and
  planned retirement month the monthly Operating sheet gives them;
- the generators on the August 2026 Retired sheet, retired 2002 to 2025, that the annual 2025 file lists on
  no sheet: whether their plant is on any sheet of the annual 2025 file, and the last earlier annual file
  (2016 to 2024) that lists them.

Two predictions were set down before it ran (docs/annualids-plan.md); each is scored by the bar below and
nothing else:

P1: of those August 2026 Retired-sheet generators the annual 2025 file lists on no sheet, more than half
    are at plants the annual 2025 file lists on no sheet.
P2: of those December 2025 Operating-sheet generators, more than half retired in 2025 by the annual file.

    python annualids.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import json
import os
import time

import annual860 as an
import retiredgap as rg

__version__ = "0.1.0"
YEARS = tuple(range(2016, 2026))
CENSUS_YEAR = 2025
LATE, LAST = "2025-12", "2026-08"
# plant -> the EIA-860M month before its generators left the Retired sheet (retiredscope-v1)
FOCUS = (("1439", "2023-12"), ("55526", "2020-01"), ("1571", "2021-11"), ("1572", "2021-11"),
         ("955", "2025-02"), ("7922", "2022-12"))


def plant_of(key):
    return key.split("/")[0]


def plant_rows(book, plant):
    """Every row of a book (annual or monthly) at one plant -> [{sheet, key, status, retirement_year,
    nameplate_mw}], by sheet and key. On a monthly Operating sheet the retirement year is the planned one."""
    out = [{"sheet": s["sheet"], "key": k, "status": an.code(f.get("status")),
            "retirement_year": an.year_of(f.get("retirement_year")), "nameplate_mw": f.get("nameplate_mw")}
           for s in book for k, f in s["keys"].items() if plant_of(k) == plant]
    return sorted(out, key=lambda r: (r["sheet"], r["key"]))


def plants(book):
    return {plant_of(k) for s in book for k in s["keys"]}


def listed(book):
    """{key: where} for every generator an annual book lists (annual860.annual_where)."""
    return {k: an.annual_where(book, k) for s in book for k in s["keys"]}


def late_operating(annual, late, last=None, year=CENSUS_YEAR):
    """Annual-retired generators (RE, SINCE..year) that the late monthly book lists on its Operating sheet only."""
    a_ret = an.annual_retired(annual, year)
    ops = {}
    for s in late:
        if s["sheet"] == "Operating":
            ops.update(s["keys"])
    keys = sorted(k for k in a_ret if an.where(late, k) == "Operating")
    rows = [{"key": k, "annual_year": an.year_of(a_ret[k].get("retirement_year")),
             "annual_mw": a_ret[k].get("nameplate_mw"), "technology": a_ret[k].get("technology"),
             "late_status": an.code(ops[k].get("status")),
             "late_planned_year": an.year_of(ops[k].get("retirement_year")),
             "late_planned_month": an.year_of(ops[k].get("retirement_month")),
             "where_last": an.where(last, k) if last is not None else None} for k in keys]
    n, hit = len(rows), sum(1 for r in rows if r["annual_year"] == year)
    return {"n": n, "years": rg.counts(r["annual_year"] for r in rows),
            "planned_years": rg.counts(r["late_planned_year"] for r in rows),
            "status": rg.counts(r["late_status"] for r in rows),
            "where_last": rg.counts(r["where_last"] for r in rows),
            "technology": rg.counts((r["technology"] for r in rows), an.TOP),
            "mw": round(sum(rg.num(r["annual_mw"]) for r in rows), 1),
            "in_census_year": hit,
            "p2": {"bar": "more than half retired in %d by the annual file" % year, "held": n > 0 and 2 * hit > n},
            "rows": rows}


def extra(annual, last, history, year=CENSUS_YEAR):
    """Generators on the last monthly book's Retired sheet(s), retired SINCE..year, that the annual book lists
    on no sheet. history: {year: listed(book)} for the earlier annual files."""
    m_old = {}
    for s in last:
        if an.is_retired_sheet(s["sheet"]) and rg.route(s["sheet"]):
            for k, f in s["keys"].items():
                y = an.year_of(f.get("retirement_year"))
                if y is not None and an.SINCE <= y <= year:
                    m_old.setdefault(k, f)
    on = plants(annual)
    keys = sorted(k for k in m_old if an.annual_where(annual, k) == "not listed")
    rows = []
    for k in keys:
        seen = [(y, h[k]) for y, h in sorted(history.items()) if k in h]
        rows.append({"key": k, "retirement_year": an.year_of(m_old[k].get("retirement_year")),
                     "nameplate_mw": m_old[k].get("nameplate_mw"), "technology": m_old[k].get("technology"),
                     "plant_listed": plant_of(k) in on,
                     "last_year": seen[-1][0] if seen else None, "last_where": seen[-1][1] if seen else None})
    n, off = len(rows), sum(1 for r in rows if not r["plant_listed"])
    return {"n": n, "plant_listed": rg.counts(r["plant_listed"] for r in rows), "plant_not_listed": off,
            "last_year": rg.counts(r["last_year"] for r in rows),
            "last_where": rg.counts(r["last_where"] for r in rows),
            "years_plant_listed": rg.counts(r["retirement_year"] for r in rows if r["plant_listed"]),
            "years_plant_not_listed": rg.counts(r["retirement_year"] for r in rows if not r["plant_listed"]),
            "mw": round(sum(rg.num(r["nameplate_mw"]) for r in rows), 1),
            "mw_plant_not_listed": round(sum(rg.num(r["nameplate_mw"]) for r in rows if not r["plant_listed"]), 1),
            "technology": rg.counts((r["technology"] for r in rows), an.TOP),
            "p1": {"bar": "more than half at plants the annual %d file lists on no sheet" % year,
                   "held": n > 0 and 2 * off > n},
            "rows": rows}


def _by_value(entries):
    return sorted(entries, key=lambda x: x["value"])


def render(result):
    md = ["# annualids %s: the plants of the 41, late monthly retirements and monthly-only retired generators"
          % __version__, "", "Follow-up to annual860-v1, with two predictions set down before it ran "
          "(docs/annualids-plan.md). MV2 of Munim, Inc. (made with AI agents).", ""]
    md += ["## Files", "", "| file | url | cached | bytes | md5 | errors |", "|---|---|---|---|---|---|"]
    for f in result["files"]:
        md.append("| annual %d | %s | %s | %s | %s | %s |" % (
            f["year"], an._cell(f.get("url")), f.get("cached"), an._cell(f.get("bytes")), an._cell(f.get("md5")),
            "; ".join(f.get("errors", [])) or "none"))
    for f in result["monthly_files"]:
        md.append("| monthly %s | %s | - | %s | %s | %s |" % (
            f["month"], an._cell(f.get("member")), an._cell(f.get("bytes")), an._cell(f.get("md5")),
            "; ".join(f["errors"]) or "none"))
    years = [f["year"] for f in result["files"] if f.get("sheets")]
    md += ["", "## The 41 in the annual files", "", "| key | left 860M | " + " | ".join(str(y) for y in years) + " |",
           "|---|---|" + "---|" * len(years)]
    for e in result["leavers"]:
        by = {r["year"]: r for r in e["years"]}
        md.append("| %s | %s | %s |" % (e["key"], e["month"], " | ".join(
            (by[y]["where"] if by[y]["where"] == "not listed" else "%s (%s, %s MW)" % (
                by[y]["where"], an._cell(by[y]["retirement_year"]), an._cell(by[y]["nameplate_mw"])))
            if y in by else "not read" for y in years)))
    md += ["", "## Rows at the focus plants", ""]
    for p, m in FOCUS:
        fp = result["focus"][p]
        md.append("Plant %s (the 41 left in the month after %s):" % (p, m))
        for src, part in (("annual", fp["annual"]), ("monthly", fp["monthly"])):
            for when in sorted(part):
                md.append("- %s %s: %s" % (src, when, "; ".join(
                    "%s %s %s (%s, %s MW)" % (r["sheet"], r["key"], an._cell(r["status"]),
                                              an._cell(r["retirement_year"]), an._cell(r["nameplate_mw"]))
                    for r in part[when]) or "no rows"))
        md.append("")
    lo = result.get("late_operating")
    if lo:
        md += ["## Annual %d retired, on the %s Operating sheet" % (CENSUS_YEAR, LATE), "",
               "Generators: %d (%s MW). Retirement years by the annual file: %s." % (
                   lo["n"], lo["mw"], an._tally(_by_value(lo["years"]))), "",
               "Status on the %s Operating sheet: %s. Planned retirement years there: %s. Where the %s workbook "
               "lists them: %s. Technologies (top %d): %s." % (
                   LATE, an._tally(lo["status"]), an._tally(_by_value(lo["planned_years"])), LAST,
                   an._tally(lo["where_last"]), an.TOP, an._tally(lo["technology"])), "",
               "P2 (%s): %d of %d; %s." % (lo["p2"]["bar"], lo["in_census_year"], lo["n"],
                                           "held" if lo["p2"]["held"] else "failed"), ""]
    ex = result.get("extra")
    if ex:
        md += ["## On the %s Retired sheet, on no sheet of the annual %d file" % (LAST, CENSUS_YEAR), "",
               "Generators: %d (%s MW). Plant on a sheet of the annual %d file: %s." % (
                   ex["n"], ex["mw"], CENSUS_YEAR, an._tally(ex["plant_listed"])), "",
               "At plants on no sheet: %d (%s MW); retirement years: %s." % (
                   ex["plant_not_listed"], ex["mw_plant_not_listed"], an._tally(_by_value(ex["years_plant_not_listed"]))),
               "", "At plants on a sheet: retirement years: %s." % an._tally(_by_value(ex["years_plant_listed"])), "",
               "Last earlier annual file (2016 to 2024) that lists them: %s. How it lists them: %s." % (
                   an._tally(_by_value(ex["last_year"])), an._tally(ex["last_where"])), "",
               "Technologies (top %d): %s." % (an.TOP, an._tally(ex["technology"])), "",
               "P1 (%s): %d of %d; %s." % (ex["p1"]["bar"], ex["plant_not_listed"], ex["n"],
                                           "held" if ex["p1"]["held"] else "failed"), ""]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "annual860": an.__version__, "retiredgap": rg.__version__,
              "user_agent": an.UA, "started_at": an.now(), "census_year": CENSUS_YEAR}
    files, history, annual = [], {}, None
    rows = {k: [] for _, k in an.LEAVERS}
    focus = {p: {"annual": {}, "monthly": {}} for p, _ in FOCUS}
    for i, year in enumerate(YEARS):
        if i:
            time.sleep(2)
        f, book = an.read_annual(year, args.data_dir)
        print("annual %d url %s cached %s bytes %s errors %s" % (
            year, f.get("url"), f.get("cached"), f.get("bytes"), f["errors"]), flush=True)
        files.append(f)
        if book is None:
            continue
        for _, k in an.LEAVERS:
            rows[k].append(an.leaver_row(book, year, k))
        for p, _ in FOCUS:
            focus[p]["annual"][str(year)] = plant_rows(book, p)
        if year == CENSUS_YEAR:
            annual = book
        else:
            history[year] = listed(book)
    result["files"] = files
    result["leavers"] = [{"month": m, "key": k, "years": rows[k]} for m, k in an.LEAVERS]
    mfiles, books = [], {}
    for m in sorted({x for _, x in FOCUS} | {LATE, LAST}):
        f, book = an.read_monthly(m, args.data_dir)
        print("monthly %s member %s errors %s" % (m, f.get("member"), f["errors"]), flush=True)
        mfiles.append(f)
        if book is None:
            continue
        for p, pm in FOCUS:
            if m in (pm, LATE, LAST):
                focus[p]["monthly"][m] = plant_rows(book, p)
        if m in (LATE, LAST):
            books[m] = book
    result["monthly_files"], result["focus"] = mfiles, focus
    if annual is not None and LATE in books:
        result["late_operating"] = late_operating(annual, books[LATE], books.get(LAST))
    if annual is not None and LAST in books:
        result["extra"] = extra(annual, books[LAST], history)
    result["finished_at"] = an.now()
    with open(os.path.join(args.out_dir, "annualids.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "annualids_leavers.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month_left", "key", "year", "where_annual", "retirement_year", "nameplate_mw"])
        for e in result["leavers"]:
            for r in e["years"]:
                w.writerow([e["month"], e["key"], r["year"], r["where"], an._cell(r["retirement_year"]),
                            an._cell(r["nameplate_mw"])])
    with open(os.path.join(args.out_dir, "annualids_focus.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["plant", "source", "when", "sheet", "key", "status", "retirement_year", "nameplate_mw"])
        for p, _ in FOCUS:
            for src in ("annual", "monthly"):
                for when, part in sorted(focus[p][src].items()):
                    for r in part:
                        w.writerow([p, src, when, r["sheet"], r["key"], an._cell(r["status"]),
                                    an._cell(r["retirement_year"]), an._cell(r["nameplate_mw"])])
    for name, part, cols in (("annualids_late_operating.csv", result.get("late_operating"),
                              ("key", "annual_year", "annual_mw", "technology", "late_status", "late_planned_year",
                               "late_planned_month", "where_last")),
                             ("annualids_extra.csv", result.get("extra"),
                              ("key", "retirement_year", "nameplate_mw", "technology", "plant_listed", "last_year",
                               "last_where"))):
        with open(os.path.join(args.out_dir, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in (part or {}).get("rows", []):
                w.writerow([an._cell(r[c]) for c in cols])
    md = render(result)
    with open(os.path.join(args.out_dir, "annualids.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
