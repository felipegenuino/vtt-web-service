<#
run.ps1 — script para rodar a aplicação no PowerShell (Windows)

Uso:
  .\run.ps1          # cria venv (se necessário), instala deps e roda a app
  .\run.ps1 -Port 5000
#>

param(
    [int]$Port = 5000
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $Root 'venv'

if (-Not (Test-Path $venvPath)) {
    Write-Host "Criando virtualenv..."
    python -m venv $venvPath
    & $venvPath\Scripts\pip.exe install --upgrade pip
    & $venvPath\Scripts\pip.exe install -r (Join-Path $Root 'requirements.txt')
}

Write-Host "Ativando virtualenv..."
. $venvPath\Scripts\Activate.ps1

if (-not $env:OLLAMA_HOST) {
    $env:OLLAMA_HOST = 'http://127.0.0.1:11434'
    Write-Host "Definido OLLAMA_HOST=$env:OLLAMA_HOST"
}

$env:FLASK_APP = 'app.py'
Write-Host "Iniciando Flask (porta $Port)..."
python -m flask run --host=0.0.0.0 --port=$Port
