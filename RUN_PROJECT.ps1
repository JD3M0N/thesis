param(
    [switch]$ReinstallDependencies,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-VenvExecutable {
    param(
        [string]$BackendDirectory,
        [string]$ExecutableName
    )

    $scriptsPath = Join-Path $BackendDirectory ".venv\Scripts\$ExecutableName"
    if (Test-Path $scriptsPath) {
        return $scriptsPath
    }

    $binPath = Join-Path $BackendDirectory ".venv\bin\$ExecutableName"
    if (Test-Path $binPath) {
        return $binPath
    }

    throw "No se encontro $ExecutableName dentro del entorno virtual en $BackendDirectory\.venv"
}

function Ensure-Command {
    param([string]$CommandName)

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "No se encontro el comando requerido: $CommandName"
    }
}

function Ensure-FileFromExample {
    param(
        [string]$TargetPath,
        [string]$ExamplePath
    )

    if (-not (Test-Path $TargetPath)) {
        Copy-Item $ExamplePath $TargetPath
        Write-Host "Creado $TargetPath a partir de $ExamplePath" -ForegroundColor Yellow
    }
}

function Get-EnvValue {
    param(
        [string]$FilePath,
        [string]$Key
    )

    $prefix = "$Key="
    $line = Get-Content $FilePath | Where-Object { $_.StartsWith($prefix) } | Select-Object -First 1
    if (-not $line) {
        return ""
    }

    return $line.Substring($prefix.Length).Trim()
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$backendEnv = Join-Path $backendDir ".env"
$backendEnvExample = Join-Path $backendDir ".env.example"
$frontendEnv = Join-Path $frontendDir ".env.local"
$frontendEnvExample = Join-Path $frontendDir ".env.example"
$requirementsFile = Join-Path $root "requirements.txt"

Write-Step "Validando herramientas base"
Ensure-Command "python"
Ensure-Command "npm"

Write-Step "Preparando archivos de entorno"
Ensure-FileFromExample -TargetPath $backendEnv -ExamplePath $backendEnvExample
Ensure-FileFromExample -TargetPath $frontendEnv -ExamplePath $frontendEnvExample

$geminiApiKey = Get-EnvValue -FilePath $backendEnv -Key "GEMINI_API_KEY"
if ([string]::IsNullOrWhiteSpace($geminiApiKey)) {
    throw "Falta GEMINI_API_KEY en backend/.env. Edita ese archivo y vuelve a ejecutar el script."
}

Write-Step "Preparando entorno virtual del backend"
if (-not (Test-Path (Join-Path $backendDir ".venv"))) {
    & python -m venv (Join-Path $backendDir ".venv")
}

$backendPython = Get-VenvExecutable -BackendDirectory $backendDir -ExecutableName "python.exe"
$backendPip = Get-VenvExecutable -BackendDirectory $backendDir -ExecutableName "pip.exe"

$mustInstallBackend = $ReinstallDependencies.IsPresent -or -not (Test-Path (Join-Path $backendDir ".venv\installation.marker"))
if ($mustInstallBackend) {
    Write-Step "Instalando dependencias del backend"
    & $backendPip install -r $requirementsFile
    & $backendPip install -e $backendDir
    New-Item -ItemType File -Path (Join-Path $backendDir ".venv\installation.marker") -Force | Out-Null
}

$mustInstallFrontend = $ReinstallDependencies.IsPresent -or -not (Test-Path (Join-Path $frontendDir "node_modules"))
if ($mustInstallFrontend) {
    Write-Step "Instalando dependencias del frontend"
    Push-Location $frontendDir
    try {
        & npm install
    }
    finally {
        Pop-Location
    }
}

Write-Step "Levantando backend en una nueva terminal"
$backendCommand = "& '$backendPython' -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell.exe -WorkingDirectory $backendDir -ArgumentList @(
    "-NoExit",
    "-Command",
    $backendCommand
)

Write-Step "Levantando frontend en una nueva terminal"
Start-Process powershell.exe -WorkingDirectory $frontendDir -ArgumentList @(
    "-NoExit",
    "-Command",
    "npm run dev"
)

if ($OpenBrowser) {
    Write-Step "Abriendo el navegador"
    Start-Process "http://localhost:3000"
}

Write-Step "Proyecto montado"
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Si cambias dependencias, vuelve a ejecutar con -ReinstallDependencies." -ForegroundColor DarkGray
