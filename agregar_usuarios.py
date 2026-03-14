# agregar_usuario.py
import hashlib, json
from pathlib import Path

def agregar_usuario(usuario, password, rol, organizacion, dojo, nombre):
    ruta = Path("data/usuarios.json")
    data = json.loads(ruta.read_text(encoding="utf-8"))
    
    nuevo = {
        "usuario":       usuario,
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "rol":           rol,
        "organizacion":  organizacion,
        "dojo":          dojo,
        "nombre":        nombre
    }
    
    data["usuarios"].append(nuevo)
    ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Usuario '{usuario}' agregado correctamente.")

# ── Modifica estos valores y ejecuta ──
agregar_usuario(
    usuario      = "aaa",
    password     = "bbb",
    rol          = "instructor",
    organizacion = "ogkv",
    dojo         = "velasquezkai",
    nombre       = "Cesar"
)