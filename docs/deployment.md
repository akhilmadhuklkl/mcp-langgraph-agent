# Deployment Guide

## Local or scheduled execution

Use the PowerShell helpers with the real MCP environment variables configured.
For repeatable local model planning, set `OLLAMA_MODEL` and
`OLLAMA_BASE_URL`, then run `scripts/run-local-model.ps1`.

## Docker

Build and run the image:

```powershell
docker build -t mcp-langgraph-agent .
docker run --rm `
  -e GITHUB_MCP_COMMAND `
  -e GITHUB_PERSONAL_ACCESS_TOKEN `
  -e GMAIL_MCP_COMMAND `
  -e GOOGLE_DRIVE_MCP_COMMAND `
  -e GOOGLE_OAUTH_CLIENT_JSON `
  mcp-langgraph-agent doctor --json
```

Mount a durable directory for SQLite history:

```powershell
docker run --rm `
  -v "${PWD}\data:/app/data" `
  -e MCP_AGENT_DB_PATH=/app/data/agent_runs.db `
  mcp-langgraph-agent metrics --json
```

The image runs as a non-root user and includes an import health check. External
OAuth files and tokens should be injected through a secret manager or runtime
environment, never copied into the image.

## Production checklist

- Use a dedicated service account or least-privilege token for each MCP server.
- Store OAuth client files and tokens in a secret manager.
- Mount persistent storage for `MCP_AGENT_DB_PATH`.
- Keep mutating tools behind the approval workflow.
- Run `doctor --json` as a deployment readiness check.
- Export metrics regularly with `metrics --json` or `metrics --csv`.
