#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MarkerMatch:
    marker: str
    marker_width: int
    caret_column: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect Twoslash marker alignment with real line and column counts. "
            "Use this instead of eyeballing spaces for `^?`, `^|`, or `^^^` lines."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files to scan for Twoslash marker lines.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [inspect_path(path) for path in args.paths]
    payload: object
    if len(reports) == 1:
        payload = reports[0]
    else:
        payload = reports
    print(json.dumps(payload, indent=2))


def inspect_path(path: Path) -> dict[str, object]:
    lines = path.read_text().splitlines()
    markers: list[dict[str, object]] = []

    for marker_line_number, marker_line in enumerate(lines, start=1):
        marker_match = detect_marker(marker_line)
        if marker_match is None:
            continue

        code_line_number = marker_line_number - 1
        code_line = "" if code_line_number < 1 else lines[code_line_number - 1]
        ruler_width = max(
            len(code_line), marker_match.caret_column + marker_match.marker_width - 1
        )

        markers.append({
            "code_line_number": code_line_number,
            "marker_line_number": marker_line_number,
            "marker": marker_match.marker,
            "marker_width": marker_match.marker_width,
            "caret_column": marker_match.caret_column,
            "code_length": len(code_line),
            "code_line": code_line,
            "marker_line": marker_line,
            "ruler": build_ruler(ruler_width),
        })

    return {
        "path": str(path),
        "marker_count": len(markers),
        "markers": markers,
    }


def detect_marker(line: str) -> MarkerMatch | None:
    stripped = line.lstrip()
    if not stripped.startswith("//"):
        return None

    if "^^^" in line:
        return MarkerMatch(
            marker="^^^", marker_width=3, caret_column=line.index("^^^") + 1
        )
    if "^?" in line:
        return MarkerMatch(
            marker="^?", marker_width=1, caret_column=line.index("^") + 1
        )
    if "^|" in line:
        return MarkerMatch(
            marker="^|", marker_width=1, caret_column=line.index("^") + 1
        )
    return None


def build_ruler(width: int) -> str:
    if width <= 0:
        return ""
    digits = "1234567890"
    chars = [digits[index % len(digits)] for index in range(width)]
    return "".join(chars)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
