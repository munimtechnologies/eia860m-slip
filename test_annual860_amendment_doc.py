"""Checks the numbers in docs/annual-flows-eia860-amendment-1.md against the raw output of compete
job annual860-v1 (data/annual860_v1.json). MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    with open(os.path.join(HERE, "docs", "annual-flows-eia860-amendment-1.md"),
              encoding="utf-8") as fh:
        doc = fh.read()
    with open(os.path.join(HERE, "data", "annual860_v1.json"), encoding="utf-8") as fh:
        out = json.load(fh)
    return doc, out


def row(out, group, state):
    return next(r for r in out["rows"]
                if (r["year"], r["group"], r["state"]) == (2017, group, state))


def fmt(mw):
    return "{:,.1f}".format(mw)


class AmendmentDocTests(unittest.TestCase):
    def test_checks_as_stated(self):
        doc, out = load()
        c = out["checks"]
        self.assertEqual((c["C1"]["pass"], c["C2"]["pass"], c["C3"]["pass"], c["all_pass"]),
                         (True, False, True, False))
        self.assertEqual(c["C2"]["missing_columns"], ["generator_operating_date"])
        self.assertTrue(c["C2"]["has_2017_and_2018"])
        self.assertNotIn("generator_operating_date", out["meta"]["annual_columns"])
        self.assertEqual((c["C3"]["rows"], c["C3"]["not_adding_up"]), (493, 0))
        self.assertIn("493 rows", doc)
        got = c["C1"]["got"]
        for key in ("all/all", "all/online_in_year", "wind_onshore/all",
                    "wind_onshore/online_in_year", "wind_onshore/slipped"):
            self.assertIn(fmt(got[key]) + " MW", doc)

    def test_no_date_seen(self):
        _, out = load()
        for r in out["rows"]:
            self.assertEqual([r[c] for c in ("before", "in_year", "next_year", "later")],
                             [0.0] * 4)

    def test_caps(self):
        doc, out = load()
        for label, group, state, floor in (("W1", "wind_onshore", "all", 0.75),
                                           ("W2", "wind_onshore", "slipped", 0.50),
                                           ("W3", "all", "all", 0.70)):
            r = row(out, group, state)
            cap = r["undated"] / r["planned_mw"]
            self.assertIn("%s: at most %.3f (%s of %s MW)" % (
                label, cap, fmt(r["undated"]), fmt(r["planned_mw"])), doc)
            self.assertEqual(out["predictions"][label]["floor"], floor)
            self.assertGreater(cap, floor)


if __name__ == "__main__":
    unittest.main()
