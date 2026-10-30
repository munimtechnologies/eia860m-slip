"""A candidate fix for PUDL issue #5514: an isolated hour with no reported load counts as a
one-hour "down" run in out_epacems__yearly_operational_characteristics.

PUDL's calculate_min_up_or_down_times (src/pudl/analysis/operational_characteristics.py)
treats every hour whose load_factor_bin is null as "down". An hour with no reported
gross_load_mw between two operating hours is a blank report, not a shutdown, so
min_down_time_hours collapses to 1 for any unit that has one.

fill_isolated_null_bins gives such an hour the previous hour's bin before run detection:
a null bin is filled only when the same unit has a non-null bin exactly one hour before and
exactly one hour after it. Two or more blank hours in a row are left alone. This is the
"carry-forward" option proposed in the issue.

patch(module, mode) wraps the module's calculate_min_up_or_down_times without changing any
of PUDL's code:
  "none"  no change
  "sort"  sort the hourly frame by unit and hour first (nothing else)
  "fill"  sort, then fill isolated null bins

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import polars as pl

VERSION = "0.1.0"
TIME_COL = "operating_datetime_utc"
BIN_COL = "load_factor_bin"


def sort_hours(df, unit_cols, time_col=TIME_COL):
    return df.sort(list(unit_cols) + [time_col])


def isolated_null_expr(unit_cols, bin_col=BIN_COL, time_col=TIME_COL):
    """True for a null bin with a non-null bin of the same unit exactly 1 h on each side.

    Assumes rows sorted by unit_cols and time_col.
    """
    same_prev = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(1)) for c in unit_cols])
    same_next = pl.all_horizontal([pl.col(c).eq(pl.col(c).shift(-1)) for c in unit_cols])
    hour_before = (pl.col(time_col) - pl.col(time_col).shift(1)).dt.total_seconds().eq(3600)
    hour_after = (pl.col(time_col).shift(-1) - pl.col(time_col)).dt.total_seconds().eq(3600)
    return (
        pl.col(bin_col).is_null()
        & pl.col(bin_col).shift(1).is_not_null()
        & pl.col(bin_col).shift(-1).is_not_null()
        & same_prev
        & same_next
        & hour_before
        & hour_after
    ).fill_null(False)


def count_isolated_null_bins(df, unit_cols, bin_col=BIN_COL, time_col=TIME_COL):
    df = sort_hours(df, unit_cols, time_col)
    return int(df.select(isolated_null_expr(unit_cols, bin_col, time_col).sum()).item())


def fill_isolated_null_bins(df, unit_cols, bin_col=BIN_COL, time_col=TIME_COL):
    """Sorted copy of df where each isolated null bin takes the previous hour's bin."""
    df = sort_hours(df, unit_cols, time_col)
    isolated = isolated_null_expr(unit_cols, bin_col, time_col)
    return df.with_columns(
        pl.when(isolated)
        .then(pl.col(bin_col).shift(1))
        .otherwise(pl.col(bin_col))
        .alias(bin_col)
    )


def is_sorted_hours(df, unit_cols, time_col=TIME_COL):
    keys = list(unit_cols) + [time_col]
    return df.select(keys).equals(df.sort(keys).select(keys))


def patch(module, mode, probe=None):
    """Replace module.calculate_min_up_or_down_times with a wrapper; returns the original.

    probe, if given, is a list; each call appends a dict saying whether the hourly frame came
    in sorted, its rows and its isolated null bins (counted, not changed, in every mode).
    """
    if mode not in ("none", "sort", "fill"):
        raise ValueError(mode)
    original = module.calculate_min_up_or_down_times

    def calculate_min_up_or_down_times(output, cems_with_stable_bins, unit_cols, up_or_down):
        if probe is not None:
            probe.append({
                "up_or_down": up_or_down,
                "sorted": is_sorted_hours(cems_with_stable_bins, unit_cols),
                "rows": cems_with_stable_bins.height,
                "isolated_null_bins": count_isolated_null_bins(cems_with_stable_bins,
                                                               unit_cols),
            })
        if mode == "sort":
            cems_with_stable_bins = sort_hours(cems_with_stable_bins, unit_cols)
        elif mode == "fill":
            cems_with_stable_bins = fill_isolated_null_bins(cems_with_stable_bins, unit_cols)
        return original(output, cems_with_stable_bins, unit_cols, up_or_down)

    module.calculate_min_up_or_down_times = calculate_min_up_or_down_times
    return original


def unpatch(module, original):
    module.calculate_min_up_or_down_times = original
