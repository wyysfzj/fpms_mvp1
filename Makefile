.PHONY: help dev-backend dev-frontend fmt lint test openapi

help:
	@echo "Targets:"
	@echo "  dev-backend    Run FastAPI with reload (SQLite)"
	@echo "  dev-frontend   Run Vite dev server"
	@echo "  fmt            Format backend (ruff)"
	@echo "  lint           Lint backend (ruff)"
	@echo "  test           Run backend tests (pytest)"
	@echo "  openapi        Export OpenAPI to docs/openapi.json"

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

fmt:
	cd backend && ruff format .

lint:
	cd backend && ruff check .

test:
	cd backend && pytest -q

openapi:
	cd backend && python scripts/export_openapi.py
