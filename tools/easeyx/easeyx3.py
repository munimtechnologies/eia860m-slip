"""easeyx3.py - can the published 2024 EPA-EIA crosswalk be carried forward to EPA's 2025 file, and
how far does the crosswalk's simplest rule (same plant id and generator id on both sides) go?
Pre-registration easeyx-3 (docs/easeyx3-plan.md in munimtechnologies/eia860m-slip).

Builds on easeyx.py 0.1.0 (easeyx-1, docs/easeyx.md) and its published 2010-2025 EPA-side build
(data/easeyx-epa-side-2025.csv). EIA side: PUDL's nightly core_eia860__scd_generators table.
Only measures; links nothing for anyone.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import easeyx as E  # noqa: E402

VERSION = "0.1.0"
REF_MD5 = "106d813fd9b850f11a0be088f317ef13"
SIDE_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/"
            "data/easeyx-epa-side-2025.csv")
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
GEN_TABLE = "core_eia860__scd_generators"
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "operational_status_code"]
GEN_NEED = ("plant_id_eia", "generator_id", "report_date")
REF_NEED = ("CAMD_PLANT_ID", "CAMD_UNIT_ID", "CAMD_GENERATOR_ID", "CAMD_STATUS",
            "EIA_PLANT_ID", "EIA_GENERATOR_ID", "MATCH_TYPE_GEN")
SIDE_COLS = ("plant_id", "unit_id", "generator_id", "latest_class", "first_year", "latest_year")
BLANKS = ("", "NA", "NAN", "NONE", "NULL")

# Gates and bars (docs/easeyx3-plan.md)
G2_SIDE_ROWS = 7187
G3_MIN_PAIRS = 20000
G3_YEAR = 2024
NEW_YEAR = 2025
P1_MIN = 0.90
P2_MIN = 0.80
P3_MIN = 0.95
P4_MIN = 0.60
P5_MIN_KEYS = 10


def blank(value):
    return value is None or str(value).strip().upper() in BLANKS


def gen_key(value):
    """Generator id for matching across EPA and EIA: stripped, upper case; blank -> ''."""
    return "" if blank(value) else str(value).strip().upper()


def plant(value):
    return "" if blank(value) else E.plant_key(str(value))


def pair(key):
    """The exact-id candidate of a CAMD key: (CAMD plant id, CAMD generator id)."""
    return (key[0], gen_key(key[2]))


def read_reference_links(text):
    """Returns (info, ref) with ref = {key: {status, links: set of (EIA plant, EIA generator),
    match_types: set}} over every row of the key."""
    reader = csv.DictReader(io.StringIO(text))
    cols = reader.fieldnames or []
    info = {"rows": 0, "missing_cols": [c for c in REF_NEED if c not in cols]}
    ref = {}
    if info["missing_cols"]:
        info["keys"] = info["linked_keys"] = 0
        return info, ref
    for row in reader:
        info["rows"] += 1
        p, u = E.plant_key(row.get("CAMD_PLANT_ID")), E.id_key(row.get("CAMD_UNIT_ID"))
        if not p or not u:
            continue
        key = (p, u, E.id_key(row.get("CAMD_GENERATOR_ID")))
        rec = ref.setdefault(key, {"status": (row.get("CAMD_STATUS") or "").strip(),
                                   "links": set(), "match_types": set()})
        ep, eg = plant(row.get("EIA_PLANT_ID")), gen_key(row.get("EIA_GENERATOR_ID"))
        if ep and eg:
            rec["links"].add((ep, eg))
        mt = (row.get("MATCH_TYPE_GEN") or "").strip()
        if not blank(mt):
            rec["match_types"].add(mt)
    info["keys"] = len(ref)
    info["linked_keys"] = sum(1 for r in ref.values() if r["links"])
    info["multi_link_keys"] = sum(1 for r in ref.values() if len(r["links"]) > 1)
    return info, ref


def read_side(text):
    """easeyx-1's EPA-side build (one row per key). Returns (info, side)."""
    reader = csv.DictReader(io.StringIO(text))
    cols = reader.fieldnames or []
    info = {"rows": 0, "missing_cols": [c for c in SIDE_COLS if c not in cols]}
    side = {}
    if info["missing_cols"]:
        info["keys"] = 0
        return info, side
    for row in reader:
        info["rows"] += 1
        key = (E.plant_key(row.get("plant_id")), E.id_key(row.get("unit_id")),
               E.id_key(row.get("generator_id")))
        side[key] = {"latest_class": (row.get("latest_class") or "").strip(),
                     "first_year": E.int_or0(row.get("first_year")),
                     "latest_year": E.int_or0(row.get("latest_year")),
                     "state": (row.get("state") or "").strip(),
                     "facility_name": (row.get("facility_name") or "").strip(),
                     "capacity": (row.get("nameplate_capacity_mw") or "").strip(),
                     "fuel": (row.get("primary_fuel_type") or "").strip()}
    info["keys"] = len(side)
    return info, side


def pudl_pairs(rows):
    """rows: iterable of (plant_id_eia, generator_id, report_date, operational_status_code).
    Returns (pairs, years): pairs = {(plant, generator): {last_year, last_status}}."""
    pairs, years = {}, set()
    for p_raw, g_raw, date, status in rows:
        p, g = plant(p_raw), gen_key(g_raw)
        y = E.int_or0(str(date or "")[:4])
        if y:
            years.add(y)
        if not p or not g:
            continue
        rec = pairs.setdefault((p, g), {"last_year": 0, "last_status": ""})
        if y >= rec["last_year"]:
            rec["last_year"] = y
            rec["last_status"] = "" if blank(status) else str(status).strip().upper()
    return pairs, years


def score(ref, side, pairs):
    m = {}
    cf = Counter()
    for key, s in side.items():
        r = ref.get(key)
        tag = "new" if r is None else ("linked" if r["links"] else "unlinked")
        cf[s["latest_class"] + "|" + tag] += 1
    opr = [k for k, s in side.items() if s["latest_class"] == "OPR"]
    opr_linked = sum(1 for k in opr if k in ref and ref[k]["links"])
    m["carry_forward"] = {"side_keys": len(side), "by_class": dict(sorted(cf.items())),
                          "opr_keys": len(opr), "opr_linked": opr_linked,
                          "share": E.share(opr_linked, len(opr))}

    first25 = sorted(k for k in ref if k in side and side[k]["first_year"] == NEW_YEAR)
    m["ref_first_seen_2025"] = {"ref_keys": len(ref),
                                "ref_keys_not_in_side": sum(1 for k in ref if k not in side),
                                "keys": len(first25),
                                "by_status": dict(sorted(Counter(ref[k]["status"]
                                                                 for k in first25).items()))}

    linked = sorted(k for k in ref if ref[k]["links"])
    same = [k for k in linked if pair(k) in ref[k]["links"]]
    loose_same = [k for k in linked
                  if any(lp == k[0] and E.loose(lg) == E.loose(gen_key(k[2]))
                         for lp, lg in ref[k]["links"])]
    m["exact_in_ref"] = {"linked_keys": len(linked), "same_ids": len(same),
                         "share": E.share(len(same), len(linked)),
                         "same_ids_loose": len(loose_same)}

    cand = [k for k in linked if pair(k) in pairs]
    hit = [k for k in cand if pair(k) in ref[k]["links"]]
    m["exact_precision"] = {"linked_keys_with_pair_in_pudl": len(cand),
                            "ref_links_to_it": len(hit), "share": E.share(len(hit), len(cand))}

    new_opr = sorted(k for k in side if k not in ref and side[k]["latest_class"] == "OPR")
    new_hit = [k for k in new_opr if pair(k) in pairs]
    m["new_opr"] = {"keys": len(new_opr), "pair_in_pudl": len(new_hit),
                    "share": E.share(len(new_hit), len(new_opr)),
                    "by_first_year": dict(sorted(Counter(str(side[k]["first_year"])
                                                         for k in new_opr).items())),
                    "pudl_last_status": dict(sorted(Counter(pairs[pair(k)]["last_status"]
                                                            for k in new_hit).items()))}

    scores = {"P1": ok(m["carry_forward"]["share"], P1_MIN),
              "P2": ok(m["exact_in_ref"]["share"], P2_MIN),
              "P3": ok(m["exact_precision"]["share"], P3_MIN),
              "P4": ok(m["new_opr"]["share"], P4_MIN),
              "P5": m["ref_first_seen_2025"]["keys"] >= P5_MIN_KEYS}

    not_same = [k for k in linked if pair(k) not in ref[k]["links"]]
    mt_all, mt_not_same = Counter(), Counter()
    for k in linked:
        mt_all.update(ref[k]["match_types"] or {""})
    for k in not_same:
        mt_not_same.update(ref[k]["match_types"] or {""})
    rep = {"match_types_linked_top20": dict(mt_all.most_common(20)),
           "match_types_not_same_top20": dict(mt_not_same.most_common(20)),
           "not_same_pair_in_pudl": sum(1 for k in not_same if pair(k) in pairs),
           "not_same_by_status": dict(sorted(Counter(ref[k]["status"] for k in not_same).items())),
           "ref_unlinked_by_status": dict(sorted(Counter(ref[k]["status"] for k in ref
                                                         if not ref[k]["links"]).items())),
           "new_by_class": dict(sorted(Counter(side[k]["latest_class"] for k in side
                                               if k not in ref).items())),
           "ref_first_seen_2025_keys": ["%s|%s|%s" % k for k in first25]}
    return m, scores, rep, not_same, new_opr


def ok(value, bar):
    return value is not None and value >= bar


def gates(ref_md5, ref_info, side_info, gen_info, pairs, years):
    g1 = ref_md5 == REF_MD5 and not ref_info["missing_cols"]
    g2 = not side_info["missing_cols"] and side_info["rows"] == G2_SIDE_ROWS
    g3 = (not [c for c in GEN_NEED if c in gen_info.get("missing_cols", [])]
          and len(pairs) >= G3_MIN_PAIRS and G3_YEAR in years)
    return ({"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)},
            {"ref_md5": ref_md5, "side_rows": side_info["rows"], "pudl_pairs": len(pairs),
             "pudl_years": [min(years), max(years)] if years else []})


def new_rows(ref, side, pairs):
    rows = []
    for k in sorted(k for k in side if k not in ref):
        s = side[k]
        hit = pairs.get(pair(k))
        rows.append([k[0], k[1], k[2], s["state"], s["facility_name"], s["latest_class"],
                     s["first_year"], s["latest_year"], s["capacity"], s["fuel"],
                     "yes" if hit else "no", hit["last_year"] if hit else "",
                     hit["last_status"] if hit else ""])
    return rows


def not_same_rows(ref, not_same, pairs):
    return [[k[0], k[1], k[2], ref[k]["status"],
             "|".join("%s:%s" % lk for lk in sorted(ref[k]["links"])),
             "yes" if pair(k) in pairs else "no",
             " || ".join(sorted(ref[k]["match_types"]))] for k in not_same]


def download(url, tries=4, timeout=600):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=E.UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), dict(resp.headers)
        except Exception as exc:  # noqa: BLE001 - retried, then raised
            last = exc
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("%s: %s" % (url, last))


def load_pudl(pl):
    raw, headers = download(NIGHTLY % GEN_TABLE)
    try:
        schema = list(pl.read_parquet_schema(io.BytesIO(raw)))
    except Exception:  # noqa: BLE001
        schema = pl.read_parquet(io.BytesIO(raw), n_rows=1).columns
    have = [c for c in GEN_COLS if c in schema]
    df = pl.read_parquet(io.BytesIO(raw), columns=have)
    info = {"url": NIGHTLY % GEN_TABLE, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "rows": df.height, "last_modified": headers.get("Last-Modified"),
            "missing_cols": [c for c in GEN_COLS if c not in schema]}
    del raw
    df = df.with_columns([pl.col(c).cast(pl.String) for c in df.columns])
    n = df.height
    cols = [df.get_column(c).to_list() if c in df.columns else [None] * n for c in GEN_COLS]
    return info, zip(*cols)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data/easey-20261109")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    import polars as pl
    res = {"tool": "easeyx3.py " + VERSION + " (easeyx.py " + E.VERSION + ")",
           "python": sys.version.split()[0], "polars": pl.__version__, "started": E.now()}
    raw, how = E.fetch(E.REF_URL, os.path.join(a.data_dir, "epa_eia_crosswalk_" + E.REF_SHA[:7] + ".csv"))
    ref_md5 = hashlib.md5(raw).hexdigest()
    ref_info, ref = read_reference_links(raw.decode("utf-8-sig", "replace"))
    res["reference"] = dict(ref_info, url=E.REF_URL, md5=ref_md5, how=how, bytes=len(raw))
    side_raw, _ = download(SIDE_URL, timeout=120)
    side_info, side = read_side(side_raw.decode("utf-8-sig", "replace"))
    res["side"] = dict(side_info, url=SIDE_URL, md5=hashlib.md5(side_raw).hexdigest(),
                       bytes=len(side_raw))
    gen_info, rows = load_pudl(pl)
    pairs, years = pudl_pairs(rows)
    res["pudl"] = dict(gen_info, pairs=len(pairs))
    g, gm = gates(ref_md5, ref_info, side_info, gen_info, pairs, years)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    if all(g.values()):
        m, scores, rep, not_same, _new_opr = score(ref, side, pairs)
        res["measures"], res["scores"], res["reported"] = m, dict(g, **scores), rep
        write_csv(os.path.join(a.out_dir, "easeyx3-new-keys.csv"),
                  ["plant_id", "unit_id", "generator_id", "state", "facility_name", "latest_class",
                   "first_year", "latest_year", "nameplate_capacity_mw", "primary_fuel_type",
                   "same_ids_in_pudl", "pudl_last_year", "pudl_last_status"],
                  new_rows(ref, side, pairs))
        write_csv(os.path.join(a.out_dir, "easeyx3-ref-not-same-ids.csv"),
                  ["plant_id", "unit_id", "generator_id", "camd_status", "eia_links",
                   "same_ids_in_pudl", "match_types"],
                  not_same_rows(ref, not_same, pairs))
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = E.now()
    with open(os.path.join(a.out_dir, "easeyx3.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
