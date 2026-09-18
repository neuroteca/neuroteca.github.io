---
proyecto: Neuroteca
tipo: arquitectura
version: "1.0"
ultima_actualizacion: 2026-09-18
estado: EN CONSTRUCCION
---

# Arquitectura de Neuroteca

> ## Arquitectura en construcción
>
> El **paso 0 se conversó el 2026-09-18** y de ahí salieron la visión de `v0`, el stack y la
> primera región. Lo que sigue sin estar escrito **sigue sin estar decidido**: no lo
> inventes. El detalle de cómo se construye vive en los documentos de fase de
> `motor/hitos/v0.1-cerebelo/`.

---

## Qué sí está decidido

Esto se decidió al diseñar el método (sesión S-01) y es vinculante:

| Decisión | Valor |
|---|---|
| **Nombre público** | **Neuroteca** — *atlas vivo del sistema nervioso* (P-05, 2026-09-18) |
| **Qué es** | Atlas interactivo de neuroanatomía y neurofisiología juntas |
| **Carácter** | Didáctico y esquemático. **No** es referencia clínica ni quirúrgica |
| **Acceso** | Libre y gratuito, usable sin conocimientos de programación |
| **Publicación** | GitHub Pages, sitio estático (sin servidor propio ni base de datos) |
| **Idioma** | Español |
| **Estructura** | Un motor + piezas, donde **una pieza es una capacidad de la aplicación**, no un dominio neuroanatómico |
| **Contenido** | Vive como datos, separado del código, conforme a `esquema-contenido.md` |
| **Modelos visuales** | Propios, con granularidad creciente (`N1` → `N5`) |
| **Presupuesto de peso** | 400 MB de sitio publicado (límite duro de Pages: ~1 GB) |
| **Licencia del código** | `MIT` (P-02, 2026-09-18) |
| **Público** | Cualquiera: **no se asume formación en neurociencia**. Los fundamentos son contenido del atlas, no requisito previo (P-04 revisado, 2026-09-18) |
| **Licencia del contenido** | `CC BY-SA 4.0` (P-01, 2026-09-18) |
| **Titular del copyright** | Maximiliano Alamilla Rodríguez (P-06, 2026-09-18) |
| **Stack** | HTML, CSS y JS estándar; datos en JSON; generador propio mínimo. **Sin framework ni dependencias que caduquen** (paso 0, 2026-09-18) |
| **Primera región** | **Cerebelo** (paso 0, 2026-09-18) |
| **Primera rebanada publicable** | Una región cerebral a nivel `N1`, con su anatomía y su fisiología, navegable y consultable (P-03, 2026-09-18) |

## Qué falta decidir

| Qué | Dónde se decide |
|---|---|
| Cómo se representa el contenido (formato de datos) | `esquema-contenido.md` v1 |
| Cómo se cargan y muestran los activos visuales | Fase 2 del hito `v0.1` |


## Versiones del motor

> **Boceto revisable.** El propósito de cada versión se puede refinar libremente hasta que
> arranca su primer hito; a partir de ahí la visión se mantiene fija y puede recibir
> cualquier número de hitos mientras no la cambien.
>
> Estados: `Boceto` · `En curso`. *(No existe "Completa": la visión no se termina.)*

| Versión | Propósito en una frase | Estado |
|---|---|---|
| `v0` | **Ver y entender una región**: mostrar una región del sistema nervioso de forma visual e interactiva y, para cada estructura, decir qué es y qué hace, con fuentes, entendible sin formación previa gracias al glosario enlazado. | En curso |

## Hitos del motor

| Hito | Frase de valor | Fase | Estado |
|---|---|---|---|
| `v0.1-cerebelo` | Girar un modelo del cerebelo, tocar una parte y leer ahí mismo qué es y qué hace | 1 | Compuerta A pendiente |

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | 2026-09-18 | **Paso 0 conversado.** Visión de `v0` («Ver y entender una región»), stack sin framework con generador propio, primera región el cerebelo, y hito `v0.1-cerebelo` abierto. |
| 0.3 | 2026-09-18 | Nombre público: **Neuroteca**, con bajada "atlas vivo del sistema nervioso" (P-05). Identificador de GitHub `neuroteca` libre y verificado. |
| 0.2 | 2026-09-18 | P-01 (contenido `CC BY-SA 4.0`) y P-04 revisado: el atlas no asume formación en neurociencia. |
| 0.1 | 2026-09-18 | Se registran P-02 (licencia del código, `MIT`), P-03 (primera rebanada: una región a `N1`) y P-04 (público principal). |
| 0 | 2026-09-17 | Esqueleto. Recoge lo decidido al diseñar el método; la arquitectura en sí sigue sin definir. |
