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

После Iteration 13.7 component catalog использует тот же shell locale context,
что и остальные BeeUI страницы. Catalog links сохраняют `lang`, где это
practically applicable. Catalog остаётся read-only и product-neutral.

## Добавления Iteration 13.6

### Chart (`type: chart`)

Safe local chart renderer for adapter-backed `layout[]`. Supports controlled chart kinds without arbitrary JS or ApexCharts options passthrough.

Поддерживаемые виды:

| Kind | Chart type |
|------|-----------|
| `line` | ApexCharts line chart |
| `bar` | ApexCharts bar chart |
| `area` | ApexCharts area chart |
| `donut` | ApexCharts donut chart (uses `labels`, not `categories`) |

Контролируемые поля:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `"Chart"` | Card title |
| `subtitle` | string | `""` | Card subtitle |
| `kind` | string | `"line"` | Chart kind: `line`, `bar`, `area`, `donut` |
| `height` | int | `300` | Chart height in px (50..800, clamped) |
| `series` | list | `[]` | Line/bar/area: `[{"name": str, "data": [num]}]`; donut: `[num]` |
| `categories` | list | `[]` | X-axis labels for line/bar/area |
| `labels` | list | `[]` | Segment labels for donut |
| `unit` | string | `""` | Display unit below chart |
| `empty_message` | string | `"No chart data"` | Message when data is empty |
| `status` | string | `""` | Badge text in card header |
| `hint` | string | `""` | Hint text below chart |

Правила:

- No arbitrary ApexCharts options passthrough.
- Only controlled fields are serialized.
- Chart script is package-local (`static/vendor/apexcharts/apexcharts.min.js`).
- Chart DOM ids are deterministic.
- Missing/empty series render as empty state, not 500.
- Unsupported kind falls back to `line`.
- Malformed payload degrades visibly.

Пример adapter-backed payload:

```json
{
  "type": "chart",
  "title": "Processed events",
  "kind": "line",
  "height": 280,
  "series": [
    { "name": "Processed", "data": [12, 18, 24, 19, 31, 42, 38] }
  ],
  "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "width": 6
}
```

### Data table (`type: data_table`)

Advanced Tabler-compatible data table for adapter-backed `layout[]`. Backward-compatible with existing `table_card`.

Поддерживаемые варианты:

| Field | Type | Description |
|-------|------|-------------|
| `variant` | string | Only `"card"` supported |
| `striped` | bool | Alternate row backgrounds |
| `mobile` | string | Responsive breakpoint: `"sm"`, `"md"`, `"lg"` or null |
| `selectable` | bool | Show checkbox column (inert) |
| `nowrap` | bool | Prevent text wrapping |
| `compact` | bool | Use `table-sm` |
| `toolbar` | object | Optional toolbar: `{search, entries, actions}` |
| `pagination` | object | Optional footer pagination: `{label, pages[]}` |

Поддерживаемые типы ячеек:

| Cell type | Payload format | Renders as |
|-----------|---------------|------------|
| `text` | `{"label": str}` or scalar | Plain text, escaped |
| `muted` | `{"label": str}` or scalar | Text with secondary color |
| `link` | `{"label": str, "href": str}` | `<a>` link (internal only) |
| `badge` | `{"label": str, "tone": str}` | Tabler badge with tone |
| `status` | `{"label": str, "status": str}` | Status dot + label |
| `avatar_text` | `{"title": str, "subtitle": str, "initials": str, "color": str}` | Avatar + text |
| `progress` | `{"label": str, "value": int, "color": str}` | Progress bar + label |
| `actions` | `[{"label": str, "href": str}]` | Action button list |

Правила:

- Все ссылки internal-only: разрешены `/...`, отклонены `//...`, `http://...`, `https://...`, `javascript:` и traversal.
- Missing values render as `n/a`.
- Unknown cell type degrades to escaped text.
- Malformed payload renders as empty table, not 500.
- No DataTables/List.js runtime in this iteration.
- Search/entries controls are inert placeholders.
- Unsafe/external links are rejected or rendered inert.

Пример adapter-backed payload:

```json
{
  "type": "data_table",
  "title": "Recent items",
  "striped": true,
  "mobile": "md",
  "selectable": true,
  "toolbar": {
    "search": true,
    "entries": true,
    "actions": [{"label": "Export", "href": "/reports/export"}]
  },
  "columns": [
    { "key": "id", "label": "ID", "cell": "link" },
    { "key": "status", "label": "Status", "cell": "badge" },
    { "key": "progress", "label": "Progress", "cell": "progress" },
    { "key": "actions", "label": "", "cell": "actions" }
  ],
  "rows": [
    {
      "id": { "label": "run_001", "href": "/runs/run_001" },
      "status": { "label": "ok", "tone": "success" },
      "progress": { "label": "72%", "value": 72 },
      "actions": [{ "label": "Open", "href": "/runs/run_001" }]
    }
  ],
  "pagination": {
    "label": "Showing 1 to 8 of 16 entries",
    "pages": [
      { "label": "1", "href": "/runs?page=1", "active": true },
      { "label": "2", "href": "/runs?page=2" }
    ]
  },
  "width": 12
}
```

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
