#!/usr/bin/env bash
# maintain.sh — Project-level maintenance for the skills repo
#
# Usage:
#   ./scripts/maintain.sh                   # run all maintenance tasks
#   ./scripts/maintain.sh sync              # sync vendored content only
#   ./scripts/maintain.sh validate          # validate all skills only
#   ./scripts/maintain.sh sync xstate       # sync a specific skill
#   ./scripts/maintain.sh validate xstate   # validate a specific skill
#   ./scripts/maintain.sh status            # show vendored content freshness
#
# Designed for humans and CI alike.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="${ROOT_DIR}/skills"
VALIDATE_SCRIPT="${SKILLS_DIR}/build-skill/scripts/validate_skill.sh"

log() { printf '\033[1;34m==> %s\033[0m\n' "$*"; }
ok() { printf '\033[1;32m ✓  %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m ⚠  %s\033[0m\n' "$*"; }
err() { printf '\033[1;31m ✗  %s\033[0m\n' "$*" >&2; }

# ── Discover skills with sync scripts ────────────────────────────────
# Convention: skills with vendored content have scripts/sync-docs.sh
find_syncable_skills() {
	find "${SKILLS_DIR}" -path '*/scripts/sync-docs.sh' -print0 \
		| xargs -0 -I{} dirname {} | xargs -I{} dirname {} | sort
}

# ── Discover all skills ──────────────────────────────────────────────
find_all_skills() {
	find "${SKILLS_DIR}" -maxdepth 2 -name 'SKILL.md' -exec dirname {} \; | sort
}

# ── Commands ─────────────────────────────────────────────────────────

cmd_sync() {
	local filter="${1:-}"
	shift || true
	local -a extra_args=("$@")
	local synced=0 failed=0

	if [[ -n "${filter}" ]]; then
		local script="${SKILLS_DIR}/${filter}/scripts/sync-docs.sh"
		if [[ ! -f "${script}" ]]; then
			err "No sync script found for '${filter}' at ${script}"
			return 1
		fi
		log "Syncing ${filter}"
		if bash "${script}" "${extra_args[@]+"${extra_args[@]}"}"; then
			ok "${filter} synced"
		else
			err "${filter} sync failed"
			return 1
		fi
		return 0
	fi

	log "Syncing all vendored skills"
	local skills
	skills="$(find_syncable_skills)"
	while IFS= read -r skill_dir; do
		local name
		name="$(basename "${skill_dir}")"
		local script="${skill_dir}/scripts/sync-docs.sh"

		log "Syncing ${name}"
		if bash "${script}" "${extra_args[@]+"${extra_args[@]}"}"; then
			ok "${name}"
			((synced++)) || true
		else
			err "${name}"
			((failed++)) || true
		fi
	done <<<"${skills}"

	echo ""
	log "Sync complete: ${synced} succeeded, ${failed} failed"
	[[ ${failed} -eq 0 ]]
}

cmd_validate() {
	local filter="${1:-}"
	local passed=0 warned=0 failed=0

	if [[ ! -f "${VALIDATE_SCRIPT}" ]]; then
		err "Validation script not found: ${VALIDATE_SCRIPT}"
		return 1
	fi

	if [[ -n "${filter}" ]]; then
		log "Validating ${filter}"
		bash "${VALIDATE_SCRIPT}" "${SKILLS_DIR}/${filter}"
		return $?
	fi

	log "Validating all skills"
	local skills
	skills="$(find_all_skills)"
	while IFS= read -r skill_dir; do
		local name
		name="$(basename "${skill_dir}")"
		local output rc
		output="$(bash "${VALIDATE_SCRIPT}" "${skill_dir}" 2>&1)" && rc=0 || rc=$?

		local wcount
		wcount="$(echo "${output}" | grep -c "WARNING" || true)"

		if [[ ${rc} -ne 0 ]]; then
			err "${name} — INVALID"
			printf '%s\n' "${output}" | sed 's/^/    /'
			((failed++)) || true
		elif [[ ${wcount} -gt 0 ]]; then
			warn "${name} — ${wcount} warning(s)"
			echo "${output}" | grep "WARNING" | sed 's/^/    /' || true
			((warned++)) || true
		else
			ok "${name}"
			((passed++)) || true
		fi
	done <<<"${skills}"

	echo ""
	log "Validation: ${passed} clean, ${warned} warned, ${failed} invalid"
	[[ ${failed} -eq 0 ]]
}

cmd_status() {
	log "Vendored content status"
	echo ""

	local skills
	skills="$(find_syncable_skills)"
	while IFS= read -r skill_dir; do
		local name
		name="$(basename "${skill_dir}")"
		local source_index="${skill_dir}/references/source-index.md"

		if [[ ! -f "${source_index}" ]]; then
			continue
		fi

		echo "  ${name}:"

		# Count vendored files by directory
		for dir in docs api; do
			if [[ -d "${skill_dir}/${dir}" ]]; then
				local count
				count="$(find "${skill_dir}/${dir}" -type f | wc -l | tr -d ' ')"
				local size
				size="$(du -sh "${skill_dir}/${dir}" 2>/dev/null | cut -f1)"
				echo "    ${dir}/  ${count} files  ${size}"
			fi
		done

		# Extract provenance from source-index.md
		python3 -c "
import re, sys
with open('${source_index}') as f:
    text = f.read()
for m in re.finditer(r'\|\s*\[([^\]]+)\][^\|]+\|\s*\x60([^\x60]+)\x60\s*\|\s*\x60?([^\x60|]*)\x60?\s*\|\s*(\S+)\s*\|', text):
    name, ref, resolved, date = m.groups()
    ver = resolved.strip() if resolved.strip() and resolved.strip() != '—' else ref
    print(f'    {name}: {ver}  (synced {date})')
" 2>/dev/null || true
		echo ""
	done <<<"${skills}"
}

cmd_all() {
	cmd_sync
	echo ""
	cmd_validate
	echo ""
	cmd_status
}

# ── Main ─────────────────────────────────────────────────────────────
case "${1:-all}" in
	sync)
		shift
		cmd_sync "$@"
		;;
	validate) cmd_validate "${2:-}" ;;
	status) cmd_status ;;
	all) cmd_all ;;
	-h | --help)
		sed -n '2,/^$/s/^# //p' "$0"
		exit 0
		;;
	*)
		err "Unknown command: $1"
		echo "Usage: $0 [sync|validate|status|all] [skill-name]"
		exit 1
		;;
esac
