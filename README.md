# BeeUI

**Reusable Web UI for Bee products, built with FastAPI, Jinja2, and Tabler.**

BeeUI provides a shared operator console instead of duplicating navigation, dashboards, tables, artifact views, and UI controls in every Bee product. It can run as a local demo or be embedded in a product such as [BeeAgent](https://github.com/beesyst/beeagent).

**BeeUI renders. The product decides.** Domain logic, data ownership, permissions, and execution remain with the embedding product.

## How it works

```text
Browser
   |
BeeUI — FastAPI, Jinja2, Tabler
   |
ProductUiAdapter
   |
Bee product — read-models, authorization, actions, artifacts
```

BeeUI handles presentation and protected Web transport. Product adapters provide the data and enforce product-specific access and action rules.

## Features

- **Shared Web console:** responsive Tabler shell, navigation, localized labels, themes, and URL-driven page tabs.
- **Reusable components:** metrics, charts, tables, filters, detail pages, and a bounded chat workspace.
- **Product adapters:** configurable pages and normalized `layout[]` blocks without product-specific HTML forks.
- **Artifacts:** bounded, redacted previews and validated internal links.
- **Operator controls:** session, role, and CSRF protection for bounded product-owned actions.
- **Self-contained assets:** packaged Tabler, icons, and supporting JavaScript/CSS; no CDN required.

BeeUI is **not** an agent runtime, scanner, business-rules engine, or independent authorization service. A standalone demo is available; remote multi-product service integration is not part of the current contract.

## Quick start

**Requirements:** Python 3.14+, Git, and [uv](https://docs.astral.sh/uv/). The launcher can install `uv` if it is missing.

```bash
git clone https://github.com/beesyst/beeui.git
cd beeui
./start.sh doctor
./start.sh web --host 127.0.0.1 --port 8780
```

Open **http://127.0.0.1:8780**.

The bundled demo has `auth.enabled: false`. Keep it on localhost; production authentication and product authorization must be configured by the embedding application.

## Embed in a Bee product

```python
from beeui_module.web.app import create_beeui_app

ui_app = create_beeui_app(
    adapter=product_adapter,
    config_path="config/beeui.yml",
    product_id="example",
    product_title="Example",
)
```

The product implements `ProductUiAdapter`, owns its `config/beeui.yml`, and supplies approved read-models and action callbacks. An existing FastAPI host can use `mount_beeui(...)` instead of a separate Web service.

## Development

```bash
uv run --frozen --group dev pytest -q
uv build --wheel
```

The development workflow is **Issue → Code → Tests → Review → PR → Merge**. Release versions are managed by the repository's Release Please workflow.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — ownership and trust boundaries
- [Integration](docs/INTEGRATION.md) — product adapters and embedding
- [Components](docs/COMPONENTS.md) — reusable UI blocks
- [Configuration](docs/CONFIG.md) — runtime and presentation settings
- [Web UI](docs/WEB_UI.md) — routes and browser behavior
- [Developer guide](docs/DEV_GUIDE.md) — local development and verification
- [Security](docs/SECURITY.md) — browser and action boundaries
- [Roadmap](docs/ROADMAP.md) — delivered and planned capabilities

**One reusable UI framework. Product-owned decisions and execution.**
