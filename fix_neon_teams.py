#!/usr/bin/env python3
"""
Script para arreglar los nombres de equipos en convocatorias en Neon.
Identifica y actualiza convocatorias que tienen valores por defecto incorrectos.
"""

import os
import sys
sys.path.insert(0, '/home/alberto/pachangas/backend')

from db import get_db_connection
from dotenv import load_dotenv

load_dotenv('/home/alberto/pachangas/backend/.env')

print("🔧 Arreglando nombres de equipos en Neon...")
print("=" * 60)

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Obtener todos los partidos con sus nombres de equipos
    print("\n[1] Obteniendo partidos con nombres de equipos...")
    cursor.execute("""
        SELECT id, equipo_a_nombre, equipo_b_nombre 
        FROM partidos 
        WHERE equipo_a_nombre IS NOT NULL 
        OR equipo_b_nombre IS NOT NULL;
    """)
    partidos = cursor.fetchall()
    print(f"    ✓ Encontrados {len(partidos)} partidos con nombres custom")

    # 2. Para cada partido, verificar y arreglar convocatorias
    total_fixes = 0
    
    for partido in partidos:
        partido_id = partido['id'] if isinstance(partido, dict) else partido[0]
        equipo_a = partido['equipo_a_nombre'] if isinstance(partido, dict) else partido[1]
        equipo_b = partido['equipo_b_nombre'] if isinstance(partido, dict) else partido[2]
        
        # Verificar si hay convocatorias con valores por defecto
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM convocatorias
            WHERE partido_id = %s AND (equipo = 'Equipo A' OR equipo = 'Equipo B');
        """, (partido_id,))
        
        result = cursor.fetchone()
        count_wrong = result['count'] if isinstance(result, dict) else result[0]
        
        if count_wrong > 0:
            print(f"\n   📋 Partido {partido_id}:")
            print(f"      Equipo A debería ser: '{equipo_a}'")
            print(f"      Equipo B debería ser: '{equipo_b}'")
            print(f"      Convocatorias a arreglar: {count_wrong}")
            
            # Arreglar Equipo A
            cursor.execute("""
                UPDATE convocatorias
                SET equipo = %s
                WHERE partido_id = %s AND equipo = 'Equipo A';
            """, (equipo_a, partido_id))
            fixes_a = cursor.rowcount
            
            # Arreglar Equipo B
            cursor.execute("""
                UPDATE convocatorias
                SET equipo = %s
                WHERE partido_id = %s AND equipo = 'Equipo B';
            """, (equipo_b, partido_id))
            fixes_b = cursor.rowcount
            
            fixes_this_match = fixes_a + fixes_b
            total_fixes += fixes_this_match
            print(f"      ✓ Arregladas {fixes_this_match} convocatorias")
    
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"✨ Total de convocatorias arregladas: {total_fixes}")
    print(f"✓ Migración completada exitosamente")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
