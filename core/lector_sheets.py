"""
lector_sheets.py
----------------
Toda la comunicación con Google Sheets.
Los demás módulos ignoran completamente la existencia de Google Sheets.

Requiere en .env:
    GOOGLE_SHEET_ID = ID del spreadsheet de Google Sheets

Requiere en la raíz del proyecto:
    credenciales.json — cuenta de servicio de Google Cloud con acceso a Sheets API
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

logger = logging.getLogger(__name__)

# ── Configuración ─────────────────────────────────────────────────────────────

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

_RUTA_CREDENCIALES = Path(__file__).parent.parent / "credenciales.json"
_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

_HOJA_ORDENES = "ORDENES"

# Columnas de la hoja ORDENES (orden exacto definido en el setup)
_COL = {
    "id_orden":          0,
    "timestamp":         1,
    "instructor":        2,
    "organizacion":      3,
    "dojo":              4,
    "ciudad":            5,
    "estado":            6,
    "total_alumnos":     7,
    "registro_inicio":   8,
    "registro_fin":      9,
}

# Columnas de las hojas por orden (estructura universal)
_COL_ALUMNO = {
    "nombre_alumno":  0,
    "cedula":         1,
    "prefijo_cedula": 2,
    "grado":          3,
    "tipo":           4,
    "notas":          5,
}

# Estados válidos de una orden
class Estado:
    PENDIENTE   = "PENDIENTE"
    APROBADA    = "APROBADA"
    RECHAZADA   = "RECHAZADA"
    PROCESANDO  = "PROCESANDO"
    COMPLETADA  = "COMPLETADA"
    ERROR       = "ERROR"


# ── Helpers privados ──────────────────────────────────────────────────────────

def _validar_configuracion() -> None:
    """
    Verifica que las variables de entorno y credenciales estén disponibles
    antes de intentar cualquier conexión.

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está definido en .env.
    """
    if not _RUTA_CREDENCIALES.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales en: {_RUTA_CREDENCIALES}\n"
            "Asegúrate de colocar credenciales.json en la raíz del proyecto."
        )

    if not _SHEET_ID:
        raise EnvironmentError(
            "La variable de entorno GOOGLE_SHEET_ID no está definida.\n"
            "Agrégala en tu archivo .env: GOOGLE_SHEET_ID=tu_id_aqui"
        )


def _fila_a_orden(fila: list) -> dict:
    """
    Convierte una fila de la hoja ORDENES en un diccionario estructurado.

    Args:
        fila: Lista de valores en el orden de _COL.

    Returns:
        Diccionario con los campos de la orden.
    """
    def get(col: str) -> str:
        idx = _COL[col]
        return fila[idx].strip() if idx < len(fila) else ""

    return {
        "id_orden":        get("id_orden"),
        "timestamp":       get("timestamp"),
        "instructor":      get("instructor"),
        "organizacion":    get("organizacion"),
        "dojo":            get("dojo"),
        "ciudad":          get("ciudad"),
        "estado":          get("estado"),
        "total_alumnos":   get("total_alumnos"),
        "registro_inicio": get("registro_inicio"),
        "registro_fin":    get("registro_fin"),
    }


def _fila_a_alumno(fila: list) -> dict:
    """
    Convierte una fila de una hoja de orden en un diccionario de alumno.

    Args:
        fila: Lista de valores en el orden de _COL_ALUMNO.

    Returns:
        Diccionario con los campos del alumno.
    """
    def get(col: str) -> str:
        idx = _COL_ALUMNO[col]
        return fila[idx].strip() if idx < len(fila) else ""

    return {
        "nombre_alumno":  get("nombre_alumno"),
        "cedula":         get("cedula"),
        "prefijo_cedula": get("prefijo_cedula"),
        "grado":          get("grado"),
        "tipo":           get("tipo"),
        "notas":          get("notas"),
    }


# ── API pública ───────────────────────────────────────────────────────────────

def conectar() -> gspread.Spreadsheet:
    """
    Establece conexión autenticada con Google Sheets via cuenta de servicio.

    Returns:
        Objeto Spreadsheet listo para operar.

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        gspread.exceptions.GSpreadException: Si la autenticación falla
            o el Sheet no es accesible con las credenciales provistas.
    """
    _validar_configuracion()

    credenciales = Credentials.from_service_account_file(
        str(_RUTA_CREDENCIALES),
        scopes=_SCOPES,
    )
    cliente = gspread.authorize(credenciales)
    spreadsheet = cliente.open_by_key(_SHEET_ID)

    logger.info("conectar | conexión establecida | sheet_id=%s", _SHEET_ID)
    return spreadsheet


def leer_ordenes(estado: Optional[str] = None) -> list[dict]:
    """
    Retorna la lista de órdenes desde la hoja ORDENES, opcionalmente
    filtradas por estado.

    Las órdenes se retornan ordenadas por timestamp ascendente (FIFO).

    Args:
        estado: Estado por el que filtrar (ej. Estado.APROBADA).
                Si es None, retorna todas las órdenes.

    Returns:
        Lista de diccionarios con los datos de cada orden.
        Lista vacía si no hay órdenes que coincidan.

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        gspread.exceptions.WorksheetNotFound: Si la hoja ORDENES no existe.
    """
    spreadsheet = conectar()
    hoja = spreadsheet.worksheet(_HOJA_ORDENES)

    # Omite la fila de encabezados (fila 1)
    filas = hoja.get_all_values()[1:]

    ordenes = [_fila_a_orden(fila) for fila in filas if any(fila)]

    if estado:
        ordenes = [o for o in ordenes if o["estado"] == estado]

    # Orden FIFO por timestamp
    ordenes.sort(key=lambda o: o["timestamp"])

    logger.info(
        "leer_ordenes | estado=%s | total=%d",
        estado or "TODOS",
        len(ordenes),
    )
    return ordenes


def leer_alumnos(id_orden: str) -> list[dict]:
    """
    Retorna los datos de todos los alumnos de una orden específica.

    Cada orden tiene su propia hoja en el spreadsheet, nombrada
    con el id_orden correspondiente.

    Args:
        id_orden: Identificador único de la orden (ej. 'ORD-2025-001').

    Returns:
        Lista de diccionarios con los datos de cada alumno.

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        gspread.exceptions.WorksheetNotFound: Si no existe una hoja
            con el nombre id_orden en el spreadsheet.
    """
    spreadsheet = conectar()

    try:
        hoja = spreadsheet.worksheet(id_orden)
    except gspread.exceptions.WorksheetNotFound:
        raise gspread.exceptions.WorksheetNotFound(
            f"No se encontró la hoja '{id_orden}' en el spreadsheet.\n"
            "Verifica que la orden existe y que su hoja fue creada correctamente."
        )

    # Omite la fila de encabezados (fila 1)
    filas = hoja.get_all_values()[1:]
    alumnos = [_fila_a_alumno(fila) for fila in filas if any(fila)]

    logger.info("leer_alumnos | id_orden=%s | total=%d", id_orden, len(alumnos))
    return alumnos


def actualizar_estado(id_orden: str, estado: str) -> None:
    """
    Cambia el estado de una orden en la hoja ORDENES.

    Busca la fila cuyo id_orden coincida y actualiza únicamente
    la celda de estado.

    Args:
        id_orden: Identificador único de la orden a actualizar.
        estado: Nuevo estado a establecer (usar constantes de Estado).

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        ValueError: Si no se encuentra ninguna orden con ese id_orden.
        gspread.exceptions.WorksheetNotFound: Si la hoja ORDENES no existe.
    """
    spreadsheet = conectar()
    hoja = spreadsheet.worksheet(_HOJA_ORDENES)

    # Busca el id_orden en la columna A (índice 1 en gspread, base 1)
    col_id = _COL["id_orden"] + 1
    col_estado = _COL["estado"] + 1

    celda = hoja.find(id_orden, in_column=col_id)

    if celda is None:
        raise ValueError(
            f"No se encontró la orden '{id_orden}' en la hoja ORDENES."
        )

    hoja.update_cell(celda.row, col_estado, estado)

    logger.info(
        "actualizar_estado | id_orden=%s | nuevo_estado=%s",
        id_orden,
        estado,
    )


def crear_orden(datos_orden: dict) -> str:
    """
    Inserta una nueva orden en la hoja ORDENES con estado PENDIENTE.

    Genera un id_orden secuencial basado en el año actual y el número
    de filas existentes en la hoja.

    Args:
        datos_orden: Diccionario con los campos de la orden:
            - instructor (str)
            - organizacion (str)
            - dojo (str)
            - tipo (str): 'dan' o 'kyu'
            - total_alumnos (int)

    Returns:
        El id_orden generado para la nueva orden (ej. 'ORD-2025-001').

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        KeyError: Si faltan campos obligatorios en datos_orden.
        gspread.exceptions.WorksheetNotFound: Si la hoja ORDENES no existe.
    """
    campos_requeridos = {"instructor", "organizacion", "dojo", "total_alumnos"}
    faltantes = campos_requeridos - datos_orden.keys()
    if faltantes:
        raise KeyError(
            f"Faltan campos obligatorios en datos_orden: {faltantes}"
        )

    spreadsheet = conectar()
    hoja = spreadsheet.worksheet(_HOJA_ORDENES)

    # Genera id_orden secuencial
    filas_existentes = len(hoja.get_all_values())  # incluye encabezado
    numero = filas_existentes  # fila 1 = encabezado, fila 2 = orden 001
    anio = datetime.now().year
    id_orden = f"ORD-{anio}-{numero:03d}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    nueva_fila = [""] * len(_COL)
    nueva_fila[_COL["id_orden"]]        = id_orden
    nueva_fila[_COL["timestamp"]]       = timestamp
    nueva_fila[_COL["instructor"]]      = datos_orden["instructor"]
    nueva_fila[_COL["organizacion"]]    = datos_orden["organizacion"]
    nueva_fila[_COL["dojo"]]            = datos_orden["dojo"]
    nueva_fila[_COL["estado"]]          = Estado.PENDIENTE
    nueva_fila[_COL["total_alumnos"]]   = str(datos_orden["total_alumnos"])
    nueva_fila[_COL["registro_inicio"]] = ""
    nueva_fila[_COL["registro_fin"]]    = ""

    hoja.append_row(nueva_fila, value_input_option="USER_ENTERED")

    logger.info(
        "crear_orden | id_orden=%s | org=%s | dojo=%s | alumnos=%d",
        id_orden,
        datos_orden["organizacion"],
        datos_orden["dojo"],
        datos_orden["total_alumnos"],
    )
    return id_orden
"""
def crear_hoja_orden(id_orden: str, alumnos: list[dict]) -> None:
    
    Crea una hoja nueva en el spreadsheet nombrada con el id_orden
    y la llena con los datos de los alumnos del lote.

    Debe llamarse inmediatamente después de crear_orden(). Si falla,
    la fila en ORDENES debe eliminarse para mantener consistencia.

    Args:
        id_orden: Identificador único de la orden (ej. 'ORD-2025-001').
        alumnos: Lista de diccionarios con los campos de cada alumno:
            - nombre_alumno (str)
            - cedula (str)
            - grado (str)
            - notas (str) — puede ser vacío

    Raises:
        FileNotFoundError: Si credenciales.json no existe.
        EnvironmentError: Si GOOGLE_SHEET_ID no está en .env.
        ValueError: Si la lista de alumnos está vacía.
        gspread.exceptions.APIError: Si falla la creación de la hoja.
    
    if not alumnos:
        raise ValueError(
            f"La lista de alumnos para la orden '{id_orden}' está vacía."
        )

    spreadsheet = conectar()
    hoja = spreadsheet.add_worksheet(title=id_orden, rows=len(alumnos) + 1, cols=4)

    encabezados = ["nombre_alumno", "cedula", "grado", "notas"]
    filas = [encabezados] + [
        [
            alumno.get("nombre_alumno", ""),
            alumno.get("cedula", ""),
            alumno.get("grado", ""),
            alumno.get("notas", ""),
        ]
        for alumno in alumnos
    ]

    hoja.update(filas, "A1")

    logger.info(
        "crear_hoja_orden | id_orden=%s | total_alumnos=%d",
        id_orden,
        len(alumnos),
    )
"""