# BeeUI — reusable UI framework для Bee-продуктов

**BeeUI** — общий Python-based UI framework для Bee-продуктов: `beecap`, `beeagent` и будущих модулей Bee ecosystem.

## Iteration 1

Текущий deliverable — minimal runnable FastAPI + Jinja2 + local static web shell.

Уже работает:

- `uv sync --frozen --extra dev`
- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh version`
- `./start.sh routes`
- `./start.sh serve --host 127.0.0.1 --port 8780`
- `import beeui_module`

Минимальная web surface Iteration 1:

- `GET /`
- `GET /health`
- `GET /static/...`

Пока не входит в scope:

- product adapters;
- auth/session;
- config UI;
- artifact browser;
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
  -> BeeUI renders operator console and future frontend shell
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

MVP делает controlled declarative console:

- pages описываются через schema/config;
- blocks описываются через schema/config;
- данные приходят из product adapter;
- artifacts отображаются через bounded artifact browser;
- write/control actions идут только через product-owned callbacks.

## Что BeeUI делает

BeeUI отвечает за:

- FastAPI app factory;
- Jinja2 templates;
- Tabler layout;
- global navigation;
- reusable blocks;
- dashboard rendering;
- runs list / run detail pages;
- artifact browser;
- JSON/JSONL preview;
- source artifact links;
- config read-model;
- config preview/apply framework;
- bounded operator actions;
- auth/session layer;
- theme customization;
- stable JSON API for future frontend;
- embedded and future standalone modes.

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

То же для BeeAgent:

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

### Future: standalone mode

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
Later: standalone.
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

Аналогично BeeCap.

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
./start.sh serve
```

Вариант с явным host/port:

```bash
./start.sh serve --host 127.0.0.1 --port 8780
```

Что показывает:

- demo dashboard;
- demo navigation;
- demo blocks;
- static/fake data sources.

### `embedded`

Основной MVP mode.

Продукт импортирует BeeUI и монтирует его в своём web process.

Пример:

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

Future scope.

В Iteration 1 standalone mode не реализован. Запуск с отдельным config-файлом будет добавлен позже, когда появится HTTP product adapter и standalone deployment contract.

## Основные возможности

### Declarative pages

Страницы задаются через config/schema.

```yaml
app:
  title: BeeCap
  product: beecap

navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list
  - title: Config
    path: /config
    icon: settings

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Operator overview
    layout:
      - row:
          - block: latest_run
            width: 3
          - block: runtime_status
            width: 3
          - block: active_orders
            width: 3
          - block: realized_profit
            width: 3
```

### Blocks

BeeUI block registry должен поддерживать reusable block types:

- `metric_card`;
- `kpi_grid`;
- `status_card`;
- `table_card`;
- `links_card`;
- `artifact_table`;
- `json_viewer`;
- `chart_card`;
- `config_form`;
- `action_card`.

Пример:

```yaml
blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: dashboard.latest_run
    value: run_id
    subtitle: started_at_utc

  runtime_status:
    type: status_card
    title: Runtime Status
    source: dashboard.runtime
    status: status
    reason: reason
```

### Data sources

MVP sources:

- `static`;
- `adapter`;
- `filesystem` через product adapter;
- позже `http`.

Пример:

```yaml
data_sources:
  dashboard:
    type: adapter
    method: get_dashboard

  runs:
    type: adapter
    method: list_runs
```

### Product adapters

Единый adapter contract:

```python
class ProductUiAdapter:
    def get_dashboard(self) -> dict: ...
    def list_runs(self, filters: dict | None = None) -> dict: ...
    def get_run(self, run_id: str) -> dict: ...
    def list_artifacts(self, run_id: str) -> dict: ...
    def read_artifact(self, run_id: str, artifact_id: str) -> dict: ...
    def get_config_read_model(self) -> dict: ...
    def preview_config_change(self, payload: dict) -> dict: ...
    def apply_config_change(self, payload: dict) -> dict: ...
    def list_actions(self) -> dict: ...
    def execute_action(self, action_id: str, payload: dict) -> dict: ...
```

BeeUI вызывает adapter.

Product adapter решает, что можно читать/делать.

## Artifact browser

BeeUI должен предоставить generic artifact browser.

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

BeeUI auth layer is planned after MVP dashboard integration.

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

Supported customization:

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
./start.sh serve
```

Запускает demo BeeUI web app.

```bash
./start.sh serve --host 127.0.0.1 --port 8780
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
./start.sh serve --host 127.0.0.1 --port 8780
```

Открыть:

```text
http://127.0.0.1:8780
```

### Без `start.sh`

```bash
uv run --frozen --extra dev python config/start.py doctor
uv run --frozen --extra dev python config/start.py serve
```

## Документация

Основная документация проекта находится в `docs/`.

Ключевые разделы:

- `docs/ROADMAP.md` — этапы и итерации;
- `docs/SDLC.md` — lightweight process, checks, PR workflow;
- `docs/SECURITY.md` — secure development rules;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;

## Целевая структура проекта

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
│       │   └── serve.py
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
│       │   │   └── index.html
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

Planned после Iteration 1:

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
- `HttpProductAdapter` — future standalone mode;
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

BeeUI API должен использовать единый envelope.

### Success

```json
{
  "ok": true,
  "status": "ok",
  "data": {},
  "warnings": [],
  "meta": {
    "source": "adapter",
    "product": "beecap"
  }
}
```

### Partial

```json
{
  "ok": true,
  "status": "partial",
  "data": {},
  "warnings": [
    {
      "code": "artifact_missing",
      "message": "health.json is missing"
    }
  ],
  "meta": {
    "source": "adapter",
    "product": "beecap"
  }
}
```

### Error

```json
{
  "ok": false,
  "status": "error",
  "error": {
    "code": "invalid_run_id",
    "message": "Invalid run_id"
  },
  "warnings": [],
  "meta": {
    "source": "beeui"
  }
}
```

## Planned routes

### HTML

```text
GET /
GET /runs
GET /runs/{run_id}
GET /runs/{run_id}/artifacts
GET /config
GET /admin
GET /login
GET /logout
```

### API

```text
GET /api/dashboard
GET /api/runs
GET /api/runs/{run_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
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
Iteration 3 — Block registry and base blocks v0
Iteration 4 — Data sources and resolver v0
Iteration 5 — Product adapter contract v0
Iteration 6 — BeeCap adapter MVP
Iteration 7 — Embedded mount API v0
Iteration 9 — BeeCap dashboard parity MVP
Iteration 10 — Runs list and run overview MVP
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
| `./start.sh serve`   | Запуск demo BeeUI web app                                   |
| `./start.sh routes`  | Показ registered routes                                     |
| `./start.sh version` | Показ версии BeeUI                                          |

### Тесты

```bash
uv run pytest -q
```

### Web smoke

```bash
./start.sh serve --host 127.0.0.1 --port 8780
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

### Future deployment

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
7. future no-code dashboard builder;
8. future standalone frontend backend.

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
Iteration 1 — Tabler web shell v0 — DONE
```

Работает:

```bash
./start.sh doctor
uv run pytest -q
./start.sh serve --host 127.0.0.1 --port 8780
```

Следующий шаг:

```text
Iteration 2 — Declarative pages and navigation v0
```
