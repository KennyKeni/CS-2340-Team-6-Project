.PHONY: reset-db

reset-db:
	@echo "Deleting database and migrations..."
	rm -f db.sqlite3
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	@echo "Creating fresh migrations..."
	uv run python manage.py makemigrations
	@echo "Applying migrations..."
	uv run python manage.py migrate
	@echo "Done!"
