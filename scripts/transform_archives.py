"""Transform year archive files into standard Name,Rating,Notes CSV format in-place.

Archive format:
  - Header row starting with "Films"
  - Entries like "Movie Title X/10" (possibly with trailing comma, 2-column layout)
  - Blank rows between entries

Output format (matches howland_ratings.csv):
  Name,Rating,Notes
"""

import csv
import re
import sys
from pathlib import Path

ARCHIVE_DIR = Path(__file__).parent.parent / "data" / "year_archives"
# Matches "X/10" or "(X/10)" anywhere in the line; captures score digits
RATING_RE = re.compile(r"\(?(\d+)/10\)?")
# Typo correction: "X/0" at end of line where X is 1-2 digits
TYPO_RE = re.compile(r"^(.*?)\s+(\d{1,2})/0$")


def parse_line(line: str) -> tuple[str, str] | None:
    """Return (name, rating) from a single entry line, or None if unparseable."""
    # Strip surrounding quotes (e.g. "Beetlejuice, Beetlejuice 8/10")
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1].strip()

    # Find the first X/10 or (X/10) occurrence
    m = RATING_RE.search(line)
    if m:
        name = line[: m.start()].strip().rstrip("(").strip()
        rating = f"{m.group(1)}/10"
        return name, rating

    # Handle typos like "7/0" → "7/10"
    m = TYPO_RE.match(line)
    if m:
        return m.group(1).strip(), f"{m.group(2)}/10"

    return None


def parse_archive(path: Path) -> list[tuple[str, str]]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for line in f:
            # Strip newline, outer whitespace, and stray commas (2-column layout)
            line = line.rstrip("\n").strip().strip(",").strip()
            # Skip blank lines, header rows, and section labels (no rating present)
            if not line or line.startswith("Films") or line.startswith("Name"):
                continue
            result = parse_line(line)
            if result is None:
                print(f"  WARNING: could not parse line in {path.name!r}: {line!r}", file=sys.stderr)
                continue
            name, rating = result
            if not name:
                continue
            rows.append((name, rating))
    return rows


def write_csv(path: Path, rows: list[tuple[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Rating", "Notes"])
        for name, rating in rows:
            writer.writerow([name, rating, ""])


def main() -> None:
    archives = sorted(ARCHIVE_DIR.glob("archive_*.csv"))
    if not archives:
        print(f"No archive files found in {ARCHIVE_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in archives:
        rows = parse_archive(path)
        write_csv(path, rows)
        print(f"Transformed {path.name}: {len(rows)} entries")


if __name__ == "__main__":
    main()
