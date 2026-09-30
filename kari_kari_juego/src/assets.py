"""
Cargador de assets: imagenes y sonidos.
"""
import os
import pygame

RUTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ASSETS = os.path.join(RUTA_RAIZ, "assets")

_cache_img = {}
_cache_sfx = {}
_musica_actual = None
_canal_pasos = None
_canal_susurro = None

TAMANO_FRAME_REF = (168, 92)

ARCHIVOS = {
    "menu":     ["musica_menu.ogg", "musica_menu.mp3", "musica_menu.wav"],
    "nivel":    ["musica_nivel.wav", "musica_nivel.ogg", "musica_nivel.mp3"],
    "linterna": ["linterna.wav", "linterna.ogg"],
    "pasos":    ["pasos.wav", "pasos.ogg"],
    "susurro":  ["susurro.ogg", "susurro.wav"],
    "dano":     ["dano.wav", "dano.ogg"],
    "saltena":  ["saltena.wav", "saltena.ogg"],
    "entrega":  ["entrega.wav", "entrega.ogg"],
    "gameover": ["gameover.wav", "gameover.ogg"],
    "victoria": ["victoria.wav", "victoria.ogg"],
}


def _placeholder(tamano, color=(255, 0, 255)):
    surf = pygame.Surface(tamano, pygame.SRCALPHA)
    surf.fill(color)
    pygame.draw.line(surf, (0, 0, 0), (0, 0), tamano, 2)
    pygame.draw.line(surf, (0, 0, 0), (tamano[0], 0), (0, tamano[1]), 2)
    return surf


def cargar_imagen(ruta_relativa, tamano=None, alpha=True):
    clave = (ruta_relativa, tamano, alpha)
    if clave in _cache_img:
        return _cache_img[clave]

    ruta_base = os.path.join(RUTA_ASSETS, ruta_relativa)
    nombre_sin_ext, ext_original = os.path.splitext(ruta_base)

    candidatos = []
    if ext_original:
        candidatos.append(ruta_base)
    for e in (".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ""):
        candidatos.append(nombre_sin_ext + e)

    img = None
    ruta_usada = None
    for ruta in candidatos:
        if os.path.isfile(ruta):
            try:
                img = pygame.image.load(ruta)
                ruta_usada = ruta
                break
            except pygame.error:
                continue

    if img is None:
        print(f"[Assets] No encontrado: {ruta_relativa}")
        img = _placeholder(tamano or (64, 64))
    else:
        es_png = (ruta_usada is not None and ruta_usada.lower().endswith(".png"))
        try:
            img = img.convert_alpha() if (es_png and alpha) else img.convert()
        except pygame.error:
            pass
        if tamano:
            img = pygame.transform.smoothscale(img, tamano)

    _cache_img[clave] = img
    return img


def cargar_spritesheet(ruta, ancho_frame, alto_frame, escala=1.0):
    try:
        hoja = cargar_imagen(ruta)
    except Exception:
        return []
    w, h = hoja.get_size()
    ok = (ancho_frame > 0 and alto_frame > 0
          and w % ancho_frame == 0 and h % alto_frame == 0
          and (w // ancho_frame) >= 2 and (h // alto_frame) >= 2)
    if not ok:
        ow = int(TAMANO_FRAME_REF[0] * escala)
        oh = int(TAMANO_FRAME_REF[1] * escala)
        ratio = min(ow / max(w, 1), oh / max(h, 1))
        return [pygame.transform.smoothscale(
            hoja, (max(1, int(w * ratio)), max(1, int(h * ratio))))]
    frames = []
    for y in range(0, h - alto_frame + 1, alto_frame):
        for x in range(0, w - ancho_frame + 1, ancho_frame):
            frame = hoja.subsurface(pygame.Rect(x, y, ancho_frame, alto_frame)).copy()
            if escala != 1.0:
                frame = pygame.transform.smoothscale(
                    frame, (int(ancho_frame * escala), int(alto_frame * escala)))
            frames.append(frame)
    return frames


def cargar_spritesheet_grid(ruta, columnas, filas, escala=1.0):
    try:
        hoja = cargar_imagen(ruta)
    except Exception:
        return []
    w, h = hoja.get_size()
    if columnas < 1 or filas < 1:
        return []
    fw, fh = w // columnas, h // filas
    if fw < 1 or fh < 1:
        return []
    ow = max(1, int(TAMANO_FRAME_REF[0] * escala))
    oh = max(1, int(TAMANO_FRAME_REF[1] * escala))
    frames = []
    for f in range(filas):
        for c in range(columnas):
            frame = hoja.subsurface(pygame.Rect(c * fw, f * fh, fw, fh)).copy()
            rw, rh = frame.get_size()
            ratio = min(ow / max(rw, 1), oh / max(rh, 1))
            frames.append(pygame.transform.smoothscale(
                frame, (max(1, int(rw * ratio)), max(1, int(rh * ratio)))))
    return frames


def _buscar_archivo(nombres):
    carpetas = [
        os.path.join(RUTA_ASSETS, "sonidos"),
        os.path.join(RUTA_RAIZ, "sonidos"),
        os.path.join(RUTA_ASSETS, "sounds"),
        os.path.join(os.getcwd(), "assets", "sonidos"),
        os.path.join(os.getcwd(), "sonidos"),
    ]
    for carpeta in carpetas:
        if not os.path.isdir(carpeta):
            continue
        for nombre in nombres:
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta):
                return ruta
            try:
                for f in os.listdir(carpeta):
                    if f.lower() == nombre.lower():
                        return os.path.join(carpeta, f)
            except OSError:
                pass
    return None


def init_audio():
    global _canal_pasos, _canal_susurro
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
        _canal_pasos = pygame.mixer.Channel(7)
        _canal_susurro = pygame.mixer.Channel(8)
    except Exception as e:
        print(f"[Audio] ERROR init mixer: {e}")
        return

    print(f"[Audio] RUTA_ASSETS = {RUTA_ASSETS}")
    carpeta = os.path.join(RUTA_ASSETS, "sonidos")
    if os.path.isdir(carpeta):
        try:
            print(f"[Audio] Contenido: {os.listdir(carpeta)}")
        except OSError:
            pass
    else:
        print(f"[Audio] NO EXISTE: {carpeta}")

    for clave, nombres in ARCHIVOS.items():
        ruta = _buscar_archivo(nombres)
        if ruta:
            try:
                snd = pygame.mixer.Sound(ruta)
                _cache_sfx[clave] = snd
                print(f"[Audio] OK  {clave} <- {os.path.basename(ruta)}")
            except Exception as e:
                _cache_sfx[clave] = None
                print(f"[Audio] Error Sound: {e}")
        else:
            _cache_sfx[clave] = None
            print(f"[Audio] FALTA {clave}")


def reproducir(clave, volumen=0.5):
    snd = _cache_sfx.get(clave)
    if snd is None:
        return
    try:
        snd.set_volume(max(0.0, min(1.0, float(volumen))))
        if clave == "susurro":
            global _canal_susurro
            if _canal_susurro is not None:
                _canal_susurro.play(snd)
            else:
                snd.play()
        else:
            snd.play()
    except Exception as e:
        print(f"[Audio] play({clave}) fallo: {e}")


def pasos_actualizar(caminando, volumen=0.4):
    global _canal_pasos
    snd = _cache_sfx.get("pasos")
    if snd is None or _canal_pasos is None:
        return
    try:
        if caminando:
            if not _canal_pasos.get_busy():
                snd.set_volume(max(0.0, min(1.0, float(volumen))))
                _canal_pasos.play(snd, loops=-1)
        else:
            if _canal_pasos.get_busy():
                _canal_pasos.stop()
    except Exception as e:
        print(f"[Audio] pasos error: {e}")


def musica(clave, volumen=0.3, loop=-1):
    global _musica_actual
    ruta = _buscar_archivo(ARCHIVOS.get(clave, []))
    if not ruta:
        print(f"[Audio] Sin musica para '{clave}'")
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volumen))))
        pygame.mixer.music.play(loop)
        _musica_actual = clave
        print(f"[Audio] Musica ON: {clave}")
    except Exception as e:
        print(f"[Audio] music error: {e}")
        _musica_actual = None


def parar_musica():
    global _musica_actual
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    _musica_actual = None


def parar_susurro():
    """Corta el susurro del Kari-Kari al alejarse."""
    global _canal_susurro
    try:
        if _canal_susurro is not None and _canal_susurro.get_busy():
            _canal_susurro.stop()
    except Exception:
        pass


def parar_efectos():
    """Detiene pasos, susurro y cualquier SFX al salir del nivel."""
    global _canal_pasos, _canal_susurro
    try:
        if _canal_pasos is not None:
            _canal_pasos.stop()
    except Exception:
        pass
    try:
        if _canal_susurro is not None:
            _canal_susurro.stop()
    except Exception:
        pass
    try:
        pygame.mixer.stop()
    except Exception:
        pass