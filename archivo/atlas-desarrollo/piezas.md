---
proyecto: Neuroteca
tipo: registro-de-piezas
version: "1.0"
ultima_actualizacion: 2026-09-18
---

# Registro de piezas

> Una **pieza** es una capacidad de la aplicación, autocontenida, que se enchufa al motor.
> **No es un dominio neuroanatómico**: la corteza o las vías motoras son contenido que
> atraviesa las piezas, no piezas.
>
> Cada pieza tiene su `ficha.md` en `piezas/<nombre>/`. Esta tabla es el índice.

## Estados

`Propuesta` (idea registrada, sin hito) · `En curso` (tiene hito abierto) · `Activa`
(publicada y en uso) · `Apagada` (existe pero está desactivada) · `Retirada`

## Piezas

| ID | Nombre | Qué hace | Esquema que usa | Versión | Estado |
|---|---|---|---|---|---|
| `visor` | Visor anatómico | Muestra el modelo de una región y abre la ficha de la parte que se toca. Se crea en `v0.1-cerebelo` | `v1` | — | Propuesta |
| `glosario` | Glosario | Contiene las **fichas fundacionales** y resuelve todo término técnico enlazado desde otras fichas. Es lo que permite que el atlas no asuma formación previa (P-04) | — | — | Propuesta |

## Motor

| Campo | Valor |
|---|---|
| **Versión actual** | `v0` — «Ver y entender una región». Hito `v0.1-cerebelo` en fase 1 |
| **Esquema de contenido** | `v0` borrador; el `v1` se crea en `v0.1-cerebelo` |
| **Arquitectura** | `motor/arquitectura.md` v1.0 — stack y visión decididos |

> **Ninguna pieza se diseña antes de que exista `esquema v1`.** Ver
> `00-metodo/README.md` → Parte I.
