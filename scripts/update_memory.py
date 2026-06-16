#!/usr/bin/env python3
"""Refresh managed memory sections after graph sync and git changes."""

from __future__ import annotations

from dataclasses import dataclass
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    GRAPH_SYNC_TIMEOUT_SEC,
    extract_human_notes_region,
    is_test_path,
    load_config,
    path_mentioned_in_region,
    risk_tags,
    subsystem_files,
)

MANAGED_START = "<!-- agentic:managed:start -->"
MANAGED_END = "<!-- agentic:managed:end -->"
UPDATE_REF = ".agentic/CONTEXT/last_update_ref"


@dataclass(frozen=True)
class GitChangeSet:
    paths: list[str]
    error: str | None = None


def repo_root() -> Path:
    root = Path.cwd()
    if not (root / ".agentic").is_dir():
        print("error: run from repository root", file=sys.stderr)
        sys.exit(1)
    return root


def run_graph_sync(root: Path) -> tuple[bool, str]:
    script = root / "scripts/agentic/graph_sync.py"
    if not script.is_file():
        return False, "graph_sync.py missing — skipped"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=root,
            capture_output=True,
            check=False,
            text=True,
            timeout=GRAPH_SYNC_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return False, f"graph_sync timed out after {GRAPH_SYNC_TIMEOUT_SEC}s"
    if result.returncode != 0:
        return False, result.stderr.strip() or "graph_sync failed"
    return True, result.stdout.strip()


def git_head(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_commit_time(root: Path, head: str | None) -> str | None:
    if not head:
        return None
    try:
        out = subprocess.run(
            ["git", "show", "-s", "--format=%cI", head],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_changed_files(root: Path, since_ref: str | None) -> GitChangeSet:
    if since_ref is None:
        return GitChangeSet([])
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", since_ref, "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return GitChangeSet([line.strip() for line in out.stdout.splitlines() if line.strip()])
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        return GitChangeSet([], f"git diff failed for {since_ref}: {detail}")
    except FileNotFoundError:
        return GitChangeSet([], "git unavailable")


def product_changed_files(changed: list[str], config: dict) -> list[str]:
    """Drop test-only paths before mapping changed files to subsystem memory."""
    return [path for path in changed if not is_test_path(path, config)]


def affected_memory_files(changed: list[str], root: Path, config: dict) -> list[str]:
    return subsystem_files(root, product_changed_files(changed, config))


def infer_subsystems(changed: list[str], root: Path, config: dict | None = None) -> list[str]:
    """Return subsystem stems for compatibility with older callers."""
    cfg = config or {}
    return [Path(path).stem for path in affected_memory_files(changed, root, cfg)]


def replace_managed_block(content: str, new_inner: str) -> str:
    if MANAGED_START not in content or MANAGED_END not in content:
        return content
    before, rest = content.split(MANAGED_START, 1)
    _, after = rest.split(MANAGED_END, 1)
    return before + MANAGED_START + new_inner + MANAGED_END + after


def format_path_list(paths: list[str]) -> str:
    return ", ".join(f"`{path}`" for path in paths) if paths else "none"


def format_plain_list(items: list[str]) -> str:
    return ", ".join(items) if items else "none"


def upsert_evidence_refresh_section(inner: str, section: str) -> str:
    pattern = r"\n## Evidence refresh\n.*?(?=\n## |\Z)"
    replacement = "\n" + section.strip() + "\n"
    if re.search(pattern, inner, flags=re.DOTALL):
        return re.sub(pattern, replacement, inner, count=1, flags=re.DOTALL)
    return inner.rstrip() + "\n\n" + section.strip() + "\n"


def refresh_managed_memory_file(
    root: Path,
    rel_path: str,
    *,
    product_paths: list[str],
    test_paths: list[str],
    risks: list[str],
    head: str | None,
    refreshed_at: str | None,
) -> bool:
    path = root / rel_path
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    if MANAGED_START not in content or MANAGED_END not in content:
        return False
    if content.index(MANAGED_START) >= content.index(MANAGED_END):
        return False

    before, rest = content.split(MANAGED_START, 1)
    inner, after_managed = rest.split(MANAGED_END, 1)
    section = "\n".join(
        [
            "## Evidence refresh",
            "",
            f"- Commit: `{head or 'unknown'}`",
            f"- Refreshed at: {refreshed_at or 'unknown'}",
            f"- Product paths: {format_path_list(product_paths)}",
            f"- Related test paths: {format_path_list(test_paths)}",
            f"- Risk tags: {format_plain_list(risks)}",
        ]
    )
    inner = upsert_evidence_refresh_section(inner, section)
    path.write_text(before + MANAGED_START + inner + MANAGED_END + after_managed, encoding="utf-8")
    return True


def refresh_memory_index(
    root: Path,
    refreshed_files: list[str],
    *,
    refreshed_at: str | None = None,
) -> bool:
    path = root / ".agentic/MEMORY_INDEX.md"
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    if MANAGED_START not in content or MANAGED_END not in content:
        return False
    if content.index(MANAGED_START) >= content.index(MANAGED_END):
        return False
    now = refreshed_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    managed, rest = content.split(MANAGED_START, 1)
    inner, after_managed = rest.split(MANAGED_END, 1)
    inner = re.sub(
        r"- Last refreshed:.*",
        f"- Last refreshed: {now}",
        inner,
        count=1,
    )
    file_list = ", ".join(f"`{f}`" for f in refreshed_files) if refreshed_files else "none"
    if "- Files refreshed this run:" in inner:
        inner = re.sub(
            r"- Files refreshed this run:.*",
            f"- Files refreshed this run: {file_list}",
            inner,
            count=1,
        )
    else:
        inner = inner.rstrip() + f"\n- Files refreshed this run: {file_list}\n"
    path.write_text(managed + MANAGED_START + inner + MANAGED_END + after_managed, encoding="utf-8")
    return True


def scan_stale_human_regions(root: Path, changed: list[str]) -> list[str]:
    proposals: list[str] = []
    seen: set[str] = set()
    for mem in (root / ".agentic").rglob("*.md"):
        text = mem.read_text(encoding="utf-8")
        human_region = extract_human_notes_region(text)
        if human_region is None:
            continue
        mem_rel = str(mem.relative_to(root))
        for rel in changed:
            if not path_mentioned_in_region(human_region, rel):
                continue
            key = f"{mem_rel}:{rel}"
            if key in seen:
                continue
            seen.add(key)
            proposals.append(
                f"{mem_rel}: human region mentions changed file `{rel}` — review for staleness"
            )
    return proposals


def main() -> int:
    root = repo_root()
    config = load_config(root)

    graph_ok, graph_msg = run_graph_sync(root)
    if graph_ok:
        print(f"graph_sync: {graph_msg}")
    else:
        print(f"note: {graph_msg}")

    ref_path = root / UPDATE_REF
    prev_ref = ref_path.read_text(encoding="utf-8").strip() if ref_path.is_file() else None
    head = git_head(root)
    change_set = git_changed_files(root, prev_ref) if prev_ref else GitChangeSet([])
    changed = change_set.paths
    change_detection = "commit-range" if prev_ref else "baseline"
    product_changed = product_changed_files(changed, config)
    affected_files = subsystem_files(root, product_changed)
    risks = risk_tags(config, changed)
    changed_tests = [path for path in changed if is_test_path(path, config)]
    refreshed_at = git_commit_time(root, head)

    refreshed: list[str] = []
    if change_set.error is None:
        for memory_file in affected_files:
            paths_for_file = [
                path for path in product_changed if memory_file in subsystem_files(root, [path])
            ]
            risks_for_file = risk_tags(config, paths_for_file + changed_tests)
            if refresh_managed_memory_file(
                root,
                memory_file,
                product_paths=paths_for_file,
                test_paths=changed_tests,
                risks=risks_for_file,
                head=head,
                refreshed_at=refreshed_at,
            ):
                refreshed.append(memory_file)
        if refreshed and refresh_memory_index(
            root,
            [*refreshed, ".agentic/MEMORY_INDEX.md"],
            refreshed_at=refreshed_at,
        ):
            refreshed.append(".agentic/MEMORY_INDEX.md")

    proposals = scan_stale_human_regions(root, changed)
    for proposal in proposals:
        print(f"proposal (needs confirmation): {proposal}")

    if head and change_set.error is None:
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        ref_path.write_text(head + "\n", encoding="utf-8")

    print("\nupdate_memory summary")
    print("=====================")
    print(f"graph status: {'ok' if graph_ok else graph_msg}")
    print(f"git HEAD: {head or 'unavailable'}")
    print(f"change detection: {change_detection}")
    print(f"update mode: {'managed refresh' if affected_files else 'memory index refresh'}")
    print(f"changed since last run: {len(changed)} file(s)")
    if changed:
        for c in changed[:20]:
            print(f"  - {c}")
        if len(changed) > 20:
            print(f"  ... and {len(changed) - 20} more")
    print(f"product files mapped: {len(product_changed)} file(s)")
    print(f"affected memory files: {', '.join(affected_files) if affected_files else 'none'}")
    print(f"risk tags: {', '.join(risks) if risks else 'none'}")
    print(f"files refreshed: {', '.join(refreshed) if refreshed else 'none'}")
    print(f"human-region proposals awaiting confirmation: {len(proposals)}")
    if proposals:
        print("proposal note: consume these before rerunning; commit-range proposals are one-shot")
    print("proposed lesson entries: none (no durable evidence without user confirmation)")
    unknowns: list[str] = []
    if change_set.error:
        unknowns.append(change_set.error)
    if not head:
        unknowns.append("git unavailable")
    if not prev_ref:
        unknowns.append("baseline established; no commit range scanned")
    if not graph_ok:
        unknowns.append(f"graph_sync: {graph_msg}")
    print(f"unknowns: {', '.join(unknowns) if unknowns else 'none'}")
    return 1 if change_set.error else 0


if __name__ == "__main__":
    raise SystemExit(main())
