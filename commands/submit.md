---
description: Guided, step-by-step submission for App Store Connect / Google Play Console
argument-hint: [ios|android]
---
Walk the user through submitting $ARGUMENTS for review. Prefer the official APIs (App Store Connect API, Google Play Developer API) or fastlane when credentials exist. When a step is only reachable in the logged-in web console, generate a Playwright script the user runs in their own authenticated browser so Greenlight can read the live page and tell them the exact next click. Never ask the user to paste screenshots manually.
