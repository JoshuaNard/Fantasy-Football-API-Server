.PHONY: install migrate start check test lint debug-espn debug-pfn

install:
	uv sync
	@printf '\033[95msource .venv/bin/activate\033[0m\n'

migrate:
	uv run python manage.py migrate

start:
	uv run python manage.py runserver

check:
	uv run python manage.py check

test:
	uv run pytest

lint:
	uv run pylint manage.py fantasy_api draft web_scraping tests

debug-espn:
	uv run python -m web_scraping.debug espn

debug-pfn:
	uv run python -m web_scraping.debug pro-football-network
