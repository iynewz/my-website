# Project Overview

This is **iynewz's dev center**, a personal technical documentation and blog site built with [Zensical](https://zensical.org/) - a modern static site generator optimized for documentation (similar to MkDocs with Material theme).

The site serves as a learning journal covering topics like C++, systems programming (CSAPP), operating systems (OSTEP), LevelDB, and personal essays. The site is deployed at https://iynewz.dev.

## Technology Stack

- **Static Site Generator**: Zensical (Python-based, Material-inspired theme)
- **Content Format**: Markdown with YAML frontmatter
- **Programming Language**: Python 3.x (for build scripts)
- **Deployment**: GitHub Pages via GitHub Actions
- **Comment System**: Giscus (GitHub Discussions-based)
- **Analytics**: Google Analytics 4
- **External Integration**: Feishu API (for daily quotes synchronization)

## Project Structure

```
my-website/
├── zensical.toml          # Main configuration file (equivalent to mkdocs.yml)
├── docs/                  # Source content directory
│   ├── index.md           # Homepage
│   ├── markdown.md        # Markdown syntax reference/examples
│   ├── quotes.json        # Daily quotes data (auto-generated from Feishu)
│   ├── javascripts/       # Custom JavaScript files
│   │   └── extra.js       # Daily quote display logic
│   ├── c-plus-plus-primer/ # C++ learning notes
│   ├── csapp/             # CSAPP (Computer Systems) notes
│   ├── OSTEP/             # OSTEP (Operating Systems) notes
│   ├── level-db/          # LevelDB study notes
│   ├── blogs/             # Blog posts
│   ├── random-thoughts/   # Personal essays
│   └── today-i-learn/     # TIL (Today I Learned) entries
├── overrides/             # Theme template overrides
│   └── partials/
│       └── comments.html  # Giscus comments integration
├── scripts/               # Automation scripts
│   └── fetch_quotes.py    # Feishu → quotes.json sync script
├── site/                  # Build output (generated, gitignored)
├── .github/workflows/     # CI/CD configuration
│   └── docs.yml           # GitHub Actions workflow
├── .venv/                 # Python virtual environment
├── .env                   # Local environment variables (gitignored)
└── .gitignore             # Git ignore rules
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

# Serve locally with auto-reload
zensical serve

# Build site (output to site/ directory)
zensical build --clean
```

### Configuration

The main configuration is in `zensical.toml`:

- `site_name`, `site_description`, `site_author`, `site_url`: Basic site metadata
- `nav`: Explicit navigation structure defining the sidebar menu
- `project.theme`: Theme customization (custom_dir, palette for dark/light mode, features)
- `project.extra`: Social links and analytics configuration

## Content Authoring Guidelines

### Markdown Frontmatter

Each markdown file can include YAML frontmatter at the top:

```yaml
---
icon: lucide/rocket        # Page icon (Lucide icons)
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

### Special Features

1. **Daily Quotes**: The homepage displays random quotes fetched from a Feishu Bitable. Edit the quotes in Feishu and run the sync script to update.

2. **Comments**: Add `comments: true` to frontmatter to enable Giscus comments on a page.

3. **Icons**: Use `icon:` in frontmatter or `:icon_name:` in content (supports Lucide and FontAwesome icons).

4. **Code Blocks**: Supports syntax highlighting, line highlighting, and annotations:
   ```markdown
   ``` python hl_lines="2" title="example.py"
   def hello():
       print("Hello")  # (1)!
   ```
   ```

## CI/CD and Deployment

The project uses GitHub Actions (`.github/workflows/docs.yml`) for automated deployment:

### Workflow Steps:

1. **Checkout** repository
2. **Install Python dependencies**: `requests`, `python-dotenv`, `zensical`
3. **Sync Feishu quotes**: Run `fetch_quotes.py` with repository secrets
4. **Commit changes**: Auto-commit updated `quotes.json` if changed
5. **Inject GA ID**: Replace `${GA_MEASUREMENT_ID}` placeholder in config
6. **Build site**: Run `zensical build --clean`
7. **Deploy to GitHub Pages**: Upload and deploy `site/` directory

### Required Repository Secrets:

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

## Code Style Guidelines

### Python Scripts

- Follow PEP 8 style guide
- Use type hints where appropriate
- Include docstrings for functions
- Handle API errors gracefully with try/except

### Markdown Content

- Use ATX-style headers (`#` not underline)
- Prefer `-` for unordered lists
- Use fenced code blocks with language specification
- Keep lines reasonably short for readability
- Use Chinese or English consistently within documents

### JavaScript

- Use ES6+ syntax
- Include error handling for async operations
- Comment complex logic

## Testing

There are no automated tests in this project. Testing is done by:

1. **Local preview**: Run `zensical serve` and verify changes visually
2. **Build verification**: Run `zensical build --clean` to ensure no build errors
3. **Link checking**: Manually verify internal links work

## Security Considerations

1. **Secrets Management**: Never commit `.env` file or hardcode secrets. Use GitHub Secrets for CI/CD.

2. **API Keys**: Feishu API credentials have limited scope (read-only access to specific Bitable).

3. **Comments**: Giscus comments are moderated through GitHub Discussions in a separate repository (`my-website-comments`).

4. **Analytics**: Google Analytics is configured to anonymize IP addresses.

5. **Dependencies**: Keep Python dependencies updated, especially `requests` and `zensical`.

## Troubleshooting

### Build Failures

- Check `zensical.toml` syntax (valid TOML format)
- Verify all referenced files in `nav` exist
- Ensure Python dependencies are installed

### Quote Sync Issues

- Verify Feishu credentials in `.env` or repository secrets
- Check Feishu Bitable structure matches expected format
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
