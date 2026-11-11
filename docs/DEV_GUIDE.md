# DEVELOPER GUIDE — BeeUI

## Purpose

This is the practical local development and verification guide for the reusable BeeUI package. For architecture and contracts see [ARCHITECTURE.md](ARCHITECTURE.md), [SPEC.md](SPEC.md), [INTEGRATION.md](INTEGRATION.md) and [COMPONENTS.md](COMPONENTS.md). For delivery gates use [SDLC.md](SDLC.md) and [SECURITY.md](SECURITY.md).

## Requirements and repository boundaries

- Python 3.14 or newer.
- `uv`, Git and a supported local browser for UI verification.
- An existing Bee product repository only when testing an embedded integration.

BeeUI and each product stay in separate repositories; a multi-root editor workspace does not merge their dependency or authorization contracts.

## Install, start and inspect

From the BeeUI repository root:

```bash
./start.sh doctor
./start.sh version
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Calling `./start.sh` without arguments runs the doctor. The launcher uses `uv sync --frozen --group dev` and `uv run --frozen --group dev`; a normal start must not rewrite the lockfile.

Equivalent direct commands:

```bash
uv sync --frozen --group dev
uv run --frozen --group dev python config/start.py doctor
uv run --frozen --group dev python config/start.py web --host 127.0.0.1 --port 8780
```

Inspect `config/settings.yml` for the configured demo host/port, storage, auth, security and feature gates. The demo starts with `auth.enabled: false`; this is not a production authorization policy.

## Tests and build

```bash
uv run --frozen --group dev pytest -q
uv run --frozen --group dev pytest -q tests/test_product_console.py
uv build --wheel
```

For changes affecting routes, action transport, rendering or browser behavior, run the relevant real HTTP/browser tests in addition to pytest. For templates, CSS/JS, icons or package data, inspect the installed wheel and check that its local asset URLs load without CDN requests.

Do not use `uv lock --check` as a routine non-dependency verification step. For a feature with no dependency declarations changed, do not inspect, regenerate or stage `uv.lock` for unrelated cleanup; verify that it is absent from the final changed-file inventory.

## Dependencies

`pyproject.toml` defines supported distributions and groups; `uv.lock` provides reproducible resolution. Change these only under a task that explicitly authorizes dependency work.

```bash
# Approved runtime dependency change
uv add PACKAGE

# Approved development dependency change
uv add --group dev PACKAGE

# Approved removal
uv remove PACKAGE

# Approved targeted lock upgrade
uv lock --upgrade-package PACKAGE
```

Review the exact dependency and supply-chain impact, commit `pyproject.toml` and/or `uv.lock` as applicable, and rerun appropriate tests. Do not mix bulk upgrades into an unrelated UI feature.

## Configuration ownership

| File                            | Responsibility                                                               |
| ------------------------------- | ---------------------------------------------------------------------------- |
| `config/settings.yml`           | BeeUI demo/runtime host, storage, logging, auth, security and feature flags. |
| `config/schema.yml`             | Declarative demo/configured pages and blocks.                                |
| `<product>/config/beeui.yml`    | Product navigation, page definitions, tabs, theme and layout.                |
| `<product>/config/settings.yml` | Product policy, credentials, external connections and execution permissions. |

Required UI configuration errors should fail early. Malformed optional adapter data should degrade safely under its block contract. Do not put arbitrary Python/JS, secrets, product execution controls or new authorization policy in `beeui.yml`.

## Embedded integration

A product normally calls:

```python
from beeui_module.web.app import create_beeui_app

ui_app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

For a preexisting FastAPI host, use `mount_beeui(parent, path="/ui", ...)`. See [INTEGRATION.md](INTEGRATION.md) for adapter signatures, response envelopes and route prefix behavior.

For coordinated development only, a consumer may temporarily point `uv` at a sibling editable BeeUI checkout. Before releasing the consumer, replace that source with an actual published BeeUI distribution, refresh the consumer's lockfile and verify installed-package behavior. Never assume a sibling directory exists on CI.

## Adding a page or component

1. Check whether an existing `layout[]` block, Tabler primitive or product `get_page` read-model already solves the problem.
2. Put product semantics in the product adapter; modify BeeUI only for reusable presentation behavior.
3. Choose explicit route ownership (`configured`, `adapter`, `metadata`) in `config/beeui.yml`.
4. Normalize types, collection bounds, links and optional fallback behavior in the owning block renderer.
5. Use escaped Jinja templates, local Tabler assets and safe DOM updates. Do not paste full upstream demo pages.
6. Add public-contract and negative tests, plus real browser verification if interaction changed.
7. Document the new contract in [COMPONENTS.md](COMPONENTS.md), HTTP implications in [WEB_UI.md](WEB_UI.md) or [API_CONTRACT.md](API_CONTRACT.md), and embedding changes in [INTEGRATION.md](INTEGRATION.md).

## Tabler reference docs versus runtime assets

The upstream documentation reference snapshot lives at `docs/vendor/tabler/`. It is not shipped to the browser as the runtime Tabler bundle.

```bash
# Update the reference snapshot locally (no automatic commit)
./scripts/sync_tabler_docs.sh

# Inspect only documentation changes
git status --short -- docs/vendor/tabler
```

The script updates the upstream commit marker, snapshot and attribution. Documentation updates are normally a separate `docs(tabler)` change; do not accidentally stage them with UI feature code. The packaged runtime assets live under `src/beeui_module/web/static/vendor/`, and changing them requires a separate compatibility/license/packaging review.

The repository also provides `.github/workflows/sync-tabler-docs.yml` for scheduled/manual snapshot synchronization through an isolated PR.

## Common failure modes

| Symptom                                            | Check                                                                                                         |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Unexpected dependency changes after normal startup | Confirm `--frozen`, inspect changed-file scope; do not conceal lock drift.                                    |
| Product page does not appear                       | Check `pages[].route.mode`, route ownership, adapter implementation and route collision rules.                |
| URL works locally but fails behind a mount         | Validate `route_prefix`, mounted path and use shared internal-link helpers.                                   |
| Action returns 401/403                             | Check session, role, CSRF, feature gate and product-specific authority separately.                            |
| An artifact link fails                             | Confirm product-owned allowlist, valid IDs, content type and access scope.                                    |
| New CSS/JS works in editable checkout only         | Build/install the wheel and inspect static asset packaging and cache version.                                 |
| A new Tabler example renders incorrectly           | Confirm the class/JS is supported by the **installed runtime assets**, not only by the updated docs snapshot. |
| UI test is green but Case handling fails           | Run the embedding host's real integration/E2E and negative authorization checks.                              |

## Scope and release discipline

Follow the approved Issue and change-level verification in [SDLC.md](SDLC.md). Keep an unrelated vendor/docs refresh out of a feature PR. Use the existing Release Please workflow rather than bumping the BeeUI version by hand in an ordinary feature branch. Record test and packaging evidence in the PR template, including any limitations or unrun checks.
