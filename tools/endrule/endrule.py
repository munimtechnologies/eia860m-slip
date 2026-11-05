"""endrule: pre-registration endrule-1 (docs/endrule-plan.md).

Does each generator's last record in PUDL's EIA-860M changelog
(core_eia860m__changelog_generators) end one month after the last EIA-860M month that lists the
generator, as PUDL PR #5731 (merged 2 November 2026) documents? MV2's own tools read a last
record's valid_until_date as the last month in force (the rule before #5731), which is one
month too late on builds made after the merge.

For the newest PUDL build it groups generators by the valid_until_date of their last record
(A9: 2026-10-01, A8: 2026-09-01, A7: 2026-08-01) and counts how many of each group EIA's July,
August and September 2026 workbooks list on a sheet PUDL reads (every sheet whose name has
neither "cancel" nor "_pr"). Gates and predictions are scored with the plan's own bars.

The file also holds listed_until_exclusive(), the reading MV2's tools need on post-#5731 builds.

PUDL's data (CC BY 4.0) and EIA's files are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

VERSION = "0.1.0"
NIGHTLY = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
           "core_eia860m__changelog_generators.parquet")
EIA_CURRENT = "https://www.eia.gov/electricity/data/eia860m/xls/%s_generator2026.xlsx"
EIA_ARCHIVE = "https://www.eia.gov/electricity/data/eia860m/archive/xls/%s_generator2026.xlsx"
MONTHS = (("2026-07", "july"), ("2026-08", "august"), ("2026-09", "september"))
SKIP = ("cancel", "_pr")
MERGED = "2026-11-02T18:13:25Z"
LATEST = "2026-09"
GROUPS = {"A9": "2026-10", "A8": "2026-09", "A7": "2026-08"}
MIN_GROUP = 10
DIFF = ["67674/LUPE3", "67788/GRS10", "69144/PV1"]
LEFT_BOTH = ["65399/U3", "65655/HECHQ", "66692/HOLLY", "66692/HOLY", "67660/MALAL",
             "68198/TRS", "68811/RIPLE"]
UA = {"User-Agent": "mv2-endrule/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def gen_id(value):
    """A generator id as text, keyed the same way on both sides: 10.0 -> '10', ' A1 ' -> 'A1',
    a whole-number id without leading zeros ('0011' -> '11', '0' stays '0'), blank -> 'nan'."""
    if value is None:
        return "nan"
    if isinstance(value, float):
        if value != value:
            return "nan"
        if value.is_integer():
            value = int(value)
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return "nan"
    return re.sub(r"^0+(?=\d)", "", text) if text.isdigit() else text


def plant_id(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def make_key(plant, gen):
    p = plant_id(plant)
    return None if p is None else "%d/%s" % (p, gen_id(gen))


def month_of(value):
    """'2026-09-01', '2026-09-01 00:00:00' or a date -> '2026-09'; blank -> None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "nat", "none"):
        return None
    return text[:7]


def month_add(month, n):
    y, m = int(month[:4]), int(month[5:7])
    i = y * 12 + (m - 1) + n
    return "%04d-%02d" % (i // 12, i % 12 + 1)


def last_ends(records):
    """(key, report_month, valid_until_month) rows -> {key: valid_until_month of the key's row
    with the latest report month}. A tie keeps the later end; a blank end reads None."""
    best = {}
    for key, rep, until in records:
        if key is None or rep is None:
            continue
        old = best.get(key)
        if old is None or rep > old[0] or (rep == old[0] and (until or "") > (old[1] or "")):
            best[key] = (rep, until)
    return {k: v[1] for k, v in best.items()}


def group_keys(ends):
    """{key: end month} -> {group: sorted keys} for GROUPS, plus counts of the rest."""
    out = {g: [] for g in GROUPS}
    other = {}
    for key, end in ends.items():
        for g, month in GROUPS.items():
            if end == month:
                out[g].append(key)
                break
        else:
            other[str(end)] = other.get(str(end), 0) + 1
    return {g: sorted(v) for g, v in out.items()}, other


def listed_until_exclusive(report_months, valid_months):
    """The last month each record is in force when every valid_until_date is exclusive (PUDL
    after PR #5731): valid month - 1. Months are integer month indexes; None stays None."""
    return [None if v is None else v - 1 for v in valid_months]


def find_header(rows, limit=10):
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip() for c in row if c is not None}
        if "Plant ID" in cells and "Generator ID" in cells:
            return i
    return None


def sheet_keys(rows):
    """Keys on one sheet (list of row tuples), or None when no header row is found."""
    h = find_header(rows)
    if h is None:
        return None
    header = [str(c).strip() if c is not None else "" for c in rows[h]]
    pi, gi = header.index("Plant ID"), header.index("Generator ID")
    keys = set()
    for row in rows[h + 1:]:
        if len(row) <= max(pi, gi):
            continue
        k = make_key(row[pi], row[gi])
        if k is not None:
            keys.add(k)
    return keys


def skipped(name):
    low = str(name).lower()
    return any(w in low for w in SKIP)


def listed(sheet_sets):
    """{sheet name: set of keys or None} -> union of keys on sheets that are not skipped."""
    out = set()
    for name, keys in sheet_sets.items():
        if keys and not skipped(name):
            out |= keys
    return out


def count_in(keys, pool):
    n = len(keys)
    k = sum(1 for x in keys if x in pool)
    return {"n": n, "in": k, "share": round(k / n, 4) if n else None}


def score(m):
    """Gates and predictions from the metrics dict m, with the plan's bars."""
    s = {}
    s["G1"] = (m["latest_report"] == LATEST and m["build_after_merge"]
               and m["groups"]["A9"] > 0)
    s["G2"] = (m["workbooks_ok"] and m["groups"]["A8"] >= MIN_GROUP
               and m["groups"]["A7"] >= MIN_GROUP)
    if not (s["G1"] and s["G2"]):
        return s
    s["P1"] = m["A8_in_2026-08"]["share"] >= 0.95
    s["P2"] = m["A8_in_2026-09"]["share"] <= 0.05
    s["P3"] = m["A7_in_2026-07"]["share"] >= 0.95 and m["A7_in_2026-08"]["share"] <= 0.05
    s["P4"] = m["A9_in_2026-09"]["share"] >= 0.99
    s["P5"] = m["diff_on_aug_planned"] == len(DIFF) and m["left_both_listed_aug"] == 0
    return s


def fetch(url, timeout=600):
    last = None
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:
            last = exc
            time.sleep(30)
    raise last


def fetch_workbook(name):
    """The first of the current and archive URLs that returns a zip (xlsx) file."""
    tried = []
    for pattern in (EIA_CURRENT, EIA_ARCHIVE):
        url = pattern % name
        try:
            raw, headers = fetch(url)
        except Exception as exc:
            tried.append("%s: %s" % (url, exc))
            continue
        if raw[:2] == b"PK":
            return url, raw, headers, tried
        tried.append("%s: not an xlsx (%d bytes)" % (url, len(raw)))
    return None, None, None, tried


def read_workbook(raw):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = sheet_keys([tuple(r) for r in ws.iter_rows(values_only=True)])
    wb.close()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "endrule.py " + VERSION, "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "downloads": {}, "errors": {}}

    def save():
        with open(os.path.join(a.out_dir, "endrule.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)

    import pandas as pd
    raw, headers = fetch(NIGHTLY)
    res["downloads"]["pudl"] = {"url": NIGHTLY, "bytes": len(raw),
                                "md5": hashlib.md5(raw).hexdigest(),
                                "last_modified": headers.get("Last-Modified")}
    lm = headers.get("Last-Modified")
    after = False
    if lm:
        from email.utils import parsedate_to_datetime
        stamp = parsedate_to_datetime(lm).strftime("%Y-%m-%dT%H:%M:%SZ")
        after = stamp > MERGED
    df = pd.read_parquet(io.BytesIO(raw),
                         columns=["plant_id_eia", "generator_id", "report_date",
                                  "valid_until_date"])
    del raw
    keys = [make_key(p, g) for p, g in zip(df["plant_id_eia"].tolist(),
                                           df["generator_id"].tolist())]
    reps = [month_of(x) for x in df["report_date"].tolist()]
    ends = [month_of(x) for x in df["valid_until_date"].tolist()]
    latest = max(r for r in reps if r)
    last = last_ends(zip(keys, reps, ends))
    groups, other = group_keys(last)
    res["pudl"] = {"rows": len(df), "keys": len(last), "latest_report": latest,
                   "build_after_merge": after, "null_valid_until_rows": sum(e is None for e in ends),
                   "group_sizes": {g: len(v) for g, v in groups.items()},
                   "other_end_months": dict(sorted(other.items())),
                   "groups": {g: v for g, v in groups.items() if g != "A9"}}
    del df
    save()

    sheets = {}
    ok = True
    for month, name in MONTHS:
        url, wraw, wh, tried = fetch_workbook(name)
        if url is None:
            res["errors"]["eia:" + month] = tried
            ok = False
            continue
        res["downloads"][month] = {"url": url, "bytes": len(wraw),
                                   "md5": hashlib.md5(wraw).hexdigest(),
                                   "last_modified": wh.get("Last-Modified"), "tried": tried}
        try:
            sheets[month] = read_workbook(wraw)
        except Exception as exc:
            res["errors"]["eia:" + month] = "%s: %s" % (type(exc).__name__, exc)
            ok = False
            continue
        names = [n.lower() for n, v in sheets[month].items() if v is not None]
        if not any(n.startswith("operating") for n in names) or not any(
                n.startswith("planned") for n in names):
            ok = False
        res["downloads"][month]["sheets"] = {n: (None if v is None else len(v))
                                             for n, v in sheets[month].items()}
        save()

    pools = {m: listed(s) for m, s in sheets.items()}
    m = {"latest_report": latest, "build_after_merge": after, "workbooks_ok": ok,
         "groups": {g: len(v) for g, v in groups.items()}}
    for g, month in (("A8", "2026-08"), ("A8", "2026-09"), ("A7", "2026-07"),
                     ("A7", "2026-08"), ("A9", "2026-09")):
        m["%s_in_%s" % (g, month)] = count_in(groups[g], pools.get(month, set()))
    aug = sheets.get("2026-08", {})
    planned = set()
    for n, v in aug.items():
        if v and n.lower().startswith("planned") and not skipped(n):
            planned |= v
    m["diff_on_aug_planned"] = sum(1 for k in DIFF if k in planned)
    m["left_both_listed_aug"] = sum(1 for k in LEFT_BOTH if k in pools.get("2026-08", set()))
    m["diff_end"] = {k: last.get(k) for k in DIFF}
    m["left_both_end"] = {k: last.get(k) for k in LEFT_BOTH}
    # Where each group's keys sit, sheet by sheet (skipped sheets included), per month.
    where = {}
    for g in ("A8", "A7"):
        where[g] = {}
        for month, s in sheets.items():
            where[g][month] = {n: sum(1 for k in groups[g] if v and k in v)
                               for n, v in s.items()}
    m["where"] = where
    # A8 and A7 keys a workbook still lists where the plan expects none (listed on a read sheet).
    m["A8_listed_sep_keys"] = sorted(k for k in groups["A8"] if k in pools.get("2026-09", set()))
    m["A7_listed_aug_keys"] = sorted(k for k in groups["A7"] if k in pools.get("2026-08", set()))
    m["A8_not_listed_aug_keys"] = sorted(k for k in groups["A8"]
                                         if k not in pools.get("2026-08", set()))
    res["metrics"] = m
    res["scores"] = score(m)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({"downloads": res["downloads"], "errors": res["errors"],
                      "pudl": {k: v for k, v in res["pudl"].items() if k != "groups"},
                      "metrics": {k: v for k, v in m.items() if k != "where"},
                      "scores": res["scores"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
