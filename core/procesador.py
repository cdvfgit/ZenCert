"""
procesador.py
-------------
Transforma datos crudos del Google Sheet en datos listos para el generador.
No conoce Google Sheets ni python-pptx.

Fuentes de verdad:
  - data/tipos_grado.json          — catálogo global de tipos de grado
  - data/organizaciones/{org}.json — colores, dojos y placeholders por organización
"""

import json
import logging
import os
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Configuración ─────────────────────────────────────────────────────────────

_RUTA_TIPOS_GRADO   = Path(__file__).parent.parent / "data" / "tipos_grado.json"
_RUTA_ORGANIZACIONES = Path(__file__).parent.parent / "data" / "organizaciones"


# ── Tablas de conversión japonesa ─────────────────────────────────────────────

# Dígitos arábigos → caracteres japoneses
DIGITOS_JP: dict[str, str] = {
    "0": "〇",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
}

# Meses en japonés (1–12)
MESES_JP: dict[int, str] = {
    1:  "一月",
    2:  "二月",
    3:  "三月",
    4:  "四月",
    5:  "五月",
    6:  "六月",
    7:  "七月",
    8:  "八月",
    9:  "九月",
    10: "十月",
    11: "十一月",
    12: "十二月",
}


# ── Helpers privados ──────────────────────────────────────────────────────────

def _cargar_tipos_grado() -> dict:
    """
    Carga el catálogo global de tipos de grado desde tipos_grado.json.

    Returns:
        Diccionario con todos los tipos de grado disponibles.

    Raises:
        FileNotFoundError: Si tipos_grado.json no existe.
        ValueError: Si el archivo contiene JSON inválido.
    """
    if not _RUTA_TIPOS_GRADO.exists():
        raise FileNotFoundError(
            f"No se encontró el catálogo de tipos en: {_RUTA_TIPOS_GRADO}\n"
            "Asegúrate de que 'data/tipos_grado.json' exista en el proyecto."
        )

    try:
        return json.loads(_RUTA_TIPOS_GRADO.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El archivo tipos_grado.json contiene JSON inválido: {e}"
        ) from e


def _cargar_config_org(organizacion: str) -> dict:
    """
    Carga la configuración específica de una organización.

    Args:
        organizacion: Código de la organización (ej. 'ocoa').

    Returns:
        Diccionario con grados, dojos y placeholders de la organización.

    Raises:
        FileNotFoundError: Si no existe el archivo de la organización.
        ValueError: Si el archivo contiene JSON inválido.
    """
    ruta = _RUTA_ORGANIZACIONES / f"{organizacion}.json"

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró configuración para la organización '{organizacion}'\n"
            f"Ruta esperada: {ruta}\n"
            "Verifica que exista el archivo en data/organizaciones/"
        )

    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El archivo {organizacion}.json contiene JSON inválido: {e}"
        ) from e


def _construir_digito_japones(numero: int) -> str:
    """
    Construye la representación japonesa de un número entero (1–99).

    Args:
        numero: Número a convertir.

    Returns:
        Representación japonesa (ej. 2 → '二', 13 → '十三', 25 → '二十五').
    """
    if numero < 10:
        return DIGITOS_JP[str(numero)]
    if numero == 10:
        return "十"

    decena = "十" if numero // 10 == 1 else DIGITOS_JP[str(numero // 10)] + "十"
    unidad = DIGITOS_JP[str(numero % 10)] if numero % 10 != 0 else ""
    return decena + unidad


def _resolver_color(
    numero: int,
    tipo: str,
    dojo: str,
    config_org: dict,
) -> str:
    """
    Resuelve el color del cinturón aplicando herencia dojo → organización.

    Busca primero en la configuración específica del dojo. Si no existe,
    busca en los grados generales de la organización.

    Args:
        numero: Número del grado.
        tipo: Tipo de grado (ej. 'dan', 'kyu', 'shodan').
        dojo: Nombre normalizado del dojo (ej. 'puerto_ordaz').
        config_org: Configuración de la organización cargada desde
                    data/organizaciones/{org}.json.

    Returns:
        Color del cinturón correspondiente.

    Raises:
        ValueError: Si no se encuentra el color para el grado indicado.
    """
    clave = str(numero)

    # Busca primero en el dojo (sobreescritura)
    color = (
        config_org
        .get("dojos", {})
        .get(dojo, {})
        .get("grados", {})
        .get(tipo, {})
        .get(clave, {})
        .get("color")
    )
    if color:
        return color

    # Si no, busca en la organización (herencia)
    color = (
        config_org
        .get("grados", {})
        .get(tipo, {})
        .get(clave, {})
        .get("color")
    )
    if color:
        return color

    raise ValueError(
        f"No se encontró el color para {numero}° {tipo} "
        f"en el dojo '{dojo}' ni en la organización '.\n"
        f"Verifica data/organizaciones/.json."
    )


# ── Funciones de formateo en español ─────────────────────────────────────────

def formatear_cedula(numero: int, prefijo: str = "V") -> str:
    """
    Formatea un número de cédula al estilo venezolano estándar.

    Args:
        numero: Número de cédula sin formato (ej. 25446976).
        prefijo: Prefijo de nacionalidad — 'V' venezolano, 'E' extranjero
                 (default: 'V').

    Returns:
        Cédula formateada (ej. 'C.I.: V- 25.446.976').

    Raises:
        ValueError: Si el número es menor o igual a cero.
        ValueError: Si el prefijo no es 'V' ni 'E'.
    """
    if numero <= 0:
        raise ValueError(
            f"El número de cédula debe ser mayor a cero. Recibido: {numero}"
        )

    prefijo_normalizado = prefijo.upper().strip()
    if prefijo_normalizado not in {"V", "E"}:
        raise ValueError(
            f"Prefijo de cédula inválido: '{prefijo}'. Debe ser 'V' o 'E'."
        )

    return f"C.I.: {prefijo_normalizado}- {numero:,}".replace(",", ".")


def formatear_registro(numero: int) -> str:
    """
    Formatea un número de registro con ceros a la izquierda.

    Args:
        numero: Número de registro (ej. 137).

    Returns:
        Registro formateado (ej. 'Registro N°: 0137').

    Raises:
        ValueError: Si el número es menor o igual a cero.
    """
    if numero <= 0:
        raise ValueError(
            f"El número de registro debe ser mayor a cero. Recibido: {numero}"
        )

    return f"{numero:04d}"


def formatear_grado_espanol(
    grado: int,
    tipo: str,
    organizacion: str,
    dojo: str,
) -> str:
    """
    Construye la descripción completa del grado en español resolviendo
    el color del cinturón desde grados.json.

    Args:
        grado: Número del grado (ej. 1).
        tipo: Tipo de grado (ej. 'dan', 'kyu', 'kyu_sho', 'shodan').
        organizacion: Código de la organización (ej. 'ocoa').
        dojo: Nombre normalizado del dojo (ej. 'puerto_ordaz').

    Returns:
        Descripción completa (ej. 'Cinturón Negro 1° Dan.',
        'Cinturón Verde 5° Kyu.').

    Raises:
        ValueError: Si el grado es menor o igual a cero.
        ValueError: Si no se encuentra el color en la configuración.
        FileNotFoundError: Si grados.json no existe.
    """
    if grado <= 0:
        raise ValueError(
            f"El número de grado debe ser mayor a cero. Recibido: {grado}"
        )

    config_org   = _cargar_config_org(organizacion)
    tipos_grado  = _cargar_tipos_grado()
    color        = _resolver_color(grado, tipo, dojo, config_org)
    nombre_tipo  = tipos_grado.get(tipo, {}).get("nombre", tipo.capitalize())

    return f"Cinturón {color} {grado}° {nombre_tipo}."


def formatear_ciudad_fecha(ciudad: str, fecha: date) -> str:
    """
    Construye la línea de ciudad y fecha en formato estándar para el certificado.

    Args:
        ciudad: Nombre de la ciudad (ej. 'Caracas').
        fecha: Objeto date de Python con la fecha del examen.

    Returns:
        Línea formateada (ej. 'Caracas, 20/02/2025').

    Raises:
        ValueError: Si la ciudad está vacía.
    """
    if not ciudad or not ciudad.strip():
        raise ValueError("El nombre de la ciudad no puede estar vacío.")

    return f"{ciudad.strip()}, {fecha.strftime('%d/%m/%Y')}"


# ── Funciones de conversión al japonés ───────────────────────────────────────

def nombre_a_katakana(
    nombre: str,
    organizacion: str = "",
    modo_prueba: bool = False,
) -> str:
    """
    Transliera un nombre hispanohablante a katakana japonés.

    En modo normal usa Gemini API. En modo prueba retorna una
    transliteración simulada sin consumir tokens.

    Args:
        nombre: Nombre completo del alumno (ej. 'Juan Pérez').
        organizacion: Código de la organización — reservado para
                      contexto futuro en el prompt (ej. 'ocoa').
        modo_prueba: Si es True, retorna katakana simulado sin
                     llamar a la API (default: False).

    Returns:
        Nombre transliterado en katakana (ej. 'ペレス フアン').

    Raises:
        EnvironmentError: Si GEMINI_API_KEY no está definida en .env.
        ValueError: Si el nombre está vacío.
        RuntimeError: Si la API retorna una respuesta inesperada.
    """
    if not nombre or not nombre.strip():
        raise ValueError("El nombre del alumno no puede estar vacío.")

    if modo_prueba:
        logger.debug("nombre_a_katakana | modo_prueba | nombre=%s", nombre)
        return _simular_katakana(nombre)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "La variable de entorno GEMINI_API_KEY no está definida.\n"
            "Agrégala en tu archivo .env: GEMINI_API_KEY=tu_clave_aqui"
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        modelo = genai.GenerativeModel("gemini-2.0-flash")

        prompt = (
            f"Transliera este nombre hispanohablante al katakana japonés.\n"
            f"Responde ÚNICAMENTE con el katakana, sin explicaciones, "
            f"sin romaji, sin puntuación adicional.\n"
            f"Formato: APELLIDO(S) NOMBRE(S) separados por un espacio.\n"
            f"Nombre: {nombre.strip()}"
        )

        respuesta = modelo.generate_content(prompt)
        katakana = respuesta.text.strip()

        if not katakana:
            raise RuntimeError(
                f"Gemini retornó una respuesta vacía para el nombre '{nombre}'."
            )

        logger.info("nombre_a_katakana | nombre=%s | katakana=%s", nombre, katakana)
        return katakana

    except Exception as e:
        # Si la API falla, registra el error y usa la simulación como respaldo
        logger.warning(
            "nombre_a_katakana | fallo API | nombre=%s | error=%s | usando respaldo",
            nombre,
            str(e),
        )
        return _simular_katakana(nombre)


def _simular_katakana(nombre: str) -> str:
    """
    Genera una transliteración katakana simulada para pruebas.

    Convierte cada palabra del nombre a una secuencia de katakana
    usando una tabla de correspondencia básica. No es fonéticamente
    preciso — su único propósito es producir texto katakana válido
    para verificar el diseño del certificado sin consumir tokens.

    Args:
        nombre: Nombre completo del alumno.

    Returns:
        Representación katakana simulada (ej. 'テスト ナマエ').
    """
    # Tabla de correspondencia básica español → katakana aproximado
    _VOCAL_KA: dict[str, str] = {
        "a": "ア", "e": "エ", "i": "イ", "o": "オ", "u": "ウ",
        "ka": "カ", "ke": "ケ", "ki": "キ", "ko": "コ", "ku": "ク",
        "sa": "サ", "se": "セ", "si": "シ", "so": "ソ", "su": "ス",
        "ta": "タ", "te": "テ", "ti": "チ", "to": "ト", "tu": "ツ",
        "na": "ナ", "ne": "ネ", "ni": "ニ", "no": "ノ", "nu": "ヌ",
        "ha": "ハ", "he": "ヘ", "hi": "ヒ", "ho": "ホ", "hu": "フ",
        "ma": "マ", "me": "メ", "mi": "ミ", "mo": "モ", "mu": "ム",
        "ra": "ラ", "re": "レ", "ri": "リ", "ro": "ロ", "ru": "ル",
        "la": "ラ", "le": "レ", "li": "リ", "lo": "ロ", "lu": "ル",
        "ya": "ヤ", "yo": "ヨ", "yu": "ユ",
        "wa": "ワ", "wi": "ウィ", "we": "ウェ", "wo": "ヲ",
        "pa": "パ", "pe": "ペ", "pi": "ピ", "po": "ポ", "pu": "プ",
        "ba": "バ", "be": "ベ", "bi": "ビ", "bo": "ボ", "bu": "ブ",
        "da": "ダ", "de": "デ", "di": "ジ", "do": "ド", "du": "ズ",
        "ga": "ガ", "ge": "ゲ", "gi": "ギ", "go": "ゴ", "gu": "グ",
        "ja": "ハ", "je": "ヘ", "ji": "ヒ", "jo": "ホ", "ju": "フ",
        "n":  "ン",
    }

    def _convertir_palabra(palabra: str) -> str:
        palabra = palabra.lower()
        resultado = []
        i = 0
        while i < len(palabra):
            # Intenta par de letras primero
            if i + 1 < len(palabra) and palabra[i:i+2] in _VOCAL_KA:
                resultado.append(_VOCAL_KA[palabra[i:i+2]])
                i += 2
            elif palabra[i] in _VOCAL_KA:
                resultado.append(_VOCAL_KA[palabra[i]])
                i += 1
            else:
                # Carácter sin mapeo — lo omite silenciosamente
                i += 1
        return "".join(resultado) if resultado else "テスト"

    palabras = nombre.strip().split()
    return " ".join(_convertir_palabra(p) for p in palabras)


def procesar_orden(
    orden: dict,
    alumnos: list[dict],
    registro_inicio: int,
    modo_prueba: bool = False,
) -> list[dict]:
    """
    Orquesta el pipeline completo de transformación de datos de una orden.

    Recibe datos crudos de Google Sheets y retorna una lista de
    diccionarios listos para que generador.py produzca el PPTX.
    No escribe en disco ni llama a Google Sheets.

    Args:
        orden: Cabecera de la orden con los campos:
            - organizacion (str): Código de la organización (ej. 'ocoa')
            - dojo (str): Nombre normalizado del dojo (ej. 'puerto_ordaz')
            - tipo (str): Tipo de grado (ej. 'dan', 'kyu')
            - ciudad (str): Ciudad del examen
            - fecha (date): Fecha del examen
        alumnos: Lista de diccionarios con los datos crudos de cada alumno:
            - nombre_alumno (str)
            - cedula (str): Número sin formato, vacío si no aplica
            - prefijo_cedula (str): 'V', 'E' o vacío si no aplica
            - grado (str): Número del grado
            - notas (str): Observaciones opcionales
        registro_inicio: Primer número de registro asignado al lote,
                         calculado previamente por registro.reservar_rango().
        modo_prueba: Si es True, usa transliteración simulada sin
                     consumir tokens de Gemini (default: False).

    Returns:
        Lista de diccionarios procesados listos para el generador,
        uno por alumno, en el mismo orden que la lista de entrada.

    Raises:
        KeyError: Si faltan campos obligatorios en orden o en algún alumno.
        FileNotFoundError: Si grados.json no existe.
        ValueError: Si algún dato no puede procesarse correctamente.
    """
    organizacion = orden["organizacion"]
    dojo         = orden["dojo"]
    ciudad       = orden["ciudad"]
    fecha        = orden["fecha"]

    # Cargar configuración una sola vez para todo el lote
    config_org  = _cargar_config_org(organizacion)
    tipos_grado = _cargar_tipos_grado()

    # Campos compartidos por todos los alumnos del lote
    fecha_espanol = formatear_ciudad_fecha(ciudad, fecha)
    fecha_jp      = fecha_a_japones(fecha)

    # Procesar cada alumno — tipo viene del alumno, no de la cabecera
    alumnos_procesados = []

    for i, alumno in enumerate(alumnos):
        numero_registro = registro_inicio + i
        numero_grado    = int(alumno["grado"])
        tipo            = alumno.get("tipo", "").strip().lower()
        prefijo         = alumno.get("prefijo_cedula", "").strip().upper()
        cedula_raw      = alumno.get("cedula", "").strip()

        if not tipo:
            raise ValueError(
                f"El alumno '{alumno.get('nombre_alumno', '?')}' no tiene tipo de grado definido."
            )

        # Formatear cédula solo si el alumno tiene documento
        if cedula_raw and prefijo in {"V", "E"}:
            cedula = formatear_cedula(int(cedula_raw), prefijo)
        else:
            cedula = ""

        # Resolver tipo efectivo (puede haber tipo_override por grado)
        tipo_efectivo = (
            config_org
            .get("grados", {})
            .get(tipo, {})
            .get(str(numero_grado), {})
            .get("tipo_override", tipo)
        )
        color       = _resolver_color(numero_grado, tipo_efectivo, dojo, config_org)
        nombre_tipo = tipos_grado.get(tipo_efectivo, {}).get("nombre", tipo_efectivo.capitalize())

        alumnos_procesados.append({
            "nombre_alumno":   alumno["nombre_alumno"].strip(),
            "cedula":          cedula,
            "grado_español":   f"Cinturón {color} {numero_grado}° {nombre_tipo}.",
            "tipo_efectivo":   tipo_efectivo,
            "kanji_grado":     obtener_kanji_grado(numero_grado, tipo_efectivo, organizacion),
            "nombre_katakana": nombre_a_katakana(
                                   alumno["nombre_alumno"],
                                   organizacion=organizacion,
                                   modo_prueba=modo_prueba,
                               ),
            "ciudad_fecha":    fecha_espanol,
            "fecha_japonesa":  fecha_jp,
            "registro":        formatear_registro(numero_registro),
            "codigo_japones":  "".join(DIGITOS_JP[d] for d in f"{numero_registro:03d}"),
        })

        logger.debug(
            "procesar_orden | alumno=%s | registro=%d | grado=%d° %s",
            alumno["nombre_alumno"],
            numero_registro,
            numero_grado,
            tipo_efectivo,
        )

    # Agrupar por tipo_efectivo para generación de PPTX separados
    grupos: dict[str, list[dict]] = {}
    for alumno in alumnos_procesados:
        tipo_ef = alumno["tipo_efectivo"]
        grupos.setdefault(tipo_ef, []).append(alumno)

    logger.info(
        "procesar_orden | id_orden=%s | org=%s | total=%d | grupos=%s",
        orden.get("id_orden", "?"),
        organizacion,
        len(alumnos_procesados),
        list(grupos.keys()),
    )

    return grupos


def fecha_a_japones(fecha: date) -> str:
    """
    Convierte un objeto date al formato japonés estándar para certificados.

    Cada dígito del año se convierte individualmente. El mes y el día
    se construyen con la lógica japonesa estándar (十 para decenas).

    Args:
        fecha: Objeto date de Python con la fecha a convertir.

    Returns:
        Fecha en formato japonés (ej. '二〇二五年二月二十日').
    """
    # Año: cada dígito se convierte individualmente
    anio_jp = "".join(DIGITOS_JP[d] for d in str(fecha.year))

    # Mes: usa la tabla directa (ya incluye 十 correctamente)
    mes_jp = MESES_JP[fecha.month]

    # Día: construido con la misma lógica que los grados
    dia_jp = _construir_digito_japones(fecha.day) + "日"

    return f"{anio_jp}年{mes_jp}{dia_jp}"


def obtener_kanji_grado(numero: int, tipo: str, organizacion: str) -> str:
    """
    Construye el kanji completo de un grado leyendo la configuración
    de la organización desde grados.json.

    Verifica primero si existe un kanji_especial para ese número y tipo.
    Si no existe, construye el kanji combinando el dígito japonés con
    el sufijo del tipo.

    Args:
        numero: Número del grado (ej. 1, 2, 3).
        tipo: Tipo de grado (ej. 'dan', 'kyu', 'shodan').
        organizacion: Código de la organización (ej. 'ocoa').

    Returns:
        Kanji completo del grado (ej. '初段', '二段', '三級').

    Raises:
        ValueError: Si el número está fuera del rango soportado (1–99).
        ValueError: Si el tipo no existe en la configuración.
        FileNotFoundError: Si grados.json no existe.
    """
    if not (1 <= numero <= 99):
        raise ValueError(
            f"Número de grado fuera de rango: {numero}. Debe estar entre 1 y 99."
        )

    tipos_grado = _cargar_tipos_grado()
    config_tipo = tipos_grado.get(tipo)

    if config_tipo is None:
        raise ValueError(
            f"El tipo de grado '{tipo}' no existe en el catálogo global.\n"
            f"Verifica data/tipos_grado.json."
        )

    # Verificar kanji especial antes de construir
    kanji_especial = config_tipo.get("kanji_especial", {}).get(str(numero))
    if kanji_especial:
        return kanji_especial

    return _construir_digito_japones(numero) + config_tipo["kanji_sufijo"]

if __name__ == "__main__":

    print(obtener_kanji_grado(1, "dan", "ocoa"))   # → 初段
    print(obtener_kanji_grado(2, "dan", "ocoa"))   # → 二段
    print(obtener_kanji_grado(1, "kyu", "ocoa"))   # → 一級
    print(obtener_kanji_grado(10, "dan", "ocoa"))  # → 十段
    print(obtener_kanji_grado(13, "kyu", "ocoa"))  # → 十三級

    print("-"*50)


    print(formatear_grado_espanol(1, "kyu", "ocoa", "puerto_ordaz"))  # → Cinturón Negro 1° Dan.
    print(formatear_grado_espanol(1, "shodan", "ocoa", "puerto_ordaz"))  # → Cinturón Verde 5° Kyu.
    print(obtener_kanji_grado(1, "dan", "ocoa"))                      # → 初段
    print(obtener_kanji_grado(3, "kyu", "ocoa"))                      # → 三級


    print("-"*50)


    print(fecha_a_japones(date(2025, 2, 20)))   # → 二〇二五年二月二十日
    print(fecha_a_japones(date(2010, 12, 31)))  # → 二〇一〇年十二月三十一日
    print(fecha_a_japones(date(2025, 1, 1)))    # → 二〇二五年一月一日


    print("-"*50)

    # Sin consumir tokens
    print(nombre_a_katakana("Juan Pérez", modo_prueba=True))

    # Con API real
    # print(nombre_a_katakana("Juan Pérez"))

    print("-"*50)

    orden = {
        "id_orden":     "ORD-2025-001",
        "organizacion": "ocoa",
        "dojo":         "puerto_ordaz",
        "ciudad":       "Caracas",
        "fecha":        date(2025, 2, 20),
    }

    alumnos = [
        {
            "nombre_alumno":  "Juan Pérez",
            "cedula":         "25446976",
            "prefijo_cedula": "V",
            "grado":          "1",
            "tipo":           "dan",
            "notas":          "",
        }
    ]

    resultado = procesar_orden(orden, alumnos, registro_inicio=138, modo_prueba=True)
    print(resultado)
    
    
    