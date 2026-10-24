"""Doc test: the dated update of 24 October 2026 at the end of docs/nexttechonce.md (first and repeat
listings) is recomputed from data/nexttech_cohort.csv, and the sentences it corrects are still there.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EARLY, LATE = ("2016-01", "2019-12"), ("2022-01", "2025-12")
UPDATE = "## Update, 24 October 2026: more repeat listings explain almost none of the extra fall"


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as fh:
        return fh.read()


def n(x):
    return "{:,}".format(x)


class NexttechonceUpdateDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read("docs", "nexttechonce.md")
        cls.upd = cls.doc[cls.doc.index(UPDATE):]
        with open(os.path.join(HERE, "data", "nexttech_cohort.csv"), newline="", encoding="utf-8") as fh:
            co = list(csv.DictReader(fh))
        cls.k = {}
        for p in (EARLY, LATE):
            seen, first, rep = set(), [0, 0], [0, 0]
            for r in sorted((r for r in co if p[0] <= r["month"] <= p[1]), key=lambda r: r["month"]):
                c = rep if r["key"] in seen else first
                seen.add(r["key"])
                c[1] += 1
                c[0] += r["now"] == "Operating"
            cls.k[p] = {"first": tuple(first), "repeat": tuple(rep),
                        "all": (first[0] + rep[0], first[1] + rep[1])}

    def s(self, p, kind):
        op, k = self.k[p][kind]
        return op / k

    def w(self, p, kind):
        return self.k[p][kind][1] / self.k[p]["all"][1]

    def test_counts(self):
        self.assertEqual(self.k[EARLY], {"first": (1006, 2179), "repeat": (974, 2044), "all": (1980, 4223)})
        self.assertEqual(self.k[LATE], {"first": (915, 2532), "repeat": (1195, 3515), "all": (2110, 6047)})

    def test_mix(self):
        for p, years in ((EARLY, "2016-2019"), (LATE, "2022-2025")):
            self.assertIn("%.1f%% of the generator-months of %s (%s of %s)" % (
                100 * self.w(p, "repeat"), years, n(self.k[p]["repeat"][1]), n(self.k[p]["all"][1])) if p == EARLY
                else "%.1f%% of those of %s (%s of %s)" % (
                100 * self.w(p, "repeat"), years, n(self.k[p]["repeat"][1]), n(self.k[p]["all"][1])), self.upd)

    def test_standardized(self):
        total = self.s(EARLY, "all") - self.s(LATE, "all")
        std = sum(self.w(EARLY, c) * self.s(LATE, c) for c in ("first", "repeat"))
        mix = std - self.s(LATE, "all")
        self.assertEqual(("%.3f" % std, "%.3f" % self.s(LATE, "all"), "%.3f" % mix, "%.3f" % total),
                         ("0.351", "0.349", "0.002", "0.120"))
        self.assertTrue(0 < mix / total < 0.02)
        self.assertTrue(0.975 < (self.s(EARLY, "all") - std) / total < 0.985)
        self.assertIn("2022-2025's generator-month share would be 0.351 instead of 0.349. The change in mix accounts "
                      "for 0.002 of the 0.120 fall, under 2%; about 98% is the fall inside each kind of listing.", self.upd)

    def test_other_weights(self):
        alt = sum(self.w(LATE, c) * self.s(EARLY, c) for c in ("first", "repeat"))
        self.assertGreater(alt, self.s(EARLY, "all"))
        self.assertEqual(("%.3f" % alt, "%.3f" % self.s(EARLY, "all")), ("0.470", "0.469"))
        self.assertGreater(self.s(EARLY, "repeat"), self.s(EARLY, "first"))
        self.assertLess(self.s(LATE, "repeat"), self.s(LATE, "first"))
        self.assertIn("2016-2019's share would have been 0.470 instead of 0.469: slightly higher", self.upd)

    def test_steeper(self):
        fr = self.s(EARLY, "repeat") - self.s(LATE, "repeat")
        ff = self.s(EARLY, "first") - self.s(LATE, "first")
        self.assertGreater(fr, ff)
        self.assertIn("fell by %.3f (%.3f to %.3f), against %.3f for first listings (%.3f to %.3f)" % (
            fr, self.s(EARLY, "repeat"), self.s(LATE, "repeat"), ff, self.s(EARLY, "first"),
            self.s(LATE, "first")), self.upd)
        self.assertEqual(("%.3f" % fr, "%.3f" % ff), ("0.137", "0.100"))

    def test_corrected_sentences_kept(self):
        before = self.doc[:self.doc.index(UPDATE)]
        for s in ("so more repeat listings pull the generator-month share down further",
                  "which is part of why the generator-month series fell as far as it did",
                  "*Corrected on 24 October 2026: the rise in the number of repeat listings explains almost none of "
                  "the gap between the two falls; their steeper fall does. See the update at the end of this note.*"):
            self.assertIn(s, before)
        for s in ('"more repeat listings pull the generator-month share down further"',
                  '"is part of why the generator-month series fell as far as it did"',
                  "[`test_nexttechonce_update_doc.py`](../test_nexttechonce_update_doc.py)"):
            self.assertIn(s, self.upd)


if __name__ == "__main__":
    unittest.main()
