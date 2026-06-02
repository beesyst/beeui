# INTEGRATION — подключение BeeUI к Bee-продуктам

## Purpose

This document describes how Bee-продукты (`beecap`, `beeagent` и будущие) подключают BeeUI как embedded UI layer.

## Current status

**Iteration 9** — BeeCap fixture adapter MVP.

- Generic `ProductUiAdapter` contract exists in `src/beeui_module/adapters/`.
- `BeeCapFixtureAdapter` in `src/beeui_module/adapters/beecap.py` is a fixture/reference implementation only.
- Real BeeCap adapter must live on the BeeCap side (see below).
- Embedded mount API (`create_beeui_app(adapter=...)`) is **not yet implemented** — planned for Iteration 10.
- This is **not** a production integration path yet.

## Architecture boundary

```text
BeeCap (product side)
  └── src/beecap_module/interfaces/ui/
        ├── adapter.py       ← real BeeCapUiAdapter (not in BeeUI)
        ├── read_model.py    ← BeeCap read-model construction
        └── artifacts.py     ← BeeCap artifact helpers

        ↓ implements ProductUiAdapter protocol

BeeUI (framework side)
  ├── src/beeui_module/adapters/
  │   ├── base.py            ← ProductUiAdapter protocol + base class
  │   ├── envelopes.py       ← stable adapter result envelopes
  │   ├── errors.py          ← stable adapter errors
  │   ├── ids.py             ← safe ID validation
  │   └── beecap.py          ← fixture/reference adapter (NOT for production)
  │
  ├── src/beeui_module/web/app.py   ← create_beeui_app(...)
  └── config/beeui.yml              ← product-specific UI config (future)
```

Main rule:

```text
BeeUI renders.
Product decides.
```

## Where the real BeeCap adapter should live

The real `BeeCapUiAdapter` belongs in the BeeCap repository, **not** in BeeUI.

Expected location:

```text
src/beecap_module/interfaces/ui/
  ├── adapter.py          ← BeeCapUiAdapter(ProductUiAdapterBase)
  ├── read_model.py       ← BeeCap read-model construction
  └── artifacts.py        ← artifact reading from BeeCap storage
```

BeeCap-side adapter is responsible for:

- reading BeeCap storage/artifacts;
- constructing read-models (dashboard, runs, artifacts);
- enforcing product-specific allowlists;
- owning product authority decisions;
- implementing bounded action callbacks (future).

## What BeeUI must NOT do during integration

- BeeUI must not read BeeCap storage/config directly.
- BeeUI must not replicate trading/domain logic.
- BeeUI must not make broker/order/runtime calls.
- BeeUI must not become a second source of truth for product state.
- BeeUI must not mutate product artifacts through read-only routes.
- BeeUI must not import `beecap_module` directly.

## Current fixture adapter

`BeeCapFixtureAdapter` in `src/beeui_module/adapters/beecap.py` exists only to:

- validate the `ProductUiAdapter` contract against realistic BeeCap-shaped data;
- provide a reference implementation for BeeCap-side adapter developers;
- enable integration tests without a real BeeCap dependency.

It is **not** a production adapter.

It does **not**:

- read BeeCap storage;
- implement trading/profit/order logic;
- provide route-level integration;
- replace the future real BeeCapUiAdapter.

## Example embedded config

An example of what a future BeeCap-specific `beeui.yml` might look like is in:

```text
examples/beecap_embedded/beeui.yml
```

This file is **not loaded at runtime**. It is documentation only.

## Future integration flow (Iteration 10+)

```python
from beeui_module.web.app import create_beeui_app
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = create_beeui_app(
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

This will be the MVP integration mode after Iteration 10.

## Security notes

- All adapter input (run_id, artifact_id) is validated through `beeui_module.adapters.ids`.
- Adapter envelopes use stable `ok|partial|error` status — raw exceptions are not leaked.
- Secrets must never cross the adapter boundary into BeeUI.
- Write/action adapter methods are unavailable by default.
