param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Request,
    [string]$GoogleOAuthClientJson = $env:GOOGLE_OAUTH_CLIENT_JSON
)

$ErrorActionPreference = "Stop"

if (-not $GoogleOAuthClientJson -or -not (Test-Path -LiteralPath $GoogleOAuthClientJson)) {
    throw "Provide -GoogleOAuthClientJson with the downloaded Google OAuth client JSON path."
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required for secure GitHub authentication."
}

$githubToken = gh auth token
if (-not $githubToken) {
    throw "Authenticate GitHub first with: gh auth login"
}

$env:GOOGLE_OAUTH_CLIENT_JSON = (Resolve-Path -LiteralPath $GoogleOAuthClientJson).Path
$env:GITHUB_PERSONAL_ACCESS_TOKEN = $githubToken
$env:GITHUB_MCP_COMMAND = "docker"
$env:GITHUB_MCP_ARGS = "run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server stdio"
$env:GMAIL_MCP_COMMAND = "powershell"
$env:GMAIL_MCP_ARGS = "-ExecutionPolicy Bypass -File scripts/run-google-mcp.ps1 https://gmailmcp.googleapis.com/mcp/v1"
$env:GOOGLE_DRIVE_MCP_COMMAND = "powershell"
$env:GOOGLE_DRIVE_MCP_ARGS = "-ExecutionPolicy Bypass -File scripts/run-google-mcp.ps1 https://drivemcp.googleapis.com/mcp/v1"

python -m mcp_agent.cli run $Request
