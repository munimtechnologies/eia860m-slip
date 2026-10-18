"""steo-text: pull the solar and wind capacity sentences out of archived Short-Term Energy Outlook PDFs.

MV2 of Munim, Inc. Made with AI agents. Apache-2.0.

For the STEO-vs-plan comparison (eia860m-slip): EIA's STEO archive is PDF only, so this downloads each
edition, extracts its text page by page with pypdf, and writes every sentence that mentions solar,
photovoltaic or wind together with a GW figure, with its page number. Nothing is interpreted here; the
sentences are read and scored by hand against a pre-registration.

    python steo_text.py --data-dir=/data --out-dir=/out jan20 feb20 jan21 ...
"""

__version__ = "0.1.0"

import argparse
import json
import os
import re
import sys
import urllib.request

ARCHIVE = "https://www.eia.gov/outlooks/steo/archives/%s.pdf"
TOPIC = re.compile(r"\b(solar|photovoltaic|PV|wind)\b", re.I)
AMOUNT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:GW|gigawatts?)\b", re.I)


def sentences(text):
    """Split page text into sentences, joining the line breaks pdf text extraction leaves inside them."""
    flat = re.sub(r"\s+", " ", text.replace("­", "")).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"(])", flat) if s.strip()]


def matches(text):
    """Sentences that name solar/PV/wind and give a GW amount."""
    return [s for s in sentences(text) if TOPIC.search(s) and AMOUNT.search(s)]


def fetch(edition, data_dir):
    path = os.path.join(data_dir, edition + ".pdf")
    if os.path.exists(path) and os.path.getsize(path) >= 10000:
        return path
    last = None
    for name in (edition, edition.capitalize()):  # the archive mixes jan23.pdf and Jan23.pdf
        req = urllib.request.Request(ARCHIVE % name, headers={"User-Agent": "MV2 of Munim, Inc. mv2@munimtech.com"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
        except Exception as e:
            last = e
            continue
        if body[:4] == b"%PDF":
            with open(path, "wb") as fh:
                fh.write(body)
            return path
        last = ValueError("%s is not a PDF" % (ARCHIVE % name))
    raise last


def extract(path):
    from pypdf import PdfReader  # imported here so the tests need only the standard library
    return [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(path).pages)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("editions", nargs="+")
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"tool": "steo-text " + __version__, "editions": {}}
    for ed in a.editions:
        try:
            pages = extract(fetch(ed, a.data_dir))
        except Exception as e:  # one bad edition must not stop the rest
            summary["editions"][ed] = {"error": repr(e)}
            print("%s: ERROR %r" % (ed, e))
            continue
        hits = [(n, s) for n, t in pages for s in matches(t)]
        with open(os.path.join(a.out_dir, ed + ".txt"), "w", encoding="utf-8") as fh:
            for n, t in pages:
                fh.write("\n===== page %d =====\n%s\n" % (n, t))
        with open(os.path.join(a.out_dir, ed + "-capacity.md"), "w", encoding="utf-8") as fh:
            fh.write("# %s: sentences naming solar/PV/wind with a GW figure\n\nSource: %s\n\n" % (ed, ARCHIVE % ed))
            for n, s in hits:
                fh.write("- p. %d: %s\n" % (n, s))
        summary["editions"][ed] = {"pages": len(pages), "sentences": len(hits)}
        print("%s: %d pages, %d sentences" % (ed, len(pages), len(hits)))
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
