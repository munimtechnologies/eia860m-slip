"""phleak.py - a profile of PUDL's uncleaned PHMSA gas distribution leaks table
(_core_phmsagas__yearly_distribution_leaks), measured against the open questions of
catalyst-cooperative/pudl#5435 and #4646: commodity values, operating_state nulls and lists, the
proposed primary key, negative values, and whether each total equals the sum of its leak sources.
Pre-registration phleak-1 (docs/phleak-plan.md in munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library plus polars (to read the nightly parquet).

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict

VERSION = "0.1.0"
TABLE = "_core_phmsagas__yearly_distribution_leaks"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet" % TABLE
UA = {"User-Agent": "mv2-phleak/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
COLS = ("report_id", "report_date", "operator_id_phmsa", "commodity", "operating_state",
        "leak_severity", "leak_source", "mains", "services")
SEVERITIES = ("all_leaks", "hazardous_leaks")
# LEAK_SOURCE_PHMSAGAS in src/pudl/metadata/enums.py
SOURCES = ("construction_defect", "corrosion_failure", "equipment_failure", "excavation_damage",
           "incorrect_operation", "material_defect", "natural_force_damage", "other",
           "other_outside_force", "outside_force", "pipe_weld_joint_failure", "third_party",
           "total")
# The commodity map PUDL already applies in core_phmsagas__yearly_distribution_by_install_decade
COMMODITY_MAP = {
    "Natural Gas": "natural_gas",
    "Propane Gas": "propane_gas",
    "Landfill Gas": "landfill_gas",
    "Synthetic Gas": "synthetic_gas",
    "Hydrogen Gas": "hydrogen_gas",
    "Nitrogen Gas": "nitrogen_gas",
    "OTHER GAS: Natural Gas": "natural_gas",
    "OTHER GAS: Nitrogen": "nitrogen_gas",
    "OTHER GAS: Propane Gas": "propane_gas",
    "OTHER GAS: Propane": "propane_gas",
    "OTHER GAS: Other Gas - Propane": "propane_gas",
    "OTHER GAS: nitrogen": "nitrogen_gas",
    "OTHER GAS: METHANE": "natural_gas",
    "OTHER GAS: City of York": "other",
    "OTHER GAS: Fuel Gas": "other",
}
NULL = "<null>"
TOL = 1.0

# Gates and bars (docs/phleak-plan.md)
G2_MIN_ROWS = 10000
G2_YEARS = (2015, 2024)
G2_MAX_FIRST_YEAR = 2003
COMMODITY_YEAR = 2015
P1_MAX_NULL_SHARE = 0.01
P3_MIN = 0.95
P4_MIN = 0.99
P6_MIN_ROWS = 100
P6_MAX_YEAR = 2003
P6_MIN = 0.95

SINGLE = re.compile(r"[A-Z]{2}")
MULTI = re.compile(r"[A-Za-z]{2}(?:[\s,;/&]+[A-Za-z]{2})+")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def text(value):
    """None for null or NaN, else str(value) unchanged (not stripped)."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return str(value)


def num(value):
    """float, or None for null, NaN or text that is not a number."""
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(out) else out


def year(date):
    """Report year from a date or datetime string; 0 if there is none."""
    s = text(date)
    if not s:
        return 0
    found = re.match(r"(\d{4})", s.strip())
    return int(found.group(1)) if found else 0


def state_kind(value):
    """'null', 'single' (two capital letters), 'multi' (two or more two-letter codes separated
    by spaces, commas, semicolons, slashes or &) or 'other'."""
    s = text(value)
    if s is None or not s.strip():
        return "null"
    s = s.strip()
    if SINGLE.fullmatch(s):
        return "single"
    if MULTI.fullmatch(s):
        return "multi"
    return "other"


def share(a, b):
    return round(a / b, 6) if b else None


def span(store, key, y):
    rec = store.setdefault(key, [y, y])
    rec[0] = min(rec[0], y)
    rec[1] = max(rec[1], y)


class Profile:
    """One pass over the rows (tuples in COLS order)."""

    def __init__(self):
        self.rows = 0
        self.years = Counter()
        self.commodity = Counter()
        self.commodity_years = {}
        self.com_rows_by_year = Counter()
        self.com_null_by_year = Counter()
        self.state_kinds = Counter()
        self.state_null_by_year = Counter()
        self.multi_by_year = Counter()
        self.other_states = Counter()
        self.op_zero_by_year = Counter()
        self.op_null_rows = 0
        self.severity = Counter()
        self.source = Counter()
        self.source_years = {}
        self.empty_rows = 0
        self.neg_rows = 0
        self.negatives = []
        # (report_id, operator, year, commodity, operating_state) -> severity -> source ->
        # [mains, services, rows]
        self.groups = {}

    def add(self, row):
        rid, date, op, com, st, sev, src, mains, serv = row
        self.rows += 1
        y = year(date)
        self.years[y] += 1
        c = text(com)
        ckey = NULL if c is None else c
        self.commodity[ckey] += 1
        span(self.commodity_years, ckey, y)
        self.com_rows_by_year[y] += 1
        if c is None:
            self.com_null_by_year[y] += 1
        kind = state_kind(st)
        self.state_kinds[kind] += 1
        if kind == "null":
            self.state_null_by_year[y] += 1
        elif kind == "multi":
            self.multi_by_year[y] += 1
        elif kind == "other":
            self.other_states[text(st)] += 1
        o = text(op)
        if o is None:
            self.op_null_rows += 1
        elif num(o) == 0:
            self.op_zero_by_year[y] += 1
        sv = text(sev) or NULL
        sc = text(src) or NULL
        self.severity[sv] += 1
        self.source[sc] += 1
        span(self.source_years, sc, y)
        m, s = num(mains), num(serv)
        if m is None and s is None:
            self.empty_rows += 1
        if (m is not None and m < 0) or (s is not None and s < 0):
            self.neg_rows += 1
            if len(self.negatives) < 500:
                self.negatives.append([y, text(rid), o, text(st), sv, sc, m, s])
        st_key = text(st)
        gkey = (text(rid) or NULL, o or NULL, y, ckey, NULL if st_key is None else st_key)
        cells = self.groups.setdefault(gkey, {}).setdefault(sv, {})
        if sc in cells:
            cells[sc][2] += 1
        else:
            cells[sc] = [m, s, 1]

    def summary(self):
        real = [y for y in self.years if y]
        return {"rows": self.rows, "groups": len(self.groups),
                "years": [min(real), max(real)] if real else [],
                "rows_without_year": self.years.get(0, 0),
                "rows_by_year": {str(k): v for k, v in sorted(self.years.items())},
                "commodity": {k: [self.commodity[k]] + self.commodity_years[k]
                              for k in sorted(self.commodity)},
                "state_kinds": dict(sorted(self.state_kinds.items())),
                "state_null_by_year": {str(k): v for k, v in sorted(self.state_null_by_year.items())},
                "multi_state_by_year": {str(k): v for k, v in sorted(self.multi_by_year.items())},
                "other_state_values_top50": dict(self.other_states.most_common(50)),
                "operator_zero_by_year": {str(k): v for k, v in sorted(self.op_zero_by_year.items())},
                "operator_zero_rows": sum(self.op_zero_by_year.values()),
                "operator_null_rows": self.op_null_rows,
                "severity": dict(sorted(self.severity.items())),
                "source": {k: [self.source[k]] + self.source_years[k] for k in sorted(self.source)},
                "rows_both_values_null": self.empty_rows,
                "negative_rows": self.neg_rows}


def sum_checks(groups, tol=TOL):
    """For each report, severity and column (mains, services): does the 'total' source equal the
    sum of the other sources within tol? Null parts are left out; a total with no non-null part is
    'total_only', parts with no total are 'no_total'. Returns (counts, by_year, failures)."""
    counts, by_year, fails = Counter(), defaultdict(Counter), []
    for gkey, sevs in groups.items():
        y = gkey[2]
        for sv in sorted(sevs):
            cells = sevs[sv]
            for ci, col in ((0, "mains"), (1, "services")):
                tot = cells.get("total")
                tv = tot[ci] if tot else None
                parts = [v[ci] for k, v in cells.items() if k != "total" and v[ci] is not None]
                if tv is None and not parts:
                    continue
                if tv is None:
                    counts[col + "|no_total"] += 1
                    continue
                if not parts:
                    counts[col + "|total_only"] += 1
                    continue
                psum = sum(parts)
                diff = tv - psum
                counts[col + "|checked"] += 1
                counts[sv + "|" + col + "|checked"] += 1
                by_year[y]["checked"] += 1
                if abs(diff) <= tol:
                    counts[col + "|passed"] += 1
                else:
                    counts[col + "|failed"] += 1
                    counts[sv + "|" + col + "|failed"] += 1
                    by_year[y]["failed"] += 1
                    fails.append([y, gkey[0], gkey[1], gkey[3], gkey[4], sv, col, tv, psum, diff,
                                  len(parts)])
    return counts, by_year, fails


def haz_checks(groups):
    """Hazardous leaks should not exceed all leaks for the same report, source and column."""
    counts, viol = Counter(), []
    for gkey, sevs in groups.items():
        a, h = sevs.get("all_leaks"), sevs.get("hazardous_leaks")
        if not a or not h:
            continue
        for src in sorted(set(a) & set(h)):
            for ci, col in ((0, "mains"), (1, "services")):
                av, hv = a[src][ci], h[src][ci]
                if av is None or hv is None:
                    continue
                counts["compared"] += 1
                if hv <= av:
                    counts["ok"] += 1
                else:
                    counts["hazardous_gt_all"] += 1
                    if len(viol) < 5000:
                        viol.append([gkey[2], gkey[0], gkey[1], gkey[3], gkey[4], src, col, av, hv])
    return counts, viol


def pk_dupes(groups):
    """Duplicate rows on the key PUDL proposes (report_id, operator_id_phmsa, operating_state,
    leak_severity, leak_source), null counted as a value. Returns (extra_rows, dup_keys, examples)."""
    prefix = Counter((g[0], g[1], g[4]) for g in groups)
    seen = Counter()
    for gkey, sevs in groups.items():
        multi = prefix[(gkey[0], gkey[1], gkey[4])] > 1
        for sv, cells in sevs.items():
            for src, cell in cells.items():
                if multi or cell[2] > 1:
                    seen[(gkey[0], gkey[1], gkey[4], sv, src)] += cell[2]
    dups = {k: n for k, n in seen.items() if n > 1}
    examples = [list(k) + [n] for k, n in sorted(dups.items())[:500]]
    return sum(n - 1 for n in dups.values()), len(dups), examples


def multi_state_score(multi_by_year, min_rows=P6_MIN_ROWS, max_year=P6_MAX_YEAR, bar=P6_MIN):
    rows = sum(multi_by_year.values())
    early = sum(n for y, n in multi_by_year.items() if 0 < y <= max_year)
    sh = share(early, rows)
    return {"rows": rows, "rows_to_" + str(max_year): early, "share": sh,
            "ok": rows >= min_rows and sh is not None and sh >= bar}


def commodity_measures(prof):
    pre = sum(prof.com_rows_by_year[y] - prof.com_null_by_year[y]
              for y in prof.com_rows_by_year if 0 < y < COMMODITY_YEAR)
    post_rows = sum(n for y, n in prof.com_rows_by_year.items() if y >= COMMODITY_YEAR)
    post_null = sum(n for y, n in prof.com_null_by_year.items() if y >= COMMODITY_YEAR)
    unmapped = sorted(v for v in prof.commodity if v != NULL and v not in COMMODITY_MAP)
    return {"pre_%d_nonnull_rows" % COMMODITY_YEAR: pre,
            "from_%d_rows" % COMMODITY_YEAR: post_rows,
            "from_%d_null_rows" % COMMODITY_YEAR: post_null,
            "from_%d_null_share" % COMMODITY_YEAR: share(post_null, post_rows),
            "unmapped_values": unmapped,
            "unmapped_rows": sum(prof.commodity[v] for v in unmapped)}


def ok(value, bar):
    return value is not None and value >= bar


def score(prof):
    m, tables = {}, {}
    cm = commodity_measures(prof)
    m["commodity"] = cm
    counts, by_year, fails = sum_checks(prof.groups)
    checked = counts["mains|checked"] + counts["services|checked"]
    passed = counts["mains|passed"] + counts["services|passed"]
    m["sums"] = dict(sorted(counts.items()), checked=checked, passed=passed,
                     share=share(passed, checked),
                     by_year={str(y): dict(c) for y, c in sorted(by_year.items())})
    hz, viol = haz_checks(prof.groups)
    m["hazardous_vs_all"] = dict(sorted(hz.items()), share=share(hz["ok"], hz["compared"]))
    extra, keys, ex = pk_dupes(prof.groups)
    m["primary_key"] = {"extra_rows": extra, "duplicate_keys": keys}
    ms = multi_state_score(prof.multi_by_year)
    m["multi_state"] = ms
    m["negatives"] = {"rows": prof.neg_rows}
    pre_key = "pre_%d_nonnull_rows" % COMMODITY_YEAR
    null_key = "from_%d_null_share" % COMMODITY_YEAR
    scores = {"P1": cm[pre_key] == 0 and cm[null_key] is not None
              and cm[null_key] <= P1_MAX_NULL_SHARE,
              "P2": not cm["unmapped_values"],
              "P3": ok(m["sums"]["share"], P3_MIN),
              "P4": ok(m["hazardous_vs_all"]["share"], P4_MIN),
              "P5": extra == 0,
              "P6": bool(ms["ok"]),
              "P7": prof.neg_rows == 0}
    tables["phleak-sum-failures.csv"] = (
        ["report_year", "report_id", "operator_id_phmsa", "commodity", "operating_state",
         "leak_severity", "column", "total", "sum_of_sources", "total_minus_sum", "sources"],
        sorted(fails, key=lambda r: [str(x) for x in r]))
    tables["phleak-hazardous-gt-all.csv"] = (
        ["report_year", "report_id", "operator_id_phmsa", "commodity", "operating_state",
         "leak_source", "column", "all_leaks", "hazardous_leaks"], viol)
    tables["phleak-pk-duplicates.csv"] = (
        ["report_id", "operator_id_phmsa", "operating_state", "leak_severity", "leak_source",
         "rows"], ex)
    multi = []
    for gkey, sevs in sorted(prof.groups.items(), key=lambda kv: [str(x) for x in kv[0]]):
        if state_kind(None if gkey[4] == NULL else gkey[4]) == "multi":
            rows = sum(cell[2] for cells in sevs.values() for cell in cells.values())
            multi.append([gkey[2], gkey[0], gkey[1], gkey[3], gkey[4], rows])
    tables["phleak-multistate-reports.csv"] = (
        ["report_year", "report_id", "operator_id_phmsa", "commodity", "operating_state", "rows"],
        multi)
    tables["phleak-negatives.csv"] = (
        ["report_year", "report_id", "operator_id_phmsa", "operating_state", "leak_severity",
         "leak_source", "mains", "services"], prof.negatives)
    tables["phleak-commodity.csv"] = (
        ["commodity", "rows", "first_year", "last_year", "pudl_install_decade_map"],
        [[k, prof.commodity[k]] + prof.commodity_years[k] + [COMMODITY_MAP.get(k, "")]
         for k in sorted(prof.commodity)])
    return m, scores, tables


def gates(info, prof):
    real = [y for y in prof.years if y]
    g1 = bool(info.get("bytes")) and not info.get("missing_cols")
    g2 = (prof.rows >= G2_MIN_ROWS and all(y in prof.years for y in G2_YEARS)
          and bool(real) and min(real) <= G2_MAX_FIRST_YEAR)
    g3 = (bool(prof.severity) and set(prof.severity) <= set(SEVERITIES)
          and set(prof.source) <= set(SOURCES))
    return ({"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)},
            {"rows": prof.rows, "years": [min(real), max(real)] if real else [],
             "severity_values": sorted(prof.severity), "source_values": sorted(prof.source)})


def download(url, tries=4, timeout=300):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # noqa: BLE001 - retried, then raised
            last = exc
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("%s: %s" % (url, last))


def load(pl, data_dir):
    raw, headers = download(URL)
    path = os.path.join(data_dir, TABLE + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    df = pl.read_parquet(io.BytesIO(raw))
    info = {"url": URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "last_modified": headers.get("Last-Modified"), "rows": df.height,
            "dtypes": {c: str(t) for c, t in zip(df.columns, df.dtypes)},
            "missing_cols": [c for c in COLS if c not in df.columns], "saved_to": path}
    del raw
    if info["missing_cols"]:
        return info, iter(())
    df = df.select(list(COLS)).with_columns(
        [pl.col(c).cast(pl.String) for c in COLS[:7]]
        + [pl.col(c).cast(pl.Float64) for c in COLS[7:]])
    return info, df.iter_rows()


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phleak-20261110")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phleak.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now()}
    info, rows = load(pl, a.data_dir)
    res["table"] = info
    prof = Profile()
    for row in rows:
        prof.add(row)
    g, gm = gates(info, prof)
    res["gates"], res["gate_measures"] = g, gm
    res["profile"] = prof.summary()
    print("gates", g, gm)
    if all(g.values()):
        m, scores, tables = score(prof)
        res["measures"], res["scores"] = m, dict(g, **scores)
        for name, (header, body) in tables.items():
            write_csv(os.path.join(a.out_dir, name), header, body)
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phleak.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
