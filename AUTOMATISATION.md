#  Automatisation ETL - Guide Complet

Automatisez vos chargements de données pour que tout fonctionne **sans intervention manuelle** !

---

##  **Option 1 : Exécution Manuelle (Locale)**

### **Sur Windows (PowerShell)**

```powershell
# 1. Ouvrir PowerShell
# 2. Aller dans le répertoire du projet
cd C:\Users\HP\Desktop\data-lake-etl

# 3. Exécuter le script
.\sync-etl.ps1
```

### **Sur Linux/Mac (Bash)**

```bash
# 1. Aller dans le répertoire
cd ~/data-lake-etl

# 2. Rendre le script exécutable
chmod +x sync-etl.sh

# 3. Exécuter
./sync-etl.sh
```

---

## ⏰ **Option 2 : Automatisation Planifiée (Windows Task Scheduler)**

### **Créer une tâche programmée qui s'exécute chaque jour à 2h du matin**

1. **Ouvrir Task Scheduler** :
   - Appuyez sur `Win + R`
   - Tapez `taskschd.msc`
   - Cliquez OK

2. **Créer une nouvelle tâche** :
   - Cliquez **Créer une tâche** (à droite)
   - Nom : `Data Lake ETL Sync`
   - Sélectionnez **Exécuter avec les privilèges les plus élevés**

3. **Onglet "Déclencheurs"** :
   - Cliquez **Nouveau**
   - **Débuter la tâche** : À une heure planifiée
   - **Date/Heure** : Demain à 02:00
   - **Répéter chaque** : 1 jour
   - Cliquez **OK**

4. **Onglet "Actions"** :
   - Cliquez **Nouveau**
   - **Action** : Démarrer un programme
   - **Programme/script** : `powershell.exe`
   - **Arguments** : 
     ```
     -NoProfile -WindowStyle Hidden -File "C:\Users\HP\Desktop\data-lake-etl\sync-etl.ps1"
     ```
   - Cliquez **OK**

5. **Onglet "Conditions"** :
   - Cochez **Ne démarrer la tâche que si l'ordinateur est connecté à Internet**
   - Cliquez **OK**

6. **Cliquez "OK"** pour sauvegarder

---

## 🔄 **Option 3 : Automatisation GitHub Actions (CI/CD)**

### **Prérequis**
- Avoir le projet sur GitHub (https://github.com/ndoye09/DatAnalystFlow360)
- GitHub Actions activé (gratuit pour les repos publics)

### **Étapes**

1. **Le fichier GitHub Actions est déjà créé** :
   - `.github/workflows/daily-etl-sync.yml`

2. **Configurez GitHub Secrets** (pour les accès privés) :
   - Allez sur votre repo GitHub
   - **Settings** → **Secrets and variables** → **Actions**
   - Cliquez **New repository secret**
   - Ajoutez vos variables (si besoin)

3. **Activez l'automatisation** :
   - Le workflow s'exécute **automatiquement chaque jour à 2h UTC**
   - Vous pouvez aussi l'exécuter manuellement :
     - Allez sur **Actions** → **Data Lake ETL - Daily Sync**
     - Cliquez **Run workflow** → **Run workflow**

4. **Surveillance** :
   - Allez sur **Actions**
   - Vous verrez tous les exécutions
   - Cliquez sur une exécution pour voir les logs

---

## 📧 **Option 4 : Notifications d'Erreurs**

### **Recevoir une notification si l'ETL échoue**

Modifiez `sync-etl.ps1` ou `.github/workflows/daily-etl-sync.yml` pour ajouter :


```yaml
- name: 📧 Envoyer une alerte email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "[ERROR] ETL Data Lake a échoué"
    to: votre-email@gmail.com
    from: etl-notifications@gmail.com
    body: "Vérifiez les logs : https://github.com/ndoye09/DatAnalystFlow360/actions"
```

#### **Slack**
```yaml
- name: 🔔 Notifier Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "[ERROR] ETL Data Lake a échoué",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*ETL Sync Failure*\nVérifiez : https://github.com/ndoye09/DatAnalystFlow360/actions"
            }
          }
        ]
      }
```

---

##  **Monitoring du Workflow**

### **Voir l'historique des exécutions**

1. **Sur GitHub** :
   - Allez sur votre repo
   - Cliquez **Actions**
   - Sélectionnez **Data Lake ETL - Daily Sync**
   - Vous verrez tous les exécutions avec [OK] ou [ERROR]

2. **Localement** (via Windows Task Scheduler) :
   - Task Scheduler → Clic droit sur la tâche → **Afficher l'historique**

---

##  **Résumé**

| Option | Fréquence | Configuration | Effort |
|--------|-----------|--------------|--------|
| **Manuelle** | À la demande | Script simple | 🟢 Facile |
| **Task Scheduler** | Programmée | 5 min | 🟢 Facile |
| **GitHub Actions** | Programmée | Déjà fait | 🔵 Moyen |
| **Notifications** | Erreurs | Webhook | 🔴 Difficile |

---

##  **Configuration Recommandée**

Pour **production**, utilisez :
1. **GitHub Actions** (automatisation gratuite)
2. **Slack Webhook** (notifications en temps réel)
3. **Exécution quotidienne à 2h du matin**

---

**Vous préférez laquelle ?** 
