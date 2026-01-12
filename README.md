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
| `Backup.py` | EBS snapshot management for persistence |
| `MEV.py` | Dynamically selects reliable MEV relays |
| `Constants.py` | Configuration and relay lists |
| `Dockerfile` | Container build with Geth, Prysm, MEV-Boost |
| `template.yaml` | CloudFormation stack for AWS infrastructure |

## Prerequisites

- Docker
- AWS CLI (configured with appropriate permissions)
- Python 3.10+

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

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export DEPLOY_ENV=dev
export ETH_ADDR=0xYourAddress

# Run (requires geth, beacon-chain, validator, mev-boost in PATH)
python Staker.py
```

### Docker

```bash
# Build
./scripts/build.sh

# Run
./scripts/run.sh
```

### AWS Deployment

```bash
# Deploy CloudFormation stack
DEPLOY_ENV=prod ./scripts/deploy.sh
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
