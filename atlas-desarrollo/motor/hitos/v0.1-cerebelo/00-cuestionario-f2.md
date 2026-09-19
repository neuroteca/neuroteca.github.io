---
proyecto: Neuroteca
pieza: motor
hito: v0.1-cerebelo
tipo: cuestionario
fase: 2
version: "1.0"
ultima_actualizacion: 2026-09-18
estado: Respondido e integrado
---

# Cuestionario · fase 2 · v0.1 «cerebelo»

> **Este es el único archivo del hito donde escribes tú.** Yo lo integro a
> `02-especificacion.md`. Contéstalo a tu ritmo; también vale por chat.
>
> Aquí están **solo** las decisiones que necesitan tu criterio. El resto de la
> especificación —formato de datos, estructura de URLs, carga bajo demanda, degradación sin
> 3D— la cierro yo y la dejo documentada en `02-especificacion.md` con su razón, para que la
> apruebes de una pasada en la compuerta B.

**Cómo responder:** basta la letra en la línea `**Respuesta:**`. Si ninguna opción te
convence, escribe lo que quieras.

---

## C-01 · Dirección de la identidad visual

Es el punto 5 del barrido de huecos y **bloquea la compuerta B**: no puedo construir con un
estilo inventado por mí sin que lo aceptes explícitamente.

Elige una dirección y **te construyo una maqueta real en HTML** con el cerebelo y una ficha,
para que la apruebes viéndola y no imaginándola.

- **A** — **Sobria, tipo libro de texto digital.** Fondo claro, tipografía de lectura larga,
  color solo para diferenciar estructuras. El contenido manda; la interfaz desaparece.
  *(Recomendada: es lo que mejor envejece y lo que menos compite con el modelo.)*
- **B** — **Oscura, tipo visor científico.** Fondo oscuro, el modelo 3D destaca mucho más,
  aire de instrumento. Contra: el texto largo cansa más en oscuro, y aquí hay fichas que se
  leen enteras.
- **C** — **Clara y cálida, tipo divulgación.** Más color, más aire, más invitación. Contra:
  puede restarle credibilidad ante un lector académico, que es parte de tu público.

*(Recuerda que el tema claro/oscuro según la preferencia del sistema ya es obligatorio por
las reglas del agente. Esto decide el carácter, no si hay modo oscuro.)*

**Respuesta:**Puede ser una mezcla de mabos? por ejemplo obscura y tipo visor para ver el modelo y clara para el glosario?

---

## C-02 · Qué se ve al entrar, antes de tocar nada

Punto 1 del barrido. Importa más de lo normal porque tu visitante puede no saber qué es
Neuroteca **ni** tener formación en neurociencia.

- **A** — **Directo al atlas:** el modelo del cerebelo y, al lado, su ficha general con la
  lista de partes. Se entiende usándolo. *(Recomendada: menos fricción, y la lista ya
  explica qué se puede hacer.)*
- **B** — **Una línea de bienvenida encima del atlas** que diga qué es esto y cómo se usa, y
  que se puede cerrar. Cuesta un poco de espacio en móvil.
- **C** — **Pantalla de entrada** antes del atlas. Explica mejor, pero mete un paso entre el
  visitante y lo que vino a ver.

**Respuesta:** A por ahora, aunque, conforme crezca, seguramente tengamos que meter algo de tutorial o elección para ir una vista o zona en lugar de meterse a una especifica.

---

## C-03 · Cómo se marca que el modelo es provisional

Decidiste arrancar con geometría aproximada por código mientras modelas el definitivo. El
visitante tiene que saberlo — la pregunta es con cuánto énfasis.

- **A** — **Etiqueta discreta y permanente** junto al modelo: «forma aproximada». Siempre
  visible, sin estorbar. *(Recomendada: honesta y no se convierte en ruido.)*
- **B** — **Aviso al entrar**, que se cierra y no vuelve. Más explícito la primera vez,
  invisible después — incluido para quien llega por un enlace directo.
- **C** — **Solo una nota en la ficha del activo**, no en el visor. Lo más discreto; también
  lo más fácil de no ver.

**Respuesta:** B

---

## C-04 · Cuánto realismo mínimo aceptas en la geometría por código

Esto fija el listón de `CA-01` y `CA-02`, y es tu criterio como anatomista y docente el que
manda. La pregunta es qué tiene que cumplir la forma aproximada para ser publicable.

- **A** — **Silueta reconocible con las cinco divisiones diferenciadas.** Se ve que es un
  cerebelo, se distinguen vermis, hemisferios y los tres lóbulos, y las posiciones relativas
  son correctas. Sin folia ni detalle de superficie. *(Recomendada: es exactamente lo que
  `N1`/`N2` exigen, ni más ni menos.)*
- **B** — **Lo anterior más la textura foliada** insinuada, aunque sea esquemática. Se
  parece más a un cerebelo de verdad; cuesta bastante más y es justo lo que tú harás mejor
  en Blender.
- **C** — **Bloques geométricos claramente esquemáticos**, sin pretensión de parecerse. Más
  rápido y más honesto sobre su provisionalidad, pero puede no enseñar la forma, que es el
  punto de un `N1`.

**Respuesta:**A

---

## Cualquier otra cosa

> Correcciones, dudas, o algo que hayas pensado leyendo. Lo que sea idea nueva fuera de
> alcance va al backlog, no a este hito — el alcance quedó congelado el 2026-09-18.

**Respuesta:**

---

## Integración

*(Lo lleno yo al integrar las respuestas.)*

| Pregunta | Respuesta de Max | Dónde quedó registrada |
|---|---|---|
| C-01 | **Mezcla:** visor oscuro tipo instrumento + superficie de lectura clara. Aceptada como dirección; **falta aprobar la maqueta** | `identidad-visual/opcion-mixta.html` · pendiente compuerta B |
| C-02 | **A** — directo al atlas. Nota: cuando el atlas crezca hará falta tutorial o elección de vista | `02-especificacion.md` · la nota va a `backlog.md` (BL-05) |
| C-03 | **B** — aviso al entrar, que se cierra y no vuelve | `02-especificacion.md`, barrido punto 1 |
| C-04 | **A** — silueta reconocible con las cinco divisiones y posiciones relativas correctas, sin folia | `02-especificacion.md`, listón de `CA-01` y `CA-02` |

**Integrado el:** 2026-09-18

## Dos reglas derivadas de C-01, para que la mezcla no se rompa

1. **El lienzo del visor es siempre oscuro**, sea cual sea el tema del sistema. Solo la
   superficie de lectura sigue la preferencia. Sin esta regla, el modelo pierde contraste en
   modo claro.
2. **En móvil las dos zonas se apilan** y queda un borde entre un bloque oscuro y uno claro.
   Ese borde se trata a propósito (margen, radio y sombra), nunca se deja como corte.

## Nota sobre C-03

El aviso al entrar es invisible para quien vuelve o llega por enlace directo. No queda hueco
porque **el esquema ya obliga a mostrar el `estado` del activo en su ficha** (`provisional` /
`definitivo`): el visitante lo ve por los dos lados, sin necesidad de una etiqueta permanente
en el visor.

---

## Corrección de Max sobre la maqueta · 2026-09-18

**Qué pidió:** que las partes estén arriba y el contenido se desarrolle hacia abajo, porque
el contenido va a crecer y con las partes abajo se pierden.

**Aplicado**, y con dos ajustes propios:

- **Fila compacta en vez de lista vertical**, y **fijada al hacer scroll**. Una lista
  vertical arriba resolvería lo de perderse pero empujaría la ficha fuera de la primera
  pantalla; una fila fijada no se pierde y tampoco ocupa.
- Se aplicó igual en móvil: visor → navegación de partes → ficha.

**Regla derivada, vinculante para la fase 2:** la navegación de partes **pertenece al motor,
no a la pieza `visor`**. Si viviera dentro del visor, apagarlo la borraría y **`CA-A1`
fallaría** — ese criterio exige que sin visor se llegue a las seis fichas. Es el primer caso
real en que el criterio de aislamiento decide dónde vive un elemento de interfaz.
