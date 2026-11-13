"""unitzero: all-zero and leading-zero ID cases in PUDL's EPA and EIA identifiers
(pre-registration id unitzero-1; plan: docs/unitzero-plan.md in munimtechnologies/eia860m-slip).

PUDL normalizes plant-part IDs in two different ways (code read on 2026-11-13):

* pudl.helpers.remove_leading_zeros_from_numeric_strings (EIA-860/860M/861/923 extract, and the
  EPA-EIA crosswalk's generator_id, boiler_id and emissions_unit_id_epa in glue.py): where a value
  matches r"^0+\\d+$" it replaces r"^0+" with "". So "007" -> "7", "0" stays "0", but "00" -> "".
* pudl.transform.epacems.transform_epacems (EPA CEMS hourly emissions_unit_id_epa): where a value
  is all digits it strips leading "0" characters. So "007" -> "7", "0" -> "" and "00" -> "".

This script measures how often those cases occur in real data: the EPA's own crosswalk
(USEPA/camd-eia-crosswalk), PUDL's nightly crosswalk and entity tables, and the unit IDs of PUDL's
nightly EPA CEMS hourly table (read column by column, never stored).

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Usage: python unitzero.py --out-dir OUT [--wait-for URL --token TEXT --minutes N]

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com).
"""

import argparse
import csv
import io
import json
import os
import re
import time
import urllib.request
from collections import Counter, defaultdict

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
CEMS_BUCKET_KEY = "pudl.catalyst.coop/nightly/core_epacems__hourly_emissions.parquet"
EPA_XW_URL = "https://raw.githubusercontent.com/USEPA/camd-eia-crosswalk/master/epa_eia_crosswalk.csv"
EPA_XW_COMMIT_URL = ("https://api.github.com/repos/USEPA/camd-eia-crosswalk/commits"
                     "?path=epa_eia_crosswalk.csv&per_page=1")
UA = {"User-Agent": "mv2-unitzero/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

# PUDL nightly tables and the (plant column, ID column) pairs read from each.
TABLES = {
    "core_epa__assn_eia_epacamd": [("plant_id_epa", "emissions_unit_id_epa"),
                                   ("plant_id_eia", "generator_id"),
                                   ("plant_id_eia", "boiler_id")],
    "core_epa__assn_eia_epacamd_subplant_ids": [("plant_id_epa", "emissions_unit_id_epa"),
                                                ("plant_id_eia", "generator_id")],
    "core_eia__entity_generators": [("plant_id_eia", "generator_id")],
    "core_eia__entity_boilers": [("plant_id_eia", "boiler_id")],
}
# EPA crosswalk (raw) ID columns and the plant column each one lives in.
EPA_XW_IDS = [("CAMD_PLANT_ID", "CAMD_UNIT_ID"), ("CAMD_PLANT_ID", "CAMD_GENERATOR_ID"),
              ("EIA_PLANT_ID", "EIA_GENERATOR_ID"), ("EIA_PLANT_ID", "EIA_BOILER_ID")]
CEMS_WANTED = ["plant_id_epa", "plant_id_eia", "emissions_unit_id_epa", "year"]

GATE_MIN_CEMS_PLANTS = 1000
P5_ROW_SHARE = 0.001

_HELPER_MATCH = re.compile(r"^0+\d+$")


# ---- the two normalizations, value by value ------------------------------------------------

def pudl_helper(value):
    """remove_leading_zeros_from_numeric_strings on one value (pandas str.contains uses
    re.search; str.replace(r"^0+", "", regex=True) is re.sub)."""
    if not isinstance(value, str):
        return value
    if _HELPER_MATCH.search(value):
        return re.sub(r"^0+", "", value)
    return value


def cems_strip(value):
    """transform_epacems on one value: all digits -> strip leading '0' characters (polars
    str.contains(r"^\\d+$") with Rust regex, where $ is the end of the text)."""
    if not isinstance(value, str):
        return value
    if re.fullmatch(r"\d+", value):
        return value.lstrip("0")
    return value


def keep_one_zero(value):
    """A normalization that agrees with both on every other value but maps all-zero IDs to '0'
    (shown for comparison only)."""
    if not isinstance(value, str):
        return value
    if re.fullmatch(r"\d+", value):
        return re.sub(r"^0+(?=\d)", "", value)
    return value


def all_zero(value):
    return isinstance(value, str) and value != "" and set(value) == {"0"}


def collisions(pairs, norm=pudl_helper):
    """pairs: iterable of (plant, raw id). Returns {(plant, normalized): sorted raw ids} for every
    normalized ID that two or more distinct raw IDs at the same plant collapse into."""
    groups = defaultdict(set)
    for plant, raw in pairs:
        if isinstance(raw, str) and raw != "":
            groups[(plant, norm(raw))].add(raw)
    return {k: sorted(v) for k, v in groups.items() if len(v) > 1}


def id_profile(values):
    """Counts of the cases that matter in one column of raw values (None = null)."""
    c = Counter()
    for v in values:
        if v is None:
            c["null"] += 1
        elif v == "":
            c["empty"] += 1
        elif v == "0":
            c["zero"] += 1
        elif all_zero(v):
            c["multi_zero"] += 1
        elif pudl_helper(v) != v:
            c["leading_zero"] += 1
        c["values"] += 1
    return {k: int(c[k]) for k in ("values", "null", "empty", "zero", "multi_zero", "leading_zero")}


# ---- scoring -------------------------------------------------------------------------------

def score(m):
    """Gate and predictions of pre-registration id unitzero-1, from the measured dict m."""
    gate = (m["downloads_ok"] and m["cems"]["rows_scanned"] == m["cems"]["rows_in_metadata"]
            and m["cems"]["plants_epa"] >= GATE_MIN_CEMS_PLANTS)
    epa_unit = m["epa_crosswalk"]["CAMD_UNIT_ID"]
    preds = {
        "P1": epa_unit["zero"] + epa_unit["multi_zero"] >= 1,
        "P2": m["cems"]["empty_unit_rows"] >= 1,
        "P3": (m["pudl"]["core_eia__entity_generators"]["generator_id"]["empty"] == 0
               and m["pudl"]["core_eia__entity_boilers"]["boiler_id"]["empty"] == 0),
        "P4": (m["epa_crosswalk_collisions"]["CAMD_UNIT_ID"]
               + m["epa_crosswalk_collisions"]["EIA_GENERATOR_ID"]) >= 1,
        "P5": m["cems"]["empty_unit_rows"] < P5_ROW_SHARE * m["cems"]["rows_scanned"],
    }
    return {"gate_G1": bool(gate), "predictions": {k: bool(v) for k, v in preds.items()},
            "held": int(sum(bool(v) for v in preds.values())), "of": len(preds)}


# ---- I/O -----------------------------------------------------------------------------------

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(url, timeout=600):
    last = None
    for attempt in range(3):
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
    """None, NaN, pd.NA and NaT are null; any str (even '') is not. Needs no pandas."""
    if v is None:
        return True
    if isinstance(v, str):
        return False
    try:
        return bool(v != v)
    except TypeError:  # pd.NA refuses bool()
        return True


def is_text(v, text):
    """v is a str equal to text (safe for None, NaN and pd.NA)."""
    return isinstance(v, str) and v == text


def as_str_or_none(series):
    return [None if isnull(v) else str(v) for v in series.tolist()]


def scan_cems(cases):
    import pyarrow.fs as pafs
    import pyarrow.parquet as pq

    fs = pafs.S3FileSystem(anonymous=True, region="us-west-2")
    info = fs.get_file_info(CEMS_BUCKET_KEY)
    with fs.open_input_file(CEMS_BUCKET_KEY) as fh:
        pf = pq.ParquetFile(fh)
        names = pf.schema_arrow.names
        cols = [c for c in CEMS_WANTED if c in names]
        res = {"bytes": int(info.size), "mtime": str(info.mtime), "columns_read": cols,
               "rows_in_metadata": int(pf.metadata.num_rows),
               "row_groups": int(pf.metadata.num_row_groups)}
        counts = Counter()
        scanned = 0
        for batch in pf.iter_batches(batch_size=1_000_000, columns=cols):
            df = batch.to_pandas()
            scanned += len(df)
            df["emissions_unit_id_epa"] = df["emissions_unit_id_epa"].astype("object")
            g = df.groupby(cols, dropna=False).size()
            for key, n in g.items():
                key = key if isinstance(key, tuple) else (key,)
                # one stable null (NaN keys would hash apart), so null units count once
                counts[tuple(None if isnull(x) else x for x in key)] += int(n)
    res["rows_scanned"] = int(scanned)
    i_plant, i_unit = cols.index("plant_id_epa"), cols.index("emissions_unit_id_epa")
    units = defaultdict(int)
    for key, n in counts.items():
        units[(key[i_plant], key[i_unit])] += n
    res["plants_epa"] = len({p for p, _ in units})
    res["plant_units"] = len(units)
    unit_vals = [None if isnull(u) else str(u) for _, u in units]
    res["unit_profile_over_plant_units"] = id_profile(unit_vals)
    res["empty_unit_rows"] = int(sum(n for (p, u), n in units.items() if is_text(u, "")))
    res["null_unit_rows"] = int(sum(n for (p, u), n in units.items() if isnull(u)))
    res["zero_unit_rows"] = int(sum(n for (p, u), n in units.items() if is_text(u, "0")))
    res["empty_unit_plants"] = sorted({str(p) for (p, u) in units if is_text(u, "")})
    for key, n in sorted(counts.items(), key=lambda kv: str(kv[0])):
        u = key[i_unit]
        if is_text(u, "") or is_text(u, "0"):
            row = dict(zip(cols, key))
            cases.append({"source": "pudl_nightly", "table": "core_epacems__hourly_emissions",
                          "column": "emissions_unit_id_epa", "plant": str(row["plant_id_epa"]),
                          "raw": u, "detail": json.dumps({k: str(v) for k, v in row.items()}),
                          "rows": n})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=240)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    out_json = os.path.join(args.out_dir, "unitzero.json")
    res = {"version": VERSION, "started": now(), "downloads": {}}
    if args.wait_for:
        live, polls, at = wait_for(args.wait_for, args.token, args.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live; no data read"
            with open(out_json, "w") as fh:
                json.dump(res, fh, indent=1)
            print(res["stopped"])
            return
    import pandas as pd

    cases = []
    ok = True

    # 1. EPA's own crosswalk, as published on GitHub (all values read as text, nothing parsed).
    try:
        raw, headers = fetch(EPA_XW_URL)
        res["downloads"]["epa_crosswalk"] = {"bytes": len(raw), "etag": headers.get("ETag")}
        try:
            res["downloads"]["epa_crosswalk"]["commit"] = json.loads(fetch(EPA_XW_COMMIT_URL, 60)[0])[0]["sha"]
        except Exception as exc:
            res["downloads"]["epa_crosswalk"]["commit_error"] = str(exc)[:300]
        rows = [{(k or "").strip().upper(): v for k, v in r.items()}
                for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))]
        res["epa_crosswalk_rows"] = len(rows)
        res["epa_crosswalk_columns"] = list(rows[0].keys()) if rows else []
        res["epa_crosswalk_missing_columns"] = sorted(
            {c for pair in EPA_XW_IDS for c in pair} - set(res["epa_crosswalk_columns"]))
        if res["epa_crosswalk_missing_columns"]:
            ok = False
        res["epa_crosswalk"] = {}
        res["epa_crosswalk_collisions"] = {}
        for plant_col, id_col in EPA_XW_IDS:
            vals = [r.get(id_col) for r in rows]
            vals = [None if v is None else v for v in vals]
            # CSV has no nulls: an empty cell is ''. Report it as empty, as read.
            res["epa_crosswalk"][id_col] = id_profile(vals)
            col = collisions([(r.get(plant_col), r.get(id_col)) for r in rows])
            res["epa_crosswalk_collisions"][id_col] = len(col)
            for (plant, norm), raws in sorted(col.items(), key=lambda kv: str(kv[0])):
                cases.append({"source": "epa_github", "table": "epa_eia_crosswalk.csv",
                              "column": id_col, "plant": plant, "raw": "|".join(raws),
                              "detail": "collide as %r" % norm, "rows": ""})
            for r in rows:
                v = r.get(id_col)
                if all_zero(v):
                    cases.append({"source": "epa_github", "table": "epa_eia_crosswalk.csv",
                                  "column": id_col, "plant": r.get(plant_col), "raw": v,
                                  "detail": json.dumps({k: r.get(k) for k in (
                                      "CAMD_PLANT_ID", "CAMD_UNIT_ID", "CAMD_GENERATOR_ID",
                                      "EIA_PLANT_ID", "EIA_GENERATOR_ID", "EIA_BOILER_ID")}),
                                  "rows": 1})
    except Exception as exc:
        ok = False
        res["epa_crosswalk_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:500])

    # 2. PUDL nightly tables.
    res["pudl"] = {}
    xw_zero_plants = set()
    for table, pairs in TABLES.items():
        try:
            raw, headers = fetch(NIGHTLY % table)
            res["downloads"][table] = {"bytes": len(raw),
                                       "last_modified": headers.get("Last-Modified"),
                                       "etag": headers.get("ETag")}
            cols = sorted({c for pair in pairs for c in pair})
            df = pd.read_parquet(io.BytesIO(raw), columns=cols)
            res["pudl"][table] = {"rows": int(len(df))}
            for plant_col, id_col in pairs:
                vals = as_str_or_none(df[id_col])
                res["pudl"][table][id_col] = id_profile(vals)
                plants = df[plant_col].tolist()
                for plant, v in zip(plants, vals):
                    if v == "" or v == "0" or all_zero(v):
                        cases.append({"source": "pudl_nightly", "table": table, "column": id_col,
                                      "plant": str(plant), "raw": v, "detail": plant_col,
                                      "rows": 1})
                        if table == "core_epa__assn_eia_epacamd" and id_col == "emissions_unit_id_epa" and v == "0":
                            xw_zero_plants.add(str(plant))
        except Exception as exc:
            ok = False
            res["pudl"][table] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:500])}

    # 3. EPA CEMS hourly unit IDs (column by column, nothing stored).
    try:
        res["cems"] = scan_cems(cases)
        cems_empty = {str(p) for p in res["cems"]["empty_unit_plants"]}
        res["cems_empty_vs_crosswalk_zero"] = {
            "cems_plants_with_empty_unit": sorted(cems_empty),
            "crosswalk_plants_with_unit_0": sorted(xw_zero_plants),
            "both": sorted(cems_empty & xw_zero_plants),
        }
    except Exception as exc:
        ok = False
        res["cems"] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
                       "rows_scanned": -1, "rows_in_metadata": 0, "plants_epa": 0,
                       "empty_unit_rows": 0}

    res["downloads_ok"] = ok
    try:
        res["score"] = score(res)
    except Exception as exc:
        res["score_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:500])
    res["cases"] = len(cases)
    res["finished"] = now()
    with open(os.path.join(args.out_dir, "unitzero-cases.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["source", "table", "column", "plant", "raw", "detail",
                                           "rows"])
        w.writeheader()
        for c in cases:
            w.writerow(c)
    with open(out_json, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "downloads"}, indent=1, default=str)[:20000])


if __name__ == "__main__":
    main()
