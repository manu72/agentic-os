---
name: agenticOS-bootstrap
description: Top-level orchestrator for installing, repairing, refreshing, migrating, or upgrading t8 Agentic OS in a repository. Detects current state, classifies the mode (init, refresh, repair, migration, upgrade), then delegates to the focused setup skills agenticOS-graph, agenticOS-memory, and agenticOS-tooling. Confirms the runtime skills agenticOS-context and agenticOS-update are ready. Use when setting up Agentic OS in a new repo, migrating from the older CODEMAP-first design, repairing a broken install, upgrading to the v2 graph-first architecture, or checking whether a repo has all required Agentic OS pieces. Do not use before ordinary coding tasks - that is agenticOS-context's job.
---

# agenticOS-bootstrap

Personal/global orchestration skill for t8 Agentic OS. One job: detect state, classify mode, delegate to focused setup skills, confirm readiness, summarise.

This skill does **not** generate graph logic, memory templates, or Python tooling itself. Those belong to `agenticOS-graph`, `agenticOS-memory`, and `agenticOS-tooling`.

## When to use

- Setting up Agentic OS in a new repository.
- Repairing a broken or partial Agentic OS install.
- Refreshing an existing Agentic OS install after time has passed.
- Migrating from the legacy CODEMAP-first design to the v2 graph-first architecture.
- Upgrading skills/tooling to a newer Agentic OS version.
- Auditing whether a repo has all required Agentic OS pieces.

## When NOT to use

- Before normal coding tasks. Use `agenticOS-context` instead.
- After durable architectural changes, incidents, or lessons. Use `agenticOS-update` instead.
- To regenerate the knowledge graph only. Use `agenticOS-graph` directly.
- To rewrite memory only. Use `agenticOS-memory` directly.
- To rebuild Python tooling only. Use `agenticOS-tooling` directly.

## Operating principle

One skill, one job. This skill orchestrates and reports status. It must not duplicate work owned by the focused skills. If a step needs to write graph code, memory files, or Python tooling, **stop and delegate**.

Architectural rules this skill enforces:

- All six Agentic OS skills are personal/global skills. Do not copy them into the repo unless the user explicitly requests pinned local skill versions.
- The repo contains Agentic OS memory (`.agentic/`), config (`.agentic/CONFIG/agentic.json`), and helper tooling (`scripts/agentic/`) — not the canonical skills.
- Understand Anything is a tool used by Agentic OS, not the owner of architecture.
- Agentic OS memory is primarily for agents; humans review and govern.
- Never silently overwrite operational memory. Managed sections may be refreshed by tooling; human sections require confirmation before edit.
- Fallback to a lightweight CODEMAP is allowed only when graph mode is unavailable. Do not recreate a giant CODEMAP as the primary architecture.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Bootstrap progress:
- [ ] Step 1: Confirm repository root
- [ ] Step 2: Detect current Agentic OS state
- [ ] Step 3: Classify mode (init | refresh | repair | migration | upgrade)
- [ ] Step 4: Confirm plan with user (modes other than refresh)
- [ ] Step 5: Delegate to /agenticOS-graph
- [ ] Step 6: Delegate to /agenticOS-memory
- [ ] Step 7: Delegate to /agenticOS-tooling
- [ ] Step 8: Confirm runtime skills are present
- [ ] Step 9: Run validate_memory.py if available
- [ ] Step 10: Print final summary
```

### Step 1 — Confirm repository root

Verify the working directory is the repo root: presence of `.git/`, or a top-level manifest (`package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.). If ambiguous, ask the user to confirm before proceeding. Do not assume.

### Step 2 — Detect current Agentic OS state

Inspect (one level deep only; do not read large files):

- `.agentic/` (does it exist?)
- `.agentic/CONFIG/agentic.json` (parse `version` field if present)
- `.agentic/GRAPH/knowledge-graph.json` (or any path declared in `agentic.json` under `graph.path`)
- `.agentic/CODEMAP.json` (legacy v1 artifact)
- `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/GRAPH_INDEX.md`
- `.agentic/SUBSYSTEMS/`, `.agentic/LESSONS/`
- `scripts/agentic/` and the four expected scripts (`graph_sync.py`, `route_task.py`, `validate_memory.py`, `update_memory.py`)
- `.understand-anything/` (existing Understand Anything output, if present)
- Personal/global Agentic OS skills if discoverable (`~/.cursor/skills/agenticOS-*`)

Record into working notes:

- which expected files exist;
- which are missing;
- whether `agentic.json.version` is `1` (legacy) or `2` (v2);
- whether the primary graph artifact exists and parses;
- whether legacy `CODEMAP.json` is the only structural artifact.

Do not read or modify any files yet.

### Step 3 — Classify mode

Apply these rules **in order**. The first match wins.

| Mode | Trigger | Meaning |
|------|---------|---------|
| `init` | No `.agentic/` directory exists. | Fresh install. All three setup skills must run from scratch. |
| `repair` | `.agentic/` exists, but `CONFIG/agentic.json` is missing/invalid, **or** required scripts in `scripts/agentic/` are missing, **or** expected memory files referenced by config do not exist. | Broken install. Run the setup skills targeted at the missing pieces only. |
| `migration` | `.agentic/CODEMAP.json` exists and `.agentic/GRAPH/` (or the configured graph path) does not, **or** `agentic.json.version` is `1` (or unset) with no graph configuration. | Legacy CODEMAP-first install. Move to graph-first while preserving human-authored memory. |
| `upgrade` | `agentic.json.version` is present but lower than the current target (`2`), **or** the install predates the current managed/human region markers. | Existing Agentic OS that needs to adopt new architecture without losing content. |
| `refresh` | Everything above passes. `.agentic/`, `CONFIG/agentic.json` v2, graph artifact, and all expected scripts are present and parseable. | Routine refresh. Re-run setup skills in idempotent mode. |

Edge case: if multiple modes could apply (e.g. both `repair` and `migration`), use the **earlier** mode in the table. Surface the secondary mode as a note in the final summary so the user knows what else was addressed.

### Step 4 — Confirm plan with user

For any mode other than `refresh`, briefly state the classified mode and the planned delegation order, and ask the user to confirm before invoking the setup skills. For `refresh`, proceed directly.

If the user wants to scope down (e.g. graph only), stop and direct them to the relevant focused skill instead.

### Step 5 — Delegate to `/agenticOS-graph`

Hand off responsibility for the structural intelligence layer. Do not perform graph work here.

Pass-through context:

- mode (`init` / `refresh` / `repair` / `migration` / `upgrade`);
- host platform — best-effort one of `cursor`, `claude-code`, `codex`, `vscode-copilot`, `copilot-cli`, `other`, or `unknown`. Infer from the runtime where possible (e.g. presence of `.cursor/` config, `CLAUDE.md`, Codex/Copilot CLI signals); if uncertain, pass `unknown` and let `agenticOS-graph` ask. Do not guess silently.
- whether `.understand-anything/` exists and whether it contains a parseable `knowledge-graph.json`;
- whether a graph path is already configured in `agentic.json`;
- whether legacy `CODEMAP.json` is present and should be retained as fallback.

On return, capture: graph provider, graph path, parseable yes/no, coverage notes, known gaps, fallback active yes/no.

### Step 6 — Delegate to `/agenticOS-memory`

Hand off responsibility for the operational memory layer. Do not write memory files here.

Pass-through context:

- mode;
- presence of existing memory files;
- presence of external instruction sources (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursor/skills/*`, `.github/copilot-instructions.md`);
- migration constraint: preserve human sections by default and surface conflicts rather than silently rewriting them.

On return, capture: which memory files were created or refreshed, which human sections were flagged for review, which conflicts were surfaced.

### Step 7 — Delegate to `/agenticOS-tooling`

Hand off responsibility for `.agentic/CONFIG/agentic.json`, `scripts/agentic/*`, and verifying the six personal/global skills exist.

Pass-through context:

- mode;
- whether a canonical t8-agentic-os install source is preferred over local generation;
- legacy scripts present (e.g. v1 `build_codemap.py`) that may need to be retired or marked deprecated.

On return, capture: which scripts were created/updated, config version after the run, whether the six personal skills are all discoverable.

### Step 8 — Confirm runtime skills are present

Verify the user has the two runtime skills available in their personal/global skills location:

- `agenticOS-context`
- `agenticOS-update`

Do not generate or copy them in this skill. If either is missing, note it in the summary as a blocker for normal use and tell the user to install/restore them. Repo-local copies are only acceptable if the user has explicitly requested pinned local skill versions.

### Step 9 — Run validation

If `scripts/agentic/validate_memory.py` exists after step 7, run:

```bash
python scripts/agentic/validate_memory.py
```

Record exit code, structural failures, and warnings. Do not attempt to auto-fix validation failures here; route them back to the relevant focused skill in the summary.

If the script does not exist (because tooling delegation was scoped down or failed), note this as a missing piece.

### Step 10 — Print final summary

Use the format in the next section.

## Delegation rules

- Always invoke setup skills in the order: `agenticOS-graph` → `agenticOS-memory` → `agenticOS-tooling`. Graph first because routing depends on structural evidence; memory second because it overlays graph; tooling last because it depends on both.
- Each setup skill owns its own files. This skill never edits `.agentic/GRAPH/`, `.agentic/SUBSYSTEMS/`, `.agentic/LESSONS/`, `.agentic/CONFIG/`, or `scripts/agentic/` directly.
- If a focused skill reports failure or low confidence, do not paper over it. Surface it in the summary and recommend the targeted re-run.
- Do not re-invoke a setup skill in the same bootstrap run unless the user requests it after reviewing the summary.
- Never run remote installers without explicit user approval. Delegate that decision to `agenticOS-graph` or `agenticOS-tooling` if it arises.

## Stop conditions

Stop and ask the user before proceeding when:

- The current directory is not clearly the repo root.
- The classified mode is `migration` or `upgrade` and the user has uncommitted changes inside `.agentic/` or `scripts/agentic/`.
- A required focused skill (`agenticOS-graph`, `agenticOS-memory`, `agenticOS-tooling`) is not discoverable.
- A focused skill exits with errors, partial completion, or conflicts that need human judgement.
- `validate_memory.py` reports structural failures (non-zero exit).
- Two modes could plausibly apply and the table tiebreaker feels wrong for the situation.
- The user has explicit, custom routing rules or memory the agent does not understand.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Final summary format

Print exactly these sections, in order. Keep it under one screen.

```
Agentic OS bootstrap summary
============================

Mode: <init | refresh | repair | migration | upgrade>
Secondary modes addressed: <list, or "none">

Graph status (from agenticOS-graph):
- Provider: <Understand Anything | fallback CODEMAP | none>
- Path: <configured graph path>
- Parseable: <yes | no>
- Coverage notes: <one line>
- Known gaps: <one line, or "none">

Memory status (from agenticOS-memory):
- Files created or refreshed: <count and brief list>
- Human sections preserved: <count>
- Human sections flagged for review: <count, with file names>
- External instruction sources ingested: <list>
- Conflicts surfaced: <count, or "none">

Tooling status (from agenticOS-tooling):
- Config version: <1 | 2 | missing>
- Scripts present: <graph_sync.py, route_task.py, validate_memory.py, update_memory.py>
- Personal skills present: <agenticOS-bootstrap, -graph, -memory, -tooling, -context, -update>
- Mode: <local-generated | canonical-install>

Validation:
- validate_memory.py: <pass | warnings | failed | not run>
- Warnings: <list, or "none">

Missing pieces:
- <bullet list, or "none">

Unknowns:
- <bullet list of things bootstrap could not determine, or "none">

Conflicts requiring human review:
- <bullet list with file paths, or "none">

Next recommended action:
- <single sentence: which skill to run next, or "Run agenticOS-context before your next coding task.">
```

## Non-goals

- Do not generate graph code or run Understand Anything directly.
- Do not write or rewrite memory templates.
- Do not generate Python tooling or `agentic.json`.
- Do not perform runtime context routing.
- Do not update operational memory after code changes.
- Do not regenerate the six canonical personal/global skills.
- Do not delete files outside scopes owned by the focused skills.
- Do not declare success on partial completion.

## Guardrails

- Evidence over guessing. If state detection is ambiguous, ask.
- Never overwrite human-authored memory without explicit confirmation.
- Never silently downgrade a graph-first install to fallback CODEMAP. Surface the failure and route to `agenticOS-graph`.
- Never expand scope beyond orchestration. If you find yourself writing code, files, or templates here, stop and delegate.
