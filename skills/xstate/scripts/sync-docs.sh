#!/usr/bin/env bash
# sync-docs.sh — Idempotent vendor of XState v5 docs + API types
#
# Sources:
#   1. statelyai/docs (GitHub) → docs/     (narrative MDX)
#   2. xstate npm package      → api/      (.d.ts declarations)
#
# Usage:
#   bash scripts/sync-docs.sh                         # defaults
#   bash scripts/sync-docs.sh --xstate-version 5.28.0 # pin exact version
#   bash scripts/sync-docs.sh --xstate-version 5     # latest 5.x (default)
#   bash scripts/sync-docs.sh --docs-ref main         # pin docs commit/branch
#   bash scripts/sync-docs.sh --dry-run               # show what would change
#
# Deterministic: same inputs → same outputs. Re-run to upgrade.

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────
XSTATE_VERSION="5"
DOCS_REPO="statelyai/docs"
DOCS_REF="main"
DOCS_SUBPATH="content/docs"
DRY_RUN=false

# ── Parse args ────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
	case "$1" in
		--xstate-version)
			XSTATE_VERSION="$2"
			shift 2
			;;
		--docs-ref)
			DOCS_REF="$2"
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

# ── Paths ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
DOCS_DIR="${SKILL_DIR}/docs"
API_DIR="${SKILL_DIR}/api"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

log() { printf '\033[1;34m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
err() { printf '\033[1;31mERR: %s\033[0m\n' "$*" >&2; }

# ── Preflight checks ─────────────────────────────────────────────────
for cmd in curl tar npm python3; do
	command -v "${cmd}" >/dev/null 2>&1 || {
		err "Missing: ${cmd}"
		exit 1
	}
done

# ── 1. Vendor narrative docs from GitHub ──────────────────────────────
log "Downloading docs from ${DOCS_REPO}@${DOCS_REF}"

TARBALL_URL="https://api.github.com/repos/${DOCS_REPO}/tarball/${DOCS_REF}"
curl -sL "${TARBALL_URL}" -o "${TMP_DIR}/docs.tar.gz"

# GitHub tarballs have a random prefix dir — find it
tar xzf "${TMP_DIR}/docs.tar.gz" -C "${TMP_DIR}"
EXTRACTED_ROOT="$(find "${TMP_DIR}" -maxdepth 1 -type d -name 'statelyai-docs-*' | head -1)"

if [[ -z "${EXTRACTED_ROOT}" || ! -d "${EXTRACTED_ROOT}/${DOCS_SUBPATH}" ]]; then
	err "${DOCS_SUBPATH} not found in tarball"
	exit 1
fi

DOC_COUNT="$(find "${EXTRACTED_ROOT}/${DOCS_SUBPATH}" \( -name '*.md' -o -name '*.mdx' \) | wc -l)"
info "Found ${DOC_COUNT} doc files"

if ${DRY_RUN}; then
	info "[dry-run] Would sync ${DOC_COUNT} files to ${DOCS_DIR}/"
else
	rm -rf "${DOCS_DIR}"
	mkdir -p "${DOCS_DIR}"
	# Copy only text docs — skip images/binaries (agents can't use them)
	(cd "${EXTRACTED_ROOT}/${DOCS_SUBPATH}" && find . \( -name '*.md' -o -name '*.mdx' \) -print0 \
		| while IFS= read -r -d '' f; do
			mkdir -p "${DOCS_DIR}/$(dirname "${f}")"
			cp "${f}" "${DOCS_DIR}/${f}"
		done)
	info "Synced ${DOC_COUNT} text files to docs/ (images excluded)"
fi

# Resolve actual commit SHA (DOCS_REF may be a branch name)
RESOLVED_SHA="$(curl -s "https://api.github.com/repos/${DOCS_REPO}/commits/${DOCS_REF}" \
	| python3 -c "import json,sys; print(json.load(sys.stdin).get('sha','unknown')[:12])")"

# ── 2. Vendor API types from npm ─────────────────────────────────────
# Resolve semver range to exact version (e.g. "5" → "5.28.0")
RESOLVED_VERSION="$(npm view "xstate@${XSTATE_VERSION}" version 2>/dev/null \
	| tail -1 | grep -oP '\d+\.\d+\.\d+' | tail -1)"
if [[ -z "${RESOLVED_VERSION}" ]]; then
	err "Could not resolve xstate@${XSTATE_VERSION}"
	exit 1
fi
log "Extracting API types for xstate@${RESOLVED_VERSION} (from specifier '${XSTATE_VERSION}')"

(cd "${TMP_DIR}" && npm pack "xstate@${RESOLVED_VERSION}" --silent)
TARBALL="$(find "${TMP_DIR}" -name 'xstate-*.tgz' | head -1)"

if [[ -z "${TARBALL}" ]]; then
	err "npm pack failed for xstate@${RESOLVED_VERSION}"
	exit 1
fi

mkdir -p "${TMP_DIR}/pkg"
tar xzf "${TARBALL}" -C "${TMP_DIR}/pkg"

# Collect .d.ts and .d.mts files
DTS_COUNT="$(find "${TMP_DIR}/pkg/package" \( -name '*.d.ts' -o -name '*.d.mts' \) | wc -l)"
info "Found ${DTS_COUNT} type declaration files"

if ${DRY_RUN}; then
	info "[dry-run] Would sync ${DTS_COUNT} type files to ${API_DIR}/"
	find "${TMP_DIR}/pkg/package" \( -name '*.d.ts' -o -name '*.d.mts' \) \
		-exec bash -c 'echo "    ${0#*/package/}"' {} \;
else
	rm -rf "${API_DIR}"
	mkdir -p "${API_DIR}"

	find "${TMP_DIR}/pkg/package" \( -name '*.d.ts' -o -name '*.d.mts' \) | while IFS= read -r f; do
		rel="${f#*/package/}"
		dest_dir="${API_DIR}/$(dirname "${rel}")"
		mkdir -p "${dest_dir}"
		cp "${f}" "${API_DIR}/${rel}"
	done
	info "Synced to api/"
fi

# Also extract package.json for version/exports metadata
if ! ${DRY_RUN}; then
	cp "${TMP_DIR}/pkg/package/package.json" "${API_DIR}/package.json"
	info "Saved api/package.json (exports map)"
fi

# ── 3. Generate routing map from frontmatter ─────────────────────────
if ! ${DRY_RUN}; then
	log "Generating routing map (parsing frontmatter)"

	ROUTING_MAP="${SKILL_DIR}/references/routing-map.md"

	# Extract title + relative path from every doc, classify into sections
	# Classification heuristics (applied to filename + title):
	#   - title contains "Stately" / "editor" / filename starts with editor-/studio- → Stately Editor
	#   - filename starts with xstate- or is immer → Integrations
	#   - title contains "migrat" / "upgrade" / filename is xstate-fsm → Migration
	#   - title/filename matches tooling keywords → Tooling
	#   - everything else → Core Concepts

	declare -a CORE=() MIGRATION=() INTEGRATIONS=() TOOLING=() EDITOR=()

	TOOLING_PATTERNS="developer.tools|export.as.code|import.from|typegen|vscode.extension|inspector|machine.restore|xstate-vscode"

	frontmatter="$(python3 "${SCRIPT_DIR}/parse-frontmatter.py" "${DOCS_DIR}")"

	while IFS=$'\t' read -r rel_path title; do
		slug="$(basename "${rel_path}" | sed 's/\.\(mdx\|md\)$//')"

		# Skip index files at root (they're landing pages)
		[[ "${slug}" == "index" && "$(dirname "${rel_path}")" == "." ]] && slug="index"

		# Classify (order matters — more specific checks first)
		if [[ "${title}" =~ Stately ]] || [[ "${title}" =~ editor ]] \
			|| [[ "${slug}" =~ ^editor- ]] || [[ "${slug}" =~ ^studio ]] \
			|| [[ "${slug}" =~ ^(annotations|assets|autolayout|canvas-view-controls|colors|descriptions|design-mode|discover|embed|figma|generate-|image|keyboard-shortcuts|live-simulation|lock-machines|packages|projects|routes|sign-up|simulate-mode|sources|teams|templates|url|user-preferences|versions|visualizer)$ ]]; then
			EDITOR+=("${title}"$'\t'"${rel_path}")
		elif echo "${slug}" | grep -qE "${TOOLING_PATTERNS}"; then
			TOOLING+=("${title}"$'\t'"${rel_path}")
		elif [[ "${title}" =~ [Mm]igrat ]] || [[ "${slug}" == "xstate-fsm" ]]; then
			MIGRATION+=("${title}"$'\t'"${rel_path}")
		elif [[ "${slug}" =~ ^xstate- ]] || [[ "${slug}" == "immer" ]]; then
			INTEGRATIONS+=("${title}"$'\t'"${rel_path}")
		else
			CORE+=("${title}"$'\t'"${rel_path}")
		fi
	done <<<"${frontmatter}"

	# Write routing map
	write_section() {
		local header="$1"
		shift
		local -a entries=("$@")
		[[ ${#entries[@]} -eq 0 ]] && return

		printf '\n## %s\n\n| Title | File |\n|-------|------|\n' "${header}" >>"${ROUTING_MAP}"
		printf '%s\n' "${entries[@]}" | sort -t$'\t' -k1,1 | while IFS=$'\t' read -r title rel; do
			# shellcheck disable=SC2016 # backticks are literal markdown, not shell
			printf '| %s | `docs/%s` |\n' "${title}" "${rel}" >>"${ROUTING_MAP}"
		done
	}

	cat >"${ROUTING_MAP}" <<'HEADER'
# Routing Map

Auto-generated from vendored doc frontmatter. Topic → doc file.
Load the file matching the user's question.
HEADER

	write_section "Core Concepts" "${CORE[@]}"
	write_section "Migration" "${MIGRATION[@]}"
	write_section "Integrations" "${INTEGRATIONS[@]}"
	write_section "Tooling" "${TOOLING[@]}"
	write_section "Stately Editor" "${EDITOR[@]}"

	ENTRY_COUNT="$(grep -c '^|[^-]' "${ROUTING_MAP}" || true)"
	info "Generated routing map with ${ENTRY_COUNT} entries from frontmatter"
fi

# ── 4. Generate source index ─────────────────────────────────────────
if ! ${DRY_RUN}; then
	log "Writing provenance to references/source-index.md"

	sync_date="$(date -u +%Y-%m-%d)"

	cat >"${SKILL_DIR}/references/source-index.md" <<EOF
# Source Index

Canonical sources and version pins for vendored content.

## Provenance

| Source | Ref | Resolved | Date |
|--------|-----|----------|------|
| [statelyai/docs](https://github.com/${DOCS_REPO}) | \`${DOCS_REF}\` | \`${RESOLVED_SHA}\` | ${sync_date} |
| [xstate npm](https://www.npmjs.com/package/xstate) | \`${XSTATE_VERSION}\` | \`${RESOLVED_VERSION}\` | ${sync_date} |

## External references (not vendored)

- [jsdocs.io/package/xstate](https://www.jsdocs.io/package/xstate) — rendered API browser
- [stately.ai/docs](https://stately.ai/docs) — official docs site

## Re-sync

\`\`\`bash
# Update to latest
bash scripts/sync-docs.sh

# Pin specific versions
bash scripts/sync-docs.sh --xstate-version ${RESOLVED_VERSION} --docs-ref ${RESOLVED_SHA}
\`\`\`

## Vendored layout

- \`docs/\` — narrative MDX from statelyai/docs (${DOC_COUNT} files)
- \`api/\` — TypeScript declarations from xstate npm (${DTS_COUNT} .d.ts files)
- \`api/package.json\` — package exports map

## Freshness rule

Guidance is pinned to versions above. When user asks about newer APIs:
1. Answer with pinned guidance first
2. State version limit
3. Recommend checking latest docs
EOF
fi

# ── Summary ───────────────────────────────────────────────────────────
log "Done"
info "xstate@${RESOLVED_VERSION} (specifier: ${XSTATE_VERSION})  |  docs@${RESOLVED_SHA}"
info "Docs: ${DOC_COUNT} files  |  API: ${DTS_COUNT} type files"
${DRY_RUN} && info "(dry-run — no files written)"
exit 0
