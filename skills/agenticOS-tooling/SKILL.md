---
name: agenticOS-tooling
description: Installs, generates, repairs, or updates the repo-local t8 Agentic OS tooling and configuration used by the runtime skills. Creates and maintains `.agentic/CONFIG/agentic.json`, `scripts/agentic/README.md`, and the four Python scripts `graph_sync.py`, `route_task.py`, `validate_memory.py`, and `update_memory.py`. Defaults to Understand Anything as the graph provider with `.agentic/GRAPH/knowledge-graph.json` as the path and `codemap` as fallback. Verifies the six canonical Agentic OS personal/global skills exist without generating repo-local copies. Tooling is deterministic, idempotent, graph-aware, and standard-library only by default. Use when initialising tooling in a new Agentic OS install, refreshing tooling after a version bump, repairing missing or broken scripts/config, or when agenticOS-bootstrap delegates tooling work. Do not use to write operational memory, install Understand Anything, or run normal coding-task routing.
---

# agenticOS-tooling

Personal/global setup and maintenance skill for the Agentic OS repo-local tooling and config. One job: produce safe, deterministic scripts and config that the runtime skills (`agenticOS-context`, `agenticOS-update`) depend on.

This skill is often invoked by `agenticOS-bootstrap`. It can also be run directly when only tooling needs attention. It does not write operational memory, run the graph provider, or compile context bundles itself.

## When to use

- Initialising repo-local tooling in a new Agentic OS install.
- Refreshing tooling after an Agentic OS version bump.
- Repairing missing, broken, or corrupted scripts/config.
- Migrating a legacy v1 install to the v2 tooling contract.
- Activating fallback `codemap` mode when the graph provider is unavailable.

## When NOT to use

- To install or refresh the structural graph. Use `agenticOS-graph`.
- To create or refresh operational memory files. Use `agenticOS-memory`.
- To compile a context bundle for a coding task. Use `agenticOS-context`.
- To append durable lessons after a code change. Use `agenticOS-update`.
- To generate repo-local copies of the six canonical personal/global skills (unless explicitly requested).

## Operating principle

> Skills orchestrate. Tools execute. Models curate.

Repo-local tooling must be:

- **Deterministic** — same inputs produce the same outputs.
- **Idempotent** — safe to re-run; never corrupts state on repeat execution.
- **Safe** — no remote installers, no writes outside `.agentic/` and `scripts/agentic/`, no silent overwrites of human content.
- **Graph-aware** — graph is the primary structural source; CODEMAP is fallback only.
- **Minimal** — standard-library Python only unless the user explicitly approves dependencies. MVP-functional, not over-engineered.
- **Designed to reduce guessing** — clear errors, explicit unknowns, refusal to fabricate.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Tooling skill progress:
- [ ] Step 1: Confirm repo root
- [ ] Step 2: Confirm .agentic/ exists (else stop)
- [ ] Step 3: Detect existing tooling/config state
- [ ] Step 4: Classify mode (init | refresh | repair | upgrade | fallback-only)
- [ ] Step 5: Create or update .agentic/CONFIG/agentic.json
- [ ] Step 6: Create or update scripts/agentic/README.md
- [ ] Step 7: Create or update scripts/agentic/graph_sync.py
- [ ] Step 8: Create or update scripts/agentic/route_task.py
- [ ] Step 9: Create or update scripts/agentic/validate_memory.py
- [ ] Step 10: Create or update scripts/agentic/update_memory.py
- [ ] Step 11: Verify the six canonical personal/global skills are discoverable
- [ ] Step 12: Run validate_memory.py
- [ ] Step 13: Print summary
```

### Step 1 — Confirm repo root

Verify `.git/` or a top-level manifest is present. If ambiguous, ask before proceeding.

### Step 2 — Confirm `.agentic/` exists

If `.agentic/` does not exist, stop and tell the user to run `agenticOS-bootstrap`. This skill assumes the memory layer is already in place (or will be created by `agenticOS-memory`).

### Step 3 — Detect existing state

Inspect (read shallowly):

- `.agentic/CONFIG/agentic.json` — parse `version`, `graph` block, `paths`, `generated_artifacts`.
- `scripts/agentic/README.md` and the four Python scripts — note presence, mtime, and whether they look v1 (legacy `build_codemap.py`) or v2.
- `.agentic/GRAPH_INDEX.md` — read graph status (provider, path, fallback, parseable).
- `.agentic/GRAPH/knowledge-graph.json` — note presence and parseability at the first byte.
- `.agentic/CODEMAP.json` — note presence (legacy or fallback artifact).

### Step 4 — Classify mode

Apply in order. First match wins.

| Mode | Trigger |
|------|---------|
| `init` | `agentic.json` is absent or unparseable. |
| `repair` | `agentic.json` exists but required scripts are missing, or `agentic.json` schema is invalid. |
| `upgrade` | `agentic.json.version` is `1` (or unset) and other files exist; legacy `build_codemap.py` present. |
| `fallback-only` | Graph provider unavailable per `GRAPH_INDEX.md`; tooling must operate against `CODEMAP.json`. |
| `refresh` | All scripts present, `agentic.json` v2, graph status clear. |

`fallback-only` may combine with any other mode. Record it as a secondary mode.

### Step 5 — Create or update `agentic.json`

Schema (keep only these top-level keys; preserve unknown user-added keys verbatim):

```json
{
  "version": 2,
  "graph": {
    "provider": "understand-anything",
    "path": ".agentic/GRAPH/knowledge-graph.json",
    "required": true,
    "fallback": "codemap"
  },
  "paths": {
    "memory_root": ".agentic",
    "scripts_root": "scripts/agentic",
    "context_cache": ".agentic/CONTEXT/last_context.json"
  },
  "ignore_globs": [
    "**/node_modules/**", "**/.venv/**", "**/venv/**", "**/dist/**",
    "**/build/**", "**/.next/**", "**/.turbo/**", "**/.cache/**",
    "**/.git/**", "**/__pycache__/**", "**/*.lock", "**/coverage/**",
    "**/.pnpm-store/**", "**/.pnpm/**", "**/vendor/**",
    "**/.parcel-cache/**", "**/.vite/**", "**/.pytest_cache/**",
    "**/.mypy_cache/**", "**/.ruff_cache/**", "**/.DS_Store"
  ],
  "test_discovery": [
    "**/tests/**", "**/__tests__/**", "**/*.test.*",
    "**/*_test.*", "**/test_*.py"
  ],
  "high_risk_patterns": [
    { "match": "**/auth/**", "tags": ["security", "authn"] },
    { "match": "**/billing/**", "tags": ["money", "compliance"] },
    { "match": "**/payments/**", "tags": ["money", "compliance"] },
    { "match": "**/migrations/**", "tags": ["data-integrity"] },
    { "match": "**/alembic/**", "tags": ["data-integrity"] },
    { "match": "**/secrets/**", "tags": ["secrets"] },
    { "match": "**/infra/**", "tags": ["infra"] }
  ],
  "freshness_rules": {
    "graph_max_age_hours": 168,
    "memory_max_age_days": 30
  },
  "validation": {
    "require_region_markers": true,
    "sample_path_check_count": 5
  },
  "generated_artifacts": [
    ".agentic/CONTEXT/last_context.json"
  ]
}
```

Rules:

- On `init`, write the full default config.
- On `refresh` / `repair` / `upgrade`, merge: update `version` and any missing required keys; preserve user-tuned values for `ignore_globs`, `high_risk_patterns`, `freshness_rules`, and unknown keys. Do not delete user-added keys.
- On `fallback-only`, set `graph.required: false` and add `.agentic/CODEMAP.json` to `generated_artifacts`. Record fallback in `GRAPH_INDEX.md` via `agenticOS-graph` if not already recorded.
- Never overwrite `graph.path` if the user has configured a custom path; preserve it.

### Step 6 — `scripts/agentic/README.md`

Short operator-facing reference. Required content:

- One-line description of each script and what it writes.
- Required runtime: Python 3.10+, standard library only.
- CWD requirement: repo root.
- Brief note that scripts must not be edited by hand if regeneration is expected; if hand-edited, the user owns drift.

### Step 7 — `graph_sync.py`

Generate an MVP-functional script meeting all of:

**Inputs:** `.agentic/CONFIG/agentic.json`.

**Behaviour:**
- Read configured graph path from `graph.path`.
- Verify the file exists, parses as JSON, is non-empty, and at least one referenced repo path resolves on disk (sample size from `validation.sample_path_check_count`).
- Compute lightweight metadata only: node count (if discernible), sample edge count, last-modified mtime.
- Update only the managed section of `.agentic/GRAPH_INDEX.md` between `<!-- agentic:managed:start -->` and `<!-- agentic:managed:end -->` markers. Preserve the human region byte-for-byte.
- Record graph freshness (compare mtime to `freshness_rules.graph_max_age_hours`); print a warning if stale.
- Never write graph content into `GRAPH_INDEX.md`.
- Exit 0 on success or non-fatal staleness; exit non-zero only on structural failure (missing file, invalid JSON, empty graph).

**Forbidden:** writing outside `.agentic/`, calling the graph provider, modifying human regions.

### Step 8 — `route_task.py`

Generate an MVP-functional router meeting all of:

**Inputs:** task string as `argv[1]`. Optional `--explain` flag to print routing trace.

**Outputs:**
- JSON context bundle to stdout.
- Same bundle cached at `.agentic/CONTEXT/last_context.json`.

**Context bundle schema (cross-skill contract; `agenticOS-context` consumes this):**

```json
{
  "task": "...",
  "confidence": "high|medium|low",
  "graph_available": true,
  "graph_source": ".agentic/GRAPH/knowledge-graph.json",
  "fallback_active": false,
  "selected_paths": [],
  "selection_reasons": {},
  "graph_nodes": [],
  "dependency_paths": [],
  "related_tests": [],
  "subsystem_files": [],
  "memory_files": [],
  "risk_tags": [],
  "unknowns": [],
  "stop_conditions": []
}
```

**Routing priority (apply in order; explicit user evidence always overrides heuristic routing):**

1. Explicit user-named files, paths, functions, symbols, endpoints, or tests.
2. Graph traversal from explicit anchors.
3. Graph search against task terms.
4. Dependency and impact expansion.
5. Related tests (`test_discovery` patterns).
6. Operational memory overlays (`PROJECT_BRIEF.md`, `MEMORY_INDEX.md`, `SUBSYSTEMS/*.md`).
7. Risk overlays (`high_risk_patterns`).
8. Fallback CODEMAP only if `graph_available == false`.
9. Filesystem fallback only when no graph and no CODEMAP can resolve the request.
10. Stop conditions (low confidence, ambiguity, missing evidence).

**Rules:**

- If a user-named file exists on disk, it MUST appear in `selected_paths`, regardless of graph routing outcome.
- Populate `selection_reasons` with a one-line reason per selected path (e.g. `"user-named"`, `"graph anchor"`, `"dependency"`, `"test for X"`).
- Keep `selected_paths` minimal — target ≤ 10 paths; prefer source-of-truth files and tests over peripheral code.
- Confidence rules:
  - `high`: explicit anchors resolved, graph traversal succeeded, tests found.
  - `medium`: heuristic match likely correct but missing tests or partial coverage.
  - `low`: weak match, no anchors, or task spans unrelated subsystems → emit a stop condition requiring user confirmation.
- On fallback-only mode, set `fallback_active: true` and degrade confidence by one level.
- Never modify `.agentic/` files other than the context cache.

### Step 9 — `validate_memory.py`

Generate an MVP-functional validator meeting all of:

**Behaviour:**

- Verify required structure: `.agentic/`, `.agentic/CONFIG/agentic.json`, `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/SUBSYSTEMS/README.md`, `.agentic/LESSONS/decisions.md`, `.agentic/LESSONS/incidents.md`.
- Verify `agentic.json` parses and contains required top-level keys.
- Verify graph path exists OR `graph.required == false` and a fallback artifact is present.
- If `validation.require_region_markers` is true, verify managed/human region markers exist (and are correctly paired) in PROJECT_BRIEF, MEMORY_INDEX, GRAPH_INDEX, and each `SUBSYSTEMS/*.md`.
- Verify the configured `paths.context_cache` directory is creatable (not the file itself).
- Sample-check up to `validation.sample_path_check_count` inline backtick-wrapped paths in memory files; warn on misses.
- Warn on stale graph (`freshness_rules.graph_max_age_hours`) and stale memory (`freshness_rules.memory_max_age_days`).
- Exit non-zero only on structural failures. Stale references and missing optional paths are warnings (exit 0).

**Forbidden:** parsing arbitrary Markdown, modifying any files, deleting anything.

### Step 10 — `update_memory.py`

Generate an MVP-functional updater meeting all of:

**Behaviour:**

- Run `graph_sync.py` first (or skip with a clear note if graph unavailable).
- If `git` is available, compute changed files since the last run (use a marker file like `.agentic/CONTEXT/last_update_ref` to record the last commit hash).
- Map changed files to affected memory files using `subsystem` inference (top-level folder match; `high_risk_patterns`; existing `SUBSYSTEMS/*.md` ownership).
- Refresh managed sections of affected memory files where safe (e.g. update `Memory freshness` block in `MEMORY_INDEX.md`).
- Preserve human regions byte-for-byte.
- For human regions that appear stale (mention removed files, contradict current evidence), print a proposed diff and require user confirmation before applying.
- Propose new `LESSONS/decisions.md` or `LESSONS/incidents.md` entries only when concrete durable evidence exists (e.g. a doc explicitly records a decision); never fabricate.
- Print a review summary listing: graph status, files refreshed, human-region proposals awaiting confirmation, proposed lesson entries, and remaining unknowns.

**Forbidden:** writing lesson entries without user confirmation, overwriting human regions, modifying files outside `.agentic/`.

### Step 11 — Verify canonical skills

Check that the six personal/global skills are discoverable in the user's personal skills location (e.g. `~/.cursor/skills/`):

- `agenticOS-bootstrap`
- `agenticOS-graph`
- `agenticOS-memory`
- `agenticOS-tooling`
- `agenticOS-context`
- `agenticOS-update`

Do not generate repo-local copies. If any are missing, record them as blockers in the summary and recommend the user install/restore them. Generate repo-local pinned copies only when the user explicitly requests them in this run.

### Step 12 — Run validation

Run:

```bash
python scripts/agentic/validate_memory.py
```

Record exit code, structural failures, and warnings. Do not auto-fix; surface in the summary.

### Step 13 — Print summary

Use the format in the next section.

## Safety rules

- Never write outside `.agentic/` and `scripts/agentic/`.
- Never modify operational memory content. The scripts may refresh managed sections only; this skill itself does not author memory.
- Never overwrite human regions or human-customised config values.
- Never use third-party Python packages unless the user explicitly approves.
- Never run remote install scripts or fetch code from the internet.
- Never duplicate the full graph into Markdown or config.
- Never recreate a giant CODEMAP as the primary structural layer.
- Replace generated tooling on `repair` / `upgrade` only after confirming the existing files match the v1 layout or are clearly broken; preserve user-edited scripts unless the user approves replacement.
- Always make scripts idempotent. Re-running them must not corrupt state.

## Stop conditions

Stop and ask the user before proceeding when:

- The current directory is not clearly the repo root.
- `.agentic/` does not exist (recommend `agenticOS-bootstrap`).
- `agentic.json` exists but has user-tuned values that would conflict with required v2 keys.
- Existing scripts appear to have been hand-edited (mtime or content diverges from a known generated template).
- Graph mode is configured as required but neither graph nor fallback is present.
- The user has uncommitted changes in `.agentic/CONFIG/` or `scripts/agentic/`.
- `validate_memory.py` reports structural failures after this run.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Final summary format

Print exactly these sections, in order. Keep it under one screen.

```
agenticOS-tooling summary
=========================

Mode: <init | refresh | repair | upgrade | fallback-only>
Secondary modes addressed: <list, or "none">

Config:
- .agentic/CONFIG/agentic.json: <created | updated | unchanged>
- Version: <1 | 2 | missing>
- Graph provider: <understand-anything | codemap>
- Graph path: <path>
- Fallback: <codemap | none>

Scripts:
- scripts/agentic/README.md: <created | updated | unchanged>
- graph_sync.py: <created | updated | unchanged | hand-edited (skipped)>
- route_task.py: <created | updated | unchanged | hand-edited (skipped)>
- validate_memory.py: <created | updated | unchanged | hand-edited (skipped)>
- update_memory.py: <created | updated | unchanged | hand-edited (skipped)>

Canonical personal skills present:
- agenticOS-bootstrap: <yes | no>
- agenticOS-graph: <yes | no>
- agenticOS-memory: <yes | no>
- agenticOS-tooling: <yes | no>
- agenticOS-context: <yes | no>
- agenticOS-update: <yes | no>

Validation:
- validate_memory.py: <pass | warnings | failed | not run>
- Warnings: <list, or "none">

Blockers:
- <bullet list, or "none">

Unknowns:
- <bullet list, or "none">

Next recommended action:
- <single sentence>
```

## Non-goals

- Do not write or rewrite `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/SUBSYSTEMS/*`, or `.agentic/LESSONS/*`.
- Do not install or refresh the structural graph.
- Do not install Understand Anything or any other provider.
- Do not perform runtime context routing.
- Do not append durable lessons after a code change.
- Do not generate repo-local copies of the six canonical personal/global skills unless explicitly requested.
- Do not introduce third-party Python dependencies without user approval.
- Do not duplicate the graph or recreate a giant CODEMAP as the primary structural layer.
- Do not run remote installers or fetch code from the internet.
