.PHONY: setup lint type test check stack stack-down

setup:        ## install python 3.12 and all dependencies
	uv python install 3.12
	uv sync --all-extras

lint:
	uv run ruff check . && uv run ruff format --check .

type:
	uv run mypy

test:
	uv run pytest -q

check: lint type test

stack:        ## start Postgres and Redis (Phase 1 and 2)
	docker compose -f deploy/docker-compose.yml --profile lite up -d

stack-down:
	docker compose -f deploy/docker-compose.yml --profile lite down
