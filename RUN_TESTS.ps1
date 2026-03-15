param()

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

function Invoke-ExternalCommand {
    param(
        [string]$WorkingDirectory,
        [string]$CommandPath,
        [string[]]$Arguments
    )

    Push-Location $WorkingDirectory
    try {
        & $CommandPath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "El comando fallo: $CommandPath $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

Write-Step "Validando prerequisitos"
Ensure-Command "npm"

if (-not (Test-Path (Join-Path $backendDir ".venv"))) {
    throw "No se encontro backend/.venv. Ejecuta primero .\RUN_PROJECT.ps1 o prepara el entorno virtual manualmente."
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    throw "No se encontro frontend/node_modules. Instala las dependencias del frontend antes de correr este script."
}

$backendPython = Get-VenvExecutable -BackendDirectory $backendDir -ExecutableName "python.exe"

Write-Step "Ejecutando tests de backend"
Invoke-ExternalCommand -WorkingDirectory $backendDir -CommandPath $backendPython -Arguments @("-m", "pytest")

Write-Step "Ejecutando tests de frontend"
Invoke-ExternalCommand -WorkingDirectory $frontendDir -CommandPath "npm" -Arguments @("run", "test")

Write-Step "Ejecutando typecheck de frontend"
Invoke-ExternalCommand -WorkingDirectory $frontendDir -CommandPath "npm" -Arguments @("run", "typecheck")

Write-Step "Generando build de frontend"
Invoke-ExternalCommand -WorkingDirectory $frontendDir -CommandPath "npm" -Arguments @("run", "build")

Write-Step "Suite completada"
Write-Host "Backend, frontend, typecheck y build finalizaron correctamente." -ForegroundColor Green
