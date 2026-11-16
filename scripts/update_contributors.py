import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "contributor-log.json"
README_FILE = PROJECT_ROOT / "README.md"
GITHUB_API = "https://api.github.com"
START_MARKER = "<!-- CONTRIBUTOR-LOG:START -->"
END_MARKER = "<!-- CONTRIBUTOR-LOG:END -->"


def github_request(url):
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN is required to access the GitHub API.")

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "contributor-tracker",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8")), response.headers.get(
                "Link", ""
            )
    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub returned HTTP {error.code} for {url}: {message}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach the GitHub API: {error.reason}") from error


def github_api(path):
    url = path if path.startswith("https://") else GITHUB_API + path
    return github_request(url)[0]


def github_api_pages(path):
    results = []
    next_url = GITHUB_API + path

    while next_url:
        page, link_header = github_request(next_url)
        if not isinstance(page, list):
            raise RuntimeError(f"Expected a list response from GitHub for {next_url}")
        results.extend(page)
        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        next_url = match.group(1) if match else None

    return results


def load_database():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding="utf-8").strip():
        return {"version": 1, "last_updated": None, "pull_requests": []}

    try:
        database = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Invalid contributor data in {DATA_FILE}: {error}") from error

    if not isinstance(database, dict) or not isinstance(
        database.get("pull_requests"), list
    ):
        raise RuntimeError(f"Unexpected contributor data format in {DATA_FILE}")
    return database


def markdown_cell(value):
    return str(value).replace("\\", "\\\\").replace("|", r"\|").replace("\n", " ")


def format_commit_range(commits, merge_commit_sha, repository):
    hashes = [commit["sha"] for commit in commits if commit.get("sha")]
    if not hashes and merge_commit_sha:
        hashes = [merge_commit_sha]
    if not hashes:
        return "—"

    first, last = hashes[0], hashes[-1]

    def link(commit_hash):
        short_hash = commit_hash[:7]
        url = f"https://github.com/{repository}/commit/{commit_hash}"
        return f"[`{short_hash}`]({url})"

    if first == last:
        return link(first)
    return f"{link(first)}...{link(last)}"


def get_pull_request_record(pull_request, repository):
    number = pull_request["number"]
    login = (pull_request.get("user") or {}).get("login") or "unknown"
    user = github_api(f"/users/{urllib.parse.quote(login, safe='')}")
    name = user.get("name") or login
    encoded_repository = urllib.parse.quote(repository, safe="/")
    commits = github_api_pages(
        f"/repos/{encoded_repository}/pulls/{number}/commits?per_page=100"
    )
    files = github_api_pages(
        f"/repos/{encoded_repository}/pulls/{number}/files?per_page=100"
    )

    changed_files = ", ".join(
        f"`{markdown_cell(item['filename'])}`"
        for item in files
        if item.get("filename")
    )
    title = markdown_cell(pull_request.get("title") or "Merged pull request")
    tasks = f"{title} — {changed_files}" if changed_files else title

    return {
        "number": number,
        "merged_at": pull_request.get("merged_at") or "",
        "name": name,
        "login": login,
        "tasks": tasks,
        "commits": format_commit_range(
            commits, pull_request.get("merge_commit_sha"), repository
        ),
        "url": pull_request["html_url"],
    }


def fetch_merged_pull_requests(repository):
    encoded_repository = urllib.parse.quote(repository, safe="/")
    pull_requests = github_api_pages(
        f"/repos/{encoded_repository}/pulls?state=closed&per_page=100&sort=updated&direction=asc"
    )
    merged = [pull for pull in pull_requests if pull.get("merged_at")]
    records = [get_pull_request_record(pull, repository) for pull in merged]
    return sorted(records, key=lambda record: (record["merged_at"], record["number"]))


def render_readme(records):
    readme = README_FILE.read_text(encoding="utf-8")
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise RuntimeError("README.md must contain exactly one pair of contributor log markers.")

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    if start >= end:
        raise RuntimeError("Contributor log markers in README.md are out of order.")

    existing_lines = [
        line
        for line in readme[start:end].splitlines()
        if line.lstrip().startswith("|")
    ]
    if len(existing_lines) < 2:
        raise RuntimeError("README.md contributor table must have a header and separator.")

    rows = []
    for record in records:
        name = markdown_cell(record["name"])
        login = markdown_cell(record["login"])
        tasks = record["tasks"]
        commits = record["commits"]
        number = record["number"]
        url = record["url"]
        rows.append(
            f"| {name} | `@{login}` | {tasks} | {commits} | [#{number}]({url}) |"
        )

    table = "\n\n" + "\n".join(existing_lines[:2] + rows) + "\n\n"
    return readme[:start] + table + readme[end:]


def write_if_changed(path, content):
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main():
    repository = os.environ.get("REPOSITORY")
    if not repository or "/" not in repository:
        raise RuntimeError("REPOSITORY must be set to an owner/repository value.")

    database = load_database()
    records = fetch_merged_pull_requests(repository)
    readme = render_readme(records)
    data_changed = records != database["pull_requests"]

    updated_database = {
        "version": 1,
        "last_updated": (
            datetime.now(timezone.utc).isoformat()
            if data_changed
            else database.get("last_updated")
        ),
        "pull_requests": records,
    }
    readme_changed = write_if_changed(README_FILE, readme)
    data_changed = write_if_changed(
        DATA_FILE, json.dumps(updated_database, indent=2, ensure_ascii=False) + "\n"
    ) or data_changed

    if readme_changed or data_changed:
        print(f"Updated contributor log with {len(records)} merged pull request(s).")
    else:
        print(f"Contributor log is up to date ({len(records)} merged pull request(s)).")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
