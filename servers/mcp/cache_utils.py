from pathlib import Path

KNOWDOCS_PATH = Path(__file__).parent / "knowdocs"


def page_exists(url: str) -> bool:
    """Return True if markdown for URL already exists in KNOWDOCS_PATH."""
    slug = url.rstrip("/").split("/")[-1] or "index"
    file_path = KNOWDOCS_PATH / f"{slug}.md"
    return file_path.is_file()


def markdown_path(url: str) -> Path:
    """Return full path to the markdown file for the URL."""
    slug = url.rstrip("/").split("/")[-1] or "index"
    return KNOWDOCS_PATH / f"{slug}.md"