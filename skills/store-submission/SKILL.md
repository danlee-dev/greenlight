---
name: store-submission
description: Guide a developer end-to-end through submitting an app for review on App Store Connect and Google Play Console, preferring official APIs and using Playwright for login-only screens. Use when the user is ready to submit or update an app, or is stuck on a console step.
---

# Store Submission

Goal: get from "build is ready" to "submitted for review" without the user pasting console screenshots.

## Strategy (in priority order)
1. Official API / fastlane when credentials exist (App Store Connect API, Google Play Developer API). No clicking.
2. Playwright co-pilot for login-only screens: generate a script the user runs in their own authenticated browser; Greenlight reads the live DOM and states the exact next action. See `app-review-guidelines/references/submission-flow.md` for which steps are login-gated.
3. Only as a last resort, ask the user to confirm a single field value.

## Flow
Use `app-review-guidelines` for the canonical step list and rejection checks. Run a `preflight` audit before submitting. After submission, track status and, on rejection, draft the fix plan and the reply to App Review.
