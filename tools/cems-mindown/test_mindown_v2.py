"""Unit tests for mindown_v2.py on a small local parquet file (need polars and pyarrow).

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import inspect
import os
import tempfile
import unittest
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq

import mindown_check as mc
import mindown_v2 as v2


def write_parquet(path):
    """Three row groups of four hours each: 2022 CO, 2024 CO, 2024 TX."""
    rows = []
    for year, state in ((2022, "CO"), (2024, "CO"), (2024, "TX")):
        for h in range(4):
            rows.append({"plant_id_eia": 1, "plant_id_epa": 1,
                         "emissions_unit_id_epa": state + "1",
                         "operating_datetime_utc": datetime(year, 3, 1, h), "state": state,
                         "operating_time_hours": 1.0, "gross_load_mw": 10.0 + h,
                         "heat_content_mmbtu": 100.0, "year": year})
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=4)


class FixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="mv2-v2test-")
        cls.path = os.path.join(cls.dir, "hourly.parquet")
        write_parquet(cls.path)

    def test_only_one_attribute_changes(self):
        old = inspect.getsource(mc.read_states)
        self.assertEqual(old.count(v2.OLD), 1)
        self.assertEqual(old.replace(v2.OLD, v2.NEW).count("path_in_schema"), 0)
        self.assertEqual(len(old.replace(v2.OLD, v2.NEW).splitlines()), len(old.splitlines()))

    def test_original_fails_on_schema_column(self):
        with self.assertRaises(AttributeError):
            mc.read_states(pq.ParquetFile(self.path), ["CO"], range(2023, 2026))

    def test_fixed_reads_only_matching_row_group(self):
        fixed = v2.fixed_read_states()
        frames, info = fixed(pq.ParquetFile(self.path), ["CO"], range(2023, 2026))
        self.assertEqual(info["row_groups"], 3)
        self.assertEqual(info["row_groups_read"], 1)
        self.assertEqual(info["missing_columns"], [])
        self.assertEqual(info["state_rows"], {"CO": 4})
        self.assertEqual(sorted(frames), ["CO"])
        self.assertNotIn("year", frames["CO"].columns)
        self.assertEqual(frames["CO"]["gross_load_mw"].to_list(), [10.0, 11.0, 12.0, 13.0])

    def test_fixed_keeps_module_globals(self):
        fixed = v2.fixed_read_states()
        self.assertIs(fixed.__globals__, mc.__dict__)

    def test_main_does_not_patch_on_import(self):
        self.assertEqual(mc.VERSION, "0.1.0")


if __name__ == "__main__":
    unittest.main()
