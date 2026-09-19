---
proyecto: Neuroteca
tipo: esquema-de-contenido
version: "0.3"
ultima_actualizacion: 2026-09-18
estado: BORRADOR — no es v1
---

# Esquema de contenido

Este documento es **el contrato entre el contenido y la aplicación**. Define qué campos
tiene una ficha, qué formatos acepta un activo visual y cómo se declara el nivel de
detalle. Se versiona **aparte** del motor y de las piezas.

> ## ⚠ Esto es `v0`: un borrador, no el contrato.
>
> **Ninguna pieza se diseña antes de que exista `esquema v1`**, y `v1` no existe hasta que
> Max lo apruebe. Lo que sigue recoge lo que ya está decidido y marca explícitamente lo que
> falta. **No completes los huecos por tu cuenta.**

## Por qué existe este documento

El contenido del atlas va a crecer durante años. La aplicación se va a reescribir varias
veces en ese tiempo. Si el contenido vive dentro del código, cada reescritura lo pone en
riesgo; si vive como datos con un contrato estable, sobrevive a todas.

Consecuencia práctica: **una ficha se edita sin tocar la aplicación, y la aplicación se
puede reescribir sin tocar una sola ficha.**

---

## La ficha

Campos **ya decididos** (sesión S-01, vinculantes):

| Campo | Qué es | Obligatorio |
|---|---|---|
| `nombre` | Término en español | Sí |
| `termino_latin` | Terminologia Anatomica | Sí, si existe |
| `sinonimos` | Otros nombres y epónimos, en campo aparte del cuerpo | No |
| `nivel_detalle` | `N1`…`N5`: a qué granularidad está representada hoy | Sí |
| `anatomia` | Descripción estructural | Sí |
| `fisiologia` | Función y mecanismo | Sí |
| `fuentes` | Lista localizable: obra, edición y página, o DOI | **Sí — sin excepción** |
| `autoria` | `Max` o `agente` | Sí |
| `estado` | `borrador` o `revisado` | Sí |
| `id` | Identificador estable y único. **No se cambia ni se reutiliza jamás** | Sí |
| `divisiones` | Cómo se subdivide, agrupado por eje (ver abajo) | No |
| `activos` | Referencias a los activos visuales de esta estructura | No |
| `tipo` | `estructura` (una parte del sistema nervioso) o `fundacional` (un concepto: potencial de acción, sinapsis…) | Sí |

Reglas vinculantes sobre estos campos:

- **Cada afirmación necesita fuente.** Un agente no es una fuente; "es sabido que" tampoco.
- **`revisado` solo lo pone la compuerta V.** Ninguna ficha llega al sitio como `revisado`
  sin haberla cruzado.
- **`nivel_detalle` se muestra siempre al visitante.** Es lo que hace honesto un atlas
  construido por granularidad creciente.
- **Las fichas `fundacionales` viven en la pieza `glosario`** y cumplen el mismo esquema,
  con fuentes y compuerta V. No son definiciones de una línea: son contenido del atlas.
  Es el mecanismo que sostiene que no se asuma formación previa (P-04).
- **La autoría se registra por ficha**, para saber después qué texto pasó por el criterio
  de Max sin tener que revisarlo todo otra vez.

### Falta decidir

- Formato concreto de los datos y su organización en el disco.
- Cómo se representan las relaciones **funcionales** entre estructuras (se conecta con,
  proyecta a). Las relaciones de composición sí están resueltas, abajo.
- Cómo se enlaza la neuroanatomía con la neurofisiología cuando una función involucra
  varias estructuras.

---

## Ejes de división: el sistema nervioso no es un árbol

> **Decidido el 2026-09-18.** Es la decisión estructural más cara de deshacer del esquema, y
> por eso se cierra antes de que exista una sola ficha publicada.

### El problema

Una estructura **no tiene un solo padre**. El cerebelo se divide de dos formas distintas y
ambas son correctas a la vez:

| Eje | Partes |
|---|---|
| **Por regiones** | vermis · hemisferios |
| **Por lóbulos** | anterior · posterior · floculonodular |

No son dos niveles de un árbol: son dos particiones del mismo tejido. El caso que lo
demuestra es el **lóbulo floculonodular**, formado por el flóculo —hemisférico— y el
nódulo, que pertenece al vermis. El mismo tejido está en las dos divisiones.

Y esto empeora al bajar de nivel: en `N4`, una vía cruza regiones enteras y no pertenece a
ninguna de forma exclusiva.

### La decisión

**La composición se modela como un grafo con ejes de división, no como un árbol.**

Cada estructura declara sus divisiones, y cada división declara su eje:

```yaml
id: cerebelo
nombre: Cerebelo
nivel_detalle: N1
divisiones:
  - eje: regiones
    nombre_visible: Por regiones
    principal: true
    partes: [vermis, hemisferios_cerebelosos]
  - eje: lobulos
    nombre_visible: Por lóbulos
    partes: [lobulo_anterior, lobulo_posterior, lobulo_floculonodular]
```

Reglas vinculantes:

- **Una estructura puede aparecer en varios ejes y bajo varios padres.** Es la norma, no la
  excepción.
- **Cada estructura declara un eje `principal`**, que es el que se usa cuando solo se puede
  mostrar uno (migas, navegación simple, orden por defecto).
- **Cada eje tiene `nombre_visible`.** El visitante siempre sabe bajo qué criterio está
  viendo una división: «por lóbulos» no es lo mismo que «por regiones», y ocultarlo
  enseñaría mal.
- **Ningún eje es más verdadero que otro.** El `principal` es una preferencia de
  presentación, no una jerarquía real.

### Identidad estable

**La URL de una estructura usa su `id`, nunca su posición en la jerarquía.**

| | |
|---|---|
| ✅ | `/estructura/lobulo-anterior` |
| ❌ | `/cerebelo/lobulos/anterior` |

**Por qué:** si la URL codifica el camino, añadir un eje, reorganizar una división o
reclasificar una estructura rompe todos los enlaces publicados y todas las citas. Con `id`
estable, la jerarquía puede evolucionar durante años sin romper nada de lo que alguien haya
citado. En un recurso académico eso no es un detalle: es la diferencia entre ser citable y
no serlo.

El `id` **no se reutiliza ni se cambia nunca**. Si una estructura se renombra, cambia
`nombre`, no `id`.

### Qué implica para la navegación

La navegación se **deriva** de este modelo, no lo define: migas hasta la estructura actual
más las divisiones de su padre, agrupadas por eje. Descender en la navegación es descender
un nivel de detalle. Con seis estructuras se ve casi igual que una lista; con seiscientas se
ve exactamente igual.

---

## El activo visual

Campos **ya decididos**:

| Campo | Qué es | Obligatorio |
|---|---|---|
| `nivel_detalle` | `N1`…`N5` — se verifica contra este, no contra la perfección | Sí |
| `origen` | `propio`, `derivado` (de qué, con qué licencia), o `terceros` (con qué permiso) | **Sí — sin excepción** |
| `licencia` | La que aplica a este activo | Sí |
| `peso` | Medido sobre el export real, no sobre el archivo fuente | Sí |
| `equivalente_textual` | Descripción que no exige ver ni manipular el activo | Sí |
| `estado` | `provisional` (aproximación de trabajo) o `definitivo` (modelado de verdad) | Sí |

Reglas vinculantes:

- **Un activo sin origen registrado no se publica**, aunque sea evidentemente propio.
- **El `estado` se muestra al visitante**, igual que el nivel de detalle. Un activo
  `provisional` presentado como definitivo rompe la honestidad del atlas.
- **La geometría se carga desde un archivo, nunca escrita dentro del código.** Sustituir un
  activo `provisional` por su versión `definitiva` es un lote de contenido con compuerta V,
  no un cambio de software.
- **Al repositorio entra solo el export optimizado.** Los archivos fuente de modelado viven
  fuera y están en `.gitignore`: Git guarda cada versión de un binario entera, y veinte
  iteraciones de un modelo pesan veinte veces.
- **Malla, no volumen.** Geometría decimada y comprimida; nunca datos volumétricos crudos
  ni escaneos de alto polígono.
- **Todo activo visual tiene equivalente textual.** Un modelo 3D nunca es la única vía de
  acceso a una información.

### Falta decidir

- Formato de intercambio de los modelos y su compresión.
- Cómo se asocia un activo a varias estructuras a la vez.
- Cómo se versiona un activo cuando sube de nivel de detalle (un lote nuevo, pero ¿sustituye
  o convive con el anterior?).

---

## Niveles de detalle

| Nivel | Qué representa | Qué se verifica |
|---|---|---|
| **N1** | Forma general: volumen y silueta de una división mayor | Forma, posición y relaciones con lo vecino |
| **N2** | Subdivisiones: giros y surcos principales, divisiones internas mayores | Lo anterior, más la correcta separación entre subdivisiones |
| **N3** | Núcleos: núcleos y grupos celulares identificables | Lo anterior, más posición y límites de cada núcleo |
| **N4** | Vías y fibras: tractos, conexiones, proyecciones | Lo anterior, más origen, trayecto y destino de cada vía |
| **N5** | Circuito: microanatomía y dinámica fisiológica | Lo anterior, más el comportamiento del circuito |

**Un `N1` es correcto aunque no tenga un solo núcleo dentro.** Ese es el punto: sin un nivel
declarado, "no tiene que ser exacto al voxel" sería inverificable y la compuerta V no se
podría cerrar nunca.

**Subir de nivel una estructura ya publicada es un lote nuevo**, no una corrección.

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 0.3 | 2026-09-18 | **Ejes de división**: la composición es un grafo, no un árbol, porque una estructura pertenece a varias particiones a la vez (el nódulo es vermis y es floculonodular). Identidad estable: la URL usa el `id`, nunca el camino. |
| 0.2 | 2026-09-18 | Campo `estado` del activo (`provisional`/`definitivo`) y la regla de cargar la geometría desde archivo, para que reemplazar un modelo sea contenido y no código. |
| 0.1 | 2026-09-18 | Campo `tipo` (`estructura` / `fundacional`) y las fichas fundacionales del glosario (P-04 revisado). |
| 0 | 2026-09-17 | Borrador inicial. Recoge lo decidido en S-01 y marca los huecos. No es el contrato: `v1` requiere aprobación de Max. |
