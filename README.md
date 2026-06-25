# Greenlight

Pass App Store and Google Play review on the first try.

Greenlight is an open-source Claude Code plugin that turns app submission from a
guessing game into a checklist. It audits your app against the current store
guidelines before you submit, generates spec-perfect store screenshots from your
real app screens, and walks you through submission without ever asking you to
paste console screenshots.

Korean: see [README.ko.md](./README.ko.md).

## Why

Submitting an app today is a loop: you click Next in App Store Connect or Google
Play Console, screenshot the page, paste it into an AI, wait, and repeat. The AI
gives stale or generic steps because it can neither see your logged-in console
nor read the live guidelines. Meanwhile the bar keeps rising. In 2026 Apple
tightened 4.3(b) against low-value apps, started blocking thin vibe-coded
wrappers under 2.5.2, and added 5.1.2(i) for AI data sharing; Google requires new
personal accounts to run a 12-tester, 14-day closed test before production.

Greenlight removes the loop. It reaches live console state through official APIs
first and a user-run Playwright script second. You never paste screenshots.

## What it does

- Pre-submission audit: scores your app against Apple and Google guidelines and
  returns a go / no-go with the exact blockers and fixes.
- Screenshot studio: captures your real app screens and renders store screenshots
  and feature graphics at exact 2026 spec sizes, with per-locale headlines.
- Guided submission: API / fastlane first; a Playwright co-pilot for login-only
  console screens.
- Privacy generator: Apple privacy labels, PrivacyInfo.xcprivacy, and Google Data
  Safety answers from a scan of your SDKs and permissions.
- Local cockpit: a localhost board showing the checklist, screenshot previews in
  device frames, and the submission tracker.

## Who it is for

Indie developers, non-developer founders, and vibe coders who can build an app
but find getting it through review slow, opaque, and easy to fail. Works for both
iOS and Android. English and Korean.

## Install

```
/plugin marketplace add danlee-dev/greenlight
/plugin install greenlight@greenlight
```

## Quickstart

```
/greenlight:preflight both     # full go / no-go audit
/greenlight:screenshots ios    # spec-exact screenshots from real screens
/greenlight:privacy            # privacy labels + data safety
/greenlight:submit ios         # guided submission, no pasting
/greenlight:cockpit            # open the local review board
```

## Killer features

- Rejection resolver: paste a rejection message and get a fix plan plus a drafted
  reply to App Review.
- Wrapper detector: warns when your app may read as a low-value 4.3(b) / 2.5.2
  wrapper, and suggests native value to add.
- Closed-testing tracker: manages Google Play's 12-tester, 14-day requirement with
  a tester kit and a countdown.
- Update guardrail: diffs metadata and binary against the last approved version to
  flag newly risky changes before you ship.

## How it works

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md). Design system:
[docs/DESIGN_CORE.md](./docs/DESIGN_CORE.md).

## Status

Early. This repository is a working scaffold plus a detailed build plan in
[BUILD_PROMPT.md](./BUILD_PROMPT.md). Contributions welcome.

## License

MIT. See [LICENSE](./LICENSE).
