import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
from juegos import Truco, Chinchon, GameManager
from estructuras import ListaEnlazada, Pila
from cartas import MazoEspanol, MazoTruco, MazoChinchon

random.seed(1)

print("=== Test estructuras ===")
lista = ListaEnlazada()
lista.insertar_final(1)
lista.insertar_final(2)
lista.insertar_inicio(0)
assert list(lista) == [0, 1, 2]
assert len(lista) == 3
assert lista.buscar(2) is True
lista.eliminar(1)
assert list(lista) == [0, 2]
print("ListaEnlazada OK:", lista)

pila = Pila()
pila.push("a"); pila.push("b"); pila.push("c")
assert pila.peek() == "c"
assert pila.pop() == "c"
assert len(pila) == 2
print("Pila OK:", pila)

print("\n=== Test mazos ===")
me = MazoEspanol()
assert me.cantidad_restante() == 50, me.cantidad_restante()
mt = MazoTruco()
assert mt.cantidad_restante() == 40, mt.cantidad_restante()
mc = MazoChinchon()
assert mc.cantidad_restante() == 48, mc.cantidad_restante()
print("Mazos OK: MazoEspanol=50, MazoTruco=40, MazoChinchon=48")

def _jugar_negociacion(truco, pasos_max=30):
    """Juega al azar, pero siempre con una jugada LEGAL según
    opciones_disponibles(), toda la negociación de envido y truco hasta
    que la mano llegue a la fase 'rondas' o termine antes ('fin_mano')."""
    pasos = 0
    while truco.fase in ("envido", "truco") and pasos < pasos_max:
        pasos += 1
        info = truco.opciones_disponibles()
        opcion = random.choice(info["opciones"])
        if info["contexto"] == "envido":
            if info["modo"] == "cantar":
                truco.cantar_envido(opcion)
            else:
                truco.responder_envido(opcion)
        else:  # contexto == "truco"
            if info["modo"] == "cantar":
                truco.cantar_truco(opcion)
            else:
                truco.responder_truco(opcion)


print("\n=== Simulación Truco ===")
gm = GameManager()
truco = gm.crear_juego("Truco", "Tester")
manos = 0
while not truco.terminado and manos < 200:
    truco.iniciar_mano()
    manos += 1
    _jugar_negociacion(truco)
    while truco.fase == "rondas" and truco.cartas_j1:
        r = truco.jugar_carta(0)
        if r.get("mano_terminada"):
            break
print(f"Truco: {manos} manos jugadas. Resultado final: {truco.puntos}, terminado={truco.terminado}")
assert truco.terminado

print("\n=== Simulación Chinchón ===")
chin = gm.crear_juego("Chinchón", "Tester")
rondas = 0
while not chin.terminado and rondas < 300:
    chin.iniciar_mano()
    rondas += 1
    turnos = 0
    while chin.fase != "fin_mano" and turnos < 60:
        turnos += 1
        if random.random() < 0.5 and chin.mazo.cantidad_restante() > 0:
            res = chin.robar_del_mazo()
        else:
            res = chin.robar_del_pozo()
            if "error" in res:
                res = chin.robar_del_mazo()
        if "error" in res:
            break
        cierre = chin.cerrar_mano()
        if "cerrador" in cierre:
            break
        idx = random.randrange(len(chin.mano_j1))
        res = chin.descartar(idx)
        if res.get("fin_mano") or chin.fase == "fin_mano":
            break
        if chin.mazo.esta_vacio() and chin.pozo.is_empty():
            break
print(f"Chinchón: {rondas} rondas jugadas. Resultado final: {chin.puntos}, terminado={chin.terminado}")

print("\nTodos los tests ejecutados sin excepciones.")
