"""
pages/login.py
--------------
Vista de autenticación del sistema.
"""

import streamlit as st
from core.auth import autenticar


def render():
    # Contenedor centrado sin columnas anidadas
    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.2, 1])

    with col_c:
        # Logo
        st.markdown("""
        <div style='text-align:center; margin-bottom:2rem;'>
            <div style='font-size:2.5rem; margin-bottom:0.75rem;
                        filter:drop-shadow(0 0 12px rgba(0,229,192,0.3));'>🥋</div>
            <div style='font-family:Syne,sans-serif; font-size:1.4rem;
                        font-weight:700; color:#f0f4f8; letter-spacing:-0.02em;
                        margin-bottom:0.3rem;'>
                Zen <span style='color:#00e5c0;'>Dojo</span>
            </div>
            <div style='font-size:0.75rem; color:#445566; letter-spacing:0.06em;
                        text-transform:uppercase; font-weight:500;'>
                Sistema de Certificados
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card contenedor visual
        st.markdown("""
        <div style='background:#0d1117; border:1px solid #1a2535;
                    border-radius:16px; padding:1.75rem 1.5rem 0.5rem 1.5rem;
                    box-shadow:0 24px 48px rgba(0,0,0,0.4);
                    margin-bottom:0.5rem;'>
            <div style='font-family:Syne,sans-serif; font-size:0.9rem;
                        font-weight:600; color:#f0f4f8; margin-bottom:1rem;'>
                Iniciar sesión
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Inputs fuera del HTML para que Streamlit los maneje correctamente
        usuario_input  = st.text_input("Usuario",    placeholder="tu_usuario",  key="li_user")
        password_input = st.text_input("Contraseña", placeholder="••••••••",
                                       type="password", key="li_pass")

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        if st.button("Ingresar →", type="primary", use_container_width=True, key="li_btn"):
            if not usuario_input.strip() or not password_input:
                st.error("Ingresa tu usuario y contraseña.")
            else:
                try:
                    resultado = autenticar(usuario_input.strip(), password_input)
                    if resultado:
                        st.session_state["usuario"] = resultado
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                except Exception as e:
                    st.error(f"Error de autenticación: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        """     
        if st.button("Ingresar →", type="primary", use_container_width=True, key="li_btn"):
            if not usuario_input.strip() or not password_input:
                st.error("Ingresa tu usuario y contraseña.")
            else:
                resultado = autenticar(usuario_input.strip(), password_input)
                if resultado:
                    st.session_state["usuario"] = resultado
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        """
        st.markdown("""
        <div style='text-align:center; font-size:0.72rem; color:#1a2535;
                    margin-top:1rem; padding-bottom:0.5rem;'>
            Acceso restringido · Personal autorizado
        </div>
        """, unsafe_allow_html=True)