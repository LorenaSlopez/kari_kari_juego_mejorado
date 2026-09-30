from src.niveles.nivel_base import NivelBase


MAPA_NIVEL_1 = [
    "############################",
    "#..........................#",
    "#..L........L..............#",
    "#..........................#",
    "#.........................##",
    "#..........................#",
    "#....####.................##",
    "####.####...........L.....##",
    "####.......................#",
    "##.L.......................#",
    "#..........................#",
    "#...............######.....#",
    "#...............######.....#",
    "#.R................###...C.#",
    "#.....######........##.....#",
    "############################",
]


class Nivel1(NivelBase):

    numero = 1

    nombre = "El primer pedido"

    mensaje_intro = (
        "NIVEL 1 — EL PRIMER PEDIDO\n\n"
        "Recoge el paquete en el restaurante,\n"
        "esquiva al Kari-Kari y entrégalo a Doña Remedios.\n\n"
        "WASD: mover | ESPACIO: linterna | SHIFT: sprint | E: interactuar"
    )

    duracion = 180.0

    entregas_objetivo = 3

    ruta_fondo = "fondos/nivel_1.jpg"

    matriz_colisiones = MAPA_NIVEL_1

    jugador_spawn = (96, 96)

    enemigos_spawn = [
        (1200, 500)
    ]

    saltenas_iniciales = [
        (500, 600),
        (900, 400),
        (1300, 700)
    ]

    saltenas_max = 3

    saltenas_intervalo = 10.0