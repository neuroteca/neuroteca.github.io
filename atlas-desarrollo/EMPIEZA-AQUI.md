---
proyecto: Atlas Neuronal
tipo: punto-de-entrada
version: "1.0"
ultima_actualizacion: 2026-09-17
---

# EMPIEZA AQUÍ

**Si eres un agente y es tu primera vez en este proyecto: este archivo es lo primero que
lees, y no haces nada más hasta terminar el procedimiento de abajo.**

Este proyecto está diseñado para que cualquier agente, sin memoria de conversaciones
previas y sin contexto de ningún tipo, pueda operarlo únicamente con estos archivos.
**Si algo no está escrito aquí, no existe.**

---

## Qué es esto

`atlas-desarrollo/` contiene **el proceso de construcción del atlas**, no el atlas.

El **Atlas Neuronal** es un atlas interactivo de neuroanatomía y neurofisiología juntas,
de acceso libre, publicado en GitHub Pages y usable sin conocimientos de programación.
Es **didáctico y esquemático**: no es una referencia clínica ni quirúrgica.

Se construye en dos carriles que avanzan en paralelo:

| Carril | Qué produce | Unidad de trabajo | Ciclo |
|---|---|---|---|
| **Software** | La aplicación: motor y piezas | **Hito** `vX.Y-<nombre>` | 5 fases, 4 compuertas (A–D) |
| **Contenido** | Fichas neuro y activos visuales | **Lote** `L-NNN` | 4 pasos, 1 compuerta (V) |

Qué es el atlas por dentro está en `motor/arquitectura.md`. Si ese archivo dice que algo
no está definido, **no lo inventes.**

---

## Regla número uno

> **Lo que no está escrito no está decidido.**
>
> No asumas. No completes huecos con lo que "tendría sentido". No digas "como habíamos
> quedado" ni "según recuerdo": no tienes memoria, solo tienes estos archivos.
>
> Si falta información, se registra como decisión abierta y se pregunta. Nunca se rellena
> en silencio.

---

## Orden de lectura obligatorio

Léelos en este orden, completos. No te saltes ninguno.

| # | Archivo | Para qué |
|---|---|---|
| 1 | `EMPIEZA-AQUI.md` | Este archivo |
| 2 | `estado.md` | **Dónde está el proyecto ahora.** Manda sobre cualquier otra cosa respecto al estado |
| 3 | `00-metodo/glosario.md` | Qué significan las palabras en este proyecto |
| 4 | `00-metodo/README.md` | El método: los dos carriles, las fases y las compuertas |
| 5 | `00-metodo/protocolo-de-sesion.md` | Cómo se abre, se cierra y se retoma una sesión |
| 6 | `00-metodo/reglas-del-agente.md` | Cómo decides sin preguntar |
| 7 | `motor/arquitectura.md` | Qué es el atlas y cómo está hecho hoy |
| 8 | `motor/esquema-contenido.md` | Cómo se estructura el contenido. **Obligatorio si vas a tocar contenido** |
| 9 | `bitacora/INDICE.md` + **la última entrada** del periodo en curso | Dónde quedó la sesión anterior |
| 10 | `piezas.md` | Qué piezas existen y en qué estado |
| 11 | `preguntas.md` | Qué está esperando respuesta de Max |
| 12 | `backlog.md` | Qué está aparcado (para no volver a proponerlo) |

Si vas a trabajar en un hito ya empezado, lee además todos los documentos de fase de ese
hito, en orden numérico. Si vas a trabajar en un lote de contenido, lee su `C0-encuadre.md`.

> **La bitácora no se lee entera nunca.** Se lee `bitacora/INDICE.md` y la última entrada
> del archivo del periodo en curso. El histórico está ahí por si se necesita, no para
> cargarlo de rutina.

> **Si solo vienes a anotar una idea o a consultar algo**, existe la **sesión ligera** en
> `00-metodo/protocolo-de-sesion.md` §0: lees solo este archivo y `estado.md`, y te
> saltas el reporte. No aplica si vas a tocar un hito, un lote, una fase o una compuerta.

---

## Reporte de orientación

Cuando termines de leer, **antes de hacer absolutamente nada más**, entrega esto a Max y
espera su visto bueno. No empieces a trabajar sin él.

```
REPORTE DE ORIENTACIÓN

1. Documentos leídos: <lista, con la versión de cada uno>
2. Estado del proyecto:
   - Carril: <software | contenido | ninguno>
   - Pieza: <motor | pieza X | ninguna>       (solo carril software)
   - Versión: <vX — propósito en una frase | ninguna>  ·  Estado: <Boceto | En curso>
   - Hito: <vX.Y-nombre | ninguno>  ·  Estado: <En curso | Bloqueado | ninguno>
   - Fase: <1-5 | ninguna>
   - Lote de contenido: <L-NNN | ninguno>  ·  Paso: <0-3 | ninguno>
   - Compuerta pendiente: <A/B/C/D/V | ninguna todavía>
3. Qué falta para cruzar esa compuerta: <lista concreta; si no hay compuerta abierta,
   qué faltará para la primera>
4. Siguiente acción que propongo: <una sola, concreta>
5. Contradicciones o huecos que detecté: <o "ninguno">
6. Lo que NO voy a hacer hasta que me confirmes: <lista; indica aquí si NO puedes
   escribir archivos>
```

Notas de formato:

- Si un documento **no tiene campo `version`**, escribe "sin versión". **No inventes un
  número** ni uses la fecha como si lo fuera.
- Si el proyecto está en cero, "ninguna compuerta pendiente" es la respuesta correcta:
  explica cuál será la primera en lugar de forzar una letra.
- Leer archivos que existen pero no están en la tabla **no es desobedecer**: la tabla es
  el mínimo, no el máximo. Decláralos aparte.

Max responde `sigue` (o te corrige). Hasta entonces, no escribes ni construyes nada.

> **Por qué esta parada existe:** si te orientaste mal, Max lo detecta en diez segundos
> en vez de después de horas de trabajo en la dirección equivocada. Es la única
> interrupción obligatoria **antes de empezar** — pero además, **todas las compuertas las
> aprueba Max**, no tú.

---

## Antes de terminar la sesión

**Nunca cierres una sesión sin ejecutar el protocolo de cierre** de
`00-metodo/protocolo-de-sesion.md`. Si no dejas el estado por escrito, el siguiente
agente empieza a ciegas y el método se rompe. Aplica aunque el trabajo haya quedado a la
mitad — sobre todo si quedó a la mitad.

---

## Si no puedes escribir archivos

Algunas plataformas te dejan leer pero no escribir en el disco de Max. Si es tu caso:

- **Dilo en el reporte de orientación**, punto 6.
- Cuando toque escribir un documento, **entrega su contenido completo** en el chat, con
  su ruta, listo para copiar y pegar. Nunca un fragmento ni un resumen.
- **Nunca marques como hecho algo que no escribiste.** Si Max no confirmó que lo guardó,
  sigue pendiente.

> Esta es la falla silenciosa más peligrosa: un agente que "actualiza `estado.md`" en su
> respuesta, Max no lo guarda, y la siguiente sesión lee un estado viejo creyendo que es
> el actual.

---

## Mapa de archivos

```
atlas_neuronal/                  ← raíz del repositorio (público)
  CLAUDE.md                      orientación mínima para el agente
  .gitignore                     excluye _referencia/ y las fuentes de modelado
  contenido/                     los datos del atlas (aún no existe)
  src/                           la aplicación (aún no existe)
  _referencia/                   PRIVADO, fuera de git. No se lee salvo que Max lo pida
  atlas-desarrollo/              ← el proceso; se versiona pero NO se publica en Pages
    EMPIEZA-AQUI.md              este archivo
    estado.md                    dónde está el proyecto ahora. TECHO: 150 líneas
    preguntas.md                 lo que espera respuesta de Max. TECHO: 100 líneas
    backlog.md                   todo lo aparcado
    piezas.md                    registro de piezas
    bitacora/
      INDICE.md                  una línea por sesión: fecha, agente, qué se hizo
      AAAA-TN.md                 entradas completas del trimestre en curso
    historial/                   lo que se retiró de estado.md al pasar el techo
    00-metodo/
      README.md                  el método
      glosario.md                qué significan las palabras aquí
      protocolo-de-sesion.md     sesión ligera, apertura, cierre, reanudación
      reglas-del-agente.md       cómo decides sin preguntar
      plantillas/                00-cuestionario … 05-cierre, C0 y C1
    motor/
      arquitectura.md            qué es el atlas (vivo)
      esquema-contenido.md       el contrato de los datos del atlas (vivo)
    piezas/
      <nombre>/ficha.md + hitos/
    lotes/
      L-NNN-<nombre>/            C0-encuadre.md, C1-verificacion.md
```

**Todo archivo que exista en el disco y no esté en este mapa es un hallazgo:** repórtalo
en el punto 5 del reporte de orientación.

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | 2026-09-17 | Versión inicial. Adaptada del método de MIA v3.10. |
