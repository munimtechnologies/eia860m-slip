"""headline: EIA's start-of-year planned capacity additions, scored against what EIA later reported.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0. Part of eia860m-slip.

Each January or February, EIA's Today in Energy states how many gigawatts of
utility-scale capacity developers plan to bring online that year, by
technology, from its Preliminary Monthly Electric Generator Inventory
(EIA-860M). Later articles and the Electric Power Annual state what was
added. data/eia_headline_plans.csv (CC BY 4.0) holds every one of those
numbers with the page it comes from and the words it rests on. This script
divides actual by plan for each year and technology, and turns the recent
ratios into a range for the year still open.

data/eia_headline_retirements.csv (since 0.2.2) holds the same kind of
numbers for planned retirements ("operators plan to retire N GW this year")
against what EIA later reported as retired; pass --retirements to use it.

Which actual is used: the most final kind that is a stated or derived value
(actual_final, then actual_later, then actual_first; the latest published
within a kind). A bound (">" or "<") is used only when no value exists, and
the ratio carries the bound.

    python headline.py --csv data/eia_headline_plans.csv --out docs/headline-plans-table.md
    python headline.py --retirements

Standard library only.
"""

import argparse
import csv
import os

__version__ = "0.2.2"

KINDS = ("plan", "actual_first", "actual_later", "actual_final", "steo")
ACTUAL_RANK = ("actual_final", "actual_later", "actual_first")
BOUNDS = ("=", "~", ">", "<")
VALUE_BOUNDS = ("=", "~")
TECHS = ("total", "solar", "battery", "wind", "gas", "coal", "nuclear")
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "data", "eia_headline_plans.csv")
RETIREMENTS_CSV = os.path.join(HERE, "data", "eia_headline_retirements.csv")


def load(path=DEFAULT_CSV):
    """Rows of the headline CSV with year as int and gw as float."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["year"] = int(r["year"])
        r["gw"] = float(r["gw"])
    return rows


def plan(rows, year, tech):
    for r in rows:
        if r["year"] == year and r["tech"] == tech and r["kind"] == "plan":
            return r
    return None


def best_actual(rows, year, tech):
    """The actual row to score (year, tech) against, or None."""
    found = [r for r in rows if r["year"] == year and r["tech"] == tech and r["kind"] in ACTUAL_RANK]
    if not found:
        return None
    values = [r for r in found if r["bound"] in VALUE_BOUNDS] or found
    return min(values, key=lambda r: (ACTUAL_RANK.index(r["kind"]), _neg(r["published"])))


def _neg(text):
    # Latest published first under min(): compare on the negated characters.
    return tuple(-ord(c) for c in text)


def realization(rows):
    """One dict per (year, tech) that has a plan: plan, actual, kind, bound and ratio."""
    out = []
    years = sorted({r["year"] for r in rows})
    for year in years:
        for tech in TECHS:
            p = plan(rows, year, tech)
            if p is None:
                continue
            a = best_actual(rows, year, tech)
            row = {"year": year, "tech": tech, "plan": p["gw"], "actual": None, "kind": "",
                   "bound": "", "ratio": None, "source": a["source"] if a else ""}
            if a is not None:
                row.update(actual=a["gw"], kind=a["kind"], bound=a["bound"], ratio=a["gw"] / p["gw"])
            out.append(row)
    return out


def projection(rows, target, years):
    """{tech: (low_gw, high_gw, n)} for target's plan, scaled by the value ratios of `years`."""
    table = realization(rows)
    out = {}
    for tech in TECHS:
        p = plan(rows, target, tech)
        ratios = [t["ratio"] for t in table if t["tech"] == tech and t["year"] in years
                  and t["ratio"] is not None and t["bound"] in VALUE_BOUNDS]
        if p is None or not ratios:
            continue
        out[tech] = (p["gw"] * min(ratios), p["gw"] * max(ratios), len(ratios))
    return out


def _ratio_text(t):
    if t["ratio"] is None:
        return ""
    mark = {"<": "< ", ">": "> ", "~": "~"}.get(t["bound"], "")
    return "%s%.0f%%" % (mark, 100.0 * t["ratio"])


def to_markdown(rows, target=None, years=()):
    lines = ["| year | technology | planned GW | actual GW | actual from | actual / plan |",
             "|---|---|---|---|---|---|"]
    for t in realization(rows):
        actual = "" if t["actual"] is None else "%s%g" % ({"<": "< ", ">": "> "}.get(t["bound"], ""), t["actual"])
        lines.append("| %d | %s | %g | %s | %s | %s |" % (t["year"], t["tech"], t["plan"], actual,
                                                          t["kind"], _ratio_text(t)))
    if target is not None:
        lines += ["", "Range for %d: its plan times the lowest and highest actual / plan of %s." % (
            target, ", ".join(str(y) for y in years)), "",
            "| technology | planned GW | low GW | high GW | years used |", "|---|---|---|---|---|"]
        for tech, (lo, hi, n) in projection(rows, target, years).items():
            lines.append("| %s | %g | %.1f | %.1f | %d |" % (tech, plan(rows, target, tech)["gw"], lo, hi, n))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default="")
    ap.add_argument("--retirements", action="store_true",
                    help="use data/eia_headline_retirements.csv (planned retirements) when --csv is not given")
    ap.add_argument("--out", default="")
    ap.add_argument("--target", type=int, default=2026)
    ap.add_argument("--years", default="2023,2024,2025")
    args = ap.parse_args(argv)
    rows = load(args.csv or (RETIREMENTS_CSV if args.retirements else DEFAULT_CSV))
    text = to_markdown(rows, args.target, tuple(int(y) for y in args.years.split(",")))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
