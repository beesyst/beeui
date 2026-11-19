# COMPONENTS — BeeUI

## Purpose

BeeUI provides generic, product-neutral Tabler presentation blocks. Products send normalized read-models through `ProductUiAdapter`; BeeUI validates and renders them without importing product rules. This document describes supported contracts rather than the chronological history of iterations.

**Do not copy upstream Tabler preview HTML or scripts into a product.** Reuse BeeUI blocks, shared Jinja primitives and package-local assets. The upstream reference snapshot is `docs/vendor/tabler/`, while runtime assets are installed under `src/beeui_module/web/static/vendor/`.

## Two presentation surfaces

- **Configured/demo pages:** declarative blocks sourced from `config/schema.yml` or configured page definitions.
- **Adapter-backed product pages:** a product returns `layout[]` with typed blocks. This is the surface for advanced data tables, charts, the chat workspace and product-specific read-models.

The two systems are not interchangeable schemas. Do not assume an adapter-only block can be introduced as a schema block without its own reviewed contract.

## Generic layout blocks

| `type`                                           | Purpose                                                                            |
| ------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `hero_snapshot`                                  | Summary card with status, values and internal links.                               |
| `metric_card`                                    | Single stat with optional status, hint, safe href and icon.                        |
| `kpi_strip`, `kpi_grid`                          | Bounded responsive KPI groups.                                                     |
| `operator_hero`                                  | High-level operator summary with controlled local illustration and trend metadata. |
| `venue_summary_grid`, `venue_card`, `mode_cards` | Product-neutral summary presentation patterns.                                     |
| `state_grid`                                     | Dense key/value state presentation.                                                |
| `quick_links`, `artifact_links`                  | Safe internal operator and artifact navigation.                                    |
| `run_table`, `status_table`, `event_table`       | Bounded generic tabular summaries.                                                 |
| `attention_list`                                 | Bounded severity-marked event/attention entries.                                   |
| `raw_json_panel`                                 | Escaped JSON presentation; never an editable object.                               |
| `chart`, `leaderboard`                           | Visual summaries from validated numeric/list input.                                |
| `data_table`                                     | Searchable/sortable/paginated advanced table with optional bounded actions.        |
| `filter_form`                                    | Product-owned GET filters using validated field types.                             |
| `group`                                          | Bounded nesting of layout blocks, currently vertical.                              |
| `chat_workspace`                                 | Bounded Case/conversation/history/context/composer presentation.                   |
| `degraded`                                       | Explicit safe fallback for malformed or unsupported block content.                 |

### Placement and size

`width`, `span` and `size` are mutually exclusive. `width`/`span` use integer grid spans 1–12; `size` is one of `S`, `M`, `L`, `XL` and maps to a fixed responsive class. Invalid adapter-backed sizing falls back to full width. Do not pass class names supplied by products into templates.

`kpi_grid.columns` supports 1, 2, 3 or 4 columns, defaulting to four for missing/invalid adapter data. `group` uses a bounded recursion depth of three. Broken optional blocks degrade rather than throwing server errors.

### Metric cards and icons

A `metric_card` uses `title`, `value` and optional status/hint. Optional `href` must be internal and validated. Optional `icon` uses a safe canonical Tabler icon name; `icon_tone` uses a fixed allowlist with safe fallback. Existing cards without `href` remain non-clickable. Product-owned data never supplies raw SVG/HTML or CSS.

## Charts and leaderboard

`chart` accepts an optional `title`, `subtitle`, `kind`, `height`, `series`, `categories`, `labels`, `unit`, `status`, `hint` and empty-state message. Implemented kinds are `line`, `bar`, `area`, `donut` and `funnel`; unsupported/malformed kinds degrade safely.

- All series and numeric coordinates are bounded and checked for finite values.
- Product adapters cannot pass arbitrary ApexCharts configuration or arbitrary colors/classes.
- Chart options are normalized and encoded as JSON for the browser; the chart asset is package-local and loaded only when necessary.
- Missing data produces an honest empty/degraded state, not a fabricated chart or HTTP 500.
- Charts nested in `group.children` are detected through the existing layout lifecycle.

`leaderboard` takes bounded ranked `items[]` with rank, escaped label, initials-only avatar, allowlisted tones, finite progress clamped to 0–100, values and optional metadata. Invalid entries are omitted. No arbitrary image URLs or CSS are accepted.

## Advanced `data_table`

A product-supplied `data_table` has `type`, required `title`, `columns[]`, `rows[]`, and optional `id`, `description`, `toolbar`, `pagination`, `variant`, `striped`, `mobile`, `selectable`, `nowrap`, `compact`, and standard sizing.

The table delegates canonical rendering to `components/primitives/canonical_table.html`. Recognized cell kinds include `text`, `muted`, `link`, `badge`, `status`, `avatar_text`, `progress`, `actions` and `toggle`. Unknown cell types degrade to escaped text; missing values display as `n/a`; unsafe links are omitted. Malformed columns/rows retain an explicit degraded table/card state, rather than crashing.

### Toolbar and GET filters

`toolbar` may contain an optional GET form and controls: `search`, `entries`, `fields[]`, `hidden`, `column_toggles[]`, `actions[]`, `apply`, `reset`. Supported functional filter field families include `text`, `select`, `checkboxes` and `date_range` (through locally packaged Litepicker when needed).

- The product owns query semantics, filtering, sorting, pagination and counts.
- An Apply action is shown only when explicitly declared; adding a date range does not invent an Apply action.
- Sort links, reset, filters, pagination and column toggles use validated internal hrefs and preserve mount prefixes.
- A safe stable table `id` enables optional same-origin progressive GET replacement. Without JS or on failure, ordinary URL/form navigation still works.
- Progressive search with an identified table debounces trimmed search strings of three or more characters, suppresses stale requests and updates URL history on successful replacement. Product-owned direct GET behavior for shorter queries remains independent.
- Functional GET forms disable browser autocomplete; no DataTables/List.js runtime is introduced.

### Pagination

`pagination.pages[]` uses validated internal hrefs with a display label and optional positive page number. The renderer collapses large page lists to a bounded neighborhood with first/current/last and ellipses. Duplicate/unsafe pages are omitted. Optional previous/next and `pagination.page_size` use safe product-supplied links/values; BeeUI does not invent page sizes.

### Bounded actions

`toolbar.actions[]` and `actions` cells may contain safe navigation `href` items or explicit product action metadata (`action_id`, escaped label/description, bounded string `args`, optional confirmation and typed fields).

Supported bounded action fields are `text`, `email`, `number`, `select`, `checkbox`, `radio` and `password`. Password fields are always initialized empty; never render supplied secrets. Optional inline editing and the guarded `pending_action_id` presentation use the existing action transport, not a new endpoint.

The default action flow is `preview_confirm_execute`: protected preview, separate confirmation, then protected execute. An explicit `direct_execute` action may use the same protected execute route for a bounded toolbar form or inline edit. Products may provide strictly validated `follow_up_action_id`/`follow_up_match_arg` behavior using only previously rendered permitted actions. A confirmation dialog is not authorization: the host must recheck role/CSRF/ownership/policy and audit the action.

## `filter_form`

`filter_form` is a standalone generic GET filter block supporting bounded `text`, `select`, `checkboxes` and `date_range` controls, hidden query arguments, safe Apply/Reset URLs, optional column-toggle behavior and the same link/path validation as tables. It does not perform product-side filtering and cannot execute a POST action.

## Generic detail page

`render_beeui_detail_page()` consumes a normalized page model with an optional safe `back_href`, title, subtitle, warnings and sections. Section kinds are `key_value`, `text`, `table` and `links`. Text is escaped; unsupported sections are omitted/degraded, and unsafe internal links are rejected. See [API_CONTRACT.md](API_CONTRACT.md) for the model and [WEB_UI.md](WEB_UI.md) for rendering behavior.

## Page tabs and shared primitives

Product configuration supports URL-driven tabs with `variant: fill_icons`, `active_param`, optional `surface: separated` and `progressive: true`. Progressive fetch replaces the matching tab surface, cancels stale requests, supports Back/Forward and falls back to canonical GET. It does not introduce a client-side product router.

Generic primitives include Tabler cards, icons, lists, dropdowns, forms, responsive tables, badges, status indicators, dates and modal/confirmation surfaces. Use the shared primitives in `src/beeui_module/web/templates/components/primitives/` rather than copy-pasting demo templates.

## `chat_workspace`

The adapter-only `chat_workspace` displays bounded conversation history, escaped factual messages, optional read-only Case context, a persistent product-controlled composer and optional same-origin polling. It creates neither a message database nor a chat/LLM runtime.

### Base shape

```json
{
  "type": "chat_workspace",
  "id": "investigation",
  "title": "New case",
  "new_href": "/cases",
  "history": [],
  "messages": [],
  "composer": {
    "action_id": "start_investigation",
    "label": "Start",
    "disabled": true,
    "fields": [
      {
        "name": "task",
        "type": "textarea",
        "label": "Task",
        "max_length": 1024
      }
    ]
  }
}
```

`disabled: true` is shown deliberately. Only an explicit `disabled: false` can enable presentation of the submit control; actual execution still requires protected host authorization.

### History and messages

- `history`: at most 25 unique entries containing bounded `id`, `title`, internal `href`, optional `active`, `status` and up to two bounded protected `actions`. History actions use the contextual composer-action schema and render in a Tabler ellipsis dropdown as a sibling of the title link; buttons are never nested in links. The product owns ownership, freshness, rename, archival and evidence semantics.
- `messages`: at most 100 unique entries with `id`, `sender` (`operator`, `host`, `assistant`), bounded `name`, plaintext `text`, optional valid ISO timestamp and status.
- Each message may contain up to three protected `actions` using the existing contextual composer-action contract. Initial HTML and polling render the same buttons through the existing protected action handler; an action with no fields submits with one click, while fields use the existing form. The product still validates ownership, authority, source, nonce and revision on POST. Optional escaped `details` (4096 characters) and product-localized `details_label` provide an expandable technical view; text plus details share the 32768-character message collection limit. Optional `links` contain up to eight `{label, href}` read-only internal navigation links, with the same validation and embedded-prefix handling as other component links. These links never trigger product actions. Stable message IDs preserve expanded details across polling updates.
- Message IDs are at most 128 characters; name up to 256; message text up to 4096, combined message text up to 32768 characters. Live updates use safe text insertion and stable identities.
- `message_style`: optional `standard` (default, compatible author/status/ISO presentation) or `conversation` (author and status badges omitted, ISO timestamps displayed with `Intl.DateTimeFormat` in the browser locale/timezone). Original timestamp data remains unchanged and DOM insertion stays escaped.
- `errors`: optional mapping of up to 16 bounded error-code identifiers to escaped localized messages of at most 512 characters; contextual action failures select only an explicit matching code, otherwise the existing generic failure label. Product exception bodies are not displayed.
- `history_notice`: optional escaped 1024-character notice for empty/filter states.
- `search`: optional GET `{href, name, value?, hidden?}`, with up to 128 characters of text and at most four bounded hidden entries. Tabs preserve bounded search and selected Case/run query state through canonical URLs.

### Read-only context

`context` accepts `{title, sections}` with up to eight unique sections. Each section has `{id, title, items, inline?}` with unique items `{id, label, value, detail?, href?, focus_primary?, tone?}`. Optional boolean `inline` groups items on a wrapping row. Simple items can use an optional `tone` (`secondary`, `blue`, `green`, `yellow` or `red`) to add a decorative status dot beside their text. Optional `href` is a validated bounded internal link with mount-prefix resolution; it never supplies action authority. Normalization defaults `detail` to an empty string, and products must use the same shape for initial context and live projections. A missing optional context DOM is ignored safely during live updates. There are at most 128 items total, at most 64 per section and a combined text budget of 32768 characters. Detail disclosures are escaped and preserve expansion state on polling. A context item with `focus_primary: true` uses its value as a button label and cannot include a link or detail. The button is shown when the existing primary composer control is enabled. It switches to the conversation panel and focuses the primary button without invoking it. Context does not grant execution or arbitrary links.

### Composer

`composer` supports `action_id`, `label`, `disabled`, `hint`, `args`, `fields`, optional `navigate`, `redirect`, `confirmation`, `settings_label`, `variant`, `submit_on_enter` and `menu`.

- Up to 10 bounded, named string args; up to eight uniquely named fields. A field name cannot override an existing arg.
- Field kinds: `text`, `url`, `textarea`, `select`, `target`, `segmented`, `secret`. Fields carry a validated name, label, bounded value, length 1–4096, `required`/`readonly` and `placement` (`inline`/`settings`).
- Contextual non-secret fields may opt into `inherit: true` to initialize from a same-named non-secret main composer control; this is presentation-only and the host revalidates submitted values. Secret inputs cannot inherit values.
- Main composer `select` fields may use `widget: dropdown` for a canonical Tabler menu with bounded options, keyboard/touch controls and selected-state feedback; `widget: native` is the compatible default. Selection still submits one named field and does not authorize execution.
- `select`/`segmented` provide 1–20 `{value,label}` options with a matching selected value; segmented selection uses native radio inputs.
- `variant: compact` renders one rounded message container with a bounded auto-growing textarea and an internal bottom toolbar: menu left, optional selections and upward-arrow Send right; visible labels for these toolbar selections remain available to assistive technology; `form` retains the existing conventional composer form.
- `target` is a neutral-icon text input, optionally with up to four allowlisted `protocols`, boolean `origin_only` and an escaped `invalid_message`. Browser target feedback is not product authorization and does not expand supported target types.
- `submit_on_enter: true` opts into textarea Enter submission; Shift+Enter inserts a newline, and IME composition is protected. The accessible icon-only submit remains available for pointer/touch use.
- `menu: {label, items}` retains one to six legacy string labels as disabled items. Interactive entries use `{id, label, kind, action}` with unique validated IDs and `kind: form`, `action` or `file`. Each action uses the bounded composer action shape (`action_id`, `args`, `fields`, `label`, `disabled`, optional `navigate`, `redirect` and escaped `confirmation`); nested controls are omitted. `action` and `file` entries have no fields. The interactive `+` trigger sits at the bottom-left inside the compact composer. Contextual forms open in a canonical Tabler modal with focus trapping, Escape/cancel and write-only secret cleanup; they do not expand the composer. A product may enable actions before a conversation exists, and owns any first-mutation creation semantics.
- `chips` accepts at most 32 unique `{id, label, edit?, remove?}` entries. Edit/remove use the same protected action shape. The product returns replacement chips after successful mutations; the renderer never mutates product state itself.
- Optional `primary` remains compatible and uses the same action shape to open a contextual modal. Mode selection can use select/segmented composer fields or a contextual action field.
- `secret` fields always normalize to an empty value, render as password inputs and clear after submission or cancellation. They are excluded from retained presentation state; adapters must never supply secrets through args, messages or error text.
- File actions open native file selection and POST multipart only to the fixed same-origin `/api/actions/upload` transport. An adapter must explicitly register that action ID through `upload_actions`; no adapter-provided upload URL is accepted.
- The complete normalized workspace has a 128 KiB serialized bound.
- `redirect` is an optional validated internal destination for successful protected actions without a returned identity; `confirmation` is optional escaped dialog text (maximum 1024 characters), with no implicit execution.
- `navigate: {href, param, result_key}` appends one validated result identifier to an internal destination after a successful protected action. No untrusted returned action URL is opened.

### Execution cards and Inspector

A message may use `kind: execution` with the existing stable message `id`, nonempty `name` and `status`, an optional extended ISO date or timestamp such as `2026-11-19T09:00:00+05:00`, and an `execution` object. The object accepts `tone` (`secondary`, `blue`, `green`, `yellow` or `red`), separate `outcome` text (160 characters), `duration_ms` (nonnegative integer through 10¹²), up to eight `metrics` rows (`label` and `value`, 80 characters each), and an optional internal `inspector_href`. Ordinary text messages retain the existing contract. Repeated tools need a distinct message ID for every execution in adapter order. The whole card opens its Inspector when a route is available. Execution status and any distinct outcome are available in a Tabler tooltip and the card’s accessible name. A separate `kind: result` message uses a `result` object with a required internal `href` to open details. It accepts the same display attributes and has no `progress` or `inspector_href`.

`progress` is optional. With a known `total`, provide an integer `completed` from zero through `total` and a positive integer `total` through 10⁹. A null or absent total inside an explicit progress object renders indeterminate progress. Omit the progress object if there is no progress to display. A request budget is a ceiling and should remain a metric unless it is also the actual amount of work.

The shared Inspector opens a same-origin GET on demand, rejects redirects, and verifies the returned `data.id` against the triggering message. Its response uses `{ok: true, data: {id, sections, checks_table?}}`. An optional `checks_table` object has one to six string `columns` and one to sixteen `rows` of the same width. Headers are nonempty and every header or cell is plain text of up to 128 characters. The table is absent when omitted. Section keys are `overview`, `checks`, `events`, `logs`, `technical` and `connections`. Each section accepts up to 32 `{label, value, href?}` rows, with labels through 128 characters and values through 1024 characters, at most 100 rows and 32,768 text characters across all sections. Omitted or empty sections are displayed as unavailable. An empty log section explicitly says no log entries are available. A row may mark an ISO timestamp with `format: timestamp`. Log rows may supply `level` as `INFO`, `WARNING` or `ERROR`. In the collapsed technical and connection sections only, `copy: true` enables copying a row without a link. Links must be internal and are resolved under the embedded prefix. Products own authorization and disclosure for the endpoint and must supply sanitized text. The dialog never interprets HTML or Markdown.

The desktop history control hides the history column and retains that preference for the browser tab. On mobile, history opens in a Tabler offcanvas. Neither control replaces the composer or restarts polling.

### Polling

Optional `refresh` contains a safe internal `href`, interval 1000–30000 ms (default 3000) and attempt bound 1–300 (default 300). The browser fetches only same-origin, bounded, non-redirecting read responses; pauses when hidden; stops after repeated failures; aborts on page disposal. Its normalized product payload is `data.presentation = {state, messages, values, complete, context?}`.

`values` is a bounded list of at most 12 `{id,value}` updates for already-rendered metric cards. Live messages and context use the same limits as initial render. `complete: true` reloads the canonical page to re-evaluate final state and permitted product actions. A non-secret message draft is kept in memory while a canonical GET replaces the matching chat or tab surface and refreshes action arguments; it is never stored in browser storage. An open contextual form or Inspector defers replacement until it is closed. Secret fields are not copied into the replacement. A read-only status GET never sends a target request.

### Security and ownership

Every displayed string is escaped or assigned as DOM text. Internal links, IDs, payload sizes and polling are bounded. The framework owns only session/role/CSRF transport, not the meanings of Target, Scope, Task, findings, AI usage, costs or current approval. The product adapter must return truthful states and reauthorize all submitted actions.

## Compatibility and tests

- Keep schema/demo blocks and earlier adapter block shapes compatible unless a reviewed breaking change is approved.
- Keep responsive layouts, RU/EN localization and light/dark behavior consistent with the existing BeeUI shell.
- Verify malformed input, expired/foreign resource visibility, internal-link safety, read-only polling, exact action authorization, keyboard interaction and installed-wheel packaging where applicable.
- Maintain the generic/product-neutral boundary; ROP and BeeScan read-models remain in their own products.

See [INTEGRATION.md](INTEGRATION.md), [WEB_UI.md](WEB_UI.md), [API_CONTRACT.md](API_CONTRACT.md) and [SECURITY.md](SECURITY.md).
