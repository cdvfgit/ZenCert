
from core.registro import leer_ultimo, reservar_rango, confirmar

print(leer_ultimo("ocoa"))           # → 0
init, end = reservar_rango("ocoa", 5)    # → (1, 5)
print(f"rango: {init,end}")
confirmar("ocoa", end)
print(leer_ultimo("ocoa"))           # → 5


# TEST CON SHEETS

print("-"*50)

from core.lector_sheets import conectar, leer_ordenes

sheet = conectar()
print(sheet.title)
ordenes = leer_ordenes()
print(ordenes)