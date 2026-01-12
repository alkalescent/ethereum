# Ethereum Staking Node

A complete Ethereum validator infrastructure running **Geth** (execution) + **Prysm** (consensus) + **MEV-Boost** on AWS ECS.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Staker.py                            │
│                   (Process Orchestrator)                    │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│   Geth   │  Beacon  │Validator │MEV-Boost │   VPN (opt)    │
│(Execution)│  Chain   │          │          │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
                           │
                    ┌──────┴──────┐
                    │   AWS ECS   │
                    │  (EC2 Mode) │
                    └─────────────┘
```

## Components

| File | Purpose |
|------|---------|
| `Staker.py` | Main orchestrator - starts/monitors all processes, handles signals |
| `Environment.py` | Runtime abstraction for AWS vs local environments |
| `Backup.py` | EBS snapshot management for persistence |
| `MEV.py` | Dynamically selects reliable MEV relays |
| `Constants.py` | Configuration and relay lists |
| `Dockerfile` | Container build with Geth, Prysm, MEV-Boost |
| `template.yaml` | CloudFormation stack for AWS infrastructure |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker
- AWS CLI (configured with appropriate permissions)
- Python 3.11+

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEPLOY_ENV` | `dev` (Holesky testnet) or `prod` (Mainnet) | ✅ |
| `ETH_ADDR` | Fee recipient address | ✅ |
| `AWS` | Set to `true` when running on AWS | ❌ |
| `DOCKER` | Set to `true` when running in container | ❌ |
| `VPN` | Set to `true` to enable VPN | ❌ |

### Network Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 30303 | TCP/UDP | Geth P2P |
| 13000 | TCP | Prysm P2P |
| 12000 | UDP | Prysm P2P |

## Development

### Install Dependencies

```bash
make install
# or: uv sync --all-groups
```

### Lint

```bash
make lint
# or: uv run ruff check . && uv run ruff format --check .
```

### Format

```bash
make format
# or: uv run ruff check --fix . && uv run ruff format .
```

### Test

```bash
make test
# or: uv run pytest tests/ -v
```

### Build Docker Image

```bash
make build
```

### Run Docker Container

```bash
make run
```

### Stop Container

```bash
make kill
```

### Deploy to AWS

```bash
make deploy
```

## MEV Relays

The node connects to multiple MEV relays for optimal block building:

**Mainnet**: Flashbots, Ultra Sound, bloXroute, Aestus, Agnostic, Eden, Manifold, Titan, Proof, Wenmerge

**Holesky**: Flashbots, Aestus, Ultra Sound, bloXroute

Relays are automatically tested on startup; unreliable ones are filtered out.

## Backup Strategy

- Snapshots created every 30 days
- Maximum 3 snapshots retained (90 days)
- Automatic launch template updates with latest snapshot
- Graceful shutdown triggers snapshot on instance draining

## Version Info

| Component | Version |
|-----------|---------|
| Geth | 1.16.7 |
| Prysm | v7.1.2 |
| MEV-Boost | 1.10.1 |
| Base Image | Ubuntu 24.04 |

## License

Private repository.
