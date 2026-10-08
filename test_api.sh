#!/bin/bash

echo "Testing API endpoints..."
echo ""

echo "1. GET /api/partidos (sin detalles):"
curl -s http://127.0.0.1:8000/api/partidos | jq '.' 2>/dev/null | head -20

echo ""
echo "2. GET /api/partidos/1/convocatorias:"
curl -s http://127.0.0.1:8000/api/partidos/1/convocatorias | jq '.' 2>/dev/null

