"""erdetail: descriptive follow-ups to the twenty-seventh result (docs/er-plan.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Read after job erplan-v1 and not pre-registered: no prediction is tested. Using erplan.py 0.1.0
(commit b73dc6a) unchanged, on the same eight Zenodo copies of the annual EIA-860 and the same
sets file, this tool reports:

1. The counts behind check F3 in each plan year (the final copy's Operable generators, how many
   the early release holds, a sample of those it does not) and each copy's generators by class.
   erplan-v1 found F3 equal to 0.9977 in all four years; the counts show whether that is a
   coincidence of rounding.
2. For sets A and A_built, the early release's plan share by single report month of first
   EIA-860M listing (February to August, then everything later).
3. For A's generators absent from the early release, the MW whose plant (plant id) has some
   other generator in that early release: a new unit at a plant the early release knows, rather
   than a plant it does not know at all.

    python erdetail.py --data-dir /data --out-dir /out
"""

import argparse
import json
import os

import erplan as ep

__version__ = "0.1.0"
MONTHS = ("m02", "m03", "m04", "m05", "m06", "m07", "m08")
LATER = "later"  # m09-m12 and after the year
SAMPLE = 20


def plant_of(key):
    return key.partition("/")[0]


def f3_detail(er, final):
    """The counts behind erplan.check_f3: the final copy's Operable keys and how many of them
    the early release holds on any sheet."""
    op = sorted(k for k, c in final.items() if c == "operable")
    missing = [k for k in op if k not in er]
    n = len(op)
    return {"final_operable": n, "found": n - len(missing), "missing": len(missing),
            "share": (n - len(missing)) / n if n else None, "missing_sample": missing[:SAMPLE]}


def class_counts(idx):
    out = {c: 0 for c in ep.CLASSES[:4]}
    for c in idx.values():
        out[c] += 1
    return out


def month_of(bucket):
    return bucket if bucket in MONTHS else LATER


def by_month(rows, years, set_name):
    """{month: {mw, er_plan_share, er_any_share}} for the set's generators of the given years,
    by report month of first EIA-860M listing; months without MW are left out."""
    out = {}
    for m in MONTHS + (LATER,):
        sel = [r for r in rows if r["year"] in years and r["set"] == set_name and "er" in r
               and month_of(r["bucket"]) == m]
        tot = sum(r["mw"] for r in sel)
        if tot <= 0:
            continue
        plan = sum(r["mw"] for r in sel if r["er"] == "plan_y")
        held = sum(r["mw"] for r in sel if r["er"] != "absent")
        out[m] = {"mw": round(tot, 1), "er_plan_share": ep.r4(plan / tot),
                  "er_any_share": ep.r4(held / tot)}
    return out


def plant_presence(rows, er_plants, years, set_name="A"):
    """For the set's generators absent from the early release, by span and pooled over years:
    their MW and the MW whose plant id has some generator in that year's early release.
    er_plants: {year: set of plant ids in the early release}."""
    out = {}
    for sp in ("all",) + tuple(ep.SPANS):
        sel = [r for r in rows if r["year"] in years and r["set"] == set_name
               and r.get("er") == "absent" and (sp == "all" or r["span"] == sp)]
        tot = sum(r["mw"] for r in sel)
        if tot <= 0:
            continue
        known = sum(r["mw"] for r in sel if plant_of(r["key"]) in er_plants.get(r["year"], ()))
        out[sp] = {"absent_mw": round(tot, 1), "plant_in_er_mw": round(known, 1),
                   "plant_in_er_share": ep.r4(known / tot), "generators": len(sel)}
    return out


def render(res):
    md = ["# erdetail %s: descriptive follow-ups to the twenty-seventh result" % __version__, "",
          "MV2 of Munim, Inc. (made with AI agents). Read after erplan-v1; not pre-registered, "
          "no prediction tested. erplan.py 0.1.0 (b73dc6a) unchanged.", "",
          "Plan years: %s." % res["years"], "",
          "## Counts behind check F3", "",
          "| year | final Operable | found in early release | missing | share |",
          "|---|---|---|---|---|"]
    for y, d in res["f3"].items():
        md.append("| %s | %d | %d | %d | %s |" % (y, d["final_operable"], d["found"], d["missing"],
                                                  d["share"]))
    md += ["", "## Generators by class in each copy", "",
           "| year | copy | plan_y | proposed_other | operable | retired |", "|---|---|---|---|---|---|"]
    for y, d in res["counts"].items():
        for kind in ("er", "final"):
            c = d[kind]
            md.append("| %s | %s | %d | %d | %d | %d |" % (y, kind, c["plan_y"], c["proposed_other"],
                                                        c["operable"], c["retired"]))
    for s in ("A", "A_built"):
        md += ["", "## %s: early release's plan share by report month of first listing" % s, "",
               "| year | month | mw | er_plan_share | er_any_share |", "|---|---|---|---|---|"]
        for y, months in res["months"][s].items():
            for m, d in months.items():
                md.append("| %s | %s | %.1f | %s | %s |" % (y, m, d["mw"], d["er_plan_share"],
                                                           d["er_any_share"]))
    md += ["", "## A absent from the early release: is its plant there?", "",
           "| span | generators | absent MW | plant in early release MW | share |",
           "|---|---|---|---|---|"]
    for sp, d in res["plants"].items():
        md.append("| %s | %d | %.1f | %.1f | %s |" % (sp, d["generators"], d["absent_mw"],
                                                     d["plant_in_er_mw"], d["plant_in_er_share"]))
    md += ["", "## Sample of final Operable keys missing from the early release", ""]
    for y, d in res["f3"].items():
        md.append("- %s: %s" % (y, ", ".join(d["missing_sample"]) or "none"))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.data_dir, exist_ok=True)
    files, idxs, valid, calls = ep.load_copies(args.data_dir, False)
    status, body, err = ep.fetch(ep.SETS_URL)
    if body is None:
        raise SystemExit("could not fetch %s: %s" % (ep.SETS_URL, err))
    rows = ep.read_sets(body.decode("utf-8"))
    idx = {y: (idxs[(y, "er")], idxs[(y, "final")]) for y in valid}
    ep.classify(rows, idx)
    years = tuple(valid)
    res = {"version": __version__, "erplan_version": ep.__version__, "years": list(years),
           "calls": len(calls),
           "f3": {str(y): f3_detail(*idx[y]) for y in years},
           "counts": {str(y): {"er": class_counts(idx[y][0]), "final": class_counts(idx[y][1])}
                      for y in years},
           "months": {s: dict([("pooled", by_month(rows, years, s))]
                              + [(str(y), by_month(rows, (y,), s)) for y in years])
                      for s in ("A", "A_built")},
           "plants": plant_presence(rows, {y: {plant_of(k) for k in idx[y][0]} for y in years},
                                    years)}
    with open(os.path.join(args.out_dir, "erdetail.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    md = render(res)
    with open(os.path.join(args.out_dir, "erdetail.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return res


if __name__ == "__main__":
    main()
