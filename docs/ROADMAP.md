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

## Этап 2 — Tabler-compatible UI foundation

### Итерация 3 — Local Tabler vendor/assets and layout parity v1

**Статус:** DONE

#### Goal

Заменить минимальный placeholder shell на локальный Tabler-compatible foundation: package-local assets, production-safe base layout, sidebar/navbar/page-wrapper/page-header/footer primitives and dark vertical operator layout.

#### Почему это нужно

BeeUI должен стать reusable UI layer, а не набором самодельных карточек. До product adapters нужно зафиксировать визуальный и структурный фундамент, совместимый с Tabler, но безопасный для Bee-продуктов.

#### Scope

Включено:

- package-local Tabler vendor assets under:

```text
src/beeui_module/static/vendor/tabler/
```

- локальные CSS/JS assets only;

- no external CDN/import/script;

- no PostHog/tracking;

- no `scripts.tabler.io/banner.js`;

- no demo sponsor blocks;

- no external font import by default;

- base layout primitives:
  - vertical sidebar;
  - top navbar/header;
  - page wrapper;
  - page header;
  - page body;
  - footer;
  - responsive container;
  - active nav state;
  - collapsed/mobile sidebar behavior where Tabler supports it;

- package templates:
  - `base.html`;
  - `page.html`;
  - `components/sidebar.html`;
  - `components/navbar.html`;
  - `components/page_header.html`;
  - `components/footer.html`;
  - `components/empty_state.html`;

- dark/light compatibility via Tabler attributes;

- demo dashboard still read-only;

- tests that forbid external scripts/styles/tracking references.

Не включено:

- full Tabler demo page copy;
- product adapters;
- block data resolver;
- forms/config apply;
- auth/session;
- arbitrary HTML/JS injection;
- no-code builder.

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI with a real local Tabler-compatible vertical layout, not a crude placeholder.

#### Checks

- `uv run pytest -q`

- `./start.sh doctor`

- `./start.sh routes`

- `./start.sh web --host 127.0.0.1 --port 8780`

- route smoke:
  - `GET /`
  - `GET /health`
  - `GET /static/css/beeui.css`
  - `GET /static/vendor/tabler/...`

- HTML/security smoke:
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `scripts.tabler.io`;
  - no `posthog`;
  - no external `http://` / `https://` scripts;
  - no external CSS imports;
  - no secrets in HTML;
  - Jinja autoescape enabled.

#### DoD

- BeeUI uses local Tabler-compatible assets;
- base layout looks structurally close to Tabler vertical layout;
- no demo/tracking/external dependencies are shipped;
- static files are served only from controlled package-local paths;
- current demo pages still render;
- no product-specific domain logic introduced.

### Итерация 4 — Theme, layout and navigation schema v1

**Статус:** DONE

#### Goal

Добавить controlled schema-driven customization для theme/layout/navigation, чтобы BeeUI visual shell настраивался через `config/schema.yml`, а не через ручные правки HTML/CSS.

#### Почему это нужно

Iteration 3 зафиксировала локальный Tabler-compatible vertical layout foundation, но часть UI-поведения всё ещё зашита в templates/CSS: dark mode, branding/logo text, container size, sidebar/navbar variants and navigation shape.

До blocks/product adapters нужно закрепить безопасный schema contract, чтобы Bee-продукты могли менять внешний вид и навигацию декларативно, без копирования BeeUI templates и без arbitrary CSS/JS.

#### Scope

Включено:

- расширение `config/schema.yml`:

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
      enabled: true
      variant: default
      sticky: false
```

- fail-fast schema validation for:
  - `app.logo_text`;
  - `app.theme`;
  - `app.layout`;
  - grouped navigation;
  - disabled navigation items;
  - internal-only navigation paths by default;

- supported theme options:
  - `mode`: `light`, `dark`, `auto`;
  - `primary`: controlled palette enum only;
  - `base`: `slate`, `gray`, `zinc`, `neutral`, `stone`;
  - `font`: `sans-serif`, `serif`, `monospace`;
  - `radius`: controlled numeric enum, for example `0`, `1`, `2`;
  - `density`: `default`, `compact`, `comfortable`;

- supported layout options:
  - `layout.type`: `vertical` only in this iteration;
  - `layout.container`: `xl`, `fluid`;
  - `layout.sidebar.variant`: `default`, `dark`;
  - `layout.sidebar.collapsed`: boolean;
  - `layout.navbar.enabled`: boolean;
  - `layout.navbar.variant`: `default`, `dark`;
  - `layout.navbar.sticky`: boolean;

- grouped navigation schema:
  - section/group title;
  - nested children;
  - disabled items;
  - active nested item;
  - duplicate nav path rejection;
  - nav path must match a declared page path;
  - external links rejected by default;

- centralized safe theme rendering:
  - `data-bs-theme` generated from validated schema;
  - CSS classes/tokens generated from safe enum values only;
  - no arbitrary CSS string from config;
  - no arbitrary JS from config;
  - no localStorage-driven persistent theme mutation;

- docs/tests update.

Не включено:

- runtime theme editor;
- user-uploaded logos;
- arbitrary color hex input;
- arbitrary CSS editor;
- arbitrary JS;
- custom HTML blocks;
- product adapters;
- block registry/rendering;
- no-code dashboard builder;
- auth/session;
- config apply.

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI where theme, layout shell options and grouped navigation are controlled by validated `config/schema.yml`.

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh routes`
- `./start.sh web --host 127.0.0.1 --port 8780`
- valid theme/layout config loads;
- invalid theme mode rejected;
- invalid primary/base/font/radius/density rejected;
- invalid layout type rejected;
- unsafe/arbitrary CSS field rejected;
- arbitrary JS field rejected;
- dark mode renders;
- light mode renders;
- primary color enum renders as controlled class/token;
- grouped navigation renders;
- disabled nav item renders but is not linked;
- active nested navigation item renders;
- duplicate nav path rejected;
- external nav link rejected unless explicitly supported later;
- no external assets introduced;
- no hidden runtime theme mutation.

#### DoD

- theme/layout/navigation are schema-driven;
- Iteration 3 hardcoded dark default is replaced by validated schema value;
- products can customize BeeUI safely through schema;
- no arbitrary CSS/JS injection;
- no external assets/tracking introduced;
- grouped navigation works without product-specific assumptions;
- no product-specific domain logic introduced;
- no new execution/write authority introduced.

---

## Этап 3 — Blocks and component system

### Итерация 5 — Block registry and static dashboard blocks v1

**Статус:** DONE

#### Goal

Добавить reusable block registry и первые production-safe dashboard blocks, чтобы страницы BeeUI собирались из declarative schema, а не из hardcoded HTML или empty placeholder.

#### Почему это нужно

После Iteration 4 BeeUI умеет рендерить schema-driven shell: theme, layout, navigation и pages. Но страницы всё ещё не имеют reusable content layer: `pages[].blocks` существует только как placeholder.

До data sources, selector resolver, adapters и BeeCap integration нужно зафиксировать безопасный block contract:

- какие block types поддерживаются;
- как blocks объявляются в schema;
- как blocks размещаются на странице;
- как renderer registry выбирает renderer;
- как invalid block config fails fast;
- как HTML escaping сохраняется для всех text values.

#### Scope

Включено:

- top-level `blocks` section in `config/schema.yml`;
- page-level block placement through existing `pages[].blocks`;
- block model;
- block placement model;
- block registry;
- renderer registry;
- layout rows/columns through simple responsive width values;
- block ids;
- block titles/subtitles;
- static/literal block values only, без resolver expressions и adapter-backed lookups;
- empty state;
- degraded state;
- error state;
- unknown block type rejection;
- unknown block reference rejection;
- duplicate block id rejection;
- invalid block width rejection;
- safe value rendering with Jinja autoescape;

Renderers:

- `metric_card`;
- `kpi_grid`;
- `status_card`;
- `table_card`;
- `links_card`;
- `alert_card`;
- `text_card`;
- `progress_card`;

Example:

```yaml
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

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    value: run_demo_001
    subtitle: Demo static value

  runtime_status:
    type: status_card
    title: Runtime
    status: ok
    value: Ready
```

Не включено:

- data sources;
- selector resolver;
- adapter-backed values;
- product adapters;
- charts;
- maps;
- artifact browser;
- arbitrary HTML block;
- arbitrary JS block;
- Markdown rendering from untrusted input;
- drag-and-drop editor;
- config apply/write.

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI pages assembled from validated reusable blocks declared in `config/schema.yml`.

#### Checks

- valid blocks schema loads;
- missing top-level `blocks` behavior is explicit and tested;
- metric card renders;
- KPI grid renders;
- status card renders;
- table card renders;
- links card renders;
- alert card renders;
- text card renders;
- progress card renders;
- empty block state renders;
- degraded/error state renders from static schema state;
- unknown block type rejected;
- unknown block reference rejected;
- invalid width rejected;
- unsafe text escaped;
- no arbitrary HTML/JS accepted from config;
- no product-specific semantics introduced;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`.

#### DoD

- blocks render from schema;
- renderer registry is domain-neutral;
- layout widths work;
- invalid block config fails fast;
- missing optional static fields do not crash the page;
- no arbitrary HTML/JS from config;
- no data resolver/adapter/product logic introduced;
- Jinja autoescape remains enabled.

### Итерация 6 — Tabler component catalog and reusable primitives v0

**Статус:** DONE

#### Goal

Создать internal component catalog и минимальный набор reusable Tabler-compatible template primitives, чтобы будущие pages/blocks/admin/operator screens собирались из controlled components, а не через копирование HTML из Tabler examples.

#### Почему это нужно

Iteration 5 добавила schema-driven blocks, но сами block templates всё ещё могут начать дублировать card/table/badge/form/progress HTML.

До data resolver, adapters, artifact browser и config/operator UI нужно централизовать безопасные UI primitives:

- common markup;
- naming rules;
- escaping expectations;
- allowed/forbidden component patterns;
- plugin placeholders without external JS/CDN;
- visible catalog routes for review and visual smoke.

#### Scope

Включено:

- internal read-only component catalog routes:
  - `/components`;
  - `/components/interface`;
  - `/components/forms`;
  - `/components/layout`;
  - `/components/extra`;
  - `/components/plugins`;

- route registration under existing `route_prefix`;
- navigation link to component catalog in demo schema, if consistent with current schema rules;
- reusable template primitives under `src/beeui_module/web/templates/components/primitives/` or equivalent controlled location;
- safe sample data defined in Python or static template context, not user-controlled HTML;
- catalog templates that render examples through reusable primitives;
- no external CDN/scripts/assets;
- no `|safe` for sample text values;
- tests for route render and escaping.

Reusable primitives v0:

- `alert`;
- `badge`;
- `breadcrumb`;
- `button`;
- `button_group`;
- `card`;
- `card_header`;
- `dropdown`;
- `empty_state`;
- `tabs`;
- `table`;
- `data_grid`;
- `form_input`;
- `form_select`;
- `form_checkbox`;
- `form_radio`;
- `form_textarea`;
- `form_selectgroup`;
- `pagination`;
- `progress`;
- `status_dot`;
- `avatar_placeholder`;
- `modal_shell`;
- `toast_placeholder`;
- `offcanvas_shell`;

Plugin placeholders:

- `chart_container`;
- `map_container`;
- `datatable_container`;

Docs:

- `docs/COMPONENTS.md`;
- component naming rules;
- allowed/forbidden components;
- safe usage examples;
- relationship between primitives and block renderers.

Не включено:

- full Tabler demo copy;
- redesign of existing Iteration 5 block renderers unless a tiny reuse cleanup is necessary;
- WYSIWYG editor;
- Dropzone/upload;
- Fullcalendar runtime integration;
- external maps;
- external charts CDN;
- arbitrary JS plugin config;
- user-supplied HTML;
- sponsor/marketing/demo pages;
- data resolver;
- product adapters;
- artifact browser;
- config apply;
- auth/session;
- operator actions.

#### Deliverable

BeeUI exposes a visible read-only component catalog and centralizes common Tabler-compatible primitives for future pages/blocks.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- component catalog routes render;
- each primitive renders with safe sample data;
- text-bearing primitives escape unsafe strings;
- no external scripts/styles/tracking references;
- no unsafe Jinja `|safe`;
- no broken static references;
- no product-specific semantics introduced.

#### DoD

- BeeUI has visible component catalog pages;
- common Tabler-compatible primitives are centralized;
- future product pages/blocks can reuse primitives instead of copying HTML;
- plugin placeholders are inert and do not load external JS;
- unsafe/demo-only Tabler features are explicitly excluded;
- no new write/action/auth/adapter authority introduced.

### Итерация 7 — Data sources and selector resolver v0

**Статус:** DONE

#### Goal

Добавить read-only data source abstraction и selector resolver, чтобы BeeUI blocks могли получать значения из controlled demo/static payloads через стабильный resolver envelope, а не только из hardcoded literal fields в block schema.

#### Почему это нужно

После Iteration 5 BeeUI умеет рендерить static/literal blocks из `config/schema.yml`, а после Iteration 6 имеет reusable component primitives. Но до product adapters нужно отделить:

- block layout/config;
- источник данных;
- selector resolution;
- partial/missing/error state.

Без этого BeeCap/BeeAgent integration начнёт протаскивать product-specific поля напрямую в generic block renderers.

Iteration 7 фиксирует безопасный read-only data layer v0, который позже сможет принимать adapter-backed payloads, но сейчас работает только с controlled demo/static data.

#### Scope

Включено:

- новый пакет `src/beeui_module/data/`:
  - `models.py`;
  - `sources.py`;
  - `selectors.py`;
  - `resolver.py`;
  - `envelopes.py` или equivalent minimal structure;

- data source model:
  - `demo`;
  - `static`;

- static source loading from controlled config/example path only;
- in-memory demo source;
- selector syntax for nested fields:
  - `dashboard.latest_run.id`;
  - `dashboard.kpis.total_runs`;
  - `runs[0].id` if list index support is implemented;
  - list selection where needed for tables/KPI grids;

- selector validation:
  - no Python eval;
  - no Jinja expression execution;
  - no method calls;
  - no arbitrary filesystem paths;
  - clear invalid selector errors;

- resolver envelope:

```json
{
  "status": "ok|partial|error",
  "data": {},
  "warnings": [],
  "source": {
    "type": "demo|static|unknown",
    "id": "..."
  }
}
```

- missing selector behavior:
  - scalar missing values become unavailable/degraded;
  - list/table missing values become empty/degraded;
  - page does not crash;

- block schema extension for resolver-backed values, using a controlled shape, for example:

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

или equivalent minimal naming, если текущий block model лучше поддерживает другой формат;

- backward compatibility:
  - existing literal block configs continue to work;
  - resolver-backed fields are optional;
  - no required config/settings keys unless necessary;

- tests for:
  - demo source load;
  - static YAML/JSON source load;
  - selector success;
  - selector missing;
  - selector invalid;
  - list selector;
  - scalar selector;
  - invalid source;
  - partial envelope;
  - stable envelope shape;
  - block degraded/empty render on missing data;
  - no secret-looking test values leaked unexpectedly;
  - no arbitrary HTML/JS accepted through data payload.

Не включено:

- BeeCap adapter;
- BeeAgent adapter;
- production HTTP adapter;
- direct product storage crawling;
- artifact browser;
- API routes;
- write sources;
- config apply;
- auth/session;
- operator actions;
- arbitrary YAML editor;
- Jinja/Python expression evaluation;
- full migration of every block renderer if a minimal resolver-backed subset is enough.

#### Deliverable

BeeUI has a read-only data resolver layer and at least a representative set of existing dashboard blocks can render values from resolver envelopes while existing literal blocks remain supported.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- demo source load;
- static source load;
- selector success;
- selector missing;
- selector invalid;
- list selector;
- scalar selector;
- invalid source;
- partial/error envelope shape;
- missing data renders degraded/empty state;
- existing Iteration 5/6 pages still render;
- no external scripts/assets introduced;
- no product-specific semantics introduced.

#### DoD

- resolver envelope shape is stable;
- data resolver is read-only;
- block renderers do not know source internals;
- missing/partial data does not crash page rendering;
- existing literal block schema remains backward compatible;
- no product adapter or product-specific assumptions introduced;
- docs explain selector syntax, source types, envelope shape and safe usage.

---

## Этап 4 — Product integration contracts

### Итерация 8 — Product adapter contract v0

**Статус:** DONE

#### Goal

Зафиксировать generic `ProductUiAdapter` contract как единственную точку подключения Bee-продуктов к BeeUI, чтобы BeeCap/BeeAgent могли отдавать dashboard/runs/artifacts/config/actions через стабильный read-model boundary без попадания product-specific логики в BeeUI core.

#### Почему это нужно

После Iteration 7 BeeUI умеет рендерить schema-driven UI и resolver-backed demo/static data. Следующий блокер для подключения BeeCap/BeeAgent — отсутствие стабильного adapter contract.

Без этого BeeUI начнёт читать product storage, config или domain internals напрямую, что создаст второй source of truth и нарушит правило:

```text
BeeUI renders.
Product decides.
```

Iteration 8 фиксирует только contract-level integration point. Concrete BeeCap/BeeAgent adapters, routes, artifact browser and embedded mount API остаются следующими итерациями.

#### Scope

Включено:

- новый пакет `src/beeui_module/adapters/`;

- `ProductUiAdapter` protocol/base class;

- adapter metadata model:
  - `product_id`;
  - `title`;
  - `version`;
  - `capabilities`;
  - `supported_pages`;

- stable adapter result/envelope model:
  - `status: ok|partial|error`;
  - `data`;
  - `warnings`;
  - `meta`;
  - error shape with stable code/message;

- required read-only methods:
  - `get_dashboard()`;
  - `list_runs()`;
  - `get_run(run_id)`;
  - `list_artifacts(run_id)`;
  - `read_artifact(run_id, artifact_id)`;
  - `get_config_read_model()`;

- optional write/action/config methods disabled by default:
  - `validate_config_candidate(candidate)`;
  - `list_actions()`;
  - `preview_action(action_id, payload)`;
  - `execute_action(action_id, payload)`;

- stable adapter errors:
  - `InvalidIdError`;
  - `NotFoundError`;
  - `PermissionDeniedError`;
  - `UnavailableError`;
  - `ValidationError`;
  - `AdapterError`;

- safe ID validation helpers:
  - product id;
  - run id;
  - artifact id;
  - action id;

- fake adapter for tests only;

- tests for:
  - metadata;
  - dashboard;
  - runs;
  - run detail;
  - artifacts list;
  - artifact read;
  - config read-model;
  - invalid run id rejection;
  - invalid artifact id rejection;
  - unavailable optional methods;
  - error envelope shape;
  - read-only methods do not mutate returned state;
  - no product-specific imports/logic.

Не включено:

- concrete BeeCap adapter;
- concrete BeeAgent adapter;
- direct product filesystem crawling;
- artifact browser routes;
- `/api/*` route contract;
- embedded mount API;
- direct execution authority;
- auth/session;
- config apply/write;
- operator action execution;
- standalone HTTP adapter.

#### Deliverable

BeeUI has a stable product integration contract and fake adapter tests. BeeCap/BeeAgent can implement this contract later without BeeUI learning product internals.

#### Checks

- fake adapter dashboard;
- fake adapter runs;
- fake adapter run detail;
- fake adapter artifact list/read;
- fake adapter config read-model;
- invalid run id rejection;
- invalid artifact id rejection;
- unavailable optional method behavior;
- adapter error envelope shape;
- no mutation in read-only methods;
- no product-specific domain logic introduced;
- `uv run pytest -q`.

#### DoD

- product integration point is stable;
- BeeUI does not read product internals without adapter;
- adapter errors are explicit and normalized;
- invalid IDs are handled safely;
- write/action/config mutation methods are unavailable unless a product explicitly implements them;
- fake adapter proves the contract without adding BeeCap/BeeAgent dependencies;
- docs explain adapter boundary and non-goals.

### Итерация 9 — BeeCap adapter fixtures MVP

**Статус:** DONE

#### Goal

Добавить BeeCap-compatible adapter/read-model MVP на fixture-based данных, чтобы проверить, что generic `ProductUiAdapter` contract подходит для BeeCap dashboard/runs/artifacts без переноса BeeCap trading/domain logic в BeeUI.

#### Почему это нужно

После Iteration 8 BeeUI имеет generic adapter contract, но контракт ещё не проверен на реалистичных BeeCap-like данных: latest run, runs, artifact references, MRKT/Binance/paper partial states, corrupted/missing artifacts.

До embedded mount API и BeeCap dashboard parity нужно доказать, что BeeUI может принимать BeeCap-shaped read-model через adapter boundary, не читая BeeCap internals напрямую и не превращаясь во второй source of truth.

#### Scope

Включено:

- `BeeCapUiAdapter` fixture/reference skeleton inside BeeUI test/support area or controlled adapter module, без dependency на реальный BeeCap package;
- BeeCap-like dashboard read-model from fixtures;
- latest run discovery from fixture/read-model data;
- run list from fixtures;
- run detail from fixtures;
- artifact references from fixtures;
- MRKT summary fields only when provided by fixture/read-model;
- Binance/paper summary fields only when provided by fixture/read-model;
- partial/missing/corrupted artifact scenarios;
- no latest run scenario;
- fixture-based tests under `tests/fixtures/beecap/`;
- `examples/beecap_embedded/beeui.yml`;
- `docs/INTEGRATION.md` with BeeCap integration boundary notes;
- docs update for current/future status.

Не включено:

- dependency/import on real `beecap_module`;
- full replacement of BeeCap current web;
- route-level adapter injection into `create_beeui_app(...)`;
- embedded mount helper;
- generic artifact browser routes;
- direct product filesystem crawling;
- trading/profit/order calculations inside BeeUI;
- config apply;
- operator actions;
- auth/session;
- no-code builder.

#### Expected BeeCap side

Real BeeCap integration should later live in BeeCap, for example:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
```

BeeUI may contain only a fixture/reference adapter proving the contract.

#### Deliverable

BeeUI has a BeeCap-compatible fixture adapter and tests proving that dashboard/runs/artifact-reference read-models can be produced through `ProductUiAdapter` without BeeUI reading BeeCap internals or implementing trading logic.

#### Checks

- BeeCap-like fixture dashboard;
- latest run fixture;
- runs list fixture;
- run detail fixture;
- artifact references fixture;
- MRKT partial fixture scenario;
- Binance/paper partial fixture scenario;
- no latest run scenario;
- corrupted artifact metadata scenario;
- invalid run id rejection;
- invalid artifact id rejection;
- no secret leakage;
- no path traversal;
- source fixtures not mutated;
- no `beecap_module` dependency/import;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### DoD

- BeeCap-like adapter/read-model works only through `ProductUiAdapter`;
- BeeUI contains no trading calculations;
- BeeUI does not read arbitrary BeeCap storage;
- BeeCap domain semantics stay in adapter/read-model fixtures and later real BeeCap-side implementation;
- partial/corrupted/missing states are explicit;
- source fixtures remain canonical and read-only;
- docs explain that real BeeCap adapter belongs to BeeCap-side integration.

### Итерация 10 — Embedded mount API v0

**Статус:** DONE

#### Goal

Сделать минимальный стабильный embedded API, через который BeeCap сначала, а позже BeeAgent, смогут подключать BeeUI как package dependency: загружать BeeUI UI config из product-side файла, передавать product metadata и adapter instance, а также монтировать BeeUI под безопасным route prefix без ручной склейки FastAPI/Jinja/static setup.

#### Почему это нужно

После Iteration 8 BeeUI имеет generic `ProductUiAdapter` contract, а после Iteration 9 контракт проверен на BeeCap-shaped fixture payloads. Но BeeUI ещё нельзя удобно подключить в BeeCap runtime: `create_beeui_app(...)` не принимает adapter/config path/product metadata, а `mount_beeui(...)` отсутствует.

Без Iteration 10 каждый продукт начнёт писать собственную glue-логику вокруг BeeUI, что снова приведёт к дублированию web setup и нарушит цель BeeUI как reusable UI framework.

#### Scope

Включено:

- расширение public app factory `create_beeui_app(...)`;
- новый helper `mount_beeui(...)`;
- загрузка UI schema/config по `config_path`;
- поддержка уже загруженного `ui_config`;
- поддержка уже загруженных `settings`;
- product metadata injection:
  - `product_id`;
  - `product_title`;
- adapter injection:
  - adapter instance accepted;
  - adapter shape validated against `ProductUiAdapter` minimum contract;
  - adapter stored in `app.state.beeui_adapter`;
  - adapter metadata stored in `app.state.beeui_product`;
- route prefix support для embedded mount;
- static/templates registration remains package-local;
- startup validation with clear errors;
- route collision guard/notes for mount helper;
- tests for app factory, mount helper, route prefix, static route, invalid adapter, config path validation;
- docs update in `docs/WEB_UI.md`, `docs/INTEGRATION.md`, `README.ru.md`, `docs/ROADMAP.md`.

Не включено:

- production BeeCap adapter;
- BeeAgent adapter implementation;
- adapter-backed block data source;
- adapter-backed dashboard rendering;
- `/api/*` routes;
- run detail routes;
- artifact browser routes;
- config apply;
- operator actions;
- auth/session;
- CORS;
- standalone multi-product service;
- distributed deployment;
- product runtime control.

#### Deliverable

BeeCap can create or mount a BeeUI FastAPI app through one stable embedded API, passing product metadata, a BeeCap-side adapter instance, and a BeeCap-side `beeui.yml` config path, while current demo routes/static/templates continue to work.

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

#### Checks

- embedded app factory with loaded `settings` / `ui_config`;
- embedded app factory with `config_path`;
- product metadata injection;
- adapter injection into `app.state`;
- invalid adapter rejection;
- missing/invalid config path rejection;
- route prefix test;
- static path test under prefix;
- mount helper test;
- route collision rejection or explicit safe error;
- existing demo mode remains compatible;
- no new `/api/*` route surface;
- no product-specific logic introduced;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### DoD

- BeeCap can connect BeeUI through minimal public app factory or mount helper;
- embedded mode remains MVP integration path;
- product-specific glue is minimal;
- adapter is accepted and validated, but not used for product rendering yet;
- current demo behavior remains backward-compatible;
- no hidden product assumptions;
- no new execution/write authority;
- docs clearly state that adapter-backed dashboard/runs/artifact rendering is later scope.

### Итерация 11 — Generic artifact browser v1

**Статус:** DONE

#### Goal

Добавить минимальный reusable read-only artifact browser для Bee-продуктов, чтобы BeeUI мог показывать allowlisted product artifacts через `ProductUiAdapter`, без прямого чтения product storage и без превращения BeeUI в filesystem browser.

#### Почему это нужно

После Iteration 10 BeeUI можно embedded-подключить к BeeCap и передать adapter, но UI всё ещё не умеет показывать product artifacts через этот adapter.

Для BeeCap это blocker: dashboard и run overview без artifact links/viewer будут почти бесполезны, потому что BeeCap operator должен быстро открывать evidence/source artifacts: JSON, JSONL, summaries, reports, health/runtime outputs.

Iteration 11 должна дать минимальный общий artifact layer, который Iteration 12 сможет использовать для BeeCap dashboard parity.

#### Scope

Включено:

- новый package layer `src/beeui_module/artifacts/`;
- artifact metadata model;
- artifact preview model;
- JSON preview;
- JSONL bounded preview;
- text preview;
- unsupported/binary metadata-only preview;
- malformed JSON/JSONL handling as partial/error state;
- large artifact preview limits;
- safe `run_id` and `artifact_id` validation through existing adapter ID helpers;
- artifact access only through `ProductUiAdapter.list_artifacts(...)` and `ProductUiAdapter.read_artifact(...)`;
- no direct product storage traversal from BeeUI;
- no raw filesystem path route params;
- read-only HTML artifact list/view routes;
- minimal read-only JSON routes for artifact list/read preview;
- route prefix compatibility;
- embedded adapter compatibility;
- graceful unavailable state when adapter is missing;
- redaction hook placeholder with no complex policy engine;
- tests for JSON, JSONL, text, malformed, large, unsupported, invalid IDs, non-allowlisted artifacts, no mutation, no secret leakage;
- docs update.

Suggested routes:

```text
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

Допустимо реализовать `GET /runs/{run_id}/artifacts/{artifact_id}` в Iteration 11, потому что иначе HTML artifact browser будет неполным.

Не включено:

- arbitrary filesystem browser;
- direct storage traversal from BeeUI;
- artifact mutation;
- upload/edit/delete;
- binary viewers beyond metadata-only;
- syntax highlighting dependency;
- full stable frontend API contract from Iteration 14;
- run detail page from Iteration 13;
- BeeCap production adapter;
- BeeAgent adapter;
- config UI;
- operator actions;
- auth/session;
- standalone service.

#### Deliverable

BeeUI can list and preview allowlisted product artifacts through `ProductUiAdapter` in embedded mode, with safe HTML/API read-only routes and bounded previews for JSON, JSONL and text artifacts.

#### Checks

- JSON artifact preview;
- JSONL artifact preview;
- malformed JSON handling;
- malformed JSONL row handling;
- text artifact preview;
- unsupported/binary metadata-only preview;
- large artifact preview limit;
- invalid `run_id` rejection;
- invalid `artifact_id` rejection;
- non-allowlisted artifact rejection;
- adapter missing/unavailable state;
- route prefix compatibility;
- no direct product filesystem read;
- no mutation;
- no secrets leakage;
- no `beecap_module` / `beeagent_module` import;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### Deliverable summary

Реализовано:

- новый пакет `src/beeui_module/artifacts/` с моделями, preview-логикой, redaction и routes;
- `ArtifactRef` и `ArtifactPreview` модели;
- JSON preview через `build_preview()` с парсингом из dict/list/str;
- JSONL preview с ограничением строк (500) и row-level warnings для malformed строк;
- text preview с ограничением символов (100K);
- unsupported/binary -> metadata-only preview;
- malformed JSON -> error state, не crash;
- malformed JSONL rows -> row-level warnings, не crash;
- large artifact limits (512KB для JSON/JSONL, 100K chars для text);
- safe ID validation через `validate_run_id()` и `validate_artifact_id()` в route handlers;
- read-only HTML artifact list + preview routes;
- read-only JSON API artifact list + preview routes;
- route prefix compatibility;
- embedded adapter compatibility через `request.app.state.beeui_adapter`;
- graceful unavailable state (503 HTML / JSON error) при отсутствии adapter;
- redaction placeholder (`redact_value`, `redact_text`) для `secret`/`token`/`password`/`api_key`/`api_secret` и аналогичных ключей;
- 46 тестов в `tests/test_artifacts.py`: redaction, preview (JSON/JSONL/text/malformed/large/unsupported), HTML routes, JSON API routes, invalid IDs, missing adapter, route prefix, security (escaping, no mutation, no write routes, no beecap import);
- обновлены тесты embedded (ожидаемые /api/\* routes);
- обновлены docs: ROADMAP, WEB_UI, INTEGRATION, README.

#### DoD

- artifact browser is reusable and product-neutral;
- source artifacts remain canonical and read-only;
- arbitrary file access is impossible from BeeUI routes;
- corrupted artifacts render as partial/error state instead of crashing;
- large artifacts are bounded;
- product adapter owns allowlist and artifact resolution;
- BeeUI does not invent artifact semantics;
- docs clearly state that BeeCap production artifact mapping belongs in BeeCap-side adapter.

---

## Этап 5 — Adapter-backed Product Console MVP

### Итерация 12 — Adapter-backed Product Console routes/API MVP

**Статус:** DONE

#### Goal

Сделать BeeUI generic adapter-backed product console MVP: dashboard, runs, run detail, venue dashboards and stable read-only JSON API through `ProductUiAdapter`, without product-specific domain logic in BeeUI core.

#### Почему это нужно

После Iteration 10–11 BeeUI уже можно embedded-подключить к продукту и показывать artifacts через adapter, но BeeUI ещё не является полноценной product console.

Сейчас BeeUI умеет:

- запускать FastAPI/Jinja/Tabler shell;
- рендерить schema-driven demo/static pages;
- принимать product adapter через `create_beeui_app(...)` / `mount_beeui(...)`;
- показывать allowlisted artifacts через adapter.

Но BeeUI ещё не умеет generic adapter-backed rendering для:

- dashboard;
- runs list;
- run detail;
- venue dashboards;
- stable read-only API envelope для этих read-models.

Без этой итерации BeeCap UI-25 не сможет сделать `/beeui` practically useful без повторного расширения BeeCap legacy templates или product-specific logic внутри BeeUI.

Iteration 12 должна дать reusable generic console layer. BeeCap-specific metrics/calculations remain BeeCap-side adapter/read-model responsibility.

#### Change level

**runtime-risk**

Причина:

- добавляются новые HTML/API routes;
- добавляется stable read-only API envelope;
- adapter payloads начинают рендериться как product console;
- меняется route/API behavior;
- operator-facing UI can affect decisions.

Security-sensitive checks are required for:

- `run_id` validation;
- `venue_id` validation;
- adapter error normalization;
- HTML escaping;
- source/evidence links;
- no mutation from GET routes;
- no secrets in HTML/API/logs.

#### Scope

**Включено:**

- adapter-backed dashboard routes:

```text
GET /
GET /api/dashboard
```

- adapter-backed runs routes:

```text
GET /runs
GET /runs/{run_id}
GET /api/runs
GET /api/runs/{run_id}
```

- adapter-backed venue dashboard routes:

```text
GET /venues/{venue_id}
GET /api/venues/{venue_id}/dashboard
```

- keep existing artifact browser routes from Iteration 11:

```text
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

- introduce generic API envelope for new read-only API routes:

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

- introduce error envelope for new read-only API routes:

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

- normalize adapter result statuses:
  - `ok`;
  - `partial`;
  - `error`;
  - unavailable adapter state;

- add generic product console renderers/templates for:
  - dashboard;
  - runs list;
  - run detail;
  - venue dashboard;

- generic UI support for adapter payload sections:
  - KPI grid;
  - metric cards;
  - status cards;
  - tables;
  - links;
  - source/evidence links;
  - warnings;
  - empty states;
  - degraded states;
  - partial states;

- extend `ProductUiAdapter` only if needed with product-neutral read-only methods:

```python
list_venues()
get_venue_dashboard(venue_id: str)
```

- route prefix compatibility;
- embedded mount compatibility;
- fake adapter / fixture adapter tests;
- docs update:
  - `docs/API_CONTRACT.md` if present or created;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/ROADMAP.md`;
  - `README.ru.md`.

#### Не включено

- BeeCap imports;
- BeeAgent imports;
- MRKT/Binance/BeeCap-specific calculations;
- direct product storage reads;
- arbitrary filesystem browsing;
- config apply;
- operator actions;
- auth/session/RBAC;
- standalone BeeUI service;
- React/Vue/Svelte frontend;
- no-code builder;
- provider calls;
- broker calls;
- runtime calls;
- replacing BeeCap `/` route;
- BeeCap parity content.

#### Deliverable

BeeUI can render a useful generic read-only product console from any product adapter.

Expected route surface after this iteration:

```text
GET /
GET /api/dashboard

GET /runs
GET /api/runs

GET /runs/{run_id}
GET /api/runs/{run_id}

GET /venues/{venue_id}
GET /api/venues/{venue_id}/dashboard

GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

BeeCap can then implement UI-25 by enriching `BeeCapUiAdapter` payloads without changing BeeUI core.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- dashboard route with fake adapter;
- dashboard API with fake adapter;
- runs route with fake adapter;
- runs API with fake adapter;
- run detail route with fake adapter;
- run detail API with fake adapter;
- venue dashboard route with fake adapter;
- venue dashboard API with fake adapter;
- artifact routes still work;
- invalid `run_id` rejected;
- invalid `venue_id` rejected;
- adapter missing/unavailable state;
- adapter error envelope;
- adapter partial envelope;
- malformed adapter payload renders degraded/error state;
- route prefix compatibility;
- embedded mount compatibility;
- source/evidence links rendered safely;
- HTML autoescape preserved;
- no mutation from GET routes;
- no secrets in HTML/API/logs;
- no external assets/scripts introduced;
- no `beecap_module` / `beeagent_module` import.

#### DoD

- BeeUI has adapter-backed dashboard/runs/run detail/venue pages;
- server-rendered UI and JSON API are aligned;
- API envelope is stable and documented;
- Product adapter remains the only source of product semantics;
- BeeUI does not invent product metrics;
- BeeUI does not read product storage directly;
- BeeUI remains read-only;
- no product-specific logic is introduced into BeeUI core;
- BeeCap UI-25 can proceed by implementing BeeCap-side read-models only.

### Итерация 12.1 — Adapter-backed Tabler dashboard blocks renderer

**Статус:** DONE

#### Goal

Добавить в BeeUI generic renderer для adapter-backed `layout[]` blocks, чтобы product adapters могли отдавать структурированную композицию dashboard/run/venue pages, а BeeUI рендерил её как полноценную Tabler operator console, без product-specific логики в BeeUI.

#### Почему это нужно

После adapter-backed Product Console MVP BeeUI умеет получать dashboard/runs/run detail/venue payloads через `ProductUiAdapter`, но primary pages могут выглядеть как generic/debug payload. Это блокирует BeeCap MVP после route switch: данные и маршруты есть, но операторский cockpit не достигнут.

BeeUI должен получить reusable визуальный слой:

- Tabler grid/cards/tables/badges/alerts;
- compact operator blocks;
- degraded/empty/partial states;
- source/evidence links;
- fallback raw/debug panel only when no structured layout exists.

BeeCap/BeeAgent остаются владельцами product semantics. BeeUI только рендерит.

#### Change level

**runtime-risk**

Security-sensitive checks required for:

- HTML escaping;
- source links;
- adapter-provided URLs/labels;
- route/API exposure;
- invalid/malformed block payloads.

#### Scope

**Включено:**

- поддержать optional `layout` field в adapter-backed payloads;
- рендерить `layout[]` на страницах:
  - `/`;
  - `/runs`;
  - `/runs/{run_id}`;
  - `/venues/{venue_id}`;
- оставить current generic payload renderer как fallback;
- добавить generic block renderers:
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
- поддержать safe width mapping to Tabler/Bootstrap column classes;
- рендерить malformed/unsupported blocks as degraded alerts, not crashes;
- сохранять API envelopes and existing route behavior;
- добавить tests для block rendering/fallback/security;
- обновить docs:
  - `docs/ROADMAP.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`.

**Не включено:**

- BeeCap-specific logic;
- BeeAgent-specific logic;
- config apply;
- auth/session/CSRF;
- operator actions;
- broker/provider/runtime calls;
- new runtime artifacts;
- arbitrary HTML/JS from adapter/config;
- visual builder;
- external CDN/assets/scripts.

#### Deliverable

BeeUI renders adapter-provided `layout[]` as product-grade Tabler dashboard pages, while products keep all domain-specific metrics and semantics inside their adapters/read-models.

#### DoD

- fake adapter renders `/`, `/runs`, `/runs/{run_id}`, `/venues/{venue_id}` through `layout[]`;
- each supported block type has tests;
- unsupported/malformed blocks render explicit degraded state;
- existing generic renderer still works when `layout` is absent;
- adapter text is escaped;
- source links are safe internal links only;
- no external assets/scripts;
- no mutation from GET routes;
- no secrets in HTML/API/logs;
- docs describe `layout[]` block contract.

### Итерация 12.2 — Tabler visual parity hardening for adapter-backed console

**Статус:** DONE

#### Goal

Довести adapter-backed BeeUI product console до визуально пригодного Tabler-grade MVP: dashboard/runs/run detail/venue pages должны выглядеть как читаемая operator console, а не как cramped generic/debug cards.

#### Почему это нужно

Iteration 12.1 добавила `layout[]` renderer для adapter-backed pages, но фактический BeeCap embedded результат остаётся визуально неприемлемым:

- KPI/metric blocks слипаются в inline text;
- cards/tables/badges не дают нормальную визуальную иерархию;
- root dashboard и venue pages не выглядят как Tabler operator cockpit;
- текущий result не соответствует цели “product-grade Tabler dashboard pages”;
- BeeCap UI-28 Config/Admin/Controls нельзя делать поверх слабого UI-фундамента.

BeeUI должен владеть rendering/layout/templates/static/common UI. BeeCap должен отдавать только adapter/read-model/artifacts/callbacks.

#### Change level

**runtime-risk**

Причина:

- меняется operator-facing HTML rendering;
- меняется визуальный contract adapter-backed routes;
- adapter-provided payload становится основой operator decisions;
- сохраняются route/API contracts, но HTML behavior меняется существенно.

Security-sensitive checks required for:

- HTML escaping;
- safe internal links;
- no secrets in HTML/API/logs;
- no external CDN/scripts/tracking;
- no provider/broker/runtime calls;
- no mutation from GET routes.

#### Scope

**Включено:**

- привести shell к Tabler-compatible structure:
  - `.page`;
  - `.navbar.navbar-vertical`;
  - `.page-wrapper`;
  - `.page-header`;
  - `.page-body`;
  - `.container-xl`;
  - `.row.row-deck.row-cards`;

- проверить и исправить local Tabler asset layer:
  - заменить слабый compatibility placeholder на reviewed local compiled Tabler core assets;
  - не использовать CDN;
  - не включать Tabler preview/demo telemetry, sponsor, PostHog, marketing/demo scripts;

- улучшить rendering текущих adapter-backed block types:
  - `hero_snapshot`;
  - `metric_card`;
  - `kpi_strip`;
  - `venue_summary_grid`;
  - `mode_cards`;
  - `status_table`;
  - `event_table`;
  - `attention_list`;
  - `artifact_links`;
  - `raw_json_panel` только как explicit fallback/debug block;

- сделать primary pages visually usable above the fold:
  - `/`;
  - `/runs`;
  - `/runs/{run_id}`;
  - `/venues/mrkt`;
  - `/venues/binance`;

- сохранить product-neutral rendering:
  - без MRKT/Binance/BeeCap-specific calculations inside BeeUI;
  - product semantics только из adapter payload;

- сохранить current API envelopes and route behavior;

- добавить visual contract tests:
  - Tabler layout/card/table classes;
  - no raw/debug panel when `layout[]` exists;
  - unsafe text escaped;
  - unsafe/external links rejected or rendered inert;
  - malformed/unsupported blocks render degraded alerts;

- обновить docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `README.ru.md`, если меняется asset/component contract.

**Не включено:**

- config apply;
- admin/support parity;
- auth/session/CSRF;
- operator actions;
- broker/provider/runtime calls;
- BeeCap-specific calculations;
- BeeAgent-specific calculations;
- arbitrary HTML/JS from adapter/config;
- visual builder;
- charts/maps;
- standalone mode;
- deleting `src/beecap_module/web`;
- rebuilding BeeCap legacy templates.

#### Deliverable

BeeUI adapter-backed product console renders as a credible Tabler operator MVP.

Expected visual behavior:

- dashboard has readable cockpit layout above the fold;
- KPI strips render as cards/stat cells, not collapsed inline text;
- tables render inside proper cards;
- statuses use visible badges/alerts/dots;
- venue pages are readable without opening raw JSON;
- unsupported/malformed blocks degrade visibly without crashing;
- primary pages do not show raw/debug panels when structured `layout[]` exists.

Expected routes to verify:

```text
GET /
GET /runs
GET /runs/{run_id}
GET /venues/mrkt
GET /venues/binance
GET /runs/{run_id}/artifacts
```

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

BeeUI route smoke:

```text
GET /
GET /runs
GET /runs/{fixture_run_id}
GET /venues/mrkt
GET /venues/binance
GET /static/css/beeui.css
GET /static/vendor/tabler/...
```

BeeCap embedded smoke after local dependency/update:

```text
GET /
GET /runs
GET /venues/mrkt
GET /venues/binance
GET /legacy/
```

Security/static checks:

- no `posthog`;
- no `scripts.tabler.io`;
- no `preview.tabler.io`;
- no `docs.tabler.io`;
- no external CDN CSS/JS;
- no secrets in HTML/API/logs;
- no provider/broker/runtime calls from GET routes;
- no mutation of product `storage/` from GET routes.

#### DoD

- BeeUI visually matches a practical Tabler operator console baseline;
- fake adapter pages render through `layout[]`;
- BeeCap embedded pages are visually acceptable for daily read-only monitoring;
- all supported layout block types have tests;
- unsupported/malformed blocks render explicit degraded state;
- adapter text remains escaped;
- adapter links are safe internal links only;
- no external assets/scripts/tracking;
- no mutation from GET routes;
- no secrets in HTML/API/logs;
- no product-specific logic is introduced into BeeUI core;
- docs describe the visual/layout hardening and asset policy.

### Итерация 12.3 — Chart layout block package/rendering integrity

**Статус:** DONE

#### Goal

Устранить несогласованность BeeUI adapter-backed `layout[]` block contract: если product adapter отдаёт block type `chart`, BeeUI должен безопасно рендерить его через package-local template или явно деградировать без `500 TemplateNotFound`.

#### Почему это нужно

После Iteration 12.1/12.2 BeeUI используется как canonical renderer для BeeCap adapter-backed pages. BeeCap может отдавать chart-like blocks для run/venue/operator dashboards. Если `chart` заявлен в renderer/API contract, но шаблон отсутствует в wheel, embedded product pages падают с `500`, что блокирует BeeCap → BeeUI production parity.

#### Change level

**runtime-risk**

Security-sensitive checks required for:

- adapter-provided chart payload escaping;
- safe internal source links;
- no external CDN/scripts;
- package-local static/template integrity;
- no mutation from GET routes.

#### Scope

**Включено:**

- проверить фактический contract:
  - `layout_renderer.py`;
  - `layout_block.html`;
  - packaged wheel contents;
  - tests;
- если `chart` поддерживается renderer/API:
  - добавить `components/layout/chart.html`;
  - подключить `chart` в `layout_block.html`;
  - добавить safe degraded/empty state;
  - добавить tests на HTML render;
  - добавить package/template integrity test;
- если `chart` не должен поддерживаться:
  - убрать `chart` из supported block types/docs/tests;
  - unsupported `chart` должен рендериться как degraded block, не падать;
- обновить docs:
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/ROADMAP.md`.

**Не включено:**

- ApexCharts/JS chart engine;
- external chart CDN;
- full trading chart;
- BeeCap-specific chart calculations;
- BeeAgent-specific logic;
- provider/broker/runtime calls;
- config/admin/actions/auth;
- new config keys;
- new dependencies unless strictly justified.

#### Deliverable

BeeUI package renders or safely degrades `chart` layout blocks without `TemplateNotFound`, and wheel/package tests guarantee that required templates are included.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- fake adapter page with `chart` block renders `200`;
- unsafe chart title/labels are escaped;
- missing/empty chart data renders empty/degraded card;
- no external CDN/scripts/assets;
- no secrets in HTML/API/logs;
- package template exists in installed package/wheel context.

#### DoD

- `chart` block contract is consistent across renderer, templates, docs and tests;
- no `500 TemplateNotFound` for adapter-provided chart blocks;
- unsupported/malformed chart payloads degrade visibly;
- BeeUI remains product-neutral;
- no product-specific chart semantics added;
- docs reflect actual supported block behavior.

### Итерация 12.4 — Operator console block primitives parity

**Статус:** DONE

#### Goal

Добавить в BeeUI достаточный набор product-neutral operator-console block primitives, чтобы BeeCap/BeeAgent могли строить полноценные read-only dashboards через adapter-provided `layout[]`, без возврата к product-owned Tabler templates и без product-specific логики внутри BeeUI.

#### Почему это нужно

После Iteration 12.1/12.2/12.3 BeeUI умеет рендерить adapter-backed `layout[]` и безопасно обрабатывать `chart` blocks, но текущий набор blocks остаётся недостаточным для реальной operator console parity:

- root dashboard не может компактно показать system snapshot, venue cards, modes, KPI и attention hierarchy;
- venue pages не имеют специализированных generic state/KPI/links sections;
- runs page не имеет полноценной operator table с run/event/artifact columns;
- BeeCap parity начинает требовать расширения BeeCap legacy templates, что противоречит цели BeeUI.

BeeUI должен владеть reusable rendering primitives. Product adapter должен владеть product semantics and metrics.

Главное правило сохраняется:

```text
BeeUI renders.
Product decides.
```

#### Change level

**runtime-risk**

Причина:

- расширяется adapter-backed `layout[]` presentation contract;
- меняется operator-facing HTML rendering;
- добавляются новые block types/templates;
- adapter-provided payload влияет на operator decisions.

Security-sensitive checks required for:

- HTML escaping;
- adapter-provided labels/values/statuses/hints;
- safe internal links only;
- malformed/unsupported block degradation;
- no external CDN/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation from GET routes.

#### Scope

**Включено:**

- добавить новые adapter-backed `layout[]` block types:

```text
operator_hero
venue_card
kpi_grid
state_grid
quick_links
run_table
```

- улучшить существующие adapter-backed blocks where needed:

```text
mode_cards
attention_list
chart
```

- сохранить existing block types:

```text
hero_snapshot
metric_card
kpi_strip
venue_summary_grid
status_table
event_table
artifact_links
raw_json_panel
degraded
```

- добавить package-local templates:

```text
src/beeui_module/web/templates/components/layout/operator_hero.html
src/beeui_module/web/templates/components/layout/venue_card.html
src/beeui_module/web/templates/components/layout/kpi_grid.html
src/beeui_module/web/templates/components/layout/state_grid.html
src/beeui_module/web/templates/components/layout/quick_links.html
src/beeui_module/web/templates/components/layout/run_table.html
```

- update dispatch in:

```text
src/beeui_module/web/templates/components/layout_block.html
```

- update renderer normalization in:

```text
src/beeui_module/blocks/layout_renderer.py
```

- use Tabler-compatible local markup patterns:
  - `.card`;
  - `.card-header`;
  - `.card-title`;
  - `.card-body`;
  - `.row`;
  - `.row-cards`;
  - `.datagrid`;
  - `.table`;
  - `.badge`;
  - `.status-dot`;
  - `.list-group`;
  - `.empty`;
  - responsive column classes;

- use uploaded Tabler examples only as visual reference for safe local patterns;

- do not copy Tabler preview/demo pages wholesale;

- do not include PostHog, preview/demo scripts, sponsor/marketing blocks, remote fonts, remote OG/meta assets or external CDN;

- keep all assets package-local;

- keep Jinja autoescape;

- no `|safe` for adapter-provided values;

- links remain internal-only:
  - allow `/...`;
  - reject `//...`;
  - reject `http://...`;
  - reject `https://...`;
  - reject schemes such as `javascript:` / `mailto:`;
  - reject traversal/control characters;

- missing display values render as `n/a`, not `None`;

- malformed blocks render `degraded`, not `500`;

- update docs:
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `README.ru.md`;
  - `docs/ROADMAP.md`.

**Не включено:**

- BeeCap-specific metrics/calculations;
- BeeAgent-specific semantics;
- direct product storage reads;
- provider/broker/runtime calls;
- config apply;
- auth/session/CSRF;
- operator actions;
- visual/no-code builder;
- arbitrary HTML/JS blocks;
- copying full Tabler demo HTML;
- external CDN/assets/scripts;
- new dependencies unless strictly justified and package-local;
- full ApexCharts integration unless local vetted assets already exist and tests prove no external network references.

#### Block contracts

##### `operator_hero`

Purpose: high-level page/system/operator snapshot.

Payload:

```json
{
  "type": "operator_hero",
  "title": "System Snapshot",
  "subtitle": "Runtime: stopped",
  "status": "ok",
  "items": [
    { "label": "Latest run", "value": "run_001", "href": "/runs/run_001" },
    { "label": "Runtime", "value": "stopped" },
    { "label": "Active venues", "value": "mrkt / live" }
  ],
  "primary_links": [{ "label": "Open latest run", "href": "/runs/run_001" }],
  "width": 12
}
```

##### `venue_card`

Purpose: compact venue/operator summary card.

Payload:

```json
{
  "type": "venue_card",
  "title": "MRKT",
  "subtitle": "Live monitoring",
  "status": "degraded",
  "items": [
    { "label": "Health", "value": "ok", "status": "ok" },
    { "label": "Mode", "value": "live" },
    { "label": "Balance", "value": "0 TON" },
    { "label": "Profit", "value": "n/a", "status": "warning" }
  ],
  "alerts": [
    { "severity": "warning", "message": "Profit unavailable: no closed trades" }
  ],
  "links": [
    { "label": "Open latest run", "href": "/runs/run_001" },
    { "label": "Open venue", "href": "/venues/mrkt" }
  ],
  "width": 6
}
```

##### `kpi_grid`

Purpose: responsive KPI stat cards for operator pages.

Payload:

```json
{
  "type": "kpi_grid",
  "title": "KPI",
  "items": [
    {
      "label": "Health",
      "value": "ok",
      "unit": "",
      "status": "ok",
      "hint": "Latest tick health"
    }
  ],
  "width": 12
}
```

##### `state_grid`

Purpose: dense key/value state section.

Payload:

```json
{
  "type": "state_grid",
  "title": "Current State",
  "items": [
    { "label": "Health", "value": "ok", "status": "ok" },
    { "label": "Tick", "value": "5 / 5" },
    { "label": "Started", "value": "2026-06-05T04:34:54Z" }
  ],
  "width": 12
}
```

##### `quick_links`

Purpose: grouped internal operator links.

Payload:

```json
{
  "type": "quick_links",
  "title": "Quick Links",
  "items": [
    { "label": "Latest Run Detail", "href": "/runs/run_001" },
    { "label": "All Runs", "href": "/runs" }
  ],
  "width": 12
}
```

##### `run_table`

Purpose: operator run/event/artifact table.

Payload:

```json
{
  "type": "run_table",
  "title": "Recent Runs",
  "columns": [
    "Run",
    "Mode",
    "Venue",
    "Symbol",
    "TF",
    "Started UTC",
    "Health",
    "Event Time UTC",
    "Event",
    "Severity",
    "Events",
    "Artifact"
  ],
  "rows": [
    {
      "run_id": "run_001",
      "run_href": "/runs/run_001",
      "mode": "live",
      "venue": "mrkt",
      "symbol": "TONNFT",
      "timeframe": "1m",
      "started_utc": "2026-06-05 04:34:54",
      "health": "ok",
      "event_time_utc": "2026-06-05 04:35:36",
      "event": "venues/mrkt/lifecycle",
      "severity": "info",
      "events": "9",
      "artifact": "lifecycle.jsonl",
      "artifact_href": "/runs/run_001/artifacts/lifecycle_jsonl"
    }
  ],
  "filters": true,
  "width": 12
}
```

#### Deliverable

BeeUI exposes a product-neutral operator console block set that is sufficient for BeeCap read-only parity without adding BeeCap-specific templates or logic to BeeUI.

Expected result:

- dashboard can render system snapshot, KPI cards, venue cards and modes;
- venue pages can render operator hero, KPI grid, current state, venue state, attention and quick links;
- runs page can render a dense run/event/artifact table;
- all blocks use local Tabler-compatible markup;
- unsupported/malformed blocks degrade safely;
- adapter text is escaped;
- adapter links are internal-only.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- each new block renders through `render_layout`;
- each new block renders through fake adapter HTML route;
- unsafe text is escaped;
- external links are not rendered as active links;
- missing values render `n/a`;
- malformed payloads degrade without `500`;
- `run_table` renders required columns;
- `mode_cards` supports count/latest/latest_href/href safely;
- `chart` remains package-local and does not load external JS/CDN;
- package template integrity test covers every include from `layout_block.html`;
- no product-specific imports:
  - no `beecap_module`;
  - no `beeagent_module`;

- no external references in production templates/static:
  - no `posthog`;
  - no `scripts.tabler.io`;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
  - no remote font import;

- no `|safe` for adapter-provided fields.

Route smoke:

```text
GET /
GET /runs
GET /venues/mrkt
GET /venues/binance
GET /static/vendor/tabler/css/...
GET /static/css/beeui.css
```

#### DoD

- new operator block contract is implemented, documented and tested;
- BeeUI remains product-neutral;
- BeeCap/BeeAgent semantics stay behind product adapters;
- existing adapter-backed routes/API envelopes remain compatible;
- no product-specific logic is introduced;
- no direct product storage reads are introduced;
- no provider/broker/runtime calls are introduced;
- no external assets/scripts/tracking are introduced;
- no secrets leak into HTML/API/logs;
- malformed/unsupported blocks degrade visibly;
- docs reflect the actual supported block behavior;
- BeeCap can proceed with parity by enriching its product-side `layout[]`.

### Итерация 12.5 — Page block reference schema compatibility hotfix

**Статус:** DONE

#### Goal

Исправить BeeUI embedded startup compatibility для product-side `beeui.yml`, чтобы `pages[].blocks[]` поддерживал page-level block reference objects вида `{id: str, enabled?: bool}` наряду с существующим block placement format, без sanitizing, без мутации config и без fallback в product legacy UI.

#### Почему это нужно

После Iteration 12.4 BeeUI имеет достаточный набор operator-console blocks, но BeeCap canonical BeeUI startup может падать на schema validation до рендера adapter-backed pages:

```text
pages[0].blocks[0] contains unsupported keys: enabled, id
```

Из-за этого BeeCap root app включает legacy fallback, `/` снова отдаёт legacy templates, а BeeUI navigation/route parity не проверяется.

Это не проблема BeeCap read-model или layout renderer. Это несовместимость BeeUI schema validator с product-side page block reference format, который BeeCap использует для фильтрации/упорядочивания generated `layout[]`.

#### Change level

**runtime-risk**

Причина:

- меняется BeeUI UI schema/config validation;
- embedded app startup behavior меняется с fallback/fail на successful BeeUI initialization;
- route behavior product canonical UI зависит от успешной загрузки `beeui.yml`;
- operator-facing root routes должны перестать падать в legacy fallback.

Security-sensitive checks required for:

- config validation boundaries;
- no arbitrary keys in `pages[].blocks[]`;
- no config mutation/sanitizing;
- no secrets in logs;
- no hidden fallback paths;
- no unsafe links introduced.

#### Scope

**Включено:**

- расширить BeeUI schema validation для `pages[].blocks[]`, чтобы поддерживались block reference objects:

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - id: system_snapshot
        enabled: true
```

- сохранить существующий supported placement format, если он уже есть, например:

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - block: latest_run
        width: 3
```

- `id` должен быть safe identifier / block reference string;
- `enabled` optional, boolean, default behavior equivalent to enabled;
- неизвестные ключи в page block reference должны продолжать fail-fast;
- invalid `id` / invalid `enabled` должны fail-fast;
- не strip-ить `pages[].blocks`;
- не генерировать `.beeui_sanitized.yml`;
- не мутировать `config/beeui.yml`;
- BeeUI должен стартовать напрямую с product-side `config/beeui.yml`;
- добавить regression tests на ошибку:

```text
pages[0].blocks[0] contains unsupported keys: enabled, id
```

- обновить docs:
  - `docs/ROADMAP.md`;
  - `docs/API_CONTRACT.md` или `docs/WEB_UI.md`, где описан page/block config contract;
  - `README.ru.md`, если там перечислен поддерживаемый embedded config behavior.

**Не включено:**

- BeeCap-specific metrics/calculations;
- изменение BeeCap `read_model.py`;
- возврат sanitizing-заглушки `_page["blocks"] = []`;
- генерация sanitized config;
- legacy removal;
- auth/session/config apply/operator actions;
- новые block renderers;
- provider/broker/runtime calls;
- новые dependencies;
- изменение `pyproject.toml.version`.

#### Deliverable

BeeUI accepts product-side `beeui.yml` with page block references shaped as `{id: str, enabled?: bool}` and starts successfully in embedded mode without falling back to legacy-only UI.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Regression tests:

- valid `pages[].blocks[]` entry with `{id, enabled}` loads;
- valid `{id}` without `enabled` loads;
- valid existing `{block, width}` placement still loads;
- invalid extra key in `{id, enabled}` fails fast;
- invalid non-string `id` fails fast;
- invalid non-bool `enabled` fails fast;
- config loader does not mutate source config;
- no sanitized config file is created.

Embedded BeeCap verification after dependency update:

```text
GET /
GET /modes/live
GET /modes/paper
GET /modes/dry-run
GET /venues/binance
GET /venues/mrkt
```

Expected:

- BeeUI initialization succeeds;
- no new `BeeUI initialization failed` entry in logs;
- BeeUI root HTML contains no `/legacy` links;
- `/legacy` may remain mounted only as explicit compatibility fallback.

#### DoD

- `pages[].blocks[]` schema contract is compatible with product-side BeeUI config;
- BeeUI startup no longer fails on `{id, enabled}` block references;
- existing schema block placement contract remains backward-compatible;
- invalid block reference objects still fail fast;
- no config mutation/sanitizing is introduced;
- BeeUI remains product-neutral;
- BeeCap can continue using product-side `read_model.py` to interpret `id/enabled`;
- tests and docs reflect the actual supported config behavior.

---

## Этап 6 — Config/Auth/Actions foundation

### Итерация 13 — Auth/session/CSRF boundary for config/action routes MVP

**Статус:** DONE

#### Goal

Добавить минимальный reusable auth/session/CSRF boundary для BeeUI config/action POST routes, чтобы product-owned config apply and operator action callbacks нельзя было вызвать без явной operator authentication, role check and CSRF protection.

#### Почему это нужно

После BeeCap UI-28 BeeUI/BeeCap config/admin/action parity достигла local MVP: config preview/apply and action preview/execute идут через product adapter callbacks, с validation, backup and audit on product side.

Но POST routes без auth/session/CSRF нельзя считать customer/public-safe:

```text
POST /api/config/preview
POST /api/config/apply
POST /api/actions/preview
POST /api/actions/execute
```

Даже если product callback остаётся bounded, сам transport boundary должен быть защищён в BeeUI, потому что BeeUI владеет generic web shell, browser routes, session model and CSRF checks.

Эта итерация закрывает security gap между local/operator-only MVP and remotely exposed operator console.

#### Change level

**security-sensitive**

Причина:

- auth/session boundary;
- signed cookies/session handling;
- CSRF protection;
- POST routes;
- role-aware access;
- config mutation callbacks;
- operator action callbacks;
- secret/token handling;
- HTML/API exposure.

#### Scope

**Включено:**

- minimal BeeUI auth/session service;
- explicit auth-disabled local/dev mode;
- auth-enabled token/session mode;
- login/logout routes;
- signed session cookie;
- role model:
  - `viewer`;
  - `operator`;
  - `admin`;

- CSRF token generation and validation for browser/API POST routes;
- fail-fast startup validation when auth is enabled but required secret/token env vars are missing;
- protection for:
  - `POST /api/config/preview`;
  - `POST /api/config/apply`;
  - `POST /api/actions/preview`;
  - `POST /api/actions/execute`;

- role checks:
  - `viewer`: read-only only;
  - `operator`: action preview/execute only when product callback allows;
  - `admin`: config preview/apply and admin/config flows;

- safe unauthenticated responses:
  - HTML redirect or `401`;
  - API `401` envelope;

- safe unauthorized responses:
  - API `403` envelope;

- security headers baseline for auth/config/action pages;
- no default secrets in repository;
- no secrets in HTML/API/logs;
- tests for auth disabled/enabled modes, login/logout, CSRF, role denial, allowed flows and callback dispatch;
- docs update:
  - `docs/ROADMAP.md`;
  - `docs/SECURITY.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `README.ru.md`.

**Не включено:**

- OAuth;
- SSO;
- user database;
- password reset;
- multi-tenant auth;
- SQLAdmin;
- arbitrary YAML editor;
- direct runtime execution;
- direct broker/provider/manual order controls;
- product-specific auth logic;
- standalone SaaS auth model;
- changing BeeCap config/action semantics;
- moving product validation/audit into BeeUI.

#### Deliverable

BeeUI protects config/action POST routes with reusable auth/session/CSRF checks while keeping product authority behind adapter callbacks.

Expected behavior:

- auth disabled works only when explicitly configured as local/dev mode;
- auth enabled without required secret/token config fails fast;
- unauthenticated POST is rejected;
- missing/invalid CSRF is rejected;
- viewer cannot mutate config or execute actions;
- admin/operator roles are enforced;
- product callbacks remain the only execution boundary;
- no secrets leak to HTML/API/logs;
- BeeCap web console can move from local/operator-only toward customer-safe deployment after adopting this BeeUI version.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- auth disabled mode must be explicit;
- auth enabled without session secret fails fast;
- auth enabled without operator/admin token fails fast;
- login success;
- login failure;
- logout clears session;
- unauthenticated POST rejected;
- missing CSRF rejected;
- invalid CSRF rejected;
- valid CSRF accepted;
- viewer denied config apply;
- viewer denied action execute;
- admin allowed config preview/apply if adapter allows;
- operator allowed action preview/execute if adapter allows;
- adapter denial still returns explicit denied envelope;
- no product callback called when auth/CSRF fails;
- no secrets in HTML/API/logs;
- no provider/broker/runtime calls from BeeUI.

#### DoD

- BeeUI owns reusable auth/session/CSRF shell;
- config/action POST routes are protected before product callbacks are called;
- auth-disabled local mode is explicit and documented;
- auth-enabled mode fails fast without required secrets;
- role checks work;
- CSRF checks work;
- product callbacks remain source of business authority;
- no product-specific logic is introduced into BeeUI;
- docs clearly distinguish local/operator-only mode from customer/public-safe mode.

### Итерация 13.1 — Dashboard layout primitives, URL tabs and locale seed

**Статус:** DONE

#### Goal

Добавить минимальные reusable BeeUI primitives для customer-friendly product dashboards: декларативные размеры блоков, URL-driven Tabler tabs, locale/i18n seed и более чистый generic dashboard fallback без raw JSON как primary UX.

#### Почему это нужно

После Iteration 12.x BeeUI уже умеет рендерить adapter-backed `layout[]` и operator-console blocks, а после Iteration 13 имеет auth/session/CSRF boundary. Но для BeeAgent UI-5 и будущих BeeCap/BeeScan dashboards не хватает небольшого reusable presentation foundation:

- продукты хотят управлять размерами blocks без ручного копирования Tabler classes;
- run switcher и similar navigation нужны как generic Tabler URL tabs, а не product-owned HTML;
- pages должны получать resolved locale, чтобы продукты могли рендерить RU/EN labels без собственной routing glue;
- generic dashboard fallback не должен выглядеть как debug/raw JSON page.

Эта итерация закрывает reusable BeeUI UI primitives перед BeeAgent integration/polish, не добавляя product-specific semantics.

Главное правило сохраняется:

```text
BeeUI renders.
Product decides.
```

#### Change level

**runtime-risk**

Причина:

- меняется schema/block placement contract;
- меняется adapter-backed layout block normalization/rendering;
- меняется template/context rendering behavior;
- добавляется locale resolution from query params;
- меняется operator-facing generic dashboard fallback;
- docs/tests must reflect updated UI contract.

Security-sensitive checks required for:

- HTML escaping;
- safe internal links in tabs;
- invalid schema values;
- malformed adapter payload degradation;
- no external CDN/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation from GET routes.

#### Scope

**Включено:**

- добавить reusable block layout sizing contract for schema/demo page placements:
  - existing `width: 1..12` remains supported;
  - optional `span: 1..12`;
  - optional `size: S|M|L|XL`;
  - invalid values fail fast;
  - conflicting layout keys in schema placements fail fast;
  - existing configs remain backward-compatible;

- добавить layout sizing support for adapter-backed `layout[]` blocks:
  - existing `width` remains supported;
  - optional `span`;
  - optional `size`;
  - invalid/malformed adapter values degrade safely to `col-12`, not `500`;

- supported size mapping:

```text
S  -> span 4  -> col-12 col-md-6 col-lg-4
M  -> span 6  -> col-12 col-lg-6
L  -> span 8  -> col-12 col-lg-8
XL -> span 12 -> col-12
```

- centralize width/span/size mapping in a product-neutral helper so templates do not duplicate mapping logic;

- add reusable Tabler-compatible URL tabs primitive/helper:
  - `ul.nav.nav-tabs.card-header-tabs`;
  - `li.nav-item`;
  - `a.nav-link`;
  - active item support;
  - normal `href` links;
  - optional overflow dropdown for older items;
  - safe internal links only;
  - no JS-only tab panes required;

- add locale/i18n seed to UI schema:

```yaml
locale:
  default: en
  available:
    - en
    - ru
```

- locale behavior:
  - default locale comes from UI config;
  - query param `lang` can override locale only if allowlisted;
  - invalid `lang` falls back to default;
  - resolved locale is exposed to templates/context;
  - no persistence;
  - no user settings;
  - no database;
  - BeeUI does not translate product-specific strings;

- generic dashboard cleanup:
  - when structured dashboard fields exist, render summary cards/sections first;
  - raw/debug technical payload is shown only inside clearly separated/collapsible `Technical details`;
  - API responses remain unchanged;
  - fallback remains useful if adapter does not provide `layout[]`;

- docs update:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md` if block/layout contract is documented there;
  - `README.ru.md`.

**Не включено:**

- BeeAgent-specific ROP labels;
- BeeCap-specific metrics/calculations;
- MRKT/Binance/ROP/capability-specific logic;
- full i18n translation catalog;
- persisted user language preferences;
- auth changes;
- config apply;
- operator actions;
- standalone service;
- visual/no-code builder;
- drag-and-drop layout;
- charts/ApexCharts;
- external CDN/assets/scripts;
- new dependencies unless strictly justified.

#### Deliverable

BeeUI provides product-neutral dashboard layout primitives that products can reuse for polished dashboards without copying Tabler templates or hardcoding layout behavior.

Expected behavior:

- schema/demo pages can use `width`, `span` or `size` for block placement;
- adapter-backed `layout[]` blocks can use `width`, `span` or `size`;
- invalid schema layout values fail fast;
- malformed adapter layout values degrade visibly without crashing;
- URL-driven Tabler nav-tabs can render active links and optional overflow dropdown;
- resolved locale is available in request/template context;
- `?lang=ru` works when `ru` is allowlisted;
- invalid `lang` falls back safely;
- generic dashboard fallback no longer shows raw JSON as the primary UX;
- raw technical payload, when present, is separated into `Technical details`.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- valid `size: S|M|L|XL` renders expected responsive classes;
- valid `span: 4|6|8|12` renders expected responsive classes;
- existing `width` placements remain backward-compatible;
- invalid schema `size` fails fast;
- invalid schema `span` fails fast;
- conflicting schema layout keys fail fast;
- malformed adapter-backed `layout[]` size/span/width degrades to safe full-width rendering;
- URL-driven tabs render Tabler nav-tabs markup;
- active tab receives `.active`;
- overflow dropdown renders when overflow items are provided;
- unsafe/external tab links are not rendered as active links;
- locale default resolves from config;
- `?lang=ru` resolves to `ru` when allowlisted;
- invalid `?lang=bad` falls back to default;
- resolved locale is available in template context;
- generic dashboard primary HTML does not expose raw JSON/debug details as the main visible section;
- technical details are separated/collapsible if raw payload is still rendered;
- no product-specific imports:
  - no `beecap_module`;
  - no `beeagent_module`;
- no external references:
  - no `posthog`;
  - no `scripts.tabler.io`;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
- no unsafe `|safe` for adapter/config-provided fields;
- no mutation from GET routes;
- no secrets in HTML/API/logs.

#### DoD

- layout size primitives are implemented, documented and tested;
- existing `width` config remains backward-compatible;
- schema invalid values fail fast;
- adapter malformed values degrade safely;
- URL tab primitive is product-neutral and safe-link aware;
- locale seed is config-driven and query-param override is allowlisted;
- BeeUI does not translate product-specific strings;
- generic dashboard primary UX is customer-friendly, not raw/debug-first;
- API envelopes remain backward-compatible;
- no product-specific logic is introduced;
- no direct product storage reads are introduced;
- no provider/broker/runtime calls are introduced;
- no external CDN/scripts/tracking are introduced;
- docs reflect the updated layout/tabs/locale contract.

### Итерация 13.2 — Generic adapter pages and configurable Tabler primitives

**Статус:** DONE

#### Goal

Добавить в BeeUI generic adapter-backed custom pages и configurable Tabler-compatible `tabs` / `accordion` primitives, чтобы BeeAgent/BeeCap могли строить product dashboards через `beeui.yml` + adapter read-model/layout без product-owned Jinja templates.

#### Почему это нужно

После Iteration 13.1 BeeUI уже имеет sizing primitives, URL tabs seed and locale seed, но BeeAgent UI-5 показала архитектурный gap:

```text
BeeAgent начал создавать собственные Jinja templates/manual HTML dashboard.
```

Это ломает целевое правило:

```text
BeeUI renders.
Product decides.
```

BeeUI должен владеть shell, templates, tabs, accordion, dashboard layout, artifact viewer and generic pages. Product должен отдавать только adapter/read-model/layout/artifact allowlist/domain data.

Дополнительно Tabler examples показывают несколько safe визуальных вариантов `tabs` and `accordion`, но BeeUI не должен копировать Tabler preview pages целиком и не должен тянуть demo scripts, PostHog, remote fonts, sponsor blocks or external assets.

#### Change level

**runtime-risk**

Причина:

- меняется UI schema/config contract;
- добавляются configurable component variants;
- добавляются generic adapter-backed custom routes;
- расширяется optional adapter page read-model boundary;
- меняется HTML rendering для dashboard technical details;
- operator-facing GET routes влияют на dashboard UX.

Security-sensitive checks required for:

- HTML escaping;
- safe internal links in tabs;
- deterministic/safe accordion ids;
- route collision validation;
- invalid schema fail-fast;
- malformed adapter payload degradation;
- no external CDN/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation from GET routes.

#### Scope

**Включено:**

- добавить configurable URL tabs primitive v1:
  - `ul.nav.nav-tabs.card-header-tabs`;
  - URL-driven links only;
  - active state from allowlisted query param;
  - safe internal links only;
  - optional disabled items;
  - optional dropdown/overflow items;
  - no JS-only hidden panes;
  - no arbitrary HTML labels;
  - no unsafe `|safe`;

- поддержать safe tab variants by canonical names:

```text
default
reverse
fill
icons
fill_icons
dropdown
```

- если реализуются numeric aliases, они должны нормализоваться в canonical names:

```text
1 -> default
2 -> reverse
3 -> icons
4 -> dropdown
5 -> fill
6 -> fill_icons
```

Canonical docs/config examples must use names, not numbers.

- добавить configurable accordion/collapsible primitive v1:
  - deterministic ids;
  - collapsed/open initial state;
  - single-open mode through `data-bs-parent`;
  - multi-open mode if simple and safe;
  - safe escaped titles/body;
  - no arbitrary HTML body from adapter/config;
  - no full Tabler preview copy;

- поддержать accordion variants by canonical names:

```text
default
flush
tabs
inverted
inverted_plus
icons
```

- если реализуются numeric aliases, они должны нормализоваться в canonical names:

```text
1 -> default
2 -> flush
3 -> tabs
4 -> inverted
5 -> inverted_plus
6 -> icons
```

Canonical docs/config examples must use names, not numbers.

- добавить optional component config defaults, for example:

```yaml
components:
  tabs:
    variant: default
  accordion:
    variant: default
```

- добавить optional page-level tabs config, for example:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title: ROP Dashboard
    subtitle: ROP operator dashboard
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

- invalid component/page tab config fails fast;

- missing component config uses documented safe defaults;

- unknown component variant fails fast;

- unsafe/external tab links fail fast for config and degrade for adapter-provided payloads;

- replace generic dashboard fallback `Technical details` from raw `<details>` to BeeUI accordion/collapsible primitive;

- confirm or harden adapter-backed `layout[]` sizing:
  - `width: 1..12`;
  - `span: 1..12`;
  - `size: S|M|L|XL`;
  - invalid schema sizing fails fast;
  - malformed adapter sizing degrades to `col-12`;

- добавить generic adapter-backed custom pages v0:
  - product declares page in `beeui.yml`;
  - BeeUI registers safe GET route;
  - route must not conflict with reserved routes;
  - BeeUI calls optional adapter method, for example:

```python
get_page(page_id: str, query: Mapping[str, str])
```

- if method unavailable, render explicit unavailable/degraded state;

- default base adapter returns unavailable;

- returned `layout[]` renders through existing generic layout renderer;

- BeeUI must not know ROP/MRKT/Binance/Bitrix semantics;

- Artifact viewer remains BeeUI-owned:
  - HTML artifact browser remains generic BeeUI route;
  - API artifact route remains BeeUI-owned JSON envelope;
  - product adapter owns allowlist/content.

- update docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/INTEGRATION.md`;
  - `README.ru.md` if user-facing config examples changed.

**Не включено:**

- BeeAgent-specific ROP labels;
- BeeCap-specific metrics/calculations;
- MRKT/Binance/ROP/Bitrix semantics;
- full i18n catalog;
- persisted user preferences;
- auth/session/CSRF changes;
- config apply;
- operator actions;
- POST routes;
- no-code builder;
- drag-and-drop;
- charts/ApexCharts;
- arbitrary HTML/JS blocks;
- full Tabler demo page copy;
- PostHog/demo scripts/sponsor blocks/remote fonts/external CDN;
- new dependencies unless strictly justified;
- `pyproject.toml.version` change.

#### Deliverable

BeeUI can render custom product pages such as `/rop` through `beeui.yml` + adapter read-model/layout, with reusable configurable Tabler-compatible tabs and accordion primitives, without any product-owned HTML templates.

Expected behavior:

```text
config/beeui.yml declares /rop
BeeAgent adapter returns page read-model/layout
BeeUI registers /rop
BeeUI renders shell/page/tabs/accordion/cards/tables/artifacts
BeeAgent owns only domain data and artifact allowlist
```

#### Checks

- `uv run pytest -q`;
- `uv run pytest -q -W error::UserWarning`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- tabs primitive renders `nav nav-tabs card-header-tabs`;
- each supported tab variant renders expected safe classes;
- invalid tabs variant fails fast in config;
- numeric aliases, if supported, normalize to canonical names;
- active tab is selected only from allowlisted `active_param`;
- invalid active tab falls back safely;
- unsafe/external tab href is rejected or rendered inert;
- accordion primitive renders local Tabler/Bootstrap markup;
- each supported accordion variant renders expected safe classes;
- invalid accordion variant fails fast;
- deterministic accordion ids are generated safely;
- `Technical details` uses accordion, not raw `<details>`;
- schema block `width/span/size` works;
- invalid schema sizing fails fast;
- malformed adapter sizing degrades to `col-12`;
- configured custom page `/rop` renders through adapter page method;
- unavailable adapter page renders degraded/empty state;
- route collision/reserved paths rejected;
- GET custom pages do not mutate storage/source config;
- no product-specific strings/imports in BeeUI generic renderer;
- no external references:
  - `posthog`;
  - `scripts.tabler.io`;
  - `preview.tabler.io`;
  - `docs.tabler.io`;
  - `cdn.jsdelivr`;
  - remote font imports;

- no unsafe `|safe` for adapter/config-provided fields;
- no secrets in HTML/API/logs.

#### DoD

- configurable tabs primitive is implemented, documented and tested;
- configurable accordion primitive is implemented, documented and tested;
- technical details fallback uses BeeUI accordion;
- custom adapter-backed pages work through BeeUI generic page renderer;
- adapter page method is optional and backward-compatible;
- existing ProductUiAdapter implementations do not break;
- route collisions are rejected fail-fast;
- invalid config fails fast;
- malformed adapter payload degrades visibly;
- BeeUI remains product-neutral;
- Artifact viewer remains BeeUI-owned;
- no external assets/scripts/tracking are introduced;
- no GET route mutates product storage/config/artifacts;
- docs reflect actual config/component/page contracts.

### Итерация 13.3 — Tabler attached tabs and accordion visual parity hardening

**Статус:** DONE

#### Goal

Исправить BeeUI renderer/CSS для Tabler-compatible page tabs and accordion primitives, чтобы adapter-backed custom pages, включая BeeAgent `/rop`, рендерились без product-owned HTML templates: tabs должны быть attached к общей card/body, а `Technical details` должен выглядеть и работать как стандартный Tabler accordion с видимым chevron.

#### Почему это нужно

После Iteration 13.2 BeeUI умеет регистрировать generic adapter-backed custom pages и configurable `tabs` / `accordion` primitives. Но фактический BeeAgent UI-5 smoke показал visual/renderer gap:

- `/rop` tabs рендерятся как отдельная card перед page blocks;
- между active tab `Overview` и первым block `Run Overview` появляется внешний зазор;
- tabs визуально не attached к card body, как в Tabler examples;
- `Technical details` на dashboard выглядит как большая статичная строка;
- chevron/accordion affordance не виден;
- пользователь не понимает, что block раскрываемый.

Это нельзя исправлять в BeeAgent через product-owned Jinja templates. BeeAgent должен отдавать только config/read-model/layout. BeeUI должен владеть shell, tabs, accordion, page renderer, CSS and Tabler-compatible primitives.

Главное правило сохраняется:

```text
BeeUI renders.
Product decides.
```

#### Change level

**runtime-risk**

Причина:

- меняется BeeUI page renderer HTML structure;
- меняется rendering behavior для configured page tabs;
- меняется accordion primitive markup/CSS;
- меняется operator-facing UI для adapter-backed product pages;
- текущие BeeAgent UI-5 routes зависят от BeeUI renderer output.

Security-sensitive checks required for:

- HTML escaping;
- safe internal links in tabs;
- deterministic/safe accordion ids;
- no external CDN/scripts/tracking;
- no product-specific imports;
- no unsafe Jinja `|safe`;
- no mutation from GET routes;
- no secrets in HTML/API/logs.

#### Scope

**Включено:**

- исправить page-level tabs placement в BeeUI renderer:
  - если page has configured tabs, tabs и page blocks должны рендериться внутри одной card;
  - использовать Tabler-compatible structure:

```html
<div class="card beeui-page-tabs-card">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs">
      ...
    </ul>
  </div>
  <div class="card-body">
    <section aria-label="Page blocks">...</section>
  </div>
</div>
```

- убрать standalone tabs card pattern перед page blocks:

```html
<div class="card mb-3">...</div>
<section aria-label="Page blocks">...</section>
```

- page title/subtitle должны оставаться выше tabs card;

- tabs не должны перекрывать subtitle;

- между tabs header и page blocks не должно быть внешнего margin-gap;

- нормальный `card-body` padding допустим;

- между самими blocks внутри body остаётся стандартный Tabler grid gap;

- active tab and disabled tab behavior должны сохраниться;

- `?tab=overview|queue|sources|attachments|evidence` должен работать как раньше;

- invalid tab fallback должен работать как раньше;

- route prefix support должен сохраниться;

- исправить `Technical details` accordion rendering:
  - использовать стандартный Tabler-compatible accordion markup;
  - `Technical details` должен быть `button.accordion-button collapsed`;
  - chevron должен быть видимым справа через `.accordion-button-toggle`;
  - использовать local inline SVG chevron или existing BeeUI icon primitive;
  - не использовать external icon/CDN;
  - не использовать `accordion-tabs` для technical details;
  - размер шрифта должен соответствовать accordion button/card text, не page-title;
  - сохранить accessibility attributes:
    - `type="button"`;
    - `data-bs-toggle="collapse"`;
    - `data-bs-target`;
    - `aria-expanded`;
    - `aria-controls`;

- добавить/обновить CSS только в BeeUI static layer, если одного Tabler markup недостаточно;

- добавить regression tests for HTML structure and safety;

- обновить docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`, если там описан tabs/accordion/page contract.

**Не включено:**

- BeeAgent-owned Jinja templates;
- `src/beeagent_module/interfaces/ui/templates`;
- package-data for BeeAgent UI templates;
- `Jinja2Templates` inside BeeAgent UI integration;
- `_build_rop_html`;
- `_build_modules_html`;
- `_build_artifact_viewer_html`;
- `_build_shell_context`;
- `_render_page`;
- BeeAgent/BeeCap/MRKT/Binance/ROP-specific logic inside BeeUI;
- new no-code builder;
- auth/session/CSRF changes;
- config apply;
- operator actions;
- POST routes;
- arbitrary HTML/JS;
- new dependencies;
- external Tabler preview assets/scripts;
- `pyproject.toml.version` change;
- `uv.lock` change unless dependencies are explicitly changed.

#### Deliverable

BeeUI renders configured page tabs and technical details accordion with Tabler-compatible visual structure:

```text
/rop
  page title/subtitle
  single attached tabs card
    card-header: nav-tabs
    card-body: page blocks
```

```text
/
  Technical details
    standard accordion button
    visible chevron
    collapsed/expandable affordance
```

BeeAgent can keep using BeeUI through `create_beeui_app(...)` and adapter-provided read-model/layout without product-owned templates.

#### Checks

- `uv run pytest -q`;
- `uv run pytest -q -W error::UserWarning`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- configured page with tabs renders `beeui-page-tabs-card`;
- tabs and `section aria-label="Page blocks"` are inside the same card;
- no standalone `<div class="card mb-3">` tabs card before page blocks;
- page title renders before tabs;
- page subtitle renders before tabs;
- first page block renders inside `.beeui-page-tabs-card .card-body`;
- active tab still receives `.active`;
- disabled tab remains disabled/inert;
- invalid tab query falls back safely;
- `route_prefix` tab hrefs still work;
- `Technical details` renders inside `.accordion`;
- `Technical details` uses `.accordion-button.collapsed`;
- `Technical details` contains `.accordion-button-toggle`;
- `Technical details` does not use `accordion-tabs`;
- accordion ids are deterministic and safe;
- unsafe text remains escaped;
- no unsafe `|safe`;
- no external references:
  - `posthog`;
  - `scripts.tabler.io`;
  - `preview.tabler.io`;
  - `docs.tabler.io`;
  - `cdn.jsdelivr`;
  - remote font imports;

- no product-specific imports:
  - `beecap_module`;
  - `beeagent_module`;

- no GET route mutates storage/config/artifacts.

BeeAgent embedded smoke after BeeUI update:

```text
GET /
GET /rop
GET /rop?tab=overview
GET /rop?tab=queue
GET /rop?tab=sources
GET /rop?tab=attachments
GET /rop?tab=evidence
GET /modules
```

Expected:

- `/rop` tabs visually attached to page blocks card;
- no external gap between tabs header and first block container;
- normal gap remains between blocks inside card body;
- `Technical details` has visible chevron and normal accordion font size;
- BeeAgent still has no product-owned HTML templates.

#### DoD

- page tabs attached-card renderer is implemented, documented and tested;
- `Technical details` accordion uses Tabler-compatible markup with visible chevron;
- BeeUI remains product-neutral;
- BeeAgent keeps only config/read-model/layout/artifact allowlist;
- no BeeAgent HTML templates are introduced;
- no external assets/scripts/tracking are introduced;
- no unsafe Jinja `|safe` is introduced;
- no secrets leak into HTML/API/logs;
- no GET route mutates product storage/config/artifacts;
- docs reflect actual tabs/accordion/page rendering behavior;
- BeeAgent UI-5 can proceed after dependency update and smoke verification.

### Итерация 13.4 — Generic layout groups, KPI grid columns, and page spacing normalization

**Status:** DONE

#### Goal

Extend BeeUI’s product-neutral layout renderer so adapter-backed pages can express both flat Tabler dashboard rows and simple nested layout groups without product-owned Jinja templates or product-specific CSS.

This iteration follows It13.3.

It13.3 fixed Tabler visual parity for attached page tabs and accordion rendering. After reviewing Tabler dashboard layout patterns, one additional generic layout capability is needed before BeeAgent UI-5 can be closed cleanly:

- consistent page-body spacing across dashboard/custom/modules/runs render paths;
- optional `kpi_grid.columns` for compact KPI grids;
- bounded generic layout groups for Tabler-style nested column compositions.

#### Context

Tabler dashboard layouts are not always flat lists of cards.

Some rows are simple flat compositions:

```text
M + S + S
6 + 3 + 3 = 12
```

```text
S + S + S + S
3 + 3 + 3 + 3 = 12
```

Other rows are nested compositions:

```text
OUTER ROW:
  LEFT GROUP 6:
    - Storage card       12 inside group
    - Activity feed card 12 inside group

  RIGHT BLOCK 6:
    - Development activity
```

BeeUI currently has generic blocks and outer `width/span/size` handling, but it needs a small product-neutral way to express grouped blocks inside a column.

This must stay generic:

- BeeUI renders layout primitives;
- product adapters decide which domain blocks appear where;
- BeeUI must not know ROP, BeeAgent, BeeCap, MRKT, Binance, Bitrix or other product semantics;
- BeeAgent must not add product-owned Jinja templates to solve layout.

#### Scope

Included:

- Audit current BeeUI implementation before making changes.
- Normalize page-body spacing across relevant render paths:
  - adapter-backed dashboard `/`;
  - custom adapter pages such as `/rop`;
  - modules/custom page `/modules`;
  - runs page `/runs`;
  - pages with tabs;
  - pages without tabs.

- Ensure all relevant pages use a Tabler-compatible structure equivalent to:

```html
<div class="page-header d-print-none">
  <div class="container-xl">...</div>
</div>

<div class="page-body">
  <div class="container-xl">...</div>
</div>
```

- Add optional product-neutral `kpi_grid.columns` support.
- Supported `kpi_grid.columns` values:

```text
1 -> col-12
2 -> col-12 col-sm-6
3 -> col-12 col-sm-6 col-lg-4
4 -> col-12 col-sm-6 col-lg-3
```

- Default `kpi_grid.columns` remains `4`.
- Invalid adapter-provided `columns` values degrade safely to default, not `500`.
- Invalid schema/config `columns` values fail fast if schema-backed blocks accept the field.
- Add generic bounded layout group support.
- Layout group v1 supports:
  - `type: group`;
  - `width` / `span` / existing size handling at the outer level;
  - `direction: vertical` initially;
  - `children` containing normal BeeUI layout block items;
  - Tabler-compatible nested `row row-cards`;
  - children rendered with the existing block renderer.

- The layout group must be product-neutral and must not hardcode domain labels such as `Run Overview`, `Key Metrics`, `ROP`, `BeeAgent`, `BeeCap`, `MRKT`, `Binance`, or `Bitrix`.
- Add regression tests for:
  - flat `6 + 3 + 3` layout;
  - flat `3 + 3 + 3 + 3` layout;
  - nested `6 group + 6 block` layout;
  - KPI grid columns;
  - page spacing;
  - tabs still attached to page blocks;
  - safe degradation for malformed adapter payloads;
  - escaping and no unsafe external refs.

Excluded:

- Full no-code layout builder.
- Drag-and-drop layout editing.
- Arbitrary HTML/JS blocks.
- Unlimited recursive containers.
- Product-specific layout logic.
- BeeAgent/BeeCap-owned templates.
- BeeAgent/BeeCap CSS fixes for BeeUI layout.
- Auth/session/CSRF changes.
- Config apply.
- Operator actions.
- POST routes.
- Charts/ApexCharts expansion beyond existing policy.
- External Tabler preview assets/scripts.
- New dependencies.
- `pyproject.toml.version` change.
- `uv.lock` change unless dependencies unexpectedly change, which is not expected.

#### Proposed layout contract

Flat row example:

```json
[
  {
    "type": "summary",
    "title": "Welcome",
    "width": 6
  },
  {
    "type": "metric",
    "title": "Total Users",
    "width": 3
  },
  {
    "type": "metric",
    "title": "Active Users",
    "width": 3
  }
]
```

KPI grid example:

```json
{
  "type": "kpi_grid",
  "title": "Key Metrics",
  "width": 4,
  "columns": 2,
  "items": [
    { "label": "Total", "value": "42" },
    { "label": "Open", "value": "8" },
    { "label": "Closed", "value": "34" },
    { "label": "Warnings", "value": "2" },
    { "label": "Errors", "value": "0" },
    { "label": "Reviews", "value": "5" }
  ]
}
```

Nested layout group example:

```json
[
  {
    "id": "left_stack",
    "type": "group",
    "width": 6,
    "direction": "vertical",
    "children": [
      {
        "type": "storage",
        "title": "Storage",
        "width": 12
      },
      {
        "type": "activity_feed",
        "title": "Activity Feed",
        "width": 12
      }
    ]
  },
  {
    "type": "development_activity",
    "title": "Development activity",
    "width": 6
  }
]
```

Expected rendered structure:

```html
<div class="row row-deck row-cards">
  <div class="col-lg-6">
    <div class="row row-cards">
      <div class="col-12">...</div>
      <div class="col-12">...</div>
    </div>
  </div>

  <div class="col-lg-6">...</div>
</div>
```

#### Acceptance Criteria

- Existing tests remain green.
- `/`, `/rop`, `/modules`, `/runs` return `200` in relevant tests/smoke checks.
- Pages with tabs keep tabs and page blocks inside one attached Tabler card.
- Pages without tabs keep normal page block rendering.
- Page content spacing after subtitle/header is consistent across dashboard/custom/modules/runs render paths.
- `kpi_grid.columns=1` renders KPI items with `col-12`.
- `kpi_grid.columns=2` renders KPI items with `col-12 col-sm-6`.
- `kpi_grid.columns=3` renders KPI items with `col-12 col-sm-6 col-lg-4`.
- `kpi_grid.columns=4` renders KPI items with `col-12 col-sm-6 col-lg-3`.
- Missing `kpi_grid.columns` preserves current/default behavior.
- Invalid adapter-provided `kpi_grid.columns` degrades safely to default.
- Invalid schema/config-backed `columns` fails fast if schema supports the field.
- Generic `group` layout renders a nested `row row-cards` inside the parent column.
- Group children are rendered through existing BeeUI block rendering.
- Malformed adapter-provided group payload degrades visibly and safely, not `500`.
- Unsafe labels/values remain HTML-escaped.
- No external CDN/scripts/tracking are introduced.
- No product-specific imports or domain logic are introduced in `src/beeui_module`.
- No unsafe Jinja `|safe` is introduced.
- No GET route mutates storage/config/artifacts.
- `pyproject.toml.version` remains unchanged.
- `uv.lock` remains unchanged unless dependencies are explicitly changed, which is not expected.

#### Required checks

Automated:

```bash
uv run pytest -q
uv run pytest -q -W error::UserWarning
```

Targeted:

```bash
uv run pytest -q tests/test_pages.py
uv run pytest -q tests/test_product_console.py
uv run pytest -q tests/test_blocks.py
uv run pytest -q tests/test_config.py
```

Smoke:

```bash
./start.sh doctor
./start.sh routes
```

Static/security checks:

```bash
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "ROP|BeeAgent|BeeCap|MRKT|Binance|Bitrix|Run Overview|Key Metrics" src/beeui_module || true
git diff -- pyproject.toml uv.lock
```

#### Definition of Done

- Current implementation was audited first.
- No already implemented behavior was duplicated.
- Generic layout group v1 is implemented or confirmed unnecessary by code evidence.
- KPI grid columns are implemented or confirmed already present.
- Page-body spacing is normalized or confirmed already centralized.
- Tests cover flat layouts, nested groups, KPI columns, spacing, escaping, and safety behavior.
- Docs reflect the actual supported block/layout contract.
- Required checks are completed.
- No product-specific BeeUI code is introduced.
- No new dependencies are added.
- Version is not changed.
- `uv.lock` is not changed.
- PR is ready for review.

### Итерация 13.5 — Product console route metadata and navigation compatibility

**Status:** DONE

#### Goal

Fix BeeUI config validation and custom page registration so product-side `beeui.yml` can describe metadata, titles, subtitles, tabs, navigation and block/layout references for existing product console routes such as `/venues/mrkt` and `/venues/binance`, without BeeUI trying to register those paths as generic custom routes.

This iteration keeps canonical product routes intact:

```text
/venues/mrkt
/venues/binance
/modes/dry-run
/modes/paper
/modes/live
```

BeeUI must distinguish:

```text
safe internal path
  used for navigation links, tabs, links and page metadata

custom route path
  used only when BeeUI registers a new adapter-backed custom page route
```

#### Why this is needed

After Iteration 13.4, BeeUI supports product-neutral layout groups, KPI grid columns and normalized page spacing. BeeCap/BeeAgent can now describe richer operator pages through `beeui.yml`.

However, current reserved path validation is too broad. It treats paths such as:

```yaml
pages:
  - id: mrkt_dashboard
    path: /venues/mrkt

navigation:
  - title: Venues
    children:
      - title: MRKT
        path: /venues/mrkt
```

as invalid because `/venues/*` is reserved.

That is correct only for generic custom route registration. It is not correct for:

- page metadata for an existing product console route;
- sidebar navigation links to an existing internal route;
- page tabs/hrefs/links pointing to existing internal routes.

This blocks BeeCap canonical route parity and encourages wrong workarounds such as `/mrkt`, `/binance` or product-owned templates.

Main rule remains:

```text
BeeUI renders.
Product decides.
```

#### Context

Two different concepts were mixed:

| Concept                                    | Purpose                                                                  | May use `/venues/mrkt` |
| ------------------------------------------ | ------------------------------------------------------------------------ | ---------------------: |
| `pages[]` as generic custom page route     | BeeUI registers a new route and calls `adapter.get_page(page_id, query)` |                     No |
| `pages[]` as product console page metadata | BeeUI stores title/subtitle/tabs/block refs for an existing route        |                    Yes |
| `navigation[].path`                        | Sidebar/internal link to an existing internal route                      |                    Yes |
| `tabs[].href` / layout links               | Safe internal links                                                      |                    Yes |
| Custom route registration                  | Only non-reserved paths such as `/rop`, `/reports`, `/modules`           |     No for `/venues/*` |

#### Scope

**Included**

- Split path validation into two product-neutral concepts:
  - safe internal path validation;
  - custom route path validation.

- Safe internal path validation must allow internal product console paths such as:

```text
/
/runs
/runs/<safe-run-id>
/venues/mrkt
/venues/binance
/modes/dry-run
/modes/paper
/modes/live
/rop
/modules
```

- Safe internal path validation must still reject:
  - empty paths;
  - paths without leading `/`;
  - protocol-relative paths `//...`;
  - external URLs;
  - `?` / `#` in raw path fields where not expected;
  - backslashes;
  - control characters;
  - traversal segments `.` / `..`;
  - unsafe path segments.

- Custom route path validation must keep BeeUI/system/product-console owned routes reserved.

Reserved exact paths for custom route registration:

```text
/
/api
/auth
/static
/components
/health
/login
/logout
/runs
/venues
```

Reserved prefixes for custom route registration:

```text
/api/
/auth/
/static/
/components/
/runs/
/venues/
```

- `/venues/*` must be allowed as page metadata/navigation, but must not be registered as a generic custom page route.

- `/runs/*` must not be registered as a generic custom page route because run detail routes are product console routes.

- Non-reserved custom pages such as `/rop`, `/modules`, `/reports`, `/settings-lite` must continue to register as adapter-backed custom pages.

- Preserve duplicate path detection for `pages[]`.

- Preserve route collision protection for actual custom pages.

- Preserve fail-fast validation for unsafe paths.

- Preserve route prefix and embedded mount compatibility.

- Update tests for:
  - safe internal paths;
  - reserved custom route paths;
  - navigation links to `/venues/mrkt`;
  - page metadata for `/venues/mrkt`;
  - custom route registration skip for `/venues/*`;
  - custom route registration still works for `/rop`;
  - unsafe paths still fail fast;
  - no canonical route renaming.

- Update docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/API_CONTRACT.md` if route/config contract wording is affected;
  - `README.ru.md` if user-facing integration examples mention reserved paths.

**Excluded**

- Do not rename BeeCap canonical routes.
- Do not change `/venues/mrkt` to `/mrkt`, `/venue-mrkt`, `/binance`, etc.
- Do not remove venue page configs from product-side `beeui.yml`.
- Do not add product-specific MRKT/Binance/BeeCap logic to BeeUI core.
- Do not touch Binance trading/runtime/risk logic.
- Do not add auth/session/CSRF changes.
- Do not add config apply/operator actions.
- Do not add POST routes.
- Do not add no-code builder behavior.
- Do not introduce external CDN/assets/scripts.
- Do not add dependencies.
- Do not change `pyproject.toml.version`.

#### Required behavior

`navigation[].path` must be validated as a safe internal path, not as a custom route registration target.

Valid:

```yaml
navigation:
  - title: Venues
    children:
      - title: MRKT
        path: /venues/mrkt
      - title: Binance
        path: /venues/binance
```

Valid:

```yaml
pages:
  - id: mrkt_dashboard
    path: /venues/mrkt
    title: MRKT
    subtitle: MRKT venue dashboard metadata
    blocks:
      - id: system_snapshot
        enabled: true
```

This page config must be loaded and preserved as metadata, but BeeUI must not register a custom route for `/venues/mrkt`.

Valid custom page:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title: ROP Dashboard
    subtitle: ROP operator dashboard
    blocks: []
```

BeeUI may register `/rop` as an adapter-backed custom page and call:

```python
adapter.get_page("rop_dashboard", query)
```

Invalid custom route registration:

```yaml
pages:
  - id: bad_api_shadow
    path: /api/debug
```

This must not register a custom route.

#### Deliverable

BeeUI can load product-side `beeui.yml` where `pages[]` and `navigation[]` reference existing product console routes such as `/venues/mrkt` and `/venues/binance`.

Expected outcome:

- config validation succeeds;
- sidebar can link to `/venues/mrkt` and `/venues/binance`;
- product console route `/venues/{venue_id}` remains canonical;
- BeeUI does not register `/venues/mrkt` as a generic custom page;
- generic custom pages still work for non-reserved paths such as `/rop`;
- unsafe paths and real route collisions still fail fast.

#### Acceptance Criteria

- `config/beeui.yml` with `pages[].path: /venues/mrkt` validates.
- `navigation[].path: /venues/mrkt` validates when it points to declared metadata or known internal product console route.
- `/venues/mrkt` is not registered as a custom page route.
- Existing `GET /venues/{venue_id}` product console route continues to serve `/venues/mrkt`.
- `/venues/binance` behaves the same way.
- `/rop` or another non-reserved custom page still registers as adapter-backed custom page.
- `/api/*`, `/auth/*`, `/static/*`, `/components/*`, `/runs/*`, `/venues/*` cannot be registered as generic custom routes.
- Unsafe paths with `..`, `\`, `//`, control characters or external schemes are rejected.
- Navigation paths do not use the custom-route reserved check.
- Page metadata paths do not use the custom-route reserved check.
- Custom route registration does use the custom-route reserved check.
- No product-specific BeeCap/BeeAgent/MRKT/Binance logic is introduced in generic BeeUI core.
- No route renaming is introduced.
- No external assets/scripts are introduced.
- No unsafe Jinja `|safe` is introduced.
- Existing tests remain green.

#### Required checks

Automated:

```bash
uv run pytest -q
uv run pytest -q -W error::UserWarning
```

Targeted:

```bash
uv run pytest -q tests/test_config.py
uv run pytest -q tests/test_pages.py
uv run pytest -q tests/test_app.py
uv run pytest -q tests/test_product_console.py
```

Smoke:

```bash
./start.sh doctor
./start.sh routes
```

Static/security checks:

```bash
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "MRKT|Binance|BeeCap|BeeAgent|ROP" src/beeui_module/pages src/beeui_module/web src/beeui_module/blocks || true
git diff -- pyproject.toml
```

BeeCap verification after dependency update:

```bash
uv run pytest tests/test_beeui_adapter.py -q
uv run pytest -q
```

Expected BeeCap routes:

```text
GET /
GET /venues/mrkt
GET /venues/binance
GET /modes/dry-run
GET /modes/paper
GET /modes/live
```

#### Definition of Done

- Safe internal path validation and custom route path validation are separated.
- Product console page metadata paths are allowed.
- Navigation links to product console routes are allowed.
- Generic custom route registration still blocks reserved/system/product-console paths.
- `/venues/*` configs are preserved as metadata and not registered as custom pages.
- `/runs/*` custom route shadowing remains blocked.
- Non-reserved custom pages still work.
- Unsafe paths still fail fast.
- Tests cover validation and route registration behavior.
- Docs reflect the distinction between page metadata and custom route registration.
- BeeUI remains product-neutral.
- No new dependencies are added.
- `pyproject.toml.version` is not changed.
- PR is ready for review.

---

## Этап 7 — BeeAgent integration

### Итерация 14 — BeeAgent adapter MVP

**Статус:** PLANNED

#### Goal

Подключить BeeAgent к BeeUI через the same adapter-backed product console, without copying BeeCap UI.

#### Почему это нужно

BeeUI сначала должен быть доказан на BeeCap migration. После этого BeeAgent может использовать тот же product-neutral contract:

```text
Product adapter -> BeeUI console -> artifacts/config/actions
```

BeeAgent не должен получать отдельный UI stack и не должен давать BeeUI прямую authority над MCP/tools/LLM/runtime.

#### Scope

**Включено:**

- BeeAgent-compatible fixture/reference adapter;
- example BeeAgent embedded config:

```text
examples/beeagent_embedded/beeui.yml
```

- adapter-backed pages for:
  - dashboard;
  - modules;
  - runs;
  - run detail;
  - artifacts;
  - capabilities;
  - approvals placeholder;
  - bounded action placeholders;

- capability/readiness indicators:
  - module status;
  - enabled/disabled capabilities;
  - degraded/unavailable states;
  - approval-required placeholders;

- authority boundary tests;

- docs update:
  - `docs/INTEGRATION.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/ROADMAP.md`.

#### Expected BeeAgent side

Real BeeAgent integration should live in BeeAgent, for example:

```text
src/beeagent_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  capabilities.py
  actions.py
```

BeeUI may contain only fixture/reference data proving the contract.

#### Не включено

- MCP execution;
- tool calls from BeeUI;
- local LLM execution from BeeUI;
- autonomous agent controls;
- direct runtime authority;
- direct n8n/MCP/action execution;
- secrets in prompts/logs/artifacts;
- no-code builder;
- BeeAgent production adapter inside BeeUI.

#### Deliverable

BeeAgent can reuse BeeUI after BeeCap proves the architecture.

BeeUI remains product-neutral and does not know BeeAgent execution internals.

#### Checks

- `uv run pytest -q`;
- fake BeeAgent dashboard;
- modules page;
- runs page;
- run detail page;
- artifacts page;
- capabilities page;
- approvals placeholder;
- missing/partial artifacts;
- degraded capability state;
- action placeholders are denied/unavailable unless product callback allows them;
- no secret leakage;
- no direct MCP/tool/LLM execution;
- no BeeAgent runtime imports;
- authority boundary tests.

#### DoD

- BeeAgent UI uses BeeUI contract;
- BeeUI remains product-neutral;
- BeeAgent keeps authority boundary;
- capabilities/actions remain product-controlled;
- BeeUI never directly calls MCP/tools/LLM/runtime execution.

---

## Этап 8 — Future frontend/no-code/standalone

### Итерация 15 — Dashboard schema editor v0

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
- full frontend builder;
- product runtime controls;
- broker/provider actions.

#### Deliverable

Operator can change layout through safe schema, without editing YAML manually.

#### Checks

- block enable/disable;
- reorder;
- invalid layout rejection;
- audit;
- no arbitrary HTML/JS injection;
- `uv run pytest -q`.

#### DoD

- visual builder edits schema only;
- schema validation protects layout;
- no unsafe templates/scripts accepted;
- source of truth remains product/config-owned.

### Итерация 16 — Separate frontend contract v0

**Статус:** FUTURE

#### Goal

Подготовить BeeUI backend к отдельному frontend без переписывания product adapters.

#### Scope

Включено:

- stable API versioning;
- OpenAPI/schema review where applicable;
- frontend-safe envelopes;
- static frontend mount placeholder;
- CORS policy for controlled standalone mode;
- API docs;
- fixture payloads for frontend development.

Не включено:

- React/Vue/Svelte implementation;
- public SaaS;
- multi-tenant auth;
- websocket/SSE streaming;
- new runtime semantics;
- direct product storage access from frontend.

#### Deliverable

BeeUI can be used as backend for future separate frontend.

#### Checks

- API schema snapshot;
- envelope compatibility;
- CORS disabled by default;
- no secret leakage;
- `uv run pytest -q`.

#### DoD

- frontend can attach to stable backend API;
- server-rendered UI still works;
- no second source of truth introduced;
- product adapters remain canonical product boundary.

### Итерация 17 — Standalone BeeUI service v0

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
- broker/runtime authority;
- direct product filesystem reads;
- replacing embedded mode.

#### Deliverable

BeeUI can work as separate service over BeeCap/BeeAgent APIs.

#### Checks

- standalone demo;
- HTTP adapter success;
- backend unavailable state;
- timeout state;
- auth boundary docs;
- `uv run pytest -q`.

#### DoD

- standalone mode works;
- embedded mode remains supported;
- backend product APIs remain source of truth;
- degraded backend does not crash entire UI;
- no direct runtime authority is introduced.

---

## MVP path

Для быстрого выхода к practical MVP идти так:

```text
Iteration 0 — Project skeleton and startup contract
Iteration 1 — Tabler web shell v0
Iteration 2 — Declarative pages and navigation v0
Iteration 3 — Local Tabler vendor/assets and layout parity v1
Iteration 4 — Theme, layout and navigation schema v1
Iteration 5 — Block registry and static dashboard blocks v1
Iteration 7 — Data sources and resolver v0
Iteration 8 — Product adapter contract v0
Iteration 9 — BeeCap adapter fixtures MVP
Iteration 10 — Embedded mount API v0
Iteration 11 — Generic artifact browser v1

BeeCap UI-24 — Embed BeeUI and add BeeCapUiAdapter MVP
Iteration 12 — Adapter-backed Product Console MVP
BeeCap UI-25 — BeeUI Console parity MVP
BeeCap UI-26 — BeeUI default route switch with legacy fallback
```

Минимальный практический MVP считается достигнутым, когда:

- `beeui` запускается отдельно как demo;
- `beeui` подключается к `beecap` как dependency;
- BeeCap имеет product-side `BeeCapUiAdapter`;
- BeeUI mounted в BeeCap under `/beeui`;
- BeeUI рендерит dashboard/runs/run detail/venue dashboards через adapter;
- BeeCap `/beeui` полезен для daily read-only monitoring;
- BeeCap переключает canonical `/` на BeeUI-backed console;
- legacy BeeCap web остаётся только fallback under `/legacy`;
- BeeCap current web templates больше не расширяются вручную;
- BeeCap отдаёт только adapter/read-model/artifacts/callbacks;
- tests green;
- no mutation/no secrets/no provider calls/no broker calls.

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

## Migration rule for BeeCap

During migration:

```text
Before BeeCap UI-24:
  src/beecap_module/web is canonical.

BeeCap UI-24:
  BeeUI is mounted as parallel migration surface under /beeui.

BeeCap UI-25:
  /beeui becomes useful read-only console.

BeeCap UI-26:
  BeeUI becomes canonical route surface.
  legacy web moves under /legacy.

BeeCap UI-27:
  config/admin/actions move to BeeUI callbacks.

BeeCap UI-28:
  src/beecap_module/web can be removed.
```

BeeCap final target structure:

```text
src/beecap_module/
  cli/
    web.py
  interfaces/
    ui/
      __init__.py
      adapter.py
      read_model.py
      artifacts.py
      config.py
      actions.py
```

BeeCap should no longer own:

```text
src/beecap_module/web/templates/
src/beecap_module/web/static/
src/beecap_module/web/app.py
```

after full parity and legacy removal.

## Связанные документы

Для выполнения итераций вместе с этим ROADMAP используются:

- `docs/SDLC.md` — lightweight process, change levels, обязательные quality/security checks, DoD flow;
- `docs/SECURITY.md` — secure development rules и security checks;
- `docs/INTEGRATION.md` — как подключать BeeUI к BeeCap/BeeAgent;
- `docs/COMPONENTS.md` — reusable blocks/components contract;
- `docs/API_CONTRACT.md` — JSON API envelopes and route contracts;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;
- `docs/THEME.md` — theme/customization contract.
