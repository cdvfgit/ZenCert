"""
app.py
------
Punto de entrada de la aplicación Streamlit.
Maneja el estado de sesión y enruta a la vista correcta.

Uso:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Zen Dojo",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
    --bg:        #080c10;
    --bg-2:      #0d1117;
    --bg-3:      #111820;
    --border:    #1a2535;
    --border-2:  #243040;
    --cyan:      #00e5c0;
    --cyan-dim:  #00b899;
    --cyan-glow: rgba(0,229,192,0.12);
    --cyan-soft: rgba(0,229,192,0.06);
    --red:       #ff4d6a;
    --amber:     #ffb830;
    --green:     #00d17a;
    --text-1:    #f0f4f8;
    --text-2:    #8899aa;
    --text-3:    #445566;
    --radius:    10px;
    --radius-lg: 16px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 48px 48px;
    opacity: 0.15;
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer, header,
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stMainBlockContainer"] {
    padding: 1.5rem 1.25rem !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 3px; }

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--text-1) !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-3) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--radius) !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--text-3) !important; }

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
    color: var(--text-2) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-3) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--radius) !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Date */
[data-testid="stDateInput"] input {
    background: var(--bg-3) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--radius) !important;
    color: var(--text-1) !important;
}

/* Botones primarios */
[data-testid="stButton"] > button[kind="primary"] {
    background: var(--cyan) !important;
    color: #080c10 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #00ffda !important;
    box-shadow: 0 0 20px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}

/* Botones secundarios */
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.15s !important;
}

[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    background: var(--cyan-soft) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    transition: border-color 0.15s !important;
}

[data-testid="stExpander"]:hover { border-color: var(--border-2) !important; }

[data-testid="stExpander"] summary {
    color: var(--text-1) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* Alertas */
div.stSuccess > div {
    background: rgba(0,209,122,0.08) !important;
    border-left: 3px solid var(--green) !important;
    border-radius: var(--radius) !important;
    color: #b3f0d4 !important;
}

div.stError > div {
    background: rgba(255,77,106,0.08) !important;
    border-left: 3px solid var(--red) !important;
    border-radius: var(--radius) !important;
    color: #ffc0c9 !important;
}

div.stWarning > div {
    background: rgba(255,184,48,0.08) !important;
    border-left: 3px solid var(--amber) !important;
    border-radius: var(--radius) !important;
    color: #ffe8b0 !important;
}

div.stInfo > div {
    background: var(--cyan-soft) !important;
    border-left: 3px solid var(--cyan) !important;
    border-radius: var(--radius) !important;
    color: #b0f0e8 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 4px !important;
    gap: 2px !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-3) !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border: none !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--text-1) !important;
    background: var(--bg-3) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--cyan) !important;
    color: #080c10 !important;
    font-weight: 600 !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 0.85rem 1rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    color: var(--text-3) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    color: var(--text-1) !important;
    font-weight: 600 !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.25rem 0 !important;
}

/* ── Componentes propios ── */

.zd-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.25rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.zd-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-1);
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}

.zd-logo-accent { color: var(--cyan); }

.zd-user-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
}

.zd-pill {
    background: var(--bg-3);
    border: 1px solid var(--border-2);
    border-radius: 20px;
    padding: 0.22rem 0.7rem;
    font-size: 0.73rem;
    color: var(--text-2);
    font-weight: 500;
}

.zd-pill-cyan {
    background: var(--cyan-soft);
    border-color: rgba(0,229,192,0.2);
    color: var(--cyan);
    font-weight: 600;
}

/* Steps */
.zd-steps {
    display: flex;
    align-items: stretch;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: 2rem;
}

.zd-step {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.45rem;
    padding: 0.7rem 0.5rem;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-3);
    white-space: nowrap;
    transition: all 0.15s;
    position: relative;
}

.zd-step + .zd-step::before {
    content: '';
    position: absolute;
    left: 0;
    top: 20%;
    height: 60%;
    width: 1px;
    background: var(--border);
}

.zd-step-active {
    background: var(--cyan-glow);
    color: var(--cyan);
}

.zd-step-done { color: var(--green); }

.zd-step-num {
    width: 18px; height: 18px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 700;
    background: var(--border-2);
    color: var(--text-3);
    flex-shrink: 0;
}

.zd-step-active .zd-step-num { background: var(--cyan); color: #080c10; }
.zd-step-done   .zd-step-num { background: var(--green); color: #080c10; }

/* Cards */
.zd-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.5rem;
}

.zd-card-cyan {
    border-color: rgba(0,229,192,0.18);
    background: linear-gradient(135deg, var(--bg-2), rgba(0,229,192,0.03));
}

.zd-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.3rem;
}

.zd-value {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-1);
}

.zd-sub {
    font-size: 0.75rem;
    color: var(--text-2);
    margin-top: 0.15rem;
}

/* Alumno row */
.zd-alumno {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.3rem;
    transition: border-color 0.15s;
    gap: 0.5rem;
}

.zd-alumno:hover { border-color: var(--border-2); }

.zd-alumno-nombre {
    font-weight: 500;
    color: var(--text-1);
    font-size: 0.875rem;
}

.zd-alumno-meta {
    font-size: 0.73rem;
    color: var(--text-2);
    margin-top: 0.2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    align-items: center;
}

.zd-tag {
    background: var(--bg-3);
    border: 1px solid var(--border-2);
    border-radius: 4px;
    padding: 0.08rem 0.4rem;
    font-size: 0.68rem;
    color: var(--text-2);
}

.zd-tag-cyan {
    background: var(--cyan-soft);
    border-color: rgba(0,229,192,0.15);
    color: var(--cyan);
}

/* Badges */
.zd-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.55rem;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.zd-badge::before {
    content: '';
    width: 4px; height: 4px;
    border-radius: 50%;
    background: currentColor;
}

.zd-badge-pendiente  { background: rgba(255,184,48,0.1);  color: var(--amber); }
.zd-badge-aprobada   { background: var(--cyan-soft);       color: var(--cyan);  }
.zd-badge-rechazada  { background: rgba(255,77,106,0.1);  color: var(--red);   }
.zd-badge-procesando { background: rgba(99,102,241,0.1);  color: #818cf8;      }
.zd-badge-completada { background: rgba(0,209,122,0.1);   color: var(--green); }
.zd-badge-error      { background: rgba(255,77,106,0.1);  color: var(--red);   }

/* Section title */
.zd-section {
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.zd-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.zd-count {
    background: var(--cyan);
    color: #080c10;
    border-radius: 20px;
    padding: 0.05rem 0.45rem;
    font-size: 0.65rem;
    font-weight: 700;
}

/* Empty state */
.zd-empty {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-3);
}

.zd-empty-icon { font-size: 1.75rem; opacity: 0.35; margin-bottom: 0.6rem; }
.zd-empty-text { font-size: 0.85rem; }

/* Responsive móvil */
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding: 0.9rem 0.7rem !important; }
    .zd-logo { font-size: 0.95rem; }
    .zd-step { padding: 0.55rem 0.3rem; font-size: 0.7rem; }
    .zd-step-label { display: none; }
}
</style>
""", unsafe_allow_html=True)

import pages.login as _login
import pages.operador as _operador
import pages.formulario as _formulario

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

_usuario = st.session_state.get("usuario")

if _usuario is None:
    _login.render()
elif _usuario.get("rol") == "operador":
    _operador.render()
else:
    _formulario.render()