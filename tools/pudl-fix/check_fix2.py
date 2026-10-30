"""Re-run of check_fix.py 0.1.0 with PUDL's test imports carried over (E2 harness fix).

check_fix.py 0.1.0 copied PUDL's test_make_changelog* tests and the helpers they use out
of tests/unit/helpers_test.py, but not the file's own imports, so 7 of the 8 test cases
stopped with "NameError: name 'assert_frame_equal' is not defined" under both the original
and the patched function. This tool is check_fix.py 0.1.0, unchanged, plus one step: every
top-level import of helpers_test.py (except PUDL's own) that binds a name the copied tests
use is added after the module header. It also counts NameErrors, so a harness miss shows.

The scored page and the re-run's fixed bar are docs/pudl-fix.md in
munimtechnologies/eia860m-slip. PUDL's code (MIT) is downloaded at run time and not stored.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import argparse
import ast
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

# check_fix.py and keep_changes.py as committed in 840ac28, fetched by get_pinned.py.
sys.path.insert(0, os.environ.get("PUDL_FIX_PINNED", "/out/pinned"))

import check_fix as cf  # noqa: E402
import keep_changes as kc  # noqa: E402

VERSION = "0.2.0"
ADDED = []


def import_lines(test_src, names):
    """Top-level import statements of test_src, cut down to the names asked for."""
    lines = []
    for node in ast.parse(test_src).body:
        if isinstance(node, ast.Import):
            keep = [a for a in node.names if not a.name.split(".")[0] == "pudl"
                    and (a.asname or a.name.split(".")[0]) in names]
            if keep:
                lines.append("import " + ", ".join(
                    a.name + (" as " + a.asname if a.asname else "") for a in keep))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module \
                and node.module.split(".")[0] != "pudl":
            keep = [a for a in node.names if (a.asname or a.name) in names]
            if keep:
                lines.append("from %s import %s" % (node.module, ", ".join(
                    a.name + (" as " + a.asname if a.asname else "") for a in keep)))
    return lines


def add_imports(module, test_src):
    """module with the imports it needs from test_src placed after its make_changelog import."""
    tree = ast.parse(module)
    defined = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            defined.update(t.id for t in node.targets if isinstance(t, ast.Name))
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - defined
    lines = import_lines(test_src, used)
    marker = "import make_changelog\n"
    at = module.index(marker) + len(marker)
    return module[:at] + "".join(line + "\n" for line in lines) + module[at:], lines


_ORIGINAL_MODULE = cf.pudl_test_module


def pudl_test_module(test_src, impl_name):
    module, tests = _ORIGINAL_MODULE(test_src, impl_name)
    module, lines = add_imports(module, test_src)
    ADDED[:] = lines
    return module, tests


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-for", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--minutes", type=float, default=90)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    cf.pudl_test_module = pudl_test_module
    result = {"tool": "check_fix2.py " + VERSION, "check_fix": cf.VERSION,
              "keep_changes": kc.VERSION, "python": sys.version.split()[0],
              "pandas": pd.__version__, "numpy": np.__version__}
    if a.wait_for:
        live, polls, at = cf.wait_for(a.wait_for, a.token, a.minutes)
        result["page_live"] = {"live": live, "polls": polls, "at": at}
    result["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    srcs = {}
    for sha in (cf.SHA_OLD, cf.SHA_NEW):
        raw = cf.fetch(cf.RAW % (sha, "src/pudl/helpers.py"))
        func = cf.extract(raw.decode("utf-8"))
        srcs[sha] = func
        result["helpers_" + sha[:7]] = {
            "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "make_changelog_md5": hashlib.md5(func.encode("utf-8")).hexdigest()}
    orig_src = srcs[cf.SHA_NEW]
    result["E1"] = {"same_function_text": srcs[cf.SHA_OLD] == srcs[cf.SHA_NEW],
                    "target_count": orig_src.count(kc.TARGET)}
    patched_src = kc.patch_source(orig_src)
    orig, patched = cf.load(orig_src), cf.load(patched_src)

    test_raw = cf.fetch(cf.RAW % (cf.SHA_NEW, "tests/unit/helpers_test.py"))
    result["helpers_test_" + cf.SHA_NEW[:7]] = {"bytes": len(test_raw),
                                                "md5": hashlib.md5(test_raw).hexdigest()}
    e2 = cf.run_pudl_tests(test_raw.decode("utf-8"), orig_src, patched_src,
                           os.path.join(a.out_dir, "gen"))
    e2["imports_added"] = list(ADDED)
    e2["name_errors"] = sum("NameError" in text for text in e2["errors"].values())
    result["E2"] = e2
    result["E3"] = cf.check_cases(orig, patched)
    result["E4"] = cf.check_random(orig, patched)
    result["E5"] = cf.check_missing(orig, patched)
    result["E6"] = cf.check_tall(orig, patched)
    result["E7"] = cf.check_bench(orig, patched)
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(os.path.join(a.out_dir, "fix_check2.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
