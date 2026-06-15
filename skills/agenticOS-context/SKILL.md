---
name: agenticOS-context
description: Runtime context-compilation skill for repos that have t8 Agentic OS initialised. Confirms `.agentic/CONFIG/agentic.json`, `.agentic/MEMORY_INDEX.md`, `.agentic/GRAPH_INDEX.md`, and `scripts/agentic/route_task.py` are present, reads graph status from config and `GRAPH_INDEX.md` (graph-first with Understand Anything preferred, CODEMAP as fallback only), runs the routing engine with `python scripts/agentic/route_task.py "<task>"`, parses the returned context bundle, reads only the selected paths, memory files, subsystem files, and related tests, then states confidence, graph status, selection reasons, risks, unknowns, and stop conditions before implementing. Honours explicit user-named files as routing anchors that always override heuristic routing. Use before substantial coding tasks, bug fixes, PR feedback implementation, refactors, architecture changes, or test changes. Do not use for Agentic OS bootstrap/setup, memory updates after durable changes, graph repair, or tooling repair.
---

# agenticOS-context

Personal/global runtime skill. Compiles a focused, evidence-based context bundle before non-trivial coding work in any repo that has Agentic OS initialised.

This skill is the entry point for normal coding tasks. It orchestrates the routing workflow but does not perform graph traversal itself — that is delegated to the repo-local `scripts/agentic/route_task.py`.

## When to use

- Before substantial coding tasks, bug fixes, refactors, architecture changes, or test changes.
- Before implementing PR feedback in a meaningful patch.
- Before answering "how does this work" or "where do I change this" with concrete code edits.

## When NOT to use

- For Agentic OS bootstrap/setup. Use `agenticOS-bootstrap`.
- To update operational memory after durable changes. Use `agenticOS-update`.
- To repair or refresh the structural graph. Use `agenticOS-graph`.
- To repair or regenerate repo-local tooling/config. Use `agenticOS-tooling`.
- For trivial single-line edits where evidence is already in hand.

## Operating principle

> Provide the minimal sufficient evidence required for the highest quality decision.

- Graph-first: Understand Anything is the preferred structural source. CODEMAP is fallback only.
- Routing is deterministic and lives in tooling. This skill orchestrates and interprets the bundle.
- Explicit user evidence always overrides heuristic routing.
- Prefer minimal sufficient evidence over wide repo scans.
- If status, config, or routing output is broken, stop and report — do not silently proceed.
- Agentic OS memory is for agents. Read what the bundle says to read; do not invent additional reads unless a specific gap blocks the task.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Context skill progress:
- [ ] Step 1: Verify Agentic OS is initialised
- [ ] Step 2: Read agentic.json and determine graph status
- [ ] Step 3: Detect legacy repo-local v1 skill (warn only)
- [ ] Step 4: Run route_task.py with the task description
- [ ] Step 5: Parse the context bundle
- [ ] Step 6: Read only the files in the bundle
- [ ] Step 7: Handle explicit user-named files
- [ ] Step 8: State the status block before implementing
- [ ] Step 9: Honour stop conditions
- [ ] Step 10: Proceed (or hand off to other skills)
```

### Step 1 — Verify Agentic OS is initialised

Confirm all of:

- `.agentic/CONFIG/agentic.json`
- `.agentic/MEMORY_INDEX.md`
- `.agentic/GRAPH_INDEX.md`
- `scripts/agentic/route_task.py`

If any are missing, stop. Tell the user to run `agenticOS-bootstrap` (or the targeted setup skill — `agenticOS-graph`, `agenticOS-memory`, or `agenticOS-tooling`). Do not attempt setup yourself.

### Step 2 — Read config and determine graph status

Read `.agentic/CONFIG/agentic.json`. Capture:

- `graph.provider` (default expectation: `understand-anything`).
- `graph.path` (default expectation: `.agentic/GRAPH/knowledge-graph.json`; may be configured elsewhere).
- `graph.required`.
- `graph.fallback` (default: `codemap`).

Cross-check against the managed section of `.agentic/GRAPH_INDEX.md`: provider, last generated, parseable, fallback active.

Classify graph status:

- **graph-first** — graph file exists at the configured path, is parseable, fallback inactive.
- **fallback** — graph unavailable; `CODEMAP.json` present; `graph.required` is `false` or fallback explicitly active.
- **broken** — config requires the graph but neither graph nor an acceptable fallback is present.

If status is `broken`, stop. Tell the user to run `agenticOS-graph` (or `agenticOS-tooling` if config itself is wrong).

### Step 3 — Detect legacy repo-local v1 skill (warn only)

If `.cursor/skills/agenticOS-context/SKILL.md` exists in the repo, note it as legacy v1 and warn the user that the personal/global v2 skill takes precedence. Do not edit the legacy file unless the user explicitly asks.

### Step 4 — Run the routing engine

Run:

```bash
python scripts/agentic/route_task.py "<concise task description>"
```

Pass the user's task verbatim where possible. If the user has named explicit files, paths, functions, symbols, endpoints, or tests, include those terms in the task string so the router can anchor on them.

If the script fails or returns invalid JSON, stop. Recommend the user run `agenticOS-tooling` (for script issues) or `agenticOS-graph` (for graph issues). Do not retry blindly.

### Step 5 — Parse the context bundle

Bundle source of truth: stdout from the router. A cached copy is also written to `.agentic/CONTEXT/last_context.json`. Required keys to read:

- `task`
- `confidence` (`high` | `medium` | `low`)
- `graph_available` (boolean)
- `graph_source` (path)
- `fallback_active` (boolean)
- `selected_paths` (list)
- `selection_reasons` (map of path → one-line reason)
- `graph_nodes` (list)
- `dependency_paths` (list)
- `related_tests` (list)
- `subsystem_files` (list)
- `memory_files` (list)
- `risk_tags` (list)
- `unknowns` (list)
- `stop_conditions` (list)

If keys are missing or malformed, stop and report. Do not fabricate fields.

### Step 6 — Read only the files in the bundle

Read these and only these (unless step 7 or step 9 changes the scope):

- `selected_paths`
- `memory_files`
- `subsystem_files`
- `related_tests`

Do not perform wide repo scans. Do not read files outside the bundle unless a specific, named gap blocks the task. If you find yourself wanting to read more, ask first.

### Step 7 — Handle explicit user-named files

If the user explicitly named a file, path, function, symbol, endpoint, or test in their request:

- If the route bundle includes it, proceed with that file as a primary anchor.
- If the route bundle omits it but the file exists on disk, read the explicitly named file and proceed with the narrowest safe scope. Report that the routing engine needs correction (note the missing anchor in the final status).
- Do not stop merely because the route is low-confidence when the user supplied an existing file target.
- If the named file does not exist, tell the user before doing anything else.

Explicit user evidence always overrides heuristic routing. This rule is not optional.

### Step 8 — State the status block before implementing

Before writing any code, print the status block exactly in the format under "Status block format" below. The user must be able to read it and intervene if the route looks wrong.

### Step 9 — Honour stop conditions

If `stop_conditions` is non-empty, or if `confidence` is `low`:

- Do not implement.
- Show the status block.
- Ask the user to confirm the route, refine the task string, or supply more evidence.

If the bundle looks obviously wrong (missing the most relevant source-of-truth file, wrong subsystem, contradicts an explicit user anchor), refine the task string and re-run `route_task.py` once. If the second attempt is still wrong, stop and ask.

### Step 10 — Proceed (or hand off)

If status is green and the user has not requested other skills, implement using the bundle's selected evidence and the narrowest safe scope.

Other skills may be used after context is compiled if the user requests them — for example planning skills, code review skills, `/doyouunderstand`, or test skills. Agentic OS runs first because it compiles the evidence packet; downstream skills consume that evidence.

## Routing priorities the skill respects

The router applies these in order; this skill honours the same hierarchy when interpreting the bundle:

1. Explicit user-named file/path/function/symbol/endpoint/test references.
2. Graph traversal from explicit anchors.
3. Graph search against task terms.
4. Dependency and impact expansion.
5. Related tests.
6. Operational memory overlays (`PROJECT_BRIEF.md`, `MEMORY_INDEX.md`, `SUBSYSTEMS/*.md`).
7. Risk overlays (`high_risk_patterns`).
8. Fallback CODEMAP only if the graph is unavailable.
9. Filesystem fallback only when neither graph nor CODEMAP can resolve the request.
10. Stop conditions when evidence is insufficient.

Explicit user evidence overrides every heuristic step. If a user names an existing file, it must not be ignored.

## Status block format

Print this before any implementation step. Keep it tight.

```
agenticOS-context status
========================

Task: <verbatim or normalised>

Graph:
- Status: <graph-first | fallback | broken>
- Provider: <understand-anything | codemap | none>
- Source: <path>
- Fallback active: <yes | no>

Routing:
- Confidence: <high | medium | low>
- Selected paths (<n>):
  - `<path>` — <reason>
- Memory files: <list>
- Subsystem files: <list>
- Related tests: <list>
- Risk tags: <list, or "none">

Unknowns:
- <list, or "none">

Stop conditions:
- <list, or "none">

Explicit user anchors:
- <list of user-named files honoured, or "none supplied">
- Router omitted anchors: <list, or "none">

Plan:
- <one or two lines describing the narrowest safe scope you will edit>
```

## Stop conditions (skill-level)

Stop and ask the user before proceeding when:

- Agentic OS is not initialised (any required file from step 1 missing).
- Graph status is `broken`.
- `route_task.py` fails or returns invalid JSON.
- The bundle has `confidence: low` or non-empty `stop_conditions`.
- The bundle omits an explicit user-named file that exists on disk (read it and proceed with narrowest scope, but report the router gap).
- The task spans multiple unrelated subsystems with no clear anchor.
- A risk overlay flags `security`, `money`, `data-integrity`, `secrets`, or `infra` and the route confidence is not `high`.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Non-goals

- Do not bootstrap or repair Agentic OS.
- Do not modify `.agentic/` or `scripts/agentic/`.
- Do not update memory (use `agenticOS-update`).
- Do not refresh the graph (use `agenticOS-graph`).
- Do not regenerate tooling (use `agenticOS-tooling`).
- Do not perform wide repo scans by default.
- Do not ignore explicit user-named files.
- Do not silently proceed when status, config, or routing output is broken.
- Do not treat CODEMAP as primary; it is fallback only.
- Do not edit the legacy `.cursor/skills/agenticOS-context/SKILL.md` unless explicitly asked.
