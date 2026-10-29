"""Doc test: what README.md says about the September 2026 coal result (docs/coalsep.md) and the two plans added
on 28 October 2026 (docs/renew-plan.md, docs/coaloct-plan.md) matches the notes themselves, and the
paragraphs around the additions are unchanged.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

HEAD = "**EIA-860M records no U.S. coal retirement from January to September 2026.**"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


class ReadmeCoalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = read("README.md")
        cls.coalsep = read("docs", "coalsep.md")
        cls.coaloct = read("docs", "coaloct-plan.md")
        cls.renew = read("docs", "renew-plan.md")

    def test_coal_paragraph(self):
        self.assertIn(HEAD + " [`docs/coalsep.md`](docs/coalsep.md) (scored against "
                      "[`docs/coalsep-plan.md`](docs/coalsep-plan.md); the gate and 3 of 3 predictions held)",
                      self.readme)
        self.assertIn("Status: scored against its pre-registration. The gate held and 3 of 3 predictions held.",
                      self.coalsep)
        self.assertIn("no coal generator is on its Retired sheet with retirement year 2026.", self.readme)
        self.assertIn("**No coal generator is on the Retired sheet of EIA's September 2026 EIA-860M workbook with "
                      "retirement year 2026.**", self.coalsep)
        self.assertIn("because PUDL's changelog then ended with August", self.readme)
        self.assertIn("The source changed from PUDL's changelog (which still ends with August)", self.coalsep)
        self.assertIn("3,584.5 MW in 9 units, 2,569.5 MW is at plants held open by DOE 202(c) orders", self.readme)
        self.assertIn("3,584.5 MW in 9 units; 2,569.5 MW under orders", self.coalsep)
        self.assertIn("each new month is the month the order now in force expires", self.coalsep)
        self.assertIn("the earliest is Campbell 1-3 (1,330.5 MW), dated 2026-11, the month its order 202-26-39 "
                      "expires", self.coalsep)
        self.assertIn("Whether EIA's October 2026 workbook still shows no 2026 coal retirement is pre-registered in "
                      "[`docs/coaloct-plan.md`](docs/coaloct-plan.md).", self.readme)
        self.assertIn("| O1 | No coal row on the Retired sheet has retirement year 2026. |", self.coaloct)

    def test_plans_paragraph(self):
        self.assertIn("Status: pre-registered, not yet scored.", self.coaloct)
        self.assertIn("Status: pre-registered, not yet scored.", self.renew)
        self.assertIn("Also [`renew-plan.md`](docs/renew-plan.md) (whether DOE renews each of its open 202(c) orders "
                      "in time, ten forecasts with stated chances, scored on 1 December 2026 and 1 January 2027) and "
                      "[`coaloct-plan.md`](docs/coaloct-plan.md) (coal in EIA's October 2026 workbook, three bars "
                      "after a reproduction gate).", self.readme)
        rows = [ln for ln in self.renew.splitlines() if ln.startswith("| R")]
        self.assertEqual(len(rows), 10)
        self.assertIn("- R1 to R6 are scored on 1 December 2026, and R7 to R10 and T1 on 1 January 2027", self.renew)
        bars = [ln for ln in self.coaloct.splitlines() if ln.startswith("| O")]
        self.assertEqual(len(bars), 3)
        self.assertIn("## Gate G2 (reproduction)", self.coaloct)

    def test_placement_and_neighbours(self):
        listing = self.readme.index("**A list of every generator planned for October 2026, with base rates.**")
        coal = self.readme.index(HEAD)
        results = self.readme.index("## All results")
        self.assertLess(listing, coal)
        self.assertLess(coal, results)
        self.assertEqual(self.readme.count(HEAD), 1)
        self.assertEqual(self.readme.count("Also [`renew-plan.md`]"), 1)
        for s in ("p describes earlier generators like each one; it is not a forecast made with knowledge of any "
                  "plant, and it is not advice.\n\n" + HEAD,
                  "than the technology group's share, two bars). Also [`renew-plan.md`](docs/renew-plan.md)",
                  "three bars after a reproduction gate).\n\nThe code that will score October 2026,",
                  "| 6 | Coal, row by row; no coal retired in January-August 2026 | [`coal-rows.md`](docs/coal-rows.md) |",
                  "Code: Apache License 2.0 (see LICENSE)."):
            self.assertIn(s, self.readme)
        self.assertNotIn("MIT", self.readme)


if __name__ == "__main__":
    unittest.main()
