"""
Mapa: fondo + colisiones invisibles.
Las paredes NO se dibujan; solo bloquean el movimiento.
"""
import pygame
from src.assets import cargar_imagen
from src import config as C


class MapaNivel:
    def __init__(self, ruta_fondo, matriz, tam_bloque=None):
        self.tam_bloque = tam_bloque or C.TAM_BLOQUE
        self.matriz = matriz
        self.filas = len(matriz)
        self.columnas = len(matriz[0]) if matriz else 0

        for i, fila in enumerate(matriz):
            if len(fila) != self.columnas:
                raise ValueError(
                    f"Mapa inconsistente: fila {i} tiene {len(fila)} cols, "
                    f"se esperaban {self.columnas}"
                )

        self.ancho = self.columnas * self.tam_bloque
        self.alto  = self.filas * self.tam_bloque

        self.fondo = cargar_imagen(ruta_fondo, (self.ancho, self.alto), alpha=False)

        self.rects_paredes = []
        self.faroles_pos = []
        self.restaurante_rect = None
        self.cliente_rect = None

        self._construir()

    def _construir(self):
        for f, fila in enumerate(self.matriz):
            for c, ch in enumerate(fila):
                x = c * self.tam_bloque
                y = f * self.tam_bloque
                if ch == "#":
                    self.rects_paredes.append(
                        pygame.Rect(x, y, self.tam_bloque, self.tam_bloque))
                elif ch == "L":
                    self.faroles_pos.append(
                        (x + self.tam_bloque // 2, y + self.tam_bloque // 2))
                elif ch == "R":
                    self.restaurante_rect = pygame.Rect(
                        x, y, self.tam_bloque, self.tam_bloque)
                elif ch == "C":
                    self.cliente_rect = pygame.Rect(
                        x, y, self.tam_bloque, self.tam_bloque)

    def rect_mundo(self):
        return pygame.Rect(0, 0, self.ancho, self.alto)

    def dibujar_fondo(self, pantalla, camara):
        # Solo la imagen del nivel — sin bloques visibles
        pantalla.blit(self.fondo, (-int(camara.x), -int(camara.y)))

    def dibujar_debug(self, pantalla, camara):
        # Solo con F1
        for pared in self.rects_paredes:
            rp = camara.aplicar(pared)
            surf = pygame.Surface(rp.size, pygame.SRCALPHA)
            surf.fill((255, 0, 0, 50))
            pantalla.blit(surf, rp.topleft)
        if self.restaurante_rect:
            pygame.draw.rect(pantalla, (0, 255, 0),
                             camara.aplicar(self.restaurante_rect), 2)
        if self.cliente_rect:
            pygame.draw.rect(pantalla, (0, 150, 255),
                             camara.aplicar(self.cliente_rect), 2)