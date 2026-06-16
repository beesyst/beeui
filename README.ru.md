# BeeUI — переиспользуемый UI-фреймворк для Bee-продуктов

**BeeUI** — общий UI-фреймворк на Python для Bee-продуктов: `beecap`, `beeagent` и будущих модулей экосистемы Bee.

## Iteration 13.5 — Product console route metadata and navigation compatibility

Текущий результат — явное владение page route через `pages[].route.mode`.
BeeUI разделяет:

- `path` — безопасный внутренний URL для navigation, page metadata, tabs и internal links;
- `route.mode` — кто обслуживает этот URL.

Поддерживаются режимы:

- `metadata` — страница используется для navigation, title/subtitle, tabs и page metadata, но BeeUI не регистрирует concrete page route;
- `adapter` — BeeUI регистрирует route и вызывает `adapter.get_page(page_id, query)`;
- `configured` — BeeUI регистрирует route и рендерит schema/config blocks без вызова `adapter.get_page()`.

Пути продукта вроде `/venues/mrkt`, `/venues/binance`, `/modes/live`, `/hidra/binance`,
`/likes/top` являются валидными safe internal paths. BeeUI больше не хардкодит
product namespaces; поведение таких путей задаётся только через `pages[].route.mode`.
BeeUI защищает от shadowing только свои system-owned routes: `/health`, `/api`,
`/api/*`, `/auth`, `/auth/*`, `/static`, `/static/*`, `/components`,
`/components/*`, `/login`, `/logout`.

```yaml
pages:
  - id: mrkt
    path: /venues/mrkt
    route:
      mode: metadata
    title: MRKT
    subtitle: Дашборд площадки MRKT
    blocks: []

  - id: hidra_binance
    path: /hidra/binance
    route:
      mode: adapter
    title: Hidra Binance
    subtitle: Adapter-backed страница
    blocks: []

  - id: likes_top
    path: /likes/top
    route:
      mode: configured
    title: Likes
    subtitle: Configured страница
    blocks:
      - block: latest_run
        width: 12
```

## Iteration 13.4 — Generic layout groups, KPI grid columns, and page spacing normalization

Текущий результат — product-neutral layout group support, KPI grid columns и consistent page-body spacing.

В Iteration 13.4 добавлены:

- consistent page-body spacing для всех render paths (dashboard, runs, custom pages, tabs);
- `kpi_grid.columns` — optional adapter-backed field со значениями `1`, `2`, `3`, `4`, default `4`, invalid adapter values degrade to default `4`;
- generic layout group v1 — adapter-backed `type: group` с `direction: vertical`, `children` как list of layout blocks, bounded recursive children;
- `KPI_GRID_COLUMN_CLASSES` и `resolve_kpi_grid_columns()` helper;
- depth-bounded (3) group rendering через существующий layout renderer;
- `group.html` template с `row row-cards` nested wrapper;
- тесты для flat layout (`6+3+3`, `3+3+3+3`), nested group, KPI columns, degraded states, escaping.

Правила Iteration 13.4:

- `kpi_grid.columns` поддерживается только в adapter-backed `layout[]`;
- `group.direction` сейчас поддерживает только `vertical`;
- missing/invalid `group.direction` нормализуется к `vertical`;
- missing/invalid `group.children` деградирует в `degraded` block, а не в пустую группу;
- group nesting bounded depth = `3`;
- `group` не является schema/demo block type и не является no-code builder.

## Iteration 13 — Auth/session/CSRF boundary for config/action routes MVP

Текущий результат — auth/session/CSRF boundary для config/action POST routes.

В Iteration 13 добавлены:

- auth-disabled local/dev mode;
- auth-enabled token/session mode;
- login/logout HTML и API routes;
- signed session cookie (HMAC + stdlib);
- role model: `viewer`, `operator`, `admin`;
- CSRF token generation and validation;
- fail-fast startup validation when auth enabled but secrets missing;
- protected POST route stubs for:
  - `POST /api/config/preview` (admin + CSRF);
  - `POST /api/config/apply` (admin + CSRF);
  - `POST /api/actions/preview` (operator + CSRF);
  - `POST /api/actions/execute` (operator + CSRF);
- stable API error envelopes for `unauthenticated` (401), `forbidden` (403), `csrf_failed` (403);
- no product callback invocation when auth/CSRF fails;
- no secrets in HTML/API/logs;
- `config/settings.yml` — auth section;
- `auth.cookie_secure` — configurable Secure flag on session cookie (false for local/dev, true for remote);
- security headers baseline: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`;
- `src/beeui_module/auth/` — auth package (models, sessions, csrf, service, dependencies, routes);
- `src/beeui_module/web/templates/login.html` — login form template;
- `tests/test_security.py` — 60+ тестов;
- docs update.

## Iteration 13.1 — Dashboard layout primitives, URL tabs and locale seed

Текущий результат — reusable dashboard layout primitives для customer-friendly product dashboards.

В Iteration 13.1 добавлены:

- block sizing: `width` (1..12), `span` (1..12), `size` (S/M/L/XL);
- schema invalid values fail fast; adapter malformed values degrade to `col-12`;
- URL-driven Tabler tabs (`url_tabs` Jinja macro с `<a>` links и `?tab=` active state);
- locale seed (`app.locale.default` + `app.locale.available`; `?lang=` override при allowlist);
- resolved locale (`locale`) в template context для всех HTML-страниц;
- generic dashboard fallback: raw JSON в collapsible «Technical details», primary UX — summary/KPIs.

## Iteration 13.2 — Generic adapter pages and configurable Tabler primitives

Текущий результат — generic adapter-backed custom pages и configurable Tabler primitives для перехода BeeAgent/BeeCap на схему «BeeUI renders, Product decides».

В Iteration 13.2 добавлены:

- `components.tabs.variant` и `components.accordion.variant` в declarative UI schema;
- fail-fast validation для component variants;
- numeric aliases для variants с нормализацией в canonical string values;
- page-level `pages[].tabs` config:
  - `variant`;
  - `active_param`;
  - `items[]`;
  - safe internal `href`;
  - disabled tabs;
  - duplicate tab id rejection;
- route-prefix-aware tab href rendering;
- `url_tabs` macro с variant classes, explicit `href`, active state, disabled state и `aria-current`;
- `accordion` macro с deterministic ids и Tabler/Bootstrap-compatible markup;
- generic dashboard `Technical details` через BeeUI accordion вместо raw `<details>`;
- optional adapter method `get_page(page_id, query)`;
- generic adapter-backed custom pages через `pages[].route.mode: adapter`;
- adapter custom page payload redaction before HTML rendering;
- malformed custom page payload degraded state;
- reserved route collision protection, включая `/auth` namespace;
- тестовое покрытие config validation, rendering, custom pages, degraded states и security constraints.

## Iteration 13.3 — Tabler attached page tabs and generic accordion visual parity hardening

Текущий результат — Tabler-compatible attached page tabs и generic configurable accordion primitive.

В Iteration 13.3 добавлены:

- page-level tabs attached к общей card/body;
- удалён standalone tabs card перед page blocks;
- `.card.beeui-page-tabs-card` для pages с `pages[].tabs`;
- page header/title/subtitle остаются над attached tabs card;
- pages без `pages[].tabs` продолжают рендериться как раньше, без `.beeui-page-tabs-card`;
- `accordion` primitive рендерит Tabler-compatible toggle;
- chevron / plus / icons рендерятся как inline SVG без external assets;
- accordion variants остаются config-driven;
- `Technical details` является только label/content fallback-блока product dashboard, а не product-specific special-case;
- BeeUI остаётся product-neutral.

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
- configurable component defaults:
  - `components.tabs.variant`;
  - `components.accordion.variant`;
- page-level URL tabs через `pages[].tabs`;
- page-level URL tabs прикрепляются к body общей Tabler card;
- отсутствие standalone tabs card перед page blocks;
- `.beeui-page-tabs-card` для page-level tabs;
- safe internal tab href validation;
- disabled tab fallback;
- route-prefix-aware tab href rendering;
- reusable `accordion` primitive с Tabler-compatible toggle markup;
- варианты accordion управляются через `components.accordion.variant`;
- inline SVG chevron/plus/icons without external assets;
- generic adapter-backed custom pages через optional `adapter.get_page(page_id, query)`;
- redaction adapter-backed custom page payloads before render;
- malformed custom page payload degrades to explicit unavailable/error state;
- reserved route protection for `/auth`;
- embedded API тесты в `tests/test_embedded.py`;
- generic adapter-backed layout[] block renderer с 18 block types и degraded fallback;
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

Поддерживаемые top-level block types:

- `metric_card`;
- `kpi_grid`;
- `status_card`;
- `table_card`;
- `links_card`;
- `alert_card`;
- `text_card`;
- `progress_card`.

Эти blocks объявляются в top-level `blocks` и размещаются через `pages[].blocks[]`.

Поддерживаемые placement formats:

- `{block, width}`;
- `{block, span}`;
- `{block, size}`;
- `{id, enabled?}`.

Правила:

- `width` и `span`: integer `1..12`;
- `size`: `S|M|L|XL`;
- в одном placement нельзя смешивать `width`, `span`, `size`;
- schema invalid values fail-fast;
- `{id, enabled?}` — product-side page block reference и не обязан ссылаться на top-level `blocks`.

#### 2. Adapter-backed `layout[]` blocks

Используются в product console mode, когда product adapter возвращает optional поле `layout`.

Поддерживаемые adapter-backed `layout[]` типы после Iteration 13.4:

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
- `run_table`;
- `group`.

Правила:

- `width`, `span`, `size` поддерживаются;
- malformed или unsupported blocks рендерятся как `degraded`;
- malformed sizing деградирует в `col-12`, не ломая страницу;
- BeeUI не вычисляет product metrics, а только рендерит product-provided layout.

Текущая web surface после Iteration 13.5:

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
- `GET /login`
- `POST /login`
- `POST /logout`
- `GET /auth/csrf`
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
- `GET /<page-path>` для страниц с `route.mode: adapter`
- `GET /<page-path>` для страниц с `route.mode: configured`

При использовании `mount_beeui(parent, path="/ui")` маршруты доступны под `/ui/`:

- `GET /ui/`
- `GET /ui/health`
- `GET /ui/login`
- `POST /ui/login`
- `POST /ui/logout`
- `GET /ui/auth/csrf`
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
- `GET /ui/<page-path>` для страниц с `route.mode: adapter`
- `GET /ui/<page-path>` для страниц с `route.mode: configured`

При наличии adapter product console routes владеют `/` и `/runs`; без adapter сохраняется demo/schema mode.
Страницы с `route.mode: metadata` не добавляют отдельный route: они используются для navigation, title/subtitle, tabs и page metadata, а фактический запрос обслуживает существующий маршрут.
Страницы с `route.mode: adapter` рендерятся через `adapter.get_page(page_id, query)`.
Страницы с `route.mode: configured` рендерятся из schema/config blocks.

Уже реализовано в Iteration 13:

- auth/session/CSRF boundary;
- login/logout/CSRF routes;
- protected config/action POST route stubs;
- role checks;
- stable auth error envelopes.

Остаётся product-side scope:

- реальные config semantics;
- product validation;
- config apply;
- backup/audit artifacts;
- action catalog;
- action preview/execute semantics.

BeeUI защищает transport boundary. Product adapter принимает domain-решения.

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
- отдельный stable BeeUI API для внешнего frontend поверх текущего embedded surface;
- полноценный config UI read-model;
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

В текущем состоянии после Iteration 13.5 BeeUI отвечает за:

- FastAPI app factory;
- Jinja2 templates;
- Tabler layout;
- global navigation;
- reusable blocks;
- dashboard rendering for schema/demo mode and adapter-backed product console mode;
- `pages[].blocks[]` с поддержкой `width`, `span`, `size` и product-side `{id, enabled?}` references;
- adapter-backed `layout[]` rendering для product console pages через generic Tabler blocks;
- adapter-backed `layout[]` с поддержкой `width`, `span`, `size` и graceful fallback к `col-12`;
- adapter-backed `layout[]` поддерживает `type: group` для bounded nested Tabler layout groups;
- `kpi_grid` в adapter-backed `layout[]` поддерживает optional `columns` 1..4;
- configured pages и product console pages используют consistent page-body/container wrapper;
- declarative pages/navigation/theme/layout;
- static/literal and resolver-backed dashboard blocks from `config/schema.yml`;
- `app.locale` в `config/schema.yml` и resolved `locale` в template context;
- allowlist override через `?lang=` с fallback к default locale;
- configurable component defaults через `components.tabs.variant` и `components.accordion.variant`;
- page-level URL tabs через `pages[].tabs`, рендерящиеся как attached Tabler card tabs;
- safe internal tab href validation, disabled tab fallback и route-prefix-aware tab href rendering;
- `url_tabs` в component catalog как Jinja primitive для `nav nav-tabs card-header-tabs`;
- reusable `accordion` primitive с Tabler variants и visible toggle;
- BeeUI accordion не привязан к конкретному title вроде `Technical details`;
- generic dashboard fallback отделяет raw/debug payload в BeeUI accordion `Technical details`;
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
- generic adapter-backed custom pages через optional `adapter.get_page(page_id, query)`;
- redaction adapter-backed custom page payloads before render;
- malformed custom page payload degraded state;
- reserved route protection for `/auth`;
- artifact browser — HTML/JSON list and preview через adapter;
- JSON/JSONL/text bounded preview с malformed handling, preview limits и redaction;
- stable read-only API envelope для product console routes и read-only API routes для артефактов;
- auth/session/CSRF boundary для protected POST routes;
- login/logout/CSRF routes;
- role checks (`viewer`, `operator`, `admin`);
- protected transport stubs для config/action POST routes;
- stable auth error envelopes.

Запланированные обязанности:

- source artifact links;
- config read-model;
- theme customization;
- stable JSON API для будущего frontend;
- standalone mode.

Product-side scope остаётся в продукте:

- config semantics и validation;
- config apply, backups и audit artifacts;
- action catalog;
- action preview/execute semantics.

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

BeeUI опубликован в PyPI. Для BeeCap предпочтителен dependency через PyPI.

Если в `beecap/pyproject.toml` всё ещё используется local/path dependency:

```toml
dependencies = [
    "beeui @ file:///home/bee/Projects/beeui",
]
```

её нужно заменить на PyPI dependency, например:

```toml
dependencies = [
    "beeui>=0.17.0,<0.18.0",
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

### Обновление BeeUI в BeeCap из PyPI

Если BeeCap уже использует PyPI dependency:

```bash
cd ~/Projects/beecap
uv lock --upgrade-package beeui
./start.sh
uv pip show beeui

git add uv.lock
git commit -m "chore(deps): update beeui"
git push
```

Если BeeCap всё ещё использует local/path dependency:

```toml
"beeui @ file:///home/bee/Projects/beeui"
```

заменить на PyPI dependency:

```toml
"beeui>=0.17.0,<0.18.0"
```

после этого:

```bash
uv lock --upgrade-package beeui
./start.sh
uv pip show beeui

git add pyproject.toml uv.lock
git commit -m "chore(deps): update beeui"
git push
```

### Auth/session/CSRF в BeeCap

Для local/dev режима ключи окружения не нужны:

```yaml
auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false
```

Для защищённого режима:

```yaml
auth:
  enabled: true
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: true
```

Для локального HTTP можно оставить:

```yaml
cookie_secure: false
```

Для remote/HTTPS:

```yaml
cookie_secure: true
```

Переменные окружения:

```bash
export BEEUI_SESSION_SECRET="long-random-session-secret"
export BEEUI_OPERATOR_TOKEN="long-random-operator-token"
export BEEUI_ADMIN_TOKEN="long-random-admin-token"
```

Сгенерировать значения можно так:

```bash
python - <<'PY'
import secrets
for name in ("BEEUI_SESSION_SECRET", "BEEUI_OPERATOR_TOKEN", "BEEUI_ADMIN_TOKEN"):
    print(f'{name}="{secrets.token_urlsafe(48)}"')
PY
```

Если BeeCap передаёт в `create_beeui_app(settings=...)` свой settings dict, в этом dict должна быть секция `auth`. Это runtime/security settings, а не `config/beeui.yml`.

`config/beeui.yml` отвечает за layout/pages/navigation.
`auth` относится к runtime settings.

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

Текущий статус после Iteration 13.5:

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
- при наличии adapter routes `/`, `/runs`, `/runs/{run_id}` и `/venues/{venue_id}` работают в product console mode;
- auth/session/CSRF boundary и login/logout routes реализованы;
- `app.locale.default` / `app.locale.available` поддерживаются в schema;
- `?lang=` применяет locale только если значение входит в allowlist;
- resolved `locale` пробрасывается в HTML templates и в `<html lang="{{ locale|default('en') }}">`;
- configurable component defaults через `components.tabs.variant` и `components.accordion.variant`;
- page-level URL tabs через `pages[].tabs`;
- safe internal tab href validation, disabled tab fallback и route-prefix-aware tab href rendering;
- `url_tabs` работает через обычные `<a href>` и active state по `?tab=`;
- page-level tabs attached к общей Tabler card/body через `.beeui-page-tabs-card`;
- reusable `accordion` primitive используется и в generic dashboard fallback;
- generic dashboard fallback показывает summary/KPIs/structured cards, а raw/debug payload уходит в общий BeeUI accordion item с label `Technical details`;
- generic adapter-backed custom pages используют optional `get_page(page_id, query)` и рендерят только возвращённый `layout[]`;
- adapter-backed `layout[]` поддерживает `type: group` с `direction: vertical` и bounded depth 3;
- `kpi_grid.columns` поддерживает 1..4 columns для compact KPI grids;
- malformed group payload деградирует в explicit degraded block;
- page-body/container spacing унифицирован для configured/custom/product render paths;
- adapter-backed custom page payload redaction выполняется до HTML render;
- malformed custom page payload деgrades to explicit unavailable/error state;
- reserved route protection включает `/auth`;
- protected config/action POST stubs есть в BeeUI, но product semantics остаются за product adapter.

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
        size: S
```

Текущие declarative page rules:

- `page.id` must be unique;
- `page.path` must be unique и должен быть safe internal path;
- `navigation[].path` must reference declared page path;
- `pages[].route.mode` optional и может быть `metadata`, `adapter`, `configured`;
- system-owned BeeUI paths запрещены для регистрации configured/adapter routes;
- product-like paths вроде `/venues/mrkt`, `/venues/binance`, `/modes/live`, `/hidra/binance`, `/likes/top` разрешены, а route ownership задаётся через `pages[].route.mode`;
- `blocks` in page config is a list of block placements;
- placement может использовать `width`, `span` или `size`;
- `width` и `span` должны быть integer `1..12`;
- `size` должен быть `S|M|L|XL`;
- mixed sizing keys rejected fail-fast;
- placement c `block` ссылается на top-level block id;
- placement `{id, enabled?}` используется для product-side page block references;
- unknown block references are rejected fail-fast.

Пример page-level URL tabs:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title: ROP Dashboard
    subtitle: ROP operator dashboard
    blocks: []
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
        - id: disabled
          title: Disabled
          href: /rop?tab=disabled
          disabled: true
```

Правила для `pages[].tabs`:

- `href` только safe internal link;
- external/protocol-relative/javascript/mailto links rejected fail-fast;
- duplicate tab ids rejected fail-fast;
- invalid active query falls back to first enabled tab;
- disabled tab cannot become active;
- route prefix applies automatically during render.

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

Текущий contract v0 после Iteration 13.5:

```python
from typing import Mapping

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
  def get_page(
      self,
      page_id: str,
      query: Mapping[str, str],
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

`get_page()` optional: default `ProductUiAdapterBase.get_page()` возвращает unavailable, существующие adapters не обязаны реализовывать метод, product adapter владеет domain semantics страницы, а BeeUI только рендерит returned `layout[]`.

После Iteration 13.5 BeeUI вызывает adapter через embedded mount/app factory layer
для product console, страниц с `route.mode: adapter` и artifact browser routes.

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

BeeUI даёт reusable transport/UI layer для config routes, но не владеет config source of truth.

Source of truth остаётся в продукте:

```text
beecap/config/settings.yml
beeagent/config/settings.yml
```

BeeUI config UI работает через product adapter. BeeUI защищает transport boundary, а product adapter остаётся владельцем config semantics.

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

- BeeUI принимает защищённый POST request;
- проверяет auth/role/CSRF boundary;
- передаёт candidate в product validation callback;
- возвращает diff + validation result;
- сам не определяет product semantics;
- сам не пишет файлы.

### Apply

```text
POST /api/config/apply
```

Semantics:

- BeeUI принимает защищённый POST request;
- проверяет auth/role/CSRF boundary;
- пропускает только bounded transport stub;
- product определяет allowlist, validation, apply, backup и audit semantics;
- no secrets in audit;
- no runtime restart hidden behind apply.

Suggested artifacts:

```text
storage/interfaces/config_revisions/<change_id>/settings.before.yml
storage/interfaces/config_changes/<change_id>/audit.json
```

## Operator actions

BeeUI может показывать bounded operator actions и принимать защищённые POST requests, но execution semantics принадлежат продукту.

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

BeeUI auth layer уже реализован в Iteration 13.

Initial roles:

| Role       | Meaning                                            |
| ---------- | -------------------------------------------------- |
| `viewer`   | read-only UI access                                |
| `operator` | read-only + bounded allowed actions                |
| `admin`    | config/admin actions inside allowlisted boundaries |

Security rules:

- auth disabled only explicitly for local/dev;
- no default admin password in repo;
- token/session boundary for current MVP;
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

Актуальные ключевые файлы после Iteration 13.4:

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

Реализованный слой после Iteration 13.

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
GET /api/config/read-model
GET /api/actions
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
Iteration 13 — Auth/session/CSRF boundary for config/action routes MVP
Iteration 13.1 — Dashboard layout primitives, URL tabs and locale seed
Iteration 13.2 — Generic adapter pages and configurable Tabler primitives
Iteration 13.3 — Tabler attached page tabs and generic accordion visual parity hardening
Iteration 13.4 — Generic layout groups, KPI grid columns, and page spacing normalization
Iteration 13.5 — Product console route metadata and navigation compatibility
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
- auth/runtime security settings;
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
Iteration 13 — Auth/session/CSRF boundary for config/action routes MVP — ЗАВЕРШЕНО
Iteration 13.1 — Dashboard layout primitives, URL tabs and locale seed — ЗАВЕРШЕНО
Iteration 13.2 — Generic adapter pages and configurable Tabler primitives — ЗАВЕРШЕНО
Iteration 13.3 — Tabler attached page tabs and generic accordion visual parity hardening — ЗАВЕРШЕНО
Iteration 13.4 — Generic layout groups, KPI grid columns, and page spacing normalization — ЗАВЕРШЕНО
Iteration 13.5 — Product console route metadata and navigation compatibility — ЗАВЕРШЕНО
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
- `pages[].blocks[]` поддерживает `width`, `span`, `size`;
- adapter-backed `layout[]` поддерживает `width`, `span`, `size`;
- adapter-backed `layout[]` поддерживает `type: group` с `direction: vertical` и bounded depth 3;
- `kpi_grid.columns` поддерживает 1..4 columns для compact KPI grids;
- malformed group payload деградирует в explicit degraded block;
- page-body/container spacing унифицирован для configured/custom/product render paths;
- schema invalid `span` / `size` / mixed sizing keys fail-fast;
- malformed adapter-backed sizing degrade to `col-12`, не ломая страницу;
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
- layout links валидируются как safe internal links и учитывают route prefix / embedded mount path;
- `app.locale` доступен в `config/schema.yml`;
- `?lang=` работает как allowlist override и invalid `lang` fallback к default;
- `components.tabs.variant` и `components.accordion.variant` доступны в declarative UI schema;
- `pages[].tabs` поддерживает variant, active_param, explicit internal href и disabled tabs;
- `url_tabs` доступны в component catalog и page-level tabs;
- tab href валидируются как safe internal links и автоматически учитывают route prefix;
- disabled tab не становится active и invalid query fallback идёт к first enabled tab;
- generic dashboard fallback отделяет raw/debug payload в BeeUI accordion `Technical details`;
- reusable `accordion` primitive используется в generic dashboard fallback и configurable UI primitives;
- generic adapter-backed custom pages работают через optional `adapter.get_page(page_id, query)`;
- `pages[].route.mode` поддерживает `metadata`, `adapter`, `configured`;
- product metadata/navigation paths вроде `/venues/mrkt`, `/venues/binance`, `/modes/live` валидны как safe internal paths;
- generic page registration больше не основан на hardcoded product namespaces;
- BeeUI system routes по-прежнему защищены от shadowing;
- payload custom pages редактируется до HTML render, malformed payload рендерится как explicit unavailable/error state;
- route ownership для product-like paths задаётся через `pages[].route.mode`;
- реальные локальные скомпилированные CSS/JS из `@tabler/core@1.4.0` поставляются как локальные статические ресурсы пакета;
- самодельный слой совместимости `tabler-compatible` удалён из текущей runtime-поверхности;
- CSS BeeUI используется как контролируемый слой оформления продукта поверх Tabler, а не как второй CSS-фреймворк;
- тёмные оболочка, боковая панель и подвал визуально согласованы с вертикальным layout Tabler.
