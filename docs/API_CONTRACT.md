# API CONTRACT — BeeUI

## Scope and sources of truth

This document defines the implemented HTTP response envelopes and presentation integration boundary. Exact adapter signatures are in `src/beeui_module/adapters/base.py`; route registration is in `src/beeui_module/web/app.py` and `src/beeui_module/pages/router.py`; typed layout blocks are documented in [COMPONENTS.md](COMPONENTS.md).

Do not confuse three different contracts:

1. **Product console read APIs** use the stable `beeui.v0` envelope.
2. **Artifact APIs** retain their earlier adapter-result envelope (`status`/`data`/`meta`), not `beeui.v0`.
3. **Adapter `layout[]`** is a Python presentation model, not a separate HTTP endpoint or a new configuration key.

Product-specific APIs mounted by the embedding application, including BeeAgent's BeeScan status and Case APIs, are owned by that product and are not part of the generic BeeUI API contract.

## Product console read response

A successful read-only response is:

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": {},
  "warnings": [],
  "meta": {}
}
```

A normalized adapter result with `status: partial` remains a successful response and records `meta.status: "partial"` rather than claiming completeness.

An error response is:

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "adapter_unavailable",
    "message": "Adapter is not available"
  },
  "warnings": [],
  "meta": {}
}
```

Representative stable error-to-HTTP mapping:

| Error                                                    | HTTP status |
| -------------------------------------------------------- | ----------- |
| `invalid_id`                                             | 400         |
| `permission_denied`, `forbidden`, `csrf_failed`          | 403         |
| `unauthenticated`, `authentication_failed`               | 401         |
| `not_found`                                              | 404         |
| `unavailable`, `adapter_unavailable`                     | 503         |
| Malformed adapter envelope or unexpected adapter failure | 502         |

Do not leak adapter traceback, runtime secrets or raw source artifacts in either `message` or `meta`. The exact protected-route error message may depend on the session/role state; its code and HTTP behavior remain authoritative.

## Implemented product console routes

| Method and path                                  | Ownership and behavior                                         |
| ------------------------------------------------ | -------------------------------------------------------------- |
| `GET /api/dashboard`                             | `adapter.get_dashboard()`; read-only `beeui.v0`.               |
| `GET /api/runs`                                  | `adapter.list_runs()`; read-only `beeui.v0`.                   |
| `GET /api/runs/{run_id}`                         | Validated ID; `adapter.get_run(run_id)`; read-only `beeui.v0`. |
| `GET /api/venues/{venue_id}/dashboard`           | Optional adapter venue dashboard; read-only `beeui.v0`.        |
| `GET /api/runs/{run_id}/artifacts`               | Allowlisted artifact references; distinct artifact envelope.   |
| `GET /api/runs/{run_id}/artifacts/{artifact_id}` | Bounded artifact preview; distinct artifact envelope.          |

The product console routes require an installed adapter; the demo/configured experience is not a substitute for product data. Browser HTML counterparts are documented in [WEB_UI.md](WEB_UI.md). All paths may be mounted beneath an approved route prefix.

Route/run/venue/artifact IDs are validated before the corresponding adapter invocation. GET must not modify product storage or initiate an external action.

## Artifact API envelope

Artifact APIs preserve their established response shape instead of adopting `beeui.v0`:

```json
{
  "status": "ok",
  "data": [
    { "artifact_id": "report_json", "content_type": "application/json" }
  ],
  "warnings": [],
  "meta": { "product": "example", "run_id": "run_001" }
}
```

An artifact preview can look like:

```json
{
  "status": "ok",
  "data": {
    "artifact_id": "report_json",
    "content_type": "application/json",
    "preview_type": "json",
    "preview_data": { "status": "ok" },
    "truncated": false,
    "row_count": null,
    "row_warnings": [],
    "error": null,
    "metadata_only": false
  },
  "warnings": [],
  "meta": { "product": "example", "run_id": "run_001" }
}
```

Supported preview families are JSON, JSONL and text. Unsupported/binary or oversized sources yield metadata-only states; malformed JSON/JSONL produces explicit errors or row warnings rather than a crash. The established limits include 512 KiB JSON/JSONL, 500 JSONL rows and 100,000 text characters, with source constants in `src/beeui_module/artifacts/preview.py`.

`artifact_id` is an opaque allowlisted key. The product adapter maps it to an authorized resource; no URL supplies an arbitrary filesystem path. Sensitive structured keys and unstructured preview text are redacted before escaped output.

## Authentication and protected actions

BeeUI's protected POST transport consists of:

| Route                       | Required role | Required feature flag       |
| --------------------------- | ------------- | --------------------------- |
| `POST /api/config/preview`  | `admin`       | `features.config_preview`   |
| `POST /api/config/apply`    | `admin`       | `features.config_apply`     |
| `POST /api/actions/preview` | `operator`    | `features.operator_actions` |
| `POST /api/actions/execute` | `operator`    | `features.operator_actions` |

With authentication enabled, a valid authenticated session and CSRF token are required for these routes. The role check precedes all product mutation callbacks. BeeUI validates transport, bounded shape and feature eligibility; product callbacks decide whether the action or config candidate is currently allowed and how it is audited.

`auth.enabled: false` is explicit local/dev mode and is not permission for a production product to bypass its domain policy. Product authority applies regardless of BeeUI's transport state.

An action is identified by an allowlisted `action_id` and bounded arguments/fields, **not** by a browser-provided arbitrary URL. A preview/confirmation UI never substitutes for server-side execution authorization.

## Adapter result envelopes

The public adapter protocol returns `AdapterResult` or `AdapterErrorResult` from `src/beeui_module/adapters/envelopes.py`. Do not return raw FastAPI `Response` objects, unhandled exceptions or direct HTML fragments as adapter data. Adapter errors are normalized, and optional unavailable operations must report unavailable explicitly.

Example Python usage:

```python
from beeui_module.adapters.envelopes import ok_result

# Returned by an implementation of ProductUiAdapter.get_page(...)
return ok_result({
    "layout": [
        {"type": "metric_card", "title": "Authorized cases", "value": "2", "width": 4}
    ]
})
```

This presentation result is not a new JSON HTTP endpoint. The page renderer validates the nested blocks before emitting HTML.

## Adapter-backed `layout[]` contract

Product read-models may include `layout` as a list of typed blocks:

```json
{
  "layout": [
    {
      "type": "metric_card",
      "title": "Cases",
      "value": "2",
      "width": 4
    },
    {
      "type": "quick_links",
      "title": "Navigation",
      "items": [{ "label": "Runs", "href": "/runs" }],
      "width": 8
    }
  ]
}
```

This is used on adapter-backed pages, not the schema/demo block definition in `config/schema.yml`. A nonempty valid `layout[]` is rendered through the normalized generic layout system; when no layout is provided the page may use its existing generic fallback. Invalid or optional block values degrade according to the owning block renderer; they must not grant execution rights.

Supported block types include `hero_snapshot`, `metric_card`, `kpi_strip`, `kpi_grid`, `venue_summary_grid`, `venue_card`, `mode_cards`, `operator_hero`, `state_grid`, `quick_links`, `run_table`, `status_table`, `event_table`, `attention_list`, `artifact_links`, `raw_json_panel`, `chart`, `leaderboard`, `group`, `data_table`, `filter_form` and `chat_workspace`. An explicit `degraded` view is used for rejected block content.

Sizing is mutually exclusive: one of `width`, `span` or `size` (`S/M/L/XL`). Valid widths/spans are 1 through 12, mapped through fixed responsive column classes. For adapter payloads, invalid sizing degrades to a full-width column; required schema/config sizing follows its own fail-fast validation. `kpi_grid.columns` supports 1–4, defaulting to four for absent/invalid adapter values. Group nesting has a bounded depth and does not permit arbitrary component recursion.

For exact fields of charts, tables, forms and chat, see [COMPONENTS.md](COMPONENTS.md). No adapter-provided CSS classes, raw ApexCharts options, scripts or external destinations are accepted.

## Generic detail page contract

`render_beeui_detail_page()` is a Python rendering entrypoint, not a JSON API route. Its normalized model is:

```json
{
  "page_id": "event_detail",
  "title": "Event detail",
  "subtitle": "Read-only event data",
  "back_href": "/events",
  "warnings": [],
  "sections": [
    {
      "kind": "key_value",
      "title": "Attributes",
      "items": [{ "label": "Status", "value": "ok" }]
    }
  ]
}
```

Implemented section kinds: `key_value`, `text`, `table`, `links`. Unsafe `back_href`/links are rejected, missing values display as unavailable, unsupported sections are omitted/degraded, and raw content fields are not automatically exposed. This rendering contract does not create a new config key or API endpoint.

## Compatibility and evolution

- Preserve `beeui.v0` for existing console GET APIs; do not silently replace the artifact API envelope.
- Keep public action field names, callback signatures and route-prefix behavior backward compatible until an approved breaking change.
- The optional chart/table/chat presentation extensions do not imply new product execution capabilities.
- Future config-editor, admin service or a distinct frontend API require explicit implementation and versioned contracts; do not document examples as functioning routes until verified.

See [INTEGRATION.md](INTEGRATION.md) for adapter ownership and [SECURITY.md](SECURITY.md) for trust-boundary enforcement.
