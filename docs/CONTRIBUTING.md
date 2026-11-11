# CONTRIBUTING

This repository uses Conventional Commits so that release-please can automatically:

- bump the version (SemVer)
- generate Release Notes / CHANGELOG
- create tags in the form vX.Y.Z

Important: the version is bumped when a release is published (through a Release PR from release-please), rather than with every commit.

A simple, disciplined workflow:

`ROADMAP → Issue → branch → code → tests → artifacts → PR → merge`

Goals:

- small, clear changes;
- reproducible checks;
- minimal bureaucracy;
- a clean change history;
- safe work on the core platform.

## Core rules

- `main` is the only stable branch;
- all work takes place on a separate branch;
- all changes go through a PR;
- do not mix unrelated tasks in a single PR.

## Branches

Rule: `main` is the only stable/release branch. Make all changes on a separate branch → PR → merge into `main` (preferably using `Squash and merge`).

Branch naming (one branch = one task):

- `feat/<short-title>` — new functionality
- `fix/<short-title>` — a bug fix
- `docs/<short-title>` — documentation-only changes
- `chore/<short-title>` — maintenance/infrastructure/settings/supporting changes without a new feature

If an Issue number is available, include it in the branch name:

- `feat/12-config-schema`
- `fix/7-parser-crash`
- `docs/18-roadmap-update`
- `chore/22-repo-cleanup`

Naming rules:

- keep names short;
- use lowercase;
- separate words with `-`;
- one branch = one task;
- do not mix unrelated feature/fix/docs/chore changes in a single branch.

Examples:

- `feat/risk-profiles`
- `fix/parser-empty-input`
- `docs/roadmap-update`
- `docs/update-project-docs`
- `chore/contributing-update`
- `chore/repo-cleanup`

Example commands:

- create a branch: `git switch -c docs/roadmap-update`
- push to origin: `git push -u origin docs/roadmap-update`

### Commands

| Step | Goal                                                                   | Command(s)                                     | Expected output / interpretation                                                                                          |
| ---: | ---------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
|    0 | Check that the working tree is clean and you are on the correct branch | `git status`                                   | `On branch main` (or another branch) + `working tree clean` = ready. “Changes not staged…” indicates uncommitted changes. |
|    1 | List local branches and identify the current branch                    | `git branch`                                   | The current branch is marked with `*` (for example, `* main`).                                                            |
|    2 | Create a new branch for the task and switch to it                      | `git switch -c docs/contributing`              | Git switches to the new branch. To verify, `git status` should show `On branch docs/contributing`.                        |
|    3 | Stage the required file(s)                                             | `git add docs/CONTRIBUTING.md`                 | The file then appears under `Changes to be committed` in `git status`.                                                    |
|    4 | Create a commit with the correct message                               | `git commit -m "docs: add contributing guide"` | Git creates a commit and reports how many files changed.                                                                  |
|    5 | Push the branch to GitHub and set its upstream                         | `git push -u origin docs/contributing`         | The branch appears on GitHub. With `-u`, subsequent pushes can use just `git push`.                                       |
|    6 | Open a PR on GitHub and merge it into `main`                           | _(in the browser)_ PR → **Squash and merge**   | After the merge, the changes are in `main`. You can usually delete the branch with the “Delete branch” button.            |
|    7 | Update local `main` after merging the PR                               | `git switch main` + `git pull`                 | Local `main` receives the changes merged through the PR.                                                                  |
|    8 | List remote branches (origin)                                          | `git branch -r`                                | Lists branches on the server, such as `origin/main` and `origin/docs/contributing`.                                       |
|    9 | List all branches (local + remote)                                     | `git branch -a`                                | Shows the complete list: local branches + `remotes/origin/...`.                                                           |
|   10 | (Optional) Delete the local branch after the merge                     | `git branch -d docs/contributing`              | Deletes the local branch if it has already been merged. If Git refuses, the branch has not been merged.                   |

Short sequence for each task: status → switch -c → add → commit → push → PR → switch main → pull

## Workflow

### Tech Lead (merges into main)

**Start work and create a new branch**

```
git switch main
git pull --ff-only
git switch -c feat/8-iteration-0-frame_and_launch
```

Or switch to another branch:

```
git switch feat/44-it10-guardrails-v0
git fetch origin
git rebase origin/main
```

**Commit + push**

```
git add .
git commit -m "feat: iteration 0 fame and launch"
git push -u origin feat/8-iteration-0-frame_and_launch
```

**Create a PR for contributor review**

1. Go to the pull requests section on GitHub, find `feat/8-iteration-0-frame_and_launch`, and click `Compare & pull request`.
2. Enter `Fixes #8` (the Issue number to close) in `Add a description` and click `Create pull request`.
3. Select `Squash and merge` → `Confirm squash and merge` to merge into `main`.

Rule:

- only the Tech Lead performs `Squash and merge`, after reviewing the PR;
- contributors do not merge their own PRs.

4. Click `Delete branch`.
5. After the merge, update local `main`:

```
git switch main
git pull --ff-only
```

4. Delete the local branch:

```
git branch -d feat/8-iteration-0-frame_and_launch
```

Or delete the branch on origin:

```
git push origin --delete feat/8-iteration-0-frame_and_launch
```

And prune local references:

```
git fetch -p
```

5. Publish a new version of `beeui` as an installable package:

```
uv build
uv publish
```

### Reviewing a contributor's PR

**Create a separate directory for the PR, starting from the main project directory**

```
git fetch origin
git worktree add -b review/pr141 ../beeui-pr141 origin/feat/137-local_env_and_auth_diagnostics
cd ../beeui-pr141
code .
git status
git branch
```

**See which files the contributor changed relative to origin/main**

```
git fetch origin
git diff --name-only origin/main...HEAD
```

Or see what the contributor changed in a specific file:

```
git diff origin/main...HEAD -- config/start.py
```

**Use `git restore` only for files unrelated to the current task**

```
git restore uv.lock docs/AUTH_LOGS.md
git status
```

**Rebase the contributor's branch onto the latest `origin/main`, first ensuring that the working tree is clean**

```
git status
```

If there are `Changes not staged / Changes to be committed`, commit them and rebase:

```
git add .
git commit -m 'ci(docs): adjust docs workflow for private repo'
git fetch origin
git rebase origin/main
```

If `git status` shows no changes:

```
git fetch origin
git rebase origin/main
```

**If there are no errors**

```
uv run pytest -q
```

**Push the changes to the contributor's branch**

```
git push --force-with-lease origin HEAD:feat/137-local_env_and_auth_diagnostics
```

**If everything looks good**

- update the PR description;
- check the Files changed tab;
- perform Squash and merge;
- delete the branch on GitHub;
- update local main.

**From the main repository directory, remove the worktree and branch, then update main**

```
cd ../beeui
git worktree remove ../beeui-pr141
git branch -D review/pr141
git switch main
git pull --ff-only
```

### Contributor (creates PRs)

**Before starting a task**

```
git switch main
git pull --ff-only
git switch -c feat/<short-title>
```

**Commit + push + PR**

```
git add .
git commit -m "feat: <short>"
git push -u origin feat/<short-title>
```

In the PR:

- use Refs #<issue> while the PR is under review;
- do not merge it yourself;
- do not click Squash and merge;
- after feedback from the Tech Lead, push updates to the same PR branch.

**If new changes are merged into main while the contributor is working**

```
git fetch origin
git rebase origin/main
git push --force-with-lease
```

**After the PR is merged**

```
git switch main
git pull --ff-only
```

## Issues and Kanban

Create an Issue for every task and idea (rather than a separate card in a Project). The Project (Kanban) displays Issue status.

Rule:

1. Create an Issue (task = Issue).
2. Create a branch for the Issue.
3. Open a PR targeting main.
4. In the PR description, use:

- `Refs #123` — while the PR is in progress or under review;
- `Fixes #123` / `Closes #123` — when the PR is approved for merge.

Important:

- `Fixes/Closes` in a PR **does not close** the Issue when the PR is created;
- the Issue closes **only after the PR is merged into `main`**;
- for a contributor's PR, use `Refs #123` by default; the Tech Lead changes it to `Closes #123` before merging.

Labels:

- prio:high/medium/low
- (optional) bug/enhancement/doc/idea

Use:

- `Feature: <short title>` — new functionality
- `Fix: <short title>` — a bug fix
- `Bug: <short title>` — a bug report (not necessarily being fixed immediately)
- `Docs: <short title>` — documentation
- `Chore: <short title>` — maintenance/infrastructure/refactoring without new features
- `Idea: <short title>` — an idea/outline (can later become a Feature/Fix)

**Examples:**

- `Feature: add risk profiles (conservative/normal/aggressive)`
- `Fix: prevent crash on empty candles`
- `Bug: wrong PnL calculation on partial fills`
- `Docs: explain config keys and examples`
- `Chore: add pre-commit formatting`
- `Idea: capital allocation per strategy`

## Commits

Format: <type>(<scope>)!: <short description of the change>

scope is optional (for example: api, parser, docs, ci). ! indicates a breaking change (MAJOR).

Commit types (KISS):

| Type      | When to use                                              | Version impact |
| --------- | -------------------------------------------------------- | -------------- |
| feat:     | new functionality                                        | +MINOR         |
| fix:      | a bug fix                                                | +PATCH         |
| docs:     | documentation-only changes                               | none           |
| refactor: | refactoring without behavior changes                     | none           |
| test:     | tests                                                    | none           |
| chore:    | maintenance (dependencies, configuration, minor changes) | none           |
| ci:       | GitHub Actions / CI/CD                                   | none           |
| build:    | builds/packages/Docker/release tooling                   | none           |

MAJOR (breaking changes):

- feat!: ... or fix!: ...
- or a commit footer: BREAKING CHANGE: ...

Examples:

- `feat(core): add module contract v0`
- `feat(registry): add local module loading`
- `fix(settings): validate module config fail-fast`
- `docs(roadmap): update stage 3 module platform`
- `test(core): add artifact api smoke coverage`

MINOR: feat(api): add a search endpoint

PATCH: fix(parser): handle empty input without crashing

NO VERSION: docs: update README chore: add basic templates refactor(parser): simplify parsing without changing behavior

MAJOR (breaking): feat!: change the configuration format

BREAKING CHANGE: settings.yml keys have been renamed; update the configuration
