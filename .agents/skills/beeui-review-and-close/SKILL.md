---
name: beeui-review-and-close
description: Perform a complete read-only BeeUI review against an approved Issue using the exact worktree and base branch, then return one consolidated verdict and PR close package.
---

# BeeUI review and close workflow

## Purpose

Use this workflow after implementation and verification are complete.

This workflow:

* uses only Bee Dev MCP;
* is read-only;
* reviews one exact BeeUI target against one declared base branch;
* returns one consolidated verdict.

Do not:

* modify files;
* run repository commands;
* switch branches;
* create commits;
* push;
* create or update a PR;
* merge.

Follow all stable MCP, repository, architecture, review and security rules from `AGENTS.md`.

## Required inputs

Obtain:

* project;
* exact instruction worktree;
* exact target worktree;
* expected feature branch;
* expected base branch;
* Mode;
* roadmap context;
* full approved Issue;
* current PR text or `none`;
* implementation and verification evidence;
* additional targets and their declared roles;
* previous blockers when performing re-review.

The filesystem path, MCP target and Git branch are separate identifiers.

## Phase 1 — Resolve instruction and target worktrees

Use `list_worktrees` to resolve both worktrees by exact absolute path.

For the instruction worktree:

1. verify its exact path;
2. verify its expected branch;
3. obtain its MCP target;
4. read:

   * `AGENTS.md`;
   * `.agents/skills/beeui-review-and-close/SKILL.md`.

Use the instruction worktree only as an instruction source.

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
REVIEW INCOMPLETE
```

If the target project or branch differs from expected values, report the mismatch and do not issue a code verdict.

## Phase 2 — Acquire the complete review snapshot

Use:

* `get_review_manifest`;
* `get_review_bundle_page`.

Follow the complete-reading and snapshot rules from `AGENTS.md`.

The review must consume:

* the complete manifest;
* the complete non-truncated diff;
* one consistent `snapshot_id`;
* all continuation pages.

Inventory:

* committed files;
* staged files;
* unstaged files;
* untracked files;
* deleted files;
* renamed files;
* omitted files;
* redacted paths.

The manifest is authoritative for file inventory.

The diff is evidence of changed content.

Do not use compatibility `get_review_bundle` as a substitute for the paginated review bundle.

If the manifest or diff is incomplete, truncated, inconsistent or unavailable, return:

```text
REVIEW INCOMPLETE
```

Do not issue implementation findings from a partial snapshot.

## Phase 3 — Read the required files

Read completely from the target worktree:

* the approved Issue context;
* `.github/PULL_REQUEST_TEMPLATE/pr.md`;
* the relevant `docs/ROADMAP.md` section;
* `docs/SDLC.md`;
* `docs/SECURITY.md`;
* every changed and untracked text file;
* directly related tests;
* directly related unchanged contracts, callers, imports and configuration.

When applicable, also read:

* public UI and API contracts;
* templates;
* static assets;
* package-data declarations;
* configuration schemas;
* dependency declarations;
* affected documentation.

For deleted files, inspect:

* the complete diff;
* remaining references, imports, contracts and callers.

For renamed files, inspect:

* old and new paths;
* the complete destination file;
* updated references.

Read omitted relevant files directly through `read_project_file`.

If a mandatory relevant file is unreadable or redacted through the safe MCP interface, return:

```text
REVIEW INCOMPLETE
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

* implementation reports;
* verification reports;
* current PR text;
* previous review comments;
* supplied command output.

Current manifest, diff, files, contracts and observable implementation are authoritative.

Bee Dev MCP does not execute tests.

For supplied test or smoke output:

* name the reported command;
* identify it as supplied evidence;
* verify whether it covers the required scenario;
* do not claim MCP ran it.

Evaluate every Acceptance Criterion as:

* `satisfied`;
* `partially satisfied`;
* `not satisfied`;
* `not verifiable`;
* `not applicable`.

Determine the actual change level using `docs/SDLC.md` and `docs/SECURITY.md`.

Review all affected boundaries required by:

* the approved Issue;
* the actual diff;
* the actual change level;
* `AGENTS.md`;
* applicable public contracts.

A missing verification result is a blocker only when that evidence is required by the Issue, SDLC, security rules or actual changed boundary.

## Phase 6 — Identify real blockers

A blocking finding must affect readiness of the current Issue.

Examples include:

* an unmet Acceptance Criterion;
* incorrect or unsafe behavior;
* BeeUI/product/domain ownership violation;
* source-of-truth violation;
* incompatible public contract;
* broken required rendering, route or package behavior;
* missing required validation;
* missing required verification;
* unrelated files entering the change;
* unintended dependency, lockfile or version changes;
* documentation contradicting implemented public behavior;
* a required cross-repository contract gap.

Do not create blockers from:

* optional polish;
* subjective visual or naming preferences;
* speculative future architecture;
* unrelated cleanup;
* requirements absent from the approved Issue;
* MCP limitations themselves.

Perform one complete review pass and consolidate all real blockers.

## Phase 7 — Completeness gate

Before issuing a verdict, confirm:

* exact instruction worktree verified;
* exact target worktree verified;
* expected feature branch verified;
* expected base branch verified;
* complete manifest consumed;
* complete non-truncated diff consumed;
* one consistent snapshot used;
* changed and untracked files inventoried;
* changed files read completely;
* deleted and renamed paths inspected;
* relevant unchanged contracts and callers read;
* applicable additional targets evaluated;
* every Acceptance Criterion evaluated;
* supplied verification evidence evaluated;
* dependency, lockfile and version scope checked;
* package and static impact checked when applicable;
* all blockers consolidated.

If any mandatory inspection remains incomplete, return:

```text
REVIEW INCOMPLETE
```

Include:

* completed inspection;
* exact missing data, file, tool result or continuation;
* reason no code verdict was issued.

Do not include:

* speculative implementation findings;
* a correction prompt;
* a PR body;
* an approval or rejection verdict.

## Phase 8 — Verdict

For a complete review, return exactly one verdict:

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

1. Acceptance Criteria coverage;
2. files reviewed;
3. supplied verification evidence;
4. unverified non-blocking limitations;
5. reviewed target and branch;
6. recommended squash commit;
7. completed PR body;
8. merge readiness.

Do not claim that MCP ran tests or smoke commands.

### CHANGES REQUIRED

Provide every blocker in this format:

```text
### <Finding title>

Файл:
`path/to/file`

Было:
<current incorrect behavior>

Стало:
<required behavior inside the approved Issue>

Почему:
<repository evidence and concrete impact>
```

Then provide one consolidated correction prompt.

Do not prepare a final PR body while blockers remain.

## Consolidated correction prompt

Select one executor:

* `DeepSeek V4 Flash in Copilot` for one or two localized, obvious corrections;
* `DeepSeek V4 Pro in Copilot` for several connected BeeUI-layer corrections;
* `Codex` for broad, security-sensitive, dependency-sensitive or multi-subsystem corrections.

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

Use the instruction worktree only for reading instructions.
Inspect, modify and verify files only in the target worktree.
Do not modify the instruction worktree.

Approved Issue context:
<exact Issue identity and Acceptance Criteria relevant to the blockers>

Implementation and verification evidence:
<relevant current evidence or none>

Fix only the blocking findings below.
Preserve all already working behavior within the approved Issue.

Blocking findings:

<all blockers in Файл → Было → Стало → Почему format>

Run all checks required by the blockers, the actual change level and
beeui-verify-and-correct.

Return one consolidated verification and correction report according to
beeui-verify-and-correct.

Do not commit, push, create or update a PR, or merge.
```

The correction prompt must:

* include every blocker;
* include exact worktree and branch information;
* authorize modification only in the target worktree;
* reference `AGENTS.md` and `beeui-verify-and-correct`;
* include only Issue context relevant to the blockers;
* require proportional regression and full applicable verification;
* prohibit unrelated cleanup and optional polish.

Do not copy into the correction prompt:

* Bee Dev MCP restrictions;
* review-only read-only restrictions;
* MCP target identifiers;
* the full review report;
* stable rules already contained in `AGENTS.md`;
* requirements unrelated to the blockers.

## Re-review

For re-review:

1. obtain a new complete manifest and diff;
2. verify the same paths, branches and base branch;
3. verify every previous blocker;
4. evaluate all original Acceptance Criteria again;
5. inspect regressions introduced by corrections;
6. return `APPROVED` or only the remaining blockers.

Do not introduce optional findings unrelated to the original Issue or corrections.

## PR body

When approved, complete:

```text
.github/PULL_REQUEST_TEMPLATE/pr.md
```

Use only inspected implementation and supplied verification evidence.

The completed PR body must accurately represent:

* implemented scope;
* excluded scope;
* Issue and roadmap context;
* actual change level;
* changed layers and contracts;
* configuration impact;
* template, static and package impact;
* tests and smoke evidence;
* security review;
* dependency and version status;
* known limitations;
* checklist state.

Do not mark an item complete without evidence.

Use `not applicable` when appropriate.

Do not invent:

* Issue numbers;
* test or smoke results;
* artifact paths;
* dependency reviews;
* release versions;
* completed checklist evidence.

Recommend a squash commit using Conventional Commits.

Do not recommend a version bump unless the approved Issue is release-related.

## Output format

For a completed review return:

1. `Verdict`
2. `Blocking findings`
3. `Acceptance Criteria coverage`
4. `Files reviewed`
5. `Verification evidence`
6. `Unverified limitations`
7. `Close decision`
8. `PR body` when approved
9. `Consolidated correction prompt` when changes are required

For incomplete inspection return:

1. `REVIEW INCOMPLETE`
2. `Completed inspection`
3. `Missing inspection data`
4. `Reason no code verdict was issued`
