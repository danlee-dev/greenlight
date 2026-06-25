# Store Asset Specifications (2026)

Exact image requirements for the App Store and Google Play. Dimensions are in **pixels (width x height)**. Always verify the live official references before a release, since Apple adds device classes as new hardware ships:

- Apple: [Screenshot specifications (App Store Connect)](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/)
- Google: [Add preview assets to showcase your app (Play Console)](https://support.google.com/googleplay/android-developer/answer/9866151)

General rule for both stores: screenshots must reflect the actual app in use (Apple 2.3.3), not pure marketing art.

---

## A. Apple App Store

### Format rules (2026)
- Format: **PNG or JPEG**, **RGB color space**, **flattened (no alpha / no transparency)**.
- **Exact pixel dimensions** -- Apple enforces the exact size with no off-by-one tolerance.
- **1 to 10 screenshots** per device class you support (minimum 1, maximum 10).
- You only need to supply the **largest** size in each family; App Store Connect **scales down** to smaller devices if you do not provide their specific assets. Providing the native largest asset is recommended for best rendering.

### iPhone screenshots
| Display class | Required dimensions (portrait) | Notes |
|---|---|---|
| 6.9" (iPhone 17 Pro Max / 16 Pro Max class) | **1320 x 2868** | Primary size most apps lead with in 2026. Landscape = 2868 x 1320. |
| 6.7" (alternative accepted for the 6.9" slot) | **1290 x 2796** | Apple also accepts this for the 6.9" requirement. Landscape = 2796 x 1290. |
| 6.5" (older accepted alternative) | **1242 x 2688** | Accepted as an alternative iPhone size. Landscape = 2688 x 1242. |

In practice for 2026 you supply **one** iPhone set at 1320 x 2868 (or 1290 x 2796 / 1242 x 2688) and Apple scales it to all smaller iPhones. **Verify the currently accepted iPhone slots against the official screenshot-specifications page**, as Apple updates these with new hardware.

### iPad screenshots (required only if the app supports iPad)
| Display class | Required dimensions (portrait) | Notes |
|---|---|---|
| 13" (iPad Pro M4 class) | **2064 x 2752** | Primary iPad requirement. Landscape = 2752 x 2064. |
| 12.9" (older accepted alternative) | **2048 x 2732** | Accepted alternative for the 13" slot. Landscape = 2732 x 2048. |

### App icon (Apple)
- The store icon is delivered **from the app binary's asset catalog**, not uploaded separately as a marketing image. Provide a **1024 x 1024** App Store icon (PNG, no alpha, no transparency, no rounded corners -- Apple applies the mask). Xcode generates the smaller on-device sizes from the asset catalog.

### App previews (optional video)
- 15-30 seconds, per supported device class, resolution matching that device's screenshot resolution.

### Safe-area notes (Apple)
- Avoid placing critical text/UI under the **dynamic island / notch / status bar** region at the top or the **home indicator** region at the bottom of the captured frame.
- If you add marketing overlay text, keep it within the central safe band so it survives down-scaling to smaller devices.

---

## B. Google Play

### Format rules (2026)
- Screenshots: **PNG or JPEG (24-bit, no alpha for the feature graphic specifically)**.
- Screenshots accepted with the **long edge between 320 px and 3840 px**, with the long edge **no more than 2x** the short edge. Aspect ratio commonly **16:9** (landscape) or **9:16** (portrait).
- **2 to 8 screenshots** per supported device type. (At least 2 phone screenshots are required to publish; up to 8 per form factor.)

### Required graphics
| Asset | Dimensions | Format / notes |
|---|---|---|
| App icon | **512 x 512** | 32-bit PNG **with alpha**. Displayed at corners-masked by Play. |
| Feature graphic | **1024 x 500** | PNG or JPEG, **no alpha / no transparency**. Required; shown atop the listing and used for promo placements. |
| Phone screenshots | Long edge **320-3840 px**; portrait commonly **1080 x 1920** | Min 2, max 8. |
| 7" tablet screenshots | Long edge 320-3840 px (e.g. **1200 x 1920**) | Required if you target tablets / claim tablet support. |
| 10" tablet screenshots | Long edge 320-3840 px (e.g. **1600 x 2560**) | Required if you target large tablets. |
| Other form factors | Per device type | Chromebook, Wear OS, Android TV, Android Auto, XR each have their own screenshot slots if you support them. |

### Safe-area notes (Google)
- The **feature graphic** can be partly overlaid by a play button/title text in some surfaces -- keep critical content away from the center and edges; do not rely on the very edges.
- For phone screenshots, keep key content out of the extreme top/bottom where device chrome may be overlaid in previews.

---

## C. Combined required-asset checklist

| Asset | Apple App Store | Google Play |
|---|---|---|
| App/store icon | 1024 x 1024 (from asset catalog, no alpha) | 512 x 512 (32-bit PNG, with alpha) |
| Feature graphic | n/a | 1024 x 500 (no alpha) -- required |
| Primary phone screenshot | 1320 x 2868 (6.9") or 1290 x 2796 / 1242 x 2688 | >= 2 phone shots, e.g. 1080 x 1920 |
| Tablet screenshots | 2064 x 2752 (13") if iPad supported | 7"/10" if tablets supported |
| Min/max screenshots | 1 to 10 per device class | 2 to 8 per device type |
| Color / transparency | RGB, no alpha, flattened | PNG/JPEG; feature graphic no alpha; icon has alpha |
| Preview video | Optional, 15-30s | Optional promo video (YouTube URL) |

---

## D. Audit checks (Greenlight)

- Read each uploaded image's actual pixel dimensions and color mode; assert exact-match for Apple, range-match for Google.
- Flag alpha channel present on Apple screenshots or on the Google feature graphic; flag alpha **absent** on the Google icon.
- Count screenshots per device class against the min/max.
- For Apple, confirm at least the required iPhone size (and iPad size if the app declares iPad support).
- Heuristic: flag a screenshot that is near-uniform color or dominated by a logo (likely a splash/title-only screen, risking Apple 2.3.3).

---

## Sources

- [Apple: Screenshot specifications (App Store Connect)](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/)
- [Apple: Upload app previews and screenshots](https://developer.apple.com/help/app-store-connect/manage-app-information/upload-app-previews-and-screenshots/)
- [Google: Add preview assets to showcase your app](https://support.google.com/googleplay/android-developer/answer/9866151)
- Secondary cross-checks: [MobileAction App Store screenshot sizes (2026)](https://www.mobileaction.co/guide/app-screenshot-sizes-and-guidelines-for-the-app-store/), [PicsSizer Google Play sizes (2026)](https://www.picssizer.com/app-store-sizes/google-play)

---

## 한국어 요약

- **Apple 스크린샷**: PNG/JPEG, RGB, **알파 없음**, **정확한 픽셀(오차 불허)**, 기기 클래스당 1-10장. 가장 큰 사이즈만 올리면 작은 기기로 자동 축소됩니다.
- **iPhone**: 6.9형 **1320 x 2868**(대안 1290 x 2796, 1242 x 2688). **iPad**(앱이 지원할 때만): 13형 **2064 x 2752**(대안 2048 x 2732).
- **Apple 아이콘**은 별도 업로드가 아니라 에셋 카탈로그의 **1024 x 1024**(알파/둥근 모서리 없음)에서 가져옵니다.
- **Google 아이콘 512 x 512**(32비트 PNG, **알파 포함**), **피처 그래픽 1024 x 500**(**알파 없음**, 필수).
- **Google 스크린샷**: 긴 변 320-3840px, 긴 변이 짧은 변의 2배 이하, 기기 유형당 2-8장(폰 최소 2장). 폰은 보통 1080 x 1920.
- 안전 영역: 다이내믹 아일랜드/노치/홈 인디케이터(Apple), 피처 그래픽 중앙·가장자리 오버레이(Google)를 피해 핵심 요소를 배치합니다.
- 새 기기 출시에 따라 규격이 갱신되므로 공식 문서를 항상 재확인하세요.
