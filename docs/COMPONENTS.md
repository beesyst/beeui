# Components

## Назначение

Этот документ описывает внутренний каталог компонентов BeeUI и переиспользуемые контролируемые template primitives, добавленные в Iteration 6.

Главное правило:

```text
BeeUI renders.
Product decides.
```

Каталог компонентов является internal и read-only. Он предназначен для визуальной проверки и безопасного переиспользования примитивов в будущих страницах и блоках.

## Поверхность маршрутов

Маршруты каталога являются internal HTML routes и всегда работают в read-only режиме:

- `GET /components`
- `GET /components/interface`
- `GET /components/forms`
- `GET /components/layout`
- `GET /components/extra`
- `GET /components/plugins`

Все маршруты обслуживаются под настроенным `web.route_prefix`.

## Добавления Iteration 13.4

### Layout group (`type: group`)

Generic nested container для Tabler dashboard compositions.

Payload адаптера:

```json
{
  "id": "left_stack",
  "type": "group",
  "width": 6,
  "direction": "vertical",
  "children": [
    { "type": "metric_card", "title": "Storage", "value": "42", "width": 12 },
    { "type": "metric_card", "title": "Activity Feed", "value": "active", "width": 12 }
  ]
}
```

HTML-форма:

```html
<div class="row row-cards g-3">
  <div class="col-12">...</div>
  <div class="col-12">...</div>
</div>
```

Ограничения:

- `children` требуется для валидного group payload;
- `direction` optional, default `vertical`;
- invalid `direction` → `vertical`;
- `children` рендерятся через существующий BeeUI block renderer;
- missing/invalid `children` → `degraded`;
- depth limit `3`; exceeded depth returns `degraded` block;
- некорректный group payload рендерится как `degraded` block, без 500.

### Колонки KPI grid

`kpi_grid` поддерживает optional `columns` (1..4):

| columns | CSS classes |
|---------|-------------|
| 1       | `col-12` |
| 2       | `col-12 col-sm-6` |
| 3       | `col-12 col-sm-6 col-lg-4` |
| 4 (default) | `col-12 col-sm-6 col-lg-3` |

Invalid adapter values degrade to default 4 (no 500).
Это поле относится только к adapter-backed `layout[]` block `kpi_grid`.
Schema/demo `kpi_grid` этим contract не расширяется.

### Отступы страниц

Все HTML render paths (`page.html`, `product_dashboard.html`, `product_runs.html`,
`product_run_detail.html`, `product_venue_dashboard.html`) используют единый
`.page-body` wrapper:

```html
<div class="page-body">
  <div class="container-xl">...</div>
</div>
```

Страницы с tabs рендерят blocks внутри `.card.beeui-page-tabs-card` в пределах того же page-body.

## Примитивы v0

Переиспользуемые template primitives реализованы в:

- `src/beeui_module/web/templates/components/primitives/catalog_primitives.html`

Примитивы:

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
- `url_tabs` (URL-driven variant with `<a>` links and `?tab=` active state; supports `tab_class`, `active_param`, `disabled` items)
- `accordion` (Tabler/Bootstrap-compatible collapsible; deterministic ids; supports `accordion_class` for variant)
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

Инертные plugin placeholders:

- `chart_container`
- `map_container`
- `datatable_container`

## Шаблоны каталога

Шаблоны каталога реализованы в:

- `src/beeui_module/web/templates/components/catalog/index.html`
- `src/beeui_module/web/templates/components/catalog/page.html`
- `src/beeui_module/web/templates/components/catalog/sections/*.html`

Они рендерятся внутри существующей BeeUI shell (`base.html`) с теми же navigation/layout/theme context helpers, что и configured pages.

## Безопасность и ограничения

Обязательные гарантии безопасности для примитивов и страниц каталога:

- Jinja autoescape remains enabled.
- No unsafe `|safe` usage for sample/config/user-like values.
- No user-supplied HTML rendering.
- No external CDN, tracking, or third-party script/style references.
- Plugin placeholders are inert markup only.
- No runtime/product execution authority.

## Разрешённое и запрещённое использование

Разрешено:

- Read-only visual previews.
- Reuse of controlled primitives in future BeeUI templates.
- Safe literal sample text from Python-defined context.

Запрещено:

- Copying full upstream Tabler demo pages.
- Arbitrary HTML/JS/CSS from config or user input.
- External charts/maps/datatable runtime integrations in catalog.
- Product-specific domain semantics in generic primitives.
- Hidden write-side effects in GET routes.

## Iteration 12.4 — Примитивы блоков операторской консоли

Iteration 12.4 adds 6 new adapter-backed `layout[]` block types for product-neutral operator console parity:

| Block type | Template | Purpose |
|------------|----------|---------|
| `operator_hero` | `components/layout/operator_hero.html` | System/operator snapshot with datagrid items and primary action buttons |
| `venue_card` | `components/layout/venue_card.html` | Compact venue/operator summary card with items, severity alerts and footer links |
| `kpi_grid` | `components/layout/kpi_grid.html` | Responsive KPI stat cards with label, value, unit, status badge and hint |
| `state_grid` | `components/layout/state_grid.html` | Dense key/value state section using Tabler datagrid layout |
| `quick_links` | `components/layout/quick_links.html` | List group of internal operator links |
| `run_table` | `components/layout/run_table.html` | Operator run/event/artifact table with internal links for run_id and artifact |

All block templates use Tabler-compatible markup (`card`, `card-header`, `card-body`, `datagrid`, `table table-vcenter card-table`, `list-group`, `badge`, `status-dot`, `alert`) and pass through Jinja autoescaping.

Existing `mode_cards` now supports optional fields: `href`, `latest`, `latest_href`.
Existing `attention_list` handles all severity values (`warning`, `error`, `info`, `ok`, `unknown`) and missing label/message renders as `n/a`.

A new `_display_value` helper in `blocks/layout_renderer.py` ensures user-visible values never render as `None` — missing/empty values render as `n/a` by default.

## Рекомендации по переиспользованию

При добавлении будущих pages/blocks:

1. Prefer existing primitive macros first.
2. Add small primitive extensions only when needed.
3. Keep primitive interfaces generic and product-neutral.
4. Validate any new text-bearing fields and rely on autoescape.
5. Keep plugin integrations behind future bounded adapter/action iterations.
