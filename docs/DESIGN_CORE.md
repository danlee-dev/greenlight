# Greenlight Design Core

This is the design system for everything Greenlight renders: the local cockpit
UI and the store screenshot templates. It exists to make our output look
deliberately designed, not machine-emitted. Claude Code MUST read and apply this
file when building or editing any UI or rendered asset.

Apply the "Design Core" below to every surface. For the cockpit, also apply
"Module: UI web". For any in-app or device-framed mock, apply "Module: UI app".
Screenshot marketing layouts may borrow from "Module: Editorial".

Hard rule for this repo: no emojis anywhere in code, comments, docs, rendered
assets, or UI. Use icon fonts (Phosphor / Lucide with a changed weight) or
inline SVG instead.

---

## Design Core (always apply)

You are not a machine that auto-emits a design; you are a designer making
deliberate decisions for THIS brand, content, and audience. Before generating,
consciously decide the four items below and start from them. Do not converge on
the most common default template (the statistical median) of training data.
Good design comes from restraint and intentional choices, not from stacking more
effects.

Decide before generating (state briefly, then design):
1. The single accent color and why. Greenlight default accent is a confident
   green (go / approved). On a neutral base, only this one color carries emphasis.
2. The type pairing (display + body + mono) and why.
3. The ONE layout primitive repeated across the whole job (this is the signature).
4. The base grid / spacing unit.

Font system (required):
- Korean text: always Pretendard, letter-spacing -0.025em, scoped to Korean only.
  Load via CDN in the head:
  `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css`
  family: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif
- English text: do NOT use default Inter. Use an editorial / distinctive pairing.
  Greenlight cockpit default: display Archivo, body Hanken Grotesk, mono JetBrains Mono.
- Language scoping when mixed: `:lang(ko), .ko { font-family: var(--font-ko); letter-spacing:-0.025em; }`.
  For Latin words inside Korean runs, put the Latin face first then Pretendard in one stack.
- Load fonts via CDN in the HTML; do not rely on a tool font dropdown.

Typography craft:
- Real modular scale (no near-equal sizes). UI ratio ~1.25 (12/14/16/20/24/32/40/48px).
- Tracking: negative on large display (-0.02 to -0.03em), normal body, positive only on
  small uppercase labels (+0.05 to +0.08em). Korean is -0.025em.
- Line-height ~1.5 body, 1.1-1.3 display. Body measure 45-75 chars (max-width: 65ch).
- Weight contrast at the extremes (heading 700/800 + body 400). Use tabular-nums for
  numbers, tables, and metrics.

Color:
- 60-30-10: ~60% neutral surface + 30% secondary + 10% single accent. Accent only on
  emphasis / primary actions; it earns meaning through scarcity.
- No competing multi-accent or rainbow palettes. No purple/indigo gradients, no gradient
  text. Text is solid.
- Build dark/full-bleed sections only from the brand accent or a refined warm near-black
  (the #1a1a1a family). Do not converge on the default navy / slate-blue startup-deck
  background. Unless a dark surface is truly required, white / off-white + one accent is safer.
- Contrast WCAG AA: 4.5:1 body, 3:1 large text / UI components.

Layout / spacing:
- 8pt grid (8/16/24/32/48/64). Align to shared edges/baseline. Whitespace is structure:
  tight within groups, generous between sections.
- Tokenize lines and gaps: one line color + one line weight (`--line`, `--line-w`); spacing
  from 8pt tokens only. Apply the same rules everywhere.
- Keep column dividers/gutters symmetric. Use minmax(0,1fr) to prevent overflow.
- Repeat the one chosen layout primitive as the signature. Do not stack a different card
  style on every screen.

Backgrounds / assets (tasteful version only):
- The #1 AI tell is the high-chroma purple/indigo mesh + floating glow orbs. Every tasteful
  version is single-hue + low-chroma + low-alpha + grain, sitting behind content. Build
  structure from grids/grain, not color.
- Allowed: single-hue near-tonal wash; one subtle edge-anchored radial glow (alpha 0.12-0.25)
  + grain; grain overlay (inline SVG feTurbulence, opacity <=0.05); edge-masked dot/line grid
  (line opacity 5-10%); oversized brand glyph as texture at 6-10% opacity.
- Forbidden: multi-hue/rainbow mesh, floating saturated orbs, fast rainbow aurora, motion
  behind body text.
- Icons instead of emoji: prefer Phosphor (thin/regular). Default-weight Lucide on a default
  palette reads as AI; change the weight/color. Load via CDN webfont, commit to one weight.
- Motion: 150-300ms, transform/opacity only, respect prefers-reduced-motion. No
  animate-everything-on-scroll.

Forbidden (AI reflexive tells, never do these):
- Wide-tracked uppercase eyebrow/kicker stacked above every heading as decoration.
- Translucent / glassmorphic rounded button or pill stat chips with a number inside.
- Callout/alert card with a thick colored left border + rounded corners + tinted background
  (border-l-4 + rounded + bg-x-50). This is the number one AI tell.
- Fake live indicators (pulsing green dot, "Live") where nothing is live.
- Purple/indigo/pink gradients, gradient text, colored glow backgrounds.
- Emoji as icons/bullets/decoration anywhere.
- Three identical feature cards (rounded icon tile + heading + one line) repeated.
- Cards nested in cards, excessive radius on everything, a 1px border + heavy drop shadow on
  the same element.
- Generic centered hero + two buttons + badge above the H1.
- "Trusted by" logo strip, reflexive bento grid, stock 3D spheres/beams as filler.
- Buzzword copy (streamline, empower, supercharge, world-class, all-in-one), em-dash overuse.

Allowed (the tasteful version, only with a reason):
- Pull-quote: a thin 1-2px left rule only, no radius, no fill. Or large type + whitespace.
- Highlighter emphasis: mark only the single most important phrase per section, sparingly,
  one color, as a real marker covering the lower part of the line:
  `background: linear-gradient(transparent 58%, rgba(accent,.5) 58%); padding:0 .04em;
  box-decoration-break: clone;`. Not a flat full-height pill.
- Section numbers (01/02) only when genuinely a sequence.
- Glass only when there is a real z-axis layering relationship.

Output:
- Self-contained single HTML where possible (renders with no build step). Font CDN in head.
- Before generating, write the four "Decide before generating" items in 1-2 lines, then design.

---

## Module: UI web (the cockpit)

This is a web UI (a local dashboard / cockpit). 

Layout / density:
- 12-column grid + consistent gutters, 8pt spacing. Web can be denser, but keep whitespace as
  structure. Pick one layout primitive and repeat it. Single focal point per section. Pass the
  squint test.

Components / states:
- Card radius 12-16px (no excessive rounding); choose a defined edge OR a soft elevation, not
  both. Design hover/focus/active/disabled. Visible focus ring.
- Data tables/metrics use tabular-nums, direct labels, restrained chart color.
- Motion 150-300ms, eased, respect prefers-reduced-motion.

Color / a11y: 60-30-10, single accent, WCAG AA.

Recommended fonts: Korean Pretendard; English display Space Grotesk or Archivo; body Hanken
Grotesk / Public Sans / IBM Plex Sans; mono JetBrains Mono.

Hard forbid: thick colored left-border + rounded + tinted alert card, frosted glass stat
chips, fake pulsing live dot, purple/indigo gradients, three identical feature cards, nested
cards, generic centered hero + two buttons + badge, "Trusted by" strip, reflexive bento,
emoji icons.

---

## Module: UI app (device-framed mocks)

Mobile differs from web: minimal, single-column, thumb-first.
- Single-column vertical stack, lower density, one task per screen. 8pt spacing.
- Navigation: bottom tab bar or nav stack. Primary actions in the bottom thumb arc.
- Touch targets min 44x44pt (Apple) / 48x48dp (Material). Respect safe-area insets. No hover;
  design press/touch states.
- Card radius 12-16px; defined edge OR soft elevation, one only. Motion 120-300ms eased.
- 60-30-10, single accent, WCAG AA, tabular-nums for data.
- Hard forbid: glass stat chips, thick colored left-border tinted cards, fake live dots,
  purple gradients, emoji icons/tab bars, excessive rounding, border + heavy shadow together.

---

## Module index (full pack)

The author maintains a larger prompt pack. Modules available to pull when a surface calls for
it: 1) Academic talk (EN), 2) Academic talk (KO), 3) IR/startup pitch (EN), 4) IR/startup
pitch (KO), 5) General presentation, 6) Competition/demo, 7) UI web (above), 8) UI app
(above), 9) Editorial / fashion / branding (expressive). For store screenshot marketing
layouts, Module 9 (editorial: full-bleed, oversized type, grain, staggered composition,
overlap type onto a real screen capture) is the right reference, with the same forbidden list.

One-sentence rule: default Lucide + shadcn zinc + Inter + 0.5rem radius + a decorative 3D blob
+ animate-everything-on-scroll = the AI fingerprint. Break any two and it stops reading as AI.
