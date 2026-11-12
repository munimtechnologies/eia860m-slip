"""Pre-registered measurement for PUDL issue #5681 (pre-registration id spboil-1): what would
keeping `boiler_id` in core_epa__assn_eia_epacamd_subplant_ids (step 1) and adding it to the
NetworkX subplant analysis (step 2) change?

Plan with every bar: docs/spboil-plan.md in munimtechnologies/eia860m-slip. This script:

  1. waits until the plan is live (no data is read before that);
  2. downloads four of PUDL's nightly tables: the EPA-EIA crosswalk, the published subplant table,
     the EIA-860 boiler-generator associations and the EIA-860 generators (two columns);
  3. rebuilds the subplant table the way PUDL's glue asset does (unique crosswalk, the three
     augment merges, the dedup, the combustor-generator graph with unit_id_pudl folded in), and
     checks the rebuild against the published table (gate G1);
  4. step 1: counts the rows that keeping boiler_id would add, how many of them would trip the
     current (combustor, generator) row-count assertion, and how many rows would have a null
     boiler_id;
  5. step 2: adds boiler nodes, first from the crosswalk's own boiler_id (variant "xw"), then also
     from the EIA-860 boiler-generator associations (variant "xw_bga"), and counts the plants whose
     subplant grouping changes and the boilers that bridge two of today's subplants.

PUDL's data (CC BY 4.0) is downloaded at run time and not stored here. The rebuild follows
PUDL's src/pudl/dagster/assets/core/glue.py (MIT, Catalyst Cooperative) but is written anew.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import collections
import io
import json
import os
import time
import urllib.request

import networkx as nx
import pandas as pd

VERSION = "0.1.0"
NIGHTLY = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/%s.parquet"
TABLES = {
    "xw": "core_epa__assn_eia_epacamd",
    "sp": "core_epa__assn_eia_epacamd_subplant_ids",
    "bga": "core_eia860__assn_boiler_generator",
    "gens": "core_eia860__scd_generators",
}
COLUMNS = {
    "xw": ["report_year", "plant_id_epa", "emissions_unit_id_epa", "generator_id_epa",
           "plant_id_eia", "boiler_id", "generator_id"],
    "sp": ["plant_id_eia", "plant_id_epa", "subplant_id", "unit_id_pudl",
           "emissions_unit_id_epa", "generator_id"],
    "bga": ["plant_id_eia", "generator_id", "boiler_id", "unit_id_pudl"],
    "gens": ["plant_id_eia", "generator_id"],
}
ID_COLS = ("emissions_unit_id_epa", "generator_id_epa", "boiler_id", "generator_id")
INT_COLS = ("plant_id_eia", "plant_id_epa", "unit_id_pudl", "subplant_id", "report_year")
DEDUP = ["plant_id_eia", "plant_id_epa", "emissions_unit_id_epa", "generator_id", "unit_id_pudl"]
ROW_KEY = ["plant_id_epa", "emissions_unit_id_epa", "generator_id", "unit_id_pudl"]
MANUAL_PLANT = 1391
WATCH_PLANT = 52151
GATE_PLANT_SHARE = 0.99
GATE_ROW_TOL = 0.01
P2_SHARE = 0.02
P3_EXTRA = 5
P4_SHARE = 0.01
P5_NULL_SHARE = 0.5
UA = {"User-Agent": "mv2-spboil/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(url, timeout=600):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers)


def wait_for(url, token, minutes):
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if token in fetch(url, 60)[0].decode("utf-8", "replace"):
                return True, polls, now()
        except Exception:
            pass
        if time.time() > deadline:
            return False, polls, now()
        time.sleep(60)


def isnull(x):
    return x is None or (not isinstance(x, (str, tuple)) and pd.isna(x))


def normalize(df):
    df = df.copy()
    for col in INT_COLS:
        if col in df.columns:
            df[col] = df[col].astype("Int64")
    for col in ID_COLS:
        if col in df.columns:
            df[col] = df[col].astype("object").where(df[col].notna(), None)
    return df


def load(key, raw):
    return normalize(pd.read_parquet(io.BytesIO(raw), columns=COLUMNS[key]))


# ---- the rebuild (follows PUDL's glue asset) ---------------------------------------------------

def unique_crosswalk(xw):
    """Mirror of _core_epa__assn_eia_epacamd_unique: drop rows duplicated apart from report_year,
    and where one EPA unit maps to two EIA plants in different years drop its 2018 rows."""
    cols = [c for c in xw.columns if c != "report_year"]
    d = xw.drop_duplicates(subset=cols)
    one_to_many = (
        d.sort_values("report_year")
        .groupby(["plant_id_epa", "emissions_unit_id_epa"])
        .filter(lambda x: x.plant_id_eia.nunique() > 1 and x.report_year.nunique() > 1)
    )
    dropped = one_to_many[one_to_many["report_year"].eq(2018).fillna(False).astype(bool)]
    return d.drop(dropped.index).drop(columns=["report_year"]), int(len(dropped))


def epa_units(sp):
    """Every (plant_id_eia, emissions_unit_id_epa) in the published table: a superset of
    _core_epacems__emissions_unit_ids (not published), equal to it for the outer merge."""
    u = sp[sp["emissions_unit_id_epa"].notna()][["plant_id_eia", "emissions_unit_id_epa"]]
    return u.drop_duplicates().reset_index(drop=True)


def augment(unique, gens, units, bga):
    """The three augment_crosswalk_with_* merges, in PUDL's order."""
    g = gens[["plant_id_eia", "generator_id"]].drop_duplicates()
    d = unique.merge(g, how="outer", on=["plant_id_eia", "generator_id"], validate="m:1")
    d["plant_id_epa"] = d["plant_id_epa"].fillna(d["plant_id_eia"])
    d["emissions_unit_id_epa"] = d["emissions_unit_id_epa"].where(
        d["emissions_unit_id_epa"].notna(), d["generator_id"])
    d = d.merge(units, how="outer", on=["plant_id_eia", "emissions_unit_id_epa"], validate="m:m")
    u = bga[["plant_id_eia", "generator_id", "unit_id_pudl"]].drop_duplicates()
    extra = int(u.duplicated(["plant_id_eia", "generator_id"]).sum())
    if extra:  # PUDL's validate="m:1" would raise; keep the non-null unit and count it
        u = u.sort_values("unit_id_pudl").drop_duplicates(["plant_id_eia", "generator_id"])
    d = d.merge(u, how="outer", on=["plant_id_eia", "generator_id"], validate="m:1")
    return normalize(d).reset_index(drop=True), extra


def collapse(d, keep_boiler=False):
    sub = DEDUP + (["boiler_id"] if keep_boiler else [])
    return d.drop_duplicates(subset=sub).reset_index(drop=True)


def node_columns(d):
    """(combustor, generator) node of every row; a missing id becomes a per-row sentinel."""
    comb, gen = [], []
    for i, (p, u, g) in enumerate(zip(d["plant_id_eia"], d["emissions_unit_id_epa"],
                                      d["generator_id"])):
        p = None if isnull(p) else int(p)
        comb.append(("combustor", p, ("row", i) if isnull(u) else u))
        gen.append(("generator", p, ("row", i) if isnull(g) else g))
    return comb, gen


def anchor(p, u, g):
    """The node a crosswalk row's boiler hangs on: its generator, else its EPA unit."""
    p = None if isnull(p) else int(p)
    if not isnull(g):
        return ("generator", p, g)
    if not isnull(u):
        return ("combustor", p, u)
    return None


def components(d, extra_edges=()):
    """Connected-component label of every row (combustor-generator edges, generator-unit_id_pudl
    edges, plus any extra edges), as PUDL's _subplant_ids_from_prepped_crosswalk does."""
    comb, gen = node_columns(d)
    graph = nx.Graph()
    graph.add_edges_from(zip(comb, gen))
    duplicate_edges = len(d) - graph.number_of_edges()
    for gn, p, u in zip(gen, d["plant_id_eia"], d["unit_id_pudl"]):
        if not isnull(u):
            graph.add_edge(gn, ("unit", None if isnull(p) else int(p), int(u)))
    graph.add_edges_from(extra_edges)
    label = {}
    for i, nodes in enumerate(nx.connected_components(graph)):
        for n in nodes:
            label[n] = i
    return [label[c] for c in comb], label, duplicate_edges


def with_manual(d, labels):
    """PUDL's manually_update_subplant_id: all of plant 1391 is one subplant."""
    out = list(labels)
    for i, p in enumerate(d["plant_id_eia"]):
        if not isnull(p) and int(p) == MANUAL_PLANT:
            out[i] = "manual"
    return out


def row_keys(d):
    keys = []
    for row in zip(*(d[c] for c in ROW_KEY)):
        keys.append(tuple("<NA>" if isnull(x) else (int(x) if not isinstance(x, str) else x)
                          for x in row))
    return keys


def partitions(plants, labels, keys):
    """plant -> frozenset of frozensets of row keys (labels themselves are ignored)."""
    groups = collections.defaultdict(lambda: collections.defaultdict(set))
    for i, (p, lab, k) in enumerate(zip(plants, labels, keys)):
        lab = ("null", i) if isnull(lab) else lab
        groups[None if isnull(p) else int(p)][lab].add(k)
    return {p: frozenset(frozenset(s) for s in g.values()) for p, g in groups.items()}


def compare(before, after):
    plants = sorted(set(before) | set(after), key=lambda x: (x is None, x))
    return [p for p in plants if before.get(p) != after.get(p)]


# ---- step 2: boiler nodes ----------------------------------------------------------------------

def xw_boiler_edges(d):
    edges = set()
    skipped = 0
    for p, u, g, b in zip(d["plant_id_eia"], d["emissions_unit_id_epa"], d["generator_id"],
                          d["boiler_id"]):
        if isnull(b):
            continue
        a = anchor(p, u, g)
        if a is None:
            skipped += 1
            continue
        edges.add((a, ("boiler", a[1], b)))
    return sorted(edges, key=repr), skipped


def bga_boiler_edges(bga):
    e = bga[bga["boiler_id"].notna() & bga["generator_id"].notna() & bga["plant_id_eia"].notna()]
    e = e[["plant_id_eia", "generator_id", "boiler_id"]].drop_duplicates()
    return sorted({(("generator", int(p), g), ("boiler", int(p), b))
                   for p, g, b in zip(e["plant_id_eia"], e["generator_id"], e["boiler_id"])},
                  key=repr)


def bridging_boilers(edges, base_label):
    """Boilers whose neighbours sit in two or more of today's subplants."""
    by_boiler = collections.defaultdict(set)
    gens = collections.defaultdict(set)
    for a, b in edges:
        if a in base_label:
            by_boiler[b].add(base_label[a])
        if a[0] == "generator":
            gens[b].add(a[2])
    out = []
    for b, labs in by_boiler.items():
        if len(labs) > 1:
            out.append({"plant_id_eia": b[1], "boiler_id": b[2], "subplants_joined": len(labs),
                        "generators": ";".join(sorted(str(g) for g in gens[b]))})
    return sorted(out, key=lambda r: (r["plant_id_eia"], str(r["boiler_id"])))


def variant(base, edges, keys, base_part):
    labels, label_map, _ = components(base, edges)
    part = partitions(base["plant_id_eia"], with_manual(base, labels), keys)
    changed = compare(base_part, part)
    rows = []
    for p in changed:
        rows.append({"plant_id_eia": p, "subplants_before": len(base_part.get(p, ())),
                     "subplants_after": len(part.get(p, ()))})
    return part, changed, rows


# ---- scoring -----------------------------------------------------------------------------------

def score(m):
    g1 = (m["rebuild_plant_share_identical"] >= GATE_PLANT_SHARE
          and abs(m["rebuild_rows"] - m["published_rows"]) <= GATE_ROW_TOL * m["published_rows"])
    return {
        "G1": bool(g1),
        "P1": m["xw"]["plants_changed"] >= 1,
        "P2": m["xw"]["plants_changed"] < P2_SHARE * m["plants_with_crosswalk_match"],
        "P3": m["xw_bga"]["plants_changed"] <= m["xw"]["plants_changed"] + P3_EXTRA,
        "P4": m["step1"]["extra_rows"] >= P4_SHARE * m["rebuild_rows"],
        "P5": m["step1"]["null_boiler_share"] > P5_NULL_SHARE,
    }


def measure(xw, sp, bga, gens):
    m = {}
    unique, dropped_2018 = unique_crosswalk(xw)
    m["unique_crosswalk_rows"] = int(len(unique))
    m["unique_2018_rows_dropped"] = dropped_2018
    matched = unique[unique["emissions_unit_id_epa"].notna() & unique["generator_id"].notna()]
    m["plants_with_crosswalk_match"] = int(matched["plant_id_eia"].nunique())
    m["crosswalk_match_rows_with_boiler"] = int(matched["boiler_id"].notna().sum())
    d, bga_conflicts = augment(unique, gens, epa_units(sp), bga)
    m["bga_unit_conflicts"] = bga_conflicts
    base = collapse(d)
    m["rebuild_rows"] = int(len(base))
    m["published_rows"] = int(len(sp))
    labels, base_label, dup_edges = components(base)
    m["rebuild_duplicate_edges"] = int(dup_edges)
    keys = row_keys(base)
    base_part = partitions(base["plant_id_eia"], with_manual(base, labels), keys)
    pub_part = partitions(sp["plant_id_eia"], list(sp["subplant_id"]), row_keys(sp))
    differ = compare(pub_part, base_part)
    m["plants_total"] = len(base_part)
    m["rebuild_plants_differing"] = len(differ)
    m["rebuild_plants_differing_sample"] = differ[:25]
    m["rebuild_plant_share_identical"] = (1 - len(differ) / max(len(pub_part), 1))
    m["subplants_total"] = int(sum(len(v) for v in base_part.values()))

    # step 1: keep boiler_id
    keep = collapse(d, keep_boiler=True)
    comb, gen = node_columns(keep)
    pairs = collections.Counter(zip(comb, gen))
    m["step1"] = {
        "rows": int(len(keep)),
        "extra_rows": int(len(keep) - len(base)),
        "null_boiler_rows": int(keep["boiler_id"].isna().sum()),
        "null_boiler_share": float(keep["boiler_id"].isna().mean()) if len(keep) else 0.0,
        "rows_in_repeated_pairs": int(sum(c for c in pairs.values() if c > 1)),
        "extra_rows_plants": int(keep[keep.duplicated(DEDUP, keep=False)]["plant_id_eia"]
                                 .nunique()),
    }

    # step 2: boiler nodes
    e_xw, skipped = xw_boiler_edges(d)
    e_bga = bga_boiler_edges(bga)
    m["boiler_edges_xw"] = len(e_xw)
    m["boiler_edges_xw_skipped_no_anchor"] = skipped
    m["boiler_edges_bga"] = len(e_bga)
    detail = {}
    for name, edges in (("xw", e_xw), ("xw_bga", sorted(set(e_xw) | set(e_bga), key=repr))):
        part, changed, rows = variant(base, edges, keys, base_part)
        bridges = bridging_boilers(edges, base_label)
        before = sum(r["subplants_before"] for r in rows)
        after = sum(r["subplants_after"] for r in rows)
        m[name] = {"plants_changed": len(changed), "subplants_before_in_changed": before,
                   "subplants_after_in_changed": after, "subplants_merged_away": before - after,
                   "bridging_boilers": len(bridges),
                   "plants_with_bridging_boiler": len({b["plant_id_eia"] for b in bridges})}
        detail[name] = {"rows": rows, "bridges": bridges, "part": part}

    w = WATCH_PLANT
    m["watch_plant"] = {
        "plant_id_eia": w,
        "crosswalk_rows": unique[unique["plant_id_eia"].eq(w).fillna(False).astype(bool)][
            ["emissions_unit_id_epa", "boiler_id", "generator_id"]].astype(str)
        .values.tolist(),
        "bga_pairs": bga[bga["plant_id_eia"].eq(w).fillna(False).astype(bool)][
            ["boiler_id", "generator_id"]]
        .drop_duplicates().astype(str).values.tolist(),
        "subplants_today": len(base_part.get(w, ())),
        "subplants_xw": len(detail["xw"]["part"].get(w, ())),
        "subplants_xw_bga": len(detail["xw_bga"]["part"].get(w, ())),
    }
    return m, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--wait-for")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=240)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"version": VERSION, "started": now()}
    out_json = os.path.join(args.out_dir, "spboil.json")
    if args.wait_for:
        live, polls, at = wait_for(args.wait_for, args.token, args.minutes)
        res["plan_live"] = {"live": live, "polls": polls, "at": at}
        if not live:
            res["stopped"] = "plan page not live; no data read"
            with open(out_json, "w") as fh:
                json.dump(res, fh, indent=1)
            print(res["stopped"])
            return
    frames = {}
    res["downloads"] = {}
    for key, table in TABLES.items():
        for attempt in range(3):
            try:
                raw, headers = fetch(NIGHTLY % table)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(30)
        frames[key] = load(key, raw)
        res["downloads"][table] = {"bytes": len(raw), "rows": int(len(frames[key])),
                                   "last_modified": headers.get("Last-Modified"),
                                   "etag": headers.get("ETag")}
        del raw
        print(table, res["downloads"][table], flush=True)
    m, detail = measure(frames["xw"], frames["sp"], frames["bga"], frames["gens"])
    res["measures"] = m
    res["scores"] = score(m)
    for name in ("xw", "xw_bga"):
        pd.DataFrame(detail[name]["rows"], columns=["plant_id_eia", "subplants_before",
                                                    "subplants_after"]).to_csv(
            os.path.join(args.out_dir, "spboil-changed-%s.csv" % name), index=False)
        pd.DataFrame(detail[name]["bridges"], columns=["plant_id_eia", "boiler_id",
                                                       "subplants_joined", "generators"]).to_csv(
            os.path.join(args.out_dir, "spboil-bridges-%s.csv" % name), index=False)
    res["finished"] = now()
    with open(out_json, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in m.items() if k != "watch_plant"}, indent=1, default=str))
    print("scores", json.dumps(res["scores"]))


if __name__ == "__main__":
    main()
