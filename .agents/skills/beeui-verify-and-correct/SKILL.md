---
name: beeui-verify-and-correct
description: Independently verify an implemented BeeUI Issue, apply only necessary in-scope corrections, and return consolidated evidence for final read-only review.
---

# BeeUI verification and correction workflow

## Purpose

Use this workflow:

* after initial implementation;
* after implementation tests;
* after a read-only review returns blocking findings.

The executor may:

* inspect repository files;
* modify the exact target worktree;
* run local repository checks.

Do not:

* expand the approved Issue;
* add optional polish;
* perform unrelated cleanup or refactoring;
* create speculative architecture;
* create preventive corrections without a demonstrated blocker;
* commit, push, create or update a PR, or merge;
* change the project version unless the Issue is explicitly release-related.

Follow all stable repository, architecture, rendering, dependency, security and verification rules from `AGENTS.md`.

## Required inputs

Obtain:

* project;
* exact target worktree;
* expected branch;
* base branch;
* full approved Issue;
* implementation evidence;
* previous verification evidence when supplied;
* final-review blockers when supplied;
* explicitly supplied related-repository contracts.

## Workflow gates

Before proposing or editing, read every task-declared file completely; add and read any additional needed file before modifying a related file. Current files/contracts are authoritative, reports are supporting evidence. Reconcile the Issue with `docs/ROADMAP.md`, preserve “BeeUI renders, product decides”, and do not add optional polish, unrelated cleanup, speculative architecture, no-code, auth, config apply, standalone service, separate frontend or product-specific generic-renderer logic.

Determine actual change level, read applicable SDLC/security requirements and derive proportional checks from the changed boundary. Use only the smallest demonstrated correction and proportional public-behavior tests in existing files/helpers; do not create implementation-detail-only tests, duplicate assertions, new test files/helpers without need, formatting churn or unrelated test rewrites. Do not add first-party code/test comments, inline explanations, TODO/FIXME/NOTE or separators; preserve legal, license, upstream and provenance comments.

Without an explicitly approved Python dependency change, do not read or separately validate `uv.lock`; confirm only from final changed-file inventory that it is absent.

## Phase 1 — Verify the exact target

Before verification:

1. verify the current working directory;
2. verify the current branch;
3. inspect `git status`;
4. inventory committed changes relative to the base branch;
5. inventory staged, unstaged and untracked changes;
6. distinguish current-Issue changes from unrelated changes.

Stop when:

* the path differs from the requested target;
* the branch differs from the expected branch;
* mandatory Issue or target information is missing;
* unrelated changes prevent safe verification.

Do not silently:

* switch branches;
* substitute another worktree;
* reset or overwrite existing changes;
* modify an instruction or related worktree.

## Phase 2 — Read authoritative evidence

Read:

* `AGENTS.md`;
* the full approved Issue;
* the relevant `docs/ROADMAP.md` section;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* every changed and untracked file;
* directly related contracts, callers and tests;
* affected templates, static assets and package declarations;
* supplied implementation and review evidence.

Read additional unchanged files when required to understand the changed behavior or public contract.

Reports are supporting evidence only.

Current files, diff, tests, rendered behavior, logs, artifacts and package contents are authoritative.

## Phase 3 — Independently verify the implementation

Evaluate every Acceptance Criterion as:

* `satisfied`;
* `partially satisfied`;
* `not satisfied`;
* `not verifiable`;
* `not applicable`.

Determine the actual change level using `docs/SDLC.md` and `docs/SECURITY.md`.

Verify the affected boundaries defined by:

* the approved Issue;
* the actual diff;
* `AGENTS.md`;
* relevant public contracts.

At minimum, determine:

* whether the source of truth is preserved;
* whether BeeUI/product/domain ownership is correct;
* whether observable behavior matches the Issue;
* whether compatibility requirements are satisfied;
* whether required validation and degraded behavior are correct;
* whether required templates and static assets are packaged;
* whether dependency declarations and version remain in scope;
* whether required tests and smoke evidence exist;
* whether security and authority boundaries are preserved.

Do not treat a report as proof when current repository evidence contradicts it.

## Phase 4 — Classify findings

A blocking finding must demonstrate one of:

* an unsatisfied Acceptance Criterion;
* incorrect current-Issue behavior;
* unsafe current-Issue behavior;
* an architecture or ownership violation;
* a source-of-truth violation;
* a public-contract incompatibility;
* missing package or runtime behavior required by the Issue;
* missing verification required by the Issue or actual change level;
* an unintended dependency declaration, inventory `uv.lock` or version change;
* unrelated changes entering the current Issue.

Do not create blockers from:

* optional visual polish;
* subjective naming or formatting preferences;
* unrelated existing code;
* speculative future requirements;
* optional checks not required by the actual change level;
* preventive work with no demonstrated failure or risk.

Consolidate all real findings before making corrections.

## Phase 5 — Apply necessary corrections

Apply a correction only when it closes a demonstrated blocker.

Corrections must be:

* limited to the approved Issue;
* minimal and complete;
* consistent with `AGENTS.md` and current public contracts;
* covered by proportional regression verification;
* free of unrelated cleanup.

Preserve already working behavior.

Do not introduce new requirements or another review cycle “just in case”.

When no correction is required, do not change files.

## Phase 6 — Run required checks

Run checks required by:

* every corrected blocker;
* every Acceptance Criterion;
* the actual change level;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* the affected public contract.

As applicable, verify:

* targeted regressions;
* the full test suite;
* expected repository entrypoints;
* affected HTML and JSON routes;
* route-prefix and embedded-mount behavior;
* invalid and malformed inputs;
* rendering and browser-facing security;
* logs and bounded artifacts;
* templates, static assets and package contents;
* no-mutation behavior;
* dependency and version scope;
* security checks required by the changed boundary;
* `git diff --check`.

Prefer existing test files and helpers.

Record:

* exact commands;
* exit codes;
* passed;
* failed;
* skipped;
* warnings.

Do not claim a check passed when it was not executed.

When a required check cannot be run, identify it explicitly and mark the corresponding evidence as not verifiable.

## Phase 7 — Final readiness check

Before returning:

1. inspect the final changed-file inventory;
2. verify every original Acceptance Criterion again;
3. verify every supplied review blocker;
4. verify regressions introduced by corrections;
5. confirm that no unrelated files entered the change;
6. confirm dependency declaration and version status;
7. identify remaining limitations;
8. determine whether the implementation is ready for final read-only review.

## Final report

Return one consolidated report containing:

1. `Target verification`
2. `Actual changed-file inventory`
3. `Acceptance Criteria coverage`
4. `Blocking findings received`
5. `Independent findings`
6. `Corrections made`
7. `Change level`
8. `Required checks`
9. `Tests and commands`
10. `Routes and runtime smoke`
11. `Logs`
12. `Artifacts, templates and static package data`
13. `Security review`
14. `Dependencies`
15. `Unrelated-file check`
16. `Known limitations`
17. `Recommended Conventional Commit`
18. `Final readiness`
19. `Version status`

Describe every correction as:

```text
Файл:
`path/to/file`

Было:
<previous incorrect behavior>

Стало:
<implemented required behavior>

Почему:
<Acceptance Criterion, contract violation or concrete impact>
```

Do not include a raw diff.

When no correction was required, state:

```text
Правки не потребовались.
```

End with:

```text
version not changed
```

unless the approved Issue explicitly requires release versioning.
