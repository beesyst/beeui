---
name: beeui-implement-issue
description: Implement one approved BeeUI Issue in the exact target worktree and return complete implementation and verification evidence.
---

# BeeUI approved Issue implementation workflow

## Purpose

Use this workflow after:

- an Issue has been approved;
- an exact BeeUI target worktree exists;
- the expected feature branch has been prepared.

The executor may:

- inspect repository files;
- modify the exact target worktree;
- run local repository checks.

Do not:

- expand the approved Issue;
- perform unrelated refactoring, cleanup or optional visual polish;
- commit, push, create or update a PR, or merge;
- change the project version unless the Issue is explicitly release-related.

Follow all stable repository, architecture, configuration, rendering, dependency, security and verification rules from `AGENTS.md`.

## Required inputs

Obtain:

- project;
- exact target worktree;
- expected branch;
- base branch;
- approved Issue or normalized approved task contract;
- Issue source when supplied;
- planning constraints;
- explicitly supplied related-repository contracts.

## Workflow gates

Before proposing, designing or editing, read every task-declared file completely. Add and read any additional needed file before changing a related file. Current files and contracts are authoritative; reports and prior comments are supporting evidence. Map the Issue to its current `docs/ROADMAP.md` iteration, stay within approved scope, and preserve: BeeUI renders, product decides. Do not introduce optional polish, unrelated cleanup, speculative architecture, no-code, auth, config apply, standalone service, separate frontend or product-specific generic-renderer logic.

Determine change level, read applicable SDLC/security requirements, and derive proportional checks from the changed boundary. Use the smallest complete solution and proportional public-behavior tests in existing files/helpers; do not add implementation-detail-only tests, duplicate assertions, new test files/helpers without need, unrelated test rewrites or formatting churn. Do not add first-party code/test comments, inline explanations, TODO/FIXME/NOTE or separators; preserve legal, license, upstream and provenance comments.

Without an explicitly approved Python dependency change, do not read or separately validate `uv.lock`; confirm only from final changed-file inventory that it is absent.

## Phase 1 — Verify the exact target

Before changing files:

1. verify the current working directory;
2. verify the current branch;
3. inspect `git status`;
4. verify the requested target worktree;
5. identify committed, staged, unstaged and untracked changes;
6. distinguish current-Issue changes from unrelated pre-existing changes.

Stop when:

- the path differs from the requested target;
- the branch differs from the expected branch;
- unrelated changes prevent safe attribution;
- the approved Issue or normalized approved task contract is missing;
- the Issue materially conflicts with `AGENTS.md` or an existing public contract.

Do not silently:

- switch branches;
- substitute another worktree;
- reset or overwrite existing user changes;
- modify an instruction or related worktree.

## Phase 2 — Establish scope and current state

Read:

- `AGENTS.md`;
- the approved Issue or normalized approved task contract;
- the relevant `docs/ROADMAP.md` section;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- directly relevant public contracts;
- directly relevant implementation;
- directly relevant configuration;
- directly relevant tests.

Read templates, static assets, package-data declarations and documentation when affected by the Issue.

Read related repositories only when an explicitly supplied public contract must be verified.

Do not modify another repository unless the approved Issue explicitly assigns implementation there.

Treat planning reports and previous comments as supporting context only.

Current files, contracts, tests and runtime behavior are authoritative.

## Phase 3 — Classify and design the change

Determine the actual change level:

- `low-risk`;
- `runtime-risk`;
- `security-sensitive`.

Use `docs/SDLC.md` and `docs/SECURITY.md`.

Before implementation, identify:

- the current source of truth;
- the source of truth after the change;
- the BeeUI-owned responsibility;
- any product-owned or domain-owned responsibility;
- the public contract affected by the change;
- compatibility requirements;
- checks required by the actual change level.

If the actual implementation requires a higher change level than the Issue declares:

1. report the mismatch;
2. identify the affected boundary;
3. derive the additional required checks;
4. continue only when the approved scope still authorizes the change.

## Phase 4 — Implement

Implement the smallest complete solution satisfying the approved Scope and every Acceptance Criterion.

Use `AGENTS.md` as the source of stable implementation rules.

During implementation:

- reuse existing contracts, helpers, templates, components and tests;
- preserve BeeUI/product/domain ownership;
- update public contracts and documentation when observable behavior changes;
- preserve backward compatibility unless the Issue explicitly permits a breaking change;
- keep dependency declarations and project version unchanged unless the Issue explicitly requires otherwise;
- keep all changes attributable to the current Issue.

Do not add behavior merely because it may be useful in a future iteration.

## Phase 5 — Test and verify

Map every Acceptance Criterion to implementation and verification evidence.

Add or update only tests proportional to the Issue.

Prefer existing test files and helpers. Create a new test file or helper only when the required behavior cannot be covered cleanly in the existing structure.

Run all checks required by:

- the approved Issue;
- the actual change level;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- the affected public contract.

As applicable, verify:

- targeted regression behavior;
- the full test suite;
- expected repository entrypoints;
- affected HTML and JSON routes;
- route-prefix and embedded-mount behavior;
- malformed and invalid inputs;
- rendering and browser-facing security;
- logs and bounded artifacts;
- templates, static assets and installed-package contents;
- dependency and version scope;
- security checks required by the changed boundary;
- `git diff --check`.

Use `uv run` for Python commands and repository entrypoints documented by the project.

Record for every executed command:

- exact command;
- exit code;
- passed count;
- failed count;
- skipped count;
- warnings.

Do not claim that a check passed when it was not executed.

When a required check cannot be run, state:

- the exact missing check;
- why it was not run;
- what remains unverified.

## Phase 6 — Final integrity check

Before reporting completion:

1. inspect the final `git status`;
2. inspect the complete current-Issue diff;
3. confirm that no unrelated files entered the change;
4. confirm Acceptance Criteria coverage;
5. confirm documentation and contract consistency;
6. confirm dependency declaration and version status;
7. confirm project version status;
8. confirm applicable template, static and package-data integrity;
9. identify remaining limitations.
10. **mandatory comment/docstring gate**: determine the merge-base with the declared base branch, inspect the complete merge-base diff, and include untracked first-party source, template, JavaScript and test files. Review all added and changed lines by file type; use more than one complementary method and inspect every match in context. Do not accept a single brittle grep as proof. Detect first-party comments, Python docstrings, JavaScript or Jinja/HTML comments, inline explanations, `TODO`, `FIXME`, `NOTE` and decorative separators. Preserve only legal, license, copyright, upstream-vendored and provenance comments. Before readiness, explicitly list the checked source, test, JavaScript and template scope. Any prohibited addition makes the result _not ready_ until removed.

## Implementation report

Return one consolidated report containing:

1. `Target verification`
2. `Files read`
3. `Change level`
4. `Required checks`
5. `Source of truth`
6. `BeeUI/product boundary`
7. `Changed files`
8. `Acceptance Criteria coverage`
9. `Tests and commands`
10. `Routes and runtime smoke`
11. `Logs`
12. `Artifacts, templates and static package data`
13. `Security review`
14. `Dependencies`
15. `Unrelated-file check`
16. `Known limitations`
17. `Recommended Conventional Commit`
18. `Version status`

For every substantive change, use:

```text
Файл:
`path/to/file`

Было:
<previous behavior or limitation>

Стало:
<implemented behavior>

Почему:
<approved Issue requirement>
```

Do not include a raw diff.

Do not repeat the same change in several report sections.

End with:

```text
version not changed
```

unless the approved Issue explicitly requires release versioning.
