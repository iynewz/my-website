# Project Overview

This is **iynewz's dev center** (https://iynewz.dev), a personal technical documentation and blog site built with [Zensical](https://zensical.org/) - a Python-based static site generator with a Material-inspired theme (similar to MkDocs Material).

The site serves as a learning journal covering:
- C++ programming (C++ Primer notes)
- Systems programming (CSAPP - Computer Systems: A Programmer's Perspective)
- Operating systems (OSTEP - Operating Systems: Three Easy Pieces)
- Database internals (LevelDB study notes)
- Personal essays and blog posts
- Today-I-Learned (TIL) entries

## Technology Stack

- **Static Site Generator**: Zensical (Python-based, MkDocs-Material-like)
- **Configuration**: TOML format (`zensical.toml`)
- **Content Format**: Markdown with YAML frontmatter
- **Programming Language**: Python 3.x (for automation scripts)
- **Deployment**: GitHub Pages via GitHub Actions
- **Comment System**: Giscus (GitHub Discussions-based comments)
- **Analytics**: Google Analytics 4
- **External Integration**: Feishu API (for daily quotes synchronization)

## Project Structure

```
my-website/
├── zensical.toml              # Main configuration file
├── docs/                      # Source content directory
│   ├── index.md               # Homepage with daily quote display
│   ├── markdown.md            # Markdown syntax reference
│   ├── quotes.json            # Daily quotes data (auto-generated from Feishu)
│   ├── javascripts/           # Custom JavaScript files
│   │   └── extra.js           # Daily quote display logic
│   ├── c-plus-plus-primer/    # C++ learning notes (Ch 7, 12, 13, etc.)
│   ├── csapp/                 # CSAPP notes (Ch 3, 6, 8-12)
│   ├── OSTEP/                 # OSTEP notes (processes, threads, scheduling, concurrency)
│   ├── level-db/              # LevelDB study notes
│   ├── blogs/                 # Blog posts (algorithms, essays)
│   ├── random-thoughts/       # Personal essays
│   └── today-i-learn/         # TIL entries (YYMM format)
├── overrides/                 # Theme template overrides
│   └── partials/
│       └── comments.html      # Giscus comments integration template
├── scripts/                   # Automation scripts
│   └── fetch_quotes.py        # Feishu → quotes.json sync script
├── site/                      # Build output (generated, gitignored)
├── .github/workflows/         # CI/CD configuration
│   └── docs.yml               # GitHub Actions workflow
├── .venv/                     # Python virtual environment
├── .env                       # Local environment variables (gitignored)
└── .gitignore                 # Git ignore rules
```

## Build and Development Commands

### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install requests python-dotenv zensical

# Sync quotes from Feishu (optional, for local testing)
python scripts/fetch_quotes.py

# Serve locally with auto-reload (default port 8000)
zensical serve

# Build site (output to site/ directory)
zensical build --clean
```

### Configuration Details

The main configuration is in `zensical.toml`:

- **Site metadata**: `site_name`, `site_description`, `site_author`, `site_url`
- **Navigation**: Explicit `nav` array defining sidebar structure
- **Theme**: `project.theme` with palette for dark/light mode, feature toggles
- **Custom overrides**: `custom_dir = "overrides"` for template customization
- **Extra JavaScript**: `extra_javascript` for daily quotes functionality
- **Social links**: GitHub and Zhihu profiles in `project.extra.social`
- **Analytics**: Google Analytics with placeholder `${GA_MEASUREMENT_ID}`

Key theme features enabled:
- `content.code.annotate` - Code annotations
- `content.code.copy` - Copy button for code blocks
- `content.footnote.tooltips` - Inline footnote tooltips
- `navigation.footer` - Prev/next page navigation
- `navigation.indexes` - Section index pages
- `navigation.instant` - Instant navigation via XHR
- `navigation.path` - Breadcrumb navigation
- `navigation.sections` - Section grouping in sidebar
- `navigation.tabs` - Top-level tabs
- `search.highlight` - Search result highlighting
- Dark/light mode toggle with `lucide/sun` and `lucide/moon` icons

## Content Authoring Guidelines

### Markdown Frontmatter

Each markdown file can include YAML frontmatter at the top:

```yaml
---
icon: lucide/rocket        # Page icon (Lucide or FontAwesome icons)
comments: true             # Enable Giscus comments (optional)
tags:
  - 随笔                   # Content tags
  - 人际关系
---
```

### Content Organization

- Place new documentation in appropriate subdirectories under `docs/`
- Update `zensical.toml` `nav` section when adding new sections
- Use kebab-case for file names (e.g., `my-new-post.md`)
- TIL entries use YYMM format (e.g., `2603.md` for March 2026)

### Special Features

1. **Daily Quotes**: 
   - The homepage displays random quotes from `docs/quotes.json`
   - Quotes are fetched from a Feishu Bitable via `scripts/fetch_quotes.py`
   - Display logic is in `docs/javascripts/extra.js`
   - Each quote has `quote` (text), `author`, and optional `source` (URL) fields

2. **Comments**:
   - Add `comments: true` to frontmatter to enable Giscus comments
   - Comments are stored in a separate repository: `iynewz/my-website-comments`
   - Theme synchronization (light/dark) is handled automatically

3. **Icons**:
   - Use `icon:` in frontmatter for page icons
   - Supports Lucide icons (`lucide/icon-name`) and FontAwesome (`fontawesome/...`)
   - Can also use `:icon_name:` syntax in content

4. **Code Blocks**:
   - Supports syntax highlighting, line highlighting, and annotations
   ```markdown
   ``` python hl_lines="2" title="example.py"
   def hello():
       print("Hello")  # (1)!
   ```
   ```

## CI/CD and Deployment

The project uses GitHub Actions (`.github/workflows/docs.yml`) for automated deployment:

### Workflow Steps

1. **Configure GitHub Pages** - Set up Pages environment
2. **Checkout** repository
3. **Setup Python** - Install Python 3.x
4. **Install dependencies** - `requests`, `python-dotenv`, `zensical`
5. **Sync Feishu quotes** - Run `fetch_quotes.py` with repository secrets
6. **Commit changes** - Auto-commit updated `quotes.json` if changed
7. **Inject GA ID** - Replace `${GA_MEASUREMENT_ID}` placeholder in config
8. **Build site** - Run `zensical build --clean`
9. **Deploy to GitHub Pages** - Upload and deploy `site/` directory

### Required Repository Secrets

- `FEISHU_APP_ID`: Feishu app ID for quotes API
- `FEISHU_APP_SECRET`: Feishu app secret
- `FEISHU_APP_TOKEN`: Feishu Bitable app token
- `FEISHU_TABLE_ID`: Feishu table ID for quotes
- `GA_MEASUREMENT_ID`: Google Analytics measurement ID

## Environment Variables

Local development uses `.env` file (gitignored):

```bash
GA_MEASUREMENT_ID=G-XXXXXXXXXX
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
FEISHU_APP_TOKEN=xxxxxxxx
FEISHU_TABLE_ID=xxxxxxxx
```

**Never commit the `.env` file to version control.**

## Code Style Guidelines

### Python Scripts

- Follow PEP 8 style guide
- Use type hints where appropriate
- Include docstrings for functions
- Handle API errors gracefully with try/except
- Use Chinese comments for Feishu-related scripts (matching existing codebase)

Example from `fetch_quotes.py`:
```python
def get_text_field(field):
    """处理 table 的 field，可以是 str 或 list[{\"text\": ...}]"""
    if not field:
        return ""
    if isinstance(field, str):
        return field
    if isinstance(field, list) and len(field) > 0:
        return field[0].get("text", "")
    return ""
```

### Markdown Content

- Use ATX-style headers (`#` not underline)
- Prefer `-` for unordered lists
- Use fenced code blocks with language specification
- Keep lines reasonably short for readability
- Use Chinese or English consistently within documents (bilingual content is common)

### JavaScript

- Use ES6+ syntax (async/await, arrow functions)
- Include error handling for async operations
- Comment complex logic

Example from `extra.js`:
```javascript
window.document$.subscribe(async () => {
  const box = document.getElementById("daily-quote");
  if (!box) return;
  
  try {
    const quotes = await fetchQuotes();
    const q = getRandom(quotes);
    // ... display logic
  } catch (err) {
    console.error("fetchQuotes error:", err);
  }
});
```

## Testing

There are no automated tests in this project. Testing is done by:

1. **Local preview**: Run `zensical serve` and verify changes visually
2. **Build verification**: Run `zensical build --clean` to ensure no build errors
3. **Link checking**: Manually verify internal links work
4. **Quote sync testing**: Run `python scripts/fetch_quotes.py` to verify Feishu integration

## Security Considerations

1. **Secrets Management**: 
   - Never commit `.env` file or hardcode secrets
   - Use GitHub Secrets for CI/CD
   - The `.env` file is listed in `.gitignore`

2. **API Keys**: 
   - Feishu API credentials have limited scope (read-only access to specific Bitable)
   - Tokens are stored securely in GitHub Secrets

3. **Comments**: 
   - Giscus comments are moderated through GitHub Discussions in a separate repository (`my-website-comments`)
   - The comments repository is public

4. **Analytics**: 
   - Google Analytics is configured via environment variable injection in CI/CD
   - Measurement ID is not hardcoded in the config file

5. **Dependencies**: 
   - Keep Python dependencies updated, especially `requests` and `zensical`
   - Virtual environment (`.venv/`) is gitignored

## Troubleshooting

### Build Failures

- Check `zensical.toml` syntax (valid TOML format)
- Verify all referenced files in `nav` exist
- Ensure Python dependencies are installed

### Quote Sync Issues

- Verify Feishu credentials in `.env` or repository secrets
- Check Feishu Bitable structure matches expected format (fields: `quote`, `author`, `source`)
- Review API response in script output for error messages

### Comment System Not Loading

- Verify Giscus configuration in `overrides/partials/comments.html`
- Ensure the comments repository is public
- Check browser console for JavaScript errors

## Useful Resources

- [Zensical Documentation](https://zensical.org/docs/)
- [Material for MkDocs Reference](https://squidfunk.github.io/mkdocs-material/reference/) (similar syntax)
- [Feishu Open API Docs](https://open.feishu.cn/document/home/index)
- [Giscus Configuration](https://giscus.app/)
