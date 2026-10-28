"""fetch: download the pinned code and the published 0.1.0 output for job nltitle-v1, printing size and md5.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.
"""

import hashlib
import os
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/%s/%s"
NEXTLIST = "ed4cb99182d89a483062913a6685b305b3eb392a"
FILES = [
    ("1d64a6ac310fea676a5e8e6974eca8cb61c69264", "tools/annual-flows-candidate/nextcount.py", "nextcount.py"),
    ("cf668cf9873b1fd531ae3f49707456269545e7ce", "tools/annual-flows-candidate/xlsxprobe.py", "xlsxprobe.py"),
    ("329b7e6206b487312364a03fd2352bac3400bff4", "tools/annual-flows-candidate/eia860m_slip.py", "eia860m_slip.py"),
    (NEXTLIST, "tools/annual-flows-candidate/nextlist.py", "nextlist.py"),
    (NEXTLIST, "tools/annual-flows-candidate/test_nextlist.py", "test_nextlist.py"),
    (NEXTLIST, "docs/nextlist-2026-10.md", "pub/nextlist.md"),
    (NEXTLIST, "data/nextlist_v1.json", "pub/nextlist.json"),
    (NEXTLIST, "data/nextlist_2026-10.csv", "pub/nextlist_2026-10.csv"),
    (NEXTLIST, "data/nextlist_2026-09.csv", "pub/nextlist_2026-09.csv"),
    (NEXTLIST, "data/nextlist_backtest_months.csv", "pub/nextlist_backtest_months.csv"),
]


def main():
    os.makedirs("pub", exist_ok=True)
    for sha, path, dest in FILES:
        with urllib.request.urlopen(RAW % (sha, path), timeout=120) as resp:
            data = resp.read()
        with open(dest, "wb") as fh:
            fh.write(data)
        print("%s@%s -> %s: %d bytes, md5 %s" % (path, sha[:7], dest, len(data), hashlib.md5(data).hexdigest()))


if __name__ == "__main__":
    main()
