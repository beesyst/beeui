# API contract BeeUI

## Область действия

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

## Layout block contract (Iteration 12.1)

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

### Поддерживаемые block types

| Type | Описание |
|------|----------|
| `hero_snapshot` | Card с title/subtitle/status, списком items (label+value+опциональный href) и links |
| `metric_card` | Compact card с title, value, status badge и hint |
| `kpi_strip` | Горизонтальная полоса KPI items (label+value+status) |
| `kpi_grid` | Responsive KPI stat cards с label/value/unit/status/hint |
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
| `degraded` | Fallback для malformed/unsupported blocks |

### Width mapping

| width | Column class |
|-------|-------------|
| 12 | `col-12` |
| 8 | `col-12 col-lg-8` |
| 6 | `col-12 col-lg-6` |
| 4 | `col-12 col-md-6 col-lg-4` |
| 3 | `col-12 col-sm-6 col-lg-3` |
| 2 | `col-12 col-sm-6 col-lg-2` |
| other/invalid | `col-12` (default) |

### Security rules

- Все adapter-provided text values проходят через Jinja autoescaping.
- Ссылки (`href`) принимаются только internal: начинаются с `/` и не
  начинаются с `//`.
- Неизвестный или malformed block type рендерится как `degraded` block,
  а не вызывает crash.
- `layout` не меняет JSON API envelope и route behavior.
- Если adapter возвращает `layout` в payload, оно может оставаться внутри `data`; клиенты должны считать его optional presentation metadata.
- `/api/runs` сохраняет backward-compatible list contract: если adapter возвращает wrapper `{layout, runs}` или `{layout, items}`, API отдаёт список runs/items в `data`.
- Layout blocks не содержат и не допускают arbitrary HTML/JS.
