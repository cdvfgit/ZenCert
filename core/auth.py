"""
auth.py
-------
Lógica de autenticación del sistema.
Lee usuarios desde data/usuarios.json y verifica credenciales.
"""

import hashlib
import json
from pathlib import Path

_RUTA_USUARIOS = Path(__file__).parent.parent / "data" / "usuarios.json"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _cargar_usuarios() -> list[dict]:
    if not _RUTA_USUARIOS.exists():
        raise FileNotFoundError(
            f"No se encontró data/usuarios.json en: {_RUTA_USUARIOS}"
        )
    return json.loads(_RUTA_USUARIOS.read_text(encoding="utf-8"))["usuarios"]


def autenticar(usuario: str, password: str) -> dict | None:
    """
    Verifica credenciales y retorna el dict del usuario si son correctas.

    Args:
        usuario: Nombre de usuario.
        password: Contraseña en texto plano.

    Returns:
        Dict del usuario si las credenciales son correctas, None si no.
    """
    try:
        usuarios = _cargar_usuarios()
    except FileNotFoundError:
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