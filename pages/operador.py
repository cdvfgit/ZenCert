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
            for alumno in alumnos:
                cedula_txt = (
                    f"C.I. {alumno.get('prefijo_cedula','')}-{alumno['cedula']}"
                    if alumno.get("cedula") else "Sin cédula"
                )
                tipo = alumno.get("tipo", "").upper()
                grado = alumno.get("grado", "?")
                st.markdown(f"""
                <div class='zd-alumno'>
                    <div>
                        <div class='zd-alumno-nombre'>{alumno.get('nombre_alumno','—')}</div>
                        <div class='zd-alumno-meta'>
                            <span class='zd-tag'>{cedula_txt}</span>
                            <span class='zd-tag zd-tag-cyan'>{grado}° {tipo}</span>
                            {f"<span class='zd-tag'>{alumno['notas']}</span>" if alumno.get('notas') else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
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