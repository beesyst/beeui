# API contract BeeUI

## Область действия

Iteration 13 добавляет auth error envelopes, login/logout/CSRF routes и защищённые POST transport stubs.
Iteration 13.4 расширяет только adapter-backed presentation contract `layout[]`:
`kpi_grid.columns` и `type: group`. JSON API envelope, route behavior и artifact API contract не менялись.
Iteration 13.6 также расширяет только adapter-backed presentation contract
`layout[]`: добавлены `chart` и `data_table`.
JSON API envelope, route behavior и artifact API contract не менялись.
Это не schema/demo block contract и не `config/settings.yml`.
Iteration 13.8 добавляет generic detail page presentation contract.
JSON API envelope, route behavior и artifact API contract не менялись.
Новый `render_beeui_detail_page()` helper — это Python render entrypoint, не JSON API endpoint.

Iteration 12 определяет стабильный read-only envelope для adapter-backed
маршрутов product console:

- `GET /api/dashboard`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/venues/{venue_id}/dashboard`

Artifact API routes сохраняют существующий contract Iteration 11.

## Успешный ответ

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": {},
  "warnings": [],
  "meta": {}
}
```

Для adapter result со статусом `partial` ответ остаётся успешным, а
`meta.status` получает значение `"partial"`.

## Ответ с ошибкой

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "adapter_unavailable",
    "message": "Adapter is not available"
  },
  "warnings": [],
  "meta": {}
}
```

Ожидаемое соответствие HTTP status:

- `invalid_id` → `400`
- `permission_denied` → `403`
- `not_found` → `404`
- `unavailable` / `adapter_unavailable` → `503`
- некорректные adapter results и неожиданные ошибки adapter → `502`

## Правила

- Product console API routes существуют только при передаче adapter во время
  создания приложения.
- Product console read API routes используют GET и содержат `read_only: true`.
- Protected config/action transport routes используют POST и описаны отдельно в разделе Auth/error envelopes.
- `run_id` и `venue_id` валидируются до вызова adapter.
- Исключения adapter нормализуются, внутренние детали исключений не раскрываются.
- Adapter payload считается недоверенным входом.
- Секреты не должны попадать в HTML или API responses.
- Route prefix и embedded mount сохраняют тот же envelope.
- Artifact API routes не переводятся на `beeui.v0` и сохраняют contract
  Iteration 11.

## Auth/error envelopes (Iteration 13)

Auth-disabled mode используется при `auth.enabled: false`. В этом режиме
все routes доступны без аутентификации.

Auth-enabled mode (`auth.enabled: true`) требует аутентификации для
POST routes на config/action endpoints.

BeeUI реализует transport/security boundary. Product adapter остаётся
владельцем config/action semantics.

### Неаутентифицированный запрос (401)

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "unauthenticated",
    "message": "Authentication required"
  },
  "warnings": [],
  "meta": {}
}
```

### Доступ запрещён (403)

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "forbidden",
    "message": "Insufficient role: viewer"
  },
  "warnings": [],
  "meta": {}
}
```

### Ошибка CSRF (403)

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "csrf_failed",
    "message": "CSRF validation failed"
  },
  "warnings": [],
  "meta": {}
}
```

### Ошибка входа (401)

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "authentication_failed",
    "message": "Invalid credentials"
  },
  "warnings": [],
  "meta": {}
}
```

### Защищённые POST routes

| Route | Required role | CSRF | Feature flag |
|-------|--------------|------|-------------|
| `POST /api/config/preview` | admin | required | `features.config_preview` |
| `POST /api/config/apply` | admin | required | `features.config_apply` |
| `POST /api/actions/preview` | operator | required | `features.operator_actions` |
| `POST /api/actions/execute` | operator | required | `features.operator_actions` |

Product callbacks are not invoked before auth and CSRF pass.
These routes are protected transport stubs: BeeUI validates session, role,
CSRF and request shape, while product adapter owns validation/apply/action
domain behavior.

## Контракт layout blocks (Iteration 12.1)

Это presentation contract для adapter-backed product console HTML pages.
Он не заменяет schema block contract из `config/schema.yml`.

Schema blocks используются в demo/schema mode.
`layout[]` blocks используются в product console mode и приходят из product adapter.

Adapter-backed payloads (`dashboard`, `run`, `venue dashboard`, optionally `runs`)
могут содержать optional поле `layout`:

```json
{
  "latest_run": {...},
  "summary": {...},
  "layout": [
    {
      "type": "hero_snapshot",
      "title": "System",
      "subtitle": "Read-only state",
      "width": 6,
      "status": "runtime_stopped",
      "items": [
        {"label": "Latest run", "value": "run_001", "href": "/runs/run_001"},
        {"label": "Runtime", "value": "stopped"}
      ],
      "links": [
        {"label": "Open runs", "href": "/runs"}
      ]
    }
  ]
}
```

При наличии `layout` c непустым массивом HTML-страницы рендерят blocks
из `layout[]` как Tabler dashboard. При отсутствии `layout` или пустом
массиве используется generic fallback renderer.

`kpi_grid.columns` и `type: group` относятся к adapter-backed `layout[]`.
Они не добавляют новые required keys в `config/settings.yml` и не расширяют schema/demo block contract в `config/schema.yml`.

### Поддерживаемые block types

| Type | Описание |
|------|----------|
| `hero_snapshot` | Card с title/subtitle/status, списком items (label+value+опциональный href) и links |
| `metric_card` | Compact card с title, value, status badge и hint |
| `kpi_strip` | Горизонтальная полоса KPI items (label+value+status) |
| `kpi_grid` | Responsive KPI stat cards с label/value/unit/status/hint; optional `columns` (1..4, default 4) |
| `venue_summary_grid` | Card c grid layout venue summary items |
| `venue_card` | Compact venue summary card с items, alerts и links |
| `mode_cards` | Cards для режимов (label+value+status+опциональный href/latest/latest_href) |
| `operator_hero` | High-level system/operator snapshot с title/subtitle/status, datagrid items и primary_links |
| `state_grid` | Dense key/value state section с datagrid layout и опциональным status badge |
| `quick_links` | List group internal operator links |
| `run_table` | Operator run/event/artifact table с columns и dict rows (run_href, artifact_href) |
| `status_table` | Table с columns/rows |
| `event_table` | Table с columns/rows для событий |
| `attention_list` | List group с severity-dot indicators (severity: warning/error/info/ok/unknown) |
| `artifact_links` | List group artifact links с content_type badge |
| `raw_json_panel` | Card c raw JSON data |
| `chart` | Safe local chart renderer через package-local ApexCharts asset; поддерживает line/bar/area/donut; config сериализуется через `tojson`; arbitrary ApexCharts options не пробрасываются |
| `group` | Nested container с `direction` (vertical), `children` (list of layout blocks), bounded recursion depth 3 |
| `data_table` | Advanced Tabler-compatible table с toolbar, pagination, mobile labels, selectable rows и typed cells |
| `degraded` | Fallback для malformed/unsupported blocks |

### Mapping `width`/`span`/`size`

`width` (1..12), `span` (1..12) and `size` (S/M/L/XL) are mutually exclusive.
Only one sizing key may be present per block placement.

| Key | Value | Column class |
|-----|-------|-------------|
| `width` | 12 | `col-12` |
| `width` | 8 | `col-12 col-lg-8` |
| `width` | 6 | `col-12 col-lg-6` |
| `width` | 4 | `col-12 col-md-6 col-lg-4` |
| `width` | 3 | `col-12 col-sm-6 col-lg-3` |
| `width` | 2 | `col-12 col-sm-6 col-lg-2` |
| `span` | 12 | `col-12` |
| `span` | 8 | `col-12 col-lg-8` |
| `span` | 6 | `col-12 col-lg-6` |
| `span` | 4 | `col-12 col-md-6 col-lg-4` |
| `span` | 3 | `col-12 col-sm-6 col-lg-3` |
| `span` | 2 | `col-12 col-sm-6 col-lg-2` |
| `size` | XL | `col-12` |
| `size` | L | `col-12 col-lg-8` |
| `size` | M | `col-12 col-lg-6` |
| `size` | S | `col-12 col-md-6 col-lg-4` |
| other/invalid | — | `col-12` (default) |

For schema/demo placements: invalid or conflicting sizing keys fail fast.
For adapter-backed `layout[]`: invalid or conflicting sizing keys degrade to `col-12`.

### Колонки KPI grid

`kpi_grid` supports optional `columns` field:

| columns | CSS classes |
|---------|-------------|
| 1 | `col-12` |
| 2 | `col-12 col-sm-6` |
| 3 | `col-12 col-sm-6 col-lg-4` |
| 4 (default) | `col-12 col-sm-6 col-lg-3` |

Missing or invalid adapter values degrade to default 4 (no 500).
`columns` не является CSS class и не пробрасывается в HTML напрямую. BeeUI использует fixed whitelist mapping.

### Layout group (`type: group`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | Must be `"group"` |
| `width` | int | no | Column width 1..12 |
| `direction` | string | no | `"vertical"` only in v1; missing/invalid value defaults to `"vertical"` |
| `children` | array | yes | List of layout block items; missing/invalid value renders the group as `degraded` |

Children render through existing BeeUI block renderer. Depth is bounded at 3 levels; exceeded depth renders as `degraded`.

### Chart block (Iteration 13.6)

`chart` поддерживается только в adapter-backed `layout[]`.

Поля:

| Field | Type | Обязательное | Описание |
|-------|------|----------|-------------|
| `type` | string | yes | Должно быть `"chart"` |
| `title` | string | no | Заголовок |
| `subtitle` | string | no | Подзаголовок |
| `kind` | string | no | `line`, `bar`, `area`, `donut`; unsupported kind fallback к `line` |
| `height` | int | no | Ограниченная высота |
| `series` | array | no | Series payload для выбранного kind |
| `categories` | array | no | X-axis categories для line/bar/area |
| `labels` | array | no | Labels для donut |
| `unit` | string | no | Единица отображения |
| `empty_message` | string | no | Сообщение для empty state |
| `status` | string | no | Текст статуса |
| `hint` | string | no | Подсказка |
| `width` / `span` / `size` | int/string | no | Стандартный adapter-backed sizing |

Правила:

- `chart` не является schema/demo block contract и не добавляет keys в `config/settings.yml`.
- Arbitrary ApexCharts options от adapter не пробрасываются.
- CDN не используется; renderer использует package-local ApexCharts asset.
- Chart config сериализуется через Jinja `tojson` в JSON script node.
- Empty/malformed data рендерится как empty/degraded state, без 500.
- Unsupported `kind` нормализуется к `line`.
- Chart asset загружается только если на странице есть chart blocks.
- Nested chart внутри `group.children` определяется рекурсивно.

### Data table block (Iteration 13.6)

`data_table` поддерживается только в adapter-backed `layout[]`.
Existing schema/demo `table_card` остаётся без изменений.

Поля:

| Field | Type | Обязательное | Описание |
|-------|------|----------|-------------|
| `type` | string | yes | Должно быть `"data_table"` |
| `title` | string | yes | Заголовок |
| `description` | string | no | Описание |
| `variant` | string | no | `"card"` |
| `striped` | bool | no | Tabler striped table |
| `mobile` | string | no | Mobile labels breakpoint |
| `selectable` | bool | no | Selectable rows UI |
| `nowrap` | bool | no | No-wrap table cells |
| `compact` | bool | no | Compact table sizing |
| `toolbar` | object | no | Search/entries/actions toolbar |
| `columns` | array | yes | Column definitions |
| `rows` | array | yes | Row data keyed by column key |
| `pagination` | object | no | Label and page links |
| `width` / `span` / `size` | int/string | no | Стандартный adapter-backed sizing |

Типы ячеек:

- `text`;
- `muted`;
- `link`;
- `badge`;
- `status`;
- `avatar_text`;
- `progress`;
- `actions`.

Правила:

- `data_table` не является schema/demo block contract и не добавляет keys в `config/settings.yml`.
- Links являются internal-only.
- Layout links могут включать query string, например `/runs?page=2`.
- Links отклоняют scheme, netloc, protocol-relative values, traversal и control characters.
- Links префиксуются BeeUI route prefix / embedded mount path.
- Visual tokens проходят allowlist перед использованием как CSS classes.
- Malformed `columns` или `rows` рендерятся как `degraded`.
- Unknown cell type fallback к escaped text.
- Missing values рендерятся как `n/a`.
- No DataTables/List.js runtime.

### Правила безопасности

- Все adapter-provided text values проходят через Jinja autoescaping.
- Ссылки (`href`) принимаются только internal: начинаются с `/` и не
  начинаются с `//`.
- Неизвестный или malformed block type рендерится как `degraded` block,
  а не вызывает crash.
- `layout` не меняет JSON API envelope и route behavior.
- Если adapter возвращает `layout` в payload, оно может оставаться внутри `data`; клиенты должны считать его optional presentation metadata.
- `/api/runs` сохраняет backward-compatible list contract: если adapter возвращает wrapper `{layout, runs}` или `{layout, items}`, API отдаёт список runs/items в `data`.
- Layout blocks не содержат и не допускают arbitrary HTML/JS.
- Chart config сериализуется как JSON script node, не как raw HTML attribute.
- Unsafe `|safe` не используется для adapter/config values.
- Table visual tokens проходят allowlist перед CSS class suffix rendering.
- Table links являются internal-only и prefix-aware.
- Browser-executed chart path остаётся product-neutral.

## Iteration 13.8 — Generic detail page presentation contract

Iteration 13.8 добавляет detail page presentation contract для
product-neutral detail page renderer. Это Python render entrypoint, не JSON API endpoint.

JSON API envelope, route behavior и artifact API contract не меняются.

### Detail page model

```json
{
  "page_id": "event_detail",
  "title": "Event detail",
  "subtitle": "Read-only event details",
  "back_href": "/events",
  "warnings": [],
  "sections": [...]
}
```

### Section kinds

| Kind | Fields | Description |
|------|--------|-------------|
| `key_value` | `title`, `items[]` (label, value) | Tabler card with datagrid |
| `text` | `title`, `body` | Tabler card with preformatted text |
| `table` | `title`, `columns[]` (key, label), `rows[]` | Tabler card with responsive table |
| `links` | `title`, `items[]` (label, href) | Tabler card with list-group |

### Rules

- Detail page не является `layout[]` block contract и не добавляет keys в `config/settings.yml`.
- Detail page не является JSON API endpoint.
- `render_beeui_detail_page()` принимает dict, нормализует и рендерит через Jinja template.
- Unsupported/malformed sections безопасно опускаются, без 500.
- Missing значения рендерятся как `n/a`.
- `back_href` и link hrefs валидируются как safe internal paths.
- Raw поля (`raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes`) не рендерятся.
- HTML autoescape остаётся включённым.
- Unsafe `|safe` не используется.
- Route prefix / embedded mount поддерживаются через существующие link helpers.
