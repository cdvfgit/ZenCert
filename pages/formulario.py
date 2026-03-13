"""
pages/formulario.py
-------------------
Vista del instructor para crear órdenes de certificados.
Flujo: Datos de la orden → Agregar alumnos → Resumen → Enviar
"""

import json
from datetime import date
from pathlib import Path

import streamlit as st

from core.lector_sheets import crear_hoja_orden, crear_orden

_RUTA_ORGANIZACIONES = Path(__file__).parent.parent / "data" / "organizaciones"
_RUTA_TIPOS_GRADO    = Path(__file__).parent.parent / "data" / "tipos_grado.json"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _cargar_config_org(organizacion: str) -> dict:
    ruta = _RUTA_ORGANIZACIONES / f"{organizacion}.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def _cargar_tipos_grado() -> dict:
    return json.loads(_RUTA_TIPOS_GRADO.read_text(encoding="utf-8"))


def _header(usuario: dict):
    st.markdown(f"""
    <div class='app-header'>
        <div class='app-logo'>🥋 Sistema de <span>Certificados</span></div>
        <div class='app-user'>
            {usuario['organizacion'].upper()} · {usuario['dojo'].replace('_', ' ').title()}
            &nbsp;|&nbsp; <strong>{usuario['nombre']}</strong>
            &nbsp;·&nbsp; <a href='#' style='color:#ef4444;font-size:0.75rem;'
                onclick='window.location.reload()'>Salir</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _badge(estado: str) -> str:
    return f"<span class='badge badge-{estado.lower()}'>{estado}</span>"


def _step_indicator(paso_actual: int):
    pasos = ["Datos de la orden", "Agregar alumnos", "Revisar y enviar"]
    items = []
    for i, nombre in enumerate(pasos, 1):
        if i < paso_actual:
            cls = "step done"
            num = "✓"
        elif i == paso_actual:
            cls = "step active"
            num = str(i)
        else:
            cls = "step"
            num = str(i)

        items.append(f"""
        <div class='{cls}'>
            <div class='step-num'>{num}</div>
            {nombre}
        </div>
        """)
        if i < len(pasos):
            items.append("<div class='step-line'></div>")

    st.markdown(
        f"<div class='steps'>{''.join(items)}</div>",
        unsafe_allow_html=True,
    )


# ── Paso 1 — Datos de la orden ────────────────────────────────────────────────

def _paso_datos_orden(usuario: dict, config_org: dict) -> bool:
    st.markdown("#### Datos de la orden")
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class='card'>
            <div class='card-header'>Organización</div>
            <div class='card-title'>{usuario['organizacion'].upper()}</div>
            <div class='card-meta'>{usuario['dojo'].replace('_', ' ').title()}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        ciudad = st.text_input(
            "Ciudad del examen *",
            value=st.session_state.get("orden_ciudad", ""),
            placeholder="Ej: Puerto Ordaz",
            key="input_ciudad",
        )
        fecha = st.date_input(
            "Fecha del examen *",
            value=st.session_state.get("orden_fecha", date.today()),
            key="input_fecha",
            format="DD/MM/YYYY",
        )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    if st.button("Continuar →", type="primary"):
        if not ciudad.strip():
            st.error("La ciudad del examen es obligatoria.")
            return False

        st.session_state.orden_ciudad = ciudad.strip()
        st.session_state.orden_fecha  = fecha
        st.session_state.paso         = 2
        st.rerun()

    return False


# ── Paso 2 — Agregar alumnos ──────────────────────────────────────────────────

def _paso_alumnos(usuario: dict, config_org: dict, tipos_grado: dict):
    organizacion = usuario["organizacion"]
    dojo         = usuario["dojo"]

    # Tipos permitidos para este dojo
    tipos_permitidos = (
        config_org
        .get("dojos", {})
        .get(dojo, {})
        .get("tipos_permitidos", list(config_org.get("grados", {}).keys()))
    )

    if "alumnos" not in st.session_state:
        st.session_state.alumnos = []

    # ── Formulario agregar alumno ─────────────────────────────────────────
    st.markdown("#### Agregar alumno")

    with st.expander("➕  Nuevo alumno", expanded=len(st.session_state.alumnos) == 0):
        col1, col2 = st.columns([2, 1])

        with col1:
            nombre = st.text_input("Nombre completo *", key="a_nombre",
                                   placeholder="Apellido Nombre")

        with col2:
            tipo = st.selectbox(
                "Tipo de grado *",
                options=tipos_permitidos,
                format_func=lambda t: tipos_grado.get(t, {}).get("nombre", t.capitalize()),
                key="a_tipo",
            )

        col3, col4, col5 = st.columns([1, 1, 2])

        with col3:
            # Grados disponibles según tipo
            grados_config = config_org.get("grados", {}).get(tipo, {})
            opciones_grado = sorted([int(k) for k in grados_config.keys()])
            grado = st.selectbox(
                "Grado *",
                options=opciones_grado,
                format_func=lambda g: (
                    f"{g}° "
                    f"{tipos_grado.get(grados_config.get(str(g), {}).get('tipo_override', tipo), {}).get('nombre', tipo.capitalize())}"
                    f" — {grados_config.get(str(g), {}).get('color', '')}"
                ),
                key="a_grado",
            )

        with col4:
            prefijo = st.selectbox(
                "Prefijo cédula",
                options=["V", "E", "S/C"],
                key="a_prefijo",
            )

        with col5:
            cedula_disabled = prefijo == "S/C"
            cedula = st.text_input(
                "Número de cédula",
                placeholder="Sin espacios ni puntos" if not cedula_disabled else "Sin documento",
                disabled=cedula_disabled,
                key="a_cedula",
            )

        notas = st.text_input(
            "Notas (opcional)",
            placeholder="Observaciones del examen...",
            key="a_notas",
        )

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        if st.button("Agregar alumno", type="primary"):
            errores = []
            if not nombre.strip():
                errores.append("El nombre es obligatorio.")
            if prefijo != "S/C" and cedula.strip() and not cedula.strip().isdigit():
                errores.append("La cédula debe contener solo números.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                st.session_state.alumnos.append({
                    "nombre_alumno":  nombre.strip(),
                    "cedula":         cedula.strip() if prefijo != "S/C" else "",
                    "prefijo_cedula": prefijo if prefijo != "S/C" else "",
                    "grado":          str(grado),
                    "tipo":           tipo,
                    "notas":          notas.strip(),
                })
                st.success(f"✓ {nombre.strip()} agregado correctamente.")
                st.rerun()

    # ── Lista de alumnos agregados ────────────────────────────────────────
    if st.session_state.alumnos:
        st.markdown(f"""
        <div style='font-size:0.85rem; font-weight:600; color:#00d4aa;
                    text-transform:uppercase; letter-spacing:0.06em;
                    margin: 1.25rem 0 0.75rem 0;'>
            Alumnos registrados ({len(st.session_state.alumnos)})
        </div>
        """, unsafe_allow_html=True)

        for i, alumno in enumerate(st.session_state.alumnos):
            col_info, col_btn = st.columns([5, 1])

            with col_info:
                tipo_nombre = tipos_grado.get(alumno["tipo"], {}).get("nombre", alumno["tipo"])
                cedula_txt  = (
                    f"C.I. {alumno['prefijo_cedula']}-{alumno['cedula']}"
                    if alumno["cedula"] else "Sin cédula"
                )
                st.markdown(f"""
                <div class='alumno-row'>
                    <div>
                        <div class='alumno-nombre'>{alumno['nombre_alumno']}</div>
                        <div class='alumno-meta'>
                            {cedula_txt} &nbsp;·&nbsp;
                            {alumno['grado']}° {tipo_nombre}
                            {f"&nbsp;·&nbsp; {alumno['notas']}" if alumno['notas'] else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_btn:
                if st.button("✕", key=f"del_{i}", help="Eliminar alumno"):
                    st.session_state.alumnos.pop(i)
                    st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        col_back, col_next = st.columns([1, 4])
        with col_back:
            if st.button("← Atrás", type="secondary"):
                st.session_state.paso = 1
                st.rerun()
        with col_next:
            if st.button("Revisar orden →", type="primary"):
                if len(st.session_state.alumnos) == 0:
                    st.error("Agrega al menos un alumno.")
                else:
                    st.session_state.paso = 3
                    st.rerun()
    else:
        st.info("Agrega al menos un alumno para continuar.")
        if st.button("← Atrás", type="secondary"):
            st.session_state.paso = 1
            st.rerun()


# ── Paso 3 — Resumen y envío ──────────────────────────────────────────────────

def _paso_resumen(usuario: dict, tipos_grado: dict):
    st.markdown("#### Resumen de la orden")

    # Datos generales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Organización", usuario["organizacion"].upper())
    col2.metric("Dojo", usuario["dojo"].replace("_", " ").title())
    col3.metric("Ciudad", st.session_state.orden_ciudad)
    col4.metric("Fecha", st.session_state.orden_fecha.strftime("%d/%m/%Y"))

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Tabla de alumnos
    st.markdown(f"""
    <div style='font-size:0.85rem; font-weight:600; color:#00d4aa;
                text-transform:uppercase; letter-spacing:0.06em;
                margin-bottom:0.75rem;'>
        Alumnos ({len(st.session_state.alumnos)})
    </div>
    """, unsafe_allow_html=True)

    for alumno in st.session_state.alumnos:
        tipo_nombre = tipos_grado.get(alumno["tipo"], {}).get("nombre", alumno["tipo"])
        cedula_txt  = (
            f"C.I. {alumno['prefijo_cedula']}-{alumno['cedula']}"
            if alumno["cedula"] else "Sin cédula"
        )
        st.markdown(f"""
        <div class='alumno-row'>
            <div>
                <div class='alumno-nombre'>{alumno['nombre_alumno']}</div>
                <div class='alumno-meta'>
                    {cedula_txt} &nbsp;·&nbsp; {alumno['grado']}° {tipo_nombre}
                    {f"&nbsp;·&nbsp; {alumno['notas']}" if alumno['notas'] else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Advertencia antes de enviar
    st.warning(
        "⚠ Revisa los datos antes de enviar. "
        "Una vez enviada, la orden no puede modificarse."
    )

    col_back, _, col_send = st.columns([1, 3, 2])

    with col_back:
        if st.button("← Editar", type="secondary"):
            st.session_state.paso = 2
            st.rerun()

    with col_send:
        if st.button("✓ Confirmar y enviar", type="primary", use_container_width=True):
            _enviar_orden(usuario)


def _enviar_orden(usuario: dict):
    with st.spinner("Enviando orden..."):
        try:
            datos_orden = {
                "instructor":    usuario["nombre"],
                "organizacion":  usuario["organizacion"],
                "dojo":          usuario["dojo"],
                "ciudad":        st.session_state.orden_ciudad,
                "fecha":         st.session_state.orden_fecha.strftime("%Y-%m-%d"),
                "total_alumnos": str(len(st.session_state.alumnos)),
            }

            id_orden = crear_orden(datos_orden)
            crear_hoja_orden(id_orden, st.session_state.alumnos)

            # Limpiar estado
            st.session_state.paso    = 1
            st.session_state.alumnos = []
            st.session_state.pop("orden_ciudad", None)
            st.session_state.pop("orden_fecha",  None)

            st.success(f"""
            ✅ **Orden enviada exitosamente**

            Tu orden ha sido registrada con el ID **{id_orden}**.
            El operador revisará y aprobará tu solicitud en breve.
            """)

        except Exception as e:
            st.error(f"Error al enviar la orden: {e}")


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    usuario      = st.session_state.usuario
    config_org   = _cargar_config_org(usuario["organizacion"])
    tipos_grado  = _cargar_tipos_grado()

    _header(usuario)

    # Inicializar paso
    if "paso" not in st.session_state:
        st.session_state.paso = 1

    _step_indicator(st.session_state.paso)

    if st.session_state.paso == 1:
        _paso_datos_orden(usuario, config_org)
    elif st.session_state.paso == 2:
        _paso_alumnos(usuario, config_org, tipos_grado)
    elif st.session_state.paso == 3:
        _paso_resumen(usuario, tipos_grado)

    # Cerrar sesión
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    col_logout = st.columns([5, 1])[1]
    with col_logout:
        if st.button("Cerrar sesión", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()