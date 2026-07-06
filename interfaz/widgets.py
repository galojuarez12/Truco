"""
Widgets reutilizables con look moderno, construidos únicamente con
Tkinter puro (Canvas/Frame/Button) para no depender de librerías extra
como ttkbootstrap o CustomTkinter que el usuario debería instalar aparte
(ver la consigna de compatibilidad: nada de librerías innecesarias).

Los "bordes redondeados" se logran dibujando a mano sobre un Canvas, y
los paneles usan un marco parejo de color celeste suave (ver
`crear_panel_con_sombra`) en vez de una sombra genérica; el hover /
efecto de presión de los botones se logra con binds de mouse
(<Enter>/<Leave>/<ButtonPress>/<ButtonRelease>) cambiando sólo el
COLOR, nunca el tamaño, para no generar ningún artefacto visual.
"""

import tkinter as tk

from . import tema


def _puntos_rect_redondeado(x1, y1, x2, y2, radio):
    radio = min(radio, (x2 - x1) / 2, (y2 - y1) / 2)
    return [
        x1 + radio, y1,
        x2 - radio, y1,
        x2, y1,
        x2, y1 + radio,
        x2, y2 - radio,
        x2, y2,
        x2 - radio, y2,
        x1 + radio, y2,
        x1, y2,
        x1, y2 - radio,
        x1, y1 + radio,
        x1, y1,
    ]


class BotonModerno(tk.Canvas):
    """Botón blanco con esquinas redondeadas, hover, efecto de presión y
    cursor de mano, dibujado íntegramente sobre un Canvas."""

    def __init__(self, parent, texto, comando=None, ancho=220, alto=48,
                 color_normal=None, color_hover=None, color_texto=None,
                 fuente=None, radio=16, habilitado=True, color_fondo_parent=None):
        color_fondo_parent = color_fondo_parent or tema.COLOR_FONDO
        super().__init__(parent, width=ancho, height=alto,
                          bg=color_fondo_parent, highlightthickness=0, bd=0)
        self.comando = comando
        self.ancho, self.alto, self.radio = ancho, alto, radio
        self.color_normal = color_normal or tema.COLOR_PANEL
        self.color_hover = color_hover or tema.COLOR_PANEL_CLARO
        self.color_texto = color_texto or tema.COLOR_ACENTO
        self.fuente = fuente or tema.FUENTE_BOTON
        self.texto = texto
        self._habilitado = habilitado
        self._presionado = False

        self._forma = self.create_polygon(
            _puntos_rect_redondeado(2, 2, ancho - 2, alto - 2, radio),
            smooth=True, fill=self._color_actual(), outline=tema.COLOR_BORDE, width=1,
        )
        self._etiqueta = self.create_text(
            ancho / 2, alto / 2, text=texto, fill=self._color_texto_actual(),
            font=self.fuente,
        )

        for evento, manejador in (
            ("<Enter>", self._on_enter), ("<Leave>", self._on_leave),
            ("<ButtonPress-1>", self._on_press), ("<ButtonRelease-1>", self._on_release),
        ):
            self.bind(evento, manejador)

        self._actualizar_apariencia()

    # -- estado --------------------------------------------------------
    def set_habilitado(self, valor):
        self._habilitado = valor
        self._actualizar_apariencia()

    def set_texto(self, texto):
        self.texto = texto
        self.itemconfigure(self._etiqueta, text=texto)

    # -- colores segun estado -------------------------------------------
    def _color_actual(self):
        if not self._habilitado:
            return tema.COLOR_DESHABILITADO
        if self._presionado:
            return self.color_hover
        return self.color_normal

    def _color_texto_actual(self):
        return tema.COLOR_DESHABILITADO_TEXTO if not self._habilitado else self.color_texto

    def _actualizar_apariencia(self):
        self.itemconfigure(self._forma, fill=self._color_actual())
        self.itemconfigure(self._etiqueta, fill=self._color_texto_actual())
        self.configure(cursor="hand2" if self._habilitado else "arrow")

    # -- eventos ---------------------------------------------------------
    def _on_enter(self, _evento):
        if self._habilitado:
            self.itemconfigure(self._forma, fill=self.color_hover)

    def _on_leave(self, _evento):
        self._presionado = False
        self._actualizar_apariencia()

    def _on_press(self, _evento):
        if self._habilitado:
            self._presionado = True
            self.itemconfigure(self._forma, fill=self.color_hover)
            self.move(self._etiqueta, 0, 1)

    def _on_release(self, evento):
        if self._habilitado:
            self.move(self._etiqueta, 0, -1)
            self._presionado = False
            self._actualizar_apariencia()
            dentro = 0 <= evento.x <= self.ancho and 0 <= evento.y <= self.alto
            if dentro and self.comando:
                self.comando()


class BotonAccion(BotonModerno):
    """Variante chica pensada para la grilla de acciones del Truco
    (Truco / Envido / Quiero / etc.), con tamaño uniforme."""

    def __init__(self, parent, texto, comando=None, habilitado=True, **kwargs):
        kwargs.setdefault("ancho", 168)
        kwargs.setdefault("alto", 38)
        kwargs.setdefault("fuente", tema.FUENTE_BOTON_CHICA)
        kwargs.setdefault("radio", 10)
        super().__init__(parent, texto, comando=comando, habilitado=habilitado, **kwargs)


def crear_panel_con_sombra(parent, bg=None, bg_borde=None, grosor=2, **kwargs):
    """Panel blanco con un marco parejo celeste claro alrededor (frame
    exterior + panel interior), para que se note el contorno del panel
    sobre el tablero celeste sin necesidad de sombras. Devuelve
    (contenedor, panel_interior); hay que ubicar 'contenedor' en el
    layout del padre y poner los hijos dentro de 'panel_interior'."""
    bg = bg or tema.COLOR_PANEL
    bg_borde = bg_borde or tema.COLOR_BORDE
    contenedor = tk.Frame(parent, bg=bg_borde)
    panel = tk.Frame(contenedor, bg=bg, **kwargs)
    panel.pack(padx=grosor, pady=grosor, fill="both", expand=True)
    return contenedor, panel


class CartaBoton(tk.Button):
    """Botón que muestra la imagen de una carta, sin ningún efecto
    visual agregado (sin sombras, sin cambios de tamaño, sin
    transparencias): siempre la MISMA imagen, nítida y completa. El
    único indicio de que es interactiva es el cursor de mano."""

    def __init__(self, parent, imagen, comando=None, bg=None, habilitado=True, **kwargs):
        bg = bg or tema.COLOR_PANEL
        estado = "normal" if habilitado else "disabled"
        super().__init__(
            parent, image=imagen, bd=0, highlightthickness=0,
            bg=bg, activebackground=bg, relief="flat", state=estado,
            command=comando, takefocus=0, **kwargs,
        )
        self.image = imagen
        if habilitado:
            self.configure(cursor="hand2")


def etiqueta(parent, texto, fuente=None, fg=None, bg=None, **kwargs):
    """Atajo para no repetir bg/fg/fuente en cada tk.Label suelto."""
    return tk.Label(
        parent, text=texto, font=fuente or tema.FUENTE_TEXTO,
        fg=fg or tema.COLOR_TEXTO, bg=bg or tema.COLOR_FONDO, **kwargs,
    )


class _DialogoBase(tk.Toplevel):
    """Base para los diálogos propios de la app (confirmar / avisar),
    con la MISMA identidad visual y tipografía que el resto de las
    pantallas — en vez de los cuadros nativos de `tkinter.messagebox`,
    que usan la fuente por defecto del sistema operativo."""

    def __init__(self, parent, titulo, mensaje):
        super().__init__(parent)
        self.title(titulo)
        self.configure(bg=tema.COLOR_PANEL)
        self.resizable(False, False)
        raiz = parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
        self.transient(raiz)
        self.resultado = None

        marco = tk.Frame(self, bg=tema.COLOR_PANEL, padx=28, pady=22,
                          highlightthickness=2, highlightbackground=tema.COLOR_BORDE)
        marco.pack()
        etiqueta(
            marco, mensaje, fuente=tema.FUENTE_TEXTO, fg=tema.COLOR_TEXTO,
            bg=tema.COLOR_PANEL, justify="center", wraplength=340,
        ).pack(pady=(0, 20))
        self.marco_botones = tk.Frame(marco, bg=tema.COLOR_PANEL)
        self.marco_botones.pack()

        try:
            self.grab_set()
        except tk.TclError:
            pass

    def _cerrar(self, valor):
        self.resultado = valor
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


def confirmar(parent, titulo, mensaje, texto_si="Sí", texto_no="No"):
    """Reemplaza a `tkinter.messagebox.askyesno`, con la identidad
    visual unificada de la app en vez del diálogo nativo del sistema."""
    dialogo = _DialogoBase(parent, titulo, mensaje)
    BotonModerno(
        dialogo.marco_botones, texto_si, comando=lambda: dialogo._cerrar(True),
        ancho=140, alto=42, color_normal=tema.COLOR_ACENTO, color_hover=tema.COLOR_ACENTO_HOVER,
        color_texto=tema.COLOR_ACENTO_TEXTO, color_fondo_parent=tema.COLOR_PANEL,
    ).pack(side="left", padx=8)
    BotonModerno(
        dialogo.marco_botones, texto_no, comando=lambda: dialogo._cerrar(False),
        ancho=140, alto=42, color_fondo_parent=tema.COLOR_PANEL,
    ).pack(side="left", padx=8)
    dialogo.wait_window()
    return bool(dialogo.resultado)


def mostrar_info(parent, titulo, mensaje):
    """Reemplaza a `tkinter.messagebox.showinfo`, con la misma identidad
    visual unificada de la app."""
    dialogo = _DialogoBase(parent, titulo, mensaje)
    BotonModerno(
        dialogo.marco_botones, "Aceptar", comando=lambda: dialogo._cerrar(True),
        ancho=150, alto=42, color_normal=tema.COLOR_ACENTO, color_hover=tema.COLOR_ACENTO_HOVER,
        color_texto=tema.COLOR_ACENTO_TEXTO, color_fondo_parent=tema.COLOR_PANEL,
    ).pack()
    dialogo.wait_window()
