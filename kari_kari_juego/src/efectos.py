"""
Efectos visuales: viñeta, oscuridad, screen shake, parpadeo de daño.
"""
import pygame
import math
import random


class Vignette:
    def __init__(self, ancho, alto, intensidad=80):
        self.surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        cx, cy = ancho // 2, alto // 2
        max_dist = math.hypot(cx, cy)
        steps = 40
        for i in range(steps, 0, -1):
            ratio = i / steps
            radio = int(max_dist * ratio)
            alpha = int((1 - ratio) * intensidad)
            pygame.draw.circle(self.surf, (0, 0, 0, alpha), (cx, cy), radio)

    def dibujar(self, pantalla):
        pantalla.blit(self.surf, (0, 0))


class MascaraOscuridad:
    def __init__(self, ancho, alto, alpha=90):
        self.ancho = ancho
        self.alto  = alto
        self.alpha = alpha

    def dibujar(self, pantalla, focos):
        capa = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        capa.fill((5, 8, 20, self.alpha))

        for (x, y, r) in focos:
            for i in range(8, 0, -1):
                rr = int(r * i / 8)
                a_sub = min(int(self.alpha * (i / 8) * 1.15), self.alpha)
                hole = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
                pygame.draw.circle(hole, (0, 0, 0, a_sub), (rr, rr), rr)
                capa.blit(hole, (int(x) - rr, int(y) - rr),
                          special_flags=pygame.BLEND_RGBA_SUB)

        pantalla.blit(capa, (0, 0))


class Sacudida:
    def __init__(self):
        self.intensidad = 0.0

    def activar(self, intensidad=10):
        self.intensidad = max(self.intensidad, intensidad)

    def actualizar(self, dt):
        self.intensidad = max(0.0, self.intensidad - 50 * dt)

    def offset(self):
        if self.intensidad <= 0:
            return (0, 0)
        return (random.randint(-int(self.intensidad), int(self.intensidad)),
                random.randint(-int(self.intensidad), int(self.intensidad)))


class ParpadeoDaño:
    def __init__(self, ancho, alto, duracion=0.4):
        self.capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        self.tiempo = 0.0
        self.duracion = duracion

    def activar(self):
        self.tiempo = self.duracion

    def actualizar(self, dt):
        self.tiempo = max(0.0, self.tiempo - dt)

    def dibujar(self, pantalla):
        if self.tiempo > 0:
            alpha = int(140 * (self.tiempo / self.duracion))
            self.capa.fill((255, 0, 0, alpha))
            pantalla.blit(self.capa, (0, 0))