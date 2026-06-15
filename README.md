# Agentic OS

This is the source of truth for t8 Agentic OS. Agentic OS provides the core agent skills and deterministic Python scripts used to bootstrap, route, and maintain agent context in software repositories.

This repo is intentionally minimal. There is no installer or package layout yet; skills and scripts are copied or linked into their runtime locations manually for now.

## What lives here

| Path         | Purpose                                                                                 |
| ------------ | --------------------------------------------------------------------------------------- |
| `skills/`    | Canonical Agentic OS skills (`SKILL.md` per skill)                                      |
| `scripts/`   | Standard-library Python tooling for graph sync, routing, memory validation, and updates |
| `templates/` | Reserved for default `.agentic/` scaffold files (not populated yet)                     |
| `tests/`     | Reserved for script and routing tests (not populated yet)                               |

## Skills

| Skill                 | Role                                                          |
| --------------------- | ------------------------------------------------------------- |
| `agenticOS-bootstrap` | Orchestrates first-time setup, repair, refresh, and migration |
| `agenticOS-graph`     | Installs and maintains the structural knowledge graph         |
| `agenticOS-memory`    | Initialises and refreshes operational memory (`.agentic/`)    |
| `agenticOS-tooling`   | Generates and repairs repo-local scripts and config           |
| `agenticOS-context`   | Runtime context compilation for coding tasks                  |
| `agenticOS-update`    | Post-change memory and lesson maintenance                     |

Skills are designed to be installed globally (for example under `~/.agents/skills/` or your editor's skill path), not committed into consumer repositories.

## Scripts

Deterministic, stdlib-only Python 3.10+ scripts. See [`scripts/README.md`](scripts/README.md) for usage.

Run from a **consumer repository root** that has an `.agentic/` install:

```bash
python scripts/route_task.py "describe your task"
python scripts/validate_memory.py
python scripts/graph_sync.py
python scripts/update_memory.py
```

When copied into a target repo, these typically live at `scripts/agentic/` relative to that repo's root.

## Design principles

- **Skills orchestrate. Tools execute. Models curate.**
- Graph-first structural intelligence (Understand Anything preferred; CODEMAP fallback only when needed).
- Tooling is deterministic, idempotent, and safe to re-run.
- Operational memory stays in consumer repos; this repo holds the reusable core only.

## Status

Early development on the `sit` branch. Packaging, templates, and tests will be added as the tooling stabilises.
