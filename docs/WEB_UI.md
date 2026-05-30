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

- `config/settings.yml` в Iteration 1;
- product adapter;
- product-provided read-models;
- product artifacts, если они явно allowlisted adapter-ом;
- product-owned config validation callbacks;
- product-owned bounded action callbacks.

Будущий declarative UI config может использовать `config/beeui.yml` или product-specific BeeUI config после Iteration 2+.

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

Canonical web implementation в Iteration 1 живёт в `src/beeui_module/web/`.
Root-level `app.py` не является текущей точкой входа.
Templates/static находятся внутри `web/`.

```text
src/beeui_module/
  web/
    app.py
    templates/
      base.html
      index.html
      components/        # planned
    static/
      css/beeui.css
      js/beeui.js
      vendor/tabler/     # planned vendored bundle

  cli/
    main.py
    serve.py
    doctor.py

  core/
    settings.py
    paths.py
    log.py
    version.py

  pages/                 # planned/future module
  blocks/                # planned/future module
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
./start.sh serve
```

С явным host/port:

```bash
./start.sh serve --host 127.0.0.1 --port 8780
```

Doctor:

```bash
./start.sh doctor
```

Ожидаемые MVP-команды:

```bash
./start.sh doctor
./start.sh serve
```

В Iteration 1 `serve` читает `config/settings.yml`. Отдельный `--config` не является текущим CLI contract.

---

## Product integration

### Current Iteration 1 app factory

В Iteration 1 app factory принимает загруженные settings и создаёт минимальный FastAPI/Jinja2 shell.

Пример:

```python
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.web.app import create_beeui_app

settings = load_settings(settings_path())
app = create_beeui_app(settings=settings)
```

### Future embedded app factory

Фаза product integration должна использовать небольшой app factory или mount helper.

Planned для Iteration 5-7 или embedded integration phase:

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

Current Iteration 1 config file:

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

Будущий declarative UI config может использовать `config/beeui.yml` или product-specific BeeUI config после Iteration 2+.

Planned Iteration 2+ declarative UI schema example:

```yaml
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
          - block: attention
            width: 6

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: dashboard.latest_run
    value: run_id_short
    href: run_url
    empty: No run available

  runtime_status:
    type: status_card
    title: Runtime Status
    source: dashboard.runtime
    status: status
    message: message

  attention:
    type: table_card
    title: Attention
    source: dashboard.attention_items
    columns:
      - key: severity
        label: Severity
      - key: title
        label: Title
      - key: detail
        label: Detail
```

Rules:

- config schema must be validated fail-fast;
- unknown block types must fail fast or render explicit unsupported block state;
- page paths must be unique;
- navigation paths must reference known routes or be explicitly external;
- no arbitrary HTML/JS in config;
- future visual builder must edit this schema, not templates directly.

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

Current planned primitives:

- `page_title_block`;
- `sidebar`;
- `navbar`;
- `breadcrumbs`;
- `status_badge`;
- `empty_state`;
- `degraded_block`;
- `source_link`;
- `metric_card`;
- `kpi_card`;
- `status_card`;
- `data_table`;
- `links_card`;
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

Generic BeeUI surface ниже описывает planned route families. Iteration 1 route contract отдельно зафиксирован в разделе `MVP route contract`.

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

MVP route set (Iteration 1):

- `/`
- `/health`
- `/static/...`

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

Page config:

```yaml
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
```

Rules:

- page `id` must be unique;
- page `path` must be unique;
- page path must be safe;
- page cannot define arbitrary HTML;
- layout width should fit a 12-column grid;
- unknown blocks are rejected or rendered as explicit unsupported state.

## Blocks

Block config:

```yaml
blocks:
  total_profit:
    type: metric_card
    title: Total Profit
    source: dashboard.profit
    value: total_profit
    suffix: USDT
    empty: Profit unavailable
```

MVP block types:

- `metric_card`
- `kpi_grid`
- `status_card`
- `table_card`
- `links_card`

Planned block types:

- `artifact_table`
- `json_viewer`
- `chart_card`
- `action_card`
- `config_form`
- `tabs`
- `markdown_card`

Rules:

- block renderer is domain-neutral;
- block source must resolve through data resolver/adapter;
- block must handle missing/partial data;
- block must not call product APIs directly;
- block must not read filesystem directly unless it is an artifact browser block using allowlisted artifact adapter.

---

## Data resolver

Block data is resolved from adapter/source payloads.

Selector example:

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

Supported fields:

- `mode`: `light | dark | auto`;
- `primary`: controlled color token;
- `font`: controlled font token;
- `radius`: small integer scale;
- `density`: `comfortable | compact`.

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

Auth is not required for Iteration 1 MVP, but BeeUI must be designed for it.

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

### 1. Open product dashboard

1. Product starts embedded BeeUI web app.
2. Operator opens `/`.
3. BeeUI calls product adapter `get_dashboard()`.
4. BeeUI renders configured page/blocks.

### 2. Inspect runs

1. Open `/runs`.
2. BeeUI calls product adapter `list_runs()`.
3. Operator opens `/runs/{run_id}`.
4. BeeUI calls `get_run(run_id)`.

### 3. Inspect artifact

1. Open run detail.
2. Click source artifact.
3. BeeUI calls `read_artifact(run_id, artifact_id)`.
4. Product adapter resolves artifact safely.

### 4. Preview config change

1. Open `/config`.
2. Select allowlisted key.
3. Submit preview.
4. BeeUI delegates validation to product adapter.
5. No file is written.

### 5. Apply bounded config change

1. Product exposes writable config support.
2. Operator submits allowlisted change.
3. BeeUI checks stale hash.
4. Product adapter validates candidate.
5. Backup and audit are written.
6. Product config remains canonical source of truth.

## MVP route contract

Iteration 1 MVP:

- `GET /`
- `GET /health`
- `GET /static/...`

Iteration 2-4 MVP (planned):

- `GET /api/dashboard`

Iteration 5-10 MVP:

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
