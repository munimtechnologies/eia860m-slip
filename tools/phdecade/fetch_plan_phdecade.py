"""Waits until docs/phdecade-plan.md is live on eia860m-slip main, then downloads the committed
tools/phdecade files (phdecade.py, test_phdecade.py) over the workdir copies and prints their md5s,
so job phdecade-v1 reads no data before the plan is public and runs the code published with it.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import hashlib
import sys
import time
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/main/"
PLAN = RAW + "docs/phdecade-plan.md"
TOKEN = "Pre-registration id: phdecade-1."
FILES = ("phdecade.py", "test_phdecade.py")
UA = {"User-Agent": "mv2-phdecade/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main(minutes=360):
    deadline = time.time() + minutes * 60
    polls = 0
    while True:
        polls += 1
        try:
            if TOKEN in get(PLAN).decode("utf-8", "replace"):
                break
        except Exception:
            pass
        if time.time() > deadline:
            print("plan not live after %d polls (%s); no data read" % (polls, now()))
            sys.exit(1)
        time.sleep(60)
    print("plan live at poll %d (%s)" % (polls, now()))
    for name in FILES:
        for attempt in range(10):
            try:
                raw = get(RAW + "tools/phdecade/" + name)
                break
            except Exception as exc:
                print(name, "attempt", attempt + 1, exc)
                time.sleep(60)
        else:
            sys.exit(1)
        with open(name, "wb") as fh:
            fh.write(raw)
        print("fetched", name, len(raw), "bytes, md5", hashlib.md5(raw).hexdigest())


if __name__ == "__main__":
    main()
