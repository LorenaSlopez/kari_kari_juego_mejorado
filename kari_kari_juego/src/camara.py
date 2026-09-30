"""
Cámara 2D que sigue al jugador con suavizado.
"""
import pygame


class Camara:
    def __init__(self, ancho_ventana, alto_ventana, ancho_mundo, alto_mundo):
        self.ancho_ventana = ancho_ventana
        self.alto_ventana  = alto_ventana
        self.ancho_mundo   = ancho_mundo
        self.alto_mundo    = alto_mundo
        self.x = 0.0
        self.y = 0.0

    def seguir(self, objetivo_rect):
        obj_x = objetivo_rect.centerx - self.ancho_ventana // 2
        obj_y = objetivo_rect.centery - self.alto_ventana // 2

        self.x += (obj_x - self.x) * 0.15
        self.y += (obj_y - self.y) * 0.15

        if self.ancho_mundo > self.ancho_ventana:
            self.x = max(0, min(self.x, self.ancho_mundo - self.ancho_ventana))
        else:
            self.x = (self.ancho_mundo - self.ancho_ventana) / 2

        if self.alto_mundo > self.alto_ventana:
            self.y = max(0, min(self.y, self.alto_mundo - self.alto_ventana))
        else:
            self.y = (self.alto_mundo - self.alto_ventana) / 2

    def aplicar(self, rect):
        return rect.move(-int(self.x), -int(self.y))

    def aplicar_punto(self, x, y):
        return (int(x - self.x), int(y - self.y))