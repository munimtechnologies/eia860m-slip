"""nextlist: every generator EIA-860M plans to start next month, each with the on-time share of earlier ones like it.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

For a target month T, the list is every generator on the Planned sheet of EIA's workbook for the month
before T whose planned operating month is T (the next-month group of results 34 to 41). Each generator
gets its technology group (the rule of nexttech.tech_group 0.1.0, on the workbook's technology) and its
cell: first (in no next-month group since August 2015), or the months since its last next-month group
(1 month, 2-3 months, 4-12 months, more than 12 months), counted on data/nexttech_cohort.csv at commit
ea63c15 by nextcount.annotate 0.1.0.

Its p is the share of the generator-months in the same (group, cell) over the WINDOW group months before
T that were listed as operating in their month. When that cell has fewer than MIN_ROWS generator-months,
p falls back to the group's share, then the cell's share over all groups, then the share of all rows.
Two reference forecasts use the same window: r0, the share of all rows, and r1, the group's share.
p is a description of what happened to earlier generators like this one, not a forecast made with
knowledge of the plant.

The backtest builds the same p, r0 and r1 for every month from BACKTEST_FROM to the cohort file's last
month, each from the WINDOW months before it only, and scores them with the Brier score (the mean of
(p - outcome)^2; lower is better). Differences are given with 95% intervals from resampling whole plants
(plant = the key before "/"). A practice list for the last month in the cohort file must have the same
keys as that month's cohort rows (check C1).

    python nextlist.py --target 2026-10 --practice 2026-09 --out-dir /out

When the target month's outcome is published, --score-file 2026-10=monthrun_cohort.csv (written by
monthrun.py 0.1.0 for that target) scores the list with the same code. Needs nextcount.py beside it,
and xlsxprobe.py (with eia860m_slip.py and pandas) to read the workbooks.
"""

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import random
import sys

import nextcount as nc

__version__ = "0.1.0"
COHORT_MD5, COHORT_LAST = "1681df9fdee9878ca2c359d1239c6467", "2026-09"
# EIA's workbooks as monthrun-practice-v1 downloaded them (docs/sep2026.md)
WORKBOOK_MD5 = {"2026-08": "9727ac867236faab7d5503175dacdf38", "2026-09": "4c741eb77a5ccad5aca32ffe43f398af"}
SHEET = "Planned"
WINDOW = 48          # p is the share over the 48 next-month groups before the target month
MIN_ROWS = 30        # a share needs at least 30 generator-months, else the next fallback is used
CELLS = ("first", "1 month", "2-3 months", "4-12 months", "more than 12 months")
BACKTEST_FROM = "2020-01"
RESAMPLES, SEED = 2000, 20261026
BINS = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 1.01)
FIELDS = ("key", "plant_name", "state", "technology", "group", "status", "nameplate_mw", "prior", "gap", "cell",
          "p", "p_source", "p_rows", "r0", "r1")


def add_months(month, k):
    i = nc.m_index(month) + k
    return "%04d-%02d" % (i // 12, i % 12 + 1)


def window(target, n=WINDOW):
    """The first and last group month whose rows give the target month's shares."""
    return add_months(target, -n), add_months(target, -1)


def tech_group(tech):
    """An EIA-860M technology name -> solar, batteries, gas, wind or other (nexttech.tech_group 0.1.0's rule)."""
    t = str(tech or "").strip().lower()
    if t == "solar photovoltaic":
        return "solar"
    if t == "batteries":
        return "batteries"
    if t.startswith("natural gas") or t == "other natural gas":
        return "gas"
    if "wind" in t:
        return "wind"
    return "other"


def cell_of(r):
    """An annotated row -> its cell: first, or the months since its last next-month group."""
    if r["prior"] == 0:
        return "first"
    return nc.label(r["gap"], nc.GAPS)


def annotate(rows):
    """Cohort-like rows -> nextcount.annotate's rows, each with its cell."""
    return [dict(r, cell=cell_of(r)) for r in nc.annotate(rows)]


def rates(a, target, n=WINDOW):
    """Annotated rows -> {(group, cell): (on time, rows)} over the n group months before target; None
    stands for every group or every cell."""
    lo, hi = window(target, n)
    t = collections.defaultdict(lambda: [0, 0])
    for r in a:
        if lo <= r["month"] <= hi:
            ok = 1 if r["now"] == "Operating" else 0
            for k in ((r["group"], r["cell"]), (r["group"], None), (None, r["cell"]), (None, None)):
                t[k][0] += ok
                t[k][1] += 1
    return {k: tuple(v) for k, v in t.items()}


def forecast(group, cell, t, min_rows=MIN_ROWS):
    """-> (p, source, rows): the first share with at least min_rows rows of (group, cell), the group,
    the cell over all groups and all rows; all rows whatever their number when none has enough."""
    for k, src in (((group, cell), "group and cell"), ((group, None), "group"), ((None, cell), "cell")):
        op, n = t.get(k, (0, 0))
        if n >= min_rows:
            return op / n, src, n
    op, n = t.get((None, None), (0, 0))
    return (op / n if n else None), "all", n


def references(group, t, min_rows=MIN_ROWS):
    """-> (r0, r1): the share of all rows, and the group's share (r0 when the group has too few rows)."""
    op, n = t.get((None, None), (0, 0))
    r0 = op / n if n else None
    gop, gn = t.get((group, None), (0, 0))
    return r0, (gop / gn if gn >= min_rows else r0)


def predict(rows, t):
    """Annotated rows of one month and that month's rates -> the rows with p, p_source, p_rows, r0 and r1."""
    out = []
    for r in rows:
        p, src, n = forecast(r["group"], r["cell"], t)
        r0, r1 = references(r["group"], t)
        out.append(dict(r, p=p, p_source=src, p_rows=n, r0=r0, r1=r1))
    return out


def outcome(r):
    return 1 if r["now"] == "Operating" else 0


def brier(rows, col):
    return sum((r[col] - r["y"]) ** 2 for r in rows) / len(rows) if rows else None


def summary(rows):
    """Rows with y, p, r0 and r1 (and nameplate_mw where known) -> counts, Brier scores and differences."""
    s = {"rows": len(rows), "plants": len(set(r["key"].split("/")[0] for r in rows)),
         "on_time": sum(r["y"] for r in rows), "expected": sum(r["p"] for r in rows)}
    for col in ("p", "r0", "r1"):
        s["brier_" + col] = brier(rows, col)
    if rows:
        s["m_minus_r0"] = s["brier_p"] - s["brier_r0"]
        s["m_minus_r1"] = s["brier_p"] - s["brier_r1"]
    mw = [r for r in rows if r.get("nameplate_mw") not in (None, "")]
    if mw:
        s["mw"] = sum(float(r["nameplate_mw"]) for r in mw)
        s["mw_on_time"] = sum(float(r["nameplate_mw"]) for r in mw if r["y"])
        s["mw_expected"] = sum(float(r["nameplate_mw"]) * r["p"] for r in mw)
    return s


def list_summary(rows):
    """List rows (no outcome yet) -> generators, plants, MW and what p expects of them."""
    mw = [r for r in rows if r.get("nameplate_mw") not in (None, "")]
    return {"rows": len(rows), "plants": len(set(r["key"].split("/")[0] for r in rows)),
            "expected": sum(r["p"] for r in rows), "mw": sum(float(r["nameplate_mw"]) for r in mw),
            "mw_expected": sum(float(r["nameplate_mw"]) * r["p"] for r in mw)}


def boot(rows, col, ref, resamples=RESAMPLES, seed=SEED):
    """-> the 95% interval of Brier(col) - Brier(ref) over resamples of whole plants, (None, None) with
    fewer than 2 plants."""
    agg = collections.defaultdict(lambda: [0.0, 0])
    for r in rows:
        a = agg[r["key"].split("/")[0]]
        a[0] += (r[col] - r["y"]) ** 2 - (r[ref] - r["y"]) ** 2
        a[1] += 1
    plants = [tuple(agg[k]) for k in sorted(agg)]
    if len(plants) < 2:
        return None, None
    rng = random.Random(seed)
    vals = []
    for _ in range(resamples):
        d = n = 0
        for _ in plants:
            x = plants[rng.randrange(len(plants))]
            d += x[0]
            n += x[1]
        vals.append(d / n)
    vals.sort()
    return vals[int(0.025 * resamples)], vals[int(0.975 * resamples) - 1]


def calibration(rows, bins=BINS):
    out = []
    for lo, hi in zip(bins, bins[1:]):
        sel = [r for r in rows if lo <= r["p"] < hi]
        if sel:
            out.append({"p_from": lo, "p_to": min(hi, 1.0), "rows": len(sel),
                        "mean_p": sum(r["p"] for r in sel) / len(sel), "on_time": sum(r["y"] for r in sel) / len(sel)})
    return out


def backtest(a, start=BACKTEST_FROM, end=COHORT_LAST):
    """Annotated cohort rows -> every row of the months start to end with p, r0, r1 and y, each month's
    shares taken from the WINDOW months before it only."""
    by = collections.defaultdict(list)
    for r in a:
        if start <= r["month"] <= end:
            by[r["month"]].append(r)
    out = []
    for m in sorted(by):
        out += [dict(r, y=outcome(r)) for r in predict(by[m], rates(a, m))]
    return out


def by_month(rows):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["month"]].append(r)
    return [dict(summary(by[m]), month=m) for m in sorted(by)]


def build_list(cohort, target, group_rows):
    """Cohort rows, the target month and its group (rows with key, group, ...) -> the group's rows with
    prior, gap, cell, p, p_source, p_rows, r0 and r1, counted on the cohort months before target only."""
    base = [r for r in cohort if r["month"] < target]
    new = [dict(r, month=target, now="") for r in group_rows]
    a = annotate(base + new)
    return predict([r for r in a if r["month"] == target], rates(a, target))


def keys_check(listed, cohort, month):
    """C1: the practice list's keys against the cohort file's rows of that month."""
    want = {r["key"]: r["group"] for r in cohort if r["month"] == month}
    got = {r["key"]: r["group"] for r in listed}
    return {"month": month, "cohort_rows": len(want), "list_rows": len(got),
            "only_list": sorted(set(got) - set(want))[:20], "only_cohort": sorted(set(want) - set(got))[:20],
            "group_differs": sum(1 for k in set(got) & set(want) if got[k] != want[k]),
            "held": bool(want) and set(got) == set(want)}


def score(listed, outcomes):
    """The list and {key: now} for its month -> the rows with y and the summary; rows with no outcome are
    counted and left out."""
    rows = [dict(r, y=1 if outcomes[r["key"]] == "Operating" else 0) for r in listed if r["key"] in outcomes]
    s = summary(rows)
    s["missing"] = sum(1 for r in listed if r["key"] not in outcomes)
    for ref in ("r0", "r1"):
        s["interval_minus_" + ref] = boot(rows, "p", ref)
    return rows, s


def read_outcomes(data):
    """A monthrun_cohort.csv's bytes -> {key: now}."""
    return {x["key"]: x["now"] for x in csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))}


def _text(v):
    """A workbook cell as stripped text; '' for an empty cell."""
    return "" if v is None or v != v else str(v).strip()


def planned_group(path, target):
    """EIA's workbook of the month before target -> (rows of its Planned sheet planned to start in target,
    how the sheet was read). Needs pandas and xlsxprobe.py."""
    import pandas as pd
    import xlsxprobe as xp
    raw = pd.read_excel(path, sheet_name=SHEET, header=None, dtype=object)
    df, h = xp.sheet_frame(raw)
    if df is None:
        raise ValueError("the %s sheet has no row naming Plant ID and Generator ID" % SHEET)
    cols = list(df.columns)
    c = {"plant": xp.find_col(cols, "plant id"), "gen": xp.find_col(cols, "generator id"),
         "name": xp.find_col(cols, "plant name"), "state": xp.find_col(cols, "state"),
         "tech": xp.find_col(cols, "technology"), "status": xp.find_col(cols, "status"),
         "mw": xp.find_col(cols, "nameplate capacity") or xp.find_col(cols, "capacity"),
         "pm": (xp.find_col(cols, "planned", "operation", "month")
                or xp.find_col(cols, "planned", "month", exclude=("retire",))),
         "py": (xp.find_col(cols, "planned", "operation", "year")
                or xp.find_col(cols, "planned", "year", exclude=("retire",)))}
    want, out, seen, dup = nc.m_index(target), [], set(), 0
    for _, x in df.iterrows():
        if xp.month_index(x[c["py"]], x[c["pm"]]) != want:
            continue
        key = xp.norm_id(x[c["plant"]]) + "/" + xp.norm_id(x[c["gen"]])
        if key in seen:
            dup += 1
            continue
        seen.add(key)
        try:
            mw = round(float(x[c["mw"]]), 3)
        except (TypeError, ValueError):
            mw = None
        tech = _text(x[c["tech"]])
        out.append({"key": key, "plant_name": _text(x[c["name"]]) if c["name"] else "",
                    "state": _text(x[c["state"]]) if c["state"] else "", "technology": tech,
                    "group": tech_group(tech), "status": xp.status_code(x[c["status"]]), "nameplate_mw": mw})
    info = {"sheet": SHEET, "header_row": h, "rows": len(df), "columns": {k: v for k, v in c.items()},
            "duplicate_keys": dup}
    return out, info


def fetch_workbook(month, data_dir):
    """EIA's workbook for month (YYYY-MM) -> (path, record); path is None when no URL gave an xlsx file."""
    import xlsxprobe as xp
    dest = os.path.join(data_dir, "workbook_%s.xlsx" % month)
    url, errors = xp.fetch(xp.workbook_urls(month), dest)
    rec = {"month": month, "url": url, "errors": errors}
    if url is None:
        return None, rec
    with open(dest, "rb") as fh:
        b = fh.read()
    rec.update(bytes=len(b), md5=hashlib.md5(b).hexdigest(), expected_md5=WORKBOOK_MD5.get(month))
    rec["same_as_expected"] = rec["expected_md5"] is None or rec["md5"] == rec["expected_md5"]
    return dest, rec


def _f(v, fmt="%.4f"):
    return "-" if v is None else fmt % v


def _interval(iv):
    return "not computed" if iv is None or iv[0] is None else "%+.4f to %+.4f" % tuple(iv)


def render(res):
    md = ["# nextlist %s: EIA-860M generators planned for %s, with the on-time share of earlier ones like them" % (
        __version__, res["target"]), "",
        "MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0. p describes what happened to "
        "earlier generators in the same technology group and listing cell; it is not a forecast made with knowledge "
        "of any plant.", ""]
    c = res.get("cohort", {})
    md += ["Cohort file: %s (%s bytes, md5 %s; %s rows; expected md5 %s: %s)." % (
        c.get("source"), c.get("bytes"), c.get("md5"), c.get("rows"), COHORT_MD5, c.get("same")), ""]
    if res.get("error"):
        return "\n".join(md + ["Error: %s" % res["error"], ""])
    md += ["## Workbooks", "", "| month | url | bytes | md5 | as expected |", "|---|---|---|---|---|"]
    for w in res["workbooks"]:
        md.append("| %s | %s | %s | %s | %s |" % (w["month"], w.get("url"), w.get("bytes"), w.get("md5"),
                                                  w.get("same_as_expected")))
    md.append("")
    for w in res["workbooks"]:
        md += ["- %s: %s" % (w["month"], e) for e in w.get("errors", [])]
    md += ["", "## Checks", ""]
    k = res.get("c1")
    if k:
        md.append("- C1 (practice %s): %s. List %d rows, cohort file %d; only in the list %s; only in the cohort "
                  "file %s; technology group differs for %d." % (
                      k["month"], "held" if k["held"] else "failed", k["list_rows"], k["cohort_rows"],
                      k["only_list"] or "none", k["only_cohort"] or "none", k["group_differs"]))
    p = res.get("practice_vs_backtest")
    if p:
        md.append("- C2 (practice %s): the practice list's Brier scores equal the backtest's for that month: %s "
                  "(%s against %s)." % (p["month"], "held" if p["held"] else "failed", p["practice"], p["backtest"]))
    md.append("")
    b = res["backtest"]
    s = b["pooled"]
    md += ["## Backtest, %s to %s (each month from the %d months before it only)" % (b["from"], b["to"], WINDOW), "",
           "%d generator-months at %d plants; on time %d, expected by p %.1f." % (
               s["rows"], s["plants"], s["on_time"], s["expected"]), "",
           "| forecast | Brier score | minus r0 (95% interval, plants resampled) | minus r1 |", "|---|---|---|---|",
           "| p (group and cell) | %s | %+.4f (%s) | %+.4f (%s) |" % (
               _f(s["brier_p"]), s["m_minus_r0"], _interval(b["interval_minus_r0"]), s["m_minus_r1"],
               _interval(b["interval_minus_r1"])),
           "| r0 (all rows) | %s | | |" % _f(s["brier_r0"]),
           "| r1 (group) | %s | | |" % _f(s["brier_r1"]), "",
           "Months where p's Brier score is below r0's: %d of %d; below r1's: %d of %d. %d resamples, seed %d." % (
               b["months_below_r0"], len(b["months"]), b["months_below_r1"], len(b["months"]), RESAMPLES, SEED), "",
           "### Calibration, pooled", "", "| p from | p to | generator-months | mean p | on-time share |",
           "|---|---|---|---|---|"]
    for x in b["calibration"]:
        md.append("| %.1f | %.1f | %d | %.4f | %.4f |" % (x["p_from"], x["p_to"], x["rows"], x["mean_p"], x["on_time"]))
    md += ["", "### By month", "", "| month | rows | on time | expected | Brier p | Brier r0 | Brier r1 |",
           "|---|---|---|---|---|---|---|"]
    for x in b["months"]:
        md.append("| %s | %d | %d | %.1f | %s | %s | %s |" % (x["month"], x["rows"], x["on_time"], x["expected"],
                                                               _f(x["brier_p"]), _f(x["brier_r0"]), _f(x["brier_r1"])))
    for name in ("practice", "target"):
        L = res.get(name)
        if not L:
            continue
        md += ["", "## %s list: %s (from EIA's %s workbook)" % ("Practice" if name == "practice" else "The",
                                                                 L["month"], L["from"]), ""]
        if L.get("error"):
            md += ["Not built: %s" % L["error"]]
            continue
        s = L["summary"]
        md += ["%d generators at %d plants, %s MW. Expected on time by p: %.1f generators, %s MW." % (
            s["rows"], s["plants"], _f(s.get("mw"), "%.1f"), s["expected"], _f(s.get("mw_expected"), "%.1f")), "",
            "| group | cell | generators | MW | p | p from | rows behind p |", "|---|---|---|---|---|---|---|"]
        for x in L["cells"]:
            md.append("| %s | %s | %d | %.1f | %.4f | %s | %d |" % (x["group"], x["cell"], x["generators"], x["mw"],
                                                                    x["p"], x["p_source"], x["p_rows"]))
        if L.get("score"):
            t = L["score"]
            md += ["", "Scored: %d rows (%d without an outcome); on time %d against %.1f expected; MW on time %s "
                   "against %s expected. Brier p %s, r0 %s, r1 %s; p minus r0 %s; p minus r1 %s." % (
                       t["rows"], t["missing"], t["on_time"], t["expected"], _f(t.get("mw_on_time"), "%.1f"),
                       _f(t.get("mw_expected"), "%.1f"), _f(t["brier_p"]), _f(t["brier_r0"]), _f(t["brier_r1"]),
                       _interval(t["interval_minus_r0"]), _interval(t["interval_minus_r1"]))]
        md += ["", "| key | plant | state | technology | MW | status | cell | p |", "|---|---|---|---|---|---|---|---|"]
        for r in L["rows"]:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %.4f |" % (
                r["key"], r["plant_name"], r["state"], r["technology"], _f(r["nameplate_mw"], "%.1f"), r["status"],
                r["cell"], r["p"]))
    return "\n".join(md + [""])


def cell_table(rows):
    by = collections.OrderedDict()
    for r in sorted(rows, key=lambda r: (r["group"], CELLS.index(r["cell"]))):
        x = by.setdefault((r["group"], r["cell"]), {"group": r["group"], "cell": r["cell"], "generators": 0,
                                                     "mw": 0.0, "p": r["p"], "p_source": r["p_source"],
                                                     "p_rows": r["p_rows"]})
        x["generators"] += 1
        x["mw"] += float(r["nameplate_mw"] or 0)
    return list(by.values())


def make_list(cohort, target, path, rec):
    L = {"month": target, "from": add_months(target, -1)}
    if path is None:
        L["error"] = "workbook not downloaded"
        return L, []
    try:
        group, L["sheet"] = planned_group(path, target)
    except Exception as e:  # recorded, not raised
        L["error"] = "%s: %s" % (type(e).__name__, e)
        return L, []
    rows = build_list(cohort, target, group)
    rows.sort(key=lambda r: (-r["p"], -(r["nameplate_mw"] or 0), r["key"]))
    L["rows"] = [{f: r.get(f) for f in FIELDS} for r in rows]
    L["summary"] = list_summary(rows)
    L["cells"] = cell_table(rows)
    return L, rows


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: ("" if r.get(k) is None else r.get(k)) for k in fields} for r in rows)


def main(argv=None, get=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", default="2026-10")
    ap.add_argument("--practice", default=COHORT_LAST, help="a month the cohort file holds ('' for none)")
    ap.add_argument("--cohort", default="", help="a local copy of the cohort file (default: download it)")
    ap.add_argument("--data-dir", default=".")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--score-file", default="", help="YYYY-MM=monthrun_cohort.csv of the target month")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": __version__, "nextcount": nc.__version__, "started_at": nc.now(), "target": args.target,
           "window": WINDOW, "min_rows": MIN_ROWS, "workbooks": []}
    if args.cohort:
        with open(args.cohort, "rb") as fh:
            data = fh.read()
        src = args.cohort
    else:
        data, src = (get or nc.get)(nc.COHORT_URL), nc.COHORT_URL
    cohort = nc.load(data)
    md5 = hashlib.md5(data).hexdigest()
    res["cohort"] = {"source": src, "bytes": len(data), "md5": md5, "rows": len(cohort),
                     "same": md5 == COHORT_MD5 and len(cohort) == nc.COHORT_ROWS}
    print("cohort file %d bytes, md5 %s, %d rows" % (len(data), md5, len(cohort)), flush=True)
    if not res["cohort"]["same"]:
        res["error"] = "cohort file is not the one at commit ea63c15"
    else:
        bt = backtest(annotate(cohort))
        months = by_month(bt)
        res["backtest"] = {"from": BACKTEST_FROM, "to": COHORT_LAST, "pooled": summary(bt), "months": months,
                           "months_below_r0": sum(1 for x in months if x["brier_p"] < x["brier_r0"]),
                           "months_below_r1": sum(1 for x in months if x["brier_p"] < x["brier_r1"]),
                           "interval_minus_r0": boot(bt, "p", "r0"), "interval_minus_r1": boot(bt, "p", "r1"),
                           "calibration": calibration(bt)}
        write_csv(os.path.join(args.out_dir, "nextlist_backtest_months.csv"), months,
                  ["month", "rows", "plants", "on_time", "expected", "brier_p", "brier_r0", "brier_r1"])
        print("backtest: %d rows, Brier p %.4f, r0 %.4f, r1 %.4f" % (
            len(bt), res["backtest"]["pooled"]["brier_p"], res["backtest"]["pooled"]["brier_r0"],
            res["backtest"]["pooled"]["brier_r1"]), flush=True)
        for name, month in (("practice", args.practice), ("target", args.target)):
            if not month:
                continue
            path, rec = fetch_workbook(add_months(month, -1), args.data_dir)
            res["workbooks"].append(rec)
            L, rows = make_list(cohort, month, path, rec)
            res[name] = L
            if rows:
                write_csv(os.path.join(args.out_dir, "nextlist_%s.csv" % month), L["rows"], FIELDS)
            if name == "practice" and rows:
                res["c1"] = keys_check(rows, cohort, month)
                outs = {r["key"]: r["now"] for r in cohort if r["month"] == month}
                _, L["score"] = score(rows, outs)
                bm = [x for x in months if x["month"] == month]
                got = [round(L["score"][k], 10) for k in ("brier_p", "brier_r0", "brier_r1")]
                want = [round(bm[0][k], 10) for k in ("brier_p", "brier_r0", "brier_r1")] if bm else None
                res["practice_vs_backtest"] = {"month": month, "practice": got, "backtest": want, "held": got == want}
            if name == "target" and rows and args.score_file:
                m, path_s = args.score_file.split("=", 1)
                if m != month:
                    L["score_error"] = "score file is for %s, not %s" % (m, month)
                else:
                    with open(path_s, "rb") as fh:
                        b = fh.read()
                    L["score_file"] = {"path": path_s, "bytes": len(b), "md5": hashlib.md5(b).hexdigest()}
                    _, L["score"] = score(rows, read_outcomes(b))
    res["finished_at"] = nc.now()
    with open(os.path.join(args.out_dir, "nextlist.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    md = render(res)
    with open(os.path.join(args.out_dir, "nextlist.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 2 if res.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
