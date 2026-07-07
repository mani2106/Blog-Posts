import re
import pathlib

DROP_KEYS = {"layout", "keywords", "toc", "branch", "badges", "comments", "hide", "nb_path"}
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

def _strip_fences(raw_yaml: str) -> str:
    lines = raw_yaml.strip().splitlines()
    if lines and lines[0].strip() == "---":
        lines = lines[1:]
    if lines and lines[-1].strip() == "---":
        lines = lines[:-1]
    return "\n".join(lines)

def convert_frontmatter(raw_yaml: str, filename: str) -> str:
    import yaml
    body = _strip_fences(raw_yaml)
    data = yaml.safe_load(body) or {}
    m = DATE_RE.match(pathlib.Path(filename).name)
    if m:
        data.setdefault("date", m.group(1))
    if "summary" in data and "description" not in data:
        data["description"] = data.pop("summary")
    elif "summary" in data:
        data.pop("summary", None)
    for k in DROP_KEYS:
        data.pop(k, None)
    out = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    return out
