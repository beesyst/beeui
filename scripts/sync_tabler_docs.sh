#!/usr/bin/env bash

set -euo pipefail

repo_root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.."
  pwd
)"

destination="${repo_root}/docs/vendor/tabler"
upstream_repository="${TABLER_REPOSITORY:-https://github.com/tabler/tabler.git}"
upstream_ref="${TABLER_REF:-dev}"
upstream_docs_path="docs"
temporary_directory="$(mktemp -d)"
checkout_directory="${temporary_directory}/tabler"
prepared_snapshot="${temporary_directory}/snapshot"
destination_stage=""
backup_directory=""
replacement_started=false
managed_items=(content UPSTREAM_REF UPSTREAM_COMMIT)
backup_items=()
installed_items=()

fail() {
  printf 'Tabler documentation sync failed: %s\n' "$*" >&2
  exit 1
}

add_managed_item() {
  local item="$1"
  local existing

  for existing in "${managed_items[@]}"; do
    if [[ "${existing}" == "${item}" ]]; then
      return
    fi
  done

  managed_items+=("${item}")
}

restore_snapshot() {
  local item

  set +e

  for item in "${installed_items[@]}"; do
    if [[ ! -e "${backup_directory}/${item}" && ! -L "${backup_directory}/${item}" ]]; then
      rm -rf "${destination}/${item}"
    fi
  done

  for item in "${backup_items[@]}"; do
    rm -rf "${destination}/${item}"
    mv "${backup_directory}/${item}" "${destination}/${item}"
  done
}

cleanup() {
  local status="$?"

  trap - EXIT

  if [[ "${replacement_started}" == true && -n "${backup_directory}" ]]; then
    restore_snapshot
  fi

  rm -rf "${destination_stage}" "${backup_directory}" "${temporary_directory}"
  exit "${status}"
}

trap cleanup EXIT

if [[ -z "${upstream_repository}" ]]; then
  fail "TABLER_REPOSITORY must not be empty."
fi

if ! git check-ref-format --allow-onelevel "${upstream_ref}"; then
  fail "Invalid upstream ref '${upstream_ref}'."
fi

if ! git clone \
  --quiet \
  --depth 1 \
  --filter=blob:none \
  --sparse \
  --branch "${upstream_ref}" \
  -- "${upstream_repository}" \
  "${checkout_directory}"; then
  fail "Could not resolve upstream ref '${upstream_ref}' from '${upstream_repository}'."
fi

if ! upstream_commit="$(git -C "${checkout_directory}" rev-parse --verify HEAD)"; then
  fail "Could not resolve a commit for upstream ref '${upstream_ref}'."
fi

if [[ "$(git -C "${checkout_directory}" cat-file -t "${upstream_commit}:${upstream_docs_path}" 2>/dev/null || true)" != tree ]]; then
  fail "Expected documentation directory '${upstream_docs_path}' is absent from upstream commit '${upstream_commit}'."
fi

if ! git -C "${checkout_directory}" sparse-checkout set --no-cone -- "${upstream_docs_path}"; then
  fail "Could not materialize documentation directory '${upstream_docs_path}' from upstream commit '${upstream_commit}'."
fi

if [[ ! -d "${checkout_directory}/${upstream_docs_path}" ]]; then
  fail "Documentation directory '${upstream_docs_path}' was not materialized from upstream commit '${upstream_commit}'."
fi

if [[ -z "$(find "${checkout_directory}/${upstream_docs_path}" -mindepth 1 -print -quit)" ]]; then
  fail "Documentation directory '${upstream_docs_path}' is empty in upstream commit '${upstream_commit}'."
fi

attribution_files=()
while IFS= read -r attribution_file; do
  case "${attribution_file}" in
    LICENSE*|NOTICE*|COPYING*)
      if [[ "${attribution_file}" == */* ]] || [[ "$(git -C "${checkout_directory}" cat-file -t "${upstream_commit}:${attribution_file}" 2>/dev/null || true)" != blob ]]; then
        fail "Invalid upstream attribution file '${attribution_file}' in commit '${upstream_commit}'."
      fi
      attribution_files+=("${attribution_file}")
      ;;
  esac
done < <(git -C "${checkout_directory}" ls-tree --name-only "${upstream_commit}")

if [[ "${#attribution_files[@]}" -eq 0 ]]; then
  fail "No upstream LICENSE, NOTICE or COPYING file was found in commit '${upstream_commit}'."
fi

mkdir -p "${prepared_snapshot}"
cp -a \
  "${checkout_directory}/${upstream_docs_path}" \
  "${prepared_snapshot}/content"

for attribution_file in "${attribution_files[@]}"; do
  git -C "${checkout_directory}" show "${upstream_commit}:${attribution_file}" \
    > "${prepared_snapshot}/${attribution_file}"
done

printf '%s\n' "${upstream_ref}" > "${prepared_snapshot}/UPSTREAM_REF"
printf '%s\n' "${upstream_commit}" > "${prepared_snapshot}/UPSTREAM_COMMIT"

mkdir -p "${destination}"
destination_stage="$(mktemp -d "${destination}/.tabler-sync-stage.XXXXXX")"
backup_directory="$(mktemp -d "${destination}/.tabler-sync-backup.XXXXXX")"
cp -a "${prepared_snapshot}/." "${destination_stage}/"

while IFS= read -r -d '' attribution_file; do
  add_managed_item "${attribution_file}"
done < <(
  find "${destination}" \
    -maxdepth 1 \
    -type f \
    \( -iname 'LICENSE*' -o -iname 'NOTICE*' -o -iname 'COPYING*' \) \
    -printf '%f\0'
)

while IFS= read -r -d '' attribution_file; do
  add_managed_item "${attribution_file}"
done < <(
  find "${destination_stage}" \
    -maxdepth 1 \
    -type f \
    \( -iname 'LICENSE*' -o -iname 'NOTICE*' -o -iname 'COPYING*' \) \
    -printf '%f\0'
)

replacement_started=true

for item in "${managed_items[@]}"; do
  if [[ -e "${destination}/${item}" || -L "${destination}/${item}" ]]; then
    mv "${destination}/${item}" "${backup_directory}/${item}"
    backup_items+=("${item}")
  fi
done

mv "${destination_stage}/content" "${destination}/content"
installed_items+=(content)

for item in "${managed_items[@]}"; do
  if [[ "${item}" != content && -f "${destination_stage}/${item}" ]]; then
    mv "${destination_stage}/${item}" "${destination}/${item}"
    installed_items+=("${item}")
  fi
done

replacement_started=false
rm -rf "${destination_stage}" "${backup_directory}"
destination_stage=""
backup_directory=""

printf 'Tabler documentation synchronized from %s at %s\n' \
  "${upstream_ref}" \
  "${upstream_commit}"
