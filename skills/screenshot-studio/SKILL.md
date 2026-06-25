---
name: screenshot-studio
description: Generate App Store and Google Play store screenshots and feature graphics at exact 2026 spec sizes from the app's real screens, with per-locale headline copy. Use when the user needs store listing images or asks to prepare screenshots for submission.
---

# Screenshot Studio

Produce store-ready marketing screenshots that are (a) pixel-exact to the current store specs and (b) compliant with Apple 2.3.3 (screenshots must show the actual app).

## Pipeline
1. Source real screens: boot the iOS Simulator or Android emulator and drive the app to key screens, or accept user-provided captures. Do not fabricate UI.
2. Compose: place each capture in a device frame on a background, with a localized headline and subtitle.
3. Render: call the Greenlight MCP tool `generate_screenshots` (or run `server/greenlight_mcp/screenshots.py`) to output PNGs at exact sizes.
4. Review: open the cockpit to tweak headline, color, and order; hot-reload re-renders.

## Spec sizes (2026)
See `app-review-guidelines/references/store-asset-specs.md` for the authoritative table. Primary: iPhone 6.9" = 1320x2868, iPad 13" = 2064x2752, Google Play feature graphic = 1024x500 (no alpha).

## Design
The rendered output and the cockpit UI follow `docs/DESIGN_CORE.md` (anti-AI design system: single accent, no purple gradients, no glassmorphism, no emoji, 8pt grid, Pretendard for Korean).

## Notes for implementation
The current `screenshots.py` is a working Pillow reference engine. The production path should move templates to HTML/CSS rendered headless (Playwright) so the cockpit and the renderer share one template, hot-reloading like HyperFrames.
