# CLI

## Build
```
uv sync
uv pip install pyinstaller
<!-- uv run pyinstaller --onefile --name cli ./cli/__main__.py -->
uv run pyinstaller --onefile --name cli --distpath ../dist __main__.py
```

Check out scripts/cli.sh to understand!!