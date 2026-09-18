---
proyecto: Neuroteca
tipo: protocolo-de-sesion
version: "1.0"
ultima_actualizacion: 2026-09-17
---

# Protocolo de sesión

Este proyecto asume que **cada sesión la atiende un agente distinto, sin memoria de las
anteriores**. Lo único que viaja entre sesiones son los archivos.

Por eso el método vive o muere en el traspaso. Un hito bien diseñado que se pierde porque
nadie escribió dónde quedó, se pierde igual que si no se hubiera hecho.

**Definición:** una **sesión** es una conversación de trabajo, de principio a fin, con un
agente. Termina cuando Max la cierra, cuando el agente se queda sin contexto, o cuando se
completa lo que se iba a hacer.

**Una sola sesión abierta a la vez.** Si Max abre una segunda en paralelo, esa segunda es
de **solo lectura**: puede consultar y responder, pero no escribe ningún archivo. Dos
agentes escribiendo `estado.md` a la vez producen discrepancias sin causa detectable.

**Una sesión trabaja en un solo carril.** Software o contenido, no los dos. Si a mitad de
una sesión de software aparece trabajo de contenido, va al backlog o abre sesión propia.

---

## 0. Sesión ligera

No todo trabajo justifica el ritual completo. Una **sesión ligera** existe para las
interacciones de treinta segundos — anotar una idea, consultar dónde va algo, responder una
pregunta — porque si la única puerta de entrada fuera la sesión normal, Max la va a saltar,
y un método que se salta a escondidas es peor que no tener método: la degradación es
invisible.

| | Sesión ligera | Sesión normal |
|---|---|---|
| **Lectura obligatoria** | `EMPIEZA-AQUI.md` + `estado.md` | Los 12 documentos del orden |
| **Reporte de orientación** | No | Sí, y se espera el `sigue` |
| **Puede escribir en** | `backlog.md`, `preguntas.md` y una línea en la bitácora | Lo que la fase o el paso requiera |
| **Puede tocar** | Nada de hitos, lotes, fases ni compuertas | Todo |
| **Cierre** | Una línea en la bitácora y su índice | Protocolo completo (§2) |

> **Disparador de aborto:** si en una sesión ligera aparece cualquier cosa que toque un
> hito, un lote, una fase o una compuerta, **se aborta y se abre una sesión normal.** El
> agente lo dice explícitamente: *"esto ya no es una sesión ligera"*.

Formato de la línea en la bitácora:
`## S-NN — AAAA-MM-DD — <agente> — LIGERA — <qué se anotó>`

---

## 1. Apertura de sesión

1. Leer `EMPIEZA-AQUI.md` y seguir su orden de lectura obligatorio.
2. Entregar el **reporte de orientación** (formato en `EMPIEZA-AQUI.md`).
3. **Esperar el `sigue` de Max.** No escribir ni construir nada antes.
4. Registrar la sesión abierta en `bitacora/`.

### Verificación cruzada obligatoria

Antes de dar por buena tu orientación, comprueba que estas tres fuentes coinciden:

- Lo que dice `estado.md`
- Lo que dicen los documentos de fase del hito vivo (o el encuadre del lote vivo)
- Lo que dice la última entrada de la bitácora

**Si no coinciden, no elijas una y sigas.** Repórtalo en el punto 5 del reporte y deja que
Max decida. Una discrepancia aquí casi siempre significa que la sesión anterior no cerró
bien.

---

## 2. Cierre de sesión

**Obligatorio siempre**, aunque el trabajo haya quedado a la mitad — sobre todo si quedó a
la mitad. Ejecútalo *antes* de que se acabe la sesión, no cuando ya no quede espacio.

1. **Actualizar `estado.md`:** carril, pieza, hito o lote, fase o paso, compuerta
   pendiente, qué falta para cruzarla, siguiente acción concreta.
2. **Aplicar el techo duro.** Si `estado.md` pasa de 150 líneas o `preguntas.md` de 100,
   mover lo más antiguo a `historial/`. **El cierre no está completo si algún techo quedó
   rebasado** — es verificable con `wc -l`.
3. **Agregar entrada a `bitacora/AAAA-TN.md`** con el formato de abajo, y **una línea a
   `bitacora/INDICE.md`**.
4. **Si estabas en fase 3:** marcar en `03-bitacora-construccion.md` qué pasos quedaron
   completados y cuál a medias, y registrar las `DC-NN` tomadas.
5. **Si estabas en fase 1 o 2:** guardar el documento de fase con lo avanzado, aunque esté
   incompleto, marcando explícitamente qué secciones faltan.
6. **Si estabas en un lote:** marcar en qué paso quedó y qué fichas o activos están hechos.
7. **Tomar el snapshot** (`git commit`) si la sesión cruzó una compuerta B o C, o si dejó
   cambios en el código o el contenido. Un commit de más no estorba; uno de menos puede
   costar el trabajo entero.
8. **Entregar a Max el resumen de cierre:**

```
CIERRE DE SESIÓN
- Qué se hizo: <lista corta>
- Dónde quedó exactamente: <carril / pieza / hito o lote / fase o paso>
- Siguiente acción para la próxima sesión: <una, concreta>
- Bloqueado por: <o "nada">
- Archivos que modifiqué: <lista>
- Techos: estado.md <N>/150 · preguntas.md <N>/100
- Archivos que NO pude escribir y necesito que guardes tú: <o "ninguno">
```

### Formato de entrada en la bitácora

```markdown
## S-NN — AAAA-MM-DD — <agente/plataforma>

- **Carril / pieza / hito o lote / fase o paso:** <>
- **Qué se hizo:** <>
- **Dónde quedó:** <>
- **Siguiente acción:** <>
- **Bloqueado por:** <>
- **Archivos modificados:** <>
```

### Formato de línea en `INDICE.md`

`| S-NN | AAAA-MM-DD | <agente> | <carril> | <qué se hizo en ocho palabras> |`

---

## 3. Reanudación a media fase

Si la sesión anterior se cortó en medio del trabajo:

**La verdad está en los archivos, no en lo que parezca lógico.**

- **Fase 3 interrumpida:** la fuente es la tabla de avance por paso de
  `03-bitacora-construccion.md`. Antes de continuar, **verifica que el paso anterior de
  verdad produjo lo que dice que produjo.** Un paso marcado como completado por una sesión
  que se cortó puede no estarlo.
- **Fase 1 o 2 interrumpida:** la fuente es el documento de fase. Las secciones vacías o
  marcadas como faltantes son el trabajo pendiente. No des por cerrada una compuerta cuyas
  casillas no estén marcadas.
- **Lote interrumpido:** la fuente es `C0-encuadre.md` y lo que exista en `contenido/`.
  Una ficha en `borrador` es trabajo del paso 1 sin verificar, nunca contenido publicable.
- **Si no hay entrada de cierre de la sesión anterior:** trátalo como discrepancia y
  repórtalo. Reconstruye el estado leyendo los documentos, pero **deja constancia de que lo
  reconstruiste en vez de heredarlo**.

---

## 4. Precedencia entre documentos

Cuando dos documentos se contradigan, esta es la jerarquía:

| Sobre... | Manda |
|---|---|
| El estado actual del proyecto | `estado.md` |
| Qué es el atlas y cómo está hecho | `motor/arquitectura.md` |
| Cómo se estructura el contenido | `motor/esquema-contenido.md` |
| Cómo se trabaja | `00-metodo/README.md` |
| Cómo decide el agente sin preguntar | `00-metodo/reglas-del-agente.md` |
| Qué incluye un hito concreto | Los documentos de fase de ese hito |
| **La redacción exacta de una compuerta** | `00-metodo/README.md` |
| **El formato de un documento de fase** | Su plantilla en `00-metodo/plantillas/` |

Reglas adicionales:

- **Lo específico gana sobre lo general.** Un documento de fase manda sobre el método en lo
  que toca a ese hito, salvo que contradiga una compuerta.
- **Un archivo gana sobre el chat, siempre.** Lo que se haya conversado y no se haya
  escrito, no existe.
- **El repositorio gana sobre cualquier copia.** Si el mismo documento existe en dos
  soportes y difieren, manda el repositorio. Las copias son espejos, nunca fuentes.
  Repórtalo igual: una copia desactualizada significa que alguna sesión no cerró bien.
- **Una contradicción se reporta, no se resuelve en silencio.** Aunque parezca obvia cuál
  gana.

---

## 5. Si no puedes escribir archivos

Algunas plataformas dan lectura pero no escritura sobre el disco de Max.

1. **Decláralo en el reporte de orientación**, punto 6.
2. Cuando toque escribir, **entrega el contenido completo del archivo** en el chat, con su
   ruta, listo para copiar y pegar. Nunca un fragmento ni un resumen.
3. **No marques nada como hecho hasta que Max confirme que lo guardó.**
4. En el cierre, lista explícitamente lo que quedó pendiente de guardar.

> Esta es la falla silenciosa más peligrosa del arranque en frío: un agente que "actualiza
> `estado.md`" en su respuesta, Max no lo guarda, y la siguiente sesión lee un estado viejo
> creyendo que es el actual.

---

## 6. Qué NO hace una sesión

- **No empieza a trabajar sin el `sigue` de Max.**
- **No termina sin ejecutar el cierre.**
- **No inventa contexto.** Ver la regla número uno en `EMPIEZA-AQUI.md`.
- **No cruza una compuerta por su cuenta.** Las cinco compuertas las aprueba Max, incluidas
  la C y la V — que son las salidas de las fases donde el agente trabajó solo, y por eso
  las que menos puede autocertificarse.
- **No mezcla carriles.**
- **No publica contenido sin compuerta V.** Ni siquiera "provisionalmente".
- **No edita en silencio un documento de fase ya aprobado.** Requiere reapertura.
- **No deja un hito en el limbo.** Si el trabajo se detiene esperando a Max, se marca
  `Bloqueado (esperando a Max)` en `estado.md`, diciendo qué se espera, y la pregunta se
  escribe en `preguntas.md`.
- **No decide por Max en fase 1 o 2.** Ahí las decisiones se cierran preguntando; la
  autonomía del agente aplica en la fase 3.

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | 2026-09-17 | Versión inicial. Adaptado del protocolo de MIA v1.3, con techo duro, carriles y bitácora particionada. |
