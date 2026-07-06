"""
Tablero de juego del Chinchón, con exactamente el mismo look que el
resto de la app (mismos colores, marcos y tipografía que el menú
principal y el Truco) y el mismo historial de acciones a la izquierda.
"""

import tkinter as tk
from tkinter import ttk

from . import tema
from .widgets import BotonModerno, CartaBoton, crear_panel_con_sombra, etiqueta, mostrar_info

ANCHO_HISTORIAL = 300


class PantallaChinchon(tk.Frame):
    def __init__(self, parent, chinchon, imagenes, on_volver_menu, on_fin_partida):
        super().__init__(parent, bg=tema.COLOR_FONDO)
        self.chinchon = chinchon
        self.imagenes = imagenes
        self._on_volver_menu = on_volver_menu
        self._on_fin_partida = on_fin_partida

        self._armar_layout()
        self._nueva_mano()

    # ==================================================================
    def _armar_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=ANCHO_HISTORIAL)
        self.grid_columnconfigure(1, weight=1)

        self._armar_historial()

        contenido = tk.Frame(self, bg=tema.COLOR_FONDO)
        contenido.grid(row=0, column=1, sticky="nsew", padx=(9, 18), pady=18)
        self._contenido = contenido

        encabezado = tk.Frame(contenido, bg=tema.COLOR_FONDO)
        encabezado.pack(fill="x", pady=(0, 10))
        etiqueta(encabezado, "Chinchón", fuente=tema.FUENTE_TITULO_CHICO,
                 fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO).pack(side="left")
        BotonModerno(
            encabezado, "⟵ Menú", comando=self._on_volver_menu,
            ancho=110, alto=36, color_fondo_parent=tema.COLOR_FONDO,
        ).pack(side="right")

        self.lbl_marcador = etiqueta(contenido, "", fuente=tema.FUENTE_MARCADOR,
                                      fg=tema.COLOR_PANEL, bg=tema.COLOR_FONDO)
        self.lbl_marcador.pack(pady=(0, 8))

        cont_cpu, panel_cpu = crear_panel_con_sombra(contenido)
        cont_cpu.pack(fill="x", pady=6)
        self.lbl_titulo_cpu = etiqueta(
            panel_cpu, "Cartas de la CPU", fuente=tema.FUENTE_TEXTO_NEGRITA,
            fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL,
        )
        self.lbl_titulo_cpu.pack(pady=(8, 2))
        self.marco_cpu_interior = tk.Frame(panel_cpu, bg=tema.COLOR_PANEL)
        self.marco_cpu_interior.pack(padx=10, pady=(0, 10))

        cont_mesa, panel_mesa = crear_panel_con_sombra(contenido)
        cont_mesa.pack(fill="x", pady=6)
        etiqueta(panel_mesa, "Mesa de juego", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_TEXTO_SUAVE, bg=tema.COLOR_PANEL).pack(pady=(8, 2))
        fila_mesa = tk.Frame(panel_mesa, bg=tema.COLOR_PANEL)
        fila_mesa.pack(pady=(4, 14))

        self.lbl_mazo = tk.Label(
            fila_mesa, text="Mazo: --", font=tema.FUENTE_TEXTO_NEGRITA,
            bg=tema.COLOR_PANEL_CLARO, fg=tema.COLOR_TEXTO, padx=14, pady=10,
            bd=0, highlightthickness=0,
        )
        self.lbl_mazo.pack(side="left", padx=20)

        self.btn_pozo = tk.Button(
            fila_mesa, text="Pozo: --", width=16, height=3, font=tema.FUENTE_TEXTO_NEGRITA,
            bg=tema.COLOR_PANEL_CLARO, fg=tema.COLOR_TEXTO, relief="flat", bd=0,
            highlightthickness=0, command=self._robar_pozo, cursor="hand2",
        )
        self.btn_pozo.pack(side="left", padx=20)

        cont_acciones, panel_acciones = crear_panel_con_sombra(contenido)
        cont_acciones.pack(fill="x", pady=6)
        self.marco_acciones = tk.Frame(panel_acciones, bg=tema.COLOR_PANEL)
        self.marco_acciones.pack(pady=12)

        cont_mano, panel_mano = crear_panel_con_sombra(contenido)
        cont_mano.pack(fill="x", pady=6)
        etiqueta(panel_mano, "Tu mano (tocá una carta para descartarla)",
                 fuente=tema.FUENTE_TEXTO_NEGRITA, fg=tema.COLOR_TEXTO_SUAVE,
                 bg=tema.COLOR_PANEL).pack(pady=(8, 2))
        self.marco_mano = tk.Frame(panel_mano, bg=tema.COLOR_PANEL)
        self.marco_mano.pack(pady=(0, 12))

    def _armar_historial(self):
        contenedor, panel = crear_panel_con_sombra(self)
        contenedor.grid(row=0, column=0, sticky="nsew", padx=(18, 9), pady=18)
        etiqueta(panel, "Historial de la partida", fuente=tema.FUENTE_TEXTO_NEGRITA,
                 fg=tema.COLOR_ACENTO, bg=tema.COLOR_PANEL).pack(pady=(12, 6))

        marco = tk.Frame(panel, bg=tema.COLOR_PANEL)
        marco.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self.texto_log = tk.Text(
            marco, bg=tema.COLOR_PANEL, fg=tema.COLOR_TEXTO,
            font=tema.FUENTE_LOG, state="disabled", wrap="word", bd=0, highlightthickness=0,
        )
        scroll = ttk.Scrollbar(marco, command=self.texto_log.yview, style="Vertical.TScrollbar")
        self.texto_log.configure(yscrollcommand=scroll.set)
        self.texto_log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ==================================================================
    def _log(self, mensajes):
        if not mensajes:
            return
        if isinstance(mensajes, str):
            mensajes = [mensajes]
        self.texto_log.configure(state="normal")
        for m in mensajes:
            self.texto_log.insert("end", f"•  {m}\n")
        self.texto_log.see("end")
        self.texto_log.configure(state="disabled")

    def _actualizar_marcador(self):
        j1, j2 = self.chinchon.j1, self.chinchon.j2
        self.lbl_marcador.configure(
            text=f"{j1}: {self.chinchon.puntos[j1]} pts    |    {j2}: {self.chinchon.puntos[j2]} pts"
                 f"   (gana quien tenga menos al llegar a {self.chinchon.PUNTOS_DERROTA})"
        )

    def _nueva_mano(self):
        estado = self.chinchon.iniciar_mano()
        self._actualizar_marcador()
        self._log("──── Nueva mano: se repartieron 7 cartas ────")
        self._refrescar_cpu(revelar=False)
        self._refrescar_mesa(estado["cartas_restantes"])
        self._refrescar_mano()
        self._refrescar_acciones()

    def _refrescar_cpu(self, revelar=False):
        """Dibuja las cartas de la CPU arriba del tablero.

        Por defecto quedan boca abajo (dorso), como corresponde en el
        Chinchón mientras la mano está en juego. Cuando la CPU corta la
        ronda, se revelan boca arriba para que el jugador pueda
        comprobar la mano y las combinaciones con las que cerró; quedan
        así hasta que arranca la mano siguiente."""
        for w in self.marco_cpu_interior.winfo_children():
            w.destroy()

        if revelar:
            self.lbl_titulo_cpu.configure(text="Cartas de la CPU  —  reveladas al cerrar la mano")
            cartas = sorted(self.chinchon.mano_j2, key=lambda c: (c.palo, c.valor))
            for carta in cartas:
                img = self.imagenes.obtener(carta, 66, 99)
                tk.Label(self.marco_cpu_interior, image=img, bg=tema.COLOR_PANEL,
                         bd=0, highlightthickness=0).pack(side="left", padx=6, pady=6)
        else:
            self.lbl_titulo_cpu.configure(text="Cartas de la CPU")
            for _ in range(len(self.chinchon.mano_j2)):
                img = self.imagenes.obtener(None, 66, 99)
                tk.Label(self.marco_cpu_interior, image=img, bg=tema.COLOR_PANEL,
                         bd=0, highlightthickness=0).pack(side="left", padx=6, pady=6)

    def _refrescar_mesa(self, cartas_restantes):
        img_dorso = self.imagenes.obtener(None, 80, 120)
        self.lbl_mazo.configure(image=img_dorso, text=f"Mazo\n({cartas_restantes})",
                                 compound="top", font=tema.FUENTE_TEXTO_NEGRITA)
        self.lbl_mazo.image = img_dorso

        carta_pozo = self.chinchon.pozo.peek() if not self.chinchon.pozo.is_empty() else None
        if carta_pozo is not None:
            img_pozo = self.imagenes.obtener(carta_pozo, 80, 120)
            self.btn_pozo.configure(image=img_pozo, text="", width=80, height=120)
            self.btn_pozo.image = img_pozo
        else:
            self.btn_pozo.configure(text="Pozo:\nvacío", image="", width=16, height=3)

    def _refrescar_mano(self):
        for w in self.marco_mano.winfo_children():
            w.destroy()
        puede_descartar = self.chinchon.fase == "esperando_descarte"
        for i, carta in enumerate(self.chinchon.mano_j1):
            img = self.imagenes.obtener(carta, 78, 118)
            boton = CartaBoton(
                self.marco_mano, img,
                comando=(lambda idx=i: self._descartar(idx)) if puede_descartar else None,
                bg=tema.COLOR_PANEL, habilitado=puede_descartar,
            )
            boton.pack(side="left", padx=5, pady=4)

    def _refrescar_acciones(self):
        for w in self.marco_acciones.winfo_children():
            w.destroy()
        fase = self.chinchon.fase

        if fase == "esperando_robo":
            etiqueta(self.marco_acciones, "Es tu turno: robá una carta.",
                     fuente=tema.FUENTE_TEXTO_ITALICA, bg=tema.COLOR_PANEL).pack(side="left", padx=8)
            BotonModerno(self.marco_acciones, "Robar del mazo", comando=self._robar_mazo,
                         ancho=180, alto=40, color_fondo_parent=tema.COLOR_PANEL).pack(side="left", padx=6)
            BotonModerno(self.marco_acciones, "Robar del pozo", comando=self._robar_pozo,
                         ancho=180, alto=40, color_fondo_parent=tema.COLOR_PANEL).pack(side="left", padx=6)
            self.btn_pozo.configure(state="normal", cursor="hand2")

        elif fase == "esperando_descarte":
            etiqueta(self.marco_acciones, "Tocá una carta para descartar, o cerrá la mano.",
                     fuente=tema.FUENTE_TEXTO_ITALICA, bg=tema.COLOR_PANEL).pack(side="left", padx=8)
            BotonModerno(self.marco_acciones, "Cerrar mano", comando=self._cerrar_mano,
                         ancho=180, alto=40, color_normal=tema.COLOR_EXITO,
                         color_hover=tema.COLOR_EXITO_HOVER, color_texto=tema.COLOR_ACENTO_TEXTO,
                         color_fondo_parent=tema.COLOR_PANEL).pack(side="left", padx=6)
            self.btn_pozo.configure(state="disabled", cursor="arrow")

        elif fase == "fin_mano":
            if self.chinchon.terminado:
                ganador = self.chinchon.j1 if self.chinchon.puntos[self.chinchon.j1] < self.chinchon.puntos[self.chinchon.j2] else self.chinchon.j2
                detalle = (
                    f"{self.chinchon.j1}: {self.chinchon.puntos[self.chinchon.j1]} pts   |   "
                    f"{self.chinchon.j2}: {self.chinchon.puntos[self.chinchon.j2]} pts"
                )
                self.after(600, lambda: self._on_fin_partida(ganador, detalle))
            else:
                BotonModerno(self.marco_acciones, "Siguiente mano ▶", comando=self._nueva_mano,
                             ancho=220, alto=42, color_fondo_parent=tema.COLOR_PANEL).pack()

    def _refrescar_todo(self):
        self._refrescar_cpu(revelar=False)
        self._refrescar_mesa(self.chinchon.mazo.cantidad_restante())
        self._refrescar_mano()
        self._refrescar_acciones()
        self._actualizar_marcador()

    # ------------------------------------------------------------------
    def _robar_mazo(self):
        r = self.chinchon.robar_del_mazo()
        if "error" in r:
            mostrar_info(self, "Chinchón", r["error"])
            return
        self._log(f"Robaste {r['carta']} del mazo.")
        self._refrescar_todo()

    def _robar_pozo(self):
        if self.chinchon.fase != "esperando_robo":
            return
        r = self.chinchon.robar_del_pozo()
        if "error" in r:
            mostrar_info(self, "Chinchón", r["error"])
            return
        self._log(f"Robaste {r['carta']} del pozo.")
        self._refrescar_todo()

    def _cerrar_mano(self):
        r = self.chinchon.cerrar_mano()
        if "error" in r:
            mostrar_info(self, "Chinchón", r["error"])
            return
        self._mostrar_resultado_mano(r)

    def _descartar(self, indice):
        r = self.chinchon.descartar(indice)
        self._log(r["mensajes"])
        if r.get("cpu", {}).get("mensajes"):
            self._log(r["cpu"]["mensajes"])
        if r.get("fin_mano"):
            self._mostrar_resultado_mano(r["fin_mano"])
        else:
            self._refrescar_todo()

    def _mostrar_resultado_mano(self, resultado):
        self._log(resultado.get("mensajes", []))

        cerro_la_cpu = resultado.get("cerrador") == self.chinchon.j2
        if cerro_la_cpu:
            cartas_cpu = ", ".join(str(c) for c in self.chinchon.mano_j2)
            self._log([f"{self.chinchon.j2} reveló su mano al cerrar: {cartas_cpu}."])
        self._refrescar_cpu(revelar=cerro_la_cpu)

        self._log([
            f"Cerró: {resultado['cerrador']}  →  Puntos de la mano: "
            f"{self.chinchon.j1}: {resultado['puntos_mano_j1']}  |  "
            f"{self.chinchon.j2}: {resultado['puntos_mano_j2']}",
            f"Puntaje total: {self.chinchon.j1}: {resultado['puntos_totales'][self.chinchon.j1]}  |  "
            f"{self.chinchon.j2}: {resultado['puntos_totales'][self.chinchon.j2]}",
        ])
        self._actualizar_marcador()
        self._refrescar_mano()
        self._refrescar_acciones()
