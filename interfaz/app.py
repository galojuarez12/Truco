"""
Controlador principal de la interfaz: crea la ventana, arma el
GameManager y el gestor de imágenes una única vez, y se encarga de
cambiar entre pantallas.

El programa abre DIRECTAMENTE en el menú principal (Truco / Chinchón /
Salir): no hay pantalla de presentación ni demora de entrada. Los
cambios de pantalla DENTRO de la app (por ejemplo al pasar del menú a
una partida) sí llevan una transición breve, para que no se sientan
como un corte seco.
"""

import tkinter as tk

from . import tema
from .imagenes import GestorImagenes
from .animaciones import fundido_ventana
from .pantalla_bienvenida import PantallaBienvenida
from .pantalla_truco import PantallaTruco
from .pantalla_chinchon import PantallaChinchon
from .pantalla_ganador import PantallaGanador

from juegos import GameManager

ANCHO_VENTANA, ALTO_VENTANA = 1040, 820
ANCHO_MINIMO, ALTO_MINIMO = 900, 700


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Truco Argentino — Sistema de Juegos de Cartas")
        self.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.minsize(ANCHO_MINIMO, ALTO_MINIMO)
        self.configure(bg=tema.COLOR_FONDO)
        tema.configurar_estilos_ttk(self)

        self.gm = GameManager()
        self.nombre_jugador = "Octavio"
        self.imagenes = GestorImagenes("imagenes")

        self.contenedor = tk.Frame(self, bg=tema.COLOR_FONDO)
        self.contenedor.pack(fill="both", expand=True)

        # Se muestra directamente, sin fundido ni demora: es el menú
        # principal, no una pantalla de presentación.
        self._mostrar_pantalla(self._construir_bienvenida)

    # ------------------------------------------------------------------
    # MANEJO DE PANTALLAS
    # ------------------------------------------------------------------
    def _limpiar_contenedor(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def _mostrar_pantalla(self, construir_pantalla):
        self._limpiar_contenedor()
        pantalla = construir_pantalla(self.contenedor)
        pantalla.pack(fill="both", expand=True)

    def _transicionar(self, construir_pantalla):
        """Cambia de pantalla con un breve fundido de por medio (no se
        usa para la apertura inicial del programa, sólo para moverse
        entre pantallas ya con la ventana abierta)."""
        def cambiar():
            self._mostrar_pantalla(construir_pantalla)
            fundido_ventana(self, hacia=1.0, duracion_ms=180)
        fundido_ventana(self, hacia=0.3, duracion_ms=140, al_terminar=cambiar)

    # ------------------------------------------------------------------
    # CONSTRUCTORES DE PANTALLA
    # ------------------------------------------------------------------
    def _construir_bienvenida(self, parent):
        self.gm.finalizar_juego()
        return PantallaBienvenida(
            parent,
            on_truco=self._iniciar_truco,
            on_chinchon=self._iniciar_chinchon,
            on_salir=self._salir,
        )

    def _mostrar_bienvenida(self):
        self._transicionar(self._construir_bienvenida)

    def _iniciar_truco(self):
        truco = self.gm.crear_juego("Truco", self.nombre_jugador)
        self._transicionar(lambda parent: PantallaTruco(
            parent, truco, self.imagenes,
            on_volver_menu=self._mostrar_bienvenida,
            on_fin_partida=self._mostrar_ganador_truco,
        ))

    def _iniciar_chinchon(self):
        chinchon = self.gm.crear_juego("Chinchón", self.nombre_jugador)
        self._transicionar(lambda parent: PantallaChinchon(
            parent, chinchon, self.imagenes,
            on_volver_menu=self._mostrar_bienvenida,
            on_fin_partida=self._mostrar_ganador_chinchon,
        ))

    def _mostrar_ganador_truco(self, ganador, detalle):
        self._transicionar(lambda parent: PantallaGanador(
            parent, ganador, detalle,
            on_jugar_de_nuevo=self._iniciar_truco,
            on_menu=self._mostrar_bienvenida,
        ))

    def _mostrar_ganador_chinchon(self, ganador, detalle):
        self._transicionar(lambda parent: PantallaGanador(
            parent, ganador, detalle,
            on_jugar_de_nuevo=self._iniciar_chinchon,
            on_menu=self._mostrar_bienvenida,
        ))

    def _salir(self):
        self.destroy()


def main():
    app = App()
    app.mainloop()
