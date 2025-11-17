#!/bin/bash

# Script de démarrage de la stack ELK

echo "========================================="
echo "Demarrage de la stack ELK"
echo "========================================="
echo ""

# Vérifier si docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo "ERREUR: docker-compose n'est pas installé"
    exit 1
fi

# Créer les répertoires nécessaires
mkdir -p logs
mkdir -p logstash/config
mkdir -p logstash/pipeline

echo "Demarrage des services Elasticsearch, Logstash et Kibana..."
docker-compose -f docker-compose-elk.yml up -d

echo ""
echo "Attente que les services soient prets..."
sleep 10

# Vérifier l'état des services
echo ""
echo "Vérification de l'état des services..."

# Elasticsearch
echo -n "Elasticsearch: "
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "✓ PRET"
else
    echo "✗ EN ATTENTE"
fi

# Kibana
echo -n "Kibana: "
if curl -s http://localhost:5601/api/status > /dev/null 2>&1; then
    echo "✓ PRET"
else
    echo "✗ EN ATTENTE"
fi

# Logstash
echo -n "Logstash: "
if curl -s http://localhost:9600 > /dev/null 2>&1; then
    echo "✓ PRET"
else
    echo "✗ EN ATTENTE"
fi

echo ""
echo "========================================="
echo "ELK Stack en cours d'execution"
echo "========================================="
echo ""
echo "Services disponibles:"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana: http://localhost:5601"
echo "  - Logstash: localhost:5000 (TCP/UDP)"
echo ""
echo "Pour arreter: docker-compose -f docker-compose-elk.yml down"
echo ""
