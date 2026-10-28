"""Command-line entry point."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .checks import Issue, check_numeric_range, find_duplicates, find_missing
from .report import format_report
from .summary import mean_as_float


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_file(
    path: Path,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> tuple[int, list[Issue]]:
    rows = load_rows(path)
    issues: list[Issue] = []
    issues.extend(find_missing(rows, "measurement"))
    issues.extend(find_duplicates(rows, "sample_id"))
    issues.extend(check_numeric_range(rows, "measurement", minimum, maximum))
    measurements = []
    for row in rows:
        raw = row.get("measurement", "").strip()
        try:
            measurements.append(float(raw))
        except ValueError:
            continue
    if measurements:
        _ = mean_as_float(measurements)
    return len(rows), issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a research data CSV.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--minimum", type=float, default=0.0)
    parser.add_argument("--maximum", type=float, default=100.0)
    args = parser.parse_args()

    if args.minimum > args.maximum:
        parser.error("--minimum must be less than or equal to --maximum")

    row_count, issues = check_file(args.csv_file, args.minimum, args.maximum)
    print(format_report(args.csv_file.name, row_count, issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
