"""spot: print every raw PUDL EIA-860M changelog record for a few named generators.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. A hand-check aid for eia860m-slip's
plan-flows result: the rows are printed as PUDL stores them, with no reading applied, so
the state plan_flows.py gave each generator can be checked by eye.

0.2.0: reads only the named plants' rows when the parquet allows it (the Dell takes jobs of
<= 3 GB), lists the file's columns, and, when the file carries a plant name column, also
prints a few columns of the rows of plants whose name contains one of the battery plants EIA
named for 2026 (a name search, so each hit is still checked by eye).

    python spot.py --data-dir /data --out-dir /out
"""

import argparse
import glob
import os

import pandas as pd

VERSION = "0.2.0"
# The largest December-2025-book solar generators that left the 2026 book by August 2026,
# one of each kind (plan_flows_generators.csv from job plan-flows-v1).
GENERATORS = (
    ("65855", "TE1PV"),   # L -> V, 2026-10 -> 2027-05, 836.8 -> 644.8 MW
    ("65310", "DAWN1"),   # T, 2026-12 -> 2027-12
    ("66138", "INMA1"),   # T, 2026-05 -> 2029-03
    ("68231", "SDTWO"),   # P, 2026-12 -> not listed
    ("67123", "MISII"),   # V, 2026-03 -> operating, online 2025-12
)
# Battery plants EIA's Today in Energy 67205 (2026-02-20) named among 2026's largest.
NAMES = ("tehuacana", "lunis", "clear fork", "bellefield")
NAME_COLUMNS = ("plant_name_eia", "plant_name")


def select(df, generators=GENERATORS):
    """Rows of `df` for the named (plant, generator) pairs, oldest report first."""
    plant = pd.to_numeric(df["plant_id_eia"], errors="coerce").astype("Int64").astype(str)
    gen = df["generator_id"].astype(str).str.strip()
    want = {p + "/" + g for p, g in generators}
    out = df[(plant + "/" + gen).isin(want)].copy()
    out["_key"] = (plant + "/" + gen)[out.index]
    return out.sort_values(["_key", "report_date"], kind="mergesort")


def by_name(df, names=NAMES):
    """Rows whose plant name contains one of `names` (case-blind), keyed plant/generator."""
    col = next((c for c in NAME_COLUMNS if c in df.columns), None)
    if col is None:
        return None
    text = df[col].astype(str).str.lower()
    hit = df[text.str.contains("|".join(names), regex=True)]
    keys = {(str(p), str(g).strip()) for p, g in zip(pd.to_numeric(hit["plant_id_eia"], errors="coerce")
                                                     .astype("Int64").astype(str), hit["generator_id"])}
    return select(df, tuple(sorted(keys)))


def render(rows, columns=None, named=None):
    lines = ["# Raw PUDL records for the plan-flows spot check (spot %s)" % VERSION, ""]
    if columns is not None:
        lines += ["Columns in the parquet: " + ", ".join(columns), ""]
    for key, g in rows.groupby("_key", sort=False):
        lines += ["## " + key, "", "```", g.drop(columns=["_key"]).T.to_string(), "```", ""]
    if rows.empty:
        lines.append("No records found.")
    if named is None:
        lines += ["", "## Battery plants by name", "", "No plant name column in this file."]
    else:
        lines += ["", "## Battery plants by name (%s)" % ", ".join(NAMES), ""]
        if named.empty:
            lines.append("No plant name matched.")
        keep = [c for c in ("_key", "report_date", "valid_until_date") + NAME_COLUMNS + (
            "technology_description", "operational_status_code", "current_planned_generator_operating_date",
            "generator_operating_date", "capacity_mw", "summer_capacity_mw") if c in named.columns]
        if not named.empty:
            lines += ["```", named[keep].to_string(index=False), "```"]
    return "\n".join(lines)


NAMED_READ = ("plant_id_eia", "generator_id", "report_date", "valid_until_date") + NAME_COLUMNS + (
    "technology_description", "operational_status_code", "current_planned_generator_operating_date",
    "generator_operating_date", "capacity_mw", "summer_capacity_mw")


def read(path):
    """The parquet's columns; every column of the wanted plants' rows (all rows if the filter fails);
    and, if there is a plant name column, a few columns of every row for the name search."""
    import pyarrow.parquet as pq
    columns = pq.read_schema(path).names
    try:
        df = pd.read_parquet(path, filters=[("plant_id_eia", "in", sorted({int(p) for p, _ in GENERATORS}))])
    except Exception:  # noqa: BLE001 - fall back to the plain read
        df = pd.read_parquet(path)
    names = None
    if any(c in columns for c in NAME_COLUMNS):
        names = pd.read_parquet(path, columns=[c for c in NAMED_READ if c in columns])
    return columns, df, names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    hits = sorted(glob.glob(os.path.join(a.data_dir, "**", "*changelog_generators*.parquet"), recursive=True))
    if not hits:
        raise SystemExit("no changelog_generators parquet under %s" % a.data_dir)
    columns, df, names = read(hits[0])
    rows = select(df)
    named = by_name(names) if names is not None else None
    rows.drop(columns=["_key"]).to_csv(os.path.join(a.out_dir, "spot.csv"), index=False)
    if named is not None:
        named.drop(columns=["_key"]).to_csv(os.path.join(a.out_dir, "spot_named.csv"), index=False)
    md = render(rows, columns, named)
    with open(os.path.join(a.out_dir, "spot.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
