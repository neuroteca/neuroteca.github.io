---
proyecto: Atlas Neuronal
tipo: arquitectura
version: "0"
ultima_actualizacion: 2026-09-17
estado: SIN DEFINIR
---

# Arquitectura del Atlas Neuronal

> ## ⚠ Este documento está **sin definir**.
>
> **No inventes su contenido.** Si necesitas saber cómo está hecho el atlas y esta sección
> sigue aquí, la respuesta es que todavía no se ha decidido: se decide conversando con Max
> en el **paso 0** del primer hito del motor, no deduciéndolo.
>
> Un agente que rellene este archivo por su cuenta rompe la regla número uno del proyecto.

---

## Qué sí está decidido

Esto se decidió al diseñar el método (sesión S-01) y es vinculante:

| Decisión | Valor |
|---|---|
| **Qué es** | Atlas interactivo de neuroanatomía y neurofisiología juntas |
| **Carácter** | Didáctico y esquemático. **No** es referencia clínica ni quirúrgica |
| **Acceso** | Libre y gratuito, usable sin conocimientos de programación |
| **Publicación** | GitHub Pages, sitio estático (sin servidor propio ni base de datos) |
| **Idioma** | Español |
| **Estructura** | Un motor + piezas, donde **una pieza es una capacidad de la aplicación**, no un dominio neuroanatómico |
| **Contenido** | Vive como datos, separado del código, conforme a `esquema-contenido.md` |
| **Modelos visuales** | Propios, con granularidad creciente (`N1` → `N5`) |
| **Presupuesto de peso** | 400 MB de sitio publicado (límite duro de Pages: ~1 GB) |

## Qué falta decidir

| Qué | Dónde se decide |
|---|---|
| El stack técnico | Paso 0 del hito `v0.1` del motor |
| Cómo se representa el contenido (formato de datos) | `esquema-contenido.md` v1 |
| Cómo se cargan y muestran los activos visuales | Fase 2 del hito `v0.1` |
| Qué capacidades tiene la `v0` del motor | Paso 0 — tabla "Versiones", abajo |
| Público principal, nombre, licencias | `preguntas.md` (P-01 a P-05) |

## Versiones del motor

> **Boceto revisable.** El propósito de cada versión se puede refinar libremente hasta que
> arranca su primer hito; a partir de ahí la visión se mantiene fija y puede recibir
> cualquier número de hitos mientras no la cambien.
>
> Estados: `Boceto` · `En curso`. *(No existe "Completa": la visión no se termina.)*

| Versión | Propósito en una frase | Estado |
|---|---|---|
| `v0` | *(sin escribir — sale de la conversación del paso 0)* | — |

## Hitos del motor

| Hito | Frase de valor | Fase | Estado |
|---|---|---|---|
| — | — | — | Ninguno abierto |

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 0 | 2026-09-17 | Esqueleto. Recoge lo decidido al diseñar el método; la arquitectura en sí sigue sin definir. |
