# syntax=docker/dockerfile:1

# =============================================================================
# BASE STAGE - Common setup for all stages
# =============================================================================
FROM ubuntu:24.04 AS base

# Configure env vars
ARG DEPLOY_ENV
ARG VERSION
ARG ARCH
ARG VPN
ENV DEPLOY_ENV "${DEPLOY_ENV:-prod}"
ENV VERSION "${VERSION}"
ENV ARCH "${ARCH:-arm64}"
ENV VPN "${VPN:-false}"

ENV ETH_DIR "${HOME}/ethereum"
ENV EXEC_DIR "${ETH_DIR}/execution"
ENV EXTRA_DIR_BASE "/extra"
ENV EXTRA_DIR "${ETH_DIR}${EXTRA_DIR_BASE}"
ENV PRYSM_DIR_BASE "/consensus/prysm"
ENV PRYSM_DIR "${ETH_DIR}${PRYSM_DIR_BASE}"

# Install deps
RUN apt-get update && \
    apt-get install -y python3 git curl bash make

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR "${ETH_DIR}"

# =============================================================================
# TEST STAGE - Run lint and coverage checks
# =============================================================================
FROM base AS test

# Copy project files needed for testing
COPY pyproject.toml uv.lock Makefile ./
COPY src/ src/
COPY tests/ tests/

# Install dependencies and run checks using Makefile
RUN make ci
RUN make lint
RUN make cov

# Create a marker file to prove tests passed
RUN touch /tmp/.tests_passed

# =============================================================================
# DEPLOY STAGE - Runtime image (can be targeted directly to skip tests)
# =============================================================================
FROM base AS deploy

# Install Python dependencies (runtime only)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Download geth (execution)
RUN mkdir -p "${EXEC_DIR}"
WORKDIR "${EXEC_DIR}"
ENV PLATFORM_ARCH "linux-${ARCH}"
ENV GETH_VERSION 1.16.7-b9f3a3d9
ENV GETH_ARCHIVE "geth-${PLATFORM_ARCH}-${GETH_VERSION}"
RUN curl -LO "https://gethstore.blob.core.windows.net/builds/${GETH_ARCHIVE}.tar.gz"
RUN tar -xvzf "${GETH_ARCHIVE}.tar.gz"
RUN mv "${GETH_ARCHIVE}/geth" . && rm -rf "${GETH_ARCHIVE}"

RUN chmod +x geth
# Add geth to path
ENV PATH "${PATH}:${EXEC_DIR}"

# Download prysm (consensus)
RUN mkdir -p "${PRYSM_DIR}"
WORKDIR "${PRYSM_DIR}"
ENV PRYSM_VERSION v7.1.2
RUN if [ "$ARCH" = "amd64" ]; \
    then export PRYSM_PLATFORM_ARCH="modern-${PLATFORM_ARCH}"; \
    else export PRYSM_PLATFORM_ARCH="${PLATFORM_ARCH}"; \
    fi; \
    echo $PRYSM_PLATFORM_ARCH; \
    curl -Lo beacon-chain "https://github.com/prysmaticlabs/prysm/releases/download/${PRYSM_VERSION}/beacon-chain-${PRYSM_VERSION}-${PRYSM_PLATFORM_ARCH}"; \
    curl -Lo validator "https://github.com/prysmaticlabs/prysm/releases/download/${PRYSM_VERSION}/validator-${PRYSM_VERSION}-${PLATFORM_ARCH}"; \
    curl -Lo prysmctl "https://github.com/prysmaticlabs/prysm/releases/download/${PRYSM_VERSION}/prysmctl-${PRYSM_VERSION}-${PLATFORM_ARCH}"; \
    curl -Lo client-stats "https://github.com/prysmaticlabs/prysm/releases/download/${PRYSM_VERSION}/client-stats-${PRYSM_VERSION}-${PLATFORM_ARCH}";

RUN chmod +x beacon-chain validator prysmctl client-stats
# Add prysm to path
ENV PATH "${PATH}:${PRYSM_DIR}"

# Download consensus snapshot
COPY ".${PRYSM_DIR_BASE}/download_checkpoint.sh" .
RUN bash download_checkpoint.sh

# Download mev-boost (extra)
RUN mkdir -p "${EXTRA_DIR}"
WORKDIR "${EXTRA_DIR}"

ENV MEV_VERSION 1.10.1
ENV MEV_ARCHIVE "mev-boost_${MEV_VERSION}_linux_${ARCH}"

RUN curl -LO "https://github.com/flashbots/mev-boost/releases/download/v${MEV_VERSION}/${MEV_ARCHIVE}.tar.gz"
RUN tar -xvzf "${MEV_ARCHIVE}.tar.gz"
RUN chmod +x mev-boost

# Add extra to path
ENV PATH "${PATH}:${EXTRA_DIR}"

# Run app
WORKDIR "${ETH_DIR}"
COPY vpn vpn
RUN bash vpn/setup.sh

COPY src/staker src/staker
ENV PYTHONPATH="${ETH_DIR}/src"
EXPOSE 30303/tcp 30303/udp 13000/tcp 12000/udp
ENTRYPOINT ["python3", "-m", "staker.node"]

# =============================================================================
# DEFAULT STAGE - Ensures tests pass before deploy
# =============================================================================
FROM deploy AS default

# This COPY creates a dependency on the test stage
# Build will fail if tests didn't pass
COPY --from=test /tmp/.tests_passed /tmp/.tests_passed
