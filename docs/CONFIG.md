# CONFIG — BeeUI configuration

## Принцип

`beeui` использует два разных уровня конфигурации:

1. `config/settings.yml` — runtime/security config самого `beeui`:
   - web host/port;
   - logging;
   - storage;
   - security;
   - auth/session/CSRF settings;
   - product mode/metadata;
   - feature flags.

2. `config/schema.yml` — текущая demo/MVP UI schema:
   - app display metadata;
   - locale seed;
   - theme;
   - layout;
   - navigation;
   - data sources;
   - reusable blocks registry;
   - pages and block placements.

`config/beeui.yml` — целевое/future naming для product integration после adapter/block/data-source итераций. Это не текущий CLI contract.

Главное правило:

```text
settings.yml отвечает за запуск и безопасность.
schema.yml отвечает за текущий demo/MVP внешний вид, навигацию, layout, страницы и reusable blocks.
```

`beeui` не должен хранить domain/runtime logic Bee-продуктов.

Bee-продукты остаются source of truth для:

- runtime behavior;
- artifacts;
- product config validation;
- bounded execution/action APIs;
- business/domain calculations.

`beeui` только читает product read-model через adapter/API и рендерит UI.

## Файлы конфигурации

Текущая demo/MVP структура:

```text
beeui/
  config/
    settings.yml
    schema.yml
```

Целевое naming для product integration:

```text
config/settings.yml
config/beeui.yml
```

Текущая web-команда:

```bash
./start.sh web --host 127.0.0.1 --port 8780
```

Текущий CLI поддерживает `--host` и `--port` для `web`.
Он не поддерживает:

```bash
./start.sh web --config config/beeui.yml --settings config/settings.yml
```

# 1. `config/settings.yml`

## Назначение

`settings.yml` управляет запуском `beeui` как приложения.

Он не должен описывать торговые стратегии, MRKT lifecycle, BeeAgent modules или product-specific business logic.

## Минимальный пример `settings.yml`

```yaml
app:
  name: beeui
  environment: local # local | dev | prod

web:
  host: 127.0.0.1
  port: 8780
  open_browser: false
  route_prefix: ""
  cache_static: 3600

logging:
  level: INFO # DEBUG | INFO | WARNING | ERROR | CRITICAL
  utc: true
  clear_logs: false
  file: logs/app.log

storage:
  enabled: true
  root: storage

security:
  html_autoescape: true
  assets_ext: false

auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false

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

## Используемые секции `settings.yml`

| Секция       | Назначение                                                             |
| ------------ | ---------------------------------------------------------------------- |
| `app.*`      | Идентичность runtime-приложения `beeui`                                |
| `web.*`      | Host, port, route prefix, browser open behavior                        |
| `logging.*`  | Логи `beeui`                                                           |
| `storage.*`  | Локальный storage для audit/config/action artifacts, если они включены |
| `security.*` | Базовые security defaults                                              |
| `auth.*`     | Auth/session/CSRF runtime settings                                     |
| `product.*`  | Какой product adapter используется                                     |
| `features.*` | Feature flags для UI capabilities                                      |

## `app.*`

```yaml
app:
  name: beeui
  environment: local
```

### Поля

| Ключ              | Тип    | Обязательный | Значения               | Описание               |
| ----------------- | ------ | ------------ | ---------------------- | ---------------------- |
| `app.name`        | string | да           | non-empty              | Имя runtime-приложения |
| `app.environment` | string | да           | `local`, `dev`, `prod` | Окружение запуска      |

### Правила

- `app.name` не должен быть пустым.
- `app.environment=prod` должен использовать более строгие security defaults:
  - `auth.enabled=true`;
  - `auth.cookie_secure=true`;
  - `security.assets_ext=false`.

## `web.*`

```yaml
web:
  host: 127.0.0.1
  port: 8780
  open_browser: false
  route_prefix: ""
  cache_static: 3600
```

### Поля

| Ключ               | Тип    | Обязательный | Описание                         |
| ------------------ | ------ | ------------ | -------------------------------- |
| `web.host`         | string | да           | Host для uvicorn/FastAPI         |
| `web.port`         | int    | да           | Port                             |
| `web.open_browser` | bool   | да           | Открывать браузер при запуске    |
| `web.route_prefix` | string | да           | Prefix для embedded/mounted mode |
| `web.cache_static` | int    | да           | Cache для static assets          |

### Правила

- `web.port` должен быть `1..65535`.
- `web.route_prefix` должен быть пустым или начинаться с `/`.
- `web.route_prefix` не должен заканчиваться `/`, кроме самого `/`.
- `web.open_browser=true` не должен ломать запуск, если браузер открыть не удалось.

## `logging.*`

```yaml
logging:
  level: INFO
  utc: true
  clear_logs: false
  file: logs/app.log
```

### Поля

| Ключ                 | Тип    | Обязательный | Значения                                        |
| -------------------- | ------ | ------------ | ----------------------------------------------- |
| `logging.level`      | string | да           | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `logging.utc`        | bool   | да           | true/false                                      |
| `logging.clear_logs` | bool   | да           | true/false                                      |
| `logging.file`       | string | да           | path внутри проекта                             |

### Правила

- `logging.file` не должен выходить за root проекта.
- В логи нельзя писать:
  - session secrets;
  - auth tokens;
  - product API keys;
  - raw sensitive headers;
  - full config with secrets.

## `storage.*`

```yaml
storage:
  enabled: true
  root: storage
```

### Назначение

`storage` нужен `beeui` только для собственных support artifacts:

- config change audits;
- config revisions;
- operator action audits;
- auth/session diagnostics, если включено;
- future builder schema revisions.

Product runtime artifacts остаются в storage продукта, например:

```text
beecap/storage/runs/*
beeagent/storage/runs/*
```

### Поля

| Ключ              | Тип    | Обязательный | Описание                            |
| ----------------- | ------ | ------------ | ----------------------------------- |
| `storage.enabled` | bool   | да           | Разрешить локальные beeui artifacts |
| `storage.root`    | string | да           | Root directory для beeui artifacts  |

### Правила

- `storage.root` не должен выходить за root проекта.
- Product artifacts не копируются в `beeui/storage`.
- `beeui` может хранить только свои audit/support artifacts.

## `security.*`

```yaml
security:
  html_autoescape: true
  assets_ext: false
```

### Поля

| Ключ                       | Тип  | Обязательный | Описание                         |
| -------------------------- | ---- | ------------ | -------------------------------- |
| `security.html_autoescape` | bool | да           | Jinja2 autoescape                |
| `security.assets_ext`      | bool | да           | Разрешить external JS/CSS assets |

### Правила

- `security.html_autoescape` должен быть `true`.
- `security.assets_ext=false` по умолчанию.
- Production не должен зависеть от CDN.
- Tabler assets должны быть vendored/local.
- Нельзя копировать demo tracking scripts из external templates.
- Static roots должны быть path-safe.

## `auth.*`

Текущий contract после Iteration 13.

```yaml
auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false
```

### Назначение

Auth/session/CSRF layer защищает internal operator/admin UI и protected POST routes.

### Поля

| Ключ                  | Тип    | Обязательный | Описание                                 |
| --------------------- | ------ | ------------ | ---------------------------------------- |
| `auth.enabled`        | bool   | да           | Включить auth/session mode               |
| `auth.session_secret` | string | да*          | Session secret из env или runtime config |
| `auth.operator_token` | string | да*          | Operator token из env или runtime config |
| `auth.admin_token`    | string | да*          | Admin token из env или runtime config    |
| `auth.cookie_secure`  | bool   | да           | Secure flag для signed session cookie    |

`*` — обязательно при `auth.enabled=true`.

### Правила

- `auth.enabled=false` допустим только для explicit local/dev mode.
- При `auth.enabled=true` обязательны `session_secret`, `operator_token`, `admin_token`.
- Tokens/secrets должны приходить из env или внешнего runtime config и не должны коммититься как raw secrets.
- `cookie_secure=false` допустим для local HTTP.
- `cookie_secure=true` обязателен для remote/HTTPS.
- Protected POST routes требуют role + CSRF.

## `product.*`

```yaml
product:
  mode: demo
  id: demo
  title: BeeUI Demo
  adapter: static
```

### Назначение

Определяет, какой product adapter использовать.

### Modes

| Mode       | Описание                                            |
| ---------- | --------------------------------------------------- |
| `demo`     | Локальный demo mode                                 |
| `embedded` | BeeUI запущен внутри Bee-продукта                   |
| `http`     | BeeUI работает standalone и ходит в продукт по HTTP |

### Adapters

| Adapter    | Описание                     |
| ---------- | ---------------------------- |
| `static`   | Static/demo data             |
| `beecap`   | BeeCap embedded adapter      |
| `beeagent` | BeeAgent embedded adapter    |
| `http`     | Generic HTTP product adapter |

### Поля

| Ключ              | Тип    | Обязательный | Описание                   |
| ----------------- | ------ | ------------ | -------------------------- |
| `product.mode`    | string | да           | `demo`, `embedded`, `http` |
| `product.id`      | string | да           | Product id                 |
| `product.title`   | string | да           | Display title              |
| `product.adapter` | string | да           | Adapter name               |

### Правила

- `product.id` должен быть safe slug: `[a-zA-Z0-9_-]`.
- `product.mode=http` требует `http_adapter.enabled=true`.
- `product.mode=embedded` требует adapter injection из host product.
- `beeui` не должен сам угадывать product internals без adapter.

## `http_adapter.*`

Planned/future schema after product-adapter iterations.
Not implemented in current Iteration 4 runtime.

```yaml
http_adapter:
  enabled: false
  base_url: ""
  timeout_seconds: 5
  headers: {}
```

### Назначение

Используется в future standalone mode.

В MVP основной режим — embedded.

### Поля

| Ключ                           | Тип       | Обязательный | Описание               |
| ------------------------------ | --------- | ------------ | ---------------------- |
| `http_adapter.enabled`         | bool      | да           | Включить HTTP adapter  |
| `http_adapter.base_url`        | string    | да           | URL product API        |
| `http_adapter.timeout_seconds` | int/float | да           | Timeout                |
| `http_adapter.headers`         | dict      | да           | Дополнительные headers |

### Правила

- `timeout_seconds > 0`.
- Secrets/tokens не должны храниться прямо в YAML.
- Auth headers должны подставляться через env references в future iteration.
- Backend unavailable должен отображаться как degraded UI state, а не ронять весь app.

## `features.*`

```yaml
features:
  browser_artifact: false
  config_preview: false
  config_apply: false
  operator_actions: false
  api: false
```

### Поля

| Ключ                        | Тип  | Обязательный | Описание                          |
| --------------------------- | ---- | ------------ | --------------------------------- |
| `features.browser_artifact` | bool | да           | Включить artifact browser         |
| `features.config_preview`   | bool | да           | Включить config preview           |
| `features.config_apply`     | bool | да           | Включить bounded config apply     |
| `features.operator_actions` | bool | да           | Включить bounded operator actions |
| `features.api`              | bool | да           | Включить JSON API routes          |

### Правила

- `config_apply=true` требует `config_preview=true`.
- `operator_actions=true` требует product action callback.
- `auth.enabled=true` рекомендуется для любых write/control features.
- В MVP:
  - `browser_artifact=false`;
  - `api=false`;
  - `config_preview=false`;
  - `config_apply=false`;
  - `operator_actions=false`.

# 2. Текущий `config/schema.yml`

## Назначение

`config/schema.yml` — текущий demo/MVP UI schema-файл, используемый runtime и CLI после Iteration 13.1.

`config/beeui.yml` is future/product integration naming, not the current CLI contract.

`schema.yml` описывает UI:

- app display metadata;
- theme;
- navigation;
- blocks;
- pages;

Он не должен содержать secrets и product runtime logic.

## Текущий пример `config/schema.yml`

```yaml
app:
  title: BeeUI Demo
  product: demo
  logo_text: BeeUI
  locale:
    default: en
    available:
      - en
      - ru
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

## Используемые секции `schema.yml`

| Секция           | Назначение                                            |
| ---------------- | ----------------------------------------------------- |
| `app.*`          | Display metadata and theme                            |
| `navigation[]`   | Sidebar/global navigation                             |
| `data_sources.*` | Controlled read-only demo/static data sources         |
| `blocks.*`       | Reusable literal or resolver-backed block definitions |
| `pages[]`        | Pages/routes and block placement                      |

## `app.*`

```yaml
app:
  title: BeeUI Demo
  product: demo
  logo_text: BeeUI
  locale:
    default: en
    available:
      - en
      - ru
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

### Поля

| Ключ            | Тип    | Обязательный | Описание                   |
| --------------- | ------ | ------------ | -------------------------- |
| `app.title`            | string       | да           | Display title                                      |
| `app.product`          | string       | да           | Product key                                        |
| `app.logo_text`        | string       | да           | Sidebar/header logo text                           |
| `app.locale`           | dict         | нет          | Настройки locale seed                              |
| `app.locale.default`   | string       | да*          | Default locale code                                |
| `app.locale.available` | list[string] | да*          | Allowlisted locale codes                           |
| `app.theme`            | dict         | да           | Controlled theme settings                          |
| `app.layout`           | dict         | да           | Controlled layout settings                         |

`*` — обязательно, если задан `app.locale`.

### Theme fields

| Ключ                | Тип    | Обязательный | Значения                                                                                      |
| ------------------- | ------ | ------------ | --------------------------------------------------------------------------------------------- |
| `app.theme.mode`    | string | да           | `light`, `dark`, `auto`                                                                       |
| `app.theme.primary` | string | да           | `blue`, `azure`, `cyan`, `teal`, `green`, `lime`, `yellow`, `orange`, `red`, `pink`, `indigo` |
| `app.theme.base`    | string | да           | `slate`, `gray`, `zinc`, `neutral`, `stone`                                                   |
| `app.theme.font`    | string | да           | `sans-serif`, `serif`, `monospace`                                                            |
| `app.theme.radius`  | int    | да           | `0`, `1`, `2`                                                                                 |
| `app.theme.density` | string | да           | `default`, `compact`, `comfortable`                                                           |

### Layout fields

| Ключ                           | Тип    | Обязательный | Значения          |
| ------------------------------ | ------ | ------------ | ----------------- |
| `app.layout.type`              | string | да           | `vertical`        |
| `app.layout.container`         | string | да           | `xl`, `fluid`     |
| `app.layout.sidebar.variant`   | string | да           | `default`, `dark` |
| `app.layout.sidebar.collapsed` | bool   | да           | true/false        |
| `app.layout.navbar.enabled`    | bool   | да           | true/false        |
| `app.layout.navbar.variant`    | string | да           | `default`, `dark` |
| `app.layout.navbar.sticky`     | bool   | да           | true/false        |

### Правила

- Theme values must be allowlisted.
- `theme.mode: auto` is a controlled schema token for future runtime/browser preference integration. In the current implementation it renders as `data-bs-theme="auto"` and `beeui-theme-mode-auto`; it does not persist or mutate theme client-side.
- Если `app.locale` отсутствует, используется default `en`.
- `app.locale.default` должен входить в `app.locale.available`.
- `?lang=` применяется только если значение есть в `app.locale.available`.
- Invalid `?lang` делает fallback к `default`.
- BeeUI не переводит product-specific строки.
- Нельзя принимать arbitrary CSS из config.
- Layout values must be allowlisted.
- Font key должен ссылаться на known safe font mode.
- Local/static fonts не должны коммититься без проверки лицензии.

## `navigation[]`

```yaml
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
```

### Поля

| Ключ       | Тип    | Обязательный | Описание                        |
| ---------- | ------ | ------------ | ------------------------------- |
| `title`    | string | да           | Текст пункта                    |
| `path`     | string | да/нет       | Required for enabled leaf items |
| `icon`     | string | нет          | Icon key                        |
| `disabled` | bool   | нет          | Disabled leaf item without link |
| `children` | list   | нет          | Grouped nested nav items        |

### Правила

- `path` должен начинаться с `/`.
- `path` должен соответствовать существующей page или registered route.
- External nav links (`http://`, `https://`, `//`, `mailto:`, `javascript:`) rejected by default.
- Duplicate paths запрещены.
- Grouped navigation uses `children`.
- Group items omit `path`.
- Disabled leaf items may omit `path` and render without a link.

## `data_sources.*`

Текущий contract после Iteration 13.1.

```yaml
data_sources:
  demo_dashboard:
    type: demo

  static_dashboard:
    type: static
    format: yaml
    path: tests/fixtures/demo_static/dashboard.yml
```

### Supported source types

| Type      | Назначение                                | MVP |
| --------- | ----------------------------------------- | --- |
| `demo`    | Controlled built-in demo payload          | да  |
| `static`  | Controlled YAML/JSON fixture-like payload | да  |
| `adapter` | Product adapter method                    | нет |

### Demo source

```yaml
data_sources:
  demo_dashboard:
    type: demo
```

### Static source

```yaml
data_sources:
  static_dashboard:
    type: static
    format: json
    path: tests/fixtures/demo_static/dashboard.json
```

### Resolver envelope

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

### Правила

- `data_sources` lives in `config/schema.yml` because it configures BeeUI-owned read-only UI data wiring for the current demo/MVP surface.
- `data_sources` is not a second source of truth: product truth still belongs to product config/artifacts/API, while BeeUI only reads controlled demo/static payloads in Iteration 7.
- `type: demo` has no extra keys.
- `type: static` requires `format` (`yaml` or `json`) and a safe relative `path`.
- Текущий runtime Iteration 13.1 не поддерживает `data_sources.type: adapter` в `schema.yml`.
- Static source paths must stay under the BeeUI project root and may not use absolute paths or `..`.
- Source results are normalized to a stable envelope with `status`, `data`, `warnings` and `source`.
- Missing selectors return `partial` and should degrade block rendering instead of crashing the page.
- Invalid selectors and invalid sources return explicit `error` envelopes.

## `pages[]`

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks: []
```

### Поля

| Ключ       | Тип    | Обязательный | Описание                                 |
| ---------- | ------ | ------------ | ---------------------------------------- |
| `id`       | string | да           | Page ID                                  |
| `path`     | string | да           | Route                                    |
| `title`    | string | да           | Page title                               |
| `subtitle` | string | нет          | Page subtitle                            |
| `blocks`   | list   | да           | Block placement list: `{block, width|span|size}` или `{id, enabled?}` |

### Правила

- `id` должен быть safe slug.
- `path` должен начинаться с `/`.
- Duplicate page ids/paths запрещены.
- `blocks` must be a list.
- `{block, width}` / `{block, span}` / `{block, size}` ссылаются на top-level block id.
- `{id, enabled?}` — product-side page block reference.
- `width` и `span` должны быть integer `1..12`.
- `size` должен быть `S|M|L|XL`.
- Нельзя смешивать `width`, `span`, `size` в одном placement.
- Schema invalid placement fail-fast.

## `blocks.*`

```yaml
blocks:
  total_profit:
    type: metric_card
    title: Total Profit
    source: demo_dashboard
    value_selector: dashboard.kpis.total_runs
    suffix: USDT
    subtitle: Demo-backed metric
```

### Common block fields

Текущий contract поддерживает и существующие literal fields, и optional resolver-backed fields:

- `source` is optional and references `data_sources.*`;
- selector fields are optional and block-type-specific;
- existing literal fields remain supported for backward compatibility;
- arbitrary keys like `html`, `script`, `javascript`, `style`, `css`, `custom_css`, `custom_js` are rejected fail-fast;
- `links_card.links[].href` allows only safe internal paths.

| Ключ     | Тип    | Обязательный | Описание                                  |
| -------- | ------ | ------------ | ----------------------------------------- |
| `type`   | string | да           | Block type                                |
| `title`  | string | да           | Block title                               |
| `state`  | string | нет          | `normal`, `empty`, `degraded`, `error`    |
| `source` | string | нет          | Data source id for resolver-backed fields |

### Resolver-backed field examples

- `metric_card`: `value_selector`, `subtitle_selector`
- `status_card`: `status_selector`, `value_selector`, `subtitle_selector`
- `text_card`: `text_selector`
- `table_card`: `rows_selector`
- `kpi_grid`: `items_selector`

### MVP block types

| Type            | Назначение                  |
| --------------- | --------------------------- |
| `metric_card`   | Один KPI/value              |
| `kpi_grid`      | Несколько label/value полей |
| `status_card`   | Status + badge              |
| `table_card`    | Таблица                     |
| `links_card`    | Список ссылок               |
| `alert_card`    | Alert with severity         |
| `text_card`     | Plain escaped text          |
| `progress_card` | Progress 0..100             |

## `metric_card`

```yaml
blocks:
  total_profit:
    type: metric_card
    title: Total Profit
    source: dashboard
    value: profit.total
    suffix: USDT
    empty: Profit unavailable
    note: profit.note
```

### Fields

| Ключ     | Тип    | Обязательный | Описание                 |
| -------- | ------ | ------------ | ------------------------ |
| `value`  | string | да           | Selector                 |
| `suffix` | string | нет          | Unit                     |
| `href`   | string | нет          | Selector или literal URL |
| `empty`  | string | нет          | Empty state              |

## `kpi_grid`

```yaml
blocks:
  system_snapshot:
    type: kpi_grid
    title: System Snapshot
    source: dashboard
    fields:
      - label: Latest run
        value: system.latest_run_id
        href: system.latest_run_url
      - label: Runtime
        value: system.runtime_status
        badge: system.runtime_badge
```

### Fields

| Ключ             | Тип    | Обязательный | Описание             |
| ---------------- | ------ | ------------ | -------------------- |
| `fields[]`       | list   | да           | KPI field list       |
| `fields[].label` | string | да           | Label                |
| `fields[].value` | string | да           | Selector             |
| `fields[].href`  | string | нет          | Selector/literal URL |
| `fields[].badge` | string | нет          | Badge selector       |

## `status_card`

```yaml
blocks:
  runtime_status:
    type: status_card
    title: Runtime Status
    source: dashboard
    value: runtime.status
    badge: runtime.badge
    note: runtime.note
```

### Badge values

MVP badge classes should be mapped internally:

| Badge key   | Meaning       |
| ----------- | ------------- |
| `success`   | ok/healthy    |
| `warning`   | degraded      |
| `danger`    | failed        |
| `secondary` | unknown/empty |

Config не должен принимать arbitrary CSS class.

## `table_card`

```yaml
blocks:
  recent_runs:
    type: table_card
    title: Recent Runs
    source: runs
    rows: items
    columns:
      - key: run_id
        label: Run ID
        href_template: /runs/{run_id}
      - key: mode
        label: Mode
      - key: venue
        label: Venue
      - key: status
        label: Status
```

### Fields

| Ключ                      | Тип    | Обязательный | Описание          |
| ------------------------- | ------ | ------------ | ----------------- |
| `rows`                    | string | да           | Selector to list  |
| `columns[]`               | list   | да           | Columns           |
| `columns[].key`           | string | да           | Row key           |
| `columns[].label`         | string | да           | Column label      |
| `columns[].href_template` | string | нет          | Safe URL template |

### Правила

- `rows` должен указывать на list.
- Missing column value renders empty.
- `href_template` должен использовать only row fields.
- HTML escaping обязательный.

## `links_card`

```yaml
blocks:
  diagnostics:
    type: links_card
    title: Diagnostics
    source: dashboard
    links: diagnostics.links
```

Expected data:

```json
{
  "diagnostics": {
    "links": [
      { "label": "Run detail", "href": "/runs/run_001" },
      { "label": "Artifacts", "href": "/runs/run_001/artifacts" }
    ]
  }
}
```

### Правила

- Links должны быть internal или allowlisted.
- External links should be marked explicitly.
- `javascript:` URLs запрещены.

## `artifact_table`

```yaml
blocks:
  run_artifacts:
    type: artifact_table
    title: Artifacts
    source: artifacts
    rows: items
```

Expected data:

```json
{
  "items": [
    {
      "artifact_id": "run_json",
      "label": "run.json",
      "kind": "json",
      "href": "/api/runs/run_001/artifacts/run_json"
    }
  ]
}
```

### Правила

- Artifact access only by safe `artifact_id`.
- No arbitrary path from browser.
- Product adapter owns artifact allowlist.

# 3. Product adapter config examples

Примеры ниже являются целевыми/future examples. Текущий Iteration 13.1 runtime не поддерживает `data_sources.type: adapter` в `schema.yml`; product console сейчас получает данные через injected `ProductUiAdapter`, а не через schema data source adapter.

## BeeCap embedded example

`config/settings.yml`:

```yaml
app:
  name: beeui
  environment: local

web:
  host: 127.0.0.1
  port: 8780
  open_browser: true
  route_prefix: ""
  cache_static: 3600

logging:
  level: INFO
  utc: true
  clear_logs: false
  file: logs/app.log

storage:
  enabled: true
  root: storage

security:
  html_autoescape: true
  assets_ext: false

auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false

product:
  mode: embedded
  id: beecap
  title: BeeCap
  adapter: beecap
  config_path: config/beeui.yml

http_adapter:
  enabled: false
  base_url: ""
  timeout_seconds: 5
  headers: {}

features:
  browser_artifact: false
  config_preview: false
  config_apply: false
  operator_actions: false
  api: false
```

`config/beeui.yml`:

```yaml
app:
  title: BeeCap
  product: beecap
  logo_text: BeeCap
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
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Dry-run
    path: /dry-run
    icon: activity
  - title: Paper
    path: /paper
    icon: wallet
  - title: Live
    path: /live
    icon: pulse
  - title: Runs
    path: /runs
    icon: list
  - title: Artifacts
    path: /artifacts
    icon: files

data_sources:
  dashboard:
    type: adapter
    method: get_dashboard
  runs:
    type: adapter
    method: list_runs

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: BeeCap operator dashboard
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
      - row:
          - block: venue_state
            width: 6
          - block: attention_items
            width: 6
      - row:
          - block: recent_runs
            width: 12

  - id: runs
    path: /runs
    title: Runs
    subtitle: Recent BeeCap runs
    layout:
      - row:
          - block: recent_runs
            width: 12

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: dashboard
    value: system.latest_run_id
    href: system.latest_run_url
    empty: No runs yet

  runtime_status:
    type: status_card
    title: Runtime
    source: dashboard
    value: system.runtime_status
    badge: system.runtime_badge

  active_orders:
    type: metric_card
    title: Active Orders
    source: dashboard
    value: trading.active_orders
    empty: "0"

  total_profit:
    type: metric_card
    title: Total Profit
    source: dashboard
    value: trading.total_profit
    suffix: TON
    empty: Profit unavailable

  venue_state:
    type: kpi_grid
    title: Venue State
    source: dashboard
    fields:
      - label: Venue
        value: venue.name
      - label: Mode
        value: venue.mode
      - label: Rollout
        value: venue.rollout_status
        badge: venue.rollout_badge
      - label: Auth
        value: venue.auth_status
        badge: venue.auth_badge

  attention_items:
    type: table_card
    title: Attention Items
    source: dashboard
    rows: attention.items
    columns:
      - key: severity
        label: Severity
      - key: message
        label: Message
      - key: source
        label: Source

  recent_runs:
    type: table_card
    title: Recent Runs
    source: runs
    rows: items
    columns:
      - key: run_id
        label: Run ID
        href_template: /runs/{run_id}
      - key: mode
        label: Mode
      - key: venue
        label: Venue
      - key: status
        label: Status
```

## BeeAgent embedded example

`config/settings.yml`:

```yaml
app:
  name: beeui
  environment: local

web:
  host: 127.0.0.1
  port: 8781
  open_browser: true
  route_prefix: ""
  cache_static: 3600

logging:
  level: INFO
  utc: true
  clear_logs: false
  file: logs/app.log

storage:
  enabled: true
  root: storage

security:
  html_autoescape: true
  assets_ext: false

auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false

product:
  mode: embedded
  id: beeagent
  title: BeeAgent
  adapter: beeagent
  config_path: config/beeui.yml

http_adapter:
  enabled: false
  base_url: ""
  timeout_seconds: 5
  headers: {}

features:
  browser_artifact: false
  config_preview: false
  config_apply: false
  operator_actions: false
  api: false
```

`config/beeui.yml`:

```yaml
app:
  title: BeeAgent
  product: beeagent
  logo_text: BeeAgent
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
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Modules
    path: /modules
    icon: grid
  - title: Runs
    path: /runs
    icon: list
  - title: Artifacts
    path: /artifacts
    icon: files
  - title: Capabilities
    path: /capabilities
    icon: shield
  - title: Approvals
    path: /approvals
    icon: check

data_sources:
  dashboard:
    type: adapter
    method: get_dashboard
  modules:
    type: adapter
    method: list_modules
  runs:
    type: adapter
    method: list_runs
  capabilities:
    type: adapter
    method: list_capabilities

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: BeeAgent operator dashboard
    layout:
      - row:
          - block: active_modules
            width: 3
          - block: latest_run
            width: 3
          - block: pending_approvals
            width: 3
          - block: capability_status
            width: 3
      - row:
          - block: module_summary
            width: 6
          - block: recent_runs
            width: 6

blocks:
  active_modules:
    type: metric_card
    title: Active Modules
    source: dashboard
    value: modules.active_count

  latest_run:
    type: metric_card
    title: Latest Run
    source: dashboard
    value: runs.latest_run_id
    href: runs.latest_run_url
    empty: No runs yet

  pending_approvals:
    type: metric_card
    title: Pending Approvals
    source: dashboard
    value: approvals.pending_count
    empty: "0"

  capability_status:
    type: status_card
    title: Capability Status
    source: dashboard
    value: capabilities.status
    badge: capabilities.badge

  module_summary:
    type: table_card
    title: Modules
    source: modules
    rows: items
    columns:
      - key: module_id
        label: Module
      - key: status
        label: Status
      - key: last_run_id
        label: Last Run

  recent_runs:
    type: table_card
    title: Recent Runs
    source: runs
    rows: items
    columns:
      - key: run_id
        label: Run ID
        href_template: /runs/{run_id}
      - key: module
        label: Module
      - key: status
        label: Status
```

# 4. `.env`

## Назначение

`.env` хранит secrets/runtime env values.

Файл `.env` не коммитится.

Пример должен быть в:

```text
.env.example
```

## MVP `.env.example`

```dotenv
# BeeUI session secret.
# Required only when auth.enabled=true.
BEEUI_SESSION_SECRET=change_me

# Optional future HTTP adapter token.
# Do not put tokens directly into YAML.
BEEUI_HTTP_TOKEN=
```

## Правила

- Secrets не хранятся в `settings.yml` или `beeui.yml`.
- Secrets не попадают в HTML/API/logs/artifacts.
- При `auth.enabled=true` `BEEUI_SESSION_SECRET` обязателен.
- При `product.mode=http` future auth headers должны ссылаться на env, а не хранить raw token в YAML.

# 5. Validation rules

## Fail-fast validation

Текущая fail-fast validation после Iteration 13.1:

- `settings.yml` отсутствует;
- `settings.yml` не YAML dict;
- обязательные секции отсутствуют;
- `web.port` вне диапазона;
- `security.html_autoescape=false`;
- `features.config_apply=true`, но `features.config_preview=false`;
- `auth.enabled=true`, но отсутствует `session_secret`, `operator_token` или `admin_token`;
- `schema.yml` отсутствует;
- `schema.yml` не YAML dict;
- invalid app/theme/layout/navigation/page fields;
- invalid `app.locale`;
- duplicate page ids/paths;
- duplicate nav paths;
- external nav links rejected;
- reserved paths rejected;
- `pages[].blocks` must be a list;
- invalid `pages[].blocks[].span`;
- invalid `pages[].blocks[].size`;
- mixed sizing keys в одном placement rejected.

Future/product-side validation примеры:

- `config/beeui.yml` as product integration schema;
- unknown block references;
- layout row width sum > 12;
- block type unknown;
- data source type unknown;
- adapter method не allowlisted.

## Graceful/degraded behavior

`beeui` не должен падать целиком, если:

- product adapter вернул partial data;
- product backend недоступен в HTTP mode;
- artifact missing;
- artifact corrupted;
- JSONL row malformed;
- optional block data unavailable;
- adapter-backed `layout[]` содержит malformed sizing.

В этих случаях UI должен показывать:

- empty state;
- degraded state;
- warnings;
- source artifact link, если доступен.

Для adapter-backed `layout[]` malformed sizing должен degrade to `col-12`, а не вызывать fail-fast ошибку на всю страницу.

# 6. Security rules

## HTML/API

- Jinja2 autoescape должен быть включён.
- Любой user/product-provided текст escaped.
- `javascript:` URLs запрещены.
- Arbitrary HTML из config запрещён.
- Arbitrary CSS из config запрещён.
- External scripts/styles запрещены по умолчанию.
- Demo tracking scripts не допускаются.

## File/path access

- Browser/API не передаёт raw filesystem paths.
- Доступ к artifacts только через safe `artifact_id`.
- Product adapter owns allowlist.
- Path traversal blocked:
  - `..`;
  - absolute paths;
  - symlink escape;
  - encoded traversal.

## Secrets

Secrets не должны попадать в:

- HTML;
- JSON API;
- logs;
- audit artifacts;
- config read-model;
- error tracebacks.

Ключи, содержащие следующие substrings, считаются sensitive/redacted:

```text
secret
token
password
api_key
api_secret
authorization
cookie
session
private_key
```

## Write/control features

Любой write/control feature должен иметь:

- explicit feature flag;
- auth/role check, если auth enabled;
- CSRF protection for browser POST;
- product validation callback;
- audit artifact;
- explicit rejection reasons;
- no hidden fallback;
- no direct broker/runtime authority in BeeUI.

# 7. Integration rules

## Embedded mode

Bee-продукт подключает BeeUI как dependency:

```toml
dependencies = [
    "beeui @ file:///home/bee/Projects/beeui"
]
```

В продукте создаётся adapter:

```python
from beeui_module.web.app import create_beeui_app
from product_module.interfaces.ui.adapter import ProductUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=ProductUiAdapter(...),
    config_path="config/beeui.yml",
)
```

## Product responsibilities

Product adapter обязан реализовать:

- dashboard read-model;
- runs list;
- run detail;
- artifact allowlist;
- safe artifact read;
- config validation callback, если включён config preview/apply;
- bounded action callback, если включены operator actions.

## BeeUI responsibilities

BeeUI обязан:

- рендерить UI;
- валидировать UI schema;
- защищать paths;
- redacted sensitive fields;
- не мутировать product state без explicit product callback;
- не исполнять domain logic.

# 8. MVP defaults

Для быстрого MVP рекомендуется:

`config/settings.yml`:

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
  level: INFO
  utc: true
  clear_logs: false
  file: logs/app.log

storage:
  enabled: true
  root: storage

security:
  html_autoescape: true
  assets_ext: false

auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false

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

`config/schema.yml`:

```yaml
app:
  title: BeeUI Demo
  product: demo
  logo_text: BeeUI
  locale:
    default: en
    available:
      - en
      - ru
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

# 9. Checks

Минимальные проверки для config changes:

```bash
uv run pytest -q
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Проверить вручную:

- `/` renders;
- `/runs` renders;
- invalid config fails fast;
- missing source gives empty/degraded state;
- secrets are redacted;
- no external scripts are loaded;
- no product artifacts are mutated.

# 10. Версионирование config contract

Config contract должен версионироваться через docs и changelog.

При изменении schema нужно обновить:

- `docs/CONFIG.md`;
- `docs/API_CONTRACT.md`, если меняются API envelopes/routes;
- `docs/WEB_UI.md`, если меняются routes/pages;
- `docs/COMPONENTS.md`, если меняются block types;
- `README.ru.md`, если меняется запуск/MVP behavior.

breaking changes требуют отдельной итерации или явного раздела в PR.
