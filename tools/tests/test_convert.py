import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from convert_post import convert_frontmatter

def _yaml_scalar_pairs(text):
    """Map each top-level 'key: value' line to {key: value}, skipping
    block-list items. Robust to PyYAML's quote/flow-style choices."""
    pairs = {}
    for line in text.splitlines():
        if line and not line.startswith((" ", "\t", "-")) and ":" in line:
            k, _, v = line.partition(":")
            pairs[k.strip()] = v.strip()
    return pairs

def test_drops_fastpages_keys_and_maps_summary():
    raw = """---
title: "My Post"
layout: post
keywords: a, b
toc: true
branch: master
badges: true
comments: true
categories: [azure, ai]
hide: false
summary: "Real summary"
image: images/azure/d.png
---"""
    out = convert_frontmatter(raw, "2025-11-17-azure-post.md")
    pairs = _yaml_scalar_pairs(out)
    for bad in ("layout", "keywords", "toc", "branch", "badges", "comments", "hide", "nb_path", "summary"):
        assert bad not in pairs, f"{bad!r} should be dropped; output was:\n{out}"
    assert pairs.get("title") == "My Post"
    assert "azure" in out and "ai" in out                    # categories preserved (style-agnostic)
    assert "2025-11-17" in pairs.get("date", "")             # date pulled from filename
    assert "Real summary" in pairs.get("description", "")    # summary -> description
    assert pairs.get("image") == "images/azure/d.png"

def test_date_pulled_from_filename_when_absent():
    raw = '---\ntitle: "X"\n---'
    out = convert_frontmatter(raw, "2019-06-01-Fast_ai_lesson_2.md")
    assert "2019-06-01" in out

if __name__ == "__main__":
    test_drops_fastpages_keys_and_maps_summary()
    test_date_pulled_from_filename_when_absent()
    print("OK")
