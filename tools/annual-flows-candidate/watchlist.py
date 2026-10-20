"""watchlist: which planned U.S. generators changed stage or planned month in one EIA-860M report?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Compares each generator's record in force in report r - 1 with its record in force in report r
(default r: the latest report in the file) and lists every planned generator that changed:

    change         in report r - 1                    in report r
    forward        early, approved or building        a later planned band
    backward       early, approved or building        an earlier planned band
    to_operating   early, approved or building        operating (OP, SB, OS, OA)
    exit_other     early, approved or building        any other status (OT, IP, CN, RE, ...)
    left           early, approved or building        no record in force
    within_band    early, approved or building        the same band, another status (U -> TS, ...)
    delayed        early, approved or building        the same status, a later planned month
    advanced       early, approved or building        the same status, an earlier planned month
    new            no record in force                 early, approved or building
    into_planned   in force with another status       early, approved or building

Bands are stagemoves 0.1.0's (early = P, L; approved = T; building = U, V, TS); a band move takes
precedence over a status change, and a status change over a planned-month change (shift_months
is filled whenever both planned months are known). Each change is set beside the same change in
the previous HISTORY report pairs (count and MW: median and largest; delayed and advanced are
not counted there, because stagemoves' timeline keeps no planned month), and each row carries
the generator's backward moves in those pairs. Earlier steps whose 12 following reports are all
in the file give a recent base rate: the share of MW listed as operating within 12 reports, by
starting band and move (stagemoves.outcomes). MW is the capacity in report r - 1, except for new
and into_planned (report r).

No rule R re-keys are applied: a plant re-filed under a new plant id shows as one "left" row and
one "new" row; both are flagged possible_rekey when they match on rule R's terms (same technology
group and generator id, capacities within 0.05 MW, at least 10 MW) in the same report.

    python watchlist.py --data-dir /data --out-dir /out [--report YYYY-MM]
"""

import argparse
import json
import os
import statistics

import pandas as pd

import eia860m_slip as es
import stagemoves as sm

__version__ = "0.1.0"

HISTORY = 36  # earlier report pairs set beside report r
TOP = 20
FROM_PLANNED = ("forward", "backward", "to_operating", "exit_other", "left", "within_band",
                "delayed", "advanced")
CHANGES = FROM_PLANNED + ("new", "into_planned")
UNTIMED = ("delayed", "advanced")  # not counted in the history pairs
BAND_MOVES = ("forward", "backward", "to_operating", "exit_other")
ROW_COLS = ["key", "plant_id_eia", "generator_id", "plant", "state", "group", "change", "mw",
            "status_prev", "status_now", "band_prev", "band_now", "mw_prev", "mw_now",
            "planned_prev", "planned_now", "shift_months", "backward_before", "possible_rekey"]
SUM_COLS = ["change", "n", "mw", "median_n", "max_n", "median_mw", "max_mw", "pairs"]
TOP_COLS = ["key", "plant", "state", "group", "mw", "status_prev", "status_now", "planned_prev",
            "planned_now", "shift_months", "backward_before", "possible_rekey"]


def parse_month(text):
    """'2026-08' -> months since year 0 (year * 12 + month - 1)."""
    y, mo = text.strip().split("-")
    return int(y) * 12 + int(mo) - 1


def _int(v):
    return None if v is None or pd.isna(v) else int(v)


def records(snap):
    """key -> the fields read here, for the records in force in one report (es.snapshot)."""
    out = {}
    for x in snap.itertuples(index=False):
        out[x.key] = {"plant_id_eia": _int(x.plant_id_eia),
                      "generator_id": es._text(x.generator_id),
                      "plant": sm._plant(x.plant_name_eia), "state": sm._plant(x.state),
                      "group": x.group, "status": x.status, "band": sm.band(x.status),
                      "mw": float(x.capacity_mw), "planned_m": _int(x.planned_m)}
    return out


def shift(x, y):
    """Planned month in record y minus planned month in record x; None when either is missing."""
    if x["planned_m"] is None or y["planned_m"] is None:
        return None
    return y["planned_m"] - x["planned_m"]


def classify(x, y):
    """The change from record x (report r - 1) to record y (report r); x or y is None when the
    generator has no record in force. None when nothing read here changed."""
    b0 = None if x is None else x["band"]
    b1 = None if y is None else y["band"]
    if b0 in sm.ORDER:
        if y is None:
            return "left"
        mv = sm.move(b0, b1)
        if mv != "held":
            return mv
        if x["status"] != y["status"]:
            return "within_band"
        d = shift(x, y)
        if not d:
            return None
        return "delayed" if d > 0 else "advanced"
    if b1 in sm.ORDER:
        return "new" if x is None else "into_planned"
    return None


def changes(a, b, back):
    """One row per generator that changed between records a (report r - 1) and b (report r),
    in key order. back: key -> backward moves in the history pairs. MW is unrounded."""
    out = []
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        c = classify(x, y)
        if c is None:
            continue
        z = x if c in FROM_PLANNED else y
        out.append({"key": k, "plant_id_eia": z["plant_id_eia"], "generator_id": z["generator_id"],
                    "plant": z["plant"], "state": z["state"], "group": z["group"], "change": c,
                    "mw": z["mw"],
                    "status_prev": None if x is None else x["status"],
                    "status_now": None if y is None else y["status"],
                    "band_prev": None if x is None else x["band"],
                    "band_now": None if y is None else y["band"],
                    "mw_prev": None if x is None else x["mw"],
                    "mw_now": None if y is None else y["mw"],
                    "planned_prev": None if x is None else es.month_str(x["planned_m"]),
                    "planned_now": None if y is None else es.month_str(y["planned_m"]),
                    "shift_months": None if x is None or y is None else shift(x, y),
                    "backward_before": int(back.get(k, 0)), "possible_rekey": ""})
    return out


def flag_rekeys(rows):
    """Mark left rows (at least es.REKEY_MIN_MW) and new rows that match on rule R's terms: same
    technology group and generator id, capacities within es.REKEY_MW_TOL. One to one: left rows
    largest first (then key), each taking the free new row with the smallest capacity difference
    (then the lowest key). Each row of a pair names the other's key. Returns the pairs."""
    left = sorted((r for r in rows if r["change"] == "left" and r["mw_prev"] >= es.REKEY_MIN_MW),
                  key=lambda r: (-r["mw_prev"], r["key"]))
    new = [r for r in rows if r["change"] == "new"]
    pairs = 0
    for g in left:
        best = None
        for n in new:
            if (n["possible_rekey"] or n["group"] != g["group"]
                    or es._gen_id(n["generator_id"]) != es._gen_id(g["generator_id"])):
                continue
            d = abs(n["mw_now"] - g["mw_prev"])
            if d <= es.REKEY_MW_TOL and (best is None or (d, n["key"]) < best[:2]):
                best = (d, n["key"], n)
        if best is not None:
            g["possible_rekey"], best[2]["possible_rekey"] = best[1], g["key"]
            pairs += 1
    return pairs


def partition(a, b):
    """Generators in an ordered planned band in records a: count and MW by their move to records
    b (stagemoves' moves, held included, and left when they have no record in b)."""
    out = {x: {"n": 0, "mw": 0.0} for x in sm.MOVES + ("left",)}
    for k, x in a.items():
        if x["band"] not in sm.ORDER:
            continue
        y = b.get(k)
        mv = "left" if y is None else sm.move(x["band"], y["band"])
        out[mv]["n"] += 1
        out[mv]["mw"] += x["mw"]
    return out


def backward_before(s, lo, r):
    """key -> backward steps of that generator with m in lo..r - 2 (the history pairs)."""
    h = s[(s["m"] >= lo) & (s["m"] < r - 1) & (s["move"] == "backward")]
    return {k: int(v) for k, v in h.groupby("key").size().items()}


def history(t, s, left, lo, r):
    """One dict per earlier report pair (m, m + 1), m in lo..r - 2: (count, MW) of each change
    except delayed and advanced, read from stagemoves' timeline t, steps s and left."""
    out = []
    for m in range(lo, r - 1):
        f, lf = s[s["m"] == m], left[left["m"] == m]
        row = {"m": m}
        for c in BAND_MOVES:
            hit = f["move"] == c
            row[c] = (int(hit.sum()), sm._mw(f, hit))
        w = (f["move"] == "held") & (f["status"] != f["status1"])
        row["within_band"] = (int(w.sum()), sm._mw(f, w))
        row["left"] = (int(len(lf)), sm._mw(lf))
        p = t[t["m"] == m]
        prev = dict(zip(p["key"], p["band"]))
        nb = t[(t["m"] == m + 1) & t["band"].isin(list(sm.BANDS))]
        pb = nb["key"].map(prev)
        new = pb.isna()
        into = pb.notna() & ~pb.isin(list(sm.BANDS))
        row["new"] = (int(new.sum()), sm._mw(nb, new))
        row["into_planned"] = (int(into.sum()), sm._mw(nb, into))
        out.append(row)
    return out


def summary(rows, hist):
    """One row per change: count and MW in report r, and the median and largest count and MW over
    the history pairs (None for delayed and advanced, and when there are no pairs)."""
    out = []
    for c in CHANGES:
        f = [r for r in rows if r["change"] == c]
        h = [] if c in UNTIMED else [x[c] for x in hist]
        ns, mws = [n for n, _ in h], [w for _, w in h]
        out.append({"change": c, "n": len(f), "mw": round(sum(r["mw"] for r in f), 1),
                    "median_n": round(statistics.median(ns), 1) if h else None,
                    "max_n": max(ns) if h else None,
                    "median_mw": round(statistics.median(mws), 1) if h else None,
                    "max_mw": round(max(mws), 1) if h else None, "pairs": len(h)})
    return out


def top(rows, kinds):
    """The TOP largest rows of the given changes, largest MW first (then key)."""
    f = [r for r in rows if r["change"] in kinds]
    return sorted(f, key=lambda r: (-r["mw"], r["key"]))[:TOP]


def _out(r):
    """A row with its MW rounded to 0.1, for the CSV and tables."""
    return dict(r, **{c: None if r[c] is None else round(r[c], 1)
                      for c in ("mw", "mw_prev", "mw_now")})


def checks(rows, part, a, s, left, r):
    """C1: one row per generator, every change known; C2: the moves of the planned generators of
    report r - 1 add up to their MW; C3: their counts by move equal stagemoves.steps for
    m = r - 1; C4: the rows' band moves and left equal those counts, and the within-band rows
    are no more than the held generators."""
    keys = [x["key"] for x in rows]
    c1 = len(keys) == len(set(keys)) and all(x["change"] in CHANGES for x in rows)
    total = sum(x["mw"] for x in a.values() if x["band"] in sm.ORDER)
    parts = sum(v["mw"] for v in part.values())
    f, lf = s[s["m"] == r - 1], left[left["m"] == r - 1]
    theirs = {mv: int((f["move"] == mv).sum()) for mv in sm.MOVES}
    theirs["left"] = int(len(lf))
    ours = {k: v["n"] for k, v in part.items()}
    n = {c: sum(1 for x in rows if x["change"] == c) for c in CHANGES}
    held = n["within_band"] + n["delayed"] + n["advanced"]
    c4 = (all(n[c] == part[c]["n"] for c in BAND_MOVES + ("left",))
          and held <= part["held"]["n"])
    out = {"C1": {"rows": len(rows), "pass": bool(c1)},
           "C2": {"planned_mw": round(total, 1), "moves_mw": round(parts, 1),
                  "pass": bool(abs(total - parts) < 0.05)},
           "C3": {"ours": ours, "stagemoves": theirs, "pass": ours == theirs},
           "C4": {"row_counts": n, "pass": bool(c4)}}
    out["all_pass"] = all(out[k]["pass"] for k in ("C1", "C2", "C3", "C4"))
    return out


def write_md(path, meta, res):
    md = ["# EIA-860M watchlist: report %s" % meta["report"], "",
          "watchlist %s on stagemoves %s and eia860m-slip %s; data %s (latest report %s). "
          "MV2 of Munim, Inc. (made with AI agents). Code Apache-2.0; tables CC BY 4.0." % (
              meta["version"], meta["stagemoves"], meta["eia860m_slip"], meta["source"],
              meta["report_max"]), "",
          "Every planned generator whose stage band, status or planned operating month changed "
          "from report %s to report %s (PUDL report months: the month the data describes). "
          "Bands: early (P, L), approved (T), building (U, V, TS). Each change is set beside the "
          "%d report pairs %s to %s. A change can be a correction of an earlier report, not an "
          "event; statuses are self-reported." % (
              meta["previous"], meta["report"], meta["pairs"], meta["history_from"],
              meta["history_to"]), "",
          "## Changes in this report, beside the earlier report pairs", ""]
    md += es.table(res["summary"], SUM_COLS) + [""]
    for title, k in (("Largest backward moves", "top_backward"),
                     ("Largest exits (exit_other and left)", "top_exits"),
                     ("Largest delays (same status, later planned month)", "top_delayed"),
                     ("Largest new planned generators", "top_new")):
        md += ["## " + title, ""] + es.table(res[k], TOP_COLS) + [""]
    md += ["## Earlier moves: MW listed as operating within 12 reports", "",
           "Steps with m from %s to %s (their 12 following reports are all in the file), by "
           "starting band and move: a recent base rate for the moves above, not a forecast for "
           "any one generator." % (meta["history_from"], meta["outcomes_to"]), ""]
    md += es.table(res["outcomes"], sm.OUT_COLS) + [""]
    md += ["## Checks", "", "```", json.dumps(res["checks"], indent=1), "```", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--report", default=None, help="report month YYYY-MM (default: the latest)")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    import pyarrow.parquet as pq
    path = es.find_parquet(args.data_dir)
    names = pq.read_schema(path).names
    df = es.prepare(pd.read_parquet(path, columns=[c for c in es.COLUMNS if c in names]))
    last_m = int(df["report_m"].max())
    r = last_m if args.report is None else parse_month(args.report)
    if not sm.START_M < r <= last_m:
        raise SystemExit("report %s is outside %s to %s" % (
            es.month_str(r), es.month_str(sm.START_M + 1), es.month_str(last_m)))
    lo = max(sm.START_M, r - 1 - HISTORY)
    t = sm.timeline(df, lo, r)
    s, left = sm.steps(t, r)
    a, b = records(es.snapshot(df, r - 1)), records(es.snapshot(df, r))
    rows = changes(a, b, backward_before(s, lo, r))
    pairs = flag_rekeys(rows)
    hist = history(t, s, left, lo, r)
    part = partition(a, b)
    res = {"summary": summary(rows, hist),
           "top_backward": [_out(x) for x in top(rows, ("backward",))],
           "top_exits": [_out(x) for x in top(rows, ("exit_other", "left"))],
           "top_delayed": [_out(x) for x in top(rows, ("delayed",))],
           "top_new": [_out(x) for x in top(rows, ("new",))],
           "outcomes": sm.outcomes(s[s["m"] < r - 1]),
           "partition": {k: {"n": v["n"], "mw": round(v["mw"], 1)} for k, v in part.items()},
           "checks": checks(rows, part, a, s, left, r)}
    tag = es.month_str(r)
    meta = {"version": __version__, "stagemoves": sm.__version__, "eia860m_slip": es.__version__,
            "source": os.path.basename(path), "report": tag, "previous": es.month_str(r - 1),
            "report_max": es.month_str(last_m), "pairs": len(hist),
            "history_from": es.month_str(lo), "history_to": es.month_str(r - 1),
            "outcomes_to": es.month_str(r - 12), "rows": len(rows), "rekey_pairs": pairs}
    out = pd.DataFrame([_out(x) for x in rows], columns=ROW_COLS)
    for c in ("plant_id_eia", "shift_months"):
        out[c] = out[c].astype("Int64")
    out.to_csv(os.path.join(args.out_dir, "watchlist_%s.csv" % tag), index=False)
    with open(os.path.join(args.out_dir, "watchlist_%s.json" % tag), "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, **res), fh, indent=1, default=str)
    write_md(os.path.join(args.out_dir, "watchlist_%s.md" % tag), meta, res)
    print(json.dumps({"meta": meta, "summary": res["summary"], "checks": res["checks"]},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
