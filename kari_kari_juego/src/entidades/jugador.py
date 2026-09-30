import pygame
from src.assets import cargar_imagen
from src import config as C

ANCHO_FRAME = 84
ALTO_FRAME = 56


def _recortar_y_centrar(surf, ancho, alto):
    """Quita el fondo y centra el personaje."""
    w, h = surf.get_size()
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = surf.get_at((x, y))
            if a > 30 and (r + g + b) > 40:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y

    if max_x <= min_x or max_y <= min_y:
        return pygame.transform.smoothscale(surf, (ancho, alto))

    contenido = surf.subsurface(
        pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    ).copy()
    cw, ch = contenido.get_size()
    escala = min(ancho / cw, alto / ch) * 0.92
    nw = max(1, int(cw * escala))
    nh = max(1, int(ch * escala))
    contenido = pygame.transform.smoothscale(contenido, (nw, nh))

    canvas = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    canvas.fill((0, 0, 0, 0))
    canvas.blit(contenido, ((ancho - nw) // 2, (alto - nh) // 2))
    return canvas


def _cargar_frames_sdenka():
    """
    Carga las 4 filas del sheet.
    Para izquierda/derecha usamos UNA sola fila buena y la volteamos,
    así no gira al animar.
    """
    hoja = cargar_imagen("sprites/sdenka.png")
    w, h = hoja.get_size()
    fw = w // 4
    fh = h // 4

    # Cortar las 4 filas (16 frames)
    todas = []
    for fila in range(4):
        for col in range(4):
            rect = pygame.Rect(col * fw, fila * fh, fw, fh)
            frame = hoja.subsurface(rect).copy()
            frame = _recortar_y_centrar(frame, ANCHO_FRAME, ALTO_FRAME)
            todas.append(frame)

    # Fila 0 = frente, Fila 3 = espalda
    frente  = todas[0:4]    # indices 0-3
    espalda = todas[12:16]  # indices 12-15

    # Usamos la fila que NO gira (fila 1 = indices 4-7) como base de "derecha"
    # y la volteamos para crear "izquierda"
    derecha_base = todas[4:8]   # fila 1
    izquierda = [pygame.transform.flip(f, True, False) for f in derecha_base]
    derecha   = list(derecha_base)

    # Si al probar queda al revés, cambia a:
    # derecha_base = todas[8:12]  # fila 2
    # izquierda = [pygame.transform.flip(f, True, False) for f in derecha_base]
    # derecha   = list(derecha_base)

    # Orden final: [frente x4, izquierda x4, derecha x4, espalda x4]
    return frente + izquierda + derecha + espalda


class Jugador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y), 56, 56)
        self.pos = pygame.Vector2(float(x), float(y))

        self.velocidad = C.JUGADOR_VEL_BASE
        self.direccion = "abajo"
        self.frame_actual = 0
        self.tiempo_anim = 0.0
        self.en_movimiento = False

        self.frames = _cargar_frames_sdenka()

        self.dash_activo = False
        self.tiempo_dash = 0.0
        self.cooldown_dash = 0.0
        self.direccion_dash = pygame.Vector2(0, 0)

        self.invulnerable = 0.0
        self.parpadeo_daño = 0.0
        self.tiene_paquete = False

    def actualizar(self, dt, teclas, bateria, mapa, mundo_rect):
        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and bateria > 0
        self.velocidad = C.JUGADOR_VEL_SPRINT if sprint else C.JUGADOR_VEL_BASE

        dx, dy = 0.0, 0.0
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= 1.0
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += 1.0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= 1.0
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += 1.0

        if dx != 0.0 and dy != 0.0:
            dx *= 0.7071
            dy *= 0.7071

        if dx < 0:
            self.direccion = "izquierda"
        elif dx > 0:
            self.direccion = "derecha"
        elif dy < 0:
            self.direccion = "arriba"
        elif dy > 0:
            self.direccion = "abajo"

        self.en_movimiento = (dx != 0.0 or dy != 0.0)
        self.cooldown_dash = max(0.0, self.cooldown_dash - dt)

        if self.dash_activo:
            self.tiempo_dash -= dt
            vel = 520.0 * dt
            self._mover(self.direccion_dash.x * vel,
                        self.direccion_dash.y * vel,
                        mapa, mundo_rect)
            if self.tiempo_dash <= 0:
                self.dash_activo = False
        else:
            self._mover(dx * self.velocidad * dt,
                        dy * self.velocidad * dt,
                        mapa, mundo_rect)

        self.tiempo_anim += dt
        if self.en_movimiento:
            if self.tiempo_anim >= 0.12:
                self.tiempo_anim = 0.0
                self.frame_actual = (self.frame_actual + 1) % 4
        else:
            self.frame_actual = 0

        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.parpadeo_daño = max(0.0, self.parpadeo_daño - dt)

    def _mover(self, dx, dy, mapa, mundo_rect):
        self.pos.x += dx
        self.rect.x = int(round(self.pos.x))
        for pared in mapa.rects_paredes:
            if self.rect.colliderect(pared):
                if dx > 0:
                    self.rect.right = pared.left
                    self.pos.x = float(self.rect.x)
                elif dx < 0:
                    self.rect.left = pared.right
                    self.pos.x = float(self.rect.x)

        self.pos.y += dy
        self.rect.y = int(round(self.pos.y))
        for pared in mapa.rects_paredes:
            if self.rect.colliderect(pared):
                if dy > 0:
                    self.rect.bottom = pared.top
                    self.pos.y = float(self.rect.y)
                elif dy < 0:
                    self.rect.top = pared.bottom
                    self.pos.y = float(self.rect.y)

        self.rect.clamp_ip(mundo_rect)
        self.pos.x = float(self.rect.x)
        self.pos.y = float(self.rect.y)

    def intentar_dash(self, dx, dy):
        if self.cooldown_dash > 0 or self.dash_activo:
            return False
        if dx == 0 and dy == 0:
            return False
        vec = pygame.Vector2(dx, dy)
        if vec.length_squared() == 0:
            return False
        self.dash_activo = True
        self.tiempo_dash = 0.16
        self.direccion_dash = vec.normalize()
        self.cooldown_dash = 1.0
        self.invulnerable = 0.25
        return True

    def recibir_daño(self):
        if self.invulnerable > 0:
            return False
        self.parpadeo_daño = 0.4
        self.invulnerable = 0.6
        return True

    def _frame_actual(self):
        if not self.frames:
            return None
        # Orden en self.frames:
        # 0-3 frente | 4-7 izquierda (volteada) | 8-11 derecha | 12-15 espalda
        fila = {
            "abajo": 0,
            "izquierda": 1,
            "derecha": 2,
            "arriba": 3,
        }[self.direccion]
        idx = fila * 4 + self.frame_actual
        if idx >= len(self.frames):
            idx = 0
        return self.frames[idx]

    def dibujar(self, pantalla, camara):
        rect_p = camara.aplicar(self.rect)
        frame = self._frame_actual()

        if self.parpadeo_daño > 0 and int(self.parpadeo_daño * 20) % 2 == 0:
            return

        if frame:
            ox = (rect_p.width - frame.get_width()) // 2
            oy = (rect_p.height - frame.get_height()) // 2
            pantalla.blit(frame, (rect_p.x + ox, rect_p.y + oy))
        else:
            pygame.draw.rect(pantalla, C.VERDE, rect_p)
            pygame.draw.rect(pantalla, C.BLANCO, rect_p, 2)

        if self.tiene_paquete:
            pygame.draw.circle(pantalla, C.AMBAR,
                               (rect_p.centerx, rect_p.top - 12), 6)