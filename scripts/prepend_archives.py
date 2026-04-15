"""Prepend all year archive entries (oldest first) to data/howland_ratings.csv.

Each archive file must already be in Name,Rating,Notes format (run
transform_archives.py first if needed). The archives are inserted between the
header row and the existing entries so the combined file remains ordered
oldest-to-newest.
"""

import csv
from pathlib import Path

ARCHIVE_DIR = Path(__file__).parent.parent / "data" / "year_archives"
RATINGS_FILE = Path(__file__).parent.parent / "data" / "howland_ratings.csv"


def read_entries(path: Path) -> list[list[str]]:
    """Read all data rows (excluding header) from a Name,Rating,Notes CSV."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    # Skip header row
    return [r for r in rows[1:] if any(cell.strip() for cell in r)]


def main() -> None:
    archives = sorted(ARCHIVE_DIR.glob("archive_*.csv"))
    if not archives:
        print(f"No archive files found in {ARCHIVE_DIR}")
        return

    archive_entries: list[list[str]] = []
    for path in archives:
        entries = read_entries(path)
        archive_entries.extend(entries)
        print(f"  {path.name}: {len(entries)} entries")

    existing_entries = read_entries(RATINGS_FILE)
    print(f"  howland_ratings.csv: {len(existing_entries)} existing entries")

    combined = archive_entries + existing_entries
    with open(RATINGS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Rating", "Notes"])
        writer.writerows(combined)

    print(f"\nWrote {len(combined)} total entries to {RATINGS_FILE.name}")


if __name__ == "__main__":
    main()
