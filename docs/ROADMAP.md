# ROADMAP — BeeUI

## Purpose

This document defines the development path for `beeui` across stages and iterations.

`beeui` is a reusable Python UI layer for Bee products.

The project provides:

- a web surface built on FastAPI + Jinja2 + Tabler;
- declarative pages and dashboard blocks;
- product adapters for `beecap`, `beeagent`, and future Bee products;
- an artifact browser and source links;
- stable read-only JSON API contracts;
- bounded controls for configuration, administration, and operator actions;
- a theme and customization layer;
- a future foundation for a no-code dashboard builder and frontend.

`beeui` does not replace the domain and runtime core of Bee products.

Bee products retain ownership of:

- runtime behavior;
- business logic;
- artifacts;
- configuration validation;
- bounded execution APIs;
- security-sensitive authority boundaries.

`beeui` is responsible for:

- rendering;
- navigation;
- reusable UI blocks;
- read-model presentation;
- safe artifact navigation;
- HTML/API consistency;
- the auth/admin surface;
- the dashboard schema;
- a future foundation for a visual builder.

The ROADMAP serves as a lightweight SDLC artifact:

- sets the development direction;
- defines each iteration's goal;
- specifies expected behavior, artifacts, and checks;
- helps connect Issue → Code → Tests → Docs → PR → Merge.

The ROADMAP does not replace Issues and PRs:

- **Issue** explains exactly what the task requires;
- **PR** records what was actually implemented and how it was verified;
- **ROADMAP** shows the project's direction and defines completion for each iteration.

An iteration is closed through a PR.

The ROADMAP does not duplicate the full process and security rules:

- the development process and change gates are defined in `docs/SDLC.md`;
- secure development rules and security checks are defined in `docs/SECURITY.md`.

## Vision

| Area                             | Definition                                                                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Product identity**             | `beeui` evolves as a reusable UI/backend framework for Bee products, built on Python, FastAPI, Jinja2, and Tabler.                         |
| **Primary goal**                 | Remove duplicated web/UI infrastructure from `beecap`, `beeagent`, and future Bee products.                                                |
| **Execution philosophy**         | `beeui` renders and manages the interface layer; the domain product makes decisions and remains the source of truth.                       |
| **Source of truth**              | Product configuration, artifacts, and APIs remain canonical. `beeui` reads read-models/adapters and displays the result.                   |
| **KISS principle**               | Start with a declarative schema + reusable blocks + adapters. Introduce a no-code builder only after contracts stabilize.                  |
| **Security principle**           | The UI is read-only by default. All write/control actions go through bounded product callbacks/APIs, validation, backup, and audit.        |
| **Integration principle**        | The product adapter is the sole point of knowledge about BeeCap/BeeAgent domain semantics.                                                 |
| **Frontend evolution principle** | Start with a server-rendered UI. Later, a separate frontend connects to the stable BeeUI JSON API.                                         |
| **Customization principle**      | Define themes/layouts/pages/blocks through schema/config rather than copying HTML across products.                                         |
| **Anti-chaos principle**         | Bee products must not reimplement Tabler templates, sidebars, cards, tables, the artifact browser, configuration UI, or admin pages.       |
| **Authority boundary principle** | `beeui` receives no direct broker/runtime/execution authority. All potentially dangerous actions remain behind product-owned bounded APIs. |

## Development principles

Each iteration must deliver one meaningful, end-to-end capability.

Fix defects discovered during implementation within the same feature branch before PR. Do not create separate iterations for individual regressions or cosmetic adjustments.

Each iteration must:

- run through `start.sh` or the applicable CLI entrypoint;
- produce clear logs;
- preserve the `beeui_module` package structure;
- include tests for key behavior;
- preserve HTML autoescape;
- block path traversal on file/artifact routes;
- keep secrets out of HTML/API/logs/artifacts;
- avoid introducing a second source of truth;
- avoid introducing execution authority into `beeui`;
- close through Issue / PR / tests / docs;
- pass the required checks in `docs/SDLC.md` and `docs/SECURITY.md`.

For `beeui`, this means:

- low-risk changes pass baseline checks;
- runtime-risk changes require API/adapter/artifact contract verification;
- security-sensitive changes require additional verification of auth/session/file/path/write-action boundaries.

## SDLC workflow for ROADMAP items

Each iteration follows a simplified cycle:

1. **Planning**  
   The iteration is described in the ROADMAP and recorded as an Issue.

2. **Requirements**  
   The iteration defines its scope, deliverable, checks, and DoD.

3. **Implementation**  
   Changes are made on a separate branch and stay within the current iteration's scope.

4. **Verification**  
   Tests, smoke checks, route checks, HTML/API checks, and security checks are performed.

5. **Review / PR**  
   The PR records changes, tests, limitations, and known gaps.

6. **Merge**  
   The iteration is complete once its DoD is met.

## Status definitions

Allowed iteration statuses:

- **PLANNED** — planned
- **IN PROGRESS** — work in progress
- **DONE** — completed
- **DONE (partial)** — partially completed with acknowledged limitations
- **FUTURE** — deliberately deferred until baseline contracts stabilize
- **RETIRED** — a planned item withdrawn because it was superseded, already covered by actual integration, or no longer has standalone value; its ID is not reused

## Roadmap item format

Historical iterations with `DONE` status retain their existing structure and are not rewritten solely for consistency.

New iterations and materially refined `PLANNED`, `IN PROGRESS`, and `FUTURE` items use a compact structure:

- `Goal`
- `Depends on`, when real prerequisites exist
- `Change level`
- `Scope`
- `Excluded`
- `Deliverable`
- `Acceptance criteria`
- `Checks`
- `DoD`

The ROADMAP defines the product contract at the iteration level.

Full payload examples, specific implementation files, extended test matrices, and verification evidence belong in Issues and PRs.

The target length for a new iteration is 40–80 lines. A longer section is allowed only when needed to define a new public or security-sensitive contract.

## Change levels for verification

The lightweight SDLC uses three change levels:

- **low-risk** — documentation, local templates, styles, and safe read-only UI changes that do not affect adapters/APIs/security;
- **runtime-risk** — adapters, artifact parsing, configuration preview/apply, API contracts, product integration, and schema validation;
- **security-sensitive** — auth, sessions, cookies, file/path access, write controls, action execution, secrets redaction, HTML/API exposure, dependency surface.

Required checks are defined in:

- `docs/SDLC.md`
- `docs/SECURITY.md`

## Global DoD

An iteration is complete when:

- behavior is implemented within the declared scope;
- verification passes at the level required by the actual change risk and approved Issue;
- focused tests cover changed behavior and relevant negative cases;
- full regression, CLI/web smoke, browser checks and installed-package verification pass when required by the changed boundary;
- HTML autoescape is enabled;
- static assets are served through controlled mechanisms;
- secrets do not appear in HTML/API/logs/artifacts;
- path traversal is blocked on file/artifact/config routes;
- read-only routes do not mutate source artifacts;
- write/control routes, if present, enforce validation + audit;
- response envelopes remain stable wherever an API contract is declared;
- documentation is updated when a contract changes;
- Bee products do not acquire a duplicate web backend path;
- there are no hidden defaults, hidden fallback paths, or silent authority escalation.

## Target architecture

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

Core rule:

```text
BeeUI renders.
The product decides.
```

## Project structure

The current implementation uses the following source layout:

```text
beeui/
├── config/
│   ├── schema.yml
│   ├── settings.yml
│   └── start.py
├── docs/
├── scripts/
├── src/
│   └── beeui_module/
│       ├── adapters/
│       ├── api/
│       ├── artifacts/
│       ├── auth/
│       ├── blocks/
│       ├── cli/
│       ├── core/
│       ├── data/
│       ├── pages/
│       ├── theme/
│       └── web/
│           ├── app.py
│           ├── templates/
│           └── static/
├── tests/
├── pyproject.toml
├── start.sh
└── uv.lock
```

Source code and `pyproject.toml` are authoritative for exact package layout, runtime assets and distribution contents.

See [ARCHITECTURE.md](https://ARCHITECTURE.md?utm_source=chatgpt.com) for component responsibilities and DEV_GUIDE.md for development and packaging.

Product adapter ownership rule:

- production `BeeCapUiAdapter` lives in `beecap`;
- production `BeeAgentUiAdapter` lives in `beeagent`;
- BeeUI contains only generic adapter contracts;
- product-shaped fixture/reference adapters are allowed only to test a new generic contract and do not constitute production integration;
- a fixture adapter must not duplicate an actively evolving production read-model without a specific contract-testing need.

---

## Stage 1 — Foundation MVP

### Iteration 0 — Project skeleton, startup and release contract

**Status:** DONE

#### Goal

Create a minimal runnable `beeui` skeleton following the `beecap` / `beeagent` conventions: `src-layout`, `uv`, `start.sh`, `config/start.py`, basic CLI dispatch, logging, paths, tests, release-please, and package metadata.

#### Scope

Included:

- `pyproject.toml`;
- `uv.lock`;
- `start.sh`;
- `config/start.py`;
- `config/schema.yml`;
- `.gitignore`;
- `.env.example`;
- `.github/release-please/*`;
- a basic `src/beeui_module` structure;
- a basic `docs/` structure;
- a basic `tests/` structure;
- a minimal `README.ru.md`;
- the `doctor` command;
- the `version` command;
- the `routes` command;
- the `web` command as a safe placeholder/stub until Iteration 1;
- a basic logger;
- basic path helpers;
- `.gitkeep` files for `logs/` and the required `storage/` directories.

Excluded:

- Tabler templates;
- a complete FastAPI web shell;
- dashboard blocks;
- product adapters;
- auth;
- config UI;
- artifact browser;
- no-code builder.

#### Deliverable

The project installs through `uv`, runs through `./start.sh doctor`, has a reproducible `uv.lock` and release-please configuration, and provides a ready skeleton for Iteration 1.

#### Checks

- `uv sync --frozen --extra dev`
- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh version`
- `./start.sh routes`
- import smoke:
  - `python -c "import beeui_module"`

#### DoD

- the repository is no longer empty;
- `start.sh` works;
- `config/start.py` dispatch works;
- `uv.lock` is created;
- release-please configuration is added;
- tests pass;
- the project structure follows the established src-layout;
- logs/storage directories contain `.gitkeep`;
- web/UI implementation has not started before Iteration 1.

### Iteration 1 — Tabler web shell v0

**Status:** DONE

#### Goal

Set up a minimal runnable FastAPI + Jinja2 + local Tabler-compatible web shell for BeeUI demo mode so that `./start.sh web` starts a real web surface instead of a placeholder.

#### Scope

Included:

- FastAPI app factory;
- the `web` CLI command with `--host` and `--port`; optional `--reload=false` is unnecessary;
- reading `web.host`, `web.port`, `web.route_prefix`, and `web.cache_static` from `config/settings.yml`;
- Jinja2 templates with autoescape;
- package-local templates:
  - `base.html`;
  - `page.html`;
- package-local static assets:
  - `static/css/beeui.css`;
  - `static/js/beeui.js`;
  - minimal local Tabler-compatible placeholder assets if actual Tabler vendor files have not yet been added;
- a basic layout:
  - a sidebar placeholder;
  - a top navbar placeholder;
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
- tests ensuring that HTML contains no external scripts/tracking references.

Excluded:

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

`./start.sh web --host 127.0.0.1 --port 8780` starts a real BeeUI demo web shell with local static assets, renders `/`, serves `/health`, and passes route/static/security smoke tests.

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh web --host 127.0.0.1 --port 8780`
- route smoke:
  - `GET /`
  - `GET /health`
  - `GET /static/css/beeui.css`
- HTML smoke:
  - the base layout renders;
  - no external CDN/script/tracking references;
  - no secrets in HTML;
  - Jinja autoescape remains enabled.

#### DoD

- `web` is no longer a placeholder;
- the FastAPI app starts;
- the base layout renders;
- static assets are served only from the package-local static directory;
- `/health` returns safe JSON;
- route tests cover HTML, health, and static assets;
- no product-specific domain logic is added;
- no write/control surface is added.

### Iteration 2 — Declarative pages and navigation v0

**Status:** DONE

#### Goal

Add a minimal YAML-driven pages/navigation layer so that the BeeUI web shell renders pages and navigation from a declarative UI schema rather than hardcoded templates/routes.

#### Scope

Included:

- `config/schema.yml` as the demo UI schema;
- a `BeeUiConfig` model/parser for declarative UI configuration;
- fail-fast schema validation;
- navigation model;
- pages model;
- page id/path/title/subtitle;
- route generation from page configuration;
- the active navigation item;
- generic page template rendering from page configuration;
- explicit startup failure for invalid UI configuration;
- tests for valid/invalid configuration and route rendering.

Excluded:

- data sources;
- block registry;
- product adapters;
- visual builder;
- config apply;
- artifact browser;
- auth/session;
- custom page templates;
- arbitrary HTML/JS from config.

#### Config split

- `config/settings.yml` remains the runtime/system configuration.
- `config/schema.yml` becomes the declarative UI schema for demo mode.
- BeeUI must not combine runtime settings and the page/navigation schema into a single object.

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

`./start.sh web --host 127.0.0.1 --port 8780` starts BeeUI with navigation and pages rendered from `config/schema.yml`.

#### Routes

- `GET /`
- `GET /runs`
- `GET /health`
- `GET /static/...`

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh routes`
- `./start.sh web --host 127.0.0.1 --port 8780`
- valid UI configuration loads;
- missing `app.title` causes fail-fast validation;
- a duplicate page path causes fail-fast validation;
- a duplicate page ID causes fail-fast validation;
- a navigation path without a corresponding page causes fail-fast validation;
- unsafe page paths are rejected;
- the active navigation item renders;
- unknown pages return 404;
- HTML contains no external tracking scripts.

#### DoD

- page/navigation configuration works;
- invalid UI configuration fails fast;
- navigation renders without hardcoded product assumptions;
- page titles/subtitles come from configuration;
- routes are created from configuration;
- arbitrary HTML/JS from config is rejected;
- no product-specific domain logic is added.

## Stage 2 — Tabler-compatible UI foundation

### Iteration 3 — Local Tabler vendor/assets and layout parity v1

**Status:** DONE

#### Goal

Replace the minimal placeholder shell with a local Tabler-compatible foundation: package-local assets, a production-safe base layout, sidebar/navbar/page-wrapper/page-header/footer primitives, and a dark vertical operator layout.

#### Why

BeeUI should become a reusable UI layer rather than a collection of custom cards. Before introducing product adapters, establish a visual and structural foundation that is compatible with Tabler and safe for Bee products.

#### Scope

Included:

- package-local Tabler vendor assets in:

```text
src/beeui_module/static/vendor/tabler/
```

- local CSS/JS assets only;

- no external CDNs/imports/scripts;

- no PostHog/tracking;

- no `scripts.tabler.io/banner.js`;

- no demo sponsor blocks;

- no external font imports by default;

- base layout primitives:
  - vertical sidebar;
  - top navbar/header;
  - page wrapper;
  - page header;
  - page body;
  - footer;
  - responsive container;
  - active nav state;
  - collapsed/mobile sidebar behavior where supported by Tabler;

- package templates:
  - `base.html`;
  - `page.html`;
  - `components/sidebar.html`;
  - `components/navbar.html`;
  - `components/page_header.html`;
  - `components/footer.html`;
  - `components/empty_state.html`;

- dark/light compatibility through Tabler attributes;

- the demo dashboard remains read-only;

- tests prohibiting external scripts/styles/tracking references.

Excluded:

- a full copy of a Tabler demo page;
- product adapters;
- block data resolver;
- forms/config apply;
- auth/session;
- arbitrary HTML/JS injection;
- no-code builder.

#### Deliverable

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI with an actual local Tabler-compatible vertical layout instead of a basic placeholder.

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
  - Jinja autoescape is enabled.

#### DoD

- BeeUI uses local Tabler-compatible assets;
- the base layout follows the structure of the Tabler vertical layout;
- no demo/tracking/external dependencies are shipped;
- static files are served only from controlled package-local paths;
- existing demo pages continue to render;
- no product-specific domain logic is added.

### Iteration 4 — Theme, layout and navigation schema v1

**Status:** DONE

#### Goal

Add controlled schema-driven theme/layout/navigation customization so that the BeeUI visual shell is configured through `config/schema.yml` rather than manual HTML/CSS edits.

#### Why

Iteration 3 established the local Tabler-compatible vertical layout foundation, but some UI behavior is still hardcoded in templates/CSS: dark mode, branding/logo text, container size, sidebar/navbar variants, and navigation structure.

Before introducing blocks/product adapters, establish a safe schema contract so that Bee products can change appearance and navigation declaratively, without copying BeeUI templates or allowing arbitrary CSS/JS.

#### Scope

Included:

- extend `config/schema.yml`:

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
  - `primary`: a controlled palette enum only;
  - `base`: `slate`, `gray`, `zinc`, `neutral`, `stone`;
  - `font`: `sans-serif`, `serif`, `monospace`;
  - `radius`: a controlled numeric enum, such as `0`, `1`, `2`;
  - `density`: `default`, `compact`, `comfortable`;

- supported layout options:
  - `layout.type`: only `vertical` in this iteration;
  - `layout.container`: `xl`, `fluid`;
  - `layout.sidebar.variant`: `default`, `dark`;
  - `layout.sidebar.collapsed`: boolean;
  - `layout.navbar.enabled`: boolean;
  - `layout.navbar.variant`: `default`, `dark`;
  - `layout.navbar.sticky`: boolean;

- grouped navigation schema:
  - section/group heading;
  - nested children;
  - disabled items;
  - active nested item;
  - rejection of duplicate navigation paths;
  - navigation paths must match declared page paths;
  - external links are rejected by default;

- centralized safe theme rendering:
  - `data-bs-theme` is generated from the validated schema;
  - CSS classes/tokens are generated only from safe enum values;
  - no arbitrary CSS strings from config;
  - no arbitrary JS from config;
  - no persistent theme mutation through localStorage;

- documentation/test updates.

Excluded:

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

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI with theme, layout shell options, and grouped navigation controlled through validated `config/schema.yml`.

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- `./start.sh routes`
- `./start.sh web --host 127.0.0.1 --port 8780`
- valid theme/layout configuration loads;
- invalid theme modes are rejected;
- invalid primary/base/font/radius/density values are rejected;
- invalid layout types are rejected;
- unsafe/arbitrary CSS fields are rejected;
- arbitrary JS fields are rejected;
- dark mode renders;
- light mode renders;
- the primary color enum renders as a controlled class/token;
- grouped navigation renders;
- disabled navigation items render without links;
- the active nested navigation item renders;
- duplicate navigation paths are rejected;
- external navigation links are rejected unless explicitly supported in a later iteration;
- no external assets are added;
- no hidden runtime theme mutation occurs.

#### DoD

- theme/layout/navigation are schema-driven;
- the hardcoded dark default from Iteration 3 is replaced with a validated schema value;
- products can safely customize BeeUI through the schema;
- no arbitrary CSS/JS injection is possible;
- no external assets/tracking are added;
- grouped navigation works without product-specific assumptions;
- no product-specific domain logic is added;
- no new execution/write authority is added.

---

## Stage 3 — Blocks and component system

### Iteration 5 — Block registry and static dashboard blocks v1

**Status:** DONE

#### Goal

Add a reusable block registry and the first production-safe dashboard blocks so that BeeUI pages are composed from a declarative schema rather than hardcoded HTML or empty placeholders.

#### Why

After Iteration 4, BeeUI can render a schema-driven shell: theme, layout, navigation, and pages. However, pages still lack a reusable content layer: `pages[].blocks` exists only as a placeholder.

Before introducing data sources, the selector resolver, adapters, and BeeCap integration, establish a safe block contract defining:

- which block types are supported;
- how blocks are declared in the schema;
- how blocks are placed on a page;
- how the renderer registry selects a renderer;
- how invalid block configuration fails fast;
- how HTML escaping is preserved for all text values.

#### Scope

Included:

- a top-level `blocks` section in `config/schema.yml`;
- page-level block placement through the existing `pages[].blocks`;
- block model;
- block placement model;
- block registry;
- renderer registry;
- layout rows/columns using simple responsive width values;
- block ids;
- block titles/subtitles;
- static/literal block values only, without resolver expressions or adapter-backed lookups;
- empty state;
- degraded state;
- error state;
- rejection of unknown block types;
- rejection of unknown block references;
- rejection of duplicate block IDs;
- rejection of invalid block widths;
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

Excluded:

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

`./start.sh web --host 127.0.0.1 --port 8780` renders BeeUI pages composed of validated reusable blocks declared in `config/schema.yml`.

#### Checks

- valid block schemas load;
- behavior when top-level `blocks` is missing is explicitly defined and tested;
- metric cards render;
- KPI grids render;
- status cards render;
- table cards render;
- links cards render;
- alert cards render;
- text cards render;
- progress cards render;
- empty block states render;
- degraded/error states render from static schema state;
- unknown block types are rejected;
- unknown block references are rejected;
- invalid widths are rejected;
- unsafe text is escaped;
- arbitrary HTML/JS from config is rejected;
- no product-specific semantics are added;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`.

#### DoD

- blocks render from the schema;
- the renderer registry is domain-neutral;
- layout widths work;
- invalid block configuration fails fast;
- missing optional static fields do not break the page;
- arbitrary HTML/JS from config is rejected;
- no data resolver/adapter/product logic is added;
- Jinja autoescape remains enabled.

### Iteration 6 — Tabler component catalog and reusable primitives v0

**Status:** DONE

#### Goal

Create an internal component catalog and a minimal set of reusable Tabler-compatible template primitives so that future pages/blocks/admin/operator screens are composed of controlled components rather than copied HTML from Tabler examples.

#### Why

Iteration 5 added schema-driven blocks, but block templates could still begin duplicating card/table/badge/form/progress HTML.

Before introducing the data resolver, adapters, artifact browser, and configuration/operator UI, centralize safe UI primitives:

- common markup;
- naming rules;
- escaping expectations;
- allowed/prohibited component patterns;
- plugin placeholders without external JS/CDNs;
- visible catalog routes for review and visual smoke checks.

#### Scope

Included:

- internal read-only component catalog routes:
  - `/components`;
  - `/components/interface`;
  - `/components/forms`;
  - `/components/layout`;
  - `/components/extra`;
  - `/components/plugins`;

- route registration under the existing `route_prefix`;
- a component catalog navigation link in the demo schema, if consistent with current schema rules;
- reusable template primitives in `src/beeui_module/web/templates/components/primitives/` or an equivalent controlled location;
- safe sample data defined in Python or a static template context, rather than user-controlled HTML;
- catalog templates rendering examples through reusable primitives;
- no external CDNs/scripts/assets;
- no `|safe` for sample text values;
- route rendering and escaping tests.

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

Documentation:

- `docs/COMPONENTS.md`;
- component naming rules;
- allowed/prohibited components;
- safe usage examples;
- the relationship between primitives and block renderers.

Excluded:

- a full copy of the Tabler demo;
- redesign of existing block renderers from Iteration 5, except minor cleanup for reuse where necessary;
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

BeeUI provides a visible read-only component catalog and centralizes common Tabler-compatible primitives for future pages/blocks.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- component catalog routes render;
- each primitive renders with safe sample data;
- primitives containing text escape unsafe strings;
- no external scripts/styles/tracking references;
- no unsafe Jinja `|safe`;
- no broken static references;
- no product-specific semantics are added.

#### DoD

- BeeUI has visible component catalog pages;
- common Tabler-compatible primitives are centralized;
- future product pages/blocks can reuse primitives instead of copying HTML;
- plugin placeholders are inert and do not load external JS;
- unsafe/demo-only Tabler features are explicitly excluded;
- no new write/action/auth/adapter authority is added.

### Iteration 7 — Data sources and selector resolver v0

**Status:** DONE

#### Goal

Add a read-only data source abstraction and selector resolver so that BeeUI blocks can obtain values from controlled demo/static payloads through a stable resolver envelope, rather than only from hardcoded literal fields in the block schema.

#### Why

After Iteration 5, BeeUI can render static/literal blocks from `config/schema.yml`; after Iteration 6, it has reusable component primitives. Before introducing product adapters, separate:

- block layout/config;
- the data source;
- selector resolution;
- partial/missing/error state.

Otherwise, BeeCap/BeeAgent integration will begin passing product-specific fields directly into generic block renderers.

Iteration 7 establishes a safe read-only data layer v0 that can later accept adapter-backed payloads but currently works only with controlled demo/static data.

#### Scope

Included:

- a new `src/beeui_module/data/` package:
  - `models.py`;
  - `sources.py`;
  - `selectors.py`;
  - `resolver.py`;
  - `envelopes.py` or an equivalent minimal structure;

- data source model:
  - `demo`;
  - `static`;

- static source loading only from a controlled config/example path;
- in-memory demo source;
- selector syntax for nested fields:
  - `dashboard.latest_run.id`;
  - `dashboard.kpis.total_runs`;
  - `runs[0].id`, if list index support is implemented;
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
  - missing scalar values become unavailable/degraded;
  - missing list/table values become empty/degraded;
  - the page does not crash;

- extend the block schema for resolver-backed values through a controlled structure, for example:

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

or equivalent minimal naming if the current block model better supports another format;

- backward compatibility:
  - existing literal block configurations continue to work;
  - resolver-backed fields are optional;
  - no required config/settings keys unless necessary;

- tests for:
  - demo source loading;
  - static YAML/JSON source loading;
  - successful selector resolution;
  - missing selector;
  - invalid selector;
  - list selector;
  - scalar selector;
  - invalid source;
  - partial envelope;
  - stable envelope shape;
  - degraded/empty block rendering for missing data;
  - no unexpected leakage of secret-like test values;
  - rejection of arbitrary HTML/JS through data payloads.

Excluded:

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
- full migration of every block renderer if a minimal resolver-backed subset is sufficient.

#### Deliverable

BeeUI has a read-only data resolver layer, and at least a representative set of existing dashboard blocks can render values from resolver envelopes; existing literal blocks remain supported.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- demo source loading;
- static source loading;
- successful selector resolution;
- missing selector;
- invalid selector;
- list selector;
- scalar selector;
- invalid source;
- partial/error envelope shape;
- missing data renders as a degraded/empty state;
- existing pages from Iterations 5/6 continue to render;
- no external scripts/assets are added;
- no product-specific semantics are added.

#### DoD

- the resolver envelope shape is stable;
- the data resolver is read-only;
- block renderers do not know source internals;
- missing/partial data does not break page rendering;
- the existing literal block schema remains backward-compatible;
- no product adapter or product-specific assumptions are added;
- documentation explains selector syntax, source types, envelope shape, and safe usage.

---

## Stage 4 — Product integration contracts

### Iteration 8 — Product adapter contract v0

**Status:** DONE

#### Goal

Establish a generic `ProductUiAdapter` contract as the sole integration point between Bee products and BeeUI, allowing BeeCap/BeeAgent to provide dashboards/runs/artifacts/configuration/actions through a stable read-model boundary without introducing product-specific logic into BeeUI core.

#### Why

After Iteration 7, BeeUI can render a schema-driven UI and resolver-backed demo/static data. The next blocker for BeeCap/BeeAgent integration is the lack of a stable adapter contract.

Otherwise, BeeUI will begin reading product storage, configuration, or domain internals directly, creating a second source of truth and violating the rule:

```text
BeeUI renders.
The product decides.
```

Iteration 8 establishes only the contract-level integration point. Concrete BeeCap/BeeAgent adapters, routes, the artifact browser, and the embedded mount API remain for subsequent iterations.

#### Scope

Included:

- a new `src/beeui_module/adapters/` package;

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
  - an error shape with stable code/message;

- required read-only methods:
  - `get_dashboard()`;
  - `list_runs()`;
  - `get_run(run_id)`;
  - `list_artifacts(run_id)`;
  - `read_artifact(run_id, artifact_id)`;
  - `get_config_read_model()`;

- optional write/action/config methods, disabled by default:
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

- a fake adapter for tests only;

- tests for:
  - metadata;
  - dashboard;
  - runs;
  - run detail;
  - artifacts list;
  - artifact read;
  - config read-model;
  - rejection of invalid run IDs;
  - rejection of invalid artifact IDs;
  - unavailable optional methods;
  - error envelope shape;
  - verification that read-only methods do not mutate returned state;
  - absence of product-specific imports/logic.

Excluded:

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

BeeUI has a stable product integration contract and fake adapter tests. BeeCap/BeeAgent can later implement this contract without exposing product internals to BeeUI.

#### Checks

- fake adapter dashboard;
- fake adapter runs;
- fake adapter run detail;
- fake adapter artifact list/read;
- fake adapter config read-model;
- rejection of invalid run IDs;
- rejection of invalid artifact IDs;
- behavior when an optional method is unavailable;
- adapter error envelope shape;
- no mutation in read-only methods;
- no product-specific domain logic is added;
- `uv run pytest -q`.

#### DoD

- the product integration point is stable;
- BeeUI does not read product internals without an adapter;
- adapter errors are explicit and normalized;
- invalid IDs are handled safely;
- write/action/config mutation methods are unavailable until the product explicitly implements them;
- the fake adapter verifies the contract without adding BeeCap/BeeAgent dependencies;
- documentation explains the adapter boundary and non-goals.

### Iteration 9 — BeeCap adapter fixtures MVP

**Status:** DONE

#### Goal

Add a BeeCap-compatible adapter/read-model MVP using fixture data to verify that the generic `ProductUiAdapter` contract supports BeeCap dashboards/runs/artifacts without moving BeeCap trading/domain logic into BeeUI.

#### Why

After Iteration 8, BeeUI has a generic adapter contract, but it has not yet been tested against realistic BeeCap-like data: latest run, runs, artifact references, MRKT/Binance/paper partial states, and corrupted/missing artifacts.

Before introducing the embedded mount API and BeeCap dashboard parity, demonstrate that BeeUI can accept a BeeCap-shaped read-model through the adapter boundary without reading BeeCap internals directly or becoming a second source of truth.

#### Scope

Included:

- a `BeeCapUiAdapter` fixture/reference skeleton in the BeeUI test/support area or a controlled adapter module, without a dependency on the actual BeeCap package;
- a BeeCap-like dashboard read-model from fixtures;
- latest run discovery from fixture/read-model data;
- a run list from fixtures;
- run detail from fixtures;
- artifact references from fixtures;
- MRKT summary fields only when provided by the fixture/read-model;
- Binance/paper summary fields only when provided by the fixture/read-model;
- scenarios for partial/missing/corrupted artifacts;
- a scenario with no latest run;
- fixture-based tests in `tests/fixtures/beecap/`;
- `examples/beecap_embedded/beeui.yml`;
- `docs/INTEGRATION.md` with BeeCap integration boundary notes;
- documentation updates for current/future status.

Excluded:

- a dependency on/import of the actual `beecap_module`;
- full replacement of the current BeeCap web UI;
- route-level adapter injection in `create_beeui_app(...)`;
- embedded mount helper;
- generic artifact browser routes;
- direct product filesystem crawling;
- trading/profit/order calculations inside BeeUI;
- config apply;
- operator actions;
- auth/session;
- no-code builder.

#### BeeCap side

Actual BeeCap integration must later live in BeeCap, for example:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
```

BeeUI may contain only a fixture/reference adapter that verifies the contract.

#### Deliverable

BeeUI has a BeeCap-compatible fixture adapter and tests demonstrating that dashboard/runs/artifact-reference read-models can be produced through `ProductUiAdapter` without reading BeeCap internals or implementing trading logic inside BeeUI.

#### Checks

- BeeCap-like fixture dashboard;
- latest run fixture;
- runs list fixture;
- run detail fixture;
- artifact references fixture;
- MRKT partial fixture scenario;
- Binance/paper partial fixture scenario;
- a scenario with no latest run;
- corrupted artifact metadata scenario;
- rejection of invalid run IDs;
- rejection of invalid artifact IDs;
- no secret leakage;
- no path traversal;
- source fixtures are not mutated;
- no dependency on/import of `beecap_module`;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### DoD

- the BeeCap-like adapter/read-model works only through `ProductUiAdapter`;
- BeeUI contains no trading calculations;
- BeeUI does not read arbitrary BeeCap storage;
- BeeCap domain semantics remain in adapter/read-model fixtures and later in the actual BeeCap-side implementation;
- partial/corrupted/missing states are explicit;
- source fixtures remain canonical and read-only;
- documentation explains that the actual BeeCap adapter belongs to BeeCap-side integration.

### Iteration 10 — Embedded mount API v0

**Status:** DONE

#### Goal

Create a minimal stable embedded API through which BeeCap, followed by BeeAgent, can integrate BeeUI as a package dependency: load BeeUI UI configuration from a product-side file, provide product metadata and an adapter instance, and mount BeeUI under a safe route prefix without manually assembling FastAPI/Jinja/static setup.

#### Why

After Iteration 8, BeeUI has a generic `ProductUiAdapter` contract; after Iteration 9, the contract has been tested against BeeCap-shaped fixture payloads. However, BeeUI is not yet convenient to integrate into the BeeCap runtime: `create_beeui_app(...)` does not accept an adapter/config path/product metadata, and `mount_beeui(...)` is absent.

Without Iteration 10, each product will write its own BeeUI glue logic, duplicating web setup again and undermining BeeUI's purpose as a reusable UI framework.

#### Scope

Included:

- extend the public `create_beeui_app(...)` app factory;
- a new `mount_beeui(...)` helper;
- UI schema/config loading through `config_path`;
- support for an already loaded `ui_config`;
- support for already loaded `settings`;
- product metadata injection:
  - `product_id`;
  - `product_title`;
- adapter injection:
  - an adapter instance is accepted;
  - the adapter shape is validated against the minimum `ProductUiAdapter` contract;
  - the adapter is stored in `app.state.beeui_adapter`;
  - adapter metadata is stored in `app.state.beeui_product`;
- route prefix support for embedded mounts;
- static/template registration remains package-local;
- startup validation with clear errors;
- route collision guards/notes for the mount helper;
- tests for the app factory, mount helper, route prefix, static route, invalid adapters, and config path validation;
- documentation updates in `docs/WEB_UI.md`, `docs/INTEGRATION.md`, `README.ru.md`, and `docs/ROADMAP.md`.

Excluded:

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

BeeCap can create or mount a BeeUI FastAPI app through a single stable embedded API, providing product metadata, a BeeCap-side adapter instance, and a BeeCap-side `beeui.yml` config path; existing demo routes/static assets/templates continue to work.

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
- rejection of invalid adapters;
- rejection of missing/invalid config paths;
- route prefix test;
- static path test under a prefix;
- mount helper test;
- route collision rejection or an explicit safe error;
- existing demo mode remains compatible;
- no new `/api/*` route surface is added;
- no product-specific logic is added;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### DoD

- BeeCap can integrate BeeUI through a minimal public app factory or mount helper;
- embedded mode remains the MVP integration path;
- product-specific glue is minimal;
- the adapter is accepted and validated but not yet used for product rendering;
- current demo behavior remains backward-compatible;
- there are no hidden product assumptions;
- no new execution/write authority is added;
- documentation explicitly states that adapter-backed dashboard/runs/artifact rendering is later scope.

### Iteration 11 — Generic artifact browser v1

**Status:** DONE

#### Goal

Add a minimal reusable read-only artifact browser for Bee products so that BeeUI can display allowlisted product artifacts through `ProductUiAdapter` without reading product storage directly or becoming a filesystem browser.

#### Why

After Iteration 10, BeeUI can be embedded in BeeCap with an adapter, but the UI still cannot display product artifacts through that adapter.

This blocks BeeCap: dashboards and run overviews without artifact links/viewers offer little value because BeeCap operators need quick access to evidence/source artifacts: JSON, JSONL, summaries, reports, and health/runtime outputs.

Iteration 11 must provide a minimal shared artifact layer that Iteration 12 can use for BeeCap dashboard parity.

#### Scope

Included:

- a new `src/beeui_module/artifacts/` package layer;
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
- no raw filesystem path route parameters;
- read-only HTML artifact list/view routes;
- minimal read-only JSON routes for artifact list/read preview;
- route prefix compatibility;
- embedded adapter compatibility;
- graceful unavailable state when adapter is missing;
- a redaction hook placeholder without a complex policy engine;
- tests for JSON, JSONL, text, malformed, large, unsupported, invalid IDs, non-allowlisted artifacts, no mutation, and no secret leakage;
- docs update.

Proposed routes:

```text
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

Implementing `GET /runs/{run_id}/artifacts/{artifact_id}` in Iteration 11 is allowed because the HTML artifact browser would otherwise be incomplete.

Excluded:

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

BeeUI can list and preview allowlisted product artifacts through `ProductUiAdapter` in embedded mode, with safe read-only HTML/API routes and bounded previews for JSON, JSONL, and text artifacts.

#### Checks

- JSON artifact preview;
- JSONL artifact preview;
- malformed JSON handling;
- malformed JSONL row handling;
- text artifact preview;
- unsupported/binary metadata-only preview;
- large artifact preview limit;
- rejection of invalid `run_id`;
- rejection of invalid `artifact_id`;
- rejection of non-allowlisted artifacts;
- adapter missing/unavailable state;
- route prefix compatibility;
- no direct product filesystem reads;
- no mutation;
- no secret leakage;
- no imports of `beecap_module` / `beeagent_module`;
- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`.

#### Summary

Implemented:

- a new `src/beeui_module/artifacts/` package with models, preview logic, redaction, and routes;
- `ArtifactRef` and `ArtifactPreview` models;
- JSON preview through `build_preview()` with parsing from dict/list/str;
- JSONL preview with a row limit (500) and row-level warnings for malformed rows;
- text preview with a character limit (100K);
- unsupported/binary -> metadata-only preview;
- malformed JSON -> error state, no crash;
- malformed JSONL rows -> row-level warnings, no crash;
- large artifact limits (512KB for JSON/JSONL, 100K characters for text);
- safe ID validation through `validate_run_id()` and `validate_artifact_id()` in route handlers;
- read-only HTML artifact list + preview routes;
- read-only JSON API artifact list + preview routes;
- route prefix compatibility;
- embedded adapter compatibility through `request.app.state.beeui_adapter`;
- graceful unavailable state (503 HTML / JSON error) when the adapter is missing;
- redaction placeholders (`redact_value`, `redact_text`) for `secret`/`token`/`password`/`api_key`/`api_secret` and similar keys;
- 46 tests in `tests/test_artifacts.py`: redaction, preview (JSON/JSONL/text/malformed/large/unsupported), HTML routes, JSON API routes, invalid IDs, missing adapter, route prefix, security (escaping, no mutation, no write routes, no beecap import);
- embedded tests updated (expected /api/\* routes);
- documentation updated: ROADMAP, WEB_UI, INTEGRATION, README.

#### DoD

- the artifact browser is reusable and product-neutral;
- source artifacts remain canonical and read-only;
- arbitrary file access is impossible through BeeUI routes;
- corrupted artifacts render as partial/error states instead of crashing;
- large artifacts are bounded;
- the product adapter owns the allowlist and artifact resolution;
- BeeUI does not invent artifact semantics;
- documentation explicitly states that BeeCap production artifact mapping belongs to the BeeCap-side adapter.

---

## Stage 5 — Adapter-backed Product Console MVP

### Iteration 12 — Adapter-backed Product Console routes/API MVP

**Status:** DONE

#### Goal

Build a generic adapter-backed BeeUI product console MVP: dashboard, runs, run detail, venue dashboards, and a stable read-only JSON API through `ProductUiAdapter`, without product-specific domain logic in BeeUI core.

#### Why

After Iterations 10–11, BeeUI can already be embedded in a product and display artifacts through an adapter, but it is not yet a complete product console.

BeeUI currently supports:

- starting a FastAPI/Jinja/Tabler shell;
- rendering schema-driven demo/static pages;
- accepting a product adapter through `create_beeui_app(...)` / `mount_beeui(...)`;
- displaying allowlisted artifacts through an adapter.

However, BeeUI still lacks generic adapter-backed rendering for:

- dashboard;
- runs list;
- run detail;
- venue dashboards;
- a stable read-only API envelope for these read-models.

Without this iteration, BeeCap UI-25 cannot make `/beeui` practically useful without further extending BeeCap legacy templates or introducing product-specific logic into BeeUI.

Iteration 12 must provide a reusable generic console layer. BeeCap-specific metrics/calculations remain the responsibility of the BeeCap-side adapter/read-model.

#### Change level

**security-sensitive**

Rationale:

- new HTML/API routes are added;
- a stable read-only API envelope is added;
- adapter payloads begin rendering as a product console;
- route/API behavior changes;
- the operator-facing UI can influence decisions.

Security-sensitive checks are required for:

- `run_id` validation;
- `venue_id` validation;
- adapter error normalization;
- HTML escaping;
- source/evidence links;
- no mutation through GET routes;
- no secrets in HTML/API/logs.

#### Scope

**Included:**

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

- preserve existing artifact browser routes from Iteration 11:

```text
GET /runs/{run_id}/artifacts
GET /runs/{run_id}/artifacts/{artifact_id}
GET /api/runs/{run_id}/artifacts
GET /api/runs/{run_id}/artifacts/{artifact_id}
```

- introduce a generic API envelope for new read-only API routes:

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

- introduce an error envelope for new read-only API routes:

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

- extend `ProductUiAdapter` only when product-neutral read-only methods are needed:

```python
list_venues()
get_venue_dashboard(venue_id: str)
```

- route prefix compatibility;
- embedded mount compatibility;
- fake adapter / fixture adapter tests;
- docs update:
  - `docs/API_CONTRACT.md`, if present or created;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/ROADMAP.md`;
  - `README.ru.md`.

#### Out of scope

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
- dashboard route with a fake adapter;
- dashboard API with a fake adapter;
- runs route with a fake adapter;
- runs API with a fake adapter;
- run detail route with a fake adapter;
- run detail API with a fake adapter;
- venue dashboard route with a fake adapter;
- venue dashboard API with a fake adapter;
- artifact routes continue to work;
- invalid `run_id` is rejected;
- invalid `venue_id` is rejected;
- adapter missing/unavailable state;
- adapter error envelope;
- adapter partial envelope;
- malformed adapter payloads render as degraded/error states;
- route prefix compatibility;
- embedded mount compatibility;
- source/evidence links render safely;
- HTML autoescape is preserved;
- no mutation occurs through GET routes;
- no secrets in HTML/API/logs;
- no external assets/scripts are added;
- no imports of `beecap_module` / `beeagent_module`.

#### DoD

- BeeUI has adapter-backed dashboard/runs/run detail/venue pages;
- server-rendered UI and JSON API are consistent;
- the API envelope is stable and documented;
- the product adapter remains the sole source of product semantics;
- BeeUI does not invent product metrics;
- BeeUI does not read product storage directly;
- BeeUI remains read-only;
- no product-specific logic is added to BeeUI core;
- BeeCap UI-25 can proceed solely by implementing BeeCap-side read-models.

### Iteration 12.1 — Adapter-backed Tabler dashboard blocks renderer

**Status:** DONE

#### Goal

Add a generic renderer for adapter-backed `layout[]` blocks to BeeUI so that product adapters can provide structured dashboard/run/venue page compositions and BeeUI can render them as a complete Tabler operator console without product-specific logic in BeeUI.

#### Why

After the adapter-backed Product Console MVP, BeeUI can obtain dashboard/runs/run detail/venue payloads through `ProductUiAdapter`, but primary pages may look like generic/debug payloads. This blocks the BeeCap MVP after the route switch: data and routes exist, but the operator cockpit is not yet achieved.

BeeUI needs a reusable visual layer:

- Tabler grid/cards/tables/badges/alerts;
- compact operator blocks;
- degraded/empty/partial states;
- source/evidence links;
- a raw/debug fallback panel only when structured layout is absent.

BeeCap/BeeAgent retain ownership of product semantics. BeeUI only renders.

#### Change level

**security-sensitive**

Security-sensitive checks are required for:

- HTML escaping;
- source links;
- adapter-provided URLs/labels;
- route/API exposure;
- invalid/malformed block payloads.

#### Scope

**Included:**

- support the optional `layout` field in adapter-backed payloads;
- render `layout[]` on:
  - `/`;
  - `/runs`;
  - `/runs/{run_id}`;
  - `/venues/{venue_id}`;
- retain the current generic payload renderer as a fallback;
- add generic block renderers:
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
- support safe width mapping to Tabler/Bootstrap column classes;
- render malformed/unsupported blocks as degraded alerts rather than crashing;
- preserve API envelopes and existing route behavior;
- add tests for block rendering/fallback/security;
- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`.

**Excluded:**

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

BeeUI renders adapter-provided `layout[]` as product-grade Tabler dashboard pages, while products retain all domain-specific metrics and semantics in their adapters/read-models.

#### DoD

- a fake adapter renders `/`, `/runs`, `/runs/{run_id}`, and `/venues/{venue_id}` through `layout[]`;
- every supported block type has tests;
- unsupported/malformed blocks render an explicit degraded state;
- the existing generic renderer continues to work when `layout` is absent;
- adapter text is escaped;
- source links are safe internal links only;
- no external assets/scripts;
- no mutation through GET routes;
- no secrets in HTML/API/logs;
- documentation describes the `layout[]` block contract.

### Iteration 12.2 — Tabler visual parity hardening for adapter-backed console

**Status:** DONE

#### Goal

Bring the adapter-backed BeeUI product console to a visually usable Tabler-grade MVP: dashboard/runs/run detail/venue pages should look like a readable operator console rather than cramped generic/debug cards.

#### Why

Iteration 12.1 added a `layout[]` renderer for adapter-backed pages, but the actual BeeCap embedded result remains visually unacceptable:

- KPI/metric blocks run together as inline text;
- cards/tables/badges lack a clear visual hierarchy;
- the root dashboard and venue pages do not look like a Tabler operator cockpit;
- the current result does not meet the goal of “product-grade Tabler dashboard pages”;
- BeeCap UI-28 Config/Admin/Controls cannot be built on a weak UI foundation.

BeeUI must own rendering/layout/templates/static assets/common UI. BeeCap must provide only adapters/read-models/artifacts/callbacks.

#### Change level

**security-sensitive**

Rationale:

- operator-facing HTML rendering changes;
- the visual contract of adapter-backed routes changes;
- adapter-provided payloads become the basis for operator decisions;
- route/API contracts are preserved, but HTML behavior changes substantially.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links;
- no secrets in HTML/API/logs;
- no external CDNs/scripts/tracking;
- no provider/broker/runtime calls;
- no mutation through GET routes.

#### Scope

**Included:**

- align the shell with the Tabler-compatible structure:
  - `.page`;
  - `.navbar.navbar-vertical`;
  - `.page-wrapper`;
  - `.page-header`;
  - `.page-body`;
  - `.container-xl`;
  - `.row.row-deck.row-cards`;

- inspect and fix the local Tabler asset layer:
  - replace the basic compatibility placeholder with reviewed local compiled Tabler core assets;
  - do not use CDNs;
  - do not include Tabler preview/demo telemetry, sponsors, PostHog, or marketing/demo scripts;

- improve rendering of current adapter-backed block types:
  - `hero_snapshot`;
  - `metric_card`;
  - `kpi_strip`;
  - `venue_summary_grid`;
  - `mode_cards`;
  - `status_table`;
  - `event_table`;
  - `attention_list`;
  - `artifact_links`;
  - `raw_json_panel` only as an explicit fallback/debug block;

- make primary pages visually usable above the fold:
  - `/`;
  - `/runs`;
  - `/runs/{run_id}`;
  - `/venues/mrkt`;
  - `/venues/binance`;

- preserve product-neutral rendering:
  - no MRKT/Binance/BeeCap-specific calculations inside BeeUI;
  - product semantics only from adapter payloads;

- preserve current API envelopes and route behavior;

- add visual contract tests:
  - Tabler layout/card/table classes;
  - no raw/debug panel when `layout[]` is present;
  - unsafe text is escaped;
  - unsafe/external links are rejected or rendered inert;
  - malformed/unsupported blocks render as degraded alerts;

- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `README.ru.md`, if the asset/component contract changes.

**Excluded:**

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

The BeeUI adapter-backed product console renders as a credible Tabler operator MVP.

Expected visual behavior:

- the dashboard has a readable cockpit layout above the fold;
- KPI strips render as cards/stat cells rather than collapsed inline text;
- tables render inside proper cards;
- statuses use visible badges/alerts/dots;
- venue pages are readable without opening raw JSON;
- unsupported/malformed blocks degrade visibly without crashing;
- primary pages do not show raw/debug panels when structured `layout[]` is present.

Expected routes for verification:

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

BeeUI route smoke checks:

```text
GET /
GET /runs
GET /runs/{fixture_run_id}
GET /venues/mrkt
GET /venues/binance
GET /static/css/beeui.css
GET /static/vendor/tabler/...
```

BeeCap embedded smoke checks after a local dependency update:

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
- no product `storage/` mutation through GET routes.

#### DoD

- BeeUI visually meets the practical Tabler operator console baseline;
- fake adapter pages render through `layout[]`;
- BeeCap embedded pages are visually suitable for daily read-only monitoring;
- all supported layout block types have tests;
- unsupported/malformed blocks render an explicit degraded state;
- adapter text remains escaped;
- adapter links are safe internal links only;
- no external assets/scripts/tracking;
- no mutation through GET routes;
- no secrets in HTML/API/logs;
- no product-specific logic is added to BeeUI core;
- documentation describes visual/layout hardening and asset policy.

### Iteration 12.3 — Chart layout block package/rendering integrity

**Status:** DONE

#### Goal

Resolve the inconsistency in BeeUI's adapter-backed `layout[]` block contract: when a product adapter provides a `chart` block type, BeeUI must render it safely through a package-local template or explicitly degrade without `500 TemplateNotFound`.

#### Why

After Iterations 12.1/12.2, BeeUI is the canonical renderer for BeeCap adapter-backed pages. BeeCap may provide chart-like blocks for run/venue/operator dashboards. If `chart` is declared in the renderer/API contract but its template is missing from the wheel, embedded product pages fail with `500`, blocking BeeCap → BeeUI production parity.

#### Change level

**security-sensitive**

Security-sensitive checks are required for:

- adapter-provided chart payload escaping;
- safe internal source links;
- no external CDNs/scripts;
- package-local static/template integrity;
- no mutation through GET routes.

#### Scope

**Included:**

- inspect the actual contract:
  - `layout_renderer.py`;
  - `layout_block.html`;
  - contents packaged wheel;
  - tests;
- if `chart` is supported by the renderer/API:
  - add `components/layout/chart.html`;
  - wire `chart` into `layout_block.html`;
  - add a safe degraded/empty state;
  - add HTML rendering tests;
  - add a package/template integrity test;
- if `chart` should not be supported:
  - remove `chart` from supported block types/documentation/tests;
  - unsupported `chart` must render as a degraded block rather than crash;
- update documentation:
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/ROADMAP.md`.

**Excluded:**

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

The BeeUI package renders or safely degrades `chart` layout blocks without `TemplateNotFound`, and wheel/package tests ensure that required templates are included.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;
- a fake adapter page with a `chart` block returns `200`;
- unsafe chart titles/labels are escaped;
- missing/empty chart data renders an empty/degraded card;
- no external CDNs/scripts/assets;
- no secrets in HTML/API/logs;
- the package template exists in the installed package/wheel context.

#### DoD

- the `chart` block contract is consistent across the renderer, templates, documentation, and tests;
- no `500 TemplateNotFound` for adapter-provided chart blocks;
- unsupported/malformed chart payloads degrade visibly;
- BeeUI remains product-neutral;
- no product-specific chart semantics are added;
- documentation reflects the actual supported block behavior.

### Iteration 12.4 — Operator console block primitives parity

**Status:** DONE

#### Goal

Add enough product-neutral operator console block primitives to BeeUI for BeeCap/BeeAgent to build complete read-only dashboards through adapter-provided `layout[]`, without returning to product-owned Tabler templates or introducing product-specific logic into BeeUI.

#### Why

After Iterations 12.1/12.2/12.3, BeeUI can render adapter-backed `layout[]` and safely handle `chart` blocks, but the current block set is still insufficient for actual operator console parity:

- the root dashboard cannot compactly display a system snapshot, venue cards, modes, KPIs, and attention hierarchy;
- venue pages lack dedicated generic state/KPI/link sections;
- the runs page lacks a complete operator table with run/event/artifact columns;
- BeeCap parity is starting to require extensions to BeeCap legacy templates, which contradicts BeeUI's purpose.

BeeUI must own reusable rendering primitives. The product adapter must own product semantics and metrics.

The core rule remains:

```text
BeeUI renders.
The product decides.
```

#### Change level

**runtime-risk**

Rationale:

- the adapter-backed `layout[]` presentation contract expands;
- operator-facing HTML rendering changes;
- new block types/templates are added;
- adapter-provided payloads influence operator decisions.

Security-sensitive checks are required for:

- HTML escaping;
- adapter-provided labels/values/statuses/hints;
- safe internal links only;
- malformed/unsupported block degradation;
- no external CDNs/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation through GET routes.

#### Scope

**Included:**

- add new adapter-backed `layout[]` block types:

```text
operator_hero
venue_card
kpi_grid
state_grid
quick_links
run_table
```

- improve existing adapter-backed blocks where needed:

```text
mode_cards
attention_list
chart
```

- preserve existing block types:

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

- add package-local templates:

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

- use local Tabler-compatible markup patterns:
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

- use uploaded Tabler examples only as visual references for safe local patterns;

- do not copy entire Tabler preview/demo pages;

- do not include PostHog, preview/demo scripts, sponsor/marketing blocks, remote fonts, remote OG/meta assets, or external CDNs;

- keep all assets package-local;

- preserve Jinja autoescape;

- do not use `|safe` for adapter-provided values;

- links remain internal-only:
  - allow `/...`;
  - reject `//...`;
  - reject `http://...`;
  - reject `https://...`;
  - reject schemes such as `javascript:` / `mailto:`;
  - reject traversal/control characters;

- missing display values render as `n/a`, not `None`;

- malformed blocks render as `degraded`, not `500`;

- update documentation:
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `README.md`;
  - `docs/ROADMAP.md`.

**Excluded:**

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
- full ApexCharts integration unless vetted local assets already exist and tests demonstrate no external network references.

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

BeeUI provides a product-neutral operator console block set sufficient for BeeCap read-only parity without adding BeeCap-specific templates or logic to BeeUI.

Expected result:

- the dashboard can render a system snapshot, KPI cards, venue cards, and modes;
- venue pages can render an operator hero, KPI grid, current state, venue state, attention, and quick links;
- the runs page can render a dense run/event/artifact table;
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
- each new block renders through a fake adapter HTML route;
- unsafe text is escaped;
- external links do not render as active links;
- missing values render as `n/a`;
- malformed payloads degrade without `500`;
- `run_table` renders the required columns;
- `mode_cards` safely supports count/latest/latest_href/href;
- `chart` remains package-local and does not load external JS/CDNs;
- the package template integrity test covers every include in `layout_block.html`;
- no product-specific imports:
  - no `beecap_module`;
  - no `beeagent_module`;

- no external references in production templates/static assets:
  - no `posthog`;
  - no `scripts.tabler.io`;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
  - no remote font imports;

- no `|safe` for adapter-provided fields.

Route smoke checks:

```text
GET /
GET /runs
GET /venues/mrkt
GET /venues/binance
GET /static/vendor/tabler/css/...
GET /static/css/beeui.css
```

#### DoD

- the new operator block contract is implemented, documented, and tested;
- BeeUI remains product-neutral;
- BeeCap/BeeAgent semantics remain behind product adapters;
- existing adapter-backed routes/API envelopes remain compatible;
- no product-specific logic is added;
- no direct product storage reads are added;
- no provider/broker/runtime calls are added;
- no external assets/scripts/tracking are added;
- secrets do not appear in HTML/API/logs;
- malformed/unsupported blocks degrade visibly;
- documentation reflects the actual supported block behavior;
- BeeCap can continue parity work by enriching product-side `layout[]`.

### Iteration 12.5 — Page block reference schema compatibility hotfix

**Status:** DONE

#### Goal

Fix BeeUI embedded startup compatibility for product-side `beeui.yml` so that `pages[].blocks[]` supports page-level block reference objects of the form `{id: str, enabled?: bool}` alongside the existing block placement format, without sanitization, config mutation, or fallback to the product's legacy UI.

#### Why

After Iteration 12.4, BeeUI has enough operator console blocks, but canonical BeeCap BeeUI startup may fail schema validation before rendering adapter-backed pages:

```text
pages[0].blocks[0] contains unsupported keys: enabled, id
```

As a result, the BeeCap root app enables legacy fallback, `/` serves legacy templates again, and BeeUI navigation/route parity is not verified.

This is not a BeeCap read-model or layout renderer issue. The BeeUI schema validator is incompatible with the product-side page block reference format that BeeCap uses to filter/order generated `layout[]`.

#### Change level

**runtime-risk**

Rationale:

- BeeUI UI schema/config validation changes;
- embedded app startup behavior changes from fallback/failure to successful BeeUI initialization;
- product canonical UI route behavior depends on successful `beeui.yml` loading;
- operator-facing root routes must stop falling back to the legacy UI.

Security-sensitive checks are required for:

- config validation boundaries;
- no arbitrary keys in `pages[].blocks[]`;
- no config mutation/sanitization;
- no secrets in logs;
- no hidden fallback paths;
- no unsafe links.

#### Scope

**Included:**

- extend BeeUI schema validation for `pages[].blocks[]` to support block reference objects:

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - id: system_snapshot
        enabled: true
```

- preserve the existing supported placement format, if present, for example:

```yaml
pages:
  - id: dashboard
    path: /
    blocks:
      - block: latest_run
        width: 3
```

- `id` must be a safe identifier / block reference string;
- `enabled` optional, boolean, default behavior equivalent to enabled;
- unknown keys in page block references must continue to fail fast;
- invalid `id` / invalid `enabled` must fail fast;
- do not strip `pages[].blocks`;
- do not generate `.beeui_sanitized.yml`;
- do not mutate `config/beeui.yml`;
- BeeUI must start directly with product-side `config/beeui.yml`;
- add regression tests for the error:

```text
pages[0].blocks[0] contains unsupported keys: enabled, id
```

- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/API_CONTRACT.md` or `docs/WEB_UI.md`, whichever owns the page/block config contract;
  - `README.ru.md`, if it lists supported embedded config behavior.

**Excluded:**

- BeeCap-specific metrics/calculations;
- changes to BeeCap `read_model.py`;
- restoring the sanitization stub `_page["blocks"] = []`;
- sanitized config generation;
- legacy removal;
- auth/session/config apply/operator actions;
- new block renderers;
- provider/broker/runtime calls;
- new dependencies;
- changes to `pyproject.toml.version`.

#### Deliverable

BeeUI accepts product-side `beeui.yml` with page block references of the form `{id: str, enabled?: bool}` and starts successfully in embedded mode without falling back to a legacy-only UI.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Regression tests:

- a valid `pages[].blocks[]` entry with `{id, enabled}` loads;
- valid `{id}` without `enabled` loads;
- valid existing `{block, width}` placement continues to load;
- an invalid extra key in `{id, enabled}` fails fast;
- an invalid non-string `id` fails fast;
- an invalid non-bool `enabled` fails fast;
- the config loader does not mutate source config;
- no sanitized config file is created.

Embedded BeeCap verification after the dependency update:

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
- no new `BeeUI initialization failed` log entry;
- BeeUI root HTML contains no links to `/legacy`;
- `/legacy` may remain mounted only as an explicit compatibility fallback.

#### DoD

- the `pages[].blocks[]` schema contract is compatible with product-side BeeUI configuration;
- BeeUI startup no longer fails on `{id, enabled}` block references;
- the existing schema block placement contract remains backward-compatible;
- invalid block reference objects still fail fast;
- no config mutation/sanitization is added;
- BeeUI remains product-neutral;
- BeeCap can continue using product-side `read_model.py` to interpret `id/enabled`;
- tests and documentation reflect the actual supported config behavior.

---

## Stage 6 — Operator console contracts and security foundation

### Iteration 13 — Auth/session/CSRF boundary for config/action routes MVP

**Status:** DONE

#### Goal

Add a minimal reusable auth/session/CSRF boundary for BeeUI config/action POST routes so that product-owned configuration apply and operator action callbacks cannot be invoked without explicit operator authentication, role checks, and CSRF protection.

#### Why

After BeeCap UI-28, BeeUI/BeeCap config/admin/action parity has reached a local MVP: configuration preview/apply and action preview/execute go through product adapter callbacks, with validation, backup, and audit on the product side.

However, POST routes without auth/session/CSRF cannot be considered customer/public-safe:

```text
POST /api/config/preview
POST /api/config/apply
POST /api/actions/preview
POST /api/actions/execute
```

Even when product callbacks remain bounded, BeeUI must protect the transport boundary because it owns the generic web shell, browser routes, session model, and CSRF checks.

This iteration closes the security gap between a local/operator-only MVP and a remotely exposed operator console.

#### Change level

**security-sensitive**

Rationale:

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

**Included:**

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
- fail-fast startup validation when auth is enabled but required secret/token environment variables are missing;
- protection for:
  - `POST /api/config/preview`;
  - `POST /api/config/apply`;
  - `POST /api/actions/preview`;
  - `POST /api/actions/execute`;

- role checks:
  - `viewer`: read-only;
  - `operator`: action preview/execute only when permitted by the product callback;
  - `admin`: configuration preview/apply and admin/config flows;

- safe unauthenticated responses:
  - HTML redirect or `401`;
  - API `401` envelope;

- safe unauthorized responses:
  - API `403` envelope;

- baseline security headers for auth/config/action pages;
- no default secrets in the repository;
- no secrets in HTML/API/logs;
- tests for auth disabled/enabled modes, login/logout, CSRF, role denial, allowed flows, and callback dispatch;
- docs update:
  - `docs/ROADMAP.md`;
  - `docs/SECURITY.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `README.ru.md`.

**Excluded:**

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

BeeUI protects config/action POST routes through reusable auth/session/CSRF checks while retaining product authority behind adapter callbacks.

Expected behavior:

- auth disabled works only when explicitly configured as local/dev mode;
- auth enabled without required secret/token configuration fails fast;
- unauthenticated POST requests are rejected;
- missing/invalid CSRF is rejected;
- viewers cannot mutate configuration or execute actions;
- admin/operator roles are enforced;
- product callbacks remain the sole execution boundary;
- secrets do not appear in HTML/API/logs;
- the BeeCap web console can move from local/operator-only to customer-safe deployment after adopting this BeeUI version.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- auth disabled mode must be explicit;
- auth enabled without a session secret fails fast;
- auth enabled without an operator/admin token fails fast;
- login success;
- login failure;
- logout clears the session;
- unauthenticated POST requests are rejected;
- missing CSRF is rejected;
- invalid CSRF is rejected;
- valid CSRF is accepted;
- viewer denied config apply;
- viewer denied action execute;
- admins may preview/apply configuration when permitted by the adapter;
- operators may preview/execute actions when permitted by the adapter;
- adapter denial still returns an explicit denied envelope;
- product callbacks are not invoked when auth/CSRF checks fail;
- no secrets in HTML/API/logs;
- no provider/broker/runtime calls from BeeUI.

#### DoD

- BeeUI owns the reusable auth/session/CSRF shell;
- config/action POST routes are protected before product callbacks are invoked;
- auth-disabled local mode is explicit and documented;
- auth-enabled mode fails fast without required secrets;
- role checks work;
- CSRF checks work;
- product callbacks remain the source of business authority;
- no product-specific logic is added to BeeUI;
- documentation clearly distinguishes local/operator-only mode from customer/public-safe mode.

### Iteration 13.1 — Dashboard layout primitives, URL tabs and locale seed

**Status:** DONE

#### Goal

Add minimal reusable BeeUI primitives for customer-friendly product dashboards: declarative block sizing, URL-driven Tabler tabs, a locale/i18n seed, and a cleaner generic dashboard fallback without raw JSON as the primary UX.

#### Why

After Iteration 12.x, BeeUI can render adapter-backed `layout[]` and operator console blocks; after Iteration 13, it has an auth/session/CSRF boundary. However, BeeAgent UI-5 and future BeeCap/BeeScan dashboards need a small reusable presentation foundation:

- products need to control block sizes without manually copying Tabler classes;
- run switchers and similar navigation need generic Tabler URL tabs rather than product-owned HTML;
- pages need a resolved locale so that products can render RU/EN labels without their own routing glue;
- the generic dashboard fallback should not look like a debug/raw JSON page.

This iteration provides reusable BeeUI UI primitives before BeeAgent integration/polish without adding product-specific semantics.

The core rule remains:

```text
BeeUI renders.
The product decides.
```

#### Change level

**runtime-risk**

Rationale:

- the schema/block placement contract changes;
- adapter-backed layout block normalization/rendering changes;
- template/context rendering behavior changes;
- locale resolution from query parameters is added;
- the operator-facing generic dashboard fallback changes;
- documentation/tests must reflect the updated UI contract.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links in tabs;
- invalid schema values;
- malformed adapter payload degradation;
- no external CDNs/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation through GET routes.

#### Scope

**Included:**

- add a reusable block layout sizing contract for schema/demo page placements:
  - existing `width: 1..12` remains supported;
  - optional `span: 1..12`;
  - optional `size: S|M|L|XL`;
  - invalid values fail fast;
  - conflicting layout keys in schema placements fail fast;
  - existing configurations remain backward-compatible;

- add layout sizing support for adapter-backed `layout[]` blocks:
  - existing `width` remains supported;
  - optional `span`;
  - optional `size`;
  - invalid/malformed adapter values safely degrade to `col-12` rather than `500`;

- supported size mapping:

```text
S  -> span 4  -> col-12 col-md-6 col-lg-4
M  -> span 6  -> col-12 col-lg-6
L  -> span 8  -> col-12 col-lg-8
XL -> span 12 -> col-12
```

- centralize width/span/size mapping in a product-neutral helper so that templates do not duplicate mapping logic;

- add a reusable Tabler-compatible URL tabs primitive/helper:
  - `ul.nav.nav-tabs.card-header-tabs`;
  - `li.nav-item`;
  - `a.nav-link`;
  - active item support;
  - regular `href` links;
  - an optional overflow dropdown for older items;
  - safe internal links only;
  - JS-only tab panes are not required;

- add a locale/i18n seed to the UI schema:

```yaml
locale:
  default: en
  available:
    - en
    - ru
```

-- locale behavior:

- the default locale comes from UI configuration;
- the `lang` query parameter can override the locale only when allowlisted;
- invalid `lang` falls back to the default;
- the resolved locale is available in templates/context;
- no persistence;
- no user settings;
- no database;
- BeeUI does not translate product-specific strings;

- cleanup generic dashboard:
  - render summary cards/sections first when structured dashboard fields are present;
  - display the raw/debug technical payload only within a clearly separated/collapsible `Technical details` section;
  - API responses remain unchanged;
  - the fallback remains useful when the adapter does not provide `layout[]`;

- docs update:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`, if the block/layout contract is documented there;
  - `README.ru.md`.

**Excluded:**

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

- schema/demo pages can use `width`, `span`, or `size` for block placement;
- adapter-backed `layout[]` blocks can use `width`, `span`, or `size`;
- invalid schema layout values fail fast;
- malformed adapter layout values degrade visibly without crashing;
- URL-driven Tabler nav-tabs can render active links and an optional overflow dropdown;
- the resolved locale is available in the request/template context;
- `?lang=ru` works when `ru` is allowlisted;
- invalid `lang` falls back safely;
- the generic dashboard fallback no longer shows raw JSON as the primary UX;
- raw technical payloads, if present, are separated into `Technical details`.

#### Checks

- `uv run pytest -q`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- valid `size: S|M|L|XL` renders the expected responsive classes;
- valid `span: 4|6|8|12` renders the expected responsive classes;
- existing `width` placements remain backward-compatible;
- invalid schema `size` fails fast;
- invalid schema `span` fails fast;
- conflicting schema layout keys fail fast;
- malformed adapter-backed `layout[]` size/span/width degrades to safe full-width rendering;
- URL-driven tabs render Tabler nav-tabs markup;
- the active tab receives `.active`;
- the overflow dropdown renders when overflow items are provided;
- unsafe/external tab links do not render as active links;
- the default locale resolves from configuration;
- `?lang=ru` resolves to `ru` when allowlisted;
- invalid `?lang=bad` falls back to the default;
- the resolved locale is available in template context;
- primary generic dashboard HTML does not expose raw JSON/debug details as the main visible section;
- technical details are separated/collapsible if raw payloads are still rendered;
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
- no mutation through GET routes;
- no secrets in HTML/API/logs.

#### DoD

- layout size primitives are implemented, documented, and tested;
- existing `width` configuration remains backward-compatible;
- invalid schema values fail fast;
- malformed adapter values degrade safely;
- the URL tab primitive is product-neutral and validates safe links;
- the locale seed is config-controlled, and query parameter overrides are allowlisted;
- BeeUI does not translate product-specific strings;
- the primary generic dashboard UX is customer-friendly rather than centered on raw/debug output;
- API envelopes remain backward-compatible;
- no product-specific logic is added;
- no direct product storage reads are added;
- no provider/broker/runtime calls are added;
- no external CDNs/scripts/tracking are added;
- documentation reflects the updated layout/tabs/locale contract.

### Iteration 13.2 — Generic adapter pages and configurable Tabler primitives

**Status:** DONE

#### Goal

Add generic adapter-backed custom pages and configurable Tabler-compatible `tabs` / `accordion` primitives to BeeUI so that BeeAgent/BeeCap can build product dashboards through `beeui.yml` + adapter read-model/layout without product-owned Jinja templates.

#### Why

After Iteration 13.1, BeeUI has sizing primitives, a URL tabs seed, and a locale seed, but BeeAgent UI-5 revealed an architectural gap:

```text
BeeAgent began creating its own Jinja templates/manual HTML dashboard.
```

This violates the target rule:

```text
BeeUI renders.
The product decides.
```

BeeUI must own the shell, templates, tabs, accordion, dashboard layout, artifact viewer, and generic pages. The product must provide only adapters/read-models/layouts/artifact allowlists/domain data.

Tabler examples also show several safe visual variants of `tabs` and `accordion`, but BeeUI must not copy entire Tabler preview pages or pull in demo scripts, PostHog, remote fonts, sponsor blocks, or external assets.

#### Change level

**runtime-risk**

Rationale:

- the UI schema/config contract changes;
- configurable component variants are added;
- generic adapter-backed custom routes are added;
- the optional adapter page read-model boundary expands;
- HTML rendering for dashboard technical details changes;
- operator-facing GET routes affect dashboard UX.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links in tabs;
- deterministic/safe accordion ids;
- route collision validation;
- invalid schema fail-fast;
- malformed adapter payload degradation;
- no external CDNs/scripts/tracking;
- no secrets in HTML/API/logs;
- no mutation through GET routes.

#### Scope

**Included:**

- add a configurable URL tabs primitive v1:
  - `ul.nav.nav-tabs.card-header-tabs`;
  - URL-driven links only;
  - active state from an allowlisted query parameter;
  - safe internal links only;
  - optional disabled items;
  - optional dropdown/overflow items;
  - no JS-only hidden panes;
  - no arbitrary HTML labels;
  - no unsafe `|safe`;

- support safe tab variants using canonical names:

```text
default
reverse
fill
icons
fill_icons
dropdown
```

- if numeric aliases are implemented, normalize them to canonical names:

```text
1 -> default
2 -> reverse
3 -> icons
4 -> dropdown
5 -> fill
6 -> fill_icons
```

Canonical documentation/config examples must use names rather than numbers.

- add a configurable accordion/collapsible primitive v1:
  - deterministic ids;
  - collapsed/open initial state;
  - single-open mode through `data-bs-parent`;
  - multi-open mode if simple and safe;
  - safe escaped titles/body;
  - no arbitrary HTML body from adapter/config;
  - no full Tabler preview copy;

- support accordion variants using canonical names:

```text
default
flush
tabs
inverted
inverted_plus
icons
```

- if numeric aliases are implemented, normalize them to canonical names:

```text
1 -> default
2 -> flush
3 -> tabs
4 -> inverted
5 -> inverted_plus
6 -> icons
```

Canonical documentation/config examples must use names rather than numbers.

- add optional component configuration defaults, for example:

```yaml
components:
  tabs:
    variant: default
  accordion:
    variant: default
```

- add optional page-level tabs configuration, for example:

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

- invalid component/page tab configuration fails fast;

- missing component configuration uses documented safe defaults;

- unknown component variants fail fast;

- unsafe/external tab links fail fast in config and degrade in adapter-provided payloads;

- replace raw `<details>` in the generic dashboard `Technical details` fallback with the BeeUI accordion/collapsible primitive;

- confirm or strengthen adapter-backed `layout[]` sizing:
  - `width: 1..12`;
  - `span: 1..12`;
  - `size: S|M|L|XL`;
  - invalid schema sizing fails fast;
  - malformed adapter sizing degrades to `col-12`;

- add generic adapter-backed custom pages v0:
  - product declares page in `beeui.yml`;
  - BeeUI registers safe GET route;
  - route must not conflict with reserved routes;
  - BeeUI calls optional adapter method, for example:

```python
get_page(page_id: str, query: Mapping[str, str])
```

- render an explicit unavailable/degraded state when the method is unavailable;

- the default base adapter returns unavailable;

- returned `layout[]` renders through the existing generic layout renderer;

- BeeUI must not know ROP/MRKT/Binance/Bitrix semantics;

- the artifact viewer remains BeeUI-owned:
  - the HTML artifact browser remains a generic BeeUI route;
  - the artifact API route remains a BeeUI-owned JSON envelope;
  - the product adapter owns the allowlist/content.

- update docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/INTEGRATION.md`;
  - `README.ru.md`, if user-facing config examples change.

**Excluded:**

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

BeeUI can render custom product pages such as `/rop` through `beeui.yml` + adapter read-model/layout, using reusable configurable Tabler-compatible tabs and accordion primitives without product-owned HTML templates.

Expected behavior:

```text
config/beeui.yml declares /rop
The BeeAgent adapter returns a page read-model/layout
BeeUI registers /rop
BeeUI renders the shell/page/tabs/accordion/cards/tables/artifacts
BeeAgent owns only domain data and the artifact allowlist
```

#### Checks

- `uv run pytest -q`;
- `uv run pytest -q -W error::UserWarning`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Automated checks:

- the tabs primitive renders `nav nav-tabs card-header-tabs`;
- every supported tab variant renders the expected safe classes;
- invalid tab variants fail fast in config;
- numeric aliases, if supported, normalize to canonical names;
- the active tab is selected only from allowlisted `active_param` values;
- invalid active tab safely falls back;
- unsafe/external tab hrefs are rejected or rendered inert;
- the accordion primitive renders local Tabler/Bootstrap markup;
- every supported accordion variant renders the expected safe classes;
- invalid accordion variants fail fast;
- deterministic accordion IDs are generated safely;
- `Technical details` uses an accordion rather than raw `<details>`;
- schema block `width/span/size` works;
- invalid schema sizing fails fast;
- malformed adapter sizing degrades to `col-12`;
- the configured custom page `/rop` renders through the adapter page method;
- an unavailable adapter page renders a degraded/empty state;
- route collisions/reserved paths are rejected;
- GET custom pages do not mutate storage/source config;
- no product-specific strings/imports in the BeeUI generic renderer;
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

- the configurable tabs primitive is implemented, documented, and tested;
- the configurable accordion primitive is implemented, documented, and tested;
- the technical details fallback uses the BeeUI accordion;
- custom adapter-backed pages work through the BeeUI generic page renderer;
- the adapter page method is optional and backward-compatible;
- existing ProductUiAdapter implementations are not broken;
- route collisions fail fast;
- invalid config fails fast;
- malformed adapter payloads degrade visibly;
- BeeUI remains product-neutral;
- the artifact viewer remains BeeUI-owned;
- no external assets/scripts/tracking are added;
- GET routes do not mutate product storage/config/artifacts;
- documentation reflects the actual config/component/page contracts.

### Iteration 13.3 — Tabler attached tabs and accordion visual parity hardening

**Status:** DONE

#### Goal

Fix the BeeUI renderer/CSS for Tabler-compatible page tabs and accordion primitives so that adapter-backed custom pages, including BeeAgent `/rop`, render without product-owned HTML templates: tabs must attach to a shared card/body, and `Technical details` must look and behave like a standard Tabler accordion with a visible chevron.

#### Why

After Iteration 13.2, BeeUI can register generic adapter-backed custom pages and configurable `tabs` / `accordion` primitives. However, actual BeeAgent UI-5 smoke checks revealed a visual/renderer gap:

- `/rop` tabs render as a separate card before page blocks;
- an external gap appears between the active `Overview` tab and the first `Run Overview` block;
- tabs are not visually attached to the card body as in Tabler examples;
- dashboard `Technical details` looks like a large static row;
- the chevron/accordion affordance is not visible;
- users cannot tell that the block is expandable.

This must not be fixed in BeeAgent through product-owned Jinja templates. BeeAgent must provide only config/read-model/layout. BeeUI must own the shell, tabs, accordion, page renderer, CSS, and Tabler-compatible primitives.

The core rule remains:

```text
BeeUI renders.
The product decides.
```

#### Change level

**runtime-risk**

Rationale:

- the BeeUI page renderer HTML structure changes;
- rendering behavior for configured page tabs changes;
- accordion primitive markup/CSS changes;
- the operator-facing UI for adapter-backed product pages changes;
- current BeeAgent UI-5 routes depend on BeeUI renderer output.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links in tabs;
- deterministic/safe accordion ids;
- no external CDNs/scripts/tracking;
- no product-specific imports;
- no unsafe Jinja `|safe`;
- no mutation through GET routes;
- no secrets in HTML/API/logs.

#### Scope

**Included:**

- fix page-level tab placement in the BeeUI renderer:
  - when a page has configured tabs, render tabs and page blocks within one card;
  - use a Tabler-compatible structure:

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

- remove the standalone tabs card pattern before page blocks:

```html
<div class="card mb-3">...</div>
<section aria-label="Page blocks">...</section>
```

- page title/subtitle must remain above the tabs card;

- tabs must not overlap the subtitle;

- no external margin gap between the tabs header and page blocks;

- normal `card-body` padding is allowed;

- standard Tabler grid spacing remains between blocks within the body;

- active and disabled tab behavior must be preserved;

- `?tab=overview|queue|sources|attachments|evidence` must work as before;

- invalid tab fallback must work as before;

- route prefix support must be preserved;

- fix `Technical details` accordion rendering:
  - use standard Tabler-compatible accordion markup;
  - `Technical details` must be a `button.accordion-button collapsed`;
  - the chevron must be visible on the right through `.accordion-button-toggle`;
  - use a local inline SVG chevron or an existing BeeUI icon primitive;
  - do not use external icons/CDNs;
  - do not use `accordion-tabs` for technical details;
  - font size must match accordion button/card text rather than page titles;
  - preserve accessibility attributes:
    - `type="button"`;
    - `data-bs-toggle="collapse"`;
    - `data-bs-target`;
    - `aria-expanded`;
    - `aria-controls`;

- add/update CSS only in the BeeUI static layer if Tabler markup alone is insufficient;

- add regression tests for HTML structure and safety;

- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`, if it describes the tabs/accordion/page contract.

**Excluded:**

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

BeeUI renders configured page tabs and the technical details accordion with a Tabler-compatible visual structure:

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

- a configured page with tabs renders `beeui-page-tabs-card`;
- tabs and `section aria-label="Page blocks"` are inside one card;
- no standalone tabs card `<div class="card mb-3">` before page blocks;
- the page title renders before tabs;
- the page subtitle renders before tabs;
- the first page block renders inside `.beeui-page-tabs-card .card-body`;
- the active tab still receives `.active`;
- disabled tabs remain disabled/inert;
- invalid tab queries fall back safely;
- `route_prefix` tab hrefs continue to work;
- `Technical details` renders inside `.accordion`;
- `Technical details` uses `.accordion-button.collapsed`;
- `Technical details` contains `.accordion-button-toggle`;
- `Technical details` does not use `accordion-tabs`;
- accordion IDs are deterministic and safe;
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

- GET routes do not mutate storage/config/artifacts.

BeeAgent embedded smoke checks after the BeeUI update:

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

- `/rop` tabs are visually attached to the page blocks card;
- no external gap between the tabs header and the first block container;
- normal spacing remains between blocks within the card body;
- `Technical details` has a visible chevron and a normal accordion font size;
- BeeAgent still has no product-owned HTML templates.

#### DoD

- the renderer for page tabs attached to a shared card is implemented, documented, and tested;
- the `Technical details` accordion uses Tabler-compatible markup with a visible chevron;
- BeeUI remains product-neutral;
- BeeAgent retains only config/read-model/layout/artifact allowlist;
- no BeeAgent HTML templates are added;
- no external assets/scripts/tracking are added;
- no unsafe Jinja `|safe` is added;
- secrets do not appear in HTML/API/logs;
- GET routes do not mutate product storage/config/artifacts;
- documentation reflects actual tabs/accordion/page rendering behavior;
- BeeAgent UI-5 can proceed after a dependency update and smoke verification.

### Iteration 13.4 — Generic layout groups, KPI grid columns, and page spacing normalization

**Status:** DONE

#### Goal

Extend BeeUI's product-neutral layout renderer so that adapter-backed pages can express both flat Tabler dashboard rows and simple nested layout groups without product-owned Jinja templates or product-specific CSS.

This iteration follows It13.3.

It13.3 fixed Tabler visual parity for attached page tabs and accordion rendering. Analysis of Tabler dashboard layout patterns identified one more generic layout capability needed before BeeAgent UI-5 can be closed cleanly:

- consistent page-body spacing across dashboard/custom/modules/runs rendering paths;
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

BeeUI currently has generic blocks and outer `width/span/size` handling, but needs a small product-neutral way to express grouped blocks within a column.

This must remain generic:

- BeeUI renders layout primitives;
- product adapters decide which domain blocks appear and where;
- BeeUI must not know ROP, BeeAgent, BeeCap, MRKT, Binance, Bitrix, or other product semantics;
- BeeAgent must not add product-owned Jinja templates to solve layout issues.

#### Scope

Included:

- audit the current BeeUI implementation before making changes.
- normalize page-body spacing across relevant rendering paths:
  - adapter-backed dashboard `/`;
  - custom adapter pages such as `/rop`;
  - modules/custom page `/modules`;
  - runs page `/runs`;
  - pages with tabs;
  - pages without tabs.

- ensure all relevant pages use a Tabler-compatible structure equivalent to:

```html
<div class="page-header d-print-none">
  <div class="container-xl">...</div>
</div>

<div class="page-body">
  <div class="container-xl">...</div>
</div>
```

- add optional product-neutral `kpi_grid.columns` support.
- supported `kpi_grid.columns` values:

```text
1 -> col-12
2 -> col-12 col-sm-6
3 -> col-12 col-sm-6 col-lg-4
4 -> col-12 col-sm-6 col-lg-3
```

- the default `kpi_grid.columns` remains `4`.
- invalid adapter-provided `columns` values safely degrade to the default rather than `500`.
- invalid schema/config `columns` values fail fast if schema-backed blocks accept the field.
- add generic bounded layout group support.
- Layout group v1 supports:
  - `type: group`;
  - `width` / `span` / existing size handling at the outer level;
  - `direction: vertical` initially;
  - `children` containing normal BeeUI layout block items;
  - Tabler-compatible nested `row row-cards`;
  - children rendered through the existing block renderer.

- layout groups must be product-neutral and must not hardcode domain labels such as `Run Overview`, `Key Metrics`, `ROP`, `BeeAgent`, `BeeCap`, `MRKT`, `Binance`, or `Bitrix`.
- add regression tests for:
  - flat `6 + 3 + 3` layout;
  - flat `3 + 3 + 3 + 3` layout;
  - nested `6 group + 6 block` layout;
  - KPI grid columns;
  - page spacing;
  - tabs still attached to page blocks;
  - safe degradation for malformed adapter payloads;
  - escaping and no unsafe external references.

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
- changes to `pyproject.toml.version`.
- changes to `uv.lock` unless dependencies unexpectedly change; this is not expected.

#### Layout contract

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

#### Acceptance

- Existing tests remain green.
- `/`, `/rop`, `/modules`, and `/runs` return `200` in relevant tests/smoke checks.
- Pages with tabs keep tabs and page blocks within one attached Tabler card.
- Pages without tabs preserve normal page block rendering.
- Page content spacing after the subtitle/header is consistent across dashboard/custom/modules/runs rendering paths.
- `kpi_grid.columns=1` renders KPI items with `col-12`.
- `kpi_grid.columns=2` renders KPI items with `col-12 col-sm-6`.
- `kpi_grid.columns=3` renders KPI items with `col-12 col-sm-6 col-lg-4`.
- `kpi_grid.columns=4` renders KPI items with `col-12 col-sm-6 col-lg-3`.
- Missing `kpi_grid.columns` preserves current/default behavior.
- Invalid adapter-provided `kpi_grid.columns` safely degrades to the default.
- Invalid schema/config-backed `columns` fails fast if the schema supports the field.
- Generic `group` layout renders nested `row row-cards` within the parent column.
- Group children render through existing BeeUI block rendering.
- Malformed adapter-provided group payloads degrade visibly and safely rather than returning `500`.
- Unsafe labels/values remain HTML-escaped.
- No external CDNs/scripts/tracking are added.
- No product-specific imports or domain logic are added to `src/beeui_module`.
- No unsafe Jinja `|safe` is added.
- GET routes do not mutate storage/config/artifacts.
- `pyproject.toml.version` remains unchanged.
- `uv.lock` remains unchanged unless dependencies explicitly change; this is not expected.

#### Checks

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

Smoke checks:

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

#### DoD

- The current implementation has been audited first.
- Existing behavior is not duplicated.
- Generic layout group v1 is implemented or confirmed unnecessary by code evidence.
- KPI grid columns are implemented or confirmed already present.
- Page-body spacing is normalized or confirmed already centralized.
- Tests cover flat layouts, nested groups, KPI columns, spacing, escaping, and safety behavior.
- Documentation reflects the actual supported block/layout contract.
- Required checks have been completed.
- No product-specific BeeUI code is added.
- No new dependencies are added.
- The version is unchanged.
- `uv.lock` is unchanged.
- The PR is ready for review.

### Iteration 13.5 — Product console route metadata and navigation compatibility

**Status:** DONE

#### Goal

Fix BeeUI config validation and custom page registration so that product-side `beeui.yml` can describe metadata, titles, subtitles, tabs, navigation, and block/layout references for existing product console routes such as `/venues/mrkt` and `/venues/binance`, without BeeUI attempting to register those paths as generic custom routes.

This iteration preserves canonical product routes unchanged:

```text
/venues/mrkt
/venues/binance
/modes/dry-run
/modes/paper
/modes/live
```

BeeUI must distinguish between:

```text
safe internal path
  used for navigation links, tabs, links, and page metadata

custom route path
  used only when BeeUI registers a new adapter-backed custom page route
```

#### Why

After Iteration 13.4, BeeUI supports product-neutral layout groups, KPI grid columns, and normalized page spacing. BeeCap/BeeAgent can now describe richer operator pages through `beeui.yml`.

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

This is correct only for generic custom route registration. It is incorrect for:

- page metadata for an existing product console route;
- sidebar navigation links to existing internal routes;
- page tabs/hrefs/links pointing to existing internal routes.

This blocks BeeCap canonical route parity and encourages incorrect workarounds such as `/mrkt`, `/binance`, or product-owned templates.

The core rule remains:

```text
BeeUI renders.
The product decides.
```

#### Context

Two distinct concepts were conflated:

| Concept                                    | Purpose                                                                  | Can use `/venues/mrkt` |
| ------------------------------------------ | ------------------------------------------------------------------------ | ---------------------: |
| `pages[]` as a generic custom page route   | BeeUI registers a new route and calls `adapter.get_page(page_id, query)` |                     No |
| `pages[]` as product console page metadata | BeeUI stores title/subtitle/tabs/block references for an existing route  |                    Yes |
| `navigation[].path`                        | Sidebar/internal link to an existing internal route                      |                    Yes |
| `tabs[].href` / layout links               | Safe internal links                                                      |                    Yes |
| Custom route registration                  | Only non-reserved paths such as `/rop`, `/reports`, `/modules`           |     No for `/venues/*` |

#### Scope

**Included**

- separate path validation into two product-neutral concepts:
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
  - paths without a leading `/`;
  - protocol-relative paths `//...`;
  - external URLs;
  - `?` / `#` in raw path fields where they are not expected;
  - backslashes;
  - control characters;
  - traversal segments `.` / `..`;
  - unsafe path segments.

- Custom route path validation must keep BeeUI/system/product-console-owned routes reserved.

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

- `/venues/*` must be allowed as page metadata/navigation but must not be registered as a generic custom page route.

- `/runs/*` must not be registered as a generic custom page route because run detail routes are product console routes.

- Non-reserved custom pages such as `/rop`, `/modules`, `/reports`, and `/settings-lite` must continue to register as adapter-backed custom pages.

- preserve duplicate path detection for `pages[]`.

- preserve route collision protection for actual custom pages.

- preserve fail-fast validation for unsafe paths.

- preserve route prefix and embedded mount compatibility.

- update tests for:
  - safe internal paths;
  - reserved custom route paths;
  - navigation links to `/venues/mrkt`;
  - page metadata for `/venues/mrkt`;
  - skipping custom route registration for `/venues/*`;
  - custom route registration continuing to work for `/rop`;
  - unsafe paths still failing fast;
  - no canonical route renaming.

- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/API_CONTRACT.md`, if route/config contract wording is affected;
  - `README.ru.md`, if user-facing integration examples mention reserved paths.

**Excluded**

- do not rename BeeCap canonical routes;
- do not change `/venues/mrkt` to `/mrkt`, `/venue-mrkt`, `/binance`, etc.;
- do not remove venue page configs from product-side `beeui.yml`;
- do not add product-specific MRKT/Binance/BeeCap logic to BeeUI core;
- do not touch Binance trading/runtime/risk logic;
- do not add auth/session/CSRF changes;
- do not add configuration apply/operator actions;
- do not add POST routes;
- do not add no-code builder behavior;
- do not introduce external CDNs/assets/scripts;
- do not add dependencies;
- do not change `pyproject.toml.version`.

#### Behavior

`navigation[].path` must be validated as a safe internal path rather than a custom route registration target.

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

This page config must load and be retained as metadata, but BeeUI must not register a custom route for `/venues/mrkt`.

Valid custom page:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title: ROP Dashboard
    subtitle: ROP operator dashboard
    blocks: []
```

BeeUI can register `/rop` as an adapter-backed custom page and call:

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

Expected result:

- config validation succeeds;
- the sidebar can link to `/venues/mrkt` and `/venues/binance`;
- the product console route `/venues/{venue_id}` remains canonical;
- BeeUI does not register `/venues/mrkt` as a generic custom page;
- generic custom pages continue to work for non-reserved paths such as `/rop`;
- unsafe paths and real route collisions still fail fast.

#### Acceptance

- `config/beeui.yml` with `pages[].path: /venues/mrkt` validates.
- `navigation[].path: /venues/mrkt` validates when pointing to declared metadata or a known internal product console route.
- `/venues/mrkt` is not registered as a custom page route.
- The existing `GET /venues/{venue_id}` product console route continues serving `/venues/mrkt`.
- `/venues/binance` behaves the same way.
- `/rop` or another non-reserved custom page still registers as an adapter-backed custom page.
- `/api/*`, `/auth/*`, `/static/*`, `/components/*`, `/runs/*`, and `/venues/*` cannot be registered as generic custom routes.
- Unsafe paths with `..`, `\`, `//`, control characters, or external schemes are rejected.
- Navigation paths do not use the custom-route reserved check.
- Page metadata paths do not use the custom-route reserved check.
- Custom route registration uses the custom-route reserved check.
- No product-specific BeeCap/BeeAgent/MRKT/Binance logic is added to generic BeeUI core.
- No route renaming is introduced.
- No external assets/scripts are added.
- No unsafe Jinja `|safe` is added.
- Existing tests remain green.

#### Checks

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

Smoke checks:

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

BeeCap verification after the dependency update:

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

#### DoD

- Safe internal path validation and custom route path validation are separate.
- Product console page metadata paths are allowed.
- Navigation links to product console routes are allowed.
- Generic custom route registration still blocks reserved/system/product-console paths.
- `/venues/*` configs are retained as metadata and are not registered as custom pages.
- `/runs/*` custom route shadowing remains blocked.
- Non-reserved custom pages continue to work.
- Unsafe paths still fail fast.
- Tests cover validation and route registration behavior.
- Documentation reflects the distinction between page metadata and custom route registration.
- BeeUI remains product-neutral.
- No new dependencies are added.
- `pyproject.toml.version` is unchanged.
- The PR is ready for review.

### Iteration 13.6 — Safe charts and advanced Tabler tables for product dashboards

**Status:** DONE

#### Goal

Add product-neutral rendering primitives for safe local charts and advanced Tabler-compatible tables to BeeUI so that BeeAgent/BeeCap/future Bee products can build complete dashboards through `beeui.yml` + adapter-provided `layout[]`, without product-owned Jinja templates or product-specific logic inside BeeUI.

#### Why

After Iteration 13.5, BeeUI correctly distinguishes product console route metadata, navigation compatibility, and custom page registration. The next blocker before BeeAgent integration is an insufficient visual/data presentation layer for real operator dashboards.

The BeeAgent ROP dashboard needs:

- charts over time periods;
- status distributions;
- trends in processed emails/leads;
- Bitrix reconciliation charts;
- dense operator tables;
- tables with badges/statuses/actions/internal links;
- mobile-friendly Tabler table layout.

These elements must live in BeeUI rather than BeeAgent. BeeAgent must provide only product read-models, layout blocks, and domain data.

The core rule remains:

```text
BeeUI renders.
The product decides.
```

BeeUI must not know what ROP, Bitrix, leads, managers, MRKT, Binance, brokers, or strategies are. BeeUI must safely render generic chart/table blocks.

#### Change level

**security-sensitive**

Rationale:

- browser-executed chart rendering is added;
- serialization of adapter-provided chart data into HTML is added;
- the adapter-backed block contract expands;
- richer table cells, links, badges, actions, and selectable controls are added;
- a package-local vendored JS asset may be added;
- operator-facing dashboards influence decisions.

Security-sensitive checks are required for:

- HTML escaping;
- safe JSON serialization;
- safe internal links only;
- no arbitrary HTML/JS from config or adapter payload;
- no external CDN/scripts/tracking;
- no secrets in HTML/API/logs;
- malformed payload degradation;
- no mutation from GET routes;
- no product-specific imports or semantics.

#### Scope

**Included**

- add a safe local chart renderer for the adapter-backed `layout[]` block type:

```text
chart
```

- support chart kinds:

```text
line
bar
area
donut
```

- use only a package-local chart asset:
  - a local ApexCharts asset if already present;
  - or vendored package-local `apexcharts.min.js` with a license note, without Python dependency changes;
  - no CDNs;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
  - no PostHog/tracking/demo scripts.

- the chart block contract must be controlled, for example:

```json
{
  "type": "chart",
  "title": "Processed events",
  "subtitle": "Last 7 days",
  "kind": "line",
  "height": 280,
  "series": [
    {
      "name": "Processed",
      "data": [12, 18, 24, 19, 31, 42, 38]
    }
  ],
  "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "width": 6
}
```

- support empty/degraded chart states:
  - missing data;
  - empty series;
  - unsupported kind;
  - invalid series shape;
  - invalid labels/categories;
  - too-large payload.
- prohibit arbitrary ApexCharts options passthrough.
- allow only allowlisted chart options:
  - `kind`;
  - `height`;
  - `series`;
  - `categories`;
  - `labels`;
  - `unit`;
  - `empty_message`;
  - `status`;
  - `width` / `span` / `size`.
- initialize charts only on pages containing chart blocks.
- the chart script must be package-local and make no network calls.
- chart DOM IDs must be deterministic, safe, and collision-resistant.
- add an advanced Tabler-compatible data table block:

```text
data_table
```

- preserve backward compatibility for the existing `table_card`.
- `table_card` may remain a simple/static block.
- `data_table` must cover richer operator table use cases.
- supported table styles:
  - basic card table;
  - striped table;
  - mobile table with `data-label`;
  - selectable table;
  - compact table;
  - table with badges/status dots;
  - avatar/text rows;
  - progress/background rows;
  - toolbar with search/entries/actions as controlled/inert or URL-driven UI;
  - footer pagination.
- do not add actual DataTables/List.js runtimes in this iteration.
- sort/search controls may be inert or URL-driven placeholders.
- do not add arbitrary client-side sorting/search JS.
- do not add a DataTables plugin dependency.
- the `data_table` block contract must be product-neutral, for example:

```json
{
  "type": "data_table",
  "title": "Recent items",
  "description": "Latest adapter-provided rows",
  "variant": "card",
  "striped": true,
  "mobile": "md",
  "selectable": true,
  "nowrap": false,
  "toolbar": {
    "search": true,
    "entries": true,
    "actions": [{ "label": "Export", "href": "/reports/export" }]
  },
  "columns": [
    { "key": "id", "label": "ID", "sortable": true },
    { "key": "status", "label": "Status", "cell": "badge" },
    { "key": "owner", "label": "Owner", "cell": "avatar_text" },
    { "key": "progress", "label": "Progress", "cell": "progress" },
    { "key": "actions", "label": "", "cell": "actions" }
  ],
  "rows": [
    {
      "id": { "label": "run_001", "href": "/runs/run_001" },
      "status": { "label": "ok", "tone": "success" },
      "owner": {
        "title": "Operator",
        "subtitle": "demo@example.local",
        "initials": "OP"
      },
      "progress": { "label": "72%", "value": 72 },
      "actions": [{ "label": "Open", "href": "/runs/run_001" }]
    }
  ],
  "pagination": {
    "label": "Showing 1 to 8 of 16 entries",
    "pages": [
      { "label": "1", "href": "?page=1", "active": true },
      { "label": "2", "href": "?page=2" }
    ]
  },
  "width": 12
}
```

- supported safe cell types:

```text
text
muted
link
badge
status
avatar_text
progress
actions
```

- unknown cell type should degrade visibly or render as escaped text according to existing renderer policy.
- missing values render as `n/a`, not `None`.
- all links must be safe internal links:
  - allow `/...`;
  - reject `//...`;
  - reject `http://...`;
  - reject `https://...`;
  - reject `javascript:`;
  - reject `mailto:`;
  - reject traversal/control characters.
- add catalog/demo examples for:
  - chart line;
  - chart bar;
  - chart area;
  - chart donut;
  - basic table;
  - striped table;
  - mobile table;
  - selectable table;
  - avatar/status table;
  - compact progress table;
  - advanced toolbar/pagination table.
- update `config/schema.yml` demo with non-product-specific chart/table examples if it helps smoke validation.
- no required new keys in `config/settings.yml`.
- no secrets in schema/config.
- update docs:
  - `docs/ROADMAP.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/WEB_UI.md`;
  - `README.md`;
  - `docs/SECURITY.md` only if asset/security policy wording changes.

**Excluded**

- BeeAgent-specific ROP labels, metrics or business logic;
- Bitrix-specific logic;
- BeeCap-specific trading calculations;
- MRKT/Binance semantics;
- direct product storage reads;
- provider/broker/runtime calls;
- config apply;
- auth/session/CSRF changes;
- operator actions;
- POST routes;
- no-code builder;
- drag-and-drop;
- arbitrary HTML blocks;
- arbitrary JS blocks;
- arbitrary ApexCharts options passthrough;
- full Tabler demo page copy;
- PostHog/demo scripts/sponsor blocks/remote fonts/external CDN;
- DataTables/List.js real runtime;
- new Python dependencies unless strictly justified;
- `pyproject.toml.version` change;
- `uv.lock` change unless a dependency is explicitly and intentionally changed.

#### Deliverable

BeeUI provides reusable product-neutral chart and advanced table blocks for adapter-backed dashboards.

Expected result:

- product adapters can return `chart` blocks in `layout[]`;
- product adapters can return `data_table` blocks in `layout[]`;
- demo/schema pages can show representative charts/tables;
- BeeAgent can build ROP dashboard using BeeUI blocks without product-owned Jinja templates;
- BeeCap and future Bee-products can reuse the same chart/table contracts;
- malformed/unsupported chart/table payloads render explicit degraded states instead of `500`;
- all adapter/config text remains escaped;
- all active links are internal-only;
- external assets/scripts/tracking are absent.

#### Acceptance

- `chart` block renders package-local line chart.
- `chart` block renders package-local bar chart.
- `chart` block renders package-local area chart.
- `chart` block renders package-local donut chart.
- Unsupported chart kind renders explicit degraded state, not `500`.
- Missing/empty chart data renders empty/degraded state.
- Unsafe chart labels/titles are HTML-escaped.
- Chart initialization data is serialized safely.
- Chart renderer does not accept arbitrary JS/options from adapter/config.
- Chart asset is package-local.
- Chart asset is loaded only when chart blocks exist, if practical.
- `data_table` block renders Tabler-compatible card table.
- `data_table` supports `table-vcenter card-table`.
- `data_table` supports `table-striped`.
- `data_table` supports `table-mobile-md` and `data-label`.
- `data_table` supports selectable rows.
- `data_table` supports toolbar controls as controlled/inert or URL-driven markup.
- `data_table` supports footer pagination.
- `data_table` supports cell types: text, muted, link, badge, status, avatar_text, progress, actions.
- Unsafe/external links are rejected or rendered inert.
- Missing values render as `n/a`.
- Malformed table payload renders explicit degraded state, not `500`.
- Existing `table_card` configs continue to work.
- Existing `chart` placeholder behavior is replaced or made compatible with the new safe renderer.
- No product-specific imports are added:
  - no `beecap_module`;
  - no `beeagent_module`.
- No product-specific strings/semantics are added to BeeUI core.
- No external references are added:
  - no `posthog`;
  - no `scripts.tabler.io`;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
  - no remote font imports.
- No unsafe Jinja `|safe` is added for adapter/config-provided fields.
- GET routes do not mutate storage/config/artifacts.
- Secrets do not appear in HTML/API/logs.
- `pyproject.toml.version` remains unchanged.
- `uv.lock` remains unchanged unless a dependency is explicitly changed and justified.

#### Checks

Automated:

```bash
uv run pytest -q
uv run pytest -q -W error::UserWarning
```

Targeted:

```bash
uv run pytest -q tests/test_blocks.py
uv run pytest -q tests/test_pages.py
uv run pytest -q tests/test_config.py
uv run pytest -q tests/test_app.py
uv run pytest -q tests/test_security.py
```

Smoke:

```bash
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Static/security checks:

```bash
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "ROP|BeeAgent|BeeCap|MRKT|Binance|Bitrix|lead|manager|broker|strategy" src/beeui_module || true
git diff -- pyproject.toml uv.lock
```

Manual/browser smoke:

```text
GET /
GET /components
GET /components/interface
GET /components/plugins
GET /runs
GET /static/vendor/tabler/...
GET /static/css/beeui.css
```

Expected:

- demo dashboard renders without `500`;
- chart examples render where configured;
- advanced table examples render where configured;
- no external network asset references in HTML;
- no product-specific labels in BeeUI demo unless they come from fixture/demo data only.

#### DoD

- Chart renderer implemented, documented and tested.
- Advanced table/data table renderer implemented, documented and tested.
- Existing `table_card` remains backward-compatible.
- Existing adapter-backed layout renderer remains backward-compatible.
- Malformed chart/table payloads degrade visibly and safely.
- Config/schema examples remain valid.
- BeeUI remains product-neutral.
- Product adapters remain the only source of product semantics.
- No direct product storage reads are added.
- No provider/broker/runtime calls are added.
- No external CDN/scripts/tracking are added.
- No unsafe Jinja `|safe` is added for adapter/config values.
- No secrets leak into HTML/API/logs.
- Required checks are executed and recorded.
- Docs reflect the actual chart/table block contracts.
- PR is ready for review before BeeAgent Iteration 14.

### Iteration 13.7 — Locale-aware shell labels, language switcher and query-preserving navigation

**Status:** DONE

#### Goal

Add generic locale-aware rendering for shell/page/navigation/tab labels, a simple language switcher, and preservation of allowlisted query parameters in navigation/tab links to BeeUI so that product dashboards such as BeeAgent `/rop?lang=ru` retain the selected language during navigation and can render RU/EN shell labels without product-owned Jinja templates.

#### Why

After Iteration 13.6, BeeUI can safely render charts and advanced data tables, but BeeAgent UI-6 identified a real blocker:

```text
/rop?lang=ru
```

translates only some adapter-provided layout blocks, while the BeeUI shell remains partly in English:

- page title/subtitle;
- sidebar navigation labels;
- page tabs;
- tab links;
- language choice after tab navigation.

The cause is architectural: these elements are rendered by the BeeUI shell/config renderer rather than BeeAgent `read_model.py`.

BeeAgent can and must translate its domain/read-model labels through a product-side locale catalog. BeeUI must provide a generic mechanism:

```text
Product provides localized config labels.
BeeUI resolves and renders them.
BeeUI preserves locale in safe navigation links.
```

The core rule remains:

```text
BeeUI renders.
Product decides.
```

BeeUI must not know what ROP, Bitrix, leads, managers, BeeAgent, BeeCap, MRKT, or Binance are.

#### Change level

**runtime-risk**

Rationale:

- shell/navigation/tabs HTML rendering changes;
- the schema/config text contract for selected user-facing labels changes;
- URL/query behavior changes;
- route-prefix and embedded behavior must be preserved;
- operator-facing dashboards depend on correct navigation.

Security-sensitive checks are required for:

- safe internal links;
- query param allowlist;
- URL encoding;
- HTML escaping localized labels;
- invalid locale fallback;
- absence of external assets/scripts/tracking;
- absence of product-specific imports/logic;
- no mutation from GET routes.

#### Scope

**Included:**

- add schema-compatible localized text v0 for BeeUI shell fields:
  - `app.title`;
  - `app.logo_text`;
  - `navigation[].title`;
  - `navigation[].children[].title`;
  - `pages[].title`;
  - `pages[].subtitle`;
  - `pages[].tabs.items[].title`.

- preserve backward compatibility:
  - existing plain string values continue to work;
  - optional localized mapping values are supported.

- supported localized text shape:

```yaml
pages:
  - id: rop_dashboard
    path: /rop
    title:
      en: ROP Dashboard
      ru: Панель РОПа
    subtitle:
      en: ROP operator dashboard
      ru: Рабочая панель РОПа
    tabs:
      active_param: tab
      items:
        - id: overview
          title:
            en: Overview
            ru: Обзор
          href: /rop?tab=overview
```

- localized mapping rules:
  - mapping keys must be allowlisted locales from `app.locale.available`;
  - mapping must contain the default locale;
  - invalid mapping keys fail fast;
  - empty mapping fails fast;
  - invalid non-string values fail fast;
  - selected locale resolves from `?lang=...` only if allowlisted;
  - invalid `lang` falls back to `app.locale.default`;
  - missing selected locale falls back to default locale.

- add a product-neutral localized text resolution helper:
  - plain string → same string;
  - mapping → selected locale value or default locale value;
  - no translation catalog inside BeeUI;
  - no product-specific fallback strings.

- add a product-neutral URL helper for query preservation:
  - preserve only allowlisted params;
  - do not preserve arbitrary query params globally;
  - URL-encode query values;
  - keep existing href query values unless explicitly overridden;
  - reject unsafe/external hrefs according to existing safe link rules.

- preserve query params in page tabs:
  - `lang`;
  - `period`;
  - `run_id`.

- preserve `lang` in sidebar/navigation links where practical.

- add language switcher:
  - rendered only when `app.locale.available` has more than one locale;
  - labels are uppercase locale codes, e.g. `RU / EN`;
  - current locale is marked active;
  - switch href preserves current path and all current query params, replacing only `lang`;
  - no cookies;
  - no session persistence;
  - no localStorage;
  - no JS required.

- route prefix / embedded mount compatibility:
  - generated hrefs must remain correct under `web.route_prefix` and `mount_beeui(path="/ui")`;
  - no double prefixing;
  - no protocol-relative hrefs.

- update tests for:
  - localized config label validation;
  - localized page title rendering;
  - localized sidebar rendering;
  - localized tab title rendering;
  - invalid locale fallback;
  - tab links preserve `lang`, `period`, `run_id`;
  - sidebar/nav links preserve `lang`;
  - language switcher preserves current query and replaces only `lang`;
  - safe internal link behavior remains intact;
  - route prefix compatibility;
  - no unsafe `|safe`;
  - no product-specific imports/strings in BeeUI generic renderer.

- update docs:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/API_CONTRACT.md` if config/page contract is documented there;
  - `docs/COMPONENTS.md` if language switcher/component behavior is documented there;
  - `README.ru.md` if user-facing config examples change.

**Excluded:**

- BeeAgent ROP domain translations inside BeeUI;
- Bitrix/lead/manager-specific labels in BeeUI;
- modifying `beeagent-rop`;
- runtime AI execution;
- mailbox/CRM/Bitrix/module/capability execution;
- full i18n catalog;
- gettext/Babel;
- translation files;
- persisted user preferences;
- cookies/session for language;
- auth changes;
- magic-link login;
- social login;
- copying Tabler sign-in pages;
- PostHog/demo scripts/sponsor blocks/remote fonts/external CDN;
- config apply;
- operator actions;
- POST routes;
- no-code builder;
- new dependencies;
- `pyproject.toml.version` change;
- `uv.lock` change.

#### Deliverable

BeeUI can render localized shell/page/navigation/tabs labels from product-side `beeui.yml`, preserve locale in page navigation, and expose a simple query-param based language switcher.

Expected behavior:

```text
/rop?tab=overview&period=7d&lang=ru
```

renders:

- RU page title/subtitle if product config provides RU labels;
- RU sidebar labels if product config provides RU labels;
- RU tab labels if product config provides RU labels;
- language switcher with RU active;
- tab links preserving `period=7d&lang=ru`;
- no product-specific logic inside BeeUI.

#### Acceptance

- Existing configs with plain string titles still validate and render.
- Localized config mapping validates when keys are in `app.locale.available`.
- Localized config mapping fails fast when it uses unknown locale keys.
- Localized config mapping fails fast when default locale is missing.
- Localized config mapping fails fast on non-string values.
- `?lang=ru` resolves to `ru` when `ru` is allowlisted.
- Invalid `?lang=bad` falls back to default locale.
- Page title/subtitle render localized values.
- Sidebar/navigation labels render localized values.
- Page tab labels render localized values.
- Page tab hrefs preserve `lang`, `period`, `run_id`.
- Sidebar/navigation hrefs preserve `lang` where practical.
- Language switcher renders only when more than one locale is available.
- Language switcher links preserve current query params and replace only `lang`.
- Generated links remain safe internal links.
- Generated links work under route prefix / embedded mount.
- HTML labels remain escaped.
- Existing attached tabs card behavior from Iteration 13.3 remains intact.
- Existing chart/data_table behavior from Iteration 13.6 remains intact.
- No product-specific imports are added:
  - no `beecap_module`;
  - no `beeagent_module`.

- No product-specific domain strings are added to generic BeeUI renderers.
- No external references are added:
  - no `posthog`;
  - no `scripts.tabler.io`;
  - no `preview.tabler.io`;
  - no `docs.tabler.io`;
  - no `cdn.jsdelivr`;
  - no remote font imports.

- No unsafe Jinja `|safe` is added for config/adapter-provided fields.
- GET routes do not mutate storage/config/artifacts.
- `pyproject.toml.version` remains unchanged.
- `uv.lock` remains unchanged.

#### Checks

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
uv run pytest -q tests/test_security.py
```

Smoke:

```bash
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Static/security checks:

```bash
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "ROP|BeeAgent|BeeCap|MRKT|Binance|Bitrix|lead|manager|broker|strategy" src/beeui_module || true
git diff -- pyproject.toml uv.lock
```

Manual/browser smoke:

```text
GET /
GET /?lang=ru
GET /runs?lang=ru
GET /components?lang=ru
GET /rop?tab=overview&period=7d&lang=ru when a product config declares /rop
```

Expected:

- no `500`;
- language switcher visible when multiple locales configured;
- selected locale does not disappear after tab click;
- no external network asset references in HTML.

#### DoD

- Localized config text v0 is implemented, documented and tested.
- Plain string config values remain backward-compatible.
- Page title/sidebar/tabs can render RU/EN from product-side config without BeeUI product semantics.
- Query-param locale is preserved across tabs/navigation where practical.
- Language switcher works without JS, cookies, session or localStorage.
- URL/query helpers are allowlist-based and safe.
- Route prefix / embedded mount behavior remains correct.
- BeeUI remains product-neutral.
- No auth/magic-link/social-login scope is added.
- No external Tabler preview/demo code is copied.
- Tests and security checks are recorded.
- Docs reflect the actual locale/navigation contract.
- PR is ready for review before BeeAgent UI-6 closure.

### Iteration 13.8 — Generic detail page template and render helper

**Status:** DONE

#### Goal

Add a product-neutral generic detail page template and render helper to BeeUI so that Bee products can render detail/read-model pages through the shared BeeUI/Jinja/Tabler layer without manually assembling HTML strings in product routes.

#### Why

After Iteration 13.7, BeeUI can render localized shell/navigation/tabs and preserve query parameters. However, BeeAgent It31 revealed further UI architecture debt: detail pages such as `/rop/events/{event_id}` may work functionally while their HTML is still assembled manually inside product-side routes using Python f-strings/manual markup.

This violates the target rule:

```text
BeeUI renders.
Product decides.
```

Correct boundary:

- the product adapter/product route prepares a safe read-model;
- BeeUI renders HTML through a generic template/component;
- BeeUI does not know ROP/Bitrix/email classification semantics;
- the product does not copy Tabler/Jinja templates or concatenate HTML manually.

This iteration is needed before BeeAgent Iteration 14 to avoid carrying UI debt into the BeeAgent adapter MVP or proliferating product-owned HTML templates.

#### Change level

**runtime-risk**

Rationale:

- a new reusable HTML rendering path is added;
- adapter/product-provided read-model values render in operator-facing HTML;
- the integration/rendering contract for product detail pages changes;
- escaping, safe links, route prefix compatibility, and protection against raw sensitive content exposure must be preserved.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links;
- no unsafe `|safe`;
- no external assets/scripts/tracking;
- no raw email/attachment payload exposure from rendered model;
- no product-specific imports/logic;
- no mutation from GET routes.

#### Scope

**Included:**

- add a generic detail page model contract for the BeeUI rendering layer:

```json
{
  "page_id": "event_detail",
  "title": "Event detail",
  "subtitle": "Read-only event details",
  "back_href": "/events",
  "warnings": [],
  "sections": [
    {
      "title": "Summary",
      "kind": "key_value",
      "items": [
        { "label": "Subject", "value": "..." },
        { "label": "Sender", "value": "..." }
      ]
    },
    {
      "title": "Preview",
      "kind": "text",
      "body": "..."
    },
    {
      "title": "Rows",
      "kind": "table",
      "columns": [
        { "key": "name", "label": "Name" },
        { "key": "value", "label": "Value" }
      ],
      "rows": [{ "name": "Status", "value": "ok" }]
    },
    {
      "title": "Links",
      "kind": "links",
      "items": [{ "label": "Open source", "href": "/runs/run_001" }]
    }
  ]
}
```

- support only KISS section kinds:

```text
key_value
text
table
links
```

- add a package-local Jinja template, for example:

```text
src/beeui_module/web/templates/pages/detail.html
```

or the closest existing location in the current template structure.

- add a product-neutral detail page model normalizer/helper:
  - validates/normalizes supported section kinds;
  - drops or degrades unsupported/malformed sections;
  - normalizes missing display values to `n/a`;
  - validates `back_href` and section links as safe internal links;
  - preserves route prefix / embedded mount behavior through existing link helpers;
  - does not render arbitrary HTML/JS;
  - does not evaluate Jinja/Python expressions from model.

- add a public render helper or reuse the existing BeeUI shell renderer, for example:

```python
render_beeui_detail_page(request=request, page=page_model)
```

or an equivalent existing renderer entrypoint.

- the detail template must use the shared BeeUI shell:
  - base layout;
  - page header;
  - theme/layout context;
  - locale context;
  - route prefix/link helpers;
  - Jinja autoescape.

- adapter/product read-model remains source of semantics:
  - BeeUI only renders normalized detail sections;
  - product owns event lookup, artifact reading, classification, filtering and redaction.

- add tests:
  - template renders title/subtitle/back link;
  - `key_value` section renders;
  - `text` section renders;
  - `table` section renders;
  - `links` section renders only safe internal links;
  - unsafe/external links are inert/omitted;
  - unsafe text is escaped;
  - unsupported/malformed section degrades without `500`;
  - route prefix / embedded mount links remain correct;
  - raw extra fields like `raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes` are not rendered as implicit fields;
  - no product-specific imports/strings in BeeUI generic code.

- update documentation:
  - `docs/ROADMAP.md`;
  - `docs/WEB_UI.md`;
  - `docs/COMPONENTS.md`;
  - `docs/API_CONTRACT.md`;
  - `docs/INTEGRATION.md`;
  - `README.ru.md`, if the user-facing integration example changes.

**Excluded:**

- ROP-specific rendering logic;
- Bitrix-specific logic;
- email classification logic;
- `should_rop_see` logic;
- reading ROP artifact contracts inside BeeUI;
- raw `.eml` rendering;
- raw attachment rendering;
- dynamic route registration for `/rop/events/{event_id}` inside BeeUI, unless an existing generic route mechanism already supports it safely;
- BeeAgent production adapter implementation;
- modifying `beeagent-rop`;
- review save;
- POST actions;
- Bitrix write-back;
- AI assist changes;
- auth/session/CSRF changes;
- config apply;
- no-code builder;
- new dependencies;
- `pyproject.toml.version` change;
- `uv.lock` change.

#### Deliverable

BeeUI provides a reusable generic detail page renderer/template that product routes or adapter-backed pages can call with a safe read-model.

Expected product-side use:

```python
page = adapter.get_page("rop_event_detail", query)

return render_beeui_detail_page(
    request=request,
    page=page["page"],
)
```

or equivalent existing BeeUI shell renderer.

After this, BeeAgent can remove manual f-string HTML assembly for event detail and delegate rendering to BeeUI without moving ROP domain logic into BeeUI.

#### Acceptance

- Generic detail page template exists in BeeUI package templates.
- Generic detail render helper or equivalent shell renderer entrypoint exists.
- Detail page renders through Jinja template, not manual f-string HTML.
- Detail page supports section kinds:
  - `key_value`;
  - `text`;
  - `table`;
  - `links`.

- Unsupported section kinds render explicit degraded/empty state or are safely omitted without `500`.
- Missing display values render as `n/a`, not `None`.
- Title, subtitle, warnings and back link render correctly.
- Back link and section links are internal-only.
- External links are rejected, omitted or rendered inert.
- Route prefix / embedded mount link behavior remains correct.
- Adapter/product-provided text remains HTML-escaped.
- No unsafe `|safe` is added for adapter/product-provided values.
- Detail template does not expose implicit raw fields:
  - `raw_eml`;
  - `attachment_content`;
  - `payload_bytes`;
  - `content_bytes`.

- BeeUI does not import:
  - `beecap_module`;
  - `beeagent_module`.

- BeeUI generic renderer does not contain product-specific domain strings:
  - `ROP`;
  - `Bitrix`;
  - `lead`;
  - `manager`;
  - `MRKT`;
  - `Binance`;
  - `broker`;
  - `strategy`.

- Existing product console routes continue to work.
- Existing chart/data_table behavior from Iteration 13.6 remains intact.
- Existing locale/navigation behavior from Iteration 13.7 remains intact.
- GET routes remain read-only.
- No external CDN/scripts/tracking are added.
- `pyproject.toml.version` remains unchanged.
- `uv.lock` remains unchanged.

#### Checks

Automated:

```bash
uv run pytest -q
uv run pytest -q -W error::UserWarning
```

Targeted:

```bash
uv run pytest -q tests/test_pages.py
uv run pytest -q tests/test_product_console.py
uv run pytest -q tests/test_security.py
uv run pytest -q tests/test_app.py
```

Smoke:

```bash
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Static/security checks:

```bash
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "ROP|BeeAgent|BeeCap|MRKT|Binance|Bitrix|lead|manager|broker|strategy" src/beeui_module || true
rg -n "_render_event_detail_html|raw_eml|attachment_content|payload_bytes|content_bytes|RAW-EML-CONTENT|RAW-ATTACHMENT-CONTENT" src/beeui_module || true
git diff -- pyproject.toml uv.lock
```

Manual/browser smoke:

```text
GET /
GET /runs
GET /components
GET /components/interface
```

If a test/demo route is added for detail rendering:

```text
GET /<detail-demo-route>
```

Expected:

- no `500`;
- detail page renders inside BeeUI shell;
- no external network asset references in HTML;
- unsafe values are escaped;
- links are internal-only.

#### DoD

- Generic detail page template is implemented, documented and tested.
- Product-safe detail page model is normalized before render.
- Rendering remains product-neutral.
- BeeUI does not move ROP/domain logic into generic code.
- Product routes can stop assembling detail HTML manually.
- Existing adapter-backed console behavior remains compatible.
- Existing locale/query-preserving behavior remains compatible.

#### Summary

Iteration 13.8 adds:

- `src/beeui_module/pages/detail.py` — product-neutral detail page normalizer and render helper. Public entrypoint: `render_beeui_detail_page(request, page, *, templates, route_prefix, ui_config, product_title, product_id)` returns `TemplateResponse`. Internal normalizer `normalize_detail_page(raw)` validates sections, normalizes values, validates internal links, drops unsupported/malformed sections and strips raw fields (`raw_eml`, `attachment_content`, `payload_bytes`, `content_bytes`).

- `src/beeui_module/web/templates/detail.html` — Jinja template extending `base.html` with Tabler-compatible cards for section kinds: `key_value` (datagrid), `text` (preformatted card), `table` (responsive table with card-table), `links` (list-group with internal-link validation). No `|safe`. No JS.

- Section kinds: `key_value`, `text`, `table`, `links`. Unsupported kinds degrade gracefully. Missing values render as `n/a`. External/unsafe links are omitted or rendered inert. Back link is validated as internal-only.

- 12 tests in `tests/test_pages.py`: title/subtitle/back_href, key_value, text, table, links, unsafe/external links omission, escaping, unsupported section crash safety, missing values → n/a, raw fields not in normalized model, no product-specific strings in generic code, no `|safe` in template, ghost/empty sections omitted.
- No unsafe HTML rendering is introduced.
- No raw sensitive email/attachment fields are implicitly rendered.
- No dependencies are added.
- Version is not changed.
- `uv.lock` is not changed.
- PR is ready for review before BeeAgent event detail cleanup is closed.

### Iteration 13.9 — Operator UX presentation contracts, locale persistence, theme, and chart state handling

**Status:** DONE

#### Goal

Establish and extend generic operator-facing presentation contracts: filter forms, sortable data tables, locale persistence, theme selection, chart empty/error states, and product-neutral detail rendering. All changes remain bounded generic BeeUI improvements without product-specific logic.

#### Why

After Iteration 13.8, BeeUI has a generic detail page template and render helper. However, several operator-facing presentation gaps remain before BeeAgent integration begins.

This iteration is bounded: generic BeeUI rendering contracts, locale persistence, themes, chart states, and safe link helpers only. No product-specific logic.

#### Change level

**security-sensitive**

Rationale:

- adapter-backed block contracts change;
- locale persistence through a cookie is added;
- theme persistence through localStorage is added;
- the chart renderer changes;
- detail presentation semantics change;
- new generic block types and fields are added.

Work follows the approved Issue for Iteration 13.9.

Security-sensitive checks are required for:

- HTML escaping;
- safe internal links (filter form, sortable headers, all hrefs);
- locale cookie validation;
- theme localStorage validation;
- no external assets/scripts/tracking;
- no product-specific semantics;
- no mutation through GET routes.

#### Scope

**Included:**

- **Generic filter form (`filter_form`)**
  - an adapter-backed `filter_form` block type in `layout[]`;
  - supported field types: `date_range`, `text`, `select`, `checkboxes`;
  - column toggles with safe internal toggle_href;
  - reset href;
  - apply href;
  - form action through a route-prefix-aware contract;
  - all active hrefs pass the shared safe internal-link contract.

- **Sortable data table (`data_table`)**
  - preservation of `sort_href` in the normalized column model;
  - `sort_href` passes the safe internal-link validator;
  - the template displays a link only when sort_href is valid;
  - inactive and active sort states;
  - route prefix compatibility.

- **Product-neutral detail presentation**
  - removal of hardcoded product thresholds (priority, confidence);
  - allowlisted tones: `default`, `muted`, `success`, `warning`, `danger`;
  - allowlisted variants: `text`, `badge`, `boolean`, `confidence`, `long_text`;
  - unknown tones/variants safely degrade to plain text;
  - the product decides tone and display semantics;
  - `type_hint` is temporarily accepted but does not trigger product-specific decisions.

- **Locale persistence**
  - a shared locale resolution order:
    1. valid `?lang=`;
    2. valid `beeui_lang` cookie;
    3. configured default locale.
  - query and cookie values are validated against `app.locale.available`;
  - middleware does not set a cookie for an invalid locale;
  - the cookie stores only an allowlisted locale code;
  - auth routes use the shared resolver;
  - `samesite="lax"`;
  - the path matches the route prefix;
  - a centralized generic translation mechanism for BeeUI-owned strings without Babel/gettext.

- **Theme persistence**
  - modes: `system`, `light`, `dark`;
  - theme is a presentation preference only;
  - `localStorage` does not affect product behavior or authorization;
  - the value is validated against an allowlist;
  - invalid stored value → configured/default system behavior;
  - the FOUC bootstrap does not accept arbitrary JS/data;
  - system mode responds to `prefers-color-scheme`;
  - the chart theme synchronizes with the current resolved theme.

- **Chart empty and error states**
  - distinguish empty data, unavailable/degraded configuration, and runtime rendering errors;
  - determine empty states from normalized data before calling render;
  - render exceptions display generic user-readable errors;
  - browser error states do not log raw adapter payloads to the console;
  - EN/RU localization for all states.

- **Generic contracts review**
  - `progress` / `progress_tone`;
  - `compact`;
  - `chart_id`;
  - chart colors;
  - vertical/horizontal bar options;
  - `no_data`;
  - `type_hint`;
  - filter-form fields;
  - pagination labels;
  - locale-aware empty/error states.

- **Documentation**
  - `docs/THEME.md`;

- **Tests**
  - filter-form safe links;
  - embedded route prefix;
  - sortable header rendering;
  - detail neutral presentation metadata;
  - invalid presentation values;
  - locale query/cookie validation;
  - auth/artifact locale consistency;
  - theme allowlist and fallback;
  - chart empty vs error state;
  - no product-specific semantics in generic BeeUI;
  - no external dependencies/resources.

**Excluded:**

- ROP-specific semantics;
- Bitrix-specific semantics;
- BeeAgent imports;
- product classification rules;
- product confidence thresholds;
- product queue/filter taxonomies;
- product read-model composition;
- BeeAgent production integration;
- config apply/write;
- auth/RBAC changes beyond locale cookie;
- standalone service mode;
- no-code builder.

#### Deliverable

BeeUI provides complete generic operator UX presentation contracts with locale persistence, theme selection, chart state handling, and product-neutral detail rendering.

#### Checks

- `uv run pytest -q`;
- `uv run pytest -q -W error::UserWarning`;
- `./start.sh doctor`;
- `./start.sh routes`;
- `./start.sh web --host 127.0.0.1 --port 8780`;

Targeted tests:

- filter-form safe links (external, protocol-relative, traversal, control chars);
- embedded route prefix for filter form;
- data table sortable header rendering with valid/invalid sort_href;
- detail neutral presentation metadata (allowlisted tones, invalid tone fallback);
- locale query/cookie validation and priority;
- auth page locale consistency;
- artifact page locale consistency;
- theme allowlist and fallback;
- chart empty vs error state;
- no ROP/Bitrix/BeeAgent/MRKT/Binance strings in generic BeeUI code;
- no `|safe` in templates for adapter-provided values;
- no external CDN/scripts/tracking.

Security checks:

```bash
rg -n "\\|safe" src/beeui_module/web/templates || true
rg -n "beecap_module|beeagent_module" src/beeui_module || true
rg -n "posthog|scripts.tabler.io|preview.tabler.io|docs.tabler.io|cdn.jsdelivr|http://|https://" src/beeui_module/web/templates src/beeui_module/web/static || true
rg -n "ROP|BeeAgent|BeeCap|MRKT|Binance|Bitrix|lead|manager|broker|strategy" src/beeui_module || true
git diff -- pyproject.toml uv.lock
```

#### DoD

- the filter_form contract is implemented, documented, and tested;
- data_table sort_href is preserved and validated;
- the detail renderer contains no product thresholds;
- locale resolution is shared and documented;
- theme persistence is safe and documented;
- chart states distinguish empty/error/degraded;
- documentation is updated (ROADMAP, COMPONENTS, WEB_UI, API_CONTRACT, INTEGRATION, SECURITY, THEME, README);
- tests cover security, presentation, locale, theme, and chart contracts;
- BeeUI remains product-neutral;
- no product-specific logic is added;
- no external assets/scripts/tracking are added;
- dependencies/version/lockfile remain unchanged.

### Iteration 13.10 — Tabler Datepicker contract for generic date-range filters

**Status:** DONE

#### Goal

Align generic `filter_form.date_range` with the standard Tabler Datepicker presentation contract using locally vendored Litepicker, preserving the existing GET contract, partial range behavior, and product-neutral architecture.

#### Why

After Iteration 13.9, BeeUI supports generic `filter_form`, but `date_range` still renders as two browser-native `input[type=date]` controls.

This works functionally, but:

- appearance depends on the browser;
- the component does not match the Tabler Datepicker example;
- there is no consistent local calendar UX;
- Bee products must not fix this generic presentation gap with their own templates or JavaScript.

#### Depends on

- Iteration 13.9 — generic filter form, locale and theme contracts;
- existing local Tabler asset model;
- existing route-prefix and safe-rendering contracts.

#### Change level

```text
security-sensitive
```

Rationale:

- vendored browser JavaScript is added;
- package static assets change;
- adapter-backed HTML behavior changes;
- dependency/provenance review is required;
- HTML, route-prefix, and malformed-input verification is required.

#### Scope

**Included:**

- preserve the existing payload contract:

```text
type: date_range
from_value
to_value
from_label
to_label
```

- preserve canonical form field names:
  - `date_from`;
  - `date_to`;

- replace browser-native date controls with Tabler-compatible Datepicker controls;
- use the standard Tabler structure:
  - `.input-icon`;
  - `.form-control`;
  - `.input-icon-addon`;
  - calendar SVG icon;

- vendor Litepicker locally from a compatible Tabler distribution/source;
- record source, version, and license;
- do not use CDNs;
- do not include Tabler demo analytics/tracking scripts;
- initialize two independent Datepicker controls:
  - start bound;
  - end bound;

- preserve the ability to fill only one boundary;
- use `YYYY-MM-DD` as the input value and GET submission format;
- submit the GET form after a valid selection or value clearing;
- preserve a regular manual ISO input fallback without JavaScript;
- use the validated page locale for the calendar UI;
- preserve theme compatibility;
- add recursive layout detection for conditional Litepicker loading;
- load Litepicker only on pages with `date_range`;
- ensure correct route-prefix asset URLs;
- update package data;
- update:
  - `docs/ROADMAP.md`;
  - `docs/COMPONENTS.md`;
  - `docs/WEB_UI.md`;
  - `docs/INTEGRATION.md`;
  - `docs/SECURITY.md`, if static asset guidance needs clarification;
  - `README.ru.md`, if the public component example changes;

- add generic template, normalizer, asset-loading, and security tests.

**Excluded:**

- product-specific date semantics;
- BeeAgent/ROP/Bitrix imports or strings;
- `date_from <= date_to` validation inside BeeUI;
- combined product query parameter;
- product timezone decisions;
- product filtering;
- product-specific presets;
- date-time picker;
- arbitrary date formats from adapter input;
- external CDN;
- frontend build chain;
- copying the full Tabler demo page;
- analytics/tracking scripts;
- API changes;
- config mutation;
- auth/RBAC/CSRF changes;
- POST actions;
- product runtime execution;
- `pyproject.toml.version` change.

#### Deliverable

Generic adapter-backed `filter_form.date_range` renders two Tabler Datepicker controls with local Litepicker behavior while continuing to submit the established `date_from` and `date_to` GET parameters.

Products continue to decide date validation and filtering semantics.

#### Public contract

Backward-compatible input model:

```json
{
  "type": "date_range",
  "name": "date",
  "label": "Date range",
  "from_value": "2026-07-01",
  "to_value": "2026-07-31",
  "from_label": "From",
  "to_label": "To"
}
```

Rendered behavior changes, but the declarative payload and submitted parameter names remain compatible.

BeeUI must not infer:

- whether both bounds are required;
- whether bounds are inclusive;
- timezone rules;
- allowed business periods;
- product error behavior.

#### Expected outputs

- local Litepicker static asset and license/provenance record;
- updated generic Datepicker template markup;
- conditional asset loader;
- generic initialization JavaScript;
- package-data inclusion;
- updated component documentation;
- automated and browser verification.
- workflow hardening for this iteration: read-before-edit, ROADMAP scope, actual change level and proportional tests; no first-party code/test comments; Russian final-review verdicts; correction prompts that allow identical instruction/target worktrees; no `uv.lock` inspection outside an approved Python dependency change; `.agents/prompts/02-implementation-tests.md` remains unchanged.

No product runtime artifacts are created.

#### Checks

Automated:

```bash
uv run pytest -q
uv run pytest -q -W error::UserWarning
```

Targeted tests must cover:

- normalizer preserves `from_value`, `to_value`, labels and field names;
- rendered HTML uses Tabler input-icon structure;
- rendered HTML contains calendar icons;
- values remain HTML-escaped;
- `date_from` only;
- `date_to` only;
- both values;
- empty values;
- conditional Litepicker asset included exactly once when required;
- Litepicker asset absent when no `date_range` exists;
- nested/grouped layout detection;
- route-prefix asset paths;
- EN locale initialization;
- RU locale initialization;
- invalid/unknown locale cannot become arbitrary JS configuration;
- no unsafe `|safe`;
- no product imports or product-specific strings;
- malformed filter payload does not produce `500`.

Runtime smoke:

```bash
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Manual/browser scenarios:

- open a page containing `date_range`;
- select only start date;
- clear start date;
- select only end date;
- select both dates;
- verify one GET submission per completed interaction;
- verify ISO query values;
- verify light and dark themes;
- verify EN and RU;
- verify a page without date filters does not load Litepicker;
- verify no external network request is required for Datepicker operation.

Security/static checks:

```text
- review vendored asset source, version and license;
- inspect package output to ensure Litepicker files are included;
- confirm no CDN, tracking or demo scripts;
- confirm no unsafe adapter value interpolation into JavaScript;
- confirm GET routes remain read-only;
- confirm no product imports or product semantics;
- confirm version is not changed.
```

SCA/package review is required because static vendor/package-data content changes.

#### DoD

- `filter_form.date_range` uses Tabler-compatible Datepicker markup;
- Litepicker is local and reproducibly packaged;
- no external resources or tracking are introduced;
- existing declarative payload remains compatible;
- submitted names remain `date_from` and `date_to`;
- partial range behavior is preserved;
- no product date validation is moved into BeeUI;
- assets load only when needed;
- route prefix, locale and theme behavior work;
- malformed payloads degrade safely;
- documentation and tests are synchronized;
- BeeUI remains product-neutral;
- `pyproject.toml.version` is unchanged.

### Iteration 13.11 — Canonical Tabler table shell and functional toolbar

**Status:** DONE

#### Goal

Provide one reusable, product-neutral Tabler table presentation for adapter-backed product consoles and add an optional functional GET toolbar that can host date fields, search, dropdown filters, column visibility controls and reset actions.

#### Context

BeeUI currently renders `filter_form` and `data_table` as separate cards. The `data_table.toolbar.search` contract is presentation-only and inert, while product consoles such as BeeAgent ROP Queue need a functional server-side GET toolbar embedded in the table card.

The existing public table block types also use separate presentation paths, which permits visual drift between product-console tables.

#### Scope

Included:

- extend the adapter-backed `data_table` contract with an optional functional GET toolbar;
- reuse the existing controlled filter-field normalization rather than creating a second filter schema;
- support date range, text search, dropdown choices, hidden query state, reset and column toggles inside the table toolbar;
- render search and date controls without mandatory visible labels while preserving accessible names;
- render an icon-only ellipsis action after search for the column chooser;
- render filter controls with canonical Tabler button/dropdown markup;
- render reset as a standard Tabler button;
- remove implicit Apply-button rendering caused only by the presence of a date range;
- preserve explicit Apply support for consumers that request it;
- detect nested date-range controls for conditional Litepicker asset loading;
- resolve and prefix all nested active links through the existing safe internal-link contract;
- introduce one shared canonical table presentation used by adapter-backed table templates;
- keep existing public table block types backward-compatible;
- update component, web, integration and API contract documentation.

Excluded:

- product-specific filter semantics;
- BeeAgent, ROP or Bitrix-specific labels and behavior;
- client-side data filtering;
- DataTables/List.js integration;
- arbitrary adapter-provided JavaScript, HTML or CSS;
- removal of existing public table block types;
- dependency changes;
- copying a complete upstream Tabler demo page.

#### Deliverable

A backward-compatible BeeUI release in which:

- adapter-backed tables share one canonical Tabler presentation;
- a product can opt into a functional GET toolbar inside `data_table`;
- pages without an explicit toolbar remain plain tables;
- standalone `filter_form` remains supported;
- date-range controls no longer force an Apply button;
- all active links remain controlled and prefix-aware.

#### Acceptance criteria

- A `data_table` can render a functional GET form in the same card as the table and pagination.
- Date selection and clearing auto-submit the form.
- Text search submits through the GET form.
- An ellipsis action immediately after search opens the column chooser.
- Filter controls use canonical `.btn`, `.dropdown-toggle`, `.dropdown-menu` and `.dropdown-item` structures.
- Reset uses a standard `.btn`.
- No inline positioning styles are required for dropdowns.
- Visible field labels can be omitted without losing `aria-label` or equivalent accessible naming.
- Apply is rendered only when explicitly requested.
- Existing standalone `filter_form` payloads remain valid.
- Existing `data_table` payloads without the new toolbar fields render unchanged.
- Existing table block types remain supported and use the shared table presentation.
- Invalid and external href values remain inert.
- Route prefixes are applied exactly once.
- No external runtime assets or CDN references are introduced.
- Light, dark, desktop and mobile presentation remain usable.

#### Checks

- `uv run pytest -q`
- `./start.sh doctor`
- BeeUI web smoke using the expected local entrypoint
- normal, empty and malformed toolbar payload tests
- safe and unsafe href tests
- route-prefix tests
- conditional Litepicker asset tests
- HTML escaping tests
- visual review in light, dark and responsive layouts

#### Definition of Done

- generic contract and templates implemented;
- one canonical table presentation is used internally;
- backward compatibility tests pass;
- documentation is updated;
- screenshots or equivalent visual evidence are attached to the PR;
- `pyproject.toml.version` is not changed by the feature PR;
- `uv.lock` is unchanged because no dependency change is required.

### Iteration 13.12 — Fix the canonical Tabler table toolbar composition

**Status:** DONE

#### Goal

Complete the canonical Tabler `data_table` presentation so that the date range, search input, dropdown filter buttons, column chooser, reset action and table are rendered as one coherent functional table card.

#### Context

Iteration 13.11 introduced the public, product-neutral `data_table.toolbar` contract and functional GET controls.

The contract is usable, but the current renderer does not yet produce the intended canonical Tabler table composition:

- the toolbar is rendered as a separate body section rather than as part of the table header;
- controls can wrap unnecessarily on desktop;
- the toolbar date range does not fully reuse the canonical BeeUI Datepicker presentation;
- search, dropdown actions, column chooser and sorting presentation are not yet visually aligned with the shared Tabler table shell;
- the resulting consumer UI looks like a filter form placed above a table rather than one integrated table component.

This iteration is a corrective completion of Iteration 13.11. It must preserve the existing public component contract and GET behavior.

#### Scope

Included:

- render `data_table` as one canonical Tabler card containing:
  - table title;
  - date range control;
  - search control;
  - dropdown filter buttons;
  - column chooser;
  - reset action;
  - table;
  - existing pagination when supplied;
- place the functional toolbar inside the table card header rather than in a separate `card-body`;
- keep the toolbar on one line at supported desktop widths when the available space permits;
- provide controlled responsive wrapping or stacking on narrower screens;
- render `date_range` through the existing canonical BeeUI Datepicker markup and local assets;
- preserve automatic GET submission after selecting or clearing a date;
- render text search as a compact Tabler search control;
- submit text search through the existing GET form when the user presses Enter;
- render `checkboxes` toolbar fields as canonical Tabler dropdown buttons;
- preserve checked state, selected count and supplied `toggle_href` values;
- render `column_toggles` under a horizontal ellipsis action;
- position the column chooser immediately after the search control;
- render Reset as a standard Tabler button;
- render Apply only when the optional `toolbar.apply` payload is supplied;
- preserve sortable table headers and existing safe sort links;
- use the same table shell for populated, empty and degraded table states;
- add focused renderer, contract, accessibility and responsive regression tests;
- update BeeUI component and integration documentation.

Excluded:

- changes to the public `data_table.toolbar` payload schema;
- changes to GET parameter names or submission semantics;
- new pagination behavior or page-size controls;
- changes to consumer filtering, sorting or pagination logic;
- product-specific fields, labels or templates;
- ROP-specific rendering logic;
- changes to BeeAgent or other consumers;
- replacement of the existing Datepicker library;
- new frontend dependencies;
- external CDN assets;
- JavaScript framework adoption;
- redesign of unrelated BeeUI components.

#### Canonical presentation

The expected desktop composition is:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Table title                                                        │
│ [Date range] [Search] […] [Filter ▼] [Filter ▼] [Reset]           │
├─────────────────────────────────────────────────────────────────────┤
│ Column        Column        Column        Column                    │
│ Row           Row           Row           Row                       │
│ Row           Row           Row           Row                       │
├─────────────────────────────────────────────────────────────────────┤
│ Existing pagination, when supplied                                 │
└─────────────────────────────────────────────────────────────────────┘
```

The controls and the table must belong to the same card. The renderer must not emit a standalone filter card or a visually detached toolbar body.

#### Functional contract

The renderer must continue to support the Iteration 13.11 toolbar payload:

- `fields`
  - `date_range`;
  - `text`;
  - `checkboxes`;

- `hidden`;
- `column_toggles`;
- `reset`;
- optional `apply`.

Existing semantics remain unchanged:

- date and search controls submit through GET;
- hidden inputs preserve consumer-owned query state;
- dropdown and column choices use supplied safe internal links;
- Reset uses the supplied safe internal link;
- Apply is absent unless explicitly supplied;
- route-prefix resolution and escaping remain owned by BeeUI;
- GET rendering does not mutate consumer state.

#### Accessibility

- empty visible labels must not remove accessible field names;
- Datepicker inputs retain accessible start and end labels;
- search retains an accessible name through its label or placeholder;
- dropdown buttons expose their purpose and expanded state;
- the column chooser has a descriptive accessible label;
- all controls remain keyboard-operable;
- focus indicators remain visible in light and dark themes;
- icons are not the sole source of meaning for required actions.

#### Deliverable

BeeUI renders a complete functional Tabler table component in which date selection, text search, dropdown filters, column selection, reset and the table itself form one canonical card.

Existing consumers can adopt the corrected presentation without changing their payload schema or product semantics.

#### Acceptance criteria

- One `data_table` produces one canonical Tabler card.
- The toolbar is rendered inside the table card header.
- The table begins directly below the header without a separate toolbar card or detached body section.
- A `date_range` field renders the canonical BeeUI Datepicker controls.
- Selecting or clearing either date preserves the existing automatic GET behavior.
- A text field renders as a compact search control.
- Pressing Enter in search submits the existing GET form.
- `checkboxes` fields render as dropdown buttons.
- Dropdown choices preserve supplied labels, checked state and safe toggle links.
- `column_toggles` render under a horizontal ellipsis action immediately after search.
- Reset renders as a standard Tabler button using the supplied safe link.
- Apply is not rendered when `toolbar.apply` is absent.
- Apply remains supported when `toolbar.apply` is present.
- Sorting links and sorting direction remain functional.
- Existing pagination remains functional and visually attached to the same table card.
- Populated, empty and degraded tables use the same shell.
- Desktop controls remain on one line when sufficient width is available.
- Narrow layouts wrap or stack without horizontal page overflow.
- Light and dark themes render correctly.
- No product-specific rendering logic is added.
- No public component payload contract is broken.
- No external asset or CDN dependency is introduced.
- All rendered labels, values and URLs remain escaped and validated through existing BeeUI boundaries.

#### Checks

Automated:

- `uv run pytest -q`
- targeted `data_table` renderer tests;
- toolbar field-order tests;
- Datepicker markup and asset tests;
- search GET-form tests;
- dropdown choice and selected-state tests;
- column chooser placement and link tests;
- Reset and optional Apply tests;
- sortable-header regression tests;
- populated, empty and degraded table tests;
- route-prefix and safe-link tests;
- HTML escaping tests;
- accessibility attribute tests;
- `git diff --check`;
- `./start.sh doctor`.

Visual/browser verification:

- date range opens, selects and clears correctly;
- search is usable and submits on Enter;
- each dropdown button opens and exposes its choices;
- checked dropdown choices are visible;
- the horizontal ellipsis opens the column chooser;
- column visibility links work;
- Reset works;
- the table remains part of the same card;
- sorting remains usable;
- light and dark themes;
- desktop, tablet and mobile widths;
- no unexpected horizontal page overflow;
- no external network requests for table or Datepicker assets.

#### Definition of Done

- the Iteration 13.11 public toolbar contract remains compatible;
- date, search, dropdown actions, column chooser, reset and table render as one canonical Tabler component;
- Datepicker presentation is reused rather than duplicated;
- no consumer-specific logic is introduced;
- no new pagination feature is added;
- tests, doctor checks and browser verification pass;
- documentation is synchronized;
- a BeeAgent ROP Queue payload can render the intended layout without a BeeAgent presentation workaround;
- the implementation is ready for a BeeUI patch release.

### Iteration 13.13 — External-principal sessions and controlled embedding

**Status:** DONE

#### Goal

Add a product-neutral contract through which a Bee product can create a BeeUI session for an already verified external principal and safely use BeeUI inside an allowlisted cross-site iframe.

#### Scope

- add public server-side session issuance for a verified principal and explicit `UserRole`;
- do not perform external authentication inside BeeUI;
- centralize session cookie setting and deletion;
- add a configurable session lifetime;
- add allowlisted `auth.cookie_samesite`;
- require `cookie_secure=true` with `SameSite=None`;
- add controlled exact `security.frame_ancestors`;
- preserve the default `DENY` framing policy;
- when embedding is allowed, generate a compatible CSP and do not send conflicting `X-Frame-Options: DENY`;
- keep current token login backward-compatible;
- add product-neutral integration documentation and tests.

#### Excluded

- Bitrix-specific OAuth;
- BeeAgent, ROP, or CRM semantics;
- external identity-provider clients;
- OIDC discovery;
- a user directory or role mapping;
- database-backed sessions;
- cross-product SSO service;
- wildcard frame origins;
- dependency changes.

#### Deliverable

A Bee product can pass an already verified `user_id` and role to BeeUI, receive a signed session response with a controlled cookie policy, and allow embedding only from exact configured origins.

#### Acceptance criteria

- existing token login works unchanged;
- verified-principal sessions are created only through an explicit server-side API;
- arbitrary browser requests cannot choose their own role;
- the default cookie remains `SameSite=Lax`;
- `SameSite=None` is accepted only with `Secure`;
- session lifetime is bounded and validated;
- the default response retains `X-Frame-Options: DENY`;
- a configured frame origin produces exact `frame-ancestors`;
- wildcard and malformed origins are rejected;
- no product-specific imports, labels, or behavior;
- public integration contract documented.

#### Checks

- AuthService session issuance tests;
- session signing, expiry, and role validation tests;
- existing login/logout regression tests;
- cookie attribute tests;
- invalid SameSite/Secure combinations;
- frame-origin validation and response-header tests;
- route-prefix tests;
- SAST and DAST-style auth/header misuse review;
- `uv run pytest -q`;
- `./start.sh doctor`;
- browser iframe smoke through a generic test consumer.

#### DoD

- the public verified-principal session contract is implemented;
- cookie policy is centralized;
- controlled embedding preserves default-deny behavior;
- existing consumers remain backward-compatible;
- BeeUI remains product-neutral;
- tests and integration documentation are updated;
- dependencies unchanged;
- `pyproject.toml.version` unchanged.

### Iteration 13.14 — Request-scoped navigation visibility

**Status:** DONE

#### Goal

Add a product-neutral request-scoped navigation visibility contract so that an embedded Bee product can hide navigation paths unavailable to the user without product-specific Jinja forks or moving authorization semantics into BeeUI.

#### Scope

**Included:**

- add an optional public navigation visibility resolver to `create_beeui_app(...)`;
- expose the contract through `mount_beeui(...)`;
- the resolver receives the current request and canonical navigation path or an equivalent bounded context;
- `False` excludes a navigation leaf from the rendered sidebar;
- groups with no visible children do not render;
- absence of a resolver fully preserves current behavior;
- apply the resolver to all generic shell rendering paths;
- preserve the route prefix;
- preserve locale/query-preserving navigation;
- preserve active/descendant-active behavior;
- preserve configured, adapter, metadata/product-console, and detail-page rendering;
- document that the visibility contract is not route authorization;
- add product-neutral tests and integration documentation.

#### Excluded

- BeeAgent-specific scopes;
- ROP/BeeScan semantics;
- user directory;
- role-to-product mapping;
- route authorization;
- artifact authorization;
- new session claims;
- changes to `UserRole`;
- external identity provider;
- dependency changes.

#### Deliverable

A Bee product can provide BeeUI with a generic per-request decision:

```text
canonical navigation path → visible / hidden
```

and BeeUI applies it to all sidebar rendering without independently deciding product permissions.

#### Acceptance criteria

- no resolver preserves current navigation byte/behavior compatibility where practical;
- the resolver can hide a single leaf;
- nested groups with no visible children are hidden;
- visible siblings remain;
- the route prefix is preserved;
- RU/EN locale links are preserved;
- active state remains correct;
- configured pages use the resolver;
- adapter/product-console pages use the resolver;
- generic detail pages use the same visibility behavior;
- the resolver does not provide route security;
- public documentation explicitly states the presentation-only boundary;
- no consumer-specific imports/labels/logic.

#### Checks

- full `uv run pytest -q`;
- navigation visibility unit/integration tests;
- nested navigation filtering;
- empty group filtering;
- no-resolver backward compatibility;
- locale regression;
- route-prefix regression;
- configured/adapter/product-console/detail rendering regression;
- malformed/failing resolver safe behavior;
- HTML escaping regression;
- SAST;
- browser smoke with a generic consumer.

#### DoD

- the public generic visibility hook is implemented;
- all BeeUI shell render paths use the same contract;
- existing consumers remain compatible without configuration changes;
- BeeUI does not perform product authorization;
- no product-specific semantics;
- docs and tests are updated;
- dependencies unchanged;
- `pyproject.toml.version` unchanged;
- implementation is ready for a BeeUI release.

### Iteration 13.15 — Responsive Web navigation and adapter runtime v1

**Status:** DONE

#### Goal

Add a product-neutral responsive web runtime for adapter-backed BeeUI pages: configured page tabs must optionally switch server-rendered content without fully reloading the shared shell, and synchronous product adapters must not block the async web event loop.

#### Scope

- add optional `pages[].tabs.progressive`;
- preserve canonical internal `href` as the authoritative navigation contract;
- with `progressive: true`, perform same-origin tab navigation through `fetch`;
- replace only the matching page-tabs content surface;
- cancel stale requests through `AbortController`;
- update the browser URL through the History API only after a successful transition;
- support Back/Forward through `popstate`;
- preserve direct URL and browser refresh behavior;
- perform normal canonical navigation on progressive failure;
- make BeeUI browser component initialization repeatable after DOM replacement;
- preserve existing live `data_table` behavior after transitions;
- reinitialize Datepicker after transitions;
- reinitialize charts after transitions;
- allow only controlled BeeUI-owned package-local runtime assets;
- prohibit execution of arbitrary scripts from fetched HTML;
- add an optional controlled `icon` for page-tab items;
- implement existing `icons` and `fill_icons` variants through BeeUI-owned Tabler-style SVG mapping;
- add a shared async-safe execution boundary for synchronous adapter methods called from async BeeUI routes;
- apply it to relevant adapter-backed HTML/API routes;
- preserve existing adapter result/error contracts;
- preserve locale, theme, route-prefix, embedded mount, auth/session, navigation visibility, and safe-link behavior;
- update public web/component/integration documentation.

#### Excluded

- React;
- Vue;
- Svelte;
- SPA architecture;
- HTMX;
- Turbo;
- client-side product data store;
- product-specific caching;
- product-specific tab semantics;
- infinite scroll;
- arbitrary adapter-provided JavaScript;
- arbitrary external runtime assets;
- CDN;
- tracking;
- changes to BeeAgent or domain repositories;
- new Python dependencies;
- new browser dependencies;
- a version bump in the feature PR.

#### Deliverable

BeeUI provides opt-in progressive page tabs over canonical server-rendered GET routes and executes synchronous product adapters outside the async event loop.

Existing consumers without `progressive` continue to work unchanged.

#### Acceptance criteria

- existing page tabs without `progressive` preserve current navigation behavior;
- `progressive: false` preserves normal document navigation;
- `progressive: true` does not fully reload the document on a successful transition;
- canonical `<a href>` is preserved for each tab;
- only the matching page-tabs surface is replaced;
- stale responses cannot overwrite a newer transition;
- the URL changes only after a successful response;
- direct URLs and refresh work;
- Back/Forward work;
- malformed, failed, or unsafe transitions safely fall back to normal navigation;
- arbitrary fetched scripts do not execute;
- runtime assets are restricted to BeeUI-owned package-local assets;
- live tables work after tab replacement;
- Datepicker works after tab replacement;
- charts work after tab replacement;
- optional tab icons do not accept raw SVG/HTML;
- unknown icons degrade safely;
- synchronous adapter work does not run directly in the async event loop;
- slow adapter requests do not block unrelated lightweight BeeUI routes at the event-loop level;
- route-prefix and embedded mounts work;
- RU/EN work;
- light/dark work;
- GET routes remain read-only;
- no product-specific logic;
- no external runtime resources.

#### Checks

- `uv run pytest -q`;
- page-tabs schema/config tests;
- progressive/non-progressive rendering tests;
- safe/unsafe href tests;
- rapid transition / stale request tests;
- failure fallback tests;
- History API Back/Forward tests;
- route-prefix tests;
- embedded-mount tests;
- live-table reinitialization tests;
- Datepicker reinitialization tests;
- chart reinitialization tests;
- synchronous adapter concurrency regression;
- HTML escaping tests;
- controlled icon tests;
- no arbitrary script execution check;
- no external runtime asset check;
- browser smoke in RU/EN and light/dark;
- SAST;
- DAST-style navigation/resource misuse review.

#### DoD

- the progressive page-tabs contract is implemented and documented;
- async-safe adapter execution is implemented through a shared generic boundary;
- existing non-progressive consumers remain compatible;
- the existing live-table contract remains compatible;
- route-prefix and embedded integration are preserved;
- dynamic BeeUI components work correctly after transitions;
- no product-specific semantics are added;
- no frontend framework is added;
- no dependencies/vendor assets are added;
- package-local behavior is preserved;
- tests and browser verification pass;
- `pyproject.toml.version` unchanged;
- `uv.lock` unchanged.

### Iteration 13.16 — Generic bounded table actions v1

**Status:** DONE

#### Goal

Add a product-neutral presentation contract for bounded operator actions within canonical `data_table` so that Bee products can safely provide toolbar/row write actions through existing BeeUI auth/role/CSRF and `/api/actions/*` contracts without their own Jinja/JavaScript implementations.

#### Scope

- extend canonical `data_table` with an opt-in bounded action contract for toolbar and row actions;
- keep existing GET/href actions backward-compatible;
- support explicit `action_id`, a controlled label, optional bounded confirmation, and bounded args;
- support minimal interactive fields v1: `text` and `email`, including bounded initial/default values;
- use existing `POST /api/actions/preview` and `POST /api/actions/execute`;
- use the existing CSRF contract;
- preserve default `preview_confirm_execute`: Preview, separate explicit confirmation, and Execute;
- support explicit opt-in `direct_execute`: protected Execute without browser Preview/confirmation for toolbar forms and controlled inline-row editing;
- support controlled icon-only row actions and strictly table-only refresh after successful direct table mutations without document reload;
- support route prefixes and embedded mounts;
- safely display success/validation/denied/error results;
- validate action presentation payloads with fail-safe behavior;
- preserve Jinja autoescape and controlled rendering;
- update public component/web/integration/security documentation if the contract changes.

#### Excluded

- product-specific ROP/Bitrix/blacklist semantics;
- generic no-code form builder;
- arbitrary POST URLs;
- arbitrary JavaScript/HTML from config or adapter;
- arbitrary action methods;
- secret inputs;
- file upload;
- config editor;
- new auth/session model;
- new product execution authority;
- direct external API calls from BeeUI;
- database/storage implementation;
- frontend build chain;
- new runtime dependencies unless necessary.

#### Deliverable

The generic BeeUI `data_table` contract allows product adapters/render payloads to safely express bounded toolbar or row operator actions, including bounded email/text fields, initial/default values, controlled icons, and generic inline-row editing. Default `preview_confirm_execute` retains Preview, explicit confirmation, and Execute. Explicit opt-in `direct_execute` uses only protected Execute without browser Preview/confirmation; successful direct table mutations refresh only the matching live table, while bounded refresh failures remain visible without document navigation. Server auth/role/CSRF/product validation remain authoritative.

Existing GET tables/actions remain backward-compatible.

#### Acceptance criteria

- existing `data_table` GET toolbar and href actions render and behave unchanged;
- bounded action is opt-in and cannot be inferred from ordinary href actions;
- viewer cannot execute an operator action;
- operator can invoke configured bounded action through existing action endpoints;
- missing/invalid CSRF rejects request before product callback;
- interactive email/text field values are bounded and escaped;
- unknown/malformed action presentation degrades safely;
- no mutation is possible through GET;
- default action flow performs preview, explicit confirmation and then execute;
- explicit direct action calls protected Execute without browser preview or confirmation and never reloads the document after successful table mutation;
- direct refresh failure remains visibly bounded and does not navigate the document;
- unsafe/external URLs are not accepted as action destinations;
- arbitrary HTML/JS cannot be supplied through action metadata;
- route prefix is applied correctly;
- embedded/iframe presentation works with existing embedding contract;
- product adapter remains the sole owner of action semantics;
- BeeUI does not contain ROP/Bitrix-specific behavior.

#### Checks

```text
uv run pytest -q
./start.sh doctor
```

Targeted checks:

- existing data_table regression tests;
- toolbar bounded-action rendering;
- row bounded-action rendering;
- email/text input validation;
- HTML escaping/XSS cases;
- viewer → forbidden;
- operator + valid CSRF → callback invoked;
- invalid/missing CSRF → callback not invoked;
- malformed/unknown action → bounded error/degraded state;
- default preview → confirmation → execute flow and direct execute flow;
- direct table refresh success/failure without document navigation;
- route-prefix behavior;
- embedded mount behavior;
- GET does not mutate;
- no secret-like values exposed in HTML/API/logs;
- DAST-style route tests for protected POST paths;
- SAST/security review of action/HTML trust boundary.

SCA is not required if dependencies do not change.

#### DoD

- generic bounded table action contract implemented;
- no product-specific semantics added;
- existing table behavior backward-compatible;
- tests pass;
- route-prefix/embedded behavior verified;
- CSRF/role boundary verified;
- action payload and field presentation remain bounded;
- default and direct flows remain explicit and backward-compatible;
- docs updated where public contract changed;
- no new dependency unless separately justified;
- `pyproject.toml.version` not changed;
- PR reviewed and merged.

---

## Stage 7 — Consumer integration record

### Iteration 14 — BeeAgent adapter fixture MVP

**Status:** RETIRED

#### Reason

The original iteration goal was achieved through actual product-side BeeAgent integration rather than an additional BeeAgent-shaped fixture inside BeeUI.

Actual production integration lives in `beeagent`:

```
src/beeagent_module/interfaces/ui/
  app.py
  adapter.py
  read_model.py
  artifacts.py
```

---

## Stage 8 — Future frontend/no-code/standalone

### Iteration 15 — Dashboard schema editor v0

**Status:** FUTURE

#### Goal

Prepare the first step toward a no-code builder: dashboard schema editing through the UI.

#### Scope

Included:

- list pages;
- list blocks;
- enable/disable block;
- reorder blocks;
- change width;
- preview schema;
- validate before save;
- backup/audit.

Excluded:

- drag-and-drop;
- arbitrary HTML;
- custom JS;
- plugin marketplace;
- full frontend builder;
- product runtime controls;
- broker/provider actions.

#### Deliverable

Operators can change layouts through a safe schema without manually editing YAML.

#### Checks

- block enable/disable;
- reorder;
- invalid layout rejection;
- audit;
- no arbitrary HTML/JS injection;
- `uv run pytest -q`.

#### DoD

- the visual builder edits only the schema;
- schema validation protects the layout;
- unsafe templates/scripts are rejected;
- the source of truth remains product/config-owned.

### Iteration 16 — Separate frontend contract v0

**Status:** FUTURE

#### Goal

Prepare the BeeUI backend for a separate frontend without rewriting product adapters.

#### Scope

Included:

- stable API versioning;
- OpenAPI/schema review where applicable;
- frontend-safe envelopes;
- static frontend mount placeholder;
- a CORS policy for controlled standalone mode;
- API docs;
- fixture payloads for frontend development.

Excluded:

- React/Vue/Svelte implementation;
- public SaaS;
- multi-tenant auth;
- websocket/SSE streaming;
- new runtime semantics;
- direct product storage access from the frontend.

#### Deliverable

BeeUI can serve as the backend for a future separate frontend.

#### Checks

- API schema snapshot;
- envelope compatibility;
- CORS disabled by default;
- no secret leakage;
- `uv run pytest -q`.

#### DoD

- the frontend can connect to a stable backend API;
- the server-rendered UI continues to work;
- no second source of truth is added;
- product adapters remain the canonical product boundary.

### Iteration 17 — Standalone BeeUI service v0

**Status:** FUTURE

#### Goal

Add standalone mode, where BeeUI runs as a separate service and connects to Bee products through HTTP APIs.

#### Scope

Included:

- `beeui web --config ...`;
- HTTP product adapter;
- product registry;
- backend health checks;
- timeout/degraded states;
- explicit standalone deployment docs.

Excluded:

- distributed auth platform;
- service mesh;
- multi-tenant SaaS;
- broker/runtime authority;
- direct product filesystem reads;
- replacing embedded mode.

#### Deliverable

BeeUI can run as a separate service over BeeCap/BeeAgent APIs.

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
- backend product APIs remain the source of truth;
- a degraded backend does not break the entire UI;
- no direct runtime authority is added.

---

## BeeUI framework MVP baseline

**Status:** ACHIEVED

The reusable BeeUI framework baseline has been implemented and supports embedded product integration.

The implemented generic BeeUI baseline includes:

```
Foundation and schema
→ local Tabler shell
→ reusable components and blocks
→ data resolver
→ ProductUiAdapter contract
→ embedded app/mount API
→ artifact browser
→ adapter-backed product console
→ generic custom pages
→ auth/session/CSRF boundary
→ locale-aware shell and persistence
→ theme persistence
→ charts and advanced tables
→ generic detail pages
→ Tabler Datepicker
→ canonical functional table toolbar
```

The minimum practical MVP is achieved when:

- `beeui` runs independently as a demo;
- `beeui` integrates with `beecap` as a dependency;
- BeeCap has a product-side `BeeCapUiAdapter`;
- BeeUI is mounted in BeeCap under `/beeui`;
- BeeUI renders dashboard/runs/run detail/venue dashboards through the adapter;
- BeeCap `/beeui` is useful for daily read-only monitoring;
- BeeCap switches canonical `/` to the BeeUI-backed console;
- the legacy BeeCap web UI remains only as a fallback under `/legacy`;
- current BeeCap web templates are no longer extended manually;
- BeeCap provides only adapters/read-models/artifacts/callbacks;
- tests green;
- no mutation/secrets/provider calls/broker calls.

## Integration model for Bee products

### Embedded mode

The MVP integration mode.

```text
beecap process
  imports beeui
  creates BeeCapUiAdapter
  creates/mounts BeeUI FastAPI app
```

Advantages:

- fast;
- a single process;
- simpler local development;
- simpler auth/session handling;
- no CORS/service discovery.

Disadvantages:

- each product runs its own BeeUI instance;
- BeeUI upgrades come through dependency updates.

### Standalone mode

A future integration mode.

```text
beeui service
  connects to beecap API
  connects to beeagent API
  renders multi-product UI
```

Advantages:

- a single UI service;
- a simpler central operator dashboard;
- readiness for a separate frontend.

Disadvantages:

- more complex auth;
- CORS;
- service discovery;
- deployment complexity.

Decision:

```text
MVP: embedded mode.
Later: standalone.
```

## Rules for BeeCap/BeeAgent after adopting BeeUI

Bee products must not reimplement:

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

Bee products must implement:

- product read-model;
- artifact allowlist;
- product-specific summaries;
- config validation callback;
- bounded action callbacks;
- authority/security-sensitive checks.

## BeeCap migration rule

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

Final target BeeCap structure:

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

BeeCap must no longer own:

```text
src/beecap_module/web/templates/
src/beecap_module/web/static/
src/beecap_module/web/app.py
```

after full parity and legacy removal.

## Related documents

Use the following documents alongside this ROADMAP when implementing iterations:

- `docs/SDLC.md` — lightweight process, change levels, required quality/security checks, and DoD flow;
- `docs/SECURITY.md` — secure development rules and security checks;
- `docs/INTEGRATION.md` — how to integrate BeeUI with BeeCap/BeeAgent;
- `docs/COMPONENTS.md` — reusable blocks/components contract;
- `docs/API_CONTRACT.md` — JSON API envelopes and route contracts;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;
- `docs/THEME.md` — theme/customization contract.
