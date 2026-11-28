param(
  [string]$Request = "Search Gmail for MCP and find matching Drive files"
)

$ErrorActionPreference = "Stop"

Write-Host "== Readiness ==" -ForegroundColor Cyan
python -m mcp_agent.cli doctor

Write-Host "`n== Tool catalog ==" -ForegroundColor Cyan
python -m mcp_agent.cli catalog

Write-Host "`n== Plan preview ==" -ForegroundColor Cyan
python -m mcp_agent.cli plan $Request

Write-Host "`n== Local run ==" -ForegroundColor Cyan
python -m mcp_agent.cli run $Request

Write-Host "`n== Persisted metrics ==" -ForegroundColor Cyan
python -m mcp_agent.cli metrics --json
