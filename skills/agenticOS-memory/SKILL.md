---
name: agenticOS-memory
description: Initialises, refreshes, reviews, and maintains the t8 Agentic OS operational memory layer in a repository. Creates and updates `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/SUBSYSTEMS/`, and `.agentic/LESSONS/` from real repo evidence (README, docs, manifests, deployment config, existing AI instruction files, and graph status). Uses managed and human memory regions, populates both from evidence on init, refreshes managed regions freely, preserves human regions by default but reviews them for staleness and proposes confirmed edits. Memory is agent-first, routing-oriented, and never duplicates the graph or codebase structure. Use when initialising memory in a new repo, refreshing existing memory, repairing missing memory files, migrating from a legacy memory layout, or when agenticOS-bootstrap delegates memory work. Do not use to install Understand Anything, generate scripts/agentic tooling, perform runtime routing, or append durable lessons after code changes.
---

# agenticOS-memory

Personal/global setup and maintenance skill for the Agentic OS operational memory layer. One job: create, refresh, and review the memory files that overlay the structural graph with routing-useful operational knowledge.

This skill is often invoked by `agenticOS-bootstrap`. It can also be run directly when only memory needs attention. It does not touch the graph, runtime tooling, or runtime routing.

## When to use

- Initialising operational memory in a new Agentic OS install.
- Refreshing memory after notable architectural or documentation changes.
- Repairing missing or partial memory files.
- Migrating legacy memory (no managed/human regions) into the v2 layout.
- Reviewing human notes for staleness, inaccuracy, incompleteness, or conflict.

## When NOT to use

- To install or refresh the structural graph. Use `agenticOS-graph`.
- To create `.agentic/CONFIG/agentic.json` or `scripts/agentic/*`. Use `agenticOS-tooling`.
- To compile a focused context bundle for a coding task. Use `agenticOS-context`.
- To append a durable lesson, decision, or incident after a code change. Use `agenticOS-update`.

## Operating principle

Agentic OS memory is primarily for AI agents. Humans are reviewers and governors. Files must be:

- **Evidence-driven.** Every claim traces to README, docs, manifests, deployment config, an external AI instruction file, or graph status. If no evidence exists, write `Unknown` — never fabricate.
- **Agent-first.** Short bullets, concrete file paths, routing hooks, risk markers. Not prose for human readers.
- **Concise and operational.** A future agent should learn what to read, what to avoid, what is risky, and what is unknown — not the project's marketing pitch.
- **Non-duplicative.** Memory is the routing overlay on top of the graph. Do not restate the graph or list every file. Reference paths and let the graph do the structural work.
- **Refreshable, not curated-only.** Managed regions are refreshed by this skill. Human regions are preserved by default but reviewed for staleness; proposed edits apply only after confirmation.
- **Never blank.** Both managed and human regions are populated on init from real evidence. No "humans will fill this in later" placeholders.

## Managed and human regions

Every major memory file uses both regions:

```markdown
<!-- agentic:managed:start -->
Agent/tool maintained content. Refreshed freely.
<!-- agentic:managed:end -->

<!-- human:notes:start -->
Human judgement, intent, context, warnings, nuance.
Preserved by default. Reviewed for staleness. Edits require confirmation.
<!-- human:notes:end -->
```

Rules:

- On init, populate **both** regions from repo evidence. The human region is initially seeded by the agent from README/project evidence — not left empty.
- On refresh, rewrite the managed region. Do not touch the human region byte-for-byte.
- Review the human region for staleness, inaccuracy, incompleteness, or conflict with current evidence. If a problem is found, **propose** a specific edit and apply it only after the user confirms.
- Never silently overwrite the human region.
- Never delete the human region. If empty after a review pass (rare), leave a one-line evidence-derived seed.

## Inputs the skill reads

Read shallowly. Do not scan the whole codebase.

- `README*` at repo root.
- `docs/`, `ARCHITECTURE*`, `System_Architecture*`, `PRD*` (one level deep).
- Manifest files: `package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `build.gradle*`, `composer.json`, `Pipfile`.
- Deployment/config: `Dockerfile`, `docker-compose*.y*ml`, `Makefile`, `.github/workflows/`, framework configs (`vite.config.*`, `next.config.*`, `nuxt.config.*`, `astro.config.*`, `nest-cli.json`, `manage.py`, `alembic.ini`).
- Existing `.agentic/GRAPH_INDEX.md` for graph status (read only; do not modify).
- External AI instruction sources: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursor/skills/*`, `.github/copilot-instructions.md`.
- Top-level directory listing (one level deep) for subsystem evidence.
- Test directory patterns (`tests/`, `__tests__/`, `*.test.*`, `*_test.*`, `test_*.py`).

External AI instruction files are inputs, not outputs. Respect them, summarise durable rules into memory, and surface conflicts rather than rewriting the source files.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Memory skill progress:
- [ ] Step 1: Confirm repo root
- [ ] Step 2: Ensure .agentic/ folder structure exists
- [ ] Step 3: Inspect repo evidence and external AI instructions
- [ ] Step 4: Read graph status from GRAPH_INDEX.md if present
- [ ] Step 5: Create or refresh PROJECT_BRIEF.md
- [ ] Step 6: Create or refresh MEMORY_INDEX.md
- [ ] Step 7: Create or refresh SUBSYSTEMS/README.md and strong-evidence subsystem files
- [ ] Step 8: Create LESSONS/decisions.md and incidents.md (templates only on init)
- [ ] Step 9: Review human regions for staleness; propose edits with confirmation
- [ ] Step 10: Print summary
```

### Step 1 — Confirm repo root

Verify `.git/` or a top-level manifest is present. If ambiguous, ask before proceeding.

### Step 2 — Ensure folder structure

Create only what is missing:

```
.agentic/
  PROJECT_BRIEF.md
  MEMORY_INDEX.md
  SUBSYSTEMS/
    README.md
  LESSONS/
    decisions.md
    incidents.md
```

Do not delete existing files. Do not create `.agentic/CONFIG/`, `.agentic/GRAPH/`, `.agentic/CONTEXT/`, or `scripts/agentic/` here — those are owned by `agenticOS-tooling` and `agenticOS-graph`.

### Step 3 — Inspect evidence

Capture into working notes:

- Project purpose (one or two sentences).
- Primary languages, frameworks, package managers, runtimes.
- Deployment signals.
- Top-level folders that look like subsystems.
- Source-of-truth files (schemas, OpenAPI specs, IaC, migrations, config).
- External AI instruction sources present, and any rules that look durable.
- Conflicts between sources (e.g. README and `CLAUDE.md` disagree).
- Anything ambiguous → `Unknown`.

### Step 4 — Read graph status

If `.agentic/GRAPH_INDEX.md` exists, read the managed section to capture: provider, graph path, graph mode available, fallback mode, parseable. Reference these in `MEMORY_INDEX.md` rather than restating them.

If `GRAPH_INDEX.md` does not exist, note it. Memory can still be initialised; just record graph status as `unknown` in `MEMORY_INDEX.md`.

### Step 5 — `PROJECT_BRIEF.md`

Concise project-level operational overview. One screen. Both regions populated on init.

Template:

```markdown
<!-- agentic:managed:start -->
# Project brief

## Purpose
<one or two sentences derived from README. "Unknown" only if README is silent.>

## Stack
- Languages: <list>
- Frameworks: <list>
- Runtime: <node/python/jvm/etc.>
- Package manager: <npm/pnpm/uv/poetry/etc.>

## Deployment
<hosting, container, CI/CD signals; "Unknown" if not discoverable>

## Major subsystems
- <name> — <one-line role, references SUBSYSTEMS/<name>.md if created>

## Source-of-truth files
- `<path>` — <what it defines>

## External agent instruction sources
- `CLAUDE.md` — <one-line summary or "absent">
- `AGENTS.md` — <one-line summary or "absent">
- `.cursor/rules/*` — <one-line summary or "absent">
- `.cursor/skills/*` — <one-line summary or "absent">
- `.github/copilot-instructions.md` — <one-line summary or "absent">

## Conflicts
- <conflict between sources, or "none">

## Unknowns
- <explicit list, or "none">
<!-- agentic:managed:end -->

<!-- human:notes:start -->
## Product intent
<derived from README/PRD. Not blank by default.>

## Architectural philosophy
<derived from architecture docs or repo signals. Not blank by default.>

## Business constraints
<derived from docs if present, else "Unknown — review".>

## Project-specific judgement
<reviewer/maintainer notes. On init, agent seeds a one-line evidence-derived starter; humans expand later.>
<!-- human:notes:end -->
```

### Step 6 — `MEMORY_INDEX.md`

Routing-oriented operational index. Not a duplicate of the graph.

Template:

```markdown
<!-- agentic:managed:start -->
# Memory index

## Subsystems
- See `SUBSYSTEMS/` (one file per major subsystem).

## High-risk areas
- `<path or pattern>` — <risk tag, e.g. security, money, data-integrity, secrets, infra>

## Source-of-truth files
- `<path>` — <what it defines>

## Lessons and decisions index
- Decisions: `LESSONS/decisions.md`
- Incidents: `LESSONS/incidents.md`

## External instruction sources
- `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursor/skills/*`, `.github/copilot-instructions.md`

## Graph status (reference)
- See `.agentic/GRAPH_INDEX.md` (provider, path, fallback, freshness).

## Memory freshness
- Last refreshed: <ISO-8601 UTC>
- Files refreshed this run: <list>
<!-- agentic:managed:end -->

<!-- human:notes:start -->
## Routing hints
- <task intent → relevant subsystems/files/tests; seeded on init from evidence>

## Priority warnings
- <hard rules; "read this first" notes; seeded on init from evidence>
<!-- human:notes:end -->
```

### Step 7 — `SUBSYSTEMS/`

Always create `SUBSYSTEMS/README.md`:

```markdown
# Subsystems

One file per major subsystem. Each file is short and routing-oriented:

- Purpose
- Owned paths
- Public contracts
- Source-of-truth files
- Related tests
- Dependencies
- Invariants
- Common failure modes
- Do-not-do rules
- Related lessons
- Unknowns

Create a subsystem file only when evidence is strong (clear top-level folder, manifest/entry point, or explicit doc). Prefer `Unknown` over invention.
```

Create one `<subsystem>.md` only when evidence is strong. Use the same managed/human region layout. Strong evidence means at least one of:

- a dedicated top-level folder with a manifest/entry point;
- an architecture doc that names the subsystem;
- an external instruction source that names the subsystem.

Subsystem file template (keep it tight):

```markdown
<!-- agentic:managed:start -->
# <subsystem>

## Purpose
<one line>

## Owned paths
- `<path>`

## Public contracts
- <APIs, events, schemas, exported types>

## Source-of-truth files
- `<path>` — <what it defines>

## Related tests
- `<path or pattern>`

## Dependencies
- <other subsystems or external services>

## Invariants
- <hard rules — e.g. "OPENAI_API_KEY is backend-only">

## Common failure modes
- <observed or anticipated failures>

## Do-not-do rules
- <explicit prohibitions>

## Related lessons
- `LESSONS/decisions.md#<anchor>` or "none"

## Unknowns
- <explicit list, or "none">
<!-- agentic:managed:end -->

<!-- human:notes:start -->
- <human judgement, nuance, warnings; seeded on init from evidence>
<!-- human:notes:end -->
```

### Step 8 — `LESSONS/`

Create templates on init. Do not fabricate entries.

`decisions.md`:

```markdown
# Decisions

Durable architectural and design decisions only. Not every change.

## Entry template
- Date:
- Context:
- Decision:
- Consequences:
- Alternatives considered:
```

`incidents.md`:

```markdown
# Incidents

Durable lessons from failures, outages, regressions, or near-misses.

## Entry template
- Date:
- Summary:
- Root cause:
- Detection:
- Resolution:
- Prevention (rules added, tests added, code changes):
```

Seed an entry only when concrete evidence already exists in the repo (e.g. an `ARCHITECTURE.md` records a decision, or a post-mortem doc exists). Otherwise leave the templates alone — `agenticOS-update` appends entries after real durable events.

### Step 9 — Review human regions

For every file with a human region that existed before this run:

1. Compare against current managed content and current repo evidence.
2. Flag as `stale`, `inaccurate`, `incomplete`, or `conflicting` where applicable.
3. Propose a specific edit (show the diff).
4. Apply only after the user confirms.
5. If the user declines, leave the human region untouched and record the disagreement in the run summary.

For files created in this run, the agent seeds the human region from evidence. No confirmation needed for seeds, but the seed must trace to evidence and never fabricate intent.

### Step 10 — Print summary

Use the format in the next section.

## Anti-duplication rules

- Do not list every file in the repo. The graph already does that.
- Do not restate graph nodes, dependencies, or import edges in memory.
- Do not create a giant static codemap. CODEMAP is a fallback artifact owned by `agenticOS-tooling`, not memory.
- Do not paste large excerpts of the README, architecture docs, or external AI instruction files. Summarise and reference.
- Do not write prose explanations of how the code works. Reference the source-of-truth file path instead.

## Stop conditions

Stop and ask the user before proceeding when:

- The current directory is not clearly the repo root.
- Required evidence is missing or contradictory (e.g. no README, multiple conflicting architecture docs).
- A human region needs an edit that materially changes recorded intent.
- External AI instruction sources disagree with each other on durable rules.
- The user has uncommitted changes inside `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/SUBSYSTEMS/`, or `.agentic/LESSONS/`.
- A subsystem could be created with weak evidence — prefer to skip and surface as Unknown.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Final summary format

Print exactly these sections, in order. Keep it under one screen.

```
agenticOS-memory summary
========================

Mode: <init | refresh | repair | migration>

Files created or refreshed:
- PROJECT_BRIEF.md: <created | managed refreshed | unchanged>
- MEMORY_INDEX.md: <created | managed refreshed | unchanged>
- SUBSYSTEMS/README.md: <created | unchanged>
- SUBSYSTEMS/*.md: <list of subsystem files created or refreshed>
- LESSONS/decisions.md: <created | unchanged>
- LESSONS/incidents.md: <created | unchanged>

External instruction sources ingested:
- <list of files summarised, or "none present">

Graph status reference:
- <provider, fallback mode, parseable — or "GRAPH_INDEX.md absent">

Human sections:
- Preserved unchanged: <count>
- Seeded from evidence on init: <count>
- Flagged for review: <count, with file paths>
- Edited after confirmation: <count, with file paths>

Conflicts surfaced:
- <list with file paths, or "none">

Unknowns:
- <list, or "none">

Next recommended action:
- <single sentence>
```

## Non-goals

- Do not install or refresh the structural graph.
- Do not generate or modify `.agentic/CONFIG/agentic.json`.
- Do not generate or modify `scripts/agentic/*`.
- Do not create the six canonical personal/global skills.
- Do not perform runtime context routing.
- Do not append durable lessons after a code change (that is `agenticOS-update`).
- Do not duplicate the graph or recreate a giant CODEMAP.
- Do not overwrite human regions silently.
- Do not leave important sections blank for humans to fill later.
- Do not fabricate project intent, architecture, or subsystem rules.
