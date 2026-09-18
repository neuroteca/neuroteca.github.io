---
proyecto: Neuroteca
tipo: glosario
version: "1.1"
ultima_actualizacion: 2026-09-18
---

# Glosario

Estas palabras se usan aquí en un sentido **específico**, distinto del coloquial. Un agente
que las interprete a su manera va a sonar como si entendiera el proyecto sin entenderlo.

---

## El producto

**Neuroteca** — El proyecto: *atlas vivo del sistema nervioso*. Atlas interactivo de neuroanatomía y neurofisiología juntas,
de acceso libre, publicado en GitHub Pages y usable sin conocimientos de programación. Es
**didáctico y esquemático**, no una referencia clínica ni quirúrgica. Qué es en concreto
está en `motor/arquitectura.md`; si ahí está vacío, **no está definido y no se inventa**.

**Motor** — El armazón del atlas: navegación, carga de datos, tema visual, y las reglas que
deben cumplir las piezas. Hay uno solo.

**Pieza** — Una **capacidad** de la aplicación, autocontenida, que se enchufa al motor
(visor anatómico, buscador, simulador fisiológico, glosario). Si falla o se apaga, ni el
atlas ni las demás piezas se ven afectados. **Una pieza no es un dominio neuroanatómico:**
la corteza o las vías motoras son contenido, no piezas.

**Esquema de contenido** — El documento que define qué campos tiene una ficha, qué formatos
acepta un activo visual y cómo se declara el nivel de detalle. Es el contrato entre el
contenido y la aplicación, y se versiona **aparte**. Vive en `motor/esquema-contenido.md`.
Ninguna pieza se diseña antes de que exista `esquema v1`.

**Aislamiento** — La propiedad de que una pieza pueda fallar o apagarse sin afectar al
resto. No se da por buena por diseño: se prueba rompiendo la pieza a propósito (`CA-A1` y
`CA-A2`).

---

## El contenido

**Ficha** — La unidad de contenido: una estructura neuro con su descripción anatómica, su
función fisiológica, sus fuentes, su autoría y su estado.

**Activo visual** — Un modelo, diagrama, esquema o animación que representa una estructura.
Lleva siempre origen, licencia, nivel de detalle y peso registrados.

**Lote** (`L-NNN-<nombre>`) — La unidad de trabajo del carril de contenido: un conjunto de
estructuras que se redactan, modelan y verifican juntas. Lo que lo define es que comparten
fuente, nivel de detalle y sesión de verificación.

**Nivel de detalle** (`N1`…`N5`) — A qué granularidad está representada hoy una estructura,
de la forma general (`N1`) al circuito (`N5`). Se declara siempre, se muestra al visitante,
y **la verificación se hace contra el nivel declarado, no contra la perfección**. Subir de
nivel una estructura publicada es un lote nuevo, no una corrección.

**Estado de una ficha** — `borrador` (redactada, sin verificar) · `revisado` (cruzó la
compuerta V). Solo lo `revisado` se presenta como bueno en el sitio.

**Autoría** — Quién redactó la ficha: `Max` o `agente`. Se registra por ficha, para saber
después qué texto pasó por el criterio de Max sin tener que revisarlo todo otra vez.

---

## El proceso

**Carril** — Cada una de las dos vías de trabajo: **software** (produce la aplicación) y
**contenido** (produce fichas y activos). Avanzan en paralelo, pero **una sesión trabaja en
un solo carril**.

**Versión** — El contrato de **visión y capacidades** de una pieza: qué hace, a alto nivel
(`X` de `vX.Y`). Se registra como **boceto revisable** y se puede refinar hasta que arranca
su primer hito; a partir de ahí **la visión se mantiene fija** y puede recibir cualquier
número de hitos mientras no la cambien. Cambia a `X+1` cuando se agrega o quita una
capacidad de la visión, o cuando un cambio en otra parte obliga a refactorizarla.
Estados: `Boceto` · `En curso`. *(No existe "Completa": la visión no se termina.)*

**Hito** (`vX.Y-<nombre>`) — Un checkpoint de trabajo **dentro de la visión fija de su
versión**. Se puede **usar completo**, aunque haga poco. Nunca es "la base" ni "media
funcionalidad": es una rebanada vertical que entra por un lado, sale por el otro y sirve.

**Fase** — Cada una de las 5 etapas por las que pasa un hito: Diseño, Especificación,
Construcción, Uso, Cierre.

**Paso** — Cada una de las 4 etapas por las que pasa un lote de contenido: Encuadre,
Redacción y modelado, Verificación, Publicación. *(También: cada fila del plan de
construcción de la fase 2. El contexto lo distingue.)*

**Compuerta** — El punto de control entre dos fases o pasos (`A`, `B`, `C`, `D` en
software; `V` en contenido). Tiene una lista de casillas que deben estar todas marcadas
para avanzar. **Las aprueba Max, no el agente.**

**Alcance congelado** — El estado en que queda un hito tras cruzar la compuerta A. Toda
idea posterior va al backlog, no al hito.

**Reapertura** — El procedimiento para corregir un documento ya aprobado: subir su versión,
anotar el motivo, volver la compuerta a `Pendiente`. Es caro a propósito, y es la única
forma autorizada de cambiar algo congelado.

**Partición** — Lo que ocurre si los pasos ejecutados rebasan 1.5× los presupuestados: se
entrega lo que funciona y el resto pasa a un hito nuevo. **No se pide extensión: se parte.**

**Excepción** — Una de las 3 situaciones en que el agente sí detiene la construcción
(irreversible/destructiva, seguridad o exactitud publicable, cambio de alcance). En
cualquier otro caso decide solo y registra.

**`DC-NN`** — Decisión de construcción: algo que el agente decidió por su cuenta durante la
fase 3, con su razón y cómo revertirla. Al cerrar el hito, las que valga la pena fijar se
promueven a `reglas-del-agente.md`.

**Techo duro** — El límite de tamaño de los archivos que todo agente debe leer al arrancar
(`estado.md`, `preguntas.md`). Al rebasarlo, lo antiguo se mueve a `historial/`. Es lo que
hace que retomar el proyecto cueste igual el primer año que el quinto.

**Sesión** — Una conversación de trabajo, de principio a fin, con un agente. Termina cuando
Max la cierra, cuando el agente se queda sin contexto, o cuando se completa lo previsto.

**Sesión ligera** — Una interacción de treinta segundos (anotar una idea, consultar algo)
que se salta el ritual completo. No puede tocar hitos, lotes, fases ni compuertas.

---

## Palabras que NO significan lo que parece

**"Terminado"** — En el carril software, un hito no está terminado hasta que está
**publicado y verificado en el sitio real**. "Funciona en mi máquina" no cuenta.

**"Exacto"** — Correcto **al nivel de detalle declarado**. Un `N1` correcto no tiene
núcleos dentro, y está bien.

**"Fuente"** — Una obra localizable por un tercero: libro con edición y página, o artículo
con DOI. **Un agente no es una fuente.** Tampoco lo es "es sabido que".

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.1 | 2026-09-18 | El proyecto pasa a llamarse **Neuroteca**. |
| 1.0 | 2026-09-17 | Versión inicial. |
