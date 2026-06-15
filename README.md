# t8 Agentic OS

**t8 Agentic OS** is a disciplined approach to making AI agents reliable in large, complex software repositories. This repo is the **source of truth** for its core agent skills and deterministic Python scripts — the reusable kernel that gets installed into consumer repositories.

There is no installer or package layout yet. Skills and scripts are copied or linked into their runtime locations manually for now.

---

## The problem

Modern software systems are too large and too complex for stateless language models to understand in a single prompt.

The problem is not that models are unintelligent. The problem is that they are **context-bound**. Every prompt begins with amnesia. Without structure, the model compensates by guessing — and guessing leads to architectural drift, inconsistent decisions, subtle regressions, and wasted effort.

**Agentic OS treats a software repository as an operating environment for AI agents.**

Just as a traditional operating system manages memory, storage, and process scheduling for programs, Agentic OS manages **context**, **knowledge**, and **decision routing** for language models.

---

## Core principles

1. **Context is working memory** — Models perform best with the smallest set of _relevant_ evidence. More context is not inherently better; irrelevant context degrades reasoning.

2. **Memory is indexed, not dumped** — Durable knowledge is structured as an index pointing to source evidence. Memory answers: what exists, where is the source of truth, what must be read before editing, what lessons were learned, and what tests prove correctness.

3. **Routing precedes reasoning** — The first task of an agent is not coding. The first task is determining what information is required.

4. **Evidence over intuition** — Agents read canonical source files before proposing changes. When uncertainty is high, the correct response is to investigate, not improvise.

5. **Decisions must compound** — Every incident, architectural decision, and lesson learned should improve future performance. The system becomes more reliable over time.

6. **Tooling beats prompting** — Deterministic tools handle indexing, search, routing, and validation. The LLM spends its reasoning budget on judgement.

7. **Memory must stay fresh** — Generated maps are regenerated automatically. Human summaries are updated only when durable knowledge changes.

8. **Quality over token minimisation** — Lower token usage is a side effect. The true goal is fewer incorrect assumptions and higher quality outputs.

> **Skills orchestrate. Tools execute. Models curate.**

---

## The Agentic OS model

Agentic OS consists of two cooperating systems.

### Memory layer

A structured, evolving representation of:

- Architecture and subsystems
- Principles and invariants
- Lessons learned
- Change history
- File relationships (via a structural graph)

In a consumer repository, this lives under `.agentic/` — operational memory for agents, governed by humans. It is **indexed**, not a dump of the codebase.

### Context compiler

A deterministic routing engine that converts a task into a focused **context bundle**. For every prompt, it decides:

- Relevant subsystems
- Required files
- Applicable rules
- Historical lessons
- Risks, unknowns, and verification steps

The routing engine is `scripts/route_task.py`. The runtime skill `agenticOS-context` orchestrates it before non-trivial coding work.

Together, these systems pursue one objective:

> **Provide the minimal sufficient evidence required for the highest quality decision.**

---

## How this repo fits in

| Layer                                   | Where it lives                                       | Purpose                                                     |
| --------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------- |
| **Skills** (this repo → global install) | `skills/` → `~/.agents/skills/` or editor skill path | Orchestration: bootstrap, routing, memory, graph, updates   |
| **Scripts** (this repo → consumer repo) | `scripts/` → `scripts/agentic/` in target repos      | Deterministic execution: route, validate, sync, update      |
| **Memory** (consumer repo only)         | `.agentic/` in each project                          | Indexed operational knowledge for that codebase             |
| **Graph** (consumer repo)               | `.agentic/GRAPH/` via Understand Anything            | Structural intelligence (CODEMAP fallback only when needed) |

Consumer repositories get memory, config, and tooling — **not** copies of the canonical skills (unless explicitly pinned).

---

## What lives here

| Path         | Purpose                                                                                 |
| ------------ | --------------------------------------------------------------------------------------- |
| `skills/`    | Canonical Agentic OS skills (`SKILL.md` per skill)                                      |
| `scripts/`   | Standard-library Python tooling for graph sync, routing, memory validation, and updates |
| `templates/` | Reserved for default `.agentic/` scaffold files (not populated yet)                     |
| `tests/`     | Reserved for script and routing tests (not populated yet)                               |

---

## Skills

| Skill                 | Role                                                          |
| --------------------- | ------------------------------------------------------------- |
| `agenticOS-bootstrap` | Orchestrates first-time setup, repair, refresh, and migration |
| `agenticOS-graph`     | Installs and maintains the structural knowledge graph         |
| `agenticOS-memory`    | Initialises and refreshes operational memory (`.agentic/`)    |
| `agenticOS-tooling`   | Generates and repairs repo-local scripts and config           |
| `agenticOS-context`   | Runtime context compilation for coding tasks                  |
| `agenticOS-update`    | Post-change memory and lesson maintenance                     |

**Typical flow:** `agenticOS-bootstrap` sets up a repo → `agenticOS-context` runs before coding → `agenticOS-update` runs after durable changes.

---

## Scripts

Deterministic, stdlib-only **Python 3.10+** scripts. See [`scripts/README.md`](scripts/README.md) for details.

Run from a **consumer repository root** that has an `.agentic/` install:

```bash
python scripts/route_task.py "describe your task"
python scripts/validate_memory.py
python scripts/graph_sync.py
python scripts/update_memory.py
```

When copied into a target repo, these typically live at `scripts/agentic/` relative to that repo's root.

| Script               | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `route_task.py`      | Route a task string to a context bundle                   |
| `validate_memory.py` | Structural checks on memory, config, and graph            |
| `graph_sync.py`      | Validate graph JSON and record freshness                  |
| `update_memory.py`   | Sync metadata, detect git changes, refresh managed memory |

---

## The standard of success

A successful Agentic OS produces agents that:

- Read the right files first
- Ask better questions
- Make fewer assumptions
- Respect architectural boundaries
- Catch regressions earlier
- Improve with every decision

---

## Status

Early development. Work happens on the `sit` branch; changes merge to `main` via pull request. Packaging, templates, and tests will be added as the tooling stabilises.
