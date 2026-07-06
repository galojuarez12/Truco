"""
Paleta de colores, fuentes y configuración de estilos ttk usadas en TODA
la interfaz — el menú principal y los dos juegos comparten exactamente
esta misma identidad visual (mismos colores, mismos marcos, misma
tipografía), tal como pide la consigna.

Identidad: tablero celeste (bandera Argentina) con paneles, marcos y
botones blancos — elegante y moderna, sin sobrecargar. Una única
familia tipográfica (Georgia) se usa en botones, títulos, marcador,
menú y diálogos.
"""

from tkinter import ttk

# ---------------------------------------------------------------------------
# Tablero (fondo principal) — celeste, inspirado en la bandera Argentina.
# ---------------------------------------------------------------------------
COLOR_FONDO = "#7FB3E8"
COLOR_FONDO_OSCURO = "#5B93CE"

# ---------------------------------------------------------------------------
# Paneles / marcos / botones / fondos secundarios — blancos.
# ---------------------------------------------------------------------------
COLOR_PANEL = "#FFFFFF"
COLOR_PANEL_CLARO = "#EAF2FB"
COLOR_BORDE = "#BFD9F2"

# ---------------------------------------------------------------------------
# Texto y acentos
# ---------------------------------------------------------------------------
COLOR_TEXTO = "#1B2A3A"
COLOR_TEXTO_SUAVE = "#5B7285"
COLOR_ACENTO = "#2E6DA4"
COLOR_ACENTO_HOVER = "#3E82C2"
COLOR_ACENTO_TEXTO = "#FFFFFF"
COLOR_EXITO = "#2E9E5B"
COLOR_EXITO_HOVER = "#3CBB70"
COLOR_PELIGRO = "#C0392B"
COLOR_PELIGRO_HOVER = "#D9503F"
COLOR_DESHABILITADO = "#DCE6F0"
COLOR_DESHABILITADO_TEXTO = "#9AACBC"

# ---------------------------------------------------------------------------
# Detalles patrios puntuales
# ---------------------------------------------------------------------------
CELESTE = "#75AADB"
BLANCO_HUESO = "#FFFFFF"
GRIS_TEXTO = "#1B2A3A"

# ---------------------------------------------------------------------------
# Colores asociados a cada palo (para acentos y respaldo si falta una imagen)
# ---------------------------------------------------------------------------
COLORES_PALO = {
    "oro": "#c9a227",
    "copa": "#b3202a",
    "espada": "#1f5fa8",
    "basto": "#2e7d32",
    "comodin": "#6a1b9a",
}

# ---------------------------------------------------------------------------
# Tipografía — UNA sola familia en toda la app.
# ---------------------------------------------------------------------------
_FAMILIA = "Georgia"

FUENTE_TITULO = (_FAMILIA, 30, "bold")
FUENTE_TITULO_CHICO = (_FAMILIA, 20, "bold")
FUENTE_SUBTITULO = (_FAMILIA, 14)
FUENTE_BOTON = (_FAMILIA, 12, "bold")
FUENTE_BOTON_CHICA = (_FAMILIA, 10, "bold")
FUENTE_TEXTO = (_FAMILIA, 11)
FUENTE_TEXTO_NEGRITA = (_FAMILIA, 11, "bold")
FUENTE_TEXTO_ITALICA = (_FAMILIA, 10, "italic")
FUENTE_MARCADOR = (_FAMILIA, 15, "bold")
FUENTE_LOG = (_FAMILIA, 10)


def configurar_estilos_ttk(root):
    """Configura un tema ttk claro y coherente con la paleta de arriba,
    para los pocos widgets ttk que se usan (Scrollbar, Entry, etc.)."""
    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    estilo.configure(
        "Vertical.TScrollbar",
        background=COLOR_BORDE,
        troughcolor=COLOR_PANEL_CLARO,
        bordercolor=COLOR_PANEL_CLARO,
        arrowcolor=COLOR_ACENTO,
        relief="flat",
    )
    estilo.map("Vertical.TScrollbar", background=[("active", COLOR_ACENTO)])
    return estilo
