"""cellmakeup: which generators make up the stage-by-lead cells of the twenty-second result
(docs/stage-leadtime.md), above all the thin U and V cells 13-24 months out. Description, not a
scored check: no predictions were stated.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

It rebuilds leadtime.py's rows (commit 9ee085b) on the same data, checks that the four cells it
reads match the published ones (K1), and for each cell gives the MW share by technology group, the
ten generators and the ten plants with the most MW summed over the cell's rows, and how much of
the cell those ten hold.

    python cellmakeup.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import pandas as pd

import eia860m_slip as es
import leadtime as lt

__version__ = "0.1.0"

CELLS = (("U", "13-24"), ("V", "13-24"), ("U", "00-03"), ("V", "00-03"))
# K1: the published cells (docs/stage-leadtime.md, "Every cell" and the L1/L3 results):
# rows, generators, MW, on-time share.
PUBLISHED = {("U", "13-24"): (4138, 506, 636740.1, 0.2457),
             ("V", "13-24"): (315, 79, 57078.8, 0.1389),
             ("U", "00-03"): (5131, 1774, 190762.7, 0.3017),
             ("V", "00-03"): (11795, 3421, 627147.3, 0.4088)}
TOP = 10
GROUP_COLS = ["group", "rows", "generators", "mw", "mw_share", "on_time_share"]
GEN_COLS = ["key", "plant", "state", "group", "capacity_mw", "rows", "mw", "mw_share",
            "planned_first", "planned_last", "online", "on_time_share", "not_online_share"]
PLANT_COLS = ["plant_id", "plant", "state", "generators", "rows", "mw", "mw_share",
              "on_time_share"]


def _text(x):
    return x if isinstance(x, str) else None


def names(df):
    """Each generator's plant name and state from its latest record."""
    last = df.sort_values("report_m", kind="mergesort").groupby("key").tail(1).set_index("key")
    return last[["plant_name_eia", "state"]]


def _mw(f, outcome=None):
    return float(f["mw"].sum() if outcome is None else f.loc[f["outcome"] == outcome, "mw"].sum())


def makeup(f, nm, top=TOP):
    """Technology groups, top generators and top plants of one cell's rows."""
    total = _mw(f)
    groups = []
    for g, h in f.groupby("group", dropna=False):
        mw = _mw(h)
        groups.append({"group": _text(g) or "other", "rows": int(len(h)),
                       "generators": int(h["key"].nunique()), "mw": round(mw, 1),
                       "mw_share": lt._share(mw, total),
                       "on_time_share": lt._share(_mw(h, "on_time"), mw)})
    groups.sort(key=lambda x: (-x["mw"], x["group"]))
    gens = []
    for k, h in f.groupby("key"):
        mw = _mw(h)
        gens.append({"key": k,
                     "plant": _text(nm.at[k, "plant_name_eia"]) if k in nm.index else None,
                     "state": _text(nm.at[k, "state"]) if k in nm.index else None,
                     "group": _text(h["group"].iloc[0]) or "other",
                     "capacity_mw": round(float(h["mw"].max()), 1), "rows": int(len(h)),
                     "mw": round(mw, 1), "mw_share": lt._share(mw, total),
                     "planned_first": es.month_str(h["planned_m"].min()),
                     "planned_last": es.month_str(h["planned_m"].max()),
                     "online": es.month_str(h["online_m"].iloc[0]),
                     "on_time_share": lt._share(_mw(h, "on_time"), mw),
                     "not_online_share": lt._share(_mw(h, "not_online_12"), mw)})
    gens.sort(key=lambda x: (-x["mw"], x["key"]))
    f = f.assign(plant_id=[k.split("/", 1)[0] for k in f["key"]])
    plants = []
    for p, h in f.groupby("plant_id"):
        k = h["key"].iloc[0]
        mw = _mw(h)
        plants.append({"plant_id": p,
                       "plant": _text(nm.at[k, "plant_name_eia"]) if k in nm.index else None,
                       "state": _text(nm.at[k, "state"]) if k in nm.index else None,
                       "generators": int(h["key"].nunique()), "rows": int(len(h)),
                       "mw": round(mw, 1), "mw_share": lt._share(mw, total),
                       "on_time_share": lt._share(_mw(h, "on_time"), mw)})
    plants.sort(key=lambda x: (-x["mw"], x["plant_id"]))
    top_gen_mw = sum(g["mw"] for g in gens[:top])
    top_plant_mw = sum(p["mw"] for p in plants[:top])
    return {"generators": len(gens), "plants": len(plants), "mw": round(total, 1),
            "top_generators_share": lt._share(top_gen_mw, total),
            "top_plants_share": lt._share(top_plant_mw, total),
            "largest_plant_share": plants[0]["mw_share"] if plants else None,
            "groups": groups, "top_generators": gens[:top], "top_plants": plants[:top]}


def k1(c):
    """K1: the cells read here are the published cells."""
    out, ok = {}, True
    for st, b in CELLS:
        got = lt.cell(c[(c["stage_group"] == st) & (c["band"] == b)])
        want = PUBLISHED[(st, b)]
        g = (got["rows"], got["generators"], got["mw"], got["on_time_share"])
        same = (g[0] == want[0] and g[1] == want[1] and abs(g[2] - want[2]) <= 0.05
                and g[3] == want[3])
        out["%s %s" % (st, b)] = {"got": list(g), "published": list(want), "pass": bool(same)}
        ok = ok and same
    return {"cells": out, "pass": bool(ok)}


def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join("" if r.get(c) is None else str(r.get(c)) for c in cols)
                   + " |")
    return out


def write_md(path, meta, res):
    lines = ["# Which generators make up the stage-by-lead cells", "",
             "cellmakeup %s on leadtime %s and eia860m-slip %s; data %s (latest report %s), report "
             "months %s to %s. MV2 of Munim, Inc. (made with AI agents). Description, not a scored "
             "check. Code Apache-2.0; tables CC BY 4.0." % (
                 meta["version"], meta["leadtime"], meta["eia860m_slip"], meta["source"],
                 meta["report_max"], meta["first_month"], meta["last_month"]), "",
             "MW is summed over a cell's rows (one row per generator and report month), as in "
             "docs/stage-leadtime.md, so a generator listed in many reports weighs more.", "",
             "## K1: the cells match the published ones", "", "```",
             json.dumps(res["K1"], indent=1), "```"]
    for cell in res["cells"]:
        head = "%s, %s months" % (cell["stage"], cell["band"])
        lines += ["", "## %s" % head, "",
                  "%d generators at %d plants, %s MW over rows. The ten largest generators hold "
                  "%s of it, the ten largest plants %s, the largest plant %s." % (
                      cell["generators"], cell["plants"], cell["mw"],
                      cell["top_generators_share"], cell["top_plants_share"],
                      cell["largest_plant_share"]),
                  "", "### By technology group", ""]
        lines += md_table(cell["groups"], GROUP_COLS)
        lines += ["", "### Ten largest generators", ""]
        lines += md_table(cell["top_generators"], GEN_COLS)
        lines += ["", "### Ten largest plants", ""]
        lines += md_table(cell["top_plants"], PLANT_COLS)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    cols = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in cols]))
    last_m = int(df["report_m"].max())
    c = lt.rows(df, last_m)
    nm = names(df)
    res = {"K1": k1(c), "cells": []}
    for st, b in CELLS:
        f = c[(c["stage_group"] == st) & (c["band"] == b)]
        res["cells"].append(dict(stage=st, band=b, **makeup(f, nm)))
    meta = {"version": __version__, "leadtime": lt.__version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "report_max": es.month_str(last_m),
            "first_month": es.month_str(lt.START_M),
            "last_month": es.month_str(lt.end_month(last_m))}
    with open(os.path.join(args.out_dir, "cellmakeup.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "cellmakeup.md"), meta, res)
    print(json.dumps({"meta": meta, "K1": res["K1"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
