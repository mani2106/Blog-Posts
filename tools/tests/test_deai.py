import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from deai import split_blocks, iter_prose_lines, with_inline_protected, fix_em_dashes, normalize_typography, strip_invisible_unicode


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


def test_em_dash_single_clause_becomes_comma():
    assert fix_em_dashes("first section — so Quarto dropped it") == \
        "first section, so Quarto dropped it"


def test_em_dash_elaboration_becomes_colon():
    assert fix_em_dashes("straightforward — convert, standardize, and drop") == \
        "straightforward: convert, standardize, and drop"


def test_em_dash_infinitive_becomes_colon():
    assert fix_em_dashes("the goal — to ship fast, well, now") == \
        "the goal: to ship fast, well, now"


def test_em_dash_pair_becomes_parens():
    assert fix_em_dashes("My brother — the one in Norway — sent a fish") == \
        "My brother (the one in Norway) sent a fish"


def test_em_dash_three_or_more_all_commas():
    assert fix_em_dashes("a — b — c — d") == "a, b, c, d"


def test_em_dash_non_spaced_left_untouched():
    # Non-spaced em dashes are left as-is (conservative).
    assert fix_em_dashes("well—known and fine") == "well—known and fine"


def test_em_dash_none_left_untouched():
    assert fix_em_dashes("nothing here at all") == "nothing here at all"


def test_normalize_curly_quotes_to_straight():
    assert normalize_typography("“hello” world ‘x’") == '"hello" world \'x\''


def test_normalize_unicode_ellipsis():
    assert normalize_typography("wait…") == "wait..."


def test_normalize_leaves_em_dash_for_engine():
    # em dash is NOT normalized here; fix_em_dashes handles it.
    assert normalize_typography("a — b") == "a — b"


def test_strip_invisible_unicode_removes_zero_width_and_bom():
    s = "a​b‍c﻿d"   # ZWSP, ZWJ, BOM
    assert strip_invisible_unicode(s) == "abcd"


def test_strip_invisible_unicode_keeps_newline_and_tab():
    assert strip_invisible_unicode("a\nb\tc") == "a\nb\tc"


from deai import find_flags


def test_flag_vocabulary_cliche():
    text = "Let us delve into the robust details.\n"
    flags = find_flags(text)
    words = {f[2].lower() for f in flags if f[1] == 'vocab'}
    assert 'delve' in words
    assert 'robust' in words


def test_flag_not_only_but_also():
    text = "It not only works but also shines here.\n"
    cats = {f[1] for f in find_flags(text)}
    assert 'not-only-but-also' in cats


def test_flag_meta_framing():
    text = "Let's explore the idea. Here's the thing though.\n"
    cats = {f[1] for f in find_flags(text)}
    assert 'meta-framing' in cats


def test_flag_in_conclusion():
    text = "In summary, we shipped it.\n"
    cats = {f[1] for f in find_flags(text)}
    assert 'conclusion-closer' in cats


def test_flags_only_in_prose_not_code():
    text = "```\ndelve into code\n```\nplain delve here\n"
    flags = find_flags(text)
    lines = [f[0] for f in flags if f[1] == 'vocab']
    assert lines == [4]   # not line 2 (inside code block)


def test_flag_tricolon_threshold():
    # Three rule-of-three lists in one paragraph -> flag.
    text = "It is fast, cheap, and good. Also bold, smart, and kind. Plus red, green, and blue.\n"
    cats = {f[1] for f in find_flags(text)}
    assert 'tricolon-overuse' in cats


def test_flag_bold_overuse():
    # >5 bold spans per 1000 words -> flag.
    text = " **a** **b** **c** **d** **e** **f** in a short post\n"
    cats = {f[1] for f in find_flags(text)}
    assert 'bold-overuse' in cats


from deai import compute_stats


def test_stats_burstiness_on_known_lengths():
    # sentences of 2 and 10 words -> mean 6, stdev 4
    text = "I am. One two three four five six seven eight nine ten.\n"
    st = compute_stats(text)
    assert st['sentence_count'] == 2
    assert st['sentence_length_mean'] == 6.0
    assert st['sentence_length_stdev'] == 4.0


def test_stats_counts_em_dashes_and_commas():
    text = "a — b — c, d, e, f\n"
    st = compute_stats(text)
    assert st['em_dash_density_per_1k'] > 0
    assert st['comma_density_per_1k'] > 0


def test_stats_bold_spans():
    text = "this has **one** and **two** bold spans\n"
    assert compute_stats(text)['bold_spans'] == 2


def test_stats_ignore_front_matter_and_code():
    text = "---\ntitle: **not counted**\n---\nreal **bold** word\n"
    st = compute_stats(text)
    assert st['bold_spans'] == 1   # the one in front matter is excluded


import tempfile, os
from deai import process


def _write(tmp, body):
    fd, path = tempfile.mkstemp(suffix='.qmd', dir=tmp)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(body)
    return path


def test_process_dry_run_does_not_write():
    body = "a — b\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, body)
        before = open(path, encoding='utf-8').read()
        result = process(path, write=False)
        after = open(path, encoding='utf-8').read()
    assert before == after                 # file untouched
    assert result['changed'] is True
    assert result['fixed'] == "a, b\n"


def test_process_write_applies_tier1():
    body = "a — b\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, body)
        result = process(path, write=True)
        after = open(path, encoding='utf-8').read()
    assert after == "a, b\n"
    assert result['changed'] is True


def test_process_protected_regions_byte_identical():
    body = "---\ntitle: 'T — keep'\n---\nprose — here\n```\ncode — stay\n```\n[link — x](http://y/z—w)\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, body)
        result = process(path, write=True)
        after = open(path, encoding='utf-8').read()
    assert "title: 'T — keep'" in after           # front matter intact
    assert "code — stay" in after                  # code block intact
    assert "http://y/z—w" in after                 # URL intact
    assert "prose, here" in after                  # prose fixed


def test_process_returns_flags_and_stats():
    body = "We delve into it. Done.\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, body)
        result = process(path, write=False)
    assert any(f[1] == 'vocab' for f in result['flags'])
    assert 'word_count' in result['stats']
