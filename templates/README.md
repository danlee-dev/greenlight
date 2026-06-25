# Screenshot templates

Production screenshot templates live here as HTML/CSS (rendered headless with
Playwright), so the cockpit preview and the final render use the same source.
Until that lands, `server/greenlight_mcp/screenshots.py` is the working Pillow
reference engine. Each template must support exact spec sizes from
`skills/app-review-guidelines/references/store-asset-specs.md` and follow
`docs/DESIGN_CORE.md`.
