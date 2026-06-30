# INTEGRATION — подключение BeeUI к Bee-продуктам

## Назначение

Этот документ описывает, как Bee-продукты (`beecap`, `beeagent` и будущие) подключают BeeUI как embedded UI layer.

## Текущий статус

**Iteration 13.8** — Generic detail page template and render helper.

- BeeUI provides `render_beeui_detail_page()` product-neutral detail page renderer.
- Detail page supports section kinds: `key_value`, `text`, `table`, `links`.
- Detail page нормализует read-model, валидирует internal links, экранирует HTML.
- Detail page template использует общий BeeUI shell (theme, layout, locale, navigation, route prefix).
- Product routes могут вызывать `render_beeui_detail_page()` вместо ручной сборки HTML.
- Detail page не является JSON API endpoint и не меняет API contract.
- Detail page не добавляет keys в `config/settings.yml`.

**Iteration 13.7** — Locale-aware shell labels, language switcher and query-preserving navigation.

- Product-side `beeui.yml` может передавать localized shell labels.
- BeeUI resolves locale через allowlisted `?lang=`.
- BeeUI preserves locale в shell / navigation / page tabs / catalog, где это practically applicable.
- Product adapter по-прежнему владеет product-specific labels и semantics.
- Query, передаваемый в `get_page(page_id, query)`, остаётся untrusted input.
- Locale persistence не использует cookies, session или localStorage.

- Generic contract `ProductUiAdapter` существует в `src/beeui_module/adapters/`.
- `BeeCapFixtureAdapter` в `src/beeui_module/adapters/beecap.py` — только
  fixture/reference реализация.
- Реальный BeeCap adapter должен жить на стороне BeeCap (см. ниже).
- Embedded mount API (`create_beeui_app(adapter=...)`) реализован.
- Mount helper `mount_beeui(...)` реализован.
- Adapter принимается, валидируется и сохраняется в `app.state`.
- Adapter-backed product console реализован: `get_dashboard()`, `list_runs()`,
  `get_run(run_id)` и optional `get_venue_dashboard(venue_id)` вызываются из
  read-only HTML/JSON routes.
- Page route ownership (Iteration 13.5): `pages[].path`, navigation и tab href
  проверяются как safe internal paths. Пути продукта вроде `/venues/mrkt`,
  `/venues/binance`, `/modes/live`, `/hidra/binance`, `/likes/top` разрешены.
  Кто обслуживает страницу, определяет `pages[].route.mode`.
  `metadata` pages не регистрируются как concrete routes; для `/venues/mrkt`
  типичный режим — `metadata`, потому что запрос может обслуживаться существующим
  `/venues/{venue_id}`. Для новых product-owned pages можно использовать
  `route.mode: adapter`; для schema-only pages можно использовать
  `route.mode: configured`. Custom/configured/adapter route registration защищает
  BeeUI system-owned routes (`/health`, `/static`, `/api`, `/auth`, `/components`,
  `/login`, `/logout` и соответствующие system prefixes). BeeUI не хардкодит
  product namespaces и не знает семантику `venues`, `modes`, `hidra`, `likes`.
- После Iteration 13.7 product adapter может возвращать `chart` и `data_table`
  внутри adapter-backed `layout[]`.
- Product adapter владеет бизнес-метриками, временными периодами и
  ROP/Bitrix/BeeCap/BeeAgent semantics; BeeUI только рендерит нормализованный layout.
- `chart` и `data_table` работают в product console и custom adapter pages,
  если adapter возвращает их в `layout[]`.
- Chart asset локальный, без CDN.
- Links в `data_table` валидируются и префиксуются под route prefix / embedded mount.
- Adapter-backed artifact browser реализован: `adapter.list_artifacts(run_id)` и `adapter.read_artifact(run_id, artifact_id)` вызываются из read-only HTML/JSON routes.
- Artifact preview pipeline: `build_preview()` → JSON/JSONL/text/unsupported → redaction → безопасный render в escaped `<pre>`.
- Artifact routes требуют adapter; без adapter возвращают 503 unavailable state.
- При наличии adapter product console routes владеют `/` и `/runs`; без adapter сохраняется backward-compatible demo/schema mode.

## Архитектурная граница

```text
BeeCap (product side)
  └── src/beecap_module/interfaces/ui/
        ├── adapter.py       ← real BeeCapUiAdapter (not in BeeUI)
        ├── read_model.py    ← BeeCap read-model construction
        ├── custom_pages.py  ← optional custom page read-models for get_page()
        └── artifacts.py     ← BeeCap artifact helpers

        ↓ implements ProductUiAdapter protocol

BeeUI (framework side)
  ├── src/beeui_module/adapters/
  │   ├── base.py            ← ProductUiAdapter protocol + base class
  │   ├── envelopes.py       ← stable adapter result envelopes
  │   ├── errors.py          ← stable adapter errors
  │   ├── ids.py             ← safe ID validation
  │   └── beecap.py          ← fixture/reference adapter (NOT for production)
  │
  ├── src/beeui_module/web/app.py   ← create_beeui_app(...)
  └── config/beeui.yml              ← product-specific UI config (future)
```

Главное правило:

```text
BeeUI renders.
Product decides.
```

## Где должен жить реальный BeeCap adapter

Реальный `BeeCapUiAdapter` должен находиться в BeeCap repository, **не** в BeeUI.

Ожидаемое расположение:

```text
src/beecap_module/interfaces/ui/
  ├── adapter.py          ← BeeCapUiAdapter(ProductUiAdapterBase)
  ├── read_model.py       ← BeeCap read-model construction
  └── artifacts.py        ← artifact reading from BeeCap storage
```

BeeCap-side adapter отвечает за:

- reading BeeCap storage/artifacts;
- constructing read-models (dashboard, runs, artifacts);
- constructing custom page read-models;
- enforcing product-specific allowlists;
- owning product authority decisions;
- implementing optional `get_page(page_id, query)` for product-specific pages;
- treating `query` as untrusted input;
- owning `get_page()` semantics;
- not relying on BeeUI to infer semantics from path namespace;
- declaring route metadata for existing product console routes in product-side `beeui.yml`;
- returning product-neutral `layout[]`;
- constructing product-neutral chart and data table layout blocks;
- keeping product/business semantics outside BeeUI;
- passing only normalized presentation data to BeeUI;
- implementing bounded action callbacks (future scope).

## Что BeeUI не должен делать во время интеграции

- BeeUI не должен читать BeeCap storage/config напрямую.
- BeeUI не должен копировать trading/domain logic.
- BeeUI не должен выполнять broker/order/runtime calls.
- BeeUI не должен становиться вторым source of truth для product state.
- BeeUI не должен мутировать product artifacts через read-only routes.
- BeeUI не должен импортировать `beecap_module` напрямую.
- BeeUI не должен вычислять ROP/Bitrix/BeeCap/BeeAgent metrics.
- BeeUI не должен строить product-specific chart series самостоятельно.
- BeeUI не должен пробрасывать arbitrary chart JS/options от продукта.

## Текущий fixture adapter

`BeeCapFixtureAdapter` в `src/beeui_module/adapters/beecap.py` существует только для:

- проверки `ProductUiAdapter` contract на realistic BeeCap-shaped data;
- reference implementation для BeeCap-side adapter developers;
- integration tests без real BeeCap dependency.

Это **не** production adapter.

Он **не** делает следующее:

- читает BeeCap storage;
- реализует trading/profit/order logic;
- предоставляет route-level integration;
- заменяет будущий real `BeeCapUiAdapter`.

## Пример embedded config

Пример будущего BeeCap-specific `beeui.yml` находится здесь:

```text
examples/beecap_embedded/beeui.yml
```

Этот файл **не загружается в runtime**. Это только документация.

## Текущий embedded integration flow

### Через `create_beeui_app()`

```python
from beeui_module.web.app import create_beeui_app
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

### Через `mount_beeui()`

```python
from fastapi import FastAPI
from beeui_module.web.app import mount_beeui
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = FastAPI()

mount_beeui(
    app,
    path="/ui",
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

После mount маршруты BeeUI доступны под `/ui/`:

```text
/ui/
/ui/health
/ui/auth/csrf
/ui/static/...
/ui/components
/ui/runs
/ui/runs/{run_id}
/ui/venues/{venue_id}
/ui/<page-path> для route.mode: adapter
/ui/<page-path> для route.mode: configured
/ui/api/dashboard
/ui/api/runs
/ui/api/runs/{run_id}
/ui/api/venues/{venue_id}/dashboard
/ui/runs/{run_id}/artifacts
/ui/runs/{run_id}/artifacts/{artifact_id}
/ui/api/runs/{run_id}/artifacts
/ui/api/runs/{run_id}/artifacts/{artifact_id}
```

### Важные ограничения

- Adapter принимается, валидируется и сохраняется в `app.state.beeui_adapter`.
- Adapter-backed product console реализован в Iteration 12 (read-only HTML/JSON routes через adapter).
- `get_venue_dashboard(venue_id)` является optional method и при отсутствии
  возвращает explicit unavailable state.
- Adapter-backed artifact browser из Iteration 11 продолжает работать без
  изменения contract.
- Product metadata сохраняется в `app.state.beeui_product`.
- Demo mode (`create_beeui_app()` без аргументов) остаётся backward-compatible.
- BeeAgent adapter implementation остаётся future scope.
- `route.mode: metadata` не создаёт отдельный route.
- `route.mode: adapter` создаёт route и вызывает `adapter.get_page(page_id, query)`.
- `route.mode: configured` создаёт route и рендерит schema/config blocks.

## Page route ownership

Iteration 13.5 добавляет явный `pages[].route.mode`.

Product-specific page declaration остаётся в product-side `beeui.yml`:

```yaml
pages:
  - id: mrkt
    path: /venues/mrkt
    route:
      mode: metadata
    title: MRKT
    subtitle: Дашборд MRKT
    blocks: []

  - id: hidra_binance
    path: /hidra/binance
    route:
      mode: adapter
    title: Hidra Binance
    subtitle: Adapter-backed страница
    blocks: []

  - id: likes_top
    path: /likes/top
    route:
      mode: configured
    title: Likes
    subtitle: Configured страница
    blocks: []
```

Правила:

- `metadata` используется для navigation, title/subtitle, tabs и page metadata, но не создаёт concrete route;
- `adapter` создаёт route и вызывает `adapter.get_page(page_id, query)`;
- `configured` создаёт route и рендерит schema/config blocks;
- safe internal paths отделены от route registration;
- BeeUI system-owned routes защищены от shadowing;
- BeeUI не выводит смысл из path namespace.

Product adapter может реализовать:

```python
from typing import Mapping

def get_page(
    self,
    page_id: str,
    query: Mapping[str, str],
) -> AdapterResult | AdapterErrorResult:
    ...
```

Rules:

- method is optional;
- default `ProductUiAdapterBase.get_page()` returns unavailable;
- BeeUI passes `page_id` and query params;
- product adapter owns page semantics;
- BeeUI renders returned `layout[]`;
- BeeUI does not import product modules;
- BeeUI does not infer ROP/BeeCap/BeeAgent semantics;
- malformed payload degrades;
- payload is redacted before HTML rendering.

## Generic detail page integration (Iteration 13.8)

Product routes or adapter-backed custom pages can use the generic detail page
renderer instead of assembling HTML manually.

### Entrypoint

```python
from beeui_module.pages.detail import render_beeui_detail_page

response = render_beeui_detail_page(
    request=request,
    page=page_data,
    templates=templates,
    route_prefix=route_prefix,
    ui_config=ui_config,
    product_title=product_title,
    product_id=product_id,
)
```

### Detail page model

```python
page_data = {
    "page_id": "event_detail",
    "title": "Event detail",
    "subtitle": "Read-only details",
    "back_href": "/events",
    "warnings": [],
    "sections": [
        {
            "title": "Summary",
            "kind": "key_value",
            "items": [
                {"label": "Subject", "value": "..."},
            ],
        },
        {
            "title": "Preview",
            "kind": "text",
            "body": "...",
        },
        {
            "title": "Rows",
            "kind": "table",
            "columns": [{"key": "name", "label": "Name"}],
            "rows": [{"name": "Status", "value": "ok"}],
        },
        {
            "title": "Links",
            "kind": "links",
            "items": [{"label": "Open", "href": "/runs/run_001"}],
        },
    ],
}
```

### Normalization

The renderer normalizes the model before rendering:

- unsupported/malformed sections are safely omitted;
- missing values render as `n/a`;
- `back_href` and link hrefs are validated as safe internal paths;
- external/unsafe links are rendered as inert text;
- raw fields (`raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes`)
  are not implicitly rendered;
- text remains HTML-escaped (autoescape, no `|safe`).

### Template

Template: `src/beeui_module/web/templates/detail.html`.

Extends `base.html` with the same shell context (theme, layout, locale,
navigation, route prefix). No JS required. No external assets.

## Security notes / Замечания по безопасности

- Все adapter inputs (`run_id`, `venue_id`, `artifact_id`) валидируются через `beeui_module.adapters.ids`.
- `query`, передаваемый в `get_page()`, является untrusted input и должен обрабатываться product adapter как untrusted input.
- Adapter envelopes используют стабильный status `ok|partial|error`; исходные
  исключения не попадают в response.
- Product console JSON API использует стабильный read-only envelope
  `ok/api/read_only/data|error/warnings/meta`.
- Artifact API routes сохраняют существующий contract Iteration 11.
- Secrets не должны пересекать adapter boundary и попадать в BeeUI.
- Adapter custom page payload redacted before render.
- Custom pages are GET-only and read-only.
- No product callback is called for write/action semantics from custom pages.
- Write/action adapter methods недоступны по умолчанию.

### Auth/session/CSRF (Iteration 13)

- Auth-disabled mode (`auth.enabled: false`) — local/dev только.
- Auth-enabled mode требует:
  - `BEEUI_SESSION_SECRET` — для подписи session cookie;
  - `BEEUI_OPERATOR_TOKEN` — для operator role;
  - `BEEUI_ADMIN_TOKEN` — для admin role.
- Login создаёт signed session cookie (HMAC-SHA256, 24h expiry).
- CSRF token хранится в session cookie; передаётся через `X-CSRF-Token` header
  (API) или `csrf_token` form field (HTML).
- POST routes на config/action endpoints защищены auth + CSRF + role check.
- Product callbacks не вызываются до прохождения auth/CSRF.
- Secrets из `config/settings.yml` не попадают в HTML/API/logs.
