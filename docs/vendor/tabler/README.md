# Tabler upstream documentation

This directory contains an automatically synchronized read-only snapshot of
the official Tabler documentation.

## Source

- Repository: `tabler/tabler`
- Source path: `docs`
- Source ref: see `UPSTREAM_REF`
- Resolved commit: see `UPSTREAM_COMMIT`

## Update

Run:

```bash
./scripts/sync_tabler_docs.sh
```

The directory is also synchronized by:

```text
.github/workflows/sync-tabler-docs.yml
```

## Rules

* Do not edit files under `content/` manually.
* Do not treat this directory as the BeeUI architecture source of truth.
* BeeUI contracts remain defined by BeeUI documentation, configuration,
  implementation and tests.
* Check that documented Tabler behavior is compatible with the Tabler assets
  actually bundled by BeeUI.
* Preserve the upstream license and attribution files.
