.PHONY: help setup backend-setup frontend-setup db-init test clean docker-up docker-down

help:
	@echo "Intelli-Credit Development Commands"
	@echo "===================================="
	@echo "make setup          - Set up both backend and frontend"
	@echo "make backend-setup  - Set up backend environment"
	@echo "make frontend-setup - Set up frontend environment"
	@echo "make db-init        - Initialize database"
	@echo "make test           - Run all tests"
	@echo "make clean          - Clean build artifacts"
	@echo "make docker-up      - Start all services with Docker"
	@echo "make docker-down    - Stop all Docker services"

setup: backend-setup frontend-setup

backend-setup:
	@echo "Setting up backend..."
	cd backend && python -m venv venv
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	cd backend && cp .env.example .env
	@echo "Backend setup complete!"

frontend-setup:
	@echo "Setting up frontend..."
	cd frontend && npm install
	cd frontend && cp .env.example .env
	@echo "Frontend setup complete!"

db-init:
	@echo "Initializing database..."
	psql -U postgres -c "CREATE DATABASE intellicredit;" || true
	psql -U postgres -d intellicredit -f backend/app/db/schema.sql
	@echo "Database initialized!"

test:
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "All tests complete!"

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/node_modules/.cache
	@echo "Clean complete!"

docker-up:
	@echo "Starting services with Docker..."
	docker-compose up -d
	@echo "Services started! Backend: http://localhost:8000, Frontend: http://localhost:3000"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "Services stopped!"
