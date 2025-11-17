#  Guide Power BI - Data Warehouse PostgreSQL

##  Connexion PostgreSQL dans Power BI

### Étape 1 : Télécharger le Driver PostgreSQL

Power BI a besoin du driver PostgreSQL pour se connecter.

**Option A : Via Power BI (Recommandé)**
1. Ouvrir Power BI Desktop
2. Menu : `Obtenir les données` → `Plus...`
3. Chercher : `PostgreSQL`
4. Cliquer sur `PostgreSQL database`
5. Cliquer `Connecter`
6. Power BI vous proposera d'installer le driver si nécessaire

**Option B : Installation manuelle**
```
https://www.postgresql.org/download/other/
Télécharger : PostgreSQL ODBC Driver (psqlODBC)
```

---

## 🔗 Paramètres de Connexion

### Informations de connexion
```
Serveur : localhost
Port : 5432
Base de données : datawarehouse
Utilisateur : dwh_user
Mot de passe : dwh_password
```


```
Host: localhost
Database: datawarehouse
User: dwh_user
Password: dwh_password
Port: 5432
```

---

##  Étapes de Connexion dans Power BI

### 1️⃣ Lancer Power BI Desktop
- Ouvrir **Power BI Desktop**
- Accueil → `Obtenir les données`

### 2️⃣ Sélectionner PostgreSQL
```
Données → Obtenir les données → Plus...
   ↓
   Chercher : "PostgreSQL"
   ↓
   Sélectionner : "PostgreSQL database"
   ↓
   Cliquer : "Connecter"
```

### 3️⃣ Entrer les informations de serveur
```
Serveur : localhost
Base de données : datawarehouse
```
Cliquer → **OK**

### 4️⃣ Authentification
```
Connexion à la base de données
Authentification : Compte utilisateur (par défaut)
Nom d'utilisateur : dwh_user
Mot de passe : dwh_password
✓ Cliquer : "Connecter"
```

### 5️⃣ Sélectionner les tables
Dans le **Navigateur**, sélectionner :

**Tables de Staging (données brutes)**
- ✓ staging.stg_patients
- ✓ staging.stg_medical_tests
- ✓ staging.stg_medications
- ✓ staging.stg_appointments

**Tables de Dimension**
- ✓ dim.dim_patient
- ✓ dim.dim_doctor
- ✓ dim.dim_date

**Tables de Fait**
- ✓ fact.fact_medical_tests
- ✓ fact.fact_appointments

**Vues Analytics (Recommandé)**
- ✓ analytics.v_patient_health_summary
- ✓ analytics.v_health_metrics

### 6️⃣ Charger les données
```
Sélectionner les tables → "Charger"
```

Power BI téléchargera les données dans le modèle.

---

##  Dashboards Recommandés

### Dashboard 1 : Vue d'ensemble Santé
**Visualisations suggérées :**
- KPI : Nombre de patients
- KPI : Nombre de tests
- KPI : Taux d'hypertension (%)
- KPI : Taux de cholestérol élevé (%)
- Carte : Distribution par genre
- Graphique barres : Distribution âge
- Tableau : Top 10 patients à risque

### Dashboard 2 : Tests Médicaux
**Visualisations suggérées :**
- Graphique circulaire : Types de tests
- Graphique circulaire : Niveaux cholestérol
- Jauge : Cholestérol moyen
- Jauge : Tension systolique moyenne
- Tableau : Derniers tests

### Dashboard 3 : Suivi Patients
**Visualisations suggérées :**
- Carte : Patients par âge
- Tableau : Patients à risque cardiaque
- Graphique ligne : Évolution cholestérol
- Matrice : Tests par patient

### Dashboard 4 : Rendez-vous & Activités
**Visualisations suggérées :**
- Graphique barres : RDV par spécialité
- Graphique circulaire : Statut RDV (Complétés/Annulés)
- Tableau : Calendrier RDV
- Jauge : Taux complétude RDV

---

## 🔄 Modèle de Données

### Schéma Relatif
```
dim_patient ←→ fact_medical_tests
    ↓
dim_doctor ←→ fact_appointments
    ↓
dim_date (utilisé par les deux)
```

### Relations à créer dans Power BI

**1. dim_patient → fact_medical_tests**
```
De : dim.dim_patient.patient_key
À : fact.fact_medical_tests.patient_key
Cardinalité : Un vers plusieurs
```

**2. dim_patient → fact_appointments**
```
De : dim.dim_patient.patient_key
À : fact.fact_appointments.patient_key
Cardinalité : Un vers plusieurs
```

**3. dim_doctor → fact_appointments**
```
De : dim.dim_doctor.doctor_key
À : fact.fact_appointments.doctor_key
Cardinalité : Un vers plusieurs
```

**4. dim_date → fact_medical_tests**
```
De : dim.dim_date.date_key
À : fact.fact_medical_tests.test_date_key
Cardinalité : Un vers plusieurs
```

---

##  Requêtes SQL Utiles pour Power BI

### Patients à Haut Risque
```sql
SELECT 
    p.patient_key,
    p.first_name,
    p.last_name,
    p.age,
    phs.avg_cholesterol,
    phs.avg_systolic,
    phs.avg_glucose,
    phs.total_tests,
    CASE 
        WHEN phs.avg_cholesterol > 240 THEN 'Très élevé'
        WHEN phs.avg_cholesterol > 200 THEN 'Élevé'
        ELSE 'Normal'
    END as risk_level
FROM analytics.v_patient_health_summary phs
JOIN dim.dim_patient p ON phs.patient_key = p.patient_key
ORDER BY phs.avg_cholesterol DESC;
```

### Statistiques Tests
```sql
SELECT 
    test_type,
    COUNT(*) as total_tests,
    ROUND(AVG(cholesterol), 2) as avg_cholesterol,
    ROUND(AVG(glucose), 2) as avg_glucose,
    ROUND(AVG(systolic_bp), 2) as avg_systolic
FROM staging.stg_medical_tests
GROUP BY test_type;
```

### Tendance Rendez-vous
```sql
SELECT 
    DATE_TRUNC('month', appointment_date)::date as mois,
    specialty,
    COUNT(*) as nombre_rdv,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
FROM staging.stg_appointments
GROUP BY DATE_TRUNC('month', appointment_date), specialty
ORDER BY mois DESC;
```

### Patients par Groupe d'Âge
```sql
SELECT 
    CASE 
        WHEN age < 30 THEN '<30'
        WHEN age < 40 THEN '30-40'
        WHEN age < 50 THEN '40-50'
        WHEN age < 60 THEN '50-60'
        ELSE '60+'
    END as age_group,
    COUNT(*) as patient_count,
    ROUND(AVG(age), 1) as avg_age
FROM staging.stg_patients
GROUP BY age_group
ORDER BY age_group;
```

---

##  Configuration Avancée

### Actualisation Automatique des Données

**Option 1 : Power BI Service (Cloud)**
1. Publier le rapport sur Power BI Service
2. Accédé aux paramètres du dataset
3. Configurer l'actualisation planifiée
4. Planifier l'actualisation quotidienne à 02:00 UTC

**Option 2 : Desktop (Actualisation manuelle)**
```
Accueil → Actualiser
ou
Données → Actualiser tout
```

### Mesures Recommandées

**Cholestérol Moyen**
```dax
Cholestérol Moyen = AVERAGE('fact_medical_tests'[cholesterol])
```

**Patients à Risque (%)**
```dax
Patients Risque % = 
DIVIDE(
    COUNTIF('fact_medical_tests'[cholesterol] > 240),
    COUNTA('dim_patient'[patient_key]),
    0
) * 100
```

**Taux Complétude RDV**
```dax
Taux Complétude = 
DIVIDE(
    COUNTIF('fact_appointments'[status] = "Completed"),
    COUNTA('fact_appointments'[appointment_id]),
    0
) * 100
```

---

## 🐛 Dépannage

### Erreur : "Impossible de se connecter à PostgreSQL"

**Vérifier :**
1. PostgreSQL est en cours d'exécution
   ```powershell
   docker-compose -f docker-compose-dwh.yml ps
   ```

2. Port 5432 est accessible
   ```powershell
   Test-NetConnection localhost -Port 5432
   ```

3. Identifiants corrects
   - User: `dwh_user`
   - Password: `dwh_password`
   - Database: `datawarehouse`

### Erreur : "Driver PostgreSQL manquant"

**Solution :**
1. Télécharger psqlODBC
2. Installer le driver
3. Redémarrer Power BI Desktop

### Performance lente

**Optimisations :**
1. Réduire le nombre de lignes importées
2. Appliquer des filtres dans Power Query
3. Créer des agrégations dans PostgreSQL
4. Utiliser les vues analitiques au lieu des tables brutes

---

## 📚 Ressources

- **Power BI Documentation** : https://docs.microsoft.com/en-us/power-bi/
- **PostgreSQL Driver** : https://odbc.postgresql.org/
- **DAX Functions** : https://dax.guide/
- **Power BI Best Practices** : https://powerbi.microsoft.com/en-us/documentation/

---

## [OK] Checklist de Configuration

- [ ] Power BI Desktop installé
- [ ] PostgreSQL Driver (psqlODBC) installé
- [ ] PostgreSQL Data Warehouse en cours d'exécution
- [ ] Connexion PostgreSQL établie dans Power BI
- [ ] Tables chargées avec succès
- [ ] Relations créées
- [ ] Mesures DAX créées
- [ ] Dashboard créé
- [ ] Actualisation testée
- [ ] Rapport prêt pour utilisation

---

**Besoin d'aide ? Consultez ce guide ou contactez votre administrateur Data Warehouse !**
