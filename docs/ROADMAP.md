# ROADMAP — BeeUI

## Назначение

Этот документ фиксирует маршрут разработки `beeui` по этапам и итерациям.

`beeui` — reusable Python-based UI layer для Bee-продуктов.

Проект предоставляет:

- FastAPI + Jinja2 + Tabler web surface;
- declarative pages and dashboard blocks;
- product adapters for `beecap`, `beeagent` and future Bee products;
- artifact browser and source links;
- stable read-only JSON API contracts;
- bounded config/admin/operator controls;
- theme/customization layer;
- future foundation for no-code dashboard/frontend builder.

`beeui` не заменяет domain/runtime core Bee-продуктов.

Bee-продукты сохраняют ownership над:

- runtime behavior;
- business logic;
- artifacts;
- config validation;
- bounded execution APIs;
- security-sensitive authority boundaries.

`beeui` отвечает за:

- rendering;
- navigation;
- reusable UI blocks;
- read-model presentation;
- safe artifact navigation;
- HTML/API consistency;
- auth/admin surface;
- dashboard schema;
- future visual builder foundation.

ROADMAP используется как lightweight SDLC-артефакт:

- задаёт направление разработки;
- фиксирует цель каждой итерации;
- определяет ожидаемое поведение, артефакты и проверки;
- помогает связывать Issue → Code → Tests → Docs → PR → Merge.

ROADMAP не заменяет Issue и PR:

- **Issue** объясняет, что именно нужно сделать в рамках задачи;
- **PR** фиксирует, что реально было сделано и как это проверялось;
- **ROADMAP** показывает, куда идёт проект и что считается готовностью по итерациям.

Итерация закрывается через PR.

ROADMAP не дублирует полные правила процесса и безопасности:

- процесс разработки и критерии прохождения изменений описываются в `docs/SDLC.md`;
- secure development rules и security checks описываются в `docs/SECURITY.md`.

## Видение

| Блок                           | Формулировка                                                                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Идентичность продукта**      | `beeui` развивается как reusable UI/backend framework для Bee-продуктов, построенный на Python, FastAPI, Jinja2 и Tabler.                         |
| **Основная цель**              | Убрать повторяемую web/UI инфраструктуру из `beecap`, `beeagent` и будущих Bee-продуктов.                                                         |
| **Философия исполнения**       | `beeui` рендерит и управляет interface layer; domain-продукт принимает решения и остаётся source of truth.                                        |
| **Источник истины**            | Product config, product artifacts and product APIs остаются canonical source of truth. `beeui` читает read-model/adapters и отображает результат. |
| **Принцип KISS**               | Сначала declarative schema + reusable blocks + adapters. No-code builder только после стабилизации contracts.                                     |
| **Принцип безопасности**       | UI read-only by default. Любые write/control actions только через bounded product callbacks/API, validation, backup and audit.                    |
| **Принцип интеграции**         | Product adapter является единственной точкой знания о BeeCap/BeeAgent domain semantics.                                                           |
| **Принцип frontend evolution** | Сначала server-rendered UI. Позже отдельный frontend подключается к стабильному BeeUI JSON API.                                                   |
| **Принцип кастомизации**       | Theme/layout/pages/blocks описываются schema/config, а не копированием HTML по продуктам.                                                         |
| **Принцип anti-chaos**         | Bee-продукты не должны заново реализовывать Tabler templates, sidebar, cards, tables, artifact browser, config UI и admin pages.                  |
| **Принцип authority boundary** | `beeui` не получает прямой broker/runtime/execution authority. Все потенциально опасные действия остаются за product-owned bounded APIs.          |

## Принципы разработки

Делаем маленькие итерации. Каждая итерация должна:

- запускаться через `start.sh` или соответствующий CLI entrypoint;
- писать понятные логи;
- не ломать структуру пакета `beeui_module`;
- иметь тесты на ключевое поведение;
- сохранять HTML autoescape;
- блокировать path traversal для file/artifact routes;
- не раскрывать secrets в HTML/API/logs/artifacts;
- не вводить второй source of truth;
- не вводить execution authority в `beeui`;
- закрываться через Issue / PR / tests / docs;
- проходить обязательные checks из `docs/SDLC.md` и `docs/SECURITY.md`.

Для `beeui` это означает:

- low-risk изменения проходят базовые checks;
- runtime-risk изменения требуют проверки API/adapters/artifact contracts;
- security-sensitive изменения требуют усиленной проверки auth/session/file/path/write-action boundaries.

## SDLC workflow для элементов roadmap

Каждая итерация проходит по упрощённому циклу:

1. **Planning**  
   Итерация описана в ROADMAP и оформлена как Issue.

2. **Requirements**  
   Для итерации определены scope, deliverable, checks и DoD.

3. **Implementation**  
   Изменения вносятся в отдельной ветке и только в рамках текущей итерации.

4. **Verification**  
   Выполняются тесты, smoke-check, route checks, HTML/API checks и security checks.

5. **Review / PR**  
   В PR фиксируются изменения, тесты, ограничения и known gaps.

6. **Merge**  
   Итерация считается завершённой после выполнения DoD.

## Значения статусов

Допустимые статусы итераций:

- **PLANNED** — запланировано
- **IN PROGRESS** — в работе
- **DONE** — завершено
- **DONE (partial)** — завершено частично, есть осознанные ограничения
- **FUTURE** — намеренно отложено до стабилизации базовых contracts

## Уровни изменений для проверки

Для lightweight SDLC используются три уровня изменений:

- **low-risk** — docs, локальные templates, стили, безопасные read-only UI changes без влияния на adapters/API/security;
- **runtime-risk** — adapters, artifact parsing, config preview/apply, API contracts, product integration, schema validation;
- **security-sensitive** — auth, sessions, cookies, file/path access, write controls, action execution, secrets redaction, HTML/API exposure, dependency surface.

Обязательность checks определяется в:

- `docs/SDLC.md`
- `docs/SECURITY.md`

## Глобальное Definition of Done

Итерация считается завершённой, если:

- behavior реализован в рамках заявленного scope;
- `uv run pytest -q` проходит;
- relevant CLI/web smoke проходит;
- HTML autoescape включён;
- static assets обслуживаются контролируемо;
- secrets не попадают в HTML/API/logs/artifacts;
- path traversal заблокирован для file/artifact/config routes;
- read-only routes не мутируют source artifacts;
- write/control routes, если есть, проходят validation + audit;
- response envelopes стабильны там, где заявлен API contract;
- docs обновлены, если менялся contract;
- Bee-продукты не получают дублирующий web backend path;
- отсутствуют hidden defaults, hidden fallback paths и silent authority escalation.

## Целевая архитектура

```text
bee product
  ├── config/settings.yml
  ├── storage/*
  ├── product read-model
  ├── bounded product actions
  └── product validation callbacks

        ↓

beeui product adapter

        ↓

beeui
  ├── FastAPI app
  ├── Jinja2 templates
  ├── Tabler static assets
  ├── declarative pages
  ├── reusable blocks
  ├── artifact browser
  ├── config/admin UI
  ├── auth/session layer
  └── stable JSON API
```

Главное правило:

```text
BeeUI renders.
Product decides.
```

## Структура проекта

Целевая структура:

```text
beeui/
├── config/
│   ├── schema.yml
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
│       ├── app.py
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
│       ├── templates/
│       │   ├── base.html
│       │   ├── error.html
│       │   ├── login.html
│       │   ├── page.html
│       │   └── components/
│       │       ├── alert.html
│       │       ├── artifact_links.html
│       │       ├── badge.html
│       │       ├── breadcrumbs.html
│       │       ├── chart_card.html
│       │       ├── data_table.html
│       │       ├── json_viewer.html
│       │       ├── kpi_card.html
│       │       ├── metric_card.html
│       │       ├── navbar.html
│       │       ├── page_header.html
│       │       ├── sidebar.html
│       │       └── status_card.html
│       │
│       ├── static/
│       │   ├── css/
│       │   │   └── beeui.css
│       │   ├── js/
│       │   │   └── beeui.js
│       │   └── vendor/
│       │       └── tabler/
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

---

## Этап 1 — Foundation MVP

### Итерация 0 — Project skeleton, startup and release contract

**Статус:** DONE

#### Goal

Создать минимальный запускаемый каркас `beeui` в стиле `beecap` / `beeagent`: `src-layout`, `uv`, `start.sh`, `config/start.py`, базовый CLI dispatch, logging, paths, tests, release-please и package metadata.

#### Scope

Включено:

- `pyproject.toml`;
- `uv.lock`;
- `start.sh`;
- `config/start.py`;
- `config/schema.yml`;
- `.gitignore`;
- `.env.example`;
- `.github/release-please/*`;
- базовая структура `src/beeui_module`;
- базовая структура `docs/`;
- базовая структура `tests/`;
- минимальный `README.ru.md`;
- команда `doctor`;
- команда `version`;
- команда `routes`;
- команда `web` как safe placeholder/stub до Iteration 1;
- базовый logger;
- базовые paths helpers;
- `.gitkeep` для `logs/` и нужных `storage/` директорий.

Не включено:

- Tabler templates;
- полноценный FastAPI web shell;
- dashboard blocks;
- product adapters;
- auth;
- config UI;
- artifact browser;
- no-code builder.

#### Deliverable

Проект устанавливается через `uv`, запускается через `./start.sh doctor`, имеет reproducible `uv.lock`, release-please config и готовый каркас для Iteration 1.

#### Checks

- `uv sync --frozen --extra dev`
- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh version`
- `./start.sh routes`
- import smoke:
  - `python -c "import beeui_module"`

#### DoD

- repo не пустой;
- `start.sh` работает;
- `config/start.py` dispatch работает;
- `uv.lock` создан;
- release-please config добавлен;
- tests проходят;
- структура проекта соответствует принятому src-layout;
- logs/storage directories имеют `.gitkeep`;
- web/UI реализация не начата раньше Iteration 1.

### Итерация 1 — Tabler web shell v0

**Статус:** DONE

#### Goal

Поднять минимальный runnable FastAPI + Jinja2 + local Tabler-compatible web shell для BeeUI demo mode, чтобы `./start.sh web` запускал реальную web surface вместо placeholder.

#### Scope

Включено:

- FastAPI app factory;
- `web` CLI command with `--host`, `--port`, optional `--reload=false` не нужен;
- чтение `web.host`, `web.port`, `web.route_prefix`, `web.cache_static` из `config/settings.yml`;
- Jinja2 templates with autoescape;
- package-local templates:
  - `base.html`;
  - `page.html`;
- package-local static assets:
  - `static/css/beeui.css`;
  - `static/js/beeui.js`;
  - minimal local Tabler-compatible placeholder assets if real Tabler vendor files are not added yet;
- base layout:
  - sidebar placeholder;
  - top navbar placeholder;
  - page header;
  - demo dashboard content;
- routes:
  - `GET /`;
  - `GET /health`;
  - `GET /static/...`;
- read-only headers for GET routes where practical:
  - `X-BeeUI-Read-Only: true`;
  - `Cache-Control: no-store` for HTML/health;
- route tests with `httpx` / FastAPI TestClient;
- tests that HTML has no external scripts/tracking references.

Не включено:

- declarative pages/navigation schema;
- block registry;
- product adapters;
- auth/session;
- config preview/apply;
- artifact browser;
- operator actions;
- JSON API v1 beyond `/health`;
- no-code builder;
- standalone multi-product service.

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` starts a real BeeUI demo web shell with local static assets, renders `/`, returns `/health`, and passes route/static/security smoke tests.

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh web --host 127.0.0.1 --port 8780`
- route smoke:
  - `GET /`
  - `GET /health`
  - `GET /static/css/beeui.css`
- HTML smoke:
  - base layout renders;
  - no external CDN/script/tracking references;
  - no secrets in HTML;
  - Jinja autoescape stays enabled.

#### DoD

- `web` is no longer a placeholder;
- FastAPI app starts;
- base layout renders;
- static assets are served from package-local static directory only;
- `/health` returns safe JSON;
- route tests cover HTML, health and static assets;
- no product-specific domain logic is introduced;
- no write/control surface is introduced.

### Итерация 2 — Declarative pages and navigation v0

**Статус:** DONE

#### Goal

Добавить минимальный YAML-driven слой pages/navigation, чтобы BeeUI web shell рендерил страницы и навигацию из declarative UI schema, а не из hardcoded template/routes.

#### Scope

Включено:

- `config/schema.yml` как demo UI schema;
- `BeeUiConfig` model/parser для declarative UI config;
- fail-fast schema validation;
- navigation model;
- pages model;
- page id/path/title/subtitle;
- route generation from page config;
- active navigation item;
- rendering generic page template from page config;
- graceful startup failure on invalid UI config;
- tests for valid/invalid config and route rendering.

Не включено:

- data sources;
- block registry;
- product adapters;
- visual builder;
- config apply;
- artifact browser;
- auth/session;
- custom page templates;
- arbitrary HTML/JS from config.

#### Config separation

- `config/settings.yml` остаётся runtime/system config.
- `config/schema.yml` становится declarative UI schema для demo mode.
- BeeUI не должен смешивать runtime settings и page/navigation schema в один объект.

#### Example `config/schema.yml`

```yaml
app:
  title: BeeUI Demo
  product: demo

navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks: []

  - id: runs
    path: /runs
    title: Runs
    subtitle: Placeholder page for future run overview
    blocks: []
```

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` запускает BeeUI, где navigation и pages рендерятся из `config/schema.yml`.

#### Suggested routes

- `GET /`
- `GET /runs`
- `GET /health`
- `GET /static/...`

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh routes`
- `./start.sh web --host 127.0.0.1 --port 8780`
- valid UI config loads;
- missing `app.title` fails fast;
- duplicate page path fails fast;
- duplicate page id fails fast;
- navigation path without matching page fails fast;
- unsafe page path rejected;
- active nav item renders;
- unknown page returns 404;
- HTML contains no external tracking scripts.

#### DoD

- page/nav config работает;
- invalid UI config fails fast;
- navigation рендерится без hardcoded product assumptions;
- page title/subtitle берутся из config;
- routes создаются из config;
- no arbitrary HTML/JS from config;
- no product-specific domain logic introduced.

### Итерация 3 — Block registry and base blocks v0

**Статус:** PLANNED

#### Goal

Добавить reusable block registry и первые базовые dashboard blocks.

#### Scope

Включено:

- block model;
- block registry;
- layout rows/columns;
- renderers:
  - `metric_card`;
  - `kpi_grid`;
  - `status_card`;
  - `table_card`;
  - `links_card`;

- empty state;
- error state;
- unknown block rejection.

Не включено:

- charts;
- artifact browser;
- product adapters;
- no-code layout editor.

#### Example config

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    layout:
      - row:
          - block: latest_run
            width: 3
          - block: runtime_status
            width: 3

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    value: demo.latest_run
```

#### Deliverable

Dashboard можно собрать из reusable blocks.

#### Checks

- metric card render;
- KPI grid render;
- table render;
- links render;
- unknown block type rejection;
- missing data graceful state;
- `pytest -q`.

#### DoD

- blocks рендерятся по schema;
- renderer не содержит BeeCap/BeeAgent semantics;
- layout rows/columns работают;
- unknown/invalid blocks не ломают весь app.

### Итерация 4 — Data sources and resolver v0

**Статус:** PLANNED

#### Goal

Добавить data source abstraction и selector resolver для передачи данных в blocks.

#### Scope

Включено:

- static JSON data source;
- in-memory demo source;
- selector syntax для вложенных полей;
- response envelope:
  - `status`;
  - `data`;
  - `warnings`;
  - `source`;

- timeout/error model для future HTTP source;
- partial data handling.

Не включено:

- BeeCap adapter;
- BeeAgent adapter;
- HTTP adapter в production mode;
- artifact browser.

#### Deliverable

Blocks получают значения из data resolver, а не из hardcoded demo variables.

#### Checks

- static source load;
- selector success;
- selector missing;
- partial data;
- invalid source;
- `pytest -q`.

#### DoD

- block renderer не знает source details;
- missing data отображается как empty/degraded state;
- envelope shape стабилен.

---

## Этап 2 — BeeCap MVP integration

### Итерация 5 — Product adapter contract v0

**Статус:** PLANNED

#### Goal

Зафиксировать общий `ProductUiAdapter` contract для подключения Bee-продуктов.

#### Scope

Включено:

- `ProductUiAdapter` base class/protocol;
- methods:
  - `get_dashboard()`;
  - `list_runs()`;
  - `get_run(run_id)`;
  - `list_artifacts(run_id)`;
  - `read_artifact(run_id, artifact_id)`;
  - `get_config_read_model()`;

- stable error types;
- safe ID validation helpers;
- product metadata.

Не включено:

- конкретный BeeCap adapter;
- concrete BeeAgent adapter;
- write actions;
- auth.

#### Deliverable

Есть минимальный adapter contract, который можно реализовать в BeeCap/BeeAgent.

#### Checks

- fake adapter test;
- adapter error handling;
- invalid run_id rejection;
- response envelope consistency;
- `pytest -q`.

#### DoD

- product integration point стабилен;
- BeeUI не читает product internals без adapter;
- invalid IDs handled safely.

### Итерация 6 — BeeCap adapter MVP

**Статус:** PLANNED

#### Goal

Подключить BeeCap к BeeUI через embedded adapter без переноса BeeCap domain logic в BeeUI.

#### Scope

Включено:

- `BeeCapUiAdapter` skeleton;
- dashboard read-model;
- latest run;
- run list;
- run detail;
- artifact references;
- MRKT summary where artifacts exist;
- Binance/paper summary where artifacts exist;
- `examples/beecap_embedded/beeui.yml`;
- integration notes.

Не включено:

- full replacement of BeeCap current web;
- config apply;
- operator actions;
- auth;
- no-code builder.

#### Deliverable

BeeUI может отрендерить BeeCap dashboard/run overview из BeeCap adapter/read-model.

#### Expected BeeCap side

BeeCap должен предоставить тонкий integration module:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
```

#### Checks

- BeeCap-like fixture dashboard;
- runs list render;
- run detail render;
- MRKT partial artifact scenario;
- Binance partial artifact scenario;
- no secret leakage;
- path traversal rejection;
- `pytest -q`.

#### DoD

- BeeUI не содержит trading logic;
- BeeCap domain semantics остаются в BeeCap adapter/read-model;
- source artifacts не мутируются;
- dashboard работает на fixture artifacts.

### Итерация 7 — Embedded mount API v0

**Статус:** PLANNED

#### Goal

Сделать простой способ подключить BeeUI внутрь BeeCap/BeeAgent как embedded package.

#### Scope

Включено:

- `create_beeui_app(...)`;
- `mount_beeui(...)`;
- config path loading;
- adapter injection;
- static/templates registration;
- route prefix support;
- product metadata injection.

Не включено:

- standalone multi-product service;
- auth;
- CORS;
- distributed deployment.

#### Example

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

#### Deliverable

BeeCap/BeeAgent могут подключить BeeUI одной app factory/mount function.

#### Checks

- embedded app factory test;
- route prefix test;
- static path test;
- adapter injection test;
- `pytest -q`.

#### DoD

- integration API простой;
- product-specific app glue минимален;
- no hidden product assumptions.

### Итерация 8 — Generic artifact browser v1

**Статус:** PLANNED

#### Goal

Сделать reusable artifact browser для Bee-продуктов.

#### Scope

Включено:

- artifact list block;
- artifact metadata;
- safe artifact IDs;
- allowlisted artifact access;
- JSON viewer;
- JSONL preview;
- text preview;
- source links;
- malformed artifact handling;
- path traversal guard.

Не включено:

- arbitrary filesystem browser;
- artifact mutation;
- upload/edit/delete;
- binary viewers beyond safe metadata.

#### Suggested routes

- `GET /runs/{run_id}/artifacts`
- `GET /api/runs/{run_id}/artifacts`
- `GET /api/runs/{run_id}/artifacts/{artifact_id}`

#### Deliverable

BeeCap/BeeAgent могут показывать artifacts через общий BeeUI artifact browser.

#### Checks

- JSON artifact view;
- JSONL artifact view;
- malformed row handling;
- forbidden path rejection;
- non-allowlisted artifact rejection;
- no mutation check;
- no secrets leakage;
- `pytest -q`.

#### DoD

- artifact browser reusable;
- source artifacts remain canonical;
- arbitrary file access невозможен;
- corrupted artifacts render as partial/error state.

---

## Этап 3 — BeeCap replacement MVP

### Итерация 9 — BeeCap dashboard parity MVP

**Статус:** PLANNED

#### Goal

Довести BeeUI до минимальной практической замены текущего BeeCap web dashboard.

#### Scope

Включено:

- dashboard page;
- mode-aware sections:
  - dry-run;
  - paper;
  - live;

- venue-aware sections:
  - MRKT;
  - Binance;

- KPI cards:
  - latest run;
  - runtime status;
  - active orders;
  - open positions/cycles;
  - completed cycles/trades;
  - realized profit where available;

- run links;
- artifact links;
- graceful missing state.

Не включено:

- config apply;
- operator launch;
- charts;
- auth;
- no-code builder.

#### Deliverable

BeeCap can render useful operator dashboard through BeeUI.

#### Checks

- dashboard normal state;
- no latest run state;
- MRKT artifact fixture;
- Binance live artifact fixture;
- paper artifact fixture;
- partial/corrupted artifact fixture;
- no mutation;
- `pytest -q`.

#### DoD

- BeeUI dashboard gives enough value to stop expanding BeeCap templates manually;
- BeeCap-specific calculations remain in BeeCap adapter/read-model;
- dashboard is read-only.

### Итерация 10 — Runs list and run overview MVP

**Статус:** PLANNED

#### Goal

Добавить reusable run list and run detail pages.

#### Scope

Включено:

- `/runs`;
- `/runs/{run_id}`;
- search/filter/sort v0;
- run metadata;
- health/status;
- latest decision/explain summary if adapter provides it;
- linked artifacts;
- source artifact references;
- partial state rendering.

Не включено:

- advanced chart;
- replay engine;
- write actions;
- DB index.

#### Deliverable

Operator can inspect product runs through BeeUI.

#### Checks

- run list render;
- filter by mode/venue;
- run detail render;
- malformed run_id rejection;
- missing run;
- partial artifacts;
- `pytest -q`.

#### DoD

- runs can be inspected without manual storage browsing;
- run detail remains read-only;
- source artifact links visible.

### Итерация 11 — Stable BeeUI API v0 for dashboard/runs/artifacts

**Статус:** PLANNED

#### Goal

Зафиксировать первый JSON API contract для будущего separate frontend.

#### Scope

Включено:

- API response envelope;
- routes:
  - `/api/dashboard`;
  - `/api/runs`;
  - `/api/runs/{run_id}`;
  - `/api/runs/{run_id}/artifacts`;
  - `/api/runs/{run_id}/artifacts/{artifact_id}`;

- error envelope;
- partial-data envelope;
- API/UI parity tests.

Не включено:

- public external API;
- auth/RBAC;
- websocket/SSE;
- React frontend.

#### Deliverable

Future frontend can attach to BeeUI backend read-model.

#### Checks

- response shape tests;
- UI/API parity;
- error envelope;
- partial envelope;
- malformed input;
- no secret leakage;
- `pytest -q`.

#### DoD

- API responses deterministic;
- documented contract exists;
- frontend does not need to read product storage directly.

---

## Этап 4 — Config/admin/operator foundation

### Итерация 12 — Config read-model and validation preview v1

**Статус:** PLANNED

#### Goal

Дать общий config read-model and validation preview layer без arbitrary YAML editor.

#### Scope

Включено:

- config read-model;
- editable/non-editable/redacted fields;
- allowlisted future-editable keys;
- validation preview;
- product validation callback;
- diff summary;
- redaction rules;
- HTML page and JSON endpoints.

Не включено:

- actual config write;
- secrets editing;
- arbitrary YAML editor;
- live/broker controls.

#### Suggested routes

- `GET /config`
- `GET /api/config/read-model`
- `POST /api/config/preview`

#### Deliverable

Оператор видит config и может preview proposed changes без записи.

#### Checks

- read-model rendering;
- allowed preview;
- forbidden key rejection;
- invalid value rejection;
- secrets redaction;
- no file mutation;
- `pytest -q`.

#### DoD

- preview read-only;
- product validation callback reused;
- secrets не отображаются;
- no second config source.

### Итерация 13 — Bounded config apply and audit v1

**Статус:** PLANNED

#### Goal

Добавить безопасный config apply workflow для allowlisted keys.

#### Scope

Включено:

- apply endpoint/form;
- stale config hash guard;
- backup before write;
- audit artifact for accepted/rejected attempts;
- atomic/rollback-friendly write;
- product validation callback;
- explicit rejection reasons.

Не включено:

- secrets editing;
- broker/live manual controls;
- full YAML editor;
- automatic runtime restart.

#### Suggested artifacts

- `storage/interfaces/config_revisions/<change_id>/settings.before.yml`
- `storage/interfaces/config_changes/<change_id>/audit.json`

#### Deliverable

BeeUI даёт reusable bounded config apply layer, продукт определяет allowlist and validation.

#### Checks

- allowed apply;
- forbidden apply;
- stale hash rejection;
- invalid candidate rejection;
- backup creation;
- audit creation;
- no secret leakage;
- `pytest -q`.

#### DoD

- every apply attempt audited;
- source config remains canonical;
- write allowed only through product-defined allowlist;
- no hidden runtime restart.

### Итерация 14 — Bounded operator actions v1

**Статус:** PLANNED

#### Goal

Добавить generic bounded action framework для operator controls без прямой runtime authority в BeeUI.

#### Scope

Включено:

- action registry;
- action forms;
- confirmation;
- product action callback;
- validation;
- result envelope;
- audit artifact;
- disabled/denied/unavailable states.

Не включено:

- broker/manual order console;
- direct execution inside BeeUI;
- hidden background jobs;
- live authority by default.

#### Suggested artifacts

- `storage/interfaces/operator_actions/<action_id>.json`

#### Deliverable

BeeUI может показывать bounded operator buttons/forms, но выполнение происходит только через product-owned callback/API.

#### Checks

- allowed action;
- denied action;
- unavailable action;
- invalid payload;
- audit linkage;
- no secret leakage;
- `pytest -q`.

#### DoD

- BeeUI never executes product logic directly;
- all actions go through explicit product callback;
- all action attempts audited;
- read-only remains default.

---

## Этап 5 — Auth/security layer

### Итерация 15 — Auth/session/RBAC v0

**Статус:** PLANNED

#### Goal

Добавить минимальный локальный auth layer для BeeUI.

#### Scope

Включено:

- login/logout;
- password hash;
- signed session cookie;
- roles:
  - admin;
  - operator;
  - viewer;

- route protection;
- CSRF protection for POST routes;
- secure cookie settings where applicable;
- no default admin password in repo.

Не включено:

- OAuth;
- SSO;
- 2FA;
- multi-tenant SaaS auth;
- external user management.

#### Deliverable

BeeUI может защищать internal operator/admin UI.

#### Checks

- login success/failure;
- role access;
- logout;
- POST CSRF rejection;
- no plaintext password;
- no session secret leakage;
- `pytest -q`.

#### DoD

- all non-public routes protected when auth enabled;
- write routes require role + CSRF;
- secrets not logged;
- auth can be disabled only explicitly for local/dev.

---

## Этап 6 — BeeAgent integration

### Итерация 16 — BeeAgent adapter MVP

**Статус:** PLANNED

#### Goal

Подключить BeeAgent к BeeUI через adapter/schema без копирования BeeCap UI.

#### Scope

Включено:

- `BeeAgentUiAdapter`;
- dashboard;
- modules;
- runs;
- artifacts;
- capabilities;
- approvals placeholder;
- `examples/beeagent_embedded/beeui.yml`.

Не включено:

- execution authority;
- autonomous agent controls;
- MCP write actions;
- no-code builder.

#### Deliverable

BeeAgent получает operator UI поверх BeeUI.

#### Expected BeeAgent side

BeeAgent должен предоставить тонкий integration module:

```text
src/beeagent_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  capabilities.py
  actions.py
```

#### Checks

- modules page;
- runs page;
- artifacts page;
- capabilities page;
- missing/partial artifacts;
- no secret leakage;
- `pytest -q`.

#### DoD

- BeeAgent UI строится через BeeUI;
- BeeAgent keeps authority boundary;
- capabilities/actions remain product-controlled.

---

## Этап 7 — Theme and customization

### Итерация 17 — Theme/customization v1

**Статус:** PLANNED

#### Goal

Сделать controlled theme customization без ручного изменения CSS в каждом продукте.

#### Scope

Включено:

- theme config:
  - mode;
  - primary color;
  - font;
  - radius;
  - density;

- CSS variable generation;
- product branding;
- logo/title;
- local font/static asset policy.

Не включено:

- arbitrary CSS editor;
- user-uploaded unsafe assets;
- full design system editor.

#### Example

```yaml
app:
  theme:
    mode: dark
    primary: blue
    font: Inter
    radius: 2
    density: compact
```

#### Deliverable

Bee-продукты кастомизируют внешний вид через config/schema.

#### Checks

- dark/light;
- primary color;
- font variable;
- invalid theme rejection;
- no unsafe CSS injection;
- `pytest -q`.

#### DoD

- theme controlled by schema;
- no arbitrary CSS injection;
- Tabler customization centralized.

---

## Этап 8 — Frontend/no-code foundation

### Итерация 18 — Dashboard schema editor v0

**Статус:** FUTURE

#### Goal

Подготовить первый шаг к no-code builder: редактирование dashboard schema через UI.

#### Scope

Включено:

- list pages;
- list blocks;
- enable/disable block;
- reorder blocks;
- change width;
- preview schema;
- validate before save;
- backup/audit.

Не включено:

- drag-and-drop;
- arbitrary HTML;
- custom JS;
- plugin marketplace;
- full frontend builder.

#### Deliverable

Оператор может менять layout через безопасную schema, не редактируя YAML вручную.

#### Checks

- block enable/disable;
- reorder;
- invalid layout rejection;
- audit;
- no arbitrary HTML/JS injection;
- `pytest -q`.

#### DoD

- visual builder edits schema only;
- schema validation protects layout;
- no unsafe templates/scripts are accepted.

### Итерация 19 — Separate frontend contract v0

**Статус:** FUTURE

#### Goal

Подготовить BeeUI backend к отдельному frontend без переписывания product adapters.

#### Scope

Включено:

- stable API versioning;
- OpenAPI review;
- frontend-safe envelopes;
- static frontend mount placeholder;
- CORS policy for controlled standalone mode;
- API docs.

Не включено:

- React/Vue implementation;
- public SaaS;
- multi-tenant auth;
- websocket streaming.

#### Deliverable

BeeUI можно использовать как backend для future separate frontend.

#### Checks

- API schema snapshot;
- envelope compatibility;
- CORS disabled by default;
- no secret leakage;
- `pytest -q`.

#### DoD

- frontend can attach to stable backend API;
- server-rendered UI still works;
- no second source of truth introduced.

### Итерация 20 — Standalone BeeUI service v0

**Статус:** FUTURE

#### Goal

Добавить standalone mode, где BeeUI запускается отдельным сервисом и подключается к Bee-продуктам по HTTP API.

#### Scope

Включено:

- `beeui web --config ...`;
- HTTP product adapter;
- product registry;
- backend health checks;
- timeout/degraded states;
- explicit standalone deployment docs.

Не включено:

- distributed auth platform;
- service mesh;
- multi-tenant SaaS;
- broker/runtime authority.

#### Deliverable

BeeUI может работать как отдельный контейнер поверх BeeCap/BeeAgent APIs.

#### Checks

- standalone demo;
- HTTP adapter success;
- backend unavailable state;
- timeout state;
- auth boundary docs;
- `pytest -q`.

#### DoD

- standalone mode works;
- embedded mode remains supported;
- backend product APIs remain source of truth;
- degraded backend does not crash entire UI.

---

## MVP path

Для быстрого выхода к MVP идти так:

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

Минимальный практический MVP считается достигнутым, когда:

- `beeui` запускается отдельно как demo;
- `beeui` подключается к `beecap` как dependency;
- BeeCap dashboard рендерится через BeeUI;
- BeeCap current web templates больше не расширяются вручную;
- BeeCap отдаёт только adapter/read-model/artifacts;
- routes dashboard/runs/run detail работают read-only;
- tests green.

## Интеграционная модель для Bee-продуктов

### Embedded mode

MVP integration mode.

```text
beecap process
  imports beeui
  creates BeeCapUiAdapter
  creates/mounts BeeUI FastAPI app
```

Плюсы:

- быстро;
- один процесс;
- проще локальная разработка;
- проще auth/session;
- нет CORS/service discovery.

Минусы:

- каждый продукт запускает свой BeeUI instance;
- обновления BeeUI идут через dependency update.

### Standalone mode

Future integration mode.

```text
beeui service
  connects to beecap API
  connects to beeagent API
  renders multi-product UI
```

Плюсы:

- один UI service;
- проще central operator dashboard;
- готовность к отдельному frontend.

Минусы:

- сложнее auth;
- CORS;
- service discovery;
- deployment complexity.

Решение:

```text
MVP: embedded.
Later: standalone.
```

## Правила для BeeCap/BeeAgent после внедрения BeeUI

Bee-продукты не должны повторно реализовывать:

- Tabler templates;
- base layout;
- sidebar/navbar;
- KPI cards;
- generic tables;
- artifact browser;
- theme layer;
- config UI shell;
- admin/support pages;
- generic dashboard rendering.

Bee-продукты должны реализовывать:

- product read-model;
- artifact allowlist;
- product-specific summaries;
- config validation callback;
- bounded action callbacks;
- authority/security-sensitive checks.

## Связанные документы

Для выполнения итераций вместе с этим ROADMAP используются:

- `docs/SDLC.md` — lightweight process, change levels, обязательные quality/security checks, DoD flow;
- `docs/SECURITY.md` — secure development rules и security checks;
- `docs/INTEGRATION.md` — как подключать BeeUI к BeeCap/BeeAgent;
- `docs/COMPONENTS.md` — reusable blocks/components contract;
- `docs/API_CONTRACT.md` — JSON API envelopes and route contracts;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;
- `docs/THEME.md` — theme/customization contract.
