# Script de demarrage de la stack ELK pour Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Demarrage de la stack ELK" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si docker-compose existe
try {
    docker-compose --version > $null 2>&1
} catch {
    Write-Host "ERREUR: docker-compose n'est pas installe" -ForegroundColor Red
    exit 1
}


Write-Host "Creation des repertoires..." -ForegroundColor Blue
New-Item -ItemType Directory -Path logs -Force > $null
New-Item -ItemType Directory -Path logstash/config -Force > $null
New-Item -ItemType Directory -Path logstash/pipeline -Force > $null

Write-Host "Demarrage des services Elasticsearch, Logstash et Kibana..." -ForegroundColor Blue
docker-compose -f docker-compose-elk.yml up -d

Write-Host ""
Write-Host "Attente que les services soient prets..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verifier l'etat des services
Write-Host ""
Write-Host "Verification de l'etat des services..." -ForegroundColor Blue

$elasticsearch_ready = $false
$kibana_ready = $false
$logstash_ready = $false

# Elasticsearch
Write-Host -NoNewline "Elasticsearch: "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "PRET" -ForegroundColor Green
        $elasticsearch_ready = $true
    }
} catch {
    Write-Host "EN ATTENTE" -ForegroundColor Yellow
}

# Kibana
Write-Host -NoNewline "Kibana: "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5601/api/status" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "PRET" -ForegroundColor Green
        $kibana_ready = $true
    }
} catch {
    Write-Host "EN ATTENTE" -ForegroundColor Yellow
}

# Logstash
Write-Host -NoNewline "Logstash: "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9600" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "PRET" -ForegroundColor Green
        $logstash_ready = $true
    }
} catch {
    Write-Host "EN ATTENTE" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ELK Stack en cours d'execution" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services disponibles:" -ForegroundColor Cyan
Write-Host "  - Elasticsearch: http://localhost:9200" -ForegroundColor White
Write-Host "  - Kibana: http://localhost:5601" -ForegroundColor White
Write-Host "  - Logstash: localhost:5000 (TCP/UDP)" -ForegroundColor White
Write-Host ""
Write-Host "Pour arreter: docker-compose -f docker-compose-elk.yml down" -ForegroundColor Yellow
Write-Host ""

# Ouvrir Kibana dans le navigateur
if ($kibana_ready) {
    Write-Host "Ouverture de Kibana..." -ForegroundColor Blue
    Start-Process "http://localhost:5601"
}
