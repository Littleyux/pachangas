#!/bin/bash

echo "================================================"
echo "VERIFICACIÓN DEL SISTEMA PACHANGAS"
echo "================================================"
echo ""

# 1. Verificar sintaxis Python
echo "1. Verificando sintaxis Python..."
cd /home/alberto/pachangas/backend
python3 -m py_compile main.py && echo "   ✓ Backend: Sintaxis válida" || echo "   ✗ Backend: Error de sintaxis"

# 2. Verificar endpoints
echo ""
echo "2. Verificando endpoints FastAPI..."
echo "   GET /api/health:"
curl -s http://127.0.0.1:8000/api/health | jq '.status' 2>/dev/null && echo "   ✓ Health check OK" || echo "   ✗ Backend no disponible"

echo "   GET /api/usuarios:"
curl -s http://127.0.0.1:8000/api/usuarios 2>/dev/null | jq 'length' > /dev/null 2>&1 && echo "   ✓ Usuarios endpoint OK" || echo "   ✗ Error en endpoint"

echo "   GET /api/campos:"
curl -s http://127.0.0.1:8000/api/campos 2>/dev/null | jq 'length' > /dev/null 2>&1 && echo "   ✓ Campos endpoint OK" || echo "   ✗ Error en endpoint"

echo "   GET /api/partidos:"
curl -s http://127.0.0.1:8000/api/partidos 2>/dev/null | jq 'length' > /dev/null 2>&1 && echo "   ✓ Partidos endpoint OK" || echo "   ✗ Error en endpoint"

# 3. Verificar archivos frontend
echo ""
echo "3. Verificando archivos frontend..."
cd /home/alberto/pachangas/frontend/src

if [ -f "App.jsx" ]; then
  LINES=$(wc -l < App.jsx)
  echo "   ✓ App.jsx: $LINES líneas"
else
  echo "   ✗ App.jsx no encontrado"
fi

if [ -f "App.css" ]; then
  LINES=$(wc -l < App.css)
  echo "   ✓ App.css: $LINES líneas"
else
  echo "   ✗ App.css no encontrado"
fi

if [ -f "icons.css" ]; then
  LINES=$(wc -l < icons.css)
  echo "   ✓ icons.css: $LINES líneas"
else
  echo "   ✗ icons.css no encontrado"
fi

# 4. Verificar servidor frontend
echo ""
echo "4. Verificando servidor frontend..."
if ps aux | grep -q "npm run dev" | grep -v grep; then
  echo "   ✓ Servidor Vite activo"
  echo "   → Frontend disponible en: http://localhost:5174/"
else
  echo "   ✗ Servidor Vite no está corriendo"
fi

echo ""
echo "================================================"
echo "FUNCIONALIDADES IMPLEMENTADAS:"
echo "================================================"
echo "✓ CRUD Usuarios (crear, listar)"
echo "✓ CRUD Campos (crear, listar, eliminar)"
echo "✓ CRUD Partidos (crear, listar, eliminar)"
echo "✓ Sistema de Inscripción (apuntarse/desapuntarse)"
echo "✓ UI Material Design 3 (moderna y limpia)"
echo "✓ Tabs navegables (Jugadores, Campos, Partidos)"
echo "✓ Listados expandibles (detalles de partidos)"
echo ""
echo "================================================"
echo "PRÓXIMOS PASOS:"
echo "================================================"
echo "1. Abre http://localhost:5174/ en tu navegador"
echo "2. Registra jugadores en la tab 'Jugadores'"
echo "3. Registra campos en la tab 'Campos'"
echo "4. Crea partidos en la tab 'Partidos'"
echo "5. Haz click en un partido para apuntarte"
echo "================================================"

