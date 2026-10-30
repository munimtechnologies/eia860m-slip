"""Download check_fix.py and keep_changes.py as committed in 840ac28 and check_fix2.py as
committed in a8926e1 into the folder given as the first argument (default /out/pinned), and
check their md5s against the ones jobs pudl-fix-v1 and pudl-fix-v2 printed.
Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import hashlib
import os
import sys
import urllib.request

URL = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/%s/tools/pudl-fix/%s"
PINNED = [
    ("840ac280dd1a7d70d4124bc405f7c7a3ab4e39d9", "keep_changes.py",
     "4ffb24b50db7641e3ba91dea7ea7e064"),
    ("840ac280dd1a7d70d4124bc405f7c7a3ab4e39d9", "check_fix.py",
     "5054a0486fc87ea1a1d789b7a2a78c96"),
    ("a8926e1fee5a7c8ec6fac9b74489457d546973fc", "check_fix2.py", "7778e066becebc113379a7bde29a07ff"),
]
UA = {"User-Agent": "mv2-pudl-pr-check/0.1 (MV2, Munim, Inc.; mv2@munimtech.com)"}

out_dir = sys.argv[1] if len(sys.argv) > 1 else "/out/pinned"
os.makedirs(out_dir, exist_ok=True)
ok = True
for sha, name, want in PINNED:
    req = urllib.request.Request(URL % (sha, name), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    got = hashlib.md5(data).hexdigest()
    print(name, got, "ok" if got == want else "MISMATCH, expected " + want)
    ok = ok and got == want
    with open(os.path.join(out_dir, name), "wb") as f:
        f.write(data)
sys.exit(0 if ok else 1)
