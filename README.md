# Neuroteca

*Atlas vivo del sistema nervioso.* · *A living atlas of the nervous system.*

**https://neuroteca.github.io** · [English below](#english)

Atlas interactivo de **neuroanatomía y neurofisiología juntas**, de acceso libre, pensado para
estudiantes de medicina, neurociencia y psicología, y escrito para que se entienda sin formación
previa en neurociencia y sin saber programar.

> **Proyecto en construcción, en uso.** Está publicada la versión `v0.1`: la aplicación completa
> (generador, visor 3D, navegación, glosario enlazado) con el cerebelo como región de prueba. Las
> fichas publicadas están marcadas como **contenido de prueba** hasta que las sustituya el primer
> lote verificado. El plan de trabajo está en los [issues](../../issues) y en [`GUIA.md`](GUIA.md).

## Qué lo hace distinto

- **Anatomía y función en la misma ficha.** Qué es y qué hace, no una cosa o la otra.
- **Granularidad declarada.** Cada estructura dice a qué nivel está representada hoy, de la
  forma general (`N1`) al circuito (`N5`). El atlas nunca aparenta más precisión de la que tiene.
- **No asume formación previa.** Todo término técnico enlaza a una ficha del glosario, y la
  construcción falla si algún enlace se queda sin destino.
- **Con fuentes y con revisión.** Ninguna afirmación se publica sin una referencia localizable,
  y cada ficha declara quién la redactó y si ya fue revisada.
- **El sistema nervioso no es un árbol.** Una estructura puede pertenecer a varias divisiones a
  la vez: el nódulo es parte del vermis y del lóbulo floculonodular. El modelo de datos lo refleja.
- **Citable y duradero.** Cada estructura tiene una URL estable por identificador, el sitio es
  estático y funciona sin JavaScript, y cada versión etiquetada recibe un DOI.

## Advertencia

Neuroteca es un recurso **didáctico y esquemático**. No es una referencia clínica ni quirúrgica,
y no debe usarse para decisiones diagnósticas o terapéuticas.

## Cómo se construye

```
python3 herramientas/construir.py --validar   # valida las fichas
python3 herramientas/construir.py             # genera el sitio en docs/
```

Solo hace falta Python 3; no hay dependencias que instalar. El contenido vive en `contenido/`
como JSON, la aplicación en `src/`, y `docs/` es lo que publica GitHub Pages. Cómo se trabaja,
qué revisa cada pull request y qué reglas no cambian: [`GUIA.md`](GUIA.md).

## Licencias

| Qué | Licencia |
|---|---|
| Código | [MIT](LICENSE) |
| Contenido: fichas, modelos y diagramas | [CC BY-SA 4.0](LICENSE-CONTENIDO) |
| Activos derivados de terceros | La que declaren sus metadatos en `contenido/activos/` |

## Cómo citar

> Alamilla Rodríguez, M. *Neuroteca — atlas vivo del sistema nervioso*. https://neuroteca.github.io.
> Licencia CC BY-SA 4.0.

Metadatos de cita en [`CITATION.cff`](CITATION.cff). ORCID del autor:
[0009-0000-7890-4569](https://orcid.org/0009-0000-7890-4569).

---

## English

**Neuroteca** is an open-access interactive atlas that presents **neuroanatomy and
neurophysiology together**. It is written for students of medicine, neuroscience and
psychology, and it assumes no prior background in neuroscience: the fundamentals are part of the
atlas itself, as a linked glossary of foundational entries.

**Status:** work in progress, in use. Version `v0.1` ships the complete application (static
site generator, 3D viewer with a non-3D fallback, navigation across multiple anatomical axes,
linked glossary) with the cerebellum as the pilot region. Published entries are labelled as
**test content** until the first verified batch replaces them. The roadmap lives in the
[issues](../../issues).

What sets it apart:

- **Structure and function on the same page.**
- **Declared granularity.** Every structure states the level at which it is currently
  represented, from overall shape (`N1`) to circuit (`N5`), and the atlas never claims more
  precision than it has.
- **Sourced and reviewed.** No statement is published without a locatable reference, and every
  entry records its author and its review status.
- **Not a tree.** A structure can belong to several divisions at once (the nodule is part of
  both the vermis and the flocculonodular lobe); the data model reflects this.
- **Citable and durable.** Stable URLs by identifier, a static site that works without
  JavaScript, no external dependencies that can expire, and a DOI for every tagged version.

The content is in Spanish; the interface and this documentation are being made bilingual, and
the data model supports per-entry translations into further languages.

Neuroteca is a **teaching resource**, schematic by design. It is not a clinical or surgical
reference. Code is MIT-licensed; content is CC BY-SA 4.0 unless an asset's metadata says
otherwise. Citation metadata: [`CITATION.cff`](CITATION.cff).
