# THEME — BeeUI

## Purpose

BeeUI supports three presentation modes: `system`, `light` and `dark`. A theme choice changes only presentation. It cannot affect product execution, permissions, session claims or audit records.

## Configuration

The validated UI configuration may specify a default theme:

```yaml
app:
  theme:
    mode: system
    primary: blue
    base: gray
    font: sans-serif
    radius: 1
    density: default
```

The canonical values for `mode` are `system`, `light` and `dark`. The compatibility alias `auto` is normalized to `system` when accepted by configuration loading. Invalid values fail validation. Other theme tokens are constrained by their owning configuration schema; arbitrary CSS is not an allowed configuration value.

## Browser behavior

The effective theme is expressed with the `data-bs-theme` attribute on the root `<html>` element. Tabler and BeeUI styles use this attribute rather than product-specific theme logic.

The page's early theme bootstrap reads the allowlisted `beeui-theme` value from `localStorage` before initial rendering to reduce a light/dark flash. It uses the configured default if no valid browser preference exists. `system` resolves through the browser's `prefers-color-scheme` media query. Invalid stored values are discarded.

The operator can explicitly select system, light or dark. The selection persists as a local browser preference; it is not a server authorization decision, session token or source of product configuration.

## Charts and dynamic components

ApexCharts theme mode follows the effective `data-bs-theme` attribute. When the operator changes the theme, registered chart instances are updated through their supported chart update lifecycle. New chart instances inherit the current mode.

Progressive page tabs and dynamically inserted blocks must continue to use the current theme, while remaining compatible with both light and dark modes.

## Security and asset policy

- Never evaluate arbitrary theme JavaScript or CSS from a product read-model.
- Do not load scripts, fonts, stylesheets or tracking pixels from unapproved CDNs.
- Do not use browser theme state to make role, Scope or product permission decisions.
- Escape labels and validate any theme-related configuration.
- Package runtime Tabler/theme assets locally. `docs/vendor/tabler/` contains reference documentation and does not determine which runtime assets are installed.

See [WEB_UI.md](WEB_UI.md) for browser integration and [SECURITY.md](SECURITY.md) for untrusted-data rules.
