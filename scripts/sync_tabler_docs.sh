#!/usr/bin/env bash

set -euo pipefail

repo_root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.."
  pwd
)"

destination="${repo_root}/docs/vendor/tabler"
upstream_repository="https://github.com/tabler/tabler.git"
upstream_ref="${TABLER_REF:-dev}"

temporary_directory="$(mktemp -d)"

cleanup() {
  rm -rf "${temporary_directory}"
}

trap cleanup EXIT

git clone \
  --quiet \
  --depth 1 \
  --filter=blob:none \
  --sparse \
  --branch "${upstream_ref}" \
  "${upstream_repository}" \
  "${temporary_directory}/tabler"

git -C "${temporary_directory}/tabler" \
  sparse-checkout set docs/content

upstream_commit="$(
  git -C "${temporary_directory}/tabler" rev-parse HEAD
)"

rm -rf "${destination}/content"
mkdir -p "${destination}"

cp -a \
  "${temporary_directory}/tabler/docs/content" \
  "${destination}/content"

find "${destination}" \
  -maxdepth 1 \
  -type f \
  \( \
    -iname "LICENSE*" \
    -o -iname "NOTICE*" \
    -o -iname "COPYING*" \
  \) \
  -delete

find "${temporary_directory}/tabler" \
  -maxdepth 1 \
  -type f \
  \( \
    -iname "LICENSE*" \
    -o -iname "NOTICE*" \
    -o -iname "COPYING*" \
  \) \
  -exec cp -p {} "${destination}/" \;

printf '%s\n' "${upstream_ref}" \
  > "${destination}/UPSTREAM_REF"

printf '%s\n' "${upstream_commit}" \
  > "${destination}/UPSTREAM_COMMIT"

printf 'Tabler documentation synchronized from %s at %s\n' \
  "${upstream_ref}" \
  "${upstream_commit}"