"""Generate docs/blogs/index.md from blog post frontmatter."""

import os
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

def main():
    posts = []
    for f in sorted(BLOG_DIR.glob("*.md")):
        if f.name == "index.md":
            continue
        fm = extract_frontmatter(f)
        date = fm.get("date", "")
        title = extract_title(f)
        posts.append((date, title, f.name))

    posts.sort(key=lambda x: x[0], reverse=True)

    lines = [
        "---",
        "icon: lucide/notebook-pen",
        "---",
        "",
        "# Blogs",
        "",
    ]
    for date, title, fname in posts:
        date_str = f" *{date}*" if date else ""
        lines.append(f"- [{title}]({fname}){date_str}")

    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {INDEX_PATH} with {len(posts)} posts")

if __name__ == "__main__":
    main()
