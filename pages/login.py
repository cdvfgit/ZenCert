"""
pages/login.py
--------------
Vista de autenticación del sistema.
"""

import streamlit as st
from core.auth import autenticar


def render():
    # ── Layout centrado ───────────────────────────────────────────────────
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.markdown("<div style='height: 8vh'></div>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2.5rem;'>
            <div style='font-size: 2.8rem; margin-bottom: 0.5rem;'>🥋</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.02em;'>
                Sistema de <span style='color: #00d4aa;'>Certificados</span>
            </div>
            <div style='font-size: 0.8rem; color: #64748b; margin-top: 0.4rem;'>
                Artes Marciales
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card de login
        st.markdown("""
        <div style='
            background: #111827;
            border: 1px solid #1e3a4a;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1rem;
        '>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='font-size: 1rem; font-weight: 600; color: #f1f5f9;
                    margin-bottom: 1.5rem; letter-spacing: -0.01em;'>
            Iniciar sesión
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input(
            "Usuario",
            placeholder="tu_usuario",
            key="login_usuario",
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Ingresar", type="primary", use_container_width=True):
            if not usuario or not password:
                st.error("Ingresa tu usuario y contraseña.")
            else:
                resultado = autenticar(usuario.strip(), password)
                if resultado:
                    st.session_state.usuario = resultado
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align: center; font-size: 0.75rem; color: #334155; margin-top: 1rem;'>
            Acceso restringido al personal autorizado
        </div>
        """, unsafe_allow_html=True)