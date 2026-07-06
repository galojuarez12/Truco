"""
Trabajo Práctico – Programación 3
Parte 2 – Modelado de cartas (TAD Carta, Mazo, MazoEspañol)
"""

import random
from estructuras import Pila

PALOS = ("oro", "copa", "espada", "basto")
VALORES_COMPLETOS = tuple(range(1, 13))  # 1 a 12
NOMBRES_FIGURA = {10: "Sota", 11: "Caballo", 12: "Rey"}


class Carta:
    """
    TAD Carta (naipe de la baraja española).

    Invariante: o bien es_comodin() es True (valor == 0, palo == "comodin"),
    o bien 1 <= valor <= 12 y palo pertenece a PALOS.
    """

    def __init__(self, valor, palo):
        # PRE: (palo == "comodin" y valor == 0) o (1 <= valor <= 12 y palo en PALOS).
        self.valor = valor
        self.palo = palo

    def es_comodin(self):
        """POST: True si la carta es un comodín (wild)."""
        return self.palo == "comodin"

    def valor_envido(self):
        """POST: valor usado para calcular el envido en el Truco
        (las figuras 10/11/12 valen 0)."""
        return 0 if self.valor >= 10 else self.valor

    def valor_chinchon(self):
        """POST: valor usado para el puntaje en el Chinchón
        (las figuras 10/11/12 valen 10; el comodín vale 0)."""
        if self.es_comodin():
            return 0
        return 10 if self.valor >= 10 else self.valor

    def __str__(self):
        if self.es_comodin():
            return "Comodín"
        nombre = NOMBRES_FIGURA.get(self.valor, str(self.valor))
        return f"{nombre} de {self.palo.capitalize()}"

    def __eq__(self, otra):
        return isinstance(otra, Carta) and self.valor == otra.valor and self.palo == otra.palo

    def __lt__(self, otra):
        return self.valor < otra.valor

    def __gt__(self, otra):
        return self.valor > otra.valor

    def __hash__(self):
        return hash((self.valor, self.palo))


class Mazo:
    """
    TAD Mazo genérico: un conjunto de cartas apiladas (implementado con la
    Pila de la Parte 1).

    Invariante: self._pila contiene únicamente instancias de Carta.
    """

    def __init__(self):
        # POST: se crea un mazo vacío.
        self._pila = Pila()

    def barajar(self):
        """PRE: ninguna.
        POST: el orden interno de las cartas queda aleatorizado."""
        temporal = []
        while not self._pila.is_empty():
            temporal.append(self._pila.pop())
        random.shuffle(temporal)
        for carta in temporal:
            self._pila.push(carta)

    def robar_carta(self):
        """PRE: cantidad_restante() > 0.
        POST: se retorna y remueve la carta que está en el tope del mazo."""
        return self._pila.pop()

    def cantidad_restante(self):
        """POST: retorna cuántas cartas quedan en el mazo."""
        return len(self._pila)

    def esta_vacio(self):
        """POST: True si no quedan cartas para robar."""
        return self._pila.is_empty()

    def agregar_carta(self, carta):
        """PRE: ninguna. POST: 'carta' queda en el tope del mazo
        (se usa, por ejemplo, para reciclar el pozo de descarte)."""
        self._pila.push(carta)

    def __str__(self):
        return f"Mazo con {self.cantidad_restante()} carta(s)"


class MazoEspanol(Mazo):
    """
    Mazo español "completo", tal como lo pide la consigna original:
    4 palos (oro, copa, espada, basto) x 12 valores (1 a 12) + 2 comodines
    = 50 cartas en total.

    Los juegos concretos (Truco, Chinchón) heredan de esta clase y sólo
    toman el subconjunto de cartas que realmente usan, para no repetir la
    lógica de armado y barajado del mazo.
    """

    def __init__(self, incluir_comodines=True, excluir_valores=None):
        super().__init__()
        excluir_valores = excluir_valores or ()
        for palo in PALOS:
            for valor in VALORES_COMPLETOS:
                if valor not in excluir_valores:
                    self._pila.push(Carta(valor, palo))
        if incluir_comodines:
            self._pila.push(Carta(0, "comodin"))
            self._pila.push(Carta(0, "comodin"))
        self.barajar()


class MazoTruco(MazoEspanol):
    """Mazo de 40 cartas usado en el Truco: sin 8, sin 9 y sin comodines."""

    def __init__(self):
        super().__init__(incluir_comodines=False, excluir_valores=(8, 9))


class MazoChinchon(MazoEspanol):
    """Mazo de 48 cartas usado en el Chinchón: las 4 palos x 12 valores
    completos (incluye 8 y 9) y sin comodines."""

    def __init__(self):
        super().__init__(incluir_comodines=False)
