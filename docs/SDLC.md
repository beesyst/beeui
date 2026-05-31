Да. Ниже готовый `docs/SDLC.md` под `beeui`.

# SDLC — BeeUI

## Purpose

This document defines the lightweight SDLC used in `beeui`.

The goal is to keep development:

- disciplined;
- reproducible;
- easy to follow;
- safe enough for real engineering work;
- free from unnecessary bureaucracy.

`beeui` uses a practical workflow:

`ROADMAP → Issue → branch → code → tests → UI/API checks → PR → merge`

This document does not replace `docs/ROADMAP.md`.

- `ROADMAP` defines where the project goes by stages and iterations.
- `Issue` defines one concrete task.
- `PR` proves what was actually delivered and how it was verified.
- `SDLC` defines the working rules for moving changes through the project.

## Product-specific context

`beeui` is a reusable UI/backend framework for Bee products.

It provides:

- FastAPI web app foundation;
- Jinja2 templates;
- Tabler-based UI shell;
- reusable dashboard blocks;
- declarative pages/navigation;
- product adapters;
- artifact browser;
- read-only JSON APIs;
- bounded config/admin/operator controls;
- future no-code/dashboard-builder foundation.

`beeui` must not become a product runtime engine.

Domain products such as `beecap` and `beeagent` remain responsible for:

- business logic;
- runtime behavior;
- artifact semantics;
- config validation;
- execution authority;
- security-sensitive product actions.

`beeui` is responsible for:

- rendering;
- layout;
- reusable UI components;
- adapter contracts;
- safe artifact presentation;
- HTML/API consistency;
- auth/session UI layer when enabled;
- bounded UI workflows.

Main rule:

```text
BeeUI renders.
Product decides.
```

## Core principles

Development in `beeui` should follow these rules:

- make small, iteration-sized changes;
- stay inside the current iteration scope;
- prefer simple schema-driven UI over premature no-code complexity;
- keep product-specific logic outside generic BeeUI core;
- do not duplicate BeeCap/BeeAgent runtime logic in BeeUI;
- use product adapters as the boundary between BeeUI and product semantics;
- keep HTML autoescape enabled;
- validate schema/config fail-fast;
- keep logs understandable;
- keep UI/API responses reproducible;
- do not leak secrets into HTML, JSON API, logs or artifacts;
- block path traversal and arbitrary filesystem access;
- keep read-only routes read-only;
- write/control actions must go through bounded product callbacks/API;
- close work through PR, not only through comments.

## Workflow

### 1. ROADMAP

`docs/ROADMAP.md` defines:

- stage;
- iteration;
- goal;
- scope;
- deliverable;
- checks;
- DoD.

Before coding, the task should be mapped to the current iteration.

### 2. Issue

Each task should be described in an issue.

The issue should contain at least:

- summary;
- context;
- scope;
- deliverable;
- acceptance criteria;
- tests;
- UI/API checks;
- security notes if relevant.

The issue explains **what must be done**.

### 3. Branch

All implementation work should be done in a separate branch.

Recommended naming:

- `feature/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`
- `chore/<short-name>`

If useful, include iteration number:

- `feature/iter-0-skeleton`
- `feature/iter-1-tabler-shell`
- `feature/iter-6-beecap-adapter`
- `docs/sdlc-security-guidelines`

### 4. Code

Implementation rules:

- stay within the current iteration scope;
- do not mix unrelated features in one PR;
- do not add “future architecture” without current need;
- do not hardcode product-specific behavior into generic BeeUI core;
- do not make BeeUI read arbitrary product filesystem paths directly;
- do not introduce hidden defaults for security-sensitive behavior;
- do not remove existing checks without reason;
- prefer adapter interfaces over special-case branches;
- prefer schema validation over runtime guessing.

Preferred style:

- KISS;
- minimal changes;
- predictable behavior;
- PEP 8;
- explicit validation;
- clear route boundaries;
- testable helpers.

### 5. Tests

Every change should be verified at the level appropriate for its risk.

Common checks:

- automated tests: `uv run pytest -q`;
- smoke run through the expected entrypoint;
- route/API checks for web behavior;
- manual HTML inspection if UI changed;
- manual log inspection if logs changed;
- manual fixture/artifact inspection if artifact rendering changed.

If the change affects route exposure, file/path handling, auth, sessions, config mutation, product adapters, external payload parsing, serialization or dependencies, security/quality checks may also be required.

See `docs/SECURITY.md`.

### 6. UI/API checks

For web-facing changes, verify:

- route returns expected status code;
- route does not mutate source files unless explicitly designed as a bounded write route;
- response does not expose secrets;
- HTML autoescape is preserved;
- API response envelope is stable;
- error states are explicit;
- missing/partial/corrupted data does not crash the whole app;
- invalid IDs and path traversal attempts are rejected;
- static assets are loaded from controlled paths.

Typical route checks:

- `GET /`
- `GET /health`
- `GET /api/...`
- relevant product/dashboard routes for the current iteration.

### 7. Artifacts and fixtures

`beeui` itself should not own product runtime artifacts.

When tests need product-like data, use fixtures.

Typical fixture areas:

- `tests/fixtures/demo_static/`
- `tests/fixtures/beecap/`
- `tests/fixtures/beeagent/`

Artifacts/read-models should be:

- reproducible;
- understandable;
- aligned with adapter contracts;
- safe to parse;
- safe to render.

`beeui` must not silently invent missing product state.

### 8. Pull Request

A PR is the main evidence that the task is ready.

The PR should contain:

- summary;
- related issue;
- iteration reference;
- scope;
- changes;
- tests;
- UI/API checks;
- security notes;
- screenshots or route examples when useful;
- notes for reviewer.

The PR explains **what was actually delivered and verified**.

### 9. Merge

A task or iteration item is considered completed only after:

- scope is satisfied;
- required checks are completed;
- UI/API behavior is consistent;
- logs are understandable where applicable;
- docs are updated where contracts changed;
- PR is reviewed;
- changes are merged.

## Definition of Done

A task is considered done when:

- behavior is implemented within the declared scope;
- the feature runs through the intended entrypoint;
- `uv run pytest -q` passes;
- relevant smoke checks pass;
- HTML autoescape remains enabled;
- route behavior is tested if routes changed;
- API response shape is tested if API changed;
- schema/config validation is fail-fast where applicable;
- product-specific behavior is kept behind adapters;
- read-only routes do not mutate files;
- write/control routes, if any, use validation and audit;
- secrets do not leak into HTML/API/logs/artifacts;
- path traversal and arbitrary filesystem access are blocked;
- docs are updated if behavior, contract, routes, APIs, checks or security expectations changed;
- result is documented in PR and ready for merge.

## Minimal required checks

These are the default checks unless the task clearly does not need some of them.

### Base checks

- `uv run pytest -q`
- `./start.sh doctor` or the relevant CLI entrypoint
- manual inspection of logs if logging changed
- manual inspection of rendered HTML if UI changed

### Web-related checks

If the change affects web behavior, also run the affected route or app entrypoint, for example:

- `./start.sh web --host 127.0.0.1 --port 8780`
- `uv run python config/start.py web --host 127.0.0.1 --port 8780`

Verify:

- `GET /`
- `GET /health`
- relevant new route
- relevant new API endpoint
- malformed input behavior

### Adapter-related checks

If the change affects product adapters, verify:

- adapter handles normal payload;
- adapter handles missing payload;
- adapter handles malformed payload;
- adapter does not leak product secrets;
- adapter does not mutate source artifacts unless explicitly designed to do so;
- adapter errors render as explicit degraded/error states.

### Artifact/browser-related checks

If artifact browsing or parsing changes, verify:

- file exists where expected;
- only allowlisted files are accessible;
- path traversal is rejected;
- JSON/JSONL parsing is tolerant where intended;
- corrupted input produces explicit partial/error state;
- raw secrets are not rendered.

### Config-related checks

If config/schema behavior changes, verify:

- valid config loads;
- invalid config fails fast;
- unknown or unsupported values are rejected;
- no hidden defaults are introduced for required fields;
- docs are updated.

## Change levels

To avoid bureaucracy, use only three change levels.

### Low-risk

Use this when the change is mostly local and does not affect sensitive behavior.

Examples:

- docs;
- comments;
- non-security styling;
- local template cleanup;
- small test-only additions;
- small non-runtime refactor.

Usually required:

- automated tests if applicable;
- targeted smoke check if applicable;
- visual/manual check if templates changed.

### Runtime-risk

Use this when the change affects normal BeeUI behavior or product integration.

Examples:

- app factory;
- route behavior;
- schema validation;
- page/block renderer;
- adapter contract;
- artifact parsing;
- API response envelope;
- config read-model;
- dashboard behavior.

Usually required:

- `uv run pytest -q`;
- relevant CLI/web smoke;
- route/API checks;
- fixture checks;
- docs update if contract changed.

### Security-sensitive

Use this when the change affects trust boundaries or sensitive paths.

Examples:

- auth/session/cookies;
- CSRF;
- file/path handling;
- artifact browser;
- config apply/write path;
- bounded operator actions;
- product action callbacks;
- secret redaction;
- dependency changes;
- network-facing behavior;
- serialization/deserialization of untrusted input.

Usually required:

- all runtime-risk checks;
- targeted security checks from `docs/SECURITY.md`;
- malformed input checks;
- path traversal checks;
- secret leakage review;
- dependency review if dependencies changed.

## Security-aware development rule

Not every task needs every security practice.

Use only what matches the change:

- SAST mindset for code changes;
- SCA for dependency changes;
- DAST-style route checks for exposed HTTP behavior;
- fuzzing or malformed-input tests for parsers, serializers and fragile input handling;
- explicit secret leakage review for HTML/API/log/artifact surfaces.

The goal is not to “tick every box”.
The goal is to apply the right check for the right type of change.

See `docs/SECURITY.md`.

## Product adapter rules

Product adapters are the boundary between BeeUI and product-specific semantics.

Rules:

- generic BeeUI core must not know MRKT/Binance/ROP-specific business rules;
- BeeCap-specific logic belongs in BeeCap adapter/read-model code;
- BeeAgent-specific logic belongs in BeeAgent adapter/read-model code;
- adapter responses should be normalized into stable BeeUI envelopes;
- adapter errors should be explicit;
- adapter must not expose secrets;
- adapter must reject unsafe identifiers;
- adapter must avoid arbitrary filesystem access.

Good adapter responsibility:

- summarize product state;
- list safe artifacts;
- provide source links;
- expose bounded action definitions;
- call product validation callbacks.

Bad adapter responsibility:

- execute broker actions directly from BeeUI core;
- infer hidden domain state from arbitrary files;
- bypass product validation;
- mutate product config without product-owned validation.

## Route and API rules

All web/API routes should have clear behavior.

Read-only routes:

- must use safe identifiers;
- must not mutate source files;
- must not trigger product runtime execution;
- must not call broker/provider APIs directly unless explicitly part of a product-owned read adapter contract;
- must return explicit missing/partial/error states.

Write/control routes:

- must be explicit;
- must require validation;
- must use product-owned callbacks/API;
- must produce audit artifacts where applicable;
- must reject unsupported payloads;
- must not silently fallback to unsafe behavior.

API responses should use stable envelopes where practical:

```json
{
  "status": "ok",
  "data": {},
  "warnings": [],
  "source": {}
}
```

Error responses should be explicit:

```json
{
  "status": "error",
  "error": {
    "code": "invalid_input",
    "message": "..."
  }
}
```

## Template and HTML rules

Templates must follow these rules:

- Jinja2 autoescape must stay enabled;
- do not mark untrusted content safe;
- do not render raw HTML from product artifacts unless sanitized and explicitly intended;
- do not include tracking scripts from Tabler demos;
- do not load external scripts by default;
- do not expose secrets in HTML;
- keep technical debug details out of primary operator UI unless explicitly in diagnostics/admin sections.

## Static asset rules

Static assets should be controlled.

Rules:

- prefer vendored Tabler assets for stable local development;
- do not depend on CDN for core UI behavior unless explicitly documented;
- do not ship demo-only tracking scripts;
- keep custom CSS in `src/beeui_module/static/css/beeui.css`;
- keep custom JS minimal;
- avoid frontend build chains until the separate frontend phase.

## Dependency rules

Dependencies should be minimal.

Allowed baseline:

- `fastapi`;
- `jinja2`;
- `uvicorn`;
- `pyyaml`;
- `pydantic` if schema validation needs it;
- `pytest`;
- `httpx` for tests.

Before adding a dependency, check:

- does it materially reduce code?
- is it maintained?
- does it expand attack surface?
- can this be done with existing stack?
- does it require frontend build complexity?

Dependency changes are at least `runtime-risk`; security-relevant dependencies are `security-sensitive`.

## Roadmap update rules

`docs/ROADMAP.md` should be updated when:

- iteration status changes;
- goal/scope/deliverable changes;
- DoD changes;
- route/API contract changes;
- adapter contract changes;
- artifact/browser contract changes;
- checks change;
- stage wording becomes outdated.

Do not update ROADMAP for tiny internal implementation details that do not affect iteration contract.

## Docs update rules

Update docs when the contract changes.

Usually check whether these files need updates:

- `docs/ROADMAP.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/INTEGRATION.md`
- `docs/COMPONENTS.md`
- `docs/API_CONTRACT.md`
- `docs/WEB_UI.md`
- `docs/THEME.md`
- `README.ru.md`

Update them if one of the following changed:

- CLI usage;
- route behavior;
- API response shape;
- page/block schema;
- adapter contract;
- artifact browser behavior;
- config schema;
- auth/security behavior;
- verification flow.

## PR rules

Each PR should include:

- summary;
- related issue;
- iteration reference;
- change level;
- scope;
- changes;
- tests;
- UI/API checks;
- security notes;
- screenshots or route examples when useful;
- notes for reviewer.

Good rule:

- **Issue** explains the task.
- **PR** explains the delivery.
- **ROADMAP** explains the iteration-level target.

## Issue rules

Each issue should stay lightweight but useful.

It should answer:

- what needs to be done;
- why it matters;
- what is in scope;
- what result is expected;
- how it should be verified;
- what should not be included.

Do not turn the issue into a full implementation diary.

## Comments and evidence

Issue comments are allowed and useful for:

- intermediate findings;
- links to test runs;
- route output examples;
- screenshots;
- quick verification notes;
- clarifications.

But comments do not replace the PR.

Main evidence for closing work should stay in the PR.

## KISS rule for process

To keep the process simple:

- one task = one issue when practical;
- one iteration item = one focused PR when practical;
- do not mix several roadmap iterations in one PR;
- do not require documents that nobody will read;
- do not add process steps unless they help quality or safety;
- do not build no-code/dashboard-builder features before schema, adapters and blocks are stable.

## Typical developer flow

A normal development cycle in `beeui` looks like this:

1. open `docs/ROADMAP.md`;
2. select the current iteration;
3. create or refine the issue;
4. create a branch;
5. implement the change;
6. run required tests/checks;
7. inspect routes/UI/API output if applicable;
8. inspect logs if applicable;
9. update docs if needed;
10. open PR;
11. merge after review and DoD satisfaction.

## Review checklist mindset

A reviewer should be able to answer:

- does this stay inside the iteration scope?
- is BeeUI still generic?
- did product-specific logic stay behind adapters?
- are routes/API responses predictable?
- are read-only routes actually read-only?
- are file/path inputs safe?
- are secrets safe?
- are templates safe?
- are tests/checks appropriate for the risk?
- is the solution simple enough?
- is the PR enough to prove readiness?

## Summary

`beeui` uses a lightweight but real SDLC.

The key discipline is:

- small scoped iterations;
- generic BeeUI core;
- product logic behind adapters;
- declarative schema before visual builder;
- fail-fast validation;
- safe HTML/API behavior;
- reproducible UI/read-model outputs;
- evidence in PR;
- security checks only where they actually matter.
