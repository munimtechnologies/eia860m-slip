"""Tests for steo_text.py (standard library only). MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""

import unittest

import steo_text as st

PAGE = ("Electricity, coal, and renewables\nWe expect the electric power sector to add 21 GW of solar\n"
        "capacity in 2022. Wind capacity grows by 7 gigawatts in our forecast. Coal falls by 12%.\n"
        "Natural gas plants add 5 GW. Solar generation rises 30%.")


class Tests(unittest.TestCase):
    def test_sentences_join_lines(self):
        s = st.sentences(PAGE)
        self.assertIn("Electricity, coal, and renewables We expect the electric power sector to add 21 GW of solar "
                      "capacity in 2022.", s)

    def test_matches(self):
        m = st.matches(PAGE)
        self.assertEqual(len(m), 2)
        self.assertTrue(m[1].startswith("Wind capacity grows by 7 gigawatts"))

    def test_no_amount_no_match(self):
        self.assertEqual(st.matches("Solar generation rises 30%. Wind is flat."), [])


if __name__ == "__main__":
    unittest.main()
