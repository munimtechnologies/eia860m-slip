"""easeyx2.py - do EPA's public CAMPD facility bulk files also give the EPA (CAMD) attributes of
the 2024 EPA-EIA crosswalk (state, facility name, nameplate capacity, fuel, coordinates), and can
the 390 retirements they never date be dated from the last year a unit appears?
Pre-registration easeyx-2 (docs/easeyx2-plan.md in munimtechnologies/eia860m-slip).

Builds on easeyx.py 0.1.0 (easeyx-1, docs/easeyx.md): same reference (pinned commit), same
yearly files 2010-2024, same keys (plant id, unit id, generator id), same history. Only measures.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import easeyx as E  # noqa: E402

VERSION = "0.1.0"
FIRST_YEAR = 2010
LAST_YEAR = 2024
REF_MD5 = "106d813fd9b850f11a0be088f317ef13"
EASEYX1_MD5 = {
    2010: "e7a10a3a95a80045b070c6276086c89b", 2011: "5d7a2801605f65073f6373f8ba7b73f9",
    2012: "46032fc3d24cd5797ce91daac01226d9", 2013: "1e3d0e0d9025dc1f68bd1c08721c5b2d",
    2014: "ae8eadf517e77cebb257e9d6088a3af5", 2015: "e8146001fa3b73d6756e727baeb5950e",
    2016: "5ee1bbd5e9826eeaf328b3c7dca482a1", 2017: "0c08441c8773f6323fbd1132ab7e9ca3",
    2018: "82edba1e4cdd67178d0f320c7422bb96", 2019: "1f6126ae675b1921ba3d0cd6b40caa78",
    2020: "84bb601a65ae8310cfcfabf02e9f4426", 2021: "09395bdcf443ba3f1fefa3ab119e27c0",
    2022: "6fba4d434ff284dcc264fe34c036aa5f", 2023: "8737dcdcbcf4313bb15ad8ef8aa6632b",
    2024: "beb9e5f4a92a7d8c28b8eb0d59ca8c11",
}
ATTR_COLS = ("CAMD_STATE", "CAMD_FACILITY_NAME", "CAMD_NAMEPLATE_CAPACITY", "CAMD_FUEL_TYPE",
             "CAMD_LATITUDE", "CAMD_LONGITUDE")
ATTRS = ("state", "facility_name", "capacity", "fuel", "coords")

# Gates and bars (docs/easeyx2-plan.md)
G1_MIN_ROWS = 7000
G1_MAX_ROWS = 7400
G3_MIN_FOUND = 6900
G3_SILENT_MIN = 300
G3_SILENT_MAX = 500
CAP_TOL = 0.05
COORD_TOL = 0.001
P1_MIN = 0.99
P2_MIN = 0.90
P3_MIN = 0.90
P4_MIN = 0.90
P5_MIN = 0.90
P6_MIN = 0.85
EPS = 1e-9


def fnum(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def norm_text(value):
    """Lower case, runs of whitespace to one space, stripped."""
    return " ".join((value or "").split()).lower()


def read_reference_attrs(text):
    """Returns (info, ref) with ref = {key: record}; the first row of a repeated key is kept."""
    reader = csv.DictReader(io.StringIO(text))
    cols = reader.fieldnames or []
    need = tuple(E.REF_COLS) + ATTR_COLS
    info = {"rows": 0, "missing_cols": [c for c in need if c not in cols]}
    ref = {}
    if info["missing_cols"]:
        info["keys"] = 0
        return info, ref

    def g(row, name):
        return (row.get(name) or "").strip()

    for row in reader:
        info["rows"] += 1
        p, u = E.plant_key(row.get("CAMD_PLANT_ID")), E.id_key(row.get("CAMD_UNIT_ID"))
        if not p or not u:
            continue
        key = (p, u, E.id_key(row.get("CAMD_GENERATOR_ID")))
        if key in ref:
            continue
        ref[key] = {"status": g(row, "CAMD_STATUS"), "status_date": g(row, "CAMD_STATUS_DATE"),
                    "retire_year": E.int_or0(row.get("CAMD_RETIRE_YEAR")),
                    "state": g(row, "CAMD_STATE"), "facility_name": g(row, "CAMD_FACILITY_NAME"),
                    "capacity": g(row, "CAMD_NAMEPLATE_CAPACITY"), "fuel": g(row, "CAMD_FUEL_TYPE"),
                    "latitude": g(row, "CAMD_LATITUDE"), "longitude": g(row, "CAMD_LONGITUDE")}
    info["keys"] = len(ref)
    return info, ref


def compare(attr, ref_rec, file_rec):
    """True (same), False (differs) or None (one side empty or unreadable)."""
    if attr == "state":
        a = (ref_rec.get("state") or "").strip().upper()
        b = (file_rec.get("state") or "").strip().upper()
        return None if not a or not b else a == b
    if attr in ("facility_name", "fuel"):
        a, b = norm_text(ref_rec.get(attr)), norm_text(file_rec.get(attr))
        return None if not a or not b else a == b
    if attr == "capacity":
        a, b = fnum(ref_rec.get("capacity")), fnum(file_rec.get("capacity"))
        return None if a is None or b is None else abs(a - b) <= CAP_TOL + EPS
    if attr == "coords":
        vals = [fnum(ref_rec.get("latitude")), fnum(ref_rec.get("longitude")),
                fnum(file_rec.get("latitude")), fnum(file_rec.get("longitude"))]
        if any(v is None for v in vals):
            return None
        return (abs(vals[0] - vals[2]) <= COORD_TOL + EPS
                and abs(vals[1] - vals[3]) <= COORD_TOL + EPS)
    raise ValueError(attr)


def show(attr, rec):
    if attr == "coords":
        return "%s;%s" % (rec.get("latitude", ""), rec.get("longitude", ""))
    v = rec.get(attr)
    return "" if v is None else str(v)


def compare_all(ref, hist):
    """Compares each reference key found in the files with its latest-year file row."""
    counts = {a: Counter() for a in ATTRS}
    by_status = {a: Counter() for a in ATTRS}
    fuel_pairs = Counter()
    rows = []
    for key in sorted(set(ref) & set(hist)):
        entry = hist[key]
        last = entry["years"][-1]
        rec = entry["by_year"][last]
        group = "OPR" if ref[key]["status"] == "OPR" else "RET_LTCS"
        for a in ATTRS:
            res = compare(a, ref[key], rec)
            tag = "na" if res is None else ("match" if res else "differ")
            counts[a][tag] += 1
            by_status[a][group + "|" + tag] += 1
            if res is False:
                other = [y for y in entry["years"]
                         if compare(a, ref[key], entry["by_year"][y]) is True]
                if other:
                    counts[a]["differ_other_year_matches"] += 1
                if a == "fuel":
                    fuel_pairs["%s -> %s" % (ref[key]["fuel"], (rec.get("fuel") or "").strip())] += 1
                rows.append([key[0], key[1], key[2], ref[key]["status"], a, show(a, ref[key]),
                             show(a, rec), last, "|".join(map(str, other))])
    return counts, by_status, fuel_pairs, rows


def silent_ret(ref, hist):
    """Reference RET keys found in the files whose derived retirement year (easeyx-1) is 0."""
    out = []
    for key in sorted(set(ref) & set(hist)):
        if ref[key]["status"] != "RET":
            continue
        d = E.derive(hist[key])
        if d["retire_year"]:
            continue
        out.append({"key": key, "ref_retire_year": ref[key]["retire_year"],
                    "ref_status_date": ref[key]["status_date"], "last_year": d["latest_year"],
                    "years": list(hist[key]["years"]), "latest_class": d["latest_class"],
                    "latest_status": d["latest_status"]})
    return out


def diff_tag(d):
    if d < -1:
        return "<-1"
    if d > 2:
        return ">+2"
    return "%+d" % d if d else "0"


def score(ref, hist):
    counts, by_status, fuel_pairs, rows = compare_all(ref, hist)
    m = {"keys_compared": len(set(ref) & set(hist))}
    for a in ATTRS:
        c = counts[a]
        m[a] = {"match": c["match"], "differ": c["differ"], "not_comparable": c["na"],
                "share": E.share(c["match"], c["match"] + c["differ"]),
                "differ_other_year_matches": c["differ_other_year_matches"]}
    silent = silent_ret(ref, hist)
    dated = [s for s in silent if s["ref_retire_year"]]
    in_set = sum(s["ref_retire_year"] in (s["last_year"], s["last_year"] + 1) for s in dated)
    m["silent"] = {
        "keys": len(silent), "ref_retire_year_0": len(silent) - len(dated), "dated": len(dated),
        "ref_year_is_last_or_next": in_set, "share": E.share(in_set, len(dated)),
        "ref_year_is_last": sum(s["ref_retire_year"] == s["last_year"] for s in dated),
        "ref_year_is_next": sum(s["ref_retire_year"] == s["last_year"] + 1 for s in dated),
        "ref_minus_last": dict(sorted(Counter(diff_tag(s["ref_retire_year"] - s["last_year"])
                                              for s in dated).items())),
        "by_last_year": {str(y): n for y, n in sorted(Counter(s["last_year"] for s in silent).items())},
        "by_latest_class": dict(Counter(s["latest_class"] for s in silent)),
    }

    def ok(value, bar):
        return value is not None and value >= bar

    scores = {"P1": ok(m["state"]["share"], P1_MIN),
              "P2": ok(m["facility_name"]["share"], P2_MIN),
              "P3": ok(m["capacity"]["share"], P3_MIN),
              "P4": ok(m["fuel"]["share"], P4_MIN),
              "P5": ok(m["coords"]["share"], P5_MIN),
              "P6": ok(m["silent"]["share"], P6_MIN)}
    rep = {"by_status": {a: dict(sorted(by_status[a].items())) for a in ATTRS},
           "fuel_pairs_top25": dict(fuel_pairs.most_common(25)),
           "retire_year_rules": retire_rules(ref, hist)}
    return m, scores, rep, rows, silent


def retire_rules(ref, hist):
    """Reported: for reference RET keys with a retirement year, exact matches under three rules."""
    n = r0 = r1 = r2 = 0
    for key in set(ref) & set(hist):
        if ref[key]["status"] != "RET" or not ref[key]["retire_year"]:
            continue
        n += 1
        d = E.derive(hist[key])
        want = ref[key]["retire_year"]
        r0 += d["retire_year"] == want
        r1 += (d["retire_year"] or d["latest_year"]) == want
        r2 += (d["retire_year"] or d["latest_year"] + 1) == want
    return {"ref_ret_keys_dated": n, "derived_only": r0, "derived_else_last_year": r1,
            "derived_else_last_year_plus_1": r2}


def gates(ref_info, infos, ref, hist, found_min=G3_MIN_FOUND,
          silent_range=(G3_SILENT_MIN, G3_SILENT_MAX)):
    g1 = (not ref_info["missing_cols"]) and G1_MIN_ROWS <= ref_info["rows"] <= G1_MAX_ROWS
    g2 = all(y in infos and not infos[y].get("missing_cols") and not infos[y].get("error")
             for y in range(FIRST_YEAR, LAST_YEAR + 1))
    found = len(set(ref) & set(hist))
    nsilent = len(silent_ret(ref, hist))
    g3 = found >= found_min and silent_range[0] <= nsilent <= silent_range[1]
    return ({"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)},
            {"ref_rows": ref_info["rows"], "found": found, "silent": nsilent})


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
    res = {"tool": "easeyx2.py " + VERSION + " (easeyx.py " + E.VERSION + ")",
           "python": sys.version.split()[0], "started": E.now(), "reference": {"url": E.REF_URL},
           "downloads": {}}
    raw, how = E.fetch(E.REF_URL, os.path.join(a.data_dir, "epa_eia_crosswalk_" + E.REF_SHA[:7] + ".csv"))
    md5 = hashlib.md5(raw).hexdigest()
    res["reference"].update({"bytes": len(raw), "md5": md5, "how": how,
                             "same_as_easeyx1": md5 == REF_MD5})
    ref_info, ref = read_reference_attrs(raw.decode("utf-8-sig", "replace"))
    res["reference"].update(ref_info)
    files, infos = {}, {}
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        url = E.BULK_URL.format(year=year)
        try:
            body, how = E.fetch(url, os.path.join(a.data_dir, "facility-%d.csv" % year))
        except RuntimeError as exc:
            infos[year] = {"year": year, "error": str(exc)}
            res["downloads"][str(year)] = {"url": url, "error": str(exc)}
            continue
        md5 = hashlib.md5(body).hexdigest()
        res["downloads"][str(year)] = {"bytes": len(body), "md5": md5, "how": how,
                                       "same_as_easeyx1": md5 == EASEYX1_MD5[year]}
        info, recs = E.read_facility(body.decode("utf-8-sig", "replace"), year)
        infos[year], files[year] = info, recs
        print(year, "rows", info["rows"], "keys", info.get("keys"), how,
              "same md5" if md5 == EASEYX1_MD5[year] else "NEW md5")
    hist = E.build_history(files)
    g, gm = gates(ref_info, infos, ref, hist)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    if all(g.values()):
        m, scores, rep, rows, silent = score(ref, hist)
        res["measures"], res["scores"], res["reported"] = m, dict(g, **scores), rep
        write_csv(os.path.join(a.out_dir, "easeyx2-attribute-differences.csv"),
                  ["plant_id", "unit_id", "generator_id", "ref_status", "attribute", "ref_value",
                   "file_value", "file_year", "years_matching_ref"], rows)
        write_csv(os.path.join(a.out_dir, "easeyx2-silent-retirements.csv"),
                  ["plant_id", "unit_id", "generator_id", "ref_retire_year", "ref_status_date",
                   "last_year_in_files", "years_in_files", "latest_status"],
                  [[s["key"][0], s["key"][1], s["key"][2], s["ref_retire_year"],
                    s["ref_status_date"], s["last_year"], "|".join(map(str, s["years"])),
                    s["latest_status"]] for s in silent])
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = E.now()
    with open(os.path.join(a.out_dir, "easeyx2.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
