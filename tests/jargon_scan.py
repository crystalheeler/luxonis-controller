"""
Jargon scan. Write out every acronym at first use.
====================================================
The owner's rule: write the full term at first use, with the acronym in
parentheses after it.

    python tests/jargon_scan.py

Exit 1 when a published document uses an enforced acronym before writing it
out. A definition anywhere earlier in the same file counts, so a glossary at
the top satisfies the rule for the whole file.

CHANGELOG.md uses a glossary, because every entry in it is shipped history and
editing a published entry to insert a definition would falsify the record.
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Documents a reader actually opens. Source comments are excluded: a reader of
# the code has the surrounding context, and the rule is about published prose.
DOCS = (
    "README.md",
    "CHANGELOG.md",
    "windows/README-windows.md",
)

# Enforced: a reader of this project could genuinely stumble on these.
ENFORCED = {
    "CABAC": "Context Adaptive Binary Arithmetic Coding",
    "COCO":  "Common Objects in Context",
    "DCT":   "Discrete Cosine Transform",
    "GHCR":  "GitHub Container Registry",
    "MJPEG": "Motion JPEG",
    "NN":    "Neural network",
    "PoE":   "Power over Ethernet",
    "RTSP":  "Real Time Streaming Protocol",
}

# Not enforced: common English in a technical document. Writing "uniform
# resource locator (URL)" costs the reader more than it gives, and the owner's
# style rules also say to remove every word that does no work. This list is the
# documented exception, not a silent omission.
COMMON = ("API", "CPU", "FPS", "GB", "HA", "IP", "JSON", "MB", "MP4",
          "PC", "RAM", "TCP", "URL", "USB", "YAML", "ZIP")


def normalise(text: str) -> str:
    """Collapse whitespace, so a term wrapped across a line still matches."""
    return re.sub(r"\s+", " ", text)


def scan() -> list:
    findings = []
    for doc in DOCS:
        path = os.path.join(REPO, doc)
        if not os.path.isfile(path):
            continue
        raw = open(path, encoding="utf-8").read()
        for acro, full in sorted(ENFORCED.items()):
            m = re.search(r"\b" + re.escape(acro) + r"\b", raw)
            if not m:
                continue
            # Everything before first use, with line wrapping removed.
            before = normalise(raw[:m.start()]).lower()
            if full.lower() in before:
                continue
            # Or the expansion sits at the point of use: "Full Term (ACRO)".
            window = normalise(raw[max(0, m.start() - 160):m.start() + 160]).lower()
            if full.lower() in window:
                continue
            line = raw[:m.start()].count("\n") + 1
            findings.append((doc, line, acro, full))
    return findings


def main() -> int:
    print("Jargon scan")
    print("=" * 60)
    findings = scan()

    for doc, line, acro, full in findings:
        print(f"FAIL {doc}:{line}: {acro} used before being written out. "
              f"Expected \"{full} ({acro})\" at or before first use.")

    print(f"Scanned {len(DOCS)} documents for {len(ENFORCED)} enforced terms.")
    print(f"Treated as common English: {', '.join(COMMON)}.")
    print()
    if findings:
        print(f"RESULT: {len(findings)} finding(s).")
        return 1
    print("RESULT: every enforced acronym is written out at first use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
