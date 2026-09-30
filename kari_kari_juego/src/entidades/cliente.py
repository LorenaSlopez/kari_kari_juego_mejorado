import pygame
from src.assets import cargar_imagen
from src import config as C


class Cliente:
    def __init__(self, x, y):
        # Mismo tamaño visual de referencia que Sdenka / Kari-Kari (~56x56 hitbox)
        self.rect = pygame.Rect(x - 28, y - 28, 56, 56)
        self.paciencia = C.CLIENTE_PACIENCIA
        self.paciencia_max = C.CLIENTE_PACIENCIA
        self.activo = False
        # Escala al tamaño de referencia de Kari-Kari / Sdenka
        self.imagen = cargar_imagen("sprites/cliente.png", (56, 56))
        self.tiene_sprite = True

    def activar(self):
        self.activo = True
        self.paciencia = C.CLIENTE_PACIENCIA

    def actualizar(self, dt):
        if not self.activo:
            return None
        self.paciencia -= dt
        if self.paciencia <= 0:
            self.activo = False
            return "expirado"
        return None

    def dibujar(self, pantalla, camara, tiene_paquete):
        if not self.activo:
            return
        rect_p = camara.aplicar(self.rect)

        if self.tiene_sprite:
            pantalla.blit(self.imagen, rect_p.topleft)
        else:
            pygame.draw.rect(pantalla, (100, 100, 255), rect_p)
            pygame.draw.rect(pantalla, C.BLANCO, rect_p, 2)

        # Barra de paciencia
        ancho = 44
        ratio = max(0.0, self.paciencia / self.paciencia_max)
        bx = rect_p.centerx - ancho // 2
        by = rect_p.top - 12
        pygame.draw.rect(pantalla, (60, 0, 0), (bx, by, ancho, 6))
        color = C.VERDE if ratio > 0.5 else (C.AMBAR if ratio > 0.25 else C.ROJO)
        pygame.draw.rect(pantalla, color, (bx, by, int(ancho * ratio), 6))

        # Burbuja "E"
        if tiene_paquete:
            fuente = pygame.font.SysFont("Arial", 14, bold=True)
            txt = fuente.render("E", True, C.BLANCO)
            pygame.draw.circle(pantalla, (0, 120, 0),
                               (rect_p.centerx, rect_p.top - 30), 12)
            pantalla.blit(txt, (rect_p.centerx - txt.get_width() // 2,
                                rect_p.top - 30 - txt.get_height() // 2))