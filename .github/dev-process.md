# How to work in this repo

Adapted from Words & Waffles. Every session starts from a prompt that names one GitHub issue and should finish it without asking the owner anything that is not a product decision.

## Roles

- **The owner** decides scope, answers product questions, holds every account and secret, and is the only one who merges. An owner comment beats this file and the issue body.
- **The orchestrator** is the session's main model, always Opus at high effort or better. It reads the issue, splits it into units, briefs delegates, reviews, integrates, runs the checks and hands off. It writes code itself only when a brief would take longer than the code, or a delegate failed twice.
- **Delegates** (`implementer`, `mechanic`, `reviewer` in `.claude/agents/`) are cheaper pinned models that do one well-scoped unit each.
- **Perspectives** (`studio-*` in `.claude/agents/`) are the product, not the dev team. They only draw, inside an Atelier session.

## Issues are the queue

Work lives in GitHub issues. Changing the plan or the order is an edit on GitHub, never a PR.

| Type | Use for |
|---|---|
| `epic` | A goal that takes several issues; its ordered sub-issues are the queue. |
| `feat` | New or changed behavior the owner can see (a kit tool, a perspective, a board feature). |
| `fix` | Something is wrong. |
| `chore` | Upkeep: CI, tooling, an owner task, a deferred review finding. |
| `docs` | Documentation only. |

Titles read like the commit that closes them: `feat(kit): draw_state_machine with coverage overlay`. A hard dependency is a `blocked by` relation; a session does not start a blocked issue. Owner-only work is a `chore` assigned to the owner. Open product questions sit on the decisions `chore` (#5) with the default the work proceeds on; answers go into `docs/decisions.md`. Labels are applied from the title prefix by `.github/workflows/labels.yml`, so get the prefix right.

The body of a work issue: `Goal`, `Context`, `Decide in this issue`, `Units`, `Definition of done` (ending with `make verify` green, review answered, a PR that closes the issue), `Not this issue`.

## The shape of a session

1. Read the issue, its comments and its epic, `AGENTS.md`, this file and `docs/concept.md`. Search `docs/solutions/`. Check open PRs; build on an unmerged branch for the same issue rather than redoing it.
2. Set up: `uv sync` at the root.
3. Branch `<type>/<issue-number>-<slug>` from an up-to-date `main` (or the branch the session was given).
4. Do the issue, delegating per `.claude/skills/delegate/SKILL.md`. Commit small, push after every unit, one draft PR saying `Closes #<n>`.
5. Before leaving draft: `make verify` green and a review run and answered.
6. Hand off with `.claude/skills/write-handoff/SKILL.md`.
7. Stop at an owner issue, a blocking product decision, or a failure that survives two honest fixes. Say why on the issue and the PR.

Run contract: the owner merges and makes product calls; everything else proceeds on stated defaults. Never merge, push to `main`, create accounts or add secrets.

## Delegation

| Agent | Model | Use for |
|---|---|---|
| `implementer` | sonnet | One kit tool with its spec model and golden tests; the MCP server; a skill; a workflow. |
| `mechanic` | haiku | Re-rendering goldens, spec fixes, renames, lint fixes, docs from a template. |
| `reviewer` | sonnet | A focused review of a diff. |

One unit, one owner, disjoint files; parallel units use `isolation: "worktree"`; a unit that touches `pyproject.toml` or `uv.lock` runs alone. The brief carries all context. Read the diff, not the report. Escalate after two failures.

## Review

Run the checks, then a `reviewer` over the diff. For a kit change, open the changed golden images and look at them yourself: a drawing that passes its test and is ugly or illegible is a finding. The orchestrator decides which findings are real; a finding kept for later becomes a `chore`.

## Checks

```bash
make verify     # ruff, mypy, pytest (unit + golden images)
make goldens    # re-render golden images after an intended visual change; commit them with the PR
```

## What belongs in a test

Every kit tool is a pure function from a validated spec to SVG. Unit tests cover spec validation and layout maths; golden tests render every spec in `kit/tests/specs/` and compare against committed SVG. Output must be deterministic (fixed fonts, seeded layouts, no timestamps). Perspective behavior is checked by running a session on the Words & Waffles fixture and reviewing the board, not by unit tests.

## Hard lines

Rejected in review no matter who wrote them:
- Any network call while rendering, or a spec or image sent to a third-party host (Kroki, mermaid.ink, hosted PlantUML).
- An image committed without the spec that made it.
- A perspective that writes to `model/`. Only the curator merges model changes.
- `sketch` running without a timeout, outside its temp directory, or with network access.
- A secret in the repo.
- A new dependency without a sentence in the PR on why and what it costs.

## Capture and reuse learnings (Compound Engineering)

Before changing an area, search `docs/solutions/`. After solving something whose reasoning is not recoverable from the code and whose loss would cause a repeat, write one document per problem in `docs/solutions/<category>/<name>.md` with YAML frontmatter, and add it to `docs/solutions/README.md`. If nothing qualifies, say so in the PR.

## Commits and PRs

Conventional commits, small, each leaving verify green, type matching the issue. PR body: `Closes #<n>`, what changed, how it was verified (with before/after images for kit changes), what was delegated, review findings and their disposition.
