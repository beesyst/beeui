# INTEGRATION — BeeUI with Bee products

## Purpose

This guide describes the implemented embedded interface between BeeUI and a product. BeeUI is the reusable UI transport and renderer; the product owns domain state, read-models, resource authorization, evidence, external actions and audit.

**BeeUI renders. The product decides.** Use existing adapter, route and page contracts before adding new integration layers.

## Implemented integration modes

### Embedded app factory

```python
from beeui_module.web.app import create_beeui_app

app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

The product supplies a concrete adapter instance that implements the existing public protocol. The app factory validates the adapter, loads the product's UI configuration and registers the canonical BeeUI shell, system routes, configured pages and authorized product presentation routes.

Optional arguments include prepared runtime `settings`, a loaded `ui_config`, and a request-scoped `navigation_visibility_resolver`. The resolver affects navigation visibility only and must not be used as an authorization decision.

### Mount inside a product FastAPI app

```python
from fastapi import FastAPI
from beeui_module.web.app import mount_beeui

parent_app = FastAPI()

mount_beeui(
    parent_app,
    path="/ui",
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

The mount path is explicitly validated and must be a non-root safe path. The mount helper checks parent-route collisions. BeeUI-prefixed routes, safe internal links, tab URLs, static assets and artifact URLs must remain valid under `/ui` or another approved prefix.

### Standalone/demo

`create_beeui_app()` without an adapter supports the configured/demo shell. It is not a generic remote product service. Service-to-service HTTP adapters, CORS bridges, deployment discovery and their security model are future work, not part of this implemented integration contract.

## Product adapter protocol

The canonical `ProductUiAdapter` declaration is `src/beeui_module/adapters/base.py`; adapters return `AdapterResult` or `AdapterErrorResult` from `src/beeui_module/adapters/envelopes.py`.

| Protocol method                                           | Product responsibility                                               |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `get_dashboard()`                                         | Prepare a read-only dashboard model.                                 |
| `list_runs()`                                             | Return authorized run summaries.                                     |
| `get_run(run_id)`                                         | Validate access and return one run's read-model.                     |
| `list_artifacts(run_id)`                                  | Return only authorized artifact references.                          |
| `read_artifact(run_id, artifact_id)`                      | Resolve an allowlisted artifact and return bounded content/metadata. |
| `get_config_read_model()`                                 | Return an allowed, redacted configuration read-model if supported.   |
| `validate_config_candidate(candidate)`                    | Apply product rules to a bounded candidate; no generic BeeUI policy. |
| `apply_config_candidate(candidate, expected_hash, actor)` | Product-owned mutation, stale-state guard and audit.                 |
| `list_actions()`                                          | Declare explicitly permitted bounded actions.                        |
| `preview_action(action_id, payload)`                      | Product-owned non-mutating preview.                                  |
| `execute_action(action_id, payload, actor)`               | Product-owned execution and audit after transport checks.            |

`ProductUiAdapterBase` also provides optional `get_page(page_id, query)` and `get_venue_dashboard(venue_id)` hooks with unavailable defaults. Some base-class methods intentionally raise unavailable when a product does not support them. The embedding product, not BeeUI, decides which optional features are enabled.

The browser never chooses an arbitrary adapter method, executable destination or product policy. Exceptions and malformed results are normalized to bounded errors and safe degraded states.

## Product UI configuration

The product owns `config/beeui.yml`; it describes presentation, not runtime authority. Example:

```yaml
app:
  title: { en: Example Console, ru: Example Console }
  product: example
  locale:
    default: en
    available: [en, ru]
  theme:
    mode: system
  layout:
    type: vertical
    container: xl

navigation:
  - title: { en: Investigations, ru: Investigations }
    path: /investigations
    icon: shield

pages:
  - id: investigations
    path: /investigations
    route:
      mode: adapter
    title: { en: Investigations, ru: Investigations }
    tabs:
      variant: fill_icons
      progressive: true
      surface: separated
      active_param: tab
      items:
        - id: overview
          title: { en: Overview, ru: Overview }
          href: /investigations?tab=overview
          icon: dashboard
        - id: results
          title: { en: Results, ru: Results }
          href: /investigations?tab=results
          icon: report
    blocks: []
```

This illustrative config is not a built-in product page. Validate all page IDs, internal hrefs and icons through the established BeeUI config schema. `configured` pages render declared UI blocks, `adapter` pages use `get_page`, and `metadata` pages do not register a new route. BeeUI system paths are reserved.

## Adapter-backed page lifecycle

```text
GET /investigations?tab=results
  -> BeeUI verifies route ownership and validates transport/query shape
  -> ProductUiAdapter.get_page("investigations", query)
  -> product checks actor, resource IDs and owned data
  -> product returns AdapterResult containing layout[]
  -> BeeUI normalizes blocks, links, tabs and local assets
  -> escaped Jinja/Tabler page
```

A page request and read-only polling must not mutate product artifacts, launch a scan or execute a provider. Where the host must bind an authenticated principal to its adapter, use an explicit trusted host-side context; never trust a user-supplied `principal_id` as proof of identity.

Product adapter data may contain generic `layout[]` blocks, including `chart`, `data_table`, `filter_form`, `chat_workspace` and ordinary KPI/cards. BeeUI neither understands the product's Case/lead/severity meaning nor invents unknown values.

## Protected product actions

The UI invokes only BeeUI's existing feature-gated and CSRF-protected transport:

- `POST /api/actions/preview`
- `POST /api/actions/execute`
- `POST /api/config/preview`
- `POST /api/config/apply`

For auth-enabled installations, session, sufficient role and CSRF are validated before product callbacks. A product action may be presented only through a bounded action ID, allowlisted fields/args and supported UI behavior. It must be validated again by the product on execution, including resource ownership, current approval, rate/budget limits, concurrency and audit.

A button, a successful preview or a client-side target check is not proof that the product permits the operation. Do not move external provider calls or credentials into BeeUI.

## Product integration examples

### BeeAgent / ROP / BeeScan

BeeAgent supplies its own `BeeAgentUiAdapter` and `config/beeui.yml`. ROP and BeeScan use the canonical BeeUI Tabler shell, URL-driven tabs, generic blocks, controlled read-models, product-owned security checks and protected actions.

The `chat_workspace` presents BeeScan investigation history, authenticated status, results and bounded composer data. BeeAgent owns Target/Scope/Approval, Case identity and signatures, scan execution, artifacts, DAST permission and Resume validation. BeeUI does not perform target requests or validate scanner evidence.

### BeeCap and other products

The fixture adapter under `src/beeui_module/adapters/beecap.py` is a generic/reference integration for testing BeeUI presentation; it must not be mistaken for a production BeeCap integration. A real product adapter belongs under that product's `interfaces/ui` or equivalent boundary. Its domain calculations, storage paths and execution logic must not be copied into BeeUI core.

## Locale, theme, route prefix and dynamic content

- Locale selection uses valid `?lang=`, an allowlisted `beeui_lang` cookie and configured default. The product owns translations of its own labels.
- Theme is an allowlisted browser presentation preference; see [THEME.md](THEME.md).
- Internal URLs are validated, prefixed for the configured mount and encoded before entering HTML. No untrusted external scheme, protocol-relative URL or traversal path.
- Progressive tabs, live tables and chat refresh must preserve canonical GET fallback, abort stale requests and reinitialize only owned generic components.
- Layout text must be escaped. Safe DOM updates must not interpolate product data into executable markup.

## Verification checklist

Before merging an integration change, verify real product routes, authenticated and unauthorized views, query validation, scoped artifact access, protected action refusal, read-only GET immutability, route-prefix support, RU/EN and light/dark presentation, responsive layout and installed-wheel CSS/JS/templates. If external target execution is relevant, run the embedding product's actual governed E2E rather than claiming that BeeUI unit tests prove it.

## Unsupported integration shortcuts

Do not create a duplicate product web server, custom product Jinja/CSS/JS copy of a generic component, arbitrary remote adapter, direct file browser, product callback derived from an href, or a second authorization/configuration authority merely to connect a product to BeeUI.

## Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — ownership and flow.
- [API_CONTRACT.md](API_CONTRACT.md) — envelopes and protected routes.
- [COMPONENTS.md](COMPONENTS.md) — normalized presentation blocks.
- [WEB_UI.md](WEB_UI.md) — browser behavior.
- [SDLC.md](SDLC.md), [SECURITY.md](SECURITY.md) — delivery/security gates.
