"""patch_title: make nextlist 0.1.1 from nextlist.py 0.1.0 (commit ed4cb99) by fixing only the title line.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

In 0.1.0, main() stores the target month's list under res["target"], replacing the month string, so
render() printed the whole list as a Python dict in the page title (docs/nextlist-2026-10.md, line 1).
0.1.1 prints the month. Nothing else changes: each replacement must match exactly once.

    python patch_title.py nextlist.py test_nextlist.py
"""

import sys

OLD_VERSION = '__version__ = "0.1.0"'
NEW_VERSION = '__version__ = "0.1.1"'
OLD_TITLE = ('    md = ["# nextlist %s: EIA-860M generators planned for %s, with the on-time share of earlier ones like '
             'them" % (\n        __version__, res["target"]), "",')
NEW_TITLE = ('    target = res["target"]["month"] if isinstance(res["target"], dict) else res["target"]\n'
             '    md = ["# nextlist %s: EIA-860M generators planned for %s, with the on-time share of earlier ones like '
             'them" % (\n        __version__, target), "",')
TEST_ANCHOR = '\n\nif __name__ == "__main__":\n'
NEW_TEST = '''

class Title(unittest.TestCase):
    def test_title_names_the_month(self):
        # 0.1.0 printed the whole target list here; main() stores the list under res["target"].
        want = ("# nextlist %s: EIA-860M generators planned for 2026-10, with the on-time share of earlier ones "
                "like them" % nl.__version__)
        for target in ("2026-10", {"month": "2026-10", "from": "2026-09", "rows": []}):
            md = nl.render({"target": target, "cohort": {}, "error": "x"})
            self.assertEqual(md.splitlines()[0], want)
'''


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise SystemExit("%s: expected 1 match, found %d" % (what, n))
    return text.replace(old, new)


def patch_tool(src):
    src = replace_once(src, OLD_VERSION, NEW_VERSION, "version")
    return replace_once(src, OLD_TITLE, NEW_TITLE, "title")


def patch_tests(src):
    return replace_once(src, TEST_ANCHOR, NEW_TEST + TEST_ANCHOR, "test anchor")


def main(argv):
    tool, tests = argv[1], argv[2]
    for path, fn in ((tool, patch_tool), (tests, patch_tests)):
        with open(path, encoding="utf-8", newline="") as fh:
            src = fh.read()
        out = fn(src)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
        print("patched %s: %d -> %d bytes" % (path, len(src.encode("utf-8")), len(out.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
