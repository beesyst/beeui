# AGENTS.md — BeeUI repository guidance

## Purpose

This file contains stable repository-wide rules for AI agents working with `beeui`.

Task-specific requirements belong in the approved Issue.

Detailed workflows belong in `.agents/skills/`.

Prompts should normally contain only:

- selected workflow;
- exact target information;
- approved Issue;
- implementation or verification evidence;
- task-specific constraints.

Do not duplicate stable repository rules inside every executor prompt.

## Instruction precedence

Use this order:

1. Current explicit task instructions and approved Issue.
2. This `AGENTS.md`.
3. Selected repository skill.
4. Current repository contracts and documentation.
5. Implementation reports and previous comments as supporting evidence only.

The actual target worktree, current files, diff, tests, rendered behavior and package contents take precedence over stale reports.

When instructions materially conflict, stop and report the conflict.

## Agent role separation

Tool, authority and read-only restrictions apply only to the current task and agent.

When producing a prompt for another agent, do not copy the current agent's tool restrictions unless they are explicitly required for that executor.

Planning and final-review tasks may use Bee Dev MCP in read-only mode.

Implementation and correction prompts are executed by DeepSeek through Copilot or by Codex. They must instruct the executor to work in the exact target worktree using its available local repository tools.

Implementation prompts must not require:

- Bee Dev MCP;
- an MCP target;
- MCP Mode;
- read-only behavior.

Implementation executors may inspect files, modify the exact target worktree and run local checks within the approved Issue.

They must not commit, push, create or update a PR, or merge unless the current task explicitly authorizes that operation.

## Bee Dev MCP rules

These rules apply only when the current task explicitly selects Bee Dev MCP for read-only planning or review.

Bee Dev MCP is read-only.

Available repository tools include:

- `list_projects`;
- `list_worktrees`;
- `get_project_context`;
- `get_review_manifest`;
- `get_review_bundle_page`;
- `get_review_bundle` — compatibility only;
- `read_project_file`;
- `search_project`.

Do not refer to nonexistent tools such as `get_file`.

Use `get_review_manifest` and `get_review_bundle_page` for complete final reviews.

Do not repeatedly call `get_review_bundle` expecting pagination.

### Exact target resolution

Before planning or review:

1. Call `list_worktrees`.
2. Match the requested worktree by exact absolute `path`.
3. Use the returned MCP `target`.
4. Call `get_project_context`.
5. Verify:
   - project;
   - path;
   - branch;
   - HEAD;
   - dirty state.

For final review, verify the expected base branch from the complete manifest.

Do not infer a target from a branch name.

Do not substitute the main worktree for a requested feature worktree.

Do not inspect or review another worktree merely because it has a similar branch name.

### Complete reading

Repository inspection is incomplete while required data is paginated, truncated or has continuation metadata.

For manifests and diffs:

- continue with the exact `next_cursor` while `has_more=true`;
- require one consistent `snapshot_id`;
- finish only when `has_more=false`;
- require `truncated=false`.

For files:

- continue with the exact `next_line` and `next_column`;
- finish only when both are null.

Read required files listed under `omitted_files` or `related_omitted_files` directly with `read_project_file`.

Treat `truncated=true` as incomplete inspection.

Failure to retrieve mandatory MCP data is not a code defect.

When mandatory planning inspection cannot be completed, return:

```text
PLANNING INCOMPLETE
```

When mandatory review inspection cannot be completed, return:

```text
REVIEW INCOMPLETE
```

Do not return `CHANGES REQUIRED` solely because MCP data is incomplete.

## Mandatory reading

Read documents required by the selected skill.

Common documents include:

* `AGENTS.md`;
* approved Issue;
* relevant section of `docs/ROADMAP.md`;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `README.ru.md`.

When relevant, also read:

* `docs/DEV_GUIDE.md`;
* `docs/SPEC.md`;
* `docs/ARCHITECTURE.md`;
* `docs/WEB_UI.md`;
* `docs/INTEGRATION.md`;
* `docs/API_CONTRACT.md`;
* `docs/COMPONENTS.md`;
* `docs/THEME.md`;
* `config/settings.yml`;
* `config/schema.yml`;
* example product-side `beeui.yml`;
* `pyproject.toml`;
* package-data configuration;
* public product-adapter contracts;
* related product ROADMAPs and public integration contracts.

ROADMAP status does not prove implementation.

Compare ROADMAP wording with current:

* code;
* templates;
* static assets;
* configuration;
* public contracts;
* tests;
* package contents;
* rendered behavior.

## Architecture boundary

Canonical embedded flow:

```text
Browser request
→ BeeUI route, shell and transport boundary
→ generic BeeUI renderer or ProductUiAdapter
→ product-owned read-model or bounded callback
→ product runtime, artifacts or external systems
```

Canonical read-only flow:

```text
Product config / artifacts / API
→ product adapter and read-model
→ BeeUI generic layout and templates
→ operator-facing HTML or JSON
```

Canonical bounded write flow:

```text
Authenticated browser request
→ BeeUI auth, role and CSRF checks
→ product-owned bounded callback
→ product validation, authority and audit
→ product-owned mutation
```

Main rule:

```text
BeeUI renders.
Product decides.
```

### BeeUI owns

BeeUI owns generic framework behavior:

* FastAPI app factory and embedded mount helpers;
* route-prefix support;
* generic HTML and JSON route surfaces;
* Jinja2 templates and shell;
* local Tabler-compatible static assets;
* reusable layout blocks and template primitives;
* generic page, navigation and component schemas;
* controlled locale and theme presentation mechanisms;
* generic API envelopes;
* generic adapter protocol and normalized adapter errors;
* safe ID, path and internal-link validation;
* bounded artifact presentation;
* generic auth, session, role and CSRF transport boundaries;
* controlled config/action transport shells;
* package-local templates and static package data;
* generic degraded, empty and error presentation;
* component catalog and demo/reference fixtures;
* HTML escaping and browser-facing security controls.

### Product repositories own

Bee products such as BeeAgent and BeeCap own:

* product and domain semantics;
* product read-model construction;
* production implementations of `ProductUiAdapter`;
* product configuration and validation;
* product artifacts and artifact allowlists;
* product-specific metrics, labels and calculations;
* product action availability and authority;
* product callbacks for config and actions;
* product audit and mutation behavior;
* runtime, provider, broker, MCP, LLM and external-system calls;
* product security policies beyond the generic BeeUI transport boundary.

### Domain modules own

Domain modules own:

* domain models and taxonomy;
* classification and business rules;
* domain fixtures;
* domain validation;
* domain summaries and recommendations;
* bounded domain AI contracts.

### Do not

Do not:

* add product-specific domain logic to generic BeeUI renderers;
* add production BeeAgent or BeeCap adapters inside BeeUI;
* import `beeagent_module`, `beecap_module` or private product internals into generic BeeUI code;
* infer business semantics from route namespaces such as `/rop`, `/venues`, `/modes` or `/runs`;
* read arbitrary product storage or configuration directly;
* duplicate product metrics or calculations;
* call MCP, LLM, provider, broker or product runtime paths directly from BeeUI;
* create a second source of truth;
* put business decisions in templates or JavaScript;
* allow GET routes to mutate product or BeeUI state;
* bypass product validation, authority or audit;
* add arbitrary HTML, JavaScript, CSS or Jinja expressions from config or adapter payloads;
* add product-specific fallback behavior to generic components;
* introduce standalone deployment, no-code builder or separate frontend before an approved iteration.

Reference/demo fixtures may contain realistic product-shaped payloads only when clearly isolated as non-production examples.

## Sources of truth

Use:

* BeeUI runtime/system configuration: `config/settings.yml`;
* BeeUI demo/declarative schema: `config/schema.yml`;
* embedded product UI configuration: product-owned `config/beeui.yml`;
* product semantics: product adapter and product read-model;
* product state: product configuration, artifacts and APIs;
* BeeUI public contracts:

  * `docs/API_CONTRACT.md`;
  * `docs/COMPONENTS.md`;
  * `docs/INTEGRATION.md`;
  * `docs/WEB_UI.md`;
* iteration scope: approved Issue aligned with `docs/ROADMAP.md`;
* runtime evidence: rendered routes, logs and bounded artifacts;
* package evidence: installed package or wheel templates/static assets.

Rules:

* no hidden defaults for required behavior;
* no duplicate source of truth;
* required configuration must fail fast;
* optional defaults must be documented and safe;
* adapters and read-models provide data, not rendering authority;
* product artifacts are evidence, not BeeUI configuration;
* secrets belong only in environment variables or approved secret stores;
* cookies, query parameters and localStorage are user-preference or request inputs, not product configuration;
* preserve compatibility unless the Issue explicitly permits a breaking change.

## Configuration rules

### `config/settings.yml`

`config/settings.yml` contains BeeUI runtime and system settings.

A new required runtime setting must:

* have a single canonical location;
* be documented;
* be represented in examples when appropriate;
* be validated fail-fast;
* have missing and invalid tests;
* not contain committed secrets.

### `config/schema.yml`

`config/schema.yml` contains BeeUI demo/declarative UI schema.

It may define controlled:

* app metadata;
* theme;
* layout;
* locale;
* components;
* navigation;
* pages;
* demo/static data sources;
* generic blocks.

It must not accept:

* arbitrary HTML;
* arbitrary CSS;
* arbitrary JavaScript;
* Python or Jinja expressions;
* arbitrary filesystem paths;
* product execution instructions.

### Product-side `config/beeui.yml`

Product-side `beeui.yml` remains owned by the product repository.

BeeUI validates and renders its generic contract.

BeeUI must not:

* mutate product-side configuration through GET routes;
* silently sanitize invalid required structure;
* infer product domain semantics;
* introduce hidden fallback files;
* replace product validation.

## Implementation rules

* Stay inside the approved Issue.
* Prefer the smallest complete solution.
* Follow KISS.
* Do not perform unrelated refactoring.
* Do not add speculative architecture.
* Do not create abstractions without a concrete need.
* Do not duplicate existing logic.
* Reuse existing helpers, models, templates and tests.
* Do not weaken validation without a stated contract reason.
* Do not hardcode values that belong in configuration or a public contract.
* Follow PEP 8.
* Keep logs, runtime messages, API fields and internal identifiers in English.
* Keep user-facing built-in labels inside the controlled BeeUI locale mechanism when localization is required.
* Keep logs free of secrets and unnecessary product data.
* Treat config, query parameters, cookies, adapter payloads and artifact content as untrusted.
* Preserve read-only, preview-only and execution authority boundaries.
* Keep `pyproject.toml.version` unchanged for ordinary feature, fix, docs and chore work.
* Do not add comments unless the approved Issue explicitly requires documentation in code.
* Do not add a frontend build chain unless explicitly approved.
* Do not copy full upstream Tabler demo pages.

## Templates and rendering

* Keep Jinja autoescape enabled.
* Do not use unsafe `|safe` for config, adapter, artifact or user-provided values.
* Do not assemble product-facing HTML through Python string concatenation when a generic template contract exists.
* Keep templates product-neutral.
* Normalize malformed adapter payloads before rendering.
* Render unsupported or malformed optional payloads as explicit degraded or empty states when the public contract requires graceful degradation.
* Validate all active links through the shared safe internal-link contract.
* Preserve route-prefix and embedded-mount compatibility.
* Do not expose raw exceptions in HTML or JSON responses.
* Do not expose implicit raw fields merely because they exist in a payload.

## Static assets and dependencies

Static assets must be package-local unless an approved Issue explicitly defines another reviewed mode.

Do not add:

* external CDN references;
* Tabler preview/demo scripts;
* PostHog or other tracking;
* sponsor or marketing assets;
* remote font imports;
* arbitrary runtime-loaded scripts.

When adding or changing vendored assets:

* record source and upstream version;
* preserve the applicable license;
* include required files in package data;
* verify installed-package or wheel integrity;
* ensure production templates reference only local assets;
* verify no network calls are introduced;
* classify dependency or browser-executed asset changes according to `docs/SDLC.md` and `docs/SECURITY.md`.

Dependencies and `uv.lock` must not change unless required by the approved Issue.

When dependencies intentionally change:

* review the dependency surface;
* update `pyproject.toml`;
* update `uv.lock`;
* run applicable SCA;
* report exact dependency changes.

Do not run, request or require:

```text
uv lock --check
```

Do not modify `uv.lock` for unrelated cleanup.

## Documentation and contracts

Update relevant documentation when implementation changes:

* public runtime behavior;
* route surface;
* API envelope or schema;
* page, component or block contract;
* configuration;
* embedded integration contract;
* adapter protocol;
* artifact presentation;
* auth, session, CSRF or authority boundary;
* theme or locale behavior;
* static asset policy;
* packaging behavior.

Check, as applicable:

* `docs/ROADMAP.md`;
* `docs/DEV_GUIDE.md`;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `docs/WEB_UI.md`;
* `docs/INTEGRATION.md`;
* `docs/API_CONTRACT.md`;
* `docs/COMPONENTS.md`;
* `docs/THEME.md`;
* `README.ru.md`.

Do not update unrelated documentation.

When public data fields or contracts change:

* identify the source of truth;
* document compatibility impact;
* preserve existing fields when required;
* update contract tests;
* provide safe examples;
* distinguish schema/config validation from malformed adapter degradation.

## Verification

Determine the actual change level from `docs/SDLC.md` and `docs/SECURITY.md`:

* `low-risk`;
* `runtime-risk`;
* `security-sensitive`.

Run checks proportional to the actual change.

Common checks include:

* targeted tests;
* `uv run pytest -q`;
* `uv run pytest -q -W error::UserWarning` when relevant;
* `./start.sh doctor`;
* `./start.sh routes`;
* expected web entrypoint;
* affected HTML and JSON route smoke;
* route-prefix or embedded-mount smoke;
* logs inspection;
* artifact or package-data inspection;
* installed-package or wheel integrity;
* HTML escaping;
* malformed input behavior;
* safe-link validation;
* no-mutation checks;
* SAST;
* SCA;
* DAST;
* IAST;
* bounded fuzzing.

Use `uv run` for Python commands.

Use `./start.sh` for repository entrypoints where applicable.

Review agents using Bee Dev MCP cannot execute commands.

They may use supplied command output as evidence, but must:

* name the supplied command;
* distinguish reported evidence from inspected code;
* verify that required scenarios are covered;
* never claim MCP ran tests.

Missing verification is a blocker only when required by:

* the approved Issue;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* the actual changed boundary.

## Security

* Never expose secrets, tokens, passwords or complete environment dumps.
* Validate user-controlled identifiers, paths, links and query parameters.
* Keep artifact access allowlisted and bounded.
* Keep previews size-limited.
* Keep output escaping enabled.
* Treat cookies and localStorage values as untrusted presentation preferences.
* Do not let locale or theme preferences affect authorization or product behavior.
* Preserve server-side auth, role and CSRF enforcement.
* Do not introduce external mutation through read-only routes.
* Do not let adapter payloads create execution authority.
* Do not pass arbitrary JavaScript options from adapter/config to browser libraries.
* Do not log raw adapter payloads or secrets after browser-render failures.
* Do not expose raw product files through route parameters.
* Do not permit path traversal, protocol-relative links or external schemes where the contract is internal-only.
* Preserve explicit degraded and unavailable states.
* Preserve product-owned validation and authority for write callbacks.
* Keep package-local static assets free of tracking and external network references.

## Review rules

Review the exact requested target relative to the declared base branch.

Inspect:

* committed changes;
* staged changes;
* unstaged changes;
* untracked files;
* deleted files;
* renamed files;
* complete changed-file contents;
* relevant unchanged contracts and callers;
* templates and static assets;
* package-data configuration;
* supplied verification evidence.

Prioritize blockers affecting the current Issue:

* unmet Acceptance Criteria;
* incorrect or unsafe behavior;
* security or authority violations;
* BeeUI/product ownership violations;
* product-specific logic in generic BeeUI code;
* conflicting sources of truth;
* missing fail-fast validation;
* incompatible public contracts;
* broken route-prefix or embedded compatibility;
* unsafe HTML, links, paths or serialization;
* missing package templates or static assets;
* missing required verification;
* unrelated changes entering the PR;
* unintended dependency, lockfile or version changes;
* documentation contradicting public behavior.

Do not create blockers from:

* optional visual polish;
* personal naming preferences;
* speculative architecture;
* unrelated cleanup;
* requirements absent from the Issue;
* MCP limitations themselves.

Perform one complete review pass and consolidate all real blockers.

Use:

* `.agents/skills/beeui-plan-iteration/SKILL.md` for planning;
* `.agents/skills/beeui-review-and-close/SKILL.md` for final review and PR preparation.

## Required implementation evidence

The implementation report should contain:

1. target verification;
2. files read;
3. actual change level;
4. required checks;
5. source of truth;
6. BeeUI/product boundary assessment;
7. changed files;
8. Acceptance Criteria coverage;
9. exact test commands and results;
10. route, UI and runtime smoke;
11. logs inspected;
12. artifacts, static assets and package contents inspected;
13. security review;
14. dependency and lockfile status;
15. known limitations;
16. recommended Conventional Commit;
17. confirmation:

```text
version not changed
```