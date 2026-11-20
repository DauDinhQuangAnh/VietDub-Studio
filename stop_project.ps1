Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$infraMode = "auto"
$envLine = Get-Content (Join-Path $Root ".env") -ErrorAction SilentlyContinue |
    Where-Object { $_ -match "^\s*INFRA_MODE\s*=" } |
    Select-Object -First 1
if ($envLine) {
    $infraMode = ($envLine -split "=", 2)[1].Trim().Trim('"').Trim("'").ToLowerInvariant()
}

$allProcesses = @(Get-CimInstance Win32_Process)
$patterns = @(
    "celery -A worker.jobs.celery_app",
    "uvicorn api.main:app",
    "web\node_modules",
    "web/node_modules",
    "npm-cli.js run dev",
    "vite --host localhost --port 5173"
)
$rootPath = $Root.TrimEnd("\", "/")
$rootPathWithForwardSlashes = $rootPath.Replace("\", "/")
$targetIds = @{}
$targets = $allProcesses | Where-Object {
    $commandLine = $_.CommandLine
    if (-not $commandLine) {
        return $false
    }
    if (
        $commandLine.IndexOf($rootPath, [StringComparison]::OrdinalIgnoreCase) -lt 0 -and
        $commandLine.IndexOf($rootPathWithForwardSlashes, [StringComparison]::OrdinalIgnoreCase) -lt 0
    ) {
        return $false
    }
    foreach ($pattern in $patterns) {
        if ($commandLine -like "*$pattern*") {
            return $true
        }
    }
    return $false
}

foreach ($process in $targets) {
    $targetIds[$process.ProcessId] = $true
}
do {
    $changed = $false
    foreach ($process in $allProcesses) {
        if ($targetIds.ContainsKey($process.ParentProcessId) -and -not $targetIds.ContainsKey($process.ProcessId)) {
            $targetIds[$process.ProcessId] = $true
            $changed = $true
        }
    }
} while ($changed)

foreach ($processId in $targetIds.Keys) {
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}

$docker = Get-Command "docker.exe" -ErrorAction SilentlyContinue
if ($docker -and $infraMode -in @("auto", "docker")) {
    $dockerReady = $false
    try {
        & $docker.Source info 1>$null 2>$null
        $dockerReady = $LASTEXITCODE -eq 0
    } catch {
        $dockerReady = $false
    }
    if ($dockerReady) {
        try {
            & $docker.Source compose stop postgres redis 1>$null 2>$null
        } catch {
            Write-Warning "Could not stop the optional Docker database services: $($_.Exception.Message)"
        }
    }
}

foreach ($logName in @("api.out.log", "api.err.log", "celery.out.log", "celery.err.log", "web.out.log", "web.err.log")) {
    Remove-Item (Join-Path $Root $logName) -Force -ErrorAction SilentlyContinue
}
Write-Host "VietDub Studio stopped. Local database and queued jobs were kept."
