---
description: Run a full pre-submission go/no-go audit for App Store and Google Play
argument-hint: [ios|android|both]
---
Run a Greenlight preflight for the current project ($ARGUMENTS, default both).

1. Load the app-review-guidelines skill.
2. Inspect the project: bundle id / package name, Info.plist or AndroidManifest permissions, SDKs, privacy policy URL, in-app purchases, sign-in flows, and the build target API level.
3. Score every applicable guideline (Apple 2.1, 2.3.3, 3.x, 4.3(b), 5.1.1, 5.1.2(i), 2.5.2; Google data safety, permissions, target API, 12-tester closed testing).
4. Output a single go / no-go verdict with a numbered list of blockers (must-fix) and warnings (should-fix), each citing the exact rule and the fix.
5. Offer to fix what is auto-fixable (metadata, privacy manifest, screenshots) and to open the cockpit.
