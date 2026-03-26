#!/usr/bin/env python3
"""Generate routing-map.md and source-index.md for the Zod skill."""

from __future__ import annotations

import pathlib
import sys


GROUPS = {
    "Core usage": ["index.mdx", "basics.mdx"],
    "Schema API": ["api.mdx"],
    "Errors": ["error-customization.mdx", "error-formatting.mdx"],
    "Advanced features": [
        "metadata.mdx",
        "json-schema.mdx",
        "codecs.mdx",
        "ecosystem.mdx",
        "library-authors.mdx",
    ],
    "Migration / versioning": [
        "v4/index.mdx",
        "v4/changelog.mdx",
        "v4/versioning.mdx",
    ],
    "Packages": [
        "packages/zod.mdx",
        "packages/mini.mdx",
        "packages/core.mdx",
    ],
}


def load_titles(tsv_path: pathlib.Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    for line in tsv_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rel, title = line.split("\t", 1)
        titles[rel] = title
    return titles


def write_routing_map(
    refs_dir: pathlib.Path, titles: dict[str, str], short_sha: str
) -> None:
    lines = [
        "# Routing Map",
        "",
        "Auto-generated from vendored Zod docs frontmatter. Topic to exact doc path.",
        f"Pinned to commit `{short_sha}`.",
    ]

    for section, rel_paths in GROUPS.items():
        lines.extend(["", f"## {section}", "", "| Title | File |", "| --- | --- |"])
        for rel in rel_paths:
            title = titles[rel]
            lines.append(f"| {title} | `docs/{rel}` |")

    (refs_dir / "routing-map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_source_index(
    refs_dir: pathlib.Path,
    repo: str,
    ref: str,
    short_sha: str,
    sync_date: str,
) -> None:
    lines = [
        "# Source Index",
        "",
        "Canonical sources and version pins for vendored content.",
        "",
        "## Provenance",
        "",
        "| Source | Ref | Resolved | Sync date |",
        "| --- | --- | --- | --- |",
        f"| [{repo}](https://github.com/{repo}) | `{ref}` | `{short_sha}` | {sync_date} |",
        "",
        "## Vendored subtree",
        "",
        "- Upstream path: `packages/docs/content`",
        "- Included: `.md` and `.mdx` files under that subtree",
        "- Excluded: `content/blog/`, docs site app/components/pages/public assets, and build config",
        "",
        "## Refresh",
        "",
        "```bash",
        "bash skills/zod/scripts/sync-docs.sh --ref main",
        "bash skills/zod/scripts/sync-docs.sh --ref c7805073fef5b6b8857307c3d4b3597a70613bc2",
        "```",
    ]

    (refs_dir / "source-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    refs_dir = pathlib.Path(sys.argv[1])
    titles_tsv = pathlib.Path(sys.argv[2])
    repo = sys.argv[3]
    ref = sys.argv[4]
    full_sha = sys.argv[5]
    sync_date = sys.argv[6]

    short_sha = full_sha[:12]
    titles = load_titles(titles_tsv)

    write_routing_map(refs_dir, titles, short_sha)
    write_source_index(refs_dir, repo, ref, short_sha, sync_date)


if __name__ == "__main__":
    main()
