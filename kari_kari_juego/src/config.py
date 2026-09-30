"""
Constantes globales del juego — alineadas al GDD v2.0
"""

# --- Pantalla ---
ANCHO = 900
ALTO = 650
FPS = 60
TITULO = "Kari-Kari: Delivery Night"

# --- Tamaño de bloque para la matriz de colisiones ---
TAM_BLOQUE = 64

# --- Colores ---
NEGRO          = (0, 0, 0)
BLANCO         = (255, 255, 255)
AZUL_NOCTURNO  = (15, 23, 42)
AZUL_PROFUNDO  = (10, 12, 30)
MORADO_OSCURO  = (30, 27, 75)
AMARILLO       = (250, 204, 21)
AMBAR          = (245, 158, 11)
ROJO           = (220, 38, 38)
ROJO_SANGRE    = (185, 28, 28)
VERDE          = (34, 197, 94)
GRIS           = (60, 60, 80)
GRIS_CLARO     = (120, 120, 140)

# --- Jugador (GDD) ---
JUGADOR_VEL_BASE       = 200    # px/s
JUGADOR_VEL_SPRINT     = 320    # px/s con SHIFT
JUGADOR_GRASA_MAX      = 100.0
JUGADOR_BATERIA_MAX    = 100.0

# --- Linterna (GDD: -5%/s, rango ~180-220 px) ---
LINTERNA_COSTO  = 5.0     # % batería por segundo
LINTERNA_RANGO  = 180     # px para aturdir (valor del GDD)

# --- Enemigo Kari-Kari (GDD) ---
KARI_VEL_PATRULLA      = 70
KARI_VEL_PERSECUCION   = 165
KARI_RADIO_DETECCION   = 250    # px
KARI_RADIO_PIERDE      = 400
KARI_TIEMPO_ATURDIDO   = 1.5    # segundos

# --- Faroles (GDD: zona segura + recarga) ---
FAROL_RADIO             = 90
FAROL_RECARGA_BATERIA   = 2.0   # %/s  ← valor del GDD (+2%/s)
FAROL_RECARGA_GRASA     = 5.0   # HP/s mientras estás bajo el farol

# --- Oscuridad ambiental (GDD: -1 HP/s en sombra) ---
GRASA_DECAIMIENTO = 1.0

# --- Salteñas (GDD: +30 HP) ---
SALTENA_RECUPERA = 30.0

# --- Entrega (GDD) ---
ENTREGA_BONUS_GRASA          = 20.0
ENTREGA_BONUS_PUNTOS_BASE    = 100
ENTREGA_BONUS_POR_TIEMPO     = 2
ENTREGA_BONUS_POR_COMBO      = 50
CLIENTE_PACIENCIA            = 45.0