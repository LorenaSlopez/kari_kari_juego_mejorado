# Kari-Kari: Delivery Night

Survival top-down ambientado en el Casco Viejo de La Paz, organizado por niveles.

## Estructura de carpetas

```
kari_kari_juego/
├── main.py                 # Punto de entrada — ejecuta este archivo
├── requirements.txt
├── README.md
└── src/
    ├── config.py            # Constantes: tamaño de ventana, colores, FPS
    ├── estados.py            # Enum con las pantallas del juego (menú, jugando, pausa...)
    ├── juego.py               # Clase Juego: bucle principal, pantallas y progreso de niveles
    ├── entidades/
    │   ├── jugador.py         # Movimiento y dibujo de Sdenka
    │   ├── linterna.py        # Batería, encendido y haz de luz
    │   ├── farol.py            # Zonas seguras que recargan batería/grasa
    │   └── kari_kari.py       # IA del enemigo (patrulla / persecución / aturdido)
    └── niveles/
        ├── nivel_base.py      # Clase base: define qué datos tiene un nivel
        ├── nivel_1.py          # Nivel 1: "El primer pedido"
        ├── nivel_2.py          # Nivel 2: "Callejones del Casco Viejo"
        └── nivel_3.py          # Nivel 3: "Noche cerrada"
```

## Cómo correr el juego

```bash
pip install -r requirements.txt
python main.py
```

## Controles

| Tecla | Acción |
|---|---|
| WASD / Flechas | Mover |
| ESPACIO (mantener) + apuntar con el mouse | Linterna |
| E | Recoger / entregar paquete |
| ESC | Pausar / reanudar |
| ENTER | Iniciar / avanzar de nivel |
| R | Reintentar nivel tras Game Over |
| M | Volver al menú (en pausa o Game Over) |

## Cómo agregar un nivel nuevo

1. Crea `src/niveles/nivel_4.py` copiando la estructura de `nivel_3.py`.
2. Define ahí una clase `Nivel4(NivelBase)` con sus propios:
   - `numero`, `nombre`, `mensaje_intro`
   - `duracion` (segundos) y `entregas_objetivo`
   - `faroles_pos` (lista de `(x, y)` o `(x, y, radio)`)
   - `restaurante_pos` y `zona_cliente` (rectángulo donde puede aparecer el cliente)
   - `enemigos_spawn` (lista de `(x, y, velocidad_base, radio_deteccion)`, uno por cada Kari-Kari)
   - `salteñas_iniciales` y `salteñas_max`
3. En `src/niveles/__init__.py`, importa `Nivel4` y agrégalo a `LISTA_NIVELES`.

No hace falta tocar `juego.py`: la clase `Juego` recorre `LISTA_NIVELES` automáticamente.

## Próximos pasos sugeridos

- Sprites PNG y animaciones para Sdenka, el Kari-Kari y los faroles.
- Tilemap del Casco Viejo en vez de fondo liso.
- Audio: música synthwave + charangos, SFX de pasos y aturdimiento.
- Empaquetado con PyInstaller (Windows) o pygbag (Web).
