# Quarto Theme Polish — Title-Block Hero + Breathing Room

- **Date:** 2026-07-08
- **Status:** Implemented on `feature/quarto-theme-polish` (branched off `origin/master`)
- **Base theme:** Flatly (light) / Darkly (dark) — unchanged

## Goal

Polish the migrated Quarto blog's theme and add breathing room using a **hybrid layout**: a full-width **accent hero band** up top (rendered through the Quarto title block) and a centered, narrow **post grid** below. Relocate the homepage category sidebar to a dedicated **Categories** browse page. No new base theme, no full custom design.

## Non-goals

- Changing the base theme (Flatly/Darkly stay).
- Individual **post** page layout — centered via Quarto defaults. The only post-side change is a heading-level TOC fix (see [Post heading-level fix](#post-heading-level-fix-7)).
- Writing the reader-facing "rebuild the blog" post — separate follow-up, intentionally after, so it can use real screenshots.

## Locked decisions

| Decision | Choice |
|---|---|
| Direction | Polish Flatly/Darkly + add space (not a new theme, not full custom) |
| Hero approach | **Style the Quarto title block** as the hero. Pandoc absorbs the first body H1 into the title block when `title:` is set, so reusing the title block avoids extra DOM and inherits the accent color free via `$primary` (resolves per theme) |
| Full-bleed mechanism | `100vw` breakout (`width:100vw; left:50%; transform:translateX(-50%)`) on the title block — Quarto's `column-page` grid keeps a gutter even under `page-layout: full` |
| Horizontal overflow guard | `overflow-x: clip` on `#quarto-content` (**not** `hidden` — `hidden` breaks the sticky navbar) |
| Width approach | `page-layout: full` on home; cap the grid and the inner title with max-widths |
| Categories | Dedicated **Categories** browse page (grid + sidebar, filters in place). Home sidebar removed (`categories: false`) |
| Listing fields | `fields: [image, title, description, date, reading-time]` — replaces the entire card content set, so the full list is required |
| Comments | Utterances dark-mode via custom JS — base `theme: github-light`, `_includes/utterances-theme-sync.html` postMessages `github-dark` into the iframe on toggle (a `theme: [light,dark]` array is rejected by Quarto; only Giscus gets an auto-bridge) |

## Architecture

One new SCSS file, `theme-shared.scss`, carries **all** hero + grid + card rules and is compiled into **both** theme arrays. Because it references Bootstrap theme variables (`$primary`, `$gray-600`), colors resolve correctly per mode — no duplication, no per-mode color files.

Quarto's theme compile model:
- **light** = Flatly vars + `theme-shared.scss` → `$primary` = navy `#2c3e50`
- **dark**  = Darkly vars  + `theme-shared.scss` → `$primary` = muted blue `#375a7f`

So `background: $primary` on the title-block hero produces the correct band color in each mode automatically. `custom.scss` / `custom-dark.scss` remain empty reserved stubs for future per-mode overrides.

The two listings (home + categories) share `theme-shared.scss` but render differently via **config**, not CSS — `categories: false` on home, `categories: true` on the categories page; no content duplication.

## File changes

| File | Status | Change |
|---|---|---|
| `_quarto.yml` | edit | Add `theme-shared.scss` to both theme arrays; add **Categories** navbar entry (Home, Categories, About, GitHub); set Utterances base `theme: github-light`; add `include-after-body` for the comment theme-sync script |
| `index.qmd` | edit | Title-block hero (`title` + `subtitle`); `categories: false`; `fields: [image, title, description, date, reading-time]`; `page-layout: full`; `toc: false` |
| `categories.qmd` | **new** | Same listing but `categories: true`; **default** page layout (not `full`) so the sidebar renders; `toc: false` |
| `theme-shared.scss` | **new** | Title-block-as-hero full-bleed breakout; grid max-width + centering; card padding/image/typography; hover lift |
| `_includes/utterances-theme-sync.html` | **new** | PostMessages `{type:'set-theme'}` into the Utterances iframe on `.quarto-color-scheme-toggle` click; reads body-bg luminance to pick `github-light`/`github-dark` |
| `custom.scss` / `custom-dark.scss` | unchanged | Empty stubs reserved for future per-mode overrides |
| `posts/<slug>/index.qmd` (×7) | edit | Body `#` (H1) sections demoted to `##` so article TOCs populate; one post also drops a redundant duplicate-title H1 |

## Implementation detail

### `_quarto.yml`

Theme arrays:
```yaml
theme:
  light: [flatly, theme-shared.scss, custom.scss]
  dark:  [darkly,  theme-shared.scss, custom-dark.scss]
```

Navbar (Categories added between Home and About):
```yaml
navbar:
  right:
    - text: Home
      href: index.qmd
    - text: Categories
      href: categories.qmd
    - text: About
      href: about.qmd
    - icon: github
      href: https://github.com/mani2106/Blog-Posts
```

Utterances base theme (the JS picks the dark sibling). `theme:` must be a single
string — Quarto rejects a `[light, dark]` array and, unlike Giscus, provides no
auto theme-bridge for Utterances:
```yaml
comments:
  utterances:
    repo: mani2106/Blog-Posts
    theme: github-light
```
Wired site-wide via:
```yaml
format:
  html:
    include-after-body: ["_includes/utterances-theme-sync.html"]
```
The script listens for clicks on `.quarto-color-scheme-toggle`, waits ~60ms for
Quarto to flip the DOM, reads the body-background luminance, and postMessages
`{type:'set-theme', theme:'github-dark'|'github-light'}` into `iframe.utterances-frame`.
A MutationObserver does the first sync once client.js injects the iframe.

### `index.qmd` (home)

Hero is the page title block — no hand-written hero div.
```markdown
---
title: "Notes from the data-science trenches"
subtitle: "Tutorials, certification deep-dives, and field notes on ML, Azure AI, and NLP."
listing:
  contents: posts
  sort: "date desc"
  type: grid
  categories: false
  sort-ui: false
  filter-ui: false
  fields: [image, title, description, date, reading-time]
page-layout: full
toc: false
---
```

### `categories.qmd` (new browse page)

Same listing as home, but `categories: true` and the **default** page layout (no `page-layout: full`) so the category sidebar renders in the margin.
```markdown
---
title: "Categories"
listing:
  contents: posts
  sort: "date desc"
  type: grid
  categories: true
  sort-ui: false
  filter-ui: false
  fields: [image, title, description, date, reading-time]
toc: false
---
```

### `theme-shared.scss`
```scss
/*-- scss:rules --*/

/* Title-block hero — full-bleed via 100vw breakout.
   column-page keeps a gutter even under page-layout: full, so break out
   with width:100vw + left:50% + translateX(-50%). */
main.column-page #title-block-header.quarto-title-block {
  width: 100vw;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
  background: $primary;
  color: #fff;
  padding: 4rem 1.5rem;
}
/* clip (not hidden) so the sticky navbar keeps working */
#quarto-content { overflow-x: clip; }

/* Inner title capped + centered */
.quarto-title-block .quarto-title {
  max-width: 800px;
  margin-inline: auto;
}

/* Center + cap the post grid */
.quarto-listing { max-width: 1100px; margin-inline: auto; }
.list.grid { gap: 1.75rem; }

/* Cards: extra padding above the title (.card-body.post-contents);
   lighter/smaller snippet in muted gray */
.listing-description { color: $gray-600; font-size: 0.92rem; }

/* Uniform image slot */
.card-img-top img.thumbnail-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

/* Hover lift */
.quarto-grid-item {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.quarto-grid-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.12);
}
```

### Post heading-level fix (×7)

Posts touched: `azure-ai102-day1-planning-ai-soln-azure`, `azure-ai102-day2-planning-ai-soln-azure`, `azure-ai102-journey-intro`, `linear-regression-grad-desc` (also removed a redundant duplicate-title H1), `sticky-toc-component-implementation`, `wiki-data-extraction`, `jekyll-blog-security-hardening-journey`.

Body `#` (H1) sections demoted to `##`. Quarto/Pandoc treats the YAML `title:` as the document H1 and **excludes H1 from the article TOC**, so any body H1 was silently dropping those sections from the TOC. Code-block comments inside ```python / ```ruby / ```dockerfile fences (e.g. `# For JSON...`, `# Before`, `# Phase 1`) were left untouched — those are content, not headings.

## Key decisions / why-nots

- **Title-block-as-hero, not a hand-written hero div.** Pandoc absorbs the first body H1 into the title block when `title:` is set, so a hand-written hero div would either fight that or duplicate DOM. Styling the existing title block avoids extra markup and gets the accent color free via `$primary` (resolves per theme).
- **Full-bleed via `100vw` breakout** because Quarto's `column-page` grid sits inside a gutter even under `page-layout: full`.
- **`overflow-x: clip` (not `hidden`)** on `#quarto-content` — `hidden` breaks the sticky navbar.
- **Listing `fields:` replaces the entire card content set**, so the full list `[image, title, description, date, reading-time]` is required — omitting any field drops it from the card.
- **Reading-time needs no config key** — Quarto auto-computes it for listings.
- **The 7 posts use plain ```python fences (non-executable)**, so rendering them to verify the TOC was safe — no kernel needed.
- **Utterances compose box won't render from `file://`** — it needs an http(s) origin for GitHub OAuth. Expected, not a bug.
- **Utterances `theme:` is a single string only** — Quarto rejects a `[light, dark]` array and auto-bridges theme to Giscus but not Utterances, so dark-mode comments need the custom JS sync rather than a config line.

## Verification

Local render with `F:/Software/quarto/bin/quarto.cmd preview`, checked in **both** light + dark:

1. **Hero band:** renders full-bleed edge-to-edge (no gutter); title + subtitle white on `$primary`; no horizontal scrollbar.
2. **Home grid:** centered at ~1100px; **no** category sidebar; cards aligned (uniform 150px image slot); description in muted `$gray-600` at 0.92rem; hover lifts. Cards show **date + "5 min"** reading time.
3. **Categories (navbar):** sidebar present; clicking a category filters the grid in place.
4. **Article TOCs now populate** — the security-hardening post lists 8+ top-level sections with nesting (previously empty before the H1→H2 fix).
5. **Utterances** follows the toggle via the JS sync — `github-light` base, switches to `github-dark` in dark mode (verified: script present in rendered HTML; base `theme="github-light"` on the client.js tag; toggle behavior confirmed by logic review).
6. **Mobile (narrow viewport):** band stays full-bleed; grid collapses to one column; max-widths cause no overflow.

## Risks / notes

- Card-image `object-fit: cover` crops images of varying aspect ratios to a uniform 150px slot — the single biggest alignment win, but some images get cropped. Acceptable trade-off for a clean grid.
- The hero's full-bleed `100vw` depends on `overflow-x: clip` on `#quarto-content` containing the breakout; if a future Quarto version changes that wrapper, the clip rule may need to move.
- The hero's `$primary` background is coupled to the Flatly/Darkly palettes. A future base-theme swap would need the new theme's accent var to resolve equivalently.
