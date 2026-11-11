# CONFIG — BeeUI Configuration

## Purpose and configuration ownership

BeeUI separates runtime settings from presentation configuration. These files serve different purposes and must not be treated as interchangeable:

| File                            | Owner                 | Purpose                                                                                                               |
| ------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `config/settings.yml`           | BeeUI runtime         | Web binding, logging, storage, authentication, session/cookie policy, framing and feature gates                       |
| `config/schema.yml`             | BeeUI standalone/demo | Declarative demo shell, navigation, pages, local sources and reusable blocks                                          |
| `<product>/config/beeui.yml`    | Embedding product     | The same validated BeeUI presentation schema, with product navigation, page tabs, route ownership and block placement |
| `<product>/config/settings.yml` | Embedding product     | Product capabilities, credentials, execution policy, approvals and other domain-specific authority                    |

`config/beeui.yml` is **implemented and used** for embedded products, including BeeAgent; it is not a proposed future convention. The standalone CLI still loads the BeeUI runtime settings and its demo schema from the repository's canonical paths. Product-specific files are supplied through the embedded Python API.

**Invariant:** BeeUI renders normalized presentation data. Products decide what an operator may read or execute. Configuration of a page or action is not an authorization grant.

See [ARCHITECTURE.md](ARCHITECTURE.md), [INTEGRATION.md](INTEGRATION.md), [COMPONENTS.md](COMPONENTS.md) and [SECURITY.md](SECURITY.md).

## Runtime settings: `config/settings.yml`

The following example reflects the checked-in BeeUI demo settings. Environment-variable references are resolved when authentication is enabled; they are not literal secrets:

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
  frame_ancestors: []

auth:
  enabled: false
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: false
  cookie_samesite: lax
  session_age_max: 86400

product:
  mode: demo
  id: demo
  title: BeeUI Demo
  adapter: static

features:
  browser_artifact: true
  config_preview: false
  config_apply: false
  operator_actions: false
  api: false
```

### Validated runtime contract

The actual validation code is `src/beeui_module/core/settings.py`, particularly `load_settings()`. It is authoritative if examples and implementation ever diverge.

| Setting                                                                                  | Implemented validation / behavior                                                      |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `app.name`                                                                               | Required; exactly `beeui`                                                              |
| `web.host`                                                                               | Required non-empty string                                                              |
| `web.port`                                                                               | Required integer from 1 to 65535                                                       |
| `web.route_prefix`                                                                       | Required string; rejects `..` path segments                                            |
| `web.cache_static`                                                                       | Required nonnegative integer                                                           |
| `logging.clear_logs`, `logging.utc`                                                      | Required booleans                                                                      |
| `logging.level`                                                                          | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`                                      |
| `logging.file`                                                                           | Required non-empty safe relative path; no absolute path or `..`                        |
| `storage.enabled`                                                                        | Required boolean                                                                       |
| `storage.root`                                                                           | Required safe relative path                                                            |
| `security.html_autoescape`                                                               | Must be `true`                                                                         |
| `security.assets_ext`                                                                    | Required boolean; normal deployments use `false`                                       |
| `security.frame_ancestors`                                                               | Optional list of exact HTTP(S) origins; no wildcard, path, query, fragment or userinfo |
| `auth.enabled`                                                                           | Optional auth section, but when present `enabled` must be a boolean                    |
| `auth.session_secret`, `auth.operator_token`, `auth.admin_token`                         | Required and resolved to non-empty strings when `auth.enabled: true`                   |
| `auth.cookie_secure`                                                                     | Required boolean when authentication is enabled                                        |
| `auth.cookie_samesite`                                                                   | Optional `lax`, `strict` or `none`; `none` requires `cookie_secure: true`              |
| `auth.session_age_max`                                                                   | Optional integer from 60 to 604800 seconds                                             |
| `product.id`, `product.title`                                                            | Required non-empty strings                                                             |
| `features.browser_artifact`, `config_preview`, `config_apply`, `operator_actions`, `api` | Each required boolean                                                                  |

Some settings are accepted as product/deployment metadata rather than enforcing a full domain policy. Do **not** assume the loader itself enforces production environment hardening, all feature dependencies or product-specific authorization. The embedding host must apply its own security controls.

### Authentication and secrets

The demo config explicitly uses `auth.enabled: false`. Do not treat that as a production recommendation. For a protected deployment, enable authentication and supply fresh session and role credentials from the environment or another authorized external secret source:

```yaml
auth:
  enabled: true
  session_secret: ${BEEUI_SESSION_SECRET}
  operator_token: ${BEEUI_OPERATOR_TOKEN}
  admin_token: ${BEEUI_ADMIN_TOKEN}
  cookie_secure: true
  cookie_samesite: lax
  session_age_max: 86400
```

`cookie_secure: true` requires HTTPS browser access; local HTTP development may require a different explicitly scoped setup. An authenticated session and CSRF token protect the generic transport, while the product independently checks resource ownership, scopes, approvals and action arguments. Never commit actual secrets, tokens, signed sessions or private approval material.

The framing default is deny. Adding `security.frame_ancestors` allows only the exact configured origins under the validated framing contract; it does not grant access to product data.

### Features and their boundaries

- `browser_artifact` controls availability of generic artifact browsing where an adapter supplies authorized references.
- `config_preview` and `config_apply` gate the protected configuration transport. They do not supply a product config editor or validation implementation by themselves.
- `operator_actions` gates protected action preview/execute transport. The product must still implement and authorize each action.
- `api` is an existing configuration flag, not proof that a future API version or all planned endpoints exist. Consult [API_CONTRACT.md](API_CONTRACT.md) for implemented routes.

All operationally sensitive features must fail closed when their product callback or current authorization is unavailable.

## Presentation configuration: `config/schema.yml` and product `config/beeui.yml`

Both files use the same `load_beeui_config()` parser in `src/beeui_module/pages/config.py`. The parser validates known keys, supported visual options, safe routes, navigation links and page/block references.

Top-level keys:

| Key            | Meaning                                                                   |
| -------------- | ------------------------------------------------------------------------- |
| `app`          | Product display name, locale, theme and shell layout                      |
| `navigation`   | Sidebar entries and optional nested items                                 |
| `data_sources` | Controlled demo or static read-only sources for schema blocks             |
| `blocks`       | Named declarative schema/demo block definitions                           |
| `components`   | Optional default tabs/accordion variants                                  |
| `pages`        | Declared page identity, path, title, tabs, route ownership and placements |

Product-specific runtime settings, credentials, business rules and authority do not belong in this file. Adapter-backed `layout[]` is returned by the product at request time and is distinct from the schema/demo block registry.

### Minimal page example

This is an illustrative **product-owned** configuration. The product must provide the corresponding `get_page()` implementation; the YAML alone does not create its data or execution functionality.

```yaml
app:
  title:
    en: Example Console
    ru: Example Console
  product: example
  logo_text:
    en: Example
    ru: Example
  locale:
    default: en
    available: [en, ru]
  theme:
    mode: system
    primary: blue
    base: gray
    font: sans-serif
    radius: 1
    density: default
  layout:
    type: vertical
    container: xl
    sidebar:
      variant: default
      collapsed: false
    navbar:
      enabled: false
      variant: default
      sticky: false

navigation:
  - title:
      en: Investigations
      ru: Investigations
    path: /investigations
    icon: shield

data_sources: {}
blocks: {}

pages:
  - id: investigations
    path: /investigations
    route:
      mode: adapter
    title:
      en: Investigations
      ru: Investigations
    tabs:
      variant: fill_icons
      active_param: tab
      progressive: true
      surface: separated
      items:
        - id: active
          title:
            en: Active
            ru: Active
          href: /investigations?tab=active
          icon: messages
        - id: results
          title:
            en: Results
            ru: Results
          href: /investigations?tab=results
          icon: report
    blocks: []
```

Use actual translated text for each available locale in a real product; the identical English labels above keep the example language-neutral. Locale selection supports `en` and `ru`; product labels are localized by the product or configuration, not automatically translated by BeeUI.

### Application metadata, locale and theme

`app.title` and `app.logo_text` accept localized text according to the declared locales; `app.product` is a non-empty product identifier. If `app.locale` is present, `default` must be in its non-empty `available` list; supported locales are `en` and `ru`.

The theme has validated `mode`, `primary`, `base`, `font`, `radius` and `density` fields. The implemented theme parser accepts `light`, `dark`, `system` and the compatibility alias `auto` (normalized to `system`). Consult [THEME.md](THEME.md) for preference persistence and the full theme contract. Invalid required theme options fail config loading.

`app.layout` specifies the validated layout type, container, sidebar variant/collapsed state, and navbar enabled/variant/sticky state. Use the existing Tabler-compatible choices defined in `src/beeui_module/pages/config.py`; do not inject arbitrary CSS class names, HTML or JavaScript through config.

### Navigation

Each navigation item supplies a localized `title`, an optional safe icon and either a safe page `path`, or nested `children`. Disabled placeholders are supported without an active destination. An enabled leaf needs a valid path matching a declared page; duplicate navigation paths are refused. A parent with children does not also specify its own path. Visibility filtering may hide sidebar entries per request, but it is **not** route authorization.

### Pages and route ownership

Each page has a safe unique `id`, unique safe `path`, localized `title`, optional `subtitle`, block placements and optional `route`/`tabs`.

`pages[].route.mode` controls ownership:

| Mode         | Behavior                                                                                                |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `configured` | BeeUI registers the declarative page and resolves configured/demo blocks.                               |
| `adapter`    | BeeUI registers the page and requests `ProductUiAdapter.get_page(page_id, query)`.                      |
| `metadata`   | The page supplies navigation/title metadata; another already-registered route handles the HTTP request. |

The host or product must explicitly authorize access to the resulting resource. Reserved BeeUI system routes cannot be taken over by an arbitrary configured page.

### Page tabs and progressive enhancement

Tabs are canonical URL links, not a second client-side router. Current options include:

| Property       | Contract                                                                                                                           |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `variant`      | `default`, `reverse`, `fill`, `icons`, `fill_icons`, `compact_fill_icons`, `dropdown`                                              |
| `active_param` | Safe query parameter name; default `tab`                                                                                           |
| `progressive`  | Boolean; default `false`. Same-origin partial replacement is an enhancement with ordinary GET fallback.                            |
| `surface`      | `attached` (default) or `separated`                                                                                                |
| `items`        | List of uniquely identified tabs; each has `id`, localized `title`, validated internal `href`, optional safe `icon` and `disabled` |

For consistent page/route behavior, see [WEB_UI.md](WEB_UI.md). Products remain responsible for query state, selected Case/run ownership and safe result filtering.

### Global component variants

The optional `components` section configures default tabs and accordion variants, e.g.:

```yaml
components:
  tabs:
    variant: fill
  accordion:
    variant: flush
```

Only declared, validated variants are supported. Component defaults are presentation concerns, not runtime policy.

### Data sources and block registry

`data_sources` accepts controlled `demo` or constrained static sources as defined by `src/beeui_module/pages/config.py`. The static source path is validated and resolved relative to an approved schema root; it is not an arbitrary file browser or remote-fetch capability. `blocks` registers supported schema/demo components and their source bindings; `pages[].blocks` places those registered blocks.

In an embedded product, use `route.mode: adapter` and a product-owned normalized `layout[]` to display dynamic domain data. Do not copy product-specific data gathering or execution logic into generic BeeUI data sources. For supported block types and bounds, consult [COMPONENTS.md](COMPONENTS.md).

## Embedded integration and CLI

The supported Python entrypoint is:

```python
from beeui_module.web.app import create_beeui_app

app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

A product with an existing FastAPI host can instead call `mount_beeui(parent, path="/ui", ...)` to mount the application under a validated prefix. The product supplies the adapter, its read-models and security enforcement. Details are in [INTEGRATION.md](INTEGRATION.md).

For the standalone/demo CLI:

```bash
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

`./start.sh web` accepts `--host` and `--port`. It does **not** accept a product `--config` or `--settings` argument. The demo CLI obtains its canonical settings/schema via existing project path resolution. `start.sh` runs frozen `uv` dependencies; normal startup should not regenerate `uv.lock`.

## Validation and troubleshooting

The configuration loaders are the authority:

- `beeui_module.core.settings.load_settings(Path("config/settings.yml"))`
- `beeui_module.pages.config.load_beeui_config(Path("config/schema.yml"))`

From the BeeUI repository:

```bash
uv run --frozen python - <<'PY'
from pathlib import Path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config

settings = load_settings(Path("config/settings.yml"))
schema = load_beeui_config(Path("config/schema.yml"))
print(settings["app"]["name"])
print(schema.product)
PY
```

This checks the BeeUI demo configuration only. To validate a product file, call `load_beeui_config(Path("/path/to/product/config/beeui.yml"))` in an authorized development environment; product settings must be validated by the product's own loader.

Common failure classes:

| Symptom                                    | Check                                                                                                             |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Startup rejects settings                   | Required keys, types, session env references, cookie security and safe relative paths                             |
| Product page unavailable                   | `route.mode`, page ID, injected adapter and `get_page()` implementation                                           |
| Empty/degraded component                   | Schema block references versus adapter `layout[]`, payload normalization and field limits                         |
| Broken link after embedding                | Route prefix, mount path and safe internal href validation                                                        |
| Operator action disabled                   | Auth/role, CSRF, feature gate and **current product approval**; changing YAML alone must never bypass the product |
| Vendor documentation appears newer than UI | `docs/vendor/tabler` is a reference snapshot, not the installed runtime CSS/JS bundle                             |

## Security and change management

- Do not place credentials or product business logic in `schema.yml` or `beeui.yml`.
- Do not change a version, dependency lockfile or frontend asset merely to update configuration documentation.
- Do not silently add new config keys; the parser validates exact keys for presentation configuration.
- Do not treat a UI flag, navigation entry or local demo mode as authority to perform active product work.
- Treat GET and polling as read-only and verify this in product integration tests.
- Update this document whenever the runtime or presentation configuration contract changes; use [SDLC.md](SDLC.md) and [SECURITY.md](SECURITY.md) for proportional review.

## Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — ownership and trust boundaries.
- [SPEC.md](SPEC.md) — product scope and current capabilities.
- [INTEGRATION.md](INTEGRATION.md) — adapter and embedded-mode wiring.
- [WEB_UI.md](WEB_UI.md) — routes, tabs and browser behavior.
- [COMPONENTS.md](COMPONENTS.md) — reusable block contracts.
- [API_CONTRACT.md](API_CONTRACT.md) — response envelopes and protected transport.
- [THEME.md](THEME.md) — theme preferences.
- [SECURITY.md](SECURITY.md) — security requirements.
- [SDLC.md](SDLC.md) — development and verification.
