import pygame
import math
import os
from src.assets import cargar_imagen, RUTA_ASSETS

# Tamaño coherente con el resto de objetos del juego
TAMANO_SALTENA = (40, 40)


def _cargar_sprite_saltena():
    """
    Intenta cargar la salteña desde varias rutas posibles
    (con ñ, sin ñ, mayúsculas, minúsculas).
    """
    candidatos = [
        "sprites/salteña.png",
        "sprites/saltena.png",
        "sprites/salteña.PNG",
        "sprites/saltena.PNG",
        "sprites/salteña.jpg",
        "sprites/saltena.jpg",
    ]
    for ruta in candidatos:
        ruta_completa = os.path.join(RUTA_ASSETS, ruta)
        if os.path.isfile(ruta_completa):
            try:
                img = cargar_imagen(ruta, TAMANO_SALTENA)
                # Comprobar que no sea placeholder magenta
                px = img.get_at((0, 0))
                if px[:3] != (255, 0, 255):
                    print(f"[Saltena] Cargada: {ruta}")
                    return img, True
            except Exception:
                continue

    print("[Saltena] No encontrada. Se dibuja placeholder.")
    # Placeholder como fallback
    img = cargar_imagen("sprites/saltena.png", TAMANO_SALTENA)
    return img, False


class Saltena:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.imagen, self.tiene_sprite = _cargar_sprite_saltena()
        self.tiempo_flote = 0.0

    def actualizar(self, dt):
        self.tiempo_flote += dt

    def dibujar(self, pantalla, camara):
        rect_p = camara.aplicar(self.rect)
        offset_y = int(math.sin(self.tiempo_flote * 3) * 2)

        if self.tiene_sprite:
            # Centrar la imagen en el rect
            ox = (rect_p.width  - self.imagen.get_width())  // 2
            oy = (rect_p.height - self.imagen.get_height()) // 2
            pantalla.blit(self.imagen,
                          (rect_p.x + ox, rect_p.y + oy + offset_y))
        else:
            # Placeholder (círculo naranja) si no hay imagen
            pygame.draw.circle(pantalla, (210, 160, 60),
                               (rect_p.centerx, rect_p.centery + offset_y), 10)
            pygame.draw.circle(pantalla, (140, 90, 30),
                               (rect_p.centerx, rect_p.centery + offset_y), 10, 2)