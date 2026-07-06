"""
Gestor de imágenes de las cartas.

*** SOLUCIÓN AL BUG ORIGINAL ***
La versión anterior guardaba las cartas como archivos SVG con un nombre
"doble" (por ejemplo "10_oro.png.svg") y, al toparse con la extensión
".svg", intentaba convertirlas a PNG en tiempo de ejecución usando
ReportLab + rlPyCairo (o cairosvg). En Windows, ninguna de esas dos
librerías de conversión estaba instalada correctamente, así que la carga
fallaba siempre con el error:

    "cannot import desired renderPM backend rlPyCairo"

Ahora el problema se resuelve de raíz en dos pasos:

1. Los 49 SVG se convirtieron UNA sola vez (fuera del programa) a archivos
   PNG reales, guardados en 'imagenes/' con nombre simple
   (ej. "10_oro.png"). Los SVG originales quedaron archivados en
   'recursos_originales_svg/' por si en el futuro hace falta regenerarlos
   en mayor resolución; el juego ya no los toca para nada.
2. Este módulo SOLO usa Pillow (`Image.open`) para abrir esos PNG. No hay
   ninguna dependencia de ReportLab, rlPyCairo, cairosvg ni conversión de
   SVG en tiempo de ejecución.

Si en el futuro faltara algún PNG (o el archivo estuviera dañado), el
programa NO se rompe: se genera al vuelo una carta "genérica" de
respaldo dibujada con Pillow, para que la partida pueda seguir jugándose.
"""

import os

from PIL import Image, ImageTk, ImageDraw, ImageFont

from .tema import COLORES_PALO

EXTENSIONES_VALIDAS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


class GestorImagenes:
    """
    Indexa la carpeta de imágenes una única vez (clave normalizada ->
    nombre real de archivo) y después sirve PhotoImage ya redimensionados,
    con caché para no releer/redimensionar de más.
    """

    def __init__(self, carpeta="imagenes"):
        self.carpeta = carpeta
        self._cache = {}
        self._indice = self._construir_indice()

    # ------------------------------------------------------------------
    def _construir_indice(self):
        indice = {}
        if os.path.isdir(self.carpeta):
            for archivo in sorted(os.listdir(self.carpeta)):
                ruta = os.path.join(self.carpeta, archivo)
                if os.path.isfile(ruta) and archivo.lower().endswith(EXTENSIONES_VALIDAS):
                    indice[self._normalizar(archivo)] = archivo
        return indice

    @staticmethod
    def _normalizar(archivo):
        base = archivo.lower()
        for ext in EXTENSIONES_VALIDAS:
            if base.endswith(ext):
                return base[: -len(ext)]
        return base

    @staticmethod
    def _clave_de_carta(carta):
        if carta is None:
            return "dorso"
        if carta.es_comodin():
            return "comodin"
        return f"{carta.valor}_{carta.palo}"

    # ------------------------------------------------------------------
    def obtener(self, carta, ancho=110, alto=165):
        """Devuelve un ImageTk.PhotoImage de 'ancho'x'alto' para la carta
        pedida (o el dorso si carta es None). Nunca lanza una excepción:
        ante cualquier problema, devuelve una carta genérica de respaldo."""
        cache_key = ("foto", self._clave_de_carta(carta), ancho, alto)
        if cache_key in self._cache:
            return self._cache[cache_key]
        imagen = self.obtener_pil(carta, ancho, alto)
        foto = ImageTk.PhotoImage(imagen)
        self._cache[cache_key] = foto
        return foto

    def obtener_pil(self, carta, ancho=110, alto=165):
        """Igual que `obtener`, pero devuelve el objeto Pillow (Image) en
        lugar de un PhotoImage de Tkinter. Se usa para las animaciones de
        fundido, que necesitan mezclar la imagen a distintos niveles de
        opacidad antes de convertirla a PhotoImage."""
        clave = self._clave_de_carta(carta)
        cache_key = ("pil", clave, ancho, alto)
        if cache_key in self._cache:
            return self._cache[cache_key]

        nombre_archivo = self._indice.get(clave)
        try:
            if nombre_archivo is None:
                raise FileNotFoundError(f"no hay imagen indexada para '{clave}'")
            ruta = os.path.join(self.carpeta, nombre_archivo)
            imagen = Image.open(ruta).convert("RGBA")
            imagen = self._encajar_en_lienzo(imagen, ancho, alto)
        except Exception as error:
            print(f"Aviso: no se pudo cargar la imagen de '{clave}' ({error}). "
                  f"Se usa una carta genérica de respaldo.")
            imagen = self._carta_generica(carta, ancho, alto)

        self._cache[cache_key] = imagen
        return imagen

    # ------------------------------------------------------------------
    @staticmethod
    def _encajar_en_lienzo(imagen, ancho, alto):
        """Redimensiona manteniendo la proporción original (nunca deforma
        la carta) y la centra sobre un lienzo transparente del tamaño
        exacto pedido, para que todas las cartas midan siempre lo mismo."""
        lienzo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
        escala = min(ancho / imagen.width, alto / imagen.height)
        nuevo_ancho = max(1, round(imagen.width * escala))
        nuevo_alto = max(1, round(imagen.height * escala))
        redimensionada = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        offset = ((ancho - nuevo_ancho) // 2, (alto - nuevo_alto) // 2)
        lienzo.paste(redimensionada, offset, redimensionada)
        return lienzo

    def _carta_generica(self, carta, ancho, alto):
        """Dibuja (con Pillow, sin depender de ningún archivo) una carta
        de respaldo simple pero prolija: fondo blanco, borde redondeado y
        el valor/palo si se conocen, o un '?' si no hay ninguna info."""
        base_ancho, base_alto = 240, 360
        imagen = Image.new("RGBA", (base_ancho, base_alto), (0, 0, 0, 0))
        dibujo = ImageDraw.Draw(imagen)
        dibujo.rounded_rectangle(
            [6, 6, base_ancho - 6, base_alto - 6], radius=26,
            fill="#fbfaf5", outline="#2c2c2c", width=5,
        )
        color_texto = "#2c2c2c"
        texto = "?"
        if carta is not None:
            if carta.es_comodin():
                texto = "★"
                color_texto = COLORES_PALO.get("comodin", "#555555")
            else:
                texto = str(carta.valor)
                color_texto = COLORES_PALO.get(carta.palo, "#555555")

        fuente = self._fuente_generica(140)
        caja = dibujo.textbbox((0, 0), texto, font=fuente)
        ancho_texto, alto_texto = caja[2] - caja[0], caja[3] - caja[1]
        posicion = (
            (base_ancho - ancho_texto) / 2 - caja[0],
            (base_alto - alto_texto) / 2 - caja[1],
        )
        dibujo.text(posicion, texto, fill=color_texto, font=fuente)
        return self._encajar_en_lienzo(imagen, ancho, alto)

    @staticmethod
    def _fuente_generica(tamano):
        for nombre in ("georgiab.ttf", "georgia.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(nombre, tamano)
            except Exception:
                continue
        return ImageFont.load_default()
