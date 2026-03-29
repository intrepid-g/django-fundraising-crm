.PHONY: help install test lint format migrate run shell clean docker-up docker-down

# Default target
help:
	@echo "Django Fundraising CRM - Available Commands"
	@echo "============================================"
	@echo "make install     - Install dependencies"
	@echo "make migrate     - Run database migrations"
	@echo "make run         - Start development server"
	@echo "make test        - Run test suite"
	@echo "make test-cov    - Run tests with coverage"
	@echo "make lint        - Run linting (flake8)"
	@echo "make format      - Format code with black"
	@echo "make shell       - Open Django shell"
	@echo "make superuser   - Create admin superuser"
	@echo "make clean       - Clean cache and temp files"
	@echo "make docker-up   - Start Docker services"
	@echo "make docker-down - Stop Docker services"
	@echo "make docker-logs - View Docker logs"

# Development setup
install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

run:
	python manage.py runserver

shell:
	python manage.py shell

superuser:
	python manage.py createsuperuser

# Testing
test:
	pytest

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

test-v:
	pytest -v

# Code quality
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format:
	black .

format-check:
	black --check .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-shell:
	docker-compose exec web python manage.py shell

# Production helpers
collectstatic:
	python manage.py collectstatic --noinput

check:
	python manage.py check

check-deploy:
	python manage.py check --deploy
