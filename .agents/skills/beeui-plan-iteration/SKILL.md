---
name: beeui-plan-iteration
description: Plan or refine a bounded BeeUI iteration, align generic UI contracts with related products, and prepare an Issue plus execution prompts without modifying the repository.
---

# BeeUI iteration planning workflow

## Purpose

Use this workflow when:

* the next BeeUI iteration is not yet approved;
* an existing ROADMAP item must be validated or refined;
* an Issue must be prepared from the current repository state;
* a generic page, block, adapter, API or integration contract requires alignment;
* related BeeAgent, BeeCap or other product UI requirements must be separated from generic BeeUI ownership.

Do not use this workflow when an approved Issue already exists.

This workflow is read-only.

Do not modify files, switch branches, run tests or execute repository commands.

## Required inputs

Obtain:

* project;
* expected worktree path;
* expected branch;
* expected base branch;
* mode;
* last known completed iteration when supplied;
* requested UI behavior;
* product and operator constraints;
* related repositories relevant to the proposed increment.

## Resolve the repository

1. Call `list_worktrees` for the project.
2. Find the entry whose `path` exactly matches the expected worktree path.
3. Use the returned MCP `target`.
4. Call `get_project_context` for that target and mode.
5. Verify:

   * project;
   * path;
   * branch;
   * HEAD;
   * dirty state.

If the exact path or required metadata is unavailable, stop with `PLANNING INCOMPLETE`.

If the branch differs from the expected branch, report expected and actual values and do not prepare an Issue.

Do not infer the MCP target from a branch name.

## Complete-reading rule

Use `read_project_file` for repository files.

When it returns `next_line` or `next_column`, continue with those exact values until both are null.

When reading `get_review_manifest` or `get_review_bundle_page`, continue with the exact `next_cursor` while `has_more=true`.

Do not use compatibility `get_review_bundle` for pagination.

When `get_project_context` lists a required file under `omitted_files` or `related_omitted_files`, read it directly with `read_project_file`.

Do not base a planning decision on partial files or truncated repository data.

## Dirty worktree handling

A dirty worktree is not automatically a blocker.

When dirty changes affect ROADMAP, architecture, configuration or public contracts:

1. read the complete review manifest;
2. read the complete paginated diff;
3. inspect the affected files completely;
4. distinguish committed repository state from local uncommitted changes.

If the relevant state cannot be established, return `PLANNING INCOMPLETE`.

## Required reading

Read completely:

* `AGENTS.md`;
* `docs/ROADMAP.md`;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `docs/DEV_GUIDE.md`;
* `README.ru.md`;
* `.github/ISSUE_TEMPLATE/issue.md`;
* relevant architecture and specification documents;
* `docs/WEB_UI.md`;
* `docs/INTEGRATION.md`;
* `docs/API_CONTRACT.md`;
* `docs/COMPONENTS.md`;
* relevant page, block, layout, adapter and configuration contracts;
* relevant related-product ROADMAPs and public integration contracts.

When planning a product-driven BeeUI change, compare at minimum:

* BeeUI `docs/ROADMAP.md`;
* BeeUI public page and block contracts;
* BeeUI integration documentation;
* the related product’s UI roadmap or approved Issue;
* the related product adapter or read-model contract.

Related repositories do not need matching iteration numbers.

Synchronize ownership, contracts and dependencies, not numbering.

## Establish current state

Determine:

* highest completed substantial BeeUI iteration;
* current stage direction;
* implemented generic page and block capabilities;
* implemented API, theme, locale and session behavior;
* current adapter and integration boundary;
* relevant product-repository status;
* behavior implemented ahead of or behind ROADMAP wording;
* known blockers and deferred limitations;
* whether the user’s stated current iteration matches the repository.

Report inconsistencies explicitly.

Do not silently rewrite project history.

## Decide whether an iteration is justified

A numbered BeeUI iteration should deliver a coherent:

* reusable code increment;
* public page, block, API or integration-contract increment;
* operator-facing UI workflow increment;
* security or session-boundary increment.

Documentation-only and repository-maintenance work should normally be a standalone chore.

Approve an iteration only when it:

* closes a current generic UI gap;
* is not already implemented;
* has one coherent deliverable;
* is reusable across products or is explicitly scoped as an integration adapter;
* respects the rule `BeeUI renders. Product decides.`;
* has observable acceptance criteria;
* fits one focused PR or an explicitly coordinated set of PRs.

Reject or revise proposals that:

* duplicate existing behavior;
* mix independent visual, contract, security and integration features without necessity;
* move product or domain decisions into generic BeeUI;
* move generic rendering into a product repository;
* introduce a no-code builder, standalone service, unrestricted write surface or speculative architecture before its roadmap stage;
* depend on an undefined product or BeeUI contract without recording that dependency;
* use a local editable dependency as the intended merge-ready integration mechanism;
* create a second source of truth for product configuration or artifacts.

## Determine repository ownership

Classify every requested behavior before defining the iteration.

### BeeUI ownership

Examples:

* generic page and block schemas;
* generic renderers;
* generic filters and form presentation;
* generic sorting and pagination presentation;
* table, chart, detail, layout and state components;
* theme and locale mechanisms;
* generic session and CSRF behavior;
* reusable static assets;
* generic API envelopes;
* adapter interfaces;
* generic callback boundaries;
* integration documentation.

### Product-repository ownership

Examples:

* domain filters and allowed values;
* product-specific routes;
* product read-model composition;
* product statuses and labels;
* domain validation;
* artifact production;
* capability and authority decisions;
* product configuration values;
* product-specific adapter implementations.

When a feature spans repositories:

1. define the public contract;
2. assign each part to one owning repository;
3. keep each repository in its own branch and PR;
4. define dependency and compatibility requirements;
5. identify review and merge order;
6. avoid temporary local path dependencies as the final contract.

## Roadmap synchronization

Classify each relevant difference as:

* synchronized;
* intentional sequencing difference;
* stale documentation;
* blocking contract gap;
* separate follow-up.

When another repository requires changes:

* define the generic BeeUI contract;
* define the product read-model or adapter contract;
* state which repository moves first;
* state whether independent merge is safe;
* identify the minimum compatible BeeUI version or other reproducible dependency mechanism when applicable.

A related product does not make product-specific behavior generic.

A generic contract should remain product-neutral even when introduced for one product’s immediate need.

## Define the iteration

Provide Russian iteration wording containing:

* iteration number and title;
* status;
* goal;
* reason it is needed now;
* dependencies;
* included scope;
* excluded scope;
* deliverable;
* source of truth;
* BeeUI and product ownership;
* public page, block, API, adapter and configuration impact;
* compatibility impact;
* expected runtime or rendered outputs;
* change level;
* required tests and checks;
* Definition of Done.

Keep the increment substantial but bounded.

Do not combine unrelated theme, localization, navigation, chart, filter, detail, session and dependency work unless they are necessary parts of one coherent acceptance flow.

## Prepare the Issue

Use `.github/ISSUE_TEMPLATE/issue.md`.

Write the Issue in English.

Acceptance criteria must be observable and testable.

State explicitly:

* included and excluded scope;
* source of truth;
* generic versus product ownership;
* configuration impact;
* page, block, API and adapter contract impact;
* compatibility expectations;
* rendered or integration-output impact;
* verification requirements;
* security implications;
* dependency constraints;
* related-repository dependency and merge order when applicable;
* that `pyproject.toml.version` must remain unchanged unless release work is in scope.

When the API changes, require an example response envelope.

When a block schema changes, require an example declarative block configuration.

When UI state is accepted from query parameters, cookies or sessions, require validation and persistence scenarios.

## Select the executor

Choose one executor.

### DeepSeek V4 Flash in Copilot

Use for:

* small, bounded, low-risk changes;
* one or two local components;
* straightforward template or test updates;
* changes with an already defined contract.

### DeepSeek V4 Pro in Copilot

Use for:

* moderate multi-file changes;
* page, block or integration-contract work;
* changes requiring careful coordination of models, renderers, templates, tests and docs;
* runtime-risk work with a clear approved Issue.

### Codex

Use for:

* repository-wide investigation;
* broad multi-subsystem work;
* cross-repository contract changes;
* security-sensitive analysis;
* complex session, CSRF, path, serialization or dependency work;
* substantial independent diagnosis and verification.

Explain the choice briefly.

## Prepare execution prompts

### Implementation prompt

Keep it short.

This is an executor prompt for Copilot or Codex.

Do not include reviewer-only restrictions such as:

* `Use only Bee Dev MCP`;
* read-only mode;
* MCP target identifiers;
* review mode.

Require the executor to work in the exact worktree using its available local repository tools.

Include only:

* exact project, worktree and branch;
* approved Issue;
* instruction to follow `AGENTS.md`;
* applicable implementation workflow if one exists;
* scope restrictions;
* required implementation report.

Do not repeat stable repository rules already defined in `AGENTS.md` or the skill.

Require the executor to report:

* files read;
* change level;
* required checks;
* source of truth;
* architecture-boundary assessment;
* changed files;
* exact tests;
* smoke evidence;
* contract and documentation impact;
* dependency status;
* `version not changed`.

### Verification prompt

Require:

* exact changed-file list;
* exact commands and results;
* targeted and full tests when required;
* expected `./start.sh` entrypoint smoke;
* route, HTML and JSON API scenarios;
* invalid-input scenarios;
* locale, theme or session scenarios when affected;
* logs and rendered outputs inspected;
* configuration and public-contract verification;
* proportional security checks;
* unrelated-file check;
* version confirmation;
* known limitations;
* one complete report.

The verification prompt must not ask for speculative cleanup or unrelated refactoring.

## Tests and checks

Tests must remain proportional to the Issue.

Prefer updating existing test files when they already own the behavior.

Require coverage of the real public boundary, not only helper functions.

Examples:

* declarative model → generic renderer;
* product adapter payload → BeeUI page;
* route query → validation → read-model → HTML;
* route query → validation → JSON API envelope;
* theme or locale selection → persisted bounded UI state;
* unsupported block → explicit unavailable state;
* invalid or missing required configuration → fail-fast error.

Do not require new test helpers or test files without a concrete need.

## Naming

Provide:

* branch name;
* Conventional Commit title;
* repository ownership for every coordinated change;
* recommended review and merge order when multiple repositories are involved.

Use repository-consistent naming and the appropriate commit prefix:

* `feat:`;
* `fix:`;
* `docs:`;
* `refactor:`;
* `test:`;
* `chore:`;
* `ci:`;
* `build:`.

## Output format

Return:

1. `Repository state`
2. `Iteration decision`
3. `Roadmap synchronization`
4. `Ownership boundary`
5. `Updated iteration`
6. `Issue`
7. `Executor`
8. `Implementation prompt`
9. `Verification prompt`
10. `Branch and commit`
11. `Assumptions and limitations`

Do not modify or execute anything.
