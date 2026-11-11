# SPECIFICATION — BeeUI

## Purpose and scope

BeeUI is the reusable FastAPI/Jinja2/Tabler presentation and operator-interface layer for Bee products. It removes duplicate web shells, basic navigation, generic tables/charts/cards, artifact browsing and bounded action UI from individual products while preserving product-specific decision and execution boundaries.

**Design rule:** BeeUI renders; the product decides.

This specification covers existing public behavior and architectural constraints. Planned increments and their status belong in [ROADMAP.md](ROADMAP.md); this file does not turn planned functionality into a supported API.

## Terms

| Term               | Meaning                                                                               |
| ------------------ | ------------------------------------------------------------------------------------- |
| Distribution       | Installable Python package `beeui`.                                                   |
| Import package     | `beeui_module`.                                                                       |
| Product            | A separately maintained Bee application, such as BeeAgent or BeeCap.                  |
| Product adapter    | Product-owned implementation of BeeUI's `ProductUiAdapter` protocol.                  |
| Read-model         | Bounded normalized data prepared for safe presentation.                               |
| `layout[]`         | Adapter-provided list of typed, generic presentation blocks.                          |
| Configured page    | Page rendered from validated declarative UI configuration.                            |
| Adapter page       | Page whose view is returned by `get_page(page_id, query)`.                            |
| Artifact reference | An allowlisted identifier resolved by a product adapter; never a raw filesystem path. |
| Bounded action     | Explicit product action exposed through the protected BeeUI transport.                |
| Case               | A product-level investigation artifact; BeeUI does not define its semantics.          |

## Technology and distribution

- Python 3.14 or newer; FastAPI and Jinja2 server rendering.
- Official Tabler CSS/JS, Tabler icons and selected chart/date assets shipped locally inside the Python wheel.
- Configuration via validated YAML and package-local templates; no CDN dependency for core UI behavior.
- Locked dependencies through `pyproject.toml` and `uv.lock`.
- Browser enhancement is progressive; essential navigation remains functional as ordinary HTTP links.

Refer to `pyproject.toml` for actual pinned dependency versions and supported package contents rather than copying version numbers into this specification.

## Implemented product-facing capabilities

### Web shell and pages

- A canonical sidebar/layout, localized titles/navigation, theme selection and reusable templates.
- Configured/schema pages and product adapter-backed pages with explicit route ownership.
- URL-driven page tabs supporting `surface: separated`, `progressive: true` and `active_param`.
- Safe internal links and route-prefix/embedded mount handling.
- Product-driven navigation visibility as presentation-only filtering, never a route authorization substitute.

### Generic blocks and detail presentation

- Responsive cards, KPI/stat grids, statuses, lists, links, operator snapshots, groups, tables and charts.
- Advanced `data_table` with optional GET filters, columns, sorting, pagination, bounded row actions and progressive replacement.
- Bounded `filter_form`, generic detail sections and safe chart presentation.
- Generic `chat_workspace` for product-owned history/messages/context and a protected composer, including a compact Tabler variant.

Only the normalized fields declared in [COMPONENTS.md](COMPONENTS.md) and validated by current implementation are supported. An adapter cannot inject its own arbitrary markup or JavaScript.

### Product console and artifacts

- Adapter-backed dashboard/run list/run details and their read-only JSON endpoints.
- Allowlisted product artifact list and bounded JSON/JSONL/text previews; unsupported binary artifacts are metadata-only.
- Explicit redaction, safe IDs/paths, malformed-data handling and read-only semantics.
- Generic detail page renderer for approved key/value, text, table and internal-link sections.

### Protected actions and configuration transport

- Browser session, role and CSRF protection for BeeUI-controlled routes.
- Feature-gated POST transport for config preview/apply and action preview/execute.
- Product-owned allowlists, business validation, execution and audit; BeeUI provides transport, not authority.
- Default preview/confirm/execute UX for opt-in bounded table actions and explicit direct-execute variants where allowed by the contract.

A generic configuration editor, arbitrary product file browser or automatic authorization of product actions is **not** implied by these endpoints.

## Configuration contracts

| Source                     | Owns                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------- |
| `config/settings.yml`      | BeeUI host, auth, storage, security and feature gates.                             |
| `config/schema.yml`        | Configured/demo layout and page definitions.                                       |
| Product `config/beeui.yml` | Product navigation, pages, tabs, shell preferences and presentation configuration. |
| Product runtime settings   | Product scope, credentials, approvals, execution and external integrations.        |

Configuration errors involving required fields must fail predictably. Optional malformed adapter block payloads degrade safely according to the block's own contract. View configuration cannot introduce unreviewed external action destinations, scripts or filesystem access.

## Core API contracts

- Product adapter: `src/beeui_module/adapters/base.py`.
- App factory: `create_beeui_app(...)`; FastAPI mounting: `mount_beeui(...)`.
- Adapter results and error envelopes: `src/beeui_module/adapters/envelopes.py`.
- Read-only product console response envelope: `beeui.v0`.
- Artifact JSON APIs retain their distinct established adapter-result envelope; they are not silently converted to `beeui.v0`.
- Protected config/actions APIs are explicit POST routes with session/role/CSRF and feature gating.

See [API_CONTRACT.md](API_CONTRACT.md), [WEB_UI.md](WEB_UI.md) and [INTEGRATION.md](INTEGRATION.md) for exact surfaces and examples.

## Security and correctness requirements

1. Treat all adapter payloads, request parameters, stored artifacts and external evidence as untrusted.
2. Render only escaped, normalized, bounded data; no untrusted `|safe`, raw scripts or HTML fragments.
3. Keep GET and read-only polling free of product mutations, network target execution and silent artifact repair.
4. Require auth, sufficient role and valid CSRF for protected BeeUI POST routes; require product authorization independently.
5. Preserve signed/user-bound product evidence and resource ownership; BeeUI cannot infer them from a URL.
6. Reject external/protocol-relative/traversal links and unexpected identifiers.
7. Keep sensitive values out of browser data, rendered markup, public API responses, logs and preview artifacts.
8. Serve static and third-party assets from the installed package; preserve licenses and avoid tracking/demo scripts.
9. Verify browser behavior, wheel packaging, security regressions and host E2E according to change risk.

Normative development/security rules live in [SDLC.md](SDLC.md) and [SECURITY.md](SECURITY.md).

## Explicit non-goals

BeeUI is not a scanner, trading engine, AI runtime, product policy engine, case database, general-purpose message backend, remote tool executor, arbitrary YAML editor, unrestricted file manager, full CMS or visual no-code designer. Separate HTTP remote-product integration, multi-tenant control planes and an arbitrary page builder require separately approved contracts.

A product can use a text-like composer without the framework promising free-form AI chat or targetless network execution. Current BeeScan target authorization and resource policy remain in BeeAgent.

## Acceptance principles

An implemented BeeUI increment is ready for PR only when it has a real end-to-end use case, bounded public schema, explicit negative behavior, appropriate unit/integration/browser tests, installed-package verification where assets change, and an independent review. Historical acceptance evidence is recorded in the relevant Issue and PR, not added as permanent claims to this specification.

## Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — ownership and integration boundaries.
- [INTEGRATION.md](INTEGRATION.md) — embedding and product adapters.
- [COMPONENTS.md](COMPONENTS.md) — typed UI presentation contracts.
- [API_CONTRACT.md](API_CONTRACT.md) — API and result envelopes.
- [WEB_UI.md](WEB_UI.md) — browser routes and behavior.
- [THEME.md](THEME.md) — presentation preferences.
- [SDLC.md](SDLC.md), [SECURITY.md](SECURITY.md) — mandatory engineering controls.
- [ROADMAP.md](ROADMAP.md) — history and future increments.
