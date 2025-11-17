# Script de synchronisation ETL automatique pour Windows PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ETL SYNCHRONISATION AUTOMATIQUE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Date debut: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# ===== VERIFICATIONS PREALABLES =====
Write-Host "Verification de la structure..." -ForegroundColor Blue

if (-Not (Test-Path "docker-compose.yml")) {
    Write-Host "ERREUR: docker-compose.yml non trouve" -ForegroundColor Red
    exit 1
}

Write-Host "Structure OK" -ForegroundColor Green
Write-Host ""

# ===== DEMARRER LES SERVICES =====
Write-Host "Demarrage des services Docker..." -ForegroundColor Blue
docker-compose up -d
docker-compose -f docker-compose-dwh.yml up -d

Write-Host "Services demarres" -ForegroundColor Green
Write-Host ""

# ===== ATTENDRE QUE HDFS SOIT PRET =====
Write-Host "Attente que HDFS soit accessible..." -ForegroundColor Yellow

$hdfs_ready = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $result = docker exec datalake-namenode hdfs dfs -ls / 2>$null
        if ($?) {
            Write-Host "HDFS accessible" -ForegroundColor Green
            $hdfs_ready = $true
            break
        }
    } catch {
        # Continue
    }
    
    Write-Host "Tentative $i/30..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

if (-Not $hdfs_ready) {
    Write-Host "ERREUR: HDFS non accessible apres 30 tentatives" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ===== RELANCER L'ETL DATA LAKE =====
Write-Host "Relancement ETL Data Lake..." -ForegroundColor Blue
docker restart datalake-etl
Start-Sleep -Seconds 40

Write-Host ""
Write-Host "Logs ETL Data Lake:" -ForegroundColor Cyan
docker logs datalake-etl --tail 10

Write-Host ""

# ===== RELANCER L'ETL DWH =====
Write-Host "Relancement ETL Data Warehouse..." -ForegroundColor Blue
docker restart etl-dwh
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Logs ETL DWH:" -ForegroundColor Cyan
docker logs etl-dwh --tail 10

Write-Host ""

# ===== VERIFIER LES DONNEES =====
Write-Host "Verification des donnees..." -ForegroundColor Blue
Write-Host ""

try {
    $patients = docker exec datawarehouse psql -U dwh_user -d datawarehouse -t -c "SELECT COUNT(*) FROM staging.stg_patients;" 2>$null | ForEach-Object { $_.Trim() }
    $tests = docker exec datawarehouse psql -U dwh_user -d datawarehouse -t -c "SELECT COUNT(*) FROM staging.stg_medical_tests;" 2>$null | ForEach-Object { $_.Trim() }
    
    Write-Host "   Patients: $patients" -ForegroundColor Green
    Write-Host "   Tests Medicaux: $tests" -ForegroundColor Green
} catch {
    Write-Host "   Impossible de verifier les donnees" -ForegroundColor Yellow
}

# ===== RESUME FINAL =====
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SYNCHRONISATION ETL REUSSIE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Date fin: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Donnees disponibles sur: http://localhost:3000 (Metabase)" -ForegroundColor Cyan
Write-Host "PostgreSQL: localhost:5432 (dwh_user / dwh_password)" -ForegroundColor Cyan
Write-Host "HDFS: http://localhost:9871" -ForegroundColor Cyan
Write-Host ""
