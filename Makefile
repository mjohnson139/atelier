# Every check that must pass before a push. CI runs `make verify` too.
.PHONY: verify lint typecheck test goldens

verify: lint typecheck test

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest

# Re-render every golden SVG after an intended visual change. Review the diff, then commit it.
goldens:
	uv run pytest kit/tests/test_goldens.py --update-goldens
