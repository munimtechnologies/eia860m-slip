"""xwpudl: pre-registered check xwpudl-1 (plan: docs/xwpudl-plan.md in
munimtechnologies/eia860m-slip).

docs/step1d-look.md found four leads in EPA's CAMD-EIA crosswalk file (commit 3c7d672): CAMD
generators linked by step 1d ("remove leading letters") to an EIA generator of very different
size, while a generator of about the same size, which no crosswalk row links, sits under the same
or another EIA plant. PUDL publishes its own yearly runs of EPA's crosswalk
(core_epa__assn_eia_epacamd, report years 2018 on). This script reads, for every report year in
PUDL's table:

- which EIA generators each lead's CAMD generators are linked to;
- whether any row of that year links the lead's candidate EIA generator;
- whether PUDL's EIA-860 generator table (core_eia860__scd_generators) lists the candidate that
  year, with its nameplate capacity, prime mover and status;

and scores the plan's gate and predictions.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
XW_TABLE = "core_epa__assn_eia_epacamd"
GEN_TABLE = "core_eia860__scd_generators"
XW_COLS = ["report_year", "plant_id_epa", "emissions_unit_id_epa", "generator_id_epa",
           "plant_id_eia", "generator_id"]
GEN_COLS = ["plant_id_eia", "generator_id", "report_date", "capacity_mw", "prime_mover_code",
            "operational_status_code"]
UA = {"User-Agent": "mv2-xwpudl/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}
MIN_NEWEST = 2023
MIN_P4_CELLS = 10
P5_YEAR = 2021

# name, CAMD plant, {CAMD generator: (EIA plant, EIA generator) it is linked to in EPA's file},
# candidate EIA generators (no row of EPA's file links them).
LEADS = (
    ("Antelope Elk", 57865, {"ELK1": (57865, "E01"), "ELK2": (57865, "E02"),
                             "ELK3": (57865, "E03")},
     ((58835, "ELK1"), (58835, "ELK2"), (58835, "ELK3"))),
    ("Chalk Point", 1571, {"SGT1": (1571, "GT1")}, ((61890, "SGT1"),)),
    ("Glenarm", 422, {"STG5": (422, "GT5")}, ((422, "ST1"),)),
    ("LEPA Unit No. 1", 58478, {"STG1": (58478, "LEPA1")}, ((58478, "LEPA2"),)),
)
PREDICTED = {"P1": "Chalk Point", "P2": "Glenarm", "P3": "LEPA Unit No. 1"}
NEW_CANDIDATES = ((61890, "SGT1"), (422, "ST1"), (58478, "LEPA2"))


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


def index_links(rows):
    """rows: dicts with XW_COLS. Returns ({year: {(epa plant, epa gen): set of (eia plant,
    eia gen)}}, {year: set of linked (eia plant, eia gen)}, {year: set of epa plants})."""
    by_gen, linked, plants = {}, {}, {}
    for r in rows:
        y, pe, pi = pint(r.get("report_year")), pint(r.get("plant_id_epa")), pint(
            r.get("plant_id_eia"))
        ge, gi = gid(r.get("generator_id_epa")), gid(r.get("generator_id"))
        if y is None:
            continue
        if pe is not None:
            plants.setdefault(y, set()).add(pe)
        if pi is not None and gi:
            linked.setdefault(y, set()).add((pi, gi))
            if pe is not None and ge:
                by_gen.setdefault(y, {}).setdefault((pe, ge), set()).add((pi, gi))
    return by_gen, linked, plants


def lead_year(lead, by_gen_y, linked_y):
    """Status of one lead in one report year."""
    name, plant, wrong, cands = lead
    links = {g: sorted(by_gen_y.get((plant, g), set())) for g in sorted(wrong)}
    found = all(links[g] for g in wrong)
    wrong_all = found and all(wrong[g] in links[g] for g in wrong)
    to_cand = any(c in links[g] for g in wrong for c in cands)
    cand_linked = sorted(c for c in cands if c in linked_y)
    return {"links": {g: ["%s/%s" % t for t in v] for g, v in links.items()},
            "camd_gens_found": found, "linked_to_flagged": wrong_all,
            "camd_gen_to_candidate": to_cand,
            "candidates_linked": ["%s/%s" % c for c in cand_linked],
            "persists": bool(wrong_all and not cand_linked)}


def index_gens(rows, keys):
    """rows: dicts with GEN_COLS (report_date as a date or 'YYYY-..' text). Returns
    {(plant, gen): {year: {"cap", "pm", "status"}}} for the keys asked."""
    want = set(keys)
    out = {k: {} for k in keys}
    for r in rows:
        k = (pint(r.get("plant_id_eia")), gid(r.get("generator_id")))
        if k not in want:
            continue
        d = r.get("report_date")
        y = getattr(d, "year", None) or pint(str(d)[:4])
        if y is None:
            continue
        cap = r.get("capacity_mw")
        cap = None if cap is None or cap != cap else float(cap)
        prev = out[k].get(y)
        if prev is None or (prev["cap"] is None and cap is not None):
            out[k][y] = {"cap": cap, "pm": r.get("prime_mover_code"),
                         "status": r.get("operational_status_code")}
    return out


def score(res):
    s = {}
    g1 = res.get("g1")
    if not g1:
        return s
    s["G1"] = bool(g1["missing_cols"] == [] and g1["newest"] is not None
                   and g1["newest"] >= MIN_NEWEST and g1["plants_in_newest"] == 4)
    if not s["G1"]:
        return s
    newest = str(g1["newest"])
    leads = res.get("leads") or {}
    for p, name in PREDICTED.items():
        if newest in leads.get(name, {}):
            s[p] = bool(leads[name][newest]["persists"])
    p4 = res.get("p4")
    if p4 and p4["cells"] >= MIN_P4_CELLS:
        s["P4"] = p4["linked"] == 0
    p5 = res.get("p5")
    if p5:
        s["P5"] = all(p5[k] for k in p5)
    return s


def p4_cells(leads_by_year, gens, years):
    cells = linked = 0
    rows = []
    for name, plant, wrong, cands in LEADS:
        for c in cands:
            for y in years:
                info = gens.get(c, {}).get(y)
                if not info or info["cap"] is None or info["cap"] <= 0:
                    continue
                cells += 1
                hit = "%s/%s" % c in leads_by_year[name][str(y)]["candidates_linked"]
                linked += hit
                rows.append({"lead": name, "candidate": "%s/%s" % c, "year": y,
                             "cap": info["cap"], "pm": info["pm"], "status": info["status"],
                             "linked": hit})
    return {"cells": cells, "linked": linked, "rows": rows}


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


def load(name, cols, pl):
    raw, headers = fetch(NIGHTLY % name)
    try:
        schema = dict(pl.read_parquet_schema(io.BytesIO(raw)))
    except AttributeError:
        schema = dict(pl.scan_parquet(io.BytesIO(raw)).collect_schema())
    have = [c for c in cols if c in schema]
    df = pl.read_parquet(io.BytesIO(raw), columns=have)
    casts = [pl.col(c).cast(pl.String) for c, dt in df.schema.items()
             if isinstance(dt, (pl.Categorical, pl.Enum)) or dt == pl.Categorical]
    if casts:
        df = df.with_columns(casts)
    info = {"bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(), "rows": df.height,
            "last_modified": headers.get("Last-Modified"),
            "missing_cols": [c for c in cols if c not in schema]}
    return df, info


def main(argv=None):
    import polars as pl
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "xwpudl.py " + VERSION, "python": sys.version.split()[0],
           "polars": pl.__version__, "started": now(), "downloads": {}}

    def save():
        res["scores"] = score(res)
        with open(os.path.join(a.out_dir, "xwpudl.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)

    try:
        xw, res["downloads"][XW_TABLE] = load(XW_TABLE, XW_COLS, pl)
        plants = sorted({l[1] for l in LEADS})
        eia_plants = sorted({t[0] for l in LEADS for t in list(l[2].values()) + list(l[3])})
        sub = xw.filter(pl.col("plant_id_epa").cast(pl.Int64).is_in(plants)
                        | pl.col("plant_id_eia").cast(pl.Int64).is_in(eia_plants))
        rows = xw.to_dicts()
        by_gen, linked, plants_by_year = index_links(rows)
        years = sorted(linked)
        newest = years[-1] if years else None
        res["years"] = years
        res["rows_by_year"] = {str(y): sum(len(v) for v in by_gen.get(y, {}).values())
                               for y in years}
        res["g1"] = {"missing_cols": res["downloads"][XW_TABLE]["missing_cols"],
                     "newest": newest,
                     "plants_in_newest": sum(1 for p in plants
                                             if p in plants_by_year.get(newest, set()))}
        res["subset_rows"] = sorted(
            ({k: (str(v) if v is not None else "") for k, v in r.items()}
             for r in sub.to_dicts()),
            key=lambda r: (r.get("report_year", ""), r.get("plant_id_epa", ""),
                           r.get("emissions_unit_id_epa", ""), r.get("generator_id_epa", "")))
        res["leads"] = {l[0]: {str(y): lead_year(l, by_gen.get(y, {}), linked.get(y, set()))
                               for y in years} for l in LEADS}
        del xw, rows
        gens_df, res["downloads"][GEN_TABLE] = load(GEN_TABLE, GEN_COLS, pl)
        keys = [c for l in LEADS for c in l[3]] + [t for l in LEADS for t in l[2].values()]
        gsub = gens_df.filter(pl.col("plant_id_eia").cast(pl.Int64).is_in(eia_plants))
        gens = index_gens(gsub.to_dicts(), keys)
        res["eia860"] = {"%s/%s" % k: {str(y): v for y, v in sorted(d.items())}
                         for k, d in gens.items()}
        res["p4"] = p4_cells(res["leads"], gens, years)
        res["p5"] = {"%s/%s" % k: bool(gens.get(k, {}).get(P5_YEAR, {}).get("cap"))
                     for k in NEW_CANDIDATES}
        elk = res["leads"]["Antelope Elk"].get("2024")
        res["sanity_elk_2024_persists"] = bool(elk and elk["persists"])
    except Exception as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["finished"] = now()
    save()
    print(json.dumps({k: v for k, v in res.items() if k not in ("subset_rows", "leads",
                                                                "eia860", "p4")},
                     indent=1, default=str))
    print(json.dumps(res.get("p4"), indent=1, default=str))
    for name, by_year in res.get("leads", {}).items():
        for y, st in by_year.items():
            print(name, y, json.dumps(st, default=str))


if __name__ == "__main__":
    main()
