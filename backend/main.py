from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal
from db import get_db_connection

app = FastAPI(title="Pachangas API")

# Habilitar CORS para que React/Angular en el frontend pueda consultar la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema de validación para crear usuario
class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    posicion_habitual: Optional[str] = None
    nivel: Optional[float] = 5.0

# Esquema de validación para crear campo
class CampoCreate(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    tipo_superficie: str
    modalidad: Optional[str] = None  # Ya no es Literal, puede ser cualquier string
    tipo_deporte: str = "futbol"  # 'futbol', 'padel', 'tenis', 'bicicleta', 'montana'

# Esquema de validación para crear partido
class PartidoCreate(BaseModel):
    campo_id: Optional[int] = None
    titulo: str  # NUEVO - obligatorio
    fecha_hora: str  # ISO format: "2024-12-15T18:00:00"
    max_jugadores: Optional[int] = 10
    precio_total: Optional[float] = None
    equipo_a_nombre: Optional[str] = "Equipo A"
    equipo_b_nombre: Optional[str] = "Equipo B"
    tipo_deporte: str = "futbol"  # 'futbol', 'padel', 'tenis', 'bicicleta', 'montana'
    equipo_obligatorio: bool = True  # true si requiere equipos
    modalidad_tenis: Optional[str] = None  # '1v1' o '2v2' si tipo_deporte='tenis'
    # NUEVOS - para bicicleta/montana
    ruta_origen: Optional[str] = None
    ruta_destino: Optional[str] = None
    ruta_distancia_km: Optional[float] = None
    ruta_duracion_minutos: Optional[int] = None
    ruta_desnivel_metros: Optional[int] = None

class PartidoUpdate(BaseModel):
    estado: Optional[Literal["abierto", "completo", "finalizado", "cancelado"]] = None
    max_jugadores: Optional[int] = None
    precio_total: Optional[float] = None

# Esquema de validación para inscripción a partido
class ConvocatoriaCreate(BaseModel):
    usuario_id: int
    equipo: Optional[str] = "Sin Asignar"  # Cambié de Literal a str para aceptar nombres personalizados
    asistencia_confirmada: Optional[bool] = True

class ConvocatoriaUpdate(BaseModel):
    equipo: Optional[str] = None
    asistencia_confirmada: Optional[bool] = None
    pago_realizado: Optional[bool] = None

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend en FastAPI corriendo correctamente"}

# Endpoint: Obtener todos los usuarios
@app.get("/api/usuarios")
def obtener_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM usuarios ORDER BY id DESC;")
        usuarios = cursor.fetchall()
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Crear un nuevo usuario
@app.post("/api/usuarios", status_code=201)
def crear_usuario(usuario: UsuarioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, posicion_habitual, nivel)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """,
            (usuario.nombre, usuario.email, usuario.posicion_habitual, usuario.nivel)
        )
        nuevo_usuario = cursor.fetchone()
        conn.commit()
        return nuevo_usuario
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ============== ENDPOINTS DE CAMPOS ==============

# Endpoint: Obtener todos los campos (con filtro opcional por deporte)
@app.get("/api/campos")
def obtener_campos(tipo_deporte: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if tipo_deporte:
            cursor.execute(
                "SELECT * FROM campos WHERE tipo_deporte = %s ORDER BY id DESC;",
                (tipo_deporte,)
            )
        else:
            cursor.execute("SELECT * FROM campos ORDER BY id DESC;")
        campos = cursor.fetchall()
        return campos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Obtener un campo por ID
@app.get("/api/campos/{campo_id}")
def obtener_campo(campo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM campos WHERE id = %s;", (campo_id,))
        campo = cursor.fetchone()
        if not campo:
            raise HTTPException(status_code=404, detail="Campo no encontrado")
        return campo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Crear un nuevo campo
@app.post("/api/campos", status_code=201)
def crear_campo(campo: CampoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO campos (nombre, direccion, tipo_superficie, modalidad, tipo_deporte)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (campo.nombre, campo.direccion, campo.tipo_superficie, campo.modalidad, campo.tipo_deporte)
        )
        nuevo_campo = cursor.fetchone()
        conn.commit()
        return nuevo_campo
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear campo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Endpoint: Actualizar un campo
@app.put("/api/campos/{campo_id}")
def actualizar_campo(campo_id: int, campo: CampoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE campos
            SET nombre = %s, direccion = %s, tipo_superficie = %s, modalidad = %s
            WHERE id = %s
            RETURNING *;
            """,
            (campo.nombre, campo.direccion, campo.tipo_superficie, campo.modalidad, campo_id)
        )
        campo_actualizado = cursor.fetchone()
        if not campo_actualizado:
            raise HTTPException(status_code=404, detail="Campo no encontrado")
        conn.commit()
        return campo_actualizado
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar campo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Endpoint: Eliminar un campo
@app.delete("/api/campos/{campo_id}", status_code=204)
def eliminar_campo(campo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM campos WHERE id = %s;", (campo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Campo no encontrado")
        conn.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar campo: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ============== ENDPOINTS DE PARTIDOS ==============

# Endpoint: Obtener todos los partidos (con filtro opcional por deporte)
@app.get("/api/partidos")
def obtener_partidos(tipo_deporte: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if tipo_deporte:
            cursor.execute(
                """
                SELECT p.*, c.nombre as campo_nombre, c.modalidad, u.nombre as creador_nombre
                FROM partidos p
                LEFT JOIN campos c ON p.campo_id = c.id
                LEFT JOIN usuarios u ON p.creador_id = u.id
                WHERE p.tipo_deporte = %s
                ORDER BY p.fecha_hora DESC;
                """,
                (tipo_deporte,)
            )
        else:
            cursor.execute(
                """
                SELECT p.*, c.nombre as campo_nombre, c.modalidad, u.nombre as creador_nombre
                FROM partidos p
                LEFT JOIN campos c ON p.campo_id = c.id
                LEFT JOIN usuarios u ON p.creador_id = u.id
                ORDER BY p.fecha_hora DESC;
                """
            )
        partidos = cursor.fetchall()
        return partidos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Obtener un partido por ID
@app.get("/api/partidos/{partido_id}")
def obtener_partido(partido_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.*, c.nombre as campo_nombre, c.modalidad, u.nombre as creador_nombre
            FROM partidos p
            LEFT JOIN campos c ON p.campo_id = c.id
            LEFT JOIN usuarios u ON p.creador_id = u.id
            WHERE p.id = %s;
            """,
            (partido_id,)
        )
        partido = cursor.fetchone()
        if not partido:
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        return partido
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Crear un nuevo partido
@app.post("/api/partidos", status_code=201)
def crear_partido(partido: PartidoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Por ahora, creador_id se asigna como 1 (en futuro, vendría del token JWT)
        cursor.execute(
            """
            INSERT INTO partidos (campo_id, creador_id, titulo, fecha_hora, max_jugadores, precio_total, equipo_a_nombre, equipo_b_nombre, tipo_deporte, equipo_obligatorio, modalidad_tenis, ruta_origen, ruta_destino, ruta_distancia_km, ruta_duracion_minutos, ruta_desnivel_metros, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'abierto')
            RETURNING *;
            """,
            (partido.campo_id, 1, partido.titulo, partido.fecha_hora, partido.max_jugadores, partido.precio_total, partido.equipo_a_nombre, partido.equipo_b_nombre, partido.tipo_deporte, partido.equipo_obligatorio, partido.modalidad_tenis, partido.ruta_origen, partido.ruta_destino, partido.ruta_distancia_km, partido.ruta_duracion_minutos, partido.ruta_desnivel_metros)
        )
        nuevo_partido = cursor.fetchone()
        conn.commit()
        
        # Obtener datos completos con joins
        cursor.execute(
            """
            SELECT p.*, c.nombre as campo_nombre, c.modalidad, u.nombre as creador_nombre
            FROM partidos p
            LEFT JOIN campos c ON p.campo_id = c.id
            LEFT JOIN usuarios u ON p.creador_id = u.id
            WHERE p.id = %s;
            """,
            (nuevo_partido['id'],)
        )
        partido_completo = cursor.fetchone()
        return partido_completo
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear partido: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Endpoint: Actualizar un partido
@app.put("/api/partidos/{partido_id}")
def actualizar_partido(partido_id: int, partido: PartidoUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Construir UPDATE dinámico
        updates = []
        params = []
        
        if partido.estado:
            updates.append("estado = %s")
            params.append(partido.estado)
        if partido.max_jugadores:
            updates.append("max_jugadores = %s")
            params.append(partido.max_jugadores)
        if partido.precio_total is not None:
            updates.append("precio_total = %s")
            params.append(partido.precio_total)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        params.append(partido_id)
        
        cursor.execute(
            f"""
            UPDATE partidos
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING *;
            """,
            params
        )
        partido_actualizado = cursor.fetchone()
        if not partido_actualizado:
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        conn.commit()
        return partido_actualizado
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar partido: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Endpoint: Eliminar un partido
@app.delete("/api/partidos/{partido_id}", status_code=204)
def eliminar_partido(partido_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM partidos WHERE id = %s;", (partido_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        conn.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar partido: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ============== ENDPOINTS DE CONVOCATORIAS (INSCRIPCIONES) ==============

# Endpoint: Obtener jugadores inscritos en un partido
@app.get("/api/partidos/{partido_id}/convocatorias")
def obtener_convocatorias(partido_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT c.*, u.nombre, u.email, u.posicion_habitual, u.nivel
            FROM convocatorias c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.partido_id = %s
            ORDER BY c.id ASC;
            """,
            (partido_id,)
        )
        convocatorias = cursor.fetchall()
        return convocatorias
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint: Inscribir usuario a un partido
@app.post("/api/partidos/{partido_id}/convocatorias", status_code=201)
def crear_convocatoria(partido_id: int, convocatoria: ConvocatoriaCreate):
    print(f"\n{'='*60}")
    print(f"[CREATE CONVOCATORIA] Inicio - Partido: {partido_id}, Usuario: {convocatoria.usuario_id}")
    print(f"{'='*60}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f"[1] Conexión abierta, cursor type: {type(cursor)}")
        
        # Verificar que el partido existe
        print(f"[2] Verificando que partido {partido_id} existe...")
        cursor.execute("SELECT id FROM partidos WHERE id = %s;", (partido_id,))
        partido_check = cursor.fetchone()
        print(f"[2] Resultado: {partido_check}")
        if not partido_check:
            print(f"[ERROR] Partido {partido_id} no encontrado")
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        
        # Verificar que el usuario existe
        print(f"[3] Verificando que usuario {convocatoria.usuario_id} existe...")
        cursor.execute("SELECT id FROM usuarios WHERE id = %s;", (convocatoria.usuario_id,))
        usuario_check = cursor.fetchone()
        print(f"[3] Resultado: {usuario_check}")
        if not usuario_check:
            print(f"[ERROR] Usuario {convocatoria.usuario_id} no encontrado")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el usuario no está ya inscrito
        print(f"[4] Verificando duplicado...")
        cursor.execute(
            "SELECT id FROM convocatorias WHERE partido_id = %s AND usuario_id = %s;",
            (partido_id, convocatoria.usuario_id)
        )
        duplicado = cursor.fetchone()
        print(f"[4] Resultado: {duplicado}")
        if duplicado:
            print(f"[ERROR] Usuario ya inscrito")
            raise HTTPException(status_code=400, detail="El usuario ya está inscrito en este partido")
        
        # Insertar inscripción
        print(f"[5] Insertando convocatoria...")
        cursor.execute(
            """
            INSERT INTO convocatorias (partido_id, usuario_id, equipo, asistencia_confirmada)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (partido_id, convocatoria.usuario_id, convocatoria.equipo, convocatoria.asistencia_confirmada)
        )
        result = cursor.fetchone()
        print(f"[5] Result type: {type(result)}, Value: {result}")
        
        nueva_convocatoria_id = result['id'] if isinstance(result, dict) else result[0]
        print(f"[5] Nueva convocatoria ID: {nueva_convocatoria_id}")
        
        conn.commit()
        print(f"[6] Commit realizado")
        
        # Obtener datos completos con info del usuario (con mismo cursor RealDictCursor)
        print(f"[7] Obteniendo datos completos...")
        cursor.execute(
            """
            SELECT c.*, u.nombre, u.email, u.posicion_habitual, u.nivel
            FROM convocatorias c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = %s;
            """,
            (nueva_convocatoria_id,)
        )
        convocatoria_completa = cursor.fetchone()
        print(f"[7] Datos completos obtenidos: {convocatoria_completa}")
        
        print(f"[SUCCESS] Convocatoria creada exitosamente")
        print(f"{'='*60}\n")
        return convocatoria_completa
        
    except HTTPException:
        print(f"[HTTPException] Lanzada")
        raise
    except Exception as e:
        conn.rollback()
        print(f"[EXCEPTION] Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Error al inscribir: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        print(f"[CLEANUP] Conexión cerrada")

# Endpoint: Cancelar inscripción de usuario a un partido
@app.delete("/api/partidos/{partido_id}/convocatorias/{usuario_id}", status_code=204)
def eliminar_convocatoria(partido_id: int, usuario_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM convocatorias WHERE partido_id = %s AND usuario_id = %s;",
            (partido_id, usuario_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        conn.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cancelar inscripción: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Endpoint: Actualizar inscripción (equipo, asistencia, pago)
@app.put("/api/partidos/{partido_id}/convocatorias/{usuario_id}")
def actualizar_convocatoria(partido_id: int, usuario_id: int, convocatoria: ConvocatoriaUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Construir UPDATE dinámico
        updates = []
        params = []
        
        if convocatoria.equipo:
            updates.append("equipo = %s")
            params.append(convocatoria.equipo)
        if convocatoria.asistencia_confirmada is not None:
            updates.append("asistencia_confirmada = %s")
            params.append(convocatoria.asistencia_confirmada)
        if convocatoria.pago_realizado is not None:
            updates.append("pago_realizado = %s")
            params.append(convocatoria.pago_realizado)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        params.extend([partido_id, usuario_id])
        
        cursor.execute(
            f"""
            UPDATE convocatorias
            SET {', '.join(updates)}
            WHERE partido_id = %s AND usuario_id = %s
            RETURNING *;
            """,
            params
        )
        convocatoria_actualizada = cursor.fetchone()
        if not convocatoria_actualizada:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        conn.commit()
        return convocatoria_actualizada
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar inscripción: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ========== ADMIN ENDPOINTS ==========

# Endpoint: Limpiar nombres de equipos en convocatorias (arreglar valores por defecto)
@app.post("/api/admin/fix-team-names")
def fix_team_names():
    """
    Arregla convocatorias que tienen 'Equipo A' o 'Equipo B' como valores por defecto,
    cuando deberían tener los nombres custom del partido.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("\n" + "="*60)
        print("INICIANDO LIMPIEZA DE NOMBRES DE EQUIPOS")
        print("="*60)
        
        # Obtener todos los partidos con nombres custom
        cursor.execute("""
            SELECT id, equipo_a_nombre, equipo_b_nombre 
            FROM partidos 
            WHERE equipo_a_nombre IS NOT NULL 
            OR equipo_b_nombre IS NOT NULL;
        """)
        partidos = cursor.fetchall()
        print(f"\n[1] Encontrados {len(partidos)} partidos con nombres custom")
        
        total_fixes = 0
        fixes_per_partido = {}
        
        for partido_data in partidos:
            if isinstance(partido_data, dict):
                partido_id = partido_data['id']
                equipo_a = partido_data['equipo_a_nombre']
                equipo_b = partido_data['equipo_b_nombre']
            else:
                partido_id = partido_data[0]
                equipo_a = partido_data[1]
                equipo_b = partido_data[2]
            
            # Verificar cuántas convocatorias tienen valores por defecto
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM convocatorias
                WHERE partido_id = %s AND (equipo = 'Equipo A' OR equipo = 'Equipo B');
            """, (partido_id,))
            
            result = cursor.fetchone()
            count_wrong = result['count'] if isinstance(result, dict) else result[0]
            
            if count_wrong > 0:
                print(f"\n   📋 Partido {partido_id}:")
                print(f"      Teams: '{equipo_a}' vs '{equipo_b}'")
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
                
                fixes_this = fixes_a + fixes_b
                total_fixes += fixes_this
                fixes_per_partido[partido_id] = fixes_this
                print(f"      ✓ {fixes_this} convocatorias arregladas")
        
        conn.commit()
        
        print(f"\n{'='*60}")
        print(f"✨ TOTAL ARREGLADAS: {total_fixes} convocatorias")
        print(f"✓ LIMPIEZA COMPLETADA")
        print("="*60 + "\n")
        
        return {
            "success": True,
            "total_fixed": total_fixes,
            "partidos_fixed": fixes_per_partido
        }
        
    except Exception as e:
        conn.rollback()
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al limpiar equipos: {str(e)}")
    finally:
        cursor.close()
        conn.close()
from datetime import datetime, timedelta
import jwt
import bcrypt
from fastapi import Depends, Header

# ============================================
# CONFIGURACIÓN DE JWT
# ============================================
SECRET_KEY = "pachangas-secret-key-change-in-production"  # En producción usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# ============================================
# MODELOS DE AUTENTICACIÓN
# ============================================
class UsuarioLogin(BaseModel):
    email: str
    password: Optional[str] = None
    google_token: Optional[str] = None

class UsuarioLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

# ============================================
# FUNCIONES DE AUXILIAR DE AUTH
# ============================================
def hash_password(password: str) -> str:
    """Hashear password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verificar password contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decodificar token JWT"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================

@app.post("/api/auth/register", status_code=201)
def register_usuario(usuario: UsuarioCreate):
    """Registrar nuevo usuario con email y password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el email ya existe
        cursor.execute("SELECT id, email, password_hash FROM usuarios WHERE email = %s;", (usuario.email,))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Hashear password
        password_hash = hash_password("password123")  # Temporal - usar generated password
        
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, posicion_habitual, nivel, password_hash)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nombre, email, posicion_habitual, nivel, created_at;
            """,
            (usuario.nombre, usuario.email, usuario.posicion_habitual, usuario.nivel, password_hash)
        )
        nuevo_usuario = cursor.fetchone()
        conn.commit()
        
        # Crear token
        access_token = create_access_token(data={"sub": str(nuevo_usuario['id'])})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": nuevo_usuario['id'],
                "nombre": nuevo_usuario['nombre'],
                "email": nuevo_usuario['email']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/auth/login")
def login_usuario(usuario_login: UsuarioLogin):
    """Login con email y password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nombre, email, password_hash FROM usuarios WHERE email = %s;",
            (usuario_login.email,)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Verificar password
        if usuario['password_hash'] is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        if not verify_password(usuario_login.password, usuario['password_hash']):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Actualizar último login
        cursor.execute(
            "UPDATE usuarios SET last_login = NOW() WHERE id = %s;",
            (usuario['id'],)
        )
        conn.commit()
        
        # Crear token
        access_token = create_access_token(data={"sub": str(usuario['id'])})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario['id'],
                "nombre": usuario['nombre'],
                "email": usuario['email']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al login: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/auth/google")
def login_google(google_token: str):
    """Login con Google OAuth"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # En producción, verificar el token con Google API
        # Aquí asumimos que el token es válido y extraemos email
        # Para desarrollo, aceptamos cualquier token con email dummy
        import json
        import base64
        
        try:
            # Decodificar payload del JWT de Google
            payload_parts = google_token.split('.')
            if len(payload_parts) >= 2:
                payload = json.loads(base64.urlsafe_b64decode(payload_parts[1] + '=='))
                email = payload.get('email')
                name = payload.get('name', '')
                picture = payload.get('picture', '')
                
                if not email:
                    raise HTTPException(status_code=400, detail="No se pudo extraer email del token de Google")
            else:
                raise HTTPException(status_code=400, detail="Token de Google inválido")
        except Exception:
            raise HTTPException(status_code=400, detail="Token de Google inválido")
        
        # Buscar usuario por google_id o email
        cursor.execute("SELECT * FROM usuarios WHERE email = %s;", (email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            # Crear nuevo usuario
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, google_id, google_photo_url, last_login)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING *;
                """,
                (name or email.split('@')[0], email, email, picture)
            )
            usuario = cursor.fetchone()
            conn.commit()
        
        # Actualizar último login
        cursor.execute(
            "UPDATE usuarios SET last_login = NOW() WHERE id = %s;",
            (usuario['id'],)
        )
        conn.commit()
        
        # Crear token
        access_token = create_access_token(data={"sub": str(usuario['id'])})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario['id'],
                "nombre": usuario['nombre'],
                "email": usuario['email'],
                "google_photo_url": usuario.get('google_photo_url')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al login con Google: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/auth/me")
def obtener_usuario_actual(authorization: Optional[str] = Header(None)):
    """Obtener información del usuario actual desde el token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización no proporcionado")
    
    token = authorization.split(" ")[1]
    
    try:
        payload = decode_token(token)
        usuario_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nombre, email, posicion_habitual, nivel, google_photo_url, last_login FROM usuarios WHERE id = %s;",
            (usuario_id,)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
