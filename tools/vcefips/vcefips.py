# Copyright 2026 Munim, Inc.
# Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""vcefips: two place_name tests on PUDL's VCE RARE table that can never fail.

PUDL's out_vcerare__hourly_available_capacity_factor carries two
dbt_expectations tests on place_name (dbt/schema_inputs/pudl/vcerare/
out_vcerare__hourly_available_capacity_factor/schema.human.yml, main 2026-11-12):

1. expect_column_values_to_be_in_set ['oglala lakota'] with
   row_condition county_id_fips = '46012'. PR #4319 (2025-06-12) added it to
   guard the Shannon -> Oglala Lakota rename (#3914), and the docs that PR
   removed say "The VCE data includes the new FIPS code (46102)". 46012 is not
   a county: the Census 2020 South Dakota list goes 46011 (Brookings), 46013
   (Brown); Oglala Lakota is 46102. With no rows selected, the test passes
   whatever the place name is.
2. expect_column_values_to_not_be_in_set [bedford_city, clifton_forge_city,
   lake_hurron, lake_st_clair]. Since #4319, _standardize_census_names replaces
   every '_' in place_name with ' ', so no value with an underscore can appear.
   #4319 also went back to the 'lake_st_clair_michigan' spelling on purpose, so
   'lake st clair' is now an expected place name.

This script reads only the county_id_fips and place_name columns of PUDL's
nightly parquet over HTTP (DuckDB), counts rows per (county_id_fips,
place_name), and scores pre-registered predictions V1-V4 and controls C1-C2
(docs/vcefips.md). It only measures; nothing is sent to PUDL.
"""
import argparse
import csv
import json
import os
import sys
import time

TOOL = "vcefips 0.1.0"
URL = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
       "out_vcerare__hourly_available_capacity_factor.parquet")
TEST_FIPS = "46012"       # the row_condition as written
INTENDED_FIPS = "46102"   # Oglala Lakota County, SD (Census 2020; PR #4319 docs)
OLD_SHANNON_FIPS = "46113"
EXPECTED_NAME = "oglala lakota"
NOT_IN_SET = ["bedford_city", "clifton_forge_city", "lake_hurron", "lake_st_clair"]


def in_set_failures(groups, fips, value_set):
    """Rows the dbt_expectations in-set test would return for a row_condition
    county_id_fips = '<fips>': rows whose place_name is NULL or not in the set.

    groups: list of (county_id_fips, place_name, n_rows)."""
    bad = 0
    selected = 0
    for f, name, n in groups:
        if f != fips:
            continue
        selected += n
        if name is None or name not in value_set:
            bad += n
    return selected, bad


def not_in_set_failures(groups, value_set):
    """Rows the not-in-set test would return: place_name in the set."""
    return sum(n for _, name, n in groups if name is not None and name in value_set)


def spaced(values):
    return [v.replace("_", " ") for v in values]


def score(groups):
    """Score V1-V4 and C1-C2 from (county_id_fips, place_name, n_rows) groups."""
    res = {}
    sel_test, bad_test = in_set_failures(groups, TEST_FIPS, [EXPECTED_NAME])
    sel_int, bad_int = in_set_failures(groups, INTENDED_FIPS, [EXPECTED_NAME])
    names_int = sorted({str(name) for f, name, _ in groups if f == INTENDED_FIPS})
    res["V1"] = {
        "claim": "zero rows have county_id_fips = '46012', so the test as written selects nothing",
        "rows_46012": sel_test, "failing_rows_as_written": bad_test,
        "held": sel_test == 0,
    }
    res["V2"] = {
        "claim": "rows with county_id_fips = '46102' exist and all have place_name 'oglala lakota'",
        "rows_46102": sel_int, "failing_rows_corrected": bad_int,
        "place_names_46102": names_int,
        "held": sel_int > 0 and bad_int == 0,
    }
    underscored = sorted({name for _, name, _ in groups if name is not None and "_" in name})
    res["V3"] = {
        "claim": "no place_name contains '_', so the not-in-set test as written returns 0 rows",
        "place_names_with_underscore": underscored[:50],
        "n_place_names_with_underscore": len(underscored),
        "failing_rows_as_written": not_in_set_failures(groups, NOT_IN_SET),
        "held": len(underscored) == 0 and not_in_set_failures(groups, NOT_IN_SET) == 0,
    }
    names = {name for _, name, _ in groups if name is not None}
    st_clair_fips = sorted({str(f) for f, name, _ in groups if name == "lake st clair"})
    res["V4"] = {
        "claim": ("'lake st clair' and 'lake huron' are present (lake st clair with NULL "
                  "county_id_fips); 'lake hurron', 'bedford city', 'clifton forge city' are absent"),
        "lake_st_clair_present": "lake st clair" in names,
        "lake_st_clair_fips": st_clair_fips,
        "lake_huron_present": "lake huron" in names,
        "lake_hurron_present": "lake hurron" in names,
        "bedford_city_present": "bedford city" in names,
        "clifton_forge_city_present": "clifton forge city" in names,
        "rows_spaced_forms": not_in_set_failures(groups, spaced(NOT_IN_SET)),
        "held": ("lake st clair" in names and "lake huron" in names
                 and st_clair_fips == ["None"]
                 and "lake hurron" not in names and "bedford city" not in names
                 and "clifton forge city" not in names),
    }
    # Controls: the same query machinery must report failures where they exist.
    _, bad_c1 = in_set_failures(groups, INTENDED_FIPS, ["shannon"])
    res["C1"] = {
        "claim": "in-set test at '46102' with a wrong expected name ('shannon') fails on every 46102 row",
        "failing_rows": bad_c1, "rows_46102": sel_int,
        "held": sel_int > 0 and bad_c1 == sel_int,
    }
    _, bad_c1b = in_set_failures(groups, TEST_FIPS, ["shannon"])
    res["C1b"] = {
        "claim": "the as-written row_condition ('46012') with the same wrong name still returns 0 rows",
        "failing_rows": bad_c1b, "held": bad_c1b == 0,
    }
    res["C2"] = {
        "claim": "not-in-set with the four values in space form returns > 0 rows (lake st clair)",
        "failing_rows": not_in_set_failures(groups, spaced(NOT_IN_SET)),
        "held": not_in_set_failures(groups, spaced(NOT_IN_SET)) > 0,
    }
    # Exploratory, no prediction.
    res["explore"] = {
        "n_groups": len(groups),
        "n_rows": sum(n for _, _, n in groups),
        "n_fips": len({f for f, _, _ in groups if f is not None}),
        "rows_null_fips": sum(n for f, _, n in groups if f is None),
        "null_fips_place_names": sorted({str(name) for f, name, _ in groups if f is None}),
        "rows_46113": sum(n for f, _, n in groups if f == OLD_SHANNON_FIPS),
        "fips_with_more_than_one_name": sorted(
            f for f in {f for f, _, _ in groups if f is not None}
            if len({name for g, name, _ in groups if g == f}) > 1),
    }
    return res


def fetch_groups(url, threads=2, memory_limit="700MB"):
    import duckdb  # imported here so the unit tests run without it
    con = duckdb.connect()
    con.execute("SET threads=%d" % threads)
    con.execute("SET memory_limit='%s'" % memory_limit)
    try:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")
    except Exception as e:  # autoload may already cover it
        print("httpfs note:", e, file=sys.stderr)
    lit = "'" + url.replace("'", "''") + "'"
    meta = con.execute(
        "SELECT num_rows, num_row_groups, created_by FROM parquet_file_metadata(%s)"
        % lit).fetchall()
    rows = con.execute(
        "SELECT CAST(county_id_fips AS VARCHAR), CAST(place_name AS VARCHAR), COUNT(*) "
        "FROM read_parquet(%s) GROUP BY 1, 2 ORDER BY 1, 2" % lit).fetchall()
    groups = [(f, name, int(n)) for f, name, n in rows]
    return groups, [list(m) for m in meta]


def main(argv=None):
    ap = argparse.ArgumentParser(description=TOOL)
    ap.add_argument("--url", default=URL)
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    t0 = time.time()
    groups, meta = fetch_groups(args.url)
    with open(os.path.join(args.out_dir, "vcefips-groups.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["county_id_fips", "place_name", "n_rows"])
        for f, name, n in groups:
            w.writerow(["" if f is None else f, "" if name is None else name, n])
    res = score(groups)
    res["meta"] = {"tool": TOOL, "url": args.url, "parquet_metadata": meta,
                   "seconds": round(time.time() - t0, 1),
                   "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(os.path.join(args.out_dir, "vcefips-results.json"), "w",
              encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    for k in ["V1", "V2", "V3", "V4", "C1", "C1b", "C2"]:
        print(k, "HELD" if res[k]["held"] else "FAILED", json.dumps(res[k], sort_keys=True))
    print("explore", json.dumps(res["explore"], sort_keys=True))
    print("meta", json.dumps(res["meta"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
