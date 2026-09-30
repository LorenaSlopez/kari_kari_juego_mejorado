import pygame
import math
import random
from src.assets import cargar_spritesheet_grid
from src import config as C

# --- AJUSTA ESTE VALOR (debe ser igual que en jugador.py) ---
ESCALA_SPRITE = 0.5


class KariKari:
    def __init__(self, x, y):
        # Rect de colisión
        self.rect = pygame.Rect(x, y, 56, 56)
        self.pos  = pygame.Vector2(x, y)
        self.estado = "patrulla"
        self.tiempo_estado = 0.0
        self.memoria_jugador = 0.0
        self.punto_patrulla = pygame.Vector2(x, y)
        self.tiempo_nuevo_destino = 0.0
        self.direccion_huida = pygame.Vector2(1, 0)

        # Spritesheet 4x4
        self.frames = cargar_spritesheet_grid(
            "sprites/kari_kari.png",
            columnas=4, filas=4,
            escala=ESCALA_SPRITE
        )

        self.frame_actual = 0
        self.tiempo_anim = 0.0
        self.direccion = "abajo"
        self.parpadeo_aturdido = 0.0

    def actualizar(self, dt, jugador, esta_en_luz, linterna_apunta, mapa, mundo_rect):
        dx = jugador.rect.centerx - self.rect.centerx
        dy = jugador.rect.centery - self.rect.centery
        distancia = math.hypot(dx, dy)
        direccion = pygame.Vector2(dx, dy)

        if self.estado == "aturdido":
            self.tiempo_estado -= dt
            if self.tiempo_estado <= 0:
                self.estado = "huida"
                self.tiempo_estado = 0.8
                self.direccion_huida = (-direccion.normalize()
                                        if direccion.length_squared() > 0
                                        else pygame.Vector2(1, 0))

        elif self.estado == "huida":
            self.tiempo_estado -= dt
            self._mover(self.direccion_huida * 300 * dt, mapa, mundo_rect)
            if self.tiempo_estado <= 0:
                self.estado = "patrulla"

        else:
            if distancia < C.KARI_RADIO_DETECCION and not esta_en_luz:
                self.estado = "persecucion"
                self.memoria_jugador = 2.0
            elif self.estado == "persecucion":
                if distancia > C.KARI_RADIO_PIERDE or esta_en_luz:
                    self.memoria_jugador -= dt
                    if self.memoria_jugador <= 0:
                        self.estado = "patrulla"

            if linterna_apunta:
                self.estado = "aturdido"
                self.tiempo_estado = C.KARI_TIEMPO_ATURDIDO
                self.parpadeo_aturdido = 0.6

            if self.estado == "persecucion":
                if direccion.length_squared() > 0:
                    dir_norm = direccion.normalize()
                    self._mover(dir_norm * C.KARI_VEL_PERSECUCION * dt,
                                mapa, mundo_rect)
                    self._actualizar_direccion(dir_norm)
            else:
                self._patrullar(dt, mapa, mundo_rect)

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        self.tiempo_anim += dt
        if self.tiempo_anim >= 0.14:
            self.tiempo_anim = 0
            self.frame_actual = (self.frame_actual + 1) % 4
        self.parpadeo_aturdido = max(0.0, self.parpadeo_aturdido - dt)

    def _patrullar(self, dt, mapa, mundo_rect):
        self.tiempo_nuevo_destino -= dt
        if self.tiempo_nuevo_destino <= 0:
            self.punto_patrulla = pygame.Vector2(
                self.pos.x + random.randint(-180, 180),
                self.pos.y + random.randint(-180, 180)
            )
            self.tiempo_nuevo_destino = random.uniform(2.5, 4.5)

        dir_v = self.punto_patrulla - self.pos
        if dir_v.length() > 5:
            dir_norm = dir_v.normalize()
            self._mover(dir_norm * C.KARI_VEL_PATRULLA * dt, mapa, mundo_rect)
            self._actualizar_direccion(dir_norm)

    def _mover(self, delta, mapa, mundo_rect):
        nx = self.pos.x + delta.x
        ny = self.pos.y + delta.y

        rect_nuevo = pygame.Rect(int(nx), int(ny),
                                 self.rect.width, self.rect.height)
        for pared in mapa.rects_paredes:
            if rect_nuevo.colliderect(pared):
                rx = pygame.Rect(int(nx), int(self.pos.y),
                                 self.rect.width, self.rect.height)
                ry = pygame.Rect(int(self.pos.x), int(ny),
                                 self.rect.width, self.rect.height)
                if not any(rx.colliderect(p) for p in mapa.rects_paredes):
                    ny = self.pos.y
                elif not any(ry.colliderect(p) for p in mapa.rects_paredes):
                    nx = self.pos.x
                else:
                    nx, ny = self.pos.x, self.pos.y
                break

        self.pos.x = max(0, min(nx, mundo_rect.width  - self.rect.width))
        self.pos.y = max(0, min(ny, mundo_rect.height - self.rect.height))

    def _actualizar_direccion(self, dir_norm):
        if abs(dir_norm.x) > abs(dir_norm.y):
            self.direccion = "derecha" if dir_norm.x > 0 else "izquierda"
        else:
            self.direccion = "abajo" if dir_norm.y > 0 else "arriba"

    def _frame(self):
        if not self.frames:
            return None
        fila = {"abajo": 0, "izquierda": 1, "derecha": 2, "arriba": 3}[self.direccion]
        idx = min(fila * 4 + self.frame_actual, len(self.frames) - 1)
        return self.frames[idx]

    def dibujar(self, pantalla, camara):
        rect_p = camara.aplicar(self.rect)
        frame = self._frame()

        if frame:
            # Centrar el sprite sobre el rect
            ox = (rect_p.width  - frame.get_width())  // 2
            oy = (rect_p.height - frame.get_height()) // 2

            if self.parpadeo_aturdido > 0 and int(self.parpadeo_aturdido * 20) % 2 == 0:
                t = frame.copy()
                t.fill((120, 120, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
                pantalla.blit(t, (rect_p.x + ox, rect_p.y + oy))
            else:
                pantalla.blit(frame, (rect_p.x + ox, rect_p.y + oy))
        else:
            color = C.ROJO if self.estado == "persecucion" else (100, 0, 100)
            if self.estado == "aturdido":
                color = (120, 120, 255)
            pygame.draw.rect(pantalla, color, rect_p)
            pygame.draw.circle(pantalla, (255, 0, 0),
                               (rect_p.x + 10, rect_p.y + 12), 3)
            pygame.draw.circle(pantalla, (255, 0, 0),
                               (rect_p.x + 24, rect_p.y + 12), 3)

        if self.estado == "persecucion":
            pygame.draw.circle(pantalla, C.ROJO, rect_p.midtop, 4)