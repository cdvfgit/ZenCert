"""
pages/operador.py
-----------------
Vista del operador para revisar, aprobar o rechazar órdenes pendientes.
"""

import streamlit as st
from core.lector_sheets import Estado, actualizar_estado, leer_alumnos, leer_ordenes


# ── Helpers ───────────────────────────────────────────────────────────────────

def _header(usuario: dict):
    st.markdown(f"""
    <div class='app-header'>
        <div class='app-logo'>🥋 Sistema de <span>Certificados</span></div>
        <div class='app-user'>
            Panel Operador &nbsp;|&nbsp; <strong>{usuario['nombre']}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _badge(estado: str) -> str:
    return f"<span class='badge badge-{estado.lower()}'>{estado}</span>"


def _card_orden(orden: dict, alumnos: list[dict], index: int):
    """Renderiza una card expandible con los detalles de una orden."""
    estado  = orden.get("estado", "PENDIENTE")
    org     = orden.get("organizacion", "").upper()
    dojo    = orden.get("dojo", "").replace("_", " ").title()
    total   = orden.get("total_alumnos", "0")

    with st.expander(
        f"**{orden['id_orden']}** &nbsp;·&nbsp; {org} / {dojo} "
        f"&nbsp;·&nbsp; {total} alumno(s) &nbsp;·&nbsp; {orden.get('timestamp', '')[:10]}",
        expanded=False,
    ):
        # Datos generales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Instructor",    orden.get("instructor", "—"))
        col2.metric("Organización",  org)
        col3.metric("Dojo",          dojo)
        col4.metric("Alumnos",       total)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Tabla de alumnos
        if alumnos:
            st.markdown("""
            <div style='font-size:0.8rem; font-weight:600; color:#00d4aa;
                        text-transform:uppercase; letter-spacing:0.06em;
                        margin-bottom:0.5rem;'>
                Alumnos
            </div>
            """, unsafe_allow_html=True)

            for alumno in alumnos:
                cedula_txt = (
                    f"C.I. {alumno.get('prefijo_cedula','')}-{alumno['cedula']}"
                    if alumno.get("cedula") else "Sin cédula"
                )
                st.markdown(f"""
                <div class='alumno-row'>
                    <div>
                        <div class='alumno-nombre'>{alumno.get('nombre_alumno','—')}</div>
                        <div class='alumno-meta'>
                            {cedula_txt} &nbsp;·&nbsp;
                            {alumno.get('grado','?')}° {alumno.get('tipo','?').upper()}
                            {f"&nbsp;·&nbsp; {alumno['notas']}" if alumno.get('notas') else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No se pudieron cargar los alumnos de esta orden.")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Acciones
        col_apr, col_rec, _ = st.columns([1, 1, 3])

        with col_apr:
            if st.button(
                "✓ Aprobar",
                key=f"aprobar_{index}",
                type="primary",
                use_container_width=True,
            ):
                try:
                    actualizar_estado(orden["id_orden"], Estado.APROBADA)
                    st.success(f"✅ Orden {orden['id_orden']} aprobada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al aprobar: {e}")

        with col_rec:
            if st.button(
                "✕ Rechazar",
                key=f"rechazar_{index}",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state[f"confirmar_rechazo_{index}"] = True
                st.rerun()

        # Confirmación de rechazo con motivo
        if st.session_state.get(f"confirmar_rechazo_{index}"):
            motivo = st.text_input(
                "Motivo del rechazo (opcional)",
                key=f"motivo_{index}",
                placeholder="Ej: Datos incompletos, error en grado...",
            )
            col_conf, col_cancel, _ = st.columns([1, 1, 3])
            with col_conf:
                if st.button(
                    "Confirmar rechazo",
                    key=f"conf_rec_{index}",
                    type="primary",
                ):
                    try:
                        actualizar_estado(orden["id_orden"], Estado.RECHAZADA)
                        st.session_state.pop(f"confirmar_rechazo_{index}", None)
                        st.error(f"❌ Orden {orden['id_orden']} rechazada.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al rechazar: {e}")
            with col_cancel:
                if st.button("Cancelar", key=f"cancel_rec_{index}"):
                    st.session_state.pop(f"confirmar_rechazo_{index}", None)
                    st.rerun()


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    usuario = st.session_state.usuario
    _header(usuario)

    # ── Tabs por estado ───────────────────────────────────────────────────
    tab_pend, tab_apr, tab_rec = st.tabs([
        "🟡  Pendientes",
        "🟢  Aprobadas",
        "🔴  Rechazadas",
    ])

    def _renderizar_tab(estado: str):
        with st.spinner("Cargando órdenes..."):
            try:
                ordenes = leer_ordenes(estado)
            except Exception as e:
                st.error(f"No se pudo conectar con Google Sheets: {e}")
                return

        if not ordenes:
            st.markdown(f"""
            <div style='text-align:center; padding:3rem 0; color:#334155;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>—</div>
                <div>No hay órdenes en este estado.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Filtros
        col_org, col_dojo, col_refresh = st.columns([2, 2, 1])

        with col_org:
            orgs = sorted({o["organizacion"] for o in ordenes})
            filtro_org = st.selectbox(
                "Filtrar por organización",
                options=["Todas"] + orgs,
                key=f"filtro_org_{estado}",
            )

        with col_dojo:
            dojos = sorted({o["dojo"] for o in ordenes})
            filtro_dojo = st.selectbox(
                "Filtrar por dojo",
                options=["Todos"] + dojos,
                key=f"filtro_dojo_{estado}",
            )

        with col_refresh:
            st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
            if st.button("↻ Actualizar", key=f"refresh_{estado}"):
                st.rerun()

        # Aplicar filtros
        ordenes_filtradas = [
            o for o in ordenes
            if (filtro_org  == "Todas" or o["organizacion"] == filtro_org)
            and (filtro_dojo == "Todos"  or o["dojo"]         == filtro_dojo)
        ]

        st.markdown(f"""
        <div style='font-size:0.8rem; color:#64748b; margin: 0.5rem 0 1rem 0;'>
            {len(ordenes_filtradas)} orden(es) encontradas
        </div>
        """, unsafe_allow_html=True)

        for i, orden in enumerate(ordenes_filtradas):
            try:
                alumnos = leer_alumnos(orden["id_orden"])
            except Exception:
                alumnos = []

            _card_orden(orden, alumnos, f"{estado}_{i}")

    with tab_pend:
        _renderizar_tab(Estado.PENDIENTE)

    with tab_apr:
        _renderizar_tab(Estado.APROBADA)

    with tab_rec:
        _renderizar_tab(Estado.RECHAZADA)

    # Cerrar sesión
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    col_logout = st.columns([5, 1])[1]
    with col_logout:
        if st.button("Cerrar sesión", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()