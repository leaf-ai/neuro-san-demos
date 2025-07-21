from pathlib import Path

# Base directory for all cached markdown
KNOWDOCS_PATH = Path(__file__).parent / "knowdocs"

# Subdirectories for raw and enhanced markdown
RAW_MD_PATH = KNOWDOCS_PATH / "raw_md"
ENHANCED_MD_PATH = KNOWDOCS_PATH / "enhanced_md"

def _slug(url: str) -> str:
    """Return slug from URL, defaulting to 'index' if empty."""
    return url.rstrip("/").split("/")[-1] or "index"

def page_exists(url: str, enhanced: bool = False) -> bool:
    """Return True if markdown for URL already exists."""
    path_root = ENHANCED_MD_PATH if enhanced else RAW_MD_PATH
    file_path = path_root / f"{_slug(url)}.md"
    return file_path.is_file()


def markdown_path(url: str, enhanced: bool = False) -> Path:
    """Return full path to the markdown file for the URL."""
    path_root = ENHANCED_MD_PATH if enhanced else RAW_MD_PATH
    slug = url.rstrip("/").split("/")[-1] or "index"
    return path_root / f"{_slug(url)}.md"

def read_markdown(url: str, enhanced: bool = False) -> str:
    """Read markdown file for the URL, or return empty string if not found."""
    file_path = markdown_path(url, enhanced=enhanced)
    if file_path.is_file():
        return file_path.read_text(encoding="utf-8").strip()
    return ""

def write_markdown(url: str, content: str, enhanced: bool = False) -> Path:
    """Write markdown content to the file for the URL."""
    root = ENHANCED_MD_PATH if enhanced else RAW_MD_PATH
    root.mkdir(parents=True, exist_ok=True)
    file_path = markdown_path(url, enhanced=enhanced)
    file_path.write_text(content, encoding="utf-8")
    print(f"Markdown written to {file_path}")
    return file_path