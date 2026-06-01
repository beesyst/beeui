# Web UI

## Purpose

`beeui` — это reusable web UI framework для Bee-продуктов.

Он предоставляет canonical web surface, которую можно подключать к продуктам вроде:

- `beecap`;
- `beeagent`;
- будущие Bee-продукты.

`beeui` отвечает за:

- FastAPI web app;
- Jinja2 templates;
- Tabler-based product shell;
- declarative pages/navigation;
- reusable dashboard blocks;
- artifact browser;
- read-only JSON API contracts;
- bounded config/admin/operator controls;
- theme/customization layer;
- future no-code dashboard builder foundation.

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

Source of truth для `beeui` web surface:

- `config/settings.yml` как runtime/system config;
- `config/schema.yml` как declarative pages/navigation/theme/layout schema в demo mode;
- product adapter;
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

## Integration modes

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

Future integration mode.

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

Decision:

```text
MVP: embedded.
Later: standalone.
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
      vendor/tabler/     # local Tabler-compatible subset

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
  blocks/                # current static/literal block registry and renderers
  adapters/              # planned/future module
  artifacts/             # planned/future module
  api/                   # planned/future module
  auth/                  # planned/future module
  config_ui/             # planned/future module
  theme/                 # planned/future module
```

Rules:

- CLI must stay thin.
- Route/read-model/template logic must not accumulate under `src/beeui_module/cli/`.
- Templates/static are package-local to `src/beeui_module/web/templates/` and `src/beeui_module/web/static/`.
- Product-specific domain logic must not live in generic BeeUI renderers.
- `src/beeui_module/__init__.py` should stay lightweight.

## Start

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
- `schema.yml` — declarative pages/navigation/theme/layout schema.

Отдельный `--config` не является текущим CLI contract.

---

## Product integration

### Current app factory after Iteration 5

In the current Iteration 5 state, the app factory accepts loaded settings and declarative UI schema, then creates the FastAPI/Jinja2 shell with schema-driven pages, navigation, theme/layout and static/literal blocks.

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

Product adapter injection остаётся planned/future scope.

### Future embedded app factory

Фаза product integration должна использовать небольшой app factory или mount helper.

Planned for the product integration phase:

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

Альтернативная planned mount form:

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

Minimum product adapter methods:

```python
class ProductUiAdapter:
    product_id: str
    product_title: str

    def get_dashboard(self) -> dict:
        ...

    def list_runs(self, filters: dict | None = None) -> list[dict]:
        ...

    def get_run(self, run_id: str) -> dict:
        ...

    def list_artifacts(self, run_id: str) -> list[dict]:
        ...

    def read_artifact(self, run_id: str, artifact_id: str) -> dict:
        ...

    def get_config_read_model(self) -> dict:
        ...

    def preview_config_change(self, changes: list[dict]) -> dict:
        ...

    def apply_config_change(self, changes: list[dict]) -> dict:
        ...

    def list_actions(self) -> list[dict]:
        ...

    def execute_action(self, action_id: str, payload: dict) -> dict:
        ...
```

MVP adapter may implement only:

- `get_dashboard`;
- `list_runs`;
- `get_run`;
- `list_artifacts`;
- `read_artifact`.

Write/config/action methods may return explicit `unsupported`.

## BeeUI config

Current runtime config file:

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

Iteration 5 declarative UI schema example (`config/schema.yml`):

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
        width: 6
      - block: runtime_status
        width: 6

  - id: runs
    path: /runs
    title: Runs
    subtitle: Placeholder page for future run overview
    blocks: []
```

Iteration 5 block values are static/literal only. They are rendered from `config/schema.yml` and do not use adapter data sources or selector resolution yet. Dynamic adapter-backed values are planned for the data resolver and product adapter iterations.

Rules:

- config schema must be validated fail-fast;
- `app.title` and `app.product` are required;
- page `id` must be safe and unique;
- page paths must be unique;
- navigation paths must reference known page paths;
- reserved paths `/health`, `/static`, `/static/...` are rejected;
- no arbitrary HTML/JS in config;
- top-level `blocks` is required and validated as mapping;
- pages place blocks with `pages[].blocks[].block` and `pages[].blocks[].width` (`1..12`);
- unknown block references/types and invalid renderer fields fail fast;
- no arbitrary HTML/JS/CSS-like fields are accepted in blocks.

## Tabler shell policy

`beeui` uses Tabler as visual foundation.
В Iteration 1 shell является Tabler-compatible local shell. Полный vendored Tabler bundle может быть добавлен отдельной задачей, если он не принесёт demo telemetry/tracking assets.

Policy:

- use local assets by default;
- no remote scripts in production templates;
- no demo telemetry/scripts;
- no copied Tabler preview tracking;
- no marketing/sponsor/demo blocks from Tabler preview;
- static assets must be package-local or explicitly vendored;
- CSS customization must go through controlled theme variables, not arbitrary user CSS.

BeeUI currently ships a local Tabler-compatible subset under
`src/beeui_module/web/static/vendor/tabler/`.
It is not a full upstream Tabler demo bundle.
No preview/demo/tracking assets are shipped.

Forbidden in production templates:

- remote telemetry;
- `posthog`;
- `scripts.tabler.io`;
- `preview/js/demo`;
- `preview/css/demo`;
- unreviewed external CDN scripts.

Allowed:

- local Tabler CSS/JS;
- local BeeUI CSS/JS;
- controlled product logo/static assets;
- optional CDN only for explicit dev/demo mode, if documented.

## Template primitives

Shared template primitives live in:

```text
src/beeui_module/web/templates/components/
```

Current implemented shell primitives:

- `sidebar`;
- `navbar`;
- `page_header`;
- `footer`;
- `empty_state`.

Current implemented block templates after Iteration 5:

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

Status badge values:

- `ok`
- `warning`
- `error`
- `unknown`
- `partial`
- `degraded`
- `unavailable`
- `disabled`
- `blocked`
- `allowed`
- `denied`

Contract boundary:

- template primitives must stay domain-neutral;
- product-specific labels may be passed via read-model/config;
- primitives must not read product storage directly;
- primitives must not call product APIs.

## Surface model

Generic BeeUI surface ниже описывает planned route families. Current MVP route contract отдельно зафиксирован в разделе `MVP route contract`.

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

Not all routes must exist in MVP.

MVP route set after Iteration 5:

- `/`
- `/runs`
- `/health`
- `/static/...`
- `/static/vendor/tabler/css/tabler-compatible.min.css`
- `/static/vendor/tabler/js/tabler-compatible.min.js`

Iteration 5 changes page body rendering, not the public route set.

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

Rules:

- no arbitrary YAML editor;
- no secrets editing;
- no direct broker actions;
- no direct provider calls from BeeUI;
- no hidden runtime restart;
- every accepted/rejected write attempt must be auditable;
- product callback must own domain validation;
- BeeUI must not bypass product validation.

## JSON API v1

### Envelope

Success:

```json
{
  "ok": true,
  "api": "v1",
  "read_only": true,
  "data": {}
}
```

Error:

```json
{
  "ok": false,
  "api": "v1",
  "read_only": true,
  "error": "error_code",
  "detail": "Human-readable explanation"
}
```

Rules:

- `api` must be `"v1"` for stable routes;
- `read_only` must be true for GET/read routes;
- errors must use stable machine-readable `error`;
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

Page config after Iteration 5:

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

Rules:

* page `id` must be unique;
* page `path` must be unique;
* page path must be safe;
* page cannot define arbitrary HTML;
* `pages[].blocks` is a list of placements;
* each placement must reference an existing top-level `blocks` entry;
* each placement width must be an integer from `1` to `12`;
* pages with an empty `blocks` list render the shared empty state.

## Blocks

Block registry and static/literal block rendering are implemented after Iteration 5.

Top-level block config:

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

Implemented block types after Iteration 5:

* `metric_card`
* `kpi_grid`
* `status_card`
* `table_card`
* `links_card`
* `alert_card`
* `text_card`
* `progress_card`

Current limitations:

* values are static/literal values from `config/schema.yml`;
* selectors are not resolved yet;
* adapter-backed data is not available yet;
* blocks do not call product APIs;
* blocks do not read product storage;
* blocks do not render arbitrary HTML, CSS or JS.

Rules:

* block renderer is domain-neutral;
* block ids must be safe identifiers;
* block type must be one of the registered renderer types;
* unknown block references fail fast;
* unknown block types fail fast;
* renderer-specific fields fail fast when invalid;
* display values accept scalar literals only;
* nested objects/lists are rejected for scalar display values;
* `links_card` accepts internal safe paths only;
* block text is rendered through Jinja autoescape;
* no Jinja expressions from config are evaluated;
* no arbitrary HTML/JS/CSS-like fields are accepted.

Planned later block families:

* `artifact_table`
* `json_viewer`
* `chart_card`
* `action_card`
* `config_form`
* `tabs`

These require later resolver, adapter, artifact, config or action iterations and are intentionally excluded from Iteration 5.

---

## Data resolver

Data resolver is planned for Iteration 7 and is not part of the current Iteration 5 runtime.

Current Iteration 5 blocks render static/literal values from `config/schema.yml`.
Later resolver-backed blocks will resolve data from adapter/source payloads.

Planned selector example:

```yaml
value: dashboard.profit.total_profit
```

Rules:

- missing selector returns explicit unavailable state;
- selector errors must not crash whole page;
- nested selectors must not execute code;
- no template expression execution;
- no arbitrary Python eval;
- no Jinja expressions from config.

## Runs

Generic `/runs` page shows product runs if product adapter supports run listing.

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
  "api": "v1",
  "read_only": true,
  "data": {
    "runs": [],
    "count": 0,
    "filters": {},
    "warnings": []
  }
}
```

Supported generic query params:

- `q`
- `status`
- `mode`
- `venue`
- `severity`

Product adapter may ignore unsupported filters but must report this in `warnings`.

## Run detail

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

Rules:

- `run_id` must pass safe validation;
- missing run must return 404;
- malformed product payload must render degraded state;
- detail page must not mutate artifacts.

### `GET /api/runs/{run_id}`

Response:

```json
{
  "ok": true,
  "api": "v1",
  "read_only": true,
  "data": {
    "run_id": "run_...",
    "summary": {},
    "sections": [],
    "artifacts": [],
    "warnings": []
  }
}
```

## Artifact browser

Artifact browser is generic, but product adapter owns allowlist.

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

Rules:

- `artifact_id` is not raw filesystem path unless product adapter explicitly makes it safe;
- product adapter must map `artifact_id` to safe source;
- no arbitrary relative paths;
- no path traversal;
- no absolute path access from URL;
- no hidden filesystem browsing.

### `GET /api/runs/{run_id}/artifacts`

Response:

```json
{
  "ok": true,
  "api": "v1",
  "read_only": true,
  "data": {
    "run_id": "run_...",
    "artifacts": [],
    "warnings": []
  }
}
```

### `GET /api/runs/{run_id}/artifacts/{artifact_id}`

Reads one allowlisted artifact.

Supported formats:

- JSON;
- JSONL;
- text;
- metadata-only for unsupported/binary.

JSONL response should be bounded:

```json
{
  "format": "jsonl",
  "rows": [
    {
      "line_no": 1,
      "ok": true,
      "value": {}
    }
  ],
  "truncated": false,
  "limit": 200,
  "warnings": []
}
```

Oversized artifact behavior:

```json
{
  "format": "json",
  "bounded": true,
  "partial": true,
  "truncated": true,
  "reason": "artifact_too_large",
  "size_bytes": 10485760,
  "max_bytes": 1048576,
  "content": null
}
```

Rules:

- large artifacts must not be fully loaded on hot dashboard paths;
- corrupted JSONL rows are warnings, not crash;
- unsupported files return metadata or explicit unsupported;
- secrets must be redacted if product marks artifact as sensitive.

## Config read-model

BeeUI can provide generic config read-model UI if product adapter supports it.

### `GET /config`

HTML bounded config view.

Shows:

- allowlisted editable keys;
- non-editable/system-owned fields;
- redacted/secrets-related fields;
- current config hash;
- validation preview controls.

Rules:

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

Rules:

- validates in memory only;
- does not write config;
- does not write storage;
- delegates validation to product adapter;
- forbidden keys rejected;
- secrets rejected.

### `POST /api/config/apply`

Bounded config apply.

Rules:

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

Purpose:

- show support links;
- show config change audit if adapter supports it;
- show operator action audit if adapter supports it;
- show diagnostics summaries if adapter supports it;
- show product integration status.

It is not a full admin platform.

Rules:

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

Rules:

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

Supported fields:

- `mode`: `light | dark | auto`;
- `primary`: controlled color token;
- `font`: controlled font token;
- `radius`: small integer scale;
- `density`: controlled density token.

`mode: auto` is a controlled schema token for future runtime/browser preference integration.
Current runtime keeps the KISS behavior: it renders safely as `data-bs-theme="auto"` and `beeui-theme-mode-auto`, without `localStorage` persistence or client-side theme mutation.

Rules:

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

Rules:

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

## Future no-code builder

Future visual builder must edit schema, not templates.

Allowed future builder changes:

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

Current Iteration 5 scenario:

```text
1. BeeUI loads config/settings.yml.
2. BeeUI loads config/schema.yml.
3. BeeUI validates pages, navigation, theme/layout and blocks fail-fast.
4. Operator opens / or /runs.
5. BeeUI renders configured page title/subtitle/navigation.
6. BeeUI renders the schema-driven theme/layout/navigation shell.
7. BeeUI renders static/literal blocks for pages with configured block placements.
8. Pages without block placements render the shared empty state.
9. No adapter/data resolver/product artifact rendering is executed yet.
```

### 1. Open product dashboard

Planned/future dynamic dashboard scenario (requires data resolver and product adapter iterations).

1. Product starts embedded BeeUI web app.
2. Operator opens `/`.
3. BeeUI calls product adapter `get_dashboard()`.
4. BeeUI renders configured page/blocks.

### 2. Inspect runs

Planned/future (requires adapter iterations).

1. Open `/runs`.
2. BeeUI calls product adapter `list_runs()`.
3. Operator opens `/runs/{run_id}`.
4. BeeUI calls `get_run(run_id)`.

### 3. Inspect artifact

Planned/future (requires artifact/adapters iterations).

1. Open run detail.
2. Click source artifact.
3. BeeUI calls `read_artifact(run_id, artifact_id)`.
4. Product adapter resolves artifact safely.

### 4. Preview config change

Planned/future (requires config UI iterations).

1. Open `/config`.
2. Select allowlisted key.
3. Submit preview.
4. BeeUI delegates validation to product adapter.
5. No file is written.

### 5. Apply bounded config change

Planned/future (requires config apply and audit iterations).

1. Product exposes writable config support.
2. Operator submits allowlisted change.
3. BeeUI checks stale hash.
4. Product adapter validates candidate.
5. Backup and audit are written.
6. Product config remains canonical source of truth.

## MVP route contract

Current Iteration 6 MVP:

- `GET /`
- `GET /runs`
- `GET /components`
- `GET /components/interface`
- `GET /components/forms`
- `GET /components/layout`
- `GET /components/extra`
- `GET /components/plugins`
- `GET /health`
- `GET /static/...`
- `GET /static/vendor/tabler/css/tabler-compatible.min.css`
- `GET /static/vendor/tabler/js/tabler-compatible.min.js`

Iteration 6 adds internal read-only component catalog routes and reusable controlled template primitives while preserving the existing shell and static asset contract.

Planned Iteration 10+ / product integration route families:

- `GET /runs`
- `GET /runs/{run_id}`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/artifacts`
- `GET /api/runs/{run_id}/artifacts/{artifact_id}`

Later:

- `/config`
- `/admin`
- `/api/config/*`
- `/api/actions/*`
- `/login`
- `/logout`

## Related docs

- `README.ru.md`
- `docs/ROADMAP.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/INTEGRATION.md`
- `docs/COMPONENTS.md`
- `docs/API_CONTRACT.md`
- `docs/THEME.md`
