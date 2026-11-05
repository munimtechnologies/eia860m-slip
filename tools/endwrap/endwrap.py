"""endwrap: read PUDL's EIA-860M changelog end dates by the rule the build was made with.

PUDL PR #5731 (merged 2 November 2026) changed how make_changelog ends a series: every
valid_until_date is now the first month a record is no longer in force, and a generator's last
record ends one month after the last report that lists it. Before the PR, a last record ended
on that last report itself. eia860m_slip.listed_until (eia860m-slip 0.3.1) was written for the
old rule and reads a last record's end one month too late on post-merge builds (see
docs/pudl-pr2.md, "The left3 read", and docs/endrule.md).

This wrapper does not edit eia860m_slip. install() replaces eia860m_slip.listed_until, at run
time only, with a reader that first tells the two rules apart from the data:

- On a post-merge build, every generator still listed in the latest report month L whose last
  record started before L ends at L + 1 month; a generator that left ends at or before L.
- On a pre-merge build, those same records end at L, and none that started before L ends
  at L + 1.

So among last records that started before L, more ending at L + 1 than at L means the new
(exclusive) rule. Exclusive builds are read with every end as exclusive (end - 1 month);
anything else goes to the original reader unchanged.

Use: python endwrap.py some_tool.py [its arguments]   (installs, then runs the tool as
__main__), or import endwrap; endwrap.install() before the tool calls eia860m_slip.prepare.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import json
import runpy
import sys

VERSION = "0.1.0"
STATE = {"version": VERSION, "module_version": None, "calls": []}


def _int(x):
    return None if x is None or x != x else int(x)


def detect_rule(df):
    """('exclusive' | 'inclusive', counts) from a frame with key, report_m and valid_m columns
    (months as numbers, as eia860m_slip.prepare makes them)."""
    last_m = df["report_m"].max()
    is_last = df["report_m"] == df.groupby("key")["report_m"].transform("max")
    early = df[is_last & (df["report_m"] < last_m)]
    n_next = int((early["valid_m"] == last_m + 1).sum())
    n_at = int((early["valid_m"] == last_m).sum())
    rule = "exclusive" if n_next > n_at else "inclusive"
    return rule, {"latest_m": _int(last_m), "last_records_started_before_latest": int(len(early)),
                  "end_next_month": n_next, "end_latest_month": n_at}


def listed_until_exclusive(df):
    """Last report month each record is in force when every valid_until_date is exclusive:
    end - 1 month. A blank end runs to the last report, as in the original reader."""
    last_m = df["report_m"].max()
    until = df["valid_m"] - 1
    return until.fillna(last_m).clip(upper=last_m)


def make_reader(original):
    def listed_until(df):
        rule, counts = detect_rule(df)
        STATE["calls"].append(dict(counts, rule=rule))
        if rule == "exclusive":
            return listed_until_exclusive(df)
        return original(df)
    listed_until.endwrap = True
    listed_until.original = original
    return listed_until


def install(es=None):
    """Replace es.listed_until (default: the eia860m_slip module) with the rule-aware reader.
    Calling it twice changes nothing more. Returns the module."""
    if es is None:
        import eia860m_slip as es
    current = es.listed_until
    if not getattr(current, "endwrap", False):
        es.listed_until = make_reader(current)
    STATE["module_version"] = getattr(es, "__version__", None)
    return es


def run_script(argv):
    if not argv:
        sys.exit("usage: python endwrap.py TOOL.py [ARGS...]")
    install()
    sys.argv = list(argv)
    try:
        runpy.run_path(argv[0], run_name="__main__")
    finally:
        sys.stderr.write("endwrap %s: %s\n" % (VERSION, json.dumps(STATE, default=str)))


if __name__ == "__main__":
    run_script(sys.argv[1:])
