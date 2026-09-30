from src.niveles.nivel_base import NivelBase


MAPA_NIVEL_3 = [
    "############################",
    "#........#.................#",
    "#........#......L..........#",
    "#........#.................#",
    "#..#######....####.........#",
    "#..#................####...#",
    "#..#.....###...............#",
    "#..#..........L............#",
    "#..#.......................#",
    "#......###..........###....#",
    "#......###..........###....#",
    "#.........................##",
    "######.....###............##",
    "#..R.................C.....#",
    "#.....###.......###........#",
    "############################",
]

class Nivel3(NivelBase):

    numero = 3

    nombre = "Noche cerrada"

    mensaje_intro = (
        "NIVEL 3 — NOCHE CERRADA\n\n"
        "La noche más oscura. Casi no quedan faroles.\n"
        "Tres Kari-Karis te buscan. No hay margen de error.\n\n"
        "Buena suerte, Sdenka."
    )

    duracion = 120.0

    entregas_objetivo = 5

    ruta_fondo = "fondos/nivel_3.jpg"

    matriz_colisiones = MAPA_NIVEL_3

    jugador_spawn = (96, 96)

    enemigos_spawn = [
        (1050, 96),
        (650, 350),
        (1050, 550)
    ]

    saltenas_iniciales = [
        (500, 350)
    ]

    saltenas_max = 2

    saltenas_intervalo = 15.0