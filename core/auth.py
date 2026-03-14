"""
auth.py
-------
Lógica de autenticación del sistema.

Entorno local:   lee usuarios desde data/usuarios.json
Streamlit Cloud: lee usuarios desde st.secrets["usuarios"]["data"]
"""

import hashlib
import json
from pathlib import Path

_RUTA_USUARIOS = Path(__file__).parent.parent / "data" / "usuarios.json"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _en_streamlit_cloud() -> bool:
    try:
        import streamlit as st
        return "usuarios" in st.secrets
    except Exception:
        return False


def _cargar_usuarios() -> list[dict]:
    if _en_streamlit_cloud():
        import streamlit as st
        data = json.loads(st.secrets["usuarios"]["data"])
        return data["usuarios"]

    if not _RUTA_USUARIOS.exists():
        raise FileNotFoundError(
            f"No se encontró data/usuarios.json en: {_RUTA_USUARIOS}"
        )
    return json.loads(_RUTA_USUARIOS.read_text(encoding="utf-8"))["usuarios"]


def autenticar(usuario: str, password: str) -> dict | None:
    try:
        usuarios = _cargar_usuarios()
    except Exception:
        return None

    hash_ingresado = _hash(password)
    for u in usuarios:
        if u["usuario"] == usuario and u["password_hash"] == hash_ingresado:
            return u
    return None


def es_operador(usuario: dict) -> bool:
    return usuario.get("rol") == "operador"


def es_instructor(usuario: dict) -> bool:
    return usuario.get("rol") == "instructor"