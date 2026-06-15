# Веб-интерфейс

## Назначение

`beeui` — это переиспользуемый веб-фреймворк для Bee-продуктов.

Он предоставляет каноническую веб-поверхность, которую можно подключать к продуктам вроде:

- `beecap`;
- `beeagent`;
- будущие Bee-продукты.

Текущая реализованная основа после Iteration 13.4 включает:

- веб-приложение FastAPI;
- шаблоны Jinja2;
- продуктовую оболочку на основе Tabler;
- декларативные страницы и навигацию;
- переиспользуемые блоки панели;
- контролируемый resolver демонстрационных и статических данных;
- общий контракт `ProductUiAdapter` v0;
- совместимый с BeeCap fixture/reference-адаптер для проверки payload-структур BeeCap;
- встраиваемую фабрику приложения `create_beeui_app(...)` с поддержкой `config_path`, `product_id`, `product_title`, `adapter`;
- helper `mount_beeui(...)` для встраивания BeeUI в родительское приложение FastAPI;
- общие HTML-маршруты продуктовой консоли на основе адаптера через `ProductUiAdapter` (`/`, `/runs`, `/runs/{run_id}`, `/venues/{venue_id}` при наличии адаптера);
- рендеринг `layout[]` для страниц продуктовой консоли на основе адаптера;
- общие layout-блоки Tabler для панели, списка запусков, деталей запуска и страниц площадок;
- резервный `degraded`-рендеринг для некорректных и неподдерживаемых layout-блоков;
- расширенный набор adapter-backed layout блоков (Iteration 12.4):
  - `operator_hero` — системный snapshot с datagrid и primary links;
  - `venue_card` — компактная карточка площадки с items, alerts и links;
  - `kpi_grid` — responsive KPI stat cards с unit и hint;
  - `state_grid` — dense key/value state section;
  - `quick_links` — list group internal operator links;
  - `run_table` — операторская таблица с run/event/artifact columns;
- стабильный read-only JSON API envelope для маршрутов продуктовой консоли (`/api/dashboard`, `/api/runs`, `/api/runs/{run_id}`, `/api/venues/{venue_id}/dashboard`);
- общие HTML/API-маршруты браузера артефактов через `ProductUiAdapter`;
- предпросмотр JSON/JSONL/текста с ограниченными лимитами и placeholder редактирования секретов.
- реальные локальные скомпилированные CSS/JS-ресурсы `@tabler/core@1.4.0`;
- усиление визуального соответствия Tabler для продуктовой консоли на основе адаптера;
- attached page tabs card-рендеринг для страниц с `pages[].tabs`;
- generic Tabler-compatible рендеринг accordion toggle;
- варианты accordion управляются конфигом и используют inline SVG toggle-иконки;
- consistent page-body spacing через единый wrapper для всех render paths (dashboard, runs, custom pages, tabs);
- `kpi_grid.columns` — optional adapter-backed field (1..4) для compact KPI grids;
- generic layout group v1 — adapter-backed `type: group` с `direction: vertical`, bounded recursive children и nested `row row-cards` wrapper;
- тёмную вертикальную оболочку с локальным контекстом темы боковой панели;
- специфичный для BeeUI слой CSS-переопределений без повторной реализации примитивов сетки, карточек и таблиц Tabler.

`features.browser_artifact` включает/отключает Iteration 11 artifact browser HTML/API routes.
`features.api` остаётся зарезервированным для будущего stable BeeUI API contract и не отключает artifact browser API routes.

Реализованные обязанности:

- bounded config/admin/operator controls (protected POST route stubs);
- auth/session/CSRF layer (Iteration 13):
  - signed session cookie with configurable `Secure` flag (`cookie_secure`);
  - security headers baseline: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`.
- block sizing primitives (Iteration 13.1):
  - `width: 1..12` остаётся backward-compatible;
  - `span: 1..12` — прямой column span;
  - `size: S|M|L|XL` — именованный размер с заранее заданным mapping;
  - invalid значения в schema fail-fast;
  - malformed adapter-backed значения degrade to `col-12`.
- URL-driven Tabler tabs (Iteration 13.1):
  - `url_tabs` Jinja macro в `catalog_primitives.html`;
  - обычные `<a>` links с `href`;
  - active tab через query param `?tab=`;
  - invalid tab fallback к default item;
  - только safe internal links.
- locale seed (Iteration 13.1):
  - `locale.default` и `locale.available` в `config/schema.yml`;
  - `?lang=XX` override применяется только при allowlist;
  - invalid lang возвращается к default;
  - resolved `locale` пробрасывается в Jinja templates/context;
  - `<html lang="{{ locale|default('en') }}">`;
  - BeeUI не переводит product-specific строки.
- generic dashboard fallback cleanup (Iteration 13.1):
  - raw/debug technical payload in BeeUI accordion «Technical details»;
  - primary UX shows summary cards/KPIs/structured fields first.
- configurable component defaults (Iteration 13.2):
  - `components.tabs.variant` — global Tabler tabs variant (`default`, `reverse`, `fill`, `icons`, `fill_icons`, `dropdown`);
  - `components.accordion.variant` — global accordion variant (`default`, `flush`, `tabs`, `inverted`, `inverted_plus`, `icons`);
  - invalid variants fail fast; missing config uses safe defaults.
- page-level URL tabs (Iteration 13.2):
  - optional `pages[].tabs` config with variant, active_param, items;
  - URL-driven tab links with safe href validation;
  - active tab resolved from query param with allowlist fallback;
  - duplicate/unsafe tab items rejected during config validation.
- attached page tabs card contract (Iteration 13.3):
  - если page содержит `pages[].tabs`, tabs и page blocks рендерятся внутри одной `.card.beeui-page-tabs-card`;
  - структура: `.card-header` → `ul.nav.nav-tabs.card-header-tabs` → `.card-body` → `section[aria-label="Page blocks"]`;
  - page title/subtitle остаются снаружи card и рендерятся выше tabs;
  - pages без tabs продолжают рендерить blocks без `.beeui-page-tabs-card`;
  - tabs остаются URL-driven через обычные links, без JS-only pane contract.
- accordion primitive (Iteration 13.2):
  - `accordion` Jinja macro in `catalog_primitives.html`;
  - deterministic safe accordion ids;
  - generic Tabler/Bootstrap-compatible markup `accordion`, `accordion-item`, `accordion-header`, `accordion-button`, `accordion-button-toggle`, `accordion-collapse`;
  - inline SVG chevron / plus / icon toggle markup без external assets;
  - variant class mapping centralized in Python;
  - generic dashboard fallback uses the same reusable accordion primitive instead of raw `<details>`;
  - label `Technical details` относится к одному fallback item и не является отдельным BeeUI rendering contract.
- generic adapter-backed custom pages (Iteration 13.2):
  - non-reserved page paths from config register as adapter-backed GET routes;
  - `adapter.get_page(page_id, query)` called when adapter present;
  - returned `layout[]` rendered through existing generic layout renderer;
  - unavailable adapter renders explicit degraded state;
  - config validation rejects BeeUI-owned reserved paths like `/health`, `/api`, `/auth`, `/venues`, `/login`, `/logout`, `/static`, `/components`;
  - adapter-backed custom page registration additionally does not shadow `/` and `/runs`, because product console owns them when adapter is present;
  - route collisions rejected during registration.

Запланированные обязанности:

- foundation для будущего no-code dashboard builder.

`beeui` не является runtime engine.

Он не должен:

- исполнять торговую или agent/domain логику;
- принимать бизнес-решения;
- пересчитывать product state;
- вызывать broker/provider/runtime paths напрямую;
- мутировать product artifacts через read-only routes;
- становиться вторым source of truth.

Главное правило:

```text
BeeUI renders.
Product decides.
```

### Контракт attached page tabs card

Если page содержит `pages[].tabs`, BeeUI рендерит tabs и page blocks внутри
одной card. Tabs не выводятся отдельной standalone card перед blocks.

Структура:

- `.card.beeui-page-tabs-card`
- `.card-header`
- `ul.nav.nav-tabs.card-header-tabs`
- `.card-body`
- `section aria-label="Page blocks"`

Короткий HTML-фрагмент:

```html
<div class="card beeui-page-tabs-card">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs" role="tablist">...</ul>
  </div>
  <div class="card-body">
    <section aria-label="Page blocks">...</section>
  </div>
</div>
```

Правила:

- page title/subtitle остаются снаружи card и рендерятся выше tabs;
- если `pages[].tabs` отсутствует, page blocks рендерятся как раньше, без tabs-card;
- BeeUI не использует JS-only hidden panes для page tabs;
- navigation остаётся URL-driven через обычные links;
- `?tab=` определяет active state;
- invalid или disabled tab fallback остаётся прежним.

### Контракт accordion primitive

`accordion` является generic BeeUI primitive и не привязан к конкретному title
или product-specific fallback.

`Technical details` в dashboard fallback — это только label/content одного item.
Реализация accordion не содержит special-case для этого названия.

Базовая Tabler-compatible структура:

- `.accordion`
- `.accordion-item`
- `.accordion-header`
- `.accordion-button`
- `.accordion-button-toggle`
- inline SVG chevron / plus / icon
- `data-bs-toggle="collapse"`
- `aria-expanded`
- deterministic ids

Вариант берётся из `components.accordion.variant`.

| Variant | Фактические классы / поведение |
| --- | --- |
| `default` | `.accordion`, стандартный chevron toggle |
| `flush` | `.accordion.accordion-flush`, стандартный chevron toggle |
| `tabs` | `.accordion.accordion-tabs`, стандартный chevron toggle |
| `inverted` | `.accordion.accordion-inverted`, стандартный chevron toggle |
| `inverted_plus` | `.accordion.accordion-inverted.accordion-plus`, plus toggle |
| `icons` | `.accordion`, `accordion-button-icon` + стандартный chevron toggle |

Accordion markup использует локальные inline SVG и не требует external assets,
CDN, preview/demo Tabler scripts или tracking.

### Generic layout group v1

`type: group` — adapter-backed layout block для bounded nested Tabler compositions.

Поддерживается только в adapter-backed `layout[]`.

Payload:

```json
{
  "type": "group",
  "width": 6,
  "direction": "vertical",
  "children": [
    {
      "type": "metric_card",
      "title": "Storage",
      "value": "42",
      "width": 12
    }
  ]
}
```

Правила:

- `direction` сейчас поддерживает только `vertical`;
- missing/invalid `direction` нормализуется к `vertical`;
- `children` должен быть list для валидного group payload;
- missing/invalid `children` рендерится как `degraded` block;
- children рендерятся через существующий BeeUI layout renderer;
- group nesting bounded depth = 3;
- exceeded depth рендерится как `degraded` block;
- group не является schema/demo block type;
- group не является no-code builder.

### `kpi_grid.columns`

`kpi_grid.columns` — optional adapter-backed field.

| `columns` | CSS classes |
| --- | --- |
| `1` | `col-12` |
| `2` | `col-12 col-sm-6` |
| `3` | `col-12 col-sm-6 col-lg-4` |
| `4` | `col-12 col-sm-6 col-lg-3` |

Правила:

- missing `columns` → default `4`;
- invalid adapter value → default `4`;
- значение не пробрасывается как CSS class напрямую;
- field не поддерживается в schema/demo blocks.

## Source of truth

Текущий source of truth в demo mode:

- `config/settings.yml` как runtime/system config;
- `config/schema.yml` как declarative pages/navigation/theme/layout/blocks/data_sources schema;
- controlled `demo` / `static` data sources.

Source of truth для product integration после adapter wiring:

- product adapter contract;
- product-provided read-models;
- product artifacts, если они явно allowlisted adapter-ом;
- product-owned config validation callbacks;
- product-owned bounded action callbacks.

`beeui` не должен самостоятельно угадывать domain semantics из чужого `storage/`.

Например:

```text
beecap owns:
  MRKT cycles
  Binance rollout
  paper account
  trading artifacts
  runtime config validation

beeui owns:
  layout
  blocks
  tables
  links
  cards
  artifact viewer
  config UI shell
  API envelope
```

## Режимы интеграции

### Embedded mode

MVP integration mode.

```text
beecap process
  imports beeui
  creates BeeCapUiAdapter
  creates/mounts BeeUI FastAPI app
```

Плюсы:

- быстрее для MVP;
- один процесс;
- проще локальная разработка;
- проще auth/session;
- нет CORS/service discovery.

Минусы:

- каждый продукт запускает свой BeeUI instance;
- обновления BeeUI идут через dependency update.

### Standalone mode

Будущий integration mode.

```text
beeui service
  connects to beecap API
  connects to beeagent API
  renders multi-product UI
```

Плюсы:

- один UI service;
- можно сделать central operator dashboard;
- лучше подходит для будущего отдельного frontend.

Минусы:

- сложнее auth;
- CORS;
- service discovery;
- deployment complexity.

Решение:

```text
MVP: embedded.
Позже: standalone.
```

## Package layout

Canonical web implementation after Iteration 3 lives in `src/beeui_module/web/`.
Root-level `app.py` не является текущей точкой входа.
Templates/static находятся внутри `web/`.

```text
src/beeui_module/
  web/
    app.py
    templates/
      base.html
      page.html
      components/        # iteration 3 foundation
    static/
      css/beeui.css
      js/beeui.js
      vendor/tabler/     # real local compiled @tabler/core assets

  cli/
    main.py
    web.py
    doctor.py

  core/
    settings.py
    paths.py
    log.py
    version.py

  pages/                 # current declarative schema/config/router module
  blocks/                # current block registry, literal and resolver-backed renderers
  data/                  # current read-only demo/static data sources and selector resolver
  adapters/              # generic adapter contract v0 + BeeCap fixture/reference adapter
  artifacts/             # Iteration 11: artifact browser (models, preview, redaction, routes)
  api/                   # текущий helper для product console envelope
  auth/                  # Iteration 13: auth/session/CSRF boundary
  config_ui/             # будущий module
  theme/                 # будущий module
```

Правила:

- CLI must stay thin.
- Route/read-model/template logic must not accumulate under `src/beeui_module/cli/`.
- Templates/static are package-local to `src/beeui_module/web/templates/` and `src/beeui_module/web/static/`.
- Product-specific domain logic must not live in generic BeeUI renderers.
- `src/beeui_module/__init__.py` should stay lightweight.

## Public embedded API после Iteration 13.4

### `create_beeui_app()`

```python
from beeui_module.web.app import create_beeui_app

# Demo mode (backward-compatible)
app = create_beeui_app()

# Embedded mode with product metadata and adapter
app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=bee_cap_adapter,
    config_path="config/beeui.yml",
)
```

Параметры:

- `settings` — загруженный `dict` из `settings.yml` (опционально, иначе загружается автоматически).
- `ui_config` — готовый `BeeUiConfig` (опционально, иначе загружается из `config_path` или `config/schema.yml`).
- `config_path` — путь к product-specific `beeui.yml`.
- `product_id` — override для `settings.product.id` (не мутирует исходный `settings`).
- `product_title` — override для `settings.product.title` (не мутирует исходный `settings`).
- `adapter` — экземпляр product adapter, валидируется по `ProductUiAdapter` minimum protocol.

Adapter сохраняется в `app.state.beeui_adapter`. Product metadata сохраняется в `app.state.beeui_product`.

**Поведение:** adapter принимается и валидируется. При наличии adapter product console routes владеют `/` и `/runs`, а также включают read-only API routes для dashboard/runs/run detail/venue dashboard и generic custom pages для non-reserved config paths. Без adapter BeeUI остаётся backward-compatible и продолжает рендерить schema/demo pages.

После Iteration 13.4 product adapter может опционально реализовать:

```python
from typing import Mapping

def get_page(
    self,
    page_id: str,
    query: Mapping[str, str],
) -> AdapterResult | AdapterErrorResult: ...
```

### `mount_beeui()`

```python
from fastapi import FastAPI
from beeui_module.web.app import mount_beeui

parent = FastAPI()

mount_beeui(
    parent,
    path="/ui",
    product_id="beecap",
    product_title="BeeCap",
    adapter=bee_cap_adapter,
    config_path="config/beeui.yml",
)
```

Параметры:

- `app` — родительское FastAPI приложение.
- `path` — mount path (по умолчанию `/ui`). Валидируется: не пустой, не `/`, с leading `/`, без `..`, `//`, query/hash chars, без trailing slash.
- Остальные параметры передаются в `create_beeui_app()`.

Mount helper выполняет:

- создаёт дочернее приложение через `create_beeui_app(...)`;
- проверяет коллизию с существующими route родительского приложения;
- монтирует через `app.mount(path, child_app)`;
- возвращает родительское приложение.

После mount маршруты BeeUI доступны под указанным `path`:

```text
/ui/
/ui/health
/ui/static/...
/ui/components
/ui/runs
/ui/runs/{run_id}
/ui/venues/{venue_id}
/ui/auth/csrf
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

## Запуск

Локальный demo start:

```bash
./start.sh web
```

С явным host/port:

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Doctor:

```bash
./start.sh doctor
```

Ожидаемые MVP-команды:

```bash
./start.sh doctor
./start.sh web
```

В текущем MVP `web` читает `config/settings.yml` и `config/schema.yml`.

- `settings.yml` — runtime/system config.
- `schema.yml` — declarative pages/navigation/theme/layout/blocks/data_sources schema.

Отдельный `--config` не является текущим CLI contract.

---

## Product integration

### Текущая app factory после Iteration 12

App factory принимает `settings`, `ui_config`, `config_path`, product metadata и adapter. Generic `ProductUiAdapter` contract существует, `BeeCapFixtureAdapter` добавлен как fixture/reference adapter. Real BeeCap adapter должен жить в BeeCap repo.

Пример:

```python
from beeui_module.core.paths import settings_path, schema_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app

settings = load_settings(settings_path())
ui_config = load_beeui_config(schema_path())
app = create_beeui_app(settings=settings, ui_config=ui_config)
```

Generic `ProductUiAdapter` contract существует в `src/beeui_module/adapters/`. Adapter можно передать в `create_beeui_app(...)`; после Iteration 12 product console routes вызывают `get_dashboard()`, `list_runs()`, `get_run(run_id)` и optional `get_venue_dashboard(venue_id)`, а artifact browser routes продолжают вызывать `list_artifacts(run_id)` и `read_artifact(run_id, artifact_id)`.

### Контракт размещения schema/demo blocks (Iteration 12.5)

`config/schema.yml` (и product-side `beeui.yml`) содержит секцию `pages`, где
каждая страница может иметь `blocks[]`.

Поддерживаются два формата для элементов `pages[].blocks[]`:

#### 1. Block placement (существующий формат)

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - block: latest_run
        width: 3
```

- `block` (required, string): ссылка на ID объявленного top-level `blocks[]`.
  Проверяется against registry: `Unknown block reference` при отсутствии.
- `width` (required, int, 1–12): ширина блока в колонках Tabler grid.

#### 2. Page block reference (Iteration 12.5)

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - id: system_snapshot
        enabled: true
```

- `id` (required, string): safe identifier. Является product-side page/layout reference,
  **не обязан** существовать в top-level `blocks[]`. Product adapter/read_model
  владеет семантикой этих id.
- `enabled` (optional, bool, default `true`): если `false`, блок не рендерится.
- Ширина блока по умолчанию — `12` (полная ширина колонки).
- Неизвестные ключи отклоняются fail-fast.
- `id` валидируется как safe identifier (reject path traversal, unsafe chars).

Оба формата не могут быть смешаны в одном элементе. Source config не мутируется.

### Рендеринг layout blocks (Iteration 12.1 + 12.2)

Этот contract отличается от schema/demo blocks из `config/schema.yml`.

- schema/demo blocks используются для declarative pages в demo/schema mode;
- `layout[]` blocks приходят из product adapter и используются только в product console mode;
- BeeUI не вычисляет product metrics, а только рендерит переданную product adapter структуру.

Adapter-backed payloads могут содержать optional поле `layout`:
массив объектов, описывающих структуру dashboard-блоков.
При наличии `layout[]` HTML-страницы рендерят его как
Tabler dashboard grid с поддержкой `row row-deck row-cards`.

Generic layout renderer (`src/beeui_module/blocks/layout_renderer.py`)
нормализует и валидирует каждый block:

- неизвестный block type → `degraded` block;
- malformed block → `degraded` block;
- unsafe external ссылки → null (не рендерятся);
- invalid width → `col-12` default.

При отсутствии `layout` или пустом массиве используется существующий
generic fallback renderer (как в Iteration 12).

Iteration 12.2 — усиление визуального соответствия Tabler:

- BeeUI поставляет реальные локальные скомпилированные ресурсы
  `@tabler/core@1.4.0` (`tabler.min.css` и `tabler.min.js`) вместо
  самодельного подмножества совместимости;
- `beeui.css` загружается после Tabler и содержит только токены, оформление
  боковой панели и продуктовые улучшения BeeUI, не дублируя базовые классы
  сетки, карточек и таблиц;
- `kpi_strip` переведён со строчного выравнивания на статистические карточки
  (`.card.h-100` со значением `.h1` и подписью `.subheader`);
- все шаблоны layout-блоков используют совместимые с Tabler CSS-классы;
- для каждого типа блока добавлены тесты визуального контракта.

Страницы, поддерживающие layout rendering:

- `GET /` → `product_dashboard.html`
- `GET /runs` → `product_runs.html` (если adapter возвращает dict с layout)
- `GET /runs/{run_id}` → `product_run_detail.html`
- `GET /venues/{venue_id}` → `product_venue_dashboard.html`

Поддерживаемые block types описаны в `docs/API_CONTRACT.md`.

### BeeCap fixture adapter после Iteration 9

Iteration 9 добавляет `BeeCapFixtureAdapter` как тестовую/reference реализацию.

Он используется для проверки BeeCap-shaped dashboard/runs/artifact-reference payloads на соответствие generic `ProductUiAdapter` contract.

Это не production BeeCap integration и не читает BeeCap storage. Real `BeeCapUiAdapter` должен жить в BeeCap repository по пути `src/beecap_module/interfaces/ui/`.

Текущие ограничения остаются:

- BeeUI вызывает adapter только для read-only routes and does not mutate product state;
- product console uses only generic read-model methods:
  - `get_dashboard()`;
  - `list_runs()`;
  - `get_run(run_id)`;
  - `get_venue_dashboard(venue_id)` when implemented;
  - `list_artifacts(run_id)`;
  - `read_artifact(run_id, artifact_id)`;
- adapter-backed block data sources остаются future scope.

### Embedded API после Iteration 12

Фаза product integration использует небольшой app factory или mount helper.

Вариант через app factory:

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

Альтернативный mount form:

```python
from beeui_module.web.app import mount_beeui

mount_beeui(
    app,
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

### Контракт product adapter

Текущий adapter contract после Iteration 13.4:

```python
from typing import Mapping

class ProductUiAdapter:
    metadata: AdapterMetadata

    # required read-only methods
    def get_dashboard(self) -> AdapterResult | AdapterErrorResult: ...
    def list_runs(self) -> AdapterResult | AdapterErrorResult: ...
    def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...
    def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...
    def read_artifact(self, run_id: str, artifact_id: str) -> AdapterResult | AdapterErrorResult: ...
    def get_config_read_model(self) -> AdapterResult | AdapterErrorResult: ...

    # optional methods, unavailable by default in ProductUiAdapterBase
    def get_venue_dashboard(self, venue_id: str) -> AdapterResult | AdapterErrorResult: ...
    def get_page(
        self,
        page_id: str,
        query: Mapping[str, str],
    ) -> AdapterResult | AdapterErrorResult: ...
    def validate_config_candidate(self, candidate: dict) -> AdapterResult | AdapterErrorResult: ...
    def list_actions(self) -> AdapterResult | AdapterErrorResult: ...
    def preview_action(self, action_id: str, payload: dict) -> AdapterResult | AdapterErrorResult: ...
    def execute_action(self, action_id: str, payload: dict) -> AdapterResult | AdapterErrorResult: ...
```

Iteration 8 добавила generic contract и fake adapter tests.
Iteration 9 добавляет BeeCap fixture/reference adapter и BeeCap-shaped fixture tests.
Iteration 10 добавляет adapter injection в app factory и `mount_beeui(...)`.
Iteration 11 добавляет adapter-backed artifact browser routes.
Iteration 12 добавляет adapter-backed dashboard, runs, run detail, optional venue
dashboard и product console API envelope `beeui.v0`.
Iteration 13.2 добавляет optional `get_page(page_id, query)` для generic
adapter-backed custom pages.
Config apply/write, action execution и production BeeCap/BeeAgent adapters
остаются future scope.

Required read-only methods:

- `get_dashboard`;
- `list_runs`;
- `get_run`;
- `list_artifacts`;
- `read_artifact`;
- `get_config_read_model`.

Optional write/config/action methods are unavailable by default unless a product explicitly implements them later.
`get_venue_dashboard` также optional и при отсутствии возвращает explicit
unavailable state.
`get_page()` используется только для generic adapter-backed custom pages.
`ProductUiAdapterBase.get_page()` по умолчанию возвращает unavailable.
BeeUI трактует возвращённый payload как read-model, рендерит только `layout[]`,
редактирует payload перед HTML render и переводит malformed payload в degraded
state.

## BeeUI config

Текущий runtime config file:

```text
config/settings.yml
```

Пример:

```yaml
app:
  name: beeui
  environment: local

web:
  host: 127.0.0.1
  port: 8780
  open_browser: false
  route_prefix: ""
  cache_static: 3600

logging:
  clear_logs: true
  utc: true
  level: INFO
  file: logs/app.log

storage:
  enabled: true
  root: storage

security:
  html_autoescape: true
  assets_ext: false

product:
  mode: demo
  id: demo
  title: BeeUI Demo
  adapter: static

features:
  browser_artifact: false
  config_preview: false
  config_apply: false
  operator_actions: false
  api: false
```

Iteration 7 declarative UI schema example (`config/schema.yml`):

```yaml
app:
  title: BeeUI Demo
  product: demo
  logo_text: BeeUI
  theme:
    mode: dark
    primary: blue
    base: gray
    font: sans-serif
    radius: 1
    density: default
  layout:
    type: vertical
    container: xl
    sidebar:
      variant: dark
      collapsed: false
    navbar:
      enabled: false
      variant: default
      sticky: false
components:
  tabs:
    variant: fill
  accordion:
    variant: flush

navigation:
  - title: Workspace
    children:
      - title: Dashboard
        path: /
        icon: dashboard
      - title: Runs
        path: /runs
        icon: list
      - title: Reports
        disabled: true

data_sources:
  demo_dashboard:
    type: demo

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: demo_dashboard
    value_selector: dashboard.latest_run.id
    subtitle_selector: dashboard.latest_run.status

  runtime_status:
    type: status_card
    title: Runtime
    source: demo_dashboard
    status_selector: dashboard.runtime.status
    value_selector: dashboard.runtime.value

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks:
      - block: latest_run
        width: 6
      - block: runtime_status
        width: 6

  - id: runs
    path: /runs
    title: Runs
    subtitle: Placeholder page for future run overview
    blocks: []
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
        - id: queue
          title: Queue
          href: /rop?tab=queue
```

В Iteration 7 block values могут быть static/literal, а representative blocks
умеют получать read-only values из controlled `demo` и `static` sources через
stable resolver envelope. После Iteration 12 product console и artifact browser
routes используют adapter. Adapter-backed block data sources остаются future
scope и не относятся к уже реализованным product console routes.

Правила:

- config schema must be validated fail-fast;
- `app.title` and `app.product` are required;
- page `id` must be safe and unique;
- page paths must be unique;
- navigation paths must reference known page paths;
- allowed tabs variants: `default`, `reverse`, `fill`, `icons`, `fill_icons`, `dropdown`;
- allowed accordion variants: `default`, `flush`, `tabs`, `inverted`, `inverted_plus`, `icons`;
- invalid variant values fail-fast; missing config uses safe defaults;
- `pages[].tabs` supports `variant`, `active_param`, `items[]`, safe internal `href` and disabled tabs;
- duplicate tab ids rejected fail-fast;
- invalid active query falls back to first enabled tab;
- disabled tab cannot become active;
- route prefix applies automatically during render;
- reserved paths `/health`, `/api`, `/auth`, `/venues`, `/login`, `/logout`, `/static`, `/components` are rejected;
- reserved prefixes `/api/`, `/auth/`, `/venues/`, `/static/`, `/components/` are rejected;
- no arbitrary HTML/JS in config;
- top-level `blocks` is required and validated as mapping;
- top-level `data_sources` is optional and validated as mapping when present;
- pages place blocks with `pages[].blocks[].block` and `pages[].blocks[].width` (`1..12`);
- unknown block references/types and invalid renderer fields fail fast;
- selector-backed block fields require `source`;
- block `source` must reference a declared `data_sources` id;
- resolver-backed values are read-only and do not mutate source files;
- supported selector syntax is limited to identifiers, dot path and optional `[integer]` list indices;
- static source paths must be safe relative paths under the project root;
- no arbitrary HTML/JS/CSS-like fields are accepted in blocks.

## Политика Tabler shell

`beeui` использует Tabler как визуальную основу.
Shell использует реальные локальные скомпилированные ресурсы Tabler core без
демонстрационной телеметрии и ресурсов отслеживания.

Правила:

- по умолчанию используются локальные ресурсы;
- удалённые скрипты запрещены в production-шаблонах;
- демонстрационная телеметрия и скрипты не подключаются;
- отслеживание из Tabler preview не копируется;
- маркетинговые, спонсорские и демонстрационные блоки Tabler preview не поставляются;
- статические ресурсы должны входить в пакет или быть явно вендоризированы;
- CSS настраивается через контролируемые переменные темы, а не через произвольный пользовательский CSS.

BeeUI поставляет реальные локальные скомпилированные ресурсы
`@tabler/core@1.4.0` в `src/beeui_module/web/static/vendor/tabler/`.
Ресурсы предпросмотра, демонстрационные, маркетинговые и спонсорские ресурсы,
карты исходников и средства отслеживания не поставляются.

В production-шаблонах запрещены:

- удалённая телеметрия;
- `posthog`;
- `scripts.tabler.io`;
- `preview/js/demo`;
- `preview/css/demo`;
- непроверенные внешние CDN-скрипты.

Разрешены:

- локальные CSS/JS Tabler;
- локальные CSS/JS BeeUI;
- контролируемые логотипы и статические ресурсы продукта;
- необязательный CDN только для явно включённого и документированного режима разработки или демонстрации.

## Template primitives

Shared template primitives live in:

```text
src/beeui_module/web/templates/components/
```

Текущие implemented shell primitives:

- `sidebar`;
- `navbar`;
- `page_header`;
- `footer`;
- `empty_state`.

Текущие implemented block templates после Iteration 7:

- `metric_card`;
- `kpi_grid`;
- `status_card`;
- `table_card`;
- `links_card`;
- `alert_card`;
- `text_card`;
- `progress_card`.

Planned primitives for later iterations:

- `breadcrumbs`;
- `status_badge`;
- `degraded_block`;
- `source_link`;
- `artifact_links`;
- `json_viewer`;
- `chart_card`.

Resolver behavior for the current block/runtime contract:

- renderers receive resolved or degraded neutral payloads and do not need to know whether data came from literal config, demo source or static source;
- missing selector data degrades the block instead of crashing page rendering;
- Jinja autoescape remains enabled for resolved values.

Текущие block/status-card values:

- `ok`
- `warning`
- `error`
- `unknown`
- `partial`
- `degraded`
- `unavailable`
- `disabled`

Planned action-specific statuses include:

- `blocked`
- `allowed`
- `denied`

Contract boundary:

- template primitives must stay domain-neutral;
- product-specific labels may be passed via read-model/config;
- primitives must not read product storage directly;
- primitives must not call product APIs.

## Surface model

Ниже описана общая модель route families для BeeUI. Текущий фактический MVP route contract отдельно зафиксирован в разделе `MVP route contract`.

HTML routes:

- `/`
- `/pages/{page_id}` if enabled by config
- `/runs`
- `/runs/{run_id}`
- `/runs/{run_id}/artifacts`
- `/runs/{run_id}/artifacts/{artifact_id}`
- `/config`
- `/admin`
- `/login`
- `/logout`

JSON routes:

- `/api/dashboard`
- `/api/navigation`
- `/api/pages`
- `/api/pages/{page_id}`
- `/api/runs`
- `/api/runs/{run_id}`
- `/api/runs/{run_id}/artifacts`
- `/api/runs/{run_id}/artifacts/{artifact_id}`
- `/api/config/read-model`
- `/api/config/preview`
- `/api/config/apply`
- `/api/actions`
- `/api/actions/{action_id}`

Не все routes должны существовать в MVP.

Текущий набор маршрутов MVP после Iteration 13.4:

- `/`
- `/runs`
- `/runs/{run_id}`
- `/venues/{venue_id}`
- `/components`
- `/components/interface`
- `/components/forms`
- `/components/layout`
- `/components/extra`
- `/components/plugins`
- `/health`
- `/static/...`
- `/static/vendor/tabler/css/tabler.min.css`
- `/static/vendor/tabler/js/tabler.min.js`
- `/api/dashboard`
- `/api/runs`
- `/api/runs/{run_id}`
- `/api/venues/{venue_id}/dashboard`
- `/login`
- `/logout`
- `/auth/csrf`
- `/runs/{run_id}/artifacts`
- `/runs/{run_id}/artifacts/{artifact_id}`
- `/api/runs/{run_id}/artifacts`
- `/api/runs/{run_id}/artifacts/{artifact_id}`
- `/<configured-custom-page>` (adapter-backed custom page — requires adapter and non-reserved page path)

При наличии adapter product console routes владеют `/` и `/runs`. Без adapter сохраняется schema/demo mode.

Маршрут `/components/plugins` содержит только инертные заглушки каталога
компонентов. Полноценная интеграция плагинов и дополнений остаётся будущей
задачей. Интерфейс настройки темы и верхняя горизонтальная навигация остаются
будущими задачами. Auth/session/CSRF boundary и login/logout уже реализованы в
Iteration 13.

## Read-only model

GET routes are read-only by default.

GET routes must not:

- mutate product artifacts;
- mutate BeeUI config;
- mutate product config;
- call provider/broker/execution paths;
- trigger runtime;
- create new runtime state;
- write audit artifacts;
- repair corrupted artifacts silently.

Read-only responses should include:

```text
X-BeeUI-Read-Only: true
Cache-Control: no-store
```

For product-embedded mode, product may also add its own header, for example:

```text
X-BeeCap-Read-Only: true
```

## Bounded write actions

BeeUI уже поддерживает bounded mutating POST transport stubs для config/action routes.

Реализованные protected POST routes:

- `POST /api/config/preview` — protected preview transport stub;
- `POST /api/config/apply` — protected apply transport stub;
- `POST /api/actions/preview` — protected action preview transport stub;
- `POST /api/actions/execute` — protected action execute transport stub.

Правила:

- no arbitrary YAML editor;
- no secrets editing;
- no direct broker actions;
- no direct provider calls from BeeUI;
- no hidden runtime restart;
- every accepted/rejected write attempt must be auditable;
- product callback must own domain validation;
- BeeUI must not bypass product validation.
- BeeUI защищает transport boundary, а product adapter владеет config/action semantics.

## Текущий product console API и будущий frontend API

Product console routes Iteration 12 используют envelope `beeui.v0`.
Artifact API routes сохраняют существующий contract Iteration 11.
Отдельный frontend API `v1` остаётся будущим scope.

### Envelope

Success:

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

Error:

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

Правила:

- `api` равно `"beeui.v0"` для product console routes;
- `read_only` must be true for GET/read routes;
- errors use stable machine-readable `error.code`;
- raw exceptions must not leak to API response;
- secrets must not leak;
- missing/partial evidence must be explicit, not treated as zero.

## Dashboard read-model

Generic dashboard payload shape:

```json
{
  "status": "available",
  "product": {
    "id": "beecap",
    "title": "BeeCap"
  },
  "kpis": [],
  "sections": [],
  "attention_items": [],
  "links": [],
  "warnings": [],
  "source": {
    "adapter": "beecap",
    "generated_at_utc": "2026-05-30T00:00:00Z"
  }
}
```

### Форма KPI object

```json
{
  "id": "latest_run",
  "label": "Latest Run",
  "value": "run...abcd",
  "unit": null,
  "status": "ok",
  "hint": "Latest run discovered by product adapter",
  "source_run_id": "run_20260530_120000_abcd",
  "source_artifact": "run.json",
  "source_url": "/runs/run_20260530_120000_abcd",
  "updated_at": "2026-05-30T12:00:00Z"
}
```

Fields:

| Field             | Type               | Description                             |
| ----------------- | ------------------ | --------------------------------------- |
| `id`              | string             | Stable KPI id.                          |
| `label`           | string             | Human-readable label.                   |
| `value`           | string/number/null | Display value.                          |
| `unit`            | string/null        | Unit, if applicable.                    |
| `status`          | string             | UI status.                              |
| `hint`            | string/null        | Short explanation.                      |
| `source_run_id`   | string/null        | Product run id, if applicable.          |
| `source_artifact` | string/null        | Source artifact id/path, if applicable. |
| `source_url`      | string/null        | UI link to source.                      |
| `updated_at`      | string/null        | UTC timestamp, if available.            |

### Форма attention item

```json
{
  "severity": "warning",
  "title": "Missing artifact",
  "detail": "health.json is missing for latest run.",
  "source": "adapter.get_dashboard"
}
```

Allowed severity:

- `info`
- `warning`
- `error`

## Pages

Pages декларативны.

Page config after Iteration 7:

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks:
      - block: latest_run
        width: 6
      - block: runtime_status
        width: 6

  - id: runs
    path: /runs
    title: Runs
    subtitle: Placeholder page for future run overview
    blocks: []
```

Правила:

- page `id` must be unique;
- page `path` must be unique;
- page path must be safe;
- page cannot define arbitrary HTML;
- `pages[].blocks` is a list of placements;
- placement поддерживает `width`, `span`, `size`;
- `width` и `span` должны быть `1..12`;
- `size` должен быть `S|M|L|XL`;
- mixed sizing keys rejected fail-fast;
- placement с `block` должен ссылаться на существующий top-level `blocks` entry;
- `{id, enabled?}` page block refs поддерживаются для product-side references;
- pages with an empty `blocks` list render the shared empty state.

## Blocks

Block registry is implemented and supports both literal block values and resolver-backed values from controlled `demo` / `static` data sources.

Top-level literal block config:

```yaml
blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    value: run_demo_001
    subtitle: Static demo value

  runtime_status:
    type: status_card
    title: Runtime
    status: ok
    value: Ready
```

Top-level resolver-backed block config:

```yaml
data_sources:
  demo_dashboard:
    type: demo

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: demo_dashboard
    value_selector: dashboard.latest_run.id
    subtitle_selector: dashboard.latest_run.status
```

Page placement config:

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks:
      - block: latest_run
        width: 6
      - block: runtime_status
        width: 6
```

Implemented block types after Iteration 7:

- `metric_card`
- `kpi_grid`
- `status_card`
- `table_card`
- `links_card`
- `alert_card`
- `text_card`
- `progress_card`

Текущие ограничения:

- adapter-backed block data sources пока не реализованы;
- production HTTP sources are not available yet;
- blocks do not call product APIs;
- blocks do not read product storage directly;
- blocks do not render arbitrary HTML, CSS or JS.

Правила:

- block renderer is domain-neutral;
- block ids must be safe identifiers;
- block type must be one of the registered renderer types;
- unknown block references fail fast;
- unknown block types fail fast;
- unknown data source references fail fast;
- selector-backed block fields require `source`;
- display values accept scalar literals or resolved scalar/list payloads accepted by the target block type;
- invalid resolved payload degrades or errors the block without crashing page rendering;
- `links_card` accepts internal safe paths only;
- block text is rendered through Jinja autoescape;
- no Jinja expressions from config are evaluated;
- no arbitrary HTML/JS/CSS-like fields are accepted.

`url_tabs` — это template primitive для Tabler-compatible URL navigation, а не schema block type.
Schema block type `tabs` сейчас не реализован.

Запланированные block families:

- `artifact_table`
- `json_viewer`
- `chart_card`
- `action_card`
- `config_form`

Они требуют следующих adapter, artifact, config или action итераций и намеренно исключены из Iteration 7.

---

## Data resolver

Data resolver is implemented after Iteration 7 for controlled read-only `demo` and `static` YAML/JSON sources.
Adapter-backed block sources и production HTTP sources остаются будущим scope.

Selector example:

```yaml
value_selector: dashboard.latest_run.id
```

Правила:

- missing selector returns explicit degraded/partial state;
- selector errors must not crash whole page;
- nested selectors must not execute code;
- no template expression execution;
- no arbitrary Python eval;
- no Jinja expressions from config.

## Runs

После Iteration 12 `/runs` рендерит список запусков через
`adapter.list_runs()` при наличии adapter.

### `GET /runs`

Displays run list.

Generic columns:

- `Run`
- `Status`
- `Mode`
- `Venue`
- `Started`
- `Latest event`
- `Severity`
- `Artifacts`

Product may customize labels through read-model.

### `GET /api/runs`

Response:

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": [],
  "warnings": [],
  "meta": {}
}
```

Query filters пока не реализованы. Возможный future scope:

- `q`
- `status`
- `mode`
- `venue`
- `severity`

## Run detail

После Iteration 12 run detail доступен через HTML и product console API:

- `GET /runs/{run_id}`;
- `GET /api/runs/{run_id}`.

### `GET /runs/{run_id}`

Displays product run detail.

Generic sections:

- run header;
- status/health;
- latest events;
- key decisions/explain summary if adapter provides it;
- source artifacts;
- reports/linked evidence if adapter provides it;
- sanitized settings/config if adapter provides it.

Правила:

- `run_id` must pass safe validation;
- missing run must return 404;
- malformed product payload must render degraded state;
- detail page must not mutate artifacts.

### `GET /api/runs/{run_id}`

Response:

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": {
    "run_id": "run_...",
    "summary": {},
    "sections": [],
    "artifacts": []
  },
  "warnings": [],
  "meta": {}
}
```

## Artifact browser

Artifact browser реализован в Iteration 11. Product adapter владеет allowlist.

Artifact browser является generic, но product adapter владеет allowlist.

### Artifact list item shape

```json
{
  "artifact_id": "health",
  "label": "health.json",
  "path": "health.json",
  "type": "json",
  "exists": true,
  "size_bytes": 1024,
  "url": "/runs/run_.../artifacts/health"
}
```

Правила:

- `artifact_id` is not raw filesystem path unless product adapter explicitly makes it safe;
- product adapter must map `artifact_id` to safe source;
- no arbitrary relative paths;
- no path traversal;
- no absolute path access from URL;
- no hidden filesystem browsing.

### `GET /api/runs/{run_id}/artifacts` (Iteration 11)

Возвращает adapter artifact references через `adapter.list_artifacts(run_id)`.

Response использует existing adapter envelope:

```json
{
  "status": "ok",
  "data": [
    { "artifact_id": "report_json", "content_type": "application/json" },
    { "artifact_id": "log_txt", "content_type": "text/plain" }
  ],
  "warnings": [],
  "meta": { "product": "beecap", "run_id": "beecap_run_042" }
}
```

Error response при отсутствии adapter:

```json
{
  "status": "error",
  "error": {
    "code": "adapter_unavailable",
    "message": "Adapter is not available"
  }
}
```

Невалидный `run_id` возвращает 400 с error envelope.

### `GET /api/runs/{run_id}/artifacts/{artifact_id}` (Iteration 11)

Читает один allowlisted artifact через `adapter.read_artifact(run_id, artifact_id)` и применяет preview processing.

Поддерживаемые форматы:

- JSON;
- JSONL;
- text;
- metadata-only for unsupported/binary.

Response для JSON:

```json
{
  "status": "ok",
  "data": {
    "artifact_id": "summary_report",
    "content_type": "application/json",
    "preview_type": "json",
    "preview_data": { "score": 0.95, "status": "ok" },
    "truncated": false,
    "row_count": null,
    "row_warnings": [],
    "error": null,
    "metadata_only": false
  },
  "warnings": [],
  "meta": { "product": "beecap", "run_id": "beecap_run_042" }
}
```

JSONL response:

```json
{
  "status": "ok",
  "data": {
    "artifact_id": "data_jsonl",
    "content_type": "application/jsonl",
    "preview_type": "jsonl",
    "preview_data": [{ "id": 1 }, { "id": 2 }],
    "truncated": false,
    "row_count": 10,
    "row_warnings": ["Row 5: malformed JSONL row (Expecting value)"],
    "error": null,
    "metadata_only": false
  }
}
```

Поведение oversized artifact:

```json
{
  "status": "ok",
  "data": {
    "artifact_id": "large_file",
    "content_type": "application/json",
    "preview_type": "json",
    "preview_data": null,
    "truncated": false,
    "row_count": null,
    "row_warnings": [],
    "error": "Content exceeds maximum preview size",
    "metadata_only": true
  }
}
```

Лимиты:

- JSON/JSONL max bytes: 512 KB
- JSONL max rows: 500
- Text max chars: 100 000
- лимиты определены как constants в `src/beeui_module/artifacts/preview.py`

Правила:

- large artifacts return metadata-only with error message — не крашатся;
- malformed JSON returns error state, не crash;
- corrupted JSONL rows are row-level warnings, не crash;
- unsupported files return metadata-only with `preview_type: "unsupported"`;
- secrets are redacted via `redact_value()` / `redact_text()` placeholder;
- HTML templates render content inside escaped `<pre><code>` — no `|safe`.

## Config read-model

Config read-model UI/API routes запланированы для следующих config iterations. Iteration 13 уже реализует auth/session/CSRF boundary и protected POST stubs, но полноценный config read-model остаётся отдельной задачей.

BeeUI can provide generic config read-model UI if product adapter supports it.

## Будущий config UI

Config UI и `GET` read-model routes ниже ещё не реализованы как полный product-facing UI.

### `GET /config`

HTML bounded config view.

Shows:

- allowlisted editable keys;
- non-editable/system-owned fields;
- redacted/secrets-related fields;
- current config hash;
- validation preview controls.

Правила:

- no arbitrary YAML editor;
- no secrets values;
- no direct mutation through GET.

### `GET /api/config/read-model`

Response:

```json
{
  "ok": true,
  "api": "v1",
  "read_only": true,
  "data": {
    "source": "product_adapter",
    "config_hash": "abc123",
    "allowlist": {},
    "redacted_keys": [],
    "config_redacted": {}
  }
}
```

### `POST /api/config/preview`

Protected non-mutating validation preview transport stub.

Правила:

- validates in memory only;
- does not write config;
- does not write storage;
- delegates validation to product adapter;
- forbidden keys rejected;
- secrets rejected.
- BeeUI не определяет domain semantics preview.

### `POST /api/config/apply`

Protected bounded config apply transport stub.

Правила:

- only product-defined allowlisted keys;
- requires stale hash guard if product supports writable config;
- backup before successful write;
- audit for accepted/rejected attempts;
- no secrets editing;
- no arbitrary YAML editor;
- no hidden runtime restart.
- BeeUI не реализует product apply semantics самостоятельно.

Suggested audit artifact shape:

```json
{
  "change_id": "cfgchg_...",
  "ts_utc": "2026-05-30T00:00:00Z",
  "actor": "local_operator",
  "source": "beeui",
  "result": "accepted",
  "changed_keys": ["web.port"],
  "validation": {
    "status": "ok",
    "errors": []
  },
  "config_hash_before": "abc",
  "config_hash_after": "def",
  "backup_path": "storage/interfaces/config_revisions/cfgchg_.../settings.before.yml",
  "reject_reason": null
}
```

## Admin/support center

`/admin` is a generic support/admin center.

Назначение:

- show support links;
- show config change audit if adapter supports it;
- show operator action audit if adapter supports it;
- show diagnostics summaries if adapter supports it;
- show product integration status.

It is not a full admin platform.

Правила:

- GET routes are read-only;
- no separate admin app/service in MVP;
- no arbitrary filesystem browsing;
- no broker/runtime controls;
- graceful empty state if product does not support admin data.

Planned routes:

- `GET /admin`
- `GET /api/admin/summary`
- `GET /api/admin/config-changes`
- `GET /api/admin/operator-actions`
- `GET /api/admin/diagnostics`

## Actions

Action rendering/catalog UI остаются задачей следующих bounded action iterations. Iteration 13 уже реализует protected POST stubs для preview/execute, но каталог действий и execution semantics остаются на product side.

BeeUI can render bounded actions only if product adapter exposes them.

Action item shape:

```json
{
  "action_id": "operator_launch_preset",
  "label": "Launch allowed preset",
  "status": "blocked",
  "reason_code": "active_runtime_running",
  "reason": "An active runtime is already running.",
  "action_url": null,
  "requires_confirmation": true
}
```

Allowed statuses:

- `allowed`
- `blocked`
- `denied`
- `unavailable`

Правила:

- BeeUI must not invent product actions;
- product adapter owns action availability;
- product adapter owns execution;
- every mutating action must be audited;
- manual broker/provider actions are denied unless product explicitly exposes a bounded safe action.

## Theme

Theme schema is implemented in Iteration 4 as a controlled schema contract.
The template renders the validated `mode` value into `data-bs-theme` and into a `beeui-theme-mode-*` shell class.

Theme config:

```yaml
app:
  theme:
    mode: dark
    primary: blue
    base: gray
    font: sans-serif
    radius: 1
    density: default
```

Поддерживаемые fields:

- `mode`: `light | dark | auto`;
- `primary`: controlled color token;
- `font`: controlled font token;
- `radius`: small integer scale;
- `density`: controlled density token.

`mode: auto` — controlled schema token для будущей runtime/browser preference integration.
Текущий runtime сохраняет KISS behavior: безопасно рендерит `data-bs-theme="auto"` и `beeui-theme-mode-auto`, без `localStorage` persistence или client-side theme mutation.

Правила:

- no arbitrary CSS input in MVP;
- no user-provided JS;
- no unsafe CSS injection;
- product branding may include title/logo if configured safely;
- local static assets only unless explicitly reviewed.

## Security model

BeeUI must follow these rules:

- read-only by default;
- no runtime mutation through GET;
- no direct broker/provider calls;
- no secret leakage in HTML/API/logs;
- sanitized settings only;
- safe ID validation;
- bounded allowlist for artifact fetch;
- bounded product callbacks for write paths;
- CSRF protection for protected POST routes;
- secure session cookies when `auth.enabled: true`;
- no arbitrary template execution from config;
- no Jinja expressions from user config;
- no arbitrary YAML editor;
- no direct filesystem browser.

## Auth model

Auth/session/CSRF layer реализован в Iteration 13.

Текущие режимы:

- `auth.enabled: false` для explicit local/dev mode;
- `auth.enabled: true` для token/session mode.

Текущий contract:

- login/logout routes существуют;
- protected POST routes требуют auth role и CSRF;
- `cookie_secure` управляет флагом `Secure` у session cookie;
- session secret и role tokens передаются через runtime settings/env.

Roles:

- `viewer`;
- `operator`;
- `admin`.

Правила:

- auth disabled must be explicit;
- protected write routes require authenticated role;
- protected POST routes require CSRF token;
- no default tokens committed to repo;
- session secret from env/config outside repo.

## What BeeUI is not

BeeUI must not become:

- trading bot;
- agent runtime;
- broker console;
- provider API proxy;
- hidden orchestrator;
- arbitrary filesystem browser;
- arbitrary YAML editor;
- Retool clone in MVP;
- product-specific business logic dump.

BeeUI should not know what these mean internally:

- MRKT cycle profitability;
- Binance rollout gate;
- BeeAgent capability policy;
- ROP classification;
- Bitrix reconciliation;
- trading signal confidence.

It can render them if product adapter provides a normalized read-model.

## Будущий no-code builder

Будущий visual builder должен менять schema, а не templates.

Разрешённые будущие builder changes:

- enable/disable blocks;
- reorder blocks;
- change width;
- change page title;
- change nav item visibility;
- choose block type from registry;
- bind block to existing adapter source.

Forbidden:

- arbitrary HTML;
- arbitrary JS;
- arbitrary Python;
- arbitrary filesystem paths;
- arbitrary product API calls;
- editing secrets;
- bypassing product validation.

Builder flow:

```text
visual editor
  -> modifies beeui schema
  -> validates schema
  -> preview
  -> backup/audit
  -> apply
```

## Типовые сценарии оператора

Текущий сценарий после Iteration 13.4:

```text
1. BeeUI loads config/settings.yml.
2. BeeUI loads config/schema.yml or product-specific beeui.yml through config_path.
3. BeeUI validates schema fail-fast.
4. Product may pass adapter into create_beeui_app(...) or mount_beeui(...).
5. Adapter is validated and stored in app.state.beeui_adapter.
6. Product metadata is stored in app.state.beeui_product.
7. If adapter is present, product console routes call `get_dashboard()`, `list_runs()`, `get_run()` and optional `get_venue_dashboard()`.
8. Non-reserved configured custom pages call optional `get_page(page_id, query)`.
9. BeeUI resolves optional page tabs from config.
10. When tabs are configured, tabs render as attached card header and returned `layout[]` renders inside the attached card body.
11. Artifact routes call `list_artifacts()` and `read_artifact()`.
12. If adapter is absent, dashboard/runs continue to render schema/demo/static pages.
13. No product runtime/action/config mutation happens.
```

### 1. Открыть product dashboard

Текущий сценарий Iteration 13.1.

1. Product starts embedded BeeUI web app.
2. Operator opens `/`.
3. BeeUI calls product adapter `get_dashboard()`.
4. BeeUI рендерит adapter-backed product dashboard.

### 2. Проверить runs

Текущий сценарий Iteration 13.1.

1. Open `/runs`.
2. BeeUI calls product adapter `list_runs()`.
3. Operator opens `/runs/{run_id}`.
4. BeeUI calls `get_run(run_id)`.

### 3. Проверить venue dashboard

Текущий optional сценарий Iteration 13.1.

1. Open `/venues/{venue_id}` or `/api/venues/{venue_id}/dashboard`.
2. BeeUI calls optional `get_venue_dashboard(venue_id)`.
3. Если метод не реализован, BeeUI возвращает explicit unavailable state.

### Открыть adapter-backed custom page

Текущий сценарий Iteration 13.4.

1. Product declares a non-reserved page in `beeui.yml`.
2. Operator opens `/rop` or another configured page path.
3. BeeUI resolves optional page tabs from config.
4. BeeUI calls `adapter.get_page(page_id, query)`.
5. Product adapter returns read-model with optional `layout[]`.
6. If tabs are configured, BeeUI renders tabs as attached card header.
7. Returned `layout[]` renders inside the attached card body when tabs are configured.
8. BeeUI рендерит flat layout blocks и bounded `type: group` blocks через общий layout renderer.
9. BeeUI redacts payload and renders `layout[]` through generic layout renderer.
10. If adapter method is unavailable or payload is malformed, BeeUI renders explicit degraded state.

### 4. Проверить artifact

Текущий сценарий Iteration 11.

1. Open `/runs/{run_id}/artifacts`.
2. BeeUI calls `list_artifacts(run_id)`.
3. Open `/runs/{run_id}/artifacts/{artifact_id}` or `/api/runs/{run_id}/artifacts/{artifact_id}`.
4. BeeUI calls `read_artifact(run_id, artifact_id)`.
5. Product adapter resolves artifact safely.

### 4. Предпросмотр изменения config

Будущий сценарий (requires config UI iterations).

1. Open `/config`.
2. Select allowlisted key.
3. Submit preview.
4. BeeUI delegates validation to product adapter.
5. No file is written.

### 5. Применить bounded config change

Будущий сценарий (requires config apply and audit iterations).

1. Product exposes writable config support.
2. Operator submits allowlisted change.
3. BeeUI checks stale hash.
4. Product adapter validates candidate.
5. Backup and audit are written.
6. Product config remains canonical source of truth.

## MVP route contract

Текущий MVP route contract после Iteration 13.4:

- `GET /`
- `GET /runs`
- `GET /runs/{run_id}`
- `GET /venues/{venue_id}`
- `GET /components`
- `GET /components/interface`
- `GET /components/forms`
- `GET /components/layout`
- `GET /components/extra`
- `GET /components/plugins`
- `GET /health`
- `GET /static/...`
- `GET /static/vendor/tabler/css/tabler.min.css`
- `GET /static/vendor/tabler/js/tabler.min.js`
- `GET /api/dashboard`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/venues/{venue_id}/dashboard`
- `GET /login`
- `POST /login`
- `POST /logout`
- `GET /auth/csrf`
- `GET /runs/{run_id}/artifacts` (HTML artifact list — requires adapter)
- `GET /runs/{run_id}/artifacts/{artifact_id}` (HTML artifact preview — requires adapter)
- `GET /api/runs/{run_id}/artifacts` (JSON artifact list — requires adapter)
- `GET /api/runs/{run_id}/artifacts/{artifact_id}` (JSON artifact preview — requires adapter)
- `GET /<configured-custom-page>` (adapter-backed custom page — requires adapter and non-reserved page path)
- `POST /api/config/preview` (protected transport stub — requires feature flag and product callback)
- `POST /api/config/apply` (protected transport stub — requires feature flag and product callback)
- `POST /api/actions/preview` (protected transport stub — requires feature flag and product callback)
- `POST /api/actions/execute` (protected transport stub — requires feature flag and product callback)

Product console routes требуют adapter в `app.state.beeui_adapter` для adapter-backed mode. Без adapter BeeUI остаётся в schema/demo mode. Artifact routes по-прежнему требуют adapter и без него возвращают 503 с explicit unavailable state.
BeeUI реализует auth/session/CSRF boundary и transport stubs. Product adapter остаётся владельцем config/action domain semantics.

Stable read-only API envelope for product console routes:

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

Позже:

- полноценные `GET /config` и config read-model routes;
- полноценный action catalog UI/API;
- `/admin` support center;
- stable frontend API v1.

## Связанные документы

Текущие документы:

- `README.ru.md`
- `docs/API_CONTRACT.md`
- `docs/ROADMAP.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/COMPONENTS.md`
- `docs/WEB_UI.md`
- `docs/INTEGRATION.md`

Запланированные документы:

- `docs/THEME.md`
