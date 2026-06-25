---
name: app-review-guidelines
description: Knowledge base of App Store and Google Play review guidelines, common rejection reasons, submission flows, and 2026 policy changes. Use when auditing an app before submission, diagnosing a rejection, or checking store asset specs.
---

# App Review Guidelines (App Store + Google Play, 2026)

A factual reference base for **Greenlight**, the open-source tool that helps developers pass App Store and Google Play review. It captures the guideline section numbers, the rejection patterns that actually cause rejections, the exact asset specifications, the end-to-end submission flows, and the 2026 policy shifts (third-party AI disclosure and the "vibe coding" / low-value-app crackdown).

Use this skill to:
- **Audit an app before submission** -- walk the rejection lists and asset specs as a pre-flight checklist.
- **Diagnose a rejection** -- map a cited guideline section (Apple) or named policy (Google) to cause and fix.
- **Check store asset specs** -- confirm exact pixel sizes and format rules per device class.
- **Understand the submission flow** -- know which steps are public vs login-gated, and where a browser/API automation can read live state.

Authoritative sources are Apple's [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) (last updated **February 6, 2026**) and Google's [Play Console Help](https://support.google.com/googleplay/android-developer) / [Developer Program Policy](https://play.google/developer-content-policy/). Guidelines change several times a year; the reference files note where to re-verify against the live source.

## How to use this skill

1. Identify the task: pre-submission audit, rejection diagnosis, asset check, or flow question.
2. Open the matching reference file below.
3. For rejection items, each entry gives **the rule/section, why apps trip it, how to fix it, and how an automated audit can detect it** -- use the "audit detection" notes to drive Greenlight checks.
4. When a fact is high-stakes (a pixel size, a section number, a regional payment rule), follow the linked official source; the files flag anything that should be re-verified.

## Table of contents

| Reference file | What it covers |
|---|---|
| [references/apple-rejections.md](references/apple-rejections.md) | Apple's top rejection reasons with exact section numbers: 2.1 completeness/crashes, 2.3 / 2.3.3 / 2.3.7 / 2.3.10 metadata + screenshots, 3.1.1 / 3.1.1(a) / 3.1.3 payments, 4.2 minimum functionality, 4.3(a)/(b) spam, 5.1.1 privacy, 5.1.2(i) third-party AI, 2.5.2 executable code (2026 vibe-coding enforcement). |
| [references/google-rejections.md](references/google-rejections.md) | Google Play rejection reasons: the 12-testers/14-day closed-testing gate for new personal accounts, privacy policy, Data safety form, permissions justification, target API level (35), AAB/signing, store-listing policy. |
| [references/submission-flow.md](references/submission-flow.md) | Numbered end-to-end submission steps for App Store Connect and Google Play Console, each tagged public vs login-gated, with notes on where a Playwright session or official API can read live state. |
| [references/store-asset-specs.md](references/store-asset-specs.md) | Exact 2026 image sizes for both stores: iPhone 6.9" 1320x2868 (also 1290x2796), iPad 13" 2064x2752, Google feature graphic 1024x500 (no alpha), icons, phone screenshot sizes, and safe-area notes. |
| [references/privacy-and-ai-2026.md](references/privacy-and-ai-2026.md) | Apple privacy nutrition labels + PrivacyInfo.xcprivacy manifest and Required Reason APIs, Google Data safety, the 2026 third-party-AI disclosure rule (5.1.2(i)), and the vibe-coding / low-value-app crackdown (2.5.2, 4.3(b), 4.2). |

## 2026 changes at a glance

- **Apple 5.1.2(i) (added Nov 13, 2025; in force 2026):** sharing personal data with **third-party AI** now requires clear in-app disclosure (naming the provider) and explicit consent.
- **Apple 2.5.2 enforcement (from ~March 2026):** "vibe coding" apps that download/execute code to change themselves at runtime are being rejected/pulled as not self-contained (e.g. Replit, Vibecode update blocks; the app "Anything" pulled).
- **Apple 4.3(b):** saturated-category list now includes **drinking games**; mass-produced low-value apps face a higher bar.
- **Google target API level:** new apps/updates after Aug 31, 2025 must target **Android 15 (API 35)**; Play Console runs **automated AAB checks** that flag undeclared data access before human review.
- **Google closed-testing gate:** new **personal** accounts need **12 testers for 14 consecutive days** before production (reduced from 20 testers on Dec 11, 2024).

## 한국어 요약

- 본 스킬은 오픈소스 도구 **Greenlight**를 위한 App Store/Google Play 심사 기준 지식베이스로, 거절 사유(섹션 번호 포함), 제출 절차, 에셋 규격, 2026년 정책 변화를 정리합니다.
- 용도: 제출 전 점검, 거절 원인 진단, 스토어 에셋 규격 확인, 제출 절차(공개 vs 로그인 단계) 파악.
- 참조 파일은 apple-rejections.md, google-rejections.md, submission-flow.md, store-asset-specs.md, privacy-and-ai-2026.md 5개이며, 각 거절 항목은 규칙/섹션, 발생 이유, 해결법, 자동 점검 방법을 함께 제공합니다.
- 2026년 핵심 변화: Apple 5.1.2(i)(서드파티 AI 데이터 공유 공개·동의), 2.5.2 "바이브 코딩" 단속, 4.3(b) 양산형 앱 강화, Google API 35 타깃·AAB 자동 검사, 신규 개인 계정 12명/14일 비공개 테스트 게이트.
- 픽셀 규격·섹션 번호·결제 규정 등 중요한 사실은 각 파일에 링크된 공식 출처(developer.apple.com, support.google.com)로 재확인하세요(가이드라인은 연중 수회 변경됨).
