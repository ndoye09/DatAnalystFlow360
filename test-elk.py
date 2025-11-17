#!/usr/bin/env python3
"""
Script de test complet pour la solution ELK
Teste l'indexation, la recherche et le dashboard
"""

import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire monitoring au path
sys.path.insert(0, str(Path(__file__).parent / "monitoring"))

from simple_elasticsearch import SimpleElasticsearch


def test_indexation():
    """Test 1: Indexation de logs et métriques"""
    print("\n" + "="*60)
    print("TEST 1: INDEXATION DE LOGS ET MÉTRIQUES")
    print("="*60)

    es = SimpleElasticsearch()

    # Logs d'exemple
    logs_examples = [
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'logger': 'etl-monitor',
            'message': 'Démarrage du monitoring ETL',
            'module': 'main',
            'function': 'start_monitoring',
            'line': 42,
            'tags': ['etl', 'startup']
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'level': 'WARNING',
            'logger': 'data-quality',
            'message': 'Complétude basse détectée pour mysql_patients: 92.5%',
            'module': 'quality_check',
            'function': 'check_completeness',
            'line': 128,
            'tags': ['quality', 'warning', 'mysql']
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'level': 'ERROR',
            'logger': 'etl-extract',
            'message': 'Erreur de connexion à MongoDB',
            'module': 'extractors',
            'function': 'extract_mongodb',
            'line': 256,
            'tags': ['error', 'mongodb', 'connection'],
            'exception': 'ConnectionError: Unable to connect to MongoDB at mongodb://localhost:27017/'
        }
    ]

    print("\n✓ Indexation de 3 logs...")
    for i, log in enumerate(logs_examples, 1):
        if es.index_log(log):
            print(f"  {i}. ✓ {log['level']:7} - {log['message'][:50]}...")
        else:
            print(f"  {i}. ✗ Erreur indexation")
            return False

    # Métriques d'exemple
    metrics_examples = [
        {
            'timestamp': datetime.now().isoformat(),
            'metric_name': 'data_completeness',
            'value': 99.8,
            'source': 'mysql',
            'table_name': 'patients',
            'tags': ['quality-check', 'pass']
        },
        {
            'timestamp': datetime.now().isoformat(),
            'metric_name': 'duplicate_rate',
            'value': 0.2,
            'source': 'mongodb',
            'table_name': 'medical_records',
            'tags': ['quality-check', 'pass']
        },
        {
            'timestamp': datetime.now().isoformat(),
            'metric_name': 'data_completeness',
            'value': 92.5,
            'source': 'mysql',
            'table_name': 'medical_tests',
            'tags': ['quality-check', 'warning']
        },
        {
            'timestamp': datetime.now().isoformat(),
            'metric_name': 'etl_duration',
            'value': 45.2,
            'source': 'system',
            'table_name': 'performance',
            'tags': ['performance', 'timing']
        }
    ]

    print("\n✓ Indexation de 4 métriques...")
    for i, metric in enumerate(metrics_examples, 1):
        if es.index_metric(metric):
            print(f"  {i}. ✓ {metric['metric_name']:20} = {metric['value']:7.2f} ({metric['source']})")
        else:
            print(f"  {i}. ✗ Erreur indexation")
            return False

    print("\n✓ TEST 1 RÉUSSI")
    return True


def test_recherche():
    """Test 2: Recherche de logs et métriques"""
    print("\n" + "="*60)
    print("TEST 2: RECHERCHE DE LOGS ET MÉTRIQUES")
    print("="*60)

    es = SimpleElasticsearch()

    # Recherche de logs
    print("\n✓ Recherche de tous les logs...")
    all_logs = es.search_logs(limit=10)
    print(f"  Trouvés: {len(all_logs)} logs")
    for log in all_logs[:3]:
        print(f"    - [{log['level']}] {log['message'][:40]}...")

    # Recherche logs ERROR
    print("\n✓ Recherche de logs ERROR...")
    error_logs = es.search_logs(level='ERROR', limit=10)
    print(f"  Trouvés: {len(error_logs)} erreurs")
    for log in error_logs:
        print(f"    - {log['message'][:50]}...")

    # Recherche logs WARNING
    print("\n✓ Recherche de logs WARNING...")
    warning_logs = es.search_logs(level='WARNING', limit=10)
    print(f"  Trouvés: {len(warning_logs)} avertissements")

    # Recherche de métriques
    print("\n✓ Recherche de métriques 'data_completeness'...")
    completeness_metrics = es.search_metrics(metric_name='data_completeness', limit=10)
    print(f"  Trouvés: {len(completeness_metrics)} métriques")
    for metric in completeness_metrics:
        print(f"    - {metric['source']:10} {metric['table_name']:20} = {metric['value']:6.2f}%")

    # Recherche de métriques par source
    print("\n✓ Recherche de métriques MySQL...")
    mysql_metrics = es.search_metrics(source='mysql', limit=10)
    print(f"  Trouvés: {len(mysql_metrics)} métriques MySQL")

    print("\n✓ TEST 2 RÉUSSI")
    return True


def test_statistiques():
    """Test 3: Statistiques globales"""
    print("\n" + "="*60)
    print("TEST 3: STATISTIQUES GLOBALES")
    print("="*60)

    es = SimpleElasticsearch()
    stats = es.get_stats()

    print(f"\n✓ Statistiques de la base ELK:")
    print(f"  - Total logs:        {stats.get('total_logs', 0):,}")
    print(f"  - Logs ERROR:        {stats.get('errors', 0)} ⚠️")
    print(f"  - Logs WARNING:      {stats.get('warnings', 0)} ⚠️")
    print(f"  - Total métriques:   {stats.get('total_metrics', 0):,}")
    print(f"  - Taille BD:         {stats.get('db_size', 0) / 1024:.2f} KB")

    # Vérifications
    if stats.get('total_logs', 0) > 0:
        print(f"\n✓ Logs présents: OUI")
    else:
        print(f"\n✗ Logs présents: NON")
        return False

    if stats.get('total_metrics', 0) > 0:
        print(f"✓ Métriques présentes: OUI")
    else:
        print(f"✗ Métriques présentes: NON")
        return False

    print("\n✓ TEST 3 RÉUSSI")
    return True


def test_dashboard():
    """Test 4: Affichage HTML du dashboard"""
    print("\n" + "="*60)
    print("TEST 4: GÉNÉRATION DU DASHBOARD")
    print("="*60)

    es = SimpleElasticsearch()
    stats = es.get_stats()
    logs = es.search_logs(limit=20)
    metrics = es.search_metrics(limit=20)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard ELK - Logs Centralisés</title>
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
                max-width: 1400px;
                margin: 0 auto;
            }}
            header {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            header h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            header p {{
                color: #666;
                font-size: 14px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                color: #667eea;
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 10px;
            }}
            .stat-card .value {{
                font-size: 32px;
                font-weight: bold;
                color: #333;
            }}
            .stat-card .unit {{
                color: #999;
                font-size: 14px;
            }}
            .error {{ color: #e74c3c; }}
            .warning {{ color: #f39c12; }}
            .success {{ color: #27ae60; }}
            .info {{ color: #3498db; }}
            
            .section {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #333;
                margin-bottom: 15px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            table th {{
                background: #f5f5f5;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #333;
            }}
            table td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            table tr:hover {{
                background: #f9f9f9;
            }}
            
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }}
            .badge.info {{ background: #e3f2fd; color: #1976d2; }}
            .badge.warning {{ background: #fff3e0; color: #f57c00; }}
            .badge.error {{ background: #ffebee; color: #c62828; }}
            .badge.success {{ background: #e8f5e9; color: #2e7d32; }}
            
            .timestamp {{
                color: #999;
                font-size: 12px;
            }}
            
            footer {{
                text-align: center;
                color: white;
                margin-top: 30px;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1> Dashboard ELK - Logs Centralisés</h1>
                <p>Monitoring ETL en temps réel • {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>📝 Total Logs</h3>
                    <div class="value">{stats.get('total_logs', 0):,}</div>
                </div>
                <div class="stat-card">
                    <h3><span class="error">⚠️ Erreurs</span></h3>
                    <div class="value error">{stats.get('errors', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3><span class="warning"> Avertissements</span></h3>
                    <div class="value warning">{stats.get('warnings', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3> Métriques</h3>
                    <div class="value">{stats.get('total_metrics', 0):,}</div>
                </div>
            </div>
            
            <div class="section">
                <h2> Logs Récents</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Niveau</th>
                            <th>Logger</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for log in logs[:10]:
        badge_class = log['level'].lower()
        html_content += f"""
                        <tr>
                            <td class="timestamp">{log['timestamp']}</td>
                            <td><span class="badge {badge_class}">{log['level']}</span></td>
                            <td>{log['logger']}</td>
                            <td>{log['message'][:60]}...</td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2> Métriques de Qualité</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Métrique</th>
                            <th>Source</th>
                            <th>Table</th>
                            <th>Valeur</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for metric in metrics[:10]:
        status = "success" if metric['value'] > 95 else "warning" if metric['value'] > 90 else "error"
        html_content += f"""
                        <tr>
                            <td class="timestamp">{metric['timestamp']}</td>
                            <td>{metric['metric_name']}</td>
                            <td>{metric['source']}</td>
                            <td>{metric['table_name']}</td>
                            <td><span class="badge {status}">{metric['value']:.2f}%</span></td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
            
            <footer>
                <p>ELK Stack - Elasticsearch like monitoring • Generated: """ + datetime.now().isoformat() + """</p>
            </footer>
        </div>
    </body>
    </html>
    """

    # Sauvegarder le dashboard
    dashboard_path = Path("monitoring/dashboard-elk.html")
    dashboard_path.write_text(html_content, encoding='utf-8')
    print(f"\n✓ Dashboard généré: {dashboard_path}")
    print(f"✓ Taille: {len(html_content) / 1024:.2f} KB")
    print(f"✓ Ouvrir dans le navigateur: file:///{dashboard_path.absolute()}")

    print("\n✓ TEST 4 RÉUSSI")
    return True


def main():
    """Exécuter tous les tests"""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + " " * 15 + "SUITE DE TESTS ELK STACK" + " " * 19 + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)

    tests = [
        ("Indexation", test_indexation),
        ("Recherche", test_recherche),
        ("Statistiques", test_statistiques),
        ("Dashboard", test_dashboard)
    ]

    results = []
    start_time = time.time()

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ ERREUR: {e}")
            results.append((name, False))

    elapsed = time.time() - start_time

    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")

    print(f"\nTotal: {passed}/{total} tests réussis")
    print(f"Durée: {elapsed:.2f}s")

    if passed == total:
        print("\n TOUS LES TESTS SONT PASSÉS!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) en échec")
        return 1


if __name__ == "__main__":
    exit(main())
