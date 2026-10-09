-- ============================================
-- MIGRACIÓN PARA SOPORTE MULTI-DEPORTE EN NEON
-- ============================================
-- Ejecuta este script en tu base de datos Neon
-- para agregar soporte a múltiples deportes
-- ============================================

-- 1. Agregar columna tipo_deporte a tabla campos
ALTER TABLE campos 
ADD COLUMN IF NOT EXISTS tipo_deporte VARCHAR(50) DEFAULT 'futbol';

-- 2. Agregar columnas a tabla partidos
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS tipo_deporte VARCHAR(50) DEFAULT 'futbol',
ADD COLUMN IF NOT EXISTS equipo_obligatorio BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS modalidad_tenis VARCHAR(20);

-- 3. Verificar que las columnas se agregaron correctamente
-- (Ejecuta esto para verificar)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('campos', 'partidos') 
ORDER BY table_name, ordinal_position;

-- 4. Actualizar campos existentes a tipo 'futbol'
-- (Todos los campos históricos se consideran de fútbol)
UPDATE campos SET tipo_deporte = 'futbol' WHERE tipo_deporte IS NULL;

-- ============================================
-- VERIFICACIÓN: Comprobar que todo está bien
-- ============================================

-- Verificar campos
SELECT id, nombre, tipo_deporte FROM campos ORDER BY id;

-- Verificar partidos
SELECT id, equipo_a_nombre, tipo_deporte, equipo_obligatorio, modalidad_tenis FROM partidos ORDER BY id;

-- Si todo se ve bien, la migración fue exitosa ✅
