# AGENTS.md

## Overview

This repo is a Python CLI tool (`staker/`) for orchestrating Ethereum staking nodes — managing execution and consensus clients, MEV-boost, snapshots, config, and deployments via Docker on AWS ECS.

## CI Checks

All changes must pass these checks before merging (runs on ubuntu):

```bash
make lint      # ruff check . && ruff format --check .
make cov       # pytest with coverage (threshold enforced)
```

## Running Checks Locally

```bash
make ci DEV=1          # install deps (frozen lockfile, requires uv)
make lint              # lint + format check
make test              # unit tests only
make cov               # unit tests with coverage
make format            # auto-fix lint + format
```

## Project Structure

- `src/staker/` — core CLI module (node orchestration, config, environment, snapshots, MEV-boost, utils)
- `tests/` — pytest unit tests
- `scripts/` — utility scripts (build, deploy, QR codes, DDNS, update)
- `config/` — configuration files
- `pyproject.toml` — project config, dependencies, and tool settings
- `Makefile` — build/test/lint/deploy commands

## Key Conventions

- **Package manager**: `uv` (all commands run via `uv run`)
- **Linter/Formatter**: `ruff`
- **Test runner**: `pytest` with `pytest-xdist` (`-n auto`) and `pytest-cov`
- **Python version**: 3.13
