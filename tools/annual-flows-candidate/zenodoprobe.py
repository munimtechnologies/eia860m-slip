"""zenodoprobe: which dated copies of the annual EIA-860 exist from before each final release?

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

The twenty-sixth result (docs/entry-timing.md) could not separate R1 (lag) from R2 (revision)
because both fit an edge at the annual file's final release. A test that can separate them needs
a copy of the annual file dated before that release, such as EIA's early release. This probe only
finds out which copies exist. It reads metadata, never generator data:

    1. the versions of PUDL's raw EIA-860 archive on Zenodo (record 13682785 and its siblings),
       each with its publication date and the name, size and checksum of every file, and for
       each eia860-YYYY.zip the dates on which its checksum changed;
    2. HEAD requests (no bodies) for EIA's own early-release zip names, eia860YYYYER.zip, under
       EIA's current and archive folders.

Every call is recorded with its status. Honest User-Agent; at most one call every 1.5 seconds.

    python zenodoprobe.py --out-dir /out
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.request

__version__ = "0.1.0"
API = "https://zenodo.org/api/records/"
SEED = "13682785"  # PUDL Raw EIA Form 860, version 10.0.0, published 24 September 2024
UA = "mv2-munim-zenodoprobe/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
EIA = "https://www.eia.gov/electricity/data/eia860/"
ER_YEARS = tuple(range(2016, 2026))
PAGE_SIZE = 25
MAX_PAGES = 40
PAUSE = 1.5


def fetch(url, method="GET", timeout=60):
    """(status, content_type, content_length, body or None, error or None). Never raises."""
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read() if method == "GET" else None
            return (r.status, r.headers.get("Content-Type", ""),
                    r.headers.get("Content-Length"), body, None)
    except urllib.error.HTTPError as e:
        h = e.headers
        return (e.code, h.get("Content-Type", "") if h else "",
                h.get("Content-Length") if h else None, None, "HTTP %d" % e.code)
    except Exception as e:  # network errors are recorded, not raised
        return None, "", None, None, "%s: %s" % (type(e).__name__, e)


def as_json(body):
    if body is None:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def page_url(url, page):
    return "%s%ssize=%d&page=%d" % (url, "&" if "?" in url else "?", PAGE_SIZE, page)


def version_rows(page):
    """Rows (id, version, publication_date, created) from one page of a Zenodo versions list."""
    hits = ((page or {}).get("hits") or {}).get("hits") or []
    out = []
    for h in hits:
        m = h.get("metadata") or {}
        out.append({"id": str(h.get("id", "")), "version": m.get("version"),
                    "publication_date": m.get("publication_date"), "created": h.get("created")})
    return out


def file_rows(rec):
    """Rows (key, size, checksum), sorted by key, from a record's JSON ('files' as a list, or as
    {'entries': ...}) or from a record's /files listing ({'entries': [...]})."""
    rec = rec or {}
    f = rec.get("files") if "files" in rec else rec.get("entries")
    if isinstance(f, dict) and "entries" in f:
        f = f["entries"]
    if isinstance(f, dict):
        f = list(f.values())
    if not isinstance(f, list):
        f = []
    out = [{"key": x["key"], "size": x.get("size"), "checksum": x.get("checksum")}
           for x in f if isinstance(x, dict) and x.get("key")]
    return sorted(out, key=lambda r: r["key"])


def history(versions):
    """For each file key, the checksums in date order, a new entry each time the checksum changes,
    each with the first version that has it."""
    order = sorted(versions, key=lambda v: (v.get("publication_date") or "",
                                            v.get("created") or "", v["id"]))
    out = {}
    for v in order:
        for f in v.get("files") or []:
            seen = out.setdefault(f["key"], [])
            if not seen or seen[-1]["checksum"] != f["checksum"]:
                seen.append({"checksum": f["checksum"], "size": f["size"], "first_id": v["id"],
                             "first_version": v.get("version"),
                             "first_date": v.get("publication_date")})
    return out


def er_urls(year):
    name = "eia860%dER.zip" % year
    return [EIA + "xls/" + name, EIA + "archive/xls/" + name]


class Prober:
    def __init__(self, pause=PAUSE):
        self.calls, self.pause, self._last = [], pause, 0.0

    def get(self, url, method="GET"):
        wait = self._last + self.pause - time.time()
        if wait > 0:
            time.sleep(wait)
        status, ctype, length, body, err = fetch(url, method)
        self._last = time.time()
        self.calls.append({"url": url, "method": method, "status": status,
                           "content_type": ctype, "content_length": length, "error": err})
        return status, ctype, length, body, err


def probe_zenodo(p, seed=SEED):
    status, _, _, body, _ = p.get(API + seed)
    rec = as_json(body) or {}
    versions_url = ((rec.get("links") or {}).get("versions") or API + seed + "/versions")
    rows = []
    for page in range(1, MAX_PAGES + 1):
        got = version_rows(as_json(p.get(page_url(versions_url, page))[3]))
        if not got and page == 1:
            # The listing without paging parameters, in case the server refuses them.
            got = version_rows(as_json(p.get(versions_url)[3]))
            rows += got
            break
        if not got:
            break
        rows += got
    seen, versions = set(), []
    for r in rows:
        if not r["id"] or r["id"] in seen:
            continue
        seen.add(r["id"])
        files = file_rows(as_json(p.get(API + r["id"])[3]))
        if not files:
            files = file_rows(as_json(p.get(API + r["id"] + "/files")[3]))
        versions.append(dict(r, files=files))
    return {"seed_status": status, "versions_url": versions_url, "versions": versions,
            "history": history(versions)}


def probe_eia(p):
    out = []
    for y in ER_YEARS:
        for url in er_urls(y):
            status, ctype, length, _, err = p.get(url, method="HEAD")
            out.append({"year": y, "url": url, "status": status, "content_type": ctype,
                        "content_length": length, "error": err})
    return out


def write_md(path, z, eia, calls):
    md = ["# Dated copies of the annual EIA-860 (zenodoprobe %s)" % __version__, "",
          "MV2 of Munim, Inc. (made with AI agents). Metadata only: no generator data was read.",
          "", "Zenodo versions URL: %s; %d versions found; %d calls in all." % (
              z["versions_url"], len(z["versions"]), len(calls)), "",
          "## Zenodo versions", "",
          "| id | version | publication_date | files | newest eia860 file |", "|---|---|---|---|---|"]
    for v in sorted(z["versions"], key=lambda v: (v.get("publication_date") or "", v["id"])):
        years = sorted(f["key"] for f in v["files"] if f["key"].startswith("eia860-"))
        md.append("| %s | %s | %s | %d | %s |" % (v["id"], v.get("version"),
                                                  v.get("publication_date"), len(v["files"]),
                                                  years[-1] if years else ""))
    md += ["", "## Checksum changes of each eia860-YYYY.zip, 2015 on", "",
           "| file | change | first_date | first_version | first_id | size | checksum |",
           "|---|---|---|---|---|---|---|"]
    for key in sorted(k for k in z["history"] if k.startswith("eia860-") and k[7:11] >= "2015"):
        for i, h in enumerate(z["history"][key], 1):
            md.append("| %s | %d | %s | %s | %s | %s | %s |" % (
                key, i, h["first_date"], h["first_version"], h["first_id"], h["size"],
                h["checksum"]))
    md += ["", "## EIA early-release file names (HEAD only)", "",
           "| year | url | status | content_type | content_length | error |",
           "|---|---|---|---|---|---|"]
    for r in eia:
        md.append("| %d | %s | %s | %s | %s | %s |" % (r["year"], r["url"], r["status"],
                                                       r["content_type"], r["content_length"],
                                                       r["error"] or ""))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--seed", default=SEED)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    p = Prober()
    z = probe_zenodo(p, args.seed)
    eia = probe_eia(p)
    out = {"meta": {"version": __version__, "seed": args.seed, "user_agent": UA,
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
           "zenodo": z, "eia_er": eia, "calls": p.calls}
    with open(os.path.join(args.out_dir, "zenodoprobe.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    write_md(os.path.join(args.out_dir, "zenodoprobe.md"), z, eia, p.calls)
    print(json.dumps({"versions": len(z["versions"]), "calls": len(p.calls),
                      "eia_ok": sum(1 for r in eia if r["status"] == 200)}, indent=1))


if __name__ == "__main__":
    main()
