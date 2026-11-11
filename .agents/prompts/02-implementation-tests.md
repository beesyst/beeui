# BeeUI implementation and test prompt preparation

Use only BeeMCP.

Read:

- `AGENTS.md`
- `.agents/skills/beeui-implement-issue/SKILL.md`
- `.agents/skills/beeui-verify-and-correct/SKILL.md`

## Primary target

- Project: `beeui`
- Worktree: `<TARGET_WORKTREE>`
- Expected branch: `<FEATURE_BRANCH>`
- Base branch: `main`
- Mode: `<MODE>`
- Roadmap context: `<ROADMAP_CONTEXT>`

## Planning context

```text
<PLANNING_CONTEXT_OR_NONE>
```

## Approved Issue

```text
<FULL_APPROVED_ISSUE>
```

## Additional projects

```text
<ADDITIONAL_PROJECTS_OR_NONE>
```

Verify the exact target, branch, Issue, repository ownership boundaries, and applicable skills.

Do not implement the task, modify files, or run commands.

Prepare exactly two concise, ready-to-use prompts:

1. `Copilot implementation`
   - implement the Scope and meet the Acceptance Criteria;
   - run the required checks for the actual change level;
   - provide a complete implementation and verification report.

2. `Codex verification and correction`
   - independently verify the actual state of the target worktree;
   - verify all Acceptance Criteria without the first executor's report;
   - apply only necessary corrections within scope;
   - rerun the required checks;
   - provide a complete consolidated verification report.

Both prompts must:

- be independent and self-contained;
- require no data or report from the other executor;
- specify the exact worktree, branch, and base branch;
- reference `AGENTS.md` and the applicable skill;
- include the Issue source, if provided, and the same compact snapshot of the approved task contract: Summary, Scope, Excluded, Deliverable, Acceptance Criteria, Change level, required checks, and task-specific constraints;
- account only for task-specific constraints;
- account for additional repositories only in their declared roles;
- avoid duplicating standing repository rules;
- prohibit commits, pushes, PR operations, and merges;
- require neither BeeMCP, MCP Mode, nor read-only behavior from Copilot or Codex.

Return only the two ready-to-use executor prompts, without additional analysis.
