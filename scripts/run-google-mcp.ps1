param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ServerUrl
)

$ErrorActionPreference = "Stop"
$callbackPort = 33222
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
$tempOAuthPath = Join-Path ([System.IO.Path]::GetTempPath()) ("mcp-oauth-" + [guid]::NewGuid().ToString() + ".json")
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($tempOAuthPath, $oauthInfo, $utf8NoBom)
    & npx -y mcp-remote $ServerUrl $callbackPort ("--static-oauth-client-info") ("@" + $tempOAuthPath)
    exit $LASTEXITCODE
} finally {
    Remove-Item -LiteralPath $tempOAuthPath -Force -ErrorAction SilentlyContinue
}
