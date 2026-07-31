---
name: beeui-review-and-close
description: Perform a complete read-only BeeUI review against an approved Issue using the exact worktree and base branch, then return one consolidated verdict and PR close package.
---

# BeeUI review and close workflow

## Purpose

Use this workflow after implementation and verification are complete.

This workflow:

- uses only Bee Dev MCP;
- is read-only;
- reviews one exact BeeUI target against one declared base branch;
- returns one consolidated verdict.

Do not:

- modify files;
- run repository commands;
- switch branches;
- create commits;
- push;
- create or update a PR;
- merge.

Follow all stable MCP, repository, architecture, review and security rules from `AGENTS.md`.

## Required inputs

Obtain:

- project;
- exact instruction worktree;
- exact target worktree;
- expected feature branch;
- expected base branch;
- Mode;
- roadmap context;
- approved Issue content or GitHub Issue URL;
- current PR description, GitHub Pull Request URL or `none`;
- implementation and verification evidence;
- additional targets and their declared roles;
- previous blockers when performing re-review.

The filesystem path, MCP target and Git branch are separate identifiers.

## Workflow gates

Read every declared review file completely before issuing findings; add and read an additional file before relying on it. Current files/contracts are authoritative and reports are supporting evidence. Reconcile the Issue with `docs/ROADMAP.md`, preserve “BeeUI renders, product decides”, and treat optional polish, unrelated cleanup, speculative architecture, no-code, auth, config apply, standalone service, separate frontend and product-specific generic-renderer logic as out of scope.

Determine actual change level, read applicable SDLC/security requirements and derive proportional checks from the changed boundary. Do not require every security tool or treat an optional check as a blocker. Any new first-party code/test comment, inline explanation, TODO/FIXME/NOTE or decorative separator is a blocker. Preserve copyright, legal, license, upstream-vendored and provenance comments; do not require unrelated existing comments to be removed. Review unnecessary test complexity, duplicate assertions, new helpers/files without need and formatting churn as blockers only when they demonstrate scope drift, unnecessary complexity or unrelated diff. Without an approved dependency change, do not inspect `uv.lock`; confirm only from changed-file inventory that it is absent.

## Phase 0 — Resolve supplied GitHub context

Follow the GitHub context resolution contract from `AGENTS.md`.

When the approved Issue input contains a GitHub Issue URL:

1. call `get_github_context`;
2. read the Issue title;
3. read the complete Issue body;
4. read all Issue comments;
5. use explicit accepted clarifications from comments when establishing the approved scope.

When the current PR input contains a GitHub Pull Request URL:

1. call `get_github_context`;
2. read the PR title;
3. read the complete PR body;
4. read all conversation comments;
5. read reviews;
6. read inline review comments.

The approved Issue establishes the required scope and Acceptance Criteria.

The PR provides delivery, implementation and reviewer context. It does not override the approved Issue or the actual target worktree.

When pasted content and a URL are supplied together, consider both. Report a material conflict instead of silently discarding either source.

If required GitHub context cannot be read completely, return:

```text
ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА
```

## Phase 1 — Resolve instruction and target worktrees

Use `list_worktrees` to resolve both worktrees by exact absolute path.

For the instruction worktree:

1. verify its exact path;
2. verify its expected branch;
3. obtain its MCP target;
4. read:
   - `AGENTS.md`;
   - `.agents/skills/beeui-review-and-close/SKILL.md`.

When instruction and target paths differ, use the instruction worktree only as an instruction source. When they are the same absolute path, read instructions there and inspect that same exact target.

For the target worktree:

1. verify its exact path;
2. verify its project;
3. verify its expected feature branch;
4. verify HEAD and dirty state;
5. obtain its MCP target.

Inspect implementation only from the target worktree.

Do not substitute another worktree or infer a target from a branch name.

If either required worktree cannot be resolved exactly, return:

```text
ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА
```

If the target project or branch differs from expected values, report the mismatch and do not issue a code verdict.

## Phase 2 — Acquire the complete review snapshot

Use:

- `get_review_manifest`;
- `get_review_bundle_page`.

Follow the complete-reading and snapshot rules from `AGENTS.md`.

The review must consume:

- the complete manifest;
- the complete non-truncated diff;
- one consistent `snapshot_id`;
- all continuation pages.

Inventory:

- committed files;
- staged files;
- unstaged files;
- untracked files;
- deleted files;
- renamed files;
- omitted files;
- redacted paths.

The manifest is authoritative for file inventory.

The diff is evidence of changed content.

Do not use compatibility `get_review_bundle` as a substitute for the paginated review bundle.

If the manifest or diff is incomplete, truncated, inconsistent or unavailable, return:

```text
ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА
```

Do not issue implementation findings from a partial snapshot.

## Phase 3 — Read the required files

Use the complete approved Issue context resolved from the supplied input in Phase 0.

Read completely from the target worktree:

- `.github/PULL_REQUEST_TEMPLATE/pr.md`;
- the relevant `docs/ROADMAP.md` section;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- every changed and untracked text file;
- directly related tests;
- directly related unchanged contracts, callers, imports and configuration.

When applicable, also read:

- public UI and API contracts;
- templates;
- static assets;
- package-data declarations;
- configuration schemas;
- dependency declarations;
- affected documentation.

For deleted files, inspect:

- the complete diff;
- remaining references, imports, contracts and callers.

For renamed files, inspect:

- old and new paths;
- the complete destination file;
- updated references.

Read omitted relevant files directly through `read_project_file`.

If a mandatory relevant file is unreadable or redacted through the safe MCP interface, return:

```text
ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА
```

## Phase 4 — Inspect additional targets

Inspect an additional target only when it is explicitly supplied with a review role.

For each additional target:

1. resolve the exact worktree;
2. verify its expected branch;
3. follow its declared Mode and Skill;
4. inspect only the contracts needed for the BeeUI verdict.

Do not perform an independent full review of a related product repository unless its declared role explicitly requires one.

Do not include unrelated related-repository changes in the BeeUI verdict.

Report a cross-repository blocker only when the BeeUI implementation requires a public contract that is absent or incompatible in the declared related target.

## Phase 5 — Evaluate evidence and Acceptance Criteria

Follow the instruction and evidence precedence from `AGENTS.md`.

The following are supporting evidence only:

- implementation reports;
- verification reports;
- current PR text;
- previous review comments;
- supplied command output.

Current manifest, diff, files, contracts and observable implementation are authoritative.

Bee Dev MCP does not execute tests.

For supplied test or smoke output:

- name the reported command;
- identify it as supplied evidence;
- verify whether it covers the required scenario;
- do not claim MCP ran it.

Evaluate every Acceptance Criterion as:

- `satisfied`;
- `partially satisfied`;
- `not satisfied`;
- `not verifiable`;
- `not applicable`.

Determine the actual change level using `docs/SDLC.md` and `docs/SECURITY.md`.

Review all affected boundaries required by:

- the approved Issue;
- the actual diff;
- the actual change level;
- `AGENTS.md`;
- applicable public contracts.

A missing verification result is a blocker only when that evidence is required by the Issue, SDLC, security rules or actual changed boundary.

## Phase 6 — Identify real blockers

A blocking finding must affect readiness of the current Issue.

Examples include:

- an unmet Acceptance Criterion;
- incorrect or unsafe behavior;
- BeeUI/product/domain ownership violation;
- source-of-truth violation;
- incompatible public contract;
- broken required rendering, route or package behavior;
- missing required validation;
- missing required verification;
- unrelated files entering the change;
- unintended dependency declaration, inventory `uv.lock` or version changes;
- documentation contradicting implemented public behavior;
- a required cross-repository contract gap.

Do not create blockers from:

- optional polish;
- subjective visual or naming preferences;
- speculative future architecture;
- unrelated cleanup;
- requirements absent from the approved Issue;
- MCP limitations themselves.

Perform one complete review pass and consolidate all real blockers.

## Phase 7 — Completeness gate

Before issuing a verdict, confirm:

- exact instruction worktree verified;
- exact target worktree verified;
- expected feature branch verified;
- expected base branch verified;
- complete manifest consumed;
- complete non-truncated diff consumed;
- one consistent snapshot used;
- changed and untracked files inventoried;
- changed files read completely;
- deleted and renamed paths inspected;
- relevant unchanged contracts and callers read;
- applicable additional targets evaluated;
- every Acceptance Criterion evaluated;
- supplied verification evidence evaluated;
- dependency declaration and version scope checked, with `uv.lock` absent from inventory unless dependency change is approved;
- package and static impact checked when applicable;
- all blockers consolidated.

If any mandatory inspection remains incomplete, return:

```text
ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА
```

Include:

- completed inspection;
- exact missing data, file, tool result or continuation;
- reason no code verdict was issued.

Do not include:

- speculative implementation findings;
- a correction prompt;
- a PR body;
- an approval or rejection verdict.

## Phase 8 — Verdict

For a complete review, return exactly one verdict:

```text
ОДОБРЕНО ДЛЯ PR
```

or:

```text
ТРЕБУЮТСЯ ИЗМЕНЕНИЯ
```

### ОДОБРЕНО ДЛЯ PR

Use only when no blockers remain.

State exactly:

```text
Правки не нужны.
```

Then provide:

1. Покрытие критериев приёмки;
2. Проверенные файлы;
3. Доказательства проверок;
4. Непроверенные ограничения;
5. Проверенный target и branch;
6. Рекомендуемый squash commit;
7. Текст PR;
8. Решение о закрытии;
9. Явные дальнейшие действия: commit проверенных изменений, push feature branch, создание или обновление PR, ожидание CI и squash merge после approval.

Do not claim that MCP ran tests or smoke commands.

### ТРЕБУЮТСЯ ИЗМЕНЕНИЯ

Provide every blocker in this format:

### <Finding title>

Файл:

`path/to/file`

Точное место:

<existing function, class, template block, JavaScript block or configuration section>

Было:

```<language>
<exact bounded current code, configuration or template fragment>
```

Стало:

```<language>
<complete bounded replacement or insertion>
```

Почему:

<Acceptance Criterion, existing contract and concrete blocking impact>

For a code, configuration, JavaScript or template blocker, include the exact bounded current fragment and the complete bounded replacement or insertion.

For a behavior-only blocker, describe the exact observed and required behavior.

For an evidence-only blocker, provide the exact missing command or verification scenario instead of inventing a code change.

Do not return only the correction prompt. Present every real current-Issue blocker and its exact correction first, then provide one consolidated correction prompt.

Do not prepare a final PR body while blockers remain.

## Consolidated correction prompt

Select and name the executor:

- Copilot for localized, clearly specified corrections;
- Codex for broad diagnosis, multi-layer, dependency-sensitive or security-sensitive corrections.

The correction prompt is for an implementation executor, not Bee Dev MCP.

It must contain:

```text
Executor: <selected executor>

Project: beeui
Instruction worktree: <exact instruction worktree>
Target worktree: <exact target worktree>
Expected branch: <feature branch>
Base branch: <base branch>

Read instructions from:

- <instruction worktree>/AGENTS.md
- <instruction worktree>/.agents/skills/beeui-verify-and-correct/SKILL.md

If instruction and target worktrees differ, use the instruction worktree only for reading instructions and inspect, modify and verify only the target worktree. If their absolute paths are identical, read instructions and then inspect, modify and verify that same exact target worktree.

Fix only the blocking findings below.
Preserve all already working behavior within the approved Issue.

Blocking findings:

For every blocker use:

### <Finding title>

Файл:
`<path>`

Точное место:
<existing function, class, template block, JavaScript block or configuration section>

Было:
<exact bounded current fragment or observed behavior>

Стало:
<complete bounded replacement, insertion or required behavior>

Почему:
<acceptance criterion, contract violation or concrete impact>

For code, configuration, JavaScript or template blockers, include the bounded current fragment and complete replacement or insertion supplied by the review.

For behavior-only or evidence-only blockers, include the exact required behavior, command or verification scenario instead of inventing code.

Required verification:

- targeted regression tests for every blocker;
- full tests required by the actual change level;
- applicable HTML and JSON route smoke;
- applicable route-prefix and embedded-mount smoke;
- applicable malformed-input, escaping, safe-link and no-mutation checks;
- applicable template, static-asset and package-content checks;
- applicable security and public-contract checks;
- `git diff --check`;
- dependency and version verification;
- unrelated-file check.

Return one consolidated verification and correction report according to
beeui-verify-and-correct.

Do not commit, push, create or update a PR, or merge.
```

The correction prompt must:

- include every blocker;
- include exact worktree and branch information;
- authorize modification only in the target worktree;
- reference `AGENTS.md` and `beeui-verify-and-correct`;
- require proportional regression and full applicable verification;
- prohibit unrelated cleanup and optional polish.

Do not copy into the correction prompt:

- Bee Dev MCP restrictions;
- review-only read-only restrictions;
- MCP target identifiers;
- the full approved Issue;
- accumulated implementation and verification evidence;
- the full review report;
- stable rules already contained in `AGENTS.md`;
- requirements unrelated to the blockers.

## Re-review

For re-review:

1. obtain a new complete manifest and diff;
2. verify the same paths, branches and base branch;
3. verify every previous blocker;
4. evaluate all original Acceptance Criteria again;
5. inspect regressions introduced by corrections;
6. return `ОДОБРЕНО ДЛЯ PR` or only the remaining blockers.

Do not introduce optional findings unrelated to the original Issue or corrections.

## PR body

When approved, complete:

```text
.github/PULL_REQUEST_TEMPLATE/pr.md
```

Use only inspected implementation and supplied verification evidence.

The completed PR body must accurately represent:

- implemented scope;
- excluded scope;
- Issue and roadmap context;
- actual change level;
- changed layers and contracts;
- configuration impact;
- template, static and package impact;
- tests and smoke evidence;
- security review;
- dependency and version status;
- known limitations;
- checklist state.

Do not mark an item complete without evidence.

Use `not applicable` when appropriate.

Do not invent:

- Issue numbers;
- test or smoke results;
- artifact paths;
- dependency reviews;
- release versions;
- completed checklist evidence.

Recommend a squash commit using Conventional Commits.

Do not recommend a version bump unless the approved Issue is release-related.

## Output format

For a completed review return:

1. `Вердикт`
2. `Блокирующие замечания`
3. `Покрытие критериев приёмки`
4. `Проверенные файлы`
5. `Доказательства проверок`
6. `Непроверенные ограничения`
7. `Решение о закрытии`
8. `Текст PR` only when approval
9. `Сводный prompt на исправление` only when blockers exist

For incomplete inspection return:

1. `ФИНАЛЬНАЯ ПРОВЕРКА НЕ ЗАВЕРШЕНА`
2. `Что проверено`
3. `Каких данных не хватает`
4. `Почему кодовый вердикт не вынесен`
