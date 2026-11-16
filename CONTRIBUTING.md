# Contributing

Thanks for your interest in Atelier. Please read the [code of conduct](CODE_OF_CONDUCT.md) first.

Atelier is early: the concept and process are in place and the drawing kit is being built. The best way to help right now is to try ideas against the [concept](docs/concept.md) and open an issue.

## Run it

Nothing runs yet. Once the scaffold lands (#4) this section will hold the real commands; the plan is:

```sh
uv sync         # install
make verify     # ruff, mypy, pytest (unit + golden images)
make goldens    # re-render golden images after an intended visual change
```

## Hard lines

Pull requests that cross these are closed:

- Rendering that touches the network, or sends a spec, an image or repository content to a third-party host (Kroki, mermaid.ink, hosted PlantUML and the like).
- An image committed without the spec that made it.
- A perspective that writes to the design model. Only the curator does.
- A `sketch` sandbox without a timeout, outside its temp directory, or with network access.
- A secret in the repository.
- A new dependency without a sentence on why it is needed and what it costs.

## Issues

Titles use conventional-commit words, and the label follows from the title: `feat`, `fix`, `chore`, `docs`, and `epic` for a goal that takes several issues. Title it the way you would title the commit: `fix(kit): edge labels overlap in draw_graph`. The templates set the prefix for you.

## Pull requests

- Keep them small and focused, one issue each, and say `Closes #N` in the description.
- Use conventional commit messages: `feat`, `fix`, `docs`, `ci`, `chore`, `refactor` or `test`.
- `make verify` must be green. For a kit change, show before and after images.
- Pull requests are squash-merged into `main`, so the title becomes the commit.

## How agents work here

Most of the work is done by AI agents following [`AGENTS.md`](AGENTS.md) and [`.github/dev-process.md`](.github/dev-process.md). Human contributions follow the same rules.
