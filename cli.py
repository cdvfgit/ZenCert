"""
cli.py
------
Interfaz de consola del operador.
Usa Rich para menú visual, selección de órdenes, confirmación y rollback.
"""

"""
cli.py
------
Interfaz de consola del operador para el sistema de certificados.

Conecta todos los módulos del sistema en un flujo guiado:
lector_sheets → procesador → generador → registro

Uso:
    python cli.py
"""

import os
from pickle import TRUE
import sys
import traceback
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box

from core.generador import detectar_plantilla, generar_lote
from core.lector_sheets import Estado, actualizar_estado, leer_alumnos, leer_ordenes
from core.procesador import procesar_orden
from core.registro import confirmar, reservar_rango

console = Console()

# ── Paleta visual ─────────────────────────────────────────────────────────────

_VERDE   = "bold green"
_ROJO    = "bold red"
_AMARILLO = "bold yellow"
_CYAN    = "bold cyan"
_BLANCO  = "bold white"
_DIM     = "dim"


# ── Helpers de visualización ──────────────────────────────────────────────────

def _limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def _encabezado():
    console.print(Panel(
        Text("SISTEMA DE CERTIFICADOS DE KARATE DO", justify="center", style=_CYAN),
        subtitle="[dim]Sanchin Cretificate System[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()


def _separador():
    console.print("─" * 60, style=_DIM)


def _ok(msg: str):
    console.print(f"  [bold green]✓[/bold green]  {msg}")


def _error(msg: str):
    console.print(f"  [bold red]✗[/bold red]  {msg}")


def _info(msg: str):
    console.print(f"  [bold cyan]→[/bold cyan]  {msg}")


def _warn(msg: str):
    console.print(f"  [bold yellow]⚠[/bold yellow]  {msg}")


def _tabla_ordenes(ordenes: list[dict]) -> Table:
    tabla = Table(
        box=box.SIMPLE_HEAD,
        border_style="dim",
        header_style=_CYAN,
        show_lines=False,
        padding=(0, 1),
    )
    tabla.add_column("#",            style="dim",        width=4,  justify="right")
    tabla.add_column("ID Orden",     style=_BLANCO,      width=16)
    tabla.add_column("Instructor",   style="white",      width=20)
    tabla.add_column("Org",          style="cyan",       width=8)
    tabla.add_column("Dojo",         style="white",      width=16)
    tabla.add_column("Alumnos",      style="yellow",     width=8,  justify="right")
    tabla.add_column("Fecha",        style=_DIM,         width=12)

    for i, o in enumerate(ordenes, 1):
        tabla.add_row(
            str(i),
            o["id_orden"],
            o["instructor"],
            o["organizacion"],
            o["dojo"],
            o["total_alumnos"],
            o["timestamp"][:10],
        )
    return tabla


def _panel_orden(orden: dict, numero: int, total: int) -> Panel:
    contenido = (
        f"[dim]Instructor :[/dim]  {orden['instructor']}\n"
        f"[dim]Organización:[/dim] {orden['organizacion'].upper()}\n"
        f"[dim]Dojo        :[/dim] {orden['dojo'].replace('_', ' ').title()}\n"
        f"[dim]Alumnos     :[/dim] {orden['total_alumnos']}\n"
        f"[dim]Enviada     :[/dim] {orden['timestamp']}"
    )
    return Panel(
        contenido,
        title=f"[bold cyan]Orden {numero}/{total} — {orden['id_orden']}[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 2),
    )


def _resumen_final(resultados: list[dict]):
    _separador()
    console.print("\n  [bold cyan]RESUMEN DE LA SESIÓN[/bold cyan]\n")

    tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    tabla.add_column(width=20)
    tabla.add_column(width=30)
    tabla.add_column(width=12)

    for r in resultados:
        if r["estado"] == "confirmada":
            icono = "[bold green]✓[/bold green]"
            estado_txt = f"[green]Confirmada[/green] ({r['certificados']} certificados)"
        elif r["estado"] == "rechazada":
            icono = "[bold red]✗[/bold red]"
            estado_txt = "[red]Rechazada — rollback ejecutado[/red]"
        elif r["estado"] == "error":
            icono = "[bold red]✗[/bold red]"
            estado_txt = f"[red]Error — {r.get('detalle', '')}[/red]"
        else:
            icono = "[bold yellow]–[/bold yellow]"
            estado_txt = "[yellow]Omitida — vuelve a APROBADA[/yellow]"

        tabla.add_row(icono, r["id_orden"], estado_txt)

    console.print(tabla)
    console.print()


# ── Lógica de rollback ────────────────────────────────────────────────────────

def _rollback(id_orden: str, rutas_pptx: list[str]):
    """Elimina los PPTX generados y restaura el estado a APROBADA."""
    for ruta in rutas_pptx:
        try:
            Path(ruta).unlink(missing_ok=True)
        except Exception:
            pass
    try:
        actualizar_estado(id_orden, Estado.APROBADA)
        _ok(f"Rollback ejecutado — {id_orden} vuelve a APROBADA")
    except Exception as e:
        _error(f"No se pudo restaurar el estado en Sheets: {e}")


# ── Flujo de procesamiento de una orden ──────────────────────────────────────

def _procesar_orden(orden: dict, numero: int, total: int) -> dict:
    """
    Ejecuta el pipeline completo para una orden.

    Returns:
        Dict con id_orden, estado (confirmada/rechazada/error/omitida),
        certificados generados y detalle de error si aplica.
    """
    resultado = {
        "id_orden":     orden["id_orden"],
        "estado":       "omitida",
        "certificados": 0,
        "detalle":      "",
    }

    console.print(_panel_orden(orden, numero, total))
    console.print()

    rutas_generadas: list[str] = []

    try:
        # ── 1. Cambiar estado a PROCESANDO ────────────────────────────────
        actualizar_estado(orden["id_orden"], Estado.PROCESANDO)

        # ── 2. Leer alumnos ───────────────────────────────────────────────
        _info("Leyendo datos de alumnos...")
        alumnos = leer_alumnos(orden["id_orden"])
        _ok(f"{len(alumnos)} alumno(s) cargados")

        # ── 3. Reservar rango de registros ────────────────────────────────
        inicio, fin = reservar_rango(orden["organizacion"], len(alumnos))
        _info(f"Registros reservados: {inicio} → {fin}")

        # ── 4. Procesar datos ─────────────────────────────────────────────
        _info("Procesando datos...")
        
        # Convertir timestamp a fecha para procesar_orden
        fecha_obj = datetime.strptime(orden["timestamp"], "%Y-%m-%d %H:%M").date()
        
        # Crear copia de orden con el campo fecha agregado
        orden_procesable = orden.copy()
        orden_procesable["fecha"] = fecha_obj
        
        grupos = procesar_orden(
            orden=orden_procesable,
            alumnos=alumnos,
            registro_inicio=inicio,
            modo_prueba=True,
        )
        tipos = list(grupos.keys())
        _ok(f"Grupos procesados: {', '.join(tipos)}")

        # ── 5. Generar PPTX por grupo ─────────────────────────────────────
        _info("Generando certificados...")
        total_certificados = 0

        for tipo, alumnos_grupo in grupos.items():
            ruta_plantilla = detectar_plantilla(
                orden["organizacion"],
                tipo,
                orden["dojo"],
            )
            ruta_pptx = generar_lote(
                lista_alumnos=alumnos_grupo,
                ruta_plantilla=ruta_plantilla,
                id_orden=orden["id_orden"],
                organizacion=orden["organizacion"],
                nombre_salida=f"certificados_{tipo}.pptx",
            )
            rutas_generadas.append(ruta_pptx)
            total_certificados += len(alumnos_grupo)
            _ok(f"certificados_{tipo}.pptx → {Path(ruta_pptx).parent}")

        resultado["certificados"] = total_certificados

    except Exception as e:
        _error(f"Error durante la generación: {e}")
        console.print(f"  [dim]{traceback.format_exc()}[/dim]")
        _rollback(orden["id_orden"], rutas_generadas)
        resultado["estado"]  = "error"
        resultado["detalle"] = str(e)
        console.print()
        Prompt.ask("  Presiona Enter para continuar con la siguiente orden")
        return resultado

    # ── 6. Intervención manual del operador ───────────────────────────────
    console.print()
    _separador()
    console.print(
        "\n  [bold yellow]Revisa los archivos generados antes de confirmar.[/bold yellow]\n"
    )

    for ruta in rutas_generadas:
        console.print(f"  [dim]📄 {ruta}[/dim]")

    console.print()
    console.print("  [bold]¿Qué deseas hacer?[/bold]")
    console.print("  [green][C][/green] Confirmar")
    console.print("  [red][R][/red] Rechazar y ejecutar rollback")
    console.print("  [yellow][S][/yellow] Salir sin confirmar (vuelve a APROBADA)")
    console.print()

    while True:
        accion = Prompt.ask(
            "  Acción",
            choices=["c", "r", "s", "C", "R", "S"],
            show_choices=False,
        ).lower()

        if accion == "c":
            # ── Confirmar ─────────────────────────────────────────────────
            try:
                confirmar(orden["organizacion"], fin)
                actualizar_estado(orden["id_orden"], Estado.COMPLETADA)
                _ok(f"Orden {orden['id_orden']} COMPLETADA — registros actualizados")
                resultado["estado"] = "confirmada"
            except Exception as e:
                _error(f"Error al confirmar: {e}")
                resultado["estado"]  = "error"
                resultado["detalle"] = str(e)
            break

        elif accion == "r":
            # ── Rechazar y rollback ───────────────────────────────────────
            _rollback(orden["id_orden"], rutas_generadas)
            resultado["estado"] = "rechazada"
            break

        elif accion == "s":
            # ── Salir sin confirmar ───────────────────────────────────────
            _rollback(orden["id_orden"], rutas_generadas)
            resultado["estado"] = "omitida"
            _warn(f"Orden {orden['id_orden']} devuelta a APROBADA sin cambios")
            break

    console.print()
    return resultado


# ── Flujo principal ───────────────────────────────────────────────────────────

def _flujo_procesar():
    """Flujo completo de selección y procesamiento de órdenes."""
    _limpiar()
    _encabezado()

    # ── Leer órdenes aprobadas ────────────────────────────────────────────
    _info("Consultando órdenes aprobadas...")
    try:
        ordenes = leer_ordenes(Estado.APROBADA)
    except Exception as e:
        _error(f"No se pudo conectar con Google Sheets: {e}")
        Prompt.ask("\n  Presiona Enter para volver al menú")
        return

    if not ordenes:
        _warn("No hay órdenes aprobadas pendientes de procesar.")
        Prompt.ask("\n  Presiona Enter para volver al menú")
        return

    console.print(f"\n  [bold cyan]ÓRDENES APROBADAS[/bold cyan] — {len(ordenes)} disponibles\n")
    console.print(_tabla_ordenes(ordenes))
    console.print()

    # ── Selección de órdenes ──────────────────────────────────────────────
    console.print(
        "  Ingresa los números a procesar separados por espacio.\n"
        "  [dim]Ejemplo: 1 3  |  todas  |  salir[/dim]\n"
    )

    while True:
        entrada = Prompt.ask("  Selección").strip().lower()

        if entrada == "salir":
            return

        if entrada == "todas":
            seleccion = list(range(len(ordenes)))
            break

        try:
            indices = [int(x) - 1 for x in entrada.split()]
            if all(0 <= i < len(ordenes) for i in indices) and indices:
                seleccion = indices
                break
            _warn("Números fuera de rango. Intenta de nuevo.")
        except ValueError:
            _warn("Entrada inválida. Usa números, 'todas' o 'salir'.")

    ordenes_seleccionadas = [ordenes[i] for i in seleccion]
    total = len(ordenes_seleccionadas)

    console.print(f"\n  [bold cyan]PROCESANDO COLA:[/bold cyan] {total} orden(es) seleccionada(s)\n")
    _separador()

    # ── Procesar cola ─────────────────────────────────────────────────────
    resultados = []
    for numero, orden in enumerate(ordenes_seleccionadas, 1):
        console.print()
        resultado = _procesar_orden(orden, numero, total)
        resultados.append(resultado)
        _separador()

    # ── Resumen final ─────────────────────────────────────────────────────
    _resumen_final(resultados)
    Prompt.ask("  Presiona Enter para volver al menú")


# ── Menú principal ────────────────────────────────────────────────────────────

def _menu_principal():
    while True:
        _limpiar()
        _encabezado()

        console.print("  [bold cyan]MENÚ PRINCIPAL[/bold cyan]\n")
        console.print("  [bold][1][/bold]  Procesar órdenes aprobadas")
        console.print("  [bold][2][/bold]  Salir")
        console.print()

        opcion = Prompt.ask(
            "  Opción",
            choices=["1", "2"],
            show_choices=False,
        )

        if opcion == "1":
            _flujo_procesar()
        elif opcion == "2":
            _limpiar()
            console.print("\n  [dim]Hasta pronto.[/dim]\n")
            sys.exit(0)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        _menu_principal()
    except KeyboardInterrupt:
        console.print("\n\n  [dim]Sesión interrumpida.[/dim]\n")
        sys.exit(0)