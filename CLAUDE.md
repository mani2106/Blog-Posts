# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this repo is

A personal data-science blog by Manimaran Panneerselvam, built on **Quarto** (a `_quarto.yml` website project). Source lives on `master`; the live site is published to GitHub Pages at https://mani2106.github.io/Blog-Posts/ from a `gh-pages` branch that **CI regenerates on every push to `master`** — never edit `gh-pages` directly.

> **History:** Migrated Jekyll/fastpages → Quarto (cutover PR #46, 2026-07). The pre-Quarto Jekyll site is archived under `_jekyll_archive/` (reference only). Every old fastpages workflow is renamed `*.DISABLED`. If anything below conflicts with the old fastpages mental model (Liquid includes, `layout: notebook`, `nb_path`, `baseurl`, `_posts/`), trust the Quarto reality described here.

## Build, preview, deploy

No test/lint suite for the blog. "Building" means a Quarto render.

**Local preview (native Quarto):** install the Quarto CLI (CI pins **1.9.38**), then `quarto preview` — it prints the local URL. The old Jekyll/Docker toolchain (`blog-dev.ps1`, `docker-compose.yml`, `Makefile`) was removed in the migration; there is no containerized preview path now.

**Deploy (automatic):** `.github/workflows/quarto-publish.yml` runs on push to `master` (and `workflow_dispatch`):
`checkout@v4` → `quarto-dev/quarto-actions/setup@v2` (1.9.38) → `…/render@v2` → **backslash gate** → `…/publish@v2` to `gh-pages` with `render: false`.

- **Backslash gate:** the build fails if any `_site/**/*.html` has a `src="…\…"` or `href="…\…"` containing a backslash. You edit on Windows but the build runs on Linux — a backslash path-separator artifact in an `src`/`href` is a 404 in production, so don't paste Windows paths into links. The gate catches it.
- `render: false` on publish means it ships the `_site/` already rendered and gate-checked above (no double render).
- `permissions: contents: write`, `concurrency: pages`.

## Project layout

- `_quarto.yml` — project + website config. **The source of truth.**
- `index.qmd` — homepage: a post listing (`type: grid`, `page-layout: full`, `sort: date desc`, hero title-block).
- `categories.qmd`, `about.qmd`, `404.qmd` — top-level pages.
- `posts/<slug>/index.{qmd,ipynb}` — blog posts (23 total).
- `posts/_metadata.yml` — `execute.freeze: true`, `lang: en` (applied to every post).
- `images/` — post images (declared via `resources: images/**`).
- `theme-shared.scss`, `custom.scss`, `custom-dark.scss` — theme overrides (wired in `_quarto.yml format.html.theme`).
- `tools/` — notebook/doc → Quarto-post converters used during migration (`convert_post.py`, `run_convert*.py`, `tools/tests/test_convert.py`).
- `_jekyll_archive/`, `_fastpages_docs/`, `*.DISABLED` workflows — legacy reference; don't edit.

## The two authoring pipelines

Both live under `posts/<slug>/`. Use **Quarto** conventions — no Jekyll `layout:`, no `nb_path:`, no Liquid.

1. **Hand-written** — `posts/<slug>/index.qmd` with Quarto YAML front matter:
   ```yaml
   ---
   title: Azure AI-102 Certification Journey - Introduction
   categories: [azure, azure-ai, AI-102]   # list; used by categories.qmd
   date: '2025-11-11'                        # quoted; drives listing order
   description: '...'                        # shown on listing cards
   # image: images/<subdir>/<file>.png       # optional; shown on cards
   ---
   ```
   Use Quarto **callouts** (`::: {.callout-note}` … `:::`) instead of the old admonition includes, and native **Markdown footnotes** instead of the old `_plugins/footnote.rb`.

2. **Notebooks** — `posts/<slug>/index.ipynb`, **frozen** (`freeze: true`): executed once, outputs cached under `.quarto/`/`_freeze/`, not re-run on build. Convert new notebooks/docs with `tools/convert_post.py`. Don't hand-edit a frozen notebook's cached outputs — rerun via Quarto instead.

Render rules in `_quarto.yml`: `render: ["*.qmd", "posts/**"]`. Permalinks/ordering are **slug-based** (`/posts/<slug>/`), not Jekyll date-based.

## Critical config facts

- `site-url: https://mani2106.github.io/Blog-Posts/` — Quarto resolves internal URLs from this. There is **no Jekyll `baseurl`/`relative_url` filter**; use ordinary Quarto-relative links and reference images as `images/…`.
- `execute.freeze: auto` (root) + `freeze: true` (posts) — deterministic, fast builds.
- **Comments:** Utterances (`website.comments.utterances`: repo `mani2106/Blog-Posts`, label `blog-comments`). Quarto 1.9.x cannot take a light/dark array for `utterances.theme`, so dark-mode sync is done in JS — if you change comments config, find and check that JS sync, not just `_quarto.yml`.
- **Search:** Quarto built-in (`search: true`). The old Lunr `search.js`/`search-data.json` is gone.
- **TOC:** Quarto native (`toc: true`, `toc-location: right`). The old custom `toc.js`/`toc.html` is gone.
- **Math:** LaTeX (`$…$`, `$$…$$`) works out of the box via Quarto.
- **Theme / dark mode:** `flatly` (light) + `darkly` (dark) + the three SCSS files; dark mode is Quarto's native toggle (the old custom `theme-toggle.js`/FOUC script is gone).

## Active feature work & gotchas

- **Tweet generator (being revived for Quarto).** `.github/actions/tweet-generator/` is a Python GitHub Action. On `master` only `.pyc` bytecode survives — the **full `.py` sources + workflow + examples are recoverable from tag `2,0` and branch `feature/tweet-generator-integration`** (release "Changes to add tweet generator"; it ran — PRs #35–#38). `_twitter/*.txt` is the output dir (currently empty). Planned: **RSS-feed-driven discovery → OpenRouter → PR for review**; auto-posting via Buffer is a later phase (Buffer free-tier API: 100 req/24h, unlimited AI, 3 channels × 10 queued posts — connect Twitter→Buffer once, use `BUFFER_ACCESS_TOKEN`). **Gap:** Quarto has **no RSS/Atom feed yet** — must add the `quarto-atom-feed` extension + a feed block in `_quarto.yml`.

## Things that look like code but aren't active

- `_jekyll_archive/`, `_fastpages_docs/` — legacy reference.
- `.github/workflows/*.DISABLED` — disabled fastpages automation.
- `_site/`, `.quarto/`, `_freeze/` — build artifacts (gitignored).
- `.kiro/`, `_ideas/`, `new_blog/` — gitignored local scratch/specs.
- `settings.ini` — gitignored nbdev config.

## Project agent skills

Two skills are installed at **project scope** (`.agents/skills/`, symlinked into Claude Code) as optional accelerators — not build dependencies:

- **`quarto-authoring`** (`posit-dev/skills`) — Posit's official Quarto authoring/config guidance. Useful for Quarto site config (e.g. wiring the `quarto-atom-feed` extension for a post feed).
- **`github-actions-templates`** (`wshobson/agents`) — hardened, version-pinned GitHub Actions / composite-action templates.

Manage with the Skills CLI: `npx skills list` (installed), `npx skills find <query>` (search), `npx skills add <owner/repo@skill>` (install), `npx skills update` (upgrade).

## Tooling notes

- **Web search:** prefer the built-in `WebSearch` (or `mcp__duckduckgo__search`); `mcp__kindly-web-search` was unreachable this session.

## Working-directory notes (Windows)

Shell is PowerShell by default; the Bash tool here runs Git Bash (POSIX syntax). Paths contain a space (`Blog Repo`), so quote them. The repo root is `F:\Studies\Blog Repo\Blog-Posts`.
