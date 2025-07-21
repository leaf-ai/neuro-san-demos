from pathlib import Path

KNOWDOCS_PATH = Path(__file__).parent / "knowdocs"

def _slug(url: str) -> str:
    """Return slug from URL, defaulting to 'index' if empty."""
    return url.rstrip("/").split("/")[-1] or "index"

def page_exists(url: str) -> bool:
    """Return True if markdown for URL already exists in KNOWDOCS_PATH."""
    file_path = KNOWDOCS_PATH / f"{_slug(url)}.md"
    return file_path.is_file()


def markdown_path(url: str) -> Path:
    """Return full path to the markdown file for the URL."""
    slug = url.rstrip("/").split("/")[-1] or "index"
    return KNOWDOCS_PATH / f"{_slug(url)}.md"

def read_markdown(url: str) -> str:
    """Read markdown file for the URL, or return empty string if not found."""
    file_path = markdown_path(url)
    if file_path.is_file():
        return file_path.read_text(encoding="utf-8").strip()
    return ""
def write_markdown(url: str, content: str) -> Path:
    """Write markdown content to the file for the URL."""
    KNOWDOCS_PATH.mkdir(parents=True, exist_ok=True)
    file_path = markdown_path(url)
    file_path.write_text(content, encoding="utf-8")
    print(f"Markdown written to {file_path}")
    return file_path