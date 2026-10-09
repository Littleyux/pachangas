import { useEffect, useState } from 'react';
import API from './api';
import './App.css';
import './icons.css';

function App() {
  /* ========== STATE ========== */
  const [activeTab, setActiveTab] = useState('usuarios');
  
  // Usuarios
  const [usuarios, setUsuarios] = useState([]);
  const [formUsuarioAbierto, setFormUsuarioAbierto] = useState(false);
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [posicion, setPosicion] = useState('Centrocampista');
  const [nivel, setNivel] = useState(5.0);

  // Campos
  const [campos, setCampos] = useState([]);
  const [formCampoAbierto, setFormCampoAbierto] = useState(false);
  const [campoNombre, setCampoNombre] = useState('');
  const [campoDireccion, setCampoDireccion] = useState('');
  const [campoSuperficie, setCampoSuperficie] = useState('Césped Artificial');
  const [campoModalidad, setCampoModalidad] = useState('F7');

  // Partidos
  const [partidos, setPartidos] = useState([]);
  const [formPartidoAbierto, setFormPartidoAbierto] = useState(false);
  const [partidoCampoId, setPartidoCampoId] = useState('');
  const [partidoFecha, setPartidoFecha] = useState('');
  const [partidoHora, setPartidoHora] = useState('');
  const [partidoMaxJugadores, setPartidoMaxJugadores] = useState(10);
  const [partidoPrecio, setPartidoPrecio] = useState('');
  const [partidoEquipoA, setPartidoEquipoA] = useState('Equipo A');
  const [partidoEquipoB, setPartidoEquipoB] = useState('Equipo B');

  // Convocatorias
  const [convocatoriasPorPartido, setConvocatoriasPorPartido] = useState({});
  const [partidoExpandido, setPartidoExpandido] = useState(null);
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState('');
  const [equipoSeleccionado, setEquipoSeleccionado] = useState('Equipo A');

  /* ========== EFFECTS ========== */
  useEffect(() => {
    cargarUsuarios();
    cargarCampos();
    cargarPartidos();
    console.log('App montada, cargando datos...');
  }, []);

  /* ========== USUARIOS FUNCTIONS ========== */
  const cargarUsuarios = async () => {
    try {
      const res = await API.get('/usuarios');
      setUsuarios(res.data);
      console.log('Usuarios cargados:', res.data.length);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    }
  };

  const handleCrearUsuario = async (e) => {
    e.preventDefault();
    try {
      await API.post('/usuarios', {
        nombre,
        email,
        posicion_habitual: posicion,
        nivel: parseFloat(nivel),
      });
      setNombre('');
      setEmail('');
      setPosicion('Centrocampista');
      setNivel(5.0);
      setFormUsuarioAbierto(false);
      cargarUsuarios();
    } catch (error) {
      console.error('Error al crear usuario:', error);
      alert('Error al registrar usuario. Comprueba que el email no esté repetido.');
    }
  };

  /* ========== CAMPOS FUNCTIONS ========== */
  const cargarCampos = async () => {
    try {
      const res = await API.get('/campos');
      setCampos(res.data);
      console.log('Campos cargados:', res.data.length);
    } catch (error) {
      console.error('Error al cargar campos:', error);
    }
  };

  const handleCrearCampo = async (e) => {
    e.preventDefault();
    try {
      await API.post('/campos', {
        nombre: campoNombre,
        direccion: campoDireccion,
        tipo_superficie: campoSuperficie,
        modalidad: campoModalidad,
      });
      setCampoNombre('');
      setCampoDireccion('');
      setCampoSuperficie('Césped Artificial');
      setCampoModalidad('F7');
      setFormCampoAbierto(false);
      cargarCampos();
    } catch (error) {
      console.error('Error al crear campo:', error);
      alert('Error al registrar campo.');
    }
  };

  const handleEliminarCampo = async (id) => {
    if (window.confirm('¿Eliminar este campo?')) {
      try {
        await API.delete(`/campos/${id}`);
        cargarCampos();
      } catch (error) {
        console.error('Error al eliminar campo:', error);
      }
    }
  };

  /* ========== PARTIDOS FUNCTIONS ========== */
  const cargarPartidos = async () => {
    try {
      const res = await API.get('/partidos');
      setPartidos(res.data);
      console.log('Partidos cargados:', res.data.length);
    } catch (error) {
      console.error('Error al cargar partidos:', error);
    }
  };

  const handleCrearPartido = async (e) => {
    e.preventDefault();
    try {
      if (!partidoCampoId || !partidoFecha || !partidoHora) {
        alert('Por favor completa campo, fecha y hora');
        return;
      }

      const fechaHoraISO = `${partidoFecha}T${partidoHora}:00`;

      await API.post('/partidos', {
        campo_id: parseInt(partidoCampoId),
        fecha_hora: fechaHoraISO,
        max_jugadores: parseInt(partidoMaxJugadores),
        precio_total: partidoPrecio ? parseFloat(partidoPrecio) : null,
        equipo_a_nombre: partidoEquipoA,
        equipo_b_nombre: partidoEquipoB,
      });

      setPartidoCampoId('');
      setPartidoFecha('');
      setPartidoHora('');
      setPartidoMaxJugadores(10);
      setPartidoPrecio('');
      setPartidoEquipoA('Equipo A');
      setPartidoEquipoB('Equipo B');
      setFormPartidoAbierto(false);
      
      cargarPartidos();
    } catch (error) {
      console.error('Error al crear partido:', error);
      alert('Error al crear partido.');
    }
  };

  const handleEliminarPartido = async (id) => {
    if (window.confirm('¿Eliminar este partido?')) {
      try {
        await API.delete(`/partidos/${id}`);
        cargarPartidos();
      } catch (error) {
        console.error('Error al eliminar partido:', error);
      }
    }
  };

  /* ========== CONVOCATORIAS FUNCTIONS ========== */
  const cargarConvocatorias = async (partidoId) => {
    try {
      const res = await API.get(`/partidos/${partidoId}/convocatorias`);
      setConvocatoriasPorPartido(prev => ({
        ...prev,
        [partidoId]: res.data
      }));
    } catch (error) {
      console.error('Error al cargar convocatorias:', error);
    }
  };

  const handleInscribirse = async (partidoId) => {
    console.log('[DEBUG] handleInscribirse llamado', { partidoId, usuarioSeleccionado, equipoSeleccionado });
    
    if (!usuarioSeleccionado) {
      alert('Por favor selecciona un jugador');
      return;
    }
    if (!equipoSeleccionado) {
      alert('Por favor selecciona un equipo');
      return;
    }

    const payload = {
      usuario_id: parseInt(usuarioSeleccionado),
      equipo: equipoSeleccionado,
      asistencia_confirmada: true,
    };
    console.log('[DEBUG] Enviando payload:', payload);

    try {
      await API.post(`/partidos/${partidoId}/convocatorias`, payload);
      console.log('[DEBUG] Inscripción exitosa');
      
      // Resetea los selectores para la próxima inscripción
      const partido = partidos.find(p => p.id === partidoId);
      setUsuarioSeleccionado('');
      setEquipoSeleccionado(partido?.equipo_a_nombre || 'Equipo A');
      
      cargarConvocatorias(partidoId);
    } catch (error) {
      console.error('[ERROR] Error al inscribirse:', error);
      console.error('[ERROR] Response data:', error.response?.data);
      if (error.response?.status === 400) {
        alert('Este jugador ya está inscrito en este partido');
      } else if (error.response?.status === 422) {
        alert('Error de validación: ' + (error.response?.data?.detail || 'Datos inválidos'));
      } else {
        alert('Error al inscribirse al partido');
      }
    }
  };

  const handleDesinscribirse = async (partidoId, usuarioId) => {
    if (window.confirm('¿Desapuntarse del partido?')) {
      try {
        await API.delete(`/partidos/${partidoId}/convocatorias/${usuarioId}`);
        cargarConvocatorias(partidoId);
      } catch (error) {
        console.error('Error al desapuntarse:', error);
      }
    }
  };

  const abrirDetallesPartido = (partidoId) => {
    console.log('Abriendo detalles del partido:', partidoId);
    setPartidoExpandido(partidoId);
    
    // Encuentra el partido para obtener el nombre del equipo A
    const partido = partidos.find(p => p.id === partidoId);
    if (partido) {
      // Resetea el equipo seleccionado al nombre del equipo A del partido
      setEquipoSeleccionado(partido.equipo_a_nombre || 'Equipo A');
      console.log('[DEBUG] Equipo A del partido:', partido.equipo_a_nombre);
    }
    
    if (!convocatoriasPorPartido[partidoId]) {
      cargarConvocatorias(partidoId);
    }
  };

  const cerrarDetallesPartido = () => {
    setPartidoExpandido(null);
  };

  /* ========== HELPERS ========== */
  const getPositionIcon = (posicion) => {
    const iconos = {
      'Portero': '⚙️',
      'Defensa': '🛡️',
      'Centrocampista': '⚡',
      'Delantero': '🎯',
    };
    return iconos[posicion] || '⚽';
  };

  const getEstadoColor = (estado) => {
    const colores = {
      'abierto': 'chip-primary',
      'completo': 'chip-warning',
      'finalizado': 'chip-success',
      'cancelado': 'chip-error',
    };
    return colores[estado] || 'chip-primary';
  };

  const getEstadoLabel = (estado) => {
    const labels = {
      'abierto': 'Abierto',
      'completo': 'Completo',
      'finalizado': 'Finalizado',
      'cancelado': 'Cancelado',
    };
    return labels[estado] || estado;
  };

  const formatearFecha = (fechaISO) => {
    try {
      const fecha = new Date(fechaISO);
      return fecha.toLocaleDateString('es-ES', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return fechaISO;
    }
  };

  /* ========== RENDER ========== */
  return (
    <div className="app">
      {/* HEADER */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="icon icon-lg icon-primary">⚽</span>
            Pachangas
          </h1>
          <p className="text-secondary">Organiza tus partidos de fútbol</p>
        </div>
      </header>

      {/* MAIN */}
      <main className="app-container">
        {/* TABS */}
        <div className="tabs-container">
          <button
            className={`tab ${activeTab === 'usuarios' ? 'active' : ''}`}
            onClick={() => setActiveTab('usuarios')}
          >
            <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            Jugadores
          </button>
          <button
            className={`tab ${activeTab === 'campos' ? 'active' : ''}`}
            onClick={() => setActiveTab('campos')}
          >
            <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="5" y="5" width="14" height="14" rx="2"/>
              <path d="M7 10h10M7 15h10M7 12h1M7 17h1M12 12h5M12 17h5"/>
            </svg>
            Campos
          </button>
          <button
            className={`tab ${activeTab === 'partidos' ? 'active' : ''}`}
            onClick={() => setActiveTab('partidos')}
          >
            <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            Partidos
          </button>
        </div>

        {/* USUARIOS TAB */}
        <div className={`tab-content ${activeTab === 'usuarios' ? 'active' : ''}`}>
          <div className="card mb-24">
            <div className="card-header" style={{ cursor: 'pointer' }} onClick={() => setFormUsuarioAbierto(!formUsuarioAbierto)}>
              <h2>Registrar Nuevo Jugador</h2>
              <span style={{ fontSize: '20px', transition: 'transform 0.3s' }}>
                {formUsuarioAbierto ? '▼' : '▶'}
              </span>
            </div>
            {formUsuarioAbierto && (
              <form onSubmit={handleCrearUsuario}>
                <div className="grid-2">
                  <div className="form-group">
                    <label htmlFor="nombre">Nombre Completo *</label>
                    <input id="nombre" type="text" placeholder="Ej. Juan García" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="email">Correo Electrónico *</label>
                    <input id="email" type="email" placeholder="ejemplo@correo.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="posicion">Posición Habitual *</label>
                    <select id="posicion" value={posicion} onChange={(e) => setPosicion(e.target.value)}>
                      <option value="Portero">⚙️ Portero</option>
                      <option value="Defensa">🛡️ Defensa</option>
                      <option value="Centrocampista">⚡ Centrocampista</option>
                      <option value="Delantero">🎯 Delantero</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="nivel">Nivel de Juego (1.0 - 10.0) *</label>
                    <input id="nivel" type="number" step="0.5" min="1" max="10" value={nivel} onChange={(e) => setNivel(e.target.value)} />
                  </div>
                </div>
                <button type="submit" className="button button-primary mt-24">
                  <span className="icon icon-add"></span>Añadir Jugador
                </button>
              </form>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Jugadores Registrados</h2>
              <span className="card-badge">{usuarios.length} jugadores</span>
            </div>
            {usuarios.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">👤</div>
                <div className="empty-state-title">No hay jugadores registrados</div>
              </div>
            ) : (
              <div className="list-container">
                {usuarios.map((usuario) => (
                  <div key={usuario.id} className="list-item">
                    <div className="list-item-content">
                      <div className="list-item-title">{usuario.nombre}</div>
                      <div className="list-item-subtitle">{usuario.email}</div>
                      <div className="flex-gap-8 mt-16">
                        <span className="chip chip-primary">
                          {getPositionIcon(usuario.posicion_habitual)} {usuario.posicion_habitual || 'Sin definir'}
                        </span>
                      </div>
                    </div>
                    <div className="list-item-actions">
                      <div className="rating">
                        <span className="icon icon-primary">⭐</span>
                        <span className="rating-value">{usuario.nivel}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* CAMPOS TAB */}
        <div className={`tab-content ${activeTab === 'campos' ? 'active' : ''}`}>
          <div className="card mb-24">
            <div className="card-header" style={{ cursor: 'pointer' }} onClick={() => setFormCampoAbierto(!formCampoAbierto)}>
              <h2>Registrar Nuevo Campo</h2>
              <span style={{ fontSize: '20px', transition: 'transform 0.3s' }}>
                {formCampoAbierto ? '▼' : '▶'}
              </span>
            </div>
            {formCampoAbierto && (
              <form onSubmit={handleCrearCampo}>
                <div className="grid-2">
                  <div className="form-group">
                    <label htmlFor="campNombre">Nombre del Campo *</label>
                    <input id="campNombre" type="text" placeholder="Ej. Polideportivo Municipal" value={campoNombre} onChange={(e) => setCampoNombre(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="campDireccion">Dirección</label>
                    <input id="campDireccion" type="text" placeholder="Ej. Calle Principal, 123" value={campoDireccion} onChange={(e) => setCampoDireccion(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="campSuperficie">Tipo de Superficie *</label>
                    <select id="campSuperficie" value={campoSuperficie} onChange={(e) => setCampoSuperficie(e.target.value)}>
                      <option value="Césped Natural">🌱 Césped Natural</option>
                      <option value="Césped Artificial">🟢 Césped Artificial</option>
                      <option value="Pista">🔵 Pista</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="campModalidad">Modalidad *</label>
                    <select id="campModalidad" value={campoModalidad} onChange={(e) => setCampoModalidad(e.target.value)}>
                      <option value="F5">⚽ F5</option>
                      <option value="F7">⚽ F7</option>
                      <option value="F8">⚽ F8</option>
                      <option value="F11">⚽ F11</option>
                    </select>
                  </div>
                </div>
                <button type="submit" className="button button-primary mt-24">
                  <span className="icon icon-add"></span>Añadir Campo
                </button>
              </form>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Campos Disponibles</h2>
              <span className="card-badge">{campos.length} campos</span>
            </div>
            {campos.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🏟️</div>
                <div className="empty-state-title">No hay campos registrados</div>
              </div>
            ) : (
              <div className="list-container">
                {campos.map((campo) => (
                  <div key={campo.id} className="list-item">
                    <div className="list-item-content">
                      <div className="list-item-title">{campo.nombre}</div>
                      {campo.direccion && <div className="list-item-subtitle">📍 {campo.direccion}</div>}
                      <div className="flex-gap-8 mt-16">
                        <span className="chip chip-success">{campo.tipo_superficie}</span>
                        <span className="chip chip-primary">⚽ {campo.modalidad}</span>
                      </div>
                    </div>
                    <div className="list-item-actions">
                      <button className="button-icon" onClick={() => handleEliminarCampo(campo.id)} title="Eliminar campo">✕</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* PARTIDOS TAB */}
        <div className={`tab-content ${activeTab === 'partidos' ? 'active' : ''}`}>
          <div className="card mb-24">
            <div className="card-header" style={{ cursor: 'pointer' }} onClick={() => setFormPartidoAbierto(!formPartidoAbierto)}>
              <h2>Crear Nuevo Partido</h2>
              <span style={{ fontSize: '20px', transition: 'transform 0.3s' }}>
                {formPartidoAbierto ? '▼' : '▶'}
              </span>
            </div>
            {formPartidoAbierto && (
              <form onSubmit={handleCrearPartido}>
                <div className="grid-2">
                  <div className="form-group">
                    <label htmlFor="partidoCampo">Campo *</label>
                    <select id="partidoCampo" value={partidoCampoId} onChange={(e) => setPartidoCampoId(e.target.value)} required>
                      <option value="">Selecciona un campo...</option>
                      {campos.map((campo) => (
                        <option key={campo.id} value={campo.id}>{campo.nombre} ({campo.modalidad})</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoFecha">Fecha *</label>
                    <input id="partidoFecha" type="date" value={partidoFecha} onChange={(e) => setPartidoFecha(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoHora">Hora *</label>
                    <input id="partidoHora" type="time" value={partidoHora} onChange={(e) => setPartidoHora(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoMaxJugadores">Máximo de Jugadores</label>
                    <input id="partidoMaxJugadores" type="number" min="4" max="22" value={partidoMaxJugadores} onChange={(e) => setPartidoMaxJugadores(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoPrecio">Precio Total (opcional)</label>
                    <input id="partidoPrecio" type="number" step="0.01" min="0" placeholder="Ej. 50.00" value={partidoPrecio} onChange={(e) => setPartidoPrecio(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoEquipoA">Nombre Equipo A</label>
                    <input id="partidoEquipoA" type="text" placeholder="Ej. Equipo A" value={partidoEquipoA} onChange={(e) => setPartidoEquipoA(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label htmlFor="partidoEquipoB">Nombre Equipo B</label>
                    <input id="partidoEquipoB" type="text" placeholder="Ej. Equipo B" value={partidoEquipoB} onChange={(e) => setPartidoEquipoB(e.target.value)} />
                  </div>
                </div>
                <button type="submit" className="button button-primary mt-24">
                  <span className="icon icon-add"></span>Crear Partido
                </button>
              </form>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Partidos Programados</h2>
              <span className="card-badge">{partidos.length} partidos</span>
            </div>
            {partidos.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📅</div>
                <div className="empty-state-title">No hay partidos programados</div>
              </div>
            ) : (
              <div className="list-container">
                {partidos.map((partido) => (
                  <div key={partido.id}>
                    <div className="list-item" onClick={() => abrirDetallesPartido(partido.id)} style={{ cursor: 'pointer' }}>
                      <div className="list-item-content">
                        <div className="list-item-title">{partido.campo_nombre} - {partido.modalidad}</div>
                        <div className="list-item-subtitle">🕐 {formatearFecha(partido.fecha_hora)}</div>
                        <div className="flex-gap-8 mt-16">
                          <span className={`chip ${getEstadoColor(partido.estado)}`}>{getEstadoLabel(partido.estado)}</span>
                          <span className="chip chip-secondary">👥 {partido.max_jugadores} jugadores</span>
                          {partido.precio_total && <span className="chip chip-secondary">💰 €{partido.precio_total.toFixed(2)}</span>}
                        </div>
                      </div>
                      <div className="list-item-actions">
                        <button className="button-icon" onClick={(e) => { e.stopPropagation(); handleEliminarPartido(partido.id); }} title="Eliminar partido">✕</button>
                      </div>
                    </div>

                    {partidoExpandido === partido.id && (
                      <div className="partido-detalles">
                        <div className="partido-detalles-header">
                          <h3>Inscripción a Jugadores</h3>
                          <button className="button-icon" onClick={() => cerrarDetallesPartido()}>✕</button>
                        </div>

                        <div className="form-group mb-24">
                          <label>Selecciona un jugador y equipo:</label>
                          <div style={{ display: 'flex', gap: '8px', marginTop: '8px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                            <select value={usuarioSeleccionado} onChange={(e) => setUsuarioSeleccionado(e.target.value)} style={{ flex: 1, minWidth: '150px', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                              <option value="">-- Jugador --</option>
                              {usuarios.map((u) => (
                                <option key={u.id} value={u.id}>{u.nombre} - Nivel {u.nivel}</option>
                              ))}
                            </select>
                            <select value={equipoSeleccionado} onChange={(e) => setEquipoSeleccionado(e.target.value)} style={{ flex: 1, minWidth: '120px', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                              <option value={partido.equipo_a_nombre || 'Equipo A'}>{partido.equipo_a_nombre || 'Equipo A'}</option>
                              <option value={partido.equipo_b_nombre || 'Equipo B'}>{partido.equipo_b_nombre || 'Equipo B'}</option>
                            </select>
                            <button className="button button-primary" onClick={() => handleInscribirse(partido.id)} style={{ whiteSpace: 'nowrap' }}>Inscribirse</button>
                          </div>
                        </div>

                        <div>
                          <h4 style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>Inscritos ({(convocatoriasPorPartido[partido.id] || []).length})</h4>
                          {(convocatoriasPorPartido[partido.id] || []).length === 0 ? (
                            <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>Sin inscritos</p>
                          ) : (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '12px' }}>
                              {/* Equipo A */}
                              <div>
                                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--primary)', marginBottom: '8px', paddingBottom: '8px', borderBottom: '2px solid var(--primary)' }}>
                                  {partido.equipo_a_nombre || 'Equipo A'} ({(convocatoriasPorPartido[partido.id] || []).filter(c => c.equipo === (partido.equipo_a_nombre || 'Equipo A')).length})
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                  {(convocatoriasPorPartido[partido.id] || [])
                                    .filter(c => c.equipo === (partido.equipo_a_nombre || 'Equipo A'))
                                    .map((conv) => (
                                      <div key={conv.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                                        <div style={{ flex: 1 }}>
                                          <div style={{ fontWeight: '500', fontSize: '14px' }}>{conv.nombre}</div>
                                          <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{conv.posicion_habitual} • ⭐ {conv.nivel}</div>
                                        </div>
                                        <button
                                          style={{ background: 'none', border: 'none', fontSize: '16px', cursor: 'pointer', padding: '4px', color: 'var(--error)' }}
                                          onClick={() => handleDesinscribirse(partido.id, conv.usuario_id)}
                                          title="Desapuntarse"
                                        >
                                          ✕
                                        </button>
                                      </div>
                                    ))}
                                  {(convocatoriasPorPartido[partido.id] || []).filter(c => c.equipo === (partido.equipo_a_nombre || 'Equipo A')).length === 0 && (
                                    <p style={{ color: 'var(--text-tertiary)', fontSize: '12px', textAlign: 'center', padding: '20px 0' }}>Sin jugadores</p>
                                  )}
                                </div>
                              </div>

                              {/* Equipo B */}
                              <div>
                                <div style={{ fontSize: '13px', fontWeight: '600', color: '#1E8E3E', marginBottom: '8px', paddingBottom: '8px', borderBottom: '2px solid #1E8E3E' }}>
                                  {partido.equipo_b_nombre || 'Equipo B'} ({(convocatoriasPorPartido[partido.id] || []).filter(c => c.equipo === (partido.equipo_b_nombre || 'Equipo B')).length})
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                  {(convocatoriasPorPartido[partido.id] || [])
                                    .filter(c => c.equipo === (partido.equipo_b_nombre || 'Equipo B'))
                                    .map((conv) => (
                                      <div key={conv.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'var(--bg-secondary)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                                        <div style={{ flex: 1 }}>
                                          <div style={{ fontWeight: '500', fontSize: '14px' }}>{conv.nombre}</div>
                                          <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{conv.posicion_habitual} • ⭐ {conv.nivel}</div>
                                        </div>
                                        <button
                                          style={{ background: 'none', border: 'none', fontSize: '16px', cursor: 'pointer', padding: '4px', color: 'var(--error)' }}
                                          onClick={() => handleDesinscribirse(partido.id, conv.usuario_id)}
                                          title="Desapuntarse"
                                        >
                                          ✕
                                        </button>
                                      </div>
                                    ))}
                                  {(convocatoriasPorPartido[partido.id] || []).filter(c => c.equipo === (partido.equipo_b_nombre || 'Equipo B')).length === 0 && (
                                    <p style={{ color: 'var(--text-tertiary)', fontSize: '12px', textAlign: 'center', padding: '20px 0' }}>Sin jugadores</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
