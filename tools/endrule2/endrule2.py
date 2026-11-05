"""endrule2: pre-registration endrule-2 (docs/endrule2-plan.md).

endrule-1 (docs/endrule.md) could not be scored: its gate G2 asked for at least 10 generators
in each of two one-month groups, and PUDL's newest build had 4 and 8. endrule-2 asks the same
question over nine EIA-860M months (January to September 2026): does each generator's last
record in PUDL's EIA-860M changelog (core_eia860m__changelog_generators) end one month after
the last EIA-860M month that lists it, as PUDL PR #5731 documents?

For every generator whose last record ends in month E (E from 2026-02 to 2026-09), it counts
whether EIA's workbook for month E-1 lists it and whether EIA's workbook for month E lists it,
on the sheets PUDL reads (names with neither "cancel" nor "_pr"), and whether month E puts it
on the "Canceled or Postponed" sheet. Only the end months 2026-02 to 2026-07 are scored: the
12 generators ending 2026-08 and 2026-09 were already seen in endrule-1.

It reuses tools/endrule/endrule.py 0.1.0 (published with endrule-1) for keys, downloads and
sheet reading. PUDL's data (CC BY 4.0) and EIA's files are downloaded at run time and not
stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import argparse
import hashlib
import io
import json
import os
import sys
import time

import endrule as er

VERSION = "0.1.0"
MONTHS = (("2026-01", "january"), ("2026-02", "february"), ("2026-03", "march"),
          ("2026-04", "april"), ("2026-05", "may"), ("2026-06", "june"),
          ("2026-07", "july"), ("2026-08", "august"), ("2026-09", "september"))
FRESH = ("2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07")
SEEN = ("2026-08", "2026-09")
LATEST = "2026-09"
MIN_FRESH = 100


def end_groups(ends, wanted):
    """{key: end month} -> {end month: sorted keys} for the wanted end months only."""
    out = {m: [] for m in wanted}
    for key, end in ends.items():
        if end in out:
            out[end].append(key)
    return {m: sorted(v) for m, v in out.items()}


def cancel_keys(sheet_sets):
    """Keys on a "Canceled or Postponed" sheet (a name with "cancel" but not "_pr")."""
    out = set()
    for name, keys in sheet_sets.items():
        low = str(name).lower()
        if keys and "cancel" in low and "_pr" not in low:
            out |= keys
    return out


def tally(groups, pools, cancels):
    """Per end month E: n, listed in E-1, listed in E, on the cancel sheet in E."""
    rows = {}
    for e, keys in groups.items():
        prev = er.month_add(e, -1)
        rows[e] = {"n": len(keys),
                   "in_prev": sum(1 for k in keys if k in pools.get(prev, set())),
                   "in_end": sum(1 for k in keys if k in pools.get(e, set())),
                   "cancel_end": sum(1 for k in keys if k in cancels.get(e, set()))}
    return rows


def pooled(rows, months):
    n = sum(rows[m]["n"] for m in months)
    out = {"n": n}
    for f in ("in_prev", "in_end", "cancel_end"):
        k = sum(rows[m][f] for m in months)
        out[f] = k
        out[f + "_share"] = round(k / n, 4) if n else None
    return out


def score(m):
    """Gates and predictions from the metrics dict m, with the plan's bars."""
    s = {}
    s["G1"] = m["latest_report"] == LATEST and m["build_after_merge"]
    s["G2"] = m["workbooks_ok"] and m["fresh"]["n"] >= MIN_FRESH
    if not (s["G1"] and s["G2"]):
        return s
    f = m["fresh"]
    s["Q1"] = f["in_prev_share"] >= 0.95
    s["Q2"] = f["in_end_share"] <= 0.05
    s["Q3"] = all(r["n"] > 0 and r["in_prev"] / r["n"] >= 0.90 and r["in_end"] / r["n"] <= 0.10
                  for r in (m["by_end"][e] for e in FRESH))
    s["Q4"] = f["cancel_end_share"] >= 0.60
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "endrule2.py " + VERSION, "uses": "endrule.py " + er.VERSION,
           "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "downloads": {}, "errors": {}}

    def save():
        with open(os.path.join(a.out_dir, "endrule2.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)

    import pandas as pd
    raw, headers = er.fetch(er.NIGHTLY)
    res["downloads"]["pudl"] = {"url": er.NIGHTLY, "bytes": len(raw),
                                "md5": hashlib.md5(raw).hexdigest(),
                                "last_modified": headers.get("Last-Modified")}
    lm = headers.get("Last-Modified")
    after = False
    if lm:
        from email.utils import parsedate_to_datetime
        stamp = parsedate_to_datetime(lm).strftime("%Y-%m-%dT%H:%M:%SZ")
        after = stamp > er.MERGED
    df = pd.read_parquet(io.BytesIO(raw),
                         columns=["plant_id_eia", "generator_id", "report_date",
                                  "valid_until_date"])
    del raw
    keys = [er.make_key(p, g) for p, g in zip(df["plant_id_eia"].tolist(),
                                              df["generator_id"].tolist())]
    reps = [er.month_of(x) for x in df["report_date"].tolist()]
    ends = [er.month_of(x) for x in df["valid_until_date"].tolist()]
    latest = max(r for r in reps if r)
    last = er.last_ends(zip(keys, reps, ends))
    groups = end_groups(last, FRESH + SEEN + ("2026-10",))
    res["pudl"] = {"rows": len(df), "keys": len(last), "latest_report": latest,
                   "build_after_merge": after,
                   "null_valid_until_rows": sum(e is None for e in ends),
                   "group_sizes": {m: len(v) for m, v in groups.items()},
                   "groups": {m: v for m, v in groups.items() if m != "2026-10"}}
    del df
    save()

    pools, cancels, ok = {}, {}, True
    for month, name in MONTHS:
        url, wraw, wh, tried = er.fetch_workbook(name)
        if url is None:
            res["errors"]["eia:" + month] = tried
            ok = False
            continue
        res["downloads"][month] = {"url": url, "bytes": len(wraw),
                                   "md5": hashlib.md5(wraw).hexdigest(),
                                   "last_modified": wh.get("Last-Modified"), "tried": tried}
        try:
            sheets = er.read_workbook(wraw)
        except Exception as exc:
            res["errors"]["eia:" + month] = "%s: %s" % (type(exc).__name__, exc)
            ok = False
            continue
        del wraw
        names = [n.lower() for n, v in sheets.items() if v is not None]
        if not any(n.startswith("operating") for n in names) or not any(
                n.startswith("planned") for n in names):
            ok = False
        res["downloads"][month]["sheets"] = {n: (None if v is None else len(v))
                                             for n, v in sheets.items()}
        pools[month] = er.listed(sheets)
        cancels[month] = cancel_keys(sheets)
        save()

    scored = {m: groups[m] for m in FRESH + SEEN}
    rows = tally(scored, pools, cancels)
    m = {"latest_report": latest, "build_after_merge": after, "workbooks_ok": ok,
         "by_end": rows, "fresh": pooled(rows, FRESH), "seen": pooled(rows, SEEN),
         "A9_in_2026-09": er.count_in(groups["2026-10"], pools.get("2026-09", set()))}
    # Fresh keys that break the documented rule, by end month, for reading (not scored).
    m["fresh_not_listed_prev"] = {e: [k for k in groups[e]
                                      if k not in pools.get(er.month_add(e, -1), set())]
                                  for e in FRESH}
    m["fresh_listed_end"] = {e: [k for k in groups[e] if k in pools.get(e, set())]
                             for e in FRESH}
    res["metrics"] = m
    res["scores"] = score(m)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({"downloads": res["downloads"], "errors": res["errors"],
                      "pudl": {k: v for k, v in res["pudl"].items() if k != "groups"},
                      "metrics": m, "scores": res["scores"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
