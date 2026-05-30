# SPEC — BeeUI reusable UI layer

## 0. Термины

- Репозиторий: `beeui`
- Python-пакет import: `beeui_module`
- Distribution package: `beeui`
- Bee-продукт: отдельный продукт/репозиторий экосистемы Bee, например `beecap`, `beeagent`
- Product adapter: слой подключения конкретного Bee-продукта к `beeui`
- Read-model: нормализованное представление данных продукта для UI/API
- Artifact: файл/набор файлов продукта в `storage/`, которые являются evidence/source of truth
- Block: reusable UI-компонент dashboard/page, например KPI card, table, status card
- Page schema: declarative описание страницы, navigation и blocks
- Data source: источник данных для UI block: adapter, static JSON, HTTP endpoint, artifact reader
- Embedded mode: `beeui` импортируется и запускается внутри процесса Bee-продукта
- Standalone mode: `beeui` запускается отдельным сервисом и подключается к продуктам по HTTP API
- Operator UI: внутренний интерфейс управления/наблюдения
- Product frontend: будущий внешний frontend/product UI поверх стабильных BeeUI backend contracts
- Bounded action: явно разрешённое действие через product-owned callback/API с validation/audit
- Authority boundary: граница полномочий между UI и domain/runtime/product logic

## 1. Цель

Сделать универсальный Python-based UI/backend framework для Bee-продуктов.

`beeui` должен убрать повторяемую web/UI инфраструктуру из `beecap`, `beeagent` и будущих Bee-продуктов.

Проект должен предоставлять:

- FastAPI + Jinja2 + Tabler web surface;
- declarative pages/navigation/dashboard schema;
- reusable dashboard blocks;
- product adapter contract;
- artifact browser;
- read-only operator dashboards;
- stable JSON API для будущего frontend;
- bounded config/admin/operator controls;
- theme/customization layer;
- foundation для будущего no-code dashboard builder.

`beeui` не должен становиться trading engine, agent runtime, execution controller или product domain layer.

Главная формула:

```text
BeeUI renders.
Product decides.
```

## 2. Главная архитектурная идея

`beeui` — это общий interface layer.

Bee-продукты остаются владельцами:

- runtime behavior;
- business/domain logic;
- config validation;
- artifacts;
- bounded action execution;
- security-sensitive authority boundaries;
- product-specific calculations.

`beeui` владеет:

- web shell;
- layout;
- navigation;
- reusable blocks;
- page rendering;
- artifact browsing UI;
- config/admin UI shell;
- auth/session shell;
- JSON API envelopes;
- theme/customization;
- future visual builder.

Правильная схема:

```text
BeeCap / BeeAgent
  config/settings.yml
  storage/*
  product read-model
  product adapter
  product validation callbacks
  bounded product actions

        ↓

beeui ProductUiAdapter

        ↓

beeui
  FastAPI
  Jinja2
  Tabler
  pages
  blocks
  artifact browser
  config/admin/action UI
  JSON API
```

Неправильная схема:

```text
beeui напрямую угадывает структуру storage каждого продукта
beeui считает trading/domain logic
beeui сам исполняет runtime/broker/product actions
beeui становится вторым source of truth
```

## 3. Стек v0

Обязательный стек:

- Python 3.14+
- FastAPI
- Jinja2
- Tabler
- PyYAML
- pytest
- httpx для тестов
- uv как dependency/runtime tool
- file-based examples and fixtures

Опционально позже:

- SQLite для users/settings/audit index
- HTMX для lightweight интерактива
- ApexCharts для charts
- Pydantic, если ручная validation станет слишком тяжёлой

Не использовать в MVP:

- React/Vue/Svelte как обязательный frontend;
- Node build chain как core requirement;
- database-first architecture;
- full no-code builder;
- drag-and-drop layout editor;
- arbitrary YAML editor в браузере.

## 4. Принципы разработки

- KISS: минимально достаточные abstractions.
- Server-rendered HTML first.
- Schema-driven pages and blocks.
- Read-only by default.
- Write/control actions только через bounded product callbacks/API.
- Product remains source of truth.
- No hidden execution authority.
- No direct broker/runtime/product mutation from BeeUI.
- No arbitrary filesystem browsing.
- No arbitrary template/script injection.
- No secrets in HTML/API/logs/artifacts.
- HTML autoescape always on.
- All file/artifact IDs treated as untrusted input.
- Path traversal must be blocked.
- Invalid configs fail fast.
- Partial/corrupted product artifacts render as explicit degraded/partial states.
- Future no-code builder edits safe schema only, not arbitrary HTML/JS.

## 5. Product scope

### 5.1 Что входит в BeeUI

`beeui` должен уметь:

- запускаться как standalone demo app;
- подключаться embedded mode к Bee-продукту;
- читать `beeui.yml`;
- строить navigation/pages из schema;
- рендерить base Tabler layout;
- рендерить reusable blocks;
- получать данные через adapters/data sources;
- показывать dashboard;
- показывать run list / run detail, если продукт предоставляет соответствующий read-model;
- показывать artifact list / artifact preview;
- отдавать стабильный JSON API;
- показывать bounded config read-model/preview/apply, если продукт предоставляет config callbacks;
- показывать bounded actions, если продукт предоставляет action callbacks;
- поддерживать theme customization;
- в будущем поддержать visual dashboard schema editor.

### 5.2 Что не входит в BeeUI

`beeui` не должен:

- принимать торговые решения;
- классифицировать лиды/attachments;
- вызывать broker API;
- вызывать agent tools напрямую;
- мутировать runtime artifacts без product callback;
- читать secrets;
- хранить product runtime state как canonical source;
- заменять `config/settings.yml` продукта;
- создавать второй runtime engine;
- быть обязательным orchestration layer.

## 6. Режимы интеграции

### 6.1 Embedded mode

MVP integration mode.

`beeui` импортируется в продукт:

```python
from beeui_module.app import create_beeui_app
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

Плюсы:

- быстрее для MVP;
- один процесс;
- проще auth/session;
- проще локальная разработка;
- нет CORS/service discovery.

Минусы:

- каждый продукт запускает свой BeeUI instance;
- обновление BeeUI идёт через dependency update.

### 6.2 Standalone mode

Future integration mode.

```text
beeui service
  → beecap API
  → beeagent API
```

Плюсы:

- единый UI service;
- можно подключить несколько backend products;
- проще строить future product frontend.

Минусы:

- сложнее auth;
- CORS;
- service discovery;
- deployment;
- version compatibility.

Решение:

```text
MVP: embedded mode.
Future: standalone mode.
```

## 7. Product adapter contract

Каждый Bee-продукт подключается через adapter.

Минимальный contract:

```python
class ProductUiAdapter:
    product_id: str
    product_title: str

    def get_dashboard(self) -> dict:
        ...

    def list_runs(self, filters: dict | None = None) -> dict:
        ...

    def get_run(self, run_id: str) -> dict:
        ...

    def list_artifacts(self, run_id: str) -> dict:
        ...

    def read_artifact(self, run_id: str, artifact_id: str) -> dict:
        ...

    def get_config_read_model(self) -> dict:
        ...

    def preview_config_change(self, changes: list[dict]) -> dict:
        ...

    def apply_config_change(self, changes: list[dict]) -> dict:
        ...

    def list_actions(self) -> dict:
        ...

    def execute_action(self, action_id: str, payload: dict) -> dict:
        ...
```

Не все методы обязательны в v0.

Adapter обязан:

- валидировать product-specific IDs;
- не раскрывать secrets;
- возвращать explicit partial/error states;
- не мутировать source artifacts в read-only methods;
- выполнять write/control actions только через product-owned logic;
- возвращать stable envelopes.

`beeui` не должен напрямую знать внутреннюю структуру `beecap` или `beeagent`.

## 8. Конфигурация BeeUI

Основной файл:

```text
config/beeui.yml
```

Пример:

```yaml
app:
  title: BeeCap
  product: beecap
  theme:
    mode: dark
    primary: blue
    font: Inter
    density: compact

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
  - title: Admin
    path: /admin
    icon: shield

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
          - block: total_profit
            width: 3

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: dashboard.system
    value: latest_run_id
    href: latest_run_url

  runtime_status:
    type: status_card
    title: Runtime
    source: dashboard.system
    value: runtime_status
    badge: runtime_status_badge
```

Config validation:

- missing required keys fail fast;
- duplicate page paths fail fast;
- unknown block types fail fast;
- invalid layout width fail fast;
- unsafe path values rejected;
- arbitrary HTML/JS not accepted.

## 9. Pages and blocks

### 9.1 Page

Page — declarative unit:

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    layout: [...]
```

Page может содержать:

- title;
- subtitle;
- layout rows;
- blocks;
- source references;
- route metadata.

### 9.2 Block

Block — reusable UI component.

Base block types v0:

- `metric_card`
- `kpi_grid`
- `status_card`
- `table_card`
- `links_card`

Required later:

- `artifact_table`
- `json_viewer`
- `chart_card`
- `action_card`
- `config_form`

Block renderer не должен содержать product domain logic.

Он получает уже готовый normalized payload.

## 10. Data sources

Data source types:

- `static` — local JSON/demo data;
- `adapter` — product adapter method;
- `http` — future product API source;
- `artifact` — safe artifact reader через product adapter.

MVP required:

- static data source;
- adapter data source;
- selector resolver.

Response envelope:

```json
{
  "status": "ok",
  "data": {},
  "warnings": [],
  "source": {
    "type": "adapter",
    "name": "dashboard"
  }
}
```

Allowed statuses:

- `ok`
- `partial`
- `empty`
- `degraded`
- `error`

## 11. JSON API contract

BeeUI API должен использовать стабильный envelope:

```json
{
  "status": "ok",
  "data": {},
  "warnings": [],
  "errors": [],
  "meta": {
    "version": "v1"
  }
}
```

Minimum API v0:

- `GET /api/dashboard`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/artifacts`
- `GET /api/runs/{run_id}/artifacts/{artifact_id}`

Later:

- `GET /api/pages`
- `GET /api/navigation`
- `GET /api/config/read-model`
- `POST /api/config/preview`
- `POST /api/config/apply`
- `GET /api/actions`
- `POST /api/actions/{action_id}`

API rules:

- no secrets;
- deterministic response shape;
- explicit errors;
- no raw tracebacks;
- no arbitrary file paths;
- no hidden product fallback;
- UI/API semantic parity.

## 12. Artifact browser

Artifact browser должен быть reusable и safe.

Required behavior:

- list artifact metadata;
- preview JSON;
- preview JSONL;
- preview text;
- show parse warnings;
- show source links;
- show partial/corrupted states;
- block path traversal;
- allowlist artifact access.

Forbidden:

- arbitrary filesystem browsing;
- `../` path traversal;
- absolute path input from UI;
- secrets exposure;
- artifact editing in v0;
- artifact deletion in v0;
- upload in v0.

Artifact access должен идти через product adapter, а не напрямую через BeeUI guesses.

## 13. Config UI

Config UI делится на два этапа.

### 13.1 Read-model and preview

Read-only.

Required:

- show current config read-model;
- show editable/non-editable/redacted fields;
- support allowlisted preview;
- use product validation callback;
- return diff summary;
- never write files.

Routes:

- `GET /config`
- `GET /api/config/read-model`
- `POST /api/config/preview`

### 13.2 Apply and audit

Write-capable but bounded.

Required:

- explicit allowlist;
- product validation callback;
- stale hash guard;
- backup before write;
- audit artifact for accepted and rejected attempts;
- atomic/rollback-friendly write;
- no secrets in audit;
- no automatic runtime restart.

Suggested artifacts:

```text
storage/interfaces/config_revisions/<change_id>/settings.before.yml
storage/interfaces/config_changes/<change_id>/audit.json
```

BeeUI provides generic flow. Product owns actual config semantics.

## 14. Operator actions

Operator actions are disabled by default.

Action execution rules:

- product defines action list;
- product defines action payload schema/validation;
- BeeUI renders action form;
- BeeUI sends payload to product callback/API;
- product executes or denies;
- every attempt gets audit artifact;
- BeeUI never executes product logic directly.

Forbidden in v0:

- manual broker/order console;
- direct live execution;
- direct agent tool execution;
- hidden background jobs;
- arbitrary command execution.

Action result statuses:

- `accepted`
- `blocked`
- `invalid`
- `denied`
- `unavailable`
- `error`

## 15. Auth and security

Auth v0 requirements:

- login/logout;
- password hash;
- signed session cookie;
- roles:
  - `admin`
  - `operator`
  - `viewer`

- route protection;
- CSRF protection for POST routes;
- secure cookie settings where applicable;
- no default admin password committed to repo.

Auth may be disabled only explicitly for local/dev.

Security requirements:

- HTML autoescape enabled;
- no raw user HTML;
- no arbitrary JS injection;
- no secrets in HTML/API/logs/artifacts;
- file IDs treated as untrusted;
- run IDs treated as untrusted;
- artifact IDs treated as untrusted;
- config keys treated as untrusted;
- path traversal blocked;
- POST routes role-gated and CSRF-gated;
- no hidden authority escalation.

## 16. Theme and customization

Theme config:

```yaml
app:
  theme:
    mode: dark
    primary: blue
    font: Inter
    radius: 2
    density: compact
```

Supported v1 customization:

- mode: `dark|light`;
- primary color from allowlist;
- font from allowlist or safe local static;
- density: `comfortable|compact`;
- border radius scale;
- product title/logo.

Forbidden:

- arbitrary CSS editor in MVP;
- arbitrary JS;
- remote untrusted assets;
- user-uploaded executable/static assets;
- unsafe CSS injection.

## 17. BeeCap integration target

BeeCap should not keep growing its own web templates/static/dashboard code after BeeUI MVP.

BeeCap should keep:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  config_contract.py
  actions.py
```

BeeCap should eventually remove or stop expanding:

```text
src/beecap_module/web/templates/
src/beecap_module/web/static/
src/beecap_module/web/generic dashboard rendering
src/beecap_module/web/generic artifact browser
src/beecap_module/web/generic config/admin UI
```

BeeCap owns:

- MRKT semantics;
- Binance semantics;
- paper/live/dry-run meaning;
- PnL/cycle/account calculations;
- config validation;
- bounded action execution;
- runtime artifacts.

BeeUI renders BeeCap-provided read-models.

## 18. BeeAgent integration target

BeeAgent should not copy BeeCap web/UI logic.

BeeAgent should provide:

```text
src/beeagent_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  capabilities.py
  actions.py
```

BeeAgent owns:

- modules;
- runs;
- artifacts;
- capabilities;
- approvals;
- policy/authority checks;
- action validation.

BeeUI renders:

- BeeAgent dashboard;
- modules page;
- runs page;
- artifact browser;
- capabilities view;
- approvals placeholder/actions where bounded.

## 19. Project structure

Target structure:

```text
beeui/
├── config/
│   ├── demo.beeui.yml
│   └── start.py
│
├── docs/
│   ├── API_CONTRACT.md
│   ├── COMPONENTS.md
│   ├── INTEGRATION.md
│   ├── ROADMAP.md
│   ├── SDLC.md
│   ├── SECURITY.md
│   ├── SPEC.md
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
│       ├── artifacts/
│       ├── auth/
│       ├── adapters/
│       ├── blocks/
│       ├── cli/
│       ├── config_ui/
│       ├── core/
│       ├── data/
│       ├── pages/
│       ├── templates/
│       ├── static/
│       └── theme/
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

## 20. Startup contract

### 20.1 `start.sh`

`start.sh` должен:

- проверить наличие `uv`;
- установить `uv`, если отсутствует;
- выполнить `uv sync --frozen --extra dev`;
- запустить `uv run --frozen --extra dev python config/start.py "$@"`;
- не изменять `uv.lock` без явного действия разработчика.

### 20.2 `config/start.py`

Required commands v0:

```bash
./start.sh doctor
./start.sh serve
```

Later:

```bash
./start.sh serve --config config/demo.beeui.yml --host 127.0.0.1 --port 8780
./start.sh doctor
```

`doctor` должен проверять:

- package import;
- config readability;
- template/static presence;
- basic security defaults;
- logs directory.

`serve` должен запускать BeeUI web app.

## 21. MVP criteria

MVP считается достигнутым, если:

- `beeui` имеет рабочий project skeleton;
- `./start.sh doctor` работает;
- `./start.sh serve` показывает Tabler shell;
- pages/navigation читаются из `beeui.yml`;
- dashboard собирается из reusable blocks;
- data resolver работает;
- product adapter contract стабилен;
- BeeCap adapter MVP показывает dashboard/run overview на fixture или real artifacts;
- embedded mount API работает;
- BeeCap может подключить `beeui` как dependency;
- BeeCap больше не обязан расширять собственные Tabler templates для базового dashboard;
- tests green.

Minimum MVP routes:

- `GET /`
- `GET /health`
- `GET /runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/artifacts`
- `GET /api/dashboard`
- `GET /api/runs`
- `GET /api/runs/{run_id}`

## 22. Future no-code builder

No-code builder не входит в MVP.

Правильная очередность:

1. declarative YAML/Python schema;
2. stable page/block schema;
3. config read-model;
4. config apply/audit;
5. visual dashboard schema editor;
6. drag-and-drop layout editor;
7. public/frontend builder.

No-code builder должен редактировать только safe schema.

Он не должен принимать:

- arbitrary HTML;
- arbitrary JS;
- arbitrary Python;
- arbitrary filesystem paths;
- direct product execution commands.

## 23. Deployment model

### MVP deployment

Embedded per product container:

```text
container: beecap
  includes dependency: beeui
  exposes beecap web

container: beeagent
  includes dependency: beeui
  exposes beeagent web
```

This is the recommended MVP path.

### Future deployment

Standalone BeeUI service:

```text
container: beeui
container: beecap-api
container: beeagent-api
```

Standalone mode requires:

- product HTTP APIs;
- auth/session model;
- CORS policy;
- service discovery;
- version compatibility;
- stronger deployment docs.

Do not start MVP from standalone service.

## 24. Критерии готовности v1

BeeUI v1 считается готовым, если:

- BeeCap подключён через BeeUI embedded mode;
- BeeAgent подключён через BeeUI embedded mode;
- dashboard/pages/blocks reusable;
- artifact browser reusable;
- stable JSON API v1 существует;
- config read-model/preview exists;
- bounded config apply exists;
- bounded operator actions exist;
- auth/session/RBAC v0 exists;
- theme customization exists;
- no-code foundation documented;
- source of truth остаётся в product configs/artifacts/APIs;
- no secrets leak;
- no arbitrary filesystem access;
- no direct broker/runtime/agent execution authority;
- tests cover normal, partial, malformed and security-sensitive scenarios.

## 25. Что не делать

Не делать в MVP:

- полноценный Retool/Webflow;
- drag-and-drop builder;
- React frontend;
- multi-tenant SaaS;
- OAuth/SSO;
- database-first admin;
- full CMS;
- arbitrary YAML editor;
- arbitrary artifact file manager;
- direct broker controls;
- direct agent tool execution;
- background orchestration service;
- product runtime logic inside BeeUI.

## 26. Связанные документы

- `docs/ROADMAP.md` — этапы и итерации
- `docs/SDLC.md` — процесс разработки и change levels
- `docs/SECURITY.md` — secure development rules
- `docs/INTEGRATION.md` — подключение к BeeCap/BeeAgent
- `docs/COMPONENTS.md` — block/component contracts
- `docs/API_CONTRACT.md` — JSON API contracts
- `docs/WEB_UI.md` — HTML routes and UI behavior
- `docs/THEME.md` — theme/customization contract
