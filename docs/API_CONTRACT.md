# API contract BeeUI

## Область действия

Iteration 13 добавляет auth error envelopes, login/logout/CSRF routes и защищённые POST transport stubs.
Iteration 13.4 расширяет только adapter-backed presentation contract `layout[]`:
`kpi_grid.columns` и `type: group`. JSON API envelope, route behavior и artifact API contract не менялись.

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
- Все маршруты используют только GET и содержат `read_only: true`.
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
| `chart` | Server-rendered chart placeholder (no external JS); adapter-provided title/subtitle/status/symbol/timeframe/series/points/candles; empty state when no data |
| `group` | Nested container с `direction` (vertical), `children` (list of layout blocks), bounded recursion depth 3 |
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
