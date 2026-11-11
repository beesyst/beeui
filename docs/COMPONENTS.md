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

- `history`: at most 25 unique entries containing bounded `id`, `title`, internal `href`, optional `active` and `status`.
- `messages`: at most 100 unique entries with `id`, `sender` (`operator`, `host`, `assistant`), bounded `name`, plaintext `text`, optional valid ISO timestamp and status.
- Message IDs are at most 128 characters; name up to 256; message text up to 4096, combined message text up to 32768 characters. Live updates use safe text insertion and stable identities.
- `history_notice`: optional escaped 1024-character notice for empty/filter states.
- `search`: optional GET `{href, name, value?, hidden?}`, with up to 128 characters of text and at most four bounded hidden entries. Tabs preserve bounded search and selected Case/run query state through canonical URLs.

### Read-only context

`context` accepts `{title, sections}` with up to eight unique sections. Each section has `{id, title, items}` with unique items `{id, label, value, detail?}`. There are at most 128 items total, at most 64 per section and a combined text budget of 32768 characters. Detail disclosures are escaped and preserve expansion state on polling. Context does not grant execution or arbitrary links.

### Composer

`composer` supports `action_id`, `label`, `disabled`, `hint`, `args`, `fields`, optional `navigate`, `settings_label`, `variant`, `submit_on_enter` and `menu`.

- Up to 10 bounded, named string args; up to eight uniquely named fields. A field name cannot override an existing arg.
- Field kinds: `text`, `url`, `textarea`, `select`, `target`, `segmented`. Fields carry a validated name, label, bounded value, length 1–4096, `required`/`readonly` and `placement` (`inline`/`settings`).
- `select`/`segmented` provide 1–20 `{value,label}` options with a matching selected value; segmented selection uses native radio inputs.
- `variant: compact` renders Task/Target/radios/menu/send within one Tabler card footer; `form` retains the existing conventional composer form.
- `target` is a neutral-icon text input, optionally with up to four allowlisted `protocols`, boolean `origin_only` and an escaped `invalid_message`. Browser target feedback is not product authorization and does not expand supported target types.
- `submit_on_enter: true` opts into textarea Enter submission; Shift+Enter inserts a newline, and IME composition is protected. The accessible icon-only submit remains available for pointer/touch use.
- `menu: {label, items}` holds one to six bounded labels rendered **disabled only**. It provides no upload, import, export or hidden handler.
- `navigate: {href, param, result_key}` appends one validated result identifier to an internal destination after a successful protected action. No untrusted returned action URL is opened.

### Polling

Optional `refresh` contains a safe internal `href`, interval 1000–30000 ms (default 3000) and attempt bound 1–300 (default 300). The browser fetches only same-origin, bounded, non-redirecting read responses; pauses when hidden; stops after repeated failures; aborts on page disposal. Its normalized product payload is `data.presentation = {state, messages, values, complete, context?}`.

`values` is a bounded list of at most 12 `{id,value}` updates for already-rendered metric cards. Live messages and context use the same limits as initial render. `complete: true` reloads the canonical page to re-evaluate final state and permitted product actions. A read-only status GET never sends a target request.

### Security and ownership

Every displayed string is escaped or assigned as DOM text. Internal links, IDs, payload sizes and polling are bounded. The framework owns only session/role/CSRF transport, not the meanings of Target, Scope, Task, findings, AI usage, costs or current approval. The product adapter must return truthful states and reauthorize all submitted actions.

## Compatibility and tests

- Keep schema/demo blocks and earlier adapter block shapes compatible unless a reviewed breaking change is approved.
- Keep responsive layouts, RU/EN localization and light/dark behavior consistent with the existing BeeUI shell.
- Verify malformed input, expired/foreign resource visibility, internal-link safety, read-only polling, exact action authorization, keyboard interaction and installed-wheel packaging where applicable.
- Maintain the generic/product-neutral boundary; ROP and BeeScan read-models remain in their own products.

See [INTEGRATION.md](INTEGRATION.md), [WEB_UI.md](WEB_UI.md), [API_CONTRACT.md](API_CONTRACT.md) and [SECURITY.md](SECURITY.md).
