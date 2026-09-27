# Golden Example — Mostar Guide Full Prototype Build Prompt

This is the canonical golden example for `skills_UIUX/prompt-compiler/`.

It demonstrates what a strong compiled specification looks like when an existing visual prototype has a protected animation core and must be expanded without contaminating that core.

The important lesson is the **structure and evidence discipline**, not the Mostar domain itself.

---

# Mostar City — Full Prototype Build Prompt

> **Goal:** preserve the cinematic scroll homepage as the protected experience core while extending the project into a complete static multi-page prototype that can deploy directly to GitHub Pages or Vercel without a build step.
>
> **Mode:** specification / controlled extension.
>
> **Responsive scope:** responsive_all.
>
> **Core preservation:** animation engine and cinematic choreography are protected.

---

## 0. Immutable principles

All extension work is additive unless a specific exception is named below.

Preserve:

- remote asset policy for the Ogg Medium font, seven scene PNG assets and three pin-icon PNG assets;
- the existing cinematic DOM hierarchy rooted at `main.site-shell > section.cinema-scroll#cinema > div.stage` and its source-order paint behavior;
- existing `:root` custom properties and layer ownership for `.sky-img`, `.back-stack`, `.hero-title`, `.bridge-img`, `.splitframe-img`, `.frame-two-img`, `.shade`, `.intro-copy`, `.story-panel`, `.sights-slider`, `.sights-controls`;
- the existing responsive rules at 1500px / 1100px / 640px and `prefers-reduced-motion` behavior;
- the animation engine functions `clamp`, `smoothstep`, `lerp`, `segmentInOut`;
- protected scroll ranges 560–1620, 1760–2700, 2760–3560 and 3360–3660;
- the infinite slider model using three cloned sets, the `is-jumping` state, and `normalizeSightSlider`;
- the five-stage cinematic choreography and its scrub behavior.

New behavior must live in isolated files/scopes where practical. Do not rewrite the core animation engine merely to support secondary pages.

Evidence state:

- existing selectors/functions/ranges: `VERIFIED` from the source project;
- new routes/page architecture below: `PROPOSED` extension contract.

---

## 1. Current gaps to resolve before expansion

### 1.1 Bridge anchor

CURRENT: the navigation exposes a `#bridge` destination.

PROBLEM: the bridge story section does not expose the matching `id`.

IMPACT: direct navigation and keyboard navigation do not resolve to the intended content owner.

PROPOSED RESOLUTION: add `id="bridge"` to `section.story-panel-bridge` without changing its class list or DOM position.

### 1.2 Bazaar anchor

CURRENT: the navigation exposes a `#bazaar` destination.

PROBLEM: the bazaar story section does not expose the matching `id`.

PROPOSED RESOLUTION: add `id="bazaar"` to `section.story-panel-bazaar` without changing its class list or DOM position.

### 1.3 Routes destination

CURRENT: navigation exposes `#routes`, but the cinematic homepage has no matching route/section.

PROBLEM: the intended itinerary content has no owner and does not naturally belong to the protected 3700px cinematic sequence.

PROPOSED RESOLUTION: create a separate `routes.html` page and change the Routes nav destination to that relative file.

---

## 2. Target static site structure

```text
mostar/
├── index.html
├── styles.css
├── script.js
├── routes.html
├── routes.css
├── routes.js
├── shared/
│   ├── nav.css
│   ├── nav.js
│   └── footer.css
├── assets/
│   └── favicon.svg
├── vercel.json
├── robots.txt
├── sitemap.xml
├── .github/
│   └── workflows/
│       └── deploy-pages.yml
└── README.md
```

Architecture rules:

- vanilla HTML/CSS/JS only;
- no bundler;
- no framework;
- each page loads direct relative CSS/JS assets;
- internal project links use relative paths so the project remains compatible with a GitHub Pages project subpath;
- `routes.html` must not import cinematic `styles.css` or `script.js`.

---

## 3. New page — `routes.html` / Suggested routes

### Purpose

Give visitors a practical continuation after the cinematic introduction without extending or destabilizing the protected homepage timeline.

### User goal

Choose a short Mostar walking route based on available time and interest.

### Page structure

1. shared header;
2. short route hero;
3. three static route articles;
4. simple footer with return link.

### Header

Reuse the semantic structure of `header.site-header`.

Content:

- logo: `Bosnia and Herzegovina`;
- Intro → `index.html#cinema`;
- Bridge → `index.html#bridge`;
- Bazaar → `index.html#bazaar`;
- Routes → `routes.html`;
- language indicator: English.

The route page may add `.site-header--static` to opt into static/sticky positioning without changing homepage header behavior.

### Hero

```text
H1: Suggested routes
Subtext: Choose a compact way to experience Mostar by time, heritage or light.
```

### Route 01 — Old Bridge morning loop

- duration: ~1.5 hours;
- stops: 4;
- ordered stops:
  1. Stari Most;
  2. Kujundžiluk;
  3. Koski Mehmed Pasha Mosque;
  4. riverside coffee stop.

### Route 02 — Ottoman heritage walk

- duration: ~2.5 hours;
- stops: 5;
- include Kajtaz House and the War Photo Exhibition among the itinerary stops;
- preserve a logical walking order rather than presenting an unordered place list.

### Route 03 — Golden hour crossing

- duration: ~1 hour;
- stops: 3;
- optimize content and route framing around late-afternoon / golden-hour light.

### Route card semantics

Each route is an `<article>` with:

- visible `h2`;
- duration;
- stop count;
- `<ol>` for ordered stops;
- one of the existing pin-icon assets used as route/stop illustration.

Do not replace semantic headings/lists with generic `div` structures.

### Motion

No cinematic engine on this page.

Allowed enhancement:

- lightweight IntersectionObserver fade/reveal;
- no dependency on `segmentInOut`;
- reduced motion must remove the reveal transition cleanly.

---

## 4. Shared navigation contract

Move/reuse only the shared header styling needed by both pages in `shared/nav.css`.

Shared selectors include:

- `.site-header`;
- `.site-logo`;
- `.site-nav`;
- `.language-switcher`.

Rules:

- homepage DOM location remains unchanged;
- `shared/nav.css` loads before homepage `styles.css` so cinematic-specific styling may still override shared defaults;
- `routes.html` uses `.site-header--static` or equivalent isolated modifier;
- route navigation uses relative links;
- homepage Bridge/Bazaar navigation must land on useful cinematic checkpoints without modifying the protected core animation engine.

If a small helper such as `shared/nav.js` is required for mapping a hash destination to a scroll checkpoint, it must be additive and must not alter `script.js`.

---

## 5. Visual direction for the extension

### Art direction

Three adjectives:

```text
cinematic / editorial / warm-historic
```

### Preserve

- `--ink: #111411`;
- `--paper: #fdf1e1`;
- dark background family around `#0b1110`;
- Ogg Medium display typography for headings;
- existing Mostar imagery/pin visual language.

### Routes page composition

The secondary page should feel editorial and useful rather than becoming a generic SaaS card grid.

Use:

- strong title hierarchy;
- large breathing room;
- structured route information;
- restrained dividers/borders;
- content-led composition;
- subtle focus/hover affordances.

### Anti-template rules

Do not add:

- generic glassmorphism;
- neon/AI gradients;
- universal rounded cards with identical shadows;
- decorative animation on every section;
- unrelated icon libraries;
- stock travel imagery that breaks the current visual language.

---

## 6. Deployment — GitHub Pages

All internal project paths must remain relative.

Add `.github/workflows/deploy-pages.yml` using GitHub Pages Actions:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
```

README must explain that repository Settings → Pages should use `GitHub Actions` as the source when first enabling Pages.

Production deploy success must be verified from workflow evidence; configuration presence alone is not deploy PASS.

---

## 7. Deployment — Vercel

Add:

```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

Document:

- Framework preset: Other;
- no build command;
- output directory: project root (`.`);
- no SPA rewrite because the site is static multi-page HTML.

---

## 8. SEO and metadata

Add without removing existing charset/viewport/title/description/favicon metadata:

```html
<meta property="og:title" content="Mostar city" />
<meta property="og:description" content="A cinematic three-screen scroll story for Mostar city." />
<meta property="og:type" content="website" />
<meta name="theme-color" content="#0b1110" />
```

Add basic:

- `robots.txt`;
- `sitemap.xml` containing homepage and Routes page;
- favicon asset when used.

Do not use absolute-root internal asset paths that break under `/Mostar-Guide/` on GitHub Pages.

---

## 9. Accessibility extension

### Homepage

Add as the first body child:

```html
<a class="skip-link" href="#cinema">Skip to content</a>
```

The skip link must live outside pointer-event-heavy cinematic layers.

Keep focus visibility.

Bridge/Bazaar destinations must be keyboard-reachable through valid navigation targets.

### Routes

Requirements:

- route card = `<article>`;
- route name = `h2`;
- stop sequence = `<ol>`;
- links/buttons have visible focus;
- motion respects `prefers-reduced-motion`;
- body text maintains readable contrast on dark/paper surfaces.

---

## 10. QA contract

### Core regression

- [ ] protected `script.js` preservation is verified at the required level (prefer blob/hash equality when byte-for-byte preservation is the declared contract);
- [ ] five-stage choreography remains correct through representative scroll checkpoints;
- [ ] infinite slider still contains three logical cloned sets and normalizes correctly;
- [ ] slider controls activate at their intended final-stage checkpoint rather than being tested too early;
- [ ] reduced-motion behavior remains intact.

### Navigation

- [ ] `#bridge` reaches the intended bridge checkpoint/content owner;
- [ ] `#bazaar` reaches the intended bazaar checkpoint/content owner;
- [ ] Routes opens the separate `routes.html` page;
- [ ] all internal links work from the GitHub Pages project subpath.

### Routes page

- [ ] page opens without importing cinematic `script.js`;
- [ ] exactly three route articles render;
- [ ] route stop counts are 4 / 5 / 3;
- [ ] ordered stops use `<ol>`;
- [ ] shared nav/footer render without CSS collision.

### Media

- [ ] Ogg font and required remote scene/icon assets resolve;
- [ ] no project-owned 404s;
- [ ] images have non-zero natural dimensions.

### Responsive

Representative verification at mobile and desktop pressure points:

- [ ] no accidental horizontal overflow;
- [ ] navigation remains usable;
- [ ] route content reflows intentionally;
- [ ] cinematic composition does not introduce new clipping outside the existing accepted behavior.

### Accessibility

- [ ] no serious/critical Axe violations on representative routes;
- [ ] Lighthouse Accessibility target ≥ 90 when measured;
- [ ] focus and skip-link behavior works;
- [ ] reduced-motion behavior works.

### Deployment

Only when release is authorized:

- [ ] GitHub Pages workflow succeeds;
- [ ] production URL loads;
- [ ] Vercel static configuration is valid when Vercel release is in scope.

---

## 11. Deliverables

Expected implementation deliverables:

```text
index.html
styles.css
script.js
routes.html
routes.css
routes.js
shared/nav.css
shared/nav.js (only if required)
shared/footer.css
assets/favicon.svg
vercel.json
.github/workflows/deploy-pages.yml
robots.txt
sitemap.xml
README.md
```

Protected core files must only contain the specifically permitted additive changes.

---

## 12. Definition of Done

The extension is DONE only when:

- [ ] the homepage cinematic behavior is preserved at its declared preservation level;
- [ ] Bridge/Bazaar navigation resolves correctly;
- [ ] Routes exists as an independent static page;
- [ ] the new page follows the existing visual system without importing the cinematic engine;
- [ ] responsive scope has been rendered and inspected;
- [ ] accessibility checks meet the declared budget;
- [ ] required remote assets are healthy;
- [ ] deployment configuration matches static hosting constraints;
- [ ] production smoke is complete when release authority includes deploy;
- [ ] any unverified item is reported as UNKNOWN/BLOCKED rather than silently marked PASS.

---

## Why this is the golden example

This specification is useful because it does all of the following at once:

1. names exact protected owners instead of saying “keep the old animation”;
2. separates existing verified truth from proposed extension architecture;
3. defines a new page without contaminating the core engine;
4. turns UX intent into file-level and selector-level implementation constraints;
5. includes deployment/base-path realities, not only visual design;
6. expresses accessibility and QA as testable contracts;
7. prevents an implementation agent from depending on hidden chat history;
8. leaves room for root-cause repair when runtime evidence disagrees with the initial plan.

When compiling another project, match this **precision**, not this exact content or file structure.
