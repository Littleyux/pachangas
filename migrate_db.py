#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, '/home/alberto/pachangas/backend')

from db import get_db_connection
from dotenv import load_dotenv

load_dotenv('/home/alberto/pachangas/backend/.env')

print("Migrando base de datos Pachangas...")
print("")

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    print("[1] Verificando columnas en tabla 'partidos'...")
    
    # Verificar si la columna equipo_a_nombre existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='partidos' AND column_name='equipo_a_nombre'
        );
    """)
    result = cursor.fetchone()
    equipo_a_exists = result['exists'] if isinstance(result, dict) else result[0]
    
    if not equipo_a_exists:
        print("[2] Añadiendo columna 'equipo_a_nombre'...")
        cursor.execute("""
            ALTER TABLE partidos 
            ADD COLUMN equipo_a_nombre VARCHAR(100) DEFAULT 'Equipo A';
        """)
        print("    ✓ Columna 'equipo_a_nombre' añadida")
    else:
        print("    ✓ Columna 'equipo_a_nombre' ya existe")
    
    # Verificar si la columna equipo_b_nombre existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='partidos' AND column_name='equipo_b_nombre'
        );
    """)
    result = cursor.fetchone()
    equipo_b_exists = result['exists'] if isinstance(result, dict) else result[0]
    
    if not equipo_b_exists:
        print("[3] Añadiendo columna 'equipo_b_nombre'...")
        cursor.execute("""
            ALTER TABLE partidos 
            ADD COLUMN equipo_b_nombre VARCHAR(100) DEFAULT 'Equipo B';
        """)
        print("    ✓ Columna 'equipo_b_nombre' añadida")
    else:
        print("    ✓ Columna 'equipo_b_nombre' ya existe")
    
    conn.commit()
    cursor.close()
    conn.close()

    print("")
    print("✓ Migración completada exitosamente")

except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
