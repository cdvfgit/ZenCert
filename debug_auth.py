#!/usr/bin/env python3
"""
Script para diagnosticar problemas de autenticación
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.auth import _cargar_usuarios, autenticar, _hash

def main():
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN")
    print("=" * 50)
    
    # 1. Verificar archivo de usuarios
    ruta_usuarios = Path(__file__).parent / "data" / "usuarios.json"
    print(f"📁 Ruta usuarios.json: {ruta_usuarios}")
    print(f"📁 Existe: {ruta_usuarios.exists()}")
    
    if not ruta_usuarios.exists():
        print("❌ El archivo usuarios.json no existe")
        return
    
    # 2. Cargar usuarios
    try:
        usuarios = _cargar_usuarios()
        print(f"✅ Usuarios cargados: {len(usuarios)}")
        for u in usuarios:
            print(f"  - {u.get('usuario', '?')} ({u.get('rol', '?')})")
    except Exception as e:
        print(f"❌ Error cargando usuarios: {e}")
        return
    
    # 3. Probar hashing
    test_password = "admin123"
    hash_test = _hash(test_password)
    print(f"\n🔐 Hash de '{test_password}': {hash_test}")
    
    # 4. Probar autenticación
    if usuarios:
        test_user = usuarios[0]["usuario"]
        print(f"\n🧪 Probando autenticación con usuario: {test_user}")
        
        # Intentar con contraseña incorrecta
        resultado1 = autenticar(test_user, "password_incorrecto")
        print(f"  ❌ Contraseña incorrecta: {resultado1}")
        
        # Intentar con la contraseña del primer usuario (si podemos obtenerla)
        # Como solo tenemos el hash, probamos con un password común
        for test_pass in ["admin123", "password", "123456", test_user]:
            resultado2 = autenticar(test_user, test_pass)
            if resultado2:
                print(f"  ✅ Autenticación exitosa con '{test_pass}'")
                print(f"  📋 Usuario: {resultado2}")
                break
        else:
            print(f"  ❌ No se encontró contraseña válida para {test_user}")
            print("  💡 Verifica que las contraseñas en usuarios.json estén hasheadas correctamente")

if __name__ == "__main__":
    main()
