#!/usr/bin/env python3
"""
Démarrage du Dashboard ELK Web
Logs centralisés avec interface web
"""

import subprocess
import webbrowser
import time
from pathlib import Path

print("=" * 50)
print("Dashboard ELK - Logs Centralisés")
print("=" * 50)
print()

# Démarrer le serveur Flask
print(" Démarrage du dashboard...")
process = subprocess.Popen(
    ["python", "monitoring/elk_dashboard.py"],
    cwd=Path(__file__).parent
)

# Attendre que le serveur soit prêt
time.sleep(3)

# Ouvrir le navigateur
print(" Ouverture du navigateur...")
webbrowser.open("http://localhost:5000")

print()
print("Dashboard actif sur http://localhost:5000")
print("Pour arrêter: Ctrl+C")
print()

try:
    process.wait()
except KeyboardInterrupt:
    print("\n\nArrêt du dashboard...")
    process.terminate()
    process.wait()
    print("Dashboard arrêté")
