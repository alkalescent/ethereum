#!/bin/bash

set -eu

# Checkpoint sync hosts (ChainSafe/Lodestar - consistent provider for both networks)
# Hoodi: https://beaconstate-hoodi.chainsafe.io
# Mainnet: https://beaconstate-mainnet.chainsafe.io

# Default deploy env for app code should be prod
DEPLOY_ENV="${DEPLOY_ENV:-prod}"

if [[ "${DEPLOY_ENV}" = "dev" ]]
then
    NODE_HOST="https://beaconstate-hoodi.chainsafe.io"
    curl -LO https://github.com/eth-clients/hoodi/raw/main/metadata/genesis.ssz
else
    NODE_HOST="https://beaconstate-mainnet.chainsafe.io"
fi

# Download checkpoint state and block directly via beacon API
# This bypasses prysmctl which has issues with post-Fusaka (Fulu fork) format
echo "Downloading checkpoint state from ${NODE_HOST}..."
curl -H "Accept: application/octet-stream" -o state.ssz "${NODE_HOST}/eth/v2/debug/beacon/states/finalized"

echo "Downloading checkpoint block from ${NODE_HOST}..."
curl -H "Accept: application/octet-stream" -o block.ssz "${NODE_HOST}/eth/v2/beacon/blocks/finalized"

echo "Checkpoint files downloaded:"
ls -la *.ssz
