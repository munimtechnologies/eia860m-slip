"""step1d: pre-registration step1d-1 (docs/step1d-plan.md).

EPA's CAMD-EIA crosswalk (github.com/USEPA/camd-eia-crosswalk, epa_eia_crosswalk.csv) links
CAMD generators to EIA generators in sub-steps. Step 1a joins exact plant and generator ids;
1b removes special characters; 1c converts ids to numbers; 1d "removes leading letters" (it
keeps an id's trailing digits, so ELK1 and E01 both become 1). The Antelope Elk case
(CAMD 57865 ELK1-ELK3, 202 MW, linked in step 1d to EIA 57865 E01-E03, 9.3 MW) is one such
link. This counts, for every sub-step, how often a linked pair's two nameplate capacities
differ by a factor of 1.5 or more, and scores the plan's predictions.

Standard library only. EPA's file is downloaded at run time from a pinned commit and not
stored here.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

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

VERSION = "0.1.0"
COMMIT = "3c7d6724cddee38dfb6a06debca732c33a227ed6"
URL = ("https://raw.githubusercontent.com/USEPA/camd-eia-crosswalk/%s/epa_eia_crosswalk.csv"
       % COMMIT)
REQUIRED = ("CAMD_PLANT_ID", "CAMD_GENERATOR_ID", "CAMD_NAMEPLATE_CAPACITY", "EIA_PLANT_ID",
            "EIA_GENERATOR_ID", "EIA_NAMEPLATE_CAPACITY", "MATCH_TYPE_GEN")
EXTRA = ("CAMD_STATE", "CAMD_FACILITY_NAME", "CAMD_UNIT_ID", "CAMD_FUEL_TYPE", "CAMD_STATUS",
         "EIA_PLANT_NAME", "EIA_UNIT_TYPE", "EIA_FUEL_TYPE")
STEPS = ("1a", "1b", "1c", "1d", "manual", "other")
ELK_PLANT = "57865"
MIN_1A = 1000
MIN_1D = 10
UA = {"User-Agent": "mv2-step1d/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def step_of(label):
    """MATCH_TYPE_GEN text -> '1a'..'1d', 'manual', 'other', or None when blank."""
    text = (label or "").strip()
    if not text or text.upper() == "NA":
        return None
    m = re.search(r"Step\s*1([a-d])\b", text)
    if m:
        return "1" + m.group(1)
    if text.lower().startswith("manual match"):
        return "manual"
    return "other"


def number(text):
    try:
        v = float(str(text).strip())
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def clean_id(text):
    """An id as text: stripped, a whole-number float written as an integer ('1.0' -> '1')."""
    t = str(text if text is not None else "").strip()
    if t.upper() == "NA":
        return ""
    if re.fullmatch(r"\d+\.0+", t):
        t = t.split(".")[0]
    return t


def prefix(gen_id):
    m = re.match(r"[A-Za-z]*", gen_id or "")
    return m.group(0).upper()


def ratio(a, b):
    """max/min of two positive capacities, or None."""
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return max(a, b) / min(a, b)


def pairs_from_rows(rows):
    """Distinct (CAMD plant, CAMD gen, EIA plant, EIA gen) links with a step and both
    capacities > 0. Returns (pairs, counts of skipped rows)."""
    pairs = {}
    skipped = {"no_step": 0, "no_ids": 0, "no_capacity": 0, "conflicts": 0}
    for row in rows:
        step = step_of(row.get("MATCH_TYPE_GEN"))
        if step is None:
            skipped["no_step"] += 1
            continue
        key = tuple(clean_id(row.get(c)) for c in ("CAMD_PLANT_ID", "CAMD_GENERATOR_ID",
                                                   "EIA_PLANT_ID", "EIA_GENERATOR_ID"))
        if not all(key):
            skipped["no_ids"] += 1
            continue
        camd = number(row.get("CAMD_NAMEPLATE_CAPACITY"))
        eia = number(row.get("EIA_NAMEPLATE_CAPACITY"))
        r = ratio(camd, eia)
        if r is None:
            skipped["no_capacity"] += 1
            continue
        if key in pairs:
            old = pairs[key]
            if old["step"] != step or old["camd_mw"] != camd or old["eia_mw"] != eia:
                skipped["conflicts"] += 1
            continue
        pairs[key] = {"camd_plant": key[0], "camd_gen": key[1], "eia_plant": key[2],
                      "eia_gen": key[3], "step": step, "camd_mw": camd, "eia_mw": eia,
                      "ratio": round(r, 3),
                      "prefix_clash": bool(prefix(key[1]) and prefix(key[3])
                                           and prefix(key[1]) != prefix(key[3])),
                      "extra": {c: (row.get(c) or "").strip() for c in EXTRA}}
    return list(pairs.values()), skipped


def share(k, n):
    return round(k / n, 4) if n else None


def by_step(pairs):
    out = {}
    for s in STEPS:
        sel = [p for p in pairs if p["step"] == s]
        n15 = sum(1 for p in sel if p["ratio"] >= 1.5)
        out[s] = {"n": len(sel), "r15": n15, "r3": sum(1 for p in sel if p["ratio"] >= 3),
                  "share_r15": share(n15, len(sel))}
    return out


def metrics(pairs, columns_ok):
    steps = by_step(pairs)
    d = [p for p in pairs if p["step"] == "1d"]
    clash = [p for p in d if p["prefix_clash"]]
    return {"columns_ok": columns_ok, "pairs": len(pairs), "steps": steps,
            "d_r3_outside_elk": sum(1 for p in d if p["ratio"] >= 3
                                    and p["camd_plant"] != ELK_PLANT),
            "d_clash": {"n": len(clash), "r15": sum(1 for p in clash if p["ratio"] >= 1.5),
                        "share_r15": share(sum(1 for p in clash if p["ratio"] >= 1.5),
                                           len(clash))}}


def score(m):
    s = {"G1": bool(m["columns_ok"] and m["steps"]["1a"]["n"] >= MIN_1A
                    and m["steps"]["1d"]["n"] >= MIN_1D)}
    if not s["G1"]:
        return s
    a, d = m["steps"]["1a"]["share_r15"], m["steps"]["1d"]["share_r15"]
    s["S1"] = d > 0 and d >= 2 * a
    s["S2"] = m["d_r3_outside_elk"] >= 3
    s["S3"] = a < 0.10
    c = m["d_clash"]
    s["S4"] = c["n"] >= 5 and c["share_r15"] >= 0.30
    return s


def read_csv(raw):
    try:
        text = raw.decode("utf-8-sig")
        enc = "utf-8"
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
        enc = "latin-1"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    return reader.fieldnames or [], rows, enc


def fetch(url, timeout=300):
    last = None
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            last = exc
            time.sleep(30)
    raise last


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"tool": "step1d.py " + VERSION, "python": sys.version.split()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    raw = fetch(URL)
    names, rows, enc = read_csv(raw)
    res["download"] = {"url": URL, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                       "encoding": enc, "rows": len(rows), "columns": names}
    columns_ok = all(c in names for c in REQUIRED)
    res["missing_columns"] = [c for c in REQUIRED if c not in names]
    labels = {}
    for row in rows:
        lab = (row.get("MATCH_TYPE_GEN") or "").strip()
        labels[lab] = labels.get(lab, 0) + 1
    res["match_type_gen_rows"] = dict(sorted(labels.items(), key=lambda kv: -kv[1]))
    pairs, skipped = pairs_from_rows(rows) if columns_ok else ([], {})
    res["skipped_rows"] = skipped
    m = metrics(pairs, columns_ok)
    res["metrics"] = m
    res["scores"] = score(m)
    flagged = sorted((p for p in pairs if p["ratio"] >= 1.5 and p["step"] in ("1b", "1c", "1d")),
                     key=lambda p: (p["step"], -p["ratio"]))
    res["flagged_1b_1c_1d"] = flagged
    res["d_pairs"] = sorted((p for p in pairs if p["step"] == "1d"), key=lambda p: -p["ratio"])
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(a.out_dir, "step1d.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    with open(os.path.join(a.out_dir, "step1d_flagged.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["step", "ratio", "camd_plant", "camd_gen", "camd_mw", "eia_plant",
                    "eia_gen", "eia_mw", "prefix_clash"] + list(EXTRA))
        for p in flagged:
            w.writerow([p["step"], p["ratio"], p["camd_plant"], p["camd_gen"], p["camd_mw"],
                        p["eia_plant"], p["eia_gen"], p["eia_mw"], p["prefix_clash"]]
                       + [p["extra"][c] for c in EXTRA])
    print(json.dumps({k: res[k] for k in ("download", "missing_columns", "match_type_gen_rows",
                                          "skipped_rows", "metrics", "scores")}, indent=1))


if __name__ == "__main__":
    main()
