"""xwdev: pre-registered check xwdev-1 (plan: docs/xwdev-plan.md in
munimtechnologies/eia860m-slip).

docs/step1d-look.md found four leads in EPA's CAMD-EIA crosswalk file on the master branch
(commit 3c7d672, October 2022), and docs/xwpudl.md showed that all four also stand in PUDL's
yearly runs of that crosswalk (2018 to 2024). EPA's repository also has a `development` branch
whose epa_eia_crosswalk.csv was regenerated in June 2025 (commit 2b74eb4) and whose
manual_matches.xlsx was updated in October 2025 (commit 4e2c2b6). This script reads both files
at the pinned development commit and reports, for each lead:

- which EIA generators the lead's CAMD generators are linked to, and the match type;
- whether any row links the lead's candidate EIA generator;
- an outcome: "stands", "fixed", "absent" or "other";

and scores the plan's gate and predictions. It also lists, without scoring, every row of
manual_matches.xlsx that names one of the leads' plant ids.

EPA's files are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
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

VERSION = "0.1.0"
COMMIT = "3423b2ab457222e1eac5d69d25a98b5f62ce5975"
RAW = "https://raw.githubusercontent.com/USEPA/camd-eia-crosswalk/" + COMMIT + "/"
CSV_NAME = "epa_eia_crosswalk.csv"
XLSX_NAME = "manual_matches.xlsx"
UA = {"User-Agent": "mv2-xwdev/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
MIN_ROWS = 4000

# Column names looked for (case-insensitive), first match wins.
REQUIRED = {"epa_plant": ("epa_plant_id", "camd_plant_id"),
            "epa_gen": ("epa_generator_id", "camd_generator_id"),
            "eia_plant": ("eia_plant_id",),
            "eia_gen": ("eia_generator_id",)}
OPTIONAL = {"epa_unit": ("epa_unit_id", "camd_unit_id"),
            "match_gen": ("match_type_gen",)}

# Same leads as tools/xwpudl/xwpudl.py 0.1.0: name, CAMD plant, {CAMD generator: (EIA plant,
# EIA generator) it is linked to in EPA's 2022 file}, candidate EIA generators.
LEADS = (
    ("Antelope Elk", 57865, {"ELK1": (57865, "E01"), "ELK2": (57865, "E02"),
                             "ELK3": (57865, "E03")},
     ((58835, "ELK1"), (58835, "ELK2"), (58835, "ELK3"))),
    ("Chalk Point", 1571, {"SGT1": (1571, "GT1")}, ((61890, "SGT1"),)),
    ("Glenarm", 422, {"STG5": (422, "GT5")}, ((422, "ST1"),)),
    ("LEPA Unit No. 1", 58478, {"STG1": (58478, "LEPA1")}, ((58478, "LEPA2"),)),
)
PREDICTED = {"P1": "Antelope Elk", "P2": "Chalk Point", "P3": "Glenarm",
             "P4": "LEPA Unit No. 1"}
PLANT_IDS = (57865, 58835, 1571, 61890, 422, 58478)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def gid(v):
    """A generator id for comparing: strip and upper-case; 1.0 -> '1'; None/NaN -> ''."""
    if v is None:
        return ""
    if isinstance(v, float):
        if v != v:
            return ""
        if v.is_integer():
            v = int(v)
    return str(v).strip().upper()


def pint(v):
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None


def find_cols(header):
    """Returns ({key: column name as in the header}, [missing required keys])."""
    low = {}
    for h in header or []:
        if h is not None:
            low.setdefault(h.strip().lower(), h)
    found, missing = {}, []
    for key, names in list(REQUIRED.items()) + list(OPTIONAL.items()):
        for n in names:
            if n in low:
                found[key] = low[n]
                break
        else:
            if key in REQUIRED:
                missing.append(key)
    return found, missing


def index_rows(rows, cols):
    """Returns ({(epa plant, epa gen): set of (eia plant, eia gen)}, set of linked (eia plant,
    eia gen), set of epa plants)."""
    by_gen, linked, plants = {}, set(), set()
    for r in rows:
        pe, pi = pint(r.get(cols["epa_plant"])), pint(r.get(cols["eia_plant"]))
        ge, gi = gid(r.get(cols["epa_gen"])), gid(r.get(cols["eia_gen"]))
        if pe is not None:
            plants.add(pe)
        if pi is not None and gi:
            linked.add((pi, gi))
            if pe is not None and ge:
                by_gen.setdefault((pe, ge), set()).add((pi, gi))
    return by_gen, linked, plants


def lead_status(lead, by_gen, linked):
    """stands: every CAMD generator is linked to the EIA generator EPA's 2022 file links it to,
    and no row links any candidate. fixed: every CAMD generator is linked to a candidate and
    none to its 2022 EIA generator. absent: some CAMD generator has no linked row. other: the
    rest."""
    name, plant, wrong, cands = lead
    links = {g: sorted(by_gen.get((plant, g), set())) for g in sorted(wrong)}
    found = all(links[g] for g in wrong)
    to_flagged = found and all(wrong[g] in links[g] for g in wrong)
    cand_linked = sorted(c for c in cands if c in linked)
    fixed = found and all(any(c in links[g] for c in cands) and wrong[g] not in links[g]
                          for g in wrong)
    if not found:
        outcome = "absent"
    elif to_flagged and not cand_linked:
        outcome = "stands"
    elif fixed:
        outcome = "fixed"
    else:
        outcome = "other"
    return {"links": {g: ["%s/%s" % t for t in v] for g, v in links.items()},
            "candidates_linked": ["%s/%s" % c for c in cand_linked],
            "outcome": outcome}


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(not g1["missing_cols"] and g1["rows"] >= MIN_ROWS
                   and g1["plants_present"] == 4)
    if not s["G1"]:
        return s
    leads = res.get("leads") or {}
    for p, name in PREDICTED.items():
        if name in leads:
            s[p] = leads[name]["outcome"] == "stands"
    if all(p in s for p in PREDICTED):
        s["P5"] = all(s[p] for p in PREDICTED)
    return s


def scan_xlsx(raw):
    """Every row of every sheet with a cell equal to one of PLANT_IDS (descriptive only)."""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    out = {"sheets": {}, "hits": []}
    for ws in wb.worksheets:
        n, header = 0, None
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            vals = ["" if v is None else str(v) for v in row]
            if i == 0:
                header = vals
            n += 1
            if i > 0 and any(pint(v) in PLANT_IDS for v in vals if v.strip()):
                out["hits"].append({"sheet": ws.title, "row": i + 1, "values": vals})
        out["sheets"][ws.title] = {"rows": n, "header": header}
    return out


def fetch(url, timeout=300):
    last = None
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:  # retried, then raised
            last = exc
            time.sleep(30)
    raise last


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwdev.py " + VERSION, "python": sys.version.split()[0], "commit": COMMIT,
           "started": now(), "downloads": {}}
    lead_plants = sorted({l[1] for l in LEADS})
    try:
        raw = fetch(RAW + CSV_NAME)
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        header = list(reader.fieldnames or [])
        rows = list(reader)
        res["downloads"][CSV_NAME] = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                                      "rows": len(rows)}
        res["header"] = header
        cols, missing = find_cols(header)
        res["cols"] = cols
        if missing:
            res["g1"] = {"missing_cols": missing, "rows": len(rows), "plants_present": 0}
        else:
            by_gen, linked, plants = index_rows(rows, cols)
            res["g1"] = {"missing_cols": [], "rows": len(rows),
                         "plants_present": sum(1 for p in lead_plants if p in plants)}
            res["leads"] = {l[0]: lead_status(l, by_gen, linked) for l in LEADS}
            if "match_gen" in cols:
                res["match_types"] = {
                    l[0]: {g: sorted({str(r.get(cols["match_gen"]) or "") for r in rows
                                      if pint(r.get(cols["epa_plant"])) == l[1]
                                      and gid(r.get(cols["epa_gen"])) == g})
                           for g in sorted(l[2])}
                    for l in LEADS}
            res["subset_rows"] = [r for r in rows
                                  if pint(r.get(cols["epa_plant"])) in lead_plants
                                  or pint(r.get(cols["eia_plant"])) in PLANT_IDS]
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    try:
        xraw = fetch(RAW + XLSX_NAME)
        res["downloads"][XLSX_NAME] = {"bytes": len(xraw),
                                       "md5": hashlib.md5(xraw).hexdigest()}
        res["manual_matches"] = scan_xlsx(xraw)
    except Exception as exc:
        res["manual_matches_error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    res["scores"] = score(res)
    with open(os.path.join(a.out_dir, "xwdev.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("subset_rows", "header")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
