"""rehearing_202c: the rehearing record of every DOE 202(c) plant order, from DOE's own pages.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Reads data/doe_202c_rehearing.csv (one row per plant order in data/doe_202c_orders.csv,
transcribed from that order's page on energy.gov: the first request for rehearing and who
asked, DOE's "Notice of Denial of Rehearing by Operation of Law and Providing for Further
Consideration", and DOE's "Order Addressing Arguments Raised on Rehearing") and reports, as
of a date:

1. Plant orders whose 30-day window to ask for rehearing has closed, and how many drew a
   request (Federal Power Act section 313(a): within 30 days after the order is issued).
2. Days from each order to its first request, and from that request to DOE's notice.
3. When each order addressing rehearing came, counted from the expiry of the order it
   addresses (negative: before the expiry).
4. Each order's status: no request, window still open, addressed (in force or after
   expiry), or not addressed (expired, or in force with or without a notice).

Dates are calendar dates. Standard library only; reads the orders table with orders_202c.

    python rehearing_202c.py [--csv data/doe_202c_rehearing.csv] [--orders data/doe_202c_orders.csv] [--out-dir out] [--as-of 2026-10-19]
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
CSV = os.path.join(HERE, "data", "doe_202c_rehearing.csv")
DATES = ("first_request", "notice", "rehearing_order_date")
WINDOW_DAYS = 30
STATUSES = ("no request", "window open", "addressed in force", "addressed after expiry",
            "expired, not addressed", "in force, notice", "in force, no notice")


def load(path=CSV):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for c in DATES:
            r[c] = oc._date(r[c])
    return rows


def join(reh, orders):
    """Rehearing rows with their plant order's dates added, and the problems found."""
    plant = {o["order"]: o for o in orders if o["kind"] == "plant"}
    seen = Counter(r["order"] for r in reh)
    bad = ["duplicate order %s" % o for o, n in sorted(seen.items()) if n > 1]
    bad += ["%s: plant order with no rehearing row" % o for o in sorted(set(plant) - set(seen))]
    out = []
    for r in reh:
        o = plant.get(r["order"])
        if o is None:
            bad.append("%s: not a plant order in the orders table" % r["order"])
            continue
        if r["plant_key"] != o["plant_key"]:
            bad.append("%s: plant_key %r, the orders table says %r"
                       % (r["order"], r["plant_key"], o["plant_key"]))
        fr, nt, ro = r["first_request"], r["notice"], r["rehearing_order_date"]
        if fr is not None and fr < o["issued"]:
            bad.append("%s: request before the order" % r["order"])
        if fr is not None and (fr - o["issued"]).days > WINDOW_DAYS:
            bad.append("%s: first request more than %d days after the order"
                       % (r["order"], WINDOW_DAYS))
        if nt is not None and (fr is None or nt < fr):
            bad.append("%s: notice without an earlier request" % r["order"])
        if ro is not None and (nt is None or ro < nt):
            bad.append("%s: order on rehearing without an earlier notice" % r["order"])
        out.append(dict(r, issued=o["issued"], expires=o["expires"], plant=o["plant"]))
    return out, bad


def window_closed(r, as_of):
    return (as_of - r["issued"]).days > WINDOW_DAYS


def status(r, as_of):
    if r["first_request"] is None:
        return "window open" if not window_closed(r, as_of) else "no request"
    if r["rehearing_order_date"] is not None:
        if r["rehearing_order_date"] <= r["expires"]:
            return "addressed in force"
        return "addressed after expiry"
    if r["expires"] < as_of:
        return "expired, not addressed"
    return "in force, notice" if r["notice"] is not None else "in force, no notice"


def _spread(xs):
    if not xs:
        return {"n": 0, "min": None, "median": None, "max": None}
    return {"n": len(xs), "min": min(xs), "median": statistics.median(xs), "max": max(xs)}


def summary(rows, as_of):
    asked = [r for r in rows if r["first_request"] is not None]
    to_request = [(r["first_request"] - r["issued"]).days for r in asked]
    to_notice = [(r["notice"] - r["first_request"]).days for r in asked if r["notice"]]
    vs_expiry = sorted((r["rehearing_order_date"] - r["expires"]).days for r in asked
                       if r["rehearing_order_date"] is not None)
    st = Counter(status(r, as_of) for r in rows)
    plants = []
    for key in sorted({r["plant_key"] for r in rows}):
        sel = [r for r in rows if r["plant_key"] == key]
        plants.append({"plant_key": key, "plant": sel[0]["plant"], "orders": len(sel),
                       "window_closed": sum(window_closed(r, as_of) for r in sel),
                       "requested": sum(r["first_request"] is not None for r in sel),
                       "notices": sum(r["notice"] is not None for r in sel),
                       "addressed": sum(r["rehearing_order_date"] is not None for r in sel)})
    return {
        "orders": len(rows),
        "window_closed": sum(window_closed(r, as_of) for r in rows),
        "requested": len(asked),
        "requested_window_closed": sum(window_closed(r, as_of) for r in asked),
        "notices": len(to_notice),
        "notices_before_expiry": sum(1 for r in asked if r["notice"] and
                                     r["notice"] <= r["expires"]),
        "addressed": len(vs_expiry),
        "days_to_request": _spread(to_request),
        "days_to_notice": _spread(to_notice),
        "addressed_vs_expiry": vs_expiry,
        "addressed_vs_expiry_spread": _spread(vs_expiry),
        "status": {s: st.get(s, 0) for s in STATUSES},
        "plants": plants,
    }


def detail(rows, as_of):
    out = []
    for r in sorted(rows, key=lambda r: (r["plant_key"], r["issued"], r["order"])):
        ro = r["rehearing_order_date"]
        out.append({
            "order": r["order"], "plant": r["plant"], "issued": r["issued"].isoformat(),
            "expires": r["expires"].isoformat(),
            "first_request": r["first_request"].isoformat() if r["first_request"] else "",
            "requesters": r["requesters"],
            "notice": r["notice"].isoformat() if r["notice"] else "",
            "addressed": ro.isoformat() if ro else "",
            "days_after_expiry": (ro - r["expires"]).days if ro else "",
            "status": status(r, as_of)})
    return out


def run(reh, orders, as_of):
    rows, bad = join(reh, orders)
    return {"version": __version__, "as_of": as_of.isoformat(), "problems": bad,
            "summary": summary(rows, as_of), "detail": detail(rows, as_of)}


def render(res):
    s = res["summary"]
    dr, dn, dx = s["days_to_request"], s["days_to_notice"], s["addressed_vs_expiry_spread"]
    md = ["# Rehearing of DOE 202(c) plant orders", "",
          "rehearing_202c %s, as of %s. MV2 of Munim, Inc. (made with AI agents). "
          "Description only: nothing here was predicted in advance." % (res["version"],
                                                                         res["as_of"]), "",
          "Problems found in the tables: %s" % ("; ".join(res["problems"]) or "none"), "",
          "## Summary", "",
          "- Plant orders: %d; 30-day window closed: %d; with a request for rehearing: %d "
          "(%d of them with the window closed)." % (s["orders"], s["window_closed"],
                                                     s["requested"], s["requested_window_closed"]),
          "- Days from order to first request: %s to %s (median %s)." % (dr["min"], dr["max"],
                                                                          dr["median"]),
          "- Notices of denial by operation of law: %d, %s to %s days after the first request "
          "(median %s); %d of them on or before the order's expiry." % (
              s["notices"], dn["min"], dn["max"], dn["median"], s["notices_before_expiry"]),
          "- Orders addressing rehearing: %d; days after the expiry of the order addressed: "
          "%s (median %s)." % (s["addressed"], ", ".join(str(d) for d in s["addressed_vs_expiry"])
                               or "none", dx["median"]), "",
          "## Status", ""]
    md += oc.table([{"status": k, "orders": n} for k, n in s["status"].items()],
                   ["status", "orders"])
    md += ["", "## By plant", ""]
    md += oc.table(s["plants"], ["plant", "orders", "window_closed", "requested", "notices",
                                 "addressed"])
    md += ["", "## Every plant order", ""]
    md += oc.table(res["detail"], ["order", "plant", "issued", "expires", "first_request",
                                   "requesters", "notice", "addressed", "days_after_expiry",
                                   "status"])
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
    with open(os.path.join(args.out_dir, "rehearing_202c.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    text = render(res)
    with open(os.path.join(args.out_dir, "rehearing_202c.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
