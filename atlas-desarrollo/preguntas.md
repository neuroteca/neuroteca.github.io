---
proyecto: Atlas Neuronal
tipo: preguntas-abiertas
version: "1.1"
ultima_actualizacion: 2026-09-18
techo: 100 lineas
---

# Preguntas abiertas

> **Este es el archivo donde Max responde.** El agente escribe las preguntas; Max escribe
> las respuestas debajo de cada una, cuando pueda, sin necesidad de estar en una sesión.
>
> **Aquí van solo las preguntas de proyecto.** Las de un hito van en su `00-cuestionario.md`.
> Al responderse, la pregunta se retira de aquí y su respuesta se registra donde
> corresponda. Techo duro: 100 líneas.

**Cómo responder:** escribe tu respuesta en la línea `**Respuesta:**`. Si eliges una opción,
basta su letra. Si ninguna te convence, escribe lo que quieras.

---

## P-01 · Licencia del contenido *(reformulada tras tu pregunta)*

**La diferencia clave:** `BY-SA` restringe **la licencia de lo derivado** (quien lo adapte
debe publicarlo igual de abierto). `BY-NC` restringe **quién puede usarlo y para qué**
(nada comercial), pero no obliga a que lo derivado siga siendo libre.

Tres cosas que decidieron la recomendación:

1. **"Comercial" no está definido con claridad** ni por Creative Commons. ¿Universidad con
   matrícula? ¿Curso de pago? ¿Blog con publicidad? Ante la duda la gente evita el material
   NC, así que restringe más de lo que pretendías sin dar protección real.
2. **Wikipedia y Wikimedia Commons solo aceptan licencias que permitan uso comercial.** Con
   NC, ninguna imagen tuya podría ilustrar nunca un artículo sobre el tálamo. Con BY-SA sí,
   y en ambos sentidos.
3. **NC no te da derechos extra.** Sigues siendo titular del copyright: siempre podrás
   conceder licencias comerciales aparte a quien te las pida, uses la licencia que uses.

- **A** — `CC BY 4.0`: máxima difusión, incluso dentro de obras cerradas (libros de texto,
  cursos de pago). A cambio, alguien puede encerrar una versión derivada.
- **B** — `CC BY-SA 4.0`: lo derivado debe seguir siendo libre. *(Recomendada.)* **Coste
  real:** es "viral" — una editorial no podrá meter tus diagramas en un capítulo cerrado.
- **C** — `CC BY-NC 4.0`: **no recomendada en ningún escenario**, por los tres puntos de
  arriba.

**Respuesta:**

---

## P-05 · Nombre público del proyecto *(con propuestas)*

**Observación previa:** en español, **"neuronal" se refiere a las neuronas**. El atlas trata
de lóbulos, núcleos, vías y sistemas: eso es *neural* o *del sistema nervioso*. Con público
de medicina y psicología, alguien lo va a notar. La carpeta puede seguir llamándose
`atlas_neuronal`; el nombre público conviene que sea preciso.

- **A** — **Neuroatlas Vivo** — "vivo" dice a la vez que incluye fisiología (no es anatomía
  congelada) y que crece con el tiempo. Corto, funciona como dominio. *(Recomendada.)*
- **B** — **Atlas Vivo del Sistema Nervioso** — lo mismo, explícito y preciso. Largo de
  citar.
- **C** — **Cerebro Abierto** — cálido y memorable. Deja fuera médula y periférico, y tiene
  una lectura quirúrgica involuntaria.
- **D** — **Forma y Función** — nombra el diferencial (anatomía + fisiología juntas), pero
  solo no dice que es de neurociencia.
- **E** — **Atlas Neurofuncional** — preciso y citable, pero frío.

Antes de fijarlo hay que comprobar que no colisione con algo existente.

**Respuesta:**

---

## Respondidas

| ID | Pregunta | Respuesta | Dónde quedó registrada |
|---|---|---|---|
| P-02 | Licencia del código | `MIT` | `motor/arquitectura.md` |
| P-03 | Alcance de la primera versión | Una región cerebral a `N1`, anatomía y fisiología, navegable | `motor/arquitectura.md` |
| P-04 | Público principal | Estudiantes de medicina, neurociencia y **psicología**, con mínimos asumidos | `00-metodo/reglas-del-agente.md` §5 |
