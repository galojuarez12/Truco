# TP Final – Programación 3: Truco & Chinchón (con interfaz gráfica moderna)

Extiende el TP de Truco original para cumplir con la consigna final:
mantiene los TAD pedidos, agrega una interfaz gráfica en Tkinter con una
pantalla inicial para elegir el modo de juego, y conserva **Chinchón**
como segundo juego de cartas, probando que la arquitectura
(`JuegoDeCartas` + `GameManager`) efectivamente permite agregar juegos
nuevos sin tocar la estructura principal.

## Cómo ejecutarlo

```bash
pip install pillow
python3 main.py
```

Requiere `tkinter` instalado (viene con Python en Windows/Mac; en Linux
Debian/Ubuntu si falta: `sudo apt install python3-tk`) y `Pillow` para
las imágenes de las cartas. No hace falta ninguna otra librería: no se
usa ReportLab, rlPyCairo, cairosvg, ttkbootstrap ni CustomTkinter (ver
"Solución al bug de imágenes" y "Sobre la interfaz moderna" más abajo).

Se abre directamente el menú principal (sin pantalla de presentación);
desde ahí se elige **Truco contra la CPU** o **Chinchón**, ambos
jugables 1 vs CPU.

## Estructura del proyecto

| Archivo / carpeta | Contenido |
|---|---|
| `estructuras.py` | **Parte 1**: `Nodo`, `ListaEnlazada`, `Pila` (sin usar `list`/`deque`). |
| `cartas.py` | **Parte 2**: `Carta`, `Mazo`, `MazoEspanol` (50 cartas: 4 palos x 12 valores + 2 comodines, tal cual la consigna original), y dos subclases concretas: `MazoTruco` (40 cartas, sin 8/9/comodines) y `MazoChinchon` (48 cartas: los 12 valores completos, con 8 y 9, sin comodines). |
| `juegos.py` | **Parte 3 y 4**: `JuegoDeCartas` (clase base), `Truco`, `Chinchon` y `GameManager`. **Sin cambios de lógica** en esta revisión: sólo se retocó la simulación de `test_logica.py` (ver más abajo). |
| `interfaz/` | Toda la capa gráfica (Tkinter), reorganizada en módulos con responsabilidades claras — ver el detalle abajo. |
| `gui.py` | Punto de compatibilidad: reexporta `interfaz.app.main` para que `main.py` (`from gui import main`) siga funcionando sin cambios. |
| `main.py` | Punto de entrada (`python3 main.py`). |
| `imagenes/` | 49 imágenes de cartas en **PNG real** (ver más abajo). |
| `recursos_originales_svg/` | Los 49 SVG originales, archivados por si hace falta regenerar los PNG en otra resolución. El juego ya no los lee para nada. |
| `test_logica.py`, `test_combinaciones.py`, `test_cierre.py`, `test_indice_imagenes.py` | Scripts de verificación de la lógica (no requieren Tkinter). |

### El paquete `interfaz/`

| Módulo | Responsabilidad |
|---|---|
| `tema.py` | Paleta de colores, fuentes y estilos ttk. Un solo lugar para retocar todo el look. |
| `imagenes.py` | Carga de imágenes de cartas: sólo Pillow, con caché y una carta genérica de respaldo si algo faltara. |
| `animaciones.py` | Fundidos de ventana/imagen, desplazamientos y parpadeos, todo con `after()` (sin hilos ni librerías extra). |
| `widgets.py` | Botones con esquinas redondeadas/hover/presión y paneles con sombra suave, dibujados a mano sobre `Canvas`. |
| `pantalla_bienvenida.py` | Menú principal (Truco / Chinchón / Salir), con la misma identidad visual que el resto de la app. Se muestra directo, sin pantalla de presentación. |
| `pantalla_truco.py` | Tablero de juego del Truco, con el layout pedido (CPU arriba, mesa al centro, puntaje/acciones, mis cartas abajo). |
| `pantalla_chinchon.py` | Tablero de juego del Chinchón, restyleado con el mismo look. |
| `pantalla_ganador.py` | Pantalla de fin de partida. |
| `app.py` | Controlador principal: crea la ventana, arma `GameManager` + gestor de imágenes una sola vez, y cambia de pantalla (con transición) según el flujo. |

## Solución al bug de imágenes (causa raíz)

Las 49 imágenes de cartas eran en realidad archivos **SVG**, pero
guardados con un nombre "doble" (por ejemplo `10_oro.png.svg`). Al
detectar la extensión `.svg`, el código viejo intentaba convertirlas a
PNG **en tiempo de ejecución** usando ReportLab + rlPyCairo (o
cairosvg). En Windows esas dos rutas de conversión fallaban siempre,
de ahí el error `cannot import desired renderPM backend rlPyCairo`.

La solución fue de raíz, no un parche:

1. Los 49 SVG se convirtieron **una sola vez** a PNG reales (guardados
   en `imagenes/` con nombre simple, p. ej. `10_oro.png`). Los SVG
   originales quedaron archivados en `recursos_originales_svg/`.
2. `interfaz/imagenes.py` sólo usa `Image.open()` de Pillow. No queda
   ninguna dependencia de ReportLab, rlPyCairo, cairosvg ni conversión
   de SVG en tiempo de ejecución.
3. Si en el futuro faltara algún PNG, el programa **no se rompe**: se
   genera al vuelo una carta genérica de respaldo dibujada con Pillow.

## Sobre la interfaz moderna

Se modernizó toda la interfaz (menú principal, tableros, botones,
animaciones, diálogos) usando **sólo Tkinter + ttk + Pillow** — las
mismas dependencias que ya tenía el proyecto. Se evitó a propósito
sumar `ttkbootstrap` o `CustomTkinter` (mencionadas como opción) porque
el TP pide explícitamente no depender de librerías innecesarias, y esas
dos requieren instalación aparte que quizás no esté disponible en la
PC donde se corrija el trabajo. Los bordes redondeados se logran
dibujando a mano sobre `Canvas` (ver `interfaz/widgets.py`); no se usa
ningún borde, sombra ni efecto de opacidad sobre las cartas.

Identidad visual única en las tres pantallas (menú, Truco y Chinchón):
tablero **celeste**, paneles/marcos/botones **blancos**, con una sola
tipografía (Georgia) en botones, títulos, marcador, menú y diálogos.
Toda la paleta vive en un único archivo (`interfaz/tema.py`).

**Una decisión de diseño no literal** frente a la consigna, para no
perder funcionalidad ya construida: el panel de Acciones del Truco
agrega un 10º botón, **"Envido Envido"**, que no aparecía en el mockup
original pero sí es una jugada legal del motor
(`Truco.ENVIDO_SIGUIENTES`); omitirlo hubiera quitado una función que
ya funcionaba.

## Decisiones de diseño relevantes (lógica del juego, sin cambios)

- **`MazoEspanol` genérico + subclases**: la consigna original pide un
  `MazoEspanol` con los 12 valores y 2 comodines. El Truco excluye el 8,
  el 9 y los comodines; el Chinchón usa los 12 valores completos (incluye
  8 y 9) pero tampoco lleva comodines. Se mantuvo la clase base fiel a la
  consigna y cada juego hereda su propio mazo filtrado. Esto es lo que
  permite agregar un tercer juego el día de mañana sin duplicar código
  de armado/barajado.

- **Sin `input()`/`print()` en la lógica**: las clases `Truco` y `Chinchon`
  no hacen E/S directa; cada acción del jugador es un método (`cantar_envido`,
  `jugar_carta`, `robar_del_mazo`, `descartar`, `cerrar_mano`, etc.) que
  devuelve un diccionario con el resultado. Así la GUI sólo traduce clics en
  llamadas a estos métodos, y el mismo motor podría reusarse desde una
  consola o una web sin cambios.

- **Reglas de Chinchón implementadas**:
  - Mano de 7 cartas; en cada turno se roba (del mazo o del pozo) y se
    descarta.
  - Combinaciones válidas: escaleras de 3+ cartas consecutivas del mismo
    palo, o tríos/cuadras de igual valor en palos distintos. Mazo sin
    comodines: se juega con las 48 cartas reales (incluye 8 y 9).
  - Se puede cerrar la mano dejando **como máximo 1 carta suelta** (que
    cuenta a favor en el puntaje). Si las 7 cartas cierran en una única
    escalera sin ninguna suelta, es un **Chinchón** real y el rival recibe
    25 puntos de penalización extra.
  - Gana la partida quien tenga **menos** puntos acumulados cuando algún
    jugador llega a 100 (como en el golf: conviene sumar poco).
  - Estas son las reglas "estándar" más comunes de la variante argentina;
    se documentan explícitamente porque el Chinchón tiene bastantes
    variantes de mesa a mesa.

- **Truco**: la negociación de Envido y Truco ocurre en una sola fase
  antes de jugar la primera carta (documentado en `juegos.Truco`), en
  vez de permitir cantar Truco después de cada ronda como en el
  reglamento 100% real. Es una simplificación intencional que **no** se
  tocó en esta revisión.

- Los métodos principales están documentados con **PRE/POST** en sus
  docstrings, y cada TAD declara su invariante, tal como pide la consigna.

## Verificación

Antes de entregar se corrieron pruebas automáticas (sin Tkinter, sólo
lógica) que ejercitan cientos de manos simuladas de ambos juegos, casos
puntuales de detección de combinaciones y los distintos tipos de cierre
del Chinchón (con bono de Chinchón, cierre normal y cierre "cortando").
Podés volver a correrlas con:

```bash
python3 test_logica.py
python3 test_combinaciones.py
python3 test_cierre.py
python3 test_indice_imagenes.py
```

(`test_logica.py` se actualizó para llamar a `cantar_envido` /
`responder_envido` / `cantar_truco` / `responder_truco`, que es la API
real de `juegos.Truco`; antes llamaba a un método `decidir_truco` que
ya no existe y la prueba fallaba a mitad de camino.)

Además, la interfaz nueva completa (pantalla de bienvenida, Truco y
Chinchón) se ejercitó de punta a punta simulando cientos de partidas
completas con jugadas aleatorias — incluyendo Vale Cuatro, Falta
Envido, Envido Envido e Irse al Mazo — para confirmar que ningún cambio
de pantalla ni botón rompe el flujo.

## Revisión 2 — ajustes visuales y de flujo

Sobre la base de la revisión anterior, se hicieron estos cambios
puntuales (sin tocar ninguna regla del Truco, del Chinchón, la IA, los
turnos ni los puntajes):

- **Se eliminó la sombra/borde oscuro de las cartas.** La causa real
  era doble: (1) el hover de las cartas de la mano cambiaba
  `relief`/`bd` del botón, lo que Tkinter dibuja como un bisel oscuro
  alrededor de la imagen; (2) las cartas jugadas en la mesa del Truco
  tenían un borde sólido de 3px alrededor (pensado para resaltar quién
  ganaba la ronda). Se quitaron los dos; las cartas ahora se ven
  completas, sin ningún borde ni recorte.
- **Cartas jugadas visibles en el Truco**, con la misma persistencia
  que ya tenía Chinchón: quedan arriba de la mesa (carta de la CPU
  arriba, la propia abajo, tal como en una mesa real) hasta que empieza
  la mano siguiente. Se reescribió además el posicionamiento de la mesa
  usando el manejador de geometría `pack` en vez de coordenadas
  manuales (`place`), que era lo que arriesgaba a recortar las cartas
  en algunas resoluciones de ventana.
- **"Próximamente" reemplazado directamente por "Chinchón"** en el menú
  principal; ya no hay ningún texto de "beta" ni de "próximamente" en
  ningún lado. `pantalla_proximamente.py` se eliminó del proyecto por
  quedar sin uso.
- **El programa abre directo en el menú** (Truco / Chinchón / Salir):
  se sacó el fundido de entrada y la animación de aparición de los
  botones que hacían sentir la apertura como una pantalla de
  presentación.
- **Identidad visual unificada**: se llevó la misma paleta (paño verde,
  marcos de madera, acentos dorados, detalles sutiles de celeste y
  blanco) y la misma tipografía (una sola familia, Georgia, en títulos,
  botones, marcador, menú y diálogos) a las tres pantallas — antes el
  menú principal tenía un fondo blanco con bandas de bandera que no
  compartía nada con el verde/dorado del resto del juego.
- Los diálogos de confirmación/aviso (por ejemplo "¿Seguro que querés
  irte al mazo?") dejaron de usar los cuadros nativos de
  `tkinter.messagebox` (que usan la tipografía del sistema operativo) y
  ahora son ventanas propias con la misma identidad visual y
  tipográfica que el resto de la app.

## Revisión 3 — tema celeste/blanco, historial lateral y prolijidad de las cartas

Nueva vuelta de ajustes visuales, otra vez sin tocar ninguna regla,
turno, IA, puntaje ni imagen del juego:

- **Paleta celeste + blanco**: el tablero (fondo de toda la app, menú
  incluido) pasó a celeste, y los paneles, marcos y botones a blanco,
  con una tipografía única (Georgia) en todos lados. Se centralizó todo
  en `interfaz/tema.py`, así que un solo archivo define el look
  completo de las tres pantallas.
- **Historial de acciones a la izquierda**: tanto en Truco como en
  Chinchón, el panel de historial (antes una franja angosta abajo) pasó
  a ocupar todo el lateral izquierdo del tablero, con texto más grande
  y scroll, para que se lea como un historial de verdad ("Jugador canta
  Envido", "CPU tiene 31 de Envido", "CPU gana el Envido", etc. — esos
  mensajes ya los arma el motor de juego en `juegos.py`, que no se
  tocó; esta revisión sólo le dio más lugar en pantalla).
- **Cartas jugadas centradas en la mesa**: se simplificó el
  posicionamiento (con `pack` en vez de coordenadas manuales) para que
  cada ronda jugada quede como una columna centrada (carta de la CPU
  arriba, la propia abajo) y las rondas anteriores sigan visibles,
  centradas, hasta que arranca la mano siguiente.
- **Se sacaron TODOS los efectos sobre las imágenes de las cartas**
  (nada de fundidos ni de agrandar la imagen en el hover): antes, al
  pasar el mouse sobre una carta de la mano se reemplazaba por una
  versión más grande, y las cartas de la mesa aparecían con un fundido
  de opacidad progresivo. Cualquiera de los dos podía, según la
  velocidad de la máquina, dejar a la vista un cuadro a mitad de camino
  (una imagen borrosa/semi-transparente). Ahora cada carta se muestra
  siempre con la MISMA imagen, a tamaño fijo y opacidad completa; el
  único rastro de una animación es una pequeña demora entre carta y
  carta al repartir la mano (sin fundido), y la breve espera antes de
  revelar la carta de la CPU.

