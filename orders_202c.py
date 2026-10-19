"""orders_202c: every DOE Federal Power Act 202(c) emergency order of 2025-2026 as one table.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Reads data/doe_202c_orders.csv (one row per order, extension or amendment, transcribed
from DOE's 2025 and 2026 202(c) order pages, plus one amended order that only ERCOT's page
lists) and reports:

1. Orders by year issued, kind and area.
2. Event episodes: short emergency orders grouped by days in force that overlap or touch.
3. Days of the year with at least one order of a kind in force.
4. Plant chains: each plant's orders in sequence, with any days between one order's
   expiry and the next order's start.
5. Megawatts under plant orders (since 0.2.0, when data/doe_202c_plant_mw.csv is present):
   the dates the total changes, plant-days and MW-days up to the as-of date.

Kinds: plant (names a plant's units, about 90 days, renewed), event (a grid operator or
utility, days to two weeks), island (Puerto Rico and Guam system orders, about 90 days).
Days are calendar dates with the start and end dates both counted; times of day are kept
in the table but not used. Standard library only.

    python orders_202c.py [--csv data/doe_202c_orders.csv] [--out-dir out] [--as-of 2026-10-18]
"""

import argparse
import csv
import datetime as dt
import json
import os
from collections import Counter

__version__ = "0.2.0"

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "doe_202c_orders.csv")
MW_CSV = os.path.join(HERE, "data", "doe_202c_plant_mw.csv")
KINDS = ("plant", "event", "island")
DATES = ("issued", "effective", "expires")
EVENT_MAX_DAYS = 31
ONE_DAY = dt.timedelta(days=1)
COAL_FUELS = frozenset({"BIT", "SUB", "LIG", "ANT", "RC", "WC", "SGC"})


def _date(s):
    s = (s or "").strip()
    return dt.date.fromisoformat(s) if s else None


def load(path=CSV):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for c in DATES:
            r[c] = _date(r[c])
    return rows


def load_mw(path=MW_CSV):
    """Summer MW and primary fuel of the units each plant's orders cover, by plant_key."""
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["plant_key"].strip(): {"mw": float(r["summer_mw"]),
                                         "fuel": r["fuel"].strip().upper()}
                for r in csv.DictReader(fh)}


def days(r):
    """Calendar days in force, start and end dates counted (None without an expiry)."""
    if r["expires"] is None:
        return None
    return (r["expires"] - r["effective"]).days + 1


def validate(rows):
    """Problems found in the table (an empty list if none)."""
    bad = []
    seen = Counter(r["order"] for r in rows)
    bad += ["duplicate order %s" % o for o, n in sorted(seen.items()) if n > 1]
    for r in rows:
        o = r["order"]
        if r["kind"] not in KINDS:
            bad.append("%s: unknown kind %r" % (o, r["kind"]))
        if r["issued"] is None or r["effective"] is None:
            bad.append("%s: no issue or start date" % o)
            continue
        if r["effective"] < r["issued"]:
            bad.append("%s: starts before it was issued" % o)
        if r["expires"] is not None and r["expires"] < r["effective"]:
            bad.append("%s: expires before it starts" % o)
        if (r["kind"] == "plant") != bool(r["plant_key"]):
            bad.append("%s: plant_key must be set for plant orders and only for them" % o)
        if r["kind"] == "event" and (r["expires"] is None or days(r) > EVENT_MAX_DAYS):
            bad.append("%s: event order without an expiry within %d days" % (o, EVENT_MAX_DAYS))
    return bad


def counts(rows):
    by_year = Counter(r["issued"].year for r in rows)
    by_kind = Counter(r["kind"] for r in rows)
    by_year_kind = Counter((r["issued"].year, r["kind"]) for r in rows)
    ev = [r for r in rows if r["kind"] == "event"]
    area_n = Counter((r["issued"].year, r["area"]) for r in ev)
    area_days = Counter()
    for r in ev:
        area_days[(r["issued"].year, r["area"])] += days(r)
    # Plant orders' length as the statute counts it: days from start to expiry.
    lengths = Counter((r["expires"] - r["effective"]).days for r in rows
                      if r["kind"] == "plant" and r["expires"] is not None)
    return {
        "orders": len(rows),
        "by_year": {str(y): n for y, n in sorted(by_year.items())},
        "by_kind": {k: by_kind.get(k, 0) for k in KINDS},
        "by_year_kind": [{"year": y, "kind": k, "orders": by_year_kind[(y, k)]}
                         for y in sorted(by_year) for k in KINDS if by_year_kind[(y, k)]],
        "event_areas": [{"year": y, "area": a, "orders": n, "order_days": area_days[(y, a)]}
                        for (y, a), n in sorted(area_n.items(), key=lambda x: (x[0][0], -x[1],
                                                                              x[0][1]))],
        "plant_lengths": {str(n): k for n, k in sorted(lengths.items())},
    }


def episodes(rows, kind="event"):
    """Orders of a kind grouped into runs of days in force that overlap or touch."""
    sel = sorted((r for r in rows if r["kind"] == kind and r["expires"] is not None),
                 key=lambda r: (r["effective"], r["order"]))
    runs = []
    for r in sel:
        if runs and r["effective"] <= runs[-1]["end"] + ONE_DAY:
            cur = runs[-1]
            cur["end"] = max(cur["end"], r["expires"])
            cur["orders"].append(r["order"])
            cur["areas"].add(r["area"])
        else:
            runs.append({"start": r["effective"], "end": r["expires"], "orders": [r["order"]],
                         "areas": {r["area"]}})
    return [{"start": e["start"].isoformat(), "end": e["end"].isoformat(),
             "days": (e["end"] - e["start"]).days + 1, "orders": len(e["orders"]),
             "areas": ", ".join(sorted(e["areas"])), "order_list": ", ".join(e["orders"])}
            for e in runs]


def days_covered(rows, kind, start, end):
    """Dates from start to end (both counted) with at least one order of a kind in force."""
    covered = set()
    for r in rows:
        if r["kind"] != kind or r["expires"] is None:
            continue
        d, last = max(r["effective"], start), min(r["expires"], end)
        while d <= last:
            covered.add(d)
            d += ONE_DAY
    return len(covered)


def chains(rows):
    """Each plant's orders in order of start, with the days left uncovered between them."""
    out = []
    for key in sorted({r["plant_key"] for r in rows if r["kind"] == "plant"}):
        seq = sorted((r for r in rows if r["kind"] == "plant" and r["plant_key"] == key),
                     key=lambda r: (r["effective"], r["order"]))
        gaps = []
        for a, b in zip(seq, seq[1:]):
            gap = (b["effective"] - a["expires"]).days - 1
            if gap > 0:
                gaps.append({"after": a["order"], "before": b["order"],
                             "from": (a["expires"] + ONE_DAY).isoformat(),
                             "to": (b["effective"] - ONE_DAY).isoformat(), "days": gap})
        out.append({"plant_key": key, "plant": seq[0]["plant"], "area": seq[0]["area"],
                    "orders": len(seq), "renewals": len(seq) - 1,
                    "first_start": seq[0]["effective"].isoformat(),
                    "current_order": seq[-1]["order"],
                    "current_expiry": seq[-1]["expires"].isoformat(),
                    "span_days": (seq[-1]["expires"] - seq[0]["effective"]).days + 1,
                    "gaps": len(gaps), "gap_days": sum(g["days"] for g in gaps),
                    "gap_detail": "; ".join("%s to %s (%d days, between %s and %s)"
                                            % (g["from"], g["to"], g["days"], g["after"],
                                               g["before"]) for g in gaps),
                    "order_list": ", ".join(r["order"] for r in seq)})
    return out


def plant_dates(rows, key, end):
    """Dates up to end (counted) on which at least one order for the plant is in force."""
    covered = set()
    for r in rows:
        if r["kind"] != "plant" or r["plant_key"] != key or r["expires"] is None:
            continue
        d, last = r["effective"], min(r["expires"], end)
        while d <= last:
            covered.add(d)
            d += ONE_DAY
    return covered


def mw_under_order(rows, mw, as_of):
    """Summer MW under plant orders day by day up to as_of: each date the set of plants
    under order changes, with plant-days and MW-days (all and coal-fired)."""
    keys = sorted({r["plant_key"] for r in rows if r["kind"] == "plant"})
    cover = {k: plant_dates(rows, k, as_of) for k in keys if k in mw}
    out = {"missing_mw": [k for k in keys if k not in mw], "steps": [], "plant_days": 0,
           "mw_days": 0.0, "coal_mw_days": 0.0, "peak_mw": 0.0, "peak_from": None,
           "mw_as_of": 0.0, "coal_mw_as_of": 0.0}
    if not any(cover.values()):
        return out
    d, prev = min(min(c) for c in cover.values() if c), None
    while d <= as_of:
        on = [k for k in sorted(cover) if d in cover[k]]
        if on != prev:
            out["steps"].append({
                "date": d.isoformat(), "plants": len(on),
                "mw": round(sum(mw[k]["mw"] for k in on), 1),
                "coal_mw": round(sum(mw[k]["mw"] for k in on if mw[k]["fuel"] in COAL_FUELS), 1),
                "plant_list": ", ".join(on)})
            prev = on
        d += ONE_DAY
    peak = max(out["steps"], key=lambda s: s["mw"])
    out.update({
        "plant_days": sum(len(c) for c in cover.values()),
        "mw_days": round(sum(mw[k]["mw"] * len(c) for k, c in cover.items()), 1),
        "coal_mw_days": round(sum(mw[k]["mw"] * len(c) for k, c in cover.items()
                                  if mw[k]["fuel"] in COAL_FUELS), 1),
        "peak_mw": peak["mw"], "peak_from": peak["date"],
        "mw_as_of": out["steps"][-1]["mw"], "coal_mw_as_of": out["steps"][-1]["coal_mw"]})
    out["gw_years"] = round(out["mw_days"] / 1000.0 / 365.0, 2)
    return out


def table(rows, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join("" if r.get(c) is None else str(r.get(c))
                                       for c in cols) + " |")
    return lines


def run(rows, as_of, mw=None):
    year_start = dt.date(as_of.year, 1, 1)
    res = {
        "version": __version__, "as_of": as_of.isoformat(),
        "problems": validate(rows),
        "counts": counts(rows),
        "episodes": episodes(rows),
        "event_days_this_year": days_covered(rows, "event", year_start, as_of),
        "days_this_year": (as_of - year_start).days + 1,
        "chains": chains(rows),
    }
    if mw is not None:
        res["mw"] = mw_under_order(rows, mw, as_of)
    return res


def render(res):
    c = res["counts"]
    md = ["# DOE 202(c) emergency orders, 2025-2026", "",
          "orders_202c %s, table as of %s. MV2 of Munim, Inc. (made with AI agents). "
          "Description only: nothing here was predicted in advance." % (res["version"],
                                                                         res["as_of"]), "",
          "Problems found in the table: %s" % ("; ".join(res["problems"]) or "none"), "",
          "## Orders by year issued and kind", ""]
    md += table(c["by_year_kind"], ["year", "kind", "orders"])
    md += ["", "Total: %d orders, extensions and amendments (%s)." % (
        c["orders"], ", ".join("%s %d" % (k, n) for k, n in c["by_kind"].items())), "",
        "## Event orders by area", ""]
    md += table(c["event_areas"], ["year", "area", "orders", "order_days"])
    md += ["", "## Event episodes (orders whose days in force overlap or touch)", ""]
    md += table(res["episodes"], ["start", "end", "days", "orders", "areas", "order_list"])
    md += ["", "Days of %s up to %s with at least one event order in force: %d of %d." % (
        res["as_of"][:4], res["as_of"], res["event_days_this_year"], res["days_this_year"]), "",
        "## Plant chains", "",
        "Plant orders by days from start to expiry: %s." % ", ".join(
            "%s days: %d" % (n, k) for n, k in c["plant_lengths"].items()), ""]
    md += table(res["chains"], ["plant", "area", "orders", "first_start", "current_order",
                                "current_expiry", "span_days", "gaps", "gap_days",
                                "gap_detail"])
    m = res.get("mw")
    if m is not None:
        md += ["", "## Summer MW under plant orders", "",
               "Plants without a MW row: %s" % (", ".join(m["missing_mw"]) or "none"), ""]
        md += table(m["steps"], ["date", "plants", "mw", "coal_mw", "plant_list"])
        md += ["", "Up to %s: %d plant-days, %.1f MW-days (%.2f GW-years), %.1f of them coal. "
               "Peak %.1f MW from %s; %.1f MW (%.1f coal) on %s." % (
                   res["as_of"], m["plant_days"], m["mw_days"], m.get("gw_years", 0.0),
                   m["coal_mw_days"], m["peak_mw"], m["peak_from"], m["mw_as_of"],
                   m["coal_mw_as_of"], res["as_of"])]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--mw-csv", default=MW_CSV)
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    args = ap.parse_args(argv)
    mw = load_mw(args.mw_csv) if os.path.exists(args.mw_csv) else None
    res = run(load(args.csv), dt.date.fromisoformat(args.as_of), mw)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "orders_202c.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    text = render(res)
    with open(os.path.join(args.out_dir, "orders_202c.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
