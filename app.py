"""
app.py
------
Punto de entrada de la aplicación Streamlit.
Maneja el estado de sesión y enruta a la vista correcta.

Uso:
    streamlit run app.py
"""

import streamlit as st

# ── Configuración de página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="Zen Dojo",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Global ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset y base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0d1f2d 0%, #0a0a0f 60%) !important;
}

/* ── Ocultar elementos de Streamlit ── */
#MainMenu, footer, header,
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #00d4aa; border-radius: 2px; }

/* ── Tipografía ── */
h1, h2, h3 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #111827 !important;
    border: 1px solid #1e3a4a !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #00d4aa !important;
    box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.15) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background-color: #111827 !important;
    border: 1px solid #1e3a4a !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Date input ── */
[data-testid="stDateInput"] input {
    background-color: #111827 !important;
    border: 1px solid #1e3a4a !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Botones primarios ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #00d4aa, #00a896) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0, 212, 170, 0.35) !important;
}

/* ── Botones secundarios ── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    color: #00d4aa !important;
    border: 1px solid #00d4aa !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}

[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(0, 212, 170, 0.1) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #1e3a4a !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e3a4a !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Alertas ── */
[data-testid="stSuccess"] {
    background-color: rgba(0, 212, 170, 0.1) !important;
    border-left: 3px solid #00d4aa !important;
    border-radius: 8px !important;
}

[data-testid="stError"] {
    background-color: rgba(239, 68, 68, 0.1) !important;
    border-left: 3px solid #ef4444 !important;
    border-radius: 8px !important;
}

[data-testid="stWarning"] {
    background-color: rgba(245, 158, 11, 0.1) !important;
    border-left: 3px solid #f59e0b !important;
    border-radius: 8px !important;
}

[data-testid="stInfo"] {
    background-color: rgba(0, 212, 170, 0.07) !important;
    border-left: 3px solid #00d4aa !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border-color: #1e3a4a !important; margin: 1.5rem 0 !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #111827 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #1e3a4a !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #64748b !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
    border: none !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background-color: #00d4aa !important;
    color: #0a0a0f !important;
}

/* ── Cards personalizadas ── */
.card {
    background: #111827;
    border: 1px solid #1e3a4a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}

.card:hover { border-color: #00d4aa; }

.card-header {
    font-size: 0.75rem;
    font-weight: 600;
    color: #00d4aa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.25rem;
}

.card-meta {
    font-size: 0.8rem;
    color: #64748b;
}

/* ── Badge de estado ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-pendiente  { background: rgba(245,158,11,0.15); color: #f59e0b; }
.badge-aprobada   { background: rgba(0,212,170,0.15);  color: #00d4aa; }
.badge-rechazada  { background: rgba(239,68,68,0.15);  color: #ef4444; }
.badge-procesando { background: rgba(99,102,241,0.15); color: #818cf8; }
.badge-completada { background: rgba(34,197,94,0.15);  color: #22c55e; }
.badge-error      { background: rgba(239,68,68,0.15);  color: #ef4444; }

/* ── Tabla de alumnos ── */
.alumno-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #111827;
    border: 1px solid #1e3a4a;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.4rem;
    transition: border-color 0.2s;
}

.alumno-row:hover { border-color: #00d4aa33; }

.alumno-nombre { font-weight: 500; color: #f1f5f9; font-size: 0.9rem; }
.alumno-meta   { font-size: 0.75rem; color: #64748b; margin-top: 2px; }

/* ── Header de la app ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid #1e3a4a;
    margin-bottom: 2rem;
}

.app-logo {
    font-size: 1.3rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}

.app-logo span { color: #00d4aa; }

.app-user {
    font-size: 0.8rem;
    color: #64748b;
}

.app-user strong { color: #00d4aa; }

/* ── Step indicator ── */
.steps {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.step {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 500;
}

.step.active { color: #00d4aa; }
.step.done   { color: #22c55e; }

.step-num {
    width: 24px; height: 24px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700;
    background: #1e3a4a; color: #64748b;
}

.step.active .step-num { background: #00d4aa; color: #0a0a0f; }
.step.done   .step-num { background: #22c55e; color: #0a0a0f; }

.step-line { flex: 1; height: 1px; background: #1e3a4a; min-width: 20px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .app-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
    .steps { flex-wrap: wrap; }
}
</style>
""", unsafe_allow_html=True)

# ── Estado de sesión ──────────────────────────────────────────────────────────

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ── Router ────────────────────────────────────────────────────────────────────

if st.session_state.usuario is None:
    from pages.login import render
    render()
elif st.session_state.usuario["rol"] == "operador":
    from pages.operador import render
    render()
else:
    from pages.formulario import render
    render()