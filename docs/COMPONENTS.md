# Components

## Purpose

This document defines the internal BeeUI component catalog and reusable controlled template primitives introduced in Iteration 6.

Main rule:

```text
BeeUI renders.
Product decides.
```

The component catalog is read-only and internal. It is intended for visual review and safe primitive reuse by future pages and blocks.

## Route surface

Catalog routes are internal HTML routes and are always read-only:

- `GET /components`
- `GET /components/interface`
- `GET /components/forms`
- `GET /components/layout`
- `GET /components/extra`
- `GET /components/plugins`

All routes are served under configured `web.route_prefix`.

## Primitives v0

Reusable template primitives are implemented in:

- `src/beeui_module/web/templates/components/primitives/catalog_primitives.html`

Primitives:

- `alert`
- `badge`
- `breadcrumb`
- `button`
- `button_group`
- `card`
- `card_header`
- `dropdown`
- `empty_state`
- `modal_shell`
- `tabs`
- `table`
- `data_grid`
- `form_input`
- `form_select`
- `form_checkbox`
- `form_radio`
- `form_textarea`
- `form_selectgroup`
- `pagination`
- `progress`
- `status_dot`
- `avatar_placeholder`
- `toast_placeholder`
- `offcanvas_shell`

Inert plugin placeholders:

- `chart_container`
- `map_container`
- `datatable_container`

## Catalog templates

Catalog templates are implemented in:

- `src/beeui_module/web/templates/components/catalog/index.html`
- `src/beeui_module/web/templates/components/catalog/page.html`
- `src/beeui_module/web/templates/components/catalog/sections/*.html`

They render inside the existing BeeUI shell (`base.html`), with the same navigation/layout/theme context helpers used by configured pages.

## Security and constraints

Required safety guarantees for primitives and catalog pages:

- Jinja autoescape remains enabled.
- No unsafe `|safe` usage for sample/config/user-like values.
- No user-supplied HTML rendering.
- No external CDN, tracking, or third-party script/style references.
- Plugin placeholders are inert markup only.
- No runtime/product execution authority.

## Allowed and forbidden usage

Allowed:

- Read-only visual previews.
- Reuse of controlled primitives in future BeeUI templates.
- Safe literal sample text from Python-defined context.

Forbidden:

- Copying full upstream Tabler demo pages.
- Arbitrary HTML/JS/CSS from config or user input.
- External charts/maps/datatable runtime integrations in catalog.
- Product-specific domain semantics in generic primitives.
- Hidden write-side effects in GET routes.

## Reuse guidance

When adding future pages/blocks:

1. Prefer existing primitive macros first.
2. Add small primitive extensions only when needed.
3. Keep primitive interfaces generic and product-neutral.
4. Validate any new text-bearing fields and rely on autoescape.
5. Keep plugin integrations behind future bounded adapter/action iterations.
