# Pegar URL do localtunnel e configurar webhook
Write-Host "Aguardando localtunnel gerar URL..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Tentar obter URL do status
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/status" -Method GET -ErrorAction Stop
    Write-Host "✅ Webhook local OK" -ForegroundColor Green
    
    Write-Host "`n⚠️ ATENÇÃO: Verifique a URL do localtunnel na janela que abriu" -ForegroundColor Yellow
    Write-Host "A URL deve ser algo como: https://xxxxx-xxxxx-xxxxx.loca.lt" -ForegroundColor Cyan
    Write-Host "`nDigite a URL completa do localtunnel:" -ForegroundColor Yellow
    $url = Read-Host
    
    if ($url -match "https://.*\.loca\.lt") {
        Write-Host "`nConfigurando webhook com URL: $url/webhook" -ForegroundColor Cyan
        
        $body = @{
            webhook = @{
                enabled = $true
                url = "$url/webhook"
                webhook_by_events = $false
                webhook_base64 = $false
                events = @("MESSAGES_UPSERT")
            }
        } | ConvertTo-Json -Depth 10
        
        $webhookResponse = Invoke-WebRequest `
            -Uri "http://localhost:3001/webhook/set/salesforce-bot" `
            -Headers @{"apikey"="evolution_api_key_2025"} `
            -Method POST `
            -Body $body `
            -ContentType "application/json"
        
        Write-Host "`n✅ Webhook configurado com sucesso!" -ForegroundColor Green
        $webhookResponse.Content | ConvertFrom-Json | ConvertTo-Json
        
    } else {
        Write-Host "`n❌ URL inválida!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
}
