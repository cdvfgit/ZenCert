#!/usr/bin/env python3
"""
Diagnóstico del sistema de credenciales de Google Sheets
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("🔍 DIAGNÓSTICO DE CREDENCIALES GOOGLE SHEETS")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # 1. Verificar archivo de credenciales
    ruta_cred = Path(__file__).parent / "credenciales.json"
    print(f"📁 Archivo credenciales.json: {ruta_cred}")
    print(f"📁 Existe: {ruta_cred.exists()}")
    
    if ruta_cred.exists():
        try:
            with open(ruta_cred, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
            print(f"✅ Formato JSON válido")
            print(f"📧 Tipo de cuenta: {cred_data.get('type', 'service_account')}")
            print(f"📧 Project ID: {cred_data.get('project_id', 'No encontrado')}")
            print(f"📧 Client Email: {cred_data.get('client_email', 'No encontrado')}")
        except json.JSONDecodeError as e:
            print(f"❌ Error en JSON: {e}")
    
    # 2. Verificar variable de entorno
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    print(f"\n🌐 Variable GOOGLE_SHEET_ID: {'✅ Configurada' if sheet_id else '❌ No configurada'}")
    if sheet_id:
        print(f"📝 Sheet ID: {sheet_id}")
    
    # 3. Verificar archivo .env
    ruta_env = Path(__file__).parent / ".env"
    print(f"\n📄 Archivo .env: {ruta_env}")
    print(f"📄 Existe: {ruta_env.exists()}")
    
    if ruta_env.exists():
        print("📝 Contenido del .env:")
        with open(ruta_env, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip() and not line.startswith('#'):
                    print(f"  {line_num}: {line.strip()}")
    
    # 4. Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE CONFIGURACIÓN:")
    
    if ruta_cred.exists() and sheet_id:
        print("✅ Configuración completa - debería funcionar")
        print("🔗 Método: Service Account + Sheet ID")
    elif not ruta_cred.exists():
        print("❌ Falta credenciales.json")
    elif not sheet_id:
        print("❌ Falta GOOGLE_SHEET_ID en .env")
    else:
        print("❌ Faltan ambos componentes")

if __name__ == "__main__":
    main()
