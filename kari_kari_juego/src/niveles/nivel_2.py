from src.niveles.nivel_base import NivelBase


MAPA_NIVEL_2 = [

    "############################",

    "#.............#....#.......#",

    "#.........L...#....#.......#",

    "#.#######..#....####.#####.#",

    "#.#######..#.....#...#####.#",

    "#.#.....#..##..............#",

    "#.#.........L..#....L......#",

    "#.#..###.......#...........#",

    "#.#..####........###...#####",

    "###...##...###...###.##....#",

    "###...##...#####.###.##....#",

    "####..##......######.##.#..#",

    "#.........###..............#",

    "#.R.....................C..#",

    "#.....###.............##...#",

    "############################",

]


class Nivel2(NivelBase):

    numero = 2

    nombre = "Callejones del Casco Viejo"

    mensaje_intro = (
        "NIVEL 2 — CALLEJONES DEL CASCO VIEJO\n\n"
        "Las calles se estrechan. Ahora hay dos Kari-Karis\n"
        "acechando en los callejones oscuros.\n\n"
        "Usa los faroles para recargar batería. SHIFT para sprintar."
    )

    duracion = 150.0

    entregas_objetivo = 4

    ruta_fondo = "fondos/nivel_2.jpg"

    matriz_colisiones = MAPA_NIVEL_2

    # Zona transitable en la parte superior izquierda
    jugador_spawn = (120, 120)

    # Ambos enemigos quedan sobre zonas transitables
    enemigos_spawn = [
        (1100, 350),
        (1000, 550)
    ]

    # Objetos únicamente en zonas transitables
    saltenas_iniciales = [
        (400, 500),
        (1000, 400)
    ]

    saltenas_max = 3

    saltenas_intervalo = 12.0