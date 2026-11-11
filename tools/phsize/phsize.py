"""phsize.py - are the services sizes in PUDL's PHMSA gas distribution table
_core_phmsagas__yearly_distribution_by_material_and_size labelled as the form reports them?

PUDL's _core_phmsagas__yearly_distribution_by_material_and_size (src/pudl/transform/phmsagas.py)
melts the wide services columns with the filter ^services_(<materials>)_(.*)$ and then takes
main_size from each column name with an unanchored str.extract over MAIN_PIPE_SIZES_PHMSAGAS, the
MAINS size list. The services columns in PUDL's column map end in sizes that list does not have
(over_6_in, over_8_in), so reading the code: a services count for "over 6 in" would get a null
main_size, and one for "over 8 in" would be labelled 8_in (the leftmost match). This tool counts
what the published table holds. Pre-registration phsize-1 (docs/phsize-plan.md in
munimtechnologies/eia860m-slip).

Only measures; changes nothing in PUDL. Standard library, plus polars inside main() to read and
group the nightly parquet; the scoring works on the grouped rows and needs no polars.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
import urllib.request
from collections import Counter, defaultdict

VERSION = "0.1.0"
TABLE = "_core_phmsagas__yearly_distribution_by_material_and_size"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet" % TABLE
UA = {"User-Agent": "mv2-phsize/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
NEED = ("report_date", "report_id", "operator_id_phmsa", "material", "main_size", "mains_miles",
        "services")
NULL = "<null>"
# Sizes a services row can get from the services column names in PUDL's column map
# (unknown, 0.5_in_or_less, 0.5_to_1_in, 1_in_or_less, 1_to_2_in, 2_to_4_in, 4_to_6_in,
# 4_to_8_in, total; over_8_in -> 8_in; over_6_in and a bare material -> null).
SERVICE_SIZES = frozenset(("0.5_in_or_less", "0.5_to_1_in", "1_in_or_less", "1_to_2_in",
                           "2_to_4_in", "4_to_6_in", "4_to_8_in", "8_in", "total", "unknown",
                           NULL))
# Materials with a services_<material>_over_6_in column
OVER6 = ("steel", "copper", "cast_iron", "plastic", "other", "all_materials")
# Null-size services rows the code can make: over_6_in columns, services_other_alt (a by-material
# column the services filter also matches) and numeric text in services_other_material_detail
NULL_OK = OVER6 + ("other_alt", "other_material")
# Materials with a services_<material>_over_8_in column but no main_<material>_8_in_miles column
NO_MAIN8 = ("cast_or_wrought_iron", "pvc", "pe", "abs", "other_plastic", "other_alt",
            "reconditioned_cast_iron")
SAMPLE_CAP = 3000

# Gates and bars (docs/phsize-plan.md)
G2_MIN_ROWS = 100000
G2_MIN_SERVICES = 1000
P1_MIN = 100
P2_MIN = 0.99
P3_MIN = 100
P4_MAX_OTHER = 0
P5_MAX_SHARE = 0.01


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def share(a, b):
    return round(a / b, 6) if b else None


def key(value):
    """Group key text: NULL for None or NaN, else str(value)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return NULL
    return str(value)


def fnum(value):
    """float, 0.0 for None or NaN."""
    if value is None:
        return 0.0
    v = float(value)
    return 0.0 if math.isnan(v) else v


class Study:
    """Scores grouped rows: dicts with year, material, main_size, rows, mains_rows,
    services_rows, both_rows, mains_sum, services_sum (one per year x material x main_size)."""

    def __init__(self, groups):
        self.g = []
        for r in groups:
            self.g.append({"year": int(r["year"]) if r["year"] is not None else 0,
                           "material": key(r["material"]), "main_size": key(r["main_size"]),
                           "rows": int(r["rows"]), "mains_rows": int(r["mains_rows"]),
                           "services_rows": int(r["services_rows"]),
                           "both_rows": int(r["both_rows"]),
                           "mains_sum": fnum(r["mains_sum"]),
                           "services_sum": fnum(r["services_sum"])})

    def totals(self):
        t = Counter()
        for r in self.g:
            for k in ("rows", "mains_rows", "services_rows", "both_rows"):
                t[k] += r[k]
        years = [r["year"] for r in self.g if r["year"]]
        return dict(t), ([min(years), max(years)] if years else [])

    def services_by_size(self):
        out = Counter()
        for r in self.g:
            if r["services_rows"]:
                out[r["main_size"]] += r["services_rows"]
        return dict(sorted(out.items()))

    def mains_by_size(self):
        out = Counter()
        for r in self.g:
            if r["mains_rows"]:
                out[r["main_size"]] += r["mains_rows"]
        return dict(sorted(out.items()))

    def by_material(self, pick):
        """material -> [services rows, first year, last year, services sum, both rows] for the
        groups pick(r) selects (services rows only)."""
        acc = {}
        for r in self.g:
            if not r["services_rows"] or not pick(r):
                continue
            a = acc.setdefault(r["material"], [0, None, None, 0.0, 0])
            a[0] += r["services_rows"]
            a[1] = r["year"] if a[1] is None else min(a[1], r["year"])
            a[2] = r["year"] if a[2] is None else max(a[2], r["year"])
            a[3] += r["services_sum"]
            a[4] += r["both_rows"]
        return {k: [v[0], v[1], v[2], round(v[3], 3), v[4]] for k, v in sorted(acc.items())}

    def by_year(self, pick):
        out = Counter()
        for r in self.g:
            if r["services_rows"] and pick(r):
                out[str(r["year"])] += r["services_rows"]
        return dict(sorted(out.items()))

    def score(self):
        def null_size(r):
            return r["main_size"] == NULL

        def eight_no_main(r):
            return r["main_size"] == "8_in" and r["material"] in NO_MAIN8

        def eight(r):
            return r["main_size"] == "8_in"

        nul = self.by_material(null_size)
        n_null = sum(v[0] for v in nul.values())
        n_null_ok = sum(v[0] for k, v in nul.items() if k in NULL_OK)
        e_no = self.by_material(eight_no_main)
        n_e_no = sum(v[0] for v in e_no.values())
        sizes = self.services_by_size()
        other_sizes = {k: v for k, v in sizes.items() if k not in SERVICE_SIZES}
        base = sum(r["services_sum"] for r in self.g if r["main_size"] != "total")
        null_sum = sum(r["services_sum"] for r in self.g if null_size(r))
        e_no_sum = sum(r["services_sum"] for r in self.g if eight_no_main(r))
        m = {"services_by_size": sizes, "mains_by_size": self.mains_by_size(),
             "null_size_by_material": nul, "null_size_rows": n_null,
             "null_size_rows_expected_material": n_null_ok,
             "null_size_by_year": self.by_year(null_size),
             "eight_in_by_material": self.by_material(eight),
             "eight_in_no_main8_rows": n_e_no, "eight_in_no_main8_by_year": self.by_year(eight_no_main),
             "services_other_sizes": other_sizes,
             "services_sum_non_total": round(base, 3), "services_sum_null_size": round(null_sum, 3),
             "services_sum_eight_no_main8": round(e_no_sum, 3),
             "shares": {"null_ok": share(n_null_ok, n_null),
                        "null_sum": share(null_sum, base),
                        "null_plus_eight_sum": share(null_sum + e_no_sum, base)}}
        flagged = m["shares"]["null_plus_eight_sum"]
        scores = {"P1": n_null >= P1_MIN,
                  "P2": n_null > 0 and m["shares"]["null_ok"] >= P2_MIN,
                  "P3": n_e_no >= P3_MIN,
                  "P4": sum(other_sizes.values()) <= P4_MAX_OTHER,
                  "P5": flagged is not None and flagged < P5_MAX_SHARE}
        return m, scores


def gates(info, st):
    t, years = st.totals()
    g1 = bool(info.get("bytes")) and not info.get("missing_cols")
    g2 = t.get("rows", 0) >= G2_MIN_ROWS and t.get("services_rows", 0) >= G2_MIN_SERVICES
    return {"G1": bool(g1), "G2": bool(g2)}, dict(t, years=years)


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


def group(pl, df):
    """polars: one row per (year, material, main_size) with counts and sums."""
    rd = str(df.schema["report_date"])
    if rd.startswith("Date"):
        yexpr = pl.col("report_date").dt.year()
    else:
        yexpr = pl.col("report_date").cast(pl.String).str.slice(0, 4).cast(pl.Int32, strict=False)
    m = pl.col("mains_miles").cast(pl.Float64).fill_nan(None)
    s = pl.col("services").cast(pl.Float64).fill_nan(None)
    lf = df.lazy().select(
        yexpr.alias("year"), pl.col("material").cast(pl.String).alias("material"),
        pl.col("main_size").cast(pl.String).alias("main_size"), m.alias("m"), s.alias("s"),
        pl.col("report_id"), pl.col("operator_id_phmsa"))
    g = (lf.group_by(["year", "material", "main_size"])
         .agg(pl.len().alias("rows"), pl.col("m").is_not_null().sum().alias("mains_rows"),
              pl.col("s").is_not_null().sum().alias("services_rows"),
              (pl.col("m").is_not_null() & pl.col("s").is_not_null()).sum().alias("both_rows"),
              pl.col("m").sum().alias("mains_sum"), pl.col("s").sum().alias("services_sum"))
         .sort(["year", "material", "main_size"], nulls_last=True)
         .collect())
    flag = (pl.col("s").is_not_null()
            & (pl.col("main_size").is_null()
               | ((pl.col("main_size") == "8_in") & pl.col("material").is_in(list(NO_MAIN8)))))
    fl = lf.filter(flag)
    reports = {
        "null_size": fl.filter(pl.col("main_size").is_null()).select(
            pl.col("report_id").n_unique()).collect().item(),
        "eight_no_main8": fl.filter(pl.col("main_size").is_not_null()).select(
            pl.col("report_id").n_unique()).collect().item()}
    sample = (fl.sort(["year", "report_id", "material", "main_size"], nulls_last=True)
              .head(SAMPLE_CAP).collect())
    return list(g.iter_rows(named=True)), reports, list(sample.iter_rows(named=True))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/phsize-20261111")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "phsize.py " + VERSION, "python": sys.version.split()[0],
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
    # Only the columns the study needs are read, to keep memory low.
    df = pl.scan_parquet(path).select([c for c in NEED if c in schema]).collect()
    info["rows"] = df.height
    res["table"] = info
    groups, reports, sample = ([], {}, []) if info["missing_cols"] else group(pl, df)
    st = Study(groups)
    g, gm = gates(info, st)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    if all(g.values()):
        m, scores = st.score()
        m["reports"] = reports
        res["measures"], res["scores"] = m, dict(g, **scores)
        write_csv(os.path.join(a.out_dir, "phsize-groups.csv"),
                  ["year", "material", "main_size", "rows", "mains_rows", "services_rows",
                   "both_rows", "mains_sum", "services_sum"],
                  [[r["year"], r["material"], r["main_size"], r["rows"], r["mains_rows"],
                    r["services_rows"], r["both_rows"], round(r["mains_sum"], 3),
                    round(r["services_sum"], 3)] for r in st.g])
        write_csv(os.path.join(a.out_dir, "phsize-flagged-sample.csv"),
                  ["report_year", "report_id", "operator_id_phmsa", "material", "main_size",
                   "mains_miles", "services"],
                  [[r["year"], r["report_id"], r["operator_id_phmsa"], r["material"],
                    key(r["main_size"]), "" if r["m"] is None else r["m"], r["s"]]
                   for r in sample])
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "phsize.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
