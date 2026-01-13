#!/bin/bash

set -eu

# Default deploy env for infra code should be dev
DEPLOY_ENV=${DEPLOY_ENV:-dev}
# DRY_RUN=true creates changeset without executing
DRY_RUN=${DRY_RUN:-false}

if [[ "${DEPLOY_ENV}" = "dev" ]]; then
    ParamsFile=dev-parameters.env
else
    ParamsFile=parameters.env
fi

# Build deploy command
DEPLOY_CMD="aws cloudformation deploy \
    --stack-name ECS-${DEPLOY_ENV}-staking-cluster \
    --template-file template.yaml \
    --parameter-overrides $(cat "${ParamsFile}") \
    --capabilities CAPABILITY_NAMED_IAM"

if [[ "${DRY_RUN}" = "true" ]]; then
    echo "🔍 Dry run mode - creating changeset without executing"
    ${DEPLOY_CMD} --no-execute-changeset
    echo "✅ Changeset created. Review in AWS Console before executing."
    exit 0
fi

# Execute full deploy
${DEPLOY_CMD}

# Force new deployment of ECS service
# https://docs.aws.amazon.com/cli/latest/reference/ecs/update-service.html
aws ecs update-service \
    --cluster "${DEPLOY_ENV}-staking-cluster" \
    --service "${DEPLOY_ENV}_staking_service" \
    --task-definition "${DEPLOY_ENV}_eth_staker" \
    --force-new-deployment
