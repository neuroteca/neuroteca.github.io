---
proyecto: Atlas Neuronal
tipo: reglas-del-agente
version: "1.1"
ultima_actualizacion: 2026-09-18
---

# Reglas del agente

Este documento existe para que **el agente pueda decidir sin preguntar** durante la fase 3
(Construcción) y el paso 1 de un lote. Cada regla aquí es una pregunta que Max ya no tiene
que responder nunca más.

Es un documento que **crece**: al cerrar cada hito, las decisiones de construcción (`DC-NN`)
que resultaron buenas se promueven aquí para no volver a tomarlas.

**Ratificadas por Max el:** `___________`

> **Mientras ese campo esté vacío, las reglas marcadas 🔧 SON VINCULANTES de todos modos.**
> El 🔧 significa "propuesta del agente que Max aún no revisó", no "pendiente de
> aprobación": un agente que se detenga a preguntar por una regla 🔧 durante la fase 3 está
> rompiendo justamente lo que este documento existe para evitar. Si una regla 🔧 le parece
> mal, la aplica, la registra como `DC-NN` y anota la discrepancia en `backlog.md`.

---

## 1. Orden de prioridades

Cuando dos opciones compiten y ninguna regla concreta aplica, el agente decide en este
orden. La primera que discrimine, gana.

1. 🔧 **Que funcione hoy** por encima de que sea elegante.
2. 🔧 **Reversible** por encima de óptimo. Si una decisión se puede deshacer después, se
   toma la fácil ahora.
3. 🔧 **Simple** por encima de completo. Menos opciones, menos configuración, menos
   pantallas.
4. 🔧 **Consistente con lo que ya existe** por encima de mejor en aislamiento. Si el atlas
   ya hace algo de cierta forma, lo nuevo lo hace igual aunque haya una manera mejor — la
   manera mejor se propone en el backlog.
5. 🔧 **Lo que reduce fricción para el visitante** por encima de lo que se ve impresionante.
   El atlas es para alguien que llega **a estudiar**, no a admirar la interfaz — y que no
   sabe ni tiene que saber programar. El nivel de neurociencia que sí se le supone está en
   §5.

---

## 2. Las 3 excepciones — cuándo sí detenerse

El agente interrumpe la construcción **únicamente** si la decisión:

1. **Es irreversible o destructiva** sobre contenido o datos existentes — incluye todo
   cambio rompiente del esquema de contenido.
2. **Toca seguridad, privacidad o exactitud publicable**: datos de terceros, o cualquier
   afirmación neurocientífica que llegaría al sitio sin pasar por la compuerta V.
3. **Cambia el alcance** de la fase 1: agrega o quita una función, vuelve imposible un
   criterio de aceptación, **invalida el plan de construcción de la fase 2** (hay que
   reordenar, fusionar o sustituir pasos), o **requiere del motor algo que no da**.

En cualquier otro caso, el agente decide, registra `DC-NN` y continúa.

Cuando sí se detiene, lo hace así: presenta **el problema, las opciones, su recomendación y
qué se rompe con cada una** — en un solo mensaje. Nunca pregunta abierto ("¿qué
prefieres?") sin traer opciones cerradas.

---

## 3. Defaults técnicos

> **El stack del atlas todavía no está decidido.** Se decide en el primer hito del motor y
> se escribe en `motor/arquitectura.md`. Las reglas de esta sección son las que aplican
> **independientemente del stack**; no asumas ninguna tecnología concreta que no esté en
> ese archivo.

- 🔧 **El sitio es estático.** GitHub Pages sirve archivos: no hay servidor propio, no hay
  base de datos, no hay proceso en el servidor. Cualquier necesidad que exija backend es
  excepción tipo 3.
- 🔧 **Sin dependencias que no se puedan servir desde el propio repositorio.** Nada de CDN
  de terceros para lo esencial: el atlas debe seguir funcionando si ese CDN desaparece.
- 🔧 **El contenido se carga bajo demanda**, no todo al abrir. El visitante que entra a ver
  una estructura no descarga el atlas entero.
- 🔧 **Ningún activo binario se comitea en iteraciones.** Se itera fuera del repositorio y
  se comitea el export final. Git guarda cada versión entera.
- 🔧 **Toda ruta del sitio debe poder abrirse directamente.** Un enlace a una estructura
  concreta tiene que funcionar pegado en el navegador, no solo navegando desde la portada.
- 🔧 **Nada de analítica, rastreo ni cookies de terceros.** Es un recurso educativo de
  acceso libre; no recoge datos de quien lo visita.
- 🔧 **El contenido vive como datos, no incrustado en el código.** Una ficha se edita sin
  tocar la aplicación, y la aplicación se puede reescribir sin tocar el contenido.

---

## 4. Defaults visuales y de interacción

- 🔧 **Móvil no es opcional.** Todo lo que se construye funciona en teléfono. Lo que no
  pueda, se degrada explícitamente y se dice en la fase 2.
- 🔧 **Toda animación respeta `prefers-reduced-motion`.**
- 🔧 **Contraste mínimo WCAG AA** en texto y en controles.
- 🔧 **Todo lo operable con ratón es operable con teclado.** Sin excepciones.
- 🔧 **Todo activo visual tiene equivalente textual.** Un modelo 3D o un diagrama nunca es
  la única vía de acceso a una información.
- 🔧 **Tema claro y oscuro**, respetando la preferencia del sistema.
- 🔧 **El nivel de detalle se muestra siempre** junto a la estructura representada. El
  visitante nunca tiene que adivinar si lo que ve es esquemático o fino.
- 🔧 **Nada de jerga sin glosario.** El primer uso de un término técnico enlaza a su
  entrada.

---

## 5. Textos e idioma

### Público principal y nivel asumido

*(Decidido por Max — P-04, 2026-09-18. No lleva 🔧: no es propuesta del agente.)*

**El atlas se escribe para estudiantes de medicina, neurociencia y psicología.** Cuando
haya que elegir entre servir a este público o a otro, manda este.

**Se asume sabido** (no se explica, no se enlaza como si fuera novedad): qué son los
neurotransmisores, el potencial de acción, la fisiología **básica** de la neurona, y la
diferencia entre sistema nervioso central y periférico.

**Todo lo demás se explica o se enlaza al glosario.** Ante la duda sobre si algo entra en
los mínimos, se explica: sobra una frase, nunca falta un lector.

> El caso difícil es el estudiante de psicología, que llega con menos base que el de
> medicina. **Es el lector contra el que se escribe**: si él lo entiende, los demás también.

### Forma

- 🔧 **Todo en español**: interfaz, contenido, documentación, nombres de archivo de
  contenido.
- 🔧 **El código en inglés**: nombres de variables, funciones y archivos de código, por
  convención. Los mensajes de commit, en español.
- 🔧 **Terminología anatómica:** se usa el término en español, con el término en latín
  (Terminologia Anatomica) entre paréntesis en la primera mención de cada ficha. Los
  sinónimos y epónimos van en un campo aparte de la ficha, no en el cuerpo.
- 🔧 **Registro:** claro y directo, para alguien que está aprendiendo. Ni infantil ni
  paper. Si una frase necesita leerse dos veces, se reescribe.

---

## 6. Cómo registra el agente sus decisiones

Cada decisión tomada durante la construcción se anota en `03-bitacora-construccion.md` con
este formato:

```markdown
- **[DC-01]** <Qué se decidió, en una línea.>
  - **Por qué surgió:** <qué hueco apareció>
  - **Opciones:** <A / B>
  - **Elegida y razón:** <A, porque aplica la prioridad 2 (reversible)>
  - **Cómo revertir:** <qué habría que cambiar si estuvo mal>
```

El campo "cómo revertir" no es adorno: es lo que permite que Max acepte que el agente
decida solo, sabiendo que nada queda atrapado.

**Verificar, no solo marcar.** Cuando la fase 2 especifica un mecanismo concreto, marcar el
paso como completado no basta: hay que confirmar que el código correspondiente de verdad
quedó escrito y de verdad hace lo que dice.

**Antes de diagnosticar, revisar lo ya sabido.** Cuando un defecto solo se manifiesta en
una plataforma o mecanismo concreto, buscar primero en §3 y §7 de este documento si ya
existe una regla sobre eso, **antes** de generar una hipótesis nueva desde cero.

---

## 7. Reglas promovidas desde hitos y lotes anteriores

*(Al cerrar cada hito o lote, las `DC-NN` que valga la pena fijar se copian aquí con
referencia a su origen. Esta tabla está vacía porque el proyecto aún no ha cerrado ninguno.)*

| Regla | Origen | Fecha |
|---|---|---|
| — | — | — |

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.1 | 2026-09-18 | §5: público principal y nivel de conocimiento asumido (P-04). Decidido por Max, sin 🔧. |
| 1.0 | 2026-09-17 | Versión inicial. Estructura tomada de MIA v3.33; los defaults técnicos y visuales son nuevos, para un sitio estático público y accesible. |
