"""Count zero-length validity in PUDL's published forensics entity-resolution tables.

PUDL's make_changelog sets each record's valid_until_date to the report_date of the next
row in its series (id columns + column_name). The forensics tables keep one row per source
record, so a series can hold several rows on one report_date; every one of them but the
last then gets valid_until_date equal to its own report_date. PUDL's own unit test
test_make_changelog_valid_until_is_per_column asserts valid_until_date > report_date.

This tool downloads the four _core_eia__forensics_entity_resolution_* tables from PUDL's
nightly build and counts, per table, records whose valid_until_date equals (or precedes)
their report_date, and whether each such record shares its series and report_date with
another record. The plan with every bar is docs/pudl-tall-plan.md in
munimtechnologies/eia860m-slip. PUDL's data is CC BY 4.0; it is downloaded at run time.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

import pandas as pd

VERSION = "0.1.0"
BASE = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
TABLES = [
    "_core_eia__forensics_entity_resolution_boilers",
    "_core_eia__forensics_entity_resolution_generators",
    "_core_eia__forensics_entity_resolution_plants",
    "_core_eia__forensics_entity_resolution_utilities",
]
NEEDED = ["report_date", "valid_until_date", "column_name", "record_value"]
NOT_ID = NEEDED + ["entity_occurrences", "record_occurrences", "consistent_rate",
                   "is_candidate"]
UA = {"User-Agent": "mv2-pudl-tall-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read(), dict(resp.headers)


def wait_for(url, token, minutes):
    """Poll url until its text contains token; returns (live, polls, utc time)."""
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url)[0].decode("utf-8", "replace"):
                return True, polls, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        time.sleep(60)


def id_columns(df):
    return [c for c in df.columns if c not in NOT_ID]


def count_table(df):
    """Zero-length and backwards validity in one forensics table."""
    ids = id_columns(df)
    series = ids + ["column_name"]
    rd = pd.to_datetime(df["report_date"])
    vu = pd.to_datetime(df["valid_until_date"])
    group_size = df.groupby(series + ["report_date"], dropna=False, observed=True)[
        "record_value"].transform("size")
    distinct = df.assign(_v=df["record_value"].astype("string")).groupby(
        series + ["report_date"], dropna=False, observed=True)["_v"].nunique(dropna=False)
    zero = (vu == rd).fillna(False).to_numpy()
    before = (vu < rd).fillna(False).to_numpy()
    shared = (group_size > 1).to_numpy()
    out = {
        "rows": int(len(df)),
        "columns": list(map(str, df.columns)),
        "id_columns": ids,
        "valid_until_missing": int(vu.isna().sum()),
        "zero_length": int(zero.sum()),
        "zero_length_share": round(float(zero.mean()), 4) if len(df) else 0.0,
        "zero_length_sharing_series_date": int((zero & shared).sum()),
        "zero_length_alone_on_series_date": int((zero & ~shared).sum()),
        "valid_until_before_report_date": int(before.sum()),
        "rows_sharing_series_date": int(shared.sum()),
        "series_dates": int(len(distinct)),
        "series_dates_with_several_rows": int(
            (df.groupby(series + ["report_date"], dropna=False, observed=True)
             .size() > 1).sum()),
        "series_dates_with_several_values": int((distinct > 1).sum()),
    }
    if "is_candidate" in df.columns:
        cand = df["is_candidate"].fillna(False).astype(bool).to_numpy()
        out["zero_length_is_candidate"] = int((zero & cand).sum())
    examples = df[zero].sort_values(series + ["report_date"]).head(3)
    out["examples"] = [
        {k: str(v) for k, v in r.items()}
        for r in examples[series + ["report_date", "valid_until_date", "record_value"]]
        .to_dict("records")
    ]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=120)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    result = {"tool": "tall_check.py " + VERSION, "python": sys.version.split()[0],
              "pandas": pd.__version__}
    if a.wait_for:
        live, polls, at = wait_for(a.wait_for, a.token, a.minutes)
        result["plan_live"] = {"live": live, "polls": polls, "at": at}
    result["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    gate = True
    for name in TABLES:
        entry = {}
        try:
            raw, headers = fetch(BASE + name + ".parquet")
            entry["bytes"] = len(raw)
            entry["md5"] = hashlib.md5(raw).hexdigest()
            entry["last_modified"] = headers.get("Last-Modified", "")
            path = os.path.join(a.out_dir, name + ".parquet")
            with open(path, "wb") as f:
                f.write(raw)
            df = pd.read_parquet(path)
            os.remove(path)
            missing = [c for c in NEEDED if c not in df.columns]
            entry["missing_columns"] = missing
            if missing:
                gate = False
            else:
                entry.update(count_table(df))
        except Exception as exc:  # reported, not hidden
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
            gate = False
        result[name] = entry
    result["gate"] = gate
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(a.out_dir, "tall_check.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
