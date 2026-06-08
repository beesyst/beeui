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

---

## Этап 6 — Config/Auth/Actions foundation

### Итерация 13 — Config/Auth/Actions foundation MVP

**Статус:** PLANNED

#### Goal

Добавить минимальный reusable foundation для config read/preview/apply, auth/session/CSRF and bounded operator actions.

Эта итерация заменяет старые отдельные planned-итерации:

```text
It15 — Config read-model and validation preview v1
It16 — Bounded config apply and audit v1
It17 — Bounded operator actions v1
It18 — Auth/session/RBAC v0
```

#### Почему это нужно

Config apply, admin actions and operator controls нельзя развивать отдельно от auth/session/CSRF boundary.

Правильный порядок:

```text
read-only product console first
then route switch
then config/auth/actions foundation
```

Эта итерация не должна блокировать BeeCap read-only MVP. Она нужна после того, как BeeUI уже доказал себя как canonical read-only console.

#### Change level

**security-sensitive**

Причина:

- auth/session boundary;
- CSRF;
- POST routes;
- config mutation;
- operator action execution callbacks;
- audit handoff;
- secrets redaction;
- role-aware access;
- product callback authority boundary.

#### Scope

**Включено:**

- config read-model routes:

```text
GET /config
GET /api/config/read-model
```

- config preview/apply routes:

```text
POST /api/config/preview
POST /api/config/apply
```

- action routes:

```text
GET /actions
GET /api/actions
POST /api/actions/{action_id}/preview
POST /api/actions/{action_id}/execute
```

- adapter callbacks:

```python
get_config_read_model()
validate_config_candidate(candidate)
apply_config_candidate(candidate, expected_hash, actor)

list_actions()
preview_action(action_id, payload)
execute_action(action_id, payload, actor)
```

- minimal auth/session layer:
  - explicit local/dev auth-disabled mode;
  - token/session mode;
  - signed session cookie;
  - login route;
  - logout route;
  - role model:
    - `viewer`;
    - `operator`;
    - `admin`;

- CSRF protection for browser POST routes;

- no default password/token/session secret in repository;

- fail-fast validation when auth is enabled but required secret/token config is missing;

- security headers baseline:
  - `Cache-Control: no-store` for HTML/auth/config/action pages;
  - `X-Content-Type-Options`;
  - frame protection header where practical;

- config read-model rendering:
  - editable fields;
  - non-editable fields;
  - redacted secrets;
  - config hash / version token where product provides it;
  - product-provided allowlist;

- config preview:
  - no mutation;
  - product validation callback only;
  - explicit rejection reasons;

- config apply:
  - product callback only;
  - expected hash / stale guard support;
  - product-owned backup/audit behavior or audit hook;
  - no arbitrary YAML editor;

- action framework:
  - list actions;
  - preview action;
  - execute action through product callback only;
  - allowed/blocked/denied/unavailable states;
  - confirmation-ready response model;
  - audit hook convention;

- docs update:
  - `docs/SECURITY.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/ROADMAP.md`.

#### Не включено

- OAuth;
- SSO;
- user database;
- password reset;
- multi-tenant model;
- SQLAdmin;
- arbitrary YAML editor;
- secrets editing;
- direct runtime execution in BeeUI;
- direct broker/provider/manual order controls;
- background jobs;
- process supervisor;
- standalone service;
- public SaaS auth model.

#### Deliverable

BeeUI can host product-owned config/admin/action workflows safely through callbacks, without owning runtime authority.

Products define:

- config read-model;
- editable allowlist;
- validation;
- apply behavior;
- backup/audit artifacts;
- available actions;
- action preview/execute behavior.

BeeUI provides:

- rendering;
- auth/session shell;
- CSRF protection;
- role checks;
- callback dispatch;
- stable HTML/API envelopes.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- auth disabled only when explicitly configured;
- auth enabled with missing token/session secret fails fast;
- login success;
- login failure;
- logout;
- unauthenticated POST rejected when auth enabled;
- CSRF missing rejected;
- CSRF invalid rejected;
- viewer denied config apply/action execute;
- operator allowed action where adapter allows;
- admin access works for admin/config routes;
- config read-model renders redacted fields;
- config preview does not mutate;
- config apply calls adapter only;
- forbidden config key rejected by adapter;
- stale hash rejected when product reports stale candidate;
- action list renders;
- action preview calls adapter only;
- action execute calls adapter only;
- denied action returns explicit reason;
- no session/token secret leakage;
- no secrets in HTML/API/logs;
- no arbitrary YAML editor;
- no direct product execution in BeeUI;
- no provider/broker/runtime calls from BeeUI.

#### DoD

- BeeUI owns reusable auth/session/CSRF shell;
- BeeUI does not execute product logic directly;
- config/action flows go through product callbacks;
- mutation requires product validation and product-owned audit/backup handoff;
- local unauthenticated mode is explicit and documented;
- role semantics are ready for product usage;
- no hidden write/control path is introduced;
- docs describe the authority boundary.

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
