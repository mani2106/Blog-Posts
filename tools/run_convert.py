import pathlib, re
from convert_post import convert

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
OUT = ROOT / "posts"

def slugify(name: str) -> str:
    base = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name).removesuffix(".md")
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")

for p in sorted(POSTS.glob("*.md")):
    txt = p.read_text(encoding="utf-8")
    if re.search(r"layout:\s*notebook", txt) or "nb_path:" in txt:
        continue  # notebooks handled in Task 6
    out_dir = OUT / slugify(p.name)
    convert(p, out_dir / "index.qmd")
    print(f"{p.name} -> {out_dir.relative_to(ROOT)}")
