# Copilot instructions for beeui

## Project identity

`beeui` is a reusable Python/FastAPI/Jinja2/Tabler UI layer for Bee products.

Core rule:

```text
BeeUI renders.
Product decides.
```

BeeUI provides:

* FastAPI + Jinja2 + Tabler-compatible web surface;
* declarative pages/navigation/layout/theme;
* reusable UI blocks;
* read-model presentation;
* product adapter integration;
* safe artifact/config/operator UI foundation when the relevant roadmap iteration allows it;
* future stable JSON API and future no-code/dashboard builder foundation.

BeeUI is not:

* a trading engine;
* an agent runtime;
* a broker/runtime executor;
* a direct MCP/tool executor;
* a second source of truth;
* a standalone service before the relevant roadmap iteration;
* a no-code builder before the relevant roadmap iteration.

## Stack and execution

Use existing project conventions:

* Python 3.14+
* `uv`
* `src` layout
* package: `beeui_module`
* FastAPI
* Jinja2
* local Tabler-compatible assets
* YAML config/schema
* pytest
* `start.sh` + `config/start.py` as the main execution path

Use these commands unless the task explicitly requires otherwise:

```bash
uv run pytest -q
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

All suggested commands must use `uv run` or `./start.sh`.

Do not change `pyproject.toml.version` unless the task is explicitly about release/versioning.

If the task is not about release/versioning, report:

```text
pyproject.toml.version: version not changed
```

## Current documentation map

Current project docs are:

* `docs/ARCHITECTURE.md`
* `docs/CONFIG.md`
* `docs/CONTRIBUTING.md`
* `docs/DEV_GUIDE.md`
* `docs/ROADMAP.md`
* `docs/SDLC.md`
* `docs/SECURITY.md`
* `docs/SPEC.md`
* `docs/WEB_UI.md`
* `README.ru.md`

Do not reference non-existing docs as required files.

Use this mapping:

* `docs/ROADMAP.md` — iteration scope, status, deliverable, checks, DoD.
* `docs/SDLC.md` — change levels, required checks, PR workflow, DoD process.
* `docs/SECURITY.md` — trust boundary, secrets, route/input/path/template/config/API/artifact/action security.
* `docs/DEV_GUIDE.md` — developer workflow, startup commands, dependency workflow, integration guidance, AI prompt guidance.
* `docs/WEB_UI.md` — HTML routes, layout, templates, navigation, static assets, web shell behavior.
* `docs/CONFIG.md` — config/schema/source-of-truth rules.
* `docs/ARCHITECTURE.md` — architecture decisions, layer boundaries, integration boundaries.
* `docs/SPEC.md` — product/specification-level behavior.
* `docs/CONTRIBUTING.md` — contribution, branch, commit and PR conventions.
* `README.ru.md` — public/user-facing project overview, current status, setup, current capabilities, examples.

Read docs conditionally. Do not read all docs by default.

## Roadmap and scope discipline

Always align the task with the stated current iteration from `docs/ROADMAP.md`.

Read the current ROADMAP iteration section and directly relevant nearby context. Do not read the whole roadmap unless required.

Do not implement features from later iterations early.

Do not introduce before the relevant roadmap iteration:

* product adapters;
* auth/session/RBAC;
* config apply/write;
* operator action execution;
* standalone service mode;
* HTTP product adapter;
* arbitrary CSS editor;
* arbitrary JS;
* arbitrary HTML blocks;
* no-code dashboard builder;
* artifact upload/edit/delete;
* direct product runtime/broker/agent/tool execution.

Keep the change scoped to the issue and current iteration.

Use KISS:

* minimal necessary changes;
* no unrelated refactor;
* no broad rewrites;
* no speculative abstractions;
* no hidden fallback behavior;
* no silent authority escalation.

## Architecture rules

BeeUI owns:

* UI rendering;
* page/navigation/layout/theme rendering;
* generic reusable blocks;
* read-model presentation;
* safe HTML/API surface;
* generic artifact/config/action UI shell only when the relevant iteration allows it.

Bee products own:

* runtime behavior;
* business/domain logic;
* product artifacts;
* product config validation;
* bounded execution APIs;
* authority/security-sensitive checks;
* product-specific summaries and semantics.

Product adapter is the only BeeUI-side boundary that may know product-specific semantics.

Generic BeeUI code must not know domain concepts such as:

* MRKT;
* Binance;
* ROP;
* broker;
* strategy;
* cycle;
* order;
* capability;
* MCP tool;
* BeeAgent policy;
* BeeCap trading logic.

Generic renderers must work with normalized schema/config/read-model data, not product internals.

## Source of truth rules

UI source of truth:

```text
config/schema.yml in current demo/MVP mode
config/beeui.yml in planned/future product integration mode after adapter/block/data-source iterations
```

Product source of truth remains in product config, product artifacts and product APIs.

Do not create a second source of truth.

Do not duplicate product runtime settings into BeeUI-owned config unless the field is strictly a UI/layout/schema field.

If a new required config/schema key is added, it must have:

* fail-fast validation;
* tests for missing/invalid values;
* docs/example config update when public contract changes;
* clear ownership explanation.

Secrets must not appear in:

* `beeui.yml`;
* `config/schema.yml`;
* HTML;
* JSON API responses;
* logs;
* artifacts;
* committed test fixtures.

## Change levels

Classify each change as one of:

### low-risk

Use for:

* docs-only changes;
* local tests;
* safe naming/comment cleanup;
* safe template/style changes without contract/security impact;
* read-only UI presentation changes that do not change routes/API/schema/security boundaries.

Expected checks usually include:

```bash
uv run pytest -q
```

Add relevant smoke checks if web behavior is touched.

### runtime-risk

Use for changes affecting runtime behavior or contracts:

* config schema;
* page schema;
* block schema;
* route behavior;
* API response envelope;
* adapter contract;
* artifact parsing;
* data resolver;
* config preview/apply;
* product integration;
* startup behavior;
* CLI behavior.

Expected checks usually include:

```bash
uv run pytest -q
./start.sh doctor
./start.sh routes
```

Add route/API/schema/malformed-input tests as relevant.

### security-sensitive

Use for trust-boundary changes:

* auth/session/cookies;
* CSRF;
* file/path access;
* artifact browser;
* config apply/write;
* operator actions;
* secrets redaction;
* external product HTTP adapter;
* HTML/API exposure of untrusted payloads;
* dependency surface affecting runtime/security.

Expected checks include runtime-risk checks plus relevant security checks:

* path traversal rejection;
* invalid ID/input rejection;
* no arbitrary filesystem access;
* no secret leakage in HTML/API/logs/artifacts;
* no unsafe HTML/JS injection;
* no direct runtime/broker/tool authority;
* audit artifacts for write/action attempts when write/action behavior is in scope.

## Security rules

BeeUI is on a trust boundary.

Treat all external/product/config/route values as untrusted unless validated.

Required rules:

* read-only by default;
* HTML autoescape must remain enabled;
* do not render arbitrary HTML from config/product data;
* do not accept arbitrary JS snippets;
* do not use unsafe Jinja `|safe` unless explicitly justified and tested;
* validate route params and IDs;
* do not build filesystem paths directly from route params/query params;
* block path traversal for file/artifact/config routes;
* serve static assets only from controlled package-local static paths;
* do not introduce external CDN/script/tracking dependencies unless explicitly required and reviewed;
* do not expose `.env`, raw secrets, tokens, credentials or full unredacted config;
* do not dump full config/Jinja context/payloads to logs;
* no hidden write side effects in read-only routes;
* no direct shell command execution from UI;
* no direct broker/runtime/tool/agent execution from BeeUI.

If a POST/write/control route is added in an allowed iteration, it must have:

* explicit scope;
* validation;
* bounded product callback/API;
* audit trail;
* rejection behavior;
* no secret leakage;
* CSRF/auth consideration where relevant.

## Web/Jinja/static rules

Use package-local templates and static assets.

Do not copy uncleaned upstream demo pages wholesale.

Do not include:

* tracking scripts;
* analytics snippets;
* external scripts/styles;
* sponsor/demo-only assets;
* arbitrary user-provided HTML;
* unsafe inline JS from config.

Keep logs, JSON fields, API/runtime messages and internal errors in English.

Russian comments are allowed only when they clarify project-specific intent that would otherwise be lost.

## Config/schema rules

For `config/schema.yml` / `beeui.yml`:

* validate fail-fast;
* reject unknown unsafe fields if the current schema does not support them;
* reject arbitrary CSS/JS/HTML fields;
* reject external navigation links unless explicitly supported by the current iteration;
* validate page IDs, page paths, nav paths and block IDs;
* reject duplicate IDs/paths;
* ensure nav paths reference declared pages where required by the current schema;
* keep schema-owned UI configuration separate from runtime/product config.

When changing schema, final response must state:

* where the key lives;
* why it belongs there;
* why it does not create a second source of truth;
* how it is validated;
* what tests cover missing/invalid cases.

## API rules

If JSON API is touched, use stable envelopes.

Success/partial/error shapes must be deterministic and documented when public contract changes.

Do not return stack traces or raw internal exceptions.

Invalid input should return bounded errors.

Missing/partial product data should be explicit and should not crash page/API.

If API contract changes, include an example response envelope in the final response and update relevant docs.

## Adapter rules

Product adapters are the only integration boundary for Bee products.

BeeUI must not crawl product internals directly unless the current iteration explicitly implements a safe adapter-backed artifact/config mechanism.

Adapters must enforce product ownership over:

* artifact allowlists;
* config validation;
* bounded actions;
* authority checks;
* product-specific read-model semantics.

Write/action methods must be unavailable by default unless explicitly implemented by product-owned callbacks/API in the relevant iteration.

## Artifact rules

Artifact access must be allowlisted and adapter-owned.

Do not implement arbitrary filesystem browsing.

Do not mutate source artifacts from read-only routes.

For artifact-related changes, test or review:

* safe IDs;
* path traversal rejection;
* non-allowlisted artifact rejection;
* malformed/partial artifact behavior;
* large file preview limits if relevant;
* no secret leakage;
* no source artifact mutation.

## Documentation rules

Update docs only when the task changes the corresponding contract or user/developer behavior.

Read or update `README.ru.md` only when public behavior, startup commands, config examples, route/API behavior, documented status or user-facing workflow changes.

Read or update `docs/DEV_GUIDE.md` only when developer workflow, dependency workflow, integration guidance or AI prompt guidance changes.

Read or update `docs/SECURITY.md` only when a security boundary is touched.

Read or update `docs/SDLC.md` only when change levels, required checks, PR process or DoD rules change.

Read or update `docs/WEB_UI.md` when HTML routes, layout, templates, navigation, static assets or web shell behavior changes.

Read or update `docs/CONFIG.md` when config/schema/source-of-truth behavior changes.

Read or update `docs/ARCHITECTURE.md` when layer boundaries or architecture decisions change.

Read or update `docs/SPEC.md` when product-level behavior/specification changes.

Read or update `docs/CONTRIBUTING.md` when contribution/branch/commit/PR conventions change.

Read or update `docs/ROADMAP.md` when iteration status, scope, deliverable or checks change.

Do not update docs mechanically if no relevant contract or behavior changed.

## Dependency rules

Ordinary `./start.sh` must not mutate `uv.lock`.

Do not add or update dependencies unless explicitly required.

If dependencies change:

* use `uv add`, `uv remove` or `uv lock` as appropriate;
* commit both `pyproject.toml` and `uv.lock` when both change;
* keep dependency changes in a separate PR when practical;
* treat security-sensitive dependency surface changes as `security-sensitive`.

## Testing rules

Always identify required checks for the chosen change level.

Common checks:

```bash
uv run pytest -q
./start.sh doctor
./start.sh routes
./start.sh web --host 127.0.0.1 --port 8780
```

Add targeted tests when touching:

* config/schema validation;
* pages/navigation;
* block rendering;
* routes/API;
* static assets;
* templates;
* adapters;
* artifacts;
* security boundaries;
* malformed input;
* partial/missing data;
* docs-visible examples.

Do not claim tests were run unless they were actually run.

If tests were not run, say so clearly and explain why.

## Reading rules

Start from minimal relevant context.

Do not read broad unrelated files by default.

Before reading additional files, state:

* path;
* why it is needed;
* what decision depends on it.

Prefer targeted reading over full-repository exploration.

Use the current task, current ROADMAP iteration and directly affected files as the scope boundary.

## Response rules

Before editing, respond with:

1. `Что прочитал`
2. `План`
3. `Change level`
4. `Required checks`
5. `Files to change`
6. `Нужны ли дополнительные файлы`

After editing, respond with:

1. `Что прочитал`
2. `Что изменил`
3. `Change level`
4. `Required checks`
5. `Source of truth after change`
6. `Tests`
7. `Security review`
8. `Docs`
9. `pyproject.toml.version`
10. `Что написать в PR`

Keep responses concise.

Do not include full diffs unless explicitly requested.

For every new or changed config/schema key, state:

* where it lives;
* why it lives there;
* why it is not a second source of truth;
* how it is validated;
* what tests cover it.

For PR text, include:

* `Summary`
* `Tests`
* `Security review`
* `Docs`

If the task is not release/versioning, always report:

```text
pyproject.toml.version: version not changed
```
