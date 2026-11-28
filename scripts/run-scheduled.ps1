param(
  [Parameter(Mandatory = $true)]
  [string]$Request,
  [string]$OutputDirectory = "data\scheduled-runs"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputPath = Join-Path $OutputDirectory "run-$timestamp.json"
python -m mcp_agent.cli run $Request --json | Out-File -FilePath $outputPath -Encoding utf8
Write-Host "Saved scheduled run to $outputPath"
