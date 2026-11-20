$ErrorActionPreference = "Stop"

$startScript = Join-Path $PSScriptRoot "start_project.ps1"
if (-not (Test-Path $startScript)) {
    throw "Start Project script not found: $startScript"
}

& $startScript
