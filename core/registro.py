"""
registro.py
-----------
Control de numeración secuencial de certificados por organización.
Lee y escribe data/registros.json con escritura diferida.

El archivo solo se modifica en disco cuando el operador confirma
explícitamente que los certificados son correctos. Si ocurre un
rollback, este módulo no requiere ninguna acción — nunca escribió.
"""

import json
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

# Ruta al archivo de registros relativa a la raíz del proyecto
_RUTA_REGISTROS = Path(__file__).parent.parent / "data" / "registros.json"


# ── Helpers privados ──────────────────────────────────────────────────────────

def _leer_json() -> dict:
    """
    Carga el contenido completo de registros.json.

    Returns:
        Diccionario con todos los registros por organización.

    Raises:
        FileNotFoundError: Si registros.json no existe en disco.
        ValueError: Si el archivo existe pero contiene JSON inválido.
    """
    if not _RUTA_REGISTROS.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de registros en: {_RUTA_REGISTROS}\n"
            "Asegúrate de que 'data/registros.json' exista en la raíz del proyecto."
        )

    try:
        return json.loads(_RUTA_REGISTROS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El archivo de registros contiene JSON inválido: {e}\n"
            f"Ruta: {_RUTA_REGISTROS}"
        ) from e


def _escribir_json(datos: dict) -> None:
    """
    Persiste el diccionario completo en registros.json.

    Args:
        datos: Contenido completo a escribir en el archivo.

    Raises:
        OSError: Si no se puede escribir en disco.
    """
    try:
        _RUTA_REGISTROS.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        raise OSError(
            f"No se pudo escribir en registros.json: {e}\n"
            f"Ruta: {_RUTA_REGISTROS}"
        ) from e


# ── API pública ───────────────────────────────────────────────────────────────

def leer_ultimo(organizacion: str) -> int:
    """
    Retorna el último número de registro emitido para la organización.

    Si la organización no existe en el archivo, retorna 0 (ningún
    certificado emitido aún).

    Args:
        organizacion: Código de la organización (ej. 'ocoa').

    Returns:
        Último número de registro emitido, o 0 si la organización
        no tiene registros previos.

    Raises:
        FileNotFoundError: Si registros.json no existe en disco.
        ValueError: Si registros.json contiene JSON inválido.
    """
    datos = _leer_json()
    ultimo = datos.get(organizacion, {}).get("ultimo_registro", 0)
    logger.debug("leer_ultimo | org=%s | ultimo=%d", organizacion, ultimo)
    return ultimo


def reservar_rango(organizacion: str, cantidad: int) -> tuple[int, int]:
    """
    Calcula en memoria el rango de números para el lote.

    No escribe nada en disco. El rango queda reservado lógicamente
    hasta que el operador llame a confirmar() o descarte la operación.

    Args:
        organizacion: Código de la organización (ej. 'ocoa').
        cantidad: Número de certificados del lote. Debe ser >= 1.

    Returns:
        Tupla (inicio, fin) con el rango asignado al lote.
        Ejemplo: si ultimo=137 y cantidad=5 → (138, 142).

    Raises:
        ValueError: Si cantidad es menor que 1.
        FileNotFoundError: Si registros.json no existe en disco.
    """
    if cantidad < 1:
        raise ValueError(
            f"La cantidad de certificados debe ser al menos 1. Recibido: {cantidad}"
        )

    ultimo = leer_ultimo(organizacion)
    inicio = ultimo + 1
    fin = ultimo + cantidad

    logger.debug(
        "reservar_rango | org=%s | cantidad=%d | rango=(%d, %d)",
        organizacion, cantidad, inicio, fin,
    )
    return inicio, fin


def confirmar(organizacion: str, ultimo_nuevo: int) -> None:
    """
    Persiste en disco el nuevo estado del registro tras una generación
    confirmada por el operador.

    Es el único punto del módulo que escribe en disco. Solo debe
    llamarse cuando el operador ha verificado que los certificados
    son correctos.

    Args:
        organizacion: Código de la organización (ej. 'ocoa').
        ultimo_nuevo: Último número de registro del lote confirmado.

    Raises:
        ValueError: Si ultimo_nuevo es menor o igual al valor actual,
                    lo que indicaría un retroceso en la numeración.
        FileNotFoundError: Si registros.json no existe en disco.
        OSError: Si no se puede escribir en disco.
    """
    datos = _leer_json()

    registro_actual = datos.get(organizacion, {}).get("ultimo_registro", 0)

    if ultimo_nuevo <= registro_actual:
        raise ValueError(
            f"El nuevo registro ({ultimo_nuevo}) debe ser mayor al actual "
            f"({registro_actual}) para la organización '{organizacion}'."
        )

    total_anterior = datos.get(organizacion, {}).get("total_emitidos", 0)
    certificados_nuevos = ultimo_nuevo - registro_actual

    datos[organizacion] = {
        "ultimo_registro": ultimo_nuevo,
        "ultimo_actualizado": date.today().isoformat(),
        "total_emitidos": total_anterior + certificados_nuevos,
    }

    _escribir_json(datos)

    logger.info(
        "confirmar | org=%s | ultimo_nuevo=%d | total_emitidos=%d",
        organizacion,
        ultimo_nuevo,
        datos[organizacion]["total_emitidos"],
    )