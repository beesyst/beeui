# INTEGRATION — подключение BeeUI к Bee-продуктам

## Назначение

Этот документ описывает, как Bee-продукты (`beecap`, `beeagent` и будущие) подключают BeeUI как embedded UI layer.

## Текущий статус

**Iteration 13.14** — Request-scoped navigation visibility.

- BeeUI предоставляет optional public request-scoped navigation visibility resolver для `create_beeui_app(...)` и `mount_beeui(...)`.
- Resolver — это product-neutral hook:

  ```python
  navigation_visibility_resolver(request, canonical_path) -> bool
  ```

где `request` — текущий FastAPI `Request`, а `canonical_path` — canonical (непрефиксованный) path navigation item из product-side `beeui.yml` (например, `/runs`, `/venues/mrkt`). Route prefix обрабатывается внутри BeeUI.

- Если resolver вернул `False` — navigation leaf не рендерится в sidebar. Group без visible children не рендерится. Visible siblings сохраняются.
- Если resolver не передан — navigation полностью сохраняет текущее поведение (backward-compatible; существующие consumers не обязаны меняться).
- Один и тот же contract применяется ко всем generic shell rendering paths: configured pages, adapter-backed/custom pages, product console и `render_beeui_detail_page(...)`.
- Resolver является request-scoped: продукт может дать разную navigation для разных запросов без изменения schema.
- При exception в resolver item трактуется как скрытый (fail-closed): failure не раскрывает дополнительные navigation items.
- Сохраняются route prefix, RU/EN locale, `lang` preservation, active/descendant-active state и grouped navigation.

```python
from beeui_module.web.app import create_beeui_app

def navigation_visibility_resolver(request, canonical_path):
    return product_can_see_path(request, canonical_path)

app = create_beeui_app(
    product_id="beeagent",
    product_title="BeeAgent",
    adapter=bee_agent_adapter,
    config_path="config/beeui.yml",
    navigation_visibility_resolver=navigation_visibility_resolver,
)
```

Через `mount_beeui(...)` contract пробрасывается так же:

```python
mount_beeui(
    parent,
    path="/ui",
    product_id="beeagent",
    product_title="BeeAgent",
    adapter=bee_agent_adapter,
    config_path="config/beeui.yml",
    navigation_visibility_resolver=navigation_visibility_resolver,
)
```

**Пограничная граница.** Этот hook — presentation-only фильтр sidebar. Он не предоставляет и не отменяет HTTP authorization destination route: страница остаётся доступной по прямому URL, если продукт не запретил её server-side. Продукт обязан отдельно enforce server-side authorization (route/resource) и не рассматривать видимость navigation item как доступ.

**Iteration 13.13** — External-principal sessions and controlled embedding.

- Trusted product backend может создать signed BeeUI session для уже проверенного внешнего principal через публичный Python contract `AuthService.create_principal_session(user_id, role)`.
- `user_id` должен быть non-empty string; `role` должен быть explicit `UserRole` value. BeeUI не проверяет внешнюю identity и не маппит внешние credentials в роли; verification и role mapping остаются за product backend.
- Browser requests не могут выбирать или повышать role: нет browser-facing endpoint, принимающего `user_id`/`role`.
- Session cookie устанавливается и удаляется через единую централизованную policy: `AuthService.attach_session_cookie(response, cookie, path=...)` и `AuthService.delete_session_cookie(response, path=...)`. Login/logout routes используют те же helpers.
- Cookie policy настраивается через `auth.cookie_secure`, `auth.cookie_samesite` (default `lax`) и `auth.session_age_max` (default `86400`, range `60..604800`). `cookie_samesite=none` требует `cookie_secure=true`.
- Существующий формат signed cookies остаётся читаемым до configured expiry; token login/logout/CSRF/roles остаются backward-compatible.
- Controlled cross-site iframe embedding включается exact `security.frame_ancestors` origins. Default framing denial (`X-Frame-Options: DENY`) сохраняется. При непустом `security.frame_ancestors` BeeUI отправляет `Content-Security-Policy: frame-ancestors <origins>` и не отправляет конфликтующий `X-Frame-Options: DENY`.
- Wildcard, malformed, path/query/fragment и иные non-origin values отклоняются fail-fast.
- Нет BeeAgent/Bitrix/ROP-specific imports, labels или behavior; contract product-neutral.

```python
from beeui_module.auth.models import UserRole
from fastapi.responses import JSONResponse

service = request.app.state.beeui_auth_service
session, cookie = service.create_principal_session(
    user_id=verified_user_id,
    role=UserRole.operator,
)

response = JSONResponse({"ok": True, "data": {"session_started": True}})
service.attach_session_cookie(response, cookie, path="/ui")
return response
```

**Iteration 13.8** — Generic detail page template and render helper.

- BeeUI provides `render_beeui_detail_page()` product-neutral detail page renderer.
- Detail page supports section kinds: `key_value`, `text`, `table`, `links`.
- Detail page нормализует read-model, валидирует internal links, экранирует HTML.
- Detail page template использует общий BeeUI shell (theme, layout, locale, navigation, route prefix).
- Product routes могут вызывать `render_beeui_detail_page()` вместо ручной сборки HTML.
- Detail page не является JSON API endpoint и не меняет API contract.
- Detail page не добавляет keys в `config/settings.yml`.

**Iteration 13.7** — Locale-aware shell labels, language switcher and query-preserving navigation.

- Product-side `beeui.yml` может передавать localized shell labels.
- BeeUI resolves locale через allowlisted `?lang=`.
- BeeUI preserves locale в shell / navigation / page tabs / catalog, где это practically applicable.
- Product adapter по-прежнему владеет product-specific labels и semantics.
- Query, передаваемый в `get_page(page_id, query)`, остаётся untrusted input.
- Старый query-only locale contract Iteration 13.7 superseded Iteration 13.9: BeeUI использует cookie `beeui_lang`, но не session или localStorage.

- Generic contract `ProductUiAdapter` существует в `src/beeui_module/adapters/`.
- `BeeCapFixtureAdapter` в `src/beeui_module/adapters/beecap.py` — только fixture/reference реализация.
- Реальный BeeCap adapter должен жить на стороне BeeCap (см. ниже).
- Embedded mount API (`create_beeui_app(adapter=...)`) реализован.
- Mount helper `mount_beeui(...)` реализован.
- Adapter принимается, валидируется и сохраняется в `app.state`.
- Adapter-backed product console реализован: `get_dashboard()`, `list_runs()`, `get_run(run_id)` и optional `get_venue_dashboard(venue_id)` вызываются из read-only HTML/JSON routes.
- Page route ownership (Iteration 13.5): `pages[].path`, navigation и tab href проверяются как safe internal paths. Пути продукта вроде `/venues/mrkt`, `/venues/binance`, `/modes/live`, `/hidra/binance`, `/likes/top` разрешены. Кто обслуживает страницу, определяет `pages[].route.mode`. `metadata` pages не регистрируются как concrete routes; для `/venues/mrkt` типичный режим — `metadata`, потому что запрос может обслуживаться существующим `/venues/{venue_id}`. Для новых product-owned pages можно использовать `route.mode: adapter`; для schema-only pages можно использовать `route.mode: configured`. Custom/configured/adapter route registration защищает BeeUI system-owned routes (`/health`, `/static`, `/api`, `/auth`, `/components`, `/login`, `/logout` и соответствующие system prefixes). BeeUI не хардкодит product namespaces и не знает семантику `venues`, `modes`, `hidra`, `likes`.
- После Iteration 13.7 product adapter может возвращать `chart` и `data_table` внутри adapter-backed `layout[]`.
- Product adapter владеет бизнес-метриками, временными периодами и ROP/Bitrix/BeeCap/BeeAgent semantics; BeeUI только рендерит нормализованный layout.
- `chart` и `data_table` работают в product console и custom adapter pages, если adapter возвращает их в `layout[]`.
- Chart asset локальный, без CDN.
- Links в `data_table` валидируются и префиксуются под route prefix / embedded mount.
- Adapter-backed artifact browser реализован: `adapter.list_artifacts(run_id)` и `adapter.read_artifact(run_id, artifact_id)` вызываются из read-only HTML/JSON routes.
- Artifact preview pipeline: `build_preview()` → JSON/JSONL/text/unsupported → redaction → безопасный render в escaped `<pre>`.
- Artifact routes требуют adapter; без adapter возвращают 503 unavailable state.
- При наличии adapter product console routes владеют `/` и `/runs`; без adapter сохраняется backward-compatible demo/schema mode.

## Архитектурная граница

```text
BeeCap (product side)
  └── src/beecap_module/interfaces/ui/
        ├── adapter.py       ← real BeeCapUiAdapter (not in BeeUI)
        ├── read_model.py    ← BeeCap read-model construction
        ├── custom_pages.py  ← optional custom page read-models for get_page()
        └── artifacts.py     ← BeeCap artifact helpers

        ↓ implements ProductUiAdapter protocol

BeeUI (framework side)
  ├── src/beeui_module/adapters/
  │   ├── base.py            ← ProductUiAdapter protocol + base class
  │   ├── envelopes.py       ← stable adapter result envelopes
  │   ├── errors.py          ← stable adapter errors
  │   ├── ids.py             ← safe ID validation
  │   └── beecap.py          ← fixture/reference adapter (NOT for production)
  │
  ├── src/beeui_module/web/app.py   ← create_beeui_app(...)
  └── config/beeui.yml              ← product-specific UI config (future)
```

Главное правило:

```text
BeeUI renders.
Product decides.
```

## Где должен жить реальный BeeCap adapter

Реальный `BeeCapUiAdapter` должен находиться в BeeCap repository, **не** в BeeUI.

Ожидаемое расположение:

```text
src/beecap_module/interfaces/ui/
  ├── adapter.py          ← BeeCapUiAdapter(ProductUiAdapterBase)
  ├── read_model.py       ← BeeCap read-model construction
  └── artifacts.py        ← artifact reading from BeeCap storage
```

BeeCap-side adapter отвечает за:

- reading BeeCap storage/artifacts;
- constructing read-models (dashboard, runs, artifacts);
- constructing custom page read-models;
- enforcing product-specific allowlists;
- owning product authority decisions;
- implementing optional `get_page(page_id, query)` for product-specific pages;
- treating `query` as untrusted input;
- owning `get_page()` semantics;
- not relying on BeeUI to infer semantics from path namespace;
- declaring route metadata for existing product console routes in product-side `beeui.yml`;
- returning product-neutral `layout[]`;
- constructing product-neutral chart and data table layout blocks;
- keeping product/business semantics outside BeeUI;
- passing only normalized presentation data to BeeUI;
- implementing bounded action callbacks (future scope).

## Что BeeUI не должен делать во время интеграции

- BeeUI не должен читать BeeCap storage/config напрямую.
- BeeUI не должен копировать trading/domain logic.
- BeeUI не должен выполнять broker/order/runtime calls.
- BeeUI не должен становиться вторым source of truth для product state.
- BeeUI не должен мутировать product artifacts через read-only routes.
- BeeUI не должен импортировать `beecap_module` напрямую.
- BeeUI не должен вычислять ROP/Bitrix/BeeCap/BeeAgent metrics.
- BeeUI не должен строить product-specific chart series самостоятельно.
- BeeUI не должен пробрасывать arbitrary chart JS/options от продукта.

## Текущий fixture adapter

`BeeCapFixtureAdapter` в `src/beeui_module/adapters/beecap.py` существует только для:

- проверки `ProductUiAdapter` contract на realistic BeeCap-shaped data;
- reference implementation для BeeCap-side adapter developers;
- integration tests без real BeeCap dependency.

Это **не** production adapter.

Он **не** делает следующее:

- читает BeeCap storage;
- реализует trading/profit/order logic;
- предоставляет route-level integration;
- заменяет будущий real `BeeCapUiAdapter`.

## Пример embedded config

Пример будущего BeeCap-specific `beeui.yml` находится здесь:

```text
examples/beecap_embedded/beeui.yml
```

Этот файл **не загружается в runtime**. Это только документация.

## Текущий embedded integration flow

### Через `create_beeui_app()`

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

### Через `mount_beeui()`

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

После mount маршруты BeeUI доступны под `/ui/`:

```text
/ui/
/ui/health
/ui/auth/csrf
/ui/static/...
/ui/components
/ui/runs
/ui/runs/{run_id}
/ui/venues/{venue_id}
/ui/<page-path> для route.mode: adapter
/ui/<page-path> для route.mode: configured
/ui/api/dashboard
/ui/api/runs
/ui/api/runs/{run_id}
/ui/api/venues/{venue_id}/dashboard
/ui/runs/{run_id}/artifacts
/ui/runs/{run_id}/artifacts/{artifact_id}
/ui/api/runs/{run_id}/artifacts
/ui/api/runs/{run_id}/artifacts/{artifact_id}
```

### Важные ограничения

- Adapter принимается, валидируется и сохраняется в `app.state.beeui_adapter`.
- Adapter-backed product console реализован в Iteration 12 (read-only HTML/JSON routes через adapter).
- `get_venue_dashboard(venue_id)` является optional method и при отсутствии возвращает explicit unavailable state.
- Adapter-backed artifact browser из Iteration 11 продолжает работать без изменения contract.
- Product metadata сохраняется в `app.state.beeui_product`.
- Demo mode (`create_beeui_app()` без аргументов) остаётся backward-compatible.
- BeeAgent adapter implementation остаётся future scope.
- `route.mode: metadata` не создаёт отдельный route.
- `route.mode: adapter` создаёт route и вызывает `adapter.get_page(page_id, query)`.
- `route.mode: configured` создаёт route и рендерит schema/config blocks.

### Iteration 13.9 — Locale persistence

Starting from Iteration 13.9, the locale cookie `beeui_lang` is set by BeeUI middleware when `?lang=` is present and valid. The cookie path matches the configured `route_prefix`.

Products do not need to set or manage the locale cookie. BeeUI handles:

- cookie setting on valid `?lang=`;
- cookie reading on subsequent requests after valid query param;
- validation against `app.locale.available`;
- safe fallback to configured default locale.

### Iteration 13.9 — Theme persistence

Theme is persisted via `localStorage` under `beeui-theme`. Valid values: `system`, `light`, `dark`. `auto` is accepted only as a configuration compatibility alias for `system`; invalid stored values are removed.

Theme is a presentation preference only and does not affect product behavior, authorization, or business logic.

### Iteration 13.9 — Safe href contract

All active hrefs in adapter-provided `filter_form` and `data_table` blocks must pass the shared internal-link contract:

- External scheme/netloc → rejected.
- Protocol-relative `//...` → rejected.
- Path traversal → rejected.
- Control characters → rejected.
- Must start with `/`.

Invalid hrefs become `None` and render as inert text or are omitted.

Products should pass only safe internal paths for:

- `checkbox toggle_href`;
- `columns toggle_href`;
- `reset href`;
- `sort_href` in data table columns.

`filter_form` is a GET-only server-side form. JavaScript auto-submit is optional progressive enhancement; it does not change the GET contract.

For adapter-backed `data_table`, product may provide optional safe stable `id` metadata and `pagination.page_size` links. With `id`, BeeUI enhances only the table's own explicit controls through a same-origin GET and requires the response to contain the same identity before replacement. Product continues to interpret the query and returns the authoritative filtered/sorted/paginated layout. The normal href/form GET path remains the fallback; do not rely on BeeUI for product filter semantics or emit adapter-provided selectors or JavaScript.

Configured product pages may opt into `pages[].tabs.progressive: true`. Product still provides canonical safe internal tab `href` values and server-rendered GET responses; it does not provide browser code, tab caches or SPA state. BeeUI replaces only its matching page-tabs surface, initializes its own controlled live-table, Datepicker and chart components, and falls back to normal navigation for failure or unsafe destinations. Optional `items[].icon` is a BeeUI-controlled identifier, not product SVG/HTML.

BeeUI owns the controlled tab icon registry: product supplies only a safe identifier (`dashboard`, `runs`, `list`, `reports`, `chart`, `calendar`, `queue`, `messages`, `ai`, `source`, `attachment`, `evidence`, `integration`, `recommendation`). BeeUI renders its own exact Tabler Icons 2.x outline SVG geometry inline (no CDN, no external asset), with `class="icon me-2"` spacing between icon and label in every tab state. Unknown safe identifier renders no icon; raw SVG/HTML/CSS/JS from config is rejected by validation and never rendered. The registry is product-neutral — no ROP/BeeAgent/Bitrix identifiers are added.

All synchronous `ProductUiAdapter` methods invoked by BeeUI async routes run through one generic async-safe BeeUI boundary. Product method signatures and result/error envelopes do not change; adapters remain responsible for read-model construction, validation, authority and product semantics.

### Iteration 13.10 — Date-range presentation contract

Products continue to provide the same `filter_form.date_range` or `data_table.toolbar.fields[].date_range` payload: `from_value`, `to_value`, `from_label`, and `to_label`. BeeUI renders the two canonical fields as local Litepicker-backed Tabler Datepicker controls and submits only `date_from` and `date_to` in `YYYY-MM-DD` format. Either bound may be empty; BeeUI does not validate date semantics, ranges, inclusivity, or timezones. Litepicker is a package-local conditional presentation asset, and products must not add datepicker templates, JavaScript, CSS, or arbitrary datepicker options.

### Iteration 13.9 — Detail presentation metadata

Detail page `key_value` items support product-neutral presentation fields:

```json
{
  "label": "Status",
  "value": "ok",
  "display": "✓",
  "tone": "success",
  "variant": "badge",
  "collapsible": false
}
```

- `variant`: `text`, `badge`, `boolean`, `confidence`, `long_text`.
- `tone`: `default`, `muted`, `success`, `warning`, `danger`.
- Product decides tone and display semantics.
- BeeUI validates allowlisted values.
- Unknown variant/tone safely degrades to plain text.

## Page route ownership

Iteration 13.5 добавляет явный `pages[].route.mode`.

Product-specific page declaration остаётся в product-side `beeui.yml`:

```yaml
pages:
  - id: mrkt
    path: /venues/mrkt
    route:
      mode: metadata
    title: MRKT
    subtitle: Дашборд MRKT
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
    blocks: []
```

Правила:

- `metadata` используется для navigation, title/subtitle, tabs и page metadata, но не создаёт concrete route;
- `adapter` создаёт route и вызывает `adapter.get_page(page_id, query)`;
- `configured` создаёт route и рендерит schema/config blocks;
- safe internal paths отделены от route registration;
- BeeUI system-owned routes защищены от shadowing;
- BeeUI не выводит смысл из path namespace.

Product adapter может реализовать:

```python
from typing import Mapping

def get_page(
    self,
    page_id: str,
    query: Mapping[str, str],
) -> AdapterResult | AdapterErrorResult:
    ...
```

Rules:

- method is optional;
- default `ProductUiAdapterBase.get_page()` returns unavailable;
- BeeUI passes `page_id` and query params;
- product adapter owns page semantics;
- BeeUI renders returned `layout[]`;
- BeeUI does not import product modules;
- BeeUI does not infer ROP/BeeCap/BeeAgent semantics;
- malformed payload degrades;
- payload is redacted before HTML rendering.

## Generic detail page integration (Iteration 13.8)

Product routes or adapter-backed custom pages can use the generic detail page renderer instead of assembling HTML manually.

### Entrypoint

```python
from beeui_module.pages.detail import render_beeui_detail_page

response = render_beeui_detail_page(
    request=request,
    page=page_data,
    templates=templates,
    route_prefix=route_prefix,
    ui_config=ui_config,
    product_title=product_title,
    product_id=product_id,
)
```

### Detail page model

```python
page_data = {
    "page_id": "event_detail",
    "title": "Event detail",
    "subtitle": "Read-only details",
    "back_href": "/events",
    "warnings": [],
    "sections": [
        {
            "title": "Summary",
            "kind": "key_value",
            "items": [
                {"label": "Subject", "value": "..."},
            ],
        },
        {
            "title": "Preview",
            "kind": "text",
            "body": "...",
        },
        {
            "title": "Rows",
            "kind": "table",
            "columns": [{"key": "name", "label": "Name"}],
            "rows": [{"name": "Status", "value": "ok"}],
        },
        {
            "title": "Links",
            "kind": "links",
            "items": [{"label": "Open", "href": "/runs/run_001"}],
        },
    ],
}
```

### Normalization

The renderer normalizes the model before rendering:

- unsupported/malformed sections are safely omitted;
- missing values render as `n/a`;
- `back_href` and link hrefs are validated as safe internal paths;
- external/unsafe links are rendered as inert text;
- raw fields (`raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes`) are not implicitly rendered;
- text remains HTML-escaped (autoescape, no `|safe`).

### Template

Template: `src/beeui_module/web/templates/detail.html`.

Extends `base.html` with the same shell context (theme, layout, locale, navigation, route prefix). No JS required. No external assets.

## Security notes / Замечания по безопасности

- Все adapter inputs (`run_id`, `venue_id`, `artifact_id`) валидируются через `beeui_module.adapters.ids`.
- `query`, передаваемый в `get_page()`, является untrusted input и должен обрабатываться product adapter как untrusted input.
- Adapter envelopes используют стабильный status `ok|partial|error`; исходные исключения не попадают в response.
- Product console JSON API использует стабильный read-only envelope `ok/api/read_only/data|error/warnings/meta`.
- Artifact API routes сохраняют существующий contract Iteration 11.
- Secrets не должны пересекать adapter boundary и попадать в BeeUI.
- Adapter custom page payload redacted before render.
- Custom pages are GET-only and read-only.
- No product callback is called for write/action semantics from custom pages.
- Write/action adapter methods недоступны по умолчанию.

### Auth/session/CSRF (Iteration 13)

- Auth-disabled mode (`auth.enabled: false`) — local/dev только.
- Auth-enabled mode требует:
  - `BEEUI_SESSION_SECRET` — для подписи session cookie;
  - `BEEUI_OPERATOR_TOKEN` — для operator role;
  - `BEEUI_ADMIN_TOKEN` — для admin role.
- Login создаёт signed session cookie (HMAC-SHA256, 24h expiry).
- CSRF token хранится в session cookie; передаётся через `X-CSRF-Token` header (API) или `csrf_token` form field (HTML).
- POST routes на config/action endpoints защищены auth + CSRF + role check.
- Product callbacks не вызываются до прохождения auth/CSRF.
- Secrets из `config/settings.yml` не попадают в HTML/API/logs.
