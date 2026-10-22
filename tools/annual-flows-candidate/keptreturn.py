"""keptreturn: which columns let a returning value back into PUDL's EIA-860M changelog?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Descriptive census for docs/heldtrace.md; no prediction is tested. PUDL's make_changelog drops a
record equal to an earlier record of the same generator in every column but report_date. Call a
generator's status, planned operating date and nameplate MW its projection. A record whose
projection differs from the previous record's but equals an earlier record's is a return; PUDL can
only have kept it because some other column differs. For every such kept return this counts which
columns differ from the latest earlier record with the same projection: by column, by column set,
by report year and by report month, and lists the returns of given generators.

    python keptreturn.py --data-dir /data --out-dir /out [--key 3075/11 ...]
"""

import argparse
import collections
import glob
import json
import os
import time

import pandas as pd

__version__ = "0.1.0"
KEY = ("plant_id_eia", "generator_id")
PROJ = ("operational_status_code", "current_planned_generator_operating_date", "capacity_mw")
SKIP = ("report_date", "valid_until_date")
KEYS = ("3075/11", "6175/2", "3082/2", "3925/1", "3655/1")
TOP = 20


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def missing(v):
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def same(a, b):
    """Equal, with a missing value equal only to a missing value (as in drop_duplicates)."""
    ma, mb = missing(a), missing(b)
    if ma or mb:
        return ma and mb
    return bool(a == b)


def month(v):
    return pd.Timestamp(v).strftime("%Y-%m")


def census(df, keys=()):
    """df: PUDL's changelog (all columns) -> dict of counts."""
    cols = [c for c in df.columns if c not in SKIP and c not in KEY]
    df = df.sort_values(list(KEY) + ["report_date"], kind="mergesort")
    by_col, by_set, by_year, by_month = (collections.Counter() for _ in range(4))
    want = set(keys)
    ex = {k: [] for k in keys}
    n = {"records": 0, "generators": 0, "returns": 0, "no_diff": 0, "last_record": 0}
    for key, g in df.groupby(list(KEY), sort=False):
        k = "%s/%s" % key
        n["generators"] += 1
        recs = g.to_dict("records")
        seen = []
        for i, r in enumerate(recs):
            n["records"] += 1
            p = tuple(None if missing(r[c]) else r[c] for c in PROJ)
            earlier = [x for q, x in seen if q == p] if i and p != seen[-1][0] else []
            seen.append((p, r))
            if not earlier:
                continue
            j = earlier[-1]
            diff = tuple(c for c in cols if not same(r[c], j[c]))
            m = month(r["report_date"])
            n["returns"] += 1
            n["no_diff"] += not diff
            n["last_record"] += i == len(recs) - 1
            for c in diff:
                by_col[c] += 1
            by_set["+".join(diff) or "(none)"] += 1
            by_year[m[:4]] += 1
            by_month[m] += 1
            if k in want:
                ex[k].append({"month": m, "status": r["operational_status_code"],
                              "earlier": month(j["report_date"]), "diff": list(diff)})
    top = lambda c, t=None: [{"value": v, "n": x} for v, x in
                             sorted(c.items(), key=lambda y: (-y[1], y[0]))[:t]]
    return dict(n, columns=top(by_col), sets=top(by_set, TOP),
                years=[{"year": y, "n": by_year[y]} for y in sorted(by_year)],
                months=top(by_month, TOP), examples=ex)


def render(result):
    md = ["# keptreturn %s: which columns let a returning value back into PUDL's changelog" % __version__,
          "", "Descriptive census for docs/heldtrace.md; no prediction is tested. MV2 of Munim, Inc. "
          "(made with AI agents).", ""]
    if result.get("error"):
        return "\n".join(md + ["Not run: %s" % result["error"], ""])
    res = result["result"]
    md += ["PUDL file: %s (%s bytes, file time %s, latest report %s)." % (
        result["pudl"]["file"], result["pudl"]["bytes"], result["pudl"]["mtime"],
        result["pudl"]["max_report"]), "",
           "Records: %d. Generators: %d. Kept returns: %d (no differing column: %d; the generator's "
           "last record: %d)." % (res["records"], res["generators"], res["returns"], res["no_diff"],
                                  res["last_record"]), ""]
    for title, rows, label in (("Columns that differ (a return can count under several)", res["columns"], "column"),
                               ("Column sets (top %d)" % TOP, res["sets"], "columns"),
                               ("Report months (top %d)" % TOP, res["months"], "month")):
        md += ["## " + title, "", "| %s | kept returns |" % label, "|---|---|"]
        md += ["| %s | %d |" % (x["value"], x["n"]) for x in rows]
        md.append("")
    md += ["## Report years", "", "| year | kept returns |", "|---|---|"]
    md += ["| %s | %d |" % (x["year"], x["n"]) for x in res["years"]]
    for k, rows in res["examples"].items():
        md += ["", "### %s" % k, "", "| month | status | earlier record | columns that differ |", "|---|---|---|---|"]
        md += ["| %s | %s | %s | %s |" % (x["month"], x["status"], x["earlier"], ", ".join(x["diff"]))
               for x in rows]
        if not rows:
            md.append("| none | | | |")
    return "\n".join(md) + "\n"


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"), recursive=True))
    return hits[0] if hits else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--key", action="append", default=None, help="plant/generator (repeatable)")
    args = ap.parse_args(argv)
    keys = tuple(args.key or KEYS)
    os.makedirs(args.out_dir, exist_ok=True)
    result = {"version": __version__, "started_at": now(), "keys": keys}
    path = find_parquet(args.data_dir)
    if path is None:
        result["error"] = "no *changelog_generators*.parquet under %s" % args.data_dir
    else:
        df = pd.read_parquet(path)
        st = os.stat(path)
        result["pudl"] = {"file": os.path.basename(path), "bytes": st.st_size, "rows": len(df),
                          "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                          "max_report": month(df["report_date"].max()), "columns": list(df.columns)}
        result["result"] = census(df, keys)
    result["finished_at"] = now()
    with open(os.path.join(args.out_dir, "keptreturn.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "keptreturn.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
