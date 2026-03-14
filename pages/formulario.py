"""
pages/formulario.py
-------------------
Vista del instructor para crear órdenes de certificados.
Flujo: Datos de la orden → Agregar alumnos → Revisar y enviar
"""

import json
from datetime import date
from pathlib import Path

import streamlit as st
from core.lector_sheets import crear_hoja_orden, crear_orden

_RUTA_ORGANIZACIONES = Path(__file__).parent.parent / "data" / "organizaciones"
_RUTA_TIPOS_GRADO    = Path(__file__).parent.parent / "data" / "tipos_grado.json"


# ── Helpers de datos ──────────────────────────────────────────────────────────

def _cargar_config_org(organizacion: str) -> dict:
    ruta = _RUTA_ORGANIZACIONES / f"{organizacion}.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def _cargar_tipos_grado() -> dict:
    return json.loads(_RUTA_TIPOS_GRADO.read_text(encoding="utf-8"))


# ── Helpers de UI ─────────────────────────────────────────────────────────────

def _header(usuario: dict):
    org  = usuario["organizacion"].upper()
    dojo = usuario["dojo"].replace("_", " ").title()
    nombre = usuario["nombre"]

    st.markdown(f"""
    <div class='zd-header'>
        <div class='zd-logo'>🥋 Zen <span class='zd-logo-accent'>Dojo</span></div>
        <div class='zd-user-row'>
            <span class='zd-pill zd-pill-cyan'>{org}</span>
            <span class='zd-pill'>{dojo}</span>
            <span class='zd-pill'>{nombre}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _step_indicator(paso: int):
    pasos = [(1, "Orden"), (2, "Alumnos"), (3, "Revisar")]
    items = []
    for num, label in pasos:
        if num < paso:
            cls, sym = "zd-step zd-step-done", "✓"
        elif num == paso:
            cls, sym = "zd-step zd-step-active", str(num)
        else:
            cls, sym = "zd-step", str(num)
        items.append(f"<div class='{cls}'><div class='zd-step-num'>{sym}</div><span class='zd-step-label'>{label}</span></div>")

    st.markdown(f"<div class='zd-steps'>{''.join(items)}</div>", unsafe_allow_html=True)


def _seccion(titulo: str, count: int = None):
    count_html = f"<span class='zd-count'>{count}</span>" if count is not None else ""
    st.markdown(
        f"<div class='zd-section'>{titulo}{count_html}</div>",
        unsafe_allow_html=True,
    )


# ── Tabla de alumnos ─────────────────────────────────────────────────────────

def _tabla_alumnos(alumnos: list, tipos_grado: dict, editable: bool = False):
    """Renderiza una tabla limpia con los datos de los alumnos."""
    # Encabezados
    if editable:
        cols = st.columns([3, 2, 2, 1])
        headers = ["Nombre", "Cédula", "Grado", ""]
    else:
        cols = st.columns([3, 2, 2])
        headers = ["Nombre", "Cédula", "Grado"]

    for col, h in zip(cols, headers):
        col.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:0.07em;padding:0.3rem 0;border-bottom:1px solid var(--border);'>{h}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    for i, alumno in enumerate(alumnos):
        tipo_nombre = tipos_grado.get(alumno["tipo"], {}).get("nombre", alumno["tipo"])
        cedula_txt  = f"C.I. {alumno['prefijo_cedula']}-{alumno['cedula']}" if alumno.get("cedula") else "Sin cédula"
        grado_txt   = f"{alumno['grado']}° {tipo_nombre}"

        bg = "var(--bg-2)" if i % 2 == 0 else "var(--bg)"

        if editable:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        else:
            c1, c2, c3 = st.columns([3, 2, 2])

        row_style = f"background:{bg};padding:0.5rem 0.4rem;border-radius:6px;font-size:0.85rem;"

        c1.markdown(f"<div style='{row_style}color:var(--text-1);font-weight:500;'>{alumno['nombre_alumno']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='{row_style}color:var(--text-2);'>{cedula_txt}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='{row_style}'><span style='background:var(--cyan-soft);border:1px solid rgba(0,229,192,0.15);border-radius:4px;padding:0.1rem 0.4rem;font-size:0.75rem;color:var(--cyan);'>{grado_txt}</span></div>", unsafe_allow_html=True)

        if editable:
            with c4:
                st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_{i}", help="Eliminar alumno", use_container_width=True):
                    st.session_state.alumnos.pop(i)
                    st.rerun()


# ── Paso 1 — Datos de la orden ────────────────────────────────────────────────

def _paso_datos_orden(usuario: dict, config_org: dict):
    org  = usuario["organizacion"].upper()
    dojo = usuario["dojo"].replace("_", " ").title()

    # Info del dojo
    st.markdown(f"""
    <div class='zd-card zd-card-cyan' style='margin-bottom:1.25rem;'>
        <div class='zd-label'>Solicitando para</div>
        <div class='zd-value'>{org}</div>
        <div class='zd-sub'>{dojo}</div>
    </div>
    """, unsafe_allow_html=True)

    _seccion("Datos del examen")

    col1, col2 = st.columns(2)
    with col1:
        ciudad = st.text_input(
            "Ciudad *",
            value=st.session_state.get("orden_ciudad", ""),
            placeholder="Ej: Puerto Ordaz",
            key="input_ciudad",
        )
    with col2:
        fecha = st.date_input(
            "Fecha del examen *",
            value=st.session_state.get("orden_fecha", date.today()),
            key="input_fecha",
            format="DD/MM/YYYY",
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if st.button("Continuar — Agregar alumnos →", type="primary", use_container_width=True):
        if not ciudad.strip():
            st.error("La ciudad del examen es obligatoria.")
            return
        st.session_state.orden_ciudad = ciudad.strip()
        st.session_state.orden_fecha  = fecha
        st.session_state.paso         = 2
        st.rerun()


# ── Paso 2 — Agregar alumnos ──────────────────────────────────────────────────

def _paso_alumnos(usuario: dict, config_org: dict, tipos_grado: dict):
    organizacion = usuario["organizacion"]
    dojo         = usuario["dojo"]

    tipos_permitidos = (
        config_org
        .get("dojos", {})
        .get(dojo, {})
        .get("tipos_permitidos", list(config_org.get("grados", {}).keys()))
    )

    if "alumnos" not in st.session_state:
        st.session_state.alumnos = []

    # ── Formulario de alumno ──────────────────────────────────────────────
    _seccion("Nuevo alumno")

    with st.expander(
        "➕  Completar datos del alumno",
        expanded=len(st.session_state.alumnos) == 0,
    ):
        nombre = st.text_input(
            "Nombre completo *",
            key="a_nombre",
            placeholder="Apellidos y nombres como en el documento",
        )

        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox(
                "Tipo de grado *",
                options=tipos_permitidos,
                format_func=lambda t: tipos_grado.get(t, {}).get("nombre", t.capitalize()),
                key="a_tipo",
            )
        with col2:
            grados_config   = config_org.get("grados", {}).get(tipo, {})
            opciones_grado  = sorted([int(k) for k in grados_config.keys()])
            grado = st.selectbox(
                "Grado *",
                options=opciones_grado,
                format_func=lambda g: (
                    f"{g}° "
                    f"{tipos_grado.get(grados_config.get(str(g), {}).get('tipo_override', tipo), {}).get('nombre', tipo.capitalize())}"
                    f"  ·  {grados_config.get(str(g), {}).get('color', '')}"
                ),
                key="a_grado",
            )

        col3, col4 = st.columns([1, 2])
        with col3:
            prefijo = st.selectbox(
                "Documento",
                options=["V", "E", "S/C"],
                help="V = Venezolano · E = Extranjero · S/C = Sin cédula",
                key="a_prefijo",
            )
        with col4:
            cedula = st.text_input(
                "Número de cédula",
                placeholder="Solo números, sin puntos ni espacios" if prefijo != "S/C" else "No aplica",
                disabled=(prefijo == "S/C"),
                key="a_cedula",
            )

        notas = st.text_input(
            "Observaciones (opcional)",
            placeholder="Ej: Examen con condición especial",
            key="a_notas",
        )

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        if st.button("Agregar alumno a la orden", type="primary", use_container_width=True):
            errores = []
            if not nombre.strip():
                errores.append("El nombre completo es obligatorio.")
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
                # Reset inputs
                for k in ["a_nombre", "a_cedula", "a_notas"]:
                    st.session_state.pop(k, None)
                st.success(f"✓  {nombre.strip()} agregado correctamente.")
                st.rerun()

    # ── Tabla de alumnos ──────────────────────────────────────────────────
    if st.session_state.alumnos:
        _seccion("Alumnos registrados", len(st.session_state.alumnos))
        _tabla_alumnos(st.session_state.alumnos, tipos_grado, editable=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        col_back, col_next = st.columns([1, 2])
        with col_back:
            if st.button("← Atrás", type="secondary", use_container_width=True):
                st.session_state.paso = 1
                st.rerun()
        with col_next:
            if st.button("Revisar orden →", type="primary", use_container_width=True):
                st.session_state.paso = 3
                st.rerun()
    else:
        st.markdown("<div class='zd-empty'><div class='zd-empty-icon'>👤</div><div class='zd-empty-text'>Aún no has agregado alumnos a esta orden.</div></div>", unsafe_allow_html=True)
        if st.button("← Atrás", type="secondary"):
            st.session_state.paso = 1
            st.rerun()


# ── Paso 3 — Resumen y envío ──────────────────────────────────────────────────

def _paso_resumen(usuario: dict, tipos_grado: dict):
    # Datos generales de la orden
    _seccion("Datos de la orden")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Organización", usuario["organizacion"].upper())
    col2.metric("Dojo",         usuario["dojo"].replace("_", " ").title())
    col3.metric("Ciudad",       st.session_state.orden_ciudad)
    col4.metric("Fecha",        st.session_state.orden_fecha.strftime("%d/%m/%Y"))

    # Lista de alumnos
    _seccion("Alumnos", len(st.session_state.alumnos))

    _tabla_alumnos(st.session_state.alumnos, tipos_grado, editable=False)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.warning("⚠ Revisa los datos cuidadosamente. Una vez enviada, la orden no puede modificarse.")
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    col_back, col_send = st.columns([1, 2])
    with col_back:
        if st.button("← Editar", type="secondary", use_container_width=True):
            st.session_state.paso = 2
            st.rerun()
    with col_send:
        if st.button("✓ Confirmar y enviar orden", type="primary", use_container_width=True):
            _enviar_orden(usuario)


def _enviar_orden(usuario: dict):
    with st.spinner("Registrando orden..."):
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
            for key in ["paso", "alumnos", "orden_ciudad", "orden_fecha"]:
                st.session_state.pop(key, None)

            st.success(f"""
            ✅ **Orden registrada exitosamente**

            ID de tu solicitud: **{id_orden}**

            El operador revisará y procesará tu orden en breve.
            Puedes enviar una nueva orden cuando lo necesites.
            """)

        except Exception as e:
            st.error(f"No se pudo registrar la orden: {e}")


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    usuario     = st.session_state.usuario
    config_org  = _cargar_config_org(usuario["organizacion"])
    tipos_grado = _cargar_tipos_grado()

    _header(usuario)

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
        if st.button("Salir", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()