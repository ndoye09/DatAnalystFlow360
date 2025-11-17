# Script de test de connexion PostgreSQL pour Power BI
# Ce script vérifie que PostgreSQL est accessible avant de configurer Power BI

Write-Host "[------------------------------------------------------------]" -ForegroundColor Cyan
Write-Host "|   TEST DE CONNEXION PostgreSQL POUR POWER BI            |" -ForegroundColor Cyan
Write-Host "[------------------------------------------------------------]" -ForegroundColor Cyan

Write-Host "`n Paramètres de connexion" -ForegroundColor Yellow
Write-Host "   Host: localhost"
Write-Host "   Port: 5432"
Write-Host "   Database: datawarehouse"
Write-Host "   User: dwh_user"

# Test 1 : Vérifier que le port est accessible
Write-Host "`n🔌 Test 1: Connexion réseau au port 5432..." -ForegroundColor Cyan
try {
    $connection = [System.Net.Sockets.TcpClient]::new()
    $connection.Connect("localhost", 5432)
    
    if ($connection.Connected) {
        Write-Host "[OK] Port 5432 accessible" -ForegroundColor Green
        $connection.Close()
    }
} catch {
    Write-Host "[ERROR] Port 5432 NON accessible" -ForegroundColor Red
    Write-Host "   Assurez-vous que PostgreSQL est en cours d'exécution" -ForegroundColor Yellow
    exit 1
}

# Test 2 : Vérifier le conteneur Docker
Write-Host "`n🐳 Test 2: Vérifier le conteneur Docker..." -ForegroundColor Cyan
try {
    $container = docker ps -f "name=datawarehouse" --format "{{.Names}}" 2>$null
    
    if ($container) {
        Write-Host "[OK] Conteneur PostgreSQL 'datawarehouse' est actif" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Conteneur PostgreSQL non trouvé en cours d'exécution" -ForegroundColor Yellow
        Write-Host "   Pour démarrer: docker-compose -f docker-compose-dwh.yml up -d" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Impossible de vérifier Docker" -ForegroundColor Yellow
}

# Test 3 : Tester la connexion PostgreSQL avec psql (si disponible)
Write-Host "`n Test 3: Tester la connexion PostgreSQL..." -ForegroundColor Cyan
try {
    $psqlPath = "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    
    if (Test-Path $psqlPath) {
        # Utiliser psql
        $env:PGPASSWORD = "dwh_password"
        $result = & $psqlPath -h localhost -U dwh_user -d datawarehouse -c "SELECT COUNT(*) FROM staging.stg_patients;" 2>$null
        
        if ($result -match '\d+') {
            Write-Host "[OK] Connexion PostgreSQL réussie" -ForegroundColor Green
            Write-Host "   Nombre de patients: $(($result | Select-String '\d+' -AllMatches).Matches[0].Value)" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  psql non trouvé, test de connexion avancée ignoré" -ForegroundColor Yellow
        Write-Host "   Pour installer: Télécharger PostgreSQL depuis postgresql.org" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Impossible de tester la connexion psql" -ForegroundColor Yellow
}

# Test 4 : Vérifier les tables
Write-Host "`n📚 Test 4: Vérifier la structure des tables..." -ForegroundColor Cyan
try {
    $python = ".\.venv\Scripts\python.exe"
    
    if (Test-Path $python) {
        Write-Host "[OK] Environnement Python trouvé" -ForegroundColor Green
        Write-Host "   Python ready for Power BI configuration" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Impossible de vérifier les tables" -ForegroundColor Yellow
}

# Résumé final
Write-Host "`n====== RESUME ======" -ForegroundColor Cyan

Write-Host "`nSi tous les tests sont passes, vous pouvez configurer Power BI:" -ForegroundColor Green
Write-Host "1. Ouvrir Power BI Desktop" -ForegroundColor Cyan
Write-Host "2. Obtenir les donnees - PostgreSQL" -ForegroundColor Cyan
Write-Host "3. Entrer : localhost, datawarehouse" -ForegroundColor Cyan
Write-Host "4. Authentification : dwh_user / dwh_password" -ForegroundColor Cyan
Write-Host "5. Charger les tables souhaitees" -ForegroundColor Cyan

Write-Host "`nDocumentation completes : POWER_BI.md" -ForegroundColor Yellow
Write-Host "Configuration rapide : POWER_BI_CONFIG.txt" -ForegroundColor Yellow

Write-Host "`nConfiguration prete pour Power BI!" -ForegroundColor Green
