"""Unit tests for endwrap.py. Needs pandas; no network, no eia860m_slip.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.)."""

import types
import unittest

import pandas as pd

import endwrap as ew

L = 110.0  # latest report month (months as numbers, as eia860m_slip.prepare makes them)


def frame(rows):
    return pd.DataFrame(rows, columns=["key", "report_m", "valid_m"])


# After PR #5731: A still listed at L, B last listed at 107, C first and last listed at L.
NEW = frame([("1/A", 100.0, 105.0), ("1/A", 105.0, 111.0), ("2/B", 100.0, 108.0),
             ("3/C", 110.0, 111.0)])
# Before the PR: A's last record ends at L itself, B's at its last report 107.
OLD = frame([("1/A", 100.0, 105.0), ("1/A", 105.0, 110.0), ("2/B", 100.0, 107.0),
             ("3/C", 110.0, 111.0)])


class DetectTests(unittest.TestCase):
    def test_new_rule(self):
        rule, counts = ew.detect_rule(NEW)
        self.assertEqual(rule, "exclusive")
        self.assertEqual(counts, {"latest_m": 110, "last_records_started_before_latest": 2,
                                  "end_next_month": 1, "end_latest_month": 0})

    def test_old_rule(self):
        rule, counts = ew.detect_rule(OLD)
        self.assertEqual(rule, "inclusive")
        self.assertEqual(counts["end_next_month"], 0)
        self.assertEqual(counts["end_latest_month"], 1)

    def test_tie_keeps_the_original_reader(self):
        df = frame([("1/A", 100.0, 111.0), ("2/B", 100.0, 110.0), ("3/C", 110.0, 111.0)])
        self.assertEqual(ew.detect_rule(df)[0], "inclusive")


class ReaderTests(unittest.TestCase):
    def test_exclusive_reading(self):
        self.assertEqual(ew.listed_until_exclusive(NEW).tolist(), [104.0, 110.0, 107.0, 110.0])

    def test_blank_end_runs_to_latest(self):
        df = frame([("1/A", 100.0, None), ("2/B", 105.0, 108.0)])
        self.assertEqual(ew.listed_until_exclusive(df).tolist(), [105.0, 105.0])

    def test_install_dispatches_and_is_idempotent(self):
        def old_reader(df):
            return pd.Series(["original"] * len(df))
        mod = types.SimpleNamespace(listed_until=old_reader, __version__="0.3.1")
        ew.STATE["calls"].clear()
        ew.install(mod)
        first = mod.listed_until
        ew.install(mod)
        self.assertIs(mod.listed_until, first)
        self.assertIs(mod.listed_until.original, old_reader)
        self.assertEqual(mod.listed_until(OLD).tolist(), ["original"] * 4)
        self.assertEqual(mod.listed_until(NEW).tolist(), [104.0, 110.0, 107.0, 110.0])
        self.assertEqual([c["rule"] for c in ew.STATE["calls"]], ["inclusive", "exclusive"])
        self.assertEqual(ew.STATE["module_version"], "0.3.1")


if __name__ == "__main__":
    unittest.main()
