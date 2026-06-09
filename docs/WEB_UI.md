# Веб-интерфейс

## Назначение

`beeui` — это переиспользуемый веб-фреймворк для Bee-продуктов.

Он предоставляет каноническую веб-поверхность, которую можно подключать к продуктам вроде:

- `beecap`;
- `beeagent`;
- будущие Bee-продукты.

Текущая реализованная основа после Iteration 12.2 включает:

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
- тёмную вертикальную оболочку с локальным контекстом темы боковой панели;
- специфичный для BeeUI слой CSS-переопределений без повторной реализации примитивов сетки, карточек и таблиц Tabler.

`features.browser_artifact` включает/отключает Iteration 11 artifact browser HTML/API routes.
`features.api` остаётся зарезервированным для будущего stable BeeUI API contract и не отключает artifact browser API routes.

Запланированные обязанности:

- bounded config/admin/operator controls;
- auth/session layer;
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
  auth/                  # будущий module
  config_ui/             # будущий module
  theme/                 # будущий module
```

Правила:

- CLI must stay thin.
- Route/read-model/template logic must not accumulate under `src/beeui_module/cli/`.
- Templates/static are package-local to `src/beeui_module/web/templates/` and `src/beeui_module/web/static/`.
- Product-specific domain logic must not live in generic BeeUI renderers.
- `src/beeui_module/__init__.py` should stay lightweight.

## Public embedded API после Iteration 12

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

**Поведение:** adapter принимается и валидируется. При наличии adapter product console routes владеют `/` и `/runs`, а также включают read-only API routes для dashboard/runs/run detail/venue dashboard. Без adapter BeeUI остаётся backward-compatible и продолжает рендерить schema/demo pages.

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

### Layout block rendering (Iteration 12.1 + 12.2)

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

### Product adapter contract

Текущий adapter contract после Iteration 12:

```python
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
- reserved paths `/health`, `/static`, `/static/...` are rejected;
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

## Tabler shell policy

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

Generic BeeUI surface ниже описывает запланированные route families. Текущий MVP route contract отдельно зафиксирован в разделе `MVP route contract`.
Route families ниже являются общей моделью surface. Текущий MVP route contract отдельно зафиксирован в разделе `MVP route contract`.

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

Текущий набор маршрутов MVP после Iteration 12.2:

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
- `/runs/{run_id}/artifacts`
- `/runs/{run_id}/artifacts/{artifact_id}`
- `/api/runs/{run_id}/artifacts`
- `/api/runs/{run_id}/artifacts/{artifact_id}`

При наличии adapter product console routes владеют `/` и `/runs`. Без adapter сохраняется schema/demo mode. Config/action routes остаются future scope.

Маршрут `/components/plugins` содержит только инертные заглушки каталога
компонентов. Полноценная интеграция плагинов и дополнений остаётся будущей
задачей. Интерфейс настройки темы, аутентификация, вход, восстановление пароля
и верхняя горизонтальная навигация также не реализованы и относятся к будущим
итерациям.

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

BeeUI may later support bounded mutating POST paths.

Examples:

- `POST /api/config/preview` — non-mutating validation preview;
- `POST /api/config/apply` — bounded config apply;
- `POST /api/actions/{action_id}` — bounded product action;
- `POST /api/index/rebuild` — optional read-model index rebuild.

Правила:

- no arbitrary YAML editor;
- no secrets editing;
- no direct broker actions;
- no direct provider calls from BeeUI;
- no hidden runtime restart;
- every accepted/rejected write attempt must be auditable;
- product callback must own domain validation;
- BeeUI must not bypass product validation.

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

### KPI object shape

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

### Attention item shape

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

Pages are declarative.

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
- each placement must reference an existing top-level `blocks` entry;
- each placement width must be an integer from `1` to `12`;
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

Запланированные block families:

- `artifact_table`
- `json_viewer`
- `chart_card`
- `action_card`
- `config_form`
- `tabs`

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

Config read-model UI/API routes запланированы для следующих config iterations. Optional adapter method contract существует, но Iteration 11 не реализует config/action routes.

BeeUI can provide generic config read-model UI if product adapter supports it.

## Будущий config UI

Config UI и перечисленные ниже config routes ещё не реализованы.

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

Non-mutating validation preview.

Правила:

- validates in memory only;
- does not write config;
- does not write storage;
- delegates validation to product adapter;
- forbidden keys rejected;
- secrets rejected.

### `POST /api/config/apply`

Bounded config apply.

Правила:

- only product-defined allowlisted keys;
- requires stale hash guard if product supports writable config;
- backup before successful write;
- audit for accepted/rejected attempts;
- no secrets editing;
- no arbitrary YAML editor;
- no hidden runtime restart.

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

Action rendering/execution запланированы для следующих bounded action iterations. Optional adapter method contract существует, но Iteration 11 не реализует config/action routes.

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
- CSRF protection for POST routes once auth is enabled;
- secure session cookies once auth is enabled;
- no arbitrary template execution from config;
- no Jinja expressions from user config;
- no arbitrary YAML editor;
- no direct filesystem browser.

## Auth model

Auth is not required for the current MVP, but BeeUI must be designed for it.

Planned auth modes:

- `disabled_local_dev`;
- `local_users`;
- future external auth.

Roles:

- `viewer`;
- `operator`;
- `admin`.

Правила:

- auth disabled must be explicit;
- write routes require authenticated role;
- POST routes require CSRF token;
- no default admin password committed to repo;
- password hashes only;
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

## Typical operator scenarios

Текущий сценарий после Iteration 12:

```text
1. BeeUI loads config/settings.yml.
2. BeeUI loads config/schema.yml or product-specific beeui.yml through config_path.
3. BeeUI validates schema fail-fast.
4. Product may pass adapter into create_beeui_app(...) or mount_beeui(...).
5. Adapter is validated and stored in app.state.beeui_adapter.
6. Product metadata is stored in app.state.beeui_product.
7. If adapter is present, product console routes call `get_dashboard()`, `list_runs()`, `get_run()` and optional `get_venue_dashboard()` through adapter.
8. Artifact routes call `list_artifacts()` and `read_artifact()` through adapter.
9. If adapter is absent, dashboard/runs continue to render schema/demo/static pages.
10. No product runtime/action/config mutation happens.
```

### 1. Open product dashboard

Текущий сценарий Iteration 12.

1. Product starts embedded BeeUI web app.
2. Operator opens `/`.
3. BeeUI calls product adapter `get_dashboard()`.
4. BeeUI рендерит adapter-backed product dashboard.

### 2. Inspect runs

Текущий сценарий Iteration 12.

1. Open `/runs`.
2. BeeUI calls product adapter `list_runs()`.
3. Operator opens `/runs/{run_id}`.
4. BeeUI calls `get_run(run_id)`.

### 3. Inspect venue dashboard

Текущий optional сценарий Iteration 12.

1. Open `/venues/{venue_id}` or `/api/venues/{venue_id}/dashboard`.
2. BeeUI calls optional `get_venue_dashboard(venue_id)`.
3. Если метод не реализован, BeeUI возвращает explicit unavailable state.

### 4. Inspect artifact

Текущий сценарий Iteration 11.

1. Open `/runs/{run_id}/artifacts`.
2. BeeUI calls `list_artifacts(run_id)`.
3. Open `/runs/{run_id}/artifacts/{artifact_id}` or `/api/runs/{run_id}/artifacts/{artifact_id}`.
4. BeeUI calls `read_artifact(run_id, artifact_id)`.
5. Product adapter resolves artifact safely.

### 4. Preview config change

Будущий сценарий (requires config UI iterations).

1. Open `/config`.
2. Select allowlisted key.
3. Submit preview.
4. BeeUI delegates validation to product adapter.
5. No file is written.

### 5. Apply bounded config change

Будущий сценарий (requires config apply and audit iterations).

1. Product exposes writable config support.
2. Operator submits allowlisted change.
3. BeeUI checks stale hash.
4. Product adapter validates candidate.
5. Backup and audit are written.
6. Product config remains canonical source of truth.

## MVP route contract

Текущий MVP route contract Iteration 12:

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
- `GET /runs/{run_id}/artifacts` (HTML artifact list — requires adapter)
- `GET /runs/{run_id}/artifacts/{artifact_id}` (HTML artifact preview — requires adapter)
- `GET /api/runs/{run_id}/artifacts` (JSON artifact list — requires adapter)
- `GET /api/runs/{run_id}/artifacts/{artifact_id}` (JSON artifact preview — requires adapter)

Product console routes требуют adapter в `app.state.beeui_adapter` для adapter-backed mode. Без adapter BeeUI остаётся в schema/demo mode. Artifact routes по-прежнему требуют adapter и без него возвращают 503 с explicit unavailable state.

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

- `/config`
- `/admin`
- `/api/config/*`
- `/api/actions/*`
- `/login`
- `/logout`

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
