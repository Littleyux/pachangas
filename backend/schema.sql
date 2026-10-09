-- 1. Tabla de Usuarios / Jugadores
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    posicion_habitual VARCHAR(50), -- 'Portero', 'Defensa', 'Centrocampista', 'Delantero'
    nivel DECIMAL(3,1) DEFAULT 5.0,  -- De 1.0 a 10.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Instalaciones / Campos
CREATE TABLE IF NOT EXISTS campos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    tipo_superficie VARCHAR(50), -- 'Césped Artificial', 'Césped Natural', 'Pista'
    modalidad VARCHAR(20),        -- 'F5', 'F7', 'F8', 'F11'
    tipo_deporte VARCHAR(50) DEFAULT 'futbol', -- 'futbol', 'padel', 'tenis', 'bicicleta', 'montana'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Partidos
CREATE TABLE IF NOT EXISTS partidos (
    id SERIAL PRIMARY KEY,
    campo_id INT REFERENCES campos(id),
    creador_id INT REFERENCES usuarios(id),
    fecha_hora TIMESTAMP NOT NULL,
    max_jugadores INT DEFAULT 10,
    precio_total DECIMAL(6,2),
    equipo_a_nombre VARCHAR(100) DEFAULT 'Equipo A',
    equipo_b_nombre VARCHAR(100) DEFAULT 'Equipo B',
    tipo_deporte VARCHAR(50) DEFAULT 'futbol', -- 'futbol', 'padel', 'tenis', 'bicicleta', 'montana'
    equipo_obligatorio BOOLEAN DEFAULT true, -- true si requiere equipos, false si es grupo
    modalidad_tenis VARCHAR(20), -- '1v1' o '2v2', NULL si no es tenis
    estado VARCHAR(20) DEFAULT 'abierto', -- 'abierto', 'completo', 'finalizado', 'cancelado'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de Convocados (Relación Muchos a Muchos)
CREATE TABLE IF NOT EXISTS convocatorias (
    id SERIAL PRIMARY KEY,
    partido_id INT REFERENCES partidos(id) ON DELETE CASCADE,
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    equipo VARCHAR(20) DEFAULT 'Sin Asignar', -- 'Equipo A', 'Equipo B', 'Sin Asignar'
    asistencia_confirmada BOOLEAN DEFAULT TRUE,
    pago_realizado BOOLEAN DEFAULT FALSE,
    UNIQUE(partido_id, usuario_id)
);