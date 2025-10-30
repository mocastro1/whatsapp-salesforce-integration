# Script para configurar webhook no Evolution API
$body = @{
    webhook = @{
        enabled = $true
        url = "https://twelve-knives-strive.loca.lt/webhook"
        webhook_by_events = $false
        webhook_base64 = $false
        events = @(
            "MESSAGES_UPSERT"
        )
    }
} | ConvertTo-Json -Depth 10

Write-Host "Configurando webhook..." -ForegroundColor Yellow
Write-Host "URL: https://twelve-knives-strive.loca.lt/webhook" -ForegroundColor Cyan

$response = Invoke-WebRequest `
    -Uri "http://localhost:3001/webhook/set/salesforce-bot" `
    -Headers @{"apikey"="evolution_api_key_2025"} `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host "`n✅ Webhook configurado!" -ForegroundColor Green
Write-Host "`nResposta:" -ForegroundColor Yellow
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
