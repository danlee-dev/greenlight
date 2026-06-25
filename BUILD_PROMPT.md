# Greenlight - Build Prompt for Claude Code

Paste this file's contents (or run it as the opening instruction) at the root of
the `greenlight/` repository in Claude Code. It is the complete brief: what to
build, for whom, why, the exact features, the research to do first, and the
guardrails. Treat it as the source of truth and keep it updated as you build.

This repository already contains a working scaffold (manifests, commands, three
skills, a Python MCP server with a working Pillow screenshot engine, a local
cockpit, and docs). Your job is to research, verify, and grow it into the product
described below without breaking the scaffold's structure.

---

## 0. How to work

- Read these first, in order: this file, `docs/ARCHITECTURE.md`,
  `docs/DESIGN_CORE.md`, and every `skills/*/SKILL.md` plus
  `skills/app-review-guidelines/references/*`.
- Do the research in section 7 BEFORE writing feature code. Store findings as
  reference files in the relevant skill so the knowledge ships with the plugin.
- Work in vertical slices: pick one feature, make it real end to end (command ->
  skill -> MCP tool -> cockpit), then move on.
- After each slice, update `README.md`, `README.ko.md`, and the milestone list.

## 1. Mission

Make app submission a checklist, not a guessing game. Greenlight gets an app
through App Store and Google Play review on the first try by auditing it against
current guidelines before submission, generating spec-perfect store assets from
the app's real screens, and guiding submission without the user pasting console
screenshots.

## 2. Who it is for

- Primary: vibe coders and non-developer founders who can produce an app (often
  with AI) but find review opaque and easy to fail.
- Primary: indie iOS/Android developers who want a fast, reliable pre-flight.
- Secondary: small studios and agencies shipping many apps that want a repeatable
  submission pipeline.
- Bilingual from day one: English and Korean. Author and first users are Korean;
  the open-source audience is global.

## 3. The problem (what we are removing)

1. The paste loop. Today a user clicks Next in the console, screenshots the page,
   pastes it into an AI, waits, and repeats. AIs cannot see the logged-in console
   or read the live guidelines, so the steps are stale or generic.
2. Guideline audit is hard. Doing a full pass against every applicable rule, with
   the current section numbers, is tedious and error-prone.
3. Screenshots are fiddly. Each store has exact pixel sizes that change yearly,
   and Apple 2.3.3 requires screenshots to show the real app.
4. The bar is rising (2026). Apple 4.3(b) low-value crackdown, 2.5.2 blocking thin
   vibe-coded wrappers, 5.1.2(i) AI data-sharing disclosure; Google's 12-tester,
   14-day closed test for new personal accounts.

## 4. Product principles

- No paste. Reach live console state through official APIs first, a user-run
  Playwright script second. Never ask the user to paste console screenshots.
- Diagnose, do not just pass. Greenlight tells the user honestly when an app will
  likely be rejected (for example a 4.3 wrapper) and how to add real value. This
  builds trust and is itself a feature.
- Both stores, one flow. iOS and Android are first-class.
- Open and local. Ships as a Claude Code plugin; the cockpit runs on localhost;
  no Greenlight backend, no telemetry, credentials never leave the user's machine.
- Designed, not machine-emitted. Every surface follows `docs/DESIGN_CORE.md`.

## 5. Current scaffold (already in the repo)

- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.mcp.json`.
- `commands/`: preflight, audit, screenshots, submit, privacy, cockpit.
- `skills/app-review-guidelines/` with `references/` (apple, google, submission
  flow, asset specs, privacy/AI 2026). `skills/screenshot-studio/`,
  `skills/store-submission/`.
- `server/`: FastMCP server (`server.py`) exposing `list_specs`,
  `generate_screenshots`, `audit_metadata`; a working Pillow engine
  (`screenshots.py`); an audit stub (`audit.py`); a Flask cockpit
  (`cockpit/app.py` + `static/index.html`).
- `docs/DESIGN_CORE.md`, `docs/ARCHITECTURE.md`. `templates/`, `renders/`.

Grow these. Do not rename existing modules, classes, or functions (for example do
not rename `render_marketing_panel` to `enhanced_render`). Add alongside.

## 6. Architecture and install

See `docs/ARCHITECTURE.md`. Install is:

```
/plugin marketplace add danlee-dev/greenlight
/plugin install greenlight@greenlight
```

Verify this exact flow works after any manifest change.

## 7. Research to do FIRST (do not skip)

Use web access and write findings into the matching skill reference file. Cite
official URLs. Re-verify anything time-sensitive; assume specifics drift.

1. Plugin format. Verify `plugin.json`, `marketplace.json`, `.mcp.json`, command
   frontmatter, and skill frontmatter against the current Claude Code plugin docs.
   Fix the scaffold if the schema has changed. Confirm `${CLAUDE_PLUGIN_ROOT}`
   usage and how an MCP server in a plugin is launched.
2. Apple. App Store Review Guidelines with current section numbers; the real
   App Store Connect submission flow screen by screen; which steps are login-only;
   App Store Connect API capabilities (metadata, screenshot upload, build select,
   submit for review, phased release); privacy nutrition labels and
   PrivacyInfo.xcprivacy required-reason APIs; 2026 changes (4.3(b), 2.5.2,
   5.1.2(i)).
3. Google. Play Console policies and submission flow; Google Play Developer API
   (Edits, tracks, listings, screenshots); Data Safety form fields; the 12-tester
   14-day closed-testing rule and who it applies to; target API level requirement.
4. Asset specs. Confirm current exact screenshot and graphic sizes for both
   stores; update `references/store-asset-specs.md`.
5. Tooling. fastlane (deliver, supply, snapshot, screengrab, frameit), the iOS
   Simulator and Android emulator capture commands, and Playwright for Python.
6. Design references. Study Linear, Raycast, and Vercel (Geist) for restrained,
   single-accent, non-AI dashboard craft. Apply with `docs/DESIGN_CORE.md`.
7. Prior art to differentiate from: fastlane, `appstoreconnect-mcp`, existing
   screenshot skills. Greenlight's wedge is the integrated pre-audit + both stores
   + no-paste live submission + cockpit + bilingual + non-developer focus.

## 8. Core features (v1)

For each: build command -> skill guidance -> MCP tool -> cockpit view.

8.1 Pre-submission audit (`/greenlight:preflight`, `audit_metadata`)
- Input: project path and platform. Read bundle id / package name, Info.plist or
  AndroidManifest, permissions, SDKs, IAP, sign-in, privacy policy URL, target API.
- Map each fact to a rule check with status pass / warn / fail, a cited section,
  the reason it trips review, and a concrete fix.
- Output a single go / no-go and a pass-probability score. Keep the JSON shape in
  `audit.py` (`pass_probability`, `checks[]`) stable; expand the rule set.
- Acceptance: on a sample iOS and Android project, every blocker maps to a real
  rule and a fix; no false "all clear".

8.2 Screenshot studio (`/greenlight:screenshots`, `generate_screenshots`)
- See section 11. This is a headline feature the user specifically wants.

8.3 Guided submission (`/greenlight:submit`)
- See section 10 for the no-paste strategy. Prefer API / fastlane; Playwright
  co-pilot for login-only screens. Always require explicit user confirmation
  before the final "submit for review" action.

8.4 Privacy and data safety (`/greenlight:privacy`)
- Scan SDKs and permissions; generate Apple privacy label answers,
  PrivacyInfo.xcprivacy, and Google Data Safety answers; flag any collection with
  no user-facing purpose.

8.5 Metadata and ASO generator
- Generate title, subtitle, keywords, description, and "what's new" per locale
  (en, ko, extensible). Enforce guideline-safe copy (no competitor names ->
  avoids Apple 2.3.x), length limits, and keyword hygiene.

8.6 Local cockpit (`/greenlight:cockpit`)
- Visual board: audit checklist with pass / warn / fail, screenshot previews in
  exact device frames, submission step tracker. Hot-reload on file change.
  Production path: share HTML/CSS screenshot templates between cockpit and
  renderer (see section 11). Follow `docs/DESIGN_CORE.md` (Module: UI web).

## 9. Killer features (the "I want to use this" layer)

Prioritize these after core; several are cheap and very high value.

- Rejection resolver. Paste Apple's or Google's rejection text; return a root-cause
  analysis, a fix plan, and a drafted, professional reply to the review team.
- Wrapper / low-value detector. Heuristically assess whether the app reads as a
  thin 4.3(b) / 2.5.2 wrapper and suggest native value to add. Timely and trust-
  building.
- Google closed-testing tracker. Manage the 12-tester, 14-day requirement: a
  tester recruitment kit, an opt-in link and instructions, and a countdown to
  production eligibility.
- Update guardrail. Diff metadata and binary against the last approved version and
  flag newly risky changes (new permission, new SDK, changed data collection)
  before shipping an update.
- Review notes generator. Draft App Review notes and a demo account / steps so a
  reviewer can exercise gated features (a common silent rejection cause).
- Guideline change watcher. A scheduled re-check that flags when a rule the app
  depends on has changed since the last submission.
- One-command preflight. `/greenlight:preflight` runs the whole audit and prints a
  single go / no-go with the exact blockers.
- Screenshot localization. Render the same template per locale with translated
  headlines in one pass.
- If you think of an addition that makes a user say "I want this", propose it in
  the milestone notes and build it behind the same principles.

## 10. The no-paste submission strategy (detailed)

Priority order for reaching any console action:

1. Official API / fastlane when credentials exist. Use the App Store Connect API
   and the Google Play Developer API for metadata, screenshot upload, build
   selection, and submit. Store credentials only in the user's environment / a
   local untracked file; never commit them.
2. Playwright co-pilot for login-only screens. When a step is only reachable in
   the authenticated web console, generate a Playwright script the user runs in
   their own browser session. Greenlight reads the live DOM, tells the user the
   exact next action, and can fill fields when the user approves. It never stores
   the user's password and never logs in on the user's behalf without consent.
3. Last resort: ask the user to confirm a single field value, not to paste a
   screenshot.

Reference Playwright skeleton to generate (Python; the user runs it locally
against their own logged-in Chrome profile via CDP, so Greenlight never handles
credentials):

```python
# greenlight reads the live console without you pasting anything.
# 1) start Chrome with remote debugging and log in normally:
#    /Applications/Google Chrome.app/Contents/MacOS/Google Chrome \
#      --remote-debugging-port=9222 --user-data-dir="$HOME/.greenlight-chrome"
# 2) run this; it attaches to your session, never to your password.
import json, asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        # read the live state of the current console page
        state = await page.evaluate(
            "() => ({url: location.href, title: document.title,"
            " fields: [...document.querySelectorAll('input,select,textarea')]"
            ".map(e => ({name: e.name || e.id, type: e.type, value: e.value}))})"
        )
        print(json.dumps(state, ensure_ascii=False))
        # greenlight uses this snapshot to tell you the exact next click,
        # or to fill a field only after you approve it.

asyncio.run(main())
```

Build a small library of resilient selectors and page recognizers for the common
App Store Connect and Play Console steps. When a page is unrecognized, snapshot it
and ask Greenlight to classify it, then extend the recognizer. This is how the
tool stays correct as the consoles change, instead of relying on stale knowledge.

## 11. Screenshot studio (detailed)

Goal: from the app's real screens, produce store screenshots and graphics that are
pixel-exact to current specs and compliant with Apple 2.3.3.

Pipeline:
1. Capture real screens. Boot the iOS Simulator (`xcrun simctl io booted
   screenshot`) or Android emulator (`adb exec-out screencap`), or accept user
   captures. Optionally drive the app to named screens with fastlane snapshot /
   screengrab or Playwright for web. Never fabricate UI.
2. Compose. Place each capture in a device frame with a localized headline and
   subtitle on a background that follows `docs/DESIGN_CORE.md` (single accent,
   near-black or off-white, no purple gradient, no glassmorphism, no emoji).
3. Render to exact sizes from `references/store-asset-specs.md`
   (iPhone 6.9 = 1320x2868, iPad 13 = 2064x2752, Play feature = 1024x500, etc.).
4. Localize. Re-render per locale with translated copy (en, ko first).
5. Review in the cockpit; tweaks hot-reload.

Implementation note: the current `screenshots.py` is a working Pillow engine and a
fine fallback. The production path is HTML/CSS templates rendered headless with
Playwright, so the cockpit preview and the final PNG share one template (the
HyperFrames pattern: a local studio with hot reload). Keep `screenshots.py`'s
public API (`SPECS`, `render_marketing_panel`, `render_feature_graphic`) intact;
add the HTML template renderer beside it.

## 12. Design mandate

Apply `docs/DESIGN_CORE.md` to the cockpit and every rendered asset. Summary of
hard rules: one accent (Greenlight green) on a neutral base; Pretendard for Korean
(letter-spacing -0.025em) and an editorial English pairing (Archivo / Hanken
Grotesk / JetBrains Mono); 8pt grid; no purple or indigo gradients, no gradient
text, no glassmorphism, no frosted stat chips, no thick colored left-border alert
cards, no fake live dots, no emoji anywhere. Reference Linear, Raycast, and Vercel
Geist for restraint.

## 13. Tech stack and conventions

- MCP server: Python, FastMCP (`mcp` package). Renderer: Pillow now, HTML/CSS +
  Playwright next. Cockpit: Flask + static now; a small Vite app is acceptable
  later, but keep a no-build fallback. Submission: official APIs and fastlane.
- Target platform: macOS first (the author uses an Apple Silicon M3; do not assume
  Windows). Shell snippets should be zsh/bash on macOS.
- Code style, author's rules (follow exactly):
  - No emojis anywhere in code, comments, output, or docs. Use plain ASCII markers
    such as `>`, `>>`, or `-` in comments if a marker is needed.
  - Do not rename existing class or function names when extending code, and do not
    introduce names like `enhanced_x`. Add new, clearly named units beside the old.
  - Keep diffs minimal and readable; prefer clarity over cleverness.
- Keep the JSON shapes that the cockpit consumes stable (`audit.run` output,
  `SPECS`). Version any breaking change.
- Tests: add a `tests/` folder; at minimum, render every spec size and assert exact
  pixel dimensions, and validate every manifest JSON parses.

## 14. File-by-file plan

- `skills/app-review-guidelines/`: keep current; expand references as research
  lands; add a machine-readable `rules.yaml` (id, store, section, severity, check,
  fix) that `audit.py` consumes.
- `server/greenlight_mcp/audit.py`: replace the stub with a real rule engine that
  reads `rules.yaml` and inspects the project. Keep the output shape.
- `server/greenlight_mcp/screenshots.py`: keep the API; add the HTML/CSS +
  Playwright renderer and a real-screen capture helper.
- `server/greenlight_mcp/submit.py` (new): API / fastlane / Playwright co-pilot.
- `server/greenlight_mcp/privacy.py` (new): SDK + permission scan -> labels.
- `server/greenlight_mcp/cockpit/`: grow the board per Module UI web; wire
  `/api/render` and a submission tracker.
- `commands/`: keep names; flesh out prompts to call the new tools.
- `tests/`: as above.

## 15. Definition of done (v1)

- Install flow works from a clean Claude Code.
- `/greenlight:preflight both` returns a real, sourced go / no-go on a sample iOS
  and Android project.
- `/greenlight:screenshots` produces exact-size PNGs from a real simulator capture
  for both stores, in en and ko.
- `/greenlight:submit` completes a real submission via API / fastlane on a test
  app, or drives the Playwright co-pilot end to end with no pasted screenshots.
- `/greenlight:privacy` outputs valid Apple labels, a PrivacyInfo.xcprivacy, and
  Google Data Safety answers.
- Cockpit renders the three views and follows `docs/DESIGN_CORE.md`.
- README (en + ko) and ARCHITECTURE match the built behavior.

## 16. Milestones

- M0 (done): scaffold, manifests, skills, engine, cockpit, docs.
- M1: real audit rule engine (`rules.yaml`) + preflight + cockpit checklist.
- M2: screenshot studio with real-screen capture + HTML templates + localization.
- M3: guided submission (API / fastlane) + Playwright co-pilot + privacy generator.
- M4: killer features (rejection resolver, wrapper detector, closed-testing
  tracker), polish the cockpit, launch the README and a short demo.

## 17. Security and safety guardrails

- Never store, log, or transmit store credentials or passwords. Use the user's
  environment and untracked local files only.
- Never auto-submit, change pricing, or move money without explicit user
  confirmation in the same session.
- The Playwright co-pilot attaches to the user's own logged-in browser session; it
  must not perform a login on the user's behalf without consent.
- No telemetry. The cockpit binds to 127.0.0.1 only.
- Treat links and console pages cautiously; verify unfamiliar URLs with the user.

## 18. Open questions for the author

1. Distribution: a dedicated marketplace repo, or this repo as its own marketplace
   (current setup)?
2. fastlane as a hard dependency, or optional with a pure-API fallback?
3. Which locales beyond en and ko for v1?
4. Cockpit: keep no-build Flask + static, or move to Vite once it grows?
5. Should the wrapper / low-value detector be on by default in preflight?
