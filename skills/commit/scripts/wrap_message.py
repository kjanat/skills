#!/usr/bin/env python3
"""Qualify the references in a commit message and wrap it to the width GitHub shows.

GitHub keeps the newlines a message contains and rewrites the references inside
it. `owner/repo#123` is displayed as `owner#123`, and a bare `#123` that does
not resolve in this repository is displayed as, and links to, the upstream one.
Wrapping on stored width therefore leaves lines that are ragged once rendered.

Bare references are looked up in this repository through `gh`. Those that
resolve are left bare. Those that do not are rewritten to the upstream
repository, so that what is stored says where a reference points and what is
displayed reaches the margin.

Takes a commit to read the message from, or reads one on stdin.

    wrap_message.py 4ad1e18
    git log -1 --format=%B | wrap_message.py

Subject, fenced blocks, lists, quotes, indented blocks and trailers are passed
through as they are, as is any paragraph holding a word too long to wrap.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

TRAILER = re.compile(r"^[A-Za-z][A-Za-z-]*:\s")
MARKUP = re.compile(r"^\s*(?:[-*+>|]|\d+[.)]|#{1,6}\s|```|~~~)")
REFERENCE = re.compile(
    r"(?<![\w./-])(?:(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+))?#(?P<number>\d+)\b"
)


def run(command: list[str]) -> str | None:
    """Standard output of `command`, or None when it is unavailable or fails."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def repo_of_remote(remote: str) -> str | None:
    url = run(["git", "remote", "get-url", remote])
    if not url:
        return None
    match = re.search(r"[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$", url)
    return match.group(1) if match else None


def parent_of(repo: str) -> str | None:
    parent = run([
        "gh",
        "repo",
        "view",
        repo,
        "--json",
        "parent",
        "-q",
        ".parent.nameWithOwner",
    ])
    return parent or None


class References:
    """Where each reference in a message points, and how wide it is on screen."""

    def __init__(self, local: str | None, upstream: str | None) -> None:
        self.local = local
        self.upstream = upstream
        self.resolved: dict[str, str | None] = {}

    def target(self, number: str) -> str | None:
        """Repository a bare `#number` belongs to, or None when it cannot be told."""
        if self.local is None:
            return None
        if number not in self.resolved:
            found = run([
                "gh",
                "api",
                f"repos/{self.local}/issues/{number}",
                "-q",
                ".number",
            ])
            self.resolved[number] = self.local if found else self.upstream
        return self.resolved[number]

    def qualify(self, text: str) -> str:
        def rewrite(match: re.Match[str]) -> str:
            owner, repo, number = match.group("owner", "repo", "number")
            target = f"{owner}/{repo}" if owner else self.target(number)
            if target is None or target == self.local:
                return f"#{number}"
            return f"{target}#{number}"

        return REFERENCE.sub(rewrite, text)

    @staticmethod
    def displayed(text: str) -> str:
        def render(match: re.Match[str]) -> str:
            owner, number = match.group("owner", "number")
            return f"{owner}#{number}" if owner else f"#{number}"

        return REFERENCE.sub(render, text)

    @classmethod
    def width(cls, text: str) -> int:
        return len(cls.displayed(text))


def wrap_paragraph(words: list[str], width: int, floor: int) -> list[str]:
    """Break `words` into lines that display at most `width` characters."""
    count = len(words)
    if count == 0:
        return []

    shown = [References.width(word) for word in words]

    # extent[i][j] is the displayed width of words i..j joined by single spaces.
    extent = [[0] * (count + 1) for _ in range(count + 1)]
    for i in range(count):
        total = shown[i]
        extent[i][i + 1] = total
        for j in range(i + 1, count):
            total += 1 + shown[j]
            extent[i][j + 1] = total

    def layout(last_line_minimum: int) -> list[int]:
        """Cheapest set of breaks, leaving breaks[0] at 0 when the floor is unreachable."""
        cost: list[float] = [float("inf")] * (count + 1)
        breaks = [0] * (count + 1)
        cost[count] = 0.0
        for i in range(count - 1, -1, -1):
            for j in range(i + 1, count + 1):
                line = extent[i][j]
                if line > width and j > i + 1:
                    break
                if line > width:
                    penalty = 0.0
                elif j == count:
                    penalty = float("inf") if line < last_line_minimum else 0.0
                else:
                    slack = width - line
                    penalty = float(slack * slack)
                candidate = penalty + cost[j]
                if candidate < cost[i]:
                    cost[i] = candidate
                    breaks[i] = j
        return breaks

    # A last line short of the floor is refused outright rather than priced, so
    # that no weighting has to be invented to make it lose. Some paragraphs
    # cannot satisfy it, a long word followed by a short one being the plain
    # case, and those are laid out without it.
    breaks = layout(floor)
    if breaks[0] == 0:
        breaks = layout(0)

    lines = []
    start = 0
    while start < count:
        end = breaks[start]
        lines.append(" ".join(words[start:end]))
        start = end
    return lines


def is_prose(paragraph: list[str], width: int) -> bool:
    """Whether reflowing this paragraph is safe."""
    for line in paragraph:
        if line.startswith((" ", "\t")) or MARKUP.match(line) or TRAILER.match(line):
            return False
    return all(
        References.width(word) <= width for line in paragraph for word in line.split()
    )


def wrap_message(message: str, width: int, floor: int, keep_subject: bool) -> str:
    lines = message.split("\n")

    head: list[str] = []
    if keep_subject and lines:
        head.append(lines[0])
        del lines[0]
        while lines and not lines[0].strip():
            head.append(lines.pop(0))

    out: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if not paragraph:
            return
        if is_prose(paragraph, width):
            out.extend(wrap_paragraph(" ".join(paragraph).split(), width, floor))
        else:
            out.extend(paragraph)
        paragraph.clear()

    fenced = False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            flush()
            out.append(line)
            fenced = not fenced
            continue
        if fenced:
            out.append(line)
            continue
        if line.strip():
            paragraph.append(line)
        else:
            flush()
            out.append(line)
    flush()

    return "\n".join(head + out)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument(
        "commit", nargs="?", help="commit to read the message from, stdin when absent"
    )
    parser.add_argument("--width", type=int, default=72, help="displayed line width")
    parser.add_argument(
        "--floor",
        type=int,
        default=None,
        help="shortest acceptable final line of a paragraph, default half the width",
    )
    parser.add_argument("--repo", default=None, help="this repository, default origin")
    parser.add_argument(
        "--upstream", default=None, help="repository bare references fall back to"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="leave references as they are written instead of looking them up",
    )
    parser.add_argument(
        "--wrap-subject",
        action="store_true",
        help="also reflow the subject line, which is otherwise left alone",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="print stored and displayed line widths on stderr",
    )
    args = parser.parse_args()

    if args.width < 20:
        parser.error("width must be at least 20")
    floor = args.width // 2 if args.floor is None else args.floor
    if not 0 <= floor <= args.width:
        parser.error("floor must be between 0 and the width")

    if args.commit:
        message = run(["git", "log", "-1", "--format=%B", args.commit])
        if message is None:
            parser.error(f"no commit {args.commit}")
        message += "\n"
    else:
        message = sys.stdin.read()

    if args.offline:
        local = upstream = None
    else:
        local = args.repo or repo_of_remote("origin")
        upstream = args.upstream or repo_of_remote("upstream")
        if upstream is None and local is not None:
            upstream = parent_of(local)
        if local is None:
            print("no origin remote, leaving references alone", file=sys.stderr)

    references = References(local, upstream)
    trailing_newline = message.endswith("\n")
    wrapped = wrap_message(
        references.qualify(message.rstrip("\n")),
        args.width,
        floor,
        not args.wrap_subject,
    )

    sys.stdout.write(wrapped + ("\n" if trailing_newline else ""))

    if args.report:
        print(f"{'stored':>6}  {'shown':>5}", file=sys.stderr)
        for line in wrapped.split("\n"):
            print(
                f"{len(line):>6}  {References.width(line):>5}  {line}", file=sys.stderr
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
