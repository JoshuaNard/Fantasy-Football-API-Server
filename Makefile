.PHONY: install migrate start check test lint debug-draftkings debug-espn debug-fanduel debug-kalshi debug-pfn debug-vegas

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

debug-draftkings:
	uv run python -m web_scraping.debug draftkings

debug-espn:
	uv run python -m web_scraping.debug espn

debug-fanduel:
	uv run python -m web_scraping.debug fanduel

debug-kalshi:
	uv run python -m web_scraping.debug kalshi

debug-vegas:
	uv run python -m web_scraping.debug_vegas

debug-pfn:
	uv run python -m web_scraping.debug pro-football-network
