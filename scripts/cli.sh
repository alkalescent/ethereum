#!/bin/bash

set -eu
cd cli
# prefer the repository-local venv (cli/.venv) if present, otherwise use `uv run`
SITE_PACKAGES=""
if [ -x ".venv/bin/python3" ]; then
	PYTHON_BIN=".venv/bin/python3"
	SITE_PACKAGES=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_path('purelib'))")
else
	PYTHON_BIN="$(which python3 2>/dev/null || true)"
	SITE_PACKAGES=$(uv run python3 -c "import site; print(site.USER_SITE)")
fi
echo "Using python: $PYTHON_BIN"
echo "User site-packages directory: $SITE_PACKAGES"
# python3 -m PyInstaller --name cli --onefile cli/__main__.py --add-data="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt:./shamir_mnemonic"