import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cartas import Carta
from juegos import Chinchon

c = Chinchon("Tester")

def C(v, p):
    return Carta(v, p)

# Trío válido (tres cartas de igual valor, distinto palo)
trio = [C(5, "oro"), C(5, "copa"), C(5, "espada")]
assert c._es_combinacion_valida(trio) is True

# Cuadra de 4 válida
cuadra = [C(7, "oro"), C(7, "copa"), C(7, "espada"), C(7, "basto")]
assert c._es_combinacion_valida(cuadra) is True

# 5 cartas del mismo valor no es válido (no existen 5 palos)
invalido_5 = cuadra + [C(7, "oro")]
assert c._es_combinacion_valida(invalido_5) is False

# Escalera válida de 3 consecutivas mismo palo
escalera = [C(3, "oro"), C(4, "oro"), C(5, "oro")]
assert c._es_combinacion_valida(escalera) is True

# Escalera con hueco cubierto por un comodín
escalera_con_hueco = [C(3, "oro"), C(5, "oro"), Carta(0, "comodin")]
assert c._es_combinacion_valida(escalera_con_hueco) is True

# Escalera con hueco de 2 sin suficientes comodines -> inválida
escalera_hueco_grande = [C(3, "oro"), C(6, "oro"), Carta(0, "comodin")]
assert c._es_combinacion_valida(escalera_hueco_grande) is False

# Cartas sueltas de distinto palo y valor -> inválida
suelto = [C(2, "oro"), C(5, "copa"), C(9, "basto")]
assert c._es_combinacion_valida(suelto) is False

print("_es_combinacion_valida: OK")

# --- mejor_descomposicion ---
mano = [C(3, "oro"), C(4, "oro"), C(5, "oro"), C(7, "copa"), C(7, "espada"), C(7, "basto"), C(1, "copa")]
grupos, sueltas = c._mejor_descomposicion(mano)
assert len(sueltas) == 1 and sueltas[0] == C(1, "copa"), (grupos, sueltas)
print("_mejor_descomposicion (7 cartas, 1 suelta): OK ->", [len(g) for g in grupos], sueltas[0])

# Mano que arma UNA sola escalera de 7 (chinchón real)
mano_chinchon = [C(1, "oro"), C(2, "oro"), C(3, "oro"), C(4, "oro"), C(5, "oro"), C(6, "oro"), C(7, "oro")]
grupos, sueltas = c._mejor_descomposicion(mano_chinchon)
assert len(sueltas) == 0 and len(grupos) == 1 and len(grupos[0]) == 7
print("Detección de Chinchón (escalera de 7): OK")

# Mano con 0 sueltas pero en DOS combinaciones (no debe contar como chinchón)
mano_dos_grupos = [C(1, "oro"), C(2, "oro"), C(3, "oro"), C(4, "oro"), C(5, "copa"), C(5, "espada"), C(5, "basto")]
grupos, sueltas = c._mejor_descomposicion(mano_dos_grupos)
assert len(sueltas) == 0 and len(grupos) == 2, (grupos, sueltas)
print("Mano de 7 en dos grupos (0 sueltas, NO es chinchón) -> tamaños:", [len(g) for g in grupos])

print("\nTodas las verificaciones de combinaciones pasaron correctamente.")
