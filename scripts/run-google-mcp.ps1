param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ServerUrl
)

$ErrorActionPreference = "Stop"
$clientPath = $env:GOOGLE_OAUTH_CLIENT_JSON
if (-not $clientPath) {
    throw "Set GOOGLE_OAUTH_CLIENT_JSON to the downloaded Google OAuth client JSON path."
}
if (-not (Test-Path -LiteralPath $clientPath)) {
    throw "OAuth client JSON was not found at the configured path."
}

$client = Get-Content -Raw -LiteralPath $clientPath | ConvertFrom-Json
$oauth = if ($client.web) { $client.web } else { $client.installed }
if (-not $oauth.client_id -or -not $oauth.client_secret) {
    throw "OAuth client JSON does not contain client_id and client_secret."
}

$oauthInfo = @{ client_id = $oauth.client_id; client_secret = $oauth.client_secret } | ConvertTo-Json -Compress
& npx -y mcp-remote $ServerUrl --static-oauth-client-info $oauthInfo
exit $LASTEXITCODE
