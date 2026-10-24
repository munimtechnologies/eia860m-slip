"""wait_eia: wait until EIA serves its EIA-860M workbook for a month, then exit 0.

MV2 of Munim, Inc. (made with AI agents). Apache-2.0.

Checks EIA's archive and current addresses for the month's generator workbook every --every
seconds (honest User-Agent). Exits 0 as soon as one of them serves an xlsx file (zip magic
bytes), or 3 when --deadline (UTC, YYYY-MM-DDTHH:MM) passes first, so the scoring step does not
run on a file EIA has not published. Downloads nothing to disk; monthcheck.py fetches the file
itself.

    python -u wait_eia.py --month 2026-09 --deadline 2026-10-23T20:30
"""

import argparse
import calendar
import time
import urllib.request

__version__ = "0.1.0"
BASE = "https://www.eia.gov/electricity/data/eia860m/"
NAMES = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
         "october", "november", "december")
UA = "mv2-munim-wait-eia/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % __version__
MAGIC = b"PK\x03\x04"


def urls(month):
    """Archive and current URLs of EIA's workbook for report month YYYY-MM."""
    year, mm = month.split("-")
    name = "%s_generator%s.xlsx" % (NAMES[int(mm) - 1], year)
    return [BASE + "archive/xls/" + name, BASE + "xls/" + name]


def head(url):
    """The first 16 bytes a URL serves."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(16)


def served(month, get=head):
    """(url, first bytes) of the first address serving an xlsx file, or (None, notes)."""
    notes = []
    for url in urls(month):
        try:
            b = get(url)
        except Exception as e:  # recorded, not raised
            notes.append("%s: %s" % (url, type(e).__name__))
            continue
        if b[:4] == MAGIC:
            return url, b
        notes.append("%s: not xlsx (%r)" % (url, b[:8]))
    return None, notes


def deadline_ts(text):
    return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M"))


def wait(month, deadline, every, get=head, clock=time.time, sleep=time.sleep, log=print):
    """Polls until served or past deadline -> the serving url, or None."""
    while True:
        url, info = served(month, get)
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(clock()))
        if url:
            log("%s served: %s" % (stamp, url))
            return url
        log("%s not yet: %s" % (stamp, "; ".join(info)))
        if clock() + every > deadline:
            log("deadline passed: EIA's %s file was not served; nothing scored" % month)
            return None
        sleep(every)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--month", required=True)
    ap.add_argument("--deadline", required=True, help="UTC, YYYY-MM-DDTHH:MM")
    ap.add_argument("--every", type=int, default=600)
    args = ap.parse_args(argv)
    return 0 if wait(args.month, deadline_ts(args.deadline), args.every) else 3


if __name__ == "__main__":
    raise SystemExit(main())
