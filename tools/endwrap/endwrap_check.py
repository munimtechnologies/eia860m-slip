"""endwrap_check: a descriptive check (not pre-registered) of tools/endwrap on PUDL's newest
nightly EIA-860M changelog.

Mode 1 (default): downloads the nightly parquet into --pudl-dir, reads it with
eia860m_slip.prepare twice (the original reader, then with endwrap installed), and reports
which rule endwrap detects, how many records' last month in force changes, and how each
reading's snapshot of the last two report months compares with the generators EIA's own
workbooks for those months list (sheets with neither "cancel" nor "_pr", read with
tools/endrule/endrule.py 0.1.0).

Mode 2 (--compare OLD_DIR NEW_DIR): line-by-line comparison of the CSV files two watchlist
runs wrote.

PUDL's data (CC BY 4.0) and EIA's files are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import argparse
import collections
import hashlib
import json
import os
import sys
import time

VERSION = "0.1.0"
NAMES = {"2026-07": "july", "2026-08": "august", "2026-09": "september",
         "2026-10": "october", "2026-11": "november", "2026-12": "december"}
SHOW = 60


def norm_keys(es_keys):
    """eia860m_slip keys ('plant/gen' from astype(str)) -> endrule keys (leading zeros off)."""
    import endrule as er
    out = set()
    for k in es_keys:
        plant, _, gen = str(k).partition("/")
        nk = er.make_key(plant, gen)
        if nk is not None:
            out.add(nk)
    return out


def compare_sets(snap, pool):
    return {"snapshot": len(snap), "eia_listed": len(pool),
            "in_snapshot_not_listed": len(snap - pool),
            "listed_not_in_snapshot": len(pool - snap),
            "in_snapshot_not_listed_keys": sorted(snap - pool)[:SHOW]}


def compare_dirs(old_dir, new_dir):
    out = {}
    names = sorted(n for n in os.listdir(old_dir) if n.endswith(".csv"))
    for n in names:
        a = open(os.path.join(old_dir, n), encoding="utf-8").read().splitlines()
        p = os.path.join(new_dir, n)
        if not os.path.exists(p):
            out[n] = {"missing_in_new": True}
            continue
        b = open(p, encoding="utf-8").read().splitlines()
        ca, cb = collections.Counter(a), collections.Counter(b)
        only_a = sorted((ca - cb).elements())
        only_b = sorted((cb - ca).elements())
        out[n] = {"lines_old": len(a), "lines_new": len(b), "identical": a == b,
                  "only_old": len(only_a), "only_new": len(only_b),
                  "only_old_lines": only_a[:SHOW], "only_new_lines": only_b[:SHOW]}
    return out


def check(pudl_dir, out_dir):
    import pandas as pd
    import pyarrow.parquet as pq
    import endrule as er
    import eia860m_slip as es
    import endwrap as ew

    res = {"tool": "endwrap_check.py " + VERSION, "endwrap": ew.VERSION,
           "eia860m_slip": getattr(es, "__version__", None), "endrule": er.VERSION,
           "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "errors": {}}
    path = os.path.join(pudl_dir, "core_eia860m__changelog_generators.parquet")

    def save():
        with open(os.path.join(out_dir, "endwrap_check.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)

    os.makedirs(pudl_dir, exist_ok=True)
    raw, headers = er.fetch(er.NIGHTLY)
    with open(path, "wb") as fh:
        fh.write(raw)
    res["pudl"] = {"url": er.NIGHTLY, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                   "last_modified": headers.get("Last-Modified")}
    del raw
    names = set(pq.ParquetFile(path).schema_arrow.names)
    table = pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names])
    old = es.prepare(table)
    ew.install(es)
    new = es.prepare(table)
    res["detect"] = ew.STATE["calls"][-1] if ew.STATE["calls"] else None
    diff = old["until_m"] - new["until_m"]
    res["records"] = {"rows": int(len(old)), "until_changed": int((diff != 0).sum()),
                      "old_minus_new": {str(int(k)): int(v)
                                        for k, v in diff[diff != 0].value_counts().items()}}
    last_m = int(old["report_m"].max())
    res["latest_report"] = es.month_str(last_m)
    save()

    snaps = {}
    for r in (last_m - 1, last_m):
        month = es.month_str(r)
        snaps[month] = {"old": norm_keys(es.snapshot(old, r)["key"]),
                        "new": norm_keys(es.snapshot(new, r)["key"])}
    res["snapshots"] = {}
    for month, s in snaps.items():
        entry = {"old_only": sorted(s["old"] - s["new"])[:SHOW],
                 "old_only_n": len(s["old"] - s["new"]),
                 "new_only_n": len(s["new"] - s["old"])}
        name = NAMES.get(month)
        url = None
        if name is not None and month.startswith("2026"):
            url, wraw, wh, tried = er.fetch_workbook(name)
        if url is None:
            res["errors"]["eia:" + month] = "workbook not read"
        else:
            entry["eia"] = {"url": url, "md5": hashlib.md5(wraw).hexdigest(),
                            "last_modified": wh.get("Last-Modified")}
            pool = er.listed(er.read_workbook(wraw))
            del wraw
            entry["old_vs_eia"] = compare_sets(s["old"], pool)
            entry["new_vs_eia"] = compare_sets(s["new"], pool)
        res["snapshots"][month] = entry
        save()
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({k: v for k, v in res.items() if k != "snapshots"}, indent=1,
                     default=str))
    for month, e in res["snapshots"].items():
        print(month, json.dumps({k: e.get(k) for k in ("old_only_n", "new_only_n")}),
              json.dumps({k: {x: y for x, y in e.get(k, {}).items() if not x.endswith("keys")}
                          for k in ("old_vs_eia", "new_vs_eia")}))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--pudl-dir", default="pudl")
    ap.add_argument("--compare", nargs=2, metavar=("OLD_DIR", "NEW_DIR"))
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.compare:
        out = compare_dirs(*a.compare)
        with open(os.path.join(a.out_dir, "watchlist_compare.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(json.dumps({n: {k: v for k, v in d.items() if not k.endswith("_lines")}
                          for n, d in out.items()}, indent=1))
        return
    check(a.pudl_dir, a.out_dir)


if __name__ == "__main__":
    main()
