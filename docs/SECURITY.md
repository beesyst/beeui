# Security — BeeUI

## Purpose

This document defines permanent security requirements for BeeUI's web surface, product adapters, operator actions, session controls, artifact presentation and package-local assets. It is a normative engineering policy, not a changelog, security certification or substitute for product authorization.

Use [SDLC.md](SDLC.md) for risk classification, [ARCHITECTURE.md](ARCHITECTURE.md) for ownership, and the owning component/API documentation for exact schema details.

## Security boundary

**BeeUI renders. The product decides.** BeeUI protects its transport and presentation layer; it must not independently authorize a product scan, financial transaction, provider call, capability invocation, credential access or Case transition.

Product adapters provide bounded read-models, resource allowlists, product decisions and explicit callbacks. Neither valid UI metadata nor a browser role is proof of domain authority.

### Threat model

Assume all of the following are untrusted until validated: browser requests and query parameters; cookies and client state; product adapter responses; strings used in HTML; restored run/Case records; artifact identifiers and contents; route prefixes; imported/configured page metadata; third-party assets; and external service or AI-generated text.

Protect session integrity, secrets, role boundaries, product artifacts and evidence, private report contents, file paths, approved action scope, audit trails and package supply chain.

## Required controls

### Authentication, sessions and CSRF

- Authentication may be disabled explicitly for local/demo use; do not treat that development setting as a safe production default.
- With auth enabled, protected POST operations require a valid authenticated session, the specified role and CSRF validation **before** calling the adapter.
- The supported roles are `viewer`, `operator` and `admin`; product-specific scopes and ownership must be enforced by the embedding host independently.
- Session secrets and role tokens must come from approved runtime secret sources, not source code, example files, public UI data or logs.
- Apply the centralized cookie policy. `SameSite=None` requires a Secure cookie; configure `cookie_secure` appropriately for HTTPS deployment. Use the validated session lifetime limits.
- `AuthService.create_principal_session(user_id, role)` is a server-side trusted principal issuance interface. Never let a browser-supplied role select or elevate its own authority.
- A UI visibility filter hides presentation links; it is not a replacement for protected routes and resource checks.

### Read-only and bounded write behavior

- Ordinary GET routes, tab navigation, artifact previews, filters and polling must not mutate product state or initiate external target/provider execution.
- Mutating actions use explicit, feature-gated POST routes and product-owned callbacks. No action may be synthesized from a user-supplied URL, arbitrary JS or an unbounded form.
- Revalidate inputs, current product authorization, resource ownership, freshness and concurrency at execution time. A preview or disabled button is not permission.
- For bounded actions, verify the action ID, fields, arguments, confirmation flow and role/CSRF. Audit accepted and refused mutations in the product's owning system.
- Do not expose a general arbitrary YAML editor, raw configuration file manager or shell executor through generic BeeUI components.

### HTML, JavaScript and external inputs

- Keep Jinja2 HTML autoescaping active. Do not render untrusted `|safe`, arbitrary markup, data URLs, scripts, classes, CSS declarations or uncontrolled asset locations.
- Normalize adapter-provided strings, numbers, collections, lengths and selection values before passing them to templates or browser scripts.
- Use fixed Tabler/icon/style allowlists; treat unsupported optional component metadata as degraded or omitted, as the public contract specifies.
- Use `textContent` or equivalent safe DOM construction for live updates. Never interpolate product text into executable scripts or `innerHTML`.
- Validate all internal links and response URLs; refuse external, protocol-relative, traversal and malformed paths. Preserve the embedded mount prefix without bypassing validation.
- Keep browser requests same-origin, bounded, abortable and protected against stale UI updates. Progressively enhanced navigation must fall back to canonical GET.
- Render missing evidence as unavailable rather than fabricating a number or success state.

### Files, artifacts and privacy

- A URL `artifact_id` is an opaque identifier, not a filesystem pathname. Product adapters decide whether the requester may list/read it.
- Reject traversal, absolute paths, symlink escapes and unlisted artifact references; verify IDs and prefixes before filesystem access.
- Cap preview bytes, rows, characters and nested structures; use metadata-only fallback for unsupported or oversized binary data.
- Apply structured and unstructured secret redaction before rendering; render preview text escaped.
- Do not silently rewrite corrupt artifacts or leak parser exceptions, raw product evidence, credentials or private payloads in errors and logs.
- Review multi-principal resource isolation and repeat-read immutability when adding Case/run views or live polling.

### Configuration and framing

- Validate required runtime and UI config fail-fast; treat optional product payloads as untrusted presentation inputs.
- Reject arbitrary secret edits, hidden authority toggles, unreviewed external asset URLs or product policy from UI settings.
- Default framing is denied. If embedding is explicitly required, validate `security.frame_ancestors` as exact HTTP(S) origins with no wildcard/path/query/fragment and apply the documented CSP framing policy.
- Locale and theme preferences are not security claims. Locale is selected from the configured allowlist; theme state is allowlisted and affects presentation only.

### Dependencies and third-party assets

- Serve Tabler CSS/JS, icons, chart/date widgets and other runtime assets from the installed BeeUI package. Never embed upstream preview tracking, PostHog, remote demo scripts or unmanaged CDNs.
- Preserve applicable licenses/provenance for vendored assets; test package contents and installed-wheel rendering after asset changes.
- Keep `docs/vendor/tabler/` documentation synchronization separate from runtime asset upgrades. A new upstream guide does not prove that the installed Tabler version supports its example.
- Pin/review actual dependencies and lock changes when a dependency change is approved; apply supply-chain checks proportional to the new risk.

## Risk-based verification

| Check                      | Use when                                                             | Representative evidence                                                                           |
| -------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Static review / SAST**   | Changes expose data, auth, JS/HTML, callbacks or file access         | Injection, path handling, secret exposure, unsafe interpolation and prohibited actions.           |
| **SCA**                    | Dependencies or third-party assets change                            | Exact package/version/license review, vulnerability/advisory evaluation and lock reproducibility. |
| **DAST / web integration** | HTTP behavior, auth or protected routes change                       | Session, CSRF, role refusal, malformed requests, browser/route checks.                            |
| **Fuzzing/property tests** | A parser or bounded normalizer has a complex untrusted-input grammar | Oversized/deep/malformed cases and controlled degradation.                                        |
| **IAST**                   | An instrumented application and meaningful threat case justify it    | Verified runtime taint or execution evidence; not a universal PR prerequisite.                    |

Security-sensitive changes require full relevant regression and concrete denial tests, not merely an assertion that the template uses escaping. If a check is not applicable, say why; never claim a check was executed when it was not.

## Vulnerability handling and release gate

Report discovered vulnerabilities privately through the repository's approved security-reporting channel or maintainer process; do not publish credentials or exploitable private targets in Issues/PRs. Contain and fix exploitable findings in the responsible branch, verify negative cases, and avoid weakening an existing policy to make a demo pass.

Do not merge a change that expands an unintended execution authority, leaks secrets/evidence, bypasses ownership or CSRF, introduces raw HTML/JS, performs hidden writes on GET, or ships a broken dependency/runtime bundle.

## Policy maintenance

Keep these standing controls stable. Put detailed block fields in [COMPONENTS.md](COMPONENTS.md), HTTP contracts in [API_CONTRACT.md](API_CONTRACT.md), route behavior in [WEB_UI.md](WEB_UI.md) and execution-domain policies in the product's own documentation. Update this file only when the security boundary or requirements actually change.
