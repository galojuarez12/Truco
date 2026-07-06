"""
Punto de compatibilidad histórico: antes toda la interfaz vivía en este
único archivo. Ahora la interfaz está organizada en el paquete
`interfaz/` (ver interfaz/__init__.py para el detalle de cada módulo),
pero se deja este archivo para que `main.py` (`from gui import main`)
siga funcionando exactamente igual que antes, sin tener que tocarlo.
"""

from interfaz.app import main

if __name__ == "__main__":
    main()
