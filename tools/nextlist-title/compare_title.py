"""compare_title: is nextlist 0.1.1's output the published 0.1.0 output with only the title fixed?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Compares a fresh run of nextlist 0.1.1 (same arguments as job nextlist-v1) with the files published at
commit ed4cb99. Held when: the page differs only in line 1, and line 1 is the fixed title; the three CSV
files are byte-identical; the JSON differs only in version, started_at and finished_at.

    python compare_title.py --published pub --rebuilt /out/nextlist --out /out/compare.json
"""

import argparse
import json
import os
import sys

CSVS = ("nextlist_2026-10.csv", "nextlist_2026-09.csv", "nextlist_backtest_months.csv")
JSON_FREE = ("version", "started_at", "finished_at")
TITLE = ("# nextlist 0.1.1: EIA-860M generators planned for 2026-10, with the on-time share of earlier ones like "
         "them")


def read(path, mode="r"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8", "newline": ""})) as fh:
        return fh.read()


def compare_pages(pub, new):
    a, b = pub.split("\n"), new.split("\n")
    diff = [i + 1 for i in range(max(len(a), len(b))) if (a[i:i + 1] or [None]) != (b[i:i + 1] or [None])]
    return {"published_lines": len(a), "rebuilt_lines": len(b), "lines_differ": diff[:20],
            "lines_differ_count": len(diff), "published_title_chars": len(a[0]), "rebuilt_title": b[0],
            "held": diff == [1] and b[0] == TITLE}


def compare_json(pub, new):
    keys = sorted(set(pub) | set(new))
    differ = [k for k in keys if pub.get(k) != new.get(k)]
    return {"keys_differ": differ, "held": all(k in JSON_FREE for k in differ)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--published", required=True)
    ap.add_argument("--rebuilt", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = {"page": compare_pages(read(os.path.join(a.published, "nextlist.md")),
                                 read(os.path.join(a.rebuilt, "nextlist.md")))}
    res["csv"] = {}
    for name in CSVS:
        p, r = read(os.path.join(a.published, name), "rb"), read(os.path.join(a.rebuilt, name), "rb")
        res["csv"][name] = {"published_bytes": len(p), "rebuilt_bytes": len(r), "identical": p == r}
    res["json"] = compare_json(json.loads(read(os.path.join(a.published, "nextlist.json"))),
                               json.loads(read(os.path.join(a.rebuilt, "nextlist.json"))))
    res["held"] = res["page"]["held"] and res["json"]["held"] and all(x["identical"] for x in res["csv"].values())
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    print("T1 %s" % ("held" if res["held"] else "failed"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
