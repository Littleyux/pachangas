-- ============================================
-- MIGRACIÓN PARA SOPORTE MULTI-DEPORTE EN NEON
-- Octubre 2026
-- ============================================
-- INSTRUCCIONES:
-- 1. Conecta a tu base de datos Neon
-- 2. Abre el editor SQL de la consola Neon
-- 3. Copia y pega este script completo
-- 4. Ejecuta línea por línea o todo junto
-- 5. Verifica que todas las columnas se agregaron correctamente
-- ============================================

-- ============================================
-- PASO 1: Agregar columnas a tabla CAMPOS
-- ============================================
-- Agregar columna tipo_deporte (para identificar qué deporte es)
ALTER TABLE campos 
ADD COLUMN IF NOT EXISTS tipo_deporte VARCHAR(50) DEFAULT 'futbol';

-- ============================================
-- PASO 2: Agregar columnas a tabla PARTIDOS
-- ============================================

-- 2.1 Agregar título (obligatorio para todos los eventos)
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS titulo VARCHAR(200) NOT NULL DEFAULT 'Evento sin título';

-- 2.2 Agregar tipo_deporte (futbol, padel, tenis, bicicleta, montana)
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS tipo_deporte VARCHAR(50) DEFAULT 'futbol';

-- 2.3 Agregar equipo_obligatorio (true si requiere equipos, false si es grupo)
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS equipo_obligatorio BOOLEAN DEFAULT true;

-- 2.4 Agregar modalidad_tenis ('1v1' o '2v2', NULL si no es tenis)
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS modalidad_tenis VARCHAR(20);

-- 2.5 Agregar campos para rutas (bicicleta/montaña)
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ruta_origen VARCHAR(150);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ruta_destino VARCHAR(150);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ruta_distancia_km DECIMAL(5,2);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ruta_duracion_minutos INT;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ruta_desnivel_metros INT;

-- ============================================
-- PASO 3: OPCIONAL - Hacer campo_id nullable
-- ============================================
-- Si tus partidos de bicicleta/montaña no usan campo_id,
-- descomenta la siguiente línea para permitir NULL:
-- ALTER TABLE partidos 
-- ALTER COLUMN campo_id DROP NOT NULL;

-- ============================================
-- PASO 4: Actualizar datos existentes
-- ============================================

-- Asegurar que todos los campos antiguos sean tipo 'futbol'
UPDATE campos SET tipo_deporte = 'futbol' WHERE tipo_deporte IS NULL;

-- Asegurar que todos los partidos antiguos sean tipo 'futbol'
UPDATE partidos SET tipo_deporte = 'futbol' WHERE tipo_deporte IS NULL;

-- Asegurar que los partidos antiguos tengan equipo_obligatorio = true
UPDATE partidos SET equipo_obligatorio = true WHERE equipo_obligatorio IS NULL;

-- Remover valores por defecto del titulo para que sea realmente NOT NULL
UPDATE partidos SET titulo = COALESCE(titulo, campo_id::text || ' - Evento') WHERE titulo IS NULL OR titulo = 'Evento sin título';

-- ============================================
-- PASO 5: VERIFICACIÓN - Ejecuta después de la migración
-- ============================================

-- Ver estructura de tabla CAMPOS
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'campos' 
ORDER BY ordinal_position;

-- Ver estructura de tabla PARTIDOS
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'partidos' 
ORDER BY ordinal_position;

-- Ver un resumen de datos después de migración
SELECT 
  'CAMPOS' as tabla,
  COUNT(*) as total_registros,
  COUNT(DISTINCT tipo_deporte) as deportes_distintos
FROM campos
UNION ALL
SELECT 
  'PARTIDOS' as tabla,
  COUNT(*) as total_registros,
  COUNT(DISTINCT tipo_deporte) as deportes_distintos
FROM partidos;

-- Mostrar ejemplos de cada tipo de deporte en partidos
SELECT 
  id, 
  titulo, 
  tipo_deporte, 
  campo_id,
  ruta_origen,
  ruta_destino
FROM partidos 
ORDER BY tipo_deporte, id
LIMIT 20;

-- ============================================
-- ✅ SI LLEGASTE AQUÍ, LA MIGRACIÓN FUE EXITOSA
-- ============================================
-- Siguiente paso: Recarga la aplicación en el navegador
-- Los nuevos campos estarán disponibles de inmediato
