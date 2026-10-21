"""Unit tests for zenodoprobe on hand-built JSON. MV2 of Munim, Inc. (made with AI agents).
Apache-2.0."""

import os
import tempfile
import unittest

import zenodoprobe as zp


def version(vid, date, files, ver=None):
    return {"id": vid, "version": ver, "publication_date": date, "created": None, "files": files}


def f(key, checksum, size=1):
    return {"key": key, "size": size, "checksum": checksum}


class ParseTests(unittest.TestCase):
    def test_page_url(self):
        self.assertEqual(zp.page_url("https://x/versions", 2), "https://x/versions?size=25&page=2")
        self.assertEqual(zp.page_url("https://x/versions?a=1", 1),
                         "https://x/versions?a=1&size=25&page=1")

    def test_version_rows(self):
        page = {"hits": {"hits": [
            {"id": 11, "created": "2024-06-20T10:00:00+00:00",
             "metadata": {"version": "9.0.0", "publication_date": "2024-06-20"}},
            {"id": "12", "metadata": {}}]}}
        self.assertEqual(zp.version_rows(page), [
            {"id": "11", "version": "9.0.0", "publication_date": "2024-06-20",
             "created": "2024-06-20T10:00:00+00:00"},
            {"id": "12", "version": None, "publication_date": None, "created": None}])
        self.assertEqual(zp.version_rows(None), [])
        self.assertEqual(zp.version_rows({"hits": {}}), [])

    def test_file_rows_list(self):
        rec = {"files": [f("b.zip", "md5:2", 2), f("a.zip", "md5:1"), {"size": 3}]}
        self.assertEqual(zp.file_rows(rec), [f("a.zip", "md5:1"), f("b.zip", "md5:2", 2)])

    def test_file_rows_entries(self):
        rec = {"files": {"enabled": True, "entries": {"a.zip": f("a.zip", "md5:1")}}}
        self.assertEqual(zp.file_rows(rec), [f("a.zip", "md5:1")])
        listing = {"entries": [f("a.zip", "x")]}
        self.assertEqual(zp.file_rows(listing), [f("a.zip", "x")])

    def test_file_rows_nothing(self):
        self.assertEqual(zp.file_rows({"files": {"enabled": True, "count": 3}}), [])
        self.assertEqual(zp.file_rows(None), [])
        self.assertEqual(zp.file_rows({"files": None}), [])

    def test_history(self):
        vs = [version("3", "2024-09-24", [f("eia860-2023.zip", "c2")]),
              version("1", "2024-06-20", [f("eia860-2023.zip", "c1")]),
              version("2", "2024-07-15", [f("eia860-2023.zip", "c1"), f("eia860-2022.zip", "b")])]
        h = zp.history(vs)
        self.assertEqual([(x["checksum"], x["first_id"], x["first_date"])
                          for x in h["eia860-2023.zip"]],
                         [("c1", "1", "2024-06-20"), ("c2", "3", "2024-09-24")])
        self.assertEqual([x["first_id"] for x in h["eia860-2022.zip"]], ["2"])

    def test_er_urls(self):
        self.assertEqual(zp.er_urls(2019), [
            "https://www.eia.gov/electricity/data/eia860/xls/eia8602019ER.zip",
            "https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602019ER.zip"])

    def test_as_json(self):
        self.assertEqual(zp.as_json(b'{"a": 1}'), {"a": 1})
        self.assertIsNone(zp.as_json(b"<html>"))
        self.assertIsNone(zp.as_json(None))


class OutputTests(unittest.TestCase):
    def test_fetch_never_raises(self):
        status, _, _, body, err = zp.fetch("http://127.0.0.1:9/", timeout=5)
        self.assertIsNone(body)
        self.assertTrue(err)
        self.assertNotEqual(status, 200)

    def test_write_md(self):
        vs = [version("1", "2024-06-20", [f("eia860-2023.zip", "c1"), f("datapackage.json", "d")],
                      "9.0.0")]
        z = {"versions_url": "https://x/versions", "versions": vs, "history": zp.history(vs)}
        eia = [{"year": 2019, "url": "u", "status": 404, "content_type": "text/html",
                "content_length": None, "error": "HTTP 404"}]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "z.md")
            zp.write_md(path, z, eia, [{}, {}])
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("1 versions found; 2 calls in all.", text)
        self.assertIn("| 1 | 9.0.0 | 2024-06-20 | 2 | eia860-2023.zip |", text)
        self.assertIn("| eia860-2023.zip | 1 | 2024-06-20 | 9.0.0 | 1 | 1 | c1 |", text)
        self.assertIn("| 2019 | u | 404 | text/html | None | HTTP 404 |", text)


if __name__ == "__main__":
    unittest.main()
