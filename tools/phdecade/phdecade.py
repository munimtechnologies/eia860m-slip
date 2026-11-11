"""phdecade.py - in PUDL's core_phmsagas__yearly_distribution_by_install_decade, does only the
current install decade change from one report year to the next?

pudl#5505 proposes deriving yearly pipeline installations by comparing each operator's
install-decade report with the one from the year before. It expects only the current decade
bucket (2020s) to change from year to year, "but we should verify this before dropping the data".
This tool measures it for 2015-2025: for each (operator_id_phmsa, commodity, operating_state)
with exactly one report in two consecutive years, it compares every decade bucket's mains miles
and services. Pre-registration phdecade-1 (docs/phdecade-plan.md in
munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library, plus polars inside main() to read the
nightly parquet; the matching and scoring are pure Python and need no polars.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
import urllib.request
from collections import Counter

VERSION = "0.1.0"
TABLE = "core_phmsagas__yearly_distribution_by_install_decade"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet" % TABLE
UA = {"User-Agent": "mv2-phdecade/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
NEED = ("report_id", "report_date", "operator_id_phmsa", "commodity", "operating_state",
        "install_decade", "mains_miles", "services")
NULL = "<null>"
# The four oldest buckets on the form
OLD4 = ("pre_1940", "1940s", "1950s", "1960s")
# Pairs (t, t+1) with FIRST_T <= t and t+1 <= LAST_T1 (commodity is reported from 2015 on)
FIRST_T = 2015
LAST_T1 = 2025
# A bucket "changed" if |mains change| > MAINS_TOL miles (PUDL's own sum-check tolerance for
# mains) or |services change| > SERVICES_TOL
MAINS_TOL = 0.001
SERVICES_TOL = 0.0
# A "material" mains change: |change| > max(MATERIAL_MILES, MATERIAL_SHARE x the year-t value)
MATERIAL_MILES = 1.0
MATERIAL_SHARE = 0.01
TOP_CAP = 300

# Gates and bars (docs/phdecade-plan.md)
G2_MIN_PAIRS = 2000
G2_MIN_PER_YEAR = 100
G2_MIN_YEARS = 8
P1_MIN = 0.40
P2_MIN = 0.80
P4_MIN = 0.25
P5_MIN_YEARS = 8
P6_MIN = 0.40


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def share(a, b):
    return round(a / b, 6) if b else None


def key(value):
    """Key text: NULL for None or NaN, else str(value)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return NULL
    return str(value)


def fnum(value):
    """float, 0.0 for None or NaN."""
    if value is None:
        return 0.0
    v = float(value)
    return 0.0 if math.isnan(v) else v


def r3(x):
    return round(x, 3)


def decade_of(year):
    """The install-decade bucket a year's new pipe goes into: pre_1940, 1940s, ..., 2020s."""
    year = int(year)
    if year < 1940:
        return "pre_1940"
    return "%ds" % (year // 10 * 10)


def build(rows, first=FIRST_T, last=LAST_T1):
    """rows: dicts with year, report_id, operator_id_phmsa, commodity, operating_state,
    install_decade, mains_miles, services. Returns {(operator, commodity, state): {year:
    {report_id: {decade: (mains, services)}}}} for first <= year <= last. Null values count as
    0 (a bucket left blank one year and filled the next counts as a change)."""
    idx = {}
    for r in rows:
        y = r.get("year")
        if y is None or (isinstance(y, float) and math.isnan(y)):
            continue
        y = int(y)
        if y < first or y > last:
            continue
        k = (key(r["operator_id_phmsa"]), key(r["commodity"]), key(r["operating_state"]))
        rep = idx.setdefault(k, {}).setdefault(y, {}).setdefault(key(r["report_id"]), {})
        d = key(r["install_decade"])
        m, s = rep.get(d, (0.0, 0.0))
        rep[d] = (m + fnum(r["mains_miles"]), s + fnum(r["services"]))
    return idx


def match(idx, first_t=FIRST_T, last_t1=LAST_T1):
    """Pairs (key, t, t+1) where the key has exactly one report in each year. Key-years with
    more than one report are left out and counted by year."""
    pairs = []
    ambiguous = Counter()
    for k in sorted(idx):
        years = idx[k]
        for y in sorted(years):
            if len(years[y]) > 1:
                ambiguous[str(y)] += 1
        for t in range(first_t, last_t1):
            a, b = years.get(t), years.get(t + 1)
            if not a or not b or len(a) != 1 or len(b) != 1:
                continue
            pairs.append({"key": k, "t": t, "v0": next(iter(a.values())),
                          "v1": next(iter(b.values()))})
    pairs.sort(key=lambda p: (p["t"], p["key"]))
    return pairs, dict(sorted(ambiguous.items()))


def compare(p):
    """One matched pair: per-bucket changes, split into the current decade (the decade of year
    t+1) and every other bucket ("old" buckets, including unknown_decade)."""
    cur = decade_of(p["t"] + 1)
    v0, v1 = p["v0"], p["v1"]
    res = {"t": p["t"], "key": p["key"], "cur": cur, "buckets": [], "m0_total": 0.0,
           "m1_total": 0.0, "cur_dm": 0.0, "old_net_dm": 0.0, "old_gross_dm": 0.0,
           "old_m": 0, "old_m_material": 0, "old_s": 0, "any_change": False}
    for d in sorted(set(v0) | set(v1)):
        m0, s0 = v0.get(d, (0.0, 0.0))
        m1, s1 = v1.get(d, (0.0, 0.0))
        dm, ds = m1 - m0, s1 - s0
        res["m0_total"] += m0
        res["m1_total"] += m1
        cm = abs(dm) > MAINS_TOL
        cs = abs(ds) > SERVICES_TOL
        if cm or cs:
            res["any_change"] = True
        if d == cur:
            res["cur_dm"] += dm
        else:
            res["old_net_dm"] += dm
            res["old_gross_dm"] += abs(dm)
            res["old_m"] += int(cm)
            res["old_m_material"] += int(abs(dm) > max(MATERIAL_MILES, MATERIAL_SHARE * abs(m0)))
            res["old_s"] += int(cs)
        res["buckets"].append((d, d == cur, m0, m1, s0, s1, dm, ds, cm, cs))
    return res


class Study:
    """Scores matched pairs (from match())."""

    def __init__(self, pairs):
        self.c = [compare(p) for p in pairs]

    def by_t_decade(self):
        """(t, decade) -> [is_current, pairs_with_bucket, active, changed_m, changed_s, net_dm,
        gross_dm, net_ds]; active = mains > 0 in either year."""
        acc = {}
        for r in self.c:
            for (d, is_cur, m0, m1, s0, s1, dm, ds, cm, cs) in r["buckets"]:
                a = acc.setdefault((r["t"], d), [is_cur, 0, 0, 0, 0, 0.0, 0.0, 0.0])
                a[1] += 1
                a[2] += int(m0 > 0 or m1 > 0)
                a[3] += int(cm)
                a[4] += int(cs)
                a[5] += dm
                a[6] += abs(dm)
                a[7] += ds
        return acc

    def score(self):
        c = self.c
        n = len(c)
        old_m = sum(1 for r in c if r["old_m"])
        old_mm = sum(1 for r in c if r["old_m_material"])
        old_s = sum(1 for r in c if r["old_s"])
        static = sum(1 for r in c if not r["any_change"])
        miles_all = sum(r["m0_total"] for r in c)
        miles_old = sum(r["m0_total"] for r in c if r["old_m"])
        net_old = sum(r["old_net_dm"] for r in c)
        gross_old = sum(r["old_gross_dm"] for r in c)
        net_cur = sum(r["cur_dm"] for r in c)
        gross_cur = sum(abs(r["cur_dm"]) for r in c)
        cur_neg = sum(1 for r in c if r["cur_dm"] < -MAINS_TOL)
        net_total = sum(r["m1_total"] - r["m0_total"] for r in c)
        dec = {}
        old4_by_t = {}
        for (t, d), a in sorted(self.by_t_decade().items()):
            if a[0]:
                continue
            x = dec.setdefault(d, [0, 0, 0, 0, 0.0, 0.0, 0.0])
            for i in range(1, 8):
                x[i - 1] += a[i]
            if d in OLD4:
                old4_by_t[str(t)] = old4_by_t.get(str(t), 0.0) + a[5]
        years_old4_neg = sum(1 for v in old4_by_t.values() if v < -MAINS_TOL)
        s_old, s_w, s_s = share(old_m, n), share(miles_old, miles_all), share(old_s, n)
        ratio = share(gross_old, gross_cur)
        m = {"pairs": n, "pairs_old_mains_changed": old_m, "share_old_mains_changed": s_old,
             "pairs_old_mains_material": old_mm, "share_old_mains_material": share(old_mm, n),
             "pairs_old_services_changed": old_s, "share_old_services_changed": s_s,
             "pairs_static": static, "share_static": share(static, n),
             "miles_t_all": r3(miles_all), "miles_t_old_changed": r3(miles_old),
             "share_miles_old_changed": s_w,
             "net_old_dm": r3(net_old), "gross_old_dm": r3(gross_old),
             "net_cur_dm": r3(net_cur), "gross_cur_dm": r3(gross_cur),
             "ratio_gross_old_to_cur": ratio, "pairs_cur_negative": cur_neg,
             "net_total_dm": r3(net_total),
             "old_by_decade": {d: [x[0], x[1], x[2], x[3], r3(x[4]), r3(x[5]), r3(x[6])]
                               for d, x in sorted(dec.items())},
             "old4_net_dm_by_t": {k: r3(v) for k, v in sorted(old4_by_t.items())},
             "years_old4_net_negative": years_old4_neg}
        scores = {"P1": s_old is not None and s_old >= P1_MIN,
                  "P2": s_w is not None and s_w >= P2_MIN,
                  "P3": gross_old > 0 and net_old < -MAINS_TOL,
                  "P4": ratio is not None and ratio >= P4_MIN,
                  "P5": years_old4_neg >= P5_MIN_YEARS,
                  "P6": s_s is not None and s_s >= P6_MIN}
        return m, scores

    def top_old(self, cap=TOP_CAP):
        """The cap largest |mains change| old buckets."""
        out = []
        for r in self.c:
            for (d, is_cur, m0, m1, s0, s1, dm, ds, cm, cs) in r["buckets"]:
                if not is_cur and cm:
                    out.append((abs(dm), r["t"], r["key"], d, m0, m1, s0, s1, dm))
        out.sort(key=lambda x: (-x[0], x[1], x[2], x[3]))
        return out[:cap]


def gates(info, st):
    by_t = Counter(r["t"] for r in st.c)
    years_ok = sum(1 for v in by_t.values() if v >= G2_MIN_PER_YEAR)
    g1 = bool(info.get("bytes")) and not info.get("missing_cols")
    g2 = len(st.c) >= G2_MIN_PAIRS and years_ok >= G2_MIN_YEARS
    return ({"G1": bool(g1), "G2": bool(g2)},
            {"pairs": len(st.c), "pairs_by_t": {str(k): v for k, v in sorted(by_t.items())},
             "years_with_enough_pairs": years_ok})


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


def to_rows(pl, df):
    """polars: plain rows for FIRST_T..LAST_T1, plus the file's first and last year."""
    rd = str(df.schema["report_date"])
    if rd.startswith("Date"):
        yexpr = pl.col("report_date").dt.year()
    else:
        yexpr = pl.col("report_date").cast(pl.String).str.slice(0, 4).cast(pl.Int32, strict=False)
    out = df.select(yexpr.cast(pl.Int32).alias("year"),
                    pl.col("report_id").cast(pl.String),
                    pl.col("operator_id_phmsa").cast(pl.String),
                    pl.col("commodity").cast(pl.String),
                    pl.col("operating_state").cast(pl.String),
                    pl.col("install_decade").cast(pl.String),
                    pl.col("mains_miles").cast(pl.Float64),
                    pl.col("services").cast(pl.Float64))
    lo, hi = out.select(pl.col("year").min().alias("lo"), pl.col("year").max().alias("hi")).row(0)
    sub = out.filter((pl.col("year") >= FIRST_T) & (pl.col("year") <= LAST_T1))
    return list(sub.iter_rows(named=True)), [lo, hi]


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phdecade-20261111")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phdecade.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now()}
    raw, headers = download(URL)
    path = os.path.join(a.data_dir, TABLE + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    info = {"url": URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "last_modified": headers.get("Last-Modified"), "saved_to": path}
    del raw
    schema = pl.scan_parquet(path).collect_schema()
    info["dtypes"] = {c: str(t) for c, t in schema.items()}
    info["missing_cols"] = [c for c in NEED if c not in schema]
    df = pl.scan_parquet(path).select([c for c in NEED if c in schema]).collect()
    info["rows"] = df.height
    rows, years = ([], []) if info["missing_cols"] else to_rows(pl, df)
    info["years"] = years
    info["rows_in_window"] = len(rows)
    res["table"] = info
    idx = build(rows)
    pairs, ambiguous = match(idx)
    res["keys"] = len(idx)
    res["key_years"] = sum(len(v) for v in idx.values())
    res["ambiguous_key_years_by_year"] = ambiguous
    st = Study(pairs)
    g, gm = gates(info, st)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    if all(g.values()):
        m, scores = st.score()
        res["measures"], res["scores"] = m, dict(g, **scores)
        write_csv(os.path.join(a.out_dir, "phdecade-by-year-decade.csv"),
                  ["t", "decade", "is_current", "pairs_with_bucket", "active", "changed_mains",
                   "changed_services", "net_mains_change", "gross_mains_change",
                   "net_services_change"],
                  [[t, d, int(x[0]), x[1], x[2], x[3], x[4], r3(x[5]), r3(x[6]), r3(x[7])]
                   for (t, d), x in sorted(st.by_t_decade().items())])
        write_csv(os.path.join(a.out_dir, "phdecade-pairs.csv"),
                  ["t", "operator_id_phmsa", "commodity", "operating_state", "mains_t",
                   "mains_t1", "current_decade_change", "old_net_change", "old_gross_change",
                   "old_buckets_mains_changed", "old_buckets_material", "old_buckets_services_changed"],
                  [[r["t"], r["key"][0], r["key"][1], r["key"][2], r3(r["m0_total"]),
                    r3(r["m1_total"]), r3(r["cur_dm"]), r3(r["old_net_dm"]),
                    r3(r["old_gross_dm"]), r["old_m"], r["old_m_material"], r["old_s"]]
                   for r in st.c])
        write_csv(os.path.join(a.out_dir, "phdecade-top-old-changes.csv"),
                  ["t", "operator_id_phmsa", "commodity", "operating_state", "decade",
                   "mains_t", "mains_t1", "services_t", "services_t1", "mains_change"],
                  [[x[1], x[2][0], x[2][1], x[2][2], x[3], r3(x[4]), r3(x[5]), r3(x[6]),
                    r3(x[7]), r3(x[8])] for x in st.top_old()])
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phdecade.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
