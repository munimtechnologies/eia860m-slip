"""eia860m-slip: do generators planned in EIA-860M come online (or retire) when planned?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Every month, Form EIA-860M lists each planned U.S. generator (1 MW and up)
with its development stage and current planned operating month. This tool
scores those planned months as forecasts. For every monthly report, every
generator listed as planned with a planned month 0-12 months ahead becomes
one "cohort row", and its outcome is read from later reports: on time (online
by the planned month), 1-3, 4-6 or 7-12 months late, or not online within 12
months of the planned month. Shares are capacity-weighted. It also compares,
for each calendar year, the capacity planned for that year in January with
what came online.

Since 0.2.0 it scores planned retirement months the same way: every operating
generator with a planned retirement month 0-12 months ahead, against the month
it retired (its retirement date in a record that lists it as retired, else the
first report that lists it as retired, else the last report that listed it as
operating before it left EIA-860M).

Since 0.3.0 it reads PUDL's validity dates as PUDL defines them (a generator's
last record runs to the last report that lists it, inclusive), so generators
still listed are no longer counted as having left, and it splits each year's
January plan into what came online that year and what happened to the rest,
and each year's additions into what January planned and where the rest stood
in January (annual flows; checks and predictions in
docs/annual-flows-preregistration.md).

Since 0.3.1 the annual flows link a planned generator that left EIA-860M to a
new entry of the same year that is the same equipment filed under another plant
id (rule R: same technology group and generator id, capacity within 0.05 MW,
first listed 0-3 months after the old key's last listing, at least 10 MW).
Linked pairs get the fate rekeyed_online and the source rekeyed, and are listed
with their raw records (docs/annual-flows-preregistration-v2.md).

Input: Catalyst Cooperative's PUDL table core_eia860m__changelog_generators
(one record per change, valid from report_date up to valid_until_date).

    python eia860m_slip.py --data-dir /data --out-dir /out
"""

import argparse
import glob
import json
import os
import urllib.request

import numpy as np
import pandas as pd

__version__ = "0.3.1"

URL = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/"
       "core_eia860m__changelog_generators.parquet")
COLUMNS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
           "current_planned_generator_operating_date", "generator_operating_date",
           "operational_status_code", "operational_status", "technology_description",
           "fuel_type_code_pudl", "state", "planned_generator_retirement_date",
           "generator_retirement_date", "plant_name_eia")
# EIA-860M planned status codes and the stage each stands for.
PLANNED = {"P": "planning", "L": "permitting", "T": "approved", "U": "construction",
           "V": "construction", "TS": "testing", "OT": "other"}
# Coarser stages for the annual flows: not yet approved, approved, being built or tested.
STAGE_BANDS = {"P": "early", "L": "early", "T": "approved", "U": "building", "V": "building",
               "TS": "building", "OT": "other"}
OPERATING = frozenset({"OP", "SB", "OS", "OA"})
RETIRED = frozenset({"RE"})
HORIZON = 12  # a plan is scored when its planned month is 0-12 months ahead
RESOLVE = 12  # months after the planned month an outcome is waited for
LAG = 2       # months of reporting lag allowed at the end of the data
OUTCOMES = ("on_time", "late_1_3", "late_4_6", "late_7_12", "not_online_12")
LEAD_BUCKETS = ((0, 2), (3, 5), (6, 8), (9, 12))
TECH_GROUPS = (("solar photovoltaic", "solar"), ("batteries", "battery"),
               ("onshore wind turbine", "wind_onshore"),
               ("offshore wind turbine", "wind_offshore"),
               ("natural gas fired combined cycle", "gas_cc"),
               ("natural gas fired combustion turbine", "gas_ct"),
               ("natural gas internal combustion engine", "gas_ice"),
               ("conventional steam coal", "coal"), ("nuclear", "nuclear"),
               ("petroleum liquids", "oil"))
# What became of a generator in January's plan for a year, read from its own operating
# month and from the report LAG months after December.
PLAN_FATES = ("online_in_year", "online_before_year", "online_next_months", "slipped",
              "stale", "other_status", "not_listed", "rekeyed_online")
# Where a generator that came online in a year, but was not in January's plan for it,
# stood in the January report.
JOIN_SOURCES = ("new_entry", "rekeyed", "pulled_forward", "carried_over", "listed_not_planned")
# Rule R: a not_listed plan generator and a new entry are the same equipment under a new key.
REKEY_MIN_MW = 10.0  # plan side, January capacity
REKEY_MW_TOL = 0.05  # largest capacity difference
REKEY_GAP = 3        # months from the old key's last listing to the new key's first report
LINK_COLS = ("year", "plan_key", "plan_plant", "entry_key", "entry_plant", "group",
             "plan_mw", "entry_mw", "last_listed", "first_listed", "months_apart")
RECORD_COLS = ("report_date", "valid_until_date", "plant_id_eia", "generator_id", "capacity_mw",
               "current_planned_generator_operating_date", "generator_operating_date",
               "operational_status_code", "technology_description", "plant_name_eia")
MAX_RECORDS = 400


def months(values):
    """Months since year 0 (year * 12 + month - 1) as floats, NaN where missing."""
    d = pd.to_datetime(pd.Series(values), errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype(float).to_numpy()


def month_str(m):
    if m is None or m != m:
        return None
    m = int(m)
    return "%04d-%02d" % (m // 12, m % 12 + 1)


def tech_group(desc):
    if not isinstance(desc, str):
        return "other"
    text = desc.strip().lower()
    for name, group in TECH_GROUPS:
        if text == name:
            return group
    return "gas_other" if "natural gas" in text else "other"


def outcome(slip):
    if slip is None or slip != slip or slip > 12:
        return "not_online_12"
    if slip <= 0:
        return "on_time"
    if slip <= 3:
        return "late_1_3"
    if slip <= 6:
        return "late_4_6"
    return "late_7_12"


def lead_bucket(lead):
    for a, b in LEAD_BUCKETS:
        if a <= lead <= b:
            return "%02d-%02d" % (a, b)
    return None


def prepare(df):
    """Add month columns, a generator key, the status code and the technology group."""
    df = df.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["key"] = df["plant_id_eia"].astype(str) + "/" + df["generator_id"].astype(str)
    df["report_m"] = months(df["report_date"])
    df["valid_m"] = months(df["valid_until_date"])
    df["planned_m"] = months(df["current_planned_generator_operating_date"])
    df["op_date_m"] = months(df["generator_operating_date"])
    df["planned_ret_m"] = months(df["planned_generator_retirement_date"])
    df["ret_date_m"] = months(df["generator_retirement_date"])
    df["status"] = df["operational_status_code"].astype(str).str.strip().str.upper()
    df["status_text"] = df["operational_status"].astype(str).str.strip().str.lower()
    df["group"] = [tech_group(x) for x in df["technology_description"]]
    df["capacity_mw"] = pd.to_numeric(df["capacity_mw"], errors="coerce").fillna(0.0)
    df = df[df["report_m"].notna()].reset_index(drop=True)
    df["until_m"] = listed_until(df)
    return df


def listed_until(df):
    """Last report month each record is in force.

    PUDL ends a record that another record follows at that record's report_date
    (exclusive), and a generator's last record at the last report that lists it
    (inclusive; report_date + 1 month if the record starts in that report, which
    makes such a record read one month long). A blank end runs to the last report.
    """
    last_m = df["report_m"].max()
    is_last = df["report_m"] == df.groupby("key")["report_m"].transform("max")
    until = df["valid_m"].where(is_last, df["valid_m"] - 1)
    return until.fillna(last_m).clip(upper=last_m)


def snapshot(df, r):
    """Records in force at report month r: each generator's latest record reported by r,
    if it is still in force at r."""
    s = df[df["report_m"] <= r].sort_values("report_m", kind="mergesort").groupby("key").tail(1)
    return s[s["until_m"] >= r]


def online_months(df):
    """Month each generator first operated.

    Its earliest operating date in a record that lists it as operating, else
    the first report month that lists it as operating.
    """
    op = df[df["status"].isin(OPERATING)]
    if op.empty:
        return pd.Series(dtype=float)
    first_report = op.groupby("key")["report_m"].min()
    op_date = op.groupby("key")["op_date_m"].min()
    return op_date.fillna(first_report)


def is_retired(df):
    return df["status"].isin(RETIRED) | df["status_text"].str.contains("retired", regex=False)


def _latest(df):
    return df.sort_values("report_m").groupby("key").tail(1).set_index("key")


def _operating_exits(df):
    """Generators whose last record lists them as operating and that then left EIA-860M.

    A generator still listed in the last report has a last record in force at that
    report, so only a last record that ends before it is an exit.
    """
    last = _latest(df)
    return last[(last["until_m"] < df["report_m"].max()) & last["status"].isin(OPERATING)]


def retired_months(df):
    """Month each generator retired.

    Its earliest retirement date in a record that lists it as retired, else the
    first report month that lists it as retired, else (for a generator that
    left EIA-860M while listed as operating) the last report month it was listed.
    """
    gone = df[is_retired(df)]
    if gone.empty:
        ret = pd.Series(dtype=float)
    else:
        first_report = gone.groupby("key")["report_m"].min()
        ret = gone.groupby("key")["ret_date_m"].min().fillna(first_report)
    exits = _operating_exits(df)["until_m"]
    return ret.combine_first(exits).astype(float)


def retire_detection(df):
    """How each retirement was found, so a reader can judge the exit rule."""
    gone = df[is_retired(df)]
    keys = set(gone["key"])
    dated = int(gone.groupby("key")["ret_date_m"].min().notna().sum()) if len(gone) else 0
    return {"generators_with_retired_record": len(keys),
            "retired_record_with_retirement_date": dated,
            "operating_exits_without_retired_record": len(set(_operating_exits(df).index) - keys)}


def cohorts(df, last_m=None, horizon=HORIZON, resolve=RESOLVE, lag=LAG):
    """One row per (generator, report month) with the generator planned 0-horizon months ahead.

    Only planned months whose outcome window has closed (planned month +
    resolve + lag <= last report month) are kept.
    """
    if last_m is None:
        last_m = df["report_m"].max()
    online = online_months(df)
    plan = df[df["status"].isin(PLANNED) & df["planned_m"].notna()]
    rows = []
    for rec in plan.itertuples(index=False):
        d = rec.planned_m
        if d + resolve + lag > last_m:
            continue
        lo = max(rec.report_m, d - horizon)
        hi = min(rec.until_m, d)
        for r in range(int(lo), int(hi) + 1):
            rows.append((rec.key, r, d, rec.status, rec.group, rec.technology_description,
                         rec.capacity_mw))
    c = pd.DataFrame(rows, columns=["key", "report_m", "planned_m", "status", "group",
                                    "technology", "mw"])
    c["lead"] = c["planned_m"] - c["report_m"]
    c["lead_bucket"] = [lead_bucket(x) for x in c["lead"]]
    c["stage"] = c["status"].map(PLANNED)
    c["report_year"] = (c["report_m"] // 12).astype(int)
    c["online_m"] = c["key"].map(online).astype(float)
    c["slip"] = c["online_m"] - c["planned_m"]
    c["outcome"] = [outcome(s) for s in c["slip"]]
    return c


def retire_cohorts(df, last_m=None, horizon=HORIZON, resolve=RESOLVE, lag=LAG):
    """One row per (generator, report month) with an operating generator's planned
    retirement 0-horizon months ahead. Outcome keys are shared with cohorts():
    on_time = retired by the planned month, not_online_12 = not retired 12 months after it."""
    if last_m is None:
        last_m = df["report_m"].max()
    retired = retired_months(df)
    plan = df[df["status"].isin(OPERATING) & df["planned_ret_m"].notna()]
    rows = []
    for rec in plan.itertuples(index=False):
        d = rec.planned_ret_m
        if d + resolve + lag > last_m:
            continue
        lo = max(rec.report_m, d - horizon)
        hi = min(rec.until_m, d)
        for r in range(int(lo), int(hi) + 1):
            rows.append((rec.key, r, d, rec.group, rec.technology_description, rec.capacity_mw))
    c = pd.DataFrame(rows, columns=["key", "report_m", "planned_m", "group", "technology", "mw"])
    c["lead"] = c["planned_m"] - c["report_m"]
    c["lead_bucket"] = [lead_bucket(x) for x in c["lead"]]
    c["report_year"] = (c["report_m"] // 12).astype(int)
    c["retired_m"] = c["key"].map(retired).astype(float)
    c["slip"] = c["retired_m"] - c["planned_m"]
    c["outcome"] = [outcome(s) for s in c["slip"]]
    return c


def summarize(c, by=None):
    """Capacity-weighted outcome shares, overall or per value of `by` (a column or list)."""
    out = []
    parts = [("all", c)] if by is None else list(c.groupby(by, sort=True))
    for name, g in parts:
        if isinstance(name, tuple):
            name = "/".join(str(x) for x in name)
        mw = float(g["mw"].sum())
        row = {"group": str(name), "rows": int(len(g)), "generators": int(g["key"].nunique()),
               "mw": round(mw, 1)}
        for o in OUTCOMES:
            row[o] = round(float(g.loc[g["outcome"] == o, "mw"].sum()) / mw, 4) if mw > 0 else None
        row["on_time_count_share"] = round(float((g["outcome"] == "on_time").mean()), 4)
        late = g.loc[g["slip"].notna() & (g["slip"] > 0), "slip"]
        row["median_months_late_if_late"] = float(late.median()) if len(late) else None
        out.append(row)
    return out


def _closed_years(df, last_m, lag):
    first_m = df["report_m"].min()
    for year in range(int(first_m // 12), int(last_m // 12) + 1):
        if year * 12 >= first_m and year * 12 + 11 + lag <= last_m:
            yield year


def annual(df, last_m=None, lag=LAG):
    """Per calendar year and technology group: MW planned for the year in January, how much of
    it came online that year, and all MW that came online that year."""
    if last_m is None:
        last_m = df["report_m"].max()
    online = online_months(df)
    latest = _latest(df)
    rows = []
    for year in _closed_years(df, last_m, lag):
        jan, dec = year * 12, year * 12 + 11
        snap = snapshot(df, jan)
        plan = snap[snap["status"].isin(PLANNED) & (snap["planned_m"] >= jan)
                    & (snap["planned_m"] <= dec)]
        on = plan["key"].map(online).astype(float)
        came = plan[(on >= jan) & (on <= dec)]
        built_keys = online[(online >= jan) & (online <= dec)].index
        built = latest.loc[latest.index.intersection(built_keys)]
        for grp in ["all"] + sorted(set(plan["group"]) | set(built["group"])):
            def pick(f):
                return f if grp == "all" else f[f["group"] == grp]
            p, cm, b = pick(plan), pick(came), pick(built)
            p_mw = float(p["capacity_mw"].sum())
            rows.append({"year": year, "group": grp, "planned_mw": round(p_mw, 1),
                         "planned_online_same_year_mw": round(float(cm["capacity_mw"].sum()), 1),
                         "planned_online_share": (round(float(cm["capacity_mw"].sum()) / p_mw, 4)
                                                  if p_mw > 0 else None),
                         "built_mw": round(float(b["capacity_mw"].sum()), 1)})
    return rows


def plan_fates(df, year, lag=LAG, online=None):
    """Each generator in January's plan for `year` (listed as planned, planned month in the
    year), with its January capacity, group and stage band, and its fate:

    online_in_year      came online in the year
    online_before_year  its operating month is before the year (the January plan was stale)
    online_next_months  operating in the report `lag` months after December
    slipped             still planned in that report, for a month after the year
    stale               still planned in that report, for a month in the year or undated
    other_status        listed in that report with any other status (cancelled, retired, ...)
    not_listed          no record in force in that report

    (rekeyed_online is set afterwards by rule R; see rekey_links.)
    """
    if online is None:
        online = online_months(df)
    jan, dec = year * 12, year * 12 + 11
    snap = snapshot(df, jan)
    plan = snap[snap["status"].isin(PLANNED) & (snap["planned_m"] >= jan)
                & (snap["planned_m"] <= dec)]
    end = snapshot(df, dec + lag).set_index("key")
    rows = []
    for rec in plan.itertuples(index=False):
        on = online.get(rec.key, np.nan)
        if jan <= on <= dec:
            fate = "online_in_year"
        elif on < jan:
            fate = "online_before_year"
        elif rec.key not in end.index:
            fate = "not_listed"
        else:
            e = end.loc[rec.key]
            if e["status"] in OPERATING:
                fate = "online_next_months"
            elif e["status"] in PLANNED:
                fate = "slipped" if e["planned_m"] > dec else "stale"
            else:
                fate = "other_status"
        rows.append((year, rec.key, rec.group, STAGE_BANDS[rec.status], rec.capacity_mw, fate))
    return pd.DataFrame(rows, columns=["year", "key", "group", "band", "mw", "fate"])


def built_sources(df, year, online=None, latest=None):
    """Each generator that came online in `year`, with its latest capacity and group, and where
    it stood in the January report: in_plan (planned for a month in the year), or

    new_entry           not listed in January
    pulled_forward      planned in January for a month after the year
    carried_over        planned in January for a month before the year, or undated
    listed_not_planned  listed in January with a status that is not planned (mostly operating)

    (rekeyed is set afterwards by rule R; see rekey_links.)
    """
    if online is None:
        online = online_months(df)
    if latest is None:
        latest = _latest(df)
    jan, dec = year * 12, year * 12 + 11
    snap = snapshot(df, jan).set_index("key")
    rows = []
    for k in online[(online >= jan) & (online <= dec)].index:
        if k not in snap.index:
            src = "new_entry"
        else:
            j = snap.loc[k]
            if j["status"] not in PLANNED:
                src = "listed_not_planned"
            elif jan <= j["planned_m"] <= dec:
                src = "in_plan"
            elif j["planned_m"] > dec:
                src = "pulled_forward"
            else:
                src = "carried_over"
        rows.append((year, k, latest.loc[k, "group"], float(latest.loc[k, "capacity_mw"]), src))
    return pd.DataFrame(rows, columns=["year", "key", "group", "mw", "source"])


def _gen_id(v):
    return str(v).strip().casefold()


def _name(v):
    return v if isinstance(v, str) else ""


def listing(df):
    """Per generator: generator id (trimmed, any case), first report month, last listed month
    (0.3.0's reading) and the plant name in its last record that has one."""
    s = df.sort_values(["key", "report_m"], kind="mergesort")
    g = s.groupby("key")
    return pd.DataFrame({"gen": g["generator_id"].last().map(_gen_id),
                         "first_m": g["report_m"].min(), "last_m": g["until_m"].max(),
                         "name": g["plant_name_eia"].last().map(_name)})


def rekey_links(fates, built, info):
    """Rule R (docs/annual-flows-preregistration-v2.md) for one year's fates and sources.

    A plan generator g (fate not_listed, January capacity at least REKEY_MIN_MW) and an entry
    n (source new_entry) are linked when they have the same technology group and generator
    id, capacities within REKEY_MW_TOL, and n's first report is 0-REKEY_GAP months after g's
    last listed month. One to one: plan generators in order of January capacity (largest
    first, then key), each taking the free entry with the smallest capacity difference, then
    the smallest gap, then the lowest key. Returns one dict per link, in that order.
    """
    gen, first, last, name = (info[c].to_dict() for c in ("gen", "first_m", "last_m", "name"))
    gone = fates[(fates["fate"] == "not_listed") & (fates["mw"] >= REKEY_MIN_MW)]
    new = list(built[built["source"] == "new_entry"].itertuples(index=False))
    used, links = set(), []
    for g in sorted(gone.itertuples(index=False), key=lambda r: (-float(r.mw), r.key)):
        best = None
        for n in new:
            if n.key in used or n.group != g.group or gen[n.key] != gen[g.key]:
                continue
            gap = first[n.key] - last[g.key]
            d = abs(float(n.mw) - float(g.mw))
            if 0 <= gap <= REKEY_GAP and d <= REKEY_MW_TOL:
                if best is None or (d, gap, n.key) < best[:3]:
                    best = (d, gap, n.key, n)
        if best is None:
            continue
        d, gap, _, n = best
        used.add(n.key)
        links.append({"year": int(g.year), "plan_key": g.key, "plan_plant": name[g.key],
                      "entry_key": n.key, "entry_plant": name[n.key], "group": g.group,
                      "plan_mw": round(float(g.mw), 1), "entry_mw": round(float(n.mw), 1),
                      "last_listed": month_str(last[g.key]),
                      "first_listed": month_str(first[n.key]), "months_apart": int(gap)})
    return links


def _text(v):
    """A record value as text: blank when missing, dates without a midnight time."""
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return ""
    v = str(v)
    return "" if v in ("nan", "NaT", "None", "<NA>") else v.replace(" 00:00:00", "")


def link_records(df, links):
    """Raw records (as text) of every linked generator, both keys, by generator and report."""
    keys = sorted({x[k] for x in links for k in ("plan_key", "entry_key")})
    sel = df[df["key"].isin(keys)].sort_values(["key", "report_m"], kind="mergesort")
    cols = [c for c in RECORD_COLS if c in sel.columns]
    return [{c: _text(v) for c, v in rec.items()}
            for rec in sel[cols].head(MAX_RECORDS).to_dict("records")]


def _flow_row(label, fates, built):
    planned = float(fates["mw"].sum())
    row = dict(label)
    row["planned_mw"] = round(planned, 1)
    for f in PLAN_FATES:
        row[f] = round(float(fates.loc[fates["fate"] == f, "mw"].sum()), 1)
    delivered = float(fates.loc[fates["fate"].isin(["online_in_year", "rekeyed_online"]),
                                "mw"].sum())
    row["delivered_share"] = round(delivered / planned, 4) if planned > 0 else None
    parts = sum(float(fates.loc[fates["fate"] == f, "mw"].sum()) for f in PLAN_FATES)
    row["plan_identity_ok"] = abs(parts - planned) < 0.05
    if built is not None:
        b_mw = float(built["mw"].sum())
        row["built_mw"] = round(b_mw, 1)
        row["in_plan_mw"] = round(float(built.loc[built["source"] == "in_plan", "mw"].sum()), 1)
        for s in JOIN_SOURCES:
            row[s] = round(float(built.loc[built["source"] == s, "mw"].sum()), 1)
        joined = b_mw - float(built.loc[built["source"] == "in_plan", "mw"].sum())
        row["joined_share"] = round(joined / b_mw, 4) if b_mw > 0 else None
        parts = sum(float(built.loc[built["source"] == s, "mw"].sum())
                    for s in ("in_plan",) + JOIN_SOURCES)
        row["built_identity_ok"] = abs(parts - b_mw) < 0.05
    return row


def annual_flows(df, last_m=None, lag=LAG):
    """For each closed year: January's plan split by fate, and the year's additions split by
    where they stood in January, with rule R's links; by technology group, by stage band, and
    pooled over years.

    Returns (result dict, generator-level DataFrame)."""
    if last_m is None:
        last_m = df["report_m"].max()
    online = online_months(df)
    latest = _latest(df)
    info = listing(df)
    fates, built, links = [], [], []
    for year in _closed_years(df, last_m, lag):
        f = plan_fates(df, year, lag, online)
        b = built_sources(df, year, online, latest)
        found = rekey_links(f, b, info)
        f.loc[f["key"].isin([x["plan_key"] for x in found]), "fate"] = "rekeyed_online"
        b.loc[b["key"].isin([x["entry_key"] for x in found]), "source"] = "rekeyed"
        fates.append(f)
        built.append(b)
        links += found
    fates = pd.concat(fates, ignore_index=True) if fates else plan_fates(df, 0, lag, online)
    built = pd.concat(built, ignore_index=True) if built else built_sources(df, 0, online, latest)
    by_group, by_band, pooled = [], [], []
    for year in sorted(set(fates["year"]) | set(built["year"])):
        f, b = fates[fates["year"] == year], built[built["year"] == year]
        for grp in ["all"] + sorted(set(f["group"]) | set(b["group"])):
            fg = f if grp == "all" else f[f["group"] == grp]
            bg = b if grp == "all" else b[b["group"] == grp]
            by_group.append(_flow_row({"year": int(year), "group": grp}, fg, bg))
        for band in sorted(set(f["band"])):
            by_band.append(_flow_row({"year": int(year), "band": band}, f[f["band"] == band], None))
    # Pool only years whose January plan has capacity (PUDL's EIA-860M capacities start in
    # 2016), so both sides of a pooled row cover the same years.
    pooled_years = sorted(int(y) for y in set(fates.loc[fates["mw"] > 0, "year"]))
    pf = fates[fates["year"].isin(pooled_years)]
    pb = built[built["year"].isin(pooled_years)]
    big = [g for g, _ in pf.groupby("group")["mw"].sum().sort_values(ascending=False).items()]
    for grp in ["all"] + big[:5]:
        fg = pf if grp == "all" else pf[pf["group"] == grp]
        bg = pb if grp == "all" else pb[pb["group"] == grp]
        pooled.append(_flow_row({"group": grp, "band": "all"}, fg, bg))
        for band in sorted(set(fg["band"])):
            pooled.append(_flow_row({"group": grp, "band": band}, fg[fg["band"] == band], None))
    gens = pd.concat([fates.assign(kind="plan").rename(columns={"fate": "state"}),
                      built.assign(kind="built", band=None).rename(columns={"source": "state"})],
                     ignore_index=True)[["kind", "year", "key", "group", "band", "mw", "state"]]
    years = sorted(int(y) for y in set(fates["year"]))
    links_by_year = [{"year": y, "links": sum(1 for x in links if x["year"] == y),
                      "plan_mw": round(sum((x["plan_mw"] for x in links if x["year"] == y), 0.0), 1),
                      "entry_mw": round(sum((x["entry_mw"] for x in links if x["year"] == y), 0.0),
                                        1)}
                     for y in years]
    return {"years": years, "pooled_years": pooled_years, "check_month_lag": lag,
            "plan_fates": list(PLAN_FATES),
            "join_sources": list(JOIN_SOURCES),
            "rekey_rule": {"min_plan_mw": REKEY_MIN_MW, "mw_tolerance": REKEY_MW_TOL,
                           "max_gap_months": REKEY_GAP,
                           "same": ["technology group", "generator id (trimmed, any case)"]},
            "by_group": by_group, "by_band": by_band, "pooled": pooled,
            "links": links, "links_by_year": links_by_year}, gens


def retire_annual(df, last_m=None, lag=LAG):
    """Per calendar year and technology group: operating MW planned in January to retire that
    year, how much of it retired that year, and all MW that retired that year."""
    if last_m is None:
        last_m = df["report_m"].max()
    retired = retired_months(df)
    latest = _latest(df)
    rows = []
    for year in _closed_years(df, last_m, lag):
        jan, dec = year * 12, year * 12 + 11
        snap = snapshot(df, jan)
        plan = snap[snap["status"].isin(OPERATING) & (snap["planned_ret_m"] >= jan)
                    & (snap["planned_ret_m"] <= dec)]
        on = plan["key"].map(retired).astype(float)
        came = plan[(on >= jan) & (on <= dec)]
        gone_keys = retired[(retired >= jan) & (retired <= dec)].index
        gone = latest.loc[latest.index.intersection(gone_keys)]
        for grp in ["all"] + sorted(set(plan["group"]) | set(gone["group"])):
            def pick(f):
                return f if grp == "all" else f[f["group"] == grp]
            p, cm, g = pick(plan), pick(came), pick(gone)
            p_mw = float(p["capacity_mw"].sum())
            rows.append({"year": year, "group": grp, "planned_mw": round(p_mw, 1),
                         "planned_retired_same_year_mw": round(float(cm["capacity_mw"].sum()), 1),
                         "planned_retired_share": (round(float(cm["capacity_mw"].sum()) / p_mw, 4)
                                                   if p_mw > 0 else None),
                         "retired_mw": round(float(g["capacity_mw"].sum()), 1)})
    return rows


def profile(raw_columns, df):
    last = df.sort_values("report_m").groupby("key").tail(1)
    last_m = df["report_m"].max()
    plan_rows = df["status"].isin(PLANNED)
    return {
        "rows": int(len(df)), "generators": int(df["key"].nunique()),
        "columns": list(raw_columns),
        "report_min": month_str(df["report_m"].min()), "report_max": month_str(last_m),
        "distinct_report_months": int(df["report_m"].nunique()),
        "status_counts": {str(k): int(v) for k, v in df["status"].value_counts().head(30).items()},
        "operational_status_counts": {str(k): int(v) for k, v in
                                      df["operational_status"].astype(str).value_counts().head(20).items()},
        "technology_counts": {str(k): int(v) for k, v in
                              df["technology_description"].astype(str).value_counts().head(40).items()},
        "valid_until_null_rows": int(df["valid_m"].isna().sum()),
        "last_record_valid_until_set": int(last["valid_m"].notna().sum()),
        "last_record_valid_until_null": int(last["valid_m"].isna().sum()),
        "last_record_in_force_at_report_max": int((last["until_m"] >= last_m).sum()),
        "last_record_one_month_long": int((last["valid_m"] == last["report_m"] + 1).sum()),
        "first_report_with_capacity": month_str(df.loc[df["capacity_mw"] > 0, "report_m"].min()),
        "planned_rows": int(plan_rows.sum()),
        "planned_rows_without_planned_date": int((plan_rows & df["planned_m"].isna()).sum()),
        "stale_planned_generators": int((last["status"].isin(PLANNED)
                                         & (last["planned_m"] + 24 < last_m)).sum()),
        "operating_rows_with_planned_retirement": int((df["status"].isin(OPERATING)
                                                       & df["planned_ret_m"].notna()).sum()),
        "retired_rows": int(is_retired(df).sum()),
    }


def find_parquet(data_dir):
    hits = sorted(glob.glob(os.path.join(data_dir, "**", "*changelog_generators*.parquet"),
                            recursive=True))
    hits = hits or sorted(glob.glob(os.path.join(data_dir, "**", "*.parquet"), recursive=True))
    if hits:
        return hits[0]
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "core_eia860m__changelog_generators.parquet")
    urllib.request.urlretrieve(URL, path)
    return path


def table(rows, cols, labels=None):
    lines = ["| " + " | ".join(labels or cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c)
            cells.append("" if v is None else ("%.3f" % v if isinstance(v, float) and abs(v) < 10
                                               else str(v)))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def retirements(df, prof, out_dir):
    """Score planned retirement months; writes retire.json, retire.md and retire_rows.csv.gz."""
    c = retire_cohorts(df)
    big = [g for g, _ in c.groupby("group")["mw"].sum().sort_values(ascending=False).items()]
    result = {
        "version": __version__, "source": prof["source"],
        "report_min": prof["report_min"], "report_max": prof["report_max"],
        "rules": {"horizon_months": HORIZON, "resolve_months": RESOLVE, "lag_months": LAG,
                  "operating_codes": sorted(OPERATING), "retired_codes": sorted(RETIRED),
                  "outcome_keys": "on_time = retired by the planned month; "
                                  "not_online_12 = not retired 12 months after it",
                  "exit_rule": "a generator that left EIA-860M while listed as operating, with "
                               "no retired record, counts as retired in its last listed month"},
        "detection": retire_detection(df),
        "overall": summarize(c),
        "by_group": summarize(c, "group"),
        "by_lead": summarize(c, "lead_bucket"),
        "by_report_year": summarize(c, "report_year"),
        "by_group_year": summarize(c[c["group"].isin(big[:4])], ["group", "report_year"]),
        "annual": retire_annual(df),
    }
    with open(os.path.join(out_dir, "retire.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    c.to_csv(os.path.join(out_dir, "retire_rows.csv.gz"), index=False, compression="gzip")

    cols = ["group", "rows", "generators", "mw"] + list(OUTCOMES) + [
        "on_time_count_share", "median_months_late_if_late"]
    labels = ["group", "rows", "generators", "mw", "retired_by_plan", "late_1_3", "late_4_6",
              "late_7_12", "not_retired_12", "by_plan_count_share", "median_months_late_if_late"]
    det = result["detection"]
    md = ["# EIA-860M planned retirement months scored as forecasts", "",
          "Data: PUDL core_eia860m__changelog_generators (%s), reports %s to %s. eia860m-slip %s, "
          "MV2 of Munim, Inc. (made with AI agents)." % (prof["source"], prof["report_min"],
                                                         prof["report_max"], __version__), "",
          "Each row is an operating generator with a planned retirement month 0-12 months ahead "
          "in a monthly report; shares are of capacity (MW). retired_by_plan = retired by the "
          "planned month; not_retired_12 = not retired 12 months after it.", "",
          "Retirements found: %d generators with a retired record (%d with a retirement date); "
          "%d more left EIA-860M while listed as operating and are counted as retired in their "
          "last listed month." % (det["generators_with_retired_record"],
                                  det["retired_record_with_retirement_date"],
                                  det["operating_exits_without_retired_record"]), ""]
    for title, key in (("Overall", "overall"), ("By technology group", "by_group"),
                       ("By months ahead", "by_lead"), ("By report year", "by_report_year"),
                       ("Largest groups by report year", "by_group_year")):
        md += ["## " + title, ""] + table(result[key], cols, labels) + [""]
    md += ["## Planned in January to retire that year vs retired that year", ""] + table(
        result["annual"], ["year", "group", "planned_mw", "planned_retired_same_year_mw",
                           "planned_retired_share", "retired_mw"]) + [""]
    with open(os.path.join(out_dir, "retire.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:30]))
    return result


def flows(df, prof, out_dir):
    """Annual flows; writes flows.json, flows.md and flows_generators.csv.gz."""
    result, gens = annual_flows(df)
    result.update({"version": __version__, "source": prof["source"],
                   "report_min": prof["report_min"], "report_max": prof["report_max"],
                   "link_records": link_records(df, result["links"])})
    with open(os.path.join(out_dir, "flows.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    gens.to_csv(os.path.join(out_dir, "flows_generators.csv.gz"), index=False, compression="gzip")
    plan_cols = ["planned_mw"] + list(PLAN_FATES) + ["delivered_share"]
    built_cols = ["built_mw", "in_plan_mw"] + list(JOIN_SOURCES) + ["joined_share"]
    md = ["# EIA-860M annual flows: January's plan and the year's additions", "",
          "Data: PUDL core_eia860m__changelog_generators (%s), reports %s to %s. eia860m-slip %s, "
          "MV2 of Munim, Inc. (made with AI agents)." % (prof["source"], prof["report_min"],
                                                         prof["report_max"], __version__), "",
          "Plan side: every generator the January report lists as planned for a month in the "
          "year, at its January capacity (MW), by what became of it (fates read from its "
          "operating month and from the report %d months after December). Built side: every "
          "generator that came online in the year, at its latest capacity, by where it stood in "
          "January. rekeyed_online / rekeyed: a plan generator that left EIA-860M and a new entry "
          "linked by rule R as the same equipment under another key (same group and generator "
          "id, capacity within %.2f MW, first listed 0-%d months later, at least %.0f MW); "
          "delivered_share counts rekeyed_online as delivered. Checks: "
          "docs/annual-flows-preregistration-v2.md." % (LAG, REKEY_MW_TOL, REKEY_GAP,
                                                        REKEY_MIN_MW), "",
          "## January's plan by fate, by technology group", ""]
    md += table(result["by_group"], ["year", "group"] + plan_cols) + [""]
    md += ["## The year's additions by where they stood in January, by technology group", ""]
    md += table(result["by_group"], ["year", "group"] + built_cols) + [""]
    md += ["## January's plan by fate, by stage band in January", ""]
    md += table(result["by_band"], ["year", "band"] + plan_cols) + [""]
    pooled_years = result["pooled_years"]
    md += ["## Pooled over %s-%s" % (pooled_years[0] if pooled_years else "",
                                     pooled_years[-1] if pooled_years else ""), ""]
    md += table(result["pooled"], ["group", "band"] + plan_cols) + [""]
    md += table([r for r in result["pooled"] if r["band"] == "all"], ["group"] + built_cols) + [""]
    ok = all(r["plan_identity_ok"] for r in result["by_group"] + result["by_band"]
             + result["pooled"]) and all(r.get("built_identity_ok", True)
                                         for r in result["by_group"] + result["pooled"])
    md += ["Every row's parts add up to its total: %s" % ok, ""]
    md += ["## Re-key links (rule R) per year", ""]
    md += table(result["links_by_year"], ["year", "links", "plan_mw", "entry_mw"]) + [""]
    md += ["## Every re-key link", "", "%d links." % len(result["links"]), ""]
    md += table(result["links"], list(LINK_COLS)) + [""]
    md += ["## Raw records of the linked generators", "",
           "%d records%s." % (len(result["link_records"]),
                              " (the first %d)" % MAX_RECORDS
                              if len(result["link_records"]) >= MAX_RECORDS else ""), ""]
    md += table(result["link_records"], list(RECORD_COLS)) + [""]
    with open(os.path.join(out_dir, "flows.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:12]))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    path = find_parquet(args.data_dir)
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    raw = pd.read_parquet(path, columns=[c for c in COLUMNS if c in names])
    raw.head(30).to_csv(os.path.join(args.out_dir, "raw_head.csv"), index=False)
    df = prepare(raw)
    prof = profile(names, df)
    prof.update({"source": os.path.basename(path), "bytes": os.path.getsize(path),
                 "version": __version__})
    with open(os.path.join(args.out_dir, "profile.json"), "w", encoding="utf-8") as fh:
        json.dump(prof, fh, indent=1)

    c = cohorts(df)
    big = [g for g, _ in c.groupby("group")["mw"].sum().sort_values(ascending=False).items()]
    result = {
        "version": __version__, "source": prof["source"],
        "report_min": prof["report_min"], "report_max": prof["report_max"],
        "rules": {"horizon_months": HORIZON, "resolve_months": RESOLVE, "lag_months": LAG,
                  "planned_codes": PLANNED, "operating_codes": sorted(OPERATING)},
        "overall": summarize(c),
        "by_group": summarize(c, "group"),
        "by_stage": summarize(c, "stage"),
        "by_lead": summarize(c, "lead_bucket"),
        "by_report_year": summarize(c, "report_year"),
        "by_group_stage": summarize(c[c["group"].isin(big[:5])], ["group", "stage"]),
        "by_group_year": summarize(c[c["group"].isin(big[:4])], ["group", "report_year"]),
        "annual": annual(df),
    }
    with open(os.path.join(args.out_dir, "slip.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    c.to_csv(os.path.join(args.out_dir, "cohort_rows.csv.gz"), index=False, compression="gzip")

    cols = ["group", "rows", "generators", "mw"] + list(OUTCOMES) + [
        "on_time_count_share", "median_months_late_if_late"]
    md = ["# EIA-860M planned operating months scored as forecasts", "",
          "Data: PUDL core_eia860m__changelog_generators (%s), reports %s to %s. eia860m-slip %s, "
          "MV2 of Munim, Inc. (made with AI agents)." % (prof["source"], prof["report_min"],
                                                         prof["report_max"], __version__), "",
          "Each row is a generator listed as planned in a monthly report with a planned month 0-12 "
          "months ahead; shares are of capacity (MW). on_time = online by the planned month; "
          "not_online_12 = not online 12 months after it.", ""]
    for title, key in (("Overall", "overall"), ("By technology group", "by_group"),
                       ("By development stage at the report", "by_stage"),
                       ("By months ahead", "by_lead"), ("By report year", "by_report_year"),
                       ("Largest groups by stage", "by_group_stage"),
                       ("Largest groups by report year", "by_group_year")):
        md += ["## " + title, ""] + table(result[key], cols) + [""]
    md += ["## Planned in January vs built that year", ""] + table(
        result["annual"], ["year", "group", "planned_mw", "planned_online_same_year_mw",
                           "planned_online_share", "built_mw"]) + [""]
    with open(os.path.join(args.out_dir, "slip.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:40]))

    if "planned_generator_retirement_date" in names:
        retirements(df, prof, args.out_dir)
    else:
        print("no planned_generator_retirement_date column; retirement scoring skipped")
    flows(df, prof, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
