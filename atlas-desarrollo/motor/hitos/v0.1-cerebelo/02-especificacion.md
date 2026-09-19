---
proyecto: Neuroteca
pieza: motor
hito: v0.1-cerebelo
tipo: especificacion
fase: 2
version: "1.1"
ultima_actualizacion: 2026-09-18
modo_de_respuesta: cuestionario
estado_compuerta_B: Aprobada
---

# Fase 2 — Especificación · v0.1 «cerebelo»

> Traduce el diseño a algo ejecutable **y caza los huecos**. Esta es la fase que compra el
> silencio de la fase 3: al cruzar la compuerta B, la construcción va de corrido.
>
> Identidad visual aprobada por Max el 2026-09-18
> (`identidad-visual/opcion-mixta.html`). Cuestionario integrado.

## Requerimientos técnicos

| ID | Requerimiento | Por qué |
|---|---|---|
| RT-01 | Sitio **totalmente estático**: sin servidor, sin base de datos, sin proceso en tiempo de petición | GitHub Pages sirve archivos (reglas §3) |
| RT-02 | **Sin dependencias de gestor de paquetes.** Todo lo de terceros se vendoriza en el repositorio con versión fija | El proyecto debe sobrevivir a pausas largas: una cadena de build que no reinstala mata el proyecto |
| RT-03 | Cada estructura tiene **su propia página HTML completa**, legible sin JavaScript | `CA-05`, `CA-06`, `CA-A2` y la regla de «toda ruta se abre directamente» |
| RT-04 | El 3D es **mejora progresiva** sobre esa página, nunca su requisito | `CA-A1` y `CA-A2` |
| RT-05 | La geometría se carga **desde un archivo**, jamás escrita en el código | Sustituir el modelo provisional por el de Blender debe ser un lote de contenido |
| RT-06 | El contenido vive **fuera del código**, como datos conformes al esquema | Regla fundacional del proyecto |
| RT-07 | La URL de una estructura usa su `id`, **nunca su camino** en la jerarquía | Que la jerarquía evolucione sin romper citas (`esquema-contenido.md` v0.3) |
| RT-08 | Funciona en móvil sin desplazamiento horizontal ni zoom para leer | `CA-07`; reglas §4 |
| RT-09 | Contraste mínimo WCAG AA y todo lo operable con ratón operable con teclado | Reglas §4 |
| RT-10 | Sin analítica, rastreo ni cookies de terceros | Reglas §3 |
| RT-11 | Tiempo hasta ver el modelo ≤ 3 s en portátil de gama media con conexión doméstica | `CA-01`; medido, no supuesto |
| RT-12 | La construcción **falla** si un enlace de glosario apunta a una ficha inexistente | Hace `CA-04` verificable por la máquina, no por buena voluntad |

## Estructura de datos

```
contenido/                        ← el atlas (carril de contenido)
  estructuras/<id>.json           una ficha por estructura
  glosario/<id>.json              fichas fundacionales (tipo: fundacional)
  activos/cerebelo.glb            geometría
  activos/cerebelo.json           metadatos del activo (origen, licencia, estado, peso)
src/                              ← la aplicación (carril de software)
  plantillas/*.html               plantillas del generador
  estilos/tokens.css  sitio.css   tokens extraídos de la maqueta aprobada
  js/visor.js  nav.js             pieza visor y navegación del motor
  vendor/                         three.min.js y GLTFLoader.js, versión fija
herramientas/
  construir.py                    el generador
  generar-geometria.py            produce el .glb provisional
docs/                             ← SALIDA GENERADA, es lo que publica Pages
```

**Ficha de estructura**, conforme a `esquema-contenido.md` v0.3:

```json
{
  "id": "vermis",
  "tipo": "estructura",
  "nombre": "Vermis",
  "termino_latin": "Vermis cerebelli",
  "sinonimos": [],
  "nivel_detalle": "N2",
  "anatomia": ["Primer párrafo…", "Segundo párrafo…"],
  "fisiologia": ["…"],
  "fuentes": [{"obra": "…", "edicion": "…", "paginas": "…"}],
  "autoria": "Max",
  "estado": "borrador",
  "divisiones": [],
  "activos": ["cerebelo"]
}
```

**La prosa es un array de párrafos**, no una cadena larga: en JSON, un texto de tres
párrafos en una sola línea es imposible de editar y de revisar en un diff.

**Marcado inline permitido**, deliberadamente mínimo y documentado:

| Sintaxis | Significado |
|---|---|
| `[[id]]` o `[[id\|texto]]` | Enlace a ficha de glosario. Si `id` no existe, **la construcción falla** |
| `**negrita**` · `*cursiva*` | Énfasis |

Nada más. Sin tablas, sin listas, sin HTML incrustado. Un subconjunto que cabe en cuarenta
líneas de generador es un subconjunto que seguirá funcionando en diez años.

## Conformidad con el esquema de contenido

| Campo | Valor |
|---|---|
| **Versión de esquema** | `v1`, **se crea en este hito** a partir de `esquema-contenido.md` v0.3 |
| **Campos que lee** | Todos los de ficha y de activo |
| **Campos que escribe** | Ninguno: el atlas es de solo lectura |
| **Qué pasa si una ficha no los tiene** | La construcción falla con el `id` y el campo que faltan. Nunca se publica una ficha incompleta |

## Dependencias

| ID | De qué depende | Estado |
|---|---|---|
| DEP-01 | Python 3 para el generador | Disponible (verificado en esta sesión) |
| DEP-02 | Three.js y GLTFLoader, vendorizados con versión fija | Pendiente de descargar en el paso 10 |
| DEP-03 | Repositorio publicado en GitHub con Pages activado | **Pendiente: Max reserva `neuroteca`** |
| DEP-04 | Lote `L-001-cerebelo` para el contenido real | Sin arrancar. La fase 3 usa contenido de prueba |

## Decisiones cerradas

| ID | Decisión | Opciones consideradas | Elegida y por qué |
|---|---|---|---|
| DEC-01 | Generador en **Python 3, solo biblioteca estándar** | Python · Node · generador existente | Python: ya está en la máquina, sin `npm install` que caduque (RT-02). Node arrastraría justo la cadena que evitamos |
| DEC-02 | Pages sirve desde **`/docs` en la rama principal** | `/docs` · rama `gh-pages` · GitHub Actions | Sin CI que envejezca ni permisos que revisar. Coste asumido: `docs/` es salida generada y se comitea |
| DEC-03 | **JSON, un archivo por estructura** | JSON · YAML · Markdown con frontmatter | JSON lo leen Python y el navegador sin parser externo. YAML exigiría dependencia; Markdown, un parser propio arriesgado |
| DEC-04 | **Una página HTML completa por estructura**, generada; el 3D se añade encima | Página por estructura · aplicación de una sola página | Resuelve `CA-05`, `CA-06` y `CA-A2` casi gratis, y hace el atlas citable e indexable. Una SPA los convertiría a los tres en trabajo extra |
| DEC-05 | **Three.js vendorizado**, versión fija en `src/vendor/` | Three.js · WebGL a mano · sin 3D | WebGL a mano es demasiado código para el valor. Vendorizado no caduca: es un archivo, no una cadena de build |
| DEC-06 | Geometría en **glTF binario (`.glb`)**, producida por `generar-geometria.py` | `.glb` · OBJ · geometría en código | `.glb` es estándar, compacto y **lo exporta Blender de forma nativa**: el modelo definitivo de Max sustituye al provisional sin tocar una línea (RT-05) |
| DEC-07 | URLs `/estructura/<id>/` | Por `id` · por camino jerárquico | Por `id`, para que reorganizar la jerarquía no rompa citas (RT-07) |
| DEC-08 | El navegador guarda **solo el tema elegido a mano** y si ya se vio el aviso | Nada · tema · tema y progreso | Lo mínimo que mejora la vuelta sin recoger nada del visitante (RT-10). Con `try/catch`: si falla, el sitio funciona igual |
| DEC-09 | **Aviso de entrada una vez por navegador** (C-03) | — | Decisión de Max. Si el almacenamiento falla, **se muestra siempre**: el fallo seguro es hacia la honestidad |
| DEC-10 | Sin WebGL o con el visor roto, se muestra **el esquema SVG estático** más un aviso | SVG de respaldo · solo texto · pantalla de error | El SVG ya existe (viene de la maqueta) y cumple de paso como equivalente visual. `CA-A2` queda cubierto por diseño |
| DEC-11 | La **navegación vive en el motor**, no en la pieza `visor` | Motor · visor | En el visor, apagarlo la borraría y `CA-A1` fallaría |
| DEC-12 | La maqueta aprobada es la **referencia normativa** de estilo; sus tokens se extraen a `tokens.css` | — | Evita que el estilo se reinvente en la construcción |
| DEC-13 | Las fichas fundacionales son fichas normales con `tipo: fundacional`, en `contenido/glosario/` | Fichas · diccionario aparte | Mismo esquema, mismas fuentes, misma compuerta V. Un glosario con reglas propias acabaría con peor rigor que el resto |
| DEC-14 | El visor colorea **por el eje principal**; el segundo eje se resalta al pasar por sus botones | Un color fijo · color por eje activo | Con dos particiones del mismo tejido, un solo coloreado fijo mentiría sobre una de ellas |

## Decisiones abiertas

| ID | Qué falta decidir | Estado |
|---|---|---|
| — | — | **Ninguna.** La lista está vacía. |

---

## El barrido de huecos

| # | Hueco | Respuesta |
|---|---|---|
| 1 | **Estado vacío** | No existe: el sitio se genera con contenido o no se genera. La portada redirige a la ficha `cerebelo` (`N1`), que siempre tiene sus divisiones. Se ve el aviso de entrada una vez (DEC-09) |
| 2 | **Errores** | Ficha inexistente → página 404 propia con la navegación completa, nunca la de GitHub. Fallo del visor → SVG de respaldo con aviso (DEC-10). Fallo de datos → **no llega a publicarse**: la construcción falla antes |
| 3 | **Límites** | 6 estructuras y ~6 fichas de glosario. El generador no impone máximo; el presupuesto de peso sí (abajo) |
| 4 | **Textos visibles** | Se toman **literalmente de la maqueta aprobada**: «Forma aproximada», «Arrastra para girar», «Vista inicial», «Por regiones», «Por lóbulos», «Entendido», y el texto completo del aviso de entrada. No se reescriben en construcción |
| 5 | **Identidad visual** | **Cerrada.** `identidad-visual/opcion-mixta.html`, aprobada por Max el 2026-09-18. Lienzo del visor siempre oscuro; superficie de lectura según el tema del sistema |
| 6 | **Persistencia** | Solo tema y «aviso visto», en `localStorage`, con `try/catch` (DEC-08). Si se borra: vuelve el tema del sistema y reaparece el aviso. En ventana privada funciona igual, mostrando el aviso cada vez |
| 7 | **Segunda vez** | Mismo estado, sin el aviso de entrada, con el tema que eligió. No se recuerda qué estructura vio: sería seguimiento sin pedirlo |
| 8 | **Contenido previo** | Ninguno. Es la primera publicación. `esquema v1` se crea aquí y no hay nada que migrar |
| 9 | **Entradas inválidas** | No hay campos de entrada. Una URL con `id` inexistente cae en el 404 propio |
| 10 | **Pantalla y dispositivo** | Probado en la maqueta a 375 px. Las zonas se apilan: visor, navegación, ficha. Se degradan el tamaño del visor y las filas de ejes, que pasan a etiqueta sobre botones. **Nada se oculta en móvil** |
| 11 | **Deshacer** | Nada que perder: el atlas es de solo lectura |
| 12 | **Rendimiento tolerable** | ≤ 3 s hasta ver el modelo (RT-11) en portátil de gama media. **La ficha se ve antes que el modelo siempre**, porque el HTML no espera al 3D. Se mide con las herramientas del navegador en el paso 15 |
| 13 | **Fin del flujo** | No hay final: desde cualquier ficha se sigue navegando por las divisiones o por el glosario. El pie recuerda licencia y carácter didáctico |
| 14 | **Accesibilidad** | Páginas HTML completas sin JS (RT-03); navegación por teclado con foco visible (RT-09); `equivalente_textual` obligatorio por esquema; contraste AA verificado sobre los dos fondos; `prefers-reduced-motion` respetado |
| 15 | **Sin conocimiento previo** | Todo término técnico enlaza al glosario, que contiene fichas fundacionales reales. **La construcción falla si un enlace no tiene destino** (RT-12), así que la promesa es estructural, no una intención |
| 16 | **Peso** | Ver presupuesto. Lo pesado es Three.js; se carga **diferido y solo en páginas con visor** |
| 17 | **Reglas ya sabidas** | Leídas en `reglas-del-agente.md` v1.2. Aplican §3 completa (sitio estático, sin CDN, carga bajo demanda, binarios sin iterar, rutas directas, sin rastreo, contenido como datos) → RT-01/02/10 y DEC-02/05. §4 completa (móvil, movimiento reducido, contraste, teclado, equivalente textual, temas, nivel visible, glosario) → RT-08/09 y puntos 10 y 14. §5 (español, código en inglés, latín en primera mención, registro claro) → plantillas y fichas. §1 prioridad 2 (reversible) sostiene DEC-02 y DEC-05 |
| 18 | **Apagado y convivencia** *(pieza `visor`)* | Se apaga con una bandera en el manifiesto del motor; la página queda con el SVG de respaldo y la navegación intacta. No comparte estado con ninguna otra pieza: lee el `.glb` y emite selección, nada más |

---

## Plan de construcción

| # | Paso | Produce | Verificable por |
|---|---|---|---|
| 1 | Esqueleto del repositorio (`contenido/`, `src/`, `herramientas/`, `docs/`) y `construir.py` que copia estáticos y genera una página mínima | Base | `docs/index.html` existe y abre |
| 2 | Formalizar `esquema v1` y validación de campos obligatorios; 6 fichas de prueba marcadas como tales | Base de CA-03 | La construcción falla al quitar un campo obligatorio |
| 3 | Plantilla y generación de la página de ficha: nombre, latín, nivel, anatomía, fisiología, fuentes | CA-03, CA-08 | Las 6 páginas muestran los 6 campos |
| 4 | Marcado inline (`[[id]]`, `**`, `*`) y fallo de construcción si falta el destino | CA-04 | La construcción falla con un enlace roto a propósito |
| 5 | Fichas fundacionales de glosario (prueba) y sus páginas | CA-04 | Ningún enlace lleva a una entrada vacía |
| 6 | Navegación del motor: migas y divisiones por eje, en HTML, operable con teclado | CA-06 | Se recorren las 6 fichas solo con teclado |
| 7 | URLs `/estructura/<id>/` y 404 propia | CA-05 | Pegar una URL abre esa estructura |
| 8 | Estilos: `tokens.css` extraídos de la maqueta, dos zonas, temas y móvil | CA-07 | Coincide con la maqueta a 375 px y en escritorio |
| 9 | Aviso de entrada, insignias de nivel y estado del activo | CA-08 | El nivel se ve sin buscarlo; el aviso sale una vez |
| 10 | `generar-geometria.py`: `cerebelo.glb` provisional con las 5 divisiones como submallas nombradas, y su `.json` de metadatos | Base de CA-01/02 | El `.glb` abre y tiene 5 submallas con nombre |
| 11 | Vendorizar Three.js y GLTFLoader; pieza `visor`: carga, giro, zoom, vista inicial | CA-01 | Se gira arrastrando en ≤ 3 s |
| 12 | Selección: clic o toque en una submalla resalta y abre su ficha; coloreado por eje | CA-02 | Tocar el vermis lo resalta y abre su ficha |
| 13 | Degradación: sin WebGL o visor roto → SVG de respaldo y aviso; apagado desde el motor | CA-A1, CA-A2 | Se apaga y se rompe a propósito, y el atlas sigue |
| 14 | Publicar en Pages desde `docs/` y verificar en la URL real, incluido móvil | CA-07 | Se abre la URL pública y se comprueba un CA ahí |
| 15 | Medir peso y tiempo de carga reales; ajustar si hace falta | RT-11, presupuesto | Medición anotada en la bitácora |

**Cada `CA-NN` de la fase 1 aparece en la columna «Produce».**

## Presupuestos

| Presupuesto | Valor | Límite |
|---|---|---|
| **Pasos del plan** | **15** | **22** (1.5×). Al rebasarlo se aplica la partición, no se pide extensión |
| **Peso añadido al sitio** | **≈ 1 MB** estimado: Three.js y GLTFLoader ~640 KB · `.glb` provisional ~200 KB · HTML, CSS y JS propios ~60 KB · sin fuentes externas | Presupuesto global 400 MB. Se **mide** en el paso 15 sobre `docs/` |

## Dependencia del carril de contenido

La fase 3 se construye y se verifica con **contenido de prueba claramente marcado como
tal**. El cerebelo real entra por el lote `L-001-cerebelo` con su compuerta V. La frase de
valor no se cumple hasta que ambos crucen.

## Compuerta B

- [x] El barrido de huecos está respondido punto por punto.
- [x] **La lista de decisiones abiertas está vacía.**
- [x] La identidad visual quedó confirmada (maqueta aprobada por Max el 2026-09-18).
- [x] Cada `CA-NN` de la fase 1 aparece en la columna «Produce» del plan.
- [x] El plan cumple la regla de granularidad y el presupuesto en pasos está declarado.
- [x] El presupuesto de peso está declarado.
- [x] **Snapshot tomado** (`git commit` con el estado previo a construir).
- [x] Max aprobó el documento.

**Aprobado por Max el:** 2026-09-18

> **La fase 3 arranca.** El agente construye de corrido y solo se detiene por una de las
> tres excepciones. Toda decisión propia se registra como `DC-NN` en
> `03-bitacora-construccion.md`, con su razón y cómo revertirla.

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.1 | 2026-09-18 | Compuerta B aprobada. Snapshot tomado. Arranca la fase 3. |
| 1.0 | 2026-09-18 | Versión inicial, con la identidad visual ya cerrada y 14 decisiones cerradas. |
