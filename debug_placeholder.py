#!/usr/bin/env python3
"""
Script para diagnosticar qué placeholder está recibiendo datos incorrectos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from lector_sheets import leer_ordenes, Estado
from procesador import procesar_orden

def main():
    print("🔍 DIAGNÓSTICO DE PLACEHOLDERS")
    print("=" * 50)
    
    # Obtener una orden APROBADA para probar
    ordenes = leer_ordenes(Estado.APROBADA)
    
    if not ordenes:
        print("❌ No hay órdenes APROBADAS")
        return
    
    orden = ordenes[0]  # Usar la primera orden aprobada
    print(f"📋 Orden seleccionada: {orden['id_orden']}")
    print(f"📅 Fecha en orden: {orden['fecha']}")
    print(f"📍 Ciudad en orden: {orden['ciudad']}")
    
    # Leer alumnos
    from lector_sheets import leer_alumnos
    alumnos = leer_alumnos(orden['id_orden'])
    
    print(f"👥 Total alumnos: {len(alumnos)}")
    
    # Procesar la orden
    try:
        resultado = procesar_orden(orden, alumnos, registro_inicio=1, modo_prueba=True)
        
        print("\n📊 Datos procesados para el primer alumno:")
        for tipo, lista in resultado.items():
            if lista:
                alumno = lista[0]  # Primer alumno
                print(f"  🎯 Tipo: {tipo}")
                for key, value in alumno.items():
                    print(f"    {key}: {value}")
                break  # Solo mostrar el primer tipo
                
    except Exception as e:
        print(f"❌ Error procesando: {e}")

if __name__ == "__main__":
    main()
