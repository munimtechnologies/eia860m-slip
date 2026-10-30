"""Plain-Python reference rules for minimum up and down times, with and without filling
isolated null bins, used to check fill_isolated.py and PUDL's calculate_min_up_or_down_times
on random frames.

A row is (unit, hour, bin, min_stable_bin); bin and min_stable_bin are (left, right) tuples
or None. Within a unit, rows are taken in hour order.
  down hour: bin is None
  up hour:   bin and min_stable_bin are set, bin.left >= ms.left and bin.right >= ms.right
  run:       hours of one kind, each exactly one hour after the one before
  min time:  the shortest run's length, or None if the unit has no run of that kind
fill=True first gives a None bin the previous hour's bin when the same unit has a non-None
bin exactly one hour before and one hour after it.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

from datetime import timedelta

HOUR = timedelta(hours=1)


def fill_bins(hours, bins):
    out = list(bins)
    for i in range(1, len(bins) - 1):
        if (bins[i] is None and bins[i - 1] is not None and bins[i + 1] is not None
                and hours[i] - hours[i - 1] == HOUR and hours[i + 1] - hours[i] == HOUR):
            out[i] = bins[i - 1]
    return out


def shortest_run(hours, flags):
    best, run = None, 0
    for i, flag in enumerate(flags):
        if flag:
            run = run + 1 if (i > 0 and flags[i - 1] and hours[i] - hours[i - 1] == HOUR) else 1
        if run and (not flag or i == len(flags) - 1 or not flags[i + 1]
                    or hours[i + 1] - hours[i] != HOUR):
            best = run if best is None else min(best, run)
            run = 0
    return best


def min_up_down(rows, fill):
    """{unit: (min_up, min_down)} for rows of (unit, hour, bin, min_stable_bin)."""
    by_unit = {}
    for unit, hour, b, ms in rows:
        by_unit.setdefault(unit, []).append((hour, b, ms))
    result = {}
    for unit, items in by_unit.items():
        items.sort(key=lambda x: x[0])
        hours = [x[0] for x in items]
        bins = [x[1] for x in items]
        if fill:
            bins = fill_bins(hours, bins)
        up = [b is not None and ms is not None and b[0] >= ms[0] and b[1] >= ms[1]
              for b, (_, _, ms) in zip(bins, items)]
        down = [b is None for b in bins]
        result[unit] = (shortest_run(hours, up), shortest_run(hours, down))
    return result
