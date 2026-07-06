"""
Utilidades de animación mínimas, livianas (basadas en `after()`, sin
hilos ni librerías extra):

- `fundido_ventana`: fundido de toda la ventana, usado en las
  transiciones entre pantallas.
- `pulso_color`: parpadeo suave de color, usado para resaltar quién
  ganó una mano en el marcador.

Deliberadamente NO hay ningún efecto que toque las cartas (nada de
fundidos ni cambios de tamaño sobre las imágenes): se mostraron nítidas
y sin transparencias, tal como se pidió.
"""

import tkinter as tk


def _interpolar(a, b, t):
    return a + (b - a) * t


def fundido_ventana(ventana, hacia=1.0, pasos=14, duracion_ms=260, al_terminar=None):
    """Anima la transparencia de toda la ventana (fade in/out). Funciona
    muy bien en Windows/macOS. En Linux, si el gestor de ventanas no
    soporta '-alpha', se ignora silenciosamente y la ventana queda
    completamente visible (no rompe nada)."""
    try:
        inicio = float(ventana.attributes("-alpha"))
    except tk.TclError:
        if al_terminar:
            al_terminar()
        return

    paso_actual = [0]
    delay = max(1, duracion_ms // max(1, pasos))

    def tick():
        paso_actual[0] += 1
        t = paso_actual[0] / pasos
        try:
            ventana.attributes("-alpha", _interpolar(inicio, hacia, min(1.0, t)))
        except tk.TclError:
            return
        if paso_actual[0] < pasos:
            ventana.after(delay, tick)
        elif al_terminar:
            al_terminar()

    tick()


def pulso_color(widget, color_a, color_b, repeticiones=3, duracion_ms=260, atributo="bg", al_terminar=None):
    """Hace parpadear suavemente un widget entre dos colores (por ejemplo
    para resaltar quién ganó una mano en el marcador)."""
    total_pasos = repeticiones * 2
    paso_actual = [0]

    def tick():
        color = color_a if paso_actual[0] % 2 == 0 else color_b
        try:
            widget.configure(**{atributo: color})
        except tk.TclError:
            return
        paso_actual[0] += 1
        if paso_actual[0] < total_pasos:
            widget.after(duracion_ms, tick)
        else:
            try:
                widget.configure(**{atributo: color_a})
            except tk.TclError:
                pass
            if al_terminar:
                al_terminar()

    tick()
