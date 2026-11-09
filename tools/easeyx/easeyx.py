"""easeyx.py - can the EPA (CAMD) side of the 2024 EPA-EIA crosswalk be rebuilt from EPA's
public CAMPD facility bulk files? Pre-registration easeyx-1 (docs/easeyx-plan.md in
munimtechnologies/eia860m-slip).

Background: catalyst-cooperative/camd-eia-crosswalk-latest#7 ("The FACT API is dead!"). The
2024 crosswalk was built from EPA's FACT API; a first try with EASEY bulk files gave about a
quarter fewer rows for one year and far too many when all years were stacked.

This tool only measures. It downloads the reference 2024 crosswalk (pinned commit) and the
yearly facility files, builds one record per CAMD key (plant id, unit id, generator id), applies
the rule fixed in the plan (rule F) and compares the keys with the reference.

Apache-2.0. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import date

VERSION = "0.1.0"
UA = {"User-Agent": "mv2-easeyx/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
REF_SHA = "e52a3a533f745b98b88f0556473fee0d4cbcf96d"
REF_URL = ("https://raw.githubusercontent.com/catalyst-cooperative/camd-eia-crosswalk-latest/"
           + REF_SHA + "/epa_eia_crosswalk.csv")
BULK_URL = "https://api.epa.gov/easey/bulk-files/facility/facility-{year}.csv"
FIRST_YEAR = 2010
SCORED_LAST = 2024
EXTRA_YEAR = 2025
EARLIEST_RET = 2010
REQUIRED = ("facility_id", "unit_id", "year", "operating_status",
            "commercial_operation_date", "associated_generators_nameplate_capacity_mwe")
OPTIONAL = ("state", "facility_name", "primary_fuel_type", "latitude", "longitude")
REF_COLS = ("CAMD_PLANT_ID", "CAMD_UNIT_ID", "CAMD_GENERATOR_ID", "CAMD_STATUS",
            "CAMD_STATUS_DATE", "CAMD_RETIRE_YEAR")

# Gates and bars (docs/easeyx-plan.md)
G1_MIN_ROWS = 7000
G1_MAX_ROWS = 7400
G3_MIN_ROWS_2024 = 3000
G3_MIN_UNION_SHARE = 0.50
P1_MIN = 0.70
P1_MAX = 0.85
P2_MIN = 0.80
P3_MIN = 0.97
P4_MAX = 0.05
P5_MIN = 0.90

GEN_RE = re.compile(r"([^,()]+?)\s*\(([^()]*)\)")
RET_MDY = re.compile(r"retired\D*?(\d{1,2})/(\d{1,2})/(\d{4})", re.I)
RET_ISO = re.compile(r"retired\D*?(\d{4})-(\d{2})-(\d{2})", re.I)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def norm_col(name):
    """'Associated Generators & Nameplate Capacity (MWe)' -> 'associated_generators_nameplate_capacity_mwe'."""
    return re.sub(r"[^0-9a-z]+", "_", (name or "").strip().lower()).strip("_")


def plant_key(value):
    s = (value or "").strip()
    try:
        f = float(s)
    except ValueError:
        return s
    return str(int(f)) if f == int(f) else s


def id_key(value):
    return (value or "").strip()


def loose(value):
    """Secondary key form (reported only): upper case, leading zeros dropped."""
    s = (value or "").strip().upper()
    return s.lstrip("0") or ("0" if s else "")


def parse_generators(field):
    """'1 (153.1), 2 (153.1)' -> [('1', 153.1), ('2', 153.1)]; empty -> [('', None)]."""
    text = (field or "").strip()
    if not text:
        return [("", None)]
    out = []
    for gid, cap in GEN_RE.findall(text):
        gid = gid.strip().strip(",").strip()
        try:
            c = float(cap)
        except ValueError:
            c = None
        out.append((gid, c))
    return out or [(text, None)]


def status_class(status):
    t = (status or "").lower()
    if "retired" in t:
        return "RET"
    if "cold storage" in t:
        return "LTCS"
    if "future" in t:
        return "FUT"
    if "operating" in t:
        return "OPR"
    return "OTHER"


def retired_year_in(status):
    m = RET_MDY.search(status or "")
    if m:
        return int(m.group(3))
    m = RET_ISO.search(status or "")
    if m:
        return int(m.group(1))
    return None


def parse_day(value):
    s = (value or "").strip()[:10]
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", (value or "").strip())
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return None


def int_or0(value):
    try:
        return int(float((value or "").strip()))
    except ValueError:
        return 0


# ---------- reading ----------

def read_reference(text):
    """Returns (info, ref) with ref = {key: {status, status_date, retire_year}}."""
    reader = csv.DictReader(io.StringIO(text))
    cols = reader.fieldnames or []
    info = {"columns": len(cols), "missing_cols": [c for c in REF_COLS if c not in cols],
            "rows": 0, "rows_no_camd_key": 0, "duplicate_key_rows": 0,
            "keys_conflicting_status": 0}
    ref = {}
    if info["missing_cols"]:
        return info, ref
    for row in reader:
        info["rows"] += 1
        p, u = plant_key(row["CAMD_PLANT_ID"]), id_key(row["CAMD_UNIT_ID"])
        if not p or not u:
            info["rows_no_camd_key"] += 1
            continue
        key = (p, u, id_key(row["CAMD_GENERATOR_ID"]))
        rec = {"status": (row["CAMD_STATUS"] or "").strip(),
               "status_date": (row["CAMD_STATUS_DATE"] or "").strip(),
               "retire_year": int_or0(row["CAMD_RETIRE_YEAR"])}
        if key in ref:
            info["duplicate_key_rows"] += 1
            if ref[key]["status"] != rec["status"]:
                info["keys_conflicting_status"] += 1
            continue
        ref[key] = rec
    info["keys"] = len(ref)
    return info, ref


def read_facility(text, year):
    """Returns (info, records) with records = {key: record} for one yearly file."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    names = [norm_col(h) for h in header]
    idx = {n: i for i, n in enumerate(names)}
    info = {"year": year, "columns": len(names),
            "missing_cols": [c for c in REQUIRED if c not in idx], "rows": 0,
            "duplicate_keys": 0, "status_values": Counter()}
    recs = {}
    if info["missing_cols"]:
        info["status_values"] = {}
        return info, recs

    def get(row, name):
        i = idx.get(name)
        return row[i].strip() if i is not None and i < len(row) else ""

    for row in reader:
        if not row:
            continue
        info["rows"] += 1
        status = get(row, "operating_status")
        info["status_values"][status] += 1
        p, u = plant_key(get(row, "facility_id")), id_key(get(row, "unit_id"))
        for gid, cap in parse_generators(get(row, "associated_generators_nameplate_capacity_mwe")):
            key = (p, u, gid)
            if key in recs:
                info["duplicate_keys"] += 1
                continue
            recs[key] = {"status": status, "cod": get(row, "commercial_operation_date"),
                         "capacity": cap, "fuel": get(row, "primary_fuel_type"),
                         "state": get(row, "state"), "facility_name": get(row, "facility_name"),
                         "latitude": get(row, "latitude"), "longitude": get(row, "longitude")}
    info["status_values"] = dict(info["status_values"].most_common(25))
    info["keys"] = len(recs)
    return info, recs


# ---------- building ----------

def build_history(files):
    """files = {year: records}. Returns {key: {'years': [...], 'by_year': {year: rec}}}."""
    hist = defaultdict(lambda: {"years": [], "by_year": {}})
    for year in sorted(files):
        for key, rec in files[year].items():
            hist[key]["years"].append(year)
            hist[key]["by_year"][year] = rec
    return dict(hist)


def derive(entry):
    """Latest status class and derived retirement year for one key (rule in the plan)."""
    years = entry["years"]
    last = years[-1]
    latest = entry["by_year"][last]["status"]
    dated = [y for y in (retired_year_in(entry["by_year"][yr]["status"]) for yr in years) if y]
    if dated:
        ret = max(dated)
    else:
        first_ret = [yr for yr in years if status_class(entry["by_year"][yr]["status"]) == "RET"]
        ret = first_ret[0] if first_ret else 0
    return {"latest_year": last, "latest_status": latest, "latest_class": status_class(latest),
            "first_year": years[0], "retire_year": ret}


def rule_f(hist):
    """Rule F: every key seen in the files, minus keys whose latest class is FUT and keys with
    a derived retirement year before EARLIEST_RET."""
    keep = {}
    for key, entry in hist.items():
        d = derive(entry)
        if d["latest_class"] == "FUT":
            continue
        if d["retire_year"] and d["retire_year"] < EARLIEST_RET:
            continue
        keep[key] = d
    return keep


def share(a, b):
    return round(a / b, 5) if b else None


# ---------- scoring ----------

def score(ref, files, last_year=SCORED_LAST):
    rkeys = set(ref)
    nr = len(rkeys)
    in_year = set(files.get(last_year, {}))
    hist = build_history({y: r for y, r in files.items() if y <= last_year})
    union = set(hist)
    f = rule_f(hist)
    fkeys = set(f)
    miss1 = rkeys - in_year
    miss1_ret = sum(ref[k]["status"] in ("RET", "LTCS") for k in miss1)
    ret_keys = [k for k in rkeys if ref[k]["status"] == "RET" and k in hist]
    ret_match = sum(derive(hist[k])["retire_year"] == ref[k]["retire_year"] for k in ret_keys)
    sym = len(fkeys ^ rkeys)
    m = {
        "ref_keys": nr,
        "p1_keys_in_last_file": len(rkeys & in_year),
        "p1_share": share(len(rkeys & in_year), nr),
        "p2_missing_from_last_file": len(miss1),
        "p2_missing_ret_or_ltcs": miss1_ret,
        "p2_share": share(miss1_ret, len(miss1)),
        "p3_keys_in_union": len(rkeys & union),
        "p3_share": share(len(rkeys & union), nr),
        "union_keys": len(union),
        "rule_f_keys": len(fkeys),
        "p4_f_minus_ref": len(fkeys - rkeys),
        "p4_ref_minus_f": len(rkeys - fkeys),
        "p4_symmetric_difference": sym,
        "p4_share": share(sym, nr),
        "p5_ref_ret_keys_in_union": len(ret_keys),
        "p5_retire_year_match": ret_match,
        "p5_share": share(ret_match, len(ret_keys)),
    }
    scores = {
        "P1": m["p1_share"] is not None and P1_MIN <= m["p1_share"] <= P1_MAX,
        "P2": m["p2_share"] is not None and m["p2_share"] >= P2_MIN,
        "P3": m["p3_share"] is not None and m["p3_share"] >= P3_MIN,
        "P4": m["p4_share"] is not None and m["p4_share"] <= P4_MAX,
        "P5": m["p5_share"] is not None and m["p5_share"] >= P5_MIN,
    }
    return m, scores, hist, f


def gates(ref_info, file_infos, files, ref, last_year=SCORED_LAST):
    need = range(FIRST_YEAR, last_year + 1)
    g1 = (not ref_info["missing_cols"]) and G1_MIN_ROWS <= ref_info["rows"] <= G1_MAX_ROWS
    g2 = all(y in file_infos and not file_infos[y].get("missing_cols")
             and not file_infos[y].get("error") for y in need)
    union = set()
    for y in need:
        union |= set(files.get(y, {}))
    rows_last = file_infos.get(last_year, {}).get("rows", 0)
    union_share = share(len(set(ref) & union), len(ref)) or 0
    g3 = rows_last >= G3_MIN_ROWS_2024 and union_share >= G3_MIN_UNION_SHARE
    return {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)}, {
        "ref_rows": ref_info["rows"], "rows_last_file": rows_last, "union_share": union_share}


# ---------- reported, not scored ----------

def reported(ref, files, hist, f, last_year=SCORED_LAST):
    rkeys, fkeys = set(ref), set(f)
    out = {}
    units_ref = {(p, u) for p, u, _ in rkeys}
    units_last = {(p, u) for p, u, _ in files.get(last_year, {})}
    units_union = {(p, u) for p, u, _ in hist}
    out["unit_level"] = {"ref_units": len(units_ref),
                         "in_last_file": len(units_ref & units_last),
                         "in_union": len(units_ref & units_union)}
    lref = {(p, loose(u), loose(g)) for p, u, g in rkeys}
    lun = {(p, loose(u), loose(g)) for p, u, g in hist}
    out["loose_keys"] = {"ref": len(lref), "in_union": len(lref & lun)}
    extra = Counter()
    extra_years = Counter()
    for k in fkeys - rkeys:
        extra[f[k]["latest_class"]] += 1
        extra_years[f[k]["latest_year"]] += 1
    out["f_minus_ref_by_latest_class"] = dict(extra)
    out["f_minus_ref_by_latest_year"] = {str(y): n for y, n in sorted(extra_years.items())}
    miss = Counter()
    for k in rkeys - fkeys:
        if k not in hist:
            why = "not_in_files"
        elif derive(hist[k])["latest_class"] == "FUT":
            why = "future"
        else:
            why = "retired_before_%d" % EARLIEST_RET
        miss[(ref[k]["status"], why)] += 1
    out["ref_minus_f"] = {"%s|%s" % k: n for k, n in sorted(miss.items())}
    conf = Counter()
    for k in rkeys & set(hist):
        conf[(ref[k]["status"], derive(hist[k])["latest_class"])] += 1
    out["status_confusion_ref_vs_latest_class"] = {"%s|%s" % k: n for k, n in sorted(conf.items())}
    diffs = Counter()
    last = files.get(last_year, {})
    for k in rkeys & set(last):
        if ref[k]["status"] != "OPR":
            continue
        a, b = parse_day(ref[k]["status_date"]), parse_day(last[k]["cod"])
        if a is None or b is None:
            diffs["unparsed"] += 1
            continue
        d = abs((a - b).days)
        diffs["0" if d == 0 else "1" if d == 1 else "2-7" if d <= 7 else ">7"] += 1
    out["opr_status_date_vs_commercial_operation_days"] = dict(diffs)
    rety = Counter()
    for k in rkeys & set(hist):
        if ref[k]["status"] == "RET":
            dy = derive(hist[k])["retire_year"] - ref[k]["retire_year"]
            rety["0" if dy == 0 else "ref_0" if ref[k]["retire_year"] == 0 else
                 "derived_0" if derive(hist[k])["retire_year"] == 0 else
                 "+1" if dy == 1 else "-1" if dy == -1 else "other"] += 1
    out["ret_retire_year_diff"] = dict(rety)
    return out


# ---------- main ----------

def fetch(url, path, tries=4):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as fh:
            return fh.read(), "cached"
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read()
            with open(path, "wb") as fh:
                fh.write(raw)
            return raw, "downloaded"
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("%s: %s" % (url, last))


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
    res = {"tool": "easeyx.py " + VERSION, "python": sys.version.split()[0], "started": now(),
           "reference": {"url": REF_URL}, "downloads": {}}
    raw = fetch(REF_URL, os.path.join(a.data_dir, "epa_eia_crosswalk_" + REF_SHA[:7] + ".csv"))[0]
    res["reference"].update({"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest()})
    ref_info, ref = read_reference(raw.decode("utf-8-sig", "replace"))
    res["reference"].update(ref_info)
    files, infos = {}, {}
    for year in range(FIRST_YEAR, EXTRA_YEAR + 1):
        url = BULK_URL.format(year=year)
        try:
            body, how = fetch(url, os.path.join(a.data_dir, "facility-%d.csv" % year))
        except RuntimeError as exc:
            infos[year] = {"year": year, "error": str(exc)}
            res["downloads"][str(year)] = {"url": url, "error": str(exc)}
            print(year, "download failed", exc)
            continue
        res["downloads"][str(year)] = {"url": url, "bytes": len(body),
                                       "md5": hashlib.md5(body).hexdigest(), "how": how}
        info, recs = read_facility(body.decode("utf-8-sig", "replace"), year)
        infos[year], files[year] = info, recs
        print(year, "rows", info["rows"], "keys", info.get("keys"), "missing", info["missing_cols"])
    res["files"] = {str(y): i for y, i in sorted(infos.items())}
    g, gm = gates(ref_info, infos, files, ref)
    res["gates"], res["gate_measures"] = g, gm
    print("gates", g, gm)
    if all(g.values()):
        m, scores, hist, f = score(ref, files)
        res["measures"], res["scores"] = m, dict(g, **scores)
        res["reported"] = reported(ref, files, hist, f)
        rkeys = set(ref)
        write_csv(os.path.join(a.out_dir, "easeyx-ref-minus-f-2024.csv"),
                  ["plant_id", "unit_id", "generator_id", "ref_status", "ref_status_date",
                   "ref_retire_year", "years_in_files", "latest_status", "derived_retire_year"],
                  [[k[0], k[1], k[2], ref[k]["status"], ref[k]["status_date"],
                    ref[k]["retire_year"], "|".join(map(str, hist[k]["years"])) if k in hist else "",
                    derive(hist[k])["latest_status"] if k in hist else "",
                    derive(hist[k])["retire_year"] if k in hist else ""]
                   for k in sorted(rkeys - set(f))])
        write_csv(os.path.join(a.out_dir, "easeyx-f-minus-ref-2024.csv"),
                  ["plant_id", "unit_id", "generator_id", "first_year", "latest_year",
                   "latest_status", "latest_class", "derived_retire_year"],
                  [[k[0], k[1], k[2], f[k]["first_year"], f[k]["latest_year"],
                    f[k]["latest_status"], f[k]["latest_class"], f[k]["retire_year"]]
                   for k in sorted(set(f) - rkeys)])
        if EXTRA_YEAR in files:
            hist25 = build_history(files)
            f25 = rule_f(hist25)
            res["reported"]["rule_f_2025"] = {
                "keys": len(f25), "new_vs_2024_rule_f": len(set(f25) - set(f)),
                "dropped_vs_2024_rule_f": len(set(f) - set(f25)),
                "keys_first_seen_2025": sum(d["first_year"] == EXTRA_YEAR for d in f25.values())}
            rows = []
            for k in sorted(f25):
                d = f25[k]
                r = hist25[k]["by_year"][d["latest_year"]]
                rows.append([r["state"], r["facility_name"], k[0], k[1], k[2], r["capacity"],
                             r["fuel"], r["latitude"], r["longitude"], d["latest_status"],
                             d["latest_class"], d["retire_year"], r["cod"], d["first_year"],
                             d["latest_year"]])
            write_csv(os.path.join(a.out_dir, "easeyx-epa-side-2025.csv"),
                      ["state", "facility_name", "plant_id", "unit_id", "generator_id",
                       "nameplate_capacity_mw", "primary_fuel_type", "latitude", "longitude",
                       "latest_status", "latest_class", "derived_retire_year",
                       "commercial_operation_date", "first_year", "latest_year"], rows)
        print("scores", res["scores"])
        print("measures", json.dumps(m))
    else:
        res["scores"] = dict(g)
        print("a gate failed; predictions not scored")
    res["finished"] = now()
    with open(os.path.join(a.out_dir, "easeyx.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
