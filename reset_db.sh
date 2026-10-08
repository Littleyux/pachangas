#!/bin/bash

echo "Reseteando base de datos Pachangas..."
echo ""

# Conectar a PostgreSQL y ejecutar reset
psql -U dev_user -d pachangas_db -h localhost << 'SQL'

-- Eliminar tablas existentes (cascada)
DROP TABLE IF EXISTS convocatorias CASCADE;
DROP TABLE IF EXISTS partidos CASCADE;
DROP TABLE IF EXISTS campos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- Recrear tablas
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    posicion_habitual VARCHAR(50),
    nivel DECIMAL(3,1) DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE campos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    tipo_superficie VARCHAR(50),
    modalidad VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE convocatorias (
    id SERIAL PRIMARY KEY,
    partido_id INT REFERENCES partidos(id) ON DELETE CASCADE,
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    equipo VARCHAR(10) DEFAULT 'Sin Asignar',
    asistencia_confirmada BOOLEAN DEFAULT TRUE,
    pago_realizado BOOLEAN DEFAULT FALSE,
    UNIQUE(partido_id, usuario_id)
);

-- Insertar datos de prueba
INSERT INTO usuarios (nombre, email, posicion_habitual, nivel) VALUES
('Juan García', 'juan@example.com', 'Delantero', 8.5),
('Carlos López', 'carlos@example.com', 'Centrocampista', 7.0),
('Miguel Rodríguez', 'miguel@example.com', 'Defensa', 6.5),
('Antonio Sánchez', 'antonio@example.com', 'Portero', 9.0),
('Pablo Fernández', 'pablo@example.com', 'Delantero', 7.5),
('David Martínez', 'david@example.com', 'Centrocampista', 8.0);

INSERT INTO campos (nombre, direccion, tipo_superficie, modalidad) VALUES
('Polideportivo Municipal', 'Calle Principal 123', 'Césped Artificial', 'F11'),
('Pabellón Los Ángeles', 'Av. del Deporte 45', 'Pista', 'F5'),
('Campo San Pedro', 'Plaza Mayor 10', 'Césped Natural', 'F7');

INSERT INTO partidos (campo_id, creador_id, fecha_hora, max_jugadores, precio_total, estado) VALUES
(1, 1, '2024-12-20 18:00:00', 11, 100.00, 'abierto'),
(2, 2, '2024-12-21 19:00:00', 5, 40.00, 'abierto'),
(3, 3, '2024-12-22 17:30:00', 7, 60.00, 'abierto');

-- Insertar inscripciones de prueba
INSERT INTO convocatorias (partido_id, usuario_id, equipo, asistencia_confirmada) VALUES
(1, 2, 'Sin Asignar', TRUE),
(1, 4, 'Sin Asignar', TRUE),
(2, 3, 'Sin Asignar', TRUE),
(3, 5, 'Sin Asignar', TRUE);

SQL

echo "✓ Base de datos reseteada y poblada con datos de prueba"
echo ""
echo "Datos de prueba:"
echo "- 6 usuarios registrados"
echo "- 3 campos registrados"
echo "- 3 partidos creados"
echo "- 4 inscripciones de prueba"

