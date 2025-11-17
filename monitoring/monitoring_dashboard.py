#!/usr/bin/env python3
"""
Dashboard de monitoring pour l'ETL
Affiche les métriques en temps réel et génère des alertes
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """Dashboard de monitoring principal"""
    
    def __init__(self, monitoring_dir='monitoring'):
        self.monitoring_dir = Path(monitoring_dir)
        self.monitoring_dir.mkdir(exist_ok=True)
        self.metrics_history = []
        self.alerts = []
    
    def load_metrics(self, report_path='monitoring/quality_report.json'):
        """Charger les métriques de qualité"""
        try:
            with open(report_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Rapport non trouvé: {report_path}")
            return None
    
    def check_sla(self, metrics):
        """Vérifier les SLA (Service Level Agreement)"""
        alerts = []
        
        if not metrics:
            return alerts
        
        # Vérifier la complétude (SLA: > 95%)
        for check_key, check_data in metrics.get('details', {}).items():
            completeness = check_data.get('completeness', {})
            
            
            completion_str = completeness.get('completion_rate', '0%')
            completion_rate = float(completion_str.replace('%', ''))
            
            if completion_rate < 95:
                alerts.append({
                    'severity': 'WARNING',
                    'message': f"Complétude faible pour {check_key}: {completion_rate}%",
                    'timestamp': datetime.now().isoformat()
                })
            elif completion_rate < 90:
                alerts.append({
                    'severity': 'CRITICAL',
                    'message': f"Complétude critique pour {check_key}: {completion_rate}%",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Vérifier les doublons (SLA: < 1%)
        for check_key, check_data in metrics.get('details', {}).items():
            duplicates = check_data.get('duplicates', {})
            dup_str = duplicates.get('duplicate_rate', '0%')
            dup_rate = float(dup_str.replace('%', ''))
            
            if dup_rate > 1:
                alerts.append({
                    'severity': 'WARNING',
                    'message': f"Doublons détectés dans {check_key}: {dup_rate}%",
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def generate_html_dashboard(self, metrics):
        """Générer un dashboard HTML"""
        alerts = self.check_sla(metrics)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Monitoring ETL</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .metric {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .metric:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        
        .metric-value {{
            color: #333;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .status-pass {{
            color: #27ae60;
        }}
        
        .status-warning {{
            color: #f39c12;
        }}
        
        .status-critical {{
            color: #e74c3c;
        }}
        
        .alerts {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .alert-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        
        .alert-warning {{
            background: #fff3cd;
            border-left-color: #f39c12;
        }}
        
        .alert-critical {{
            background: #f8d7da;
            border-left-color: #e74c3c;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1> Dashboard Monitoring ETL</h1>
            <p class="timestamp">Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2> Résumé</h2>
                <div class="metric">
                    <div class="metric-label">Vérifications totales</div>
                    <div class="metric-value">{len(metrics.get('details', {}))}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Statut</div>
                    <div class="metric-value status-pass">✓ OK</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🚨 Alertes</h2>
                <div class="metric">
                    <div class="metric-label">Alertes actives</div>
                    <div class="metric-value">{len(alerts)}</div>
                </div>
            </div>
        </div>
        
        {self._generate_details_html(metrics)}
        
        {self._generate_alerts_html(alerts) if alerts else '<div class="alerts"><h2>[OK] Aucune alerte</h2></div>'}
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _generate_details_html(self, metrics):
        """Générer le HTML des détails"""
        html = '<div class="card"><h2> Détails des vérifications</h2>'
        
        for check_key, check_data in metrics.get('details', {}).items():
            html += f'<div class="metric"><div class="metric-label">{check_key}</div>'
            
            # Afficher le taux de complétude
            completeness = check_data.get('completeness', {})
            completion_rate = completeness.get('completion_rate', 'N/A')
            
            html += f'<div class="metric-value">{completion_rate}</div>'
            
            # Barre de progression
            completion_pct = float(completion_rate.replace('%', '')) if '%' in completion_rate else 0
            html += f'''
            <div class="progress-bar">
                <div class="progress-fill" style="width: {completion_pct}%">
                    {completion_pct:.0f}%
                </div>
            </div>
            '''
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _generate_alerts_html(self, alerts):
        """Générer le HTML des alertes"""
        html = '<div class="alerts"><h2>🚨 Alertes</h2>'
        
        for alert in alerts:
            severity = alert['severity'].lower()
            html += f'''
            <div class="alert-item alert-{severity}">
                <strong>{alert['severity']}</strong><br>
                {alert['message']}<br>
                <small>{alert['timestamp']}</small>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def save_dashboard(self, metrics, output_file='monitoring/dashboard.html'):
        """Sauvegarder le dashboard HTML"""
        html = self.generate_html_dashboard(metrics)
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[OK] Dashboard sauvegardé: {output_file}")
    
    def print_console_dashboard(self, metrics):
        """Afficher le dashboard dans la console"""
        alerts = self.check_sla(metrics)
        
        print("\n" + "="*80)
        print(" DASHBOARD MONITORING ETL")
        print("="*80)
        
        print("\n RÉSUMÉ")
        print("-" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Vérifications totales: {len(metrics.get('details', {}))}")
        print(f"Alertes: {len(alerts)}")
        
        print("\n DÉTAILS DES VÉRIFICATIONS")
        print("-" * 80)
        for check_key, check_data in metrics.get('details', {}).items():
            completeness = check_data.get('completeness', {})
            completion_rate = completeness.get('completion_rate', 'N/A')
            print(f"  {check_key}: {completion_rate}")
        
        if alerts:
            print("\n🚨 ALERTES")
            print("-" * 80)
            for alert in alerts:
                print(f"  [{alert['severity']}] {alert['message']}")
        else:
            print("\n[OK] Aucune alerte")
        
        print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    logger.info("Dashboard de monitoring disponible")
