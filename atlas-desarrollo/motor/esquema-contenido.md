---
proyecto: Neuroteca
tipo: esquema-de-contenido
version: "0.2"
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
- Cómo se representan las **relaciones** entre estructuras (contiene, se conecta con,
  proyecta a). Esto es la mitad del valor de un atlas y no está resuelto.
- Cómo se enlaza la neuroanatomía con la neurofisiología cuando una función involucra
  varias estructuras.
- Identificadores estables: qué garantiza que el enlace a una estructura siga funcionando
  dentro de cinco años.

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
| 0.2 | 2026-09-18 | Campo `estado` del activo (`provisional`/`definitivo`) y la regla de cargar la geometría desde archivo, para que reemplazar un modelo sea contenido y no código. |
| 0.1 | 2026-09-18 | Campo `tipo` (`estructura` / `fundacional`) y las fichas fundacionales del glosario (P-04 revisado). |
| 0 | 2026-09-17 | Borrador inicial. Recoge lo decidido en S-01 y marca los huecos. No es el contrato: `v1` requiere aprobación de Max. |
