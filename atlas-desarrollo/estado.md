---
proyecto: Neuroteca
tipo: estado
version: "2.1"
ultima_actualizacion: 2026-09-18
techo: 150 lineas
---

# Estado de Neuroteca

> **Este archivo describe el presente, no la historia.** Techo duro: 150 líneas. Lo que
> deje de explicar dónde estamos hoy se mueve a `historial/`, aunque haya costado
> escribirlo. El histórico completo está en `bitacora/`.

## Situación general

**El proyecto se llama Neuroteca** — *atlas vivo del sistema nervioso*.

**Paso 0 conversado y primer hito abierto.** La visión de la `v0` es «Ver y entender una
región»; el stack es HTML/CSS/JS estándar con generador propio, sin framework; la primera
región es el **cerebelo**. Todavía no existe código ni contenido.

**Modelo 3D:** se arranca con geometría aproximada por código; Max modela el definitivo en
Blender en paralelo. Por eso la geometría se carga **desde un archivo**, nunca escrita en el
código: reemplazarla será un lote de contenido, no una reescritura.

Decisiones de fondo tomadas: dos carriles (software y contenido), piezas por capacidad de
la aplicación, modelos visuales propios con granularidad creciente, publicación en GitHub
Pages, todo en español, y fuente obligatoria por ficha. **Licencias: código `MIT`,
contenido `CC BY-SA 4.0`**. **Primera rebanada publicable: una región cerebral a nivel `N1`**
con anatomía y fisiología. **El atlas no asume formación previa en neurociencia**: los
fundamentos entran como fichas fundacionales de la pieza `glosario`, y se explica por enlace,
nunca en línea.

## Trabajo vivo

| Carril | Pieza / Lote | Versión | Hito / Paso | Fase | Compuerta | Estado |
|---|---|---|---|---|---|---|
| Software | motor | `v0` | `v0.1-cerebelo` | 2 · Especificación | **B** | Cuestionario esperando a Max |
| Contenido | `L-001-cerebelo` | — | 0 · Encuadre | — | V | Sin arrancar |
| Software | `visor` (pieza) | — | se crea en `v0.1` | — | — | Propuesta |
| Software | `glosario` (pieza) | — | — | — | — | Propuesta |

`v0.1-cerebelo` entrega **la máquina**; el cerebelo lo entrega el lote `L-001-cerebelo` por
el carril de contenido. **La frase de valor no se cumple hasta que ambos crucen su
compuerta.**

## Siguiente acción

**Max responde `motor/hitos/v0.1-cerebelo/00-cuestionario-f2.md`** (cuatro preguntas:
dirección visual, primera vista, cómo se marca el modelo provisional, y listón de realismo
de la geometría). Con eso se integra `02-especificacion.md`, se construye la maqueta de
identidad visual y se cierra la compuerta B.

**Compuerta A aprobada el 2026-09-18: el alcance está congelado.** Toda idea nueva va al
backlog.

## Bloqueos

| Qué | Espera a | Desde |
|---|---|---|
| `esquema-contenido.md` v1 | Se crea dentro de `v0.1-cerebelo` | 2026-09-18 |
| Compuerta B de `v0.1-cerebelo` | Respuestas del cuestionario y maqueta visual aprobada | 2026-09-18 |

No hay preguntas de proyecto abiertas. Las licencias están creadas a nombre de Maximiliano
Alamilla Rodríguez.

**Pendiente de Max, fuera del repositorio:** reservar el identificador `neuroteca` en GitHub
creando una organización gratuita con ese nombre.

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
