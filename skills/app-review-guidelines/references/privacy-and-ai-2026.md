# Privacy and AI Disclosure (2026)

This file covers the privacy obligations both stores enforce, plus the two 2026-relevant shifts: Apple's third-party-AI data-sharing rule (5.1.2(i)) and the "vibe coding" / low-value-app crackdown (2.5.2, 4.3(b)).

---

## 1. Apple privacy nutrition labels (App Privacy)

In App Store Connect, every app completes the **App Privacy** questionnaire, which renders as the **privacy "nutrition label"** on the product page. You declare, per data type, whether it is:
- **Used to Track You** (linked to third-party data for advertising/measurement -- requires App Tracking Transparency),
- **Linked to You** (tied to identity), or
- **Not Linked to You**.

You must declare the data your app **and any third-party SDKs you bundle** collect. The label must match actual behavior; misdeclaration is an Accurate Metadata (2.3) and privacy (5.1) issue. Reference: [User Privacy and Data Use](https://developer.apple.com/app-store/user-privacy-and-data-use/).

## 2. PrivacyInfo.xcprivacy (privacy manifest) + Required Reason APIs

A **privacy manifest** is a property-list file named **`PrivacyInfo.xcprivacy`** that declares: the data types your code collects, the reasons, whether data is used for tracking, and the **Required Reason API** categories your code uses. Reference: [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk) and [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files).

Key dates and rules:
- Since **May 1, 2024**, apps using **Required Reason APIs** (certain file-timestamp, system-boot-time, disk-space, active-keyboard, and `UserDefaults` APIs) must declare an approved reason in a privacy manifest.
- Since **February 12, 2025**, if a new app (or an update that adds one) includes a **commonly used third-party SDK** from Apple's list, that SDK must ship a **signed privacy manifest**, or App Store Connect blocks submission.
- At build time, **Xcode (15+) aggregates** all app and SDK privacy manifests into a single **Privacy Report**, which feeds the App Store privacy label.

**Audit detection.**
- Assert `PrivacyInfo.xcprivacy` exists in the app bundle.
- Detect Required Reason API usage in code and assert a matching declared reason in the manifest.
- Enumerate bundled SDKs; for any on Apple's "requires manifest + signature" list, assert the SDK provides a signed manifest.
- Cross-check the manifest's declared collection against the App Privacy nutrition label.

## 3. Apple 5.1.2(i): third-party AI data-sharing disclosure (new Nov 2025, in force 2026)

Guideline 5.1.2(i) (verbatim, relevant clause):

> You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so.

This "including with third-party AI" wording was **added on November 13, 2025** and is present in the **February 6, 2026** guidelines. It makes third-party AI a regulated data-sharing destination for the first time.

What it requires in practice (per Apple's wording and developer guidance):
- **In-app disclosure** before sending personal data to an external AI service -- a buried clause in a privacy policy or general ToS is **not** sufficient.
- **Identify the recipient** (name the AI provider, e.g. OpenAI, Google Gemini, Anthropic) rather than vague "service providers" language.
- **Explicit, affirmative consent** via a visible in-app interaction (e.g. a consent dialog) before the data leaves the device.

Scope:
- Triggered by sending **personal/identifiable** user data to a **third-party** AI endpoint -- even briefly, for processing, before results return.
- **On-device** AI (Core ML, on-device Apple Intelligence) that sends nothing off-device does **not** trigger the special third-party-AI disclosure.

**Audit detection.**
- Static-scan for known third-party AI/LLM SDKs and API hostnames (OpenAI, Gemini/Google AI, Anthropic, Cohere, etc.).
- If found, assert there is an in-app consent/disclosure surface before the call, and a corresponding entry in the nutrition label / privacy manifest.
- Flag generic "we may share data with third parties" language with no named AI recipient.

## 4. Google Play Data Safety (parallel obligation)

Google's equivalent is the **Data safety** section (declared in Play Console, shown on the listing). Every app -- including ones that collect nothing -- must complete it and provide a privacy policy URL. For each data category you declare collection, sharing, purpose, security (e.g. encryption in transit), and deletion options. Reference: [Provide information for Google Play's Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469).

Google does **not** yet have a single numbered "third-party AI" clause equivalent to Apple's 5.1.2(i), but the existing rules already apply to AI data flows: sending user data to an external AI provider is **sharing** and must be declared, covered by the privacy policy, and consented to where the User Data and sensitive-data policies require. **Verify current AI-specific guidance against the live Play policies**, as Google has been issuing AI-content and generative-AI policy updates through 2025-2026. As of 2025-2026, Play Console runs **automated checks against the AAB**; undeclared data access is flagged before human review.

**Audit detection.** Same SDK/endpoint scan as Apple, cross-checked against the Data safety declaration and the privacy policy (see google-rejections.md).

## 5. The 2026 "vibe coding" / low-value-app crackdown (2.5.2, 4.3(b), 4.2)

Three guidelines drive this:

- **2.5.2 (Software Requirements).** Apps must be **self-contained** and "may not download, install, or execute code which introduces or changes features or functionality of the app." The text is old; **enforcement tightened in 2026**. From ~March 2026 Apple began rejecting/pulling **vibe coding** apps -- apps that let users generate and then **run new code/functionality inside the host app at runtime**, which changes the app after review and bypasses App Review. Reported actions: blocked updates for platforms such as **Replit** and **Vibecode**, and Apple **pulling the app "Anything"** (March 2026). Apple's stated objection is not AI-generated code per se, but code that is generated and executed **inside the shipped binary with native capability**, mutating the app post-review. Builders that emit **separately reviewed** apps are treated differently from apps that mutate themselves.

- **4.3(b) (Spam).** Mass-produced, interchangeable, low-effort apps -- including AI/template-generated output -- get rejected unless they offer "a unique, high-quality experience." Saturated categories (now including **drinking games**, added in a 2026 revision) face a higher bar.

- **4.2 (Minimum Functionality).** Thin apps and web wrappers without genuine native value do not belong on the store. AI-scaffolded apps frequently fail here when they are essentially a generated shell.

Net effect for AI-built apps in 2026: shipping is fine, but the app must (1) be self-contained (no runtime code-fetch-and-execute that alters it), (2) provide real, unique functionality, and (3) disclose and gate any third-party-AI data sharing under 5.1.2(i).

**Audit detection.**
- Detect embedded interpreters/runtimes plus remote code-fetch endpoints, and "fetch then eval/exec" patterns (2.5.2 risk).
- Detect web-wrapper dominance and near-zero native capability (4.2 risk).
- Cross-check the account for near-duplicate/reskinned apps and saturated-category placement (4.3(b) risk).

---

## Combined pre-submission privacy/AI checklist

| Check | Apple | Google |
|---|---|---|
| Privacy policy URL (reachable, app-specific) | Required (ASC + in-app) | Required (listing + in-app where applicable) |
| Privacy disclosure surface | App Privacy nutrition label | Data safety form |
| Privacy manifest file | PrivacyInfo.xcprivacy (+ Required Reason APIs, signed SDK manifests) | n/a (declared via Data safety) |
| Tracking consent | App Tracking Transparency prompt | Disclosed sharing + consent per policy |
| Third-party AI data sharing | 5.1.2(i): in-app disclosure, named provider, explicit consent | Declare as sharing; cover in policy; consent per policy |
| Runtime code execution | 2.5.2: must be self-contained | Comparable restrictions on dynamic code |
| Low-value/mass-produced | 4.3(b) / 4.2 | Store Listing / minimum-functionality policies |

---

## Sources

- [Apple: User Privacy and Data Use](https://developer.apple.com/app-store/user-privacy-and-data-use/)
- [Apple: Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- [Apple: Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [App Store Review Guidelines (5.1.2(i), 2.5.2, 4.3, 4.2), updated Feb 6, 2026](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Developer News: updated guidelines adding third-party AI clause (Nov 2025)](https://developer.apple.com/news/?id=ey6d8onl)
- [TechCrunch: Apple clamps down on apps sharing data with third-party AI](https://techcrunch.com/2025/11/13/apples-new-app-review-guidelines-clamp-down-on-apps-sharing-personal-data-with-third-party-ai/)
- [9to5Mac: Apple pulls vibe coding app 'Anything' (March 2026)](https://9to5mac.com/2026/03/30/apple-steps-up-crackdown-on-vibe-coding-apps-pulls-anything-from-the-app-store/)
- [Google: Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469)

---

## 한국어 요약

- **Apple App Privacy(영양성분표)**: 데이터 유형별로 "추적/연결됨/연결 안 됨"을 선언하며, 번들된 서드파티 SDK가 수집하는 것까지 포함해야 하고 실제 동작과 일치해야 합니다.
- **PrivacyInfo.xcprivacy(개인정보 매니페스트)**: Required Reason API 사유 선언 필요(2024-05-01부터), 주요 서드파티 SDK는 서명된 매니페스트 필수(2025-02-12부터, 없으면 제출 차단). Xcode가 전체를 모아 개인정보 라벨에 반영.
- **Apple 5.1.2(i)(2025-11 추가, 2026 시행)**: 개인정보를 **서드파티 AI**로 보낼 때 앱 내에서 명확히 공개하고(제공자 이름 명시), 명시적 동의를 먼저 받아야 합니다. 정책 링크만으로는 불충분. 기기 내(on-device) AI는 해당 없음.
- **Google 데이터 안전**: 수집 없음 포함 모든 앱이 작성. AI 전용 번호 조항은 아직 없지만, AI로 데이터 전송은 "공유"로 신고·동의·정책 반영 대상이며 AAB 자동 검사로 미신고 접근이 차단됩니다. 최신 AI 정책은 공식 문서 재확인.
- **2026 "바이브 코딩"/저품질 단속**: 2.5.2(런타임 코드 실행으로 앱을 바꾸면 자기완결성 위반, Replit/Vibecode/'Anything' 사례), 4.3(b)(양산형·포화 카테고리, drinking games 추가), 4.2(웹 래퍼·빈약한 앱).
- AI로 만든 앱도 (1) 자기완결성 유지, (2) 실질적 고유 기능, (3) 서드파티 AI 데이터 공유 공개·동의(5.1.2(i))를 충족하면 통과 가능합니다.
