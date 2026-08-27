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

После Iteration 13.7 component catalog использует тот же shell locale context, что и остальные BeeUI страницы. Catalog links сохраняют `lang`, где это practically applicable. Catalog остаётся read-only и product-neutral.

## Добавления Iteration 13.6

### Chart (`type: chart`)

Safe local chart renderer for adapter-backed `layout[]`. Supports controlled chart kinds without arbitrary JS or ApexCharts options passthrough.

Поддерживаемые виды:

| Kind    | Chart type                                               |
| ------- | -------------------------------------------------------- |
| `line`  | ApexCharts line chart                                    |
| `bar`   | ApexCharts bar chart                                     |
| `area`  | ApexCharts area chart                                    |
| `donut` | ApexCharts donut chart (uses `labels`, not `categories`) |

Контролируемые поля:

| Field           | Type   | Default           | Description                                                                                   |
| --------------- | ------ | ----------------- | --------------------------------------------------------------------------------------------- |
| `title`         | string | `"Chart"`         | Card title                                                                                    |
| `subtitle`      | string | `""`              | Card subtitle                                                                                 |
| `kind`          | string | `"line"`          | Chart kind: `line`, `bar`, `area`, `donut`                                                    |
| `height`        | int    | `300`             | Chart height in px (50..800, clamped)                                                         |
| `series`        | list   | `[]`              | Line/bar/area: `[{"name": str, "data": [finite number]}]`; donut: non-empty `[finite number]` |
| `categories`    | list   | `[]`              | X-axis labels for line/bar/area                                                               |
| `labels`        | list   | `[]`              | Segment labels for donut                                                                      |
| `unit`          | string | `""`              | Display unit below chart                                                                      |
| `empty_message` | string | `"No chart data"` | Message when data is empty                                                                    |
| `status`        | string | `""`              | Badge text in card header                                                                     |
| `hint`          | string | `""`              | Hint text below chart                                                                         |
| `chart_id`      | string | deterministic id  | `[A-Za-z][A-Za-z0-9_-]{0,63}`; invalid value uses deterministic fallback                      |
| `colors`        | list   | `[]`              | Up to 12 generic BeeUI tokens or strict `#[0-9A-Fa-f]{6}` values                              |
| `horizontal`    | bool   | `false`           | Horizontal bar layout only for `bar` charts                                                   |
| `barHeight`     | string | `"50%"`           | Horizontal bar height from `1%` to `100%`                                                     |

Правила:

- No arbitrary ApexCharts options passthrough.
- Only controlled fields are serialized.
- Chart script is package-local (`static/vendor/apexcharts/apexcharts.min.js`).
- Chart DOM ids are deterministic unless `chart_id` passes the bounded identifier contract.
- Generic color tokens map to Tabler CSS variables; strict six-digit hex colors remain hex. CSS functions, alpha formats, URLs and other arbitrary CSS are omitted.
- Series accepts only finite numeric values; booleans, `NaN`, infinities, strings and nested objects are malformed.
- `ready` has valid non-empty normalized data; `empty` has a correct empty series; `degraded` has malformed or unsupported payload; runtime browser render failure is `error`.
- Unsupported kind renders an explicit degraded state.
- Malformed payload degrades visibly.

Пример adapter-backed payload:

```json
{
  "type": "chart",
  "title": "Processed events",
  "kind": "line",
  "height": 280,
  "series": [{ "name": "Processed", "data": [12, 18, 24, 19, 31, 42, 38] }],
  "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "width": 6
}
```

### Data table (`type: data_table`)

Advanced Tabler-compatible data table for adapter-backed `layout[]`. Backward-compatible with existing `table_card`.

Начиная с Iteration 13.12 toolbar рендерится внутри card-header как часть единой канонической карточки. Column chooser использует горизонтальное многоточие (`icon-tabler-dots`). Malformed columns/rows сохраняют canonical shell, toolbar и показывают bounded degraded сообщение.

Поддерживаемые варианты:

| Field        | Type   | Description                                                                                      |
| ------------ | ------ | ------------------------------------------------------------------------------------------------ |
| `variant`    | string | Only `"card"` supported                                                                          |
| `striped`    | bool   | Alternate row backgrounds                                                                        |
| `mobile`     | string | Responsive breakpoint: `"sm"`, `"md"`, `"lg"` or null                                            |
| `selectable` | bool   | Show checkbox column (inert)                                                                     |
| `nowrap`     | bool   | Prevent text wrapping                                                                            |
| `compact`    | bool   | Use `table-sm`                                                                                   |
| `id`         | string | Optional safe stable identity for progressive GET replacement                                    |
| `toolbar`    | object | Optional toolbar: `{search, entries, actions, fields[], hidden, column_toggles[], apply, reset}` |

Toolbar fields (`toolbar.fields[]`):

| Field type   | Parameters                                                 | Description                                                        |
| ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------ |
| `date_range` | `name`, `from_value`, `to_value`, `from_label`, `to_label` | Two Tabler Datepicker inputs (from/to), backed by local Litepicker |
| `text`       | `name`, `value`, `placeholder`                             | Text/search input                                                  |
| `select`     | `name`, `value`, `options[]`, `multi`                      | Dropdown list                                                      |
| `checkboxes` | `choices[]` (`value`, `label`, `checked`, `toggle_href`)   | Checkbox group with internal toggle links                          |

Additional toolbar fields:

| Field            | Type   | Description                                                                                                           |
| ---------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| `hidden`         | object | Hidden query fields (`{key: value}`)                                                                                  |
| `column_toggles` | array  | Column visibility toggles: `[{key, label, visible, toggle_href}]`. Rendered as direct items in the ellipsis dropdown. |
| `apply`          | object | Explicit Apply button: `{label, href}`. Absent = no Apply.                                                            |
| `reset`          | object | Reset button: `{label, href}`                                                                                         |
| `pagination`     | object | Optional footer pagination: `{label, pages[]}`                                                                        |

Поддерживаемые типы ячеек:

| Cell type     | Payload format                                                   | Renders as                 |
| ------------- | ---------------------------------------------------------------- | -------------------------- |
| `text`        | `{"label": str}` or scalar                                       | Plain text, escaped        |
| `muted`       | `{"label": str}` or scalar                                       | Text with secondary color  |
| `link`        | `{"label": str, "href": str}`                                    | `<a>` link (internal only) |
| `badge`       | `{"label": str, "tone": str}`                                    | Tabler badge with tone     |
| `status`      | `{"label": str, "status": str}`                                  | Status dot + label         |
| `avatar_text` | `{"title": str, "subtitle": str, "initials": str, "color": str}` | Avatar + text              |
| `progress`    | `{"label": str, "value": int, "color": str}`                     | Progress bar + label       |
| `actions`     | `[{"label": str, "href": str}]`                                  | Action button list         |

Правила:

- Все ссылки internal-only: разрешены `/...`, отклонены `//...`, `http://...`, `https://...`, `javascript:` и traversal.
- Missing values render as `n/a`.
- Unknown cell type degrades to escaped text.
- Malformed payload renders as canonical table card with degraded message, not 500.
- No DataTables/List.js runtime; functional tables with an optional safe `id` use built-in browser APIs for progressive GET replacement only.
- Toolbar fields support functional GET form with date range, text search, select dropdowns, checkboxes, hidden fields, column toggles, reset and explicit Apply.
- Toolbar is rendered inside the table card header, not in a separate card-body.
- Malformed `columns` or `rows` preserve the canonical card, title, toolbar and show a bounded degraded alert message.
- Apply button is rendered only when explicitly requested; date ranges do not create an implicit Apply.
- Search and date range controls can omit visible labels while retaining `aria-label`.
- The column chooser ellipsis icon uses horizontal dots (`icon-tabler-dots`) and appears immediately after the first text/search field. When no text search exists, the ellipsis appears at the end of the functional fields.
- Column visibility controls are rendered as direct items in the ellipsis dropdown.
- Dropdown filters use canonical `.btn-ghost-secondary`, `.dropdown-toggle`, `.dropdown-menu` and `.dropdown-item` classes.
- Reset uses a standard `.btn-ghost-secondary`.
- A live table replaces only its matching `data-beeui-table-id` from a successful same-origin response. Product filter links, sort links, pagination and page-size controls may participate; row/detail/artifact/action navigation does not.
- Text inputs retain Enter/GET fallback. Initial automatic search for zero to two trimmed characters does not request; three or more trimmed characters request after 275 ms. After an automatic server search is active, shrinking to zero to two characters clears the automatic search with page `1` and without sending the short search parameter. Direct URLs and normal GET submission retain product-owned short-query semantics. URL state is replaced after a successful GET, so it remains refreshable without creating a history entry per keypress.
- Canonical functional GET forms and text search inputs set `autocomplete="off"` to suppress browser autocomplete and search-history suggestions while preserving the field name, accessible name and normal GET fallback.
- `pagination.pages[]` is rendered compactly: first, active neighborhood, last, ellipses and available previous/next controls. `pagination.page_size` optionally supplies product-owned `{current, options[]}` with safe internal hrefs; its selector and the records label wrap with pagination on narrow screens.
- No inline positioning styles are required for dropdown placement.
- Desktop controls remain on one row when sufficient width exists; narrow layouts wrap or stack via `flex-wrap`.
- Legacy `search`/`entries`/`actions` toolbar fields remain supported.
- Unsafe/external links are rejected or rendered inert.

Пример adapter-backed payload:

```json
{
  "type": "data_table",
  "title": "Queue",
  "striped": true,
  "mobile": "md",
  "selectable": true,
  "toolbar": {
    "search": true,
    "entries": true,
    "actions": [{ "label": "Export", "href": "/reports/export" }],
    "fields": [
      {
        "type": "date_range",
        "name": "date",
        "label": "Period",
        "from_value": "2026-07-01",
        "to_value": "2026-07-31"
      },
      {
        "type": "text",
        "name": "q",
        "placeholder": "Search..."
      },
      {
        "type": "select",
        "name": "status",
        "label": "Status",
        "value": "new",
        "options": [
          { "value": "new", "label": "New" },
          { "value": "done", "label": "Done" }
        ]
      }
    ],
    "hidden": { "tab": "queue" },
    "column_toggles": [
      { "key": "id", "label": "ID", "visible": true },
      { "key": "name", "label": "Name", "visible": false }
    ],
    "reset": { "label": "Clear", "href": "/queue?clear=1" }
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

### Filter form (`type: filter_form`)

Controlled GET filter bar for adapter-backed `layout[]`. The filter form renders as a collapsible card with form controls and submit/reset buttons.

Поля:

| Field     | Type   | Обязательное | Описание                                       |
| --------- | ------ | ------------ | ---------------------------------------------- |
| `type`    | string | yes          | Должно быть `"filter_form"`                    |
| `title`   | string | yes          | Заголовок карточки                             |
| `fields`  | array  | yes          | Список полей фильтрации                        |
| `actions` | object | no           | `{apply: {label, href}, reset: {label, href}}` |

Типы полей:

| Field type   | Параметры                                                | Описание                                                          |
| ------------ | -------------------------------------------------------- | ----------------------------------------------------------------- |
| `date_range` | `from_value`, `to_value`, `from_label`, `to_label`       | Два Tabler Datepicker input (from/to), backed by local Litepicker |
| `text`       | `name`, `value`, `placeholder`                           | Текстовый input (search)                                          |
| `select`     | `name`, `value`, `options[]`, `multi`                    | Выпадающий список                                                 |
| `checkboxes` | `choices[]` (`value`, `label`, `checked`, `toggle_href`) | Группа checkbox с internal toggle links                           |

Правила:

- Все значения проходят autoescaping.
- Форма использует `method=GET`.
- `date_range` содержит два отдельных Tabler Datepicker input с именами `date_from`/`date_to`, использующих `.input-icon` и `.input-icon-addon` с календарным SVG.
- `date_range` inputs имеют `type="text"` с `inputmode="numeric"` и `pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"` для ручного ввода ISO-дат без JavaScript.
- При наличии JavaScript Litepicker загружается условно (только для страниц с `date_range`).
- Инициализация Litepicker использует контролируемый locale из BeeUI (`en` → `en-US`, `ru` → `ru-RU`).
- `select` options с value/label.
- Missing/invalid fields degrades to empty filter form, не 500.
- `actions.apply` is a GET submit button; `method` is not an adapter-configurable field. A safe `href` becomes the form action; an unsafe href falls back to the safe prefixed current route.
- Safe `actions.reset.href`, checkbox toggle hrefs and column-toggle hrefs render as prefixed internal links; unsafe values are inert or omitted.
- JavaScript auto-submit is optional progressive enhancement; the form remains server-side GET-only.

Пример adapter-backed payload:

```json
{
  "type": "filter_form",
  "title": "Queue Filters",
  "size": "XL",
  "fields": [
    {
      "type": "date_range",
      "name": "date",
      "label": "Date range",
      "from_value": "2026-07-01",
      "to_value": "2026-07-12"
    },
    {
      "type": "text",
      "name": "q",
      "label": "Search",
      "value": "welding",
      "placeholder": "Search by sender or subject..."
    },
    {
      "type": "select",
      "name": "case_type",
      "label": "Classification",
      "value": "new_lead",
      "options": [
        { "value": "new_lead", "label": "New lead" },
        { "value": "existing_deal", "label": "Existing deal" }
      ]
    },
    {
      "type": "select",
      "name": "priority",
      "label": "Priority",
      "value": "high",
      "options": [
        { "value": "high", "label": "High" },
        { "value": "medium", "label": "Medium" },
        { "value": "low", "label": "Low" }
      ]
    },
    {
      "type": "select",
      "name": "bitrix_status",
      "label": "Bitrix status",
      "value": "unreconciled",
      "options": [
        { "value": "matched", "label": "Matched" },
        { "value": "not_found", "label": "Not found" },
        { "value": "unreconciled", "label": "Unreconciled" }
      ]
    }
  ],
  "actions": {
    "apply": { "label": "Apply", "href": "/rop?tab=queue" },
    "reset": { "label": "Clear", "href": "/rop?tab=queue" }
  }
}
```

Правила безопасности:

- Все значения экранируются через Jinja autoescape.
- `options` без `value` или `label` пропускаются.
- Неизвестный `field.type` игнорируется.
- Контролируемый package-local JavaScript BeeUI используется только для presentation Litepicker и GET auto-submit; product callback или runtime execution не вызываются.
- Adapter не передаёт JavaScript или произвольные Litepicker options; filtering, validation, timezone и range semantics остаются у product.
- Форма остаётся GET-only и пригодна для использования без JavaScript.
- `actions.apply.href`, `actions.reset.href` and toggle hrefs validate as internal links; unsafe apply keeps a GET submit using the safe prefixed current route.

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
    {
      "type": "metric_card",
      "title": "Activity Feed",
      "value": "active",
      "width": 12
    }
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

| columns     | CSS classes                |
| ----------- | -------------------------- |
| 1           | `col-12`                   |
| 2           | `col-12 col-sm-6`          |
| 3           | `col-12 col-sm-6 col-lg-4` |
| 4 (default) | `col-12 col-sm-6 col-lg-3` |

Invalid adapter values degrade to default 4 (no 500). Это поле относится только к adapter-backed `layout[]` block `kpi_grid`. Schema/demo `kpi_grid` этим contract не расширяется.

### Отступы страниц

Все HTML render paths (`page.html`, `product_dashboard.html`, `product_runs.html`, `product_run_detail.html`, `product_venue_dashboard.html`) используют единый `.page-body` wrapper:

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

| Block type      | Template                               | Purpose                                                                          |
| --------------- | -------------------------------------- | -------------------------------------------------------------------------------- |
| `operator_hero` | `components/layout/operator_hero.html` | System/operator snapshot with datagrid items and primary action buttons          |
| `venue_card`    | `components/layout/venue_card.html`    | Compact venue/operator summary card with items, severity alerts and footer links |
| `kpi_grid`      | `components/layout/kpi_grid.html`      | Responsive KPI stat cards with label, value, unit, status badge and hint         |
| `state_grid`    | `components/layout/state_grid.html`    | Dense key/value state section using Tabler datagrid layout                       |
| `quick_links`   | `components/layout/quick_links.html`   | List group of internal operator links                                            |
| `run_table`     | `components/layout/run_table.html`     | Operator run/event/artifact table with internal links for run_id and artifact    |

`operator_hero.items[].progress` accepts only finite numeric values and is clamped to `0..100`. `progress_tone` accepts only generic `bg-primary`, `bg-secondary`, `bg-success`, `bg-warning`, `bg-danger`, or `bg-info`; invalid values use `bg-primary`.

All block templates use Tabler-compatible markup (`card`, `card-header`, `card-body`, `datagrid`, `table table-vcenter card-table`, `list-group`, `badge`, `status-dot`, `alert`) and pass through Jinja autoescaping.

Existing `mode_cards` now supports optional fields: `href`, `latest`, `latest_href`. Existing `attention_list` handles all severity values (`warning`, `error`, `info`, `ok`, `unknown`) and missing label/message renders as `n/a`.

A new `_display_value` helper in `blocks/layout_renderer.py` ensures user-visible values never render as `None` — missing/empty values render as `n/a` by default.

## Iteration 13.8 — Generic detail page section kinds

Iteration 13.8 adds a product-neutral detail page renderer with controlled section kinds.

Detail page template: `src/beeui_module/web/templates/detail.html`.

Normalizer/helper: `src/beeui_module/pages/detail.py`.

Public entrypoint: `render_beeui_detail_page(request, page, *, templates, route_prefix, ui_config, product_title, product_id)`.

### Section kinds

| Kind        | Template output                                   | Normalizer                       | Fields                                      |
| ----------- | ------------------------------------------------- | -------------------------------- | ------------------------------------------- |
| `key_value` | Tabler card with `datagrid`                       | `_normalize_key_value_section()` | `title`, `items[]` (label, value)           |
| `text`      | Tabler card with `<pre class="mb-0 text-break">`  | `_normalize_text_section()`      | `title`, `body`                             |
| `table`     | Tabler card with `table table-vcenter card-table` | `_normalize_table_section()`     | `title`, `columns[]` (key, label), `rows[]` |
| `links`     | Tabler card with `list-group list-group-flush`    | `_normalize_links_section()`     | `title`, `items[]` (label, href)            |

### Normalization rules

- Unsupported kinds are safely omitted.
- Missing `items`, `columns`, `rows` or `body` cause the section to be omitted.
- Missing label/value renders as `n/a`.
- Links are validated as safe internal paths.
- External/unsafe links render as inert text.
- Raw implicit fields (`raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes`) are not included in normalized output.
- HTML autoescape remains enabled; no `|safe` for adapter/product values.

### Template markup

The template uses the same Tabler-compatible primitives as the rest of BeeUI:

- `datagrid` for key_value sections;
- `pre.text-break` for text sections;
- `table.table-vcenter.card-table` for table sections;
- `list-group.list-group-flush` for links sections.

No JS is required. No external assets are referenced.

## Iteration 13.9 — Filter form (`type: filter_form`)

Controlled GET filter bar for adapter-backed `layout[]`.

### Supported field types

| Field type   | Parameters                                                                 | Description                                                                                                      |
| ------------ | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `date_range` | `from_value`, `to_value`, `from_label`, `to_label`                         | Two Tabler Datepicker inputs (from/to) backed by local Litepicker, auto-submit on selection, manual ISO fallback |
| `text`       | `name`, `value`, `placeholder`                                             | Text search input                                                                                                |
| `select`     | `name`, `value`, `options[]`, `multi`                                      | Dropdown with auto-submit                                                                                        |
| `checkboxes` | `choices[]` (value, label, checked, toggle_href), `open`, `selected_count` | Dropdown checkbox group with toggle links                                                                        |

### Safe href contract

All active hrefs validate through the shared internal-link contract:

| Href source                    | Validation              | Invalid behavior                                               |
| ------------------------------ | ----------------------- | -------------------------------------------------------------- |
| checkbox `toggle_href`         | internal-link validator | Rendered as inert text                                         |
| columns `toggle_href`          | internal-link validator | Rendered as inert text                                         |
| columns `toggle_href` (header) | internal-link validator | Columns button not shown                                       |
| `reset` href                   | internal-link validator | Reset button not shown                                         |
| `apply` href                   | internal-link validator | GET submit remains; safe prefixed current-route action is used |

### Data table sortable columns

Columns in `data_table` blocks support `sort_href`:

```json
{
  "key": "status",
  "label": "Status",
  "sortable": true,
  "sort_href": "/runs?sort=status&dir=asc"
}
```

- `sort_href` is validated through the shared internal-link contract.
- Invalid `sort_href` is rendered as plain label, not a link.
- Template renders sort link only when `sort_href` is valid.
- `asc`/`ascending` normalize to `ascending`; `desc`/`descending` normalize to `descending`.
- Unknown direction renders an inactive safe header.

## Iteration 13.9 — Detail presentation metadata

Detail page `key_value` items support product-neutral presentation fields:

| Field     | Type   | Allowed values                                        | Description                             |
| --------- | ------ | ----------------------------------------------------- | --------------------------------------- |
| `variant` | string | `text`, `badge`, `boolean`, `confidence`, `long_text` | Renders as badge, boolean display, etc. |
| `tone`    | string | `default`, `muted`, `success`, `warning`, `danger`    | Color tone for the value                |
| `display` | string | any                                                   | Display string for boolean variants     |

Product decides tone and display semantics. BeeUI validates allowlisted values. Unknown variant/tone safely degrades to plain text.

Built-in labels introduced by this contract use the BeeUI `en`/`ru` catalog; adapter-provided labels remain escaped product text.

### Backward compatibility

- When explicit `variant` is absent, neutral `type_hint` aliases `long_text`, `boolean`, and `confidence` map to the matching variant. `priority` and unknown values map to plain text without tone.
- Explicit `variant` takes precedence over `type_hint`.
- Plain text items without variant/tone render as before.

## Рекомендации по переиспользованию

При добавлении будущих pages/blocks:

1. Prefer existing primitive macros first.
2. Add small primitive extensions only when needed.
3. Keep primitive interfaces generic and product-neutral.
4. Validate any new text-bearing fields and rely on autoescape.
5. Keep plugin integrations behind future bounded adapter/action iterations.
