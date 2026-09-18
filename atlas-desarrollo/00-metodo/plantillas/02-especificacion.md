---
proyecto: Atlas Neuronal
pieza: motor | <nombre de pieza>
hito: vX.Y-<nombre>
tipo: especificacion
fase: 2
version: "1.0"
ultima_actualizacion: AAAA-MM-DD
modo_de_respuesta: cuestionario
estado_compuerta_B: Pendiente
---

# Fase 2 — Especificación · vX.Y «<nombre>»

> Aquí el agente traduce el diseño a algo ejecutable **y, sobre todo, caza los huecos**.
> Esta es la fase que compra el silencio de la fase 3.
>
> **Regla de promoción obligatoria:** toda nota de `01-diseno.md` que diga "se cierra en
> fase 2" se convierte, sin excepción, en una fila de la tabla de decisiones abiertas.

## Requerimientos técnicos

| ID | Requerimiento | Por qué |
|---|---|---|
| RT-01 | | |

## Estructura de datos

<Qué se guarda, en qué formato, dónde vive, cómo se lee.>

## Conformidad con el esquema de contenido

*(Solo si este hito toca contenido. Si no, borrar esta sección.)*

| Campo | Valor |
|---|---|
| **Versión de esquema que usa** | |
| **Campos que lee** | |
| **Campos que escribe** | |
| **Qué pasa si una ficha no los tiene** | |

## Dependencias

| ID | De qué depende | Estado |
|---|---|---|
| DEP-01 | | Disponible / Pendiente |

## Decisiones cerradas

| ID | Decisión | Opciones consideradas | Elegida y por qué |
|---|---|---|---|
| DEC-01 | | | |

## Decisiones abiertas

> **Esta tabla debe llegar a cero antes de la compuerta B.** Cada fila es una pregunta para
> Max con opciones cerradas y una recomendación.

| ID | Qué falta decidir | Opciones | Recomendación | Estado |
|---|---|---|---|---|
| DEC-A1 | | | | Abierta |

---

## El barrido de huecos

> Se responde **punto por punto, por escrito**. Cada respuesta que no exista se convierte
> en una decisión abierta que hay que cerrar antes de la compuerta B.

| # | Hueco | Respuesta |
|---|---|---|
| 1 | **Estado vacío** — qué se ve la primera vez, sin datos | |
| 2 | **Errores** — qué pasa si algo falla, y qué ve el visitante | |
| 3 | **Límites** — cuántos elementos, qué tamaño, qué pasa al rebasarlo | |
| 4 | **Textos visibles** — texto exacto de cada botón, título y mensaje | |
| 5 | **Identidad visual** — confirmada con Max, o placeholder aceptado como tal | |
| 6 | **Persistencia** — qué guarda el navegador, qué pasa si se borra, qué pasa en modo privado | |
| 7 | **Segunda vez** — qué se ve al reabrir, qué recuerda | |
| 8 | **Contenido previo** — hay que migrar fichas o activos ya publicados | |
| 9 | **Entradas inválidas** — qué pasa con una URL que ya no existe o una entrada rara | |
| 10 | **Pantalla y dispositivo** — móvil **no es opcional**; qué se degrada en pantalla pequeña | |
| 11 | **Deshacer** — qué se puede perder desde la interfaz, y si se recupera | |
| 12 | **Rendimiento tolerable** — cuánto puede tardar, **en qué conexión y qué equipo**. Se mide | |
| 13 | **Fin del flujo** — qué pasa cuando el visitante termina, a dónde va | |
| 14 | **Accesibilidad** — teclado, equivalente textual, contraste. Todo activo visual necesita alternativa | |
| 15 | **Sin conocimiento previo** — lo entiende alguien sin neurociencia ni código, sin leer instrucciones | |
| 16 | **Peso** — cuánto añade al sitio publicado, medido sobre el export real | |
| 17 | **Reglas ya sabidas** — qué reglas de `reglas-del-agente.md` aplican, leídas en el archivo, no de memoria | |
| 18 | **Apagado y convivencia** *(solo piezas)* — qué pasa al apagarla, qué comparte con otras | |

---

## Plan de construcción

> **Regla de granularidad:** un paso produce algo verificable por sí solo y cabe en una
> tanda de trabajo. Si no se puede describir en una línea concreta, hay que partirlo. Un
> plan con menos de 3 pasos casi siempre está mal desglosado.

| # | Paso | Produce | Verificable por |
|---|---|---|---|
| 1 | | CA-01 | |
| 2 | | | |

**Cada `CA-NN` de la fase 1 debe aparecer en la columna "Produce".**

## Presupuestos

| Presupuesto | Valor | Límite |
|---|---|---|
| **Pasos del plan** | <N> | **<N × 1.5>** — al rebasarlo se aplica la partición |
| **Peso añadido al sitio** | <MB> | Presupuesto global: 400 MB de sitio publicado |

## Compuerta B

- [ ] El barrido de huecos está respondido punto por punto.
- [ ] **La lista de decisiones abiertas está vacía.**
- [ ] La identidad visual quedó confirmada o explícitamente aceptada como placeholder.
- [ ] Cada `CA-NN` de la fase 1 aparece en la columna "Produce" del plan.
- [ ] El plan cumple la regla de granularidad y el presupuesto en pasos está declarado.
- [ ] El presupuesto de peso está declarado.
- [ ] **Snapshot tomado** (`git commit` con el estado previo a construir).
- [ ] Max aprobó el documento.

**Aprobado por Max el:** AAAA-MM-DD

## Historial de versiones
| Versión | Fecha | Cambio principal |
|---|---|---|
| 1.0 | AAAA-MM-DD | Versión inicial |
