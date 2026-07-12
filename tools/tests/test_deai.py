import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from deai import split_blocks, iter_prose_lines, with_inline_protected


def test_split_blocks_frontmatter_is_protected():
    text = "---\ntitle: T\n---\nbody line\n"
    kinds = [kind for kind, _ in split_blocks(text)]
    assert kinds == ['frontmatter', 'prose']


def test_split_blocks_fenced_code_is_protected():
    text = "intro\n```python\nx = 1 — 2\n```\noutro\n"
    kinds = [kind for kind, _ in split_blocks(text)]
    assert kinds == ['prose', 'codeblock', 'prose']


def test_split_blocks_tilde_fence_is_protected():
    text = "a\n~~~\ncode — here\n~~~\nb\n"
    kinds = [kind for kind, _ in split_blocks(text)]
    assert kinds == ['prose', 'codeblock', 'prose']


def test_iter_prose_lines_skips_protected_with_correct_numbers():
    text = "---\ntitle: T\n---\nproseA\n```\ncode\n```\nproseB\n"
    pairs = list(iter_prose_lines(text))
    # line 1-3 front matter skipped, line 4 prose, 5-7 code skipped, line 8 prose
    assert pairs == [(4, 'proseA'), (8, 'proseB')]


def test_with_inline_protected_leaves_code_spans_alone():
    calls = []
    def fn(s):
        calls.append(s)
        return s.upper()
    out = with_inline_protected("keep `code — x` and text", fn)
    assert "`code — x`" in out          # code span untouched
    assert "KEEP" in out and "TEXT" in out  # prose transformed


def test_with_inline_protected_leaves_link_urls_alone():
    def fn(s):
        return s.replace('—', ',')
    out = with_inline_protected("see [a — b](http://x/y—z) now", fn)
    assert "http://x/y—z" in out    # URL untouched
    assert "a , b" in out           # link text is prose -> transformed


def test_with_inline_protected_leaves_image_destinations_alone():
    def fn(s):
        return s.replace('—', ',')
    out = with_inline_protected("![alt — x](http://y/z—w.png)", fn)
    assert "http://y/z—w.png" in out   # image URL untouched


def test_with_inline_protected_handles_code_span_adjacent_to_link():
    def fn(s):
        return s.upper()
    out = with_inline_protected("see `x`](http://x/y) now", fn)
    assert "`x`" in out              # code span untouched (lowercase x preserved)
    assert "http://x/y" in out       # link URL untouched
    assert "SEE" in out and "NOW" in out  # surrounding prose transformed
