"""
Estados del juego (pantallas).
"""
from enum import Enum, auto


class Estado(Enum):
    MENU             = auto()
    INTRO_NIVEL      = auto()
    JUGANDO          = auto()
    PAUSA            = auto()
    GAME_OVER        = auto()
    NIVEL_COMPLETADO = auto()
    VICTORIA_FINAL   = auto()