"""coal25: the generator rows behind eia860_final's 2025 coal retirements, and rows rated above nameplate.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. Companion to eia860_final.py.

The 2025 coal retirements in the final 2025 Form EIA-860 sum to more net summer
capacity (2,688.4 MW) than nameplate (2,626.0 MW); in 2023 and 2024 summer was
89-90% of nameplate. This lists every 2025 coal retirement row and, for each data
year, counts the rows (operable, and retired in that year) whose summer rating is
above nameplate, by energy-source group, with the largest excesses.

    python coal25.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860_final as ef

FIELDS = ("plant code", "plant name", "state", "generator id", "technology", "energy source 1",
          "nameplate capacity (mw)", "summer capacity (mw)", "winter capacity (mw)",
          "operating month", "operating year", "retirement month", "retirement year", "status")


def clean(v):
    """A JSON-safe value: None for blanks and NaN, numbers and strings as they are, else str."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, (bool, int, float, str)):
        return v
    return str(v)


def pick(df):
    """{field: column} for the FIELDS this sheet has."""
    out = {}
    for f in FIELDS:
        try:
            out[f] = ef.col(df, f)
        except KeyError:
            pass
    return out


def records(df, cols):
    return [{f: clean(row[c]) for f, c in cols.items()} for _, row in df.iterrows()]


def over_nameplate(df, top=15):
    """Rows whose summer capacity is above a positive nameplate: counts, excess MW by group, largest rows."""
    summer = ef.num(df[ef.col(df, "summer capacity (mw)")])
    plate = ef.num(df[ef.col(df, "nameplate capacity (mw)")])
    groups = df[ef.col(df, "energy source 1")].map(ef.group_of)
    excess = summer - plate
    m = (excess > 0) & (plate > 0)
    by = {}
    for g in sorted(set(groups[m])):
        mg = m & (groups == g)
        by[g] = {"n": int(mg.sum()), "excess_mw": round(float(excess[mg].sum()), 1)}
    cols = pick(df)
    cols["excess_mw"] = "_excess"
    sub = df[m].assign(_excess=excess[m]).sort_values("_excess", ascending=False).head(top)
    return {"rows": int(len(df)), "over": int(m.sum()), "by_group": by, "largest": records(sub, cols)}


def year_result(zip_path, year):
    s, _, _ = ef.read_generators(zip_path)
    rt_re = ef.retired_rows(s["retired"])
    gone = rt_re[ef.num(rt_re[ef.col(rt_re, "retirement year")]) == year]
    coal = gone[gone[ef.col(gone, "energy source 1")].map(ef.group_of) == "coal"]
    return ({"operable": over_nameplate(s["operable"]), "retired_in_year": over_nameplate(gone)},
            records(coal, pick(coal)))


def to_markdown(result):
    lines = ["# 2025 coal retirements in Form EIA-860, and rows rated above nameplate", ""]
    coal = result.get("coal_retired_2025") or []
    if coal:
        lines += ["## Coal generators retired in 2025 (%d rows)" % len(coal), "",
                  "| plant (code) | state | generator | nameplate MW | summer MW | winter MW | retired |",
                  "|---|---|---|---:|---:|---:|---|"]
        for r in coal:
            lines.append("| %s (%s) | %s | %s | %s | %s | %s | %s/%s |" % (
                r.get("plant name"), r.get("plant code"), r.get("state"), r.get("generator id"),
                r.get("nameplate capacity (mw)"), r.get("summer capacity (mw)"), r.get("winter capacity (mw)"),
                r.get("retirement month"), r.get("retirement year")))
        lines.append("")
    for year, d in sorted(result["over_nameplate"].items()):
        lines += ["## %s: rows with summer capacity above nameplate" % year, ""]
        for part, o in d.items():
            groups = ", ".join("%s %d (+%.1f MW)" % (g, v["n"], v["excess_mw"]) for g, v in o["by_group"].items())
            lines.append("- %s: %d of %d rows; %s" % (part, o["over"], o["rows"], groups or "none"))
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
    result = {"coal_retired_2025": None, "over_nameplate": {}, "errors": {}}
    for year in ef.YEARS:
        try:
            path = ef.find_zip(args.data_dir, year)
            if path is None:
                raise FileNotFoundError("no EIA-860 %d zip under %s" % (year, args.data_dir))
            result["over_nameplate"][year], coal = year_result(path, year)
            if year == 2025:
                result["coal_retired_2025"] = coal
        except Exception as e:  # record and go on: one bad year must not hide the others
            result["errors"][year] = "%s: %s" % (type(e).__name__, e)
    with open(os.path.join(args.out_dir, "coal25.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    with open(os.path.join(args.out_dir, "coal25.md"), "w", encoding="utf-8") as fh:
        fh.write(to_markdown(result))
    print(to_markdown(result))


if __name__ == "__main__":
    main()
