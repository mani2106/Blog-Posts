"""deai.py — reduce AI-generation tells in Quarto (.qmd) blog posts.

Tier 1 (auto-fix on --write): em dashes, curly quotes, unicode ellipsis,
invisible unicode. Tier 2/3 (flag only): vocabulary cliches, structural
patterns. Tier 4 (report only): burstiness + density stats.
Stdlib only.
"""
import re
import unicodedata
from pathlib import Path

_FENCE_OPEN = re.compile(r'^\s{0,3}(`{3,}|~{3,})')


def split_blocks(text):
    """Yield (kind, chunk) where kind is 'frontmatter', 'codeblock', or 'prose'.

    Partitions the file so callers can transform only prose chunks.
    """
    lines = text.splitlines(keepends=True)
    n = len(lines)
    i = 0
    # YAML front matter: opening '---' at the very start, closing '---'.
    if n > 0 and lines[0].strip() == '---':
        close = None
        for j in range(1, n):
            if lines[j].strip() == '---':
                close = j
                break
        if close is not None:
            yield ('frontmatter', ''.join(lines[:close + 1]))
            i = close + 1
    while i < n:
        m = _FENCE_OPEN.match(lines[i])
        if m:
            fence_char = '`' if '`' in m.group(1) else '~'
            closer = re.compile(r'^\s{0,3}' + re.escape(fence_char * 3))
            start = i
            i += 1
            while i < n and not closer.match(lines[i]):
                i += 1
            i += 1  # consume the closing fence line
            yield ('codeblock', ''.join(lines[start:i]))
        else:
            yield ('prose', lines[i])
            i += 1


def iter_prose_lines(text):
    """Yield (1-based line_number, line_text) for prose lines only."""
    line_no = 0
    for kind, chunk in split_blocks(text):
        for line in chunk.splitlines():
            line_no += 1
            if kind == 'prose':
                yield (line_no, line)


# Inline code spans (incl. double-backtick) and Markdown link/image
# *destinations* (the ](url) tail). Link text stays prose and may transform.
_INLINE_PROTECTED = re.compile(r'(`+)[^`]+\1|\]\([^)]*\)')


def with_inline_protected(line, fn):
    """Apply fn(str)->str to the parts of `line` that are NOT inline code
    spans or Markdown link/image constructs. Protected spans pass through."""
    out = []
    last = 0
    for m in _INLINE_PROTECTED.finditer(line):
        out.append(fn(line[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(fn(line[last:]))
    return ''.join(out)


def _is_elaboration(right):
    """Heuristic: does the right side of a dash elaborate/list (-> colon)
    rather than continue a flowing clause (-> comma)?"""
    r = right.lstrip()
    if not r:
        return False
    if re.match(r'^to\s+\w', r):                 # infinitive: "to ship..."
        return True
    if re.match(r'^\w+ing\s+\w', r):             # gerund/imperative -ing: "converting..."
        return True
    head = r.split('.', 1)[0]                    # first clause only
    if head.count(',') >= 2:                     # multi-item list
        return True
    return False


def fix_em_dashes(s):
    """Replace spaced em dashes (' — ') by context.

    1 split  -> colon (elaboration) or comma (default)
    2 splits -> parentheses (parenthetical pair)
    3+       -> all commas
    0 spaced -> unchanged (non-spaced em dashes left alone)
    """
    parts = s.split(' — ')
    n = len(parts) - 1
    if n <= 0:
        return s
    if n == 1:
        left, right = parts
        joiner = ': ' if _is_elaboration(right) else ', '
        return left + joiner + right
    if n == 2:
        a, b, c = parts
        return f'{a} ({b}) {c}'
    return ', '.join(parts)


def normalize_typography(s):
    """Curly/smart quotes -> straight; unicode ellipsis -> '...'."""
    s = s.replace("“", '"').replace("”", '"')   # double curly
    s = s.replace("‘", "'").replace("’", "'")   # single curly / apostrophe
    s = s.replace("…", '...')                        # ellipsis
    return s


def strip_invisible_unicode(s):
    """Remove Unicode control (Cc) and format (Cf) chars, keep newlines/tabs."""
    keep = ('\n', '\t', '\r')
    return ''.join(
        ch for ch in s
        if ch in keep or unicodedata.category(ch) not in ('Cc', 'Cf')
    )


_VOCAB = {
    'delve': 'examine / explore',
    'tapestry': 'mix / range',
    'testament': 'evidence / proof',
    'robust': 'strong / reliable',
    'seamless': 'smooth / integrated',
    'seamlessly': 'smoothly',
    'leverage': 'use / draw on',
    'underscore': 'highlight / emphasize',
    'navigate': 'work through / manage',
    'landscape': 'field / area',
    'realm': 'area / domain',
    'plethora': 'many / abundance',
    'myriad': 'many / numerous',
    'foster': 'encourage / support',
    'pivotal': 'important / key',
    'intricate': 'complex / detailed',
    'nuanced': 'subtle / detailed',
    'elevate': 'improve / strengthen',
    'empower': 'enable / support',
    'journey': 'process / path',
    'arguably': 'delete or strengthen',
    'importantly': 'delete',
    'significantly': 'delete or quantify',
    'game-changer': 'major shift',
    'game-changing': 'significant',
    'harness': 'use / apply',
    'unleash': 'release / apply',
    'cutting-edge': 'latest / advanced',
    'state-of-the-art': 'current / advanced',
}

_TRICOLON = re.compile(r',\s+[\w-]+(?:\s+[\w-]+)*,\s+and\s+[\w-]+')
_BOLD = re.compile(r'\*\*[^*]+\*\*')
_NOT_ONLY = re.compile(r'\bnot only\b.{0,80}?\bbut also\b', re.I)
_META = re.compile(
    r"\blet'?s (explore|dive in|unpack|dive deep)\b"
    r"|\bhere'?s the (thing|deal)\b"
    r"|\bat the end of the day\b"
    r"|\bit'?s worth noting\b",
    re.I,
)
_CONCLUSION = re.compile(r'^in (summary|conclusion|closing)\b|^to summarize\b|^key takeaways\b', re.I)
_ITS_NOT = re.compile(r"\bit'?s not (just|merely|simply)\b.{0,60}?,\s*it'?s\b", re.I)
_TRANSITION = re.compile(r'^(furthermore|moreover|additionally),', re.I)


def _flag(line_no, category, snippet, suggestion):
    return (line_no, category, snippet, suggestion)


def find_flags(text):
    """Scan prose for Tier 2/3 tells. Returns (line_no, category, snippet, suggestion)."""
    flags = []
    tricolon_total = 0
    bold_total = 0
    word_total = 0
    for line_no, line in iter_prose_lines(text):
        lower = line.lower()
        for word, sug in _VOCAB.items():
            if re.search(r'\b' + re.escape(word) + r'\b', lower):
                flags.append(_flag(line_no, 'vocab', word, sug))
        if _NOT_ONLY.search(line):
            flags.append(_flag(line_no, 'not-only-but-also', line.strip()[:60], 'split into two clauses'))
        if _ITS_NOT.search(line):
            flags.append(_flag(line_no, 'its-not-its', line.strip()[:60], 'state positively'))
        if _META.search(line):
            flags.append(_flag(line_no, 'meta-framing', line.strip()[:60], 'delete; start with content'))
        if _CONCLUSION.search(line.strip()):
            flags.append(_flag(line_no, 'conclusion-closer', line.strip()[:60], 'delete or end on substance'))
        if _TRANSITION.search(line.strip()):
            flags.append(_flag(line_no, 'predictable-transition', line.strip()[:60], 'remove or vary'))
        tricolon_total += len(_TRICOLON.findall(line))
        bold_total += len(_BOLD.findall(line))
        word_total += len(line.split())
    if tricolon_total >= 3:
        flags.append(_flag(0, 'tricolon-overuse', f'{tricolon_total} rule-of-three lists', 'vary list lengths'))
    if word_total and bold_total * 1000 / word_total > 5:
        flags.append(_flag(0, 'bold-overuse', f'{bold_total} bold spans / {word_total} words', 'reduce bolding'))
    return flags


_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')


def _prose_text(text):
    return ''.join(chunk for kind, chunk in split_blocks(text) if kind == 'prose')


def compute_stats(text):
    """Tier 4: report-only statistical signals (burstiness proxy + densities)."""
    prose = _prose_text(text)
    sentences = [s for s in _SENT_SPLIT.split(prose) if s.strip()]
    counts = [len(s.split()) for s in sentences]
    n = len(counts)
    mean = sum(counts) / n if n else 0.0
    variance = sum((c - mean) ** 2 for c in counts) / n if n else 0.0
    words = prose.split()
    wc = len(words) if words else 1
    return {
        'word_count': len(words),
        'sentence_count': n,
        'sentence_length_mean': round(mean, 1),
        'sentence_length_stdev': round(variance ** 0.5, 1),
        'em_dash_density_per_1k': round(prose.count('—') * 1000 / wc, 1),
        'comma_density_per_1k': round(prose.count(',') * 1000 / wc, 1),
        'bold_spans': len(_BOLD.findall(prose)),
    }


def _tier1(s):
    """Compose the Tier 1 transforms for one prose string (no inline code)."""
    s = fix_em_dashes(s)
    s = normalize_typography(s)
    s = strip_invisible_unicode(s)
    return s


def _fix_text(text):
    """Apply Tier 1 to prose only; return fixed text."""
    out = []
    for kind, chunk in split_blocks(text):
        if kind == 'prose':
            line = chunk.rstrip('\n')
            fixed = with_inline_protected(line, _tier1)
            out.append(fixed + '\n')
        else:
            out.append(chunk)
    return ''.join(out)


def process(path, write=False):
    """Run the full pipeline on one file. Never writes unless write=True."""
    p = Path(path)
    original = p.read_text(encoding='utf-8')
    fixed = _fix_text(original)
    result = {
        'original': original,
        'fixed': fixed,
        'changed': fixed != original,
        'flags': find_flags(original),
        'stats': compute_stats(original),
        'path': str(p),
    }
    if write:
        p.write_text(fixed, encoding='utf-8')
    return result


import argparse
import difflib


def _collect(target):
    p = Path(target)
    if p.is_file():
        return [p]
    if p.is_dir():
        return sorted(p.rglob('index.qmd'))
    return sorted(Path('.').glob(target))   # treat as glob pattern


def _expand_targets(targets):
    paths = []
    for t in targets:
        paths.extend(_collect(t))
    return paths


def _print_report(result, show_stats=True):
    path = result['path']
    if result['changed']:
        diff = difflib.unified_diff(
            result['original'].splitlines(keepends=True),
            result['fixed'].splitlines(keepends=True),
            fromfile=path, tofile=path, lineterm='',
        )
        print(f'\n=== {path} (Tier 1 diff) ===')
        for line in diff:
            print(line.rstrip('\n'))
    else:
        print(f'\n=== {path} (no Tier 1 changes) ===')
    if result['flags']:
        print('--- flags ---')
        for line_no, cat, snippet, sug in result['flags']:
            where = f'L{line_no}' if line_no else 'doc'
            print(f'  [{cat}] {where}: {snippet!r} -> {sug}')
    if show_stats:
        print('--- stats ---')
        for k, v in result['stats'].items():
            print(f'  {k}: {v}')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Reduce AI-generation tells in Quarto posts.')
    parser.add_argument('target', nargs='*', help='file/dir/glob (default: posts/**/index.qmd)')
    parser.add_argument('--write', action='store_true', help='apply Tier 1 fixes in place')
    parser.add_argument('--check', action='store_true', help='exit 1 if any tell found')
    parser.add_argument('--no-stats', action='store_true', help='suppress Tier 4 stats')
    args = parser.parse_args(argv)

    paths = _expand_targets(args.target or ['posts/**/index.qmd'])
    if not paths:
        print('no files matched')
        return 0

    rc = 0
    for p in paths:
        is_notebook = p.suffix == '.ipynb'
        if is_notebook and args.write:
            print(f'{p}: notebook (.ipynb) is flag-only; --write refused.')
            args_write = False
        else:
            args_write = args.write
        result = process(p, write=args_write)
        _print_report(result, show_stats=not args.no_stats)
        if args.check and (result['changed'] or result['flags']):
            rc = 1
    return rc


if __name__ == '__main__':
    raise SystemExit(main())

