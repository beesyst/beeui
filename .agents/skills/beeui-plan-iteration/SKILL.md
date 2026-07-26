---
name: beeui-plan-iteration
description: Inspect the current BeeUI implementation through Bee Dev MCP, validate the necessity and repository ownership of a bounded task, reconcile docs/ROADMAP.md and public UI contracts, and prepare a copy-ready iteration or standalone task plus complete Issues without modifying repositories.
---

# BeeUI iteration planning workflow

## Purpose

Use this workflow when:

- the next BeeUI iteration is not yet approved;
- an existing roadmap item must be validated or refined;
- a proposed UI/framework task must be checked against current implementation;
- an Issue must be prepared from current repository state;
- BeeUI and product repository contracts require alignment;
- a product request may require a new reusable BeeUI primitive or renderer.

Do not use this workflow when a complete Issue has already been approved.

This workflow is read-only.

Use only Bee Dev MCP for repository inspection.

Do not:

- modify files;
- switch branches;
- run shell or Git commands;
- run tests;
- create commits;
- prepare implementation prompts;
- prepare verification prompts;
- prepare a PR body.

## Required inputs

The external prompt `.agents/prompts/01-planning.md` passes:

- `MAIN_WORKTREE` — absolute path to the BeeUI worktree;
- `MODE` — Bee Dev MCP context mode;
- `ROADMAP_CONTEXT` — known iteration, proposed standalone task or `none`;
- `TASK_OR_IDEA` — proposed work;
- `CONTEXT_OR_NONE` — additional context or `none`;
- `ADDITIONAL_PROJECTS_OR_NONE` — related product repositories or `none`.

The external prompt also declares:

- project;
- expected branch;
- base branch.

Treat paths, project names and branches as exact input values.

## Workflow gates

Before proposing a task, read every declared task file completely; add and read any additional needed file before relying on it. Current files/contracts are authoritative and reports are supporting evidence. Reconcile work with `docs/ROADMAP.md`, keep it within scope, preserve “BeeUI renders, product decides”, and hand off KISS constraints: no optional polish, unrelated cleanup, speculative architecture, no-code, auth, config apply, standalone service, separate frontend or product-specific generic-renderer logic.

Determine the actual change level, read applicable SDLC/security requirements and derive proportional checks from the changed boundary. Handoffs must require existing test files/helpers where possible, public-behavior coverage, no duplicate or implementation-detail-only tests, no formatting churn, and no first-party code/test comments except legal, license, upstream and provenance material. Without an approved Python dependency change, handoffs must not read or separately validate `uv.lock`; final inventory alone confirms it is absent.

## ROADMAP_CONTEXT semantics

Handle three variants.

### Variant A — Known numbered iteration

Example:

```text
Iteration 13.10 in docs/ROADMAP.md
```

This is a user-supplied reference that must be validated.

It may describe:

* an existing roadmap item;
* a proposed next item that has not yet been inserted.

Validate:

* whether `docs/ROADMAP.md` exists;
* whether the iteration exists;
* its status and current scope;
* whether the number is unique;
* whether the insertion point is correct;
* whether the stage fits the task;
* whether the task is already implemented;
* whether an existing item already covers it;
* whether the roadmap wording is stale relative to implementation.

The absence of a proposed next iteration from the roadmap is not itself an error.

If the reference is valid, use it.

If it is stale, duplicated, completed, assigned to the wrong stage or inconsistent, explain the correction and select the correct item or insertion point.

### Variant B — Proposed standalone task

Example:

```text
Standalone Fix outside a numbered iteration; validate against current docs/ROADMAP.md
```

Validate that the task is genuinely narrow enough for standalone handling.

If it creates a substantial reusable component, rendering behavior, public contract, route, schema, API, package asset, dependency or operator workflow, reject the standalone classification and propose a numbered iteration.

### Variant C — No known iteration

Canonical value:

```text
none
```

Determine independently:

* whether a numbered iteration is required;
* which stage fits;
* what iteration number should be used;
* where it belongs;
* whether an existing item should be reused or refined.

## Resolve repositories through Bee Dev MCP

Resolve `MAIN_WORKTREE` before planning.

1. Call `list_worktrees` for `beeui`.
2. Match `MAIN_WORKTREE` by exact absolute path.
3. Use the returned MCP target.
4. Call `get_project_context` with the supplied Mode.
5. Verify:

   * project;
   * path;
   * branch;
   * HEAD;
   * dirty state.

For each additional project, repeat exact-path resolution.

Do not:

* infer a target from a branch name;
* substitute the main worktree for a requested worktree;
* assume repositories share iteration numbers;
* execute shell or Git commands.

If the exact worktree cannot be resolved, report the mismatch and stop planning for that target.

If the actual branch differs from the expected branch, report both and do not prepare an implementation Issue for that target.

A dirty worktree is not automatically a blocker.

When dirty changes affect relevant:

* ROADMAPs;
* architecture;
* contracts;
* implementation;
* configuration;
* dependencies;

inspect the current MCP snapshot and distinguish:

* committed state;
* staged changes;
* unstaged changes;
* untracked files.

Do not represent uncommitted content as merged project history.

## Complete reading rule

Repository inspection is incomplete while required content is truncated, omitted or has continuation metadata.

For files:

* continue with the exact `next_line` and `next_column`;
* finish only when both are null.

For manifests or bundles when required:

* continue with the exact `next_cursor`;
* finish only when `has_more=false`;
* require one consistent snapshot.

Read omitted relevant files directly.

If mandatory information cannot be retrieved, return:

```text
PLANNING INCOMPLETE
```

Explain exactly what could not be inspected.

Do not invent repository facts.

## Targeted discovery

Use this sequence:

1. Identify the task type.
2. Inspect repository and dirty state.
3. Read the relevant ROADMAP section.
4. Read process and security rules.
5. Read relevant public contracts.
6. Inspect current implementation and tests.
7. Compare neighbouring completed and planned items.
8. Inspect additional repositories only to the depth required by their declared role.
9. Determine repository ownership.
10. Determine whether companion repository changes are necessary.

Read at minimum in BeeUI:

* `AGENTS.md`;
* `docs/ROADMAP.md`;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `.github/ISSUE_TEMPLATE/issue.md`;
* relevant implementation;
* relevant tests.

When relevant, also inspect:

* `README.ru.md`;
* `docs/DEV_GUIDE.md`;
* `docs/SPEC.md`;
* `docs/WEB_UI.md`;
* `docs/INTEGRATION.md`;
* `docs/API_CONTRACT.md`;
* `docs/COMPONENTS.md`;
* `docs/THEME.md`;
* `config/settings.yml`;
* `config/schema.yml`;
* `pyproject.toml`;
* package-data declarations;
* templates and static assets.

For cross-repository requests, inspect in the product repository only:

* repository guidance;
* relevant roadmap;
* public UI integration contracts;
* adapter/read-model contract;
* relevant dependency declaration;
* current product implementation demonstrating the gap.

The presence of a product repository in additional projects does not authorize planning changes there.

Treat it as contract context unless a product-side change is proven necessary.

## Primary roadmap

The primary BeeUI roadmap is:

```text
docs/ROADMAP.md
```

Use it when the result concerns:

* generic rendering;
* layout or reusable blocks;
* templates or static assets;
* component primitives;
* route or API framework behavior;
* schema/config validation;
* adapter protocol;
* embedded app or mount contract;
* artifact presentation;
* generic auth/session/CSRF transport;
* locale or theme framework behavior;
* package-level browser assets;
* generic operator UX.

Product-specific requirements remain in the product repository roadmap even when a reusable BeeUI change is required.

A product requirement and a reusable BeeUI implementation may therefore require coordinated but separate Issues.

## Repository ownership decision

### BeeUI ownership

A task belongs in BeeUI when it creates or changes a reusable, product-neutral capability such as:

* generic component or layout primitive;
* generic renderer;
* reusable template;
* generic route or API envelope;
* adapter protocol;
* embedded integration mechanism;
* safe internal-link behavior;
* locale/theme framework behavior;
* package-local static asset;
* generic artifact browser behavior;
* generic transport security boundary.

### Product repository ownership

A task belongs in the product repository when it concerns:

* production adapter implementation;
* product read-model;
* product labels and metrics;
* product navigation composition;
* domain-specific query/filter semantics;
* product artifact allowlist;
* product configuration semantics;
* product actions or authority;
* runtime integration;
* product-specific charts or table data.

### Domain repository ownership

A task belongs in a domain module when it concerns:

* taxonomy;
* classification;
* business rules;
* domain validation;
* domain AI eligibility;
* domain fixtures;
* domain recommendations.

### Forbidden ownership shifts

Do not:

* move product semantics into BeeUI;
* move generic rendering into product-owned templates;
* make BeeUI read product storage directly;
* make the product duplicate BeeUI templates/static primitives;
* combine independent repository implementations in one Issue.

## Establish current state

Determine:

* highest completed relevant iteration;
* neighbouring `DONE`, `PLANNED`, `FUTURE` and deferred work;
* current stage direction;
* implementation ahead of or behind roadmap wording;
* active public contracts;
* current package/static behavior;
* known blockers;
* whether `ROADMAP_CONTEXT` is accurate;
* whether the proposed task already exists;
* whether a planned item already covers it.

Report roadmap inconsistencies explicitly.

Do not silently rewrite completed history.

## Decide whether an iteration is justified

### Numbered iteration

A numbered iteration is normally required when the task substantially changes:

* operator or user workflow;
* reusable UI component;
* generic renderer;
* route or API behavior;
* schema or configuration contract;
* adapter protocol;
* package template or static asset contract;
* browser-executed dependency;
* security or authority boundary;
* cross-repository integration;
* locale or theme behavior;
* artifact presentation;
* package or wheel integrity;
* a testable reusable BeeUI capability.

Documentation should normally accompany the technical increment.

### Standalone task

Standalone is appropriate for genuinely small work such as:

* typo;
* formatting;
* narrow documentation correction;
* local bugfix without public contract impact;
* repository housekeeping;
* small test correction;
* small packaging correction with no new behavior.

A standalone task has no iteration number.

### Decision values

Choose one:

```text
reuse
refine
replace
insert
standalone
reject as unnecessary
```

Meanings:

* `reuse` — an existing item already covers the task;
* `refine` — an existing item needs clearer bounded wording;
* `replace` — stale future scope should be replaced;
* `insert` — a new numbered item is justified;
* `standalone` — the work is genuinely outside numbered product flow;
* `reject as unnecessary` — no implementation task is justified.

Justify the decision with repository evidence.

## Approval criteria

Approve an iteration only when it:

* closes a current gap;
* is not already implemented;
* has one coherent deliverable;
* respects BeeUI/product/domain ownership;
* has observable Acceptance Criteria;
* identifies a source of truth;
* records compatibility requirements;
* fits one focused BeeUI PR or an explicitly coordinated repository sequence.

Reject or revise proposals that:

* duplicate current behavior;
* mix independent features;
* add product logic to BeeUI;
* add generic rendering to product-owned templates;
* introduce speculative architecture;
* create a second source of truth;
* depend on an undefined contract without assigning ownership;
* combine unrelated repositories in one Issue.

## Evaluate solution options

When multiple valid boundaries exist, provide no more than three options.

For each state:

* repository ownership;
* implementation outline;
* advantages;
* disadvantages;
* compatibility impact;
* dependency or release impact.

Recommend one option using:

* KISS;
* current public contracts;
* smallest complete change;
* no duplicate source of truth;
* no product-specific generic code;
* minimum cross-repository coupling.

Do not create artificial alternatives.

## Roadmap reconciliation

Before creating a new iteration:

1. Identify neighbouring completed and future items.
2. Check whether an existing item already covers the scope.
3. Detect stale or contradictory future wording.
4. Determine the correct stage.
5. Determine the insertion point.
6. Verify iteration ID uniqueness.
7. Check references and dependencies.
8. Decide whether future items require refinement or retirement.

Do not automatically append to the end of the file.

Do not renumber completed history.

## Iteration numbering

Use minimally disruptive numbering.

Rules:

1. Never renumber `DONE` items.
2. Never change completed iteration IDs.
3. A direct follow-up may use decimal numbering such as `13.10`.
4. Do not force decimal numbering for an independent increment.
5. A standalone task has no iteration number.
6. Renumber only not-completed items when unavoidable.
7. Prefer retiring stale future scope over mass renumbering when references may exist.
8. Do not create duplicate IDs.
9. Show exact renumbering or retirement mapping when required.

## Cross-repository planning

When more than one repository requires implementation:

```text
one implementation repository
= one Issue
= one target worktree
= one feature branch
= one PR
```

A single product requirement may therefore require:

* one BeeUI Issue for reusable framework behavior;
* one product Issue for adapter/read-model integration.

Specify:

* public contract;
* ownership;
* dependency direction;
* implementation order;
* merge order;
* release/dependency update sequence;
* compatibility requirements.

Do not synchronize iteration numbers across repositories.

Synchronize contracts and release order instead.

Run:

```text
.agents/prompts/02-implementation-tests.md
```

separately for every implementation repository.

## Implementation plan

For every implementation target, specify:

* repository;
* primary responsibility;
* existing implementation to reuse;
* confirmed files or layers likely to change;
* public contracts to add or change;
* configuration impact;
* dependency impact;
* static/package impact;
* expected artifacts or outputs;
* backward compatibility;
* security constraints;
* tests;
* route/browser smoke;
* documentation;
* implementation order;
* completion criteria.

Do not invent exact paths without repository evidence.

When the exact file is uncertain, name the confirmed layer and state that the concrete location must be verified by the implementation executor.

## Define the iteration or standalone task

Provide the planning result in Russian.

### Numbered iteration

Include:

* iteration number and title;
* exact roadmap file;
* stage;
* status `PLANNED`;
* goal;
* why it is needed now;
* dependencies;
* included scope;
* excluded scope;
* deliverable;
* source of truth;
* repository ownership;
* configuration and contract impact;
* package/static impact;
* change level;
* required checks;
* Definition of Done.

Produce a copy-ready roadmap fragment matching local style.

The fragment must include:

* scope;
* deliverable;
* contracts;
* security;
* tests;
* documentation;
* Acceptance Criteria;
* non-goals.

### Standalone task

Do not invent an iteration number.

Include:

* title;
* standalone classification;
* reason;
* included and excluded scope;
* deliverable;
* repository ownership;
* contract/config impact;
* change level;
* checks;
* Definition of Done.

Do not produce a fake roadmap fragment.

### Reuse, refine, replace or reject

Identify the exact existing item.

Provide replacement wording only when roadmap wording must change.

Do not create a duplicate iteration.

## Prepare complete Issues

For every implementation target, produce one complete copy-ready Issue in English.

Use the target repository Issue template.

For BeeUI use:

```text
.github/ISSUE_TEMPLATE/issue.md
```

Each Issue must include:

* title;
* summary;
* type;
* exact iteration or standalone classification;
* exact stage when applicable;
* context and current limitation;
* repository scope;
* included scope;
* excluded scope;
* deliverable;
* implementation requirements;
* source of truth;
* public contracts;
* config impact;
* route/API/component impact;
* template/static/package impact;
* security constraints;
* backward compatibility;
* tests;
* smoke checks;
* documentation;
* Acceptance Criteria;
* dependencies;
* implementation evidence;
* Definition of Done.

Use observable requirements.

Do not use vague phrases such as:

```text
implement as needed
update relevant tests
follow best practices
```

The Issue and roadmap fragment must align.

When multiple Issues are required, label them by repository and execution order.

## Issue-specific BeeUI requirements

When relevant, explicitly state:

* whether product-specific logic is forbidden;
* whether product imports are forbidden;
* whether GET routes remain read-only;
* whether route-prefix compatibility is required;
* whether embedded mount compatibility is required;
* whether templates/static files must be package-local;
* whether installed-package or wheel verification is required;
* whether a new dependency or vendored asset is allowed;
* whether `uv.lock` may change;
* whether API envelopes remain backward-compatible;
* whether config invalid values fail fast;
* whether malformed adapter payloads degrade safely;
* whether HTML autoescape and safe internal links must be preserved.

## Change level and checks

Determine the actual expected change level:

* `low-risk`;
* `runtime-risk`;
* `security-sensitive`.

Use `docs/SDLC.md` and `docs/SECURITY.md`.

Define required checks, as applicable:

* targeted tests;
* `uv run pytest -q`;
* `uv run pytest -q -W error::UserWarning`;
* `./start.sh doctor`;
* `./start.sh routes`;
* web smoke;
* affected HTML/API routes;
* route-prefix smoke;
* embedded mount smoke;
* malformed input;
* safe-link validation;
* HTML escaping;
* no-mutation checks;
* package template/static integrity;
* SAST;
* SCA;
* DAST;
* IAST;
* bounded fuzzing.

Do not require every security tool for every task.

Explain why checks are applicable or not applicable.

## Dependencies and release sequencing

When BeeUI changes are consumed by a product:

1. implement BeeUI in its own branch;
2. merge BeeUI;
3. publish or otherwise make the approved BeeUI version available;
4. update the product dependency;
5. update the product lockfile only as part of that approved product Issue;
6. run product integration tests and smoke.

Do not use editable local paths as final dependency evidence unless explicitly approved for development-only verification.

Do not invent a future release number.

During planning, state that the product lower bound must be set to the actual released BeeUI version.

## Executor complexity notes

Record only task-specific factors affecting later executor selection:

* number of BeeUI layers;
* security sensitivity;
* browser-executed code;
* dependency or vendored asset changes;
* package integrity;
* cross-repository release sequencing;
* migration complexity.

Do not select the executor during planning.

Executor selection belongs to:

```text
.agents/prompts/02-implementation-tests.md
```

## Task-specific implementation constraints

Identify only constraints that must be passed to implementation, for example:

* repository ownership;
* required public contract;
* compatibility;
* source of truth;
* forbidden product logic;
* merge and release order;
* dependency restrictions;
* package/static requirements;
* authority restrictions;
* version restrictions.

Do not prepare an implementation prompt.

## Task-specific verification constraints

Define:

* change level;
* targeted scenarios;
* compatibility checks;
* route/browser smoke;
* package integrity;
* artifact/log checks;
* security checks;
* cross-repository contract checks;
* dependency/version checks;
* forbidden mutation, leakage and external-network checks.

Do not prepare a verification prompt.

## Naming

For each implementation target provide:

* repository;
* branch name;
* Conventional Commit title.

Use repository conventions.

Do not propose a version bump unless the task is explicitly release-related.

For ordinary work require:

```text
version not changed
```

## Phase boundary

This skill performs planning only.

Do not prepare:

* Copilot prompts;
* Codex prompts;
* implementation prompts;
* test-execution prompts;
* verification prompts;
* correction prompts;
* final-review prompts;
* PR bodies.

Implementation prompt preparation belongs to:

```text
.agents/prompts/02-implementation-tests.md
```

Final read-only review belongs to:

```text
.agents/prompts/03-final-review.md
```

## Output format

Return:

```text
## Executive verdict

## Repository state

## Current implementation and contracts

## Roadmap selection

## Roadmap reconciliation

## Necessity verdict

## Architecture and repository ownership

## Implementation plan

## Iteration numbering and insertion

## Copy-ready roadmap iteration or standalone task

## Copy-ready Issue
```

For multiple Issues use:

```text
## Copy-ready Issues
```

Then return:

```text
## Implementation order

## Verification and security

## Branch and commit naming

## Planning handoff
```

Add only when needed:

```text
## Assumptions or blockers
```

## Planning handoff

Return:

```text
Primary product repository:
Primary roadmap:
Stage:
Iteration:
Decision:
Implementation targets:
Issue count:
Execution order:
Required separate prompt-02 runs:
Task-specific implementation constraints:
Task-specific verification constraints:
```

For standalone work:

```text
Iteration: none
```

For rejected work:

```text
Implementation targets: none
Issue count: 0
Required separate prompt-02 runs: 0
```

Do not create:

* YAML handoff files;
* JSON planning artifacts;
* automatic roadmap edits;
* automatic Issues;
* branches;
* commits.

Do not modify or execute anything.
