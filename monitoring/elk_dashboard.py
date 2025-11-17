"""
Web UI simple pour visualiser les logs ELK
Utilise Flask pour afficher les logs et métriques
"""

from flask import Flask, render_template_string, request, jsonify
from simple_elasticsearch import SimpleElasticsearch
from datetime import datetime
import json

app = Flask(__name__)
es = SimpleElasticsearch()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ELK Dashboard - Logs Centralisés</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
        header { background: #222; padding: 20px; border-bottom: 3px solid #FF7700; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
        .stat-box { background: #2a2a2a; padding: 20px; border-left: 4px solid #FF7700; border-radius: 4px; }
        .stat-number { font-size: 28px; font-weight: bold; color: #FF7700; }
        .stat-label { font-size: 14px; color: #aaa; margin-top: 5px; }
        .filters { background: #2a2a2a; padding: 15px; margin-bottom: 20px; border-radius: 4px; display: flex; gap: 10px; }
        .filters input, .filters select { padding: 8px; background: #333; color: #fff; border: 1px solid #444; border-radius: 4px; }
        .logs-container { background: #2a2a2a; border-radius: 4px; overflow: hidden; }
        .log-entry { padding: 15px; border-bottom: 1px solid #333; }
        .log-entry:hover { background: #333; }
        .log-timestamp { color: #888; font-size: 12px; }
        .log-level { display: inline-block; padding: 2px 8px; border-radius: 3px; font-weight: bold; font-size: 11px; margin-right: 10px; }
        .log-level.ERROR { background: #d32f2f; }
        .log-level.WARNING { background: #f57c00; }
        .log-level.INFO { background: #1976d2; }
        .log-message { margin-top: 5px; color: #ddd; }
        .log-meta { font-size: 12px; color: #666; margin-top: 8px; }
        .tabs { display: flex; gap: 0; margin-bottom: 20px; border-bottom: 2px solid #333; }
        .tab { padding: 12px 20px; background: none; color: #aaa; border: none; cursor: pointer; border-bottom: 3px solid transparent; }
        .tab.active { color: #FF7700; border-bottom-color: #FF7700; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .metric-item { background: #2a2a2a; padding: 15px; border-radius: 4px; }
        .metric-name { color: #FF7700; font-weight: bold; }
        .metric-value { font-size: 24px; margin: 10px 0; }
    </style>
</head>
<body>
    <header>
        <h1> ELK Dashboard - Logs Centralisés</h1>
        <p>Monitoring et visualisation des logs ETL</p>
    </header>

    <div class="container">
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="total-logs">0</div>
                <div class="stat-label">Logs Total</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #d32f2f;" id="error-logs">0</div>
                <div class="stat-label">Erreurs</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #f57c00;" id="warning-logs">0</div>
                <div class="stat-label">Avertissements</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="total-metrics">0</div>
                <div class="stat-label">Métriques</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('logs-tab')"> Logs</button>
            <button class="tab" onclick="switchTab('metrics-tab')"> Métriques</button>
            <button class="tab" onclick="switchTab('errors-tab')">⚠️ Erreurs</button>
        </div>

        <div class="filters">
            <input type="text" id="search-input" placeholder="Rechercher..." onkeyup="filterLogs()">
            <select id="level-filter" onchange="filterLogs()">
                <option value="">Tous les niveaux</option>
                <option value="ERROR">Erreurs</option>
                <option value="WARNING">Avertissements</option>
                <option value="INFO">Info</option>
            </select>
            <button onclick="loadData()" style="padding: 8px 15px; background: #FF7700; color: #fff; border: none; cursor: pointer; border-radius: 4px;">Actualiser</button>
        </div>

        <div id="logs-tab" class="tab-content active">
            <div class="logs-container" id="logs-list">
                <!-- Logs will be loaded here -->
            </div>
        </div>

        <div id="metrics-tab" class="tab-content">
            <div class="metrics-grid" id="metrics-list">
                <!-- Metrics will be loaded here -->
            </div>
        </div>

        <div id="errors-tab" class="tab-content">
            <div class="logs-container" id="errors-list">
                <!-- Errors will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            loadData();
        }

        function loadData() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-logs').textContent = data.total_logs;
                    document.getElementById('error-logs').textContent = data.errors;
                    document.getElementById('warning-logs').textContent = data.warnings;
                    document.getElementById('total-metrics').textContent = data.total_metrics;
                });

            fetch('/api/logs')
                .then(r => r.json())
                .then(logs => displayLogs(logs));

            fetch('/api/metrics')
                .then(r => r.json())
                .then(metrics => displayMetrics(metrics));

            fetch('/api/logs?level=ERROR')
                .then(r => r.json())
                .then(errors => displayErrors(errors));
        }

        function displayLogs(logs) {
            const container = document.getElementById('logs-list');
            container.innerHTML = logs.map(log => `
                <div class="log-entry">
                    <div class="log-timestamp">${log.timestamp}</div>
                    <span class="log-level ${log.level}">${log.level}</span>
                    <strong>${log.logger}</strong>
                    <div class="log-message">${log.message}</div>
                    <div class="log-meta">${log.module}:${log.function}:${log.line}</div>
                </div>
            `).join('');
        }

        function displayMetrics(metrics) {
            const container = document.getElementById('metrics-list');
            container.innerHTML = metrics.map(m => `
                <div class="metric-item">
                    <div class="metric-name">${m.metric_name}</div>
                    <div class="metric-value">${m.value.toFixed(2)}</div>
                    <div class="log-meta">${m.source} / ${m.table_name}</div>
                </div>
            `).join('');
        }

        function displayErrors(errors) {
            const container = document.getElementById('errors-list');
            container.innerHTML = errors.map(log => `
                <div class="log-entry" style="background: rgba(211, 47, 47, 0.1);">
                    <div class="log-timestamp">${log.timestamp}</div>
                    <span class="log-level ERROR">ERROR</span>
                    <strong>${log.logger}</strong>
                    <div class="log-message">${log.message}</div>
                </div>
            `).join('');
        }

        function filterLogs() {
            const searchInput = document.getElementById('search-input').value;
            const levelFilter = document.getElementById('level-filter').value;
            const logs = document.querySelectorAll('.log-entry');

            logs.forEach(log => {
                const message = log.textContent.toLowerCase();
                const level = log.querySelector('.log-level')?.textContent || '';
                const matchSearch = message.includes(searchInput.toLowerCase());
                const matchLevel = !levelFilter || level === levelFilter;

                log.style.display = matchSearch && matchLevel ? 'block' : 'none';
            });
        }

        // Load data on page load
        window.addEventListener('load', loadData);
        setInterval(loadData, 10000); // Refresh every 10 seconds
    </script>
</body>
</html>
'''


@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/stats')
def api_stats():
    return jsonify(es.get_stats())


@app.route('/api/logs')
def api_logs():
    level = request.args.get('level')
    limit = request.args.get('limit', 100, type=int)
    logs = es.search_logs(level=level, limit=limit)
    return jsonify(logs)


@app.route('/api/metrics')
def api_metrics():
    metric_name = request.args.get('metric_name')
    source = request.args.get('source')
    limit = request.args.get('limit', 100, type=int)
    metrics = es.search_metrics(metric_name=metric_name, source=source, limit=limit)
    return jsonify(metrics)


@app.route('/api/index', methods=['POST'])
def api_index():
    data = request.json
    if data.get('type') == 'metric':
        result = es.index_metric(data)
    else:
        result = es.index_log(data)
    return jsonify({'success': result})


if __name__ == '__main__':
    print(" ELK Dashboard en cours d'exécution sur http://localhost:5000")
    print(" Accédez au dashboard: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
