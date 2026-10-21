"""erplan: were the annual-only generators already in the annual EIA-860's early release?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The twenty-sixth result (docs/entry-timing.md) found that the annual EIA-860's plan-only
generators for a year Y (set A) enter EIA-860M from February to August of Y and then stop, at
about the time of the annual file's final release. That edge fits R1 (lag: the annual filing
held the project and EIA-860M listed it later) and R2 (revision: the annual record was added
during Y, after the project appeared in EIA-860M) alike. This tool reads dated copies of the
annual file from PUDL's raw EIA-860 archive on Zenodo: for each plan year Y 2022-2025, the
early release of report year Y - 1 (published by PUDL before EIA-860M's July report of Y came
out) and the final release. Each generator of the twenty-sixth result's sets
(data/entrytime_sets.csv at commit c7eca74) gets one class in each copy, by plant id and
generator id (trimmed, any case):

    plan_y          on the Proposed sheet with a current planned operation year of Y
    proposed_other  on the Proposed sheet with another year or none
    operable        on the Operable sheet (and not on the Proposed sheet)
    retired         only on the Retired and Canceled sheet
    absent          on none of them

Spans of first EIA-860M listing: early = February-March reports, mid = April-June,
late = July-August, edge = September-December or after Y. Shares are MW shares.

Checks and predictions: docs/er-plan-preregistration.md.

    python erplan.py --structure-only --data-dir /data --out-dir /out   (headers only)
    python erplan.py --data-dir /data --out-dir /out
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import zipfile

__version__ = "0.1.0"
UA = "mv2-munim-erplan/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
SETS_URL = ("https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/"
            "c7eca747bde864f05f6c9ea8ebd74352bcb6d748/data/entrytime_sets.csv")
# Plan year Y -> copies of eia860-(Y-1).zip: (Zenodo record id, size, md5, publication date),
# from zenodoprobe-v1 (the first copy of each file, and its last change).
COPIES = {
    2022: {"er": ("6954131", 19822280, "8a2a3369a21e3218ab547b31076a9efb", "2022-08-02"),
           "final": ("7113854", 20114180, "9caab707948ddee58bc748b6f5e43aa1", "2022-09-26")},
    2023: {"er": ("8164776", 20765549, "3af89bb4b830b801fda08905ec9feba4", "2023-07-19"),
           "final": ("10067566", 20646976, "2fbba665a021a7b4943349d72405cddd", "2023-11-02")},
    2024: {"er": ("11662381", 21049060, "9c22c886654df97cce513699487fb837", "2024-06-15"),
           "final": ("13682785", 21237983, "12ad0f63fabf0025ebf53f6728f13c18", "2024-09-24")},
    2025: {"er": ("15629904", 21997466, "55d018066f22a4285c170c8217aea099", "2025-06-12"),
           "final": ("17091669", 22100342, "684352896d6a62b5d2d98a403b30e120", "2025-09-10")},
}
CLASSES = ("plan_y", "proposed_other", "operable", "retired", "absent")
RANK = {c: i for i, c in enumerate(CLASSES)}
SPANS = {"early": ("m02", "m03"), "mid": ("m04", "m05", "m06"), "late": ("m07", "m08"),
         "edge": ("m09", "m10", "m11", "m12", "after")}
SETS = ("A", "A_built", "B")
PLANT = ("plant code", "plant id")
GEN = ("generator id",)
YEAR = ("current year", "current planned operation year", "planned operation year")
HEAD_ROWS = 10
# Check C1: pooled 2018-2025 MW of the sets as docs/entry-timing.md states them, and A's
# July-August MW (8,253.0 + 4,829.3).
EXPECTED_SETS = {"A": 55263.5, "A_built": 36998.4, "B": 32937.3}
EXPECTED_A_LATE = 13082.3
F1_MIN = 0.95   # A's MW in the final copy at all
F2_MIN = 0.90   # A's MW in the final copy's plan for Y
F3_MIN = 0.95   # final Operable keys found in the early release
P1_MIN = 0.70
P3_MAX = 0.20
R2_MAX = 0.30
YEAR_MIN_MW = 100.0
TOP = 15
PAUSE = 2.0


def norm(s):
    return re.sub(r"\s+", " ", "" if s is None else str(s)).strip().lower()


def gen_id(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip().upper()
    return s or None


def key(plant, gen):
    """'plant/GEN' as annual860.norm_key builds it; None if either part is missing."""
    try:
        p = int(float(plant))
    except (TypeError, ValueError):
        return None
    g = gen_id(gen)
    return None if g is None else "%d/%s" % (p, g)


def as_year(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def sheet_kind(name):
    n = norm(name)
    for kind in ("operable", "proposed", "retired"):
        if n.startswith(kind):
            return kind
    return None


def generator_members(names):
    return [n for n in names if re.search(r"(^|/)3_1_generator[^/]*\.xlsx$", n, re.I)]


def header(rows, limit=HEAD_ROWS):
    """(index, normalized cells) of the first row naming both a plant and a generator column."""
    for i, r in enumerate(rows[:limit]):
        cells = [norm(c) for c in (r or ())]
        if any(c in PLANT for c in cells) and any(c in GEN for c in cells):
            return i, cells
    return None, None


def col(cells, names):
    for n in names:
        if n in cells:
            return cells.index(n)
    return None


def cell(row, i):
    return row[i] if row is not None and i is not None and i < len(row) else None


def early_marked(member, above):
    """Does the workbook call itself an early release (file name or a row above the header)?"""
    if "early release" in norm(member.replace("_", " ")):
        return True
    return any("early release" in norm(c) for r in above for c in (r or ()))


def structure(sheets):
    """Per relevant sheet: kind, header row, columns and the text above the header. No data row
    is read here."""
    out, problems = {}, []
    for name, rows in sheets.items():
        kind = sheet_kind(name)
        if kind is None:
            continue
        i, cells = header(rows)
        if i is None:
            problems.append("no header row in sheet %r" % name)
            out[name] = {"kind": kind, "header_row": None}
            continue
        miss = [] if kind != "proposed" or col(cells, YEAR) is not None else ["year"]
        if miss:
            problems.append("no current-year column in sheet %r" % name)
        out[name] = {"kind": kind, "header_row": i, "columns": [c for c in cells if c],
                     "above": [[str(c) for c in (r or ()) if c not in (None, "")]
                               for r in rows[:i]]}
    kinds = {v["kind"] for v in out.values() if v.get("header_row") is not None}
    for kind in ("operable", "proposed"):
        if kind not in kinds:
            problems.append("no usable %s sheet" % kind)
    return out, problems


def index(sheets, year):
    """{key: class} over the Operable, Proposed and Retired sheets, best class first."""
    found = {}
    for name, rows in sheets.items():
        kind = sheet_kind(name)
        if kind is None:
            continue
        i, cells = header(rows)
        if i is None:
            continue
        pc, gc, yc = col(cells, PLANT), col(cells, GEN), col(cells, YEAR)
        if kind == "proposed" and yc is None:
            continue
        for r in rows[i + 1:]:
            k = key(cell(r, pc), cell(r, gc))
            if k is None:
                continue
            if kind == "proposed":
                c = "plan_y" if as_year(cell(r, yc)) == year else "proposed_other"
            else:
                c = kind
            if k not in found or RANK[c] < RANK[found[k]]:
                found[k] = c
    return found


def span(bucket):
    for s, bs in SPANS.items():
        if bucket in bs:
            return s
    return "other"


def read_sets(text):
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        plant, _, gen = r["key"].partition("/")
        rows.append({"year": int(r["year"]), "set": r["set"], "key": key(plant, gen) or r["key"],
                     "group": r["group"], "mw": float(r["mw"]), "bucket": r["bucket"],
                     "span": span(r["bucket"])})
    return rows


def classify(rows, idx):
    """Adds 'er' and 'final' classes to the rows of each year in idx ({year: (er, final)})."""
    for r in rows:
        if r["year"] in idx:
            er, final = idx[r["year"]]
            r["er"] = er.get(r["key"], "absent")
            r["final"] = final.get(r["key"], "absent")
    return rows


def tally(rows, years, set_name, span_name="all", field="er", group="all"):
    out = {c: 0.0 for c in CLASSES}
    for r in rows:
        if (r["year"] in years and r["set"] == set_name and field in r
                and (span_name == "all" or r["span"] == span_name)
                and (group == "all" or r["group"] == group)):
            out[r[field]] += r["mw"]
    return out


def share(t, classes=("plan_y",)):
    tot = sum(t.values())
    return sum(t[c] for c in classes) / tot if tot > 0 else None


def check_c1(rows):
    got = {s: round(sum(r["mw"] for r in rows if r["set"] == s and 2018 <= r["year"] <= 2025), 1)
           for s in EXPECTED_SETS}
    late = round(sum(r["mw"] for r in rows if r["set"] == "A" and 2018 <= r["year"] <= 2025
                     and r["span"] == "late"), 1)
    ok = (all(abs(got[s] - v) <= 0.15 for s, v in EXPECTED_SETS.items())
          and abs(late - EXPECTED_A_LATE) <= 0.15)
    return {"pass": ok, "got": got, "a_late": late}


def check_f(rows, years):
    t = tally(rows, years, "A", field="final")
    f1 = share(t, ("plan_y", "proposed_other", "operable", "retired"))
    f2 = share(t)
    return {"f1": f1, "f2": f2, "f1_pass": f1 is not None and f1 >= F1_MIN,
            "f2_pass": f2 is not None and f2 >= F2_MIN}


def check_f3(er, final):
    """Share of the final copy's Operable keys found anywhere in the early release."""
    op = [k for k, c in final.items() if c == "operable"]
    if not op:
        return None
    return sum(1 for k in op if k in er) / len(op)


def predictions(rows, years):
    late = share(tally(rows, years, "A", "late"))
    early = share(tally(rows, years, "A", "early"))
    by_year = {}
    for y in years:
        t = tally(rows, (y,), "A", "late")
        if sum(t.values()) >= YEAR_MIN_MW:
            by_year[y] = share(t)
    n_ok = sum(1 for v in by_year.values() if v >= P1_MIN)
    p1 = None if late is None else late >= P1_MIN
    p2 = None if len(by_year) < 3 else n_ok >= 3
    p3 = None if late is None or early is None else early - late <= P3_MAX
    return {"late": late, "early": early, "late_by_year": by_year, "years_ok": n_ok,
            "P1": p1, "P2": p2, "P3": p3, "reading": reading(late)}


def reading(late):
    if late is None:
        return "no data"
    if late >= P1_MIN:
        return "most late entrants were in the early release (R1 for most)"
    if late <= R2_MAX:
        return "most late entrants were not in the early release's plan (R2 for most)"
    return "mixed"


# ---- input/output (not unit-tested: network and workbooks) ----

def fetch(url, timeout=300):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), None
    except urllib.error.HTTPError as e:
        return e.code, None, "HTTP %d" % e.code
    except Exception as e:  # recorded, not raised
        return None, None, "%s: %s" % (type(e).__name__, e)


def copy_urls(rec, name):
    return ["https://zenodo.org/records/%s/files/%s?download=1" % (rec, name),
            "https://zenodo.org/api/records/%s/files/%s/content" % (rec, name)]


def get_copy(data_dir, rec, name, size, md5, calls):
    path = os.path.join(data_dir, "%s-%s" % (rec, name))
    if os.path.exists(path):
        with open(path, "rb") as fh:
            if hashlib.md5(fh.read()).hexdigest() == md5:
                return path
    for url in copy_urls(rec, name):
        for _ in range(3):
            status, body, err = fetch(url)
            got = hashlib.md5(body).hexdigest() if body is not None else None
            calls.append({"url": url, "status": status, "error": err,
                          "bytes": None if body is None else len(body), "md5": got})
            if body is not None and got == md5 and len(body) == size:
                with open(path, "wb") as fh:
                    fh.write(body)
                return path
            time.sleep(60 if status == 429 else PAUSE)
    return None


def read_sheets(data, header_only):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        if sheet_kind(ws.title) is None:
            out[ws.title] = []
            continue
        ws.reset_dimensions()  # some workbooks state a wrong sheet size
        rows = []
        for r in ws.iter_rows(values_only=True):
            rows.append(r)
            if header_only and len(rows) >= HEAD_ROWS:
                break
        out[ws.title] = rows
    wb.close()
    return out


def open_copy(path, header_only):
    """(info, sheets or None) for one downloaded zip."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        gm = generator_members(names)
        info = {"members": names, "generator_members": gm}
        if len(gm) != 1:
            info["problems"] = ["%d generator workbooks" % len(gm)]
            return info, None
        sheets = read_sheets(z.read(gm[0]), header_only)
    st, problems = structure(sheets)
    above = [r for v in st.values() for r in v.get("above", [])]
    info.update({"sheet_names": list(sheets), "sheets": st, "problems": problems,
                 "early_marked": early_marked(gm[0], above)})
    return info, (None if header_only else sheets)


def load_copies(data_dir, header_only):
    """Downloads and checks the eight copies; unless header_only, indexes each workbook at once
    (index(), not the rows, is kept, to save memory)."""
    calls, files, idxs = [], {}, {}
    for y, kinds in COPIES.items():
        for kind, (rec, size, md5, date) in kinds.items():
            name = "eia860-%d.zip" % (y - 1)
            path = get_copy(data_dir, rec, name, size, md5, calls)
            f = {"plan_year": y, "kind": kind, "record": rec, "file": name, "date": date,
                 "d1": path is not None}
            if path is not None:
                try:
                    info, sh = open_copy(path, header_only)
                except Exception as e:  # an unreadable workbook fails D2, it does not stop the run
                    info, sh = {"problems": ["%s: %s" % (type(e).__name__, e)]}, None
                f.update(info)
                f["d2"] = not info.get("problems")
                f["e1"] = info.get("early_marked") == (kind == "er")
                idxs[(y, kind)] = None if sh is None else index(sh, y)
                del sh
            files["%d-%s" % (y, kind)] = f
    valid = [y for y in COPIES if all(
        files["%d-%s" % (y, k)].get(c) for k in ("er", "final") for c in ("d1", "d2", "e1"))]
    return files, idxs, valid, calls


def r4(x):
    return None if x is None else round(x, 4)


def write_structure(out_dir, files, valid, calls):
    with open(os.path.join(out_dir, "erplan-structure.json"), "w", encoding="utf-8") as fh:
        json.dump({"version": __version__, "files": files, "valid_years": valid, "calls": calls},
                  fh, indent=1)
    md = ["# erplan %s: structure of the dated EIA-860 copies (headers only)" % __version__, "",
          "MV2 of Munim, Inc. (made with AI agents). No data row was analysed or written.", "",
          "Plan years with both copies passing D1, D2 and E1: %s." % (valid or "none"), "",
          "| copy | record | date | D1 md5 | D2 sheets | E1 marking | generator workbook | problems |",
          "|---|---|---|---|---|---|---|---|"]
    for k, f in files.items():
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, f["record"], f["date"], f["d1"], f.get("d2"), f.get("e1"),
            ", ".join(f.get("generator_members", [])), "; ".join(f.get("problems", []))))
    md += ["", "## Header rows", ""]
    for k, f in files.items():
        for name, s in (f.get("sheets") or {}).items():
            md.append("- %s / %s (%s): header row %s; above: %s; columns: %s" % (
                k, name, s["kind"], s.get("header_row"),
                json.dumps(s.get("above", []))[:300], ", ".join(s.get("columns", []))))
    with open(os.path.join(out_dir, "erplan-structure.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def tables(rows, years):
    out = []
    groups = ["all"] + sorted({r["group"] for r in rows if r["year"] in years})
    for s in SETS:
        for sp in ("all",) + tuple(SPANS):
            for g in groups:
                for y in ("pooled",) + tuple(years):
                    ys = years if y == "pooled" else (y,)
                    er = tally(rows, ys, s, sp, "er", g)
                    fi = tally(rows, ys, s, sp, "final", g)
                    tot = sum(er.values())
                    if tot <= 0:
                        continue
                    row = {"year": y, "set": s, "span": sp, "group": g, "mw": round(tot, 1),
                           "er_plan_share": r4(share(er)),
                           "er_any_share": r4(share(er, CLASSES[:4])),
                           "final_plan_share": r4(share(fi))}
                    row.update({"er_" + c: round(er[c], 1) for c in CLASSES})
                    out.append(row)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--structure-only", action="store_true")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    files, idxs, valid, calls = load_copies(args.data_dir, args.structure_only)
    write_structure(args.out_dir, files, valid, calls)
    if args.structure_only:
        print(json.dumps({"valid_years": valid, "calls": len(calls)}, indent=1))
        return
    status, body, err = fetch(SETS_URL)
    if body is None:
        raise SystemExit("could not fetch %s: %s" % (SETS_URL, err))
    rows = read_sets(body.decode("utf-8"))
    idx, f3 = {}, {}
    for y in valid:
        er, final = idxs[(y, "er")], idxs[(y, "final")]
        idx[y] = (er, final)
        f3[y] = check_f3(er, final)
    classify(rows, idx)
    years = tuple(valid)
    c1 = check_c1(rows)
    f = check_f(rows, years)
    f3_ok = bool(f3) and all(v is not None and v >= F3_MIN for v in f3.values())
    scored = c1["pass"] and f["f1_pass"] and f["f2_pass"] and f3_ok and len(years) >= 3
    pred = predictions(rows, years)
    tab = tables(rows, years)
    top = sorted((r for r in rows if r["year"] in idx and r["set"] == "A"
                  and r["span"] == "late" and r["er"] != "plan_y"),
                 key=lambda r: (-r["mw"], r["key"]))[:TOP]
    out = {"meta": {"version": __version__, "sets_url": SETS_URL, "user_agent": UA,
                    "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "years": list(years)},
           "checks": {"C1": c1, "F": f, "F3": {str(k): r4(v) for k, v in f3.items()},
                      "F3_pass": f3_ok, "scored": scored},
           "predictions": dict(pred, late=r4(pred["late"]), early=r4(pred["early"]),
                               late_by_year={str(k): r4(v)
                                             for k, v in pred["late_by_year"].items()}),
           "tables": tab, "top_late_not_in_er_plan": top}
    with open(os.path.join(args.out_dir, "erplan.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(args.out_dir, "erplan_rows.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "set", "key", "group", "mw", "bucket", "span", "er", "final"])
        for r in rows:
            if r["year"] in idx:
                w.writerow([r["year"], r["set"], r["key"], r["group"], r["mw"], r["bucket"],
                            r["span"], r["er"], r["final"]])
    md = ["# erplan %s: annual-only generators in the annual EIA-860's early release" % __version__,
          "", "MV2 of Munim, Inc. (made with AI agents). Pre-registration: "
          "docs/er-plan-preregistration.md.", "",
          "Plan years scored: %s. Scored: %s." % (list(years), scored), "",
          "## Checks", "",
          "- C1 (sets file matches the twenty-sixth result): %s %s, A late %s" % (
              c1["pass"], c1["got"], c1["a_late"]),
          "- F1 (A's MW in the final copy at all >= %.2f): %s (%s)" % (F1_MIN, f["f1_pass"],
                                                                      r4(f["f1"])),
          "- F2 (A's MW in the final copy's plan for Y >= %.2f): %s (%s)" % (
              F2_MIN, f["f2_pass"], r4(f["f2"])),
          "- F3 (final Operable keys in the early release >= %.2f each year): %s %s" % (
              F3_MIN, f3_ok, {str(k): r4(v) for k, v in f3.items()}),
          "", "## Predictions", "",
          "- A late (July-August) share in the early release's plan for Y: %s" % r4(pred["late"]),
          "- A early (February-March) share: %s" % r4(pred["early"]),
          "- by year (late MW >= %.0f): %s" % (YEAR_MIN_MW, {str(k): r4(v) for k, v in
                                                             pred["late_by_year"].items()}),
          "- P1 (late >= %.2f): %s" % (P1_MIN, pred["P1"]),
          "- P2 (late >= %.2f in at least 3 years): %s (%d years)" % (P1_MIN, pred["P2"],
                                                                     pred["years_ok"]),
          "- P3 (early - late <= %.2f): %s" % (P3_MAX, pred["P3"]),
          "- reading: %s" % pred["reading"], "",
          "## Tables (all groups: erplan.json; every generator: erplan_rows.csv)", "",
          "| year | set | span | mw | er_plan_share | er_any_share | final_plan_share | "
          "plan_y | proposed_other | operable | retired | absent |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in tab:
        if r["group"] == "all":
            md.append("| %s | %s | %s | %.1f | %s | %s | %s | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
                r["year"], r["set"], r["span"], r["mw"], r["er_plan_share"], r["er_any_share"],
                r["final_plan_share"], r["er_plan_y"], r["er_proposed_other"], r["er_operable"],
                r["er_retired"], r["er_absent"]))
    md += ["", "## Largest late A generators not in the early release's plan for Y", "",
           "| year | key | group | mw | bucket | er | final |", "|---|---|---|---|---|---|---|"]
    for r in top:
        md.append("| %d | %s | %s | %.1f | %s | %s | %s |" % (
            r["year"], r["key"], r["group"], r["mw"], r["bucket"], r["er"], r["final"]))
    with open(os.path.join(args.out_dir, "erplan.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(json.dumps({"scored": scored, "years": list(years), "P1": pred["P1"],
                      "P2": pred["P2"], "P3": pred["P3"]}, indent=1))


if __name__ == "__main__":
    main()
