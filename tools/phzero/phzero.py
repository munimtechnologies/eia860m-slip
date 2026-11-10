"""phzero.py - can the zero operator ids left in PUDL's PHMSA gas distribution operators table
(core_phmsagas__yearly_distribution_operators) be filled with confidence?

PUDL's backfill_zero_operator_id_phmsa (src/pudl/transform/phmsagas.py) replaces a 0 id only from
a LATER report (groupby on the title-cased operator name, then bfill). This tool measures, on the
published table, how many zero (or null) ids remain, how many have an exact-name match with a
real id (and whether it is later, same-year or only earlier), how many a normalized name or a
normalized name plus office state would give exactly one id, and how often each rule gives the
right id when it is tried on rows whose id is known (leave-one-out).
Pre-registration phzero-1 (docs/phzero-plan.md in munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library plus polars (to read the nightly parquet).

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import bisect
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
TABLE = "core_phmsagas__yearly_distribution_operators"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet" % TABLE
UA = {"User-Agent": "mv2-phzero/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
NEED = ("report_id", "report_date", "operator_id_phmsa", "operator_name_phmsa")
OPTIONAL = ("office_state",)
# Tokens dropped by the normalized name (after lower-casing, & -> and, punctuation -> space)
STOP = frozenset(("inc", "incorporated", "co", "company", "corp", "corporation", "llc", "ltd",
                  "lp", "the", "of"))
RULES = ("exact", "norm", "norm_state")
EARLY = 1990
MISS_CAP = 5000

# Gates and bars (docs/phzero-plan.md)
G2_MIN_ROWS = 50000
G2_MAX_FIRST_YEAR = 1975
G2_LAST_YEAR = 2024
G3_MIN_ZEROS = 500
P1_RANGE = (1500, 2800)
P2_YEARS = (1976, 1983)
P2_MIN = 0.99
P3_MAX = 0.01
P4_MIN = 0.05
P5_MIN_GAIN = 0.05
P6_MIN = 0.98
P7_MIN = 0.97
P8_MIN = 0.97


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


def parse_id(value):
    """(id, kind) with kind 'null', 'zero' or 'id'."""
    v = num(value)
    if v is None:
        return None, "null"
    if v == 0:
        return 0, "zero"
    return int(v), "id"


def exact_key(name):
    """PUDL's grouping key: the name title-cased (str.title), nothing else; None if blank."""
    s = text(name)
    if s is None or not s.strip():
        return None
    return s.title()


def norm_key(name):
    """Lower-case, & -> and, every non-alphanumeric run -> one space, STOP tokens dropped."""
    s = text(name)
    if s is None:
        return None
    s = re.sub(r"[^a-z0-9]+", " ", s.lower().replace("&", " and "))
    toks = [t for t in s.split() if t not in STOP]
    return " ".join(toks) or None


def state_key(value):
    s = text(value)
    if s is None or not s.strip():
        return None
    return s.strip().upper()


def share(a, b):
    return round(a / b, 6) if b else None


def ok(value, bar):
    return value is not None and value >= bar


def ids_text(ids):
    return " ".join(str(i) for i in ids)


# row layout: [year, report_id, id, kind, exact, norm, state, raw_name]
Y, RID, ID, KIND, EXACT, NORM, STATE, RAW = range(8)


class Study:
    """Collects the rows (tuples: report_id, report_date, operator_id_phmsa, operator_name_phmsa,
    office_state)."""

    def __init__(self):
        self.rows = []
        self.years = Counter()
        self.kinds = Counter()
        self.zero_by_year = Counter()

    def add(self, row):
        rid, date, op, name, st = row
        y = year(date)
        i, kind = parse_id(op)
        self.rows.append([y, text(rid), i, kind, exact_key(name), norm_key(name), state_key(st),
                          text(name)])
        self.years[y] += 1
        self.kinds[kind] += 1
        if kind != "id":
            self.zero_by_year[y] += 1

    def zeros(self):
        return self.kinds["zero"] + self.kinds["null"]


def key_of(r, which):
    if which == "exact":
        return r[EXACT]
    if which == "norm":
        return r[NORM]
    if r[NORM] is None or r[STATE] is None:
        return None
    return (r[NORM], r[STATE])


def index(rows, which):
    """key -> [(year, id)] over rows with a real (non-zero, non-null) id."""
    idx = defaultdict(list)
    for r in rows:
        if r[KIND] != "id":
            continue
        k = key_of(r, which)
        if k is not None:
            idx[k].append((r[Y], r[ID]))
    return idx


def zero_rows(rows, idxs):
    """For every zero or null id row: the ids each rule offers, when the exact-name ids were
    reported (later / same_year / earlier / none) and the id a cautious fill would propose
    (exact unique, else normalized name + state unique, else normalized name unique)."""
    counts, out = Counter(), []
    for r in rows:
        if r[KIND] == "id":
            continue
        counts["zero_or_null"] += 1
        counts[r[KIND]] += 1
        y = r[Y]
        if 0 < y < EARLY:
            counts["before_%d" % EARLY] += 1
        if P2_YEARS[0] <= y <= P2_YEARS[1]:
            counts["in_%d_%d" % P2_YEARS] += 1
        rec = {}
        for which in RULES:
            k = key_of(r, which)
            ids = sorted({i for _, i in idxs[which].get(k, [])}) if k is not None else []
            rec[which] = ids
            if ids:
                counts[which + "|any"] += 1
            if len(ids) == 1:
                counts[which + "|unique"] += 1
        ex = idxs["exact"].get(r[EXACT], []) if r[EXACT] is not None else []
        if any(yy > y for yy, _ in ex):
            when = "later"
        elif any(yy == y for yy, _ in ex):
            when = "same_year"
        elif ex:
            when = "earlier"
        else:
            when = "none"
        counts["exact|when_" + when] += 1
        proposal, rule = "", ""
        for which in ("exact", "norm_state", "norm"):
            if len(rec[which]) == 1:
                proposal, rule = rec[which][0], which
                break
        if rule:
            counts["proposal|" + rule] += 1
        out.append([y, r[RID], r[KIND], r[RAW], r[STATE] or "", ids_text(rec["exact"]), when,
                    ids_text(rec["norm"]), ids_text(rec["norm_state"]), proposal, rule])
    return counts, out


def tally(c, misses, rule, eras, r, true, pred):
    good = pred == {true}
    for e in eras:
        c["%s|%s|predicted" % (rule, e)] += 1
        if good:
            c["%s|%s|correct" % (rule, e)] += 1
        elif len(pred) > 1:
            c["%s|%s|tie" % (rule, e)] += 1
    if not good and len(misses) < MISS_CAP:
        misses.append([rule, r[Y], r[RID], r[RAW], r[STATE] or "", true, ids_text(sorted(pred))])


def loo(rows, idxs, early=EARLY):
    """Leave-one-out on rows with a real id: what would each rule give if this id were 0?
    pudl_later = ids on the nearest later year with the same exact name (PUDL's bfill; a year
    with two ids counts as a tie, not correct); exact_earlier = the same looking back (a ffill);
    unique_<rule> = the other rows' ids for the key, used only if there is exactly one."""
    c, misses = Counter(), []
    counters = {w: {k: Counter(i for _, i in v) for k, v in idxs[w].items()} for w in RULES}
    by_year = {}
    for k, v in idxs["exact"].items():
        d = defaultdict(set)
        for yy, i in v:
            d[yy].add(i)
        ys = sorted(d)
        by_year[k] = (ys, [d[yy] for yy in ys])
    for r in rows:
        if r[KIND] != "id":
            continue
        y, true = r[Y], r[ID]
        eras = ["all"] + (["early"] if 0 < y < early else [])
        if r[EXACT] in by_year:
            ys, sets = by_year[r[EXACT]]
            j = bisect.bisect_right(ys, y)
            if j < len(ys):
                tally(c, misses, "pudl_later", eras, r, true, sets[j])
            j = bisect.bisect_left(ys, y) - 1
            if j >= 0:
                tally(c, misses, "exact_earlier", eras, r, true, sets[j])
        for w in RULES:
            k = key_of(r, w)
            if k is None or k not in counters[w]:
                continue
            cnt = counters[w][k]
            others = {i for i, n in cnt.items() if n - (1 if i == true else 0) > 0}
            if len(others) == 1:
                tally(c, misses, "unique_" + w, eras, r, true, others)
    return c, misses


def precision(c, rule, era):
    return share(c["%s|%s|correct" % (rule, era)], c["%s|%s|predicted" % (rule, era)])


def multi_id_names(idxs):
    """Exact (title-cased) names reported with more than one real id."""
    out = []
    for k, v in idxs["exact"].items():
        ids = sorted({i for _, i in v})
        if len(ids) > 1:
            ys = [yy for yy, _ in v]
            out.append([k, len(ids), ids_text(ids), len(v), min(ys), max(ys)])
    out.sort(key=lambda x: (-x[1], x[0]))
    return out


def score(st):
    idxs = {w: index(st.rows, w) for w in RULES}
    zc, zrows = zero_rows(st.rows, idxs)
    lc, misses = loo(st.rows, idxs)
    multi = multi_id_names(idxs)
    z = zc["zero_or_null"]
    shares = {"before_%d" % EARLY: share(zc["before_%d" % EARLY], z),
              "in_%d_%d" % P2_YEARS: share(zc["in_%d_%d" % P2_YEARS], z),
              "exact_later": share(zc["exact|when_later"], z),
              "exact_unique": share(zc["exact|unique"], z),
              "norm_unique": share(zc["norm|unique"], z),
              "norm_state_unique": share(zc["norm_state|unique"], z),
              "norm_gain_over_exact": share(zc["norm|unique"] - zc["exact|unique"], z)}
    prec = {"%s|%s" % (rule, era): precision(lc, rule, era)
            for rule in ("pudl_later", "exact_earlier") + tuple("unique_" + w for w in RULES)
            for era in ("all", "early")}
    m = {"zeros": dict(sorted(zc.items())), "shares": shares, "loo": dict(sorted(lc.items())),
         "precision": prec, "multi_id_exact_names": len(multi),
         "zeros_by_year": {str(k): v for k, v in sorted(st.zero_by_year.items())},
         "distinct": {w: len(idxs[w]) for w in RULES}}
    scores = {"P1": P1_RANGE[0] <= z <= P1_RANGE[1],
              "P2": ok(shares["in_%d_%d" % P2_YEARS], P2_MIN),
              "P3": shares["exact_later"] is not None and shares["exact_later"] <= P3_MAX,
              "P4": ok(shares["exact_unique"], P4_MIN),
              "P5": ok(shares["norm_gain_over_exact"], P5_MIN_GAIN),
              "P6": ok(prec["pudl_later|all"], P6_MIN),
              "P7": ok(prec["pudl_later|early"], P7_MIN),
              "P8": ok(prec["unique_norm|early"], P8_MIN)}
    tables = {
        "phzero-zero-rows.csv": (
            ["report_year", "report_id", "id_kind", "operator_name_phmsa", "office_state",
             "exact_ids", "exact_when", "norm_ids", "norm_state_ids", "proposed_id",
             "proposed_by"], zrows),
        "phzero-multi-id-names.csv": (
            ["operator_name_title", "ids", "id_list", "rows", "first_year", "last_year"], multi),
        "phzero-loo-misses.csv": (
            ["rule", "report_year", "report_id", "operator_name_phmsa", "office_state",
             "true_id", "rule_ids"], misses)}
    return m, scores, tables


def gates(info, st, min_rows=G2_MIN_ROWS, min_zeros=G3_MIN_ZEROS):
    real = [y for y in st.years if y]
    g1 = bool(info.get("bytes")) and not info.get("missing_cols")
    g2 = (len(st.rows) >= min_rows and bool(real) and min(real) <= G2_MAX_FIRST_YEAR
          and G2_LAST_YEAR in st.years)
    g3 = st.zeros() >= min_zeros
    return ({"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)},
            {"rows": len(st.rows), "years": [min(real), max(real)] if real else [],
             "kinds": dict(sorted(st.kinds.items())), "rows_without_year": st.years.get(0, 0)})


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
            "missing_cols": [c for c in NEED if c not in df.columns],
            "missing_optional": [c for c in OPTIONAL if c not in df.columns], "saved_to": path}
    del raw
    if info["missing_cols"]:
        return info, iter(())
    for c in OPTIONAL:
        if c not in df.columns:
            df = df.with_columns(pl.lit(None, dtype=pl.String).alias(c))
    cols = list(NEED + OPTIONAL)
    df = df.select(cols).with_columns([pl.col(c).cast(pl.String) for c in cols])
    return info, df.iter_rows()


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phzero-20261110")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phzero.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now()}
    info, rows = load(pl, a.data_dir)
    res["table"] = info
    st = Study()
    for row in rows:
        st.add(row)
    g, gm = gates(info, st)
    res["gates"], res["gate_measures"] = g, gm
    res["rows_by_year"] = {str(k): v for k, v in sorted(st.years.items())}
    print("gates", g, gm)
    if all(g.values()):
        m, scores, tables = score(st)
        res["measures"], res["scores"] = m, dict(g, **scores)
        for name, (header, body) in tables.items():
            write_csv(os.path.join(a.out_dir, name), header, body)
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phzero.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
