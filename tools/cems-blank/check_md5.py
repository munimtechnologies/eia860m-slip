"""Prints the md5 of every file job cems-blank-v1 runs and stops the job unless the five
tools/cems-mindown files equal the ones job cems-mindown-v3 checked.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import hashlib
import sys

PINNED = {"fill_isolated.py": "2d53f47ee6cdc563852d1a8ca22f2d04",
          "reference.py": "6bf95c64b5d92241ae6354bf9e8ee7e0",
          "stubs.py": "7a9833ebd0cae3a894704bf93a491707",
          "mindown_check.py": "2fbec382159a62d6fa3f1bd65754fe12",
          "mindown_v2.py": "28dc58b1e62da86ffc8543a38ba2b6db"}
OURS = ("blank_check.py", "test_blank_check.py", "v3_units.csv")


def md5(name):
    with open(name, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    bad = []
    for name in list(PINNED) + list(OURS):
        got = md5(name)
        print(name, got)
        if name in PINNED and got != PINNED[name]:
            bad.append(name)
    if bad:
        print("md5 differs from cems-mindown-v3:", bad)
        sys.exit(1)
    print("all 5 pinned md5 equal cems-mindown-v3")


if __name__ == "__main__":
    main()
