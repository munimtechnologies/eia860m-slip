"""Doc test: what README.md says about the thirtieth result and the September 2026 plan matches
the notes themselves (docs/annualids.md, docs/sep2026-plan.md).

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class ReadmeIndexTests(unittest.TestCase):
    def setUp(self):
        self.readme = read("README.md")

    def test_annualids(self):
        doc = read("docs", "annualids.md")
        self.assertIn("2 of 2 predictions held.", doc)
        self.assertIn("| 30 | Retired generators only the monthly file lists are at plants the annual file "
                      "no longer lists (2 of 2 held) | [`annualids.md`](docs/annualids.md) |", self.readme)
        self.assertIn("(thirtieth result, scored; 2 of 2 held)", self.readme)
        for s in ("2,703 generators retired in 2002 to 2025", "(87,678.1 MW)", "2,703 of 2,703"):
            self.assertIn(s, doc)
        self.assertIn("lists 2,703 generators retired in 2002 to 2025 (87,678.1 MW)", self.readme)
        self.assertIn("Every one of the 2,703 is at a plant that the annual 2025 file lists on no sheet.", doc)

    def test_sep2026_plan(self):
        doc = read("docs", "sep2026-plan.md")
        self.assertIn("Status: pre-registered, not yet scored.", doc)
        self.assertIn("Pre-registered, not yet scored: [`sep2026-plan.md`](docs/sep2026-plan.md)", self.readme)
        for s in ("within 3% of August 2026's", "At most 50 generators leave in September 2026.",
                  "Fewer than 10 of the generators that leave in September 2026 were on the Retired sheet",
                  "of the shares of the 24 months before it"):
            self.assertIn(s, doc)
        for s in ("at most 50 generators leave", "fewer than 10 of them leave from the Retired sheet",
                  "between the second lowest and the second highest of the 24 months before"):
            self.assertIn(s, self.readme)

    def test_links_kept(self):
        for name in ("changelog-revert.md", "history-revert.md", "heldtrace.md", "annualids.md",
                     "sep2026-plan.md", "eia860m-changelog-from-workbooks.md"):
            self.assertIn("(docs/%s)" % name, self.readme)
        self.assertIn("117,110 rows from July 2015 to August 2026", self.readme)


if __name__ == "__main__":
    unittest.main()
