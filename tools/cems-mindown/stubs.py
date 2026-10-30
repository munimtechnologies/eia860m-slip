"""Lets PUDL's operational_characteristics.py and its unit tests run without installing PUDL.

Writes a minimal package tree:
  <root>/dagster.py                      asset/AssetIn/Field/AssetExecutionContext stand-ins
  <root>/pudl/logging_helpers.py         get_logger -> logging.getLogger
  <root>/pudl/metadata/enums.py          EPACEMS_STATES (used only by the Dagster asset)
  <root>/pudl/analysis/operational_characteristics.py   PUDL's file, unchanged
and a test folder with PUDL's test file, unchanged, and a conftest.py that applies
fill_isolated.patch(mode) from the MV2_PATCH environment variable before the tests import.

Nothing here changes PUDL's code; the Dagster stand-ins only make the decorators no-ops.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import os

DAGSTER_STUB = '''"""Stand-in for the parts of dagster that operational_characteristics.py imports."""


class AssetExecutionContext:
    pass


class AssetIn:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


class Field:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


def asset(*args, **kwargs):
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return args[0]
    return lambda fn: fn
'''

LOGGING_STUB = '''import logging


def get_logger(name):
    return logging.getLogger(name)
'''

ENUMS_STUB = '''EPACEMS_STATES = ["CO", "IN", "WI"]
'''

CONFTEST = '''import os

import fill_isolated
import pudl.analysis.operational_characteristics as oc

fill_isolated.patch(oc, os.environ.get("MV2_PATCH", "none"))
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def build(root, module_source, test_source=None):
    """Write the stub tree under root; returns (package_root, test_dir or None)."""
    pkg = os.path.join(root, "pkg")
    write(os.path.join(pkg, "dagster.py"), DAGSTER_STUB)
    write(os.path.join(pkg, "pudl", "__init__.py"), "")
    write(os.path.join(pkg, "pudl", "logging_helpers.py"), LOGGING_STUB)
    write(os.path.join(pkg, "pudl", "metadata", "__init__.py"), "")
    write(os.path.join(pkg, "pudl", "metadata", "enums.py"), ENUMS_STUB)
    write(os.path.join(pkg, "pudl", "analysis", "__init__.py"), "")
    write(os.path.join(pkg, "pudl", "analysis", "operational_characteristics.py"),
          module_source)
    tests = None
    if test_source is not None:
        tests = os.path.join(root, "tests")
        write(os.path.join(tests, "operational_characteristics_test.py"), test_source)
        write(os.path.join(tests, "conftest.py"), CONFTEST)
    return pkg, tests
