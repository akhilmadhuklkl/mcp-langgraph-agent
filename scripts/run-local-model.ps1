param(
  [Parameter(Mandatory = $true)]
  [string]$Request,
  [string]$Model = "llama3.2:3b",
  [string]$BaseUrl = "http://127.0.0.1:11434/v1",
  [switch]$Json
)

$ErrorActionPreference = "Stop"
$env:OLLAMA_MODEL = $Model
$env:OLLAMA_BASE_URL = $BaseUrl

$jsonArgument = if ($Json) { "--json" } else { $null }
python -m mcp_agent.cli run $Request --model $jsonArgument
