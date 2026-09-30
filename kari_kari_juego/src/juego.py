"""
Clase Juego — susurro solo cerca del Kari-Kari.
"""
import pygame
import sys
import math
import random
from typing import Optional

from src import config as C
from src.estados import Estado
from src.assets import (
    cargar_imagen, reproducir, musica, parar_musica, parar_efectos,
    parar_susurro, init_audio, pasos_actualizar,
)
from src.camara import Camara
from src.efectos import Vignette, MascaraOscuridad, Sacudida, ParpadeoDaño
from src.entidades.jugador import Jugador
from src.entidades.linterna import Linterna
from src.entidades.saltena import Saltena
from src.niveles import LISTA_NIVELES
from src.niveles.nivel_base import NivelBase
from src.niveles.mapa_nivel import MapaNivel


class Juego:
    def __init__(self):
        pygame.init()
        init_audio()

        self.pantalla = pygame.display.set_mode((C.ANCHO, C.ALTO))
        pygame.display.set_caption(C.TITULO)
        self.reloj = pygame.time.Clock()

        self.f_titulo  = pygame.font.SysFont("Arial", 56, bold=True)
        self.f_media   = pygame.font.SysFont("Arial", 28, bold=True)
        self.f_normal  = pygame.font.SysFont("Arial", 20)
        self.f_pequena = pygame.font.SysFont("Arial", 16)

        self.vignette  = Vignette(C.ANCHO, C.ALTO)
        self.oscuridad = MascaraOscuridad(C.ANCHO, C.ALTO, alpha=90)
        self.shake     = Sacudida()
        self.parpadeo  = ParpadeoDaño(C.ANCHO, C.ALTO)

        self.estado = Estado.MENU
        self.indice_nivel = 0

        self.nivel:    Optional[NivelBase] = None
        self.mapa:     Optional[MapaNivel] = None
        self.camara:   Optional[Camara]    = None
        self.jugador:  Optional[Jugador]   = None
        self.linterna: Optional[Linterna]  = None

        self.bateria = C.JUGADOR_BATERIA_MAX
        self.grasa   = C.JUGADOR_GRASA_MAX
        self.puntos  = 0
        self.mostrar_debug = False
        self.tiempo_mensaje = 0.0
        self.img_restaurante = cargar_imagen("sprites/restaurante.png", (64, 64))

        self._espacio_antes = False
        self._caminaba = False
        self._tiempo_paso = 0.0
        self._susurro_cd = 0.0
        self._botones_menu = []

        musica("menu", volumen=0.3)

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            dt = self.reloj.tick(C.FPS) / 1000.0
            dt = min(dt, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    ejecutando = False
                self._manejar_evento(ev)
            self._actualizar(dt)
            self._dibujar()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def _manejar_evento(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.estado == Estado.MENU:
                for rect, idx in self._botones_menu:
                    if rect.collidepoint(ev.pos):
                        self.indice_nivel = idx
                        self.puntos = 0
                        parar_efectos()
                        parar_musica()
                        self._cargar_nivel(idx)
            return

        if ev.type != pygame.KEYDOWN:
            return

        if self.estado == Estado.MENU:
            if ev.key == pygame.K_RETURN or ev.key in (pygame.K_1, pygame.K_KP1):
                self.indice_nivel = 0
                self.puntos = 0
                parar_efectos()
                parar_musica()
                self._cargar_nivel(0)
            elif ev.key in (pygame.K_2, pygame.K_KP2):
                self.indice_nivel = 1
                self.puntos = 0
                parar_efectos()
                parar_musica()
                self._cargar_nivel(1)
            elif ev.key in (pygame.K_3, pygame.K_KP3):
                self.indice_nivel = 2
                self.puntos = 0
                parar_efectos()
                parar_musica()
                self._cargar_nivel(2)

        elif self.estado == Estado.INTRO_NIVEL:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.estado = Estado.JUGANDO
                parar_musica()
                musica("nivel", volumen=0.25)

        elif self.estado == Estado.JUGANDO:
            if ev.key == pygame.K_ESCAPE:
                self.estado = Estado.PAUSA
            elif ev.key == pygame.K_F1:
                self.mostrar_debug = not self.mostrar_debug

        elif self.estado == Estado.PAUSA:
            if ev.key == pygame.K_ESCAPE:
                self.estado = Estado.JUGANDO
            elif ev.key == pygame.K_m:
                self.estado = Estado.MENU
                parar_efectos()
                parar_musica()
                musica("menu", volumen=0.3)

        elif self.estado == Estado.GAME_OVER:
            if ev.key == pygame.K_r:
                self._cargar_nivel(self.indice_nivel)
            elif ev.key == pygame.K_m:
                self.estado = Estado.MENU
                parar_efectos()
                parar_musica()
                musica("menu", volumen=0.3)

        elif self.estado == Estado.NIVEL_COMPLETADO:
            if ev.key == pygame.K_RETURN:
                self.indice_nivel += 1
                if self.indice_nivel >= len(LISTA_NIVELES):
                    self.estado = Estado.VICTORIA_FINAL
                    parar_efectos()
                    parar_musica()
                    reproducir("victoria", 0.7)
                else:
                    parar_efectos()
                    parar_musica()
                    self._cargar_nivel(self.indice_nivel)

        elif self.estado == Estado.VICTORIA_FINAL:
            if ev.key == pygame.K_RETURN:
                self.estado = Estado.MENU
                parar_efectos()
                parar_musica()
                musica("menu", volumen=0.3)

    def _cargar_nivel(self, idx):
        clase = LISTA_NIVELES[idx]
        self.nivel = clase()
        assert self.nivel is not None
        self.mapa = self.nivel.mapa
        assert self.mapa is not None

        jx, jy = self.nivel.jugador_spawn
        self.jugador = Jugador(jx, jy)
        self.linterna = Linterna()
        self.camara = Camara(C.ANCHO, C.ALTO, self.mapa.ancho, self.mapa.alto)

        self.bateria = C.JUGADOR_BATERIA_MAX
        self.grasa   = C.JUGADOR_GRASA_MAX
        self._espacio_antes = False
        self._caminaba = False
        self._tiempo_paso = 0.0
        self._susurro_cd = 0.0
        parar_efectos()

        self.estado = Estado.INTRO_NIVEL
        self.tiempo_mensaje = 0.0

    def _actualizar(self, dt):
        self.shake.actualizar(dt)
        self.parpadeo.actualizar(dt)
        if self.estado == Estado.JUGANDO:
            self._actualizar_jugando(dt)
        elif self.estado == Estado.INTRO_NIVEL:
            self.tiempo_mensaje += dt

    def _actualizar_jugando(self, dt):
        assert self.nivel is not None
        assert self.mapa is not None
        assert self.jugador is not None
        assert self.linterna is not None
        assert self.camara is not None

        teclas = pygame.key.get_pressed()

        espacio_ahora = bool(teclas[pygame.K_SPACE]) and self.bateria > 0
        self.linterna.actualizar(dt, teclas, self.bateria)
        if espacio_ahora and not self._espacio_antes:
            reproducir("linterna", 0.6)
        self._espacio_antes = espacio_ahora
        if self.linterna.encendida:
            self.bateria = max(0.0, self.bateria - C.LINTERNA_COSTO * dt)

        self.jugador.actualizar(dt, teclas, self.bateria,
                                self.mapa, self.mapa.rect_mundo())

        caminando = (
            teclas[pygame.K_w] or teclas[pygame.K_UP]
            or teclas[pygame.K_s] or teclas[pygame.K_DOWN]
            or teclas[pygame.K_a] or teclas[pygame.K_LEFT]
            or teclas[pygame.K_d] or teclas[pygame.K_RIGHT]
        )
        pasos_actualizar(caminando, volumen=0.4)
        self._caminaba = caminando

        bajo_farol = any(f.contiene(self.jugador.rect) for f in self.nivel.faroles)
        if bajo_farol:
            self.bateria = min(C.JUGADOR_BATERIA_MAX,
                               self.bateria + C.FAROL_RECARGA_BATERIA * dt)
            self.grasa = min(C.JUGADOR_GRASA_MAX,
                             self.grasa + C.FAROL_RECARGA_GRASA * dt)
        else:
            self.grasa = max(0.0, self.grasa - C.GRASA_DECAIMIENTO * dt)

        jugador_en_luz = self.linterna.encendida and self.bateria > 0
        for kari in self.nivel.enemigos:
            apunta = self.linterna.apunta_a(self.jugador.rect, kari.rect, self.camara)
            kari.actualizar(dt, self.jugador, jugador_en_luz, apunta,
                            self.mapa, self.mapa.rect_mundo())
            if kari.rect.colliderect(self.jugador.rect):
                if self.jugador.recibir_daño():
                    self.grasa = max(0.0, self.grasa - 20.0)
                    self.parpadeo.activar()
                    self.shake.activar(12)
                    reproducir("dano", 0.75)

        # Susurro SOLO cerca; al alejarse se CORTA
        self._susurro_cd = max(0.0, self._susurro_cd - dt)
        dist = self.nivel.distancia_al_enemigo_mas_cercano(self.jugador.rect)
        RADIO_SUSURRO = 220
        if dist < RADIO_SUSURRO:
            if self._susurro_cd <= 0.0:
                reproducir("susurro", 0.5)
                self._susurro_cd = 2.0
        else:
            parar_susurro()
            self._susurro_cd = 0.0

        for s in self.nivel.saltenas[:]:
            if self.jugador.rect.colliderect(s.rect):
                self.nivel.saltenas.remove(s)
                self.grasa = min(C.JUGADOR_GRASA_MAX,
                                 self.grasa + C.SALTENA_RECUPERA)
                reproducir("saltena", 0.6)

        self.nivel.tiempo_nueva_saltena -= dt
        if (self.nivel.tiempo_nueva_saltena <= 0
                and len(self.nivel.saltenas) < self.nivel.saltenas_max):
            self.nivel.tiempo_nueva_saltena = self.nivel.saltenas_intervalo
            pos = self._generar_saltena()
            if pos:
                self.nivel.saltenas.append(Saltena(*pos))

        if (self.nivel.restaurante_rect
                and self.jugador.rect.colliderect(self.nivel.restaurante_rect)
                and not self.jugador.tiene_paquete):
            self.jugador.tiene_paquete = True

        if (self.nivel.cliente and self.nivel.cliente.activo
                and self.jugador.tiene_paquete
                and teclas[pygame.K_e]
                and self.jugador.rect.colliderect(self.nivel.cliente.rect)):
            self._entregar_paquete()

        self.nivel.actualizar(dt, self.jugador, self.jugador.tiene_paquete)
        self.camara.seguir(self.jugador.rect)

        if self.grasa <= 0:
            self.grasa = 0
            self.estado = Estado.GAME_OVER
            parar_efectos()
            parar_musica()
            reproducir("gameover", 0.7)
        elif self.nivel.terminado:
            if self.nivel.victoria:
                self.estado = Estado.NIVEL_COMPLETADO
                parar_efectos()
                reproducir("entrega", 0.55)
            else:
                self.estado = Estado.GAME_OVER
                parar_efectos()
                parar_musica()
                reproducir("gameover", 0.7)

    def _generar_saltena(self):
        assert self.jugador is not None
        assert self.mapa is not None
        assert self.nivel is not None
        mundo = self.mapa.rect_mundo()
        for _ in range(40):
            x = random.randint(mundo.left + 60, mundo.right - 80)
            y = random.randint(mundo.top + 60, mundo.bottom - 80)
            rect = pygame.Rect(x, y, 20, 20)
            if any(rect.colliderect(p) for p in self.mapa.rects_paredes):
                continue
            if math.hypot(x - self.jugador.rect.centerx,
                          y - self.jugador.rect.centery) < 200:
                continue
            if any(math.hypot(x - f.centro.x, y - f.centro.y) < 120
                   for f in self.nivel.faroles):
                continue
            return (x, y)
        return None

    def _entregar_paquete(self):
        assert self.jugador is not None
        assert self.nivel is not None
        self.jugador.tiene_paquete = False
        self.nivel.entregas_realizadas += 1
        self.nivel.combo += 1
        self.nivel.tiempo_combo = 5.0
        bonus_tiempo = int(self.nivel.tiempo_restante * C.ENTREGA_BONUS_POR_TIEMPO)
        bonus_combo  = self.nivel.combo * C.ENTREGA_BONUS_POR_COMBO
        self.puntos += C.ENTREGA_BONUS_PUNTOS_BASE + bonus_tiempo + bonus_combo
        self.grasa = min(C.JUGADOR_GRASA_MAX, self.grasa + C.ENTREGA_BONUS_GRASA)
        reproducir("entrega", 0.65)
        if self.nivel.entregas_realizadas >= self.nivel.entregas_objetivo:
            self.nivel.terminado = True
            self.nivel.victoria  = True
        elif self.nivel.cliente:
            self.nivel.cliente.activar()

    def _dibujar(self):
        self.pantalla.fill(C.AZUL_PROFUNDO)
        if self.estado == Estado.MENU:
            self._dibujar_menu()
        elif self.estado == Estado.INTRO_NIVEL:
            self._dibujar_intro()
        elif self.estado in (Estado.JUGANDO, Estado.PAUSA):
            self._dibujar_juego()
            if self.estado == Estado.PAUSA:
                self._dibujar_pausa()
        elif self.estado == Estado.GAME_OVER:
            self._dibujar_game_over()
        elif self.estado == Estado.NIVEL_COMPLETADO:
            self._dibujar_nivel_completado()
        elif self.estado == Estado.VICTORIA_FINAL:
            self._dibujar_victoria()

    def _dibujar_menu(self):
        try:
            fondo = cargar_imagen("fondos/fondo_menu", (C.ANCHO, C.ALTO), alpha=False)
            self.pantalla.blit(fondo, (0, 0))
        except Exception:
            self.pantalla.fill(C.AZUL_NOCTURNO)
        titulo = self.f_titulo.render("KARI-KARI", True, C.AMBAR)
        subt   = self.f_media.render("Delivery Night", True, C.BLANCO)
        self.pantalla.blit(titulo, (C.ANCHO // 2 - titulo.get_width() // 2, 80))
        self.pantalla.blit(subt,   (C.ANCHO // 2 - subt.get_width()   // 2, 145))
        nombres = [
            "Nivel 1 - El primer pedido",
            "Nivel 2 - Callejones",
            "Nivel 3 - Noche cerrada",
        ]
        self._botones_menu = []
        bw, bh = 420, 48
        bx = C.ANCHO // 2 - bw // 2
        by0 = 220
        mx, my = pygame.mouse.get_pos()
        for i, nombre in enumerate(nombres):
            rect = pygame.Rect(bx, by0 + i * 64, bw, bh)
            self._botones_menu.append((rect, i))
            hover = rect.collidepoint(mx, my)
            color_bg = C.AMBAR if hover else (30, 40, 70)
            color_borde = C.BLANCO if hover else C.GRIS_CLARO
            pygame.draw.rect(self.pantalla, color_bg, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, color_borde, rect, 2, border_radius=8)
            txt = self.f_normal.render(nombre, True, C.NEGRO if hover else C.BLANCO)
            self.pantalla.blit(txt, (rect.centerx - txt.get_width() // 2,
                                     rect.centery - txt.get_height() // 2))
        hint = self.f_pequena.render(
            "Clic en un nivel  |  ENTER = Nivel 1  |  Teclas 1 2 3",
            True, C.GRIS_CLARO)
        self.pantalla.blit(hint, (C.ANCHO // 2 - hint.get_width() // 2, C.ALTO - 90))
        info = self.f_pequena.render(
            "WASD mover / ESPACIO linterna / SHIFT sprint / E interactuar",
            True, C.GRIS_CLARO)
        self.pantalla.blit(info, (C.ANCHO // 2 - info.get_width() // 2, C.ALTO - 55))

    def _dibujar_intro(self):
        assert self.nivel is not None
        self.pantalla.fill(C.AZUL_NOCTURNO)
        y = 150
        for i, linea in enumerate(self.nivel.mensaje_intro.split("\n")):
            fuente = self.f_media if i == 0 else self.f_normal
            color  = C.AMBAR if i == 0 else C.BLANCO
            txt = fuente.render(linea, True, color)
            self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, y))
            y += 45
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            txt = self.f_normal.render("Presiona ENTER para comenzar", True, C.GRIS_CLARO)
            self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, C.ALTO - 100))

    def _dibujar_juego(self):
        assert self.nivel is not None
        assert self.mapa is not None
        assert self.jugador is not None
        assert self.linterna is not None
        assert self.camara is not None
        offset = self.shake.offset()
        mundo = pygame.Surface((C.ANCHO, C.ALTO))
        mundo.fill(C.AZUL_PROFUNDO)
        self.mapa.dibujar_fondo(mundo, self.camara)
        if self.mostrar_debug:
            self.mapa.dibujar_debug(mundo, self.camara)
        for f in self.nivel.faroles:
            f.dibujar(mundo, self.camara)
        if self.nivel.restaurante_rect:
            r = self.camara.aplicar(self.nivel.restaurante_rect)
            mundo.blit(self.img_restaurante, r.topleft)
            pygame.draw.rect(mundo, C.AMBAR, r, 2)
        for s in self.nivel.saltenas:
            s.dibujar(mundo, self.camara)
        if self.nivel.cliente:
            self.nivel.cliente.dibujar(mundo, self.camara, self.jugador.tiene_paquete)
        for e in self.nivel.enemigos:
            e.dibujar(mundo, self.camara)
        self.jugador.dibujar(mundo, self.camara)
        self.linterna.dibujar(mundo, self.camara, self.jugador.rect)
        jug_p = self.camara.aplicar_punto(self.jugador.rect.centerx, self.jugador.rect.centery)
        focos = [(jug_p[0], jug_p[1], 130)]
        for f in self.nivel.faroles:
            fx, fy = self.camara.aplicar_punto(f.centro.x, f.centro.y)
            focos.append((fx, fy, f.radio))
        self.oscuridad.dibujar(mundo, focos)
        self.pantalla.blit(mundo, (offset[0], offset[1]))
        self.vignette.dibujar(self.pantalla)
        self.parpadeo.dibujar(self.pantalla)
        self._dibujar_hud()

    def _dibujar_hud(self):
        assert self.nivel is not None
        assert self.jugador is not None
        pygame.draw.rect(self.pantalla, (20, 20, 30), (0, 0, C.ANCHO, 6))
        pygame.draw.rect(self.pantalla, (20, 20, 30), (0, C.ALTO - 6, C.ANCHO, 6))
        pygame.draw.rect(self.pantalla, (20, 20, 30), (0, 0, 6, C.ALTO))
        pygame.draw.rect(self.pantalla, (20, 20, 30), (C.ANCHO - 6, 0, 6, C.ALTO))
        panel = pygame.Surface((C.ANCHO - 20, 90), pygame.SRCALPHA)
        panel.fill((10, 12, 25, 200))
        self.pantalla.blit(panel, (10, 10))
        self._barra(20, 20, 200, 18, self.grasa / C.JUGADOR_GRASA_MAX,
                    (200, 40, 40), f"GRASA {int(self.grasa)}%")
        self._barra(20, 50, 200, 18, self.bateria / C.JUGADOR_BATERIA_MAX,
                    C.AMBAR, f"BATERIA {int(self.bateria)}%")
        m = int(self.nivel.tiempo_restante) // 60
        s = int(self.nivel.tiempo_restante) % 60
        t = self.f_normal.render(f"TIEMPO {m:02d}:{s:02d}", True, C.BLANCO)
        self.pantalla.blit(t, (C.ANCHO // 2 - 60, 25))
        t2 = self.f_normal.render(
            f"ENTREGAS {self.nivel.entregas_realizadas}/{self.nivel.entregas_objetivo}",
            True, C.BLANCO)
        self.pantalla.blit(t2, (C.ANCHO // 2 - 60, 55))
        t3 = self.f_normal.render(f"PTS {self.puntos}", True, C.AMBAR)
        self.pantalla.blit(t3, (C.ANCHO - 160, 25))
        if self.nivel.combo > 1:
            t4 = self.f_media.render(f"COMBO x{self.nivel.combo}", True, C.AMBAR)
            self.pantalla.blit(t4, (C.ANCHO - 200, 55))
        t5 = self.f_pequena.render(
            f"Nivel {self.nivel.numero}: {self.nivel.nombre}", True, C.GRIS_CLARO)
        self.pantalla.blit(t5, (20, 105))
        if self.jugador.tiene_paquete:
            txt = self.f_normal.render("LLEVAS EL PAQUETE - ENTREGA CON E", True, C.AMBAR)
            self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, C.ALTO - 50))
        dist = self.nivel.distancia_al_enemigo_mas_cercano(self.jugador.rect)
        if dist < 200:
            alpha = int(255 * (1 - dist / 200))
            ov = pygame.Surface((C.ANCHO, C.ALTO), pygame.SRCALPHA)
            ov.fill((180, 0, 0, alpha // 4))
            self.pantalla.blit(ov, (0, 0))

    def _barra(self, x, y, ancho, alto, ratio, color, etiqueta):
        pygame.draw.rect(self.pantalla, (40, 40, 55), (x, y, ancho, alto))
        pygame.draw.rect(self.pantalla, color, (x, y, int(ancho * ratio), alto))
        pygame.draw.rect(self.pantalla, C.BLANCO, (x, y, ancho, alto), 2)
        txt = self.f_pequena.render(etiqueta, True, C.BLANCO)
        self.pantalla.blit(txt, (x + 6, y + 2))

    def _dibujar_pausa(self):
        ov = pygame.Surface((C.ANCHO, C.ALTO), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.pantalla.blit(ov, (0, 0))
        txt = self.f_titulo.render("PAUSA", True, C.BLANCO)
        self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, 200))
        t1 = self.f_normal.render("ESC - Reanudar", True, C.BLANCO)
        t2 = self.f_normal.render("M - Volver al menu", True, C.BLANCO)
        self.pantalla.blit(t1, (C.ANCHO // 2 - t1.get_width() // 2, 300))
        self.pantalla.blit(t2, (C.ANCHO // 2 - t2.get_width() // 2, 340))

    def _dibujar_game_over(self):
        try:
            fondo = cargar_imagen("fondos/fondo_gameover", (C.ANCHO, C.ALTO), alpha=False)
            self.pantalla.blit(fondo, (0, 0))
        except Exception:
            self.pantalla.fill((40, 0, 0))
        ov = pygame.Surface((C.ANCHO, C.ALTO), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 120))
        self.pantalla.blit(ov, (0, 0))
        txt = self.f_titulo.render("GAME OVER", True, C.ROJO_SANGRE)
        self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, 150))
        sub = self.f_media.render(
            f"El Kari-Kari te atrapo... (Puntos: {self.puntos})", True, C.BLANCO)
        self.pantalla.blit(sub, (C.ANCHO // 2 - sub.get_width() // 2, 240))
        t1 = self.f_normal.render("R - Reintentar nivel", True, C.BLANCO)
        t2 = self.f_normal.render("M - Volver al menu", True, C.BLANCO)
        self.pantalla.blit(t1, (C.ANCHO // 2 - t1.get_width() // 2, 340))
        self.pantalla.blit(t2, (C.ANCHO // 2 - t2.get_width() // 2, 380))

    def _dibujar_nivel_completado(self):
        assert self.nivel is not None
        self.pantalla.fill(C.AZUL_NOCTURNO)
        txt = self.f_titulo.render("NIVEL COMPLETADO", True, C.VERDE)
        self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, 150))
        sub = self.f_media.render(self.nivel.nombre, True, C.AMBAR)
        self.pantalla.blit(sub, (C.ANCHO // 2 - sub.get_width() // 2, 240))
        info = self.f_normal.render(f"Puntos totales: {self.puntos}", True, C.BLANCO)
        self.pantalla.blit(info, (C.ANCHO // 2 - info.get_width() // 2, 300))
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            t = self.f_normal.render("ENTER - Siguiente nivel", True, C.BLANCO)
            self.pantalla.blit(t, (C.ANCHO // 2 - t.get_width() // 2, 420))

    def _dibujar_victoria(self):
        self.pantalla.fill((20, 0, 40))
        txt = self.f_titulo.render("VENCISTE AL KARI-KARI", True, C.AMBAR)
        self.pantalla.blit(txt, (C.ANCHO // 2 - txt.get_width() // 2, 150))
        sub = self.f_media.render(
            "Sdenka entrego todos los pedidos y sobrevivio la noche", True, C.BLANCO)
        self.pantalla.blit(sub, (C.ANCHO // 2 - sub.get_width() // 2, 240))
        info = self.f_normal.render(f"PUNTUACION FINAL: {self.puntos}", True, C.VERDE)
        self.pantalla.blit(info, (C.ANCHO // 2 - info.get_width() // 2, 320))
        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            t = self.f_normal.render("ENTER - Volver al menu", True, C.BLANCO)
            self.pantalla.blit(t, (C.ANCHO // 2 - t.get_width() // 2, 450))