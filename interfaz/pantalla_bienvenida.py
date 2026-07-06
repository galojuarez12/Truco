"""
Pantalla de bienvenida / menú principal.

Comparte exactamente la misma identidad visual que el resto de la app:
tablero celeste, panel blanco con borde celeste suave, misma
tipografía. Se muestra de una: sin fundido de entrada, sin animación de
aparición, sin demora — es el menú principal, no una pantalla de
presentación.
"""

import tkinter as tk

from . import tema
from .widgets import BotonModerno, crear_panel_con_sombra, etiqueta


class PantallaBienvenida(tk.Frame):
    def __init__(self, parent, on_truco, on_chinchon, on_salir):
        super().__init__(parent, bg=tema.COLOR_FONDO)
        self._on_truco = on_truco
        self._on_chinchon = on_chinchon
        self._on_salir = on_salir

        centro = tk.Frame(self, bg=tema.COLOR_FONDO)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        contenedor, panel = crear_panel_con_sombra(centro, grosor=3)
        contenedor.pack()

        etiqueta(
            panel, "🂡 Bienvenido Octavio", fuente=tema.FUENTE_TITULO,
            fg=tema.COLOR_ACENTO, bg=tema.COLOR_PANEL,
        ).pack(padx=50, pady=(36, 10))

        # cinta celeste sutil: detalle patrio, discreto
        tk.Frame(panel, bg=tema.CELESTE, height=3).pack(fill="x", padx=70)

        etiqueta(
            panel, "Elegí el modo de juego", fuente=tema.FUENTE_SUBTITULO,
            fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL,
        ).pack(pady=(14, 26))

        botones_frame = tk.Frame(panel, bg=tema.COLOR_PANEL)
        botones_frame.pack(padx=50, pady=(0, 40))

        BotonModerno(
            botones_frame, "🃏  Truco contra la CPU", comando=self._on_truco,
            ancho=300, alto=52, color_normal=tema.COLOR_ACENTO, color_hover=tema.COLOR_ACENTO_HOVER,
            color_texto=tema.COLOR_ACENTO_TEXTO, color_fondo_parent=tema.COLOR_PANEL,
        ).pack(pady=8)
        BotonModerno(
            botones_frame, "🂮  Chinchón", comando=self._on_chinchon,
            ancho=300, alto=52, color_fondo_parent=tema.COLOR_PANEL,
        ).pack(pady=8)
        BotonModerno(
            botones_frame, "🚪  Salir", comando=self._on_salir,
            ancho=300, alto=52, color_normal=tema.COLOR_PELIGRO,
            color_hover=tema.COLOR_PELIGRO_HOVER, color_texto=tema.COLOR_ACENTO_TEXTO,
            color_fondo_parent=tema.COLOR_PANEL,
        ).pack(pady=8)
