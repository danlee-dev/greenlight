# End-to-End Submission Flow: App Store Connect and Google Play Console (2026)

This file walks both submission pipelines step by step. Each step is tagged:

- **[PUBLIC]** -- documented, knowable without an account (we can describe and lint against it).
- **[LOGIN]** -- happens behind the developer account login; an automated tool needs the developer's authenticated session (e.g. an authenticated Playwright browser session, or the App Store Connect API / Google Play Developer API) to read or act on it.

Where a Playwright-driven browser can usefully read the live console state, it is called out as **[PLAYWRIGHT-READABLE]**.

---

## A. App Store Connect (iOS / iPadOS)

Prerequisite: enrollment in the Apple Developer Program (USD 99/year), an App ID / bundle ID, and signing set up. The official references are [App Store Connect workflow](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow) and [Submit an app](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/).

1. **[PUBLIC]** Enroll in the Apple Developer Program and accept the latest agreements (Paid Apps agreement if charging). Configure App Store Connect account roles and, for paid apps, banking/tax in Agreements, Tax, and Banking.
2. **[LOGIN]** **Register the bundle ID** in Certificates, Identifiers & Profiles (or let Xcode manage it).
3. **[LOGIN]** **Create the app record** in App Store Connect -> Apps -> "+" -> New App. Required fields: **platform, app name, primary language, bundle ID, SKU**, and user access. The name must be unique and <= 30 characters. **[PLAYWRIGHT-READABLE]** -- the Apps list and a record's status are visible here.
4. **[PUBLIC]** **Build and archive** the app in Xcode (Release configuration), incrementing version (CFBundleShortVersionString) and build number (CFBundleVersion). Include the `PrivacyInfo.xcprivacy` manifest (see privacy-and-ai-2026.md).
5. **[LOGIN]** **Upload the build** via Xcode Organizer ("Distribute App") or the **Transporter** Mac app (drag-and-drop the `.ipa`). Apple runs automated processing (minutes to ~1 hour); the build then appears under the app record. **[PLAYWRIGHT-READABLE]** -- build processing state shows in the TestFlight / Build sections.
6. **[LOGIN]** (Optional but recommended) **TestFlight** beta: distribute to internal/external testers; external testing requires a Beta App Review.
7. **[LOGIN]** **Complete the version's App Store information**: description, keywords, support URL, marketing URL (optional), promotional text, category, age rating questionnaire, and **upload screenshots/app previews** (at minimum the required device sizes -- see store-asset-specs.md). Attach the processed build to the version. **[PLAYWRIGHT-READABLE]** -- each field's filled/empty state and validation errors are visible.
8. **[LOGIN]** **App Privacy ("nutrition label")**: complete the data-collection questionnaire (data types, linkage, tracking). You cannot submit without this. Add the **privacy policy URL**.
9. **[LOGIN]** **Compliance questionnaires (legally binding)** answered at submission: **Export Compliance** (encryption), **Content Rights** (rights to third-party content), and **Advertising Identifier / IDFA** (whether you use IDFA and why).
10. **[LOGIN]** **Pricing and Availability**: set price tier (or free) and territory availability.
11. **[LOGIN]** **Add for Review -> Submit for Review.** Choose to add the version to a new or existing submission; optionally include in-app events, IAPs, or custom product pages in the same submission. Add **App Review notes** (demo account credentials, anything the reviewer must know). Status moves Ready for Review -> In Review. **[PLAYWRIGHT-READABLE]** -- submission status is the main thing a browser flow would poll.
12. **[PUBLIC/LOGIN]** **Review outcome**: typically ~24-48 hours (often <1 day in 2026). On approval, choose **manual** or **automatic** release (or phased release for an update). On rejection, Apple cites the guideline section in Resolution Center; respond or resubmit. After approval it can take up to ~24 hours to appear on the store.

Automation note: App Store Connect also exposes an **App Store Connect API** (JWT-authenticated REST) for most of steps 3-12; prefer it over browser automation where possible. A Playwright session is mainly useful for reading live status and fields that the API does not expose, or for visual verification of the listing.

---

## B. Google Play Console (Android)

Prerequisite: a Google Play Developer account (one-time USD 25), identity verification, and a signed **AAB**. Official references: [Prepare your app for review](https://support.google.com/googleplay/android-developer/answer/9859455) and [Control when app changes are reviewed and published](https://support.google.com/googleplay/android-developer/answer/9859654).

1. **[PUBLIC]** Create the Play Developer account, complete **identity (and, for orgs, D-U-N-S/organization) verification**, and accept the Developer Distribution Agreement. New accounts face extra verification.
2. **[LOGIN]** **Create app** in Play Console -> "Create app". Provide: **app name (<= 30 chars), default language, app or game, free or paid**, and acknowledge the Developer Program Policies and US export laws. **[PLAYWRIGHT-READABLE]** -- the app list and creation form.
3. **[LOGIN]** **Dashboard "Set up your app" tasks** (each must be completed; incomplete tasks block publishing): app access (login instructions/credentials for review), ads declaration, content ratings (IARC questionnaire), target audience and content, news-app declaration, COVID/contact-tracing declaration if applicable, **Data safety form**, **privacy policy URL**, and government-app / financial-features declarations as relevant. **[PLAYWRIGHT-READABLE]** -- each task shows a completed/incomplete state.
4. **[LOGIN]** **Main store listing**: app name, short description (<= 80 chars), full description (<= 4000 chars), **app icon (512x512)**, **feature graphic (1024x500, no alpha)**, **phone screenshots** (and tablet/other form factors if supported), optional promo video. See store-asset-specs.md.
5. **[PUBLIC]** **Build a signed AAB** targeting the current required API level (35 as of this writing) and enroll in **Play App Signing**.
6. **[LOGIN]** **Closed testing (mandatory for new personal accounts)**: create a Closed testing track, upload the AAB, add **>= 12 testers**, distribute the opt-in link, and run the test **14 consecutive days**. (See google-rejections.md.) **[PLAYWRIGHT-READABLE]** -- tester counts and track status are visible; this is the key gate a browser flow would verify.
7. **[LOGIN]** **Apply for production access** (new personal accounts) after the 14-day window with 12+ opted-in testers; await Google approval.
8. **[LOGIN]** **Create a production release**: Release -> Production -> "Create new release". Upload (or promote) the AAB, set the release name and **release notes**, and review the pre-launch report / warnings.
9. **[LOGIN]** **Set rollout countries/regions** and (optionally) a **staged rollout** percentage.
10. **[LOGIN]** **Send for review** / **Save and publish**. Note Play Console's "Save for later" lets you stage some changes without submitting them. The release enters review; status shows In review -> then rolls out. **[PLAYWRIGHT-READABLE]** -- release/review status is the main poll target.
11. **[PUBLIC/LOGIN]** **Review outcome**: usually 1-3 days (longer for new accounts or sensitive categories). Rejections name the violated policy in the Policy status / inbox; fix and resubmit. After approval, the staged rollout proceeds to the configured percentage/regions.

Automation note: Google also offers the **Google Play Developer Publishing API** (edits-based) for uploading bundles, updating listings, and managing tracks/rollouts; prefer it over browser automation. A Playwright session is most useful for reading the **closed-testing tester count / 14-day status**, the per-task completion state on the dashboard, and the live review/policy status, which are convenient to read visually.

---

## Side-by-side: what gates a first submission

| Stage | App Store Connect | Google Play Console |
|---|---|---|
| Account cost | USD 99/year | USD 25 one-time |
| Mandatory pre-review testing | None required (TestFlight optional) | New personal accounts: closed test, 12 testers, 14 days |
| Artifact | `.ipa` via Xcode/Transporter | signed `.aab` |
| Privacy disclosure | App Privacy nutrition label + privacy policy URL + PrivacyInfo.xcprivacy | Data safety form + privacy policy URL |
| Binding questionnaires | Export, Content Rights, IDFA | Content rating (IARC), ads, target audience, data safety |
| Typical review time | ~24-48h | 1-3 days |
| Release control | Manual / automatic / phased | Staged rollout %, regions; "Save for later" |

---

## Sources

- [App Store Connect workflow](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow)
- [Overview of submitting for review (App Store Connect)](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/overview-of-submitting-for-review/)
- [Submit an app (App Store Connect)](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/)
- [Prepare your app for review (Play Console)](https://support.google.com/googleplay/android-developer/answer/9859455)
- [Control when app changes are reviewed and published (Play Console)](https://support.google.com/googleplay/android-developer/answer/9859654)
- [App testing requirements for new personal developer accounts](https://support.google.com/googleplay/android-developer/answer/14151465)

---

## 한국어 요약

- 본 문서는 각 단계를 **[PUBLIC]**(계정 없이 알 수 있음)와 **[LOGIN]**(개발자 계정 로그인 필요)으로 구분하고, 브라우저(Playwright)로 라이브 상태를 읽을 수 있는 지점을 **[PLAYWRIGHT-READABLE]**로 표시합니다.
- **App Store Connect**: 앱 레코드 생성(이름 30자 이하, bundle ID/SKU) -> Xcode/Transporter로 `.ipa` 업로드/처리 -> 버전 정보·스크린샷·App Privacy 라벨·개인정보 URL 입력 -> 수출/콘텐츠권리/IDFA 질문 -> Submit for Review. 심사는 보통 24-48시간이며 승인 후 수동/자동/단계 출시 선택.
- **Google Play Console**: 계정/신원 인증 -> 앱 생성(이름 30자 이하) -> 대시보드 설정 작업(앱 접근·콘텐츠 등급·데이터 안전·개인정보 URL 등) -> 스토어 리스팅(아이콘 512, 피처 그래픽 1024x500) -> 서명된 AAB.
- **신규 개인 계정**은 프로덕션 전에 **테스터 12명 / 14일 연속 비공개 테스트**를 통과하고 프로덕션 액세스 신청·승인을 받아야 합니다(핵심 게이트).
- 프로덕션 릴리스 생성 -> 출시 국가/단계 롤아웃 설정 -> 심사 제출(보통 1-3일). 거절 시 정책명을 명시하므로 수정 후 재제출.
- 자동화는 가급적 **App Store Connect API**와 **Google Play Developer Publishing API**를 우선 사용하고, Playwright는 주로 비공개 테스트 인원/14일 상태, 작업 완료 상태, 심사 상태 등 라이브 상태 읽기에 활용합니다.
