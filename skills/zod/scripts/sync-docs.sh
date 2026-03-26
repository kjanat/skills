#!/usr/bin/env bash
# sync-docs.sh — Idempotent vendor of Zod v4 docs
#
# Source:
#   colinhacks/zod -> packages/docs/content -> docs/
#
# Usage:
#   bash scripts/sync-docs.sh
#   bash scripts/sync-docs.sh --ref main
#   bash scripts/sync-docs.sh --ref <sha>
#   bash scripts/sync-docs.sh --dry-run

set -euo pipefail

REPO="colinhacks/zod"
REF="main"
DOCS_SUBPATH="packages/docs/content"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
	case "$1" in
		--ref)
			REF="$2"
			shift 2
			;;
		--dry-run)
			DRY_RUN=true
			shift
			;;
		-h | --help)
			sed -n '2,/^$/s/^# //p' "$0"
			exit 0
			;;
		*)
			echo "Unknown arg: $1" >&2
			exit 1
			;;
	esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
DOCS_DIR="${SKILL_DIR}/docs"
REFS_DIR="${SKILL_DIR}/references"
PARSE_FRONTMATTER="${SCRIPT_DIR}/parse-frontmatter.py"
GENERATE_REFERENCES="${SCRIPT_DIR}/generate-references.py"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

log() { printf '\033[1;34m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
err() { printf '\033[1;31mERR: %s\033[0m\n' "$*" >&2; }

for cmd in curl tar python3; do
	command -v "${cmd}" >/dev/null 2>&1 || {
		err "Missing: ${cmd}"
		exit 1
	}
done

for script in "${PARSE_FRONTMATTER}" "${GENERATE_REFERENCES}"; do
	[[ -f "${script}" ]] || {
		err "Missing helper script: ${script}"
		exit 1
	}
done

log "Downloading ${REPO}@${REF}"
TARBALL_URL="https://api.github.com/repos/${REPO}/tarball/${REF}"
curl -sL "${TARBALL_URL}" -o "${TMP_DIR}/repo.tar.gz"
tar xzf "${TMP_DIR}/repo.tar.gz" -C "${TMP_DIR}"

EXTRACTED_ROOT="$(find "${TMP_DIR}" -maxdepth 1 -type d -name 'colinhacks-zod-*' | head -1)"
if [[ -z "${EXTRACTED_ROOT}" || ! -d "${EXTRACTED_ROOT}/${DOCS_SUBPATH}" ]]; then
	err "${DOCS_SUBPATH} not found in tarball"
	exit 1
fi

DOC_COUNT="$(find "${EXTRACTED_ROOT}/${DOCS_SUBPATH}" -type f \( -name '*.md' -o -name '*.mdx' \) ! -path '*/blog/*' | wc -l | tr -d ' ')"
info "Found ${DOC_COUNT} vendorable docs files (excluding blog)"

if ${DRY_RUN}; then
	info "[dry-run] Would sync ${DOC_COUNT} files to ${DOCS_DIR}/"
else
	rm -rf "${DOCS_DIR}"
	mkdir -p "${DOCS_DIR}"
	(
		cd "${EXTRACTED_ROOT}/${DOCS_SUBPATH}"
		find . -type f \( -name '*.md' -o -name '*.mdx' \) ! -path './blog/*' -print0 \
			| while IFS= read -r -d '' f; do
				mkdir -p "${DOCS_DIR}/$(dirname "${f}")"
				cp "${f}" "${DOCS_DIR}/${f}"
			done
	)
	info "Synced ${DOC_COUNT} files to docs/"
fi

RESOLVED_SHA="$(
	curl -s "https://api.github.com/repos/${REPO}/commits/${REF}" \
		| python3 -c 'import json,sys; print(json.load(sys.stdin).get("sha","unknown"))'
)"
RESOLVED_SHORT="${RESOLVED_SHA:0:12}"
SYNC_DATE="$(date -u +%Y-%m-%d)"

if ! ${DRY_RUN}; then
	log "Generating references"
	TITLES_TSV="${TMP_DIR}/titles.tsv"
	python3 "${PARSE_FRONTMATTER}" "${DOCS_DIR}" >"${TITLES_TSV}"
	python3 "${GENERATE_REFERENCES}" \
		"${REFS_DIR}" \
		"${TITLES_TSV}" \
		"${REPO}" \
		"${REF}" \
		"${RESOLVED_SHA}" \
		"${SYNC_DATE}"
	info "Generated routing-map.md and source-index.md"
fi

log "Done"
info "Resolved commit: ${RESOLVED_SHORT}"
