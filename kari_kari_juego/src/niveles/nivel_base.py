"""
Clase base de todos los niveles.
Define qué datos tiene cada nivel y crea los objetos del mundo.
"""
import pygame
from src.niveles.mapa_nivel import MapaNivel
from src.entidades.farol import Farol
from src.entidades.kari_kari import KariKari
from src.entidades.saltena import Saltena
from src.entidades.cliente import Cliente


class NivelBase:
    # --- Metadatos ---
    numero = 1
    nombre = "Nivel base"
    mensaje_intro = ""

    # --- Configuración ---
    duracion = 180.0
    entregas_objetivo = 3

    # --- Assets ---
    ruta_fondo = "fondos/nivel_1.jpg"
    matriz_colisiones = None

    # --- Spawns ---
    jugador_spawn = (96, 96)
    enemigos_spawn = []                # [(x, y), ...]
    saltenas_iniciales = []            # [(x, y), ...]
    saltenas_max = 3
    saltenas_intervalo = 10.0

    def __init__(self):
        self.mapa = MapaNivel(self.ruta_fondo, self.matriz_colisiones)

        self.faroles = [Farol(x, y) for (x, y) in self.mapa.faroles_pos]
        self.enemigos = [KariKari(x, y) for (x, y) in self.enemigos_spawn]
        self.saltenas = [Saltena(x, y) for (x, y) in self.saltenas_iniciales]

        self.cliente = None
        if self.mapa.cliente_rect:
            self.cliente = Cliente(self.mapa.cliente_rect.centerx,
                                   self.mapa.cliente_rect.centery)
            self.cliente.activar()

        self.restaurante_rect = self.mapa.restaurante_rect

        self.tiempo_restante     = self.duracion
        self.entregas_realizadas = 0
        self.combo               = 0
        self.tiempo_combo        = 0.0
        self.tiempo_nueva_saltena = self.saltenas_intervalo
        self.terminado = False
        self.victoria  = False

    def rect_mundo(self):
        return self.mapa.rect_mundo()

    def actualizar(self, dt, jugador, tiene_paquete):
        self.tiempo_restante -= dt
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            self.terminado = True
            self.victoria  = False

        if self.tiempo_combo > 0:
            self.tiempo_combo -= dt
            if self.tiempo_combo <= 0:
                self.combo = 0

        for s in self.saltenas:
            s.actualizar(dt)

        if self.cliente:
            resultado = self.cliente.actualizar(dt)
            if resultado == "expirado":
                self.combo = 0

    def distancia_al_enemigo_mas_cercano(self, jugador_rect):
        if not self.enemigos:
            return 9999
        return min(
            pygame.Vector2(e.rect.center).distance_to(
                pygame.Vector2(jugador_rect.center))
            for e in self.enemigos
        )