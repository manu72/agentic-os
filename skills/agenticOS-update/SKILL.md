---
name: agenticOS-update
description: Runtime maintenance skill for repos with t8 Agentic OS initialised. Keeps operational memory, graph metadata, and routing support current after durable changes — new subsystems, architectural decisions, deployment shifts, security rules, data model changes, production incidents, regressions, or important design decisions. Reads `.agentic/CONFIG/agentic.json`, checks graph status (graph-first via Understand Anything; CODEMAP fallback only when graph is unavailable), inspects git status and diff for change context, runs `python scripts/agentic/update_memory.py`, refreshes managed memory sections, reviews human sections for staleness and proposes confirmed edits, appends lessons or decisions only when knowledge is durable, then runs `python scripts/agentic/validate_memory.py`. Memory is agent-first, concise, and routing-useful — never bloated. Use after durable changes worth a future agent's attention. Do not use after routine code changes, for initial bootstrap, for graph or tooling repair, or for normal coding-task context routing.
---

# agenticOS-update

Personal/global runtime maintenance skill. Refreshes Agentic OS memory and graph status after a change creates durable knowledge worth preserving for future agents.

This skill is the counterpart to `agenticOS-context`: context is read-only routing before a task; update is the write-side maintenance after a task. It does not bootstrap, repair, or compile context bundles.

## When to use

Use after a change creates durable knowledge, such as:

- new subsystem;
- architecture change;
- deployment change;
- security rule;
- data model change;
- graph/routing failure lesson;
- production incident;
- regression or near-miss;
- important design decision;
- new source-of-truth file;
- major folder restructure.

## When NOT to use

- After routine implementation details.
- After small copy/UI changes.
- Before normal coding tasks (use `agenticOS-context`).
- For initial bootstrap (use `agenticOS-bootstrap`).
- For graph-only repair (use `agenticOS-graph`) — unless the user wants memory updated too.
- For tooling repair (use `agenticOS-tooling`).

## Operating principle

> Only add to Agentic OS memory when a future AI agent would benefit from knowing it.

- Memory is agent-first. Humans review and govern; they are not the audience.
- Memory is an index, not a duplicate of the code or the graph.
- Managed sections are refreshed by tooling. Human sections are preserved by default but reviewed for staleness, inaccuracy, incompleteness, or conflict.
- Never silently overwrite human sections. Propose edits and require confirmation.
- Never bloat. Short bullets, paths, risk tags, do-not-do rules.
- Never proceed when validation has structural failures.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Update skill progress:
- [ ] Step 1: Verify Agentic OS is initialised
- [ ] Step 2: Read agentic.json and check graph status
- [ ] Step 3: Detect legacy repo-local v1 skill (warn only)
- [ ] Step 4: Inspect change context (git status/diff, renamed/added/removed paths)
- [ ] Step 5: Run update_memory.py and review the report
- [ ] Step 6: Refresh managed memory sections where safe
- [ ] Step 7: Review human sections; propose edits with confirmation
- [ ] Step 8: Add or propose lessons/decisions only when durable
- [ ] Step 9: Run validate_memory.py
- [ ] Step 10: Print summary and recommend commit
```

### Step 1 — Verify Agentic OS is initialised

Confirm all of:

- `.agentic/CONFIG/agentic.json`
- `.agentic/MEMORY_INDEX.md`
- `.agentic/GRAPH_INDEX.md`
- `scripts/agentic/update_memory.py`
- `scripts/agentic/validate_memory.py`

If any are missing, stop. Tell the user to run `agenticOS-bootstrap` (or the targeted setup skill). Do not attempt setup yourself.

### Step 2 — Read config and check graph status

Read `.agentic/CONFIG/agentic.json`:

- `graph.provider` (expected: `understand-anything`).
- `graph.path` (preferred: `.agentic/GRAPH/knowledge-graph.json`; may differ).
- `graph.required`, `graph.fallback`.

Cross-check the managed section of `.agentic/GRAPH_INDEX.md`. Classify graph status as `graph-first`, `fallback`, or `broken` (matches `agenticOS-context` semantics).

If status is `broken`, stop. Recommend `agenticOS-graph` or `agenticOS-tooling` and exit without modifying memory.

### Step 3 — Detect legacy repo-local v1 skill (warn only)

If `.cursor/skills/agenticOS-update/SKILL.md` exists in the repo, note it as legacy v1 and warn the user that the personal/global v2 skill takes precedence. Do not edit the legacy file unless the user explicitly asks.

### Step 4 — Inspect change context

Use git to scope the update:

```bash
git status --short
git diff --stat HEAD
git log --name-status -1
```

Capture into working notes:

- changed/added/removed/renamed paths;
- major folders added or removed (potential new or retired subsystems);
- changed source-of-truth files (schemas, OpenAPI specs, IaC, migrations, security config);
- changes to external AI instruction sources (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursor/skills/*`, `.github/copilot-instructions.md`).

If `git` is unavailable or the repo is in a detached or dirty state that prevents reliable diffing, surface that as an unknown rather than guessing.

### Step 5 — Run `update_memory.py` and review

Run:

```bash
python scripts/agentic/update_memory.py
```

The script refreshes managed sections where safe, refreshes graph status via `graph_sync.py`, and prints a review report listing:

- graph status;
- files whose managed sections were refreshed;
- human regions flagged for review;
- proposed lesson/decision entries.

If the script fails, stop. Recommend `agenticOS-tooling` and do not patch memory by hand.

Do not accept the report blindly. Treat each suggestion as a proposal that must pass the durable-memory criteria below.

### Step 6 — Refresh managed sections where safe

Managed sections may be rewritten freely if the refresh is supported by current repo evidence. Spot-check:

- `MEMORY_INDEX.md` — subsystem list, high-risk areas, source-of-truth files, lessons/decisions index, graph status reference, freshness timestamp.
- `GRAPH_INDEX.md` — provider, path, parseable, fallback, last checked, last generated, known gaps.
- `PROJECT_BRIEF.md` managed block — stack, deployment, major subsystems, source-of-truth files, external instruction sources, unknowns, conflicts.
- `SUBSYSTEMS/*.md` managed blocks — purpose, owned paths, public contracts, source-of-truth files, related tests, invariants, do-not-do rules.

Never modify human regions in this step.

### Step 7 — Review human sections; propose edits with confirmation

For each file with a human region:

1. Compare against current managed content and current repo evidence.
2. Flag as `stale`, `inaccurate`, `incomplete`, or `conflicting` where applicable.
3. Propose a specific edit (show the diff).
4. Apply only after the user confirms.
5. If the user declines, leave the human region untouched and record the disagreement in the summary.

Human sections are not untouchable, but they are not auto-editable either.

### Step 8 — Add or propose lessons/decisions only when durable

Apply the durable-memory criteria (next section). Accept proposals that pass; reject the rest. Keep entries one or two lines with links to source-of-truth files or commit hashes where useful.

- `LESSONS/decisions.md` — durable architectural and design decisions only.
- `LESSONS/incidents.md` — durable lessons from failures, outages, regressions, or near-misses only.

If no durable knowledge was created by the change, add nothing.

### Step 9 — Run `validate_memory.py`

Run:

```bash
python scripts/agentic/validate_memory.py
```

- Structural failures (non-zero exit): stop. Surface the failure in the summary. Recommend the targeted setup skill.
- Warnings (stale references, missing optional paths): record and proceed.

### Step 10 — Print summary and recommend commit

Use the format under "Final summary format" below. Recommend committing memory and code changes together so the operational record stays in sync with the codebase.

## Durable-memory criteria

Only add to Agentic OS memory when a future AI agent would benefit from knowing it.

Examples worth remembering:

- “Realtime token endpoint is the security boundary; never expose OpenAI API keys to frontend.”
- “This repo uses Hono, not Express.”
- “Graph routing missed explicit file anchors; route_task.py was fixed to prioritise explicit evidence.”
- “Deployment is Vercel frontend + backend API, no persistent DB in Phase 1.”

Examples not worth remembering:

- “Fixed typo.”
- “Adjusted padding.”
- “Renamed variable.”
- “Updated dependency patch version.”
- “Added one-off test fixture.”

Decision filter: if the entry would not change how a future agent reads, edits, or avoids breaking the system, do not record it.

## Managed and human region rules

Memory files use both regions:

```markdown
<!-- agentic:managed:start -->
Agent/tool maintained content. Refreshed by tooling.
<!-- agentic:managed:end -->

<!-- human:notes:start -->
Human judgement, context, warnings, nuance.
Preserved by default. Reviewed for staleness. Edits require confirmation.
<!-- human:notes:end -->
```

Rules:

- Managed sections may be updated by tooling on every run.
- Human sections are not untouchable. They should be reviewed for stale or incorrect information, but changes require explicit confirmation.
- Never silently overwrite human sections.
- Never delete a human region; if it would be left empty after a review pass, leave a one-line evidence-derived note instead.

## Stop conditions

Stop and ask the user before proceeding when:

- Any required init file from step 1 is missing.
- Graph status is `broken`.
- `update_memory.py` or `validate_memory.py` fails or returns malformed output.
- `git` is unavailable or the repo is in a state that prevents reliable change detection.
- A proposed human-section edit materially changes recorded intent.
- A proposed lesson/decision does not pass the durable-memory criteria.
- Validation reports structural failures.
- The user has staged or unstaged changes in `.agentic/` that this run did not produce.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Final summary format

Print exactly these sections, in order. Keep it under one screen.

```
agenticOS-update summary
========================

Trigger: <one-line description of the durable change>

Graph:
- Status: <graph-first | fallback | broken>
- Provider: <understand-anything | codemap | none>
- Last generated: <ISO-8601 UTC | unknown>

Change context:
- Files changed: <count>
- Major folders added/removed: <list, or "none">
- Source-of-truth files touched: <list, or "none">

Managed sections refreshed:
- <file path>: <one-line note>
- <file path>: <one-line note>

Human sections:
- Preserved unchanged: <count>
- Edits proposed: <count, with file paths>
- Edits applied after confirmation: <count, with file paths>
- Edits declined by user: <count, with file paths>

Lessons / decisions:
- Added: <count, with one-line summaries>
- Skipped as non-durable: <count, with reasons>

Validation:
- validate_memory.py: <pass | warnings | failed>
- Warnings: <list, or "none">

Unknowns / conflicts:
- <bullet list, or "none">

Commit recommendation:
- <single sentence: e.g. "Commit .agentic/ updates with the code change", or "Do not commit; resolve validation failures first">
```

## Non-goals

- Do not bootstrap or repair Agentic OS.
- Do not install or refresh Understand Anything.
- Do not regenerate `.agentic/CONFIG/agentic.json` or `scripts/agentic/*`.
- Do not perform runtime context routing.
- Do not create broad documentation bloat.
- Do not duplicate the graph or any code into memory.
- Do not recreate CODEMAP as the primary structural layer.
- Do not silently overwrite human sections.
- Do not add routine implementation chatter to `LESSONS/`.
- Do not treat stale memory as acceptable.
- Do not proceed when validation has structural failures.
- Do not edit the legacy `.cursor/skills/agenticOS-update/SKILL.md` unless explicitly asked.
