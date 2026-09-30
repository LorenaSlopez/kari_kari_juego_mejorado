import pygame
import math
from src.assets import cargar_imagen
from src import config as C


class Linterna:
    def __init__(self):
        self.encendida = False
        self.imagen = cargar_imagen("vfx/luz_linterna.png", (200, 200))
        self.tiene_sprite = self.imagen.get_width() > 100

    def actualizar(self, dt, teclas, bateria):
        self.encendida = teclas[pygame.K_SPACE] and bateria > 0
        return self.encendida

    def apunta_a(self, jugador_rect, objetivo_rect, camara):
        """True si el mouse apunta hacia el objetivo (cono ~45° del GDD)."""
        if not self.encendida:
            return False

        dx = objetivo_rect.centerx - jugador_rect.centerx
        dy = objetivo_rect.centery - jugador_rect.centery
        dist = math.hypot(dx, dy)
        if dist > C.LINTERNA_RANGO:
            return False

        mx, my = pygame.mouse.get_pos()
        if camara:
            mx += camara.x
            my += camara.y

        ang_mouse = math.atan2(my - jugador_rect.centery,
                               mx - jugador_rect.centerx)
        ang_enemigo = math.atan2(dy, dx)
        diff = abs((ang_mouse - ang_enemigo + math.pi) % (2 * math.pi) - math.pi)
        return diff < math.radians(45)

    def dibujar(self, pantalla, camara, jugador_rect):
        if not self.encendida:
            return

        origen = camara.aplicar_punto(jugador_rect.centerx, jugador_rect.centery)
        mx, my = pygame.mouse.get_pos()

        if self.tiene_sprite:
            dx = mx - origen[0]
            dy = my - origen[1]
            angulo = -math.degrees(math.atan2(dy, dx))
            img_rot = pygame.transform.rotate(self.imagen, angulo)
            rect_img = img_rot.get_rect(center=origen)
            pantalla.blit(img_rot, rect_img.topleft,
                          special_flags=pygame.BLEND_RGBA_ADD)
        else:
            pygame.draw.line(pantalla, C.AMBAR, origen, (mx, my), 3)
            pygame.draw.circle(pantalla, C.AMARILLO, (mx, my), 40, 2)
            pygame.draw.circle(pantalla, C.AMBAR, (mx, my), 4)