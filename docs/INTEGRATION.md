# INTEGRATION — подключение BeeUI к Bee-продуктам

## Назначение

Этот документ описывает, как Bee-продукты (`beecap`, `beeagent` и будущие) подключают BeeUI как embedded UI layer.

## Текущий статус

**Iteration 13.2** — generic adapter-backed custom pages and configurable Tabler primitives.

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
- Adapter-backed custom pages (Iteration 13.2): optional `get_page(page_id, query)` метод,
  default base adapter возвращает unavailable. При наличии adapter, не-reserved
  страницы из `beeui.yml` рендерятся через `get_page()` с `layout[]` renderer.
  Reserved routes (`/health`, `/static`, `/api`, `/auth`, `/components`, `/login`,
  `/logout`, `/runs`, `/venues`, `/`) не перекрываются. `/` и `/runs`
  принадлежат product console при наличии adapter. `/auth` и `/auth/*` —
  BeeUI auth namespace и не должны перекрываться.
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
- returning product-neutral `layout[]`;
- implementing bounded action callbacks (future scope).

## Что BeeUI не должен делать во время интеграции

- BeeUI не должен читать BeeCap storage/config напрямую.
- BeeUI не должен копировать trading/domain logic.
- BeeUI не должен выполнять broker/order/runtime calls.
- BeeUI не должен становиться вторым source of truth для product state.
- BeeUI не должен мутировать product artifacts через read-only routes.
- BeeUI не должен импортировать `beecap_module` напрямую.

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
/ui/<configured-custom-page>
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
- Custom page route существует только если страница объявлена в `beeui.yml`, path non-reserved, а adapter реализует `get_page()`; иначе рендерится unavailable/degraded state.

## Adapter-backed custom pages

Iteration 13.2 добавляет optional custom page capability.

Product-specific page declaration stays in product-side `beeui.yml`:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title: ROP Dashboard
    subtitle: ROP operator dashboard
    blocks: []
    tabs:
      variant: fill
      active_param: tab
      items:
        - id: overview
          title: Overview
          href: /rop?tab=overview
```

Product adapter may implement:

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
