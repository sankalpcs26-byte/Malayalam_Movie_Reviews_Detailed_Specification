import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


# Paths are based on the project root, so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "contributor-log.json"
README_FILE = PROJECT_ROOT / "README.md"

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPOSITORY = os.getenv("REPOSITORY")
GITHUB_API = "https://api.github.com"

START_MARKER = "<!-- CONTRIBUTOR_TABLE_START -->"
END_MARKER = "<!-- CONTRIBUTOR_TABLE_END -->"


def github_request(url):
    """Send a request to GitHub and return the decoded JSON response."""
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "contributor-tracker",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub returned HTTP {error.code}: {message}") from error


def github_api(path):
    """Fetch one GitHub API resource."""
    url = path if path.startswith("https://") else GITHUB_API + path
    return github_request(url)


def github_api_pages(path):
    """Fetch every page of a GitHub API list endpoint."""
    results = []
    next_url = GITHUB_API + path

    while next_url:
        request = urllib.request.Request(
            next_url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "contributor-tracker",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                results.extend(json.loads(response.read().decode("utf-8")))
                link_header = response.headers.get("Link", "")

        except urllib.error.HTTPError as error:
            message = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"GitHub returned HTTP {error.code}: {message}"
            ) from error

        match = re.search(r'<([^>]+)>;\\s*rel="next"', link_header)
        next_url = match.group(1) if match else None

    return results


def load_database():
    """Load saved contribution history, or start with an empty database."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        return {
            "version": 1,
            "last_updated": None,
        }
