---
proyecto: Neuroteca
pieza: motor
hito: v0.1-cerebelo
tipo: bitacora-construccion
fase: 3
version: "1.0"
ultima_actualizacion: 2026-09-18
estado_compuerta_C: Pendiente
---

# Fase 3 — Bitácora de construcción · v0.1 «cerebelo»

> Aquí solo se ejecuta el plan de la fase 2, sin consultar, salvo las **3 excepciones**.
>
> **Este archivo es la fuente de verdad si la sesión se corta.** Un paso marcado como
> completado por una sesión que se cortó puede no estarlo: antes de continuar, verifica que
> el paso anterior de verdad produjo lo que dice.

## Avance por paso

| # | Paso | Estado | Evidencia |
|---|---|---|---|
| 1 | Esqueleto del repositorio y `construir.py` | **Completado** | Existen `contenido/`, `src/`, `herramientas/construir.py`. `--validar` corre y devuelve 0 |
| 2 | `esquema v1` y validación; 6 fichas de prueba | **Completado** | `python herramientas/construir.py --validar` → «13 fichas válidas». Probado el fallo: quitar un campo obligatorio o romper un enlace detiene la construcción con código 1 |
| 3 | Plantilla y generación de la página de ficha | Pendiente | |
| 4 | Marcado inline y fallo por enlace sin destino | **Adelantado en el paso 2** | Verificado con un enlace roto a propósito: `[[estructura_inexistente]]` → construcción detenida, código 1, con archivo y campo señalados |
| 5 | Fichas fundacionales de glosario | **Completado** | 7 fichas en `contenido/glosario/`, todas con destino desde las estructuras |
| 6 | Navegación del motor: migas y ejes | Pendiente | |
| 7 | URLs `/estructura/<id>/` y 404 propia | Pendiente | |
| 8 | Estilos desde la maqueta aprobada | Pendiente | |
| 9 | Aviso de entrada e insignias | Pendiente | |
| 10 | `generar-geometria.py` y `cerebelo.glb` | Pendiente | |
| 11 | Vendorizar Three.js; pieza `visor` | Pendiente | |
| 12 | Selección y coloreado por eje | Pendiente | |
| 13 | Degradación y apagado del visor | Pendiente | |
| 14 | Publicar en Pages y verificar en la URL real | Pendiente | Necesita el repositorio remoto (DEP-03) |
| 15 | Medir peso y tiempo reales | Pendiente | |

**Pasos presupuestados:** 15 · **Límite de partición (1.5×):** 22 · **Ejecutados:** 3

> Los pasos 4 y 5 se completaron dentro del 2 porque la validación de enlaces no se puede
> escribir sin enlaces que validar, ni probar sin fichas de glosario a las que apuntar.
> Es adelanto dentro del plan, no cambio del plan: **no toca el presupuesto ni la partición**.

## Decisiones de construcción

- **[DC-01]** Las fichas `fundacional` usan `definicion` y `explicacion` en vez de
  `anatomia` y `fisiologia`.
  - **Por qué surgió:** el esquema exige `anatomia` y `fisiologia` en toda ficha, pero una
    ficha fundacional como «propiocepción» **no tiene anatomía**: es un concepto, no una
    estructura. Con el esquema tal cual, habría que rellenar un campo obligatorio con algo
    falso, que es justo lo que este proyecto no hace.
  - **Opciones:** (A) campos obligatorios según el `tipo`; (B) dejar `anatomia` vacía en las
    fundacionales; (C) sacar el glosario del esquema y darle uno propio.
  - **Elegida y razón:** **A**. (B) obligaría a aflojar la validación para todas las fichas y
    perderíamos la garantía en las de estructura. (C) contradice `DEC-13`, que puso el
    glosario bajo el mismo esquema, mismas fuentes y misma compuerta V precisamente para que
    no tuviera peor rigor que el resto.
  - **Cómo revertir:** son dos diccionarios en `construir.py` (`PROPIOS` y `PROSA`). Volver a
    una lista única de campos obligatorios es borrar seis líneas.
  - **Pendiente:** llevarlo a `esquema-contenido.md` al formalizar `v1`, en el paso 3.

- **[DC-02]** Las fichas de prueba llevan un campo `prueba: true`.
  - **Por qué surgió:** el método exige que la fase 3 use «contenido de prueba claramente
    marcado como tal», pero no decía cómo se marca. Un comentario en el texto se puede colar
    a producción sin que nada lo detecte.
  - **Opciones:** (A) campo `prueba` en la ficha; (B) una carpeta aparte; (C) confiar en que
    `estado: borrador` baste.
  - **Elegida y razón:** **A**. Es verificable por la máquina: el generador puede negarse a
    publicar, o marcarlo de forma visible, y no depende de dónde esté el archivo ni de que
    alguien se acuerde. (C) no sirve: `borrador` significa «sin verificar», no «inventado
    para probar», y confundirlos sería peligroso en contenido médico.
  - **Cómo revertir:** quitar el campo de las 13 fichas y una comprobación del generador.

## Excepciones que detuvieron la construcción

| # | Tipo (1/2/3) | Qué pasó | Qué decidió Max | Fecha |
|---|---|---|---|---|
| — | — | Ninguna | — | — |

## Compuerta C

- [ ] Todos los criterios de aceptación **vigentes** se cumplen, verificados uno por uno.
- [ ] La bitácora de construcción está completa.
- [ ] **Publicado y verificado en el sitio real**, incluida la carga en móvil.
- [ ] El peso real está medido y dentro del presupuesto.
- [ ] `CA-A1` y `CA-A2` probados de verdad, apagando y rompiendo la pieza.
- [ ] `esquema-contenido.md` y `arquitectura.md` actualizados.
- [ ] **Snapshot tomado** y **etiqueta `v0.1`** creada.
- [ ] **Max aprobó el cierre de la construcción.**

**Aprobado por Max el:** ____-__-__

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | 2026-09-18 | Pasos 1, 2, 4 y 5 completados. `DC-01` y `DC-02` registradas. |
