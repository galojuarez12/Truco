import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cartas import Carta, MazoChinchon
from juegos import Chinchon


def C(v, p):
    return Carta(v, p)


# --- Caso 1: cierre con bono de Chinchón (escalera de 7 + 1 carta cualquiera) ---
chin = Chinchon("Ana")
chin.mazo = MazoChinchon()
chin.mano_j1 = [C(1, "oro"), C(2, "oro"), C(3, "oro"), C(4, "oro"), C(5, "oro"),
                C(6, "oro"), C(7, "oro"), C(2, "copa")]  # 8 cartas (ya "robó")
chin.mano_j2 = [C(4, "basto"), C(6, "copa"), C(11, "espada"), C(1, "basto"),
                C(3, "copa"), C(10, "basto"), C(12, "oro")]
chin.fase = "esperando_descarte"

r = chin.cerrar_mano()
assert "error" not in r, r
assert r["chinchon"] is True, r
assert r["puntos_mano_j1"] == 0
print("Caso 1 (Chinchón real) OK ->", r["mensajes"], "| puntos:", r["puntos_totales"])

# --- Caso 2: cierre normal (0 sueltas pero en 2 combinaciones, sin bono) ---
chin2 = Chinchon("Ana")
chin2.mazo = MazoChinchon()
chin2.mano_j1 = [C(1, "oro"), C(2, "oro"), C(3, "oro"), C(4, "oro"),
                 C(5, "copa"), C(5, "espada"), C(5, "basto"), C(9 % 8, "copa")]
# la última carta (índice 7) es la que se descarta al cerrar
chin2.mano_j1[7] = C(1, "copa")
chin2.mano_j2 = [C(4, "basto"), C(6, "copa"), C(11, "espada"), C(1, "basto"),
                 C(3, "copa"), C(10, "basto"), C(12, "oro")]
chin2.fase = "esperando_descarte"

r2 = chin2.cerrar_mano()
assert "error" not in r2, r2
assert r2["chinchon"] is False, r2
assert r2["puntos_mano_j1"] == 0
print("Caso 2 (cierre normal, sin bono) OK ->", r2["mensajes"], "| puntos:", r2["puntos_totales"])

# --- Caso 3: cierre "cortando" con 1 carta suelta ---
chin3 = Chinchon("Ana")
chin3.mazo = MazoChinchon()
chin3.mano_j1 = [C(1, "oro"), C(2, "oro"), C(3, "oro"), C(5, "copa"), C(5, "espada"),
                 C(5, "basto"), C(12, "basto"), C(6, "copa")]
chin3.mano_j2 = [C(4, "basto"), C(6, "espada"), C(11, "espada"), C(1, "basto"),
                 C(3, "copa"), C(10, "basto"), C(12, "oro")]
chin3.fase = "esperando_descarte"

r3 = chin3.cerrar_mano()
assert "error" not in r3, r3
assert r3["chinchon"] is False
assert r3["puntos_mano_j1"] > 0
print("Caso 3 (cierre cortando, con 1 suelta) OK -> puntos_mano_j1:", r3["puntos_mano_j1"])

# --- Caso 4: no se puede cerrar (demasiadas cartas sueltas) ---
chin4 = Chinchon("Ana")
chin4.mazo = MazoChinchon()
chin4.mano_j1 = [C(1, "oro"), C(4, "copa"), C(7, "espada"), C(10, "basto"),
                 C(2, "basto"), C(11, "oro"), C(6, "espada"), C(12, "copa")]
chin4.mano_j2 = [C(4, "basto"), C(6, "espada"), C(11, "espada"), C(1, "basto"),
                 C(3, "copa"), C(10, "basto"), C(12, "oro")]
chin4.fase = "esperando_descarte"
r4 = chin4.cerrar_mano()
assert "error" in r4, r4
print("Caso 4 (no puede cerrar) OK ->", r4["error"])

print("\nTodas las pruebas de cierre pasaron correctamente.")
