---
proyecto: Neuroteca
pieza: motor
hito: v0.1-cerebelo
tipo: bitacora-construccion
fase: 3
version: "1.1"
ultima_actualizacion: 2026-09-19
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
| 3 | Plantilla y generación de la página de ficha | **Completado** | 13 páginas en `docs/`, con nombre, latín, nivel, anatomía/fisiología (o definición/explicación) y fuentes |
| 4 | Marcado inline y fallo por enlace sin destino | **Adelantado en el paso 2** | Verificado con un enlace roto a propósito: `[[estructura_inexistente]]` → construcción detenida, código 1, con archivo y campo señalados |
| 5 | Fichas fundacionales de glosario | **Completado** | 7 fichas en `contenido/glosario/`, todas con destino desde las estructuras |
| 6 | Navegación del motor: migas y ejes | **Completado** | Migas «Cerebelo › Lóbulo floculonodular» y los dos ejes etiquetados, en HTML puro, sin JavaScript |
| 7 | URLs `/estructura/<id>/` y 404 propia | **Completado** | `http://localhost:8765/estructura/vermis/` abre esa ficha directamente. `404.html` generado |
| 8 | Estilos desde la maqueta aprobada | **Completado** | `tokens.css` y `sitio.css` extraídos de la maqueta. Verificado servido por HTTP |
| 9 | Aviso de entrada e insignias | **Completado** | Aviso una vez por navegador; insignias de nivel, estado y contenido de prueba |
| 10 | `generar-geometria.py` y `cerebelo.glb` | **Completado** | `.glb` válido de 279 KB con **6 sectores** nombrados. Cabecera y longitudes verificadas leyendo el binario |
| 11 | Vendorizar Three.js; pieza `visor` | **Completado** | Three.js `0.185.1` fijado en `src/vendor/` (5 archivos, 933 KB, MIT). El modelo carga, gira y hace zoom |
| 12 | Selección y coloreado por eje | **Completado** | Clic en un sector abre su ficha. Coloreado por el eje principal y resaltado del otro al apuntar a sus botones, con ratón y con teclado |
| 13 | Degradación y apagado del visor | **Completado** | `CA-A1`: apagada en `src/piezas.json`, el sitio pasa de 1293 KB a **78 KB** y sigue navegable. `CA-A2`: borrado el `.glb`, aparece el esquema con el aviso «No se pudo cargar el modelo» |
| 14 | Publicar en Pages y verificar en la URL real | **Completado** | **https://neuroteca.github.io** en línea. Verificado ahí el visor 3D, la navegación y la carga en móvil de 375 px |
| 15 | Medir peso y tiempo reales | **Completado** | **348 KB por la red** (1237 KB sin comprimir). Descarga completa en frío y secuencial: 2353 ms. Primer byte del HTML: 169 ms |

**Pasos presupuestados:** 15 · **Límite de partición (1.5×):** 22 · **Ejecutados:** 15

> **Sin partición y sin reaperturas.** El plan se ejecutó completo dentro del presupuesto.

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

- **[DC-03]** El separador de las fuentes se escapa por trozos, no después de unir.
  - **Por qué surgió:** al revisar la primera página generada, la lista de fuentes mostraba
    `&middot;` literal en vez del punto. Escapaba la cadena ya unida, así que el `&` del
    separador se escapaba a sí mismo.
  - **Opciones:** (A) escapar cada trozo y unir después; (B) usar el carácter `·` directamente
    en vez de la entidad.
  - **Elegida y razón:** **A**. (B) esconde el error en vez de corregirlo: en cuanto una
    fuente traiga un `&` de verdad, volvería a romperse.
  - **Cómo revertir:** una línea en `_ficha_html`.
  - **Cómo se detectó:** mirando la página real en el navegador, no el código. Es la razón
    de la regla «verificar, no solo marcar».

- **[DC-04]** La malla se parte en **seis sectores**, no en cinco piezas.
  - **Por qué surgió:** el plan pedía «las 5 divisiones como submallas nombradas», pero una
    estructura pertenece a varios ejes a la vez. Partir por «regiones» dejaría los lóbulos
    sin geometría propia, y partir por «lóbulos» haría lo mismo con vermis y hemisferios.
  - **Opciones:** (A) seis sectores {vermis, hemisferios} × {anterior, posterior,
    floculonodular}, y cada división se compone uniendo los suyos; (B) elegir un eje
    canónico y representar el otro solo con color; (C) duplicar la geometría, una copia por
    eje.
  - **Elegida y razón:** **A**. (B) contradice el modelo de grafo del esquema justo donde más
    se nota. (C) duplica el peso y crea dos verdades que pueden divergir.
  - **Cómo revertir:** cambiar `sector_de()` para que devuelva un solo eje.
  - **Nota:** esto no cambia el alcance ni invalida el plan; es cómo se cumple el paso 10.

- **[DC-05]** El ancho del vermis es proporcional al ancho local, no fijo.
  - **Por qué surgió:** con un umbral fijo de `|x|`, cerca de los extremos superior e
    inferior la malla se estrecha por debajo de ese umbral y **el casquete entero quedaba
    clasificado como vermis**. Se vio en el recuento de vértices por sector, no en la
    pantalla.
  - **Opciones:** (A) umbral proporcional al ancho local; (B) dejarlo y documentarlo.
  - **Elegida y razón:** **A**. El vermis es una franja medial estrecha a cualquier altura,
    no un cono. (B) publicaría una relación anatómica falsa en el eje principal.
  - **Cómo revertir:** tres líneas en `sector_de()`.
  - **Queda declarado** en los metadatos del activo: lo más débil de la aproximación son los
    extremos superior e inferior, donde la malla se estrecha más que un cerebelo real. Sirve
    de nota para Max al modelar el definitivo.

- **[DC-06]** El SVG se oculta con `setAttribute('hidden','')` **más** una regla
  `[hidden] { display: none !important }`.
  - **Por qué surgió:** al cargar el 3D se veían **las dos representaciones a la vez**. Dos
    causas encadenadas: (1) `hidden` **no existe como propiedad en un `SVGElement`**, así que
    `svg.hidden = true` creaba una propiedad de JavaScript que no llegaba al DOM; (2) aunque
    llegara, `.visor svg { display: block }` gana el empate de especificidad al atributo.
  - **Elegida y razón:** atributo explícito más regla CSS explícita. Las dos hacen falta:
    una sola no basta.
  - **Cómo revertir:** dos líneas.
  - **Lo que duele:** la causa (2) **ya estaba escrita** en las reglas promovidas del método
    de MIA, que leí al diseñar este método, y aun así la pisé. Es el argumento literal de la
    regla «antes de diagnosticar, revisar lo ya sabido». **Se promueve a
    `reglas-del-agente.md` al cerrar el hito.**

- **[DC-07]** Los enlaces a CSS y JS llevan una versión derivada del contenido.
  - **Por qué surgió:** la corrección del CSS no aparecía en el navegador porque servía una
    copia en caché. Perdí una vuelta entera diagnosticando un fallo que ya estaba arreglado.
    En un sitio publicado le pasaría a cada visitante que ya hubiera entrado antes.
  - **Opciones:** (A) sello del contenido en la URL; (B) cabeceras de caché — imposible, Pages
    no las deja configurar; (C) nada.
  - **Elegida y razón:** **A**, que además es lo único disponible en un sitio estático.
  - **Cómo revertir:** quitar `version_de()` y los cuatro marcadores de la plantilla.

- **[DC-08]** La cámara se encuadra a partir de la caja del modelo, no con valores fijos.
  - **Por qué surgió:** con la cámara fija, cualquier modelo de otro tamaño quedaría fuera de
    plano. El modelo definitivo de Blender **no va a tener las mismas dimensiones** que la
    aproximación por código.
  - **Elegida y razón:** encuadre automático. Es lo que hace cierta la promesa de `RT-05`:
    sustituir el `.glb` no debe obligar a tocar el visor, ni siquiera la cámara.
  - **Cómo revertir:** fijar `camara.position` y los límites de distancia a mano.

## Excepciones que detuvieron la construcción

| # | Tipo (1/2/3) | Qué pasó | Qué decidió Max | Fecha |
|---|---|---|---|---|
| 1 | Seguridad | El paso 11 exige **descargar Three.js de internet** e incorporarlo al repositorio. Un agente no descarga archivos de fuera sin autorización explícita, por mucho que la fuente sea conocida. Se presentó con la alternativa de reconsiderar `DEC-05` | **Autorizado.** Se mantiene `DEC-05` y se descarga desde cdn.jsdelivr.net con versión fija | 2026-09-19 |

## Verificación de los criterios de aceptación

Todos comprobados **en el sitio publicado**, no en local.

| ID | ¿Se cumple? | Evidencia |
|---|---|---|
| CA-01 | Sí | El modelo se ve y gira arrastrando en `https://neuroteca.github.io/estructura/cerebelo/`. Primer byte del HTML 169 ms; todo el conjunto en frío y en secuencia, 2353 ms |
| CA-02 | Sí | Clic en el centro del modelo → abre la ficha del **vermis**, que es la estructura que ocupa esa posición |
| CA-03 | Sí | Las 6 estructuras muestran nombre, latín, nivel, anatomía, fisiología y fuente |
| CA-04 | Sí | **Verificable por la máquina:** la construcción falla si un `[[id]]` no tiene destino. Probado con un enlace roto a propósito |
| CA-05 | Sí | `/estructura/lobulo_floculonodular/` pegada en otra ventana abre esa estructura |
| CA-06 | Sí | Desde la ficha del vermis, el tabulador alcanza las 6 estructuras más los enlaces de glosario. «Saltar al contenido» es el primer foco |
| CA-07 | Sí | Comprobado en el sitio real a 375 px: visor, navegación y ficha, sin desplazamiento horizontal ni zoom para leer |
| CA-08 | Sí | El nivel aparece como insignia junto al título y junto a cada entrada de la navegación |
| CA-A1 | Sí | Apagada la pieza en `src/piezas.json`: el sitio pasa de 1293 KB a **78 KB** y sigue navegable. No deja residuo |
| CA-A2 | Sí | Borrado el `.glb`: aparece el esquema SVG con el aviso «No se pudo cargar el modelo». Ficha y navegación intactas |

## Medición final

| Qué | Valor | Presupuesto |
|---|---|---|
| Peso por la red, página con visor | **348 KB** | — |
| Peso sin comprimir | 1237 KB | ~1 MB estimado en fase 2 |
| Sitio completo en disco | 1293 KB | 400 MB |
| Sin la pieza `visor` | 78 KB | — |

Lo que pesa es Three.js: 236 KB de los 348. La geometría, 111 KB. **Todo lo propio del
atlas —HTML, CSS, JavaScript— suma 10 KB.**

## Compuerta C

- [x] Todos los criterios de aceptación **vigentes** se cumplen, verificados uno por uno.
- [x] La bitácora de construcción está completa.
- [x] **Publicado y verificado en el sitio real**, incluida la carga en móvil.
- [x] El peso real está medido y dentro del presupuesto.
- [x] `CA-A1` y `CA-A2` probados de verdad, apagando y rompiendo la pieza.
- [x] `esquema-contenido.md` y `arquitectura.md` actualizados.
- [x] **Snapshot tomado** y **etiqueta `v0.1`** creada.
- [ ] **Max aprobó el cierre de la construcción.**

> **Lo que este hito NO entrega:** el cerebelo de verdad. Las 13 fichas son contenido de
> prueba marcado como tal, y el modelo es una forma aproximada. Eso llega por el lote
> `L-001-cerebelo`, con su compuerta V. La frase de valor no se cumple del todo hasta
> entonces, y estaba previsto desde la fase 1.

**Aprobado por Max el:** ____-__-__

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.4 | 2026-09-19 | Pasos 14 y 15 completados. Los 10 criterios verificados en el sitio publicado. Compuerta C presentada a Max. |
| 1.3 | 2026-09-19 | Pasos 11, 12 y 13 completados. `CA-A1` y `CA-A2` probados de verdad. `DC-06`, `DC-07` y `DC-08` registradas. |
| 1.2 | 2026-09-19 | Paso 10 completado. `DC-04` y `DC-05` registradas. Construcción detenida en el paso 11 por autorización de descarga. |
| 1.1 | 2026-09-19 | Pasos 3, 6, 7, 8 y 9 completados: el sitio ya se genera y se navega. `DC-03` registrada. |
| 1.0 | 2026-09-18 | Pasos 1, 2, 4 y 5 completados. `DC-01` y `DC-02` registradas. |
