#!/bin/bash

set -eu
source config.env

docker build \
    -t ethereum \
    --network=host \
    --build-arg DEPLOY_ENV=prod \
    --build-arg ARCH=amd64 \
    --build-arg \
    VPN=true \
    .
