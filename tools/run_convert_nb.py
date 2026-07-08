import pathlib, re
from convert_post import convert_notebook, convert_frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB = ROOT / "_notebooks"
POSTS = ROOT / "_posts"
OUT = ROOT / "posts"

def slugify(name: str) -> str:
    base = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name).removesuffix(".ipynb")
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")

def corresponding_md(nb_name: str) -> pathlib.Path:
    # fastpages writes _posts/<date>-<slug>.md, turning the notebook's spaces into dashes.
    return POSTS / (nb_name.removesuffix(".ipynb").replace(" ", "-") + ".md")

def fm_from_md(md_path: pathlib.Path, nb_name: str) -> str:
    # Source AUTHORITATIVE front matter (real title/categories/description) from the
    # generated post, reusing the tested convert_frontmatter (drops notebook keys,
    # keeps title/categories/description/image, pulls date from filename). Falls back
    # to a filename-derived title only if the generated post is missing.
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        print(f"warning: {nb_name}: no generated post at {md_path.name}; using filename-derived front matter")
        title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", nb_name).removesuffix(".ipynb").replace("_", " ")
        return convert_frontmatter(f"title: {title}\n", nb_name)
    return convert_frontmatter("---\n" + m.group(1) + "\n---", nb_name)

for nb in sorted(NB.glob("*.ipynb")):
    fm_yaml = fm_from_md(corresponding_md(nb.name), nb.name)
    out_dir = OUT / slugify(nb.name)
    convert_notebook(nb, out_dir / "index.ipynb", fm_yaml)
    print(f"{nb.name} -> {out_dir.relative_to(ROOT)}")
