"""Descriptive look (no predictions) at one crosswalk case found by pre-registration xwcap-1:
EPA CEMS units 1-3 of plant 57865 (EPA's "Antelope Elk Energy Center") are linked to 9.3 MW
engines E01-E03 of EIA plant 57865 ("Antelope Station"), while their highest hourly gross load
is about 204 MW. Public EIA-860M listings put Golden Spread's three ~200 MW Elk combustion
turbines under a different EIA plant, 58835 ("Elk Station").

This script writes, for plants 57865 and 58835 only:
- every EIA-860 generator row PUDL publishes (core_eia860__scd_generators), all years;
- every crosswalk link PUDL publishes (core_epa__assn_eia_epacamd) touching either plant;
- every row of PUDL's CEMS operational characteristics for EPA plants 57865 and 58835;
- yearly EIA-923 net generation by generator (core_eia923__monthly_generation), if readable;
- every row of EPA's crosswalk CSV (USEPA/camd-eia-crosswalk, pinned commit) for either plant,
  plus the header and the number of rows per generator match type (population sizes only).

PUDL's data (CC BY 4.0) and EPA's crosswalk are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import tempfile
import time
import urllib.request

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
EPA_SHA = "3c7d6724cddee38dfb6a06debca732c33a227ed6"
EPA_CSV = ("https://raw.githubusercontent.com/USEPA/camd-eia-crosswalk/%s/epa_eia_crosswalk.csv"
           % EPA_SHA)
PLANTS = (57865, 58835)
PLANT_TEXT = tuple(str(p) for p in PLANTS)
GEN_TABLE = "core_eia860__scd_generators"
XW_TABLE = "core_epa__assn_eia_epacamd"
OPS_TABLE = "out_epacems__yearly_operational_characteristics"
G923_TABLE = "core_eia923__monthly_generation"
UA = {"User-Agent": "mv2-xwelk/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def epa_rows(text, plants=PLANT_TEXT):
    """Rows of EPA's crosswalk CSV whose CAMD or EIA plant id is one of plants, the header,
    and the number of rows per value of every column whose name contains MATCH_TYPE."""
    reader = csv.DictReader(io.StringIO(text))
    header = list(reader.fieldnames or [])
    mt_cols = [c for c in header if "MATCH_TYPE" in c.upper()]
    counts = {c: {} for c in mt_cols}
    keep = []
    n = 0
    for row in reader:
        n += 1
        for c in mt_cols:
            v = (row.get(c) or "").strip()
            counts[c][v] = counts[c].get(v, 0) + 1
        ids = {(row.get("CAMD_PLANT_ID") or "").strip(), (row.get("EIA_PLANT_ID") or "").strip(),
               (row.get("MOD_EIA_PLANT_ID") or "").strip()}
        if ids & set(plants):
            keep.append(row)
    return {"header": header, "rows": n, "match_type_counts": counts, "plant_rows": keep}


def yearly_sum(rows, key_cols, date_col, value_col):
    """Sums value_col by key_cols and the year of date_col (a date, datetime or ISO text)."""
    out = {}
    for r in rows:
        d = r.get(date_col)
        if d is None:
            continue
        year = d.year if hasattr(d, "year") else int(str(d)[:4])
        k = tuple(r.get(c) for c in key_cols) + (year,)
        v = r.get(value_col)
        if v is None:
            out.setdefault(k, None)
            continue
        out[k] = (out.get(k) or 0.0) + v
    return [dict(zip(list(key_cols) + ["year", value_col], list(k) + [v]))
            for k, v in sorted(out.items(), key=lambda kv: tuple(str(x) for x in kv[0]))]


def fetch(url, timeout=600):
    last = None
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # retried, then raised
            last = exc
            time.sleep(30)
    raise last


def strings(df, pl):
    casts = [pl.col(c).cast(pl.String) for c, dt in df.schema.items()
             if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical]
    return df.with_columns(casts) if casts else df


def pudl_rows(name, filt, pl, tmp, info):
    """Downloads one nightly table to a temp file, scans it lazily and returns the rows
    filt(lazyframe, schema) keeps, as dicts."""
    raw, headers = fetch(NIGHTLY % name)
    info[name] = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                  "last_modified": headers.get("Last-Modified")}
    path = os.path.join(tmp, name + ".parquet")
    with open(path, "wb") as fh:
        fh.write(raw)
    del raw
    lf = pl.scan_parquet(path)
    schema = lf.collect_schema()
    info[name]["columns"] = list(schema.names())
    df = strings(filt(lf, schema).collect(), pl)
    os.remove(path)
    return df.to_dicts()


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwelk.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}, "errors": {}}
    tmp = tempfile.mkdtemp()

    def save():
        with open(os.path.join(a.out_dir, "xwelk.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def plant_eia(lf, schema):
        return lf.filter(pl.col("plant_id_eia").cast(pl.Int64).is_in(list(PLANTS)))

    def xw(lf, schema):
        cond = pl.col("plant_id_eia").cast(pl.Int64).is_in(list(PLANTS))
        cond = cond | pl.col("plant_id_epa").cast(pl.Int64).is_in(list(PLANTS))
        return lf.filter(cond)

    def ops(lf, schema):
        return lf.filter(pl.col("plant_id_epa").cast(pl.Int64).is_in(list(PLANTS)))

    def g923(lf, schema):
        cols = [c for c in ("plant_id_eia", "generator_id", "report_date", "net_generation_mwh")
                if c in schema.names()]
        return plant_eia(lf, schema).select(cols)

    for key, name, filt in (("eia860_generators", GEN_TABLE, plant_eia),
                            ("crosswalk_links", XW_TABLE, xw),
                            ("cems_operational", OPS_TABLE, ops),
                            ("eia923_monthly", G923_TABLE, g923)):
        try:
            res[key] = pudl_rows(name, filt, pl, tmp, res["downloads"])
        except Exception as exc:
            res["errors"][key] = "%s: %s" % (type(exc).__name__, exc)
        save()
    if res.get("eia923_monthly"):
        res["eia923_yearly"] = yearly_sum(res.pop("eia923_monthly"),
                                          ("plant_id_eia", "generator_id"), "report_date",
                                          "net_generation_mwh")
    try:
        raw, headers = fetch(EPA_CSV)
        res["downloads"]["epa_eia_crosswalk.csv"] = {
            "commit": EPA_SHA, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest()}
        res["epa_crosswalk"] = epa_rows(raw.decode("utf-8-sig", "replace"))
    except Exception as exc:
        res["errors"]["epa_crosswalk"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    save()
    for key in ("eia860_generators", "crosswalk_links", "cems_operational"):
        rows = res.get(key) or []
        if rows:
            path = os.path.join(a.out_dir, "xwelk_%s.csv" % key)
            cols = sorted({c for r in rows for c in r})
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for r in rows:
                    w.writerow(r)
    summary = {k: (len(v) if isinstance(v, list) else v) for k, v in res.items()
               if k not in ("epa_crosswalk",)}
    summary["epa_plant_rows"] = res.get("epa_crosswalk", {}).get("plant_rows")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
