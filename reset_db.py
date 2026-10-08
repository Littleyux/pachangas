#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, '/home/alberto/pachangas/backend')

from db import get_db_connection
from dotenv import load_dotenv

load_dotenv('/home/alberto/pachangas/backend/.env')

print("Reseteando base de datos Pachangas...")
print("")

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Eliminar tablas existentes
    cursor.execute("DROP TABLE IF EXISTS convocatorias CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS partidos CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS campos CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS usuarios CASCADE;")

    # Crear tablas
    cursor.execute("""
        CREATE TABLE usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            posicion_habitual VARCHAR(50),
            nivel DECIMAL(3,1) DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE campos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            direccion VARCHAR(255),
            tipo_superficie VARCHAR(50),
            modalidad VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE partidos (
            id SERIAL PRIMARY KEY,
            campo_id INT REFERENCES campos(id),
            creador_id INT REFERENCES usuarios(id),
            fecha_hora TIMESTAMP NOT NULL,
            max_jugadores INT DEFAULT 10,
            precio_total DECIMAL(6,2),
            estado VARCHAR(20) DEFAULT 'abierto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE convocatorias (
            id SERIAL PRIMARY KEY,
            partido_id INT REFERENCES partidos(id) ON DELETE CASCADE,
            usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
            equipo VARCHAR(20) DEFAULT 'Sin Asignar',
            asistencia_confirmada BOOLEAN DEFAULT TRUE,
            pago_realizado BOOLEAN DEFAULT FALSE,
            UNIQUE(partido_id, usuario_id)
        );
    """)

    # Insertar datos de prueba - Usuarios
    usuarios_data = [
        ('Juan García', 'juan@example.com', 'Delantero', 8.5),
        ('Carlos López', 'carlos@example.com', 'Centrocampista', 7.0),
        ('Miguel Rodríguez', 'miguel@example.com', 'Defensa', 6.5),
        ('Antonio Sánchez', 'antonio@example.com', 'Portero', 9.0),
        ('Pablo Fernández', 'pablo@example.com', 'Delantero', 7.5),
        ('David Martínez', 'david@example.com', 'Centrocampista', 8.0),
    ]

    for nombre, email, posicion, nivel in usuarios_data:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, posicion_habitual, nivel) VALUES (%s, %s, %s, %s);",
            (nombre, email, posicion, nivel)
        )

    # Insertar datos de prueba - Campos
    campos_data = [
        ('Polideportivo Municipal', 'Calle Principal 123', 'Césped Artificial', 'F11'),
        ('Pabellón Los Ángeles', 'Av. del Deporte 45', 'Pista', 'F5'),
        ('Campo San Pedro', 'Plaza Mayor 10', 'Césped Natural', 'F7'),
    ]

    for nombre, direccion, superficie, modalidad in campos_data:
        cursor.execute(
            "INSERT INTO campos (nombre, direccion, tipo_superficie, modalidad) VALUES (%s, %s, %s, %s);",
            (nombre, direccion, superficie, modalidad)
        )

    # Insertar datos de prueba - Partidos
    partidos_data = [
        (1, 1, '2024-12-20 18:00:00', 11, 100.00),
        (2, 2, '2024-12-21 19:00:00', 5, 40.00),
        (3, 3, '2024-12-22 17:30:00', 7, 60.00),
    ]

    for campo_id, creador_id, fecha_hora, max_jugadores, precio in partidos_data:
        cursor.execute(
            "INSERT INTO partidos (campo_id, creador_id, fecha_hora, max_jugadores, precio_total) VALUES (%s, %s, %s, %s, %s);",
            (campo_id, creador_id, fecha_hora, max_jugadores, precio)
        )

    # Insertar inscripciones de prueba
    inscripciones_data = [
        (1, 2),
        (1, 4),
        (2, 3),
        (3, 5),
    ]

    for partido_id, usuario_id in inscripciones_data:
        cursor.execute(
            "INSERT INTO convocatorias (partido_id, usuario_id) VALUES (%s, %s);",
            (partido_id, usuario_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✓ Base de datos reseteada y poblada con datos de prueba")
    print("")
    print("Datos creados:")
    print("- 6 usuarios registrados")
    print("- 3 campos registrados")
    print("- 3 partidos creados")
    print("- 4 inscripciones de prueba")
    print("")
    print("Ahora recarga la página del navegador (Ctrl+F5)")

except Exception as e:
    print(f"✗ Error: {str(e)}")
    sys.exit(1)

