# INTEGRATION — подключение BeeUI к Bee-продуктам

## Назначение

Этот документ описывает, как Bee-продукты (`beecap`, `beeagent` и будущие) подключают BeeUI как embedded UI layer.

## Текущий статус

**Iteration 11** — Generic artifact browser v1.

- Generic `ProductUiAdapter` contract существует в `src/beeui_module/adapters/`.
- `BeeCapFixtureAdapter` в `src/beeui_module/adapters/beecap.py` — только fixture/reference implementation.
- Реальный BeeCap adapter должен жить на стороне BeeCap (см. ниже).
- Embedded mount API (`create_beeui_app(adapter=...)`) реализован.
- Mount helper `mount_beeui(...)` реализован.
- Adapter принимается, валидируется и сохраняется в `app.state`.
- Adapter-backed artifact browser реализован: `adapter.list_artifacts(run_id)` и `adapter.read_artifact(run_id, artifact_id)` вызываются из read-only HTML/JSON routes.
- Artifact preview pipeline: `build_preview()` → JSON/JSONL/text/unsupported → redaction → безопасный render в escaped `<pre>`.
- Artifact routes требуют adapter; без adapter возвращают 503 unavailable state.
- Это MVP integration path; adapter-backed dashboard/runs rendering остаётся future scope (Iteration 12+).

## Архитектурная граница

```text
BeeCap (product side)
  └── src/beecap_module/interfaces/ui/
        ├── adapter.py       ← real BeeCapUiAdapter (not in BeeUI)
        ├── read_model.py    ← BeeCap read-model construction
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
- enforcing product-specific allowlists;
- owning product authority decisions;
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

```
/ui/
/ui/health
/ui/static/...
/ui/components
/ui/runs/{run_id}/artifacts
/ui/runs/{run_id}/artifacts/{artifact_id}
/ui/api/runs/{run_id}/artifacts
/ui/api/runs/{run_id}/artifacts/{artifact_id}
```

### Важные ограничения

- Adapter принимается, валидируется и сохраняется в `app.state.beeui_adapter`.
- Adapter-backed artifact browser реализован в Iteration 11 (read-only HTML/JSON routes через adapter).
- Adapter-backed dashboard/runs rendering остаётся future scope (Iteration 12+).
- Product metadata сохраняется в `app.state.beeui_product`.
- Demo mode (`create_beeui_app()` без аргументов) остаётся backward-compatible.
- BeeAgent adapter implementation остаётся future scope.

## Security notes / Замечания по безопасности

- Все adapter inputs (`run_id`, `artifact_id`) валидируются через `beeui_module.adapters.ids`.
- Adapter envelopes используют стабильный status `ok|partial|error`; raw exceptions не попадают в response.
- Secrets не должны пересекать adapter boundary и попадать в BeeUI.
- Write/action adapter methods недоступны по умолчанию.
