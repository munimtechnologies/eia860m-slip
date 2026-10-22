"""gapcensus: which generators leave EIA's monthly EIA-860M workbook, and do they come back?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive follow-up to docs/heldtrace.md (job retiredgap-v1 found 279 generators missing from
EIA's own November 2024 file and listed again in December); no prediction is tested. It replays
the 134 workbooks of PUDL's raw archive (Zenodo record 22995197, md5-checked as layouts.py 0.1.0
checks them) with history.py 0.1.0's reader and the same event rule that wrote the rebuilt
changelog (first, changed, left, back), and:

- rebuilds data/eia860m_changelog_from_workbooks.csv.gz and compares its text with the
  published copy (a reproducibility check of the same code, not an independent check);
- for every "left" event, records the sheet the generator was on the month before and when, if
  ever, it came back: after 1 month, 2 to 12 months, more than 12, or not by the last month;
- lists every month in which generators were missing for exactly one month, and whether PUDL's
  changelog has a record in force for them in that month;
- for November 2024, which sheets of the workbook (the left-out ones included) list the
  generators that left, and the changelog rows of those that were not back in December or were
  not on the Retired sheet;
- with --eia-month YYYY-MM, downloads EIA's own file for that month (honest User-Agent; PK magic,
  bytes and md5 recorded): a month in the archive is compared with the archive's copy by md5; the
  month after the archive's last is read and its rows are appended to the rebuilt changelog.

    python gapcensus.py --data-dir /data --out-dir /out [--eia-month 2026-09]
"""

import argparse
import collections
import csv
import gzip
import io
import json
import os
import time
import urllib.request
import zipfile

import pandas as pd

import eia860m_slip as es
import history as hs
import layouts as ly
import retiredgap as rg
import revert as rv

__version__ = "0.1.0"
PUBLISHED = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/"
             "e4ecb0d748bf7dc4738c27811e5fc07775eb72a3/data/eia860m_changelog_from_workbooks.csv.gz")
UA = "mv2-munim-gapcensus/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
OUTCOMES = ("back_1", "back_2_12", "back_13_plus", "not_back")
SHEETS = ("Operating", "Planned", "Retired")
NOV = ("2024-11", "2024-12")
PUDL_COLS = ("plant_id_eia", "generator_id", "report_date", "valid_until_date")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def m_index(month):
    """'YYYY-MM' -> months since year 0, so that consecutive months differ by 1."""
    y, m = month.split("-")
    return int(y) * 12 + int(m) - 1


def m_str(i):
    return "%04d-%02d" % (i // 12, i % 12 + 1)


def next_month(month):
    return m_str(m_index(month) + 1)


def sheet_group(sheet):
    """A sheet name -> Operating, Planned, Retired or other."""
    s = str(sheet or "").strip().lower()
    for g in SHEETS:
        if s.startswith(g.lower()):
            return g
    return "other"


def outcome(gap):
    """Months absent before coming back (None: not back) -> one of OUTCOMES."""
    if gap is None:
        return "not_back"
    return "back_1" if gap == 1 else "back_2_12" if gap <= 12 else "back_13_plus"


class Census:
    """The rebuilt changelog's event rule (history.replay's loop) plus a record of every left
    event and when the generator came back."""

    def __init__(self):
        self.last, self.prev = {}, set()
        self.open = {}          # key -> index into self.lefts of its open left event
        self.lefts = []         # [month, key, sheet before, month back or None]
        self.months = []

    def feed(self, month, wm, sheets):
        """One month: wm {key: projection}, sheets {key: sheet} -> the month's changelog rows as
        (key, event, v), in history.replay's order (listed keys sorted, then left keys sorted)."""
        rows = []
        for k in sorted(wm):
            w = wm[k]
            v = (sheets[k], w[0], w[1], None if w[2] is None else round(w[2], 3))
            ev = ("first" if k not in self.last else "back" if k not in self.prev
                  else "changed" if v != self.last[k] else None)
            if ev == "back" and k in self.open:
                self.lefts[self.open.pop(k)][3] = month
            self.last[k] = v
            if ev:
                rows.append((k, ev, v))
        for k in sorted(self.prev - set(wm)):
            rows.append((k, "left", None))
            self.open[k] = len(self.lefts)
            self.lefts.append([month, k, self.last[k][0], None])
        self.prev = set(wm)
        self.months.append(month)
        return rows

    def gap(self, e):
        return None if e[3] is None else m_index(e[3]) - m_index(e[0])

    def outcomes(self):
        """Left events by year left and sheet group before leaving -> counts by outcome."""
        c = collections.Counter()
        for e in self.lefts:
            c[(e[0][:4], sheet_group(e[2]), outcome(self.gap(e)))] += 1
        groups = sorted({(y, g) for y, g, _ in c})
        return [dict({"year": y, "sheet": g, "left": sum(c[(y, g, o)] for o in OUTCOMES)},
                     **{o: c[(y, g, o)] for o in OUTCOMES}) for y, g in groups]

    def one_month(self):
        """[(missing month, key, sheet before)] for every generator missing for exactly one month."""
        return [(e[0], e[1], e[2]) for e in self.lefts if self.gap(e) == 1]


def by_sheet(rows):
    """Outcome rows -> totals by sheet group (all years)."""
    t = collections.OrderedDict()
    for r in rows:
        x = t.setdefault(r["sheet"], dict({"sheet": r["sheet"], "left": 0}, **{o: 0 for o in OUTCOMES}))
        for c in ("left",) + OUTCOMES:
            x[c] += r[c]
    return [t[g] for g in sorted(t)]


def gap_months(pairs, pudl=None):
    """One-month gaps [(month, key, sheet)] and {(key, month): PUDL status} -> one row per month."""
    out = collections.OrderedDict()
    for m, k, s in sorted(pairs):
        r = out.setdefault(m, dict({"month": m, "n": 0, "pudl_in_force": 0},
                                   **{g: 0 for g in SHEETS + ("other",)}))
        r["n"] += 1
        r[sheet_group(s)] += 1
        if pudl and pudl.get((k, m)) == "in force":
            r["pudl_in_force"] += 1
    return list(out.values())


def pudl_status(df, pairs):
    """PUDL's changelog rows (columns PUDL_COLS) and [(key, 'YYYY-MM')] -> {(key, month):
    'in force' (latest record reported by then has no valid_until_date or a later one),
    'closed' (it ends on or before the month) or 'none' (no record reported by then)}."""
    key = df["plant_id_eia"].astype(str) + "/" + df["generator_id"].astype(str)
    want = {k for k, _ in pairs}
    sub = df.assign(key=key)[key.isin(want)]
    recs = collections.defaultdict(list)
    for k, r, u in zip(sub["key"], pd.to_datetime(sub["report_date"]), pd.to_datetime(sub["valid_until_date"])):
        recs[k].append((r, u))
    out = {}
    for k, m in pairs:
        t = pd.Timestamp(m + "-01")
        got = sorted(((r, u) for r, u in recs.get(k, []) if r <= t), key=lambda x: x[0])
        if not got:
            out[(k, m)] = "none"
        else:
            u = got[-1][1]
            out[(k, m)] = "in force" if pd.isna(u) or u > t else "closed"
    return out


def log_text(rows):
    """Changelog row dicts -> the CSV text history.py writes (csv.DictWriter, header first)."""
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, hs.LOG_COLS)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def compare_text(published, rebuilt):
    """Two CSV texts -> {same, lines_published, lines_rebuilt, first_difference}."""
    a, b = published.splitlines(), rebuilt.splitlines()
    first = next((i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
    if first is None and len(a) != len(b):
        first = min(len(a), len(b)) + 1
    return {"same": published == rebuilt, "lines_published": len(a), "lines_rebuilt": len(b),
            "first_difference": first,
            "published_line": a[first - 1] if first and first <= len(a) else None,
            "rebuilt_line": b[first - 1] if first and first <= len(b) else None}


def eia_plan(month, archive_months):
    """What --eia-month does with a month: 'compare' (the archive has it), 'append' (the month
    after the archive's last) or 'skip'."""
    if month in archive_months:
        return "compare"
    if archive_months and month == next_month(archive_months[-1]):
        return "append"
    return "skip"


def nov_sheets(book, keys):
    """A workbook read by retiredgap.read_book and keys -> counts of where each key is listed
    (sheet names joined with '+', every sheet counted, 'not listed' when on none)."""
    where = collections.defaultdict(list)
    for s in book:
        for k in s["keys"]:
            where[k].append(s["sheet"])
    return collections.Counter("+".join(where[k]) if where.get(k) else "not listed" for k in keys)


def _get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def render(result):
    md = ["# gapcensus %s: generators that leave EIA's monthly EIA-860M workbook" % __version__, "",
          "Descriptive follow-up to docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. "
          "(made with AI agents).", ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    md += ["Workbook months read: %d (%s to %s); not readable: %s." % (
        len(result["months"]), result["months"][0], result["months"][-1],
        ", ".join(result["months_unreadable"]) or "none"), ""]
    c = result.get("published")
    md += ["## Rebuilt changelog against the published copy", ""]
    if c is None or c.get("error"):
        md += ["Not compared: %s" % (c or {}).get("error", "no published copy"), ""]
    else:
        md += ["Published: %s (%d bytes, md5 %s)." % (c["url"], c["bytes"], c["md5"]), "",
               "Same text through %s: %s. Lines: published %d, rebuilt %d. First difference: %s." % (
                   c["through"], c["same"], c["lines_published"], c["lines_rebuilt"],
                   c["first_difference"] or "none"), ""]
        if c["first_difference"]:
            md += ["Published line: `%s`" % c["published_line"], "", "Rebuilt line: `%s`" % c["rebuilt_line"], ""]
    md += ["Rebuilt rows: %d (%s)." % (result["log_rows"], result["log_file"]), ""]
    e = result.get("eia")
    if e:
        md += ["## EIA's own file for %s" % e["month"], "",
               "Plan: %s. URL: %s. Bytes: %s. md5: %s. Errors: %s." % (
                   e["plan"], e.get("url") or "-", e.get("bytes"), e.get("md5"), "; ".join(e.get("errors", [])) or "none")]
        if e["plan"] == "compare":
            md += ["", "Archive copy: %s bytes, md5 %s. Same file: %s." % (
                e.get("archive_bytes"), e.get("archive_md5"), e.get("same_file"))]
        if e["plan"] == "append":
            md += ["", "Readable: %s; problems: %s. Keys: %s. Rows appended: %s (%s)." % (
                e.get("readable"), "; ".join(e.get("problems", [])) or "none", e.get("keys"),
                e.get("rows_appended"), ", ".join("%s %d" % (k, v) for k, v in sorted(e.get("events", {}).items())) or "none")]
        md.append("")
    res = result["result"]
    md += ["## Left events by sheet the month before, and what happened (all years)", "",
           "Last month read: %s. back_1: listed again the next month; back_2_12 and back_13_plus: "
           "after that many months; not_back: not listed again by the last month." % result["months"][-1], "",
           "| sheet | left | %s |" % " | ".join(OUTCOMES), "|---|---|" + "---|" * len(OUTCOMES)]
    for r in res["by_sheet"]:
        md.append("| %s | %d | %s |" % (r["sheet"], r["left"], " | ".join(str(r[o]) for o in OUTCOMES)))
    md += ["", "## By year left", "", "| year | sheet | left | %s |" % " | ".join(OUTCOMES),
           "|---|---|---|" + "---|" * len(OUTCOMES)]
    for r in res["outcomes"]:
        md.append("| %s | %s | %d | %s |" % (r["year"], r["sheet"], r["left"],
                                            " | ".join(str(r[o]) for o in OUTCOMES)))
    md += ["", "## Months in which generators were missing for exactly one month", "",
           "pudl_in_force: PUDL's changelog has a record in force for the generator in that month "
           "(its latest record reported by then has no valid_until_date or a later one). PUDL: %s." % (
               result.get("pudl_note") or "-"), "",
           "| missing month | generators | %s | pudl_in_force |" % " | ".join(SHEETS + ("other",)),
           "|---|---|" + "---|" * (len(SHEETS) + 2)]
    for r in res["gap_months"]:
        md.append("| %s | %d | %s | %d |" % (r["month"], r["n"], " | ".join(
            str(r[g]) for g in SHEETS + ("other",)), r["pudl_in_force"]))
    md += ["", "PUDL status of all one-month gaps: %s." % (", ".join(
        "%s %d" % (k, v) for k, v in sorted(res["pudl_counts"].items())) or "none")]
    n = res.get("nov")
    if n:
        md += ["", "## November 2024", "",
               "Generators that left in %s: %d. Where the %s workbook lists them (every sheet, the "
               "left-out ones included):" % (NOV[0], n["left"], NOV[0]), "", "| sheets | generators |", "|---|---|"]
        md += ["| %s | %d |" % (x["where"], x["n"]) for x in n["where"]]
        md += ["", "Outcomes of the %s left events: %s." % (NOV[0], ", ".join(
            "%s %d" % (o, n["outcomes"].get(o, 0)) for o in OUTCOMES)), "",
               "### Changelog rows of those not back in %s or not on the Retired sheet before leaving" % NOV[1], "",
               "| report_month | key | event | sheet | status | planned_month | nameplate_mw |",
               "|---|---|---|---|---|---|---|"]
        md += ["| %s | %s | %s | %s | %s | %s | %s |" % (r["report_month"], r["key"], r["event"], r["sheet"],
                                                        r["status"], r["planned_month"], r["nameplate_mw"])
               for r in n["rows"]]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--eia-month", default=None, help="YYYY-MM: EIA's own file to compare or append")
    ap.add_argument("--published", default=PUBLISHED)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "history": hs.__version__, "user_agent": UA, "started_at": now()}
    zips, paths = [], []
    for year in ly.YEARS:
        p, z = ly.get_zip(year, args.data_dir, ly.ZIP_MD5.get(year), None)
        z.update(year=year, ok=p is not None)
        zips.append(z)
        if p is not None:
            paths.append((year, p))
    result["zips"] = zips
    if len(paths) != len(ly.YEARS):
        result["error"] = "zips with a listed md5: %d of %d" % (len(paths), len(ly.YEARS))
    else:
        census, rows, infos = Census(), [], []

        def feed(month, wb):
            for k, ev, v in census.feed(month, rv.w_map(wb), dict(zip(wb["key"], wb["sheet"]))):
                rows.append(hs.log_row(month, k, ev, v))

        for month, wb in hs.workbooks(paths, infos):
            if wb is not None:
                feed(month, wb)
        archive_months = [i["month"] for i in infos]
        result["months_unreadable"] = [i["month"] for i in infos if not i["readable"]]
        archive_rows = len(rows)
        if args.eia_month:
            e = {"month": args.eia_month, "plan": eia_plan(args.eia_month, archive_months)}
            if e["plan"] != "skip":
                data, e["url"], e["errors"] = rg.download(rg.eia_urls(args.eia_month), get=_get)
                if data is not None:
                    e.update(bytes=len(data), md5=rg.md5(data))
                    if e["plan"] == "compare":
                        a = next(i for i in infos if i["month"] == args.eia_month)
                        with zipfile.ZipFile(dict(paths)[int(args.eia_month[:4])]) as zf:
                            e["archive_bytes"] = len(zf.read(a["member"]))
                        e.update(archive_md5=a["md5"], same_file=a["md5"] == e["md5"])
                    else:
                        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
                        wb, info = hs.month_frame(args.eia_month, sheets)
                        e.update(readable=info["readable"], problems=info["problems"], keys=info["keys"])
                        if info["readable"]:
                            feed(args.eia_month, wb)
                            new = rows[archive_rows:]
                            e["rows_appended"] = len(new)
                            e["events"] = dict(collections.Counter(r["event"] for r in new))
            result["eia"] = e
        result["months"] = census.months
        text = log_text(rows)
        result["log_file"] = hs.LOG_FILE
        result["log_rows"] = len(rows)
        with gzip.open(os.path.join(args.out_dir, hs.LOG_FILE), "wt", newline="", encoding="utf-8") as fh:
            fh.write(text)
        try:
            raw = _get(args.published)
            pub = gzip.decompress(raw).decode("utf-8")
            c = compare_text(pub, log_text(rows[:archive_rows]))
            c.update(url=args.published, bytes=len(raw), md5=rg.md5(raw), through=archive_months[-1])
        except Exception as ex:  # recorded, not raised
            c = {"error": "%s: %s" % (type(ex).__name__, ex)}
        result["published"] = c
        pairs = census.one_month()
        pudl = {}
        try:
            path = es.find_parquet(args.data_dir)
            df = pd.read_parquet(path, columns=list(PUDL_COLS))
            pudl = pudl_status(df, [(k, m) for m, k, _ in pairs])
            result["pudl_note"] = "%s, latest report %s" % (os.path.basename(path), str(df["report_date"].max())[:10])
        except Exception as ex:  # recorded, not raised
            result["pudl_note"] = "not read: %s: %s" % (type(ex).__name__, ex)
        out = census.outcomes()
        res = {"outcomes": out, "by_sheet": by_sheet(out), "gap_months": gap_months(pairs, pudl),
               "pudl_counts": dict(collections.Counter(pudl.values()))}
        nov = [e for e in census.lefts if e[0] == NOV[0]]
        if nov:
            n = {"left": len(nov), "outcomes": dict(collections.Counter(outcome(census.gap(e)) for e in nov))}
            with zipfile.ZipFile(dict(paths)[int(NOV[0][:4])]) as zf:
                member = rg.member_for(zf.namelist(), NOV[0])
                book, err = rg.read_book(zf.read(member)) if member else (None, "no member")
            n["where"] = ([{"where": w, "n": c} for w, c in nov_sheets(book, [e[1] for e in nov]).most_common()]
                          if book else [{"where": "not read: %s" % err, "n": len(nov)}])
            odd = {e[1] for e in nov if e[3] != NOV[1] or sheet_group(e[2]) != "Retired"}
            n["keys"] = sorted(odd)
            n["rows"] = [r for r in rows if r["key"] in odd]
            res["nov"] = n
        result["result"] = res
        with open(os.path.join(args.out_dir, "gapcensus_left_events.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["month_left", "key", "sheet_before", "month_back", "months_absent", "outcome",
                        "pudl_in_missing_month"])
            for e in census.lefts:
                g = census.gap(e)
                w.writerow([e[0], e[1], e[2], e[3] or "", "" if g is None else g, outcome(g),
                            pudl.get((e[1], e[0]), "") if g == 1 else ""])
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "gapcensus.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "gapcensus.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
