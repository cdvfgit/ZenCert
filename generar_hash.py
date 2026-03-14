#!/usr/bin/env python3
"""
Script para generar hashes SHA256 para usuarios.json
"""

import hashlib
import json
from pathlib import Path

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("🔐 GENERADOR DE HASHES PARA USUARIOS")
    print("=" * 50)
    
    # Usuarios y passwords sugeridos
    usuarios_sugeridos = {
        "ope": "admin123",           # Operador
        "ocoa": "ocoa123",          # Instructor OCOA  
        "cesar": "cesar123",        # Instructor Cesar
    }
    
    print("Hashes generados:")
    print("-" * 30)
    
    usuarios_json = {"usuarios": []}
    
    for usuario, password in usuarios_sugeridos.items():
        hash_password = _hash(password)
        rol = "operador" if usuario == "ope" else "instructor"
        
        print(f"{usuario}: {password} → {hash_password}")
        
        usuarios_json["usuarios"].append({
            "usuario": usuario,
            "password_hash": hash_password,
            "rol": rol,
            "nombre": usuario.upper() if usuario != "cesar" else "Sensei Cesar",
            "organizacion": "ocoa" if usuario != "ope" else "",
            "dojo": "puerto_ordaz" if usuario != "ope" else ""
        })
    
    print("\n" + "=" * 50)
    print("📄 JSON generado para data/usuarios.json:")
    print(json.dumps(usuarios_json, indent=2, ensure_ascii=False))
    
    # Guardar en archivo
    ruta = Path(__file__).parent / "data" / "usuarios.json"
    ruta.write_text(json.dumps(usuarios_json, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Guardado en: {ruta}")

if __name__ == "__main__":
    main()
