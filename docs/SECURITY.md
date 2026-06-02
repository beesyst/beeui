# SECURITY — BeeUI

## Purpose

This document defines the practical security rules for `beeui`.

The goal is to improve UI/backend safety without creating unnecessary bureaucracy.

This is **not** a formal enterprise security program.

It is a lightweight engineering guide for deciding:

- what needs security attention;
- which checks are worth running;
- how to keep secrets, config, artifacts and UI/API responses safe;
- how to align security checks with the SDLC-light workflow.

Use this document together with:

- `docs/SDLC.md`
- `docs/ROADMAP.md`
- `docs/INTEGRATION.md`
- `docs/API_CONTRACT.md`
- `docs/WEB_UI.md`

## Security principles

Security in `beeui` should follow these principles:

- read-only by default;
- protect secrets first;
- never expose product secrets through HTML/API/logs/artifacts;
- validate configuration explicitly;
- fail fast on invalid required inputs;
- treat product artifacts and adapter responses as untrusted input;
- keep UI useful but not overexposed;
- avoid hidden defaults for sensitive behavior;
- minimize attack surface;
- prefer simple designs over complex, fragile abstractions;
- keep product authority outside `beeui`;
- apply security checks proportionally to the change.

## What we protect

At minimum, `beeui` should protect:

- product secrets and environment references;
- session cookies and auth state;
- config values and config-change audit trails;
- artifact integrity and predictable artifact access;
- product runtime/source artifacts from unintended mutation;
- product adapter boundaries;
- HTML rendering safety;
- API response safety;
- dependency hygiene;
- file/path handling;
- parsing of external, product-provided or user-controlled input.

## What beeui must not own

`beeui` must not become the authority source for product runtime behavior.

`beeui` must not own:

- trading decisions;
- broker calls;
- live execution;
- BeeAgent capability execution;
- product policy decisions;
- runtime guardrails;
- product config validation source of truth;
- product artifact semantics beyond display/read-model mapping.

Those responsibilities remain inside the product:

- `beecap`;
- `beeagent`;
- future Bee products.

Main rule:

```text
BeeUI renders.
Product decides.
```

## Security-sensitive areas in beeui

Changes in these areas should be treated more carefully:

- `config/start.py`
- `config/*.yml`
- `src/beeui_module/app.py`
- `src/beeui_module/server.py`
- `src/beeui_module/settings.py`
- `src/beeui_module/config.py`
- `src/beeui_module/api/*`
- `src/beeui_module/adapters/*`
- `src/beeui_module/artifacts/*`
- `src/beeui_module/auth/*`
- `src/beeui_module/config_ui/*`
- `src/beeui_module/actions/*`
- `src/beeui_module/core/security.py`
- `src/beeui_module/templates/*`
- `src/beeui_module/static/*`
- dependency files:
  - `pyproject.toml`
  - `uv.lock`

## Core rules

### 1. Product source of truth stays in the product

`beeui` must not invent product state.

If data is unavailable, partial or corrupted, `beeui` should show:

- `empty`;
- `partial`;
- `degraded`;
- `unavailable`;
- explicit warning or reason.

It must not silently fabricate:

- profit;
- execution status;
- account state;
- approval status;
- runtime state;
- artifact content.

### 2. Read-only is the default

All routes and adapters are read-only by default.

Write/control behavior is allowed only when all are true:

- the route is explicitly designed as a bounded action;
- the product adapter exposes an explicit callback/API for it;
- validation is performed before execution;
- the action is audited;
- the user/session has the required role if auth is enabled;
- no broker/live/runtime authority is introduced implicitly.

Not allowed:

- hidden runtime mutation from dashboard routes;
- implicit config writes from preview routes;
- direct broker/order calls from `beeui`;
- arbitrary filesystem writes;
- automatic runtime restart/reload after config apply unless explicitly implemented, validated and documented.

### 3. Config is explicit and validated

Required `beeui` behavior must be controlled by config, not hidden code defaults.

If a new required key is introduced:

- it must be explicitly present in the relevant config example;
- it must be validated by `beeui` config loading;
- the app must fail fast with a clear error if it is missing or invalid;
- docs must be updated if the contract changed.

Product-specific config validation remains the product's responsibility.

`beeui` may call product validation callbacks, but must not replace them.

### 4. Secrets must not leak

Secrets must never appear in:

- HTML responses;
- JSON API responses;
- logs;
- storage artifacts;
- audit artifacts;
- test snapshots;
- PR screenshots;
- example payloads committed to repo.

Safe practice:

- never dump full config blindly;
- never dump full env;
- redact keys containing:
  - `secret`
  - `token`
  - `password`
  - `api_key`
  - `api_secret`
  - `authorization`
  - `cookie`
  - `session`
  - `credential`

- never serialize raw secrets into JSON/JSONL;
- never expose sensitive request headers.

### 5. Logs must be useful but safe

Logs should be:

- understandable;
- in English;
- sufficient for debugging;
- free from secret values.

Allowed:

- high-level runtime events;
- route startup events;
- adapter names;
- reason codes;
- safe artifact identifiers;
- non-sensitive config choices;
- state transitions.

Not allowed:

- raw secret values;
- full environment dumps;
- full request/response dumps with credentials;
- full cookies;
- session signing secrets;
- sensitive headers;
- unredacted product config.

### 6. Artifacts must be reproducible and safe

`beeui` should avoid creating artifacts unless they are needed for:

- config change audit;
- operator action audit;
- support diagnostics;
- reproducible UI/backend behavior.

Artifacts should be:

- predictable;
- useful for debugging;
- consistent with logs;
- free from secrets.

If a new artifact is introduced, ask:

- does it help reproduce UI/admin/action behavior?
- does it expose anything sensitive?
- does it duplicate product source of truth?
- does it need redaction or omission?
- is it clearly marked as UI/support/audit artifact, not runtime truth?

### 7. External/product input is untrusted by default

Treat as untrusted:

- CLI args;
- config values;
- product adapter responses;
- HTTP responses from product APIs;
- file contents loaded from disk;
- restored JSON artifacts;
- JSONL rows;
- query parameters;
- form payloads;
- uploaded/static files if such support is added later.

Validate before use where reasonable.

Do not trust product artifacts just because they were created locally. Local artifacts can be corrupted, stale or user-modified.

### 8. HTML rendering must be safe

Jinja autoescape must remain enabled for HTML templates.

Do not render raw HTML from:

- product artifacts;
- adapter responses;
- config values;
- user input;
- markdown converted from untrusted sources;

unless it passes a deliberate sanitization path.

Avoid:

- `|safe` on untrusted values;
- inline scripts with user-controlled data;
- raw JSON insertion into HTML without safe serialization;
- dynamic template path selection from user input.

### 9. File and path access must be bounded

Any file/artifact access must be bounded by explicit roots and allowlists.

Required practices:

- use project/product root paths explicitly;
- validate `run_id`, `artifact_id`, `config_id`, `action_id`;
- normalize and resolve paths before reading;
- verify resolved paths stay under allowed root;
- reject `..`, absolute paths and traversal attempts;
- avoid arbitrary filesystem browsing.

`beeui` artifact browser must never become a general file explorer.

### 10. Keep the trusted surface small

Do not add complexity unless needed.

Good security in `beeui` usually means:

- fewer moving parts;
- explicit behavior;
- narrow adapter interfaces;
- simple validation;
- bounded serialization;
- stable response envelopes;
- clear refusal states;
- no hidden fallback paths.

## Product adapter security rules

Product adapters are a primary trust boundary.

Adapters must:

- expose only product-approved read-models;
- validate input identifiers;
- redact secrets;
- avoid returning full raw config unless sanitized;
- avoid exposing arbitrary file paths;
- return explicit partial/error states;
- keep optional write/action methods unavailable by default unless explicitly implemented by product-owned bounded callbacks/API;
- never execute product runtime logic unless called through a bounded action path.

Adapters must not:

- call broker/live APIs directly from UI routes;
- bypass product guardrails;
- mutate product runtime artifacts from read-only routes;
- invent product state;
- silently repair corrupted product artifacts.

## Artifact browser rules

Artifact browser must be safe by design.

Allowed:

- listing allowlisted artifacts;
- showing metadata;
- rendering JSON safely;
- rendering JSONL with parse warnings;
- rendering text artifacts as escaped text;
- linking to known source artifacts.

Not allowed:

- arbitrary path browsing;
- editing artifacts;
- deleting artifacts;
- uploading artifacts;
- showing raw secrets;
- following symlinks outside allowed roots;
- rendering untrusted HTML as HTML.

Malformed JSON/JSONL must produce explicit warnings and partial state, not server crashes.

## API security rules

JSON APIs must use stable envelopes.

Recommended envelope:

```json
{
  "status": "ok",
  "data": {},
  "warnings": [],
  "errors": [],
  "meta": {}
}
```

Error responses should be explicit and safe:

- no stack traces in production responses;
- no secrets;
- no full config dumps;
- no raw sensitive payloads;
- clear reason codes where useful.

API routes must validate:

- path params;
- query params;
- JSON body shape;
- artifact identifiers;
- mode/page/block identifiers.

## Config UI security rules

Config UI must be bounded.

Allowed:

- read-only config read-model;
- redacted config display;
- allowlisted key preview;
- validation preview;
- bounded apply flow with backup and audit.

Not allowed:

- arbitrary YAML editor;
- secrets editing;
- editing broker/live credentials;
- editing product execution internals unless explicitly allowed by product;
- hidden runtime restart/reload;
- writing config without validation;
- writing config without audit.

For config apply:

- require allowlisted keys;
- require stale hash / optimistic guard if implemented;
- validate candidate before write;
- write backup before successful write;
- audit accepted and rejected attempts;
- never serialize full secret-bearing config into audit artifacts.

## Bounded action security rules

Bounded actions must be explicit.

Each action should define:

- action id;
- title;
- description;
- required role;
- payload schema;
- validation callback;
- product execution callback;
- allowed/disabled/denied state;
- audit behavior.

Actions must not:

- be generated from arbitrary user-provided code;
- call product internals without adapter boundary;
- bypass product validation;
- introduce live/broker authority unless product explicitly implements and gates it;
- execute in background without visible result/audit.

Every action attempt should produce an audit artifact when action auditing is enabled.

## Auth/session security rules

When auth is enabled:

- all non-public routes require authentication;
- write/control routes require proper role;
- POST routes require CSRF protection or an equivalent anti-forgery mechanism;
- session cookies must be signed;
- password hashes must be stored safely;
- no default admin password must be committed;
- auth disabled mode must be explicit and intended for local/dev only.

Roles:

- `viewer` — read-only;
- `operator` — bounded operator actions;
- `admin` — admin/config/support functions.

Auth is not required in the first MVP, but when added, it must not be partial or decorative.

## Static asset security rules

Static assets should be controlled.

Allowed:

- vendored Tabler CSS/JS;
- local `beeui.css`;
- local `beeui.js`;
- product logo if safely configured.

Avoid:

- loading production assets from uncontrolled CDNs by default;
- copying demo tracking scripts;
- inline scripts with untrusted values;
- user-controlled static asset paths.

If external CDN support is added, it must be explicit and documented.

## Dependency rules

When dependencies change:

- keep changes intentional and minimal;
- commit both `pyproject.toml` and `uv.lock`;
- review why the package is needed;
- review whether it affects runtime or attack surface;
- avoid dependencies that are unnecessary for KISS MVP.

Do not add dependencies “just in case”.

High-sensitivity dependency areas:

- auth/session packages;
- template/rendering packages;
- markdown/HTML sanitization packages;
- file upload or parsing packages;
- HTTP client/server packages;
- admin framework packages.

## Security checks in this project

To keep the process simple, use only the checks that fit the change.

## SAST

### What it means here

Static review of source code for risky patterns.

### Use SAST when

Run or consider SAST when a PR changes:

- config parsing;
- auth/session handling;
- adapter boundaries;
- artifact browser;
- file/path handling;
- API request/response handling;
- serialization/deserialization;
- template rendering;
- bounded actions;
- config apply;
- dependency surface.

### Typical things to look for

- secret leakage to logs or responses;
- unsafe file/path usage;
- missing validation;
- unsafe `|safe` usage in templates;
- dynamic template selection;
- overly broad exception swallowing;
- insecure debug code;
- dangerous dynamic execution;
- fragile parsing of untrusted data;
- write action without audit.

### Lightweight rule

For most code PRs, a simple static safety pass is enough:

- manual review with security mindset;
- plus automated static scan if available.

## SCA

### What it means here

Software Composition Analysis: dependency review.

### Use SCA when

Run or consider SCA when:

- `pyproject.toml` changes;
- `uv.lock` changes;
- a dependency is added, removed or upgraded.

### Typical things to look for

- known vulnerable packages;
- unnecessary packages;
- overly broad dependency additions;
- packages with risky maintenance history;
- packages that increase server/browser attack surface.

### Lightweight rule

If dependencies changed, SCA is required.
If dependencies did not change, SCA is usually not needed.

## DAST

### What it means here

Dynamic testing of exposed web/API behavior.

### Use DAST when

Run or consider DAST when a change affects:

- HTTP routes;
- request/response handling;
- API endpoints;
- config apply endpoints;
- artifact browser endpoints;
- auth/session routes;
- bounded action routes.

### Typical things to look for

- malformed path params;
- malformed query values;
- malformed JSON bodies;
- path traversal attempts;
- method misuse;
- unsafe redirects;
- unsafe error paths;
- crashes under bad inputs.

### Lightweight rule

For `beeui`, lightweight DAST-style route checks are useful for web/API changes.

Minimum examples:

- bad `run_id`;
- bad `artifact_id`;
- unknown page/block;
- invalid mode;
- invalid config key;
- invalid action payload;
- non-GET request to read-only route.

## IAST

### What it means here

Interactive testing with runtime instrumentation or deeper runtime observation.

### Use IAST when

Consider IAST only for higher-risk changes such as:

- auth/session implementation;
- config apply;
- bounded action execution;
- artifact parsing from untrusted/corrupted files;
- standalone service mode with HTTP product adapters.

### Lightweight rule

IAST is **not default** for everyday work.
Use it only when a change is clearly security-sensitive and runtime-observable.

## Fuzzing

### What it means here

Feeding unexpected or malformed input to fragile code paths.

### Use fuzzing when

Consider fuzzing for code that parses or restores:

- JSON;
- JSONL;
- config-like data;
- CLI input;
- HTTP payloads;
- artifact IDs;
- route params;
- custom selector paths;
- adapter responses.

### Good candidates in beeui

- settings/config validation helpers;
- artifact readers;
- JSONL preview parser;
- selector resolver;
- route param validators;
- config apply payload validator;
- action payload validator.

### Lightweight rule

Do not fuzz everything.
Use fuzzing only for code that can realistically break on malformed input.

## Security levels for PRs

Use these three practical levels.

### Low-risk

Examples:

- docs only;
- comments only;
- test-only changes;
- visual styling without data/API changes;
- non-sensitive template adjustments;
- formatting.

Usually enough:

- normal review;
- targeted tests if needed.

### Runtime-risk

Examples:

- app factory changes;
- config loading;
- page/block schema;
- adapter contract;
- artifact parsing;
- API contract;
- dashboard read-model;
- product integration;
- config preview.

Usually needed:

- `pytest -q`;
- web/CLI smoke;
- route checks if web/API changed;
- HTML/API response inspection;
- SAST mindset review.

### Security-sensitive

Examples:

- auth/session logic;
- password/session storage;
- config apply;
- bounded operator actions;
- artifact browser path handling;
- file/path access;
- dependency updates;
- standalone HTTP product adapters;
- user-controlled HTML/markdown rendering;
- secrets redaction logic.

Usually needed:

- all runtime-risk checks;
- SAST;
- SCA if dependencies changed;
- DAST-style route tests if HTTP routes changed;
- targeted fuzzing if parsing/restoring untrusted input;
- deeper runtime review if auth/action/config mutation path changed.

## Minimal security checklist for developers

Before opening PR, check:

- are secrets kept out of HTML/API/logs/artifacts?
- are required config keys validated fail-fast?
- did I avoid hidden defaults for sensitive behavior?
- did I keep the change inside the intended scope?
- did I avoid unnecessary abstraction?
- if dependencies changed, were they reviewed?
- if external/product input is parsed, is handling robust enough?
- are artifacts safe to store and inspect?
- are read-only routes actually read-only?
- are write/control routes validated and audited?
- is path traversal blocked where file access exists?
- is HTML autoescape preserved?

## Minimal security checklist for reviewers

During review, ask:

- does this change touch auth, sessions, dependencies, parsing, file paths, config apply or actions?
- does it introduce a new trust boundary?
- are logs still safe?
- are HTML/API responses still safe?
- are artifacts still safe?
- are required validations explicit?
- are product authority boundaries preserved?
- is any check from this document missing?
- is the solution simple enough?

## Secure logging rules

Allowed:

- startup events;
- route registration events;
- high-level adapter events;
- reason codes;
- artifact identifiers;
- sanitized config choices;
- state transitions.

Not allowed:

- raw secret values;
- full env dumps;
- session cookies;
- password hashes;
- bearer tokens;
- API keys;
- full request headers;
- unredacted product configs;
- stack traces in user-facing responses.

## Secure artifact rules

Allowed when useful:

- config change audit summary;
- config backup without additional secret exposure beyond existing local file;
- operator action audit summary;
- support diagnostics;
- UI read-model snapshots if intentionally added;
- safe artifact metadata.

Not allowed:

- raw API secrets;
- full sensitive headers;
- env dumps;
- unsafe snapshots that expose credentials;
- arbitrary full product config inside audit artifact;
- hidden runtime state that becomes a second source of truth.

## Secure API response rules

Allowed:

- status;
- reason codes;
- sanitized read-model data;
- safe artifact metadata;
- redacted config values;
- product-provided non-sensitive summaries.

Not allowed:

- secrets;
- raw env;
- raw cookies;
- unredacted config;
- server filesystem absolute paths unless explicitly safe and needed;
- Python tracebacks in normal API responses.

## Path / file safety rules

When working with files:

- prefer explicit project/product paths;
- avoid uncontrolled path building from untrusted input;
- validate assumptions before reading stored artifacts;
- do not trust restored JSON blindly;
- reject traversal;
- reject absolute paths from route params;
- keep artifact access allowlisted;
- avoid following symlinks outside allowed roots.

## HTML/template safety rules

When working with templates:

- keep Jinja autoescape enabled;
- do not use `|safe` on untrusted input;
- escape artifact text;
- escape JSONL preview text;
- safely serialize JSON for script contexts;
- avoid inline scripts using raw user/product data;
- do not load templates based on user-controlled paths.

## Config / validation safety rules

When a new config key affects UI/backend behavior:

- define it explicitly in config examples;
- validate it in `beeui` config loader;
- fail fast if missing or invalid;
- update docs if the contract changed.

When config preview/apply delegates to product validation:

- product validation result must be explicit;
- invalid product config must be rejected;
- BeeUI must not silently repair product config;
- BeeUI must not invent product defaults.

## Product integration safety rules

When adding a product integration:

- create a product adapter;
- keep product semantics inside product adapter/read-model;
- keep product runtime behavior inside product;
- define artifact allowlist;
- define config allowlist if config UI is used;
- define action allowlist if bounded actions are used;
- add tests for partial/missing/corrupted product artifacts;
- document integration boundaries in `docs/INTEGRATION.md`.

Do not import deep product internals randomly throughout `beeui`.
Product knowledge must be concentrated in the adapter/integration layer.

## Standalone mode safety rules

Standalone mode is future scope and must be treated carefully.

If added:

- HTTP product adapters must have timeouts;
- backend unavailable state must be explicit;
- CORS must be disabled or narrow by default;
- auth boundary must be explicit;
- product API credentials must not be logged;
- degraded backend must not crash entire UI;
- standalone mode must not bypass product validation/action boundaries.

Embedded mode remains preferred for MVP.

## Security and SDLC integration

Use security as part of the normal workflow:

1. identify change level;
2. implement minimally;
3. run required checks;
4. inspect logs/HTML/API/artifacts;
5. document verification in PR.

Do not create separate bureaucracy unless the project actually needs it.

## What not to do

Avoid these patterns:

- hidden required defaults in code;
- logging sensitive runtime state;
- dependency additions without review;
- broad refactors mixed with security-sensitive changes;
- arbitrary YAML editor;
- arbitrary artifact filesystem browser;
- direct broker/runtime execution from UI;
- rendering untrusted artifact HTML as HTML;
- using `|safe` to “fix” display issues;
- turning `beeui` into a second product runtime;
- “future-proof” abstractions that increase risk and complexity;
- marking every PR as requiring every type of security testing.

## Practical defaults

To keep this lightweight:

- most PRs need normal review + tests;
- web/API PRs need route checks;
- artifact/file PRs need path traversal and malformed file checks;
- code-heavy adapter/API PRs need SAST mindset review;
- dependency PRs need SCA;
- auth/config-apply/action PRs are security-sensitive;
- fuzzing is targeted, not mandatory everywhere.

## Summary

Security in `beeui` should stay practical.

The main rules are:

- keep product source of truth in the product;
- read-only by default;
- protect secrets;
- validate config explicitly;
- keep logs safe;
- keep HTML/API responses safe;
- keep artifacts safe;
- review dependencies;
- block path traversal;
- preserve product authority boundaries;
- use only the security checks that match the real risk;
- keep everything simple enough to maintain.
