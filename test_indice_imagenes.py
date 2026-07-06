import os

CARPETA = "imagenes"
# Ya no se contempla ".svg": las 49 imagenes de cartas ahora son PNG
# reales (ver interfaz/imagenes.py para el detalle de la solucion al
# bug de carga de imagenes).
EXTENSIONES = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


def normalizar_nombre(archivo):
    base = archivo.lower()
    cambiado = True
    while cambiado:
        cambiado = False
        for ext in EXTENSIONES:
            if base.endswith(ext):
                base = base[: -len(ext)]
                cambiado = True
    return base


def construir_indice(carpeta=CARPETA):
    indice = {}
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta):
            indice[normalizar_nombre(archivo)] = archivo
    return indice


indice = construir_indice()
print(f"Archivos indexados: {len(indice)}")

PALOS = ("oro", "copa", "espada", "basto")
faltantes = []
for palo in PALOS:
    for valor in range(1, 13):
        clave = f"{valor}_{palo}"
        if clave not in indice:
            faltantes.append(clave)
        else:
            assert indice[clave].lower().startswith(clave)

print("dorso ->", indice.get("dorso"))
print("comodin ->", indice.get("comodin", "(no existe, se usará el texto de reemplazo)"))
print("Cartas numéricas faltantes en el índice:", faltantes if faltantes else "ninguna")

assert not faltantes, "Deberían estar las 48 cartas numéricas (4 palos x 12 valores)."
assert indice.get("dorso") is not None, "Debería existir el dorso."
print("\nÍndice de imágenes: OK")
