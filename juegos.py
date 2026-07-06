"""
Trabajo Práctico – Programación 3
Parte 3 – Sistema de juegos de cartas (JuegoDeCartas, Truco, Chinchón)
Parte 4 – Game Manager

Estas clases NO usan input()/print(): cada acción del jugador humano se
dispara desde la interfaz gráfica (ver gui.py) llamando a un método, que
devuelve un diccionario con la información necesaria para actualizar la
pantalla. Así el mismo motor de juego podría reutilizarse con cualquier
otra interfaz (consola, web, etc.).
"""

import random
import itertools

from cartas import MazoTruco, MazoChinchon
from estructuras import Pila


class JuegoDeCartas:
    """
    Clase base que representa un juego de cartas en general.

    Invariante: self.puntos es un diccionario con exactamente dos claves
    (los nombres de los jugadores) y valores enteros >= 0.
    """

    def __init__(self, nombre_j1, nombre_j2="CPU"):
        # PRE: nombre_j1 y nombre_j2 son strings no vacíos y distintos entre sí.
        # POST: se inicializan los puntajes en 0 y no hay mazo creado todavía.
        self.j1 = nombre_j1
        self.j2 = nombre_j2
        self.puntos = {self.j1: 0, self.j2: 0}
        self.mazo = None
        self.terminado = False

    def __str__(self):
        return (f"{self.__class__.__name__}: {self.j1} {self.puntos[self.j1]} "
                f"- {self.puntos[self.j2]} {self.j2}")

    def reiniciar(self):
        """PRE: ninguna. POST: puntajes en 0 y terminado en False."""
        self.puntos = {self.j1: 0, self.j2: 0}
        self.terminado = False


# =============================================================================
# TRUCO
# =============================================================================

class Truco(JuegoDeCartas):
    """
    Truco argentino sin Flor, un jugador humano contra la CPU, con
    negociación completa de apuestas:

    - Envido: Envido -> Envido Envido -> Real Envido -> Falta Envido.
    - Truco: Truco -> Retruco -> Vale Cuatro.
    - En cualquiera de las dos cadenas, quien recibe un canto puede
      responder Quiero, No Quiero, o subir la apuesta (si hay un escalón
      siguiente disponible).
    - Durante la fase de juego de cartas, el jugador humano puede
      abandonar la mano con "Irse al Mazo".

    Simplificación de diseño (documentada a propósito): la negociación del
    Truco ocurre en UNA sola fase, antes de jugar la primera carta —igual
    que ya hacía la versión anterior—, en lugar de permitir cantar Truco
    después de cada ronda como en el reglamento 100% real. Esto mantiene
    acotada la máquina de estados sin perder la posibilidad de llegar a
    Vale Cuatro.

    Invariante: mientras self.fase == "rondas", len(self.cartas_j1) ==
    len(self.cartas_j2) == 3 - cantidad_de_rondas_jugadas.
    """

    PUNTOS_VICTORIA = 30

    # Jerarquía de cartas específica del Truco (no es una propiedad general
    # de la carta, por eso vive en esta clase y no en Carta).
    _ORDEN_TRUCO = {
        (1, "espada"): 14, (1, "basto"): 13, (7, "espada"): 12, (7, "oro"): 11,
        (3, "oro"): 10, (3, "copa"): 10, (3, "espada"): 10, (3, "basto"): 10,
        (2, "oro"): 9, (2, "copa"): 9, (2, "espada"): 9, (2, "basto"): 9,
        (1, "copa"): 8, (1, "oro"): 7,
        (12, "oro"): 6, (12, "copa"): 6, (12, "espada"): 6, (12, "basto"): 6,
        (11, "oro"): 5, (11, "copa"): 5, (11, "espada"): 5, (11, "basto"): 5,
        (10, "oro"): 4, (10, "copa"): 4, (10, "espada"): 4, (10, "basto"): 4,
        (7, "copa"): 3, (7, "basto"): 3,
        (6, "oro"): 2, (6, "copa"): 2, (6, "espada"): 2, (6, "basto"): 2,
        (5, "oro"): 1, (5, "copa"): 1, (5, "espada"): 1, (5, "basto"): 1,
        (4, "oro"): 0, (4, "copa"): 0, (4, "espada"): 0, (4, "basto"): 0,
    }

    # ---- cadenas de apuestas -------------------------------------------

    ENVIDO_INCREMENTOS = {"envido": 2, "envido_envido": 2, "real_envido": 3}
    ENVIDO_SIGUIENTES = {
        None: ["envido", "real_envido", "falta_envido"],
        "envido": ["envido_envido", "real_envido", "falta_envido"],
        "envido_envido": ["real_envido", "falta_envido"],
        "real_envido": ["falta_envido"],
        "falta_envido": [],
    }
    NOMBRES_ENVIDO = {
        "envido": "Envido", "envido_envido": "Envido Envido",
        "real_envido": "Real Envido", "falta_envido": "Falta Envido",
    }

    TRUCO_VALORES = {"truco": 2, "retruco": 3, "vale_cuatro": 4}
    TRUCO_SIGUIENTES = {
        None: ["truco"],
        "truco": ["retruco"],
        "retruco": ["vale_cuatro"],
        "vale_cuatro": [],
    }
    NOMBRES_TRUCO = {
        "truco": "¡Truco!", "retruco": "¡Retruco!", "vale_cuatro": "¡Vale Cuatro!",
    }

    def __init__(self, nombre_j1="Jugador 1"):
        super().__init__(nombre_j1, "CPU")
        self.cartas_j1 = []
        self.cartas_j2 = []
        self.rondas = []
        self.cartas_jugadas = []  # [(carta_j1, carta_j2), ...] de la mano actual, para la mesa
        self.puntos_truco_en_juego = 1
        self.fase = "envido"  # envido -> truco -> rondas -> fin_mano
        self.partidas_ganadas = {self.j1: 0, self.j2: 0}
        self._reset_negociacion_envido()
        self._reset_negociacion_truco()

    def _reset_negociacion_envido(self):
        self.envido_nivel = None
        self.envido_acumulado = 0
        self.envido_acumulado_previo = 0
        self.envido_falta = False
        self.envido_cantor = None
        self.envido_sub_fase = "esperando_canto_humano"

    def _reset_negociacion_truco(self):
        self.truco_nivel = None
        self.truco_cantor = None
        self.truco_sub_fase = "esperando_canto_humano"

    def _jerarquia(self, carta):
        return self._ORDEN_TRUCO.get((carta.valor, carta.palo), -1)

    def mostrar_tanteador(self, jugador):
        pts = self.puntos[jugador]
        return f"{pts} pts ({'Malas' if pts <= 15 else 'Buenas'})"

    def iniciar_mano(self):
        """PRE: ninguna mano en curso.
        POST: se reparten 3 cartas a cada jugador, se resetea el estado de
        la mano (incluidas ambas negociaciones) y la fase pasa a 'envido'."""
        self.mazo = MazoTruco()
        self.cartas_j1 = [self.mazo.robar_carta() for _ in range(3)]
        self.cartas_j2 = [self.mazo.robar_carta() for _ in range(3)]
        self.rondas = []
        self.cartas_jugadas = []
        self.puntos_truco_en_juego = 1
        self.fase = "envido"
        self._reset_negociacion_envido()
        self._reset_negociacion_truco()
        return list(self.cartas_j1)

    def ronda_actual(self):
        """POST: número de ronda (1, 2 o 3) que se está jugando o se jugará."""
        return len(self.rondas) + 1

    def _calcular_envido(self, cartas):
        por_palo = {}
        for c in cartas:
            por_palo.setdefault(c.palo, []).append(c.valor_envido())
        max_envido = 0
        for valores in por_palo.values():
            if len(valores) >= 2:
                ordenados = sorted(valores, reverse=True)
                puntos = 20 + ordenados[0] + ordenados[1]
            else:
                puntos = valores[0]
            max_envido = max(max_envido, puntos)
        return max_envido

    # ------------------------------------------------------------------
    # Info para la interfaz: qué puede hacer el humano en este momento.
    # ------------------------------------------------------------------

    def opciones_disponibles(self):
        """POST: describe qué botones debería poder tocar el jugador humano
        en el estado actual, para que el panel de acciones de la GUI se
        arme dinámicamente en lugar de tener botones fijos."""
        if self.fase == "envido":
            if self.envido_sub_fase == "esperando_canto_humano":
                return {"contexto": "envido", "modo": "cantar",
                        "opciones": list(self.ENVIDO_SIGUIENTES[None]) + ["pasar"]}
            return {"contexto": "envido", "modo": "responder",
                    "opciones": ["quiero", "no_quiero"] + self.ENVIDO_SIGUIENTES[self.envido_nivel]}
        if self.fase == "truco":
            if self.truco_sub_fase == "esperando_canto_humano":
                return {"contexto": "truco", "modo": "cantar",
                        "opciones": list(self.TRUCO_SIGUIENTES[None]) + ["pasar"]}
            return {"contexto": "truco", "modo": "responder",
                    "opciones": ["quiero", "no_quiero"] + self.TRUCO_SIGUIENTES[self.truco_nivel]}
        if self.fase == "rondas":
            return {"contexto": "rondas", "modo": "jugar",
                    "opciones": ["jugar_carta", "irse_al_mazo"]}
        return {"contexto": "fin_mano", "modo": None, "opciones": []}

    # ------------------------------------------------------------------
    # ENVIDO
    # ------------------------------------------------------------------

    def _aplicar_canto_envido(self, tipo, cantor):
        self.envido_acumulado_previo = self.envido_acumulado
        if tipo == "falta_envido":
            self.envido_falta = True
        else:
            self.envido_acumulado += self.ENVIDO_INCREMENTOS[tipo]
        self.envido_nivel = tipo
        self.envido_cantor = cantor

    def cantar_envido(self, tipo):
        """
        PRE: self.fase == "envido" y self.envido_sub_fase == "esperando_canto_humano";
        tipo en self.ENVIDO_SIGUIENTES[None] + ["pasar"].
        POST: si 'tipo' es "pasar", le da el turno a la CPU para que abra
        el envido ella misma; si no, aplica el canto y hace responder a la CPU.
        """
        resultado = {"mensajes": []}
        if tipo == "pasar":
            resultado["mensajes"].append(f"{self.j1} no cantó envido.")
            r_cpu = self._cpu_intentar_abrir_envido()
            resultado["mensajes"].extend(r_cpu["mensajes"])
            if r_cpu.get("pendiente"):
                self.envido_sub_fase = "esperando_respuesta_humano"
            else:
                self._pasar_a_fase_truco()
            return resultado

        self._aplicar_canto_envido(tipo, cantor=self.j1)
        resultado["mensajes"].append(f"{self.j1} canta {self.NOMBRES_ENVIDO[tipo]}.")
        r_cpu = self._cpu_responder_envido()
        resultado["mensajes"].extend(r_cpu["mensajes"])
        if r_cpu.get("resuelto"):
            resuelto = r_cpu["resuelto"]
            resultado["mensajes"].extend(resuelto.pop("mensajes", []))
            resultado.update(resuelto)
            self._pasar_a_fase_truco()
        else:
            self.envido_sub_fase = "esperando_respuesta_humano"
        return resultado

    def responder_envido(self, respuesta):
        """
        PRE: self.fase == "envido" y self.envido_sub_fase == "esperando_respuesta_humano"
        (la CPU cantó o subió último); respuesta en {"quiero","no_quiero"} o
        un escalón legal de self.ENVIDO_SIGUIENTES[self.envido_nivel].
        """
        resultado = {"mensajes": []}
        if respuesta == "quiero":
            resultado.update(self._resolver_envido(quiere=True))
            self._pasar_a_fase_truco()
            return resultado
        if respuesta == "no_quiero":
            resultado.update(self._resolver_envido(quiere=False))
            self._pasar_a_fase_truco()
            return resultado

        self._aplicar_canto_envido(respuesta, cantor=self.j1)
        resultado["mensajes"].append(f"{self.j1} sube a {self.NOMBRES_ENVIDO[respuesta]}.")
        r_cpu = self._cpu_responder_envido()
        resultado["mensajes"].extend(r_cpu["mensajes"])
        if r_cpu.get("resuelto"):
            resuelto = r_cpu["resuelto"]
            resultado["mensajes"].extend(resuelto.pop("mensajes", []))
            resultado.update(resuelto)
            self._pasar_a_fase_truco()
        return resultado

    def _cpu_decision_envido(self):
        envido_cpu = self._calcular_envido(self.cartas_j2)
        escalables = self.ENVIDO_SIGUIENTES.get(self.envido_nivel, [])
        if envido_cpu >= 31 and escalables and not self.envido_falta:
            return escalables[0]
        umbral = 18 + self.envido_acumulado // 2
        if envido_cpu >= umbral:
            return "quiero"
        return "no_quiero"

    def _cpu_responder_envido(self):
        decision = self._cpu_decision_envido()
        mensajes = []
        if decision == "quiero":
            mensajes.append(f"{self.j2} dice: ¡QUIERO!")
            return {"mensajes": mensajes, "resuelto": self._resolver_envido(quiere=True)}
        if decision == "no_quiero":
            mensajes.append(f"{self.j2} dice: NO QUIERO.")
            return {"mensajes": mensajes, "resuelto": self._resolver_envido(quiere=False)}
        self._aplicar_canto_envido(decision, cantor=self.j2)
        mensajes.append(f"{self.j2} sube a {self.NOMBRES_ENVIDO[decision]}.")
        return {"mensajes": mensajes, "pendiente": True}

    def _cpu_intentar_abrir_envido(self):
        envido_cpu = self._calcular_envido(self.cartas_j2)
        mensajes = []
        if envido_cpu >= 28:
            tipo = "real_envido" if envido_cpu >= 31 else "envido"
            self._aplicar_canto_envido(tipo, cantor=self.j2)
            mensajes.append(f"{self.j2} canta {self.NOMBRES_ENVIDO[tipo]}.")
            return {"mensajes": mensajes, "pendiente": True}
        mensajes.append(f"{self.j2} tampoco cantó envido.")
        return {"mensajes": mensajes, "pendiente": False}

    def _resolver_envido(self, quiere):
        mensajes = []
        if quiere:
            envido_j1 = self._calcular_envido(self.cartas_j1)
            envido_j2 = self._calcular_envido(self.cartas_j2)
            ganador = self.j1 if envido_j1 >= envido_j2 else self.j2
            mensajes.append(f"Tus tantos: {envido_j1} | Tantos de {self.j2}: {envido_j2}")
            if self.envido_falta:
                puntos = self.PUNTOS_VICTORIA - self.puntos[ganador]
            else:
                puntos = self.envido_acumulado
            self.puntos[ganador] += puntos
            mensajes.append(f"¡Ganó el envido {ganador}! (+{puntos} pts)")
        else:
            ganador = self.envido_cantor
            puntos = max(1, self.envido_acumulado_previo)
            self.puntos[ganador] += puntos
            mensajes.append(f"No se quiso el envido. {ganador} se lleva {puntos} pts.")
        return {"mensajes": mensajes, "puntos": dict(self.puntos),
                "fin_partida": self._chequear_fin_partida()}

    def _pasar_a_fase_truco(self):
        if self._chequear_fin_partida():
            self.fase = "fin_mano"
        else:
            self.fase = "truco"
            self.truco_sub_fase = "esperando_canto_humano"

    # ------------------------------------------------------------------
    # TRUCO / RETRUCO / VALE CUATRO
    # ------------------------------------------------------------------

    def _aplicar_canto_truco(self, tipo, cantor):
        self.truco_nivel = tipo
        self.truco_cantor = cantor

    def cantar_truco(self, tipo):
        """
        PRE: self.fase == "truco" y self.truco_sub_fase == "esperando_canto_humano";
        tipo en self.TRUCO_SIGUIENTES[None] (== ["truco"]) + ["pasar"].
        """
        resultado = {"mensajes": []}
        if tipo == "pasar":
            resultado["mensajes"].append(f"{self.j1} no cantó Truco.")
            r_cpu = self._cpu_intentar_abrir_truco()
            resultado["mensajes"].extend(r_cpu["mensajes"])
            if r_cpu.get("pendiente"):
                self.truco_sub_fase = "esperando_respuesta_humano"
            else:
                self.fase = "rondas"
            return resultado

        self._aplicar_canto_truco(tipo, cantor=self.j1)
        resultado["mensajes"].append(f"{self.j1} canta: {self.NOMBRES_TRUCO[tipo]}")
        r_cpu = self._cpu_responder_truco()
        resultado["mensajes"].extend(r_cpu["mensajes"])
        if r_cpu.get("resuelto"):
            resuelto = r_cpu["resuelto"]
            resultado["mensajes"].extend(resuelto.pop("mensajes", []))
            resultado.update(resuelto)
        else:
            self.truco_sub_fase = "esperando_respuesta_humano"
        return resultado

    def responder_truco(self, respuesta):
        """
        PRE: self.fase == "truco" y self.truco_sub_fase == "esperando_respuesta_humano";
        respuesta en {"quiero","no_quiero"} o un escalón legal de
        self.TRUCO_SIGUIENTES[self.truco_nivel].
        """
        resultado = {"mensajes": []}
        if respuesta == "quiero":
            resultado.update(self._resolver_truco_negociacion(quiere=True))
            return resultado
        if respuesta == "no_quiero":
            resultado.update(self._resolver_truco_negociacion(quiere=False))
            return resultado

        self._aplicar_canto_truco(respuesta, cantor=self.j1)
        resultado["mensajes"].append(f"{self.j1} sube a {self.NOMBRES_TRUCO[respuesta]}")
        r_cpu = self._cpu_responder_truco()
        resultado["mensajes"].extend(r_cpu["mensajes"])
        if r_cpu.get("resuelto"):
            resuelto = r_cpu["resuelto"]
            resultado["mensajes"].extend(resuelto.pop("mensajes", []))
            resultado.update(resuelto)
        return resultado

    def _cpu_decision_truco(self):
        max_jerarquia = max(self._jerarquia(c) for c in self.cartas_j2)
        escalables = self.TRUCO_SIGUIENTES.get(self.truco_nivel, [])
        if max_jerarquia >= 12 and escalables:
            return escalables[0]
        umbral = 6 + self.TRUCO_VALORES.get(self.truco_nivel, 1)
        if max_jerarquia >= umbral or random.random() < 0.35:
            return "quiero"
        return "no_quiero"

    def _cpu_responder_truco(self):
        decision = self._cpu_decision_truco()
        mensajes = []
        if decision == "quiero":
            mensajes.append(f"{self.j2} dice: ¡QUIERO!")
            return {"mensajes": mensajes, "resuelto": self._resolver_truco_negociacion(quiere=True)}
        if decision == "no_quiero":
            mensajes.append(f"{self.j2} dice: NO QUIERO.")
            return {"mensajes": mensajes, "resuelto": self._resolver_truco_negociacion(quiere=False)}
        self._aplicar_canto_truco(decision, cantor=self.j2)
        mensajes.append(f"{self.j2} sube a {self.NOMBRES_TRUCO[decision]}")
        return {"mensajes": mensajes, "pendiente": True}

    def _cpu_intentar_abrir_truco(self):
        max_jerarquia = max(self._jerarquia(c) for c in self.cartas_j2)
        mensajes = []
        if max_jerarquia >= 9:
            self._aplicar_canto_truco("truco", cantor=self.j2)
            mensajes.append(f"{self.j2} canta: {self.NOMBRES_TRUCO['truco']}")
            return {"mensajes": mensajes, "pendiente": True}
        mensajes.append(f"{self.j2} tampoco cantó Truco.")
        return {"mensajes": mensajes, "pendiente": False}

    def _resolver_truco_negociacion(self, quiere):
        mensajes = []
        if quiere:
            self.puntos_truco_en_juego = self.TRUCO_VALORES[self.truco_nivel]
            mensajes.append(f"¡Se juega por {self.puntos_truco_en_juego} puntos!")
            self.fase = "rondas"
            return {"mensajes": mensajes}
        ganador = self.truco_cantor
        niveles = ["truco", "retruco", "vale_cuatro"]
        idx = niveles.index(self.truco_nivel)
        puntos = self.TRUCO_VALORES[niveles[idx - 1]] if idx > 0 else 1
        self.puntos[ganador] += puntos
        mensajes.append(f"No se quiso. {ganador} se lleva {puntos} pts.")
        self.fase = "fin_mano"
        return {"mensajes": mensajes, "mano_terminada": True, "ganador_mano": ganador,
                "fin_partida": self._chequear_fin_partida()}

    # ------------------------------------------------------------------
    # RONDAS (juego de cartas) e IRSE AL MAZO
    # ------------------------------------------------------------------

    def jugar_carta(self, indice):
        """
        PRE: self.fase == "rondas"; 0 <= indice < len(self.cartas_j1).
        POST: se juega la carta elegida, la CPU responde con una carta al
        azar, se resuelve la ronda y -si corresponde- la mano completa.
        """
        resultado = {"mensajes": []}
        c_j1 = self.cartas_j1.pop(indice)
        idx_cpu = random.randrange(len(self.cartas_j2))
        c_j2 = self.cartas_j2.pop(idx_cpu)
        resultado["carta_j1"] = str(c_j1)
        resultado["carta_j2"] = str(c_j2)
        self.cartas_jugadas.append((c_j1, c_j2))

        if self._jerarquia(c_j1) > self._jerarquia(c_j2):
            ganador_ronda = "j1"
            resultado["mensajes"].append(f"Ganaste la ronda con {c_j1} contra {c_j2}.")
        elif self._jerarquia(c_j2) > self._jerarquia(c_j1):
            ganador_ronda = "j2"
            resultado["mensajes"].append(f"{self.j2} ganó la ronda con {c_j2} contra {c_j1}.")
        else:
            ganador_ronda = "parda"
            resultado["mensajes"].append(f"Ronda PARDA: {c_j1} y {c_j2} empatan.")
        self.rondas.append(ganador_ronda)
        resultado["ganador_ronda"] = ganador_ronda

        ganador_mano = self._evaluar_rondas()
        if ganador_mano is None and len(self.rondas) == 3:
            ganador_mano = self.j1  # condición de mano: gana quien es mano

        if ganador_mano:
            self.puntos[ganador_mano] += self.puntos_truco_en_juego
            self.fase = "fin_mano"
            resultado["mano_terminada"] = True
            resultado["ganador_mano"] = ganador_mano
            resultado["mensajes"].append(
                f"¡{ganador_mano} se lleva el Truco! (+{self.puntos_truco_en_juego} pts)"
            )
            resultado["fin_partida"] = self._chequear_fin_partida()
        return resultado

    def irse_al_mazo(self):
        """PRE: self.fase == "rondas".
        POST: el jugador humano abandona la mano; la CPU se lleva los
        puntos que estaban en juego (self.puntos_truco_en_juego)."""
        self.puntos[self.j2] += self.puntos_truco_en_juego
        self.fase = "fin_mano"
        return {
            "mensajes": [f"{self.j1} se fue al mazo. {self.j2} se lleva "
                         f"{self.puntos_truco_en_juego} pts."],
            "mano_terminada": True,
            "ganador_mano": self.j2,
            "fin_partida": self._chequear_fin_partida(),
        }

    def _evaluar_rondas(self):
        r = self.rondas
        if r.count("j1") == 2:
            return self.j1
        if r.count("j2") == 2:
            return self.j2
        if len(r) == 2 and r[0] == "parda" and r[1] != "parda":
            return self.j1 if r[1] == "j1" else self.j2
        if len(r) == 2 and r[1] == "parda" and r[0] != "parda":
            return self.j1 if r[0] == "j1" else self.j2
        return None

    def _chequear_fin_partida(self):
        if self.puntos[self.j1] >= self.PUNTOS_VICTORIA or self.puntos[self.j2] >= self.PUNTOS_VICTORIA:
            self.terminado = True
            ganador = self.j1 if self.puntos[self.j1] >= self.PUNTOS_VICTORIA else self.j2
            self.partidas_ganadas[ganador] += 1
            return ganador
        return None


# =============================================================================
# CHINCHÓN
# =============================================================================

class Chinchon(JuegoDeCartas):
    """
    Chinchón, un jugador humano contra la CPU, con mazo español de 48
    cartas (los 4 palos x 12 valores completos, incluyendo 8 y 9, y
    sin comodines).

    Reglas implementadas:
    - Cada jugador tiene 7 cartas en mano.
    - En su turno, un jugador roba una carta (del mazo o del pozo de
      descarte) quedando con 8, y luego descarta una, volviendo a 7.
    - Una combinación válida es una escalera (3 o más cartas consecutivas
      del mismo palo) o un trío/cuadra (3 o 4 cartas del mismo valor, en
      palos distintos).
    - Un jugador puede cerrar la mano cuando, dejando a lo sumo 1 carta
      suelta, el resto de su mano se descompone completamente en
      combinaciones válidas.
    - Al cerrar la mano, cada jugador suma a su puntaje total los puntos
      de las cartas que le quedaron sueltas (las figuras valen 10). Si
      alguien cierra sin ninguna carta suelta ("Chinchón" perfecto), el
      rival recibe además una penalización extra.
    - Gana la partida quien tenga MENOS puntos acumulados cuando algún
      jugador llega a PUNTOS_DERROTA.

    Invariante: len(self.mano_j1) y len(self.mano_j2) están siempre entre
    CARTAS_POR_MANO y CARTAS_POR_MANO + 1 mientras la mano está en curso.
    """

    CARTAS_POR_MANO = 7
    PUNTOS_DERROTA = 100
    BONUS_CHINCHON = 25

    def __init__(self, nombre_j1="Jugador 1"):
        super().__init__(nombre_j1, "CPU")
        self.mano_j1 = []
        self.mano_j2 = []
        self.pozo = Pila()
        self.fase = "esperando_robo"  # esperando_robo -> esperando_descarte -> fin_mano

    def iniciar_mano(self):
        """PRE: ninguna mano en curso.
        POST: se reparten 7 cartas a cada jugador y se destapa la primera
        carta del pozo de descarte."""
        self.mazo = MazoChinchon()
        self.mano_j1 = [self.mazo.robar_carta() for _ in range(self.CARTAS_POR_MANO)]
        self.mano_j2 = [self.mazo.robar_carta() for _ in range(self.CARTAS_POR_MANO)]
        self.pozo = Pila()
        self.pozo.push(self.mazo.robar_carta())
        self.fase = "esperando_robo"
        return {
            "mano": list(self.mano_j1),
            "pozo_arriba": str(self.pozo.peek()),
            "cartas_restantes": self.mazo.cantidad_restante(),
        }

    # --- combinaciones -----------------------------------------------------

    @staticmethod
    def _es_combinacion_valida(cartas):
        """POST: True si 'cartas' forma una escalera o un trío/cuadra válidos."""
        if len(cartas) < 3:
            return False
        comodines = [c for c in cartas if c.es_comodin()]
        reales = [c for c in cartas if not c.es_comodin()]
        if not reales:
            return False

        # Trío / cuadra: mismo valor, hasta 4 cartas en total.
        if len(set(c.valor for c in reales)) == 1 and len(cartas) <= 4:
            return True

        # Escalera: mismo palo, valores consecutivos (los comodines llenan huecos).
        if len(set(c.palo for c in reales)) == 1:
            valores = sorted(c.valor for c in reales)
            if len(set(valores)) != len(valores):
                return False  # no puede haber valores repetidos en una escalera
            huecos = sum(b - a - 1 for a, b in zip(valores, valores[1:]))
            return huecos <= len(comodines)

        return False

    def _mejor_descomposicion(self, cartas):
        """
        Búsqueda recursiva sobre las cartas de una mano (7 u 8 cartas, un
        espacio de búsqueda chico) que encuentra la descomposición en
        combinaciones que deja la menor cantidad de puntos sueltos.
        POST: retorna (grupos, sueltas).
        """
        cartas = list(cartas)
        mejor = {"grupos": [], "sueltas": cartas}

        def puntos(sueltas):
            return sum(c.valor_chinchon() for c in sueltas)

        def backtrack(restantes, grupos_actuales):
            nonlocal mejor
            if puntos(restantes) < puntos(mejor["sueltas"]):
                mejor = {"grupos": list(grupos_actuales), "sueltas": list(restantes)}
            n = len(restantes)
            tam_max = min(n, 7)
            for tam in range(tam_max, 2, -1):
                for combo in itertools.combinations(range(n), tam):
                    subset = [restantes[i] for i in combo]
                    if self._es_combinacion_valida(subset):
                        resto = [restantes[i] for i in range(n) if i not in combo]
                        backtrack(resto, grupos_actuales + [subset])

        backtrack(cartas, [])
        return mejor["grupos"], mejor["sueltas"]

    def puntos_de_mano(self, cartas):
        """POST: puntaje (suma de cartas sueltas) de la mejor descomposición posible."""
        _, sueltas = self._mejor_descomposicion(cartas)
        return sum(c.valor_chinchon() for c in sueltas)

    # --- turno del jugador humano ------------------------------------------

    def robar_del_mazo(self):
        """PRE: self.fase == "esperando_robo"."""
        if self.mazo.esta_vacio():
            return {"error": "El mazo está vacío."}
        carta = self.mazo.robar_carta()
        self.mano_j1.append(carta)
        self.fase = "esperando_descarte"
        return {"carta": str(carta), "mano": list(self.mano_j1)}

    def robar_del_pozo(self):
        """PRE: self.fase == "esperando_robo" y el pozo no está vacío."""
        if self.pozo.is_empty():
            return {"error": "El pozo está vacío."}
        carta = self.pozo.pop()
        self.mano_j1.append(carta)
        self.fase = "esperando_descarte"
        return {"carta": str(carta), "mano": list(self.mano_j1)}

    def descartar(self, indice):
        """
        PRE: self.fase == "esperando_descarte"; 0 <= indice < len(mano_j1).
        POST: se descarta la carta elegida, termina el turno humano, juega
        automáticamente la CPU su turno completo y el control vuelve a
        'esperando_robo' (o a 'fin_mano' si alguien cerró).
        """
        carta = self.mano_j1.pop(indice)
        self.pozo.push(carta)
        resultado = {"descartada": str(carta), "mensajes": [f"{self.j1} descartó {carta}."]}

        resultado_cpu = self._turno_cpu()
        resultado["cpu"] = resultado_cpu
        if resultado_cpu.get("cierre"):
            resultado["fin_mano"] = resultado_cpu["cierre"]
        else:
            self.fase = "esperando_robo"
        return resultado

    def cerrar_mano(self):
        """
        PRE: self.fase == "esperando_descarte" (el jugador ya robó y tiene 8 cartas).
        POST: si existe alguna carta que, descartada, deja el resto de la mano
        con a lo sumo 1 carta suelta, se cierra la mano y se calcula el puntaje.
        Si las 7 cartas restantes quedan combinadas en una única escalera (sin
        ninguna suelta), se trata de un "Chinchón" y el rival recibe el bono.
        """
        cartas = list(self.mano_j1)
        mejor_opcion = None
        for idx in range(len(cartas)):
            restantes = cartas[:idx] + cartas[idx + 1:]
            grupos, sueltas = self._mejor_descomposicion(restantes)
            if len(sueltas) <= 1 and (mejor_opcion is None or len(sueltas) < len(mejor_opcion[2])):
                mejor_opcion = (idx, grupos, sueltas)

        if mejor_opcion is None:
            return {"error": "No podés cerrar: te quedan demasiadas cartas sueltas."}

        idx, grupos, sueltas = mejor_opcion
        descartada = cartas[idx]
        self.mano_j1.remove(descartada)
        self.pozo.push(descartada)
        return self._finalizar_mano(cerrador=self.j1, grupos=grupos, sueltas=sueltas)

    # --- turno de la CPU -----------------------------------------------------

    def _turno_cpu(self):
        mensajes = []
        carta_pozo = self.pozo.peek() if not self.pozo.is_empty() else None
        conviene_pozo = False
        if carta_pozo is not None:
            puntos_con_pozo = self.puntos_de_mano(self.mano_j2 + [carta_pozo])
            puntos_sin_pozo = self.puntos_de_mano(self.mano_j2)
            conviene_pozo = puntos_con_pozo < puntos_sin_pozo

        if self.mazo.esta_vacio() and carta_pozo is None:
            return {"mensajes": ["No quedan cartas para robar. La mano queda sin cierre."],
                     "sin_cartas": True}

        if conviene_pozo or (self.mazo.esta_vacio() and carta_pozo is not None):
            carta = self.pozo.pop()
            origen = "el pozo"
        else:
            carta = self.mazo.robar_carta()
            origen = "el mazo"
        self.mano_j2.append(carta)
        mensajes.append(f"{self.j2} robó de {origen}.")

        mejor_opcion = None
        for idx in range(len(self.mano_j2)):
            restantes = self.mano_j2[:idx] + self.mano_j2[idx + 1:]
            grupos, sueltas = self._mejor_descomposicion(restantes)
            if len(sueltas) <= 1 and (mejor_opcion is None or len(sueltas) < len(mejor_opcion[2])):
                mejor_opcion = (idx, grupos, sueltas)
        if mejor_opcion is not None:
            idx, grupos, sueltas = mejor_opcion
            descartada = self.mano_j2.pop(idx)
            self.pozo.push(descartada)
            mensajes.append(f"{self.j2} descartó {descartada} y cerró la mano.")
            cierre = self._finalizar_mano(cerrador=self.j2, grupos=grupos, sueltas=sueltas)
            return {"mensajes": mensajes, "cierre": cierre}

        _, sueltas = self._mejor_descomposicion(self.mano_j2)
        peor = max(sueltas, key=lambda c: c.valor_chinchon()) if sueltas else self.mano_j2[-1]
        self.mano_j2.remove(peor)
        self.pozo.push(peor)
        mensajes.append(f"{self.j2} descartó {peor}.")
        return {"mensajes": mensajes}

    # --- cierre y puntaje ----------------------------------------------------

    def _finalizar_mano(self, cerrador, grupos=None, sueltas=None):
        puntos_j1 = self.puntos_de_mano(self.mano_j1)
        puntos_j2 = self.puntos_de_mano(self.mano_j2)

        # "Chinchón": el cerrador combinó sus 7 cartas en UNA sola escalera,
        # sin ninguna carta suelta (no alcanza con dejar 0 puntos sueltos
        # repartidos en varias combinaciones: tiene que ser una única corrida).
        chinchon_perfecto = (
            grupos is not None and sueltas is not None
            and len(sueltas) == 0 and len(grupos) == 1 and len(grupos[0]) == 7
        )

        self.puntos[self.j1] += puntos_j1
        self.puntos[self.j2] += puntos_j2

        mensajes = []
        if chinchon_perfecto:
            perdedor = self.j2 if cerrador == self.j1 else self.j1
            self.puntos[perdedor] += self.BONUS_CHINCHON
            mensajes.append(
                f"¡{cerrador} cerró con Chinchón! {perdedor} recibe {self.BONUS_CHINCHON} puntos extra."
            )

        self.fase = "fin_mano"
        return {
            "cerrador": cerrador,
            "puntos_mano_j1": puntos_j1,
            "puntos_mano_j2": puntos_j2,
            "chinchon": chinchon_perfecto,
            "puntos_totales": dict(self.puntos),
            "fin_partida": self._chequear_fin_partida(),
            "mensajes": mensajes,
        }

    def _chequear_fin_partida(self):
        if self.puntos[self.j1] >= self.PUNTOS_DERROTA or self.puntos[self.j2] >= self.PUNTOS_DERROTA:
            self.terminado = True
            return self.j1 if self.puntos[self.j1] < self.puntos[self.j2] else self.j2
        return None


# =============================================================================
# PARTE 4 – GAME MANAGER
# =============================================================================

class GameManager:
    """
    Responsable de iniciar el programa, crear el juego elegido y coordinar
    el flujo general de la partida. Agregar un juego nuevo sólo requiere
    darlo de alta en JUEGOS_DISPONIBLES: el resto del sistema (incluida la
    interfaz gráfica) no necesita cambiar su estructura principal.
    """

    JUEGOS_DISPONIBLES = ("Truco", "Chinchón")

    def __init__(self):
        self.juego_actual = None

    def crear_juego(self, nombre_juego, nombre_jugador):
        """PRE: nombre_juego en JUEGOS_DISPONIBLES.
        POST: se crea, guarda y retorna la instancia del juego elegido."""
        nombre_jugador = nombre_jugador.strip() or "Jugador 1"
        if nombre_juego == "Truco":
            self.juego_actual = Truco(nombre_jugador)
        elif nombre_juego == "Chinchón":
            self.juego_actual = Chinchon(nombre_jugador)
        else:
            raise ValueError(f"Juego desconocido: {nombre_juego}")
        return self.juego_actual

    def finalizar_juego(self):
        """POST: se libera la partida actual."""
        self.juego_actual = None

    def __str__(self):
        if self.juego_actual is None:
            return "GameManager sin partida activa"
        return f"GameManager -> {self.juego_actual}"