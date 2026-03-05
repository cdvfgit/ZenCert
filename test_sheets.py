#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conexión con Google Sheets
y el contenido de las órdenes.
"""

import os
from pathlib import Path

# Agregar el directorio core al path
import sys
sys.path.insert(0, str(Path(__file__).parent / "core"))

from lector_sheets import leer_ordenes, Estado, conectar

def main():
    print("🔍 DIAGNÓSTICO DE GOOGLE SHEETS")
    print("=" * 50)
    
    # 1. Verificar configuración
    print("\n1. Verificando configuración...")
    try:
        from lector_sheets import _validar_configuracion
        _validar_configuracion()
        print("✅ Configuración válida")
        
        # Mostrar variables (sin valores sensibles)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        print(f"   📄 GOOGLE_SHEET_ID: {'✅ Configurado' if sheet_id else '❌ No configurado'}")
        
        cred_path = Path(__file__).parent / "credenciales.json"
        print(f"   🔐 credenciales.json: {'✅ Existe' if cred_path.exists() else '❌ No existe'}")
        
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        return
    
    # 2. Probar conexión
    print("\n2. Probando conexión...")
    try:
        spreadsheet = conectar()
        print(f"✅ Conexión exitosa")
        print(f"   📊 Spreadsheet: {spreadsheet.title}")
        
        # Listar hojas disponibles
        hojas = spreadsheet.worksheets()
        print(f"   📋 Hojas encontradas: {[hoja.title for hoja in hojas]}")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 3. Leer todas las órdenes
    print("\n3. Leyendo todas las órdenes...")
    try:
        todas_ordenes = leer_ordenes(estado=None)
        print(f"✅ Se encontraron {len(todas_ordenes)} órdenes totales")
        
        if todas_ordenes:
            print("\n   📋 Estados encontrados:")
            estados = {}
            for orden in todas_ordenes:
                estado = orden.get("estado", "SIN_ESTADO")
                estados[estado] = estados.get(estado, 0) + 1
            
            for estado, count in estados.items():
                print(f"      - {estado}: {count}")
        
    except Exception as e:
        print(f"❌ Error leyendo órdenes: {e}")
        return
    
    # 4. Filtrar por APROBADA
    print("\n4. Filtrando órdenes APROBADAS...")
    try:
        ordenes_aprobadas = leer_ordenes(estado=Estado.APROBADA)
        print(f"✅ Se encontraron {len(ordenes_aprobadas)} órdenes APROBADAS")
        
        if ordenes_aprobadas:
            print("\n   📋 Órdenes APROBADAS:")
            for i, orden in enumerate(ordenes_aprobadas, 1):
                print(f"      {i}. {orden['id_orden']} - {orden['instructor']} - {orden['estado']}")
        else:
            print("\n   ⚠️  No hay órdenes con estado 'APROBADA'")
            print("   📝 Estados disponibles en la clase Estado:")
            print(f"      - Estado.PENDIENTE = '{Estado.PENDIENTE}'")
            print(f"      - Estado.APROBADA = '{Estado.APROBADA}'")
            print(f"      - Estado.RECHAZADA = '{Estado.RECHAZADA}'")
            print(f"      - Estado.PROCESANDO = '{Estado.PROCESANDO}'")
            print(f"      - Estado.COMPLETADA = '{Estado.COMPLETADA}'")
            print(f"      - Estado.ERROR = '{Estado.ERROR}'")
        
    except Exception as e:
        print(f"❌ Error filtrando órdenes: {e}")
        return
    
    # 5. Mostrar ejemplo de orden
    if todas_ordenes:
        print("\n5. Ejemplo de primera orden:")
        primera = todas_ordenes[0]
        for key, value in primera.items():
            print(f"   {key}: '{value}'")
    
    # 6. Verificar estructura de columnas
    print("\n6. Verificando estructura de columnas...")
    try:
        spreadsheet = conectar()
        hoja_ordenes = spreadsheet.worksheet("ORDENES")
        
        # Obtener la primera fila (encabezados)
        encabezados = hoja_ordenes.row_values(1)
        print("   📋 Encabezados encontrados:")
        for i, encabezado in enumerate(encabezados):
            print(f"      Columna {i}: '{encabezado}'")
        
        # Obtener la primera fila de datos
        if len(todas_ordenes) > 0:
            primera_fila = hoja_ordenes.row_values(2)  # Fila 2 (primera fila de datos)
            print("\n   📊 Primera fila de datos:")
            for i, valor in enumerate(primera_fila):
                print(f"      Columna {i}: '{valor}'")
                
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")

if __name__ == "__main__":
    main()
