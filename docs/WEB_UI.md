# WEB UI — BeeUI

## Purpose and current status

BeeUI exposes an implemented server-rendered web shell and product-console integration. It combines validated configured pages, optional product adapter-backed pages, generic Tabler blocks, read-only views, artifact previews, guarded actions, page tabs, theme and locale behavior. The web layer is **presentation and transport**, not a product's execution authority.

This document describes implemented browser and route behavior. [API_CONTRACT.md](API_CONTRACT.md) owns JSON envelopes, [COMPONENTS.md](COMPONENTS.md) owns block schema, and [INTEGRATION.md](INTEGRATION.md) owns product embedding. Planned config-editor, remote-adapter, admin and future frontend APIs are not represented as implemented routes here.

## Public embedded application

```python
from beeui_module.web.app import create_beeui_app, mount_beeui

# Existing FastAPI-compatible product adapter implementation
ui_app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)

# Alternative: mount in an existing FastAPI host
# mount_beeui(parent_app, path="/ui", adapter=product_adapter,
#             config_path="config/beeui.yml")
```

`create_beeui_app` optionally accepts prepared runtime `settings`, a loaded `ui_config`, `config_path`, product metadata overrides and a request-scoped `navigation_visibility_resolver`. The resolver only hides or shows sidebar links; it does **not** authorize a URL or product resource. Adapter and product metadata are stored in app state.

`mount_beeui` verifies a safe, non-root mount path and rejects incompatible route collisions. Internal links and static paths are adapted to the approved prefix. A product must not replace BeeUI system routes through its configured page list.

Without an adapter, the app retains its supported configured/demo mode. A remote HTTP product-backend service is not implied.

## Implemented browser routes

| HTML/browser route                                            | Behavior                                                 |
| ------------------------------------------------------------- | -------------------------------------------------------- |
| `GET /`                                                       | Demo/configured dashboard or adapter dashboard.          |
| `GET /runs`                                                   | Product run list where an adapter is available.          |
| `GET /runs/{run_id}`                                          | Validated run detail and supported generic sections.     |
| `GET /venues/{venue_id}`                                      | Optional venue detail/read-model where supported.        |
| `GET /runs/{run_id}/artifacts`                                | Allowlisted artifact list (adapter required).            |
| `GET /runs/{run_id}/artifacts/{artifact_id}`                  | Bounded escaped artifact preview (adapter required).     |
| `GET /<configured-page-path>`                                 | Page with `route.mode: configured`.                      |
| `GET /<adapter-page-path>`                                    | Page with `route.mode: adapter`, invoking `get_page`.    |
| `GET /components` and `/components/{category}`                | Component catalog and established categories.            |
| `GET /health`                                                 | Health response.                                         |
| `GET /static/...`                                             | Package-local CSS, JS, Tabler and other approved assets. |
| `GET /login`, `POST /login`, `POST /logout`, `GET /auth/csrf` | Built-in authentication/session browser routes.          |

Catalog categories currently include `interface`, `forms`, `layout`, `extra` and `plugins`. Generic read-only product APIs include `/api/dashboard`, `/api/runs`, `/api/runs/{run_id}` and optional venue dashboard. Artifact JSON API endpoints are separate, as described in [API_CONTRACT.md](API_CONTRACT.md).

Protected POST transport routes: `/api/config/preview`, `/api/config/apply`, `/api/actions/preview`, `/api/actions/execute`. Each requires the appropriate feature gate and callback; exposing a transport route does not imply a working generic configuration editor or authorized product action.

The embedding host can register its own product-specific routes, such as BeeAgent's BeeScan Case or status API. Those routes are **not** generic BeeUI APIs and are governed by the host's authorization contract.

## Page ownership and navigation

Page definitions belong to `config/schema.yml` or a product-specific `config/beeui.yml`. `pages[].route.mode` chooses `configured`, `adapter` or `metadata`. A `metadata` entry contributes UI metadata but does not register a new HTTP route. System-owned prefixes remain reserved.

For adapter pages, BeeUI calls `get_page(page_id, query)` and renders the returned normalized `layout[]` through the canonical `page.html`. All query values are untrusted strings; the product must validate domain parameters, such as Case IDs, date ranges or approved target selection.

### Page tabs

Tab definitions are URL-driven, for example:

```yaml
pages:
  - id: investigations
    path: /investigations
    route:
      mode: adapter
    title:
      en: Investigations
      ru: Investigations
    tabs:
      variant: fill_icons
      progressive: true
      surface: separated
      active_param: tab
      items:
        - id: investigation
          title: { en: Investigation, ru: Investigation }
          href: /investigations?tab=investigation
          icon: messages
        - id: results
          title: { en: Results, ru: Results }
          href: /investigations?tab=results
          icon: report
    blocks: []
```

This is an illustrative page name, not a new BeeUI built-in route. Valid variants include the existing allowlisted Tabler tab mappings (`default`, `reverse`, `fill`, `icons`, `fill_icons`, `compact_fill_icons`, `dropdown` where supported by the page/config model).

`surface: separated` renders tabs in their own Tabler card with page blocks below. With `progressive: true`, same-origin GET fetches replace only the matching tab surface, maintain browser history, cancel stale responses and reinitialize affected components. Back/Forward works. If JavaScript is disabled or a fetch fails, the canonical URL remains usable through ordinary navigation.

Locale and bounded query state may be preserved by the built-in tab/link handling; the product remains responsible for validating selected IDs and deciding which query parameters are meaningful.

## Layout and components

The canonical page template renders `layout[]` through generic block normalization. Standard blocks include cards, KPI grids, statuses, lists, charts, `data_table`, `filter_form`, bounded groups, detail sections and `chat_workspace`. Unknown/malformed optional blocks use explicit degraded/empty presentation according to the contract; they must not return raw data or raise an unhandled browser error.

- Every block follows allowlisted width and visual token mappings.
- Links are internal-only and adjusted for a validated mount prefix.
- Chart and date-picker assets are loaded only when a page needs them, from package-local files.
- Product-provided text is escaped. No adapter may supply arbitrary HTML, JavaScript or CSS.
- Different pages may use standard card and table primitives without implementing a new product-side HTML template.

See [COMPONENTS.md](COMPONENTS.md) for exact fields, bounds and compatibility rules.

## Product console and generic detail pages

An adapter-backed dashboard, run list or run detail is a server-rendered view over read-only product data. Generic run headers, statuses, events and artifacts are rendered only when the product supplies them. Missing metrics must display as unavailable instead of as a false zero.

`render_beeui_detail_page()` is a Python helper for a normalized detail page with `key_value`, `text`, `table` and `links` sections. Its `back_href` and section links are safe internal paths. Product-specific detail routes may call this helper through their own adapter/host integration; it does not create a new public JSON endpoint.

## Artifact browser

The product adapter controls whether an operator can list and read a given artifact. BeeUI validates run/artifact references, obtains allowlisted content through adapter callbacks, redacts sensitive values and displays bounded previews.

- JSON and JSONL are parsed within declared size/row limits; malformed lines create warnings.
- Text content is truncated/bounded and escaped.
- Unsupported/binary/oversized sources produce metadata-only output.
- Direct filesystem paths, traversal, symlink escapes and raw product evidence are not exposed by a public URL.
- Listing or previewing never repairs the underlying product artifact.

See [API_CONTRACT.md](API_CONTRACT.md) for the distinct artifact JSON envelope and preview metadata.

## Operator action UI

### Transport and authority

Action-enabled controls use the protected generic `/api/actions/preview` and `/api/actions/execute` transport. BeeUI enforces configured feature eligibility, session/role/CSRF and bounded payloads. The product owns action IDs, permitted arguments, current resource ownership, approval, conflict handling and audit.

The default bounded table action follows preview, separate confirmation and execute. Explicit `direct_execute` performs the same protected execution check without a preview when the product action contract permits it. Product-supplied URLs cannot be used as arbitrary action endpoints. Rejected actions must remain safe without unintended retries or hidden writes.

### Chat workspace

`chat_workspace` is a generic adapter-backed Case/conversation view with bounded history, text messages, context, composer, optional compact radio/target/menu layout and read-only polling. It is not a full AI conversation backend.

The compact composer has a Task textarea, optional product-supported Target text group, mode/selection radios, a deliberately disabled placeholder menu and an accessible icon-only submit control. Optional `submit_on_enter` supports Enter while preserving Shift+Enter and IME input. An enabled button is not execution permission; the product must authorize before beginning a real run.

Live status polling is same-origin, capped, cancels on exit, uses escaped text DOM updates, preserves message identity and reloads the canonical page at completion to obtain current authorized actions. Polling must never initiate a target request or mutate Case files. Details of the exact normalized payload are in [COMPONENTS.md](COMPONENTS.md).

## Locale

Built-in BeeUI labels use the configured supported locale set (currently English and Russian in the default catalogue). Resolution follows valid `?lang=` query, valid `beeui_lang` cookie, then configured default. Invalid values do not override the allowlist. Product labels and business vocabulary are supplied by the product adapter.

The language switcher preserves safe current navigation state where supported. The cookie is a presentation preference, not a session token or a basis for access control.

## Theme

The effective theme is applied through `html[data-bs-theme]`. Explicit system/light/dark preferences are validated and stored locally in the browser; `system` resolves through `prefers-color-scheme`. ApexCharts follows the current effective theme. See [THEME.md](THEME.md).

## Authentication and framing

`auth.enabled: false` is explicit local/demo behavior. When enabled, BeeUI uses signed sessions with `viewer`, `operator` and `admin` roles and centralized CSRF protection on guarded POST routes. Secure cookie attributes and session age are controlled by validated runtime settings; secrets stay out of templates and logs.

By default, responses deny framing (`X-Frame-Options: DENY`). A validated nonempty exact-origin `security.frame_ancestors` list enables the documented CSP embedding policy. Browser UI access does not establish product resource ownership; the host must enforce that boundary.

## Read-only behavior and response safety

GET routes, filters, tabs, artifact previews and status refresh must not perform product writes, external scans, provider requests or silent storage repair. Read-only responses use appropriate non-cacheable/readonly headers; product hosts may add their own. API and HTML errors are normalized, with no traceback or raw secret output.

A new feature affecting the browser must be tested against session and CSRF refusal, malformed inputs, internal links, route-prefix mounts, RU/EN and light/dark when relevant, mobile layout, package-installed assets and real host execution when product actions are involved.

## Not implemented by this contract

A full general-purpose configuration editor, independent `/admin` service and diagnostics API, arbitrary product remote adapter, full frontend API v1, no-code dashboard builder, unrestricted file manager and standalone chat/LLM runtime are not implied by the generic shell or transport methods. Their future designs must not be presented as working routes.

## Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — boundaries and module ownership.
- [INTEGRATION.md](INTEGRATION.md) — app factory, embedding and product adapters.
- [COMPONENTS.md](COMPONENTS.md) — block and interaction schemas.
- [API_CONTRACT.md](API_CONTRACT.md) — read/action/artifact API envelopes.
- [THEME.md](THEME.md) — theme behavior.
- [SECURITY.md](SECURITY.md) — standing security rules.
