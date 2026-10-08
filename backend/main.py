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
    modalidad: Optional[Literal["F5", "F7", "F8", "F11"]] = None

# Esquema de validación para crear partido
class PartidoCreate(BaseModel):
    campo_id: int
    fecha_hora: str  # ISO format: "2024-12-15T18:00:00"
    max_jugadores: Optional[int] = 10
    precio_total: Optional[float] = None

class PartidoUpdate(BaseModel):
    estado: Optional[Literal["abierto", "completo", "finalizado", "cancelado"]] = None
    max_jugadores: Optional[int] = None
    precio_total: Optional[float] = None

# Esquema de validación para inscripción a partido
class ConvocatoriaCreate(BaseModel):
    usuario_id: int
    equipo: Optional[Literal["Equipo A", "Equipo B", "Sin Asignar"]] = "Sin Asignar"
    asistencia_confirmada: Optional[bool] = True

class ConvocatoriaUpdate(BaseModel):
    equipo: Optional[Literal["Equipo A", "Equipo B", "Sin Asignar"]] = None
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

# Endpoint: Obtener todos los campos
@app.get("/api/campos")
def obtener_campos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
            INSERT INTO campos (nombre, direccion, tipo_superficie, modalidad)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """,
            (campo.nombre, campo.direccion, campo.tipo_superficie, campo.modalidad)
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

# Endpoint: Obtener todos los partidos
@app.get("/api/partidos")
def obtener_partidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
            INSERT INTO partidos (campo_id, creador_id, fecha_hora, max_jugadores, precio_total, estado)
            VALUES (%s, %s, %s, %s, %s, 'abierto')
            RETURNING *;
            """,
            (partido.campo_id, 1, partido.fecha_hora, partido.max_jugadores, partido.precio_total)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar que el partido existe
        cursor.execute("SELECT id FROM partidos WHERE id = %s;", (partido_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s;", (convocatoria.usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el usuario no está ya inscrito
        cursor.execute(
            "SELECT id FROM convocatorias WHERE partido_id = %s AND usuario_id = %s;",
            (partido_id, convocatoria.usuario_id)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El usuario ya está inscrito en este partido")
        
        # Insertar inscripción
        cursor.execute(
            """
            INSERT INTO convocatorias (partido_id, usuario_id, equipo, asistencia_confirmada)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """,
            (partido_id, convocatoria.usuario_id, convocatoria.equipo, convocatoria.asistencia_confirmada)
        )
        nueva_convocatoria = cursor.fetchone()
        conn.commit()
        
        # Obtener datos completos con info del usuario
        cursor.execute(
            """
            SELECT c.*, u.nombre, u.email, u.posicion_habitual, u.nivel
            FROM convocatorias c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = %s;
            """,
            (nueva_convocatoria['id'],)
        )
        convocatoria_completa = cursor.fetchone()
        return convocatoria_completa
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al inscribir: {str(e)}")
    finally:
        cursor.close()
        conn.close()

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
