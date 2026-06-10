# BeeUI — переиспользуемый UI-фреймворк для Bee-продуктов

**BeeUI** — общий UI-фреймворк на Python для Bee-продуктов: `beecap`, `beeagent` и будущих модулей экосистемы Bee.

## Iteration 12.4

Текущий результат — расширение adapter-backed `layout[]` contract для
product-neutral operator console parity. BeeUI теперь поддерживает 17
adapter-backed типов блоков и отдельный `degraded` fallback.

В Iteration 12.4 добавлены:

- `operator_hero`;
- `venue_card`;
- `kpi_grid`;
- `state_grid`;
- `quick_links`;
- `run_table`.

Также обновлены:

- `mode_cards` — optional `href`, `latest`, `latest_href`;
- `attention_list` — severity `warning`, `error`, `info`, `ok`, `unknown`;
- `_display_value()` — безопасное отображение user-visible значений без `None`;
- `run_table` — строгий 12-column operator contract.

Полный объём Iteration 12.4 описан в `docs/ROADMAP.md`.

Уже работает:

- всё из Iteration 10: `create_beeui_app(...)`, `mount_beeui(...)`, adapter injection, product metadata, mount path validation;
- `uv sync --frozen --extra dev`;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh version`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- `import beeui_module`;
- schema-driven theme/layout/navigation в `config/schema.yml`;
- schema-driven literal и resolver-backed blocks в `config/schema.yml`;
- read-only `demo` data source;
- read-only `static` YAML/JSON data source;
- stable resolver envelope для controlled block value resolution;
- dashboard blocks рендерятся из top-level `blocks` и `pages[].blocks[]`;
- generic adapter contract package `src/beeui_module/adapters/`;
- stable adapter envelopes (`ok|partial|error`) and stable adapter errors;
- safe adapter ID helpers for `product_id`, `run_id`, `venue_id`, `artifact_id`, `action_id`;
- BeeCap-compatible fixture adapter `BeeCapFixtureAdapter`;
- controlled BeeCap-like fixtures under `tests/fixtures/beecap/`;
- BeeCap adapter fixture tests in `tests/test_beecap_adapter.py`;
- integration boundary docs in `docs/INTEGRATION.md`;
- embedded BeeCap example in `examples/beecap_embedded/beeui.yml`;
- `GET /api/dashboard` — JSON API dashboard envelope;
- `GET /runs` — HTML runs list через adapter when adapter is present;
- `GET /runs/{run_id}` — HTML run detail через adapter;
- `GET /api/runs` — JSON API runs list;
- `GET /api/runs/{run_id}` — JSON API run detail;
- `GET /venues/{venue_id}` — HTML venue dashboard через adapter;
- `GET /api/venues/{venue_id}/dashboard` — JSON API venue dashboard;
- `GET /runs/{run_id}/artifacts` — HTML список артефактов;
- `GET /runs/{run_id}/artifacts/{artifact_id}` — HTML preview артефакта;
- `GET /api/runs/{run_id}/artifacts` — JSON API список артефактов;
- `GET /api/runs/{run_id}/artifacts/{artifact_id}` — JSON API preview артефакта;
- JSON preview с redaction;
- JSONL preview до 500 строк с row-level warnings;
- text preview до 100 000 символов;
- unsupported/binary artifacts отображаются как metadata-only;
- malformed JSON/JSONL не ломают страницу/API;
- large JSON/JSONL preview ограничен 512 KB;
- safe `run_id` / `artifact_id` validation;
- redaction placeholder для `secret`, `token`, `password`, `api_key`, `api_secret`;
- доступ к артефактам идёт только через `ProductUiAdapter.list_artifacts()` и `ProductUiAdapter.read_artifact()`;
- при отсутствии adapter возвращается explicit 503 unavailable state;
- `features.browser_artifact` включает/отключает HTML/API artifact routes;
- `features.api` остаётся зарезервированным для будущего stable BeeUI API и не отключает artifact browser API routes;
- `create_beeui_app(settings, ui_config, *, config_path, product_id, product_title, adapter)`;
- `mount_beeui(parent_app, *, path, ...)` для встраивания BeeUI в родительское FastAPI приложение;
- `app.state.beeui_adapter` — сохранение adapter instance;
- `app.state.beeui_product` — сохранение product metadata;
- runtime-валидация adapter на соответствие минимальному протоколу `ProductUiAdapter`;
- валидация mount path (безопасный путь, без path traversal);
- проверка коллизии маршрутов при mount;
- embedded API тесты в `tests/test_embedded.py`;
- generic adapter-backed layout[] block renderer c 17 block types и degraded fallback;
- расширенный набор adapter-backed layout блоков (Iteration 12.4):
  - `operator_hero` — системный snapshot с datagrid и primary links;
  - `venue_card` — компактная карточка площадки с items, alerts и links;
  - `kpi_grid` — responsive KPI stat cards с unit и hint;
  - `state_grid` — dense key/value state section;
  - `quick_links` — list group internal operator links;
  - `run_table` — операторская таблица с run/event/artifact columns;
  - расширенный `mode_cards` с optional href/latest/latest_href;
  - улучшенный `attention_list` с поддержкой всех severity и n/a fallback;
  - helper `_display_value` для отображения значений без None;
- реальные локальные скомпилированные ресурсы ядра Tabler `@tabler/core@1.4.0`;
- локальные `tabler.min.css` / `tabler.min.js` без CDN, ресурсов предпросмотра и демонстрационных ресурсов, а также без отслеживания;
- вертикальная оболочка Tabler с локальным контекстом тёмной темы для боковой панели;
- слой переопределений BeeUI без дублирования базового Tabler-фреймворка для сетки, карточек, таблиц, кнопок и бейджей;
- прозрачный подвал и отсутствие белого переопределения поверхности в тёмном режиме;
- layout blocks рендерятся на `/`, `/runs`, `/runs/{run_id}`, `/venues/{venue_id}`;
- fallback to generic renderer when layout absent.

### Два block contract в BeeUI

BeeUI сейчас поддерживает два разных block contract.

#### 1. Schema/demo blocks

Используются в `config/schema.yml` для demo/schema mode и declarative pages.

Поддерживаемые adapter-backed `layout[]` типы:

- `hero_snapshot`;
- `metric_card`;
- `kpi_strip`;
- `venue_summary_grid`;
- `mode_cards`;
- `status_table`;
- `event_table`;
- `attention_list`;
- `artifact_links`;
- `raw_json_panel`;
- `chart`;
- `operator_hero`;
- `venue_card`;
- `kpi_grid`;
- `state_grid`;
- `quick_links`;
- `run_table`.

`degraded` используется как fallback для malformed или unsupported blocks.

Эти blocks объявляются в top-level `blocks` и размещаются через `pages[].blocks[]`.

`pages[].blocks[]` поддерживает два формата (Iteration 12.5):

- `{block, width}` — placement с указанием ширины (колонки 1–12);
- `{id, enabled?}` — page block reference без ширины (по умолчанию col-12).

#### 2. Adapter-backed `layout[]` blocks

Используются в product console mode, когда product adapter возвращает optional поле `layout`.

Поддерживаемые типы:

- `hero_snapshot`;
- `metric_card`;
- `kpi_strip`;
- `venue_summary_grid`;
- `mode_cards`;
- `status_table`;
- `event_table`;
- `attention_list`;
- `artifact_links`;
- `raw_json_panel`.

Malformed или unsupported blocks рендерятся как `degraded` block, а не ломают страницу.

Текущая web surface после Iteration 12.2:

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
- `GET /runs/{run_id}/artifacts`
- `GET /runs/{run_id}/artifacts/{artifact_id}`
- `GET /api/runs/{run_id}/artifacts`
- `GET /api/runs/{run_id}/artifacts/{artifact_id}`

При использовании `mount_beeui(parent, path="/ui")` маршруты доступны под `/ui/`:

- `GET /ui/`
- `GET /ui/health`
- `GET /ui/static/...`
- `GET /ui/runs`
- `GET /ui/runs/{run_id}`
- `GET /ui/venues/{venue_id}`
- `GET /ui/api/dashboard`
- `GET /ui/api/runs`
- `GET /ui/api/runs/{run_id}`
- `GET /ui/api/venues/{venue_id}/dashboard`
- `GET /ui/runs/{run_id}/artifacts`
- `GET /ui/runs/{run_id}/artifacts/{artifact_id}`
- `GET /ui/api/runs/{run_id}/artifacts`
- `GET /ui/api/runs/{run_id}/artifacts/{artifact_id}`

При наличии adapter product console routes владеют `/` и `/runs`; без adapter сохраняется demo/schema mode. Config/actions остаются future scope.

Shell и dashboard рендерятся через component templates:

- `components/sidebar.html`;
- `components/navbar.html`;
- `components/page_header.html`;
- `components/footer.html`;
- `components/empty_state.html`.
- block component templates для literal и resolver-backed dashboard blocks.

Tabler core vendor assets поставляются локально из package path:

- `src/beeui_module/web/static/vendor/tabler/css/tabler.min.css`
- `src/beeui_module/web/static/vendor/tabler/js/tabler.min.js`
- `src/beeui_module/web/static/vendor/tabler/LICENSE`

Assets взяты из official `@tabler/core@1.4.0` npm dist. BeeUI не требует
Node/npm во время установки или runtime. Preview/demo/marketing/sponsor,
source maps и tracking assets не поставляются.

Navigation, theme и layout shell options (title/subtitle/paths/logo_text/theme/layout) рендерятся из `config/schema.yml`.

Пока не входит в scope:

- production BeeCap/BeeAgent adapters;
- stable BeeUI API для config/actions;
- auth/session;
- config UI;
- no-code builder.

Проект нужен, чтобы не писать заново в каждом продукте:

- web shell;
- sidebar / navbar / layout;
- dashboard;
- KPI cards;
- tables;
- artifact browser;
- config UI;
- operator/admin pages;
- theme customization;
- bounded operator actions;
- стабильный read-only JSON API для будущего frontend.

BeeUI строится как reusable layer поверх:

- **FastAPI** — web runtime;
- **Jinja2** — server-rendered HTML templates;
- **Tabler** — UI/admin visual foundation;
- **Pydantic / dataclasses** — schema/config/read-model contracts;
- **file/API adapters** — подключение к Bee-продуктам.

BeeUI не является trading engine, agent runtime или backend core. Он не принимает domain-решения и не получает прямую execution authority.

Главное правило:

```text
BeeUI renders.
Product decides.
```

## Зачем нужен BeeUI

Сейчас `beecap` и `beeagent` начинают дублировать один и тот же UI-слой:

- разные web directories;
- разные templates;
- разные CSS;
- разные dashboards;
- разные artifact viewers;
- разные admin/config pages;
- разные operator controls.

Это быстро превращается в хаос.

BeeUI решает эту проблему как общий UI/runtime package:

```text
beecap
  -> exposes read-model / artifacts / bounded actions
  -> BeeUI renders dashboard, runs, artifacts, config/admin pages

beeagent
  -> exposes modules / runs / capabilities / artifacts
  -> BeeUI renders operator console and будущий frontend shell
```

## Текущий фокус проекта

Текущий фокус BeeUI:

- быстро дойти до MVP;
- подключить `beecap` как первый продукт;
- перестать расширять кастомный web UI внутри `beecap`;
- затем подключить `beeagent`;
- сохранить KISS, безопасность и read-only по умолчанию;
- подготовить основу для будущего no-code dashboard/frontend builder.

MVP не пытается сразу стать полноценным Retool/Webflow/Admin SaaS.

Целевой MVP делает controlled declarative console:

- pages описываются через schema/config;
- blocks описываются через schema/config;
- данные приходят из product adapter;
- artifacts отображаются через bounded artifact browser;
- write/control actions идут только через product-owned callbacks.

## Что BeeUI делает

В текущем состоянии после Iteration 12.4 BeeUI отвечает за:

- FastAPI app factory;
- Jinja2 templates;
- Tabler layout;
- global navigation;
- reusable blocks;
- dashboard rendering for schema/demo mode and adapter-backed product console mode;
- adapter-backed `layout[]` rendering для product console pages через generic Tabler blocks;
- declarative pages/navigation/theme/layout;
- static/literal and resolver-backed dashboard blocks from `config/schema.yml`;
- generic product adapter contract v0 in `src/beeui_module/adapters/`;
- BeeCap-compatible fixture/reference adapter for contract validation;
- embedded app factory `create_beeui_app(...)`;
- mount helper `mount_beeui(...)`;
- загрузку product-specific UI config через `config_path`;
- product metadata injection;
- adapter injection, validation и сохранение в `app.state.beeui_adapter`;
- сохранение product metadata в `app.state.beeui_product`;
- проверку mount path и route collision guard;
- product console — HTML/JSON dashboard, runs, run detail и venue dashboard через adapter;
- artifact browser — HTML/JSON list and preview через adapter;
- JSON/JSONL/text bounded preview с malformed handling, preview limits и redaction;
- stable read-only API envelope для product console routes и read-only API routes для артефактов.

Запланированные обязанности:

- source artifact links;
- config read-model;
- config preview/apply framework;
- bounded operator actions;
- auth/session layer;
- theme customization;
- stable JSON API для будущего frontend;
- standalone mode.

## Чего BeeUI не делает

BeeUI не должен:

- принимать торговые решения;
- запускать broker/API calls напрямую;
- читать secrets;
- менять runtime state без product callback;
- самостоятельно парсить domain logic BeeCap/BeeAgent;
- становиться вторым source of truth;
- заменять `config/settings.yml` продукта;
- заменять `storage/` artifacts продукта;
- исполнять live/broker actions;
- делать hidden fallback execution;
- обходить product validation/security boundaries.

Все domain-sensitive вещи остаются в продукте.

## Интеграционная модель

### MVP: embedded mode

Для MVP BeeUI подключается как dependency внутрь продукта.

```text
beecap process
  imports beeui
  creates BeeCapUiAdapter
  mounts BeeUI FastAPI app
```

Для BeeAgent это пока будущий scope. Целевая структура может быть похожей:

```text
beeagent process
  imports beeui
  creates BeeAgentUiAdapter
  mounts BeeUI FastAPI app
```

Плюсы:

- быстро;
- один процесс;
- проще локальная разработка;
- проще auth/session;
- нет CORS;
- нет отдельного service discovery;
- меньше deployment complexity.

Минусы:

- каждый продукт запускает свой BeeUI instance;
- обновление BeeUI идёт через dependency update.

### Будущий `standalone` mode

Позже BeeUI сможет работать отдельным сервисом:

```text
beeui service
  -> connects to beecap API
  -> connects to beeagent API
  -> renders multi-product UI
```

Плюсы:

- один UI service;
- можно сделать unified Bee dashboard;
- проще отдельный frontend;
- можно держать `beecap` и `beeagent` как backend/API services.

Минусы:

- сложнее auth;
- CORS;
- network timeouts;
- service discovery;
- deployment complexity.

Решение:

```text
MVP: embedded.
Позже: standalone.
```

## Как подключать к BeeCap

На этапе разработки `beeui` лежит рядом:

```text
~/Projects/
  beecap/
  beeagent/
  beeui/
```

В `beecap/pyproject.toml` для локальной разработки:

```toml
dependencies = [
    "beeui @ file:///home/bee/Projects/beeui",
]
```

Или временно:

```bash
cd ~/Projects/beecap
uv pip install -e ../beeui
```

Целевой вариант после стабилизации:

```toml
dependencies = [
    "beeui @ git+ssh://git@github.com/beesyst/beeui.git@v0.1.0",
]
```

Минимальный integration point в BeeCap:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  actions.py
```

BeeCap adapter отвечает за:

- dashboard read-model;
- runs list;
- run detail;
- artifact allowlist;
- artifact reading;
- config read-model;
- config validation callback;
- bounded action callbacks.

BeeUI не должен напрямую знать внутреннюю trading-логику BeeCap.

## Как подключать к BeeAgent

BeeAgent integration — будущий scope. Ниже оставлена только минимальная целевая структура, чтобы не создавать впечатление готовой реализации.

Целевой integration point:

```text
src/beeagent_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  capabilities.py
  actions.py
```

BeeAgent adapter отвечает за:

- dashboard read-model;
- modules;
- runs;
- artifacts;
- capabilities;
- approvals;
- bounded actions;
- authority/capability checks.

BeeUI не должен получать прямую authority на tools/MCP/runtime actions.

## Режимы работы BeeUI

### `demo`

Локальный demo mode.

Используется для разработки BeeUI без BeeCap/BeeAgent.

```bash
./start.sh web
```

Вариант с явным host/port:

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Что показывает:

- schema-driven demo pages;
- schema-driven navigation;
- schema-driven theme/layout;
- static/literal и resolver-backed dashboard blocks из `config/schema.yml`;
- controlled read-only `demo` data source;
- controlled read-only `static` YAML/JSON data source;
- empty state для pages без block placements.

### `embedded`

Основное направление MVP integration.

Продукт импортирует BeeUI и монтирует его в своём web process.

Текущий статус после Iteration 12.2:

- generic adapter contract существует;
- BeeCap fixture/reference adapter существует для contract validation;
- production BeeCap adapter остаётся ответственностью BeeCap-side;
- `create_beeui_app(...)` accepts `config_path`, product metadata and adapter;
- `mount_beeui(...)` mounts BeeUI into parent FastAPI app;
- adapter is validated and stored in `app.state.beeui_adapter`;
- product metadata is stored in `app.state.beeui_product`;
- product console routes используют adapter для `get_dashboard()`, `list_runs()`, `get_run()` и optional `get_venue_dashboard()`;
- artifact browser routes уже используют adapter для `list_artifacts()` и `read_artifact()`;
- `/api/runs/{run_id}/artifacts*` routes доступны при `features.browser_artifact: true`;
- при наличии adapter routes `/`, `/runs`, `/runs/{run_id}` и `/venues/{venue_id}` работают в product console mode.

Embedded example:

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

### `standalone`

Будущий scope.

В текущем MVP standalone mode не реализован. Запуск с отдельным config-файлом будет добавлен позже, когда появится HTTP product adapter и standalone deployment contract.

## Основные возможности

### Declarative pages

Страницы задаются через config/schema.

```yaml
blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    value: run_demo_001
    subtitle: Static demo value

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks:
      - block: latest_run
        width: 3
```

Текущие declarative page rules:

- `page.id` must be unique;
- `page.path` must be unique;
- `navigation[].path` must reference declared page path;
- reserved paths `/health`, `/static`, `/static/...` are rejected;
- `blocks` in page config is a list of block placements;
- each placement references a top-level block id;
- `width` must be an integer from `1` to `12`;
- unknown block references are rejected fail-fast.

### Blocks

Текущий block contract после Iteration 7 поддерживает literal fields и resolver-backed fields из controlled read-only `demo` / `static` data sources.

Top-level `blocks` defines reusable block definitions.
`pages[].blocks[]` defines where these blocks appear on a page.

Сейчас поддерживаются типы блоков:

- `metric_card`;
- `kpi_grid`;
- `status_card`;
- `table_card`;
- `links_card`;
- `alert_card`;
- `text_card`;
- `progress_card`.

Пример:

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

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks:
      - block: latest_run
        width: 3
      - block: runtime_status
        width: 3
```

Текущие правила:

- block ids must be safe identifiers;
- unknown block types are rejected;
- unknown block references are rejected;
- renderer-specific fields are validated fail-fast;
- text values are rendered through Jinja autoescape;
- no arbitrary HTML/JS/CSS from config;
- `links_card.href` accepts internal safe paths only;
- display values may be literal scalars or resolver-backed values from controlled demo/static sources;
- missing/empty page placements render an empty state.

Реализовано в Iteration 7:

- read-only data resolver;
- selector syntax with dot path and optional `[index]` lookup;
- `demo` source;
- `static` YAML/JSON source;
- stable resolver envelope;
- degraded block rendering on missing selector data.

Пока не реализовано:

- production BeeCap/BeeAgent adapters;
- adapter-backed block data in runtime;
- charts/maps;
- artifact/config/action blocks;
- arbitrary HTML/JS blocks.

### Data sources

Iteration 7 поддерживает controlled read-only data sources в `config/schema.yml`.
Текущие supported source types:

- `demo`
- `static` with `format: yaml|json` and a safe relative `path`

Resolver envelope:

```json
{
  "status": "ok|partial|error",
  "data": {},
  "warnings": [
    {
      "code": "selector_missing",
      "message": "Selector not found: dashboard.latest_run.id"
    }
  ],
  "source": {
    "type": "demo|static|unknown",
    "id": "demo_dashboard"
  }
}
```

Текущая block schema остаётся backward-compatible: literal fields продолжают работать, resolver-backed fields опциональны.
Adapter-backed data sources остаются будущим scope и не входят в текущие runtime source types Iteration 7.

Resolver-backed block example:

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

Resolver envelope — внутренний block data-resolution contract в Iteration 7.
Он не является contract для product console `/api/*` routes.
Product console API использует отдельный envelope `beeui.v0`, а публичный `v1`
для отдельного frontend остаётся будущим scope.

### Product adapters

Product adapter contract реализован в Iteration 8 как generic boundary в `src/beeui_module/adapters/`.

Scope Iteration 8:

- generic `ProductUiAdapter` protocol/base contract;
- stable adapter envelopes for `ok|partial|error`;
- stable adapter error classes and error envelope helper;
- safe id validation helpers;
- optional write/action methods are disabled by default.

Non-goals Iteration 8:

- no production BeeCap adapter;
- no concrete BeeAgent adapter;
- no direct product filesystem crawling;
- public route surface не менялся в Iteration 8;
- no direct execution authority.

Iteration 9 добавляет BeeCap fixture/reference adapter support:

- `BeeCapFixtureAdapter` validates BeeCap-shaped dashboard/runs/artifact-reference payloads;
- fixtures live under `tests/fixtures/beecap/`;
- this adapter is not a production BeeCap integration;
- real BeeCap adapter must live on the BeeCap side under `src/beecap_module/interfaces/ui/`;
- Iteration 10 добавила app factory adapter injection и `mount_beeui(...)`;
- Iteration 11 добавила adapter-backed artifact browser routes;
- Iteration 12 добавила adapter-backed dashboard, runs, run detail, venue dashboard и stable read-only API envelope.

Iteration 12.1 добавляет optional presentation contract:

- product adapter может вернуть `layout[]` внутри dashboard/run/runs/venue payload;
- BeeUI рендерит `layout[]` через generic Tabler blocks;
- `layout[]` не является source of truth;
- product adapter остаётся владельцем product semantics;
- при отсутствии `layout[]` используется generic fallback renderer.

Текущий contract v0 после Iteration 12:

```python
class ProductUiAdapter:
  # required read-only
  def get_dashboard(self) -> AdapterResult | AdapterErrorResult: ...
  def list_runs(self) -> AdapterResult | AdapterErrorResult: ...
  def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...
  def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...
  def read_artifact(
      self,
      run_id: str,
      artifact_id: str,
  ) -> AdapterResult | AdapterErrorResult: ...
  def get_config_read_model(self) -> AdapterResult | AdapterErrorResult: ...

  # optional, unavailable by default
  def get_venue_dashboard(
      self,
      venue_id: str,
  ) -> AdapterResult | AdapterErrorResult: ...
  def validate_config_candidate(
      self,
      candidate: dict,
  ) -> AdapterResult | AdapterErrorResult: ...
  def list_actions(self) -> AdapterResult | AdapterErrorResult: ...
  def preview_action(
      self,
      action_id: str,
      payload: dict,
  ) -> AdapterResult | AdapterErrorResult: ...
  def execute_action(
      self,
      action_id: str,
      payload: dict,
  ) -> AdapterResult | AdapterErrorResult: ...
```

После Iteration 12 BeeUI вызывает adapter через embedded mount/app factory layer
для product console и artifact browser routes.

Product adapter решает, что можно читать/делать.

## Artifact browser

BeeUI предоставляет generic artifact browser после Iteration 11.

Он отображает:

- JSON;
- JSONL;
- text;
- metadata;
- parse warnings;
- source links;
- partial/corrupted state.

Правила:

- только allowlisted artifacts;
- никакого arbitrary filesystem browsing;
- path traversal заблокирован;
- source artifacts не мутируются;
- secrets redacted;
- corrupted artifacts не ломают page.

Routes:

```text
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

## Config UI

BeeUI должен дать reusable config UI layer, но не владеть config source of truth.

Source of truth остаётся в продукте:

```text
beecap/config/settings.yml
beeagent/config/settings.yml
```

BeeUI config UI работает через product adapter.

### Read-model

```text
GET /config
GET /api/config/read-model
```

Показывает:

- editable fields;
- non-editable fields;
- redacted fields;
- current values;
- validation metadata;
- constraints/options.

### Preview

```text
POST /api/config/preview
```

Semantics:

- build candidate config in memory;
- call product validation callback;
- return diff + validation result;
- no file writes.

### Apply

```text
POST /api/config/apply
```

Semantics:

- only allowlisted keys;
- stale config hash guard;
- validate candidate through product validation callback;
- backup current config;
- write canonical product config;
- create audit artifact;
- no secrets in audit;
- no runtime restart hidden behind apply.

Suggested artifacts:

```text
storage/interfaces/config_revisions/<change_id>/settings.before.yml
storage/interfaces/config_changes/<change_id>/audit.json
```

## Operator actions

BeeUI can show bounded operator actions, but action execution belongs to the product.

Example actions:

- start allowed preset;
- refresh index;
- run doctor;
- create report;
- open artifact;
- create draft;
- approve safe internal action.

Forbidden by default:

- broker manual order;
- direct live execution;
- secret editing;
- arbitrary shell command;
- arbitrary config mutation;
- runtime kill/restart unless product explicitly exposes bounded callback.

All action attempts should create audit artifacts:

```text
storage/interfaces/operator_actions/<action_id>.json
```

## Auth and roles

BeeUI auth layer запланирован после MVP dashboard integration.

Initial roles:

| Role       | Meaning                                            |
| ---------- | -------------------------------------------------- |
| `viewer`   | read-only UI access                                |
| `operator` | read-only + bounded allowed actions                |
| `admin`    | config/admin actions inside allowlisted boundaries |

Security rules:

- auth disabled only explicitly for local/dev;
- no default admin password in repo;
- password hash only;
- signed session cookies;
- CSRF protection for POST routes;
- no secrets in logs;
- no secrets in HTML/API.

## Theme customization

BeeUI theme config:

```yaml
app:
  theme:
    mode: dark
    primary: blue
    font: Inter
    radius: 2
    density: compact
```

Поддерживаемая кастомизация:

- dark/light;
- primary color;
- font family;
- border radius;
- density;
- product title;
- logo;
- favicon;
- compact mode.

Forbidden by default:

- arbitrary CSS editor;
- arbitrary JS;
- unsafe HTML injection;
- user-uploaded executable assets.

## Технологический стек

- **Python 3.14+**
- **src-layout** — пакет `beeui_module` в `src/`
- **FastAPI** — web runtime
- **Jinja2** — templates
- **Tabler** — dashboard/admin UI foundation
- **PyYAML** — config/schema files
- **pytest** — тесты
- **httpx** — web route tests
- **uv** — dependency/install/runtime workflow
- **file-based artifacts** — для audits/examples/demo
- **future**: optional standalone HTTP adapter

## Управление и запуск

Запуск — через `start.sh`.

### Установка

После clone:

```bash
git clone git@github.com:beesyst/beeui.git
cd beeui
./start.sh doctor
```

`start.sh`:

- проверяет наличие `uv`;
- если `uv` отсутствует — устанавливает его;
- ставит зависимости из `uv.lock`;
- запускает `config/start.py`;
- не должен скрыто менять runtime contracts.

### Команды

```bash
./start.sh doctor
```

Проверяет:

- Python version;
- package import;
- config files;
- templates/static availability;
- basic environment.

```bash
./start.sh web
```

Запускает demo BeeUI web app.

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Запускает demo web app на конкретном host/port.

```bash
./start.sh routes
```

Показывает registered routes.

```bash
./start.sh version
```

Показывает версию BeeUI.

---

## Локальная разработка

### Установка зависимостей

```bash
uv sync --frozen --extra dev
```

### Тесты

```bash
uv run pytest -q
```

### Запуск demo UI

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Открыть:

```text
http://127.0.0.1:8780
```

### Без `start.sh`

```bash
uv run --frozen --extra dev python config/start.py doctor
uv run --frozen --extra dev python config/start.py web
```

## Документация

Основная документация проекта находится в `docs/`.

Ключевые разделы:

- `docs/ROADMAP.md` — этапы и итерации;
- `docs/SDLC.md` — lightweight process, checks, PR workflow;
- `docs/SECURITY.md` — secure development rules;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;
- `docs/API_CONTRACT.md` — product console API envelope и граница artifact API.

## Целевая структура проекта

Актуальные ключевые файлы после Iteration 12.2:

```text
config/
  settings.yml
  schema.yml

docs/
  API_CONTRACT.md
  INTEGRATION.md

examples/
  beecap_embedded/
    beeui.yml

tests/
  fixtures/
    beecap/

src/beeui_module/
  blocks/
    __init__.py
    models.py
    registry.py
    renderers.py
  cli/
    doctor.py
    main.py
    web.py
  core/
    paths.py
    settings.py
    log.py
    version.py
  data/
    __init__.py
    models.py
    resolver.py
    selectors.py
    sources.py
  adapters/
    __init__.py
    base.py
    envelopes.py
    errors.py
    ids.py
    beecap.py
  artifacts/
    __init__.py
    models.py
    preview.py
    redaction.py
    routes.py
  api/
    __init__.py
    envelopes.py
  pages/
    config.py
    models.py
    product_console.py
    router.py
  web/
    app.py
    templates/
      base.html
      page.html
      product_dashboard.html
      product_runs.html
      product_run_detail.html
      product_venue_dashboard.html
      components/
        alert_card.html
        footer.html
        kpi_grid.html
        links_card.html
        metric_card.html
        navbar.html
        page_header.html
        progress_card.html
        sidebar.html
        status_card.html
        table_card.html
        text_card.html
        empty_state.html
      artifacts/
        list.html
        detail.html
    static/
      css/beeui.css
      js/beeui.js
      vendor/
        tabler/
          css/tabler.min.css
          js/tabler.min.js
```

Остальная структура ниже — целевая для следующих итераций.

```text
beeui/
├── config/
│   ├── settings.yml
│   └── start.py
│
├── docs/
│   ├── API_CONTRACT.md
│   ├── COMPONENTS.md
│   ├── INTEGRATION.md
│   ├── ROADMAP.md
│   ├── SDLC.md
│   ├── SECURITY.md
│   ├── THEME.md
│   └── WEB_UI.md
│
├── examples/
│   ├── demo_static/
│   ├── beecap_embedded/
│   └── beeagent_embedded/
│
├── logs/
│   └── app.log
│
├── src/
│   └── beeui_module/
│       ├── __init__.py
│       ├── config.py
│       ├── errors.py
│       ├── server.py
│       ├── settings.py
│       │
│       ├── api/
│       │   ├── envelopes.py
│       │   └── routes.py
│       │
│       ├── artifacts/
│       │   ├── browser.py
│       │   ├── models.py
│       │   ├── readers.py
│       │   └── safe_paths.py
│       │
│       ├── auth/
│       │   ├── models.py
│       │   ├── password.py
│       │   ├── permissions.py
│       │   ├── routes.py
│       │   ├── service.py
│       │   └── sessions.py
│       │
│       ├── adapters/
│       │   ├── base.py
│       │   ├── filesystem.py
│       │   ├── http.py
│       │   ├── product.py
│       │   ├── beecap.py
│       │   └── beeagent.py
│       │
│       ├── blocks/
│       │   ├── models.py
│       │   ├── registry.py
│       │   ├── renderers.py
│       │   └── types/
│       │       ├── artifact_table.py
│       │       ├── chart_card.py
│       │       ├── json_viewer.py
│       │       ├── kpi_grid.py
│       │       ├── links_card.py
│       │       ├── metric_card.py
│       │       ├── status_card.py
│       │       └── table_card.py
│       │
│       ├── cli/
│       │   ├── doctor.py
│       │   ├── main.py
│       │   └── web.py
│       │
│       ├── config_ui/
│       │   ├── apply.py
│       │   ├── audit.py
│       │   ├── preview.py
│       │   ├── read_model.py
│       │   └── routes.py
│       │
│       ├── core/
│       │   ├── ids.py
│       │   ├── json.py
│       │   ├── logging.py
│       │   ├── paths.py
│       │   └── security.py
│       │
│       ├── data/
│       │   ├── envelopes.py
│       │   ├── resolver.py
│       │   ├── selectors.py
│       │   └── sources.py
│       │
│       ├── pages/
│       │   ├── models.py
│       │   ├── registry.py
│       │   ├── renderer.py
│       │   └── router.py
│       │
│       ├── web/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── templates/
│       │   │   ├── base.html
│       │   │   └── page.html
│       │   └── static/
│       │       ├── css/
│       │       │   └── beeui.css
│       │       └── js/
│       │           └── beeui.js
│       │
│       └── theme/
│           ├── css.py
│           ├── models.py
│           └── service.py
│
├── tests/
│   ├── test_adapters.py
│   ├── test_app.py
│   ├── test_artifacts.py
│   ├── test_blocks.py
│   ├── test_config.py
│   ├── test_pages.py
│   ├── test_security.py
│   └── test_smoke.py
│
├── pyproject.toml
├── README.ru.md
├── start.sh
└── uv.lock
```

## Архитектура

### 1. App/Web layer

Отвечает за:

- FastAPI app factory;
- templates/static;
- routes;
- global layout;
- API routes;
- error pages.

Ключевые модули:

```text
src/beeui_module/web/app.py
src/beeui_module/web/templates/
src/beeui_module/web/static/
```

Planned after Iteration 2:

```text
src/beeui_module/server.py
src/beeui_module/pages/
```

### 2. Adapter layer

Отвечает за подключение к продуктам.

```text
src/beeui_module/adapters/
```

Типы adapters:

- `ProductUiAdapter` — base contract;
- `BeeCapUiAdapter` — BeeCap-specific read-model adapter;
- `BeeAgentUiAdapter` — BeeAgent-specific read-model adapter;
- `HttpProductAdapter` — будущий standalone mode;
- `FilesystemAdapter` — demo/local artifact reading.

### 3. Data resolver layer

Отвечает за:

- source lookup;
- selector resolution;
- partial data;
- warnings/errors;
- normalized envelopes.

```text
src/beeui_module/data/
```

### 4. Blocks layer

Отвечает за reusable UI blocks.

```text
src/beeui_module/blocks/
src/beeui_module/web/templates/components/
```

### 5. Artifact layer

Отвечает за safe artifact navigation.

```text
src/beeui_module/artifacts/
```

Security responsibilities:

- artifact allowlist;
- safe IDs;
- path traversal guard;
- JSON/JSONL tolerant parsing;
- redaction;
- no mutation.

### 6. Config UI layer

Отвечает за:

- config read-model;
- preview;
- apply;
- audit;
- backup.

```text
src/beeui_module/config_ui/
```

Важно:

- product config remains source of truth;
- product validation callback is mandatory for apply;
- BeeUI does not invent config semantics.

### 7. Auth layer

Planned layer.

```text
src/beeui_module/auth/
```

Отвечает за:

- users;
- sessions;
- roles;
- permissions;
- CSRF;
- route protection.

## JSON API contract

В Iteration 12 API contracts разделены:

- product console routes используют read-only envelope `beeui.v0`;
- artifact API routes сохраняют существующий Iteration 11 adapter/artifact envelope;
- отдельный frontend API `v1` ещё не реализован.

### Success

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

### Partial

Adapter result со статусом `partial` остаётся успешным:

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": {},
  "warnings": [],
  "meta": {
    "status": "partial"
  }
}
```

### Error

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

Подробный contract product console API описан в `docs/API_CONTRACT.md`.
Artifact API routes не переводились на `beeui.v0` и сохраняют contract
Iteration 11.

## Routes

### Текущая HTML surface

```text
GET /
GET /runs
GET /runs/{run_id}
GET /venues/{venue_id}
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
```

### Текущая API surface

```text
GET /api/dashboard
GET /api/runs
GET /api/runs/{run_id}
GET /api/venues/{venue_id}/dashboard
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

### Future scope

```text
GET /config
GET /admin
GET /login
GET /logout
GET /api/config/read-model
POST /api/config/preview
POST /api/config/apply
GET /api/actions
POST /api/actions/{action_id}
```

Routes can be mounted under prefix:

```text
/ui
/console
/admin
```

depending on product integration.

## Безопасность

BeeUI находится на trust boundary, потому что отображает:

- configs;
- artifacts;
- operator actions;
- diagnostics;
- product state;
- potential admin controls.

Правила безопасности:

- read-only by default;
- all IDs are untrusted input;
- path traversal guard everywhere;
- HTML autoescape enabled;
- no arbitrary HTML/JS blocks;
- artifact access allowlisted;
- config write allowlisted;
- action execution product-owned;
- secrets redacted in HTML/API/logs/audits;
- POST routes protected by CSRF when auth enabled;
- no direct broker/runtime authority;
- no hidden fallback from denied action to allowed action;
- no automatic runtime restart after config apply.

Особо запрещено:

- отдавать `.env`;
- отдавать raw secret values;
- читать arbitrary path из query param;
- делать direct shell commands из UI;
- делать live broker calls из BeeUI;
- писать runtime artifacts без product-owned action callback.

## MVP roadmap summary

Критический путь к MVP:

```text
Iteration 0 — Project skeleton and startup contract
Iteration 1 — Tabler web shell v0
Iteration 2 — Declarative pages and navigation v0
Iteration 3 — Local Tabler vendor/assets and layout parity v1
Iteration 4 — Theme, layout and navigation schema v1
Iteration 5 — Block registry and static dashboard blocks v1
Iteration 7 — Data sources and resolver v0
Iteration 8 — Product adapter contract v0
Iteration 9 — BeeCap adapter MVP
Iteration 10 — Embedded mount API v0
Iteration 11 — Generic artifact browser v1
Iteration 12 — Adapter-backed Product Console routes/API MVP
Iteration 12.1 — Adapter-backed Tabler dashboard blocks renderer
Iteration 12.2 — Усиление визуального соответствия Tabler для продуктовой консоли на основе адаптера
Iteration 12.3 — Chart layout block package/rendering integrity
Iteration 12.4 — Operator console block primitives parity
BeeCap UI-25 — BeeUI Console parity MVP
BeeCap UI-26 — BeeUI default route switch with legacy fallback
```

MVP считается достигнутым, если:

- `beeui` запускается отдельно как demo;
- `beeui` подключается к `beecap`;
- BeeCap dashboard рендерится через BeeUI;
- BeeCap current custom templates больше не расширяются вручную;
- run list / run detail / artifact links работают;
- UI read-only по умолчанию;
- tests green.

## Что должно остаться в BeeCap/BeeAgent после внедрения BeeUI

Bee-продукты сохраняют:

- core runtime;
- config validation;
- product artifacts;
- product read-model;
- domain-specific summaries;
- bounded actions;
- authority/security checks.

Bee-продукты больше не должны дублировать:

- base web shell;
- Tabler layout;
- sidebar/navbar;
- reusable KPI cards;
- generic tables;
- generic artifact browser;
- theme layer;
- common config UI;
- common admin/support pages.

## Диагностика и тесты

### Диагностика

| Команда              | Что делает                                                  |
| -------------------- | ----------------------------------------------------------- |
| `./start.sh doctor`  | Проверка окружения, структуры, imports, config availability |
| `./start.sh web`     | Запуск demo BeeUI web app                                   |
| `./start.sh routes`  | Показ registered routes                                     |
| `./start.sh version` | Показ версии BeeUI                                          |

### Тесты

```bash
uv run pytest -q
```

### Web smoke

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Проверить:

```text
http://127.0.0.1:8780/
http://127.0.0.1:8780/health
```

### Security smoke

Проверить:

- no secrets in HTML;
- no secrets in API;
- invalid run_id rejected;
- path traversal rejected;
- POST routes do not work without explicit implementation;
- static files limited to BeeUI static directory.

## Deployment

### MVP deployment

Embedded per product.

```text
container: beecap
  includes beeui dependency
  exposes beecap web

container: beeagent
  includes beeui dependency
  exposes beeagent web
```

Плюсы:

- проще;
- меньше сетевых связей;
- быстрее MVP;
- меньше auth/CORS проблем.

### Будущий deployment

Standalone BeeUI.

```text
container: beeui
container: beecap-api
container: beeagent-api
```

Использовать только после стабилизации:

- BeeUI API contracts;
- product APIs;
- auth/session model;
- deployment model.

## Важно

BeeUI — это не просто UI kit.

Правильное определение:

```text
BeeUI is a reusable UI/runtime framework for Bee products.
```

Он должен развиваться от простого embedded UI package к platform layer:

1. server-rendered operator console;
2. reusable dashboard blocks;
3. artifact/config/admin views;
4. stable JSON API;
5. auth/RBAC;
6. bounded operator controls;
7. будущий no-code dashboard builder;
8. будущий standalone frontend backend.

Неправильное направление:

```text
Сразу делать no-code Retool/Webflow clone.
```

Это приведёт к месячной разработке без MVP.

Правильное направление:

```text
Declarative schema first.
Visual builder later.
```

## Текущий статус

Проект создан как отдельная repo:

```text
~/Projects/beeui
```

Текущий статус:

```text
Iteration 12.4 — Operator console block primitives parity — ЗАВЕРШЕНО
```

Работает:

```bash
./start.sh doctor
./start.sh routes
uv run pytest -q
./start.sh web --host 127.0.0.1 --port 8780
```

- `/` рендерит literal и resolver-backed dashboard blocks from schema;
- `/runs` рендерит empty state для страницы без block placements;
- `/components*` рендерит internal read-only catalog of controlled primitives;
- resolver-backed blocks читают значения из controlled read-only `demo` / `static` sources;
- missing selector data рендерит degraded/error block state вместо падения страницы;
- generic `ProductUiAdapter` contract доступен в `src/beeui_module/adapters/`;
- optional adapter write/action methods недоступны по умолчанию;
- `BeeCapFixtureAdapter` валидирует BeeCap-shaped fixture payloads;
- BeeCap-like fixtures покрывают dashboard, runs, artifact references, partial и corrupted artifact states;
- integration boundary задокументирован в `docs/INTEGRATION.md`;
- `create_beeui_app(...)` accepts `config_path`, product metadata and adapter;
- `mount_beeui(...)` mounts BeeUI into parent FastAPI app;
- adapter is validated and stored in `app.state.beeui_adapter`;
- product metadata is stored in `app.state.beeui_product`;
- artifact browser HTML/API routes работают через adapter;
- `/api/runs/{run_id}/artifacts*` routes доступны при `features.browser_artifact: true`;
- product console HTML/API routes работают через adapter when adapter is present;
- adapter-backed `layout[]` blocks рендерятся на `/`, `/runs`, `/runs/{run_id}`, `/venues/{venue_id}`;
- malformed/unsupported layout blocks рендерятся как degraded state;
- layout links валидируются как safe internal links и учитывают route prefix / embedded mount path.
- реальные локальные скомпилированные CSS/JS из `@tabler/core@1.4.0` поставляются как локальные статические ресурсы пакета;
- самодельный слой совместимости `tabler-compatible` удалён из текущей runtime-поверхности;
- CSS BeeUI используется как контролируемый слой оформления продукта поверх Tabler, а не как второй CSS-фреймворк;
- тёмные оболочка, боковая панель и подвал визуально согласованы с вертикальным layout Tabler.
