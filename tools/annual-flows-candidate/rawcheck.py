"""rawcheck: is PUDL's archived copy of an EIA-860M workbook the file EIA serves today?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Job xlsxprobe-v3 found that for report 2026-08 the planned operating month in EIA's workbook
and in PUDL's records differs for 7 of 2,309 planned generators, and the August watchlist
edition built from the workbook lists generators that PUDL's edition does not. This probe asks
where such a disagreement starts. It finds the copies of eia860m-YYYY.zip in PUDL's raw EIA-860M
archive on Zenodo (record 22995197 and its other versions) first published on or after a given
date, downloads at most three of them (each checked against Zenodo's md5), takes the month's
workbook out of each and compares it with the workbook EIA serves today, as downloaded by
workbook.py: first by md5, then, when they differ, generator by generator (status, planned
month, capacity) with workbook.py's reader. The generators workbook.py's self-check listed as
differences are shown one by one in every source.

Descriptive only: no prediction is tested. Honest User-Agent; Zenodo metadata calls go through
zenodoprobe's Prober (at most one every 1.5 seconds).

    python rawcheck.py --out-dir /out --month 2026-08 --month 2026-07 \
        --workbook-json /out/workbook.json
"""

import argparse
import hashlib
import io
import json
import os
import re
import time
import urllib.request
import zipfile

import pandas as pd

import eia860m_slip as es
import workbook as wk
import xlsxprobe as xp
import zenodoprobe as zp

__version__ = "0.1.0"
SEED = "22995197"     # PUDL Raw EIA Form 860M, version 50.0.0, published 27 September 2026
SINCE = "2026-09-24"  # EIA released the August 2026 workbook on 24 September 2026
MAX_COPIES = 3
SAMPLE = 30
MW_TOL = 0.05
FIELDS = ("status", "planned_m", "capacity_mw")
UA = "mv2-munim-rawcheck/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__


def zip_key(month):
    """PUDL's archive file for report month YYYY-MM."""
    return "eia860m-%s.zip" % month[:4]


def pick_copies(history, key, since, limit=MAX_COPIES):
    """The copies of file key (zenodoprobe.history entries, oldest first) first published on or
    after since, the newest limit of them, oldest first; the newest copy alone when none is
    that recent; [] when the key has no copies."""
    seen = history.get(key) or []
    recent = [h for h in seen if (h.get("first_date") or "") >= since]
    if not recent:
        return seen[-1:]
    return recent[-limit:]


def member_for(names, month):
    """(member, all hits): the zip member holding report month YYYY-MM's workbook. A hit is a
    spreadsheet whose name has the month's English name and the year (august_generator2026.xlsx)
    or the year and month number (2026-08, 2026_08, 202608); the shortest name wins."""
    year, mm = month.split("-")
    word = xp.MONTHS[int(mm) - 1]
    pat = re.compile(r"%s[-_]?%s(?!\d)" % (year, mm))
    hits = []
    for n in names:
        base = n.rsplit("/", 1)[-1].lower()
        if not base.endswith((".xlsx", ".xls")):
            continue
        if (word in base and year in base) or pat.search(base):
            hits.append(n)
    hits.sort(key=lambda n: (len(n), n))
    return (hits[0] if hits else None), hits


def md5(data):
    return hashlib.md5(data).hexdigest()


def checksum_ok(data, checksum):
    """Does data match Zenodo's 'md5:...' checksum? None when there is no md5 checksum."""
    if not checksum or not str(checksum).startswith("md5:"):
        return None
    return md5(data) == str(checksum)[4:]


def file_urls(record_id, key):
    return ["https://zenodo.org/api/records/%s/files/%s/content" % (record_id, key),
            "https://zenodo.org/records/%s/files/%s?download=1" % (record_id, key)]


def download(url, timeout=900):
    """(bytes, None) or (None, error). Never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), None
    except Exception as e:  # recorded, not raised
        return None, "%s: %s" % (type(e).__name__, e)


def frame(data):
    """A workbook's bytes -> (workbook.py's generator records indexed by key, None), or (None,
    error) when the bytes cannot be read."""
    try:
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None, dtype=object)
    except Exception as e:  # recorded, not raised
        return None, "%s: %s" % (type(e).__name__, e)
    wb, _, _ = wk.workbook_frame(sheets)
    return wb.set_index("key"), None


def same_value(field, a, b):
    """Do two sources agree on one field? Capacity within MW_TOL; two missing values agree."""
    if field == "capacity_mw":
        return abs(float(a) - float(b)) <= MW_TOL
    a_na, b_na = a is None or a != a, b is None or b != b
    if a_na or b_na:
        return a_na and b_na
    return a == b


def diff(z, e):
    """Generator-by-generator differences between an archived workbook z and EIA's e (frames
    indexed by key)."""
    both = z.index.intersection(e.index)
    only_z, only_e = sorted(z.index.difference(e.index)), sorted(e.index.difference(z.index))
    res = {"archive_keys": int(len(z)), "eia_keys": int(len(e)), "both": int(len(both)),
           "archive_only_n": len(only_z), "eia_only_n": len(only_e),
           "archive_only": only_z[:SAMPLE], "eia_only": only_e[:SAMPLE], "fields": {}}
    for f in FIELDS:
        bad = sorted(k for k in both if not same_value(f, z.at[k, f], e.at[k, f]))
        res["fields"][f] = {"differ": len(bad),
                            "sample": [{"key": k, "archive": xp._plain(z.at[k, f]),
                                        "eia": xp._plain(e.at[k, f])} for k in bad[:SAMPLE]]}
    return res


def interest(path, month):
    """The keys workbook.py's self-check listed as differences for month, from its JSON."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, TypeError):
        return []
    for m in data.get("months", []):
        if m.get("report") == month and m.get("self_check"):
            return [d["key"] for d in m["self_check"].get("difference_sample", [])]
    return []


def show(frames, keys):
    """For each key, its sheet, status, planned month and MW in each named frame (None when
    the frame is missing or lacks the key)."""
    out = []
    for k in keys:
        row = {"key": k}
        for name, f in frames.items():
            if f is not None and k in f.index:
                row[name] = {"sheet": f.at[k, "sheet"], "status": f.at[k, "status"],
                             "planned": es.month_str(f.at[k, "planned_m"]),
                             "mw": xp._plain(f.at[k, "capacity_mw"])}
            else:
                row[name] = None
        out.append(row)
    return out


def load_copies(z, keys, since):
    """Download the picked copies of each zip key -> (descriptions, [(description, ZipFile)])."""
    infos, archives = [], []
    for key in keys:
        for h in pick_copies(z["history"], key, since):
            info = dict(h, key=key, tried=[])
            data = None
            for url in file_urls(h["first_id"], key):
                data, err = download(url)
                info["tried"].append({"url": url, "error": err})
                if data is not None:
                    break
            infos.append(info)
            if data is None:
                continue
            info.update(bytes=len(data), md5=md5(data), checksum_ok=checksum_ok(data, h.get("checksum")))
            try:
                zf = zipfile.ZipFile(io.BytesIO(data))
            except zipfile.BadZipFile as e:
                info["error"] = "not a zip: %s" % e
                continue
            info["members"] = sorted(zf.namelist())
            archives.append((info, zf))
    return infos, archives


def check_month(month, eia_data, archives, keys):
    """One report month: EIA's file against each archived copy's member for that month."""
    entry = {"month": month, "eia_bytes": len(eia_data) if eia_data else None,
             "eia_md5": md5(eia_data) if eia_data else None, "copies": [], "keys": []}
    e_frame, err = frame(eia_data) if eia_data else (None, "EIA workbook not downloaded")
    entry["eia_error"] = err
    frames = {"eia": e_frame}
    for info, zf in archives:
        if info["key"] != zip_key(month):
            continue
        member, hits = member_for(zf.namelist(), month)
        c = {"first_id": info["first_id"], "first_date": info.get("first_date"),
             "first_version": info.get("first_version"), "member": member, "hits": hits}
        entry["copies"].append(c)
        if member is None:
            continue
        data = zf.read(member)
        c.update(bytes=len(data), md5=md5(data), same_file=bool(eia_data) and md5(data) == entry["eia_md5"])
        if c["same_file"]:
            continue
        z_frame, zerr = frame(data)
        c["error"] = zerr
        frames["archive_%s" % info["first_id"]] = z_frame
        if z_frame is not None and e_frame is not None:
            c["diff"] = diff(z_frame, e_frame)
    entry["keys"] = show(frames, keys)
    return entry


def render(result):
    md = ["# PUDL's archived EIA-860M workbooks against EIA's (rawcheck %s)" % __version__, "",
          "Descriptive probe, no prediction tested. MV2 of Munim, Inc. (made with AI agents).", "",
          "Zenodo: %s; %d versions found; copies on or after %s:" % (
              result["versions_url"], result["zenodo_versions"], result["since"]), "",
          "| record | first published | version | bytes | md5 matches Zenodo | error |",
          "|---|---|---|---|---|---|"]
    for c in result["copies"]:
        errs = "; ".join(t["error"] for t in c.get("tried", []) if t["error"])
        md.append("| %s | %s | %s | %s | %s | %s |" % (
            c["first_id"], c.get("first_date"), c.get("first_version"), c.get("bytes"),
            c.get("checksum_ok"), c.get("error") or errs))
    for m in result["months"]:
        md += ["", "## %s" % m["month"], "",
               "EIA's file today: %s bytes, md5 %s%s." % (
                   m["eia_bytes"], m["eia_md5"],
                   " (%s)" % m["eia_error"] if m["eia_error"] else ""), ""]
        for c in m["copies"]:
            line = "- Copy %s (%s): member %s" % (c["first_id"], c["first_date"], c["member"])
            if c["member"] is not None:
                line += ", md5 %s, same file as EIA's: %s" % (c["md5"], c["same_file"])
            md.append(line)
            d = c.get("diff")
            if d:
                md.append("  - keys: archive %d, EIA %d, both %d, archive only %d, EIA only %d; "
                          "differ: %s" % (d["archive_keys"], d["eia_keys"], d["both"],
                                          d["archive_only_n"], d["eia_only_n"],
                                          ", ".join("%s %d" % (f, d["fields"][f]["differ"])
                                                    for f in FIELDS)))
        if m["keys"]:
            names = [k for k in m["keys"][0] if k != "key"]
            md += ["", "| key | " + " | ".join(names) + " |",
                   "|---|" + "---|" * len(names)]
            for row in m["keys"]:
                cells = []
                for n in names:
                    v = row[n]
                    cells.append("" if v is None else "%s: %s, %s, %s MW" % (
                        v["sheet"], v["status"], v["planned"], v["mw"]))
                md.append("| %s | %s |" % (row["key"], " | ".join(cells)))
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--month", action="append", default=None, help="YYYY-MM (repeatable)")
    ap.add_argument("--workbook-dir", default=".", help="where workbook.py saved workbook_*.xlsx")
    ap.add_argument("--workbook-json", default=None, help="workbook.py's workbook.json")
    ap.add_argument("--seed", default=SEED)
    ap.add_argument("--since", default=SINCE)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    months = args.month or ["2026-08"]
    eia = {}
    for m in months:
        path = os.path.join(args.workbook_dir, "workbook_%s.xlsx" % m)
        if not os.path.exists(path):
            xp.fetch(xp.workbook_urls(m), path)
        eia[m] = open(path, "rb").read() if os.path.exists(path) else None
    p = zp.Prober()
    z = zp.probe_zenodo(p, args.seed)
    keys = sorted({zip_key(m) for m in months})
    infos, archives = load_copies(z, keys, args.since)
    result = {"meta": {"version": __version__, "seed": args.seed, "user_agent": UA,
                       "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
              "versions_url": z["versions_url"], "zenodo_versions": len(z["versions"]),
              "since": args.since, "history": {k: z["history"].get(k, []) for k in keys},
              "copies": infos, "calls": p.calls, "months": []}
    for m in months:
        want = interest(args.workbook_json, m) if args.workbook_json else []
        result["months"].append(check_month(m, eia[m], archives, want))
    with open(os.path.join(args.out_dir, "rawcheck.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    md = render(result)
    with open(os.path.join(args.out_dir, "rawcheck.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    return result


if __name__ == "__main__":
    main()
