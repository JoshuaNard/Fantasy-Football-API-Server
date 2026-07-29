.PHONY: install migrate start check test

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
