# Google Play: Common Rejection Reasons (2026)

Source of truth: the [Play Console Help](https://support.google.com/googleplay/android-developer) and the [Developer Program Policy](https://play.google/developer-content-policy/). Google does not number its policies like Apple; rejections cite a named policy plus a remediation deadline.

Each item below gives: (a) the policy area, (b) why apps trip it, (c) how to fix/avoid it, and (d) how an automated pre-submission audit (Greenlight) could detect it. Note that Google Play increasingly runs **automated pre-checks against the uploaded AAB** before human review, so static, code-level violations are caught early.

---

## Closed-testing gate for new personal accounts (12 testers, 14 consecutive days)

**Policy.** [App testing requirements for new personal developer accounts](https://support.google.com/googleplay/android-developer/answer/14151465). Personal developer accounts **created after November 13, 2023** must run a closed test before they can apply for production access. Current requirement (2026): **at least 12 testers opted in to the closed test, continuously for the last 14 days**, before you apply for production access. Google reduced the threshold from 20 to 12 testers on **December 11, 2024**; the 14-day duration is unchanged. This applies to **personal** accounts only -- **organization** accounts are exempt.

**Why teams trip it.** Treating it as a normal review step and submitting straight to production; not lining up 12 real testers; testers opting in late so the 14-day clock has not elapsed; using emulators or fake accounts (Google monitors real engagement). Note: once a tester opts in they count toward the 14 days even if they later uninstall.

**Fix / avoid.**
- Plan ~3 weeks of lead time: recruit 12+ real testers (real Android devices, real Google accounts), create a Closed testing track, distribute the opt-in link, and keep the test running 14 consecutive days.
- Keep testers actively using the app during the window; spread across device types for coverage.
- Only after the 14-day window with 12+ opted-in testers can you request production access.

**Audit detection.**
- Read account type (personal vs organization) and creation date; if personal and post-2023-11-13, require evidence of an active closed track.
- Via Play Console (login-gated): count opted-in testers on the closed track and compute days-since-opt-in; warn if < 12 testers or < 14 continuous days.
- Pre-flight checklist item: block "ready for production" until the gate is satisfied.

---

## Missing, broken, or mismatched privacy policy

**Policy.** [User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311) and Data safety requirements. A privacy policy URL is **mandatory** for every app (entered in the store listing / App content section). It must be on an active, public URL (not a PDF, not editable by users), apply specifically to the app, and cover what data the app collects/uses/shares.

**Why apps trip it.** No privacy policy URL; a dead or 404 link; a generic template that does not match the app's actual data practices; a policy that omits data types the app actually collects (e.g. location); the in-app privacy policy link is missing.

**Fix / avoid.**
- Provide a live, app-specific privacy policy URL that lists every collected data type, all uses, sharing, retention, and deletion/consent process.
- Ensure the same policy is linked inside the app where the app handles personal/sensitive data.
- Keep it consistent with the Data safety form (mismatches are a rejection trigger).

**Audit detection.**
- Assert a privacy policy URL is present in the store listing; HTTP-check for 200 and that it is HTML (reject PDF-only).
- NLP-check the policy for required elements (data types, sharing, retention, deletion, contact) and cross-check declared data types against the Data safety form and against permissions in the manifest.

---

## Data safety section: missing, incomplete, or mismatched declaration

**Policy.** [Provide information for Google Play's Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469). **Every** app must complete the Data safety form -- even apps that collect no data (they declare "no data collected" and still provide a privacy policy). For each of the data categories the form asks: is it collected, is it shared, why, how is it secured (e.g. encryption in transit), and can users request deletion. "Collection" = transmitting data off the device; "sharing" = transferring to a third party (including SDK providers that use the data for their own purposes).

**What changed (2025 to 2026).** Google's 2025 policy update reclassified the Android Advertising ID / device identifiers, tightened the definition of "sharing," and increased automated enforcement. Play Console now runs automated checks against your AAB; **if your binary accesses data types you did not declare, you are flagged before human review.** Keep the form current with every release.

**Why apps trip it.** Declaring "no data collected" while a bundled SDK (analytics, ads, crash reporting) transmits identifiers; under-declaring shared data; declaring deletion is available when there is no deletion path; the Data safety form contradicting the privacy policy.

**Fix / avoid.**
- Inventory every SDK and what it sends off-device; declare all collected and shared data types accurately.
- Reconcile the form with the privacy policy and with the actual manifest permissions and network calls.
- Provide a real deletion mechanism if you declare one.

**Audit detection.**
- Diff the Data safety declaration against (1) manifest permissions, (2) statically detected SDKs and their known data behavior, (3) network endpoints found in the binary; flag any data type accessed but not declared.
- Cross-check Data safety vs privacy policy for contradictions (collected/shared/deletion claims).

---

## Permissions and sensitive APIs not justified (or restricted-permission declaration missing)

**Policy.** [Permissions and APIs that Access Sensitive Information](https://support.google.com/googleplay/android-developer/answer/9888170). You may only request permissions/sensitive APIs "necessary to implement current features or services" that are promoted in your listing. Sensitive permissions (background location, SMS/Call Log, "All files access" / MANAGE_EXTERNAL_STORAGE, AccessibilityService, package visibility, exact alarms, etc.) require an approved use case and often a Permissions Declaration form; some require a video demo.

**Why apps trip it.** Requesting background location, SMS, Call Log, or All-files-access without an eligible, prominent use case; leaving permissions in the manifest that the app no longer uses; using AccessibilityService for non-accessibility purposes; missing the in-app prominent disclosure + runtime consent for sensitive data (especially location) before the system permission prompt.

**Fix / avoid.**
- Request the minimum permissions; remove unused ones from the manifest.
- For each restricted permission, confirm eligibility, complete the Permissions Declaration, and (where required) record the demo video.
- Add a prominent in-app disclosure and runtime consent before accessing sensitive data, independent of the OS prompt.

**Audit detection.**
- Parse AndroidManifest.xml for `uses-permission`; flag the restricted set (ACCESS_BACKGROUND_LOCATION, READ_SMS, READ_CALL_LOG, MANAGE_EXTERNAL_STORAGE, BIND_ACCESSIBILITY_SERVICE, QUERY_ALL_PACKAGES, SCHEDULE_EXACT_ALARM, etc.).
- For each restricted permission, require a justification entry and a completed declaration; flag permissions with no corresponding code usage (dead permissions).
- Detect that a prominent-disclosure screen exists before location/sensitive access.

---

## Target API level requirement not met

**Policy.** [Target API level requirements for Google Play apps](https://support.google.com/googleplay/android-developer/answer/11926878) / [Android developer target SDK guide](https://developer.android.com/google/play/requirements/target-sdk). New apps and updates submitted after **August 31, 2025** must target **Android 15 (API level 35) or higher** (Wear OS, Android Automotive OS, and Android TV: Android 14 / API 34 or higher). Extensions to **November 1, 2025** were available. Existing apps generally must target at least API 34 to remain available to new users on newer OS versions. **Verify the current minimum against the official page before each release -- Google raises it roughly once a year.**

**Why apps trip it.** Building against an older `targetSdkVersion`; relying on a deprecated SDK; an extension lapsing.

**Fix / avoid.** Set `targetSdkVersion` to the current required level (35 as of this writing), retest behavior changes introduced by that API level, and ship as an AAB.

**Audit detection.**
- Read `targetSdkVersion` from the AAB/manifest and compare to the current required level (config-driven so the threshold can be updated); flag if below.

---

## Wrong artifact format / unsigned or unstable build

**Policy.** Google Play requires the **Android App Bundle (AAB)** as the standard publishing format for new apps (APK uploads are no longer accepted for new apps). The build must be signed (Play App Signing) and stable.

**Why apps trip it.** Uploading an APK for a new app; an unsigned or debug build; crashes/ANRs on the review devices.

**Fix / avoid.** Publish a signed `.aab`, enroll in Play App Signing, and test for crashes/ANRs (Android vitals) before release.

**Audit detection.**
- Verify the upload is `.aab`, is signed, is a release (not debuggable) build, and that `android:debuggable` is not set; surface known-crash signals from pre-launch report if available.

---

## Misleading store listing / metadata and policy-content violations

**Policy.** [Store Listing and Promotion policies](https://support.google.com/googleplay/android-developer/answer/9898842) and the broader Developer Program Policy. Listings must not be misleading (false claims, fake reviews, irrelevant keywords), must use accurate screenshots/feature graphic, and must not include disallowed content (per the content policies for your category).

**Why apps trip it.** Keyword stuffing in title/description; screenshots that do not reflect the app; claiming features the app lacks; impersonation; restricted content (gambling, financial-services, health, AI-generated/inappropriate content) without meeting that category's policy.

**Fix / avoid.** Keep title/short/full description accurate; use real screenshots and a compliant feature graphic (1024x500, no alpha -- see store-asset-specs.md); meet any category-specific policy; avoid trademarked/competitor terms.

**Audit detection.**
- Lint title/short/full description length and for keyword-stuffing / competitor terms; verify feature graphic and screenshot specs; cross-check declared category against restricted-content policy checklists.

---

## Account-level / financial / new-account scrutiny

**Policy.** New accounts and certain categories (finance, health, crypto, kids) get extra verification. Google may require D-U-N-S / organization verification, and applies the closed-testing gate (above) to new personal accounts.

**Why apps trip it.** Incomplete account verification; sensitive category without the required licensing/declarations; new account hitting the testing gate.

**Fix / avoid.** Complete identity/organization verification early; for regulated categories, gather licensing and complete category declarations before submission.

**Audit detection.** Checklist gating: verification status, category declarations, testing-gate status -- mostly login-gated reads from Play Console.

---

## Quick reference: Google Play top-rejection map

| Policy area | One-line risk | Strong static-audit signal? |
|---|---|---|
| Closed-testing gate (new personal accounts) | < 12 testers or < 14 continuous days before production | Yes (Play Console read) |
| Privacy policy | Missing/broken/mismatched policy URL | Yes (URL + content check) |
| Data safety form | Undeclared collected/shared data; mismatch with binary | Yes (manifest/SDK/endpoint diff) |
| Permissions / sensitive APIs | Unjustified restricted permission; no declaration; no prominent disclosure | Yes (manifest scan) |
| Target API level | targetSdkVersion below current requirement (35) | Yes (manifest read) |
| Artifact format | Not an AAB / unsigned / debuggable | Yes |
| Store listing | Misleading copy/screenshots; restricted content | Partial |
| Account/category scrutiny | Verification or category declarations incomplete | Partial (login-gated) |

---

## Sources

- [App testing requirements for new personal developer accounts (12 testers / 14 days)](https://support.google.com/googleplay/android-developer/answer/14151465)
- [Provide information for Google Play's Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469)
- [Permissions and APIs that Access Sensitive Information](https://support.google.com/googleplay/android-developer/answer/9888170)
- [Target API level requirements for Google Play apps](https://support.google.com/googleplay/android-developer/answer/11926878) and [target SDK guide](https://developer.android.com/google/play/requirements/target-sdk)
- [Prepare your app for review](https://support.google.com/googleplay/android-developer/answer/9859455)
- [Developer Program Policy / Developer Policy Center](https://play.google/developer-content-policy/)
- Secondary: [PrimeTestLab: Google Play app rejection rate 2026](https://primetestlab.com/blog/google-play-app-rejection-rate-2026), [OneMobile: common Google Play rejections](https://onemobile.ai/common-google-play-store-rejections/)

---

## 한국어 요약

- **신규 개인 계정 비공개 테스트 게이트(가장 흔한 차단점)**: 2023-11-13 이후 생성된 개인 계정은 프로덕션 액세스 신청 전 **테스터 12명, 연속 14일** 비공개 테스트가 필요합니다(2024-12-11에 20명에서 12명으로 완화). 조직 계정은 면제입니다.
- **개인정보처리방침 URL 필수**: 활성 HTML URL(PDF 불가), 앱에 특화, 수집 데이터 전부 명시. 끊긴 링크나 데이터 안전 양식과의 불일치는 거절 사유입니다.
- **데이터 안전(Data safety) 양식**: 데이터를 수집하지 않아도 반드시 작성. 2025년 업데이트로 광고 ID 재분류, "공유" 정의 강화, **AAB 자동 검사**로 미신고 데이터 접근 시 사람 심사 전에 차단됩니다.
- **권한/민감 API**: 리스팅에 명시된 현재 기능에 필요한 권한만 요청. 백그라운드 위치, SMS, 전체 파일 접근 등은 사전 선언과 (경우에 따라) 데모 영상이 필요하며, 시스템 권한 요청 전 앱 내 명시적 고지가 필요합니다.
- **타깃 API 레벨**: 2025-08-31 이후 제출은 **Android 15(API 35)** 이상 타깃 필수(Wear/Auto/TV는 API 34). 매년 상향되므로 공식 문서 재확인 필요.
- **배포 형식**: 신규 앱은 **AAB**(서명, 안정 빌드) 필수. APK 업로드, 디버그/미서명 빌드는 거절됩니다.
- Greenlight 자동 점검은 매니페스트 권한, SDK/네트워크 엔드포인트와 데이터 안전 신고 대조, 타깃 SDK, 개인정보처리방침 URL, 스토어 에셋 규격을 정적으로 잡고, 테스트 게이트/계정 인증은 콘솔 로그인 기반으로 확인합니다.
