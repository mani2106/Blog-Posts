# Design: `tools/deai.py` — de-AI-ify for Quarto posts

**Date:** 2026-07-11
**Status:** Approved (design phase)
**Target post (motivating example):** `posts/jekyll-to-quarto-migration/index.qmd`

## Problem

Several posts read as AI-generated. The strongest, most visible tell is **em-dash overuse** (`—`): the migration post alone has em dashes on 16 lines. Other tells (curly quotes, vocabulary clichés, tricolons, bold-term overuse) appear at lower frequency. We want a deterministic tool that reduces these tells without rewriting prose in a way that makes it worse.

## Goal / non-goals

**Goal:** a standalone, dependency-free Python script that (a) mechanically fixes the tells that are safe to auto-fix, (b) flags the tells that need human judgment, and (c) reports statistical signals — by default as a dry-run diff, never touching files unless asked.

**Non-goals (explicitly out of scope):**
- Auto-rewriting vocabulary or sentence structure (would degrade prose — the core failure mode to avoid).
- Auto-editing frozen `.ipynb` notebooks (cached JSON; too risky to machine-edit). Notebooks may be *flagged*, never auto-written.
- LLM-based rephrasing / perplexity scoring (adds API/dependency + non-determinism).
- CI/pre-commit enforcement now (a later phase; `--check` is provided so it can be wired in later).

## Research basis

Design is grounded in a four-subagent research pass (punctuation, vocabulary, syntax/structure, detector-metrics + blog-prose). Key conclusion: **tells split cleanly into "safe to fix mechanically" vs "needs human judgment."** Tells group into four tiers:

- **Tier 1 — mechanical, safe to auto-fix:** em dashes, curly/smart quotes, unicode ellipsis (`…`), invisible unicode artifacts (zero-width chars, stray BOM/control chars).
- **Tier 2 — vocabulary clichés (flag + suggest):** delve, tapestry, testament, robust, seamless, leverage, underscore, navigate, landscape, realm, plethora, myriad, foster, pivotal, intricate, nuanced, elevate, empower, journey, "it's worth noting", "importantly/significantly", "let's dive in", "game-changer", harness/unleash, "cutting-edge", "state-of-the-art".
- **Tier 3 — structural (flag only):** tricolon/rule-of-three overuse, "Not only… but also", "It's not X, it's Y", meta-framing ("Let's explore", "Here's the thing", "At the end of the day"), "In conclusion/summary" closers, predictable transitions (Furthermore/Moreover/Additionally at paragraph starts), bold-term overuse.
- **Tier 4 — statistical (report only):** burstiness (stdev of sentence word counts; low = AI), em-dash & comma density per 1000 words, sentence-count. (Perplexity needs an LM — excluded.)

## Architecture: tiers → actions

| Tier | Tells | Action |
|---|---|---|
| 1 | em dashes, curly quotes, unicode ellipsis, invisible unicode | **auto-fix** on `--write` |
| 2 / 3 | vocab clichés, tricolons, meta-framing, bold-overuse, "In conclusion", predictable transitions | **flag only** — line number + suggested fix |
| 4 | burstiness, em-dash/comma density, sentence-length variance | **report only** |

The tool **never** auto-rewrites Tier 2/3.

## Component breakdown

Single file `tools/deai.py`, stdlib only. Logical units (kept as small functions so each is testable in isolation):

1. **`split_regions(text)`** — markdown-aware segmentation. Returns regions tagged `prose` vs `protected`. Protected = YAML front matter, fenced code blocks (` ``` `), inline code spans, and URL/link destinations. All Tier 1 replacements run **only on `prose` regions**. This is the safety-critical unit.
2. **`fix_em_dashes(line)`** — the context-rules engine (see below). Returns the rewritten line.
3. **`normalize_typography(line)`** — curly quotes → straight; `…` → `...`; (called on prose only).
4. **`strip_invisible_unicode(line)`** — remove `Cc`/`Cf` category chars except `\n`, `\t` (zero-width space/joiner, BOM, etc.).
5. **`find_flags(text)`** — Tier 2/3 scanner. Returns a list of `(line_no, category, match, suggestion)`.
6. **`compute_stats(text)`** — Tier 4 numbers (burstiness, densities, sentence count).
7. **`process(path, write=False)`** — orchestrates 1–6 on one file; returns a report object and (if `write`) applies Tier 1 changes.
8. **CLI (`main`)** — argparse: target (file/glob/dir, default `posts/**/index.qmd`), `--write`, `--check`, `--no-flags`/`--no-stats`. Default = dry-run diff + flags + stats.

## Em-dash algorithm (the nuanced part)

Applied per prose line, after region-splitting. Three rules, in order:

1. **Parenthetical pair** — a segment with exactly two `—` forming `A — B — C` → `A (B) C`.
   - `"My brother — the one in Norway — sent a fish."` → `"My brother (the one in Norway) sent a fish."`
2. **Elaboration / list-intro** — single `—` where the right-hand side is an elaboration: starts with an infinitive (`to X`), an `-ing` or past-tense verb, or is a multi-item list (≥2 commas). → **colon**.
   - `"straightforward — convert every post, standardize, and drop"` → `"straightforward: convert every post, standardize, and drop"`
3. **Default clause break** — any other single `—`. → **comma** (safe default; a comma is almost never grammatically wrong where a dash sat).
   - `"first real section — so Quarto silently dropped"` → `"first real section, so Quarto silently dropped"`

**3+ dashes on a segment** (rare): do not attempt paren pairing; every dash → comma. Pairing is only applied to the clean exactly-two case. This avoids mis-grouping when a line mixes a parenthetical with a clause break.

**Safety net:** every Tier 1 change is shown in the diff for review. Rules 1–3 are heuristics; the comma default guarantees grammatical safety even when the heuristic is unsure. (Period-as-replacement for two independent clauses was considered and **deferred** — not in the chosen comma/colon/parens set.)

## Markdown safety (critical for `.qmd`)

`split_regions` must protect, and never edit inside:
- YAML front matter (between the opening `---` … closing `---` at file start).
- Fenced code blocks (```` ``` ```` … ```` ``` ````), including language-tagged and indented.
- Inline code spans (`` ` … ` ``), including backtick-quoted code.
- URLs and Markdown link destinations (`[text](url)` → never alter `url`; image `src` likewise).

A dash inside `title:` front matter, a code example, or a URL must survive untouched. This is the highest-risk requirement; it gets the most test coverage.

## CLI

```
python tools/deai.py [target]            # dry-run: diff + flags + stats (default target: posts/**/index.qmd)
python tools/deai.py posts/<slug>/index.qmd
python tools/deai.py --write [target]    # apply Tier 1 fixes in place
python tools/deai.py --check [target]    # exit 1 if any tell found (for future CI/pre-commit)
python tools/deai.py --no-stats [target] # suppress Tier 4 report
```

Default behavior is **dry-run** — no file is modified unless `--write` is passed.

## File scope

- **In scope (auto-fix + flag):** all `posts/**/index.qmd` (8 files; 3 currently have tells).
- **Flag-only (never auto-written):** `posts/**/index.ipynb` — emit flags only, refuse `--write` on notebooks (print a notice).
- Top-level pages (`index.qmd`, `categories.qmd`, `about.qmd`, `404.qmd`) are included when explicitly passed.

## Testing

`tools/tests/test_deai.py`, plain pytest functions, stdlib only — matching `tools/tests/test_convert.py`'s convention. Cases:

- `fix_em_dashes`: pair → parens; single → comma; elaboration → colon.
- `normalize_typography`: each curly-quote char → straight; `…` → `...`.
- `strip_invisible_unicode`: zero-width space/joiner and BOM removed; `\n`/`\t` preserved.
- `split_regions`: front matter untouched; fenced block untouched; inline code span untouched; URL in a Markdown link untouched; a `—` inside each protected region is preserved verbatim.
- `find_flags`: a known cliché ("delve") flagged with suggestion; a tricolon counted; "In conclusion" flagged.
- `compute_stats`: burstiness computed on a crafted input with known sentence lengths.
- `process(..., write=False)`: returns expected diff and does not modify the file on disk.
- `process(..., write=True)`: writes the Tier-1-fixed file and leaves protected regions byte-identical.

## Out of scope / future

- CI/pre-commit wiring (`--check` is the hook point).
- Auto-fix for `.ipynb` notebooks.
- LLM rephrase / perplexity scoring.
- Period as an em-dash replacement option.
