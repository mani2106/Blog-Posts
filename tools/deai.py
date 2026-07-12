"""deai.py — reduce AI-generation tells in Quarto (.qmd) blog posts.

Tier 1 (auto-fix on --write): em dashes, curly quotes, unicode ellipsis,
invisible unicode. Tier 2/3 (flag only): vocabulary cliches, structural
patterns. Tier 4 (report only): burstiness + density stats.
Stdlib only.
"""
import re

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
