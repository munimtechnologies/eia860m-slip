"""Unit tests for check_fix2.py's import step (need pandas). Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import unittest

from check_fix2 import add_imports, import_lines

TEST_SRC = """import zipfile
from datetime import date, datetime

import numpy as np
import pyarrow.parquet as pq
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

import pudl.helpers
from pudl.helpers import make_changelog


def test_make_changelog_x():
    assert_frame_equal(np.ones(1), np.ones(1))
"""

MODULE = """import datetime

import numpy as np
import pandas as pd
import pytest

from impl_orig import make_changelog


def _helper():
    return 1


def test_make_changelog_x():
    df = _helper()
    assert_frame_equal(df, df)
"""


class ImportStepTests(unittest.TestCase):
    def test_only_names_asked_for(self):
        self.assertEqual(import_lines(TEST_SRC, {"assert_frame_equal", "np"}),
                         ["import numpy as np",
                          "from pandas.testing import assert_frame_equal"])

    def test_alias_and_dotted_import(self):
        self.assertEqual(import_lines(TEST_SRC, {"pq", "zipfile"}),
                         ["import zipfile", "import pyarrow.parquet as pq"])

    def test_pudl_imports_never_added(self):
        self.assertEqual(import_lines(TEST_SRC, {"pudl", "make_changelog"}), [])

    def test_add_imports_after_make_changelog(self):
        out, lines = add_imports(MODULE, TEST_SRC)
        self.assertEqual(lines, ["from pandas.testing import assert_frame_equal"])
        self.assertIn("from impl_orig import make_changelog\n"
                      "from pandas.testing import assert_frame_equal\n", out)
        self.assertTrue(out.endswith("assert_frame_equal(df, df)\n"))
        compile(out, "<module>", "exec")


if __name__ == "__main__":
    unittest.main()
