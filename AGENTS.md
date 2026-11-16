# Agent instructions

Atelier: a studio of AI perspectives (designer, architect, implementer, tester) that draw software designs with a local Python drawing kit, look at what they drew, revise, and argue. A curator runs each session. `kit/` is the drawing kit and its MCP server; `.claude/agents/studio-*.md` are the perspectives; `.claude/skills/atelier/` runs a session.

- **The queue is GitHub issues.** Epics hold sub-issues; the sub-issue order is the order of work. Titles and labels use `epic`, `feat`, `fix`, `chore`, `docs`. Details: `.github/dev-process.md`.
- **Every session starts with a prompt that names one issue:** `Work on mjohnson139/atelier#<n>: check out main, read the issue and AGENTS.md, and do it.`
- **End every issue by handing it off:** `.claude/skills/write-handoff/SKILL.md`.
- **Scope:** the issue and its epic. The concept is `docs/concept.md`; decisions and their defaults are in `docs/decisions.md`.
- **Delegate:** the orchestrator is always Opus at high effort or better, and owns design, planning, judgment and review. Well-scoped units go to `implementer` (sonnet), `mechanic` (haiku) or `reviewer` (sonnet) with a brief from `.claude/skills/delegate/SKILL.md`. Do not confuse these with the `studio-*` perspectives, which only draw.
- **Run hands-off:** implement, review, open the PR and babysit CI without asking. The owner merges and makes product calls.
- **Before every push:** `make verify` (ruff, mypy, pytest, golden images). Every PR body says `Closes #<n>`.
- **Never:** merge, push to `main`, add a secret, send a spec or image to a third-party host (no Kroki, mermaid.ink or hosted renderers), or commit an image without the spec that made it.
