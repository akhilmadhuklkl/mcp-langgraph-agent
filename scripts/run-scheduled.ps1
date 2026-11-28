param(
  [Parameter(Mandatory = $true)]
  [string]$Request,
  [string]$OutputDirectory = "data\scheduled-runs",
  [switch]$Model
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputPath = Join-Path $OutputDirectory "run-$timestamp.json"
$modelArgument = if ($Model) { "--model" } else { $null }
python -m mcp_agent.cli run $Request --json $modelArgument | Out-File -FilePath $outputPath -Encoding utf8
Write-Host "Saved scheduled run to $outputPath"
