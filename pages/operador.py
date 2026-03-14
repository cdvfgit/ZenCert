"""
pages/operador.py
-----------------
Vista del operador para revisar, aprobar o rechazar órdenes pendientes.
"""

import streamlit as st
from core.lector_sheets import Estado, actualizar_estado, leer_alumnos, leer_ordenes


# ── Helpers de UI ─────────────────────────────────────────────────────────────

def _header(usuario: dict):
    st.markdown(f"""
    <div class='zd-header'>
        <div class='zd-logo'>🥋 Zen <span class='zd-logo-accent'>Dojo</span></div>
        <div class='zd-user-row'>
            <span class='zd-pill zd-pill-cyan'>Operador</span>
            <span class='zd-pill'>{usuario['nombre']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _badge(estado: str) -> str:
    return f"<span class='zd-badge zd-badge-{estado.lower()}'>{estado}</span>"


def _seccion(titulo: str, count: int = None):
    count_html = f"<span class='zd-count'>{count}</span>" if count is not None else ""
    st.markdown(
        f"<div class='zd-section'>{titulo}{count_html}</div>",
        unsafe_allow_html=True,
    )


def _tabla_alumnos_op(alumnos: list):
    """Tabla de solo lectura para el operador."""
    c1, c2, c3 = st.columns([3, 2, 2])
    for col, h in zip([c1,c2,c3], ["Nombre","Cédula","Grado"]):
        col.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:0.07em;padding:0.3rem 0;border-bottom:1px solid var(--border);'>{h}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    for i, alumno in enumerate(alumnos):
        cedula_txt = f"C.I. {alumno.get('prefijo_cedula','')}-{alumno['cedula']}" if alumno.get("cedula") else "Sin cédula"
        tipo  = alumno.get("tipo","").upper()
        grado = alumno.get("grado","?")
        bg    = "var(--bg-2)" if i % 2 == 0 else "var(--bg)"
        row   = f"background:{bg};padding:0.5rem 0.4rem;border-radius:6px;font-size:0.85rem;"

        c1, c2, c3 = st.columns([3, 2, 2])
        c1.markdown(f"<div style='{row}color:var(--text-1);font-weight:500;'>{alumno.get('nombre_alumno','—')}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='{row}color:var(--text-2);'>{cedula_txt}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='{row}'><span style='background:var(--cyan-soft);border:1px solid rgba(0,229,192,0.15);border-radius:4px;padding:0.1rem 0.4rem;font-size:0.75rem;color:var(--cyan);'>{grado}° {tipo}</span></div>", unsafe_allow_html=True)


def _card_orden(orden: dict, alumnos: list[dict], index):
    org   = orden.get("organizacion", "").upper()
    dojo  = orden.get("dojo", "").replace("_", " ").title()
    total = orden.get("total_alumnos", "0")
    fecha = orden.get("timestamp", "")[:10]
    id_o  = orden["id_orden"]

    with st.expander(
        f"{id_o}  ·  {org} / {dojo}  ·  {total} alumno(s)  ·  {fecha}",
        expanded=False,
    ):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Instructor",   orden.get("instructor", "—"))
        col2.metric("Organización", org)
        col3.metric("Dojo",         dojo)
        col4.metric("Fecha examen", orden.get("fecha", "—"))

        # Alumnos
        if alumnos:
            _seccion("Alumnos", len(alumnos))
            _tabla_alumnos_op(alumnos)
        else:
            st.info("No se pudieron cargar los alumnos de esta orden.")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Acciones
        col_apr, col_rec, _ = st.columns([1, 1, 2])

        with col_apr:
            if st.button("✓ Aprobar", key=f"apr_{index}",
                         type="primary", use_container_width=True):
                try:
                    actualizar_estado(id_o, Estado.APROBADA)
                    st.success(f"✅ {id_o} aprobada correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al aprobar: {e}")

        with col_rec:
            if st.button("✕ Rechazar", key=f"rec_{index}",
                         type="secondary", use_container_width=True):
                st.session_state[f"_rec_{index}"] = True
                st.rerun()

        # Confirmación de rechazo
        if st.session_state.get(f"_rec_{index}"):
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            motivo = st.text_input(
                "Motivo del rechazo (opcional)",
                key=f"mot_{index}",
                placeholder="Ej: Datos incompletos, error en el grado...",
            )
            col_ok, col_cancel, _ = st.columns([1, 1, 2])
            with col_ok:
                if st.button("Confirmar rechazo", key=f"ok_rec_{index}", type="primary"):
                    try:
                        actualizar_estado(id_o, Estado.RECHAZADA)
                        st.session_state.pop(f"_rec_{index}", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al rechazar: {e}")
            with col_cancel:
                if st.button("Cancelar", key=f"can_rec_{index}", type="secondary"):
                    st.session_state.pop(f"_rec_{index}", None)
                    st.rerun()


# ── Tab por estado ────────────────────────────────────────────────────────────

def _renderizar_tab(estado: str):
    with st.spinner("Cargando..."):
        try:
            ordenes = leer_ordenes(estado)
        except Exception as e:
            st.error(f"No se pudo conectar con Google Sheets: {e}")
            return

    if not ordenes:
        st.markdown("""
        <div class='zd-empty'>
            <div class='zd-empty-icon'>📭</div>
            <div class='zd-empty-text'>No hay órdenes en este estado.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Filtros
    col_org, col_dojo, col_btn = st.columns([2, 2, 1])

    with col_org:
        orgs = sorted({o["organizacion"] for o in ordenes})
        filtro_org = st.selectbox(
            "Organización",
            options=["Todas"] + orgs,
            key=f"forg_{estado}",
        )

    with col_dojo:
        dojos = sorted({o["dojo"] for o in ordenes})
        filtro_dojo = st.selectbox(
            "Dojo",
            options=["Todos"] + dojos,
            key=f"fdojo_{estado}",
        )

    with col_btn:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        if st.button("↻", key=f"ref_{estado}", help="Actualizar", use_container_width=True):
            st.rerun()

    # Aplicar filtros
    ordenes_filtradas = [
        o for o in ordenes
        if (filtro_org  == "Todas" or o["organizacion"] == filtro_org)
        and (filtro_dojo == "Todos" or o["dojo"]         == filtro_dojo)
    ]

    st.markdown(f"""
    <div style='font-size:0.75rem; color:var(--text-3);
                margin:0.3rem 0 0.75rem 0;'>
        {len(ordenes_filtradas)} orden(es) encontrada(s)
    </div>
    """, unsafe_allow_html=True)

    for i, orden in enumerate(ordenes_filtradas):
        try:
            alumnos = leer_alumnos(orden["id_orden"])
        except Exception:
            alumnos = []
        _card_orden(orden, alumnos, f"{estado}_{i}")


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    usuario = st.session_state.usuario
    _header(usuario)

    tab_pend, tab_apr, tab_rec = st.tabs([
        "🟡  Pendientes",
        "🟢  Aprobadas",
        "🔴  Rechazadas",
    ])

    with tab_pend:
        _renderizar_tab(Estado.PENDIENTE)

    with tab_apr:
        _renderizar_tab(Estado.APROBADA)

    with tab_rec:
        _renderizar_tab(Estado.RECHAZADA)

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    col_logout = st.columns([5, 1])[1]
    with col_logout:
        if st.button("Salir", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()