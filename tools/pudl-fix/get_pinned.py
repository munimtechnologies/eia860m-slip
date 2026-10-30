"""Download keep_changes.py and check_fix.py exactly as committed in 840ac28 into the folder
given as the first argument (default /out/pinned) and check their md5s against the ones job
pudl-fix-v1 printed. Apache-2.0. MV2 of Munim, Inc. (made with AI agents)."""

import hashlib
import os
import sys
import urllib.request

SHA = "840ac280dd1a7d70d4124bc405f7c7a3ab4e39d9"
URL = "https://raw.githubusercontent.com/munimtechnologies/eia860m-slip/%s/tools/pudl-fix/%s"
MD5 = {
    "keep_changes.py": "4ffb24b50db7641e3ba91dea7ea7e064",
    "check_fix.py": "5054a0486fc87ea1a1d789b7a2a78c96",
}
UA = {"User-Agent": "mv2-pudl-fix-check/0.2 (MV2, Munim, Inc.; mv2@munimtech.com)"}

out_dir = sys.argv[1] if len(sys.argv) > 1 else "/out/pinned"
os.makedirs(out_dir, exist_ok=True)
ok = True
for name, want in MD5.items():
    req = urllib.request.Request(URL % (SHA, name), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    got = hashlib.md5(data).hexdigest()
    print(name, got, "ok" if got == want else "MISMATCH, expected " + want)
    ok = ok and got == want
    with open(os.path.join(out_dir, name), "wb") as f:
        f.write(data)
sys.exit(0 if ok else 1)
