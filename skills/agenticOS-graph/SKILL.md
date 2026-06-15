---
name: agenticOS-graph
description: Installs, validates, refreshes, or repairs the structural graph layer used by t8 Agentic OS. Uses Understand Anything as the preferred graph provider and writes to .agentic/GRAPH/knowledge-graph.json by default. Records graph status in .agentic/GRAPH_INDEX.md and updates the graph path in .agentic/CONFIG/agentic.json when the provider's native output path is used instead. Falls back to a CODEMAP cache only when graph mode is unavailable, and surfaces installation blockers, freshness issues, and unknowns rather than guessing. Use when initialising, refreshing, repairing, or migrating the structural intelligence layer, or when agenticOS-bootstrap delegates graph work. Do not use to write operational memory or runtime tooling.
---

# agenticOS-graph

Personal/global setup and maintenance skill for the Agentic OS structural graph layer. One job: graph install, refresh, validation, and status reporting.

This skill is often invoked by `agenticOS-bootstrap`. It can also be run directly when only the graph needs attention. It does not touch operational memory files, runtime skills, or `scripts/agentic/*` beyond what is needed to record graph status.

## When to use

- Initialising the graph layer in a new Agentic OS install.
- Refreshing an existing graph after significant code changes.
- Repairing a missing, corrupt, or stale graph artifact.
- Migrating from a legacy CODEMAP-first install to a graph-first one.
- Confirming graph freshness before another skill relies on it.

## When NOT to use

- To create or rewrite operational memory. Use `agenticOS-memory`.
- To create or repair `agentic.json` schema, scripts, or runtime tooling. Use `agenticOS-tooling`.
- To run normal coding tasks. Use `agenticOS-context`.
- To record durable lessons after a change. Use `agenticOS-update`.

## Operating principle

Understand Anything (UA) is the preferred structural provider, but it is just a tool. Agentic OS owns the architecture and the contract:

- Preferred graph path: `.agentic/GRAPH/knowledge-graph.json`.
- If UA cannot write to that path, use UA's native output path and record the actual path in both `.agentic/CONFIG/agentic.json` (`graph.path`) and `.agentic/GRAPH_INDEX.md`.
- Do not duplicate the full graph into Markdown. `GRAPH_INDEX.md` holds status only, not graph content.
- CODEMAP is fallback-only. Never recreate a giant CODEMAP as the primary structural layer.
- Filesystem lookup may support explicit file/path matches in the router, but is not the primary structural layer.
- Graph freshness must be visible. If unknown, mark it unknown.
- Trust policy:
  - **First-party marketplace/plugin install commands** (e.g. Claude Code `/plugin install`, Cursor Settings → Plugins) may be **suggested** to the user directly. The host IDE owns the consent UX.
  - **Remote shell installers** (curl-pipe-sh, `iwr | iex`, npx of unknown packages, etc.) must never be quoted or executed without **explicit, separate user approval** for that specific command.
- Preserve all human-authored content in `GRAPH_INDEX.md`. Update only the managed section.

## Workflow

Copy this checklist into TodoWrite and track progress:

```
Graph skill progress:
- [ ] Step 1: Confirm repo root
- [ ] Step 2: Detect graph state
- [ ] Step 3: Detect Understand Anything availability
- [ ] Step 4: Decide graph path
- [ ] Step 5: Generate or refresh graph (or activate fallback)
- [ ] Step 6: Validate graph artifact
- [ ] Step 7: Update GRAPH_INDEX.md managed section
- [ ] Step 8: Update agentic.json graph path if needed
- [ ] Step 9: Print summary
```

### Step 1 — Confirm repo root

Verify `.git/` or a top-level manifest is present. If ambiguous, ask the user to confirm before proceeding. Do not assume.

### Step 2 — Detect graph state

Inspect (one level deep, do not read large files):

- `.agentic/GRAPH/knowledge-graph.json` (preferred artifact).
- `.understand-anything/` and any other UA-native graph output directory.
- `.agentic/CONFIG/agentic.json`. Parse `graph.provider`, `graph.path`, `graph.required`, `graph.fallback` if present.
- `.agentic/GRAPH_INDEX.md`. If present, identify managed and human regions; do not modify yet.
- `.agentic/CODEMAP.json`. Note only — this skill does not regenerate it. CODEMAP regeneration belongs to `agenticOS-tooling` when fallback mode is active.

Record into working notes:

- preferred graph artifact present? parseable on first byte check?
- UA-native graph artifact present? at what path?
- configured graph path from `agentic.json`, if any;
- whether the current install is graph-first or CODEMAP-only (legacy).

### Step 3 — Detect Understand Anything availability

The only **reliable** filesystem signal that UA is usable in the target repo is the presence of a parseable graph artifact. "Plugin installed but never run" is not reliably observable, so do not try to infer it — prompt instead.

Check in this order. Stop at the first hit:

1. **Configured graph path parses.** `agentic.json.graph.path` points at a file that exists and parses as JSON on a first-byte check.
2. **UA native artifact present.** `.understand-anything/knowledge-graph.json` (or any sibling JSON in `.understand-anything/`) exists and parses.
3. **Vendored UA directory.** `.understand-anything/` exists (any contents) — implies a prior install or vendored use; the user may need to run `/understand` to produce the artifact.
4. **Legacy signals (optional, low confidence):** `command -v understand-anything`, `understand-anything` in `package.json`, or `pip show understand-anything`. Useful if present but not required.

If none of the above resolve to a parseable artifact, classify UA as **not available** and proceed to the install-or-fallback prompt below.

#### UA not available — install or fallback prompt

Detect the host platform from working notes provided by `agenticOS-bootstrap` (`cursor`, `claude-code`, `codex`, `vscode-copilot`, `copilot-cli`, `other`, or `unknown`). Lead with the matching block; include the others for reference but do not duplicate them all in chat.

Offer three paths, in this order:

**Option A — Install the UA plugin for your host (preferred).**

The marketplace/plugin install for your host owns its own consent UX, so these may be quoted directly. They are **not** silent remote installers.

- **Cursor (auto-discovery):** Cursor auto-discovers UA when the UA repo is cloned. If not auto-detected, open **Settings → Plugins** and add `https://github.com/Lum1104/Understand-Anything`.
- **Claude Code:**

  ```text
  /plugin marketplace add Lum1104/Understand-Anything
  /plugin install understand-anything
  ```

- **Copilot CLI:**

  ```bash
  copilot plugin install Lum1104/Understand-Anything:understand-anything-plugin
  ```

- **VS Code + GitHub Copilot:** auto-discovery via `.copilot-plugin/plugin.json` when the UA repo is cloned.

After install, the user generates the graph by running `/understand` (or the equivalent slash command for their host). Default UA output is `.understand-anything/knowledge-graph.json`.

**Option B — One-line installer (Codex / Gemini CLI / OpenCode / Antigravity / Pi / Vibe / Hermes / Cline / KIMI / VS Code).**

This path uses `curl | bash` (or `iwr | iex` on Windows) and falls under the **remote shell installer** trust rule. Do **not** quote or run the commands unless the user explicitly approves *this specific step*. If they do, then quote (do not execute on their behalf) the relevant command from the UA README, e.g.:

```bash
# Only with explicit user approval:
curl -fsSL https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/install.sh | bash -s <platform>
```

Supported `<platform>` values per UA README: `gemini`, `codex`, `opencode`, `pi`, `openclaw`, `antigravity`, `vibe`, `vscode`, `hermes`, `cline`, `kimi`.

**Option C — Activate CODEMAP fallback.**

Skip UA entirely. Set provider to `codemap` and continue. CODEMAP generation is owned by `agenticOS-tooling`. Surface the trade-off: structural routing quality is reduced, and graph mode should be revisited later.

**After the prompt:**

- Wait for the user's choice. Do not pick on their behalf.
- If they install UA (Option A or B), wait until the graph artifact appears, then re-detect from Step 3 and proceed.
- If they choose Option C, set provider `codemap` and continue to Step 4.
- Do not infer that "UA is installed" from any signal other than a parseable artifact appearing on disk.

### Step 4 — Decide graph path

Decision rules, applied in order:

1. If the user explicitly named a graph path in this run, use it.
2. Else if `agentic.json.graph.path` is set and the file exists, use it.
3. Else if UA is available and can write to `.agentic/GRAPH/knowledge-graph.json`, use that.
4. Else if UA writes only to a native path (e.g. `.understand-anything/knowledge-graph.json`), use the native path and plan to record it in `agentic.json`.
5. Else if UA is not available and the user approved fallback, set provider to `codemap` and target `.agentic/CODEMAP.json`.

Record the chosen path and provider into working notes. If still uncertain, stop and ask.

### Step 5 — Generate or refresh graph (or activate fallback)

Branch based on provider:

**Provider `understand-anything`:**

- Canonical generation command (host-side slash command, runs in the agent/chat surface — not a shell command unless the host documents otherwise):

  ```text
  /understand
  ```

  Optional flags per UA README: `--language <code>`, `--auto-update`, scope path (e.g. `/understand src/frontend`).

- For refresh, `/understand` is incremental by default.
- Do not invent flags. If unsure how to invoke UA in this host, ask the user once.
- Capture only a brief stdout/stderr summary into working notes. Do not paste the full graph anywhere.
- After generation, expect the artifact at `.understand-anything/knowledge-graph.json` unless UA's host integration writes elsewhere. Record the actual path in Step 8.

**Provider `codemap` (fallback only):**

- Do not generate the CODEMAP here. Note that `agenticOS-tooling` owns CODEMAP generation in fallback mode. Record fallback as active and proceed to validation against the existing or newly generated CODEMAP file.
- If `.agentic/CODEMAP.json` is missing and fallback is required, surface that as a blocker and recommend running `agenticOS-tooling`.

### Step 6 — Validate graph artifact

For the chosen artifact, verify all of:

- exists at the configured path;
- parses as valid JSON (or the provider's expected format);
- is non-empty (has a top-level structure plus at least one node/entry);
- references at least one path that resolves on disk inside the repo (spot-check up to five sample paths).

Record validation results. Mark `parseable: yes/no`, `non_empty: yes/no`, `sample_paths_resolve: <hit>/<sample>`.

If validation fails:

- Do not retry generation automatically. Surface the failure with the exact error and the chosen path.
- Recommend re-running this skill after the user has addressed the cause, or escalate to `agenticOS-bootstrap` if multiple layers are broken.

### Step 7 — Update `.agentic/GRAPH_INDEX.md` managed section

If `GRAPH_INDEX.md` does not exist, create it with both regions. If it exists, update only the managed region. Preserve the human region byte-for-byte.

Region markers:

```markdown
<!-- agentic:managed:start -->
...managed content...
<!-- agentic:managed:end -->

<!-- human:notes:start -->
...human content preserved as-is...
<!-- human:notes:end -->
```

Managed section template (keep this short; status only, not graph content):

```markdown
## Graph status

- Provider: <understand-anything | codemap | none>
- Graph path: `<configured path>`
- Graph mode available: <yes | no>
- Fallback mode: <none | codemap>
- Last checked: <ISO-8601 UTC>
- Last generated: <ISO-8601 UTC | unknown>
- Parseable: <yes | no>
- Non-empty: <yes | no>
- Sample paths resolve: <hit>/<sample>
- Coverage notes: <one line, or "unknown">
- Known gaps: <one line, or "none">
- Unknowns: <one line, or "none">
```

Human section (created once if missing, never overwritten after that):

```markdown
## Human notes

Routing hints, judgement calls, and provider-specific quirks live here.
```

### Step 8 — Update `agentic.json` graph path if needed

If the chosen graph path differs from `agentic.json.graph.path` (or the field is missing), update only the `graph` block:

- `graph.provider`
- `graph.path`
- `graph.required` (preserve existing value if set; default `true` only if not set)
- `graph.fallback` (preserve existing value if set; default `codemap` only if not set)

Do not modify any other field in `agentic.json`. If the file does not exist, do not create it here — that is `agenticOS-tooling`'s job. Surface the missing config as a blocker.

### Step 9 — Print summary

Use the format in the next section.

## Stop conditions

Stop and ask the user before proceeding when:

- The current directory is not clearly the repo root.
- Understand Anything availability is uncertain or installation method is unclear.
- The graph path is ambiguous (multiple candidates, no clear configured path).
- A graph file appears at the configured path but does not parse.
- Validation fails after generation and the cause is unclear.
- `agentic.json` is missing and the run cannot proceed without it.
- The user has uncommitted changes in `.agentic/GRAPH/` or `.understand-anything/`.

When stopping, state: what was attempted, what blocked progress, and the single recommended next action.

## Final summary format

Print exactly these sections, in order. Keep it under one screen.

```
agenticOS-graph summary
=======================

Mode: <init | refresh | repair | migration>

Provider: <understand-anything | codemap | none>
Graph path: <path or "not configured">
Graph mode available: <yes | no>
Fallback mode: <none | codemap>

Generation:
- Action: <generated | refreshed | reused existing | skipped>
- Last generated: <ISO-8601 UTC | unknown>

Validation:
- Parseable: <yes | no>
- Non-empty: <yes | no>
- Sample paths resolve: <hit>/<sample>
- Errors: <list, or "none">

Files updated:
- .agentic/GRAPH_INDEX.md: <created | managed section updated | unchanged>
- .agentic/CONFIG/agentic.json graph block: <updated | unchanged | not present>

Known gaps:
- <bullet list, or "none">

Unknowns:
- <bullet list, or "none">

Installation blockers:
- <bullet list, or "none">

Next recommended action:
- <single sentence: e.g. "Re-run after installing UA", "Run agenticOS-tooling to create agentic.json", or "Graph is fresh; proceed.">
```

## Non-goals

- Do not write or rewrite `.agentic/PROJECT_BRIEF.md`, `.agentic/MEMORY_INDEX.md`, `.agentic/SUBSYSTEMS/*`, or `.agentic/LESSONS/*`.
- Do not generate or update `scripts/agentic/*` other than reading them to confirm fallback support.
- Do not create or modify the six canonical personal/global skills.
- Do not perform runtime context routing.
- Do not duplicate the graph into Markdown or memory files.
- Do not recreate a giant CODEMAP as the primary structural layer.
- Do not run remote shell installers (curl-pipe-sh, `iwr | iex`) without explicit per-command user approval.
- Do not infer "UA is installed" from anything other than a parseable artifact on disk.
- Do not pick an install path on the user's behalf — present the options for their host and wait.
- Do not overwrite the human section of `GRAPH_INDEX.md`.
