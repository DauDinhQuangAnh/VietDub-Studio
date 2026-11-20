Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Step($Message) {
    Write-Host "[Start Project] $Message" -ForegroundColor Cyan
}

function Load-EnvFile($Path) {
    if (-not (Test-Path $Path)) {
        Copy-Item (Join-Path $Root ".env.example") $Path
        Write-Step "Created .env from .env.example"
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or $line -notmatch "=") {
            return
        }

        $name, $value = $line -split "=", 2
        $value = $value.Trim()
        if ($value.Length -ge 2 -and $value[0] -eq $value[-1] -and $value[0] -in @('"', "'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name.Trim(), $value, "Process")
    }
}

function Invoke-NativeQuiet($Command) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        & $Command 1>$null 2>$null
        return $LASTEXITCODE
    } catch {
        return 1
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Resolve-PythonExe {
    $pythonLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($pythonLauncher) {
        foreach ($version in @("3.11")) {
            try {
                $candidate = & $pythonLauncher.Source "-$version" -c "import struct, sys; print(sys.executable if sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8 else '')" 2>$null
                if ($LASTEXITCODE -eq 0 -and $candidate) {
                    return ($candidate | Select-Object -Last 1).Trim()
                }
            } catch {
                continue
            }
        }
    }

    $pythonCommand = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        try {
            $candidate = & $pythonCommand.Source -c "import struct, sys; print(sys.executable if sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8 else '')" 2>$null
            if ($LASTEXITCODE -eq 0 -and $candidate) {
                return ($candidate | Select-Object -Last 1).Trim()
            }
        } catch {
            # Microsoft Store aliases can exist on PATH without a Python install.
        }
    }

    throw "Python 3.11 x64 was not found. Install Python 3.11 from python.org, enable Add Python to PATH, then run Start Project.bat again."
}

function Ensure-PythonEnvironment {
    $python = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $basePython = Resolve-PythonExe
        $environmentDir = Join-Path $Root ".venv"
        Write-Step "Creating the project Python environment"
        & $basePython -m venv $environmentDir
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Python's built-in venv module is unavailable; trying virtualenv."
            if (Test-Path $environmentDir) {
                Remove-Item -LiteralPath $environmentDir -Recurse -Force
            }

            if ((Invoke-NativeQuiet { & $basePython -m virtualenv --version }) -ne 0) {
                & $basePython -m pip install --disable-pip-version-check --user virtualenv
                if ($LASTEXITCODE -ne 0) {
                    throw "Could not install virtualenv for $basePython."
                }
            }

            & $basePython -m virtualenv $environmentDir
            if ($LASTEXITCODE -ne 0) {
                throw "Could not create .venv with either venv or virtualenv using $basePython."
            }
        }
    }

    $requirementsHash = (Get-FileHash (Join-Path $Root "requirements.txt") -Algorithm SHA256).Hash
    $hashFile = Join-Path $Root ".venv\requirements.sha256"
    $installedHash = if (Test-Path $hashFile) { (Get-Content $hashFile -Raw).Trim() } else { "" }
    if ($installedHash -ne $requirementsHash) {
        Write-Step "Installing Python packages (first run can take a while)"
        & $python -m pip install --disable-pip-version-check --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            throw "Could not upgrade pip."
        }
        & $python -m pip install --disable-pip-version-check --prefer-binary -r (Join-Path $Root "requirements.txt")
        if ($LASTEXITCODE -ne 0) {
            throw "Python package installation failed. See the error above, fix it, then run Start Project.bat again."
        }
        & $python -m pip install --disable-pip-version-check --no-deps "deepfilternet==0.5.6"
        if ($LASTEXITCODE -ne 0) {
            throw "DeepFilterNet installation failed. See the error above, then run Start Project.bat again."
        }
        Set-Content -Path $hashFile -Value $requirementsHash -Encoding ASCII
    }

    return $python
}

function Ensure-NodeRuntime {
    $systemNpm = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
    if ($systemNpm) {
        $systemNode = Get-Command "node.exe" -ErrorAction SilentlyContinue
        if ($systemNode -and (Test-NodeCompatible $systemNode.Source)) {
            return [pscustomobject]@{ Node = $systemNode.Source; Npm = $systemNpm.Source }
        }
    }

    $toolsDir = Join-Path $Root ".tools\node"
    $localNpm = Get-ChildItem $toolsDir -Filter "npm.cmd" -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { Test-NodeCompatible (Join-Path $_.DirectoryName "node.exe") } |
        Select-Object -First 1
    if ($localNpm) {
        return [pscustomobject]@{
            Node = Join-Path $localNpm.DirectoryName "node.exe"
            Npm = $localNpm.FullName
        }
    }

    $architecture = if ($env:PROCESSOR_ARCHITEW6432) {
        $env:PROCESSOR_ARCHITEW6432
    } else {
        $env:PROCESSOR_ARCHITECTURE
    }
    $nodeArchitecture = switch ($architecture.ToUpperInvariant()) {
        "ARM64" { "arm64" }
        "AMD64" { "x64" }
        default { throw "Unsupported Windows architecture for the bundled Node.js runtime: $architecture" }
    }

    Write-Step "Downloading a portable Node.js runtime for the web interface"
    $releases = Invoke-RestMethod "https://nodejs.org/dist/index.json"
    $release = $releases |
        Where-Object { $_.lts -and $_.files -contains "win-$nodeArchitecture-zip" } |
        Select-Object -First 1
    if (-not $release) {
        throw "Could not find a supported Node.js LTS download for Windows $nodeArchitecture."
    }

    $null = New-Item -ItemType Directory -Force $toolsDir
    $archive = Join-Path $toolsDir "node-$($release.version)-win-$nodeArchitecture.zip"
    $url = "https://nodejs.org/dist/$($release.version)/node-$($release.version)-win-$nodeArchitecture.zip"
    Invoke-WebRequest -Uri $url -OutFile $archive
    Expand-Archive -LiteralPath $archive -DestinationPath $toolsDir -Force
    Remove-Item $archive -Force

    $nodeDir = Join-Path $toolsDir "node-$($release.version)-win-$nodeArchitecture"
    $nodePath = Join-Path $nodeDir "node.exe"
    $npmPath = Join-Path $nodeDir "npm.cmd"
    if (-not (Test-Path $npmPath) -or -not (Test-NodeCompatible $nodePath)) {
        throw "The downloaded Node.js archive did not contain node.exe and npm.cmd."
    }
    return [pscustomobject]@{
        Node = $nodePath
        Npm = $npmPath
    }
}

function Test-NodeCompatible($NodePath) {
    if (-not (Test-Path $NodePath)) {
        return $false
    }
    try {
        $versionText = & $NodePath --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        $version = [Version]($versionText.Trim() -replace "^v", "")
        return $version.Major -ge 20
    } catch {
        return $false
    }
}

function Ensure-FfmpegRuntime {
    $systemFfmpeg = Get-Command "ffmpeg.exe" -ErrorAction SilentlyContinue
    $systemFfprobe = Get-Command "ffprobe.exe" -ErrorAction SilentlyContinue
    if ($systemFfmpeg -and $systemFfprobe) {
        return Split-Path $systemFfmpeg.Source
    }

    $toolsBin = Join-Path $Root ".tools\ffmpeg\bin"
    if ((Test-Path (Join-Path $toolsBin "ffmpeg.exe")) -and (Test-Path (Join-Path $toolsBin "ffprobe.exe"))) {
        return $toolsBin
    }

    Write-Step "Downloading portable FFmpeg (needed to process audio/video)"
    $null = New-Item -ItemType Directory -Force $toolsBin
    $archivePath = Join-Path $Root ".tools\ffmpeg-release-essentials.zip"
    Invoke-WebRequest `
        -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" `
        -OutFile $archivePath

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
    try {
        foreach ($entry in $archive.Entries) {
            if ($entry.FullName -match "(^|/)bin/(ffmpeg|ffprobe)\.exe$") {
                $destination = Join-Path $toolsBin $entry.Name
                $sourceStream = $entry.Open()
                $destinationStream = [System.IO.File]::Create($destination)
                try {
                    $sourceStream.CopyTo($destinationStream)
                } finally {
                    $destinationStream.Dispose()
                    $sourceStream.Dispose()
                }
            }
        }
    } finally {
        $archive.Dispose()
        Remove-Item $archivePath -Force
    }

    if (-not (Test-Path (Join-Path $toolsBin "ffmpeg.exe")) -or -not (Test-Path (Join-Path $toolsBin "ffprobe.exe"))) {
        throw "The FFmpeg download did not contain both ffmpeg.exe and ffprobe.exe."
    }
    return $toolsBin
}

function Start-DockerDesktopIfNeeded {
    $docker = Get-Command "docker.exe" -ErrorAction SilentlyContinue
    if (-not $docker) {
        return $false
    }
    if ((Invoke-NativeQuiet { docker info }) -eq 0) {
        return $true
    }

    $desktopPaths = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Programs\Docker\Docker\Docker Desktop.exe"
    )
    $desktop = $desktopPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $desktop) {
        return $false
    }

    Write-Step "Starting Docker Desktop"
    Start-Process -FilePath $desktop -WindowStyle Hidden
    for ($i = 0; $i -lt 60; $i++) {
        if ((Invoke-NativeQuiet { docker info }) -eq 0) {
            return $true
        }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Wait-DockerService($Service, $Command) {
    for ($i = 0; $i -lt 30; $i++) {
        if ((Invoke-NativeQuiet { docker compose exec -T $Service $Command }) -eq 0) {
            return $true
        }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Get-LocalDatabaseUrl {
    $storageDir = Join-Path $Root "storage"
    $null = New-Item -ItemType Directory -Force $storageDir
    $databasePath = (Join-Path $storageDir "app.db").Replace("\", "/")
    return "sqlite:///$databasePath"
}

function Select-Infrastructure {
    $mode = if ($env:INFRA_MODE) { $env:INFRA_MODE.Trim().ToLowerInvariant() } else { "auto" }
    if ($mode -eq "local") {
        $env:DATABASE_URL = Get-LocalDatabaseUrl
        $env:REDIS_URL = ""
        Write-Step "Using SQLite files in storage/; Docker is not needed"
        return
    }
    if ($mode -eq "custom") {
        if (-not $env:DATABASE_URL) {
            throw "INFRA_MODE=custom requires DATABASE_URL in .env."
        }
        Write-Step "Using the database and queue configured in .env"
        return
    }
    if ($mode -notin @("auto", "docker")) {
        throw "INFRA_MODE must be auto, local, docker, or custom."
    }

    $dockerReady = Start-DockerDesktopIfNeeded
    if ($dockerReady) {
        $composeExitCode = Invoke-NativeQuiet { docker compose up -d postgres redis }
        if ($composeExitCode -eq 0) {
            $postgresReady = Wait-DockerService "postgres" @(
                "pg_isready", "-U", "subtitle_studio", "-d", "subtitle_studio"
            )
            $redisReady = Wait-DockerService "redis" @("redis-cli", "ping")
            if ($postgresReady -and $redisReady) {
                $env:DATABASE_URL = "postgresql+psycopg2://subtitle_studio:subtitle_studio@localhost:15432/subtitle_studio"
                $env:REDIS_URL = "redis://localhost:6379/0"
                Write-Step "Docker is ready; using its PostgreSQL and Redis services"
                return
            }
        }
    }

    if ($mode -eq "docker") {
        throw "Docker was required but its database services could not start. Check Docker Desktop and run Start Project again."
    }

    $env:DATABASE_URL = Get-LocalDatabaseUrl
    $env:REDIS_URL = ""
    Write-Warning "Docker is unavailable; using SQLite database and task queue files in storage/."
}

function Stop-DevProcesses {
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
}

function Start-LoggedProcess($Name, $FilePath, $ArgumentList, $WorkingDirectory) {
    $stdout = Join-Path $Root "$Name.out.log"
    $stderr = Join-Path $Root "$Name.err.log"
    Write-Step "Starting $Name"
    return Start-Process -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -WindowStyle Hidden `
        -PassThru
}

function Wait-HttpReady($Url, $Name, $Process, $ErrorLog) {
    for ($i = 0; $i -lt 40; $i++) {
        if ($Process.HasExited) {
            $details = if (Test-Path $ErrorLog) { Get-Content $ErrorLog -Raw } else { "" }
            throw "$Name stopped during startup. $details"
        }
        try {
            $response = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "$Name did not become ready at $Url."
}

Load-EnvFile (Join-Path $Root ".env")
$env:PYTHONIOENCODING = "utf-8"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$python = Ensure-PythonEnvironment
$nodeRuntime = Ensure-NodeRuntime
$ffmpegBin = Ensure-FfmpegRuntime
$torchLib = Join-Path $Root ".venv\Lib\site-packages\torch\lib"
$ctranslate2Lib = Join-Path $Root ".venv\Lib\site-packages\ctranslate2"
$env:PATH = "$ffmpegBin;$($nodeRuntime.Node | Split-Path);$torchLib;$ctranslate2Lib;$env:PATH"

Select-Infrastructure

Write-Step "Stopping any previous VietDub Studio processes"
Stop-DevProcesses
Start-Sleep -Seconds 1

$webDir = Join-Path $Root "web"
$packageHash = (Get-FileHash (Join-Path $webDir "package-lock.json") -Algorithm SHA256).Hash
$packageHashFile = Join-Path $Root ".tools\web-package-lock.sha256"
$installedPackageHash = if (Test-Path $packageHashFile) { (Get-Content $packageHashFile -Raw).Trim() } else { "" }
if (-not (Test-Path (Join-Path $webDir "node_modules")) -or $installedPackageHash -ne $packageHash) {
    Write-Step "Installing web interface packages"
    & $nodeRuntime.Npm ci --prefix $webDir --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) {
        throw "Web package installation failed."
    }
    $null = New-Item -ItemType Directory -Force (Split-Path $packageHashFile)
    Set-Content -Path $packageHashFile -Value $packageHash -Encoding ASCII
}

foreach ($logName in @("api.out.log", "api.err.log", "celery.out.log", "celery.err.log", "web.out.log", "web.err.log")) {
    Remove-Item (Join-Path $Root $logName) -Force -ErrorAction SilentlyContinue
}
Write-Step "Starting the API and applying database migrations"
$api = Start-LoggedProcess `
    -Name "api" `
    -FilePath $python `
    -ArgumentList @("-m", "uvicorn", "api.main:app", "--host", "localhost", "--port", "8000") `
    -WorkingDirectory $Root
Wait-HttpReady "http://localhost:8000/api/health" "API" $api (Join-Path $Root "api.err.log")

$celery = Start-LoggedProcess `
    -Name "celery" `
    -FilePath $python `
    -ArgumentList @("-m", "celery", "-A", "worker.jobs.celery_app", "worker", "--loglevel=info", "--pool=solo") `
    -WorkingDirectory $Root
$web = Start-LoggedProcess `
    -Name "web" `
    -FilePath $nodeRuntime.Npm `
    -ArgumentList @("run", "dev", "--", "--host", "localhost", "--port", "5173") `
    -WorkingDirectory $webDir
Wait-HttpReady "http://localhost:5173" "Web interface" $web (Join-Path $Root "web.err.log")

Write-Host ""
Write-Host "VietDub Studio is ready: http://localhost:5173" -ForegroundColor Green
Write-Host "Database: $env:DATABASE_URL"
if ($env:REDIS_URL) {
    Write-Host "Task queue: Docker Redis"
} else {
    Write-Host "Task queue: SQLite in storage/"
}
Write-Host "Logs: api.*.log, celery.*.log, web.*.log"
Start-Process "http://localhost:5173"
