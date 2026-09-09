param([switch]$Foreground)
$ErrorActionPreference = "Stop"
$FactoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BoltRoot = Join-Path (Split-Path $FactoryRoot) "bolt.diy"
$FactoryPython = Join-Path $FactoryRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $FactoryPython)) { throw "Missing Factory .venv Python." }
if (-not (Test-Path -LiteralPath $BoltRoot)) { throw "Missing bolt.diy sibling repository." }
if (-not (Get-Command npx.cmd -ErrorAction SilentlyContinue)) { throw "Node.js/npm is required." }

if (-not (Test-Path -LiteralPath (Join-Path $BoltRoot "node_modules"))) {
    Push-Location $BoltRoot
    try {
        & npx.cmd --yes pnpm@9.14.4 install --frozen-lockfile
        if ($LASTEXITCODE -ne 0) { throw "Bolt dependency install failed." }
    } finally { Pop-Location }
}

$BridgeListener = Get-NetTCPConnection -State Listen -LocalPort 8788 -ErrorAction SilentlyContinue
if ($BridgeListener) {
    $BridgeHealth = Invoke-RestMethod -Uri "http://127.0.0.1:8788/health" -TimeoutSec 10
    if ($BridgeHealth.root -ne $FactoryRoot) { throw "Port 8788 belongs to a different service." }
    Write-Host "Factory bridge is already running."
} else {
    $BridgeScript = Join-Path $FactoryRoot "apps\bridge\server.py"
    Start-Process -FilePath $FactoryPython -ArgumentList '-u', ('"' + $BridgeScript + '"') -WorkingDirectory $FactoryRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $FactoryRoot ".bridge-start.stdout.log") -RedirectStandardError (Join-Path $FactoryRoot ".bridge-start.stderr.log") | Out-Null
    Write-Host "Factory bridge started in background."
}

$BoltListener = Get-NetTCPConnection -State Listen -LocalPort 5173 -ErrorAction SilentlyContinue
if ($BoltListener) {
    $BoltProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($BoltListener[0].OwningProcess)"
    if ($BoltProcess.CommandLine -notlike "*$BoltRoot*") { throw "Port 5173 belongs to another process; it was not stopped." }
    Write-Host "Workbench is already running."
} elseif ($Foreground) {
    Push-Location $BoltRoot
    try {
        & npx.cmd --yes pnpm@9.14.4 dev --host 127.0.0.1
        if ($LASTEXITCODE -ne 0) { throw "Bolt dev server exited with code $LASTEXITCODE" }
    } finally { Pop-Location }
} else {
    Start-Process powershell -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', 'npx.cmd --yes pnpm@9.14.4 dev --host 127.0.0.1' -WorkingDirectory $BoltRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $BoltRoot ".workbench-start.stdout.log") -RedirectStandardError (Join-Path $BoltRoot ".workbench-start.stderr.log") | Out-Null
    Write-Host "Workbench started in background. Logs: bolt.diy/.workbench-start.*.log"
}
Write-Host "Open http://localhost:5173/uiux after the dev server reports ready." -ForegroundColor Green
