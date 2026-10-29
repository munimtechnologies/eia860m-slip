"""A consecutive-only replacement for the drop_duplicates step in PUDL's make_changelog.

make_changelog (src/pudl/helpers.py) keeps the first record of every distinct set of
values in a series, so a value that changes and later comes back (A, B, A) is dropped
and B stays in force. keep_changes keeps a record when no record of its series on the
series' previous report date has the same values, so the returning A is kept.

Missing values compare equal, as they do in drop_duplicates. Several records may share
one series and report date (the tall forensics tables): a record is then kept when its
values were not among the previous date's records, and only once per date.

Apache-2.0. Made with AI agents working in MV2's name (MV2, Munim, Inc.).
"""

import pandas as pd

VERSION = "0.1.0"


def keep_changes(df: pd.DataFrame, series_cols: list[str]) -> pd.DataFrame:
    """Rows of ``df`` whose values differ from every row on the series' previous date.

    The values compared are all columns except ``report_date`` (the subset make_changelog
    passes to drop_duplicates). Row order and index are kept.
    """
    if df.empty:
        return df
    value_cols = [c for c in df.columns if c != "report_date"]
    # One id per distinct set of values and one per series, with missing values equal.
    vid = df.groupby(value_cols, dropna=False, sort=False, observed=True).ngroup()
    sid = df.groupby(series_cols, dropna=False, sort=False, observed=True).ngroup()
    key = pd.DataFrame(
        {
            "sid": sid.to_numpy(),
            "date": df["report_date"].to_numpy(),
            "vid": vid.to_numpy(),
        }
    )
    dates = key[["sid", "date"]].drop_duplicates().sort_values(["sid", "date"])
    dates["prev"] = dates.groupby("sid")["date"].shift()
    key = key.merge(dates, on=["sid", "date"], how="left")
    seen = key[["sid", "date", "vid"]].drop_duplicates()
    seen = seen.rename(columns={"date": "prev"}).assign(in_prev=True)
    key = key.merge(seen, on=["sid", "prev", "vid"], how="left")
    repeat = key["in_prev"].notna().to_numpy() & key["prev"].notna().to_numpy()
    repeat |= key.duplicated(["sid", "date", "vid"]).to_numpy()
    return df[~repeat]


# make_changelog's dedup step at PUDL af08a70 / 4d3366b, and what replaces it.
TARGET = """    df_changelog = df_all.sort_values(
        sort_cols, kind="stable", key=_sort_key
    ).drop_duplicates(
        subset=[c for c in df_all if c != "report_date"],
        keep="first",
    )
"""
REPLACEMENT = """    df_changelog = keep_changes(
        df_all.sort_values(sort_cols, kind="stable", key=_sort_key), series_cols
    )
"""


def patch_source(func_source: str) -> str:
    """make_changelog's source with its drop_duplicates step swapped for keep_changes."""
    n = func_source.count(TARGET)
    if n != 1:
        raise ValueError("drop_duplicates step found %d times, expected 1" % n)
    return func_source.replace(TARGET, REPLACEMENT)
