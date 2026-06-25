# Apple App Store: Top Rejection Reasons (2026)

Source of truth: the [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), last updated **February 6, 2026**. Section numbers and quoted rule text below are taken from that page. When a rule's exact wording matters for a decision, re-read the live page; Apple revises it several times a year.

This file lists the rejection reasons that account for most real-world App Review rejections, with: (a) the rule and section, (b) why apps trip it, (c) how to fix or avoid it, and (d) how an automated pre-submission audit (e.g. Greenlight) could detect it.

Cross-cutting note on detectability: App Review is partly a human, dynamic-runtime process. An automated audit can catch *static* and *metadata* violations with high confidence (missing privacy policy URL, screenshot dimensions, hardcoded external payment links, debug symbols), but it can only *flag risk* for behavioral rules (crashes under reviewer conditions, "is this app-like enough", misleading UX). Treat audit output as a pre-flight checklist, not a guarantee.

---

## 2.1 App Completeness (crashes, placeholders, broken demo accounts)

**Rule.** Guideline 2.1 (parent section "2. Performance"). Quoted:

> Submissions to App Review ... should be final versions with all necessary metadata and fully functional URLs included; placeholder text, empty websites, and other temporary content should be scrubbed before submission. Make sure your app has been tested on-device for bugs and stability before you submit it, and include demo account info (and turn on your back-end service!) if your app includes a login. ... We will reject incomplete app bundles and binaries that crash or exhibit obvious technical problems.

2.1(b) adds that in-app purchases must be "complete, up-to-date, visible to the reviewer and functional."

**Why apps trip it.** This is consistently the single largest bucket of rejections. Common causes: the app crashes on the reviewer's device or OS version; a login wall with no working demo account (or the backend was off during review); placeholder "Lorem ipsum" / "Coming soon" screens; dead support/marketing URLs; a feature that needs hardware the reviewer does not have; IAPs that are not in the "Ready to Submit" state.

**Fix / avoid.**
- Test on a clean device and on the oldest OS you claim to support; test on at least one small-screen device.
- Provide a working demo account in App Review notes, or a built-in demo mode (demo mode needs prior Apple approval). Confirm the backend is live and will stay live during review.
- Remove placeholder copy and assets; verify every URL (support, marketing, privacy) returns 200.
- Set all referenced IAPs to a submittable state and attach them to the version; explain any that cannot be exercised in review notes.

**Audit detection.**
- Parse the Info.plist / build for placeholder strings ("lorem", "TODO", "coming soon", "test123").
- HTTP-check support URL, marketing URL, and privacy policy URL for 200 status.
- Detect a login screen (heuristic: presence of auth fields) and warn if no demo credentials are present in submission notes.
- Static crash-risk signals: force-unwraps near network code, missing error handling, debug `fatalError`/`abort` calls left in release config.
- Confirm at least one IAP product is attached when StoreKit entitlements/products are present in the binary.

---

## 2.3 / 2.3.1 / 2.3.3 / 2.3.7 / 2.3.10 Accurate Metadata

**Rule.** Guideline 2.3 ("Accurate Metadata"):

> Customers should know what they're getting when they download or buy your app, so make sure all your app metadata, including privacy information, your app description, screenshots, and previews accurately reflect the app's core experience ...

Key sub-points:
- **2.3.1** -- no hidden/undocumented features; new features must be described "with specificity" in the Notes for Review ("generic descriptions will be rejected"); misleading marketing of content/services the app does not offer (example given: "iOS-based virus and malware scanners") or a false price is grounds for removal "whether within or outside of the App Store."
- **2.3.3** -- "Screenshots should show the app in use, and not merely the title art, login page, or splash screen." Overlays for input demonstration are allowed.
- **2.3.7** -- unique app name; keywords that accurately describe the app; do not pack metadata with trademarked terms, popular app names, or pricing. **App names must be limited to 30 characters.**
- **2.3.10** -- keep metadata focused on the app; do not include names/icons/imagery of other mobile platforms or alternative marketplaces unless via approved interactive functionality; "Don't include irrelevant information."

**Why apps trip it.** Screenshots that show only a splash/login screen or are pure marketing renders that do not reflect actual UI; descriptions promising features the build does not contain; keyword stuffing competitor or trademarked names; mentioning "Android" or "Google Play" in metadata; app name over 30 characters; review notes that just say "bug fixes and new features" for a substantive change.

**Fix / avoid.**
- Use real in-app screenshots; text/graphic overlays are fine but the underlying frame must be the actual app.
- Make description and "What's New" match the build exactly; describe new features specifically in review notes.
- App name <= 30 chars; do not include competitor names, prices, or other platforms in name/subtitle/keywords.
- Remove references to other platforms or stores from copy and screenshots.

**Audit detection.**
- Assert app name length <= 30 characters.
- Scan name, subtitle, keywords, and description for: other-platform tokens ("Android", "Google Play", "Windows", "APK"), pricing tokens, and a configurable list of common trademarks/top-app names.
- Verify the number and pixel dimensions of uploaded screenshots per device class (see store-asset-specs.md) and flag screenshots that are pure splash/logo (heuristic: very low UI element density / near-uniform color).
- Flag generic review notes (string match on "bug fixes", "minor improvements") when the version diff indicates new user-facing features.

---

## 3.1.1 In-App Purchase (and 3.1.1(a) / 3.1.3 external purchase links)

**Rule.** Guideline 3.1.1 (parent "3. Business"):

> If you want to unlock features or functionality within your app ... you must use in-app purchase. Apps may not use their own mechanisms to unlock content or functionality, such as license keys, augmented reality markers, QR codes, cryptocurrencies and cryptocurrency wallets, etc.

3.1.1(a) "Link to Other Purchase Methods" and 3.1.3 "Other Purchase Methods" govern when external purchase links/buttons are allowed. The critical regional carve-out: external purchase calls-to-action are broadly prohibited "In all other storefronts, except for the United States storefront." US-storefront apps no longer require an entitlement to include buttons/external links/CTAs to other purchase methods; non-US storefronts generally still do (via StoreKit External Purchase Link Entitlement, Music Streaming Services Entitlement, or Reader app entitlements). The rules here are jurisdiction-specific and changing fast (Epic v. Apple fallout) -- **verify against the live guideline and your storefront before relying on any external-link behavior.**

**Why apps trip it.** Selling digital goods/subscriptions through Stripe/PayPal/your own checkout instead of StoreKit; unlocking premium features with a license key or promo code bought off-platform; linking out to a web paywall in a non-US storefront without the entitlement; crypto/NFT purchases that unlock app functionality.

**Fix / avoid.**
- Use StoreKit in-app purchase for any digital content or functionality consumed in the app.
- Physical goods and "real world" services may and must use other payment methods (do **not** use IAP for those).
- If you want external links, confirm storefront eligibility and apply for the relevant entitlement where required (non-US).
- NFTs: IAP only; viewing owned NFTs is fine but ownership must not unlock features.

**Audit detection.**
- Static-scan the binary/JS bundle for third-party payment SDKs (Stripe, Braintree, PayPal, Adyen) and for `http(s)` checkout URLs reachable from purchase UI.
- Flag StoreKit absence when the app description/metadata references "subscription", "premium", "unlock", "pro".
- Detect external "Buy"/"Subscribe" links and check whether an external-purchase entitlement is present in the provisioning profile; warn for non-US storefronts.

---

## 4.2 Minimum Functionality (repackaged websites, thin apps)

**Rule.** Guideline 4.2:

> Your app should include features, content, and UI that elevate it beyond a repackaged website. If your app is not particularly useful, unique, or "app-like," it doesn't belong on the App Store. ... If your App doesn't provide some sort of lasting entertainment value or adequate utility, it may not be accepted.

**Why apps trip it.** A WebView wrapper around an existing site with no native capability; a single static page; an app that is "just a song or movie" (belongs in iTunes) or "just a book or game guide" (belongs in Apple Books). This overlaps heavily with the 2026 low-value / "vibe-coded" crackdown (see 4.3(b) below).

**Fix / avoid.** Add genuine native value: push notifications, offline mode, device integrations (camera, location, widgets, Siri), or interactive features a website cannot provide. A pure web wrapper is high risk.

**Audit detection.**
- Detect that the app's main view hierarchy is dominated by a single `WKWebView` pointing at a remote URL with little/no native UI.
- Count native capabilities declared (entitlements, frameworks linked: notifications, Core Location, widgets, etc.); flag if effectively zero.

---

## 4.3 Spam -- 4.3(a) duplicate Bundle IDs, 4.3(b) saturated/low-value categories

**Rule.** Guideline 4.3 "Spam":

> (a) Don't create multiple Bundle IDs of the same app. If your app has different versions for specific locations, sports teams, universities, etc., consider submitting a single app and provide the variations using in-app purchase.
> (b) Also avoid piling on to a category that is already saturated; the App Store has enough fart, burp, flashlight, fortune telling, dating, drinking games, and Kama Sutra apps, etc. already. We will reject these apps unless they provide a unique, high-quality experience. Spamming the store may lead to your removal from the Apple Developer Program.

(Note: **drinking games** were added to the saturated-category list in a 2026 revision. "Copycats" is a separate guideline, **4.1**, not 4.3 -- impersonating or cloning another app falls under 4.1.)

**Why apps trip it.** Shipping many near-identical apps that differ only by branding/content (template farms); a low-effort entry into a saturated category; AI/template-generated apps that look interchangeable. In 2026 Apple is enforcing 4.3(b) and 4.2 aggressively against mass-produced "vibe-coded" output (see privacy-and-ai-2026.md).

**Fix / avoid.** Consolidate variants into one app using IAP/configuration instead of many Bundle IDs. For saturated categories, demonstrate a clearly unique, high-quality experience. Avoid shipping cookie-cutter apps from the same account.

**Audit detection.**
- Cross-check the developer account's other Bundle IDs for near-duplicate names, identical asset hashes, or shared code signatures (template reuse).
- Match the app's primary category and keywords against a list of Apple-named saturated categories and warn.
- Image/asset-similarity check against the account's existing apps to flag reskins.

---

## 5.1.1 Data Collection and Storage (privacy policy, consent, account deletion)

**Rule.** Guideline 5.1.1. Highlights:
- **5.1.1(i) Privacy Policies** -- every app must link to a privacy policy in App Store Connect metadata **and** within the app, accessibly. The policy must identify what data is collected and all uses; confirm third parties (analytics, ad networks, SDKs) provide equal data protection; and explain retention/deletion and how to revoke consent / request deletion.
- **5.1.1(ii) Permission** -- must secure user consent for data collection; purpose strings must "clearly and completely describe your use of the data"; provide a way to withdraw consent.
- **5.1.1(iii) Data Minimization** -- request only data relevant to core functionality; prefer out-of-process pickers / share sheets over full Photos/Contacts access.
- **5.1.1(v) Account Sign-In** -- if the app supports account creation, it **must offer account deletion within the app**; don't require login if there are no significant account-based features.

**Why apps trip it.** Missing or dead privacy policy URL; vague purpose strings ("This app needs camera access"); requesting permissions the app never uses; offering sign-up but no in-app account deletion; requiring a social login as the only entry path.

**Fix / avoid.**
- Add a reachable privacy policy URL in ASC and an in-app link.
- Write specific `NS...UsageDescription` purpose strings for every permission, describing the actual use.
- Remove unused permission declarations.
- Implement in-app account deletion if you offer account creation.

**Audit detection.**
- Assert privacy policy URL present in metadata and reachable (200); ideally also detect an in-app privacy link.
- Parse Info.plist for each `NS*UsageDescription`; flag missing or boilerplate strings (length/keyword heuristic), and flag declared permissions/frameworks with no corresponding usage string.
- Detect account-creation flows (sign-up endpoints/SDKs) and check for an account-deletion path; warn if absent.

---

## 5.1.2 Data Use and Sharing -- including 5.1.2(i) third-party AI

**Rule.** Guideline 5.1.2(i):

> Unless otherwise permitted by law, you may not use, transmit, or share someone's personal data without first obtaining their permission. ... You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so. ... You must receive explicit permission from users via the App Tracking Transparency APIs to track their activity.

The clause "including with third-party AI" was added in the **November 13, 2025** guidelines revision and is present in the February 6, 2026 text. See privacy-and-ai-2026.md for full treatment.

**Why apps trip it.** Sending user content (prompts, photos, messages, contacts) to an external LLM/AI API (OpenAI, Google Gemini, Anthropic, etc.) without an in-app disclosure and explicit opt-in; tracking across apps without an ATT prompt; repurposing collected data without new consent; gating core functionality on enabling tracking/notifications.

**Fix / avoid.**
- Add an explicit, in-app, plain-language disclosure naming the third-party AI provider before any personal data is sent, with an affirmative opt-in (a privacy-policy link alone is insufficient).
- Implement the ATT prompt before any cross-app tracking and only track after authorization.
- On-device AI (Core ML, Apple Intelligence on-device) that sends nothing off-device does not trigger the third-party-AI disclosure.

**Audit detection.**
- Static-scan for known AI/LLM API endpoints and SDKs; if found, check for the presence of a disclosure/consent screen in the flow and an entry in the privacy nutrition label / `PrivacyInfo.xcprivacy`.
- Detect tracking SDKs / IDFA access and assert an ATT request (`requestTrackingAuthorization`) exists in the binary.
- Cross-check declared data-collection in the nutrition label against network destinations found statically.

---

## 2.5.2 Software Requirements (downloading or executing code) -- the 2026 "vibe coding" crackdown

**Rule.** Guideline 2.5.2:

> Apps should be self-contained in their bundles, and may not read or write data outside the designated container area, nor may they download, install, or execute code which introduces or changes features or functionality of the app, including other apps. Educational apps designed to teach, develop, or allow students to test executable code may, in limited circumstances, download code provided that such code is not used for other purposes. Such apps must make the source code provided by the app completely viewable and editable by the user.

**What changed in 2026.** The *text* of 2.5.2 is long-standing; what changed is **enforcement**. Beginning around March 2026, Apple began rejecting and pulling "vibe coding" apps -- apps that let a user generate and then run new app code/functionality inside the host app at runtime -- citing 2.5.2's self-containment rule. Reported actions included blocking updates for platforms such as Replit and Vibecode, and Apple pulling the app "Anything" from the App Store (March 2026). Apple's position, as reported: it is not banning AI-generated code as a concept, but it objects to code generated and executed *inside the shipped binary with native capability* that changes the app after review, bypassing App Review. Apps that help users build *other* apps (which are then themselves reviewed/distributed separately) are treated differently from apps that mutate themselves at runtime.

**Why apps trip it.** Embedding an interpreter/runtime that downloads and executes arbitrary user- or AI-generated code that alters the app's features; hot-patching native behavior at runtime; an in-app "generate an app and run it here" loop. The educational-code exception is narrow and requires the source to be fully viewable/editable and not used for other purposes.

**Fix / avoid.**
- Keep the shipped app self-contained; do not download/execute code that changes its features.
- If your product is a builder, generate outputs that ship as separately reviewed apps, not as live mutations of the host binary.
- For genuinely educational code sandboxes, meet the narrow exception (viewable/editable source, no other use) and disclose clearly in review notes.

**Audit detection.**
- Detect embedded scripting/interpreter runtimes (e.g. JavaScriptCore used to execute downloaded code, Lua/Python embeds, dynamic `dlopen` of downloaded libraries) and remote code-fetch endpoints.
- Flag "download then execute" patterns: network fetch of a script/bundle followed by an eval/exec call.
- Heuristic flag for apps whose description includes "build an app", "generate and run", "vibe code" and which embed a runtime.

---

## Quick reference: Apple top-rejection map

| Section | Title | One-line risk | Strong static-audit signal? |
|---|---|---|---|
| 2.1 | App Completeness | Crashes, placeholders, no demo account, dead URLs | Partial (URLs, placeholders, IAP state) |
| 2.3 / 2.3.1 | Accurate Metadata | Misleading screenshots/description, undocumented features | Partial (screenshot specs, name length, keywords) |
| 2.3.3 | Screenshots | Splash/login-only screenshots | Partial (dimension + density heuristic) |
| 2.3.7 | Metadata/keywords | Name > 30 chars, trademark/competitor stuffing | Yes |
| 2.3.10 | Metadata focus | Mentions other platforms/stores | Yes |
| 3.1.1 / 3.1.1(a) / 3.1.3 | In-App Purchase | Non-IAP digital sales, disallowed external links | Yes (payment SDK / URL scan) |
| 4.2 | Minimum Functionality | Web wrapper / thin app | Partial (WebView dominance) |
| 4.3(a) | Spam | Duplicate Bundle IDs | Yes (account cross-check) |
| 4.3(b) | Spam | Saturated/low-value/mass-produced app | Partial (category + similarity) |
| 5.1.1 | Data Collection | No privacy policy, vague purpose strings, no account deletion | Yes |
| 5.1.2(i) | Data Use & Sharing | Third-party AI data sharing without disclosure/consent; no ATT | Partial (endpoint scan) |
| 2.5.2 | Software Requirements | Downloading/executing code that changes the app (vibe coding) | Partial (runtime + remote-fetch detection) |

---

## Sources

- [App Store Review Guidelines (developer.apple.com), updated Feb 6, 2026](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Developer News: Updated App Review Guidelines (Nov 2025, added third-party AI clause)](https://developer.apple.com/news/?id=ey6d8onl)
- [TechCrunch: Apple's new guidelines clamp down on apps sharing data with third-party AI](https://techcrunch.com/2025/11/13/apples-new-app-review-guidelines-clamp-down-on-apps-sharing-personal-data-with-third-party-ai/)
- [9to5Mac: Apple pulls vibe coding app 'Anything' (March 2026)](https://9to5mac.com/2026/03/30/apple-steps-up-crackdown-on-vibe-coding-apps-pulls-anything-from-the-app-store/)
- [9to5Mac: Apple pushing back on 'vibe coding' iPhone apps](https://9to5mac.com/2026/03/18/apple-pushing-back-on-vibe-coding-iphone-apps-developers-say/)
- Secondary overviews of common 2026 rejections: [OpenSpace Services](https://www.openspaceservices.com/blog/mobile-app-development/apple-app-store-rejection-guide-2026-the-15-most-common-reasons-and-how-to-fix-each), [AppTester.co](https://www.apptester.co/blog/app-store-guidelines)

---

## 한국어 요약

- 가장 빈번한 거절 사유는 **2.1 App Completeness**(크래시, 플레이스홀더, 작동하지 않는 데모 계정/백엔드, 죽은 URL)이며, 정적 검사로는 URL 200 확인, 플레이스홀더 문자열, IAP 상태 정도만 잡을 수 있습니다.
- **2.3 메타데이터** 계열: 스크린샷은 실제 사용 화면이어야 하고(스플래시/로그인 화면만은 거절, 2.3.3), 앱 이름은 30자 이하(2.3.7), 다른 플랫폼/스토어 언급 금지(2.3.10), 새 기능은 심사 노트에 구체적으로 기술해야 합니다.
- **결제는 디지털 콘텐츠면 반드시 StoreKit IAP**(3.1.1). 외부 결제 링크 허용 여부는 스토어프런트(미국 vs 그 외)와 entitlement에 따라 달라지며 자주 바뀌므로 공식 문서를 재확인해야 합니다.
- **4.2/4.3(b)**: 단순 웹 래퍼나 양산형 저품질 앱은 거절 대상이며, 2026년에는 AI로 대량 생성된 앱에 대한 단속이 강화되었습니다. 동일 앱의 Bundle ID 중복(4.3(a))도 금지입니다.
- **5.1.1 개인정보**: 도달 가능한 개인정보처리방침 URL(스토어와 앱 내 모두), 구체적인 권한 사용 목적 문자열, 계정 생성 시 앱 내 계정 삭제 기능이 필수입니다.
- **5.1.2(i)**: 개인정보를 **서드파티 AI**로 보낼 때는 앱 내에서 명확히(제공자 명시) 공개하고 명시적 동의를 받아야 합니다(2025년 11월 추가, 2026년 2월 기준 유지). 교차 앱 추적은 ATT 프롬프트가 필요합니다.
- **2.5.2 "바이브 코딩" 단속(2026)**: 규칙 문구는 기존과 동일하나, 런타임에 코드를 내려받아 실행하며 앱 기능을 바꾸는 앱을 자기완결성(self-contained) 위반으로 거절/삭제하기 시작했습니다(2026년 3월 Replit/Vibecode 업데이트 차단, 'Anything' 삭제 보도).
- 자동 사전 점검(Greenlight)은 정적/메타데이터 위반(URL, 스크린샷 규격, 결제 SDK, 권한 문자열, AI 엔드포인트)을 높은 신뢰도로 잡지만, 크래시나 "앱다움" 같은 동적 판단은 위험 신호로만 표시할 수 있습니다.
