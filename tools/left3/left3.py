"""Descriptive look (no predictions) at the generators behind docs/pudl-pr2.md: the 3 keys where
PUDL's EIA-860M changelog and the workbook route disagree after PR #5731 ("none -> left"),
the 7 other keys both count as "left" in September 2026, and the 9 keys of the plan.

For each key it writes:
- every row of PUDL's core_eia860m__changelog_generators for the key, from the build job
  pudl-pr2-v1 read (the parquet in --data-dir, if present) and from today's nightly build;
- every row for the key on EVERY sheet of EIA's August and September 2026 EIA-860M workbooks,
  including "Canceled or Postponed" and the _PR sheets, which workbook.py skips.

PUDL's data (CC BY 4.0) and EIA's files are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import argparse
import glob
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"
NIGHTLY = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
           "core_eia860m__changelog_generators.parquet")
EIA = "https://www.eia.gov/electricity/data/eia860m/xls/%s_generator2026.xlsx"
MONTHS = ("august", "september")
UA = {"User-Agent": "mv2-left3/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
DIFF = ["67674/LUPE3", "67788/GRS10", "69144/PV1"]
LEFT_BOTH = ["65399/U3", "65655/HECHQ", "66692/HOLLY", "66692/HOLY", "67660/MALAL",
             "68198/TRS", "68811/RIPLE"]
NINE = ["66545/MMTHS", "66893/TXJS2", "67836/GSP1", "67836/GSP2", "68149/RAVEB",
        "68240/SS3PV", "69463/BCRSP", "69967/FTS", "70202/PS56"]
KEYS = DIFF + LEFT_BOTH + NINE


def split_key(key):
    plant, gen = key.split("/", 1)
    return int(plant), gen


def norm_gen(value):
    """EIA generator ids as text: 10.0 -> '10', ' A1 ' -> 'A1'."""
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        if value.is_integer():
            return str(int(value))
    return str(value).strip()


def norm_plant(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def find_header(rows, limit=10):
    """Index of the first of the first `limit` rows that has both a 'Plant ID' and a
    'Generator ID' cell, or None."""
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip() for c in row if c is not None}
        if "Plant ID" in cells and "Generator ID" in cells:
            return i
    return None


def sheet_rows(rows, keys):
    """Rows (as dicts keyed by the header) of one sheet whose (Plant ID, Generator ID) is in keys."""
    h = find_header(rows)
    if h is None:
        return None, []
    header = [str(c).strip() if c is not None else "" for c in rows[h]]
    pi, gi = header.index("Plant ID"), header.index("Generator ID")
    want = {split_key(k) for k in keys}
    out = []
    for row in rows[h + 1:]:
        if len(row) <= max(pi, gi):
            continue
        k = (norm_plant(row[pi]), norm_gen(row[gi]))
        if k in want:
            out.append({header[j]: (None if v is None else str(v))
                        for j, v in enumerate(row) if j < len(header) and header[j]})
    return h, out


def fetch(url, timeout=600):
    last = None
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # retried, then raised
            last = exc
            time.sleep(30)
    raise last


def pudl_rows(path, keys):
    import pandas as pd
    df = pd.read_parquet(path)
    cols = list(df.columns)
    df["_key"] = (df["plant_id_eia"].astype("Int64").astype(str) + "/"
                  + df["generator_id"].astype(str).str.strip())
    sub = df[df["_key"].isin(keys)].drop(columns=["_key"])
    sort = [c for c in ("plant_id_eia", "generator_id", "report_date") if c in cols]
    sub = sub.sort_values(sort)
    return cols, len(df), [{c: (None if pd.isna(v) else str(v)) for c, v in r.items()}
                           for r in sub.to_dict("records")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "left3.py " + VERSION, "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "keys": KEYS,
           "groups": {"diff": DIFF, "left_both": LEFT_BOTH, "nine": NINE},
           "downloads": {}, "pudl": {}, "eia": {}, "errors": {}}

    def save():
        with open(os.path.join(a.out_dir, "left3.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)

    builds = []
    for p in sorted(glob.glob(os.path.join(a.data_dir, "**", "*.parquet"), recursive=True)):
        with open(p, "rb") as fh:
            builds.append(("data_dir:" + os.path.relpath(p, a.data_dir),
                           p, hashlib.md5(fh.read()).hexdigest(), None))
    try:
        raw, headers = fetch(NIGHTLY)
        today = os.path.join(a.out_dir, "_nightly.parquet")
        with open(today, "wb") as fh:
            fh.write(raw)
        builds.append(("nightly_today", today, hashlib.md5(raw).hexdigest(),
                       headers.get("Last-Modified")))
    except Exception as exc:
        res["errors"]["nightly_today"] = "%s: %s" % (type(exc).__name__, exc)
    for name, path, md5, lm in builds:
        try:
            cols, n, rows = pudl_rows(path, KEYS)
            res["pudl"][name] = {"md5": md5, "last_modified": lm, "rows_total": n,
                                 "columns": cols, "rows": rows}
        except Exception as exc:
            res["errors"]["pudl:" + name] = "%s: %s" % (type(exc).__name__, exc)
        save()
    if os.path.exists(os.path.join(a.out_dir, "_nightly.parquet")):
        os.remove(os.path.join(a.out_dir, "_nightly.parquet"))

    import openpyxl
    for month in MONTHS:
        url = EIA % month
        try:
            raw, headers = fetch(url)
            res["downloads"][month] = {"url": url, "bytes": len(raw),
                                       "md5": hashlib.md5(raw).hexdigest(),
                                       "last_modified": headers.get("Last-Modified")}
            wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
            res["eia"][month] = {}
            for ws in wb.worksheets:
                rows = [list(r) for r in ws.iter_rows(values_only=True)]
                h, found = sheet_rows(rows, KEYS)
                res["eia"][month][ws.title] = {"header_row": h, "rows": len(rows),
                                               "found": found}
            wb.close()
        except Exception as exc:
            res["errors"]["eia:" + month] = "%s: %s" % (type(exc).__name__, exc)
        save()

    # Where each key sits: sheets per month, and PUDL row count per build.
    where = {}
    for key in KEYS:
        plant, gen = split_key(key)
        w = {}
        for month, sheets in res["eia"].items():
            w[month] = sorted(s for s, v in sheets.items()
                              if any(norm_plant(r.get("Plant ID")) == plant
                                     and norm_gen(r.get("Generator ID")) == gen
                                     for r in v["found"]))
        for name, b in res["pudl"].items():
            w["pudl:" + name] = sum(1 for r in b["rows"]
                                    if norm_plant(r.get("plant_id_eia")) == plant
                                    and norm_gen(r.get("generator_id")) == gen)
        where[key] = w
    res["where"] = where
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({"downloads": res["downloads"], "errors": res["errors"],
                      "pudl_builds": {k: {x: v[x] for x in ("md5", "last_modified", "rows_total")}
                                      for k, v in res["pudl"].items()},
                      "where": where}, indent=1, default=str))


if __name__ == "__main__":
    main()
