# Contributing

## Local setup

Use Python 3.11 or newer, then install the development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run the checks before opening a change:

```powershell
ruff check .
python -m pytest tests
```

## Integration work

The default tests use local MCP mocks and do not require external credentials.
Live GitHub, Gmail, and Google Drive checks are opt-in through the scripts in
`scripts/` and must never be added to the normal CI workflow with personal
credentials.

## Pull requests

- Keep changes focused and add tests for behavior changes.
- Do not commit `.env` files, OAuth client JSON, tokens, or API keys.
- Explain user-visible behavior and verification results in the pull request.
- Keep commits small enough to review independently.
