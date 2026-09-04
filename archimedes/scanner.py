from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

from .models import Asset

EXTENSIONS = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".sql": "SQL", ".yaml": "YAML",
    ".yml": "YAML", ".json": "JSON", ".md": "Markdown", ".html": "HTML",
    ".css": "CSS", ".sh": "Shell", ".toml": "TOML"
}
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


def terms(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u3040-\u30ff\u4e00-\u9fff]{2,}", text.lower())
    return sorted(set(words))[:200]


def classify(path: Path) -> str:
    if path.name in {"README.md", "AGENTS.md", "CLAUDE.md", "SKILL.md"}: return "documentation"
    if ".github" in path.parts and path.suffix in {".yml", ".yaml"}: return "workflow"
    if path.suffix in {".yaml", ".yml", ".json", ".toml"}: return "config"
    if path.suffix == ".ipynb": return "notebook"
    if path.suffix in {".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java", ".sh"}: return "code"
    return "file"


def scan_local(root: str | Path) -> list[Asset]:
    root = Path(root).resolve()
    assets: list[Asset] = []
    for p in root.rglob("*"):
        if not p.is_file() or any(part in SKIP for part in p.parts): continue
        rel = p.relative_to(root)
        try: text = p.read_text(encoding="utf-8", errors="ignore")[:100_000]
        except OSError: text = ""
        stat = p.stat()
        assets.append(Asset(
            id=f"file:{rel.as_posix()}", kind=classify(p), name=p.name, path=rel.as_posix(),
            language=EXTENSIONS.get(p.suffix.lower()), lifecycle="reusable" if p.name.startswith(("README", "AGENTS", "SKILL")) else "experimental",
            terms=terms(p.name + " " + text), metadata={"bytes": stat.st_size, "mtime": stat.st_mtime}
        ))
    return assets


def scan_github(owner: str, token: str | None = None) -> list[Asset]:
    url = f"https://api.github.com/users/{urllib.parse.quote(owner)}/repos?per_page=100&type=all"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token: req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r: repos = json.load(r)
    return [Asset(
        id=f"repo:{r['full_name']}", kind="repository", name=r["name"], repository=r["full_name"],
        language=r.get("language"), lifecycle="reusable", terms=terms((r.get("name") or "") + " " + (r.get("description") or "")),
        metadata={k: r.get(k) for k in ("stargazers_count", "forks_count", "size", "archived", "default_branch", "updated_at")}
    ) for r in repos]


def write_jsonl(assets: list[Asset], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(a.to_dict(), ensure_ascii=False) + "\n" for a in assets), encoding="utf-8")
