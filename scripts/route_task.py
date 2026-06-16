#!/usr/bin/env python3
"""Route a task string to a context bundle for agenticOS-context."""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    graph_path_from_config,
    graph_rel_path_str,
    load_config,
    resolve_repo_file,
)

MAX_PATHS = 10
MAX_DEPENDENCY_PATHS = 5
MAX_TEST_PATHS = 5
CODE_EXTENSIONS = (
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".md",
    ".mjs",
    ".cjs",
    ".css",
    ".glsl",
    ".svelte",
)
RISK_STOP_TAGS = {"security", "money", "data-integrity", "secrets", "infra"}
STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "in", "on", "at", "of", "with",
    "fix", "add", "update", "change", "implement", "refactor", "debug", "test",
    "how", "what", "when", "where", "why", "is", "are", "be", "do", "does",
}

PATH_CANDIDATE = re.compile(
    r"(?:`)?((?:[\w@.+-]+/)+[\w@.+/-]+\.(?:json|tsx?|jsx?|py|md|mjs|cjs|css|glsl|svelte))(?:`)?",
    re.IGNORECASE,
)
SYMBOL_CANDIDATE = re.compile(r"\b([A-Z][A-Za-z0-9_]+)\b")
BACKTICK_PATH = re.compile(r"`([^`\n]+)`")


def repo_root() -> Path:
    root = Path.cwd()
    if not (root / ".agentic").is_dir():
        print(json.dumps({"error": "run from repository root"}), file=sys.stderr)
        sys.exit(1)
    return root


def load_graph(root: Path, config: dict) -> tuple[dict | None, bool, str, bool, str, list[str]]:
    graph_path = graph_path_from_config(root, config)
    rel = graph_rel_path_str(root, config, graph_path)
    errors: list[str] = []
    if graph_path.is_file():
        try:
            with graph_path.open(encoding="utf-8") as fh:
                return json.load(fh), True, rel, False, "graph-first", []
        except json.JSONDecodeError as exc:
            errors.append(f"graph JSON is invalid: {rel} ({exc.msg})")
    else:
        errors.append(f"graph file missing: {rel}")

    graph_config = config.get("graph", {})
    graph_required = not isinstance(graph_config, dict) or graph_config.get("required", True)
    if graph_required:
        return None, False, rel, False, "broken", errors

    codemap = root / ".agentic/CODEMAP.json"
    if codemap.is_file():
        try:
            with codemap.open(encoding="utf-8") as fh:
                return json.load(fh), False, ".agentic/CODEMAP.json", True, "fallback", errors
        except json.JSONDecodeError as exc:
            errors.append(f"CODEMAP JSON is invalid: .agentic/CODEMAP.json ({exc.msg})")
    else:
        errors.append("CODEMAP fallback missing: .agentic/CODEMAP.json")
    return None, False, rel, False, "broken", errors


def candidate_path_strings(task: str) -> list[str]:
    candidates: list[str] = []
    for match in PATH_CANDIDATE.finditer(task):
        candidate = match.group(1)
        if candidate not in candidates:
            candidates.append(candidate)
    for match in BACKTICK_PATH.finditer(task):
        raw = match.group(1).strip()
        if ("/" in raw or "." in raw) and raw not in candidates:
            candidates.append(raw)
    return candidates


def extract_explicit_paths(task: str, root: Path) -> list[str]:
    found: list[str] = []
    root_resolved = root.resolve()
    for candidate in candidate_path_strings(task):
        resolved = resolve_repo_file(root, candidate)
        if resolved is None:
            continue
        rel = str(resolved.relative_to(root_resolved))
        if rel not in found:
            found.append(rel)
    return found


def task_terms(task: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_/-]*", task.lower())
    terms: list[str] = []
    for tok in tokens:
        if tok in STOPWORDS or len(tok) < 3:
            continue
        if tok not in terms:
            terms.append(tok)
        for part in tok.replace("-", "/").split("/"):
            if len(part) >= 3 and part not in STOPWORDS and part not in terms:
                terms.append(part)
    return terms


def task_symbols(task: str) -> list[str]:
    """Extract likely code symbols without treating short acronyms as anchors."""
    symbols: list[str] = []
    for match in SYMBOL_CANDIDATE.findall(task):
        if len(match) <= 2 and match.isupper():
            continue
        if match not in symbols:
            symbols.append(match)
    return symbols


def index_graph(graph: dict) -> tuple[dict[str, dict], dict[str, list[str]], dict[str, str]]:
    by_id: dict[str, dict] = {}
    file_by_path: dict[str, str] = {}
    adjacency: dict[str, list[str]] = {}
    for node in graph.get("nodes", []):
        nid = node.get("id")
        if isinstance(nid, str):
            by_id[nid] = node
            if node.get("type") == "file":
                fp = node.get("filePath")
                if isinstance(fp, str):
                    file_by_path[fp] = nid
    for edge in graph.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        etype = edge.get("type", "")
        if not isinstance(src, str) or not isinstance(tgt, str):
            continue
        if etype in {"imports", "depends_on", "uses", "calls", "references"}:
            adjacency.setdefault(src, []).append(tgt)
            adjacency.setdefault(tgt, []).append(src)
    return by_id, adjacency, file_by_path


def node_to_path(node: dict) -> str | None:
    fp = node.get("filePath")
    if isinstance(fp, str):
        return fp
    return None


def graph_search(graph: dict, terms: list[str], limit: int) -> list[tuple[str, str, float]]:
    scores: dict[str, float] = {}
    reasons: dict[str, str] = {}
    for node in graph.get("nodes", []):
        fp = node_to_path(node)
        if not fp:
            continue
        hay = " ".join(
            str(node.get(k, "")) for k in ("name", "filePath", "summary", "id")
        ).lower()
        tags = node.get("tags") or []
        if isinstance(tags, list):
            hay += " " + " ".join(str(t) for t in tags).lower()
        score = 0.0
        for term in terms:
            if term in hay:
                score += 2.0 if node.get("type") == "file" else 1.0
            if term in fp.lower():
                score += 3.0
        if score > 0:
            prev = scores.get(fp, 0.0)
            if score > prev:
                scores[fp] = score
                reasons[fp] = "graph search"
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [(p, reasons[p], s) for p, s in ranked[:limit]]


def expand_dependencies(
    seeds: list[str],
    by_id: dict[str, dict],
    adjacency: dict[str, list[str]],
    file_by_path: dict[str, str],
    limit: int,
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    seen: set[str] = set(seeds)
    queue: list[str] = []
    for seed in seeds:
        nid = file_by_path.get(seed)
        if nid:
            queue.append(nid)
    while queue and len(results) < limit:
        nid = queue.pop(0)
        for neighbor in adjacency.get(nid, []):
            node = by_id.get(neighbor)
            if not node:
                continue
            fp = node_to_path(node)
            if not fp or fp in seen:
                continue
            seen.add(fp)
            results.append((fp, "dependency"))
            if len(results) >= limit:
                break
            if neighbor in adjacency:
                queue.append(neighbor)
    return results


def is_test_path(path: str, config: dict) -> bool:
    """True when path matches configured test_discovery globs."""
    patterns = config.get("test_discovery", [])
    return any(isinstance(pat, str) and glob_match(pat, path) for pat in patterns)


def discover_tests(root: Path, config: dict, paths: list[str]) -> list[str]:
    patterns = config.get("test_discovery", [])
    tests: list[str] = []
    for path in paths:
        stem = Path(path).stem
        parent = Path(path).parent.name
        candidates: list[Path] = []
        for base in (root / "__tests__", root / "tests"):
            if base.is_dir():
                for item in base.rglob("*"):
                    if not item.is_file():
                        continue
                    if "__pycache__" in item.parts or item.suffix.lower() not in CODE_EXTENSIONS:
                        continue
                    rel = str(item.relative_to(root))
                    name_lower = item.name.lower()
                    if stem.lower() in name_lower or parent.lower() in name_lower:
                        candidates.append(item)
        for cand in candidates:
            rel = str(cand.relative_to(root))
            matched = any(glob_match(pat, rel) for pat in patterns)
            if matched and rel not in tests:
                tests.append(rel)
    return tests[:5]


def owned_paths_from_subsystem(text: str) -> list[str]:
    """Extract owned path prefixes from the ## Owned paths section."""
    lower = text.lower()
    marker = "## owned paths"
    start = lower.find(marker)
    if start < 0:
        return []
    section = text[start + len(marker) :]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    prefixes: list[str] = []
    for match in BACKTICK_PATH.finditer(section):
        raw = match.group(1).strip().replace("\\", "/")
        if raw.endswith("/"):
            prefixes.append(raw)
        elif "/" in raw:
            prefixes.append(raw + "/")
        else:
            prefixes.append(raw)
    return prefixes


def subsystem_matches(stem: str, owned_prefixes: list[str], paths: list[str]) -> bool:
    for path in paths:
        norm = path.replace("\\", "/")
        for prefix in owned_prefixes:
            p = prefix.replace("\\", "/")
            if norm == p.rstrip("/") or norm.startswith(p):
                return True
        if stem in Path(norm).parts:
            return True
    return False


def subsystem_files(root: Path, paths: list[str]) -> list[str]:
    subsystems: list[str] = []
    sub_dir = root / ".agentic/SUBSYSTEMS"
    if not sub_dir.is_dir() or not paths:
        return subsystems
    for fp in sorted(sub_dir.glob("*.md")):
        if fp.name == "README.md":
            continue
        text = fp.read_text(encoding="utf-8")
        stem = fp.stem
        if subsystem_matches(stem, owned_paths_from_subsystem(text), paths):
            rel = str(fp.relative_to(root))
            if rel not in subsystems:
                subsystems.append(rel)
    return subsystems


def memory_files(root: Path) -> list[str]:
    files = [
        ".agentic/PROJECT_BRIEF.md",
        ".agentic/MEMORY_INDEX.md",
    ]
    return [f for f in files if (root / f).is_file()]


def risk_tags(config: dict, paths: list[str]) -> list[str]:
    tags: list[str] = []
    for path in paths:
        for rule in config.get("high_risk_patterns", []):
            if not isinstance(rule, dict):
                continue
            match = rule.get("match", "")
            rule_tags = rule.get("tags", [])
            if isinstance(match, str) and isinstance(rule_tags, list) and glob_match(match, path):
                for tag in rule_tags:
                    if isinstance(tag, str) and tag not in tags:
                        tags.append(tag)
    return tags


def _segment_match(pattern_seg: str, path_seg: str) -> bool:
    if pattern_seg == "*":
        return True
    if any(ch in pattern_seg for ch in "*?["):
        return fnmatch.fnmatchcase(path_seg, pattern_seg)
    return pattern_seg == path_seg


def glob_match(pattern: str, path: str) -> bool:
    """Match path against a glob pattern with recursive ** segments."""
    norm = path.replace("\\", "/")
    parts = pattern.replace("\\", "/").split("/")
    return _glob_parts(parts, norm.split("/"))


def _glob_parts(pattern_parts: list[str], path_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    head, *tail = pattern_parts
    if head == "**":
        if _glob_parts(tail, path_parts):
            return True
        if path_parts:
            return _glob_parts(pattern_parts, path_parts[1:])
        return False
    if not path_parts:
        return False
    if head == "*":
        if not _glob_parts(tail, path_parts[1:]):
            return False
        return True
    if not _segment_match(head, path_parts[0]):
        return False
    return _glob_parts(tail, path_parts[1:])


def ignored_by_config(path: str, config: dict) -> bool:
    default_ignore_parts = {
        "node_modules",
        ".git",
        ".next",
        "dist",
        "build",
        ".venv",
        "coverage",
        "__pycache__",
    }
    norm = path.replace("\\", "/")
    if any(part in default_ignore_parts for part in Path(norm).parts):
        return True
    for pattern in config.get("ignore_globs", []):
        if not isinstance(pattern, str):
            continue
        if glob_match(pattern, norm) or glob_match(pattern, norm + "/"):
            return True
    return False


def filesystem_fallback(root: Path, config: dict, terms: list[str], limit: int) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        kept_dirs: list[str] = []
        for dirname in dirnames:
            rel_dir = str(Path(dirpath, dirname).relative_to(root))
            if not ignored_by_config(rel_dir, config):
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for name in filenames:
            path = Path(dirpath, name)
            rel = str(path.relative_to(root))
            if path.suffix.lower() not in CODE_EXTENSIONS or ignored_by_config(rel, config):
                continue
            lower = name.lower()
            if any(t in lower for t in terms):
                results.append((rel, "filesystem fallback"))
                if len(results) >= limit:
                    return results
    return results


def build_bundle(
    task: str,
    root: Path,
    config: dict,
    graph: dict | None,
    graph_available: bool,
    graph_source: str,
    fallback_active: bool,
    graph_status: str,
    graph_errors: list[str],
    explain: bool,
) -> dict:
    selected: list[str] = []
    reasons: dict[str, str] = {}
    graph_nodes: list[str] = []
    unknowns: list[str] = []
    stop_conditions: list[str] = []
    explicit_graph_matches = 0

    def add_path(path: str, reason: str) -> bool:
        if path not in selected and len(selected) < MAX_PATHS:
            selected.append(path)
            reasons[path] = reason
            return True
        return path in selected

    explicit = extract_explicit_paths(task, root)
    for p in explicit:
        add_path(p, "user-named")

    terms = task_terms(task)
    if graph_status == "broken":
        unknowns.extend(graph_errors)
        stop_conditions.append("required graph unavailable — run agenticOS-graph")
    elif graph and (graph_available or fallback_active):
        search_reason = "graph search" if graph_available else "codemap search"
        anchor_reason = "graph anchor" if graph_available else "codemap anchor"
        by_id, adjacency, file_by_path = index_graph(graph)
        if explicit:
            for p in explicit:
                nid = file_by_path.get(p)
                if nid:
                    explicit_graph_matches += 1
                    graph_nodes.append(nid)
            for p, reason in expand_dependencies(
                explicit, by_id, adjacency, file_by_path, MAX_DEPENDENCY_PATHS
            ):
                add_path(p, reason)
        if not explicit:
            search_limit = max(0, MAX_PATHS - len(selected))
            for p, _reason, _score in graph_search(graph, terms, search_limit):
                add_path(p, search_reason)
                nid = file_by_path.get(p)
                if nid and nid not in graph_nodes:
                    graph_nodes.append(nid)
        for sym in task_symbols(task):
            for node in graph.get("nodes", []):
                if node.get("name") == sym or sym in str(node.get("id", "")):
                    fp = node_to_path(node)
                    if fp:
                        add_path(fp, anchor_reason)
                        nid = node.get("id")
                        if isinstance(nid, str) and nid not in graph_nodes:
                            graph_nodes.append(nid)
    elif not graph_available and not fallback_active:
        unknowns.append("graph unavailable and no CODEMAP fallback")

    if graph_status != "broken" and not selected and terms:
        for p, reason in filesystem_fallback(root, config, terms, MAX_PATHS):
            add_path(p, reason)

    product_paths = [p for p in selected if not is_test_path(p, config)]
    related_tests = discover_tests(root, config, product_paths)[:MAX_TEST_PATHS]
    subsystem_files_list = subsystem_files(root, product_paths)
    memory_files_list = memory_files(root)
    dependency_paths = [p for p, r in reasons.items() if r == "dependency"]
    risk = risk_tags(config, selected + related_tests)

    has_anchors = bool(explicit)
    if graph_status == "broken":
        confidence = "low"
    elif has_anchors and graph_available and explicit_graph_matches:
        confidence = "high"
    elif selected and (graph_available or explicit):
        confidence = "medium"
    else:
        confidence = "low"
        stop_conditions.append("weak routing match — confirm target files with user")

    if fallback_active:
        if confidence == "high":
            confidence = "medium"

    blocking_risks = [tag for tag in risk if tag in RISK_STOP_TAGS]
    if blocking_risks and confidence != "high":
        joined = ", ".join(blocking_risks)
        stop_conditions.append(f"risk tags require high confidence: {joined}")

    bundle = {
        "task": task,
        "confidence": confidence,
        "graph_status": graph_status,
        "graph_available": graph_available,
        "graph_source": graph_source,
        "fallback_active": fallback_active,
        "graph_errors": graph_errors,
        "explicit_paths": explicit,
        "selected_paths": selected,
        "selection_reasons": reasons,
        "graph_nodes": graph_nodes[:15],
        "dependency_paths": dependency_paths,
        "related_tests": related_tests,
        "subsystem_files": subsystem_files_list,
        "memory_files": memory_files_list,
        "risk_tags": risk,
        "unknowns": unknowns,
        "stop_conditions": stop_conditions,
    }

    if explain:
        print("Routing trace:", file=sys.stderr)
        for p in selected:
            print(f"  {p}: {reasons.get(p, '?')}", file=sys.stderr)
        print(f"confidence={confidence}", file=sys.stderr)

    return bundle


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--explain"]
    explain = "--explain" in sys.argv[1:]
    if not args:
        print(json.dumps({"error": "usage: route_task.py <task> [--explain]"}), file=sys.stderr)
        return 1

    task = " ".join(args)
    root = repo_root()
    config = load_config(root)
    graph, graph_available, graph_source, fallback_active, graph_status, graph_errors = load_graph(
        root, config
    )

    bundle = build_bundle(
        task,
        root,
        config,
        graph,
        graph_available,
        graph_source,
        fallback_active,
        graph_status,
        graph_errors,
        explain,
    )

    cache_rel = config.get("paths", {}).get("context_cache", ".agentic/CONTEXT/last_context.json")
    cache_path = root / cache_rel
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(bundle, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
