#!/bin/bash

# Test de endpoints de partidos
echo "Testing Pachangas API Endpoints..."
echo ""

echo "1. Health Check:"
curl -s http://127.0.0.1:8000/api/health | jq . 2>/dev/null || echo "Backend no está disponible"
echo ""

echo "2. Obtener Campos:"
curl -s http://127.0.0.1:8000/api/campos 2>/dev/null | jq '.[0] // "Sin campos"' || echo "No se puede conectar"
echo ""

echo "3. Obtener Partidos:"
curl -s http://127.0.0.1:8000/api/partidos 2>/dev/null | jq '.[0] // "Sin partidos"' || echo "No se puede conectar"

echo ""
echo "✓ Test completado"
