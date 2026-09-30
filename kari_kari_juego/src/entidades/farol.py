import pygame
from src.assets import cargar_imagen
from src import config as C


class Farol:
    def __init__(self, x, y, radio=None):
        self.rect   = pygame.Rect(x - 20, y - 20, 40, 40)
        self.radio  = radio or C.FAROL_RADIO
        self.centro = pygame.Vector2(x, y)
        # Farol vertical: altura proporcional a la referencia de personajes
        self.imagen = cargar_imagen("sprites/farol.png", (42, 84))
        self.tiene_sprite = True

    def contiene(self, rect_objetivo, padding=0):
        return self.centro.distance_to(
            pygame.Vector2(rect_objetivo.centerx, rect_objetivo.centery)
        ) < self.radio + padding

    def dibujar(self, pantalla, camara):
        centro_p = camara.aplicar_punto(self.centro.x, self.centro.y)

        # Halo de luz
        halo = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            r = int(self.radio * i / 6)
            a = int(30 + (6 - i) * 10)
            pygame.draw.circle(halo, (245, 158, 11, a),
                               (self.radio, self.radio), r)
        pantalla.blit(halo, (centro_p[0] - self.radio, centro_p[1] - self.radio))

        rect_p = camara.aplicar(self.rect)
        if self.tiene_sprite:
            pantalla.blit(self.imagen,
                          (rect_p.centerx - self.imagen.get_width() // 2,
                           rect_p.bottom - self.imagen.get_height()))
        else:
            pygame.draw.circle(pantalla, C.AMBAR, centro_p, 12)
            pygame.draw.circle(pantalla, C.AMARILLO, centro_p, 6)