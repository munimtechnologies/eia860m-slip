"""Tests for wait_eia.py. MV2 of Munim, Inc. (made with AI agents). Apache-2.0."""

import unittest

import wait_eia as we

XLSX = b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\x00\x00"
HTML = b"<!DOCTYPE html>\n<h"


class UrlTests(unittest.TestCase):
    def test_urls(self):
        self.assertEqual(we.urls("2026-09"), [
            "https://www.eia.gov/electricity/data/eia860m/archive/xls/september_generator2026.xlsx",
            "https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx"])

    def test_deadline(self):
        self.assertEqual(we.deadline_ts("1970-01-01T01:00"), 3600)


class ServedTests(unittest.TestCase):
    def test_current_address(self):
        url, b = we.served("2026-09", get=lambda u: XLSX if "/xls/sep" in u and "archive" not in u else HTML)
        self.assertTrue(url.endswith("/xls/september_generator2026.xlsx"))
        self.assertNotIn("archive", url)

    def test_error_recorded(self):
        def get(u):
            raise OSError("boom")
        url, notes = we.served("2026-09", get=get)
        self.assertIsNone(url)
        self.assertEqual(len(notes), 2)
        self.assertTrue(notes[0].endswith(": OSError"))


class WaitTests(unittest.TestCase):
    def run_wait(self, pages, deadline, every=10):
        t = [0.0]
        slept, logs = [], []

        def get(u):
            return pages[int(t[0] // every)] if "archive" not in u else HTML

        def sleep(s):
            slept.append(s)
            t[0] += s

        url = we.wait("2026-09", deadline, every, get=get, clock=lambda: t[0], sleep=sleep, log=logs.append)
        return url, slept, logs

    def test_served_on_third_try(self):
        url, slept, logs = self.run_wait([HTML, HTML, XLSX], deadline=100)
        self.assertTrue(url.endswith("september_generator2026.xlsx"))
        self.assertEqual(slept, [10, 10])
        self.assertEqual(len(logs), 3)

    def test_deadline(self):
        url, slept, logs = self.run_wait([HTML] * 10, deadline=25)
        self.assertIsNone(url)
        self.assertEqual(slept, [10, 10])
        self.assertIn("deadline passed", logs[-1])


if __name__ == "__main__":
    unittest.main()
