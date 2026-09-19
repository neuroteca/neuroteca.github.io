# Neuroteca

*Atlas vivo del sistema nervioso.*

Atlas interactivo de **neuroanatomía y neurofisiología juntas**, de acceso libre, pensado
para que se entienda sin formación previa en neurociencia y sin saber programar.

> **En construcción.** Todavía no hay nada publicado. Este repositorio contiene el método de
> trabajo y el primer hito en curso.

## Qué lo hace distinto

- **Anatomía y función en la misma ficha.** Qué es y qué hace, no una cosa o la otra.
- **Granularidad declarada.** Cada estructura dice a qué nivel está representada hoy, de la
  forma general (`N1`) al circuito (`N5`). El atlas nunca aparenta más precisión de la que
  tiene.
- **No asume formación previa.** Todo término técnico enlaza a una ficha del glosario, y la
  construcción falla si algún enlace se queda sin destino.
- **Con fuentes.** Ninguna afirmación se publica sin una referencia localizable.
- **El sistema nervioso no es un árbol.** Una estructura puede pertenecer a varias
  divisiones a la vez: el nódulo es parte del vermis y del lóbulo floculonodular. El modelo
  de datos lo refleja en vez de forzar una jerarquía falsa.

## Advertencia

Neuroteca es un recurso **didáctico y esquemático**. No es una referencia clínica ni
quirúrgica, y no debe usarse para decisiones diagnósticas o terapéuticas.

## Licencias

| Qué | Licencia |
|---|---|
| Código | [MIT](LICENSE) |
| Contenido: fichas, modelos y diagramas | [CC BY-SA 4.0](LICENSE-CONTENIDO) |

## Cómo se construye

El proceso completo está en [`atlas-desarrollo/`](atlas-desarrollo/) y es público a
propósito. Se trabaja en dos carriles —software y contenido—, por hitos pequeños y
completos, con compuertas que hay que cruzar para avanzar. Nada se construye con decisiones
abiertas, y nada se publica sin verificar.

Si quieres entender cómo, empieza por
[`atlas-desarrollo/EMPIEZA-AQUI.md`](atlas-desarrollo/EMPIEZA-AQUI.md).

## Cómo citar

> Alamilla Rodríguez, M. *Neuroteca — atlas vivo del sistema nervioso*.
> Licencia CC BY-SA 4.0.
