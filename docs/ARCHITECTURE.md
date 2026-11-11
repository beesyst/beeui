# ARCHITECTURE — BeeUI

## Purpose

BeeUI is the reusable server-rendered presentation layer for Bee products. It combines FastAPI, Jinja2, a locally packaged Tabler UI, validated page definitions, product adapters, reusable layout blocks, safe artifact previews, and protected operator-action transport.

**BeeUI renders. The product decides.** BeeUI does not execute security scans, operate brokers, authorize a product target, classify business events, or own a product's run/Case state.

This document describes implemented ownership boundaries and architecture. See [SPEC.md](SPEC.md) for requirements, [INTEGRATION.md](INTEGRATION.md) for embedding, [COMPONENTS.md](COMPONENTS.md) for presentation schemas, and [SECURITY.md](SECURITY.md) for normative controls.

## Ownership

| BeeUI owns                                                                    | The embedding product owns                                                      |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| HTML/JSON web surface, Tabler shell, templates, local assets                  | Domain-specific read-models, Case/run meanings and business rules               |
| Validated UI configuration, page registration, navigation and URL-driven tabs | Its own `config/beeui.yml` and decisions about visible pages                    |
| Safe generic block rendering, escaping, links and degraded states             | Truthful values, bounded evidence and product-specific labels                   |
| Session, role and CSRF mechanisms for BeeUI-controlled routes                 | Domain permissions, approved scopes, resource ownership and execution authority |
| Bounded protected action transport                                            | The action catalog, validation, execution, rejection and audit                  |
| Bounded generic artifact previews and redaction                               | Artifact allowlists, identifiers, confidential content and access decisions     |
| Locale, theme, progressive navigation and route-prefix handling               | External systems, credentials, providers, budgets and product lifecycle         |

An authenticated UI session does **not** independently authorize a product action. A visible action or a well-formed adapter response does not grant access to the underlying resource.

## Runtime flow

```text
Browser
  -> BeeUI FastAPI routes / authentication / CSRF
  -> configured page or ProductUiAdapter.get_page(page_id, query)
  -> product-owned read-model
  -> validated layout[] and safe internal links
  -> BeeUI Jinja2 / package-local Tabler
  -> escaped HTML or normalized JSON

Protected POST
  -> BeeUI session / role / CSRF / request bounds
  -> ProductUiAdapter preview/execute/apply callback
  -> product-specific policy, mutation and audit
  -> normalized response
```

All normal page, inspection and polling GETs are read-only with respect to product state and external targets. Product mutation belongs behind explicit protected POST callbacks; GET handlers must not repair or create product artifacts as a side effect.

## Configuration sources

- `config/settings.yml`: BeeUI runtime settings (host, logging, storage, authentication, security, feature gates and demo metadata).
- `config/schema.yml`: declarative demo/configured UI.
- `<product>/config/beeui.yml`: product navigation, page ownership, tabs, layout, theme and permitted view metadata.
- `<product>/config/settings.yml`: product runtime settings and authorization; never relocated into BeeUI.

Invalid required UI configuration fails at load time. Malformed optional product presentation data is normalized or degraded according to the owning block contract, without exposing stack traces. The browser never becomes a secondary configuration authority.

## Integration modes

### Embedded (implemented and preferred)

```python
from beeui_module.web.app import create_beeui_app

app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

The product can also embed BeeUI within an existing FastAPI application through `mount_beeui(parent, path="/ui", ...)`. BeeUI validates the mount path and route collisions and prefixes internal links. No second service, remote adapter or CORS bridge is necessary.

### Standalone/demo (implemented)

Calling `create_beeui_app()` without a product adapter supports the local demo/configured experience. It is **not** a supported arbitrary remote-product backend integration. A separate service-to-service HTTP adapter is future scope and must have an explicit security contract before implementation.

## Pages and route ownership

`pages[].route.mode` selects a page's owner:

| Mode         | Behavior                                                                          |
| ------------ | --------------------------------------------------------------------------------- |
| `configured` | BeeUI registers the route and renders configured/schema blocks.                   |
| `adapter`    | BeeUI registers the route and obtains its `layout[]` from the product adapter.    |
| `metadata`   | Page metadata contributes navigation/titles; no new concrete route is registered. |

System-owned paths (including `/api`, `/auth`, `/static`, `/components`, and `/health`) cannot be replaced by product pages. Links and route parameters are validated and prefixed through BeeUI's shared helpers.

Page tabs are ordinary URL-driven links. Optional progressive enhancement replaces a bounded same-origin tab surface, retains canonical GET navigation and falls back to a full-page navigation on failure. BeeAgent ROP and BeeScan use the same generic tab contract.

## Adapter and component layers

The canonical protocol lives in `src/beeui_module/adapters/base.py`. `ProductUiAdapter` defines dashboard, runs, run detail, artifact list/read, configuration read-model and action callback signatures. `ProductUiAdapterBase` also provides optional `get_page` and venue-page hooks; unsupported optional operations explicitly report unavailable. See [INTEGRATION.md](INTEGRATION.md) for the method inventory and envelopes.

Presentation components live in `src/beeui_module/blocks/` and are rendered by generic Jinja templates under `src/beeui_module/web/templates/`. Source code, not a roadmap entry, establishes whether a block or field is implemented.

The generic `chat_workspace` is a bounded conversation/history/composer/context presentation component, not a messaging service, agent runtime or independent chat backend. In the BeeScan integration, a protected BeeAgent action creates or resumes the authorized Case; BeeUI only presents authenticated facts returned by the BeeAgent adapter.

## Source layout

```text
src/beeui_module/
  adapters/       Public protocol, envelopes and error normalization
  artifacts/      Bounded previews and redaction
  auth/           Session, roles and CSRF
  blocks/         Generic layout normalization and renderers
  cli/            Doctor, routes and web entrypoints
  core/           Runtime utilities and settings
  data/           Controlled configured/demo sources
  pages/          Page definitions, ownership, navigation and tabs
  web/
    app.py        App factory, embedding and protected routes
    templates/    Canonical Jinja2 page/component templates
    static/       Package-local styles, scripts and upstream assets
```

The actual file tree and `pyproject.toml` are authoritative for packaging details.

## Non-negotiable invariants

- Keep product-specific policy, execution and artifacts behind the product adapter.
- Keep required config validation fail-fast, with explicit degraded behavior for malformed optional product presentation data.
- Escape untrusted output; never accept raw HTML, CSS, JavaScript or arbitrary action destinations from an adapter.
- Validate internal URLs, identifiers, fields, input bounds, route prefixes and artifact references.
- Enforce session/role/CSRF before invoking protected product callbacks; product authorization is still required afterward.
- Serve runtime CSS/JS/fonts only from the installed package. `docs/vendor/tabler/` is a reference documentation snapshot, **not** the production asset bundle.
- Reuse established protocols and Tabler primitives before introducing new abstraction layers.

For delivery and review requirements, consult [SDLC.md](SDLC.md) and [SECURITY.md](SECURITY.md).
