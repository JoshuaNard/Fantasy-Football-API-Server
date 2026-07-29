.PHONY: install migrate start check

install:
	python -m pip install -r requirements.txt

migrate:
	python manage.py migrate

start:
	python manage.py runserver

check:
	python manage.py check
