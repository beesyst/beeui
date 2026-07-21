---
name: beeui-review-and-close
description: Perform a complete read-only BeeUI review against an approved Issue, using the exact worktree and base branch, then return one consolidated verdict and PR close package.
---

# BeeUI review and close workflow

## Purpose

Use this workflow after implementation is complete and the user has supplied:

* an approved Issue or acceptance criteria;
* implementation evidence;
* exact worktree information;
* expected branch and base branch.

This workflow is read-only.

Do not:

* modify files;
* run repository commands;
* switch branches;
* create commits;
* push;
* create or merge a PR.

## Required inputs

Obtain:

* project;
* expected worktree path;
* expected branch;
* expected base branch;
* mode;
* full Issue;
* implementation evidence;
* related product-repository context when explicitly requested;
* previous blocking findings for re-review.

The worktree path, MCP target and Git branch are separate identifiers.

## Phase 1 — Resolve the exact target

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

If the exact path or mandatory metadata is unavailable, return `REVIEW INCOMPLETE`.

If the project or branch differs from the expected value, report expected and actual values and do not issue a code verdict.

Do not infer an MCP target from a branch name.

Do not substitute the main worktree for a requested feature worktree.

## Phase 2 — Read the complete manifest and diff

### Review manifest

1. Call `get_review_manifest` with an empty cursor.
2. Append each returned `content` page.
3. Continue with the exact `next_cursor` while `has_more=true`.
4. Require the same `snapshot_id` on every page.
5. Parse the combined content as one JSON manifest.

Verify:

* project;
* target;
* branch;
* HEAD;
* expected base branch;
* dirty state;
* committed files;
* staged files;
* unstaged files;
* untracked files;
* deleted files;
* renamed files;
* omitted or redacted paths.

### Review diff

1. Call `get_review_bundle_page` with an empty cursor.
2. Append each returned `content` page.
3. Continue with the exact `next_cursor` while `has_more=true`.
4. Require the same snapshot as the manifest.
5. Finish only when:

   * `has_more=false`;
   * `next_cursor=null`;
   * `truncated=false`.

Do not use compatibility `get_review_bundle` as a substitute.

If pagination fails, the snapshot changes or the diff is truncated, return `REVIEW INCOMPLETE`.

The manifest is the authoritative file inventory.

The complete diff is evidence of the changes.

## Phase 3 — Resolve review instructions

Read `AGENTS.md` and this skill from the primary target.

If they are absent because the feature worktree predates their introduction, use the explicitly supplied canonical `beeui/main` worktree:

1. resolve it through `list_worktrees`;

2. verify its exact path and `main` branch through `get_project_context`;

3. read:

   * `AGENTS.md`;
   * `.agents/skills/beeui-review-and-close/SKILL.md`;

4. use them only as review instructions;

5. continue reviewing code exclusively from the original target.

Their absence from a legacy feature worktree is not a finding.

Do not silently choose another instruction source.

## Phase 4 — Read required files

Use `read_project_file`.

When it returns `next_line` or `next_column`, continue with those exact values until both are null.

Read completely:

* `AGENTS.md`;
* this skill;
* `.github/PULL_REQUEST_TEMPLATE/pr.md`;
* relevant `docs/ROADMAP.md` section;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* `docs/DEV_GUIDE.md`;
* `README.ru.md`;
* `docs/WEB_UI.md`;
* `docs/INTEGRATION.md`;
* `docs/API_CONTRACT.md`;
* `docs/COMPONENTS.md`;
* relevant architecture, configuration and package contracts;
* every changed and untracked text file;
* relevant tests;
* directly related unchanged imports, models, registries, renderers, templates, routes, adapters, configuration and callers.

When relevant, inspect:

* `pyproject.toml`;
* dependency lockfile;
* application factory and entrypoint;
* page and block models;
* page and block registries;
* layout and component renderers;
* Jinja templates;
* static JavaScript and CSS;
* locale and theme mechanisms;
* session and CSRF boundaries;
* adapter interfaces;
* safe-path and artifact-display helpers;
* API response-envelope implementation.

For deleted files:

* inspect the complete diff;
* inspect affected current imports, contracts and callers.

For renamed files:

* inspect old and new paths in the manifest and diff;
* read the destination file completely;
* verify updated references.

If a required relevant file is omitted, redacted or unreadable through the available safe MCP interface, return `REVIEW INCOMPLETE`.

Do not issue a verdict from partial file content.

## Phase 5 — Related product-repository context

When a related product repository is explicitly supplied:

1. resolve its exact path through `list_worktrees`;
2. verify its expected branch through `get_project_context`;
3. read only the public product adapter, read-model, route or configuration contracts required to review the BeeUI target;
4. do not perform an independent review of the related repository;
5. do not include unrelated related-repository state in the BeeUI verdict.

For cross-repository UI work:

* BeeUI owns generic rendering and reusable UI primitives.
* Product repositories own product adapters, product read-models and product semantics.
* Domain business rules belong in the owning product or domain module.
* Product-specific behavior must not be added to generic BeeUI components.
* Generic rendering logic must not be duplicated in a product repository.

If the BeeUI Issue explicitly requires compatibility with the supplied product branch:

* compare every consumed and produced public field;
* verify block-type names;
* verify required and optional fields;
* verify validation ownership;
* verify rendering and serialization behavior;
* verify query-state preservation;
* verify error, empty and unavailable states;
* verify compatibility and dependency expectations.

A missing or incompatible required product contract is a blocker when cross-repository integration is part of the Issue.

Do not block an independently valid generic BeeUI contract solely because a related product has not adopted it, unless product integration is an acceptance criterion.

If the BeeUI implementation contains product-specific branching to satisfy one related product, report an architecture blocker even when the current product integration appears to work.

## Phase 6 — Evidence and acceptance criteria

Follow the instruction and evidence precedence defined in `AGENTS.md`.

The implementation report is supporting evidence, not the source of truth.

Bee Dev MCP cannot execute tests.

Treat supplied command output as reported evidence and never claim MCP ran the commands.

Evaluate every acceptance criterion as:

* satisfied;
* partially satisfied;
* not satisfied;
* not verifiable;
* not applicable.

Check as applicable:

* observable HTML behavior;
* JSON API behavior;
* public page and block contracts;
* generic rendering behavior;
* adapter compatibility;
* configuration source of truth;
* fail-fast validation;
* architecture ownership;
* backward compatibility;
* query, cookie and session validation;
* theme and locale persistence;
* loading, empty, success, warning, error, disabled and unavailable states;
* escaping and safe rendering;
* path and artifact-access boundaries;
* session, role and CSRF boundaries;
* read-only and bounded-action guarantees;
* documentation;
* required tests, smoke and logs;
* dependency and lockfile scope;
* version declarations.

`Not verifiable` is a blocker only when the Issue, SDLC or security rules require that evidence for merge readiness.

## Phase 7 — Contract review

For every new or changed public model field, block type, route, query parameter or API field, determine:

1. source of truth;
2. owning repository;
3. where it is created;
4. where it is validated;
5. where it is rendered or serialized;
6. whether it is required or optional;
7. fallback or unavailable behavior;
8. compatibility impact;
9. documentation coverage;
10. test coverage through the real public boundary.

Do not accept:

* a helper-only test as proof that the public renderer works;
* a monkeypatch as proof of compatibility with the actual generic registry;
* a local editable checkout as proof of merge-ready dependency compatibility;
* silent dropping of documented public fields;
* product-specific field names in generic logic without a justified generic contract;
* template behavior that bypasses model validation;
* query or cookie values that become product configuration.

## Phase 8 — Scope review

Compare the complete manifest and diff with the approved Issue.

Determine:

* whether every changed file supports the Issue;
* whether unrelated visual or infrastructure work entered the PR;
* whether theme, locale, navigation, charts, filters, detail rendering, auth, dependency or API changes were actually approved;
* whether public-contract changes were declared;
* whether dependency changes were declared;
* whether ROADMAP and Issue remain aligned;
* whether the work should have been separated into coordinated PRs;
* whether documentation describes the actual implemented behavior.

A broad change is not automatically a blocker.

It is a blocker when unrelated behavior enters the current PR, required review level is bypassed, or acceptance and compatibility cannot be established.

## Phase 9 — Blocking findings

A blocker must affect readiness of the current Issue.

Examples:

* unmet acceptance criteria;
* incorrect or unsafe rendering;
* broken route or JSON API behavior;
* security, session or CSRF bypass;
* user-controlled path or HTML risk;
* product-specific behavior in a generic BeeUI component;
* generic renderer or template logic duplicated outside BeeUI;
* conflicting source of truth;
* missing fail-fast validation;
* incompatible page, block, API or adapter contract;
* required public fields silently discarded;
* incorrect query encoding or state preservation;
* incorrect sorting, filtering or pagination behavior;
* missing required verification;
* unrelated changes entering the PR;
* unintended dependency, lockfile or version changes;
* non-reproducible local dependency configuration;
* documentation contradicting public behavior;
* missing required cross-repository compatibility.

Do not make blockers from:

* optional visual polish;
* personal naming preferences;
* speculative future architecture;
* unrelated cleanup;
* requirements absent from the Issue;
* MCP limitations themselves;
* a related product not adopting an independently valid generic contract when integration is outside the Issue.

Find and consolidate all real blockers before returning the verdict.

## Phase 10 — Completeness gate

Before issuing a code verdict, confirm:

* exact target and branch verified;
* expected base branch verified;
* complete manifest consumed;
* complete non-truncated diff consumed;
* manifest and diff use the same snapshot;
* changed and untracked files fully inventoried;
* required changed files fully read;
* deleted and renamed paths inspected;
* relevant unchanged contracts read;
* requested related-product context evaluated;
* every acceptance criterion evaluated;
* public-contract impact evaluated;
* verification evidence evaluated;
* dependency and version scope checked;
* all blockers consolidated.

If any mandatory inspection remains incomplete, return:

```text
REVIEW INCOMPLETE
```

Include:

* completed inspection;
* exact missing tool, metadata, file or continuation;
* reason no code verdict was issued.

Do not include:

* implementation findings based on partial inspection;
* correction prompt;
* PR body;
* code verdict.

## Phase 11 — Verdict

Return exactly one completed-review verdict:

```text
APPROVED
```

or:

```text
CHANGES REQUIRED
```

### APPROVED

Use only when no blockers remain.

State exactly:

```text
Правки не нужны.
```

Then provide:

1. acceptance-criteria coverage;
2. files reviewed;
3. supplied verification evidence;
4. non-blocking limitations;
5. reviewed branch and HEAD;
6. recommended branch and squash commit;
7. completed PR body using the repository template;
8. merge readiness;
9. related-repository dependency or merge order when applicable.

Do not claim MCP ran tests.

### CHANGES REQUIRED

Provide every blocker in this format:

```text
### <Finding title>

Файл:
`path/to/file`

Было:
<current incorrect behavior>

Стало:
<required behavior within the Issue>

Почему:
<evidence and impact>
```

For a cross-repository finding, also state:

```text
Owner:
`beeui` or the related product repository

Integration impact:
<effect on the related public contract>
```

Then provide one consolidated correction prompt.

Do not prepare a final PR body while blockers remain.

## Consolidated correction prompt

The prompt must be short, self-contained and written in Russian unless another language is requested.

Include:

* exact project, target, worktree, branch, base branch and mode;
* instruction to follow `AGENTS.md` and the applicable skill;
* correction objective;
* all blocking findings;
* affected files or contracts where known;
* related-repository contract requirements when applicable;
* required regression tests and verification;
* implementation-report requirements;
* explicit prohibition of unrelated work, dependency changes, version changes, commit, push, PR and merge.

Do not repeat the full Issue, review report or stable repository rules.

Do not introduce new requirements or optional improvements.

Require confirmation:

```text
version not changed
```

If a dependency change is itself an approved required correction, do not prohibit it. Require exact declaration, lockfile consistency, SCA evidence and reproducible installation instead.

## Re-review

For re-review:

1. obtain a new complete manifest and paginated diff;
2. verify the same path, branch and base;
3. verify every previous blocker;
4. evaluate the original acceptance criteria again;
5. inspect regressions introduced by corrections;
6. re-check related public contracts when affected;
7. return `APPROVED` or only the remaining blockers.

Do not introduce unrelated optional findings.

## PR preparation

When approved, complete `.github/PULL_REQUEST_TEMPLATE/pr.md` from inspected facts and supplied evidence.

The PR body must state:

* concrete behavior changed;
* included and excluded scope;
* related Issue and ROADMAP iteration;
* change level;
* page, block, API, adapter and configuration impact;
* dependency status;
* exact supplied test commands and results;
* manual or smoke scenarios;
* security checks required and completed;
* documentation changes;
* known limitations;
* related-repository dependency and merge order when applicable;
* `version not changed`.

Do not mark an unchecked verification item as completed.

Do not invent issue numbers, commands, outputs or artifacts.

## Branch and commit naming

Use the Issue type and repository conventions.

Examples:

* `feat/<issue>-<short-name>`;
* `fix/<issue>-<short-name>`;
* `docs/<issue>-<short-name>`;
* `chore/<issue>-<short-name>`.

Recommended squash commit prefixes:

* `feat:`;
* `fix:`;
* `docs:`;
* `refactor:`;
* `test:`;
* `chore:`;
* `ci:`;
* `build:`.

Use a scope when it improves precision:

```text
feat(blocks): add generic filter form
fix(router): validate dashboard query parameters
feat(theme): add persisted dark theme
```

Do not describe a breaking change unless the inspected public contract actually requires one.

## Output format

For a completed review:

1. `Verdict`
2. `Blocking findings`
3. `Acceptance Criteria coverage`
4. `Files reviewed`
5. `Verification evidence`
6. `Unverified limitations`
7. `Close decision`
8. `Branch and commit`
9. `PR body` when approved
10. `Consolidated correction prompt` when changes are required

For incomplete inspection:

1. `REVIEW INCOMPLETE`
2. `Completed inspection`
3. `Missing inspection data`
4. `Reason no code verdict was issued`
