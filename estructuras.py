"""
Trabajo Práctico – Programación 3
Parte 1 – Estructuras lineales (TAD Nodo, ListaEnlazada, Pila)

Estas estructuras están implementadas SIN usar list, deque ni ninguna
colección ya provista por el lenguaje: todo se maneja con nodos enlazados
a mano, tal como pide la consigna.
"""


class Nodo:
    """
    TAD Nodo.

    Invariante: self.dato puede ser cualquier valor; self.siguiente es una
    instancia de Nodo o None (si es el último nodo de la secuencia).
    """

    def __init__(self, dato, siguiente=None):
        # PRE: ninguna.
        # POST: se crea un nodo que guarda 'dato' y apunta a 'siguiente'.
        self.dato = dato
        self.siguiente = siguiente

    def __str__(self):
        return str(self.dato)


class ListaEnlazada:
    """
    TAD Lista implementado con nodos enlazados (lista simplemente enlazada).

    Invariante: self.cabeza es None (lista vacía) o un Nodo cuya cadena de
    'siguiente' termina en None; self._tamanio siempre coincide con la
    cantidad real de nodos alcanzables desde self.cabeza.
    """

    def __init__(self):
        # POST: se crea una lista vacía.
        self.cabeza = None
        self._tamanio = 0

    def insertar_inicio(self, dato):
        """PRE: ninguna.
        POST: 'dato' queda como nueva cabeza de la lista; longitud += 1."""
        nuevo = Nodo(dato, self.cabeza)
        self.cabeza = nuevo
        self._tamanio += 1

    def insertar_final(self, dato):
        """PRE: ninguna.
        POST: 'dato' queda como último elemento de la lista; longitud += 1."""
        nuevo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamanio += 1

    def eliminar(self, dato):
        """PRE: ninguna.
        POST: si 'dato' está en la lista, se elimina la PRIMERA ocurrencia
        y la longitud disminuye en 1; si no está, la lista queda sin cambios."""
        if self.cabeza is None:
            return
        if self.cabeza.dato == dato:
            self.cabeza = self.cabeza.siguiente
            self._tamanio -= 1
            return
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.dato == dato:
                actual.siguiente = actual.siguiente.siguiente
                self._tamanio -= 1
                return
            actual = actual.siguiente

    def buscar(self, dato):
        """PRE: ninguna.
        POST: retorna True si 'dato' aparece en la lista, False en caso contrario."""
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return True
            actual = actual.siguiente
        return False

    def esta_vacia(self):
        """POST: retorna True si la lista no tiene elementos."""
        return self.cabeza is None

    def __len__(self):
        return self._tamanio

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def __str__(self):
        elementos = ""
        actual = self.cabeza
        while actual:
            elementos += str(actual.dato) + " "
            actual = actual.siguiente
        return elementos + "None"


class Pila:
    """
    TAD Pila (LIFO), implementado sobre ListaEnlazada.

    Invariante: el tope de la pila es siempre self._lista.cabeza (la última
    carta empujada es la primera en salir).
    """

    def __init__(self):
        # POST: se crea una pila vacía.
        self._lista = ListaEnlazada()

    def push(self, dato):
        """PRE: ninguna. POST: 'dato' queda en el tope de la pila."""
        self._lista.insertar_inicio(dato)

    def pop(self):
        """PRE: la pila no debe estar vacía.
        POST: se retorna y remueve el elemento del tope."""
        if self.is_empty():
            raise ValueError("La pila está vacía.")
        tope = self._lista.cabeza.dato
        self._lista.cabeza = self._lista.cabeza.siguiente
        self._lista._tamanio -= 1
        return tope

    def peek(self):
        """PRE: la pila no debe estar vacía.
        POST: retorna el elemento del tope sin removerlo."""
        if self.is_empty():
            raise ValueError("La pila está vacía.")
        return self._lista.cabeza.dato

    def is_empty(self):
        """POST: retorna True si la pila no tiene elementos."""
        return self._lista.esta_vacia()

    def __len__(self):
        return len(self._lista)

    def __str__(self):
        return str(self._lista)
