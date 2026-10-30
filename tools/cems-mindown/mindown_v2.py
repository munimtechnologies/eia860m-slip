"""Re-run wrapper for the cems-mindown-1 check (re-run id cems-mindown-1-R).

Job cems-mindown-v1 stopped before its real-data step: read_states in mindown_check.py 0.1.0
asks a pyarrow ColumnSchema for path_in_schema, an attribute only ColumnChunkMetaData has
(the schema column calls it path). This wrapper takes read_states' own source, replaces that
one attribute and nothing else, and runs mindown_check.main unchanged: same bars, states,
report year, read cap and scoring code as docs/cems-mindown-plan.md. mindown_check.py itself
stays at 0.1.0.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import inspect

import mindown_check as mc

VERSION = "0.1.0"
OLD = "md.schema.column(j).path_in_schema"
NEW = "md.schema.column(j).path"


def fixed_read_states(module=mc):
    """module.read_states with OLD replaced by NEW; raises if OLD is not there exactly once."""
    src = inspect.getsource(module.read_states)
    if src.count(OLD) != 1:
        raise RuntimeError("read_states does not hold the line this fix replaces")
    names = {}
    exec(compile(src.replace(OLD, NEW), module.__file__, "exec"), module.__dict__, names)
    return names["read_states"]


def main(argv=None):
    mc.read_states = fixed_read_states()
    mc.VERSION = "%s via mindown_v2.py %s" % (mc.VERSION, VERSION)
    mc.main(argv)


if __name__ == "__main__":
    main()
