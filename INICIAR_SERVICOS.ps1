# Script para subir todos os servicos
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  INICIANDO TODOS OS SERVICOS DO PROJETO" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan

$workdir = Get-Location

# === CONFIG ===
# Arquivo de webhook a ser iniciado pela rotina. Altere se quiser outro webhook.
$WEBHOOK_SCRIPT = 'webhook_captura_mensagens.py'  # default: webhook que captura mensagens e responde com IA para o número monitorado

# 1. Evolution API
Write-Host ""
Write-Host "[1/3] Evolution API (Docker)..." -ForegroundColor White
$evolution = docker ps --filter "name=evolution_api" --format "{{.Status}}"
if ($evolution -like "*Up*") {
    Write-Host "      OK - Ja esta rodando" -ForegroundColor Green
} else {
    Write-Host "      Iniciando..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "      OK - Iniciado" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# 2. Webhook de Captura
Write-Host ""
Write-Host "[2/3] Webhook de Captura..." -ForegroundColor White
try {
    $test = Invoke-WebRequest -Uri "http://localhost:8000/status" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "      OK - Ja esta rodando" -ForegroundColor Green
} catch {
    Write-Host "      Iniciando em nova janela..." -ForegroundColor Yellow
    $cmd = "cd '$workdir'; Write-Host 'WEBHOOK DE CAPTURA' -ForegroundColor Cyan; C:/Programas/Scripts/conda.exe run -p C:\Programas --no-capture-output python $WEBHOOK_SCRIPT"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Start-Sleep -Seconds 3
    Write-Host "      OK - Iniciado" -ForegroundColor Green
}

# 3. Localtunnel
Write-Host ""
Write-Host "[3/3] Localtunnel..." -ForegroundColor White
$ltProcess = Get-Process -Name node -ErrorAction SilentlyContinue
if ($ltProcess) {
    Write-Host "      OK - Ja esta rodando" -ForegroundColor Green
} else {
    Write-Host "      Iniciando em nova janela..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'LOCALTUNNEL' -ForegroundColor Cyan; lt --port 8000"
    Start-Sleep -Seconds 3
    Write-Host "      OK - Iniciado" -ForegroundColor Green
    Write-Host ""
    Write-Host "      ATENCAO: Verifique a URL na janela do Localtunnel" -ForegroundColor Yellow
    Write-Host "      Depois execute: .\reconfigurar_webhook.ps1" -ForegroundColor Yellow
}

# Status Final
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  SERVICOS INICIADOS" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Verificando status..." -ForegroundColor White
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Evolution API:" -ForegroundColor Cyan
docker ps --filter "name=evolution_api" --format "   {{.Names}}: {{.Status}}"

Write-Host ""
Write-Host "Webhook:" -ForegroundColor Cyan
try {
    $status = Invoke-WebRequest -Uri "http://localhost:8000/status" -Method GET -TimeoutSec 3 | ConvertFrom-Json
    Write-Host "   Status: Online" -ForegroundColor Green
    Write-Host "   Mensagens capturadas: $($status.mensagens_capturadas)" -ForegroundColor White
} catch {
    Write-Host "   Status: Aguardando inicializacao..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Localtunnel:" -ForegroundColor Cyan
Write-Host "   Verifique a URL na janela aberta" -ForegroundColor White

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Copie a URL do Localtunnel da janela que abriu"
Write-Host "2. Execute: powershell -ExecutionPolicy Bypass .\reconfigurar_webhook.ps1"
Write-Host "3. Teste enviando mensagem de qualquer WhatsApp"
Write-Host ""
