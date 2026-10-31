# Guía de trabajo de Neuroteca

*Atlas vivo del sistema nervioso.* Atlas interactivo de neuroanatomía y neurofisiología juntas,
de acceso libre, en https://neuroteca.github.io. Didáctico y esquemático: no es referencia
clínica ni quirúrgica. No asume formación previa: los fundamentos son fichas del propio atlas.

Esta guía es **la única que hay que leer para trabajar**. Si algo no está escrito aquí ni en el
código, no está decidido: se pregunta en el pull request o se abre un issue, no se rellena.

## Cómo está hecho

| Carpeta | Qué contiene |
|---|---|
| `contenido/` | **El atlas, como datos.** `estructuras/<id>.json` (una ficha por estructura), `glosario/<id>.json` (fichas fundacionales: conceptos), `sistemas/<id>.json` (funciones que atraviesan varias estructuras, con su circuito), `<id>.<idioma>.json` junto a cada ficha (su traducción), `activos/` (modelos 3D, esquemas SVG y sus metadatos), `paginas/` (páginas sueltas como «Acerca de»). |
| `src/` | **La aplicación.** Plantillas, estilos, JavaScript, Three.js vendorizado y los textos de la interfaz por idioma (`idiomas/<idioma>.json`). Sin gestor de paquetes. |
| `herramientas/` | `construir.py` valida el contenido y genera el sitio. `generar-geometria.py` produce el modelo provisional. Solo biblioteca estándar de Python. |
| `docs/` | **Salida generada.** Es lo que publica GitHub Pages. No se edita a mano; se regenera y se comitea. |
| `archivo/` | Material retirado. No rige. |

```
python3 herramientas/construir.py --validar   # comprueba las fichas sin escribir nada
python3 herramientas/construir.py             # regenera docs/
python3 -m http.server 8765 --directory docs  # sirve el sitio en local
```

### La ficha

Cada ficha es un JSON con `id` (estable, nunca se cambia ni se reutiliza; es la URL), `tipo`
(`estructura` o `fundacional`), `nombre`, `termino_latin`, `sinonimos`, `nivel_detalle` (`N1`
forma general … `N5` circuito; **siempre visible al lector**), `fuentes` (obligatorio), `autoria`,
`estado` (`borrador` o `revisado`), y la prosa en párrafos: `anatomia` y `fisiologia` para
estructuras, `definicion` y `explicacion` para fundacionales. Las estructuras declaran
`divisiones` por **ejes** (una parte puede estar en varios ejes a la vez) y `activos`.

Marcado permitido en la prosa: `[[id]]` o `[[id|texto]]` para enlazar al glosario, `**negrita**`,
`*cursiva*`, `[texto](https://…)` para un enlace externo (fuentes abiertas, ORCID), `` `código` ``
y `[^n]` al final de una frase para decir en qué fuente de la ficha (la número *n*) se apoya.
Nada más. **La construcción falla** si un enlace no tiene destino, una referencia apunta a una
fuente que no existe o falta un campo.

Cada fuente es `{obra, edicion, paginas}` y, cuando lo tiene, `doi` o `url`, que el sitio
muestra como enlace. Una fuente abierta (libro de texto libre, terminología oficial, artículo
con DOI) vale tanto como una de pago: lo que importa es que cualquiera pueda ir y comprobar.

El esquema completo, con la razón de cada campo, está en
`archivo/atlas-desarrollo/motor/esquema-contenido.md` (v0.3) más la decisión DC-01 de
`archivo/atlas-desarrollo/motor/hitos/v0.1-cerebelo/03-bitacora-construccion.md`, que aquí queda
formalizada: las fichas fundacionales usan `definicion` y `explicacion` en vez de `anatomia` y
`fisiologia`. El generador es la referencia operativa: lo que `construir.py` valida es lo que vale.

### La ficha de sistema

Una función real atraviesa varias estructuras. El tercer tipo, `sistema`, vive en
`contenido/sistemas/<id>.json` y se publica en `/sistema/<id>/`. Lleva los campos comunes más
`funcion` y `circuito` (prosa, con el mismo marcado), `estructuras` (lista ordenada de ids de
estructuras implicadas; cada una muestra a cambio «Sistemas en los que participa») y `esquema`:
`columnas` (cada una con `titulo` y `nodos` `{id, nombre}`) y `flechas` (`{de, a, texto}`). El
generador dibuja el diagrama desde ahí; un nodo cuyo `id` es una ficha se convierte en enlace, y
los demás se marcan como «sin ficha todavía». La prosa de `circuito` es el equivalente textual
del diagrama: tiene que contar lo mismo. La pieza `esquema` (JavaScript) solo añade el resaltado.

### La traducción de una ficha

`contenido/<carpeta>/<id>.<idioma>.json` con `id`, `idioma` y solo los campos que traduce:
`nombre`, `sinonimos`, `anatomia`, `fisiologia`, `definicion`, `explicacion`, `funcion`,
`circuito`, `ejes` (nombre de cada eje de división) y `nodos` (nombre de cada nodo del esquema). Cualquier otro campo hace fallar la construcción: `fuentes`, `estado`,
`nivel_detalle` y `divisiones` son una sola verdad y viven en la ficha en español. Un campo
ausente se muestra en español con la insignia «traducción pendiente».

### El activo

`contenido/activos/<id>.json` describe el modelo de una región: `nivel_detalle`, `origen`
(`propio`, `derivado` o `terceros`), `licencia`, `atribucion` (obligatoria si no es propio),
`estado` (`provisional` o `definitivo`), `peso_bytes`, `equivalente_textual`, `modelo` (el `.glb`),
`esquema` (el `.svg` que se ve sin JavaScript), `eje_visor` (qué eje de división pintan las
piezas) y `colores` (un color por `id` de parte; el generador los convierte en variables CSS
`--c-<id>` que usan el SVG y el 3D). Los archivos nombrados tienen que existir.

### Las páginas sueltas

`contenido/paginas/<id>.json` con un bloque por idioma (`titulo`, `descripcion`, `secciones`).
A diferencia de las fichas, una página suelta **debe** estar en todos los idiomas del sitio.

## Cómo se trabaja

- **Una rama y un pull request por cambio**: un lote de contenido, o un cambio de software. No
  se mezclan en el mismo PR.
- **Max revisa y aprueba cada PR.** Mezclar en `main` publica. Para contenido, aprobar el PR es
  la **verificación** (antes llamada compuerta V): solo entonces una ficha pasa a `revisado`.
- **Los issues son el backlog.** Toda idea, defecto o duda va a un issue, no a un documento.
- **El historial de git es la bitácora.** Los mensajes de commit y las descripciones de PR
  explican el porqué; no hay diario de sesiones.
- **Las versiones se etiquetan** (`v0.1`, `v0.2`…) cuando se cierra un conjunto de PRs que vale
  la pena citar. Cada etiqueta se deposita en Zenodo y recibe DOI.
- La plantilla de PR (`.github/pull_request_template.md`) lleva la lista de revisión.

## Reglas que no cambian

1. **Ninguna afirmación sin fuente localizable** (obra, edición y página, o DOI, o sección de un
   libro abierto). **Un agente no es una fuente**; «es sabido que» tampoco.
2. **`revisado` lo pone Max**, nunca el agente. Hasta entonces la ficha dice `borrador` y el
   sitio lo muestra.
3. **El nivel de detalle se declara y se muestra.** Un `N1` correcto no tiene núcleos dentro.
4. **Todo término técnico enlaza al glosario** en su primer uso. Se explica por enlace, no con
   paréntesis. Nada se explica en línea si no cabe en media frase.
5. **El contenido vive como datos**, fuera del código. Una ficha se edita sin tocar la
   aplicación; la aplicación se reescribe sin tocar una ficha.
6. **Cada página funciona sin JavaScript** y se puede abrir por su URL directa. El 3D es una
   mejora encima, nunca un requisito. Si una pieza falla, el resto sigue.
7. **Sin dependencias que caduquen**: nada de gestor de paquetes ni CDN para lo esencial.
8. **Móvil, teclado, contraste AA, `prefers-reduced-motion`, equivalente textual de todo lo
   visual.** Sin analítica ni rastreo.
9. **Todo activo visual declara origen, licencia, nivel y estado** (`provisional` o
   `definitivo`), y el lector lo ve. Al repositorio entra solo el export optimizado.
10. **Idiomas.** El español es el archivo canónico de cada ficha. Cada idioma adicional es una
    superposición (`<id>.en.json`) que traduce los campos que quiera; lo que falte se muestra
    en español marcado como sin traducir. Las URL en español no cambian; cada idioma añade su
    prefijo (`/en/…`). Los textos de la interfaz viven en `src/idiomas/`; añadir un idioma es
    añadir un archivo ahí y los bloques correspondientes en `contenido/paginas/`.
11. **Código en inglés, todo lo demás en español**: interfaz, contenido, commits, documentación.

## Qué revisa Max en un PR de contenido

- [ ] Cada afirmación tiene fuente citada y localizable; las páginas o secciones citadas dicen
      lo que la ficha dice.
- [ ] El texto es correcto **al nivel de detalle declarado**, no «a la perfección».
- [ ] Lo establecido y lo discutido están diferenciados donde aplica.
- [ ] Ningún término técnico sin enlace al glosario; ninguna explicación en línea larga.
- [ ] Registro claro y directo, para alguien que está aprendiendo. Latín en la primera mención.
- [ ] Activos nuevos: origen, licencia y atribución registrados; peso medido.
- [ ] `python3 herramientas/construir.py --validar` pasa y `docs/` está regenerado.

## Para agentes

Lee `AGENTS.md` y esta guía; no hace falta nada más para empezar. No hay reporte de orientación
ni ritual de cierre: el PR es el reporte. Si cambias cómo se trabaja, cambia esta guía en el
mismo PR. Si encuentras una contradicción entre esta guía y el código, repórtala en el PR en vez
de resolverla en silencio. `_referencia/` es privado y nunca entra a git.

## Licencias y cita

Código `MIT` (`LICENSE`). Contenido, modelos y diagramas `CC BY-SA 4.0` (`LICENSE-CONTENIDO`),
salvo los activos derivados de terceros, que llevan su propia licencia en sus metadatos. Cómo
citar el proyecto: `CITATION.cff`. Los metadatos que Zenodo lee al depositar cada etiqueta están
en `.zenodo.json`; las dos cosas se actualizan juntas en cada versión.
