"""step1d_look: a descriptive follow-up to pre-registration step1d-1 (not pre-registered).

step1d-1 (docs/step1d.md) counted EPA CAMD-EIA crosswalk links whose two nameplate capacities
differ by 1.5 times or more. A size gap flags a link for a person to check; it does not say what
the right link is. For every flagged link (any step, ratio >= 1.5) and every step-1d link whose
two ids start with different letters, this lists what EIA's September 2026 EIA-860M generator
workbook shows:

- the EIA generator the crosswalk links to (sheet, nameplate MW, prime mover, status);
- every generator at the linked EIA plant;
- every EIA generator in the CAMD unit's state whose id is exactly the CAMD generator id;
- "closer candidates": generators from those two lists, other than the linked one, whose
  nameplate is within 1.5 times of the CAMD nameplate, and whether any crosswalk row already
  links each of them.

It sets no bars and scores nothing. A closer candidate is a lead for a person, not a finding.

Uses tools/step1d/step1d.py 0.1.0 (downloaded unchanged) for the crosswalk pairs. EPA's file
and EIA's workbook are downloaded at run time and not stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import argparse
import hashlib
import io
import json
import os
import sys
import time

import step1d as s1

VERSION = "0.1.0"
EIA_URLS = ("https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx",
            "https://www.eia.gov/electricity/data/eia860m/archive/xls/"
            "september_generator2026.xlsx")
WANT = (("plant_id", ("plant id",)), ("plant_name", ("plant name",)),
        ("state", ("plant state",)), ("gen_id", ("generator id",)),
        ("mw", ("nameplate capacity",)), ("pm", ("prime mover",)),
        ("tech", ("technology",)), ("status", ("status",)))
NEAR = 1.5
MAX_AT_PLANT = 60
GROUPS = ("1d far apart", "1d letters differ", "1b/1c far apart", "1a far apart",
          "manual far apart")


def text(v):
    return "" if v is None else str(v).strip()


def norm_gen(v):
    """A generator id for comparing: 1.0 -> '1', ' elk1 ' -> 'ELK1', '01' stays '01'."""
    if v is None:
        return ""
    if isinstance(v, float):
        if v != v:
            return ""
        if v.is_integer():
            v = int(v)
    t = str(v).strip().upper()
    return "" if t in ("NAN", "NA") else t


def plant_int(v):
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None


def find_header(rows, limit=10):
    for i, row in enumerate(rows[:limit]):
        cells = {str(c).strip() for c in row if c is not None}
        if "Plant ID" in cells and "Generator ID" in cells:
            return i
    return None


def column_map(header):
    """{field: column index} for the WANT fields; the first column whose name starts with a
    field's prefix wins."""
    low = [text(c).lower() for c in header]
    out = {}
    for field, prefixes in WANT:
        for i, name in enumerate(low):
            if any(name.startswith(p) for p in prefixes):
                out[field] = i
                break
    return out


def records_from_sheet(name, rows):
    h = find_header(rows)
    if h is None:
        return []
    cols = column_map(rows[h])
    if "plant_id" not in cols or "gen_id" not in cols:
        return []
    out = []
    for row in rows[h + 1:]:
        def cell(field):
            i = cols.get(field)
            return row[i] if i is not None and i < len(row) else None
        p, g = plant_int(cell("plant_id")), norm_gen(cell("gen_id"))
        if p is None or not g:
            continue
        out.append({"sheet": name, "plant": p, "gen": g, "name": text(cell("plant_name")),
                    "state": text(cell("state")).upper(), "mw": s1.number(cell("mw")),
                    "pm": text(cell("pm")), "tech": text(cell("tech")),
                    "status": text(cell("status"))})
    return out


def build_index(records):
    by_plant, by_gen_state = {}, {}
    for r in records:
        by_plant.setdefault(r["plant"], []).append(r)
        by_gen_state.setdefault((r["gen"], r["state"]), []).append(r)
    return by_plant, by_gen_state


def crosswalk_links(rows):
    """(EIA plant, EIA generator) pairs that any crosswalk row links to."""
    out = set()
    for row in rows:
        p, g = plant_int(row.get("EIA_PLANT_ID")), norm_gen(s1.clean_id(row.get("EIA_GENERATOR_ID")))
        if p is not None and g:
            out.add((p, g))
    return out


def camd_rows_by_plant(rows):
    out = {}
    for row in rows:
        plant = s1.clean_id(row.get("CAMD_PLANT_ID"))
        if not plant:
            continue
        out.setdefault(plant, []).append({
            "unit": text(row.get("CAMD_UNIT_ID")), "gen": s1.clean_id(row.get("CAMD_GENERATOR_ID")),
            "mw": s1.number(row.get("CAMD_NAMEPLATE_CAPACITY")),
            "eia_plant": s1.clean_id(row.get("EIA_PLANT_ID")),
            "eia_gen": s1.clean_id(row.get("EIA_GENERATOR_ID")),
            "eia_mw": s1.number(row.get("EIA_NAMEPLATE_CAPACITY")),
            "step": s1.step_of(row.get("MATCH_TYPE_GEN")) or text(row.get("MATCH_TYPE_GEN"))})
    return out


def group_of(p):
    if p["ratio"] >= NEAR:
        return {"1d": "1d far apart", "1b": "1b/1c far apart", "1c": "1b/1c far apart",
                "1a": "1a far apart", "manual": "manual far apart"}.get(p["step"])
    if p["step"] == "1d" and p["prefix_clash"]:
        return "1d letters differ"
    return None


def compact(r):
    return {k: r[k] for k in ("sheet", "plant", "gen", "name", "state", "mw", "pm", "tech",
                              "status")}


def look(p, by_plant, by_gen_state, linked, camd_rows):
    ep, eg = plant_int(p["eia_plant"]), norm_gen(p["eia_gen"])
    cg, st = norm_gen(p["camd_gen"]), text(p["extra"].get("CAMD_STATE")).upper()
    at_plant = by_plant.get(ep, [])
    same_id = [r for r in by_gen_state.get((cg, st), []) if (r["plant"], r["gen"]) != (ep, eg)]
    cands, seen = [], set()
    for r in at_plant + same_id:
        k = (r["plant"], r["gen"])
        if k == (ep, eg) or k in seen:
            continue
        seen.add(k)
        rr = s1.ratio(p["camd_mw"], r["mw"])
        if rr is not None and rr < NEAR:
            c = compact(r)
            c.update({"ratio": round(rr, 3), "linked_by_crosswalk": k in linked,
                      "at_linked_plant": r["plant"] == ep,
                      "same_id_same_state": r["gen"] == cg and r["state"] == st})
            cands.append(c)
    cands.sort(key=lambda c: (c["linked_by_crosswalk"], c["ratio"], c["plant"], c["gen"]))
    out = {k: p[k] for k in ("camd_plant", "camd_gen", "eia_plant", "eia_gen", "step",
                             "camd_mw", "eia_mw", "ratio", "prefix_clash")}
    out["extra"] = p["extra"]
    out["group"] = group_of(p)
    out["linked_in_sep_2026"] = [compact(r) for r in at_plant if r["gen"] == eg]
    out["eia_at_linked_plant"] = [compact(r) for r in
                                  sorted(at_plant, key=lambda r: r["gen"])[:MAX_AT_PLANT]]
    out["eia_at_linked_plant_n"] = len(at_plant)
    out["same_id_same_state"] = [compact(r) for r in same_id]
    out["closer_candidates"] = cands
    out["unlinked_closer_n"] = sum(1 for c in cands if not c["linked_by_crosswalk"])
    out["camd_plant_rows"] = camd_rows.get(p["camd_plant"], [])
    return out


def summarize(looks):
    out = {}
    for g in GROUPS:
        sel = [x for x in looks if x["group"] == g]
        out[g] = {"n": len(sel),
                  "linked_gen_in_sep_2026": sum(1 for x in sel if x["linked_in_sep_2026"]),
                  "with_unlinked_closer": sum(1 for x in sel if x["unlinked_closer_n"] > 0),
                  "with_same_id_same_state": sum(1 for x in sel if x["same_id_same_state"])}
    return out


def fmt_rec(r):
    mw = "?" if r["mw"] is None else ("%g" % r["mw"])
    return "%s/%s %s, %s MW, %s, %s (%s)" % (r["plant"], r["gen"], r["name"], mw,
                                            r["pm"] or "?", r["sheet"], r["status"] or "?")


def markdown(res):
    lines = ["# step1d look (descriptive, not pre-registered)", "",
             "EIA workbook: %s (md5 %s)" % (res["eia"]["url"], res["eia"]["md5"]), ""]
    for g in GROUPS:
        sel = [x for x in res["looks"] if x["group"] == g]
        lines += ["## %s (%d)" % (g, len(sel)), ""]
        for x in sel:
            e = x["extra"]
            lines.append("- %s r=%s: CAMD %s %s unit %s gen %s %g MW -> EIA %s/%s %g MW (%s)" % (
                x["step"], x["ratio"], x["camd_plant"], e.get("CAMD_FACILITY_NAME", ""),
                e.get("CAMD_UNIT_ID", ""), x["camd_gen"], x["camd_mw"], x["eia_plant"],
                x["eia_gen"], x["eia_mw"], e.get("EIA_UNIT_TYPE", "")))
            for r in x["linked_in_sep_2026"]:
                lines.append("  - linked, Sep 2026: " + fmt_rec(r))
            if not x["linked_in_sep_2026"]:
                lines.append("  - linked generator not in the Sep 2026 workbook")
            for c in x["closer_candidates"]:
                lines.append("  - closer (r=%s, %s%s%s): %s" % (
                    c["ratio"], "linked elsewhere" if c["linked_by_crosswalk"] else "UNLINKED",
                    ", at linked plant" if c["at_linked_plant"] else "",
                    ", same id same state" if c["same_id_same_state"] else "", fmt_rec(c)))
            others = ["%s->%s/%s(%s)" % (r["gen"], r["eia_plant"], r["eia_gen"], r["step"])
                      for r in x["camd_plant_rows"]]
            lines.append("  - CAMD plant rows: " + "; ".join(others))
        lines.append("")
    return "\n".join(lines) + "\n"


def fetch_workbook():
    tried = []
    for url in EIA_URLS:
        try:
            raw = s1.fetch(url)
        except Exception as exc:
            tried.append("%s: %s" % (url, exc))
            continue
        if raw[:2] == b"PK":
            return url, raw, tried
        tried.append("%s: not an xlsx (%d bytes)" % (url, len(raw)))
    raise RuntimeError("no workbook: %s" % tried)


def read_workbook(raw):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    records, sheets = [], {}
    for ws in wb.worksheets:
        if "_pr" in ws.title.lower():
            continue
        recs = records_from_sheet(ws.title, [tuple(r) for r in ws.iter_rows(values_only=True)])
        sheets[ws.title] = len(recs)
        records += recs
    wb.close()
    return records, sheets


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "step1d_look.py " + VERSION, "uses": "step1d.py " + s1.VERSION,
           "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    raw = s1.fetch(s1.URL)
    names, rows, enc = s1.read_csv(raw)
    res["crosswalk"] = {"url": s1.URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                        "rows": len(rows)}
    pairs, skipped = s1.pairs_from_rows(rows)
    url, wraw, tried = fetch_workbook()
    res["eia"] = {"url": url, "bytes": len(wraw), "md5": hashlib.md5(wraw).hexdigest(),
                  "tried": tried}
    records, sheets = read_workbook(wraw)
    del wraw
    res["eia"]["sheets"] = sheets
    by_plant, by_gen_state = build_index(records)
    linked = crosswalk_links(rows)
    camd = camd_rows_by_plant(rows)
    chosen = [p for p in pairs if group_of(p)]
    chosen.sort(key=lambda p: (GROUPS.index(group_of(p)), -p["ratio"], p["camd_plant"],
                               p["camd_gen"]))
    looks = [look(p, by_plant, by_gen_state, linked, camd) for p in chosen]
    res["summary"] = summarize(looks)
    elk = [x for x in looks if x["camd_plant"] == "57865" and x["camd_gen"] == "ELK1"]
    res["sanity_elk1_finds_58835"] = bool(elk) and any(
        c["plant"] == 58835 and c["gen"] == "ELK1" for c in elk[0]["closer_candidates"])
    res["looks"] = looks
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(a.out_dir, "step1d_look.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    with open(os.path.join(a.out_dir, "step1d_look.md"), "w", encoding="utf-8") as fh:
        fh.write(markdown(res))
    print(json.dumps({k: res[k] for k in ("crosswalk", "eia", "summary",
                                          "sanity_elk1_finds_58835")}, indent=1))


if __name__ == "__main__":
    main()
