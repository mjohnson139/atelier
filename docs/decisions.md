# Decisions

Product decisions the owner has made, newest first. Open questions go on an owner-assigned `chore` with the default the work proceeds on, and move here once answered.

## Decided

### 2026-11-16: The starting choices are confirmed
The owner affirmed every default on #5:
- The project is called **Atelier**, licensed MIT.
- The kit is Python 3.12 managed with uv; specs are JSON validated by Pydantic.
- Perspectives are named by role (designer, architect, implementer, tester); personality lives in the profile, not a name.
- SVG is committed; PNG is generated for `look` and the board.
- Models: the curator runs on Opus 5.5 at high effort; perspectives on Sonnet 5.5; `--showcase` puts a perspective on Fable 5.2 for a final pass; the mechanic runs on Haiku 5.5.
- v1 runs inside Claude Code (agents, a local MCP server, the `atelier` skill); the API CLI comes in the headless epic.
- The first subject is Words & Waffles.

### 2026-11-16: Public from day one, with a protected `main`
The repository is public. `main` takes changes only through pull requests, merged by squash, with linear history and no force pushes or deletion; merged branches are deleted automatically. The ruleset lives in `.github/rulesets/main.json` so it is reviewable and can be re-imported; the `verify` check becomes required once CI exists (#3, #4).

### 2026-11-16: Labels follow issue titles
The type labels (`epic`, `feat`, `fix`, `chore`, `docs`) are created and applied by `.github/workflows/labels.yml` from each issue's title prefix, so a title and its label never drift apart.
