# rusops.py - does PUDL split RUS Form 7 "other capital credits" across two opex_type labels?
# pre-registration id rusops-1 (plan: docs/rusops-plan.md in munimtechnologies/eia860m-slip).
# By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
# Apache-2.0. PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.
#
# PUDL builds core_rus7__yearly_statement_of_operations by matching every column name of
# src/pudl/package_data/rus7/column_maps/statement_of_operations.csv against
#   ^(<group>)_(.+)_(opex_ytd|opex_ytd_budget|opex_report_month)$
# (src/pudl/transform/rus7.py), so the middle part becomes opex_type. If one of the three
# columns of an item is spelled differently, that item's values land under two opex_type
# labels. This script (1) applies the same regex to the column map, byte for byte, at a
# recorded commit, (2) profiles the two labels in PUDL's nightly core and out tables and
# (3) measures what the split does to a Form 7 line-29 totals check. It only measures.
import argparse
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict

VERSION = "0.1.0"
UA = {"User-Agent": "MV2-Munim-Inc rusops/0.1.0 (mv2@munimtech.com)"}
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
TABLES = ("core_rus7__yearly_statement_of_operations", "out_rus7__yearly_statement_of_operations")
COMMIT_URL = "https://api.github.com/repos/catalyst-cooperative/pudl/commits/main"
COLMAP_PATH = "src/pudl/package_data/rus7/column_maps/statement_of_operations.csv"
RAW = "https://raw.githubusercontent.com/catalyst-cooperative/pudl/%s/" + COLMAP_PATH
GROUPS = ["cost_of_electric_service", "opex", "patronage_and_operating_margins",
          "patronage_capital_or_margins"]
PERIODS = ["opex_ytd", "opex_ytd_budget", "opex_report_month"]
PATTERN = re.compile(rf"^({'|'.join(GROUPS)})_(.+)_({'|'.join(PERIODS)})$")
KEY = ("borrower_id_rus", "report_date")
OCC = "other_capital_credits"
OCC_YTD = "other_capital_credits_ytd"
TOL = 10
P3_SHARE = 0.01
P5_SHARE = 0.05


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(url, timeout=300):
    last = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # retried, then raised
            last = exc
            time.sleep(20)
    raise last


def wait_for(url, token, minutes):
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url, 60)[0].decode("utf-8", "replace"):
                return True, polls, now()
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, now()
        time.sleep(60)


def isnull(v):
    if v is None:
        return True
    try:
        return bool(v != v)  # NaN
    except TypeError:
        return True


def colmap_periods(header_fields):
    """Apply PUDL's regex to every column name. Returns ({(group, type): sorted periods},
    [names that do not match])."""
    found = defaultdict(set)
    unmatched = []
    for name in header_fields:
        m = PATTERN.match(name)
        if m is None:
            unmatched.append(name)
            continue
        found[(m.group(1), m.group(2))].add(m.group(3))
    return {k: sorted(v) for k, v in found.items()}, unmatched


def orphans(periods_by_item):
    """Items that do not have all three periods."""
    return {"%s|%s" % k: v for k, v in sorted(periods_by_item.items()) if len(v) < 3}


def profile(rows, label):
    """Row count, non-null and non-zero counts per value column for one opex_type."""
    out = {"rows": 0, "keys": 0}
    keys = set()
    for p in PERIODS:
        out[p] = {"nonnull": 0, "abs_gt_tol": 0}
    for r in rows:
        if r.get("opex_type") != label:
            continue
        out["rows"] += 1
        keys.add(tuple(r[k] for k in KEY))
        for p in PERIODS:
            v = r.get(p)
            if not isnull(v):
                out[p]["nonnull"] += 1
                if abs(float(v)) > TOL:
                    out[p]["abs_gt_tol"] += 1
    out["keys"] = len(keys)
    return out


def sums_by_key(rows, value_col):
    """{(borrower, date): {(group, type): SUM(value) or None}} like the dbt macro's step 1."""
    out = defaultdict(dict)
    for r in rows:
        g, t = r.get("opex_group"), r.get("opex_type")
        if g is None or t is None:
            continue
        key = tuple(r[k] for k in KEY)
        v = r.get(value_col)
        lab = (g, t)
        if isnull(v):
            out[key].setdefault(lab, None)
        else:
            cur = out[key].get(lab)
            out[key][lab] = float(v) if cur is None else cur + float(v)
    return out


def line29_items(merged):
    """Form 7 Part A line 29 = line 21 + lines 22-28."""
    items = [("patronage_and_operating_margins", "total_minus")]
    for t in ("non_operating_margins_interest", "construction_funds_allowance",
              "equity_investment_losses", "non_operating_margins_other",
              "generation_and_transmission_capital", OCC, "extraordinary_items"):
        items.append(("patronage_capital_or_margins", t))
    if merged:
        items.append(("patronage_capital_or_margins", OCC_YTD))
    return items


LINE29_TOTAL = ("patronage_capital_or_margins", "total")


def check(sums, items, total, tol=TOL):
    """Macro steps 2-3: failure if both sides non-null and |sum - total| > tol."""
    n = no_total = no_subs = 0
    fails = []
    for key, labs in sums.items():
        s = None
        for lab in items:
            v = labs.get(lab)
            if v is not None:
                s = (s or 0.0) + v
        g = labs.get(total)
        if g is None:
            no_total += 1
            continue
        if s is None:
            no_subs += 1
            continue
        n += 1
        if abs(s - g) > tol:
            fails.append({"key": [str(k) for k in key], "subcomponents_sum": s, "total": g,
                          "absolute_diff": abs(s - g)})
    fails.sort(key=lambda f: -f["absolute_diff"])
    return {"groups_checked": n, "groups_without_total": no_total,
            "groups_without_subcomponents": no_subs, "failures": len(fails),
            "failure_share": round(len(fails) / n, 5) if n else None,
            "largest_failures": fails[:10]}


def gate(res):
    ok = res.get("colmap") is not None and "error" not in res.get("colmap", {})
    for t in TABLES:
        tr = res.get("tables", {}).get(t, {})
        if "error" in tr or sorted(tr.get("opex_groups", [])) != sorted(GROUPS):
            ok = False
    return ok


def score(res):
    core = res["tables"][TABLES[0]]
    out = res["tables"][TABLES[1]]

    def split_ok(tr):
        a, b = tr["profile"][OCC_YTD], tr["profile"][OCC]
        return (a["rows"] >= 1 and a["opex_ytd"]["nonnull"] == 0
                and a["opex_ytd_budget"]["nonnull"] == 0
                and b["opex_report_month"]["nonnull"] == 0)

    keys = core["borrower_years"]
    l29m = core["line29"]["opex_report_month"]
    l29y = core["line29"]["opex_ytd"]
    return {
        "P1": split_ok(core),
        "P2": split_ok(out),
        "P3": core["profile"][OCC_YTD]["opex_report_month"]["abs_gt_tol"] >= P3_SHARE * keys,
        "P4": l29m["as_labelled"]["failures"] > l29m["merged"]["failures"],
        "P5": (l29y["merged"]["groups_checked"] > 0 and
               l29y["merged"]["failures"] < P5_SHARE * l29y["merged"]["groups_checked"]),
    }


def run_table(table, data_dir):
    import polars as pl
    path = os.path.join(data_dir, table + ".parquet")
    raw, headers = fetch(NIGHTLY + table + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    df = pl.read_parquet(path)
    cols = [c for c in list(KEY) + ["opex_group", "opex_type"] + PERIODS if c in df.columns]
    df = df.select(cols).with_columns(pl.col("opex_group").cast(pl.Utf8),
                                      pl.col("opex_type").cast(pl.Utf8))
    rows = df.to_dicts()
    res = {"rows": len(rows), "bytes": len(raw), "last_modified": headers.get("Last-Modified"),
           "etag": headers.get("ETag"),
           "opex_groups": sorted({r["opex_group"] for r in rows if r["opex_group"]}),
           "opex_types": sorted({r["opex_type"] for r in rows if r["opex_type"]}),
           "borrower_years": len({tuple(r[k] for k in KEY) for r in rows})}
    res["profile"] = {OCC: profile(rows, OCC), OCC_YTD: profile(rows, OCC_YTD)}
    by_year = defaultdict(int)
    for r in rows:
        if r["opex_type"] == OCC_YTD and not isnull(r["opex_report_month"]) \
                and abs(float(r["opex_report_month"])) > TOL:
            by_year[str(r["report_date"])[:4]] += 1
    res["occ_ytd_monthly_abs_gt_tol_by_year"] = dict(sorted(by_year.items()))
    res["line29"] = {}
    for p in PERIODS:
        sums = sums_by_key(rows, p)
        res["line29"][p] = {
            "as_labelled": check(sums, line29_items(False), LINE29_TOTAL),
            "merged": check(sums, line29_items(True), LINE29_TOTAL),
        }
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--data-dir", default="/data/rusops-1")
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=0)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    res = {"version": VERSION, "started": now(), "tolerance": TOL}
    if a.wait_for:
        live, polls, at = wait_for(a.wait_for, a.token, a.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live"
            with open(os.path.join(a.out_dir, "rusops.json"), "w") as fh:
                json.dump(res, fh, indent=1)
            print("plan page not live; nothing read")
            return 1
    try:
        sha = json.loads(fetch(COMMIT_URL, 60)[0])["sha"]
        text = fetch(RAW % sha, 60)[0].decode("utf-8-sig")
        header = text.splitlines()[0].split(",")
        per, unmatched = colmap_periods(header)
        res["colmap"] = {"commit": sha, "fields": len(header), "items": len(per),
                         "unmatched": unmatched, "orphans": orphans(per),
                         "fields_with_ytd_before_period": [h for h in header
                                                           if h.endswith("_ytd_opex_report_month")]}
    except Exception as exc:
        res["colmap"] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
    res["tables"] = {}
    for t in TABLES:
        try:
            res["tables"][t] = run_table(t, a.data_dir)
        except Exception as exc:
            res["tables"][t] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
    res["gate_G1"] = gate(res)
    if res["gate_G1"]:
        res["scores"] = score(res)
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "rusops.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({"gate_G1": res["gate_G1"], "scores": res.get("scores"),
                      "orphans": res["colmap"].get("orphans")}, default=str))
    for t, tr in res["tables"].items():
        if "error" in tr:
            print(t, tr["error"])
            continue
        print(t, tr["rows"], "borrower-years", tr["borrower_years"])
        print("  profile", json.dumps(tr["profile"]))
        for p, v in tr["line29"].items():
            print("  line29", p, {k: (x["groups_checked"], x["failures"]) for k, x in v.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
