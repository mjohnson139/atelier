# Decisions

Product decisions the owner has made, newest first, then the defaults in force until the owner answers the matching item on #5.

## Decided

### 2026-11-16: Public from day one, with a protected `main`
The repository is public. `main` takes changes only through pull requests, merged by squash, with linear history and no force pushes or deletion; merged branches are deleted automatically. The ruleset lives in `.github/rulesets/main.json` so it is reviewable and can be re-imported; the `verify` check becomes required once CI exists (#3, #4).

### 2026-11-16: Labels follow issue titles
The type labels (`epic`, `feat`, `fix`, `chore`, `docs`) are created and applied by `.github/workflows/labels.yml` from each issue's title prefix, so a title and its label never drift apart.

## In force by default

### 2026-11-16: Starting defaults
- Repo name `atelier`; MIT licence.
- Kit in Python 3.12 managed with uv; specs are JSON validated by Pydantic.
- Perspectives are named by role, not given personal names.
- SVG is committed; PNG is generated for `look` and the board.
- v1 runs inside Claude Code (agents + MCP server + skill). The API CLI is v2.
- Models: curator on Opus 5.5 at high effort; perspectives on Sonnet 5.5; `--showcase` promotes a perspective to Fable 5.2 for a final pass; mechanic on Haiku 5.5.
- First subject: Words & Waffles.
