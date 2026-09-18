---
proyecto: Atlas Neuronal
tipo: estado
version: "1.1"
ultima_actualizacion: 2026-09-18
techo: 150 lineas
---

# Estado del Atlas Neuronal

> **Este archivo describe el presente, no la historia.** Techo duro: 150 líneas. Lo que
> deje de explicar dónde estamos hoy se mueve a `historial/`, aunque haya costado
> escribirlo. El histórico completo está en `bitacora/`.

## Situación general

**El método está montado; el atlas no ha empezado.** No existe código, ni contenido, ni
arquitectura definida. Lo único que hay es el proceso con el que se va a construir, escrito
en `00-metodo/`, y el repositorio git inicializado.

Decisiones de fondo tomadas: dos carriles (software y contenido), piezas por capacidad de
la aplicación, modelos visuales propios con granularidad creciente, publicación en GitHub
Pages, todo en español, y fuente obligatoria por ficha. **Licencia del código `MIT`**,
**público principal estudiantes de medicina, neurociencia y psicología**, y **primera
rebanada publicable: una región cerebral a nivel `N1`** con anatomía y fisiología.

## Trabajo vivo

| Carril | Pieza / Lote | Versión | Hito / Paso | Fase | Compuerta | Estado |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | Sin trabajo abierto |

**Nada abierto todavía.** El primer trabajo será el hito `v0.1` del motor, y no puede
arrancar hasta que exista `motor/arquitectura.md` con la visión de `v0` escrita.

## Siguiente acción

**Conversar el paso 0 del motor:** qué es el atlas en concreto, qué capacidades tendrá la
`v0`, **qué región cerebral es la primera**, y con qué stack. De esa conversación salen
`motor/arquitectura.md` (tabla de versiones) y la frase de valor del hito `v0.1`.

Quedan dos preguntas abiertas en `preguntas.md` (P-01 licencia del contenido, P-05 nombre
público). **No bloquean el paso 0**, pero el nombre conviene fijarlo antes de publicar nada,
porque cambiarlo después cuesta URLs y citas.

## Bloqueos

| Qué | Espera a | Desde |
|---|---|---|
| Arranque del hito `v0.1` del motor | Conversación del paso 0 con Max | 2026-09-17 |
| `esquema-contenido.md` v1 | La misma conversación (el esquema depende de qué muestra el atlas) | 2026-09-17 |

Las preguntas abiertas están en `preguntas.md`, no aquí. **P-01 y P-05 siguen abiertas.**

## Recordatorios de método

- **Ninguna sesión cierra sin ejecutar el protocolo de cierre**, aunque el trabajo quede a
  la mitad.
- **Los techos son parte del cierre:** `estado.md` ≤ 150 líneas, `preguntas.md` ≤ 100.
  Verificable con `wc -l`.
- **Una sesión, un carril.**
- **`_referencia/` nunca entra a git.** Contiene material privado y este repositorio es
  público.
- **Un hito no está terminado hasta estar publicado y verificado en el sitio real.**
- **Ninguna ficha llega al sitio como `revisado` sin cruzar la compuerta V.**

## Pendientes de método

Dos entregables acordados que aún no se han escrito:

1. **Saneamiento de MIA** — procedimiento para aplicar el techo duro a `estado.md` (3.667
   líneas) y `bitacora-sesiones.md` (12.859 líneas) del proyecto MIA, que ya sufren el
   problema que este método previene.
2. **Método genérico portable** — plantilla neutra, reutilizable en otros proyectos, que
   destile lo que aquí resulte universal (compuertas, barrido de huecos, reglas
   acumulables, techo duro). Se extrae **después** de que este método tenga uso real, no
   antes: solo el uso dice qué partes eran universales.
