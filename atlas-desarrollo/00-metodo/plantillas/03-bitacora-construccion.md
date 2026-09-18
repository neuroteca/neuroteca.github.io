---
proyecto: Atlas Neuronal
pieza: motor | <nombre de pieza>
hito: vX.Y-<nombre>
tipo: bitacora-construccion
fase: 3
version: "1.0"
ultima_actualizacion: AAAA-MM-DD
estado_compuerta_C: Pendiente
---

# Fase 3 — Bitácora de construcción · vX.Y «<nombre>»

> Aquí solo se ejecuta el plan de la fase 2. El agente construye de corrido, sin consultar,
> salvo las **3 excepciones**. Cada decisión que tenga que tomar se registra abajo.
>
> **Este archivo es la fuente de verdad si la sesión se corta.** Un paso marcado como
> completado por una sesión que se cortó puede no estarlo: antes de continuar, verifica que
> el paso anterior de verdad produjo lo que dice.

## Avance por paso

| # | Paso | Estado | Evidencia |
|---|---|---|---|
| 1 | <del plan de la fase 2> | Pendiente / En curso / Completado | <qué se puede mirar para confirmarlo> |
| 2 | | Pendiente | |

**Pasos presupuestados:** <N> · **Límite de partición (1.5×):** <N × 1.5> · **Ejecutados:** <N>

> Si los ejecutados rebasan el límite, **el agente se detiene y aplica el procedimiento de
> partición** (`00-metodo/README.md` → Parte II). No se pide extensión: se parte.

## Decisiones de construcción

> Formato obligatorio. El campo "cómo revertir" no es adorno: es lo que permite que Max
> acepte que el agente decida solo, sabiendo que nada queda atrapado.

- **[DC-01]** <Qué se decidió, en una línea.>
  - **Por qué surgió:** <qué hueco apareció>
  - **Opciones:** <A / B>
  - **Elegida y razón:** <A, porque aplica la prioridad 2 (reversible)>
  - **Cómo revertir:** <qué habría que cambiar si estuvo mal>

## Excepciones que detuvieron la construcción

> Si esta tabla no está vacía, la **meta-revisión del método es obligatoria** en la fase 5:
> significa que a la fase 2 le faltó prever algo.

| # | Tipo (1/2/3) | Qué pasó | Qué decidió Max | Fecha |
|---|---|---|---|---|
| — | — | — | — | — |

## Compuerta C

- [ ] Todos los criterios de aceptación **vigentes** se cumplen, verificados uno por uno.
- [ ] La bitácora de construcción está completa.
- [ ] **Publicado y verificado en el sitio real**: se abrió la URL de GitHub Pages y se
      comprobó ahí al menos un `CA`, y la carga en móvil.
- [ ] El peso real del sitio publicado está medido y dentro del presupuesto.
- [ ] Si es pieza: `CA-A1` y `CA-A2` probados de verdad (apagándola y rompiéndola), y
      `piezas.md` actualizado.
- [ ] Si cambió el esquema: `esquema-contenido.md` y `arquitectura.md` actualizados.
- [ ] **Snapshot tomado** (`git commit`) y **etiqueta `vX.Y`** creada.
- [ ] **Max aprobó el cierre de la construcción.**

> **"Funciona en mi máquina" no cruza esta compuerta.** El atlas existe para que lo use
> gente en la web; hasta que no está en la web, el hito no terminó.

**Aprobado por Max el:** AAAA-MM-DD

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | AAAA-MM-DD | Versión inicial |
