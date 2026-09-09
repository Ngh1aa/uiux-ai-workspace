param([switch]$Foreground)
$ErrorActionPreference = "Stop"
$FactoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$FactoryPython = Join-Path $FactoryRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $FactoryPython)) { throw "Missing Factory .venv Python at $FactoryPython" }

# 1. Bridge (port 8788)
$BridgeListener = Get-NetTCPConnection -State Listen -LocalPort 8788 -ErrorAction SilentlyContinue
if ($BridgeListener) {
    Write-Host "Bridge (8788) already running."
} else {
    $BridgeScript = Join-Path $FactoryRoot "apps\bridge\server.py"
    Start-Process -FilePath $FactoryPython -ArgumentList '-u', ('"' + $BridgeScript + '"') -WorkingDirectory $FactoryRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $FactoryRoot ".bridge-start.stdout.log") -RedirectStandardError (Join-Path $FactoryRoot ".bridge-start.stderr.log") | Out-Null
    Write-Host "Bridge started in background. Logs: .bridge-start.*.log"
}

# 2. Console (port 5174 mặc định, khác với Bolt.diy ở 5173)
$ConsolePort = if ($env:UIUX_CONSOLE_PORT) { [int]$env:UIUX_CONSOLE_PORT } else { 5174 }
$ConsoleListener = Get-NetTCPConnection -State Listen -LocalPort $ConsolePort -ErrorAction SilentlyContinue
if ($ConsoleListener) {
    Write-Host "Console ($ConsolePort) already running."
    $Opened = $true
} else {
    $ConsoleScript = Join-Path $FactoryRoot "apps\web\server.py"
    if ($Foreground) {
        Write-Host "Starting console in foreground on $ConsolePort…"
        Push-Location $FactoryRoot
        try { & $FactoryPython '-u', $ConsoleScript } finally { Pop-Location }
        return
    } else {
        Start-Process -FilePath $FactoryPython -ArgumentList '-u', ('"' + $ConsoleScript + '"') -WorkingDirectory $FactoryRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $FactoryRoot ".console-start.stdout.log") -RedirectStandardError (Join-Path $FactoryRoot ".console-start.stderr.log") | Out-Null
        Write-Host "Console started in background. Logs: .console-start.*.log"
        $Opened = $true
    }
}

# 3. Wait briefly for ports, then report health
Start-Sleep -Seconds 1
try {
    $Bridge = Invoke-RestMethod -Uri "http://127.0.0.1:8788/health" -TimeoutSec 5
    Write-Host "Bridge healthy: $( $Bridge.status )" -ForegroundColor Green
} catch {
    Write-Host "Bridge chưa sẵn sàng: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Workbench Console: http://localhost:$ConsolePort/" -ForegroundColor Cyan
Write-Host "Bridge API (raw):  http://localhost:8788/health" -ForegroundColor DarkCyan
