"""court_202c: court petitions for review of DOE 202(c) plant orders, from CourtListener.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Reads data/doe_202c_petitions.csv (one row per petition for review found in CourtListener's
RECAP archive of the D.C. and Ninth Circuit dockets: the docket, filing date, petitioners,
the DOE order the record names, how that order is known, the lead docket of its
consolidated group, and the latest status the archive shows) and reports, as of a date:

1. Petitions by court, status, plant and how the challenged order is known.
2. The plant orders named in a petition, and days from each order's expiry to the
   petition (negative: filed while the order was in force).
3. Orders decided: days from the first petition and from the order's expiry to the decision.
4. Petitions held in abeyance, by the date of the abeyance order, and the oldest open one.

Federal Power Act section 313(b): a petition for review is filed within 60 days after DOE's
order on rehearing (or its deemed denial). Dates are calendar dates. Standard library only;
reads the orders table with orders_202c.

    python court_202c.py [--csv data/doe_202c_petitions.csv] [--orders data/doe_202c_orders.csv] [--out-dir out] [--as-of 2026-10-19]
"""

import argparse
import csv
import datetime as dt
import json
import os
import statistics
from collections import Counter

import orders_202c as oc

__version__ = "0.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "doe_202c_petitions.csv")
DATES = ("filed", "status_date")
COURTS = ("cadc", "ca9")
STATUSES = ("decided", "abeyance", "briefing", "no later order seen")
EVIDENCE = ("petition", "filing", "secondary")


def load(path=CSV):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for c in DATES:
            r[c] = oc._date(r[c])
    return rows


def join(pets, orders):
    """Petition rows with their order's dates added (where the order is known), and the
    problems found."""
    plant = {o["order"]: o for o in orders if o["kind"] == "plant"}
    keys = {o["plant_key"] for o in plant.values()}
    seen = Counter(r["docket"] for r in pets)
    bad = ["duplicate docket %s" % d for d, n in sorted(seen.items()) if n > 1]
    out = []
    for r in pets:
        d = r["docket"]
        if r["court"] not in COURTS:
            bad.append("%s: court %r" % (d, r["court"]))
        if r["status"] not in STATUSES:
            bad.append("%s: status %r" % (d, r["status"]))
        elif (r["status_date"] is None) != (r["status"] == "no later order seen"):
            bad.append("%s: status date does not fit status %r" % (d, r["status"]))
        if r["filed"] is not None and r["status_date"] is not None and \
                r["status_date"] < r["filed"]:
            bad.append("%s: status dated before the petition" % d)
        if any(k not in keys for k in r["plant_key"].split("-")):
            bad.append("%s: plant_key %r not in the orders table" % (d, r["plant_key"]))
        if r["lead"] and r["lead"] not in seen:
            bad.append("%s: lead docket %s not in the table" % (d, r["lead"]))
        if bool(r["order"]) != bool(r["order_evidence"]) or \
                (r["order_evidence"] and r["order_evidence"] not in EVIDENCE):
            bad.append("%s: order %r with evidence %r" % (d, r["order"], r["order_evidence"]))
        row = dict(r, issued=None, expires=None)
        if r["order"]:
            o = plant.get(r["order"])
            if o is None:
                bad.append("%s: %s is not a plant order in the orders table" % (d, r["order"]))
            else:
                if r["plant_key"] != o["plant_key"]:
                    bad.append("%s: plant_key %r, the orders table says %r"
                               % (d, r["plant_key"], o["plant_key"]))
                if r["filed"] is not None and r["filed"] < o["issued"]:
                    bad.append("%s: petition before the order" % d)
                row.update(issued=o["issued"], expires=o["expires"])
        out.append(row)
    return out, bad


def _spread(xs):
    if not xs:
        return {"n": 0, "min": None, "median": None, "max": None}
    return {"n": len(xs), "min": min(xs), "median": statistics.median(xs), "max": max(xs)}


def summary(rows, as_of):
    timed = [r for r in rows if r["expires"] is not None and r["filed"] is not None]
    vs_expiry = sorted((r["filed"] - r["expires"]).days for r in timed)
    decided = []
    for o in sorted({r["order"] for r in rows if r["status"] == "decided" and r["order"]}):
        sel = [r for r in rows if r["order"] == o and r["status"] == "decided"]
        first = min(r["filed"] for r in sel if r["filed"] is not None)
        on = sel[0]["status_date"]
        decided.append({"order": o, "petitions": len(sel), "decided": on.isoformat(),
                        "days_after_first_petition": (on - first).days,
                        "days_after_expiry": (on - sel[0]["expires"]).days})
    open_rows = [r for r in rows if r["status"] != "decided" and r["filed"] is not None]
    oldest = min(open_rows, key=lambda r: (r["filed"], r["docket"])) if open_rows else None
    st = Counter(r["status"] for r in rows)
    ab = Counter(r["status_date"].isoformat() for r in rows if r["status"] == "abeyance")
    plants = []
    for key in sorted({r["plant_key"] for r in rows}):
        sel = [r for r in rows if r["plant_key"] == key]
        plants.append({"plant_key": key, "petitions": len(sel),
                       "orders_named": ", ".join(sorted({r["order"] for r in sel if r["order"]})),
                       "decided": sum(r["status"] == "decided" for r in sel),
                       "abeyance": sum(r["status"] == "abeyance" for r in sel)})
    return {
        "petitions": len(rows),
        "courts": dict(sorted(Counter(r["court"] for r in rows).items())),
        "status": {s: st.get(s, 0) for s in STATUSES},
        "order_evidence": dict(sorted(Counter(r["order_evidence"] or "none"
                                              for r in rows).items())),
        "orders_named": sorted({r["order"] for r in rows if r["order"]}),
        "filed_vs_expiry": vs_expiry,
        "filed_vs_expiry_spread": _spread(vs_expiry),
        "filed_in_force": sum(1 for x in vs_expiry if x <= 0),
        "filed_after_expiry": sum(1 for x in vs_expiry if x > 0),
        "decided": decided,
        "abeyance_orders": dict(sorted(ab.items())),
        "oldest_open": {"docket": oldest["docket"], "filed": oldest["filed"].isoformat(),
                        "status": oldest["status"],
                        "days_open": (as_of - oldest["filed"]).days} if oldest else None,
        "plants": plants,
    }


def detail(rows):
    out = []
    for r in sorted(rows, key=lambda r: (r["court"], r["docket"])):
        out.append({
            "docket": r["docket"], "court": r["court"],
            "filed": r["filed"].isoformat() if r["filed"] else "",
            "petitioners": r["petitioners"], "order": r["order"],
            "evidence": r["order_evidence"], "plant": r["plant_key"], "lead": r["lead"],
            "days_after_expiry": (r["filed"] - r["expires"]).days
            if r["expires"] is not None and r["filed"] is not None else "",
            "status": r["status"],
            "status_date": r["status_date"].isoformat() if r["status_date"] else ""})
    return out


def run(pets, orders, as_of):
    rows, bad = join(pets, orders)
    return {"version": __version__, "as_of": as_of.isoformat(), "problems": bad,
            "summary": summary(rows, as_of), "detail": detail(rows)}


def render(res):
    s = res["summary"]
    fx = s["filed_vs_expiry_spread"]
    md = ["# Court petitions for review of DOE 202(c) plant orders", "",
          "court_202c %s, as of %s. MV2 of Munim, Inc. (made with AI agents). "
          "Description only: nothing here was predicted in advance." % (res["version"],
                                                                         res["as_of"]), "",
          "Problems found in the tables: %s" % ("; ".join(res["problems"]) or "none"), "",
          "## Summary", "",
          "- Petitions: %d (%s)." % (s["petitions"], ", ".join(
              "%s %d" % kv for kv in s["courts"].items())),
          "- Status: %s." % ", ".join("%s %d" % kv for kv in s["status"].items()),
          "- Plant orders named in the record: %d (%s)." % (len(s["orders_named"]),
                                                            ", ".join(s["orders_named"])),
          "- Days from the named order's expiry to the petition: %s to %s (median %s); "
          "%d filed while the order was in force, %d after it expired." % (
              fx["min"], fx["max"], fx["median"], s["filed_in_force"], s["filed_after_expiry"])]
    for d in s["decided"]:
        md.append("- Decided: %s (%d petitions) on %s, %d days after the first petition and "
                  "%d days after the order expired." % (d["order"], d["petitions"], d["decided"],
                                                        d["days_after_first_petition"],
                                                        d["days_after_expiry"]))
    if s["oldest_open"]:
        o = s["oldest_open"]
        md.append("- Oldest open petition: %s, filed %s, %d days open (%s)."
                  % (o["docket"], o["filed"], o["days_open"], o["status"]))
    md += ["", "## Abeyance orders", ""]
    md += oc.table([{"dated": k, "petitions": n} for k, n in s["abeyance_orders"].items()],
                   ["dated", "petitions"])
    md += ["", "## By plant", ""]
    md += oc.table(s["plants"], ["plant_key", "petitions", "orders_named", "decided",
                                 "abeyance"])
    md += ["", "## Every petition", ""]
    md += oc.table(res["detail"], ["docket", "court", "filed", "petitioners", "order",
                                   "evidence", "plant", "lead", "days_after_expiry", "status",
                                   "status_date"])
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--orders", default=oc.CSV)
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    args = ap.parse_args(argv)
    res = run(load(args.csv), oc.load(args.orders), dt.date.fromisoformat(args.as_of))
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "court_202c.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    text = render(res)
    with open(os.path.join(args.out_dir, "court_202c.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
