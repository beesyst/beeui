---
name: beeui-plan-iteration
description: Inspect the current BeeUI implementation through Bee Dev MCP, critically validate task necessity and repository ownership, reconcile docs/ROADMAP.md and public UI contracts, and prepare a compact roadmap item or standalone task plus complete copy-ready Issues without modifying repositories.
---

# BeeUI iteration planning workflow

## Purpose

Use this workflow when:

* a BeeUI task or product idea has not yet been approved;
* an existing BeeUI roadmap item must be validated, refined or replaced;
* proposed framework work may already exist in the current implementation;
* a product request may require a reusable BeeUI capability;
* ownership between BeeUI, a product repository and a domain module is unclear;
* coordinated repository changes may be required;
* a complete Issue must be prepared from current repository evidence.

Do not use this workflow when a complete Issue has already been approved and the task is ready for `.agents/prompts/02-implementation-tests.md`.

Planning must determine:

* what BeeUI already provides;
* what product-facing gap actually remains;
* whether BeeUI work is necessary now;
* whether the requested behavior is generic or product-specific;
* whether an existing public contract is sufficient;
* which roadmap owns each increment;
* which repositories must change;
* what must remain excluded;
* what prompt 02 must receive.

This workflow is read-only.

Use only Bee Dev MCP for repository inspection.

Do not:

* modify files;
* switch branches;
* run shell or Git commands;
* run tests;
* create or update Issues;
* create branches, commits or PRs;
* prepare implementation, verification, correction or review prompts;
* prepare PR bodies.

## Repository guidance

Read and follow `AGENTS.md`.

`AGENTS.md` owns stable repository-wide rules, including:

* Bee Dev MCP usage;
* exact target resolution;
* complete reading;
* the `BeeUI renders. Product decides.` boundary;
* sources of truth;
* configuration, template and static-asset rules;
* security and verification requirements;
* dependency and `uv.lock` restrictions;
* package and installed-wheel integrity;
* version restrictions.

Do not repeat all of `AGENTS.md`, `docs/SDLC.md` or `docs/SECURITY.md` in planning output or generated Issues.

This skill owns only:

* the planning decision algorithm;
* roadmap reconciliation;
* generic-versus-product ownership decisions;
* cross-repository sequencing;
* roadmap and Issue output contracts;
* the planning handoff.

## Required inputs

The external prompt `.agents/prompts/01-planning.md` provides:

* `MAIN_WORKTREE`;
* `MODE`;
* `ROADMAP_CONTEXT`;
* `TASK_OR_IDEA`;
* `CONTEXT_OR_NONE`;
* `ADDITIONAL_PROJECTS_OR_NONE`;
* declared project;
* expected branch;
* base branch.

Treat paths, project names, branches, modes and repository roles as exact input values.

Pass `MODE` unchanged to applicable Bee Dev MCP calls.

Do not silently substitute another:

* worktree;
* repository;
* branch;
* roadmap;
* mode.

## Core planning rules

### Evidence before agreement

Treat the proposed task, roadmap reference and supplied reports as hypotheses.

Validate material assumptions against current:

* code;
* templates;
* static assets;
* configuration;
* public contracts;
* package declarations;
* tests;
* rendered behavior;
* dirty changes.

Current repository files and public contracts are authoritative.

Reports, screenshots, previous planning outputs and implementation summaries are supporting evidence only.

Do not automatically accept:

* the proposed iteration ID;
* the proposed stage;
* the proposed repository;
* the proposed generic abstraction;
* the proposed dependency;
* the proposed solution;
* the proposed urgency;
* the assumption that BeeUI must change.

### Critical planning

Answer:

* What reusable capability exists now?
* What product requirement is not supported?
* Is the gap generic or product-specific?
* Is the public BeeUI contract actually insufficient?
* Is the behavior already implemented?
* Does an existing roadmap item cover it?
* Can the product solve it through the current adapter or schema?
* Would the proposal move product decisions into BeeUI?
* Is there a smaller complete solution?
* What should not be built?
* What should BeeUI prioritize next?

When the user’s framing is wrong:

1. show the mismatch using repository evidence;
2. preserve the underlying product intent where possible;
3. correct roadmap, scope, numbering or ownership;
4. provide a usable corrected planning result.

### KISS

Recommend the smallest reusable change that closes the verified gap.

Avoid:

* optional visual polish;
* unrelated cleanup;
* broad refactoring;
* speculative abstractions;
* product-specific behavior in generic code;
* duplicate rendering systems;
* standalone services;
* no-code builders;
* separate frontends;
* frontend build chains without approved scope;
* unnecessary browser or Python dependencies;
* unnecessary cross-repository changes;
* future work hidden inside current scope.

### Roadmap and Issue separation

The roadmap is a compact iteration-level contract.

The Issue is the detailed execution contract.

Do not turn the roadmap into a full implementation specification.

Do not make the Issue so vague that implementation must repeat planning.

## ROADMAP_CONTEXT

`ROADMAP_CONTEXT` is a hypothesis to validate, not an instruction to approve the referenced item.

### Known numbered iteration

Example:

```
Iteration 13.10 in docs/ROADMAP.md
```

Validate:

* that `docs/ROADMAP.md` exists;
* that the iteration exists or is a valid proposed insertion;
* that its ID is unique;
* its status and current scope;
* neighbouring completed and unfinished items;
* whether implementation already delivered it;
* whether another item covers the work;
* whether its stage remains correct;
* whether the wording is stale relative to current contracts.

If the referenced iteration is `DONE`:

* preserve completed history;
* never return it to `PLANNED`;
* never create another item with the same ID;
* determine whether the request is already implemented;
* use a new unique ID only for genuine follow-up work.

Use decimal numbering only for a direct continuation.

Use the next appropriate independent ID for independent work.

The absence of a proposed item from the roadmap is not itself an error.

### Proposed standalone task

Standalone is appropriate only when the work:

* is narrow and local;
* creates no substantial reusable capability;
* introduces no public contract;
* does not materially change rendering, routes or operator workflow;
* does not add package assets or dependencies;
* does not change security or authority boundaries;
* does not require coordinated product releases.

Reject standalone classification when the task creates a substantial:

* reusable component;
* renderer;
* route or API contract;
* adapter contract;
* configuration schema;
* embedded integration;
* browser asset;
* package contract;
* cross-repository capability.

### No known iteration

Canonical value:

```
none
```

Determine independently:

* whether BeeUI work is required;
* whether an existing item should be reused;
* whether unfinished scope should be refined or replaced;
* whether a new iteration is justified;
* whether the task is standalone;
* which stage owns it;
* which unique ID fits;
* whether the work should be deferred or rejected.

Do not require `unknown`.

## Repository resolution and reading

Use the exact target-resolution and complete-reading rules from `AGENTS.md`.

For every declared repository:

1. resolve the exact absolute worktree path through `list_worktrees`;
2. use the returned MCP target;
3. call `get_project_context` with the supplied mode;
4. verify project, path, branch, HEAD and dirty state.

If the primary worktree cannot be resolved, return:

```
PLANNING INCOMPLETE
```

If an additional repository is mandatory for an ownership or contract decision and cannot be resolved, return `PLANNING INCOMPLETE`.

If the actual branch differs from the expected branch:

* report both values;
* do not prepare an implementation Issue for that target;
* continue only with read-only analysis that remains valid.

A dirty worktree is not automatically a blocker.

When dirty work affects planning, distinguish:

* committed state;
* staged changes;
* unstaged changes;
* untracked files;
* deleted or renamed files.

Do not present uncommitted work as merged history.

Do not base a decision on truncated, omitted or partial mandatory content.

If mandatory evidence cannot be retrieved, return:

```
PLANNING INCOMPLETE
```

State what is missing and which decision cannot be made.

## Discovery workflow

Use this sequence:

1. parse `TASK_OR_IDEA`;
2. resolve declared worktrees;
3. inspect relevant dirty state;
4. read the referenced roadmap item and neighbours;
5. read repository guidance and applicable process/security rules;
6. inspect relevant BeeUI public contracts;
7. inspect current implementation and tests;
8. inspect package, template and static-asset behavior when relevant;
9. inspect the product-side adapter, read-model or integration contract when supplied;
10. compare roadmap, implementation, contracts and rendered behavior;
11. identify the actual gap;
12. determine generic, product and domain ownership;
13. determine whether companion repository changes are necessary;
14. assess necessity and timing;
15. select the planning decision;
16. prepare roadmap output, Issues and handoff.

Do not read repositories indiscriminately.

## Required inspection

Read at minimum in BeeUI:

* `AGENTS.md`;
* `docs/ROADMAP.md`;
* the relevant neighbouring roadmap items;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `.github/ISSUE_TEMPLATE/issue.md`;
* relevant implementation;
* relevant tests.

Read as applicable:

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
* app factory and route surfaces;
* adapter protocol;
* component models and renderers;
* templates;
* JavaScript and CSS assets;
* auth, session and CSRF transport;
* packaging and installed-package tests.

For a product repository supplied as additional context, inspect only what is required to determine:

* the product requirement;
* current adapter or read-model behavior;
* current BeeUI dependency;
* public integration contract;
* whether the gap can be solved product-side;
* whether product-side changes are also required.

An additional repository is contract-only until a required implementation change is proven.

## Current state and actual gap

Determine:

* highest completed relevant BeeUI iteration;
* neighbouring `DONE`, `PLANNED`, `FUTURE` and deferred work;
* current stage direction;
* active public contracts;
* reusable components already available;
* route, prefix and embedded behavior;
* current package and static-asset behavior;
* known blockers and deferred limitations;
* implementation-roadmap drift;
* whether the task is already implemented;
* whether another item covers it;
* whether product usage is behind the current BeeUI contract.

Roadmap status is not implementation evidence.

Classify relevant drift as:

```
implementation ahead of roadmap
roadmap ahead of implementation
product integration behind BeeUI
stale future scope
duplicated scope
duplicated iteration ID
completed-history documentation debt
blocking public-contract gap
intentional sequencing difference
separate follow-up
```

Do not create a BeeUI feature solely to compensate for:

* stale documentation;
* incorrect product integration;
* unused existing adapter capabilities;
* product-specific data-shaping problems.

State the verified gap using:

* current behavior;
* required behavior;
* evidence of absence or insufficiency;
* affected public contract;
* product or operator impact;
* why it matters now.

Separate real gaps from:

* documentation drift;
* local defects;
* product adapter defects;
* contract mismatches;
* optional polish;
* future ideas.

## Necessity verdict

Return exactly one:

```
necessary now
necessary after prerequisite
useful but defer
already covered
already implemented
product-side only
standalone maintenance
not justified
```

Consider:

* reusable value across products;
* current product demand;
* roadmap direction;
* prerequisite readiness;
* existing public contracts;
* compatibility burden;
* package and browser-asset cost;
* security impact;
* cross-repository release cost;
* whether one focused increment can deliver it.

Do not approve BeeUI work only because it could be generalized.

Provide concise evidence-based project-development advice when useful.

## Roadmap ownership

### BeeUI roadmap

Use:

```
docs/ROADMAP.md
```

when the main result is a reusable product-neutral capability, such as:

* generic rendering;
* reusable layout or component behavior;
* template or static-asset infrastructure;
* generic HTML or JSON routes;
* route-prefix or embedded-mount behavior;
* adapter protocol;
* generic configuration schema;
* generic API envelope;
* artifact presentation framework;
* generic authentication, session or CSRF transport;
* locale or theme framework;
* package or installed-wheel behavior;
* generic degraded, empty or error states.

### Product roadmap

Keep the product requirement in the product repository roadmap when it concerns:

* product read-models;
* product labels and metrics;
* navigation composition;
* product query or filter semantics;
* artifact allowlists;
* product configuration;
* product actions and authority;
* product charts or table data;
* runtime integration;
* product-specific widget payloads.

A product requirement may need:

* one product roadmap item;
* one reusable BeeUI roadmap item;
* separate coordinated Issues.

### Domain roadmap

Use the domain repository roadmap for:

* taxonomy;
* classification;
* business rules;
* domain validation;
* domain fixtures;
* domain AI contracts;
* domain recommendations and summaries.

Do not move domain behavior into BeeUI or the product adapter.

## Repository ownership

Apply the full architecture boundary from `AGENTS.md`.

Verify that:

### BeeUI owns

* generic rendering and layouts;
* reusable product-neutral components;
* templates and package-local assets;
* generic route and API mechanisms;
* generic configuration and adapter schemas;
* route-prefix and embedded integration;
* generic auth, role, session and CSRF transport;
* safe-link, path and escaping behavior;
* generic degraded and unavailable states;
* package and installed-wheel integrity.

### Product repositories own

* product semantics;
* production adapters;
* read-model construction;
* labels, metrics and calculations;
* product configuration;
* artifacts and allowlists;
* actions and authority;
* callbacks, audit and mutations;
* runtime and external-system integration.

### Domain modules own

* domain models and taxonomy;
* classification and business rules;
* domain fixtures and validation;
* domain summaries, recommendations and AI contracts.

Do not:

* put product semantics in generic BeeUI code;
* add production product adapters to BeeUI;
* import private product or domain internals;
* infer semantics from product route names;
* make BeeUI read product storage directly;
* duplicate product calculations;
* put business decisions in templates or JavaScript;
* duplicate BeeUI rendering in product templates;
* create a second source of truth;
* combine independent repository changes in one Issue.

## Planning decision

Choose exactly one:

```
reuse
refine
replace
insert
standalone
reject as unnecessary
```

### Reuse

Use when an unfinished item already covers the verified task without material changes.

Identify the exact roadmap, stage and iteration.

Do not generate duplicate roadmap wording.

### Refine

Use when an unfinished item is correct in direction but needs clearer:

* scope;
* generic boundary;
* exclusions;
* compatibility;
* acceptance criteria;
* checks;
* sequencing.

Do not refine completed history.

### Replace

Use when unfinished future scope is stale, duplicated or based on an incorrect BeeUI/product boundary.

Show:

* the item being replaced;
* why it is stale;
* replacement wording;
* downstream impact.

### Insert

Use when no current item covers a verified reusable gap.

A new item must:

* close a current gap;
* create one coherent reusable deliverable;
* remain product-neutral;
* preserve compatibility or explicitly define change;
* have observable acceptance criteria;
* fit one focused BeeUI Issue;
* match the current roadmap direction.

### Standalone

Use only for genuinely small maintenance outside numbered product flow.

### Reject as unnecessary

Use when:

* the capability already exists;
* another item covers it;
* the gap is product-side only;
* the proposal duplicates a contract or renderer;
* the abstraction is premature;
* no reusable BeeUI responsibility remains.

Explain the simpler product-side or existing-contract alternative where applicable.

## Iteration versus standalone

A numbered iteration is normally required for substantial changes to:

* reusable UI components;
* generic renderers;
* route or API behavior;
* configuration schema;
* adapter protocol;
* embedded or route-prefix behavior;
* package templates or static assets;
* browser-executed dependencies;
* security or authority transport;
* locale or theme behavior;
* artifact presentation;
* package or wheel integrity;
* cross-repository public contracts;
* another testable reusable capability.

Standalone is normally appropriate for:

* typo or formatting fixes;
* narrow documentation alignment;
* small test corrections;
* repository housekeeping;
* narrow local bugs without public-contract impact;
* small skill maintenance;
* small packaging corrections without new behavior.

Documentation normally accompanies technical work rather than becoming a separate iteration.

## Solution options

Present no more than three materially valid options.

For each option state:

* BeeUI, product and domain ownership;
* implementation boundary;
* contracts reused or changed;
* advantages and disadvantages;
* compatibility impact;
* dependency and release impact;
* principal risk.

Recommend one using:

* smallest complete reusable change;
* strongest reuse of current contracts;
* correct BeeUI/product boundary;
* no second source of truth;
* no product-specific generic code;
* minimum coupling and migration;
* proportionate verification;
* no speculative architecture.

Do not manufacture alternatives.

If one valid bounded solution exists, state that directly.

## Roadmap reconciliation and numbering

Before changing `docs/ROADMAP.md`:

1. inspect the referenced item;
2. inspect neighbouring completed and unfinished items;
3. check overlapping and duplicate scope;
4. check duplicate IDs;
5. compare implementation with roadmap claims;
6. select the correct stage and insertion point;
7. preserve completed history;
8. decide whether unfinished items need refinement, retirement or renumbering;
9. check references and dependencies.

Rules:

* never change or renumber `DONE` IDs;
* never reuse a completed ID;
* never leave duplicate IDs;
* use decimal numbering only for direct continuation;
* use the next suitable whole number for independent work;
* renumber unfinished items only when unavoidable;
* prefer retiring stale future scope over mass renumbering;
* do not synchronize IDs with product repositories;
* show an exact retirement or renumbering map when required.

Do not automatically append to the end of the roadmap.

## Cross-repository planning

Use:

```
one implementation repository
= one Issue
= one target worktree
= one feature branch
= one PR
```

A product requirement may therefore require:

* one BeeUI Issue for reusable framework behavior;
* one product Issue for adapter, read-model or dependency integration.

For every implementation target define:

* repository responsibility;
* public contract;
* dependency direction;
* prerequisites;
* implementation and merge order;
* release or dependency-update order;
* compatibility requirements;
* verification and completion condition.

Do not assign product work merely because a product repository was supplied.

Do not assign BeeUI work until the current public contract is proven insufficient.

When a product consumes a BeeUI change:

1. implement and verify BeeUI;
2. merge BeeUI;
3. make an approved BeeUI revision available;
4. update the product to an actually available version or revision;
5. update product dependency files only inside the approved product Issue;
6. run product integration and route/browser smoke.

Do not invent a future BeeUI version.

Run `.agents/prompts/02-implementation-tests.md` separately for every repository Issue.

## Implementation plan

For each implementation target provide:

* repository and responsibility;
* current implementation to reuse;
* verified layers likely to change;
* behavior and public contracts to change;
* source of truth;
* configuration impact;
* route, API, component or adapter impact;
* template, static or package impact;
* dependency impact;
* compatibility requirements;
* security and authority constraints;
* automated scenarios;
* route, browser or package smoke;
* documentation;
* implementation order;
* completion criteria.

Do not invent exact file paths.

When a file is unconfirmed, name the verified layer and require the executor to confirm the concrete location.

Do not turn the plan into an executor prompt.

## Roadmap output contract

For a numbered item, provide a compact copy-ready fragment with exactly these iteration headings:

```
Goal
Scope
Excluded
Deliverable
Acceptance criteria
Checks
DoD
```

Use this form:

```
## Этап <номер> — <English stage title>

### Итерация <ID> — <English iteration title>

**Статус:** PLANNED

#### Goal

<Russian content>

#### Scope

<Russian content>

#### Excluded

<Russian content>

#### Deliverable

<Russian content>

#### Acceptance criteria

<Russian content>

#### Checks

<Russian content>

#### DoD

<Russian content>
```

Rules:

* stage and iteration titles are English;
* body is Russian;
* technical identifiers remain unchanged;
* include only iteration-level information;
* move implementation detail into the Issue;
* target 40–60 lines;
* absolute maximum 80 lines;
* do not add extra iteration headings;
* do not repeat an existing stage heading when only an iteration block must be inserted.

For `reuse`, do not generate a duplicate fragment.

For `refine` or `replace`, provide the complete replacement fragment.

For `reject as unnecessary`, provide no fake iteration.

## Standalone output contract

For standalone work provide:

```
Title:
Classification: standalone
Reason:
Scope:
Excluded:
Deliverable:
Checks:
DoD:
Roadmap insertion required: no
```

Use Russian except for technical identifiers.

Do not invent an iteration number.

## Issue preparation

Prepare one complete Issue in English per implementation repository.

Read and follow the target repository’s actual:

```
.github/ISSUE_TEMPLATE/issue.md
```

Rules:

* preserve the actual heading order;
* fill all relevant sections;
* use the actual roadmap file;
* use observable and testable requirements;
* keep Issue scope aligned with the roadmap;
* do not duplicate stable rules from `AGENTS.md`;
* include only task-specific constraints.

For standalone work state:

```
Iteration: none
```

The Issue must cover as applicable:

* current limitation and why now;
* repository ownership;
* included and excluded scope;
* deliverable;
* source of truth;
* public contracts;
* configuration impact;
* route, API, component or adapter impact;
* template, static and package impact;
* dependency impact;
* compatibility requirements;
* security and authority constraints;
* automated tests;
* route, browser and package smoke;
* documentation;
* dependencies and sequencing;
* Acceptance Criteria;
* Definition of Done;
* `version not changed`.

Do not use vague requirements such as:

```
implement as needed
update relevant tests
follow best practices
handle edge cases
make it robust
```

### BeeUI-specific Issue decisions

When applicable, explicitly state:

* whether product-specific logic is forbidden;
* whether product imports are forbidden;
* whether GET routes remain read-only;
* whether route-prefix compatibility is required;
* whether embedded-mount compatibility is required;
* whether API envelopes remain compatible;
* whether invalid configuration fails fast;
* whether malformed optional adapter data degrades safely;
* whether autoescape and safe internal links must be preserved;
* whether templates and static assets remain package-local;
* whether installed-package or wheel verification is required;
* whether external network references are forbidden;
* whether a dependency or vendored asset change is approved;
* whether dependency files may change.

Determine the expected change level from current SDLC and security rules:

```
low-risk
runtime-risk
security-sensitive
```

Require only checks proportional to the approved boundary.

Never require:

```
uv lock --check
```

Do not propose a version bump unless the task is explicitly release-related.

## Planning handoff constraints

Provide concise task-specific implementation constraints, including only applicable:

* generic versus product ownership;
* current implementation to reuse;
* required public contract;
* source of truth;
* compatibility;
* forbidden product logic or imports;
* route-prefix and embedded behavior;
* configuration and adapter behavior;
* template, static and package requirements;
* dependency restrictions;
* external-network restrictions;
* merge and release order;
* version restriction;
* dirty-worktree reconciliation.

Provide concise task-specific verification constraints, including only applicable:

* expected change level;
* Acceptance Criteria scenarios;
* targeted and full tests;
* HTML and JSON route smoke;
* route-prefix or embedded smoke;
* browser behavior;
* malformed config or adapter input;
* autoescape and safe-link checks;
* read-only and no-mutation checks;
* package or wheel integrity;
* static-asset provenance;
* external-network checks;
* dependency status;
* cross-repository contract checks.

Do not prepare implementation, verification or correction prompts.

Record only material executor complexity factors:

* number of repositories;
* number of BeeUI layers;
* browser-executed code;
* security sensitivity;
* dependency or vendored-asset changes;
* package integrity;
* compatibility or migration;
* cross-repository release sequencing.

Do not select Copilot or Codex.

## Naming

For each implementation repository provide:

* recommended branch name;
* recommended Conventional Commit title.

Follow current repository conventions.

Do not propose commit operations, push commands, tags or invented release numbers.

For ordinary work state:

```
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

Implementation and verification prompt preparation belongs to:

```
.agents/prompts/02-implementation-tests.md
```

Final read-only review and PR preparation belongs to:

```
.agents/prompts/03-final-review.md
```

## Output format

Return these sections in order:

```
## Executive verdict
## Repository state
## Current implementation and contracts
## Roadmap selection
## Roadmap reconciliation
## Necessity verdict
## Architecture and repository ownership
## Solution options and recommendation
## Implementation plan
## Iteration numbering and insertion
## Copy-ready roadmap iteration or standalone task
## Copy-ready Issue
```

Use `## Copy-ready Issues` when more than one repository requires implementation.

Then return:

```
## Implementation order
## Verification and security
## Branch and commit naming
## Project-development recommendations
## Planning handoff
```

Add `## Assumptions or blockers` only when necessary.

Write:

* planning analysis in Russian;
* roadmap body in Russian;
* roadmap stage and iteration titles in English;
* Issues in English;
* technical identifiers unchanged.

Keep analysis concise.

Do not repeat the same evidence across sections.

Do not claim Bee Dev MCP ran tests.

## Planning handoff

Return:

```
Primary product repository:
Primary roadmap:
Stage:
Iteration:
Decision:
Necessity verdict:
Implementation targets:
Issue count:
Execution order:
Required separate prompt-02 runs:
Source of truth:
Public contracts:
Compatibility requirements:
Task-specific implementation constraints:
Task-specific verification constraints:
Executor complexity factors:
Version status:
```

For standalone work:

```
Iteration: none
```

For rejected or product-side-only work with no BeeUI implementation:

```
Implementation targets: none
Issue count: 0
Required separate prompt-02 runs: 0
```

When more than one repository must change, list implementation targets in execution order.

Do not create:

* YAML handoff files;
* JSON planning artifacts;
* automatic roadmap edits;
* automatic Issues;
* branches;
* commits;
* PRs.

Do not modify or execute anything.
