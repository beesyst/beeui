# CONFIG — BeeUI configuration

## Принцип

`beeui` использует два разных уровня конфигурации:

1. `config/settings.yml` — runtime-настройки самого `beeui`:
   - web host/port;
   - logging;
   - storage;
   - auth;
   - security;
   - product adapter mode.

2. `config/beeui.yml` — declarative UI schema:
   - название приложения;
   - theme;
   - navigation;
   - pages;
   - blocks;
   - data sources.

Главное правило:

```text
settings.yml отвечает за запуск и безопасность.
beeui.yml отвечает за внешний вид, страницы и блоки.
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

Целевая структура:

```text
beeui/
  config/
    settings.yml
    beeui.yml
    demo.beeui.yml
```

Для demo/MVP допускается:

```text
config/demo.beeui.yml
```

Но для реального подключения к `beecap` / `beeagent` лучше использовать:

```text
config/settings.yml
config/beeui.yml
```


# 1. `config/settings.yml`

## Назначение

`settings.yml` управляет запуском `beeui` как приложения.

Он не должен описывать торговые стратегии, MRKT lifecycle, BeeAgent modules или product-specific business logic.

## Минимальный пример `settings.yml` v0

```yaml
app:
  name: beeui
  environment: local # local | dev | prod

web:
  host: 127.0.0.1
  port: 8780
  open_browser: false
  route_prefix: ""
  static_cache_seconds: 3600

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
  allow_external_assets: false
  allowed_static_roots:
    - src/beeui_module/static

auth:
  enabled: false
  session:
    cookie_name: beeui_session
    secret_env: BEEUI_SESSION_SECRET
    secure_cookie: false
    same_site: lax
  users:
    source: local_file
    file: config/users.yml

product:
  mode: demo # demo | embedded | http
  id: demo
  title: BeeUI Demo
  adapter: static # static | beecap | beeagent | http
  config_path: config/beeui.yml

http_adapter:
  enabled: false
  base_url: ""
  timeout_seconds: 5
  headers: {}

features:
  artifact_browser: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: true
```


## Используемые секции `settings.yml`

| Секция           | Назначение                                                             |
| ---------------- | ---------------------------------------------------------------------- |
| `app.*`          | Идентичность runtime-приложения `beeui`                                |
| `web.*`          | Host, port, route prefix, browser open behavior                        |
| `logging.*`      | Логи `beeui`                                                           |
| `storage.*`      | Локальный storage для audit/config/action artifacts, если они включены |
| `security.*`     | Базовые security defaults                                              |
| `auth.*`         | Local auth/session settings                                            |
| `product.*`      | Какой product adapter используется                                     |
| `http_adapter.*` | Настройки standalone HTTP adapter                                      |
| `features.*`     | Feature flags для UI capabilities                                      |


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
  - `auth.session.secure_cookie=true`;
  - `security.allow_external_assets=false`.


## `web.*`

```yaml
web:
  host: 127.0.0.1
  port: 8780
  open_browser: false
  route_prefix: ""
  static_cache_seconds: 3600
```

### Поля

| Ключ                       | Тип    | Обязательный | Описание                         |
| -------------------------- | ------ | ------------ | -------------------------------- |
| `web.host`                 | string | да           | Host для uvicorn/FastAPI         |
| `web.port`                 | int    | да           | Port                             |
| `web.open_browser`         | bool   | да           | Открывать браузер при запуске    |
| `web.route_prefix`         | string | да           | Prefix для embedded/mounted mode |
| `web.static_cache_seconds` | int    | да           | Cache для static assets          |

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
  allow_external_assets: false
  allowed_static_roots:
    - src/beeui_module/static
```

### Поля

| Ключ                             | Тип          | Обязательный | Описание                      |
| -------------------------------- | ------------ | ------------ | ----------------------------- |
| `security.html_autoescape`       | bool         | да           | Jinja2 autoescape             |
| `security.allow_external_assets` | bool         | да           | Разрешить CDN/external JS/CSS |
| `security.allowed_static_roots`  | list[string] | да           | Разрешённые static roots      |

### Правила

- `security.html_autoescape` должен быть `true`.
- `security.allow_external_assets=false` по умолчанию.
- Production не должен зависеть от CDN.
- Tabler assets должны быть vendored/local.
- Нельзя копировать demo tracking scripts из external templates.
- Static roots должны быть path-safe.


## `auth.*`

```yaml
auth:
  enabled: false
  session:
    cookie_name: beeui_session
    secret_env: BEEUI_SESSION_SECRET
    secure_cookie: false
    same_site: lax
  users:
    source: local_file
    file: config/users.yml
```

### Назначение

Auth нужен для internal operator/admin UI.

В MVP auth может быть выключен для local/dev, но архитектурно должен быть предусмотрен.

### Поля

| Ключ                         | Тип    | Обязательный | Описание                        |
| ---------------------------- | ------ | ------------ | ------------------------------- |
| `auth.enabled`               | bool   | да           | Включить auth                   |
| `auth.session.cookie_name`   | string | да           | Имя cookie                      |
| `auth.session.secret_env`    | string | да           | Env-переменная с session secret |
| `auth.session.secure_cookie` | bool   | да           | Secure cookie flag              |
| `auth.session.same_site`     | string | да           | `lax`, `strict`, `none`         |
| `auth.users.source`          | string | да           | Источник users                  |
| `auth.users.file`            | string | да           | Файл users для local auth       |

### Правила

- При `auth.enabled=true` env из `auth.session.secret_env` обязателен.
- Пароли нельзя хранить plaintext.
- Write routes требуют role + CSRF.
- В `prod` auth должен быть включён.
- `secure_cookie=true` обязателен для HTTPS/prod.


## `product.*`

```yaml
product:
  mode: demo
  id: demo
  title: BeeUI Demo
  adapter: static
  config_path: config/beeui.yml
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

| Ключ                  | Тип    | Обязательный | Описание                   |
| --------------------- | ------ | ------------ | -------------------------- |
| `product.mode`        | string | да           | `demo`, `embedded`, `http` |
| `product.id`          | string | да           | Product id                 |
| `product.title`       | string | да           | Display title              |
| `product.adapter`     | string | да           | Adapter name               |
| `product.config_path` | string | да           | Путь к `beeui.yml`         |

### Правила

- `product.id` должен быть safe slug: `[a-zA-Z0-9_-]`.
- `product.config_path` не должен выходить за root проекта.
- `product.mode=http` требует `http_adapter.enabled=true`.
- `product.mode=embedded` требует adapter injection из host product.
- `beeui` не должен сам угадывать product internals без adapter.


## `http_adapter.*`

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
  artifact_browser: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: true
```

### Поля

| Ключ                        | Тип  | Обязательный | Описание                          |
| --------------------------- | ---- | ------------ | --------------------------------- |
| `features.artifact_browser` | bool | да           | Включить artifact browser         |
| `features.config_preview`   | bool | да           | Включить config preview           |
| `features.config_apply`     | bool | да           | Включить bounded config apply     |
| `features.operator_actions` | bool | да           | Включить bounded operator actions |
| `features.api`              | bool | да           | Включить JSON API routes          |

### Правила

- `config_apply=true` требует `config_preview=true`.
- `operator_actions=true` требует product action callback.
- `auth.enabled=true` рекомендуется для любых write/control features.
- В MVP:
  - `artifact_browser=true`;
  - `api=true`;
  - `config_preview=false`;
  - `config_apply=false`;
  - `operator_actions=false`.


# 2. `config/beeui.yml`

## Назначение

`beeui.yml` описывает UI:

- app display metadata;
- theme;
- navigation;
- pages;
- blocks;
- data sources.

Он не должен содержать secrets и product runtime logic.

## Минимальный пример `beeui.yml` v0

```yaml
app:
  title: BeeUI Demo
  product: demo
  version_label: MVP
  theme:
    mode: dark
    primary: blue
    font: system
    radius: 2
    density: comfortable

navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list
  - title: Artifacts
    path: /artifacts
    icon: files

data_sources:
  demo:
    type: static
    data:
      latest_run:
        value: run_demo_001
        href: /runs/run_demo_001
      runtime_status:
        value: ok
        badge: success
      active_orders:
        value: 0
      total_profit:
        value: null
        note: Profit unavailable in demo mode
      runs:
        - run_id: run_demo_001
          mode: demo
          venue: demo
          status: ok

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
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
          - block: recent_runs
            width: 12

  - id: runs
    path: /runs
    title: Runs
    subtitle: Recent runs
    layout:
      - row:
          - block: recent_runs
            width: 12

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: demo
    value: latest_run.value
    href: latest_run.href

  runtime_status:
    type: status_card
    title: Runtime Status
    source: demo
    value: runtime_status.value
    badge: runtime_status.badge

  active_orders:
    type: metric_card
    title: Active Orders
    source: demo
    value: active_orders.value

  total_profit:
    type: metric_card
    title: Total Profit
    source: demo
    value: total_profit.value
    empty: Profit unavailable
    note: total_profit.note

  recent_runs:
    type: table_card
    title: Recent Runs
    source: demo
    rows: runs
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


## Используемые секции `beeui.yml`

| Секция           | Назначение                     |
| ---------------- | ------------------------------ |
| `app.*`          | Display metadata and theme     |
| `navigation[]`   | Sidebar/global navigation      |
| `data_sources.*` | Откуда брать данные для blocks |
| `pages[]`        | Pages/routes/layout            |
| `blocks.*`       | Reusable UI blocks             |


## `app.*`

```yaml
app:
  title: BeeUI Demo
  product: demo
  version_label: MVP
  theme:
    mode: dark
    primary: blue
    font: system
    radius: 2
    density: comfortable
```

### Поля

| Ключ                | Тип    | Обязательный | Описание               |
| ------------------- | ------ | ------------ | ---------------------- |
| `app.title`         | string | да           | Display title          |
| `app.product`       | string | да           | Product key            |
| `app.version_label` | string | нет          | UI version/build label |
| `app.theme`         | dict   | да           | Theme settings         |

### Theme fields

| Ключ                | Тип    | Обязательный | Значения                                         |
| ------------------- | ------ | ------------ | ------------------------------------------------ |
| `app.theme.mode`    | string | да           | `light`, `dark`, `auto`                          |
| `app.theme.primary` | string | да           | `blue`, `green`, `red`, `orange`, `purple`, etc. |
| `app.theme.font`    | string | да           | `system`, `inter`, custom safe key               |
| `app.theme.radius`  | int    | да           | `0..4`                                           |
| `app.theme.density` | string | да           | `compact`, `comfortable`, `spacious`             |

### Правила

- Theme values must be allowlisted.
- Нельзя принимать arbitrary CSS из config.
- Font key должен ссылаться на known safe font mode.
- Local/static fonts не должны коммититься без проверки лицензии.


## `navigation[]`

```yaml
navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list
```

### Поля

| Ключ       | Тип    | Обязательный | Описание         |
| ---------- | ------ | ------------ | ---------------- |
| `title`    | string | да           | Текст пункта     |
| `path`     | string | да           | Route            |
| `icon`     | string | нет          | Icon key         |
| `children` | list   | нет          | Nested nav items |

### Правила

- `path` должен начинаться с `/`.
- `path` должен соответствовать существующей page или registered route.
- Duplicate paths запрещены.
- Nested navigation допускается, но MVP может поддерживать только 1 уровень.


## `data_sources.*`

```yaml
data_sources:
  demo:
    type: static
    data: {}

  dashboard:
    type: adapter
    method: get_dashboard

  runs:
    type: adapter
    method: list_runs

  external:
    type: http
    url: http://127.0.0.1:8765/api/ui/dashboard
    timeout_seconds: 5
```

### Supported source types

| Type      | Назначение             | MVP                |
| --------- | ---------------------- | ------------------ |
| `static`  | Inline/demo data       | да                 |
| `adapter` | Product adapter method | да                 |
| `http`    | HTTP JSON source       | позже/MVP optional |
| `file`    | Safe local JSON file   | optional           |

### Static source

```yaml
data_sources:
  demo:
    type: static
    data:
      status: ok
```

### Adapter source

```yaml
data_sources:
  dashboard:
    type: adapter
    method: get_dashboard
```

### HTTP source

```yaml
data_sources:
  dashboard:
    type: http
    url: http://127.0.0.1:8765/api/ui/dashboard
    timeout_seconds: 5
```

### Правила

- `static.data` должен быть dict/list/scalar JSON-compatible.
- `adapter.method` должен быть allowlisted.
- `http.url` не должен содержать secrets.
- HTTP errors должны давать degraded/partial state.
- Source result нормализуется в envelope:
  - `status`;
  - `data`;
  - `warnings`;
  - `source`.


## `pages[]`

```yaml
pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    layout:
      - row:
          - block: latest_run
            width: 3
          - block: runtime_status
            width: 3
```

### Поля

| Ключ       | Тип    | Обязательный | Описание           |
| ---------- | ------ | ------------ | ------------------ |
| `id`       | string | да           | Page ID            |
| `path`     | string | да           | Route              |
| `title`    | string | да           | Page title         |
| `subtitle` | string | нет          | Page subtitle      |
| `layout`   | list   | да           | Rows/blocks layout |

### Layout row

```yaml
layout:
  - row:
      - block: latest_run
        width: 3
      - block: runtime_status
        width: 3
```

### Правила

- `id` должен быть safe slug.
- `path` должен начинаться с `/`.
- Duplicate page ids/paths запрещены.
- `width` должен быть `1..12`.
- Сумма widths в row не должна превышать `12`.
- Unknown block reference должен fail fast.


## `blocks.*`

```yaml
blocks:
  total_profit:
    type: metric_card
    title: Total Profit
    source: dashboard
    value: profit.total
    suffix: USDT
    empty: Profit unavailable
```

### Common block fields

| Ключ     | Тип    | Обязательный | Описание                                |
| -------- | ------ | ------------ | --------------------------------------- |
| `type`   | string | да           | Block type                              |
| `title`  | string | да           | Block title                             |
| `source` | string | нет          | Data source key                         |
| `empty`  | string | нет          | Empty state text                        |
| `note`   | string | нет          | Note/subtitle selector or literal       |
| `class`  | string | нет          | Safe style class key, not arbitrary CSS |

### MVP block types

| Type             | Назначение                           |
| ---------------- | ------------------------------------ |
| `metric_card`    | Один KPI/value                       |
| `kpi_grid`       | Несколько label/value полей          |
| `status_card`    | Status + badge                       |
| `table_card`     | Таблица                              |
| `links_card`     | Список ссылок                        |
| `artifact_table` | Artifact list                        |
| `json_viewer`    | Safe JSON preview                    |
| `chart_card`     | Chart placeholder / later ApexCharts |


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
  static_cache_seconds: 3600

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
  allow_external_assets: false
  allowed_static_roots:
    - src/beeui_module/static

auth:
  enabled: false
  session:
    cookie_name: beeui_session
    secret_env: BEEUI_SESSION_SECRET
    secure_cookie: false
    same_site: lax
  users:
    source: local_file
    file: config/users.yml

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
  artifact_browser: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: true
```

`config/beeui.yml`:

```yaml
app:
  title: BeeCap
  product: beecap
  version_label: BeeUI MVP
  theme:
    mode: dark
    primary: blue
    font: system
    radius: 2
    density: comfortable

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
  static_cache_seconds: 3600

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
  allow_external_assets: false
  allowed_static_roots:
    - src/beeui_module/static

auth:
  enabled: false
  session:
    cookie_name: beeui_session
    secret_env: BEEUI_SESSION_SECRET
    secure_cookie: false
    same_site: lax
  users:
    source: local_file
    file: config/users.yml

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
  artifact_browser: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: true
```

`config/beeui.yml`:

```yaml
app:
  title: BeeAgent
  product: beeagent
  version_label: BeeUI MVP
  theme:
    mode: dark
    primary: blue
    font: system
    radius: 2
    density: comfortable

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

`beeui` должен падать до запуска web server, если:

- `settings.yml` отсутствует;
- `settings.yml` не YAML dict;
- обязательные секции отсутствуют;
- `web.port` вне диапазона;
- `security.html_autoescape=false`;
- `product.config_path` небезопасен;
- `product.mode=http`, но `http_adapter.enabled=false`;
- `features.config_apply=true`, но `features.config_preview=false`;
- `auth.enabled=true`, но env из `auth.session.secret_env` отсутствует;
- `beeui.yml` отсутствует;
- `beeui.yml` содержит duplicate page paths;
- `beeui.yml` содержит unknown block references;
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
- optional block data unavailable.

В этих случаях UI должен показывать:

- empty state;
- degraded state;
- warnings;
- source artifact link, если доступен.


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
from beeui_module.app import create_beeui_app
from product_module.interfaces.ui.adapter import ProductUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=ProductUiAdapter(...),
    settings_path="config/settings.yml",
    ui_config_path="config/beeui.yml",
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
  static_cache_seconds: 3600

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
  allow_external_assets: false
  allowed_static_roots:
    - src/beeui_module/static

auth:
  enabled: false
  session:
    cookie_name: beeui_session
    secret_env: BEEUI_SESSION_SECRET
    secure_cookie: false
    same_site: lax
  users:
    source: local_file
    file: config/users.yml

product:
  mode: demo
  id: demo
  title: BeeUI Demo
  adapter: static
  config_path: config/beeui.yml

http_adapter:
  enabled: false
  base_url: ""
  timeout_seconds: 5
  headers: {}

features:
  artifact_browser: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: true
```

`config/beeui.yml`:

```yaml
app:
  title: BeeUI Demo
  product: demo
  version_label: MVP
  theme:
    mode: dark
    primary: blue
    font: system
    radius: 2
    density: comfortable

navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list

data_sources:
  demo:
    type: static
    data:
      latest_run:
        value: run_demo_001
        href: /runs/run_demo_001
      runtime_status:
        value: ok
        badge: success
      runs:
        - run_id: run_demo_001
          mode: demo
          venue: demo
          status: ok

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    layout:
      - row:
          - block: latest_run
            width: 4
          - block: runtime_status
            width: 4
      - row:
          - block: recent_runs
            width: 12

  - id: runs
    path: /runs
    title: Runs
    subtitle: Recent runs
    layout:
      - row:
          - block: recent_runs
            width: 12

blocks:
  latest_run:
    type: metric_card
    title: Latest Run
    source: demo
    value: latest_run.value
    href: latest_run.href

  runtime_status:
    type: status_card
    title: Runtime Status
    source: demo
    value: runtime_status.value
    badge: runtime_status.badge

  recent_runs:
    type: table_card
    title: Recent Runs
    source: demo
    rows: runs
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


# 9. Checks

Минимальные проверки для config changes:

```bash
uv run pytest -q
./start.sh doctor
./start.sh serve --config config/beeui.yml --settings config/settings.yml
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
