"""
Module d'intégration ELK (Elasticsearch + Logstash + Kibana)
pour centraliser les logs de monitoring et qualité
"""

import json
import logging
import socket
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ElasticsearchHandler(logging.Handler):
    """Handler personnalisé pour envoyer les logs à Elasticsearch via Logstash"""

    def __init__(self, host: str = "localhost", port: int = 5000):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self._connect()

    def _connect(self):
        """Établir la connexion socket à Logstash"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logging.info(f"✅ Connecté à Logstash: {self.host}:{self.port}")
        except Exception as e:
            logging.warning(f"⚠️  Impossible de connecter à Logstash: {e}")
            self.socket = None

    def emit(self, record: logging.LogRecord):
        """Envoyer le log à Logstash en JSON"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                log_entry["exception"] = self.format(record)

            if self.socket:
                message = json.dumps(log_entry) + "\n"
                self.socket.send(message.encode())
            else:
                # Réessayer de se connecter
                self._connect()
                if self.socket:
                    message = json.dumps(log_entry) + "\n"
                    self.socket.send(message.encode())

        except Exception as e:
            self.handleError(record)

    def close(self):
        """Fermer la connexion socket"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        super().close()


class ELKLogger:
    """Logger centralisé avec support ELK stack"""

    def __init__(
        self,
        name: str = "etl-monitoring",
        logstash_host: str = "localhost",
        logstash_port: int = 5000,
        file_logging: bool = True,
        log_dir: str = "./logs"
    ):
        """
        Initialiser le logger avec support ELK

        Args:
            name: Nom du logger
            logstash_host: Host de Logstash
            logstash_port: Port de Logstash
            file_logging: Activer les logs fichier
            log_dir: Répertoire des logs
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Format commun
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier
        if file_logging:
            Path(log_dir).mkdir(exist_ok=True)
            log_file = Path(log_dir) / f"{name}-{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Handler Elasticsearch/Logstash
        try:
            es_handler = ElasticsearchHandler(logstash_host, logstash_port)
            es_handler.setLevel(logging.INFO)
            self.logger.addHandler(es_handler)
        except Exception as e:
            self.logger.warning(f"⚠️  ELK non disponible: {e}")

    def log_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """
        Logger une métrique de qualité

        Args:
            metric_name: Nom de la métrique
            value: Valeur (généralement un pourcentage)
            tags: Tags additionnels (source, table, etc.)
        """
        tags = tags or {}
        message = f"METRIC: {metric_name}={value} | tags={json.dumps(tags)}"
        self.logger.info(message)

    def log_quality_check(
        self,
        table: str,
        completeness: float,
        duplicates: float,
        status: str,
        details: Optional[Dict] = None
    ):
        """
        Logger un check de qualité

        Args:
            table: Nom de la table
            completeness: Pourcentage de complétude
            duplicates: Pourcentage de doublons
            status: PASS, WARNING, CRITICAL
            details: Détails supplémentaires
        """
        entry = {
            "table": table,
            "completeness": completeness,
            "duplicates": duplicates,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

        if details:
            entry.update(details)

        message = f"QUALITY_CHECK: {json.dumps(entry)}"

        if status == "CRITICAL":
            self.logger.error(message)
        elif status == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def get_logger(self):
        """Retourner le logger Python standard"""
        return self.logger


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le logger ELK
    elk_logger = ELKLogger(
        name="etl-monitoring",
        logstash_host="localhost",
        logstash_port=5000,
        file_logging=True
    )

    logger = elk_logger.get_logger()

    # Exemples de logs
    logger.info("🚀 Démarrage du monitoring ETL")
    logger.debug("Configuration: DEBUG mode")

    # Logs de métriques
    elk_logger.log_metric("data_completeness", 99.5, {"source": "mysql", "table": "patients"})
    elk_logger.log_metric("duplicate_rate", 0.3, {"source": "mongodb", "table": "medical_tests"})

    # Logs de qualité
    elk_logger.log_quality_check(
        table="patients",
        completeness=99.8,
        duplicates=0.1,
        status="PASS",
        details={"rows": 1000, "checked_at": datetime.now().isoformat()}
    )

    elk_logger.log_quality_check(
        table="medical_records",
        completeness=92.5,
        duplicates=2.1,
        status="WARNING",
        details={"rows": 5000, "missing_fields": ["diagnosis"]}
    )

    logger.info("✅ Logs envoyés à ELK")
