#!/usr/bin/env python3
"""Build backend wheel and frontend assets, then bundle into a tarball.

If environment variables for an internal registry or GitHub are provided,
artifacts are uploaded for external access.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import tarfile

import requests

ROOT = pathlib.Path(__file__).parent.resolve()
DIST = ROOT / "dist"
FRONTEND = ROOT / "apps" / "legal_discovery"
FRONTEND_DIST = FRONTEND / "dist"


def build_backend() -> pathlib.Path:
    """Build the backend wheel using python -m build."""
    subprocess.run(
        ["python", "-m", "build", "--wheel", "--outdir", str(DIST)], check=True
    )
    wheel = next(DIST.glob("*.whl"))
    return wheel


def build_frontend() -> None:
    """Install frontend dependencies and build assets using npm."""
    subprocess.run(["npm", "--prefix", str(FRONTEND), "ci"], check=True)
    subprocess.run(["npm", "--prefix", str(FRONTEND), "run", "build"], check=True)


def create_tarball(wheel: pathlib.Path) -> pathlib.Path:
    """Package the wheel and frontend assets into a gzip tarball."""
    tar_path = DIST / f"release-{wheel.stem}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(wheel, arcname=wheel.name)
        tar.add(FRONTEND_DIST, arcname="frontend")
    return tar_path


def upload_internal_registry(tar_path: pathlib.Path) -> None:
    """Upload artifact to an internal registry if configured."""
    url = os.environ.get("INTERNAL_REGISTRY_URL")
    token = os.environ.get("INTERNAL_REGISTRY_TOKEN")
    if not url:
        return
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    with tar_path.open("rb") as fh:
        requests.put(f"{url.rstrip('/')}/{tar_path.name}", headers=headers, data=fh)


def upload_github_release(tar_path: pathlib.Path, wheel: pathlib.Path) -> None:
    """Upload artifact to GitHub Releases if credentials are present."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not (repo and token):
        return
    version = wheel.name.split("-")[1]
    tag = f"v{version}"
    api = "https://api.github.com"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    # Create or fetch release
    r = requests.get(f"{api}/repos/{repo}/releases/tags/{tag}", headers=headers)
    if r.status_code == 404:
        r = requests.post(
            f"{api}/repos/{repo}/releases",
            headers=headers,
            json={"tag_name": tag, "name": tag},
        )
    r.raise_for_status()
    upload_url = r.json()["upload_url"].split("{")[0]
    with tar_path.open("rb") as fh:
        headers_update = headers.copy()
        headers_update["Content-Type"] = "application/gzip"
        requests.post(
            f"{upload_url}?name={tar_path.name}",
            headers=headers_update,
            data=fh,
        )


def main() -> None:
    DIST.mkdir(exist_ok=True)
    wheel = build_backend()
    build_frontend()
    tar_path = create_tarball(wheel)
    upload_internal_registry(tar_path)
    upload_github_release(tar_path, wheel)
    print(f"Created {tar_path}")


if __name__ == "__main__":
    main()
