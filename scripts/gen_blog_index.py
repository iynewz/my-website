"""Generate docs/blogs/index.md from blog post frontmatter."""

import re
from pathlib import Path

BLOG_DIR = Path("docs/blogs")
INDEX_PATH = BLOG_DIR / "index.md"


def extract_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm


def extract_title(path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^# (.+)$", text, re.MULTILINE)
    return m.group(1) if m else path.stem


def extract_excerpt(path, max_chars=140):
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    body = re.sub(r"^# .+\n", "", body, count=1, flags=re.MULTILINE)
    for para in body.split("\n\n"):
        para = para.strip()
        if not para or para.startswith(("#", ">", "*", "-", "`", "|")):
            continue
        para = re.sub(r"\s+", " ", para)
        if len(para) > max_chars:
            para = para[: max_chars - 1].rstrip() + "…"
        return para
    return ""


def main():
    posts = []
    for f in sorted(BLOG_DIR.glob("*.md")):
        if f.name == "index.md":
            continue
        fm = extract_frontmatter(f)
        posts.append(
            {
                "date": fm.get("date", ""),
                "title": extract_title(f),
                "excerpt": extract_excerpt(f),
                "fname": f.name,
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)

    lines = [
        "---",
        "icon: lucide/notebook-pen",
        "hide:",
        "  - navigation",
        "  - toc",
        "---",
        "",
        "# Blogs",
        "",
    ]
    for p in posts:
        date_str = f" <span class=\"post-date\">· {p['date']}</span>" if p["date"] else ""
        lines.append(f"### [{p['title']}]({p['fname']}){date_str}")
        lines.append("")
        if p["excerpt"]:
            lines.append(p["excerpt"])
            lines.append("")

    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {INDEX_PATH} with {len(posts)} posts")


if __name__ == "__main__":
    main()
