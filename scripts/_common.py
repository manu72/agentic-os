"""Shared helpers for agentic OS scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_GRAPH_PATH = ".agentic/GRAPH/knowledge-graph.json"
DEFAULT_SAMPLE_COUNT = 5
MAX_SAMPLE_COUNT = 100
GRAPH_SYNC_TIMEOUT_SEC = 120

HUMAN_NOTES_START = "<!-- human:notes:start -->"
HUMAN_NOTES_END = "<!-- human:notes:end -->"


def config_section(config: dict, key: str) -> dict:
    section = config.get(key, {})
    return section if isinstance(section, dict) else {}


def load_config(root: Path, *, label: str = "error") -> dict:
    config_path = root / ".agentic/CONFIG/agentic.json"
    if not config_path.is_file():
        print(f"{label}: missing {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with config_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"{label}: agentic.json invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"{label}: agentic.json must be a JSON object", file=sys.stderr)
        sys.exit(1)
    return data


def graph_path_from_config(root: Path, config: dict) -> Path:
    graph_cfg = config_section(config, "graph")
    rel = graph_cfg.get("path", DEFAULT_GRAPH_PATH)
    if not isinstance(rel, str) or not rel.strip():
        rel = DEFAULT_GRAPH_PATH
    return root / rel


def graph_rel_path_str(root: Path, config: dict, graph_path: Path) -> str:
    graph_cfg = config_section(config, "graph")
    configured = graph_cfg.get("path")
    if isinstance(configured, str) and configured.strip():
        return configured
    try:
        return str(graph_path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(graph_path)


def parse_sample_count(
    raw: object,
    *,
    default: int = DEFAULT_SAMPLE_COUNT,
    strict: bool = False,
    warn_fn=None,
) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        msg = f"invalid sample_path_check_count {raw!r}; using default {default}"
        if strict:
            print(f"error: {msg}", file=sys.stderr)
            sys.exit(1)
        if warn_fn:
            warn_fn(msg)
        return default
    if value <= 0:
        msg = f"sample_path_check_count must be positive, got {value}; using default {default}"
        if strict:
            print(f"error: {msg}", file=sys.stderr)
            sys.exit(1)
        if warn_fn:
            warn_fn(msg)
        return default
    if value > MAX_SAMPLE_COUNT:
        if warn_fn:
            warn_fn(f"sample_path_check_count {value} exceeds max {MAX_SAMPLE_COUNT}; capping")
        return MAX_SAMPLE_COUNT
    return value


def resolve_repo_file(root: Path, candidate: str) -> Path | None:
    root_resolved = root.resolve()
    try:
        resolved = (root / candidate).resolve()
    except OSError:
        return None
    try:
        if not resolved.is_relative_to(root_resolved):
            return None
    except ValueError:
        return None
    if not resolved.is_file():
        return None
    return resolved


def extract_human_notes_region(text: str) -> str | None:
    if HUMAN_NOTES_START not in text or HUMAN_NOTES_END not in text:
        return None
    start_idx = text.index(HUMAN_NOTES_START) + len(HUMAN_NOTES_START)
    end_idx = text.index(HUMAN_NOTES_END)
    if start_idx > end_idx:
        return None
    return text[start_idx:end_idx]


def path_mentioned_in_region(region: str, rel: str) -> bool:
    if f"`{rel}`" in region:
        return True
    for line in region.splitlines():
        idx = line.find(rel)
        while idx >= 0:
            before = line[idx - 1] if idx > 0 else " "
            after_idx = idx + len(rel)
            after = line[after_idx] if after_idx < len(line) else " "
            if before in " `'\"([" and after in " `'\").,;:]":
                return True
            idx = line.find(rel, idx + 1)
    return False
