"""
Pantalla de fin de partida ("pantalla del ganador" del diagrama de flujo
pedido). Se muestra una vez que algún jugador llega al puntaje de
victoria/derrota del juego que se esté jugando. Comparte el mismo
tablero celeste, panel blanco y tipografía que el resto de la app.
"""

import tkinter as tk

from . import tema
from .widgets import BotonModerno, crear_panel_con_sombra, etiqueta


class PantallaGanador(tk.Frame):
    def __init__(self, parent, ganador, detalle, on_jugar_de_nuevo, on_menu):
        super().__init__(parent, bg=tema.COLOR_FONDO)
        self._on_jugar_de_nuevo = on_jugar_de_nuevo
        self._on_menu = on_menu

        centro = tk.Frame(self, bg=tema.COLOR_FONDO)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        contenedor, panel = crear_panel_con_sombra(centro, grosor=3)
        contenedor.pack()

        etiqueta(panel, "🏆", fuente=tema.FUENTE_TITULO, bg=tema.COLOR_PANEL).pack(
            padx=60, pady=(36, 6))
        etiqueta(
            panel, f"¡{ganador} ganó la partida!",
            fuente=tema.FUENTE_TITULO_CHICO, fg=tema.COLOR_ACENTO, bg=tema.COLOR_PANEL,
        ).pack(pady=(0, 8))
        if detalle:
            etiqueta(
                panel, detalle, fuente=tema.FUENTE_SUBTITULO,
                fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL,
            ).pack(pady=(0, 26))
        else:
            tk.Frame(panel, height=18, bg=tema.COLOR_PANEL).pack()

        botones = tk.Frame(panel, bg=tema.COLOR_PANEL)
        botones.pack(pady=(0, 36))
        BotonModerno(
            botones, "🔁  Jugar de nuevo", comando=self._on_jugar_de_nuevo,
            ancho=280, alto=48, color_normal=tema.COLOR_ACENTO, color_hover=tema.COLOR_ACENTO_HOVER,
            color_texto=tema.COLOR_ACENTO_TEXTO, color_fondo_parent=tema.COLOR_PANEL,
        ).pack(pady=6)
        BotonModerno(
            botones, "⟵  Volver al menú", comando=self._on_menu,
            ancho=280, alto=44, color_fondo_parent=tema.COLOR_PANEL,
        ).pack(pady=6)
