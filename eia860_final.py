"""eia860_final: sum Form EIA-860 generator additions and retirements for a data year, by energy source.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. Companion to eia860m-slip.

The Electric Power Annual's Table 4.6 gives each year's utility-scale additions
and retirements (net summer MW) from Form EIA-860. EIA released the final 2025
EIA-860 on 2026-09-10, but the Electric Power Annual 2025 is not out yet. This
script reads the EIA-860 generator file (3_1_Generator_Y<year>.xlsx) and sums:

- additions: Operable generators whose Operating Year is the data year (and,
  reported separately, retired generators built and retired in that year);
- retirements: generators with status RE whose Retirement Year is the data year.

It first does the same for 2023 and 2024 and compares with the published Table
4.6 totals. Only if both years reproduce within 1% (the gate) are the 2025 sums
used to score the predictions eia860m-slip stated in its docs (headline-plans.md,
headline-retirements.md). The first run (2026-10-16) reproduced every 2023 and
2024 row to the printed decimal; see docs/eia860-2025-scored.md.

    pip install pandas openpyxl
    python eia860_final.py --data-dir /data --out-dir /out
"""

import argparse
import glob
import io
import json
import os
import re
import shutil
import tempfile
import urllib.request
import zipfile

import pandas as pd

__version__ = "0.2.5"

YEARS = (2023, 2024, 2025)
URLS = {2025: "https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip",
        2024: "https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip",
        2023: "https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602023.zip"}

# Electric Power Annual Table 4.6, net summer MW as printed (2024 live page, 2023 archive; read 2026-10-15/16).
EPA = {
    2024: {"additions": {"total": 50454.0, "solar": 30915.9, "wind": 5154.3, "gas": 2113.1, "nuclear": 1114.0},
           "retirements": {"total": 9027.4, "coal": 3958.6, "gas": 4269.2}},
    2023: {"additions": {"total": 42318.0, "solar": 18887.6, "wind": 6586.4, "gas": 8701.3, "nuclear": 1114.0},
           "retirements": {"total": 15237.9, "coal": 9224.9, "gas": 5128.0}},
}
TOLERANCE = 0.01

# 2025, MW. Plans and first counts are EIA's Today in Energy figures (eia860m-slip CSVs);
# ranges are the predictions stated in eia860m-slip's docs before this file was read.
PLAN = {"additions_total": 63000.0, "additions_solar": 32500.0, "additions_battery": 18200.0,
        "additions_wind": 7700.0, "additions_gas": 4400.0,
        "retirements_total": 12300.0, "retirements_coal": 8100.0, "retirements_gas": 2600.0}
FIRST = {"additions_total": 53000.0, "additions_solar": 27200.0, "additions_battery": 15000.0,
         "retirements_total": 4600.0, "retirements_coal": 2600.0}
PREDICTED = {"additions_total": (55000.0, 55500.0), "additions_solar": (27900.0, 28000.0),
             "retirements_total": (5200.0, 5500.0)}

COAL = {"ANT", "BIT", "LIG", "SGC", "SUB", "WC", "RC"}
SOURCES = {"NG": "gas", "NUC": "nuclear", "WND": "wind", "SUN": "solar", "MWH": "battery"}


def norm(c):
    return re.sub(r"\s+", " ", str(c)).strip().lower()


def with_header(raw):
    """A sheet read with header=None, re-headed at the row that holds 'Plant Code'; note rows dropped."""
    for i in range(min(10, len(raw))):
        cells = [norm(v) for v in raw.iloc[i].tolist()]
        if "plant code" in cells:
            df = raw.iloc[i + 1:].copy()
            df.columns = cells
            df = df[pd.to_numeric(df["plant code"], errors="coerce").notna()]
            return df.reset_index(drop=True)
    raise ValueError("no 'Plant Code' header row in the first 10 rows")


def col(df, name):
    """The column called `name`, else the first column containing it."""
    if name in df.columns:
        return name
    for c in df.columns:
        if name in c:
            return c
    raise KeyError(name)


def num(s):
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def group_of(code):
    code = str(code).strip().upper()
    if code in COAL:
        return "coal"
    return SOURCES.get(code, "other")


def sums(df):
    """{group: {summer_mw, nameplate_mw, n}} for each energy-source group present, plus 'total'."""
    summer = num(df[col(df, "summer capacity (mw)")])
    nameplate = num(df[col(df, "nameplate capacity (mw)")])
    groups = df[col(df, "energy source 1")].map(group_of)
    out = {}
    for g in sorted(set(groups)) + ["total"]:
        m = pd.Series(True, index=df.index) if g == "total" else groups == g
        out[g] = {"summer_mw": round(float(summer[m].sum()), 1),
                  "nameplate_mw": round(float(nameplate[m].sum()), 1), "n": int(m.sum())}
    return out


def retired_rows(df):
    status = df[col(df, "status")].astype(str).str.strip().str.upper()
    return df[status.str.startswith("RE")]


def read_generators(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if re.search(r"3_1_generator.*\.xlsx$", n, re.I)]
        if not names:
            raise ValueError("no 3_1_Generator xlsx in %s" % zip_path)
        data = z.read(names[0])
    sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    out = {}
    for name, raw in sheets.items():
        k = norm(name)
        if k.startswith("operable"):
            out["operable"] = with_header(raw)
        elif k.startswith("retired"):
            out["retired"] = with_header(raw)
    return out, names[0], list(sheets)


def year_summary(zip_path, year):
    s, member, sheet_names = read_generators(zip_path)
    try:
        return _year_summary(s, member, sheet_names, year)
    except KeyError as e:
        # Name the columns that were there, so a format change can be fixed from the log alone.
        raise KeyError("%s; sheets %s; columns %s" % (e, sheet_names, {k: list(v.columns) for k, v in s.items()}))


def _year_summary(s, member, sheet_names, year):
    op, rt = s["operable"], s["retired"]
    rt_re = retired_rows(rt)
    added = op[num(op[col(op, "operating year")]) == year]
    try:
        same = rt_re[num(rt_re[col(rt_re, "operating year")]) == year]
    except KeyError:
        same = rt_re.iloc[0:0]
    gone = rt_re[num(rt_re[col(rt_re, "retirement year")]) == year]
    status = rt[col(rt, "status")].astype(str).str.strip().str.upper().value_counts()
    return {"member": member, "sheets": sheet_names,
            "rows": {"operable": len(op), "retired_sheet": len(rt), "retired_status_re": len(rt_re)},
            "retired_sheet_status": {str(k): int(v) for k, v in status.items()},
            "additions": sums(added), "additions_built_and_retired_same_year": sums(same),
            "retirements": sums(gone)}


def calibrate(summary, epa):
    out = {}
    for kind in ("additions", "retirements"):
        for g, want in epa[kind].items():
            got = summary[kind].get(g, {"summer_mw": 0.0})["summer_mw"]
            out["%s_%s" % (kind, g)] = {"computed": got, "epa": want, "rel_diff": round((got - want) / want, 5)}
    return out


def gate(calibrations, tol=TOLERANCE):
    """True if every year's additions and retirements totals are within tol of Table 4.6."""
    if not calibrations:
        return False
    return all(abs(v["rel_diff"]) <= tol for cal in calibrations.values()
               for k, v in cal.items() if k.endswith("_total"))


def score(summary):
    out = {}
    for key in sorted(set(PLAN) | set(FIRST) | set(PREDICTED)):
        kind, g = key.split("_", 1)
        got = summary[kind].get(g, {"summer_mw": 0.0})["summer_mw"]
        row = {"computed_mw": got}
        if key in PLAN:
            row["plan_mw"] = PLAN[key]
            row["of_plan"] = round(got / PLAN[key], 4)
        if key in FIRST:
            row["first_count_mw"] = FIRST[key]
            row["revision_vs_first"] = round(got / FIRST[key] - 1.0, 4)
        if key in PREDICTED:
            lo, hi = PREDICTED[key]
            row["predicted_mw"] = [lo, hi]
            row["in_range"] = lo <= got <= hi
        out[key] = row
    return out


def find_zip(data_dir, year):
    """A zip under data_dir that holds 3_1_Generator_Y<year>.xlsx, or None."""
    for path in sorted(glob.glob(os.path.join(data_dir, "**", "*"), recursive=True)):
        if not os.path.isfile(path) or not zipfile.is_zipfile(path):
            continue
        with zipfile.ZipFile(path) as z:
            if any(re.search(r"3_1_generator_y%d\.xlsx$" % year, n, re.I) for n in z.namelist()):
                return path
    return None


def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "eia860-final (MV2 of Munim, Inc.; mv2@munimtech.com)"})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as fh:
        shutil.copyfileobj(r, fh)
    return dest


def to_markdown(result):
    lines = ["# Form EIA-860 final additions and retirements, computed from the generator file", "",
             "Net summer MW. Gate: 2023 and 2024 totals within %.0f%% of Electric Power Annual Table 4.6: **%s**."
             % (100 * TOLERANCE, "passed" if result["gate_passed"] else "FAILED"), ""]
    for year, cal in sorted(result["calibration"].items()):
        lines += ["## Calibration %s" % year, "", "| item | computed | Table 4.6 | difference |", "|---|---|---|---|"]
        for k, v in cal.items():
            lines.append("| %s | %.1f | %.1f | %+.2f%% |" % (k, v["computed"], v["epa"], 100 * v["rel_diff"]))
        lines.append("")
    if result.get("score_2025"):
        lines += ["## 2025", "", "| item | computed MW | plan MW | of plan | first count MW | vs first | predicted | in range |",
                  "|---|---|---|---|---|---|---|---|"]
        for k, r in result["score_2025"].items():
            lines.append("| %s | %.1f | %s | %s | %s | %s | %s | %s |" % (
                k, r["computed_mw"], r.get("plan_mw", ""),
                "%.1f%%" % (100 * r["of_plan"]) if "of_plan" in r else "",
                r.get("first_count_mw", ""),
                "%+.1f%%" % (100 * r["revision_vs_first"]) if "revision_vs_first" in r else "",
                "%g-%g" % tuple(r["predicted_mw"]) if "predicted_mw" in r else "",
                r.get("in_range", "")))
        lines.append("")
    for year, err in sorted(result["errors"].items()):
        lines.append("Error for %s: %s" % (year, err))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    result = {"summaries": {}, "calibration": {}, "errors": {}, "sources": {}}
    for year in YEARS:
        try:
            path = find_zip(args.data_dir, year) if os.path.isdir(args.data_dir) else None
            if path is None:
                path = fetch(URLS[year], os.path.join(tmp, "eia860%d.zip" % year))
            result["sources"][year] = {"url": URLS[year], "file": os.path.basename(path),
                                       "bytes": os.path.getsize(path)}
            result["summaries"][year] = year_summary(path, year)
            if year in EPA:
                result["calibration"][year] = calibrate(result["summaries"][year], EPA[year])
        except Exception as e:  # record and go on: one bad year must not hide the others
            result["errors"][year] = "%s: %s" % (type(e).__name__, e)
    result["gate_passed"] = len(result["calibration"]) == 2 and gate(result["calibration"])
    if result["gate_passed"] and 2025 in result["summaries"]:
        result["score_2025"] = score(result["summaries"][2025])
    with open(os.path.join(args.out_dir, "eia860_final.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "eia860_final.md"), "w", encoding="utf-8") as fh:
        fh.write(to_markdown(result))
    print(to_markdown(result))


if __name__ == "__main__":
    main()
