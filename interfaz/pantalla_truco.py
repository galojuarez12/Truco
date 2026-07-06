"""
Tablero de juego del Truco.

Distribución (igual a la especificación pedida: franjas de ancho
completo arriba/abajo, y en el medio tres columnas):

    ┌──────────────────────────────────────────────────────────┐
    │                     Cartas de la CPU                     │
    ├───────────┬────────────────────────────────┬─────────────┤
    │           │                                │             │
    │ Historial │            Tablero             │  Acciones   │
    │  (~10%    │        (cartas jugadas,        │             │
    │  del      │    se ven las de los dos)       │             │
    │  ancho)   │                                │             │
    ├───────────┴────────────────────────────────┴─────────────┤
    │                       Mis cartas                          │
    └──────────────────────────────────────────────────────────┘

El marcador (puntaje/ronda/partidas) va como una franja fina arriba,
sin panel propio, para no competir con las cuatro zonas de la
especificación.

Toda la lógica de reglas vive en `juegos.Truco`; esta clase sólo dibuja
y traduce clics en llamadas a sus métodos. Las únicas decisiones "extra"
que toma esta capa son puramente de presentación (qué botón mostrar
habilitado, cuánto tardar en revelar la carta de la CPU, qué texto
mostrar mientras tanto), nunca reglas del juego.
"""

import tkinter as tk
from tkinter import ttk

from . import tema
from .widgets import BotonModerno, BotonAccion, CartaBoton, crear_panel_con_sombra, etiqueta, confirmar
from .animaciones import pulso_color

# Reparto de ancho de la fila media (Historial | Tablero | Acciones),
# como PARTES relativas (no píxeles fijos) para que se mantenga la
# proporción al redimensionar la ventana: 1 de cada 10 partes para el
# historial (10% como máximo), 5 para el tablero y 4 para acciones.
_PARTES_HISTORIAL = 1
_PARTES_TABLERO = 5
_PARTES_ACCIONES = 4

# Fuente reducida sólo para el historial angosto del Truco (no afecta
# el historial del Chinchón, que sigue usando tema.FUENTE_LOG).
_FUENTE_LOG_HISTORIAL = ("Georgia", 9)

# id de acción -> (texto del botón, color)
_BOTONES_ACCION = [
    ("truco", "¡Truco!", tema.COLOR_ACENTO),
    ("retruco", "¡Re Truco!", tema.COLOR_ACENTO),
    ("vale_cuatro", "¡Vale Cuatro!", tema.COLOR_ACENTO),
    ("envido", "Envido", tema.COLOR_ACENTO),
    ("envido_envido", "Envido Envido", tema.COLOR_ACENTO),
    ("real_envido", "Real Envido", tema.COLOR_ACENTO),
    ("falta_envido", "Falta Envido", tema.COLOR_ACENTO),
    ("quiero", "Quiero", tema.COLOR_EXITO),
    ("no_quiero", "No Quiero", tema.COLOR_PELIGRO),
    ("irse_al_mazo", "Ir al Mazo", tema.COLOR_PELIGRO),
]


class PantallaTruco(tk.Frame):
    def __init__(self, parent, truco, imagenes, on_volver_menu, on_fin_partida):
        super().__init__(parent, bg=tema.COLOR_FONDO)
        self.truco = truco
        self.imagenes = imagenes
        self._on_volver_menu = on_volver_menu
        self._on_fin_partida = on_fin_partida
        self._bloqueado = False
        self.botones_accion = {}

        self._armar_layout()
        self._empezar_mano()

    # ==================================================================
    # ARMADO DE LA PANTALLA (se construye una sola vez)
    # ==================================================================
    def _armar_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # encabezado
        self.grid_rowconfigure(1, weight=0)  # marcador
        self.grid_rowconfigure(2, weight=0)  # Cartas de la CPU
        self.grid_rowconfigure(3, weight=1)  # Historial | Tablero | Acciones (se expande)
        self.grid_rowconfigure(4, weight=0)  # Mis cartas

        self._armar_encabezado()
        self._armar_marcador()
        self._armar_panel_cpu()
        self._armar_fila_media()
        self._armar_panel_mano()

    def _armar_encabezado(self):
        encabezado = tk.Frame(self, bg=tema.COLOR_FONDO)
        encabezado.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 4))
        etiqueta(
            encabezado, "Truco Argentino (sin Flor)",
            fuente=tema.FUENTE_TITULO_CHICO, fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO,
        ).pack(side="left")
        BotonModerno(
            encabezado, "⟵ Menú", comando=self._on_volver_menu,
            ancho=110, alto=36, color_fondo_parent=tema.COLOR_FONDO,
        ).pack(side="right")

    def _armar_marcador(self):
        """Franja fina con el puntaje, sin panel propio (la especificación
        no pide una zona aparte para esto), en línea con lo que ya hace
        el marcador de Chinchón."""
        fila = tk.Frame(self, bg=tema.COLOR_FONDO)
        fila.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))

        self.lbl_puntaje_j1 = etiqueta(fila, "", fuente=tema.FUENTE_MARCADOR,
                                        fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO)
        self.lbl_puntaje_j1.pack(side="left", padx=(0, 18))
        self.lbl_puntaje_j2 = etiqueta(fila, "", fuente=tema.FUENTE_MARCADOR,
                                        fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO)
        self.lbl_puntaje_j2.pack(side="left", padx=(0, 18))
        self.lbl_ronda = etiqueta(fila, "", fuente=tema.FUENTE_TEXTO_ITALICA,
                                   fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO)
        self.lbl_ronda.pack(side="left", padx=(0, 18))
        self.lbl_partidas = etiqueta(fila, "", fuente=tema.FUENTE_TEXTO,
                                      fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO)
        self.lbl_partidas.pack(side="left")

    def _armar_panel_cpu(self):
        contenedor, panel = crear_panel_con_sombra(self)
        contenedor.grid(row=2, column=0, sticky="ew", padx=18, pady=6)
        etiqueta(panel, "Cartas de la CPU", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL).pack(pady=(8, 2))
        self.marco_cpu_interior = tk.Frame(panel, bg=tema.COLOR_PANEL, height=110)
        self.marco_cpu_interior.pack(fill="x", padx=10, pady=(0, 10))

    # -- fila media: Historial | Tablero | Acciones -----------------------
    def _armar_fila_media(self):
        fila_media = tk.Frame(self, bg=tema.COLOR_FONDO)
        fila_media.grid(row=3, column=0, sticky="nsew", padx=18, pady=6)
        fila_media.grid_rowconfigure(0, weight=1)
        fila_media.grid_columnconfigure(0, weight=_PARTES_HISTORIAL)
        fila_media.grid_columnconfigure(1, weight=_PARTES_TABLERO)
        fila_media.grid_columnconfigure(2, weight=_PARTES_ACCIONES)

        self._armar_historial(fila_media)
        self._armar_panel_mesa(fila_media)
        self._armar_panel_acciones(fila_media)

    def _armar_historial(self, parent):
        contenedor, panel = crear_panel_con_sombra(parent)
        contenedor.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        etiqueta(panel, "Historial", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_ACENTO, bg=tema.COLOR_PANEL).pack(pady=(10, 4))

        marco = tk.Frame(panel, bg=tema.COLOR_PANEL)
        marco.pack(fill="both", expand=True, padx=6, pady=(0, 10))
        self.texto_historial = tk.Text(
            marco, bg=tema.COLOR_PANEL, fg=tema.COLOR_TEXTO,
            font=_FUENTE_LOG_HISTORIAL, state="disabled", wrap="word", bd=0,
            highlightthickness=0,
        )
        scroll = ttk.Scrollbar(marco, command=self.texto_historial.yview,
                               style="Vertical.TScrollbar")
        self.texto_historial.configure(yscrollcommand=scroll.set)
        self.texto_historial.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _armar_panel_mesa(self, parent):
        contenedor, panel = crear_panel_con_sombra(parent)
        contenedor.grid(row=0, column=1, sticky="nsew", padx=9)
        etiqueta(panel, "Tablero", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL).pack(pady=(8, 2))
        self.marco_mesa_interior = tk.Frame(panel, bg=tema.COLOR_PANEL)
        self.marco_mesa_interior.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _armar_panel_acciones(self, parent):
        contenedor, panel = crear_panel_con_sombra(parent)
        contenedor.grid(row=0, column=2, sticky="nsew", padx=(9, 0))
        etiqueta(panel, "ACCIONES", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_ACENTO, bg=tema.COLOR_PANEL).pack(pady=(10, 6))

        grilla = tk.Frame(panel, bg=tema.COLOR_PANEL)
        grilla.pack(padx=8, pady=(0, 6))
        for indice, (id_accion, texto, color) in enumerate(_BOTONES_ACCION):
            fila_grilla, columna_grilla = divmod(indice, 2)
            boton = BotonAccion(
                grilla, texto, comando=lambda i=id_accion: self._click_accion(i),
                color_normal=color, color_texto=tema.COLOR_ACENTO_TEXTO,
                habilitado=False, color_fondo_parent=tema.COLOR_PANEL,
            )
            boton.grid(row=fila_grilla, column=columna_grilla, padx=4, pady=3)
            self.botones_accion[id_accion] = boton

        self.boton_siguiente_mano = BotonModerno(
            panel, "▶  Siguiente Mano", comando=self._click_siguiente_mano,
            ancho=352, alto=42, habilitado=False, color_fondo_parent=tema.COLOR_PANEL,
        )
        self.boton_siguiente_mano.pack(pady=(2, 12))

    def _armar_panel_mano(self):
        contenedor, panel = crear_panel_con_sombra(self)
        contenedor.grid(row=4, column=0, sticky="ew", padx=18, pady=(6, 18))
        etiqueta(panel, "Mis cartas", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL).pack(pady=(8, 2))
        self.marco_mano_interior = tk.Frame(panel, bg=tema.COLOR_PANEL)
        self.marco_mano_interior.pack(pady=(0, 12))


    # ==================================================================
    # FLUJO DE MANO
    # ==================================================================
    def _empezar_mano(self):
        """Primera mano de la partida: no hace falta la transición de
        'repartiendo cartas' (recién se entró a la pantalla), pero sí
        el reparto de a una carta por vez."""
        self.truco.iniciar_mano()
        self._actualizar_marcador()
        self._refrescar_cpu()
        self._refrescar_mesa()
        self._refrescar_mano(animar_entrada=True)
        self._refrescar_acciones()
        self._log(["──── Nueva mano ────"])

    def _iniciar_nueva_mano(self):
        self._bloqueado = True
        self._refrescar_acciones()
        for w in self.marco_mesa_interior.winfo_children():
            w.destroy()
        etiqueta(self.marco_mesa_interior, "Repartiendo cartas…",
                 fuente=tema.FUENTE_SUBTITULO, bg=tema.COLOR_PANEL).pack(expand=True)
        for w in self.marco_mano_interior.winfo_children():
            w.destroy()
        for w in self.marco_cpu_interior.winfo_children():
            w.destroy()
        self.after(500, self._revelar_mano_nueva)

    def _revelar_mano_nueva(self):
        self.truco.iniciar_mano()
        self._bloqueado = False
        self._actualizar_marcador()
        self._refrescar_cpu()
        self._refrescar_mesa()
        self._refrescar_mano(animar_entrada=True)
        self._refrescar_acciones()
        self._log(["──── Nueva mano ────"])

    # ==================================================================
    # RENDER: CARTAS DE LA CPU
    # ==================================================================
    def _refrescar_cpu(self):
        for w in self.marco_cpu_interior.winfo_children():
            w.destroy()
        for _ in self.truco.cartas_j2:
            img = self.imagenes.obtener(None, 66, 99)
            tk.Label(self.marco_cpu_interior, image=img, bg=tema.COLOR_PANEL,
                     bd=0, highlightthickness=0).pack(side="left", padx=6, pady=6)

    # ==================================================================
    # RENDER: MESA (las cartas jugadas quedan centradas y visibles hasta
    # que empieza la mano siguiente)
    # ==================================================================
    def _mensaje_fase(self, fase, info):
        if fase == "envido":
            if info["modo"] == "cantar":
                return "Fase de Envido\nElegí un canto o decí \"No Quiero\" para pasar."
            return "La CPU cantó algo de Envido.\n¿Qué hacés?"
        if fase == "truco":
            if info["modo"] == "cantar":
                return "Fase de Truco\n¿Cantás algo antes de jugar?"
            return "La CPU cantó Truco.\n¿Qué hacés?"
        return ""

    def _refrescar_mesa(self, ocultar_ultima_cpu=False, revelando_cpu=False):
        for w in self.marco_mesa_interior.winfo_children():
            w.destroy()

        fase = self.truco.fase
        if fase in ("envido", "truco"):
            info = self.truco.opciones_disponibles()
            etiqueta(
                self.marco_mesa_interior, self._mensaje_fase(fase, info),
                fuente=tema.FUENTE_SUBTITULO, bg=tema.COLOR_PANEL, justify="center",
            ).pack(expand=True)
            return

        if not self.truco.cartas_jugadas:
            texto = "Mano finalizada." if fase == "fin_mano" else "Elegí una carta de tu mano para empezar la ronda."
            etiqueta(self.marco_mesa_interior, texto, fuente=tema.FUENTE_SUBTITULO,
                     bg=tema.COLOR_PANEL).pack(expand=True)
            return

        # Fila centrada (pack la centra sola dentro del panel) con una
        # "columna" por cada ronda ya jugada en esta mano — quedan
        # visibles hasta que empiece la mano siguiente.
        fila = tk.Frame(self.marco_mesa_interior, bg=tema.COLOR_PANEL)
        fila.pack(expand=True)

        total = len(self.truco.cartas_jugadas)
        for i, (carta_j1, carta_j2) in enumerate(self.truco.cartas_jugadas):
            es_ultima = i == total - 1
            ocultar_cpu = ocultar_ultima_cpu and es_ultima
            duelo = self._crear_duelo(
                fila, carta_j1, None if ocultar_cpu else carta_j2,
                cpu_pensando=ocultar_cpu,
            )
            duelo.pack(side="left", padx=16)

    def _crear_duelo(self, parent, carta_j1, carta_j2, cpu_pensando=False):
        """Una 'columna' de la mesa para una ronda: la carta de la CPU
        arriba, la mía abajo — como en una mesa de Truco real. Sin
        bordes ni sombras: sólo la imagen de la carta, completa."""
        marco = tk.Frame(parent, bg=tema.COLOR_PANEL)

        etiqueta(
            marco, "CPU pensando…" if cpu_pensando else "Jugador CPU",
            fuente=tema.FUENTE_TEXTO_NEGRITA, fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL,
        ).pack()
        img_cpu = self.imagenes.obtener(carta_j2, 108, 162)
        lbl_cpu = tk.Label(marco, image=img_cpu, bg=tema.COLOR_PANEL, bd=0, highlightthickness=0)
        lbl_cpu.image = img_cpu
        lbl_cpu.pack(pady=(2, 12))

        img_jugador = self.imagenes.obtener(carta_j1, 108, 162)
        lbl_jugador = tk.Label(marco, image=img_jugador, bg=tema.COLOR_PANEL, bd=0, highlightthickness=0)
        lbl_jugador.image = img_jugador
        lbl_jugador.pack(pady=(12, 2))
        etiqueta(
            marco, "Jugador", fuente=tema.FUENTE_TEXTO_NEGRITA,
            fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL,
        ).pack()
        return marco

    # ==================================================================
    # RENDER: MI MANO
    # ==================================================================
    def _refrescar_mano(self, animar_entrada=False):
        for w in self.marco_mano_interior.winfo_children():
            w.destroy()
        habilitado = self.truco.fase == "rondas" and not self._bloqueado

        cartas = list(self.truco.cartas_j1)
        if not animar_entrada:
            for idx, carta in enumerate(cartas):
                self._crear_boton_mano(carta, idx, habilitado)
            return

        # Reparto: las cartas van apareciendo de a una, en orden, sin
        # ningún efecto de transparencia — sólo una pequeña demora entre
        # una y la siguiente.
        for idx, carta in enumerate(cartas):
            self.after(idx * 150, lambda c=carta, i=idx: self._crear_boton_mano(c, i, False))
        self.after(150 * max(1, len(cartas)) + 100, self._refrescar_mano)

    def _crear_boton_mano(self, carta, idx, habilitado):
        img = self.imagenes.obtener(carta, 108, 162)
        boton = CartaBoton(
            self.marco_mano_interior, img,
            comando=(lambda i=idx: self._jugar_carta(i)) if habilitado else None,
            bg=tema.COLOR_PANEL, habilitado=habilitado,
        )
        boton.pack(side="left", padx=10, pady=6)

    # ==================================================================
    # ACCIONES (Truco / Envido / Quiero / etc.)
    # ==================================================================
    def _estado_botones_accion(self):
        estados = {id_accion: False for id_accion, *_ in _BOTONES_ACCION}
        fase = self.truco.fase
        if self._bloqueado or fase not in ("envido", "truco", "rondas"):
            return estados
        if fase == "rondas":
            estados["irse_al_mazo"] = True
            return estados

        info = self.truco.opciones_disponibles()
        modo, opciones = info["modo"], info["opciones"]
        grupo = ("envido", "envido_envido", "real_envido", "falta_envido") if fase == "envido" \
            else ("truco", "retruco", "vale_cuatro")
        for tipo in grupo:
            if tipo in opciones:
                estados[tipo] = True
        if modo == "responder":
            estados["quiero"] = "quiero" in opciones
        estados["no_quiero"] = ("no_quiero" in opciones) or (modo == "cantar" and "pasar" in opciones)
        return estados

    def _refrescar_acciones(self):
        estados = self._estado_botones_accion()
        for id_accion, boton in self.botones_accion.items():
            boton.set_habilitado(estados.get(id_accion, False))
        puede_continuar = self.truco.fase == "fin_mano" and not self.truco.terminado and not self._bloqueado
        self.boton_siguiente_mano.set_habilitado(puede_continuar)

    def _click_accion(self, id_accion):
        if self._bloqueado:
            return
        info = self.truco.opciones_disponibles()
        fase, modo = self.truco.fase, info["modo"]

        if id_accion == "irse_al_mazo":
            if not confirmar(
                self, "Ir al mazo",
                f"¿Seguro que querés irte al mazo?\n"
                f"{self.truco.j2} se llevará {self.truco.puntos_truco_en_juego} punto(s).",
            ):
                return
            resultado = self.truco.irse_al_mazo()
        elif id_accion in ("envido", "envido_envido", "real_envido", "falta_envido"):
            resultado = self.truco.cantar_envido(id_accion) if modo == "cantar" else self.truco.responder_envido(id_accion)
        elif id_accion in ("truco", "retruco", "vale_cuatro"):
            resultado = self.truco.cantar_truco(id_accion) if modo == "cantar" else self.truco.responder_truco(id_accion)
        elif id_accion == "quiero":
            resultado = self.truco.responder_envido("quiero") if fase == "envido" else self.truco.responder_truco("quiero")
        elif id_accion == "no_quiero":
            if modo == "cantar":
                resultado = self.truco.cantar_envido("pasar") if fase == "envido" else self.truco.cantar_truco("pasar")
            else:
                resultado = self.truco.responder_envido("no_quiero") if fase == "envido" else self.truco.responder_truco("no_quiero")
        else:
            return

        self._despues_de_accion(resultado)

    def _despues_de_accion(self, resultado):
        self._log(resultado.get("mensajes", []))
        self._actualizar_marcador()
        if self.truco.fase == "fin_mano":
            self._mostrar_fin_mano(resultado)
        else:
            self._refrescar_mesa()
            self._refrescar_mano()
            self._refrescar_acciones()

    # ==================================================================
    # JUGAR UNA CARTA (con la pequeña espera "natural" de la CPU)
    # ==================================================================
    def _jugar_carta(self, indice):
        if self._bloqueado or self.truco.fase != "rondas":
            return
        self._bloqueado = True
        resultado = self.truco.jugar_carta(indice)
        self._refrescar_mano()
        self._refrescar_acciones()
        self._refrescar_mesa(ocultar_ultima_cpu=True)
        self.after(700, lambda: self._revelar_jugada_cpu(resultado))

    def _revelar_jugada_cpu(self, resultado):
        self._refrescar_mesa(revelando_cpu=True)
        mensajes = [f"Jugaste: {resultado['carta_j1']}  |  {self.truco.j2} jugó: {resultado['carta_j2']}"]
        mensajes += resultado.get("mensajes", [])
        self._log(mensajes)
        self._actualizar_marcador()
        if self.truco.fase == "fin_mano":
            self._mostrar_fin_mano(resultado)
        else:
            self._bloqueado = False
            self._refrescar_mano()
            self._refrescar_acciones()

    # ==================================================================
    # FIN DE MANO / FIN DE PARTIDA
    # ==================================================================
    def _mostrar_fin_mano(self, resultado):
        self._bloqueado = False
        self._refrescar_mesa()
        self._refrescar_acciones()

        ganador_mano = resultado.get("ganador_mano")
        if ganador_mano == self.truco.j1:
            pulso_color(self.lbl_puntaje_j1, tema.COLOR_ACENTO_HOVER, tema.COLOR_PANEL, repeticiones=3, duracion_ms=200)
        elif ganador_mano == self.truco.j2:
            pulso_color(self.lbl_puntaje_j2, tema.COLOR_ACENTO_HOVER, tema.COLOR_PANEL, repeticiones=3, duracion_ms=200)

        fin_partida = resultado.get("fin_partida")
        if fin_partida or self.truco.terminado:
            ganador = fin_partida or (
                self.truco.j1 if self.truco.puntos[self.truco.j1] >= self.truco.PUNTOS_VICTORIA else self.truco.j2
            )
            self.after(1300, lambda: self._ir_a_ganador(ganador))

    def _ir_a_ganador(self, ganador):
        detalle = (
            f"{self.truco.j1}: {self.truco.puntos[self.truco.j1]} pts   |   "
            f"{self.truco.j2}: {self.truco.puntos[self.truco.j2]} pts"
        )
        self._on_fin_partida(ganador, detalle)

    def _click_siguiente_mano(self):
        if self.truco.fase != "fin_mano" or self.truco.terminado or self._bloqueado:
            return
        self._iniciar_nueva_mano()

    # ==================================================================
    # UTILIDADES
    # ==================================================================
    def _actualizar_marcador(self):
        j1, j2 = self.truco.j1, self.truco.j2
        self.lbl_puntaje_j1.configure(text=f"{j1}: {self.truco.mostrar_tanteador(j1)}")
        self.lbl_puntaje_j2.configure(text=f"{j2}: {self.truco.mostrar_tanteador(j2)}")
        self.lbl_partidas.configure(
            text=f"Partidas ganadas — {j1}: {self.truco.partidas_ganadas[j1]}   "
                 f"{j2}: {self.truco.partidas_ganadas[j2]}"
        )
        self.lbl_ronda.configure(
            text=f"Ronda {self.truco.ronda_actual()} de 3" if self.truco.fase == "rondas" else ""
        )

    def _log(self, mensajes):
        if not mensajes:
            return
        if isinstance(mensajes, str):
            mensajes = [mensajes]
        self.texto_historial.configure(state="normal")
        for m in mensajes:
            self.texto_historial.insert("end", f"•  {m}\n")
        self.texto_historial.see("end")
        self.texto_historial.configure(state="disabled")
