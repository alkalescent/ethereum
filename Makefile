.PHONY: install lint test build run deploy clean

# Install dependencies
install:
	uv sync --all-groups

# Run linting
lint:
	uv run ruff check .
	uv run ruff format --check .

# Format code
format:
	uv run ruff check --fix .
	uv run ruff format .

# Run tests
test:
	uv run pytest tests/ -v

# Build Docker image
build:
	docker build -t eth-staker --build-arg DEPLOY_ENV=$(DEPLOY_ENV) --build-arg ARCH=$(ARCH) .

# Run locally (requires DEPLOY_ENV and ETH_ADDR)
run:
	uv run python Staker.py

# Deploy to AWS
deploy:
	./scripts/deploy.sh

# Clean build artifacts
clean:
	rm -rf .venv .pytest_cache __pycache__ .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
