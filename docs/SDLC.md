# SDLC — BeeUI

## Purpose

BeeUI uses a lightweight, evidence-driven software development lifecycle. An approved Issue defines an actionable scope; a feature branch contains its implementation and corrections; tests and inspected runtime artifacts establish behavior; a PR records the verified result. [ROADMAP.md](ROADMAP.md) owns staged product increments, while [SECURITY.md](SECURITY.md) defines standing security requirements.

The objective is a working, reproducible, secure change with minimal process overhead.

## Principles

- **KISS, YAGNI, DRY.** Prefer existing product adapters, page tabs, blocks, Tabler primitives and contracts to new frameworks or alternative rendering paths.
- One iteration should deliver one meaningful end-to-end capability. Repair defects found during that iteration on the same branch before PR; do not create an iteration for each regression.
- BeeUI owns reusable presentation. Product-specific authorization, evidence, business rules and execution remain in the embedding product.
- Treat the code and tests as the current implementation; ROADMAP and historical PR text are planning/evidence, not proof that a capability exists.
- Distinguish observed results, simulations, assumptions and limitations. Do not claim successful hosted CI or external integration without evidence.
- Use the approved release workflow for version changes. Feature, fix and docs work does not require an ad hoc package version bump.
- Do not broaden an Issue merely because adjacent cleanup seems attractive.

## Workflow

```text
ROADMAP / observed problem / existing contract
  -> approved Issue (scope, acceptance, exclusions, risk)
  -> dedicated branch and implementation
  -> focused tests and proportional full regression
  -> genuine UI/API/packaging/security evidence
  -> independent final review
  -> PR and hosted CI
  -> merge
  -> release through the repository's release process
```

### Plan and implement

1. Read the Issue, current source, tests, relevant integration contracts and existing documentation.
2. Identify an actual user or operator outcome and its source of truth.
3. Select the smallest implementation that respects `ProductUiAdapter` and package-local Tabler boundaries.
4. Keep unrelated code and docs untouched; do not create placeholder functionality.
5. Preserve backward compatibility unless the approved Issue explicitly authorizes a change.
6. When two repositories must change, define ownership and verification in both; do not let a local editable dependency substitute for a release dependency in the final consumer PR.

### Verify

- Run targeted tests for the changed contract and negative cases.
- Run the full relevant pytest suite for runtime-risk and security-sensitive changes.
- For routes and UI behavior, verify real HTTP responses, state transitions and browser screenshots at relevant sizes/themes/locales.
- For CSS/JS/templates/assets, inspect the installed wheel, not just an editable source checkout.
- For artifact, action or auth changes, test malformed and adversarial inputs, privilege refusal, escaping and no-mutation behavior.
- Verify `git diff --check`, the changed-file inventory and the absence of accidental secrets or unrelated vendor changes.
- Record actual command results, failure cases and limitations in the PR.

### Review and deliver

1. Request the independent read-only final review required by the repository workflow.
2. Correct blocking findings within the current branch and rerun proportional checks.
3. Open a PR using `.github/PULL_REQUEST_TEMPLATE/pr.md`; link its approved Issue.
4. Wait for required hosted checks, reconcile substantive new findings, then merge.
5. Close the Issue/iteration only when the defined delivery and release dependency gates are satisfied.

## Change levels and verification

| Level                  | Typical changes                                                                                                     | Minimum evidence                                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Low-risk**           | Documentation, isolated tests, presentation text without changed contracts                                          | Focused checks, links/format review and changed-file scope.                                                           |
| **Runtime-risk**       | Adapter responses, blocks, page routing, table behavior, UI settings, static JS/CSS                                 | Focused and relevant full tests; HTTP and browser smoke; degraded states; wheel/assets where applicable.              |
| **Security-sensitive** | Auth/session/CSRF, protected actions, artifact/path handling, untrusted rendering, secrets, dependency supply chain | Runtime-risk checks plus explicit threat/negative tests, product authority validation, redaction and security review. |

Risk is determined by the actual changed boundary, not by the Issue label. SAST, SCA, DAST, IAST and fuzzing are applied when they address a concrete risk; do not report an unrun check as passed. For dependency changes, review declarations and lock changes together and perform applicable supply-chain checks.

## Configuration, dependencies and documentation

- Keep required configuration explicit and validated. Reject hidden authority defaults.
- `pyproject.toml` contains declared dependencies; `uv.lock` pins them for reproducibility. Do not regenerate/inspect the lockfile for an unrelated non-dependency task.
- Reuse package-local Tabler assets. A documentation snapshot refresh under `docs/vendor/tabler/` is a separate docs change from a runtime asset upgrade.
- Update the **owning** document for any public API, block, browser, integration, theme or security contract change; avoid copying the same normative content into multiple files.
- Keep documentation in English, except protected files explicitly excluded from a task. Do not silently replace a normative contract with a vague summary.

## Definition of Done

A change is done when the approved behavior works end to end, relevant negative cases refuse safely, tests match the actual risk, the public contract/documentation is accurate, the wheel serves the required assets, the final review has no blockers, and the PR has passed its required gates. A green unit test alone does not prove complete browser or product integration.

## Release

Releases follow the repository's configured Release Please workflow on `main`. Do not set arbitrary package versions in ordinary branches. Consumers must use the actual published distribution and a reproducible lockfile before their own release/merge gates; local editable paths are for coordinated development only.

For security policy see [SECURITY.md](SECURITY.md); for practical commands see [DEV_GUIDE.md](DEV_GUIDE.md).
