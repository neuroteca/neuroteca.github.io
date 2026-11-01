#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el mapa de orientación `src/piezas/mapa-sagital.json` y las láminas de
`src/piezas/laminas/` a partir de mallas 3D reales: proyecta cada región o parte a un plano
(vista lateral, medial, anterior, posterior o transversal) y traza el contorno de la silueta.
Nada se dibuja a mano: si una malla cambia, se vuelve a correr el script y el dibujo cambia.

Entrada: las mallas de `fuentes-3d/` (fuera de git: son pesadas y ya están publicadas), una
carpeta por fuente según `FUENTES` y, dentro, una subcarpeta por región nombrada con el id de
la ficha raíz (con o sin prefijo numérico: `04_cerebelo` o `cerebelo`) con sus `.obj` y, si la
fuente lo trae, un `indice.tsv` (archivo, objeto, colecciones) que permite agrupar mallas por
colección además de por nombre:

- `fuentes-3d/zanatomy/`: objetos exportados del `Startup.blend` de Z-Anatomy con
  `herramientas/exportar-zanatomy.py` (metros; x+ = lado izquierdo, y- = anterior,
  z+ = superior). Es la fuente de todo lo que se publica hoy: trae la corteza por lóbulos y
  circunvoluciones, los núcleos del telencéfalo, el tálamo, el hipotálamo y el epitálamo,
  el tronco con varios núcleos, el cerebelo por lobulillos y un corte transversal de la médula.
- `fuentes-3d/bodyparts3d/`: BodyParts3D 4.0 (árbol PART-OF), mm, mismos ejes. Fuente
  original de Z-Anatomy; queda disponible como alternativa (`FUENTE_MAPA`, `fuente` en cada
  lámina) pero no trae tálamo, ni divisiones del cerebelo, ni médula.

    python3 herramientas/proyectar-mapa.py

Salida: `src/piezas/mapa-sagital.json` (el mapa de regiones) y una lámina por entrada de
`LAMINAS` en `src/piezas/laminas/<region>-<eje>.json` (las partes con ficha de esa región,
cada una con su silueta visible en la vista elegida). El generador lee ambas cosas tal cual.

Limitaciones conocidas de las mallas que el script compensa y el JSON declara:
- La médula espinal de Z-Anatomy mide medio metro (sigue la columna). En el mapa solo entra su
  tramo superior (`MEDULA_LARGO` mm bajo el bulbo), recortado por un plano y marcado en
  `recortados` para que el sitio lo pinte con trazo discontinuo. Su lámina es un corte
  transversal real (intersección de las mallas con un plano a `corte` mm del extremo superior).
- Z-Anatomy no trae el subtálamo, la cápsula interna ni los núcleos del cerebelo: esas fichas
  quedan sin lámina.

Solo biblioteca estándar.
"""

import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'src', 'piezas', 'mapa-sagital.json')

RES = 0.5            # mm por píxel del raster de trabajo
MARGEN = 4.0         # mm alrededor de la caja del encéfalo
ANCHO_REF = 400      # ancho del viewBox
AREA_MIN = 12.0      # mm² mínimos para conservar una isla de silueta
TOLERANCIA = 0.45    # mm de tolerancia al simplificar el contorno
MEDULA_LARGO = 24.0  # mm de médula que entran en el mapa por debajo del bulbo

# Orden de pintado (lo de atrás primero) y qué regiones son esquemáticas.
ORDEN = ['telencefalo', 'tronco_encefalico', 'medula_espinal', 'cerebelo', 'diencefalo']
RECORTADOS = ['medula_espinal']  # regiones que el mapa muestra solo en parte (trazo discontinuo)
MALLAS_MAPA = {'medula_espinal': ('White_matter',)}  # regiones cuya silueta sale solo de algunas mallas
OMITIR_MAPA = {'diencefalo': ('hypophysis',)}  # mallas exportadas con la región que no entran en su silueta

# Vistas: (x, y, z) en mm -> (horizontal, vertical, profundidad); profundidad mayor = más
# cerca del observador. Ejes: x+ = izquierda del cuerpo, y- = anterior, z+ = superior.
# `recorte` = (eje, valor, lado) deja solo lo que queda a ese lado del plano (hemisección).
# `corte` = eje del plano cuya intersección con las mallas se dibuja (secciones).
VISTAS = {
    'lateral': {'proy': lambda x, y, z: (y, z, x)},        # desde la izquierda; anterior a la izquierda
    'medial': {'proy': lambda x, y, z: (y, z, x), 'recorte': (0, 0.0, -1)},  # mitad derecha vista desde la línea media; anterior a la izquierda
    'anterior': {'proy': lambda x, y, z: (x, z, -y)},      # de frente; la izquierda del cuerpo a la derecha
    'posterior': {'proy': lambda x, y, z: (-x, z, y)},     # desde atrás
    'transversal': {'proy': lambda x, y, z: (-x, y, -z), 'corte': 2},  # sección horizontal vista desde abajo; posterior arriba
}

# Fuentes de mallas: carpeta (relativa a la raíz), factor a mm y atribución.
FUENTES = {
    'zanatomy': {
        'carpeta': os.path.join('fuentes-3d', 'zanatomy'),
        'escala': 1000.0,
        'fuente': {
            'nombre': 'Z-Anatomy',
            'version': 'Startup.blend (2023)',
            'titular': 'Z-Anatomy, derivado de BodyParts3D (© The Database Center for Life Science)',
            'licencia': 'CC BY-SA 4.0',
            'url': 'https://github.com/Z-Anatomy/Models-of-human-anatomy',
            'atribucion': 'Z-Anatomy (CC BY-SA 4.0), derived from BodyParts3D, © The Database Center for Life Science (CC BY-SA 2.1 Japan)',
        },
    },
    'bodyparts3d': {
        'carpeta': os.path.join('fuentes-3d', 'bodyparts3d'),
        'escala': 1.0,
        'fuente': {
            'nombre': 'BodyParts3D',
            'version': '4.0 (árbol PART-OF)',
            'titular': 'The Database Center for Life Science',
            'licencia': 'CC BY-SA 2.1 JP',
            'url': 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html',
            'atribucion': 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan',
        },
    },
}
FUENTE_MAPA = 'zanatomy'

# Láminas: por ficha (región N1 o N2), una lista. Cada entrada:
#   eje     división de la ficha a la que corresponde (nombre del archivo: <ficha>-<eje>.json)
#   vista   clave de `VISTAS`
#   partes  {id de ficha: claves}; la primera parte cuyas claves casen se queda la malla. Una
#           clave es un fragmento del nombre de archivo (sin distinguir mayúsculas), «^…» si
#           debe ir al principio, o «@Colección» para casar por colección del índice. Una malla
#           que no case con ninguna parte se dibuja apagada y sin enlace, y no oculta nada.
#   mallas  carpeta de región de la que salen las mallas (por defecto, la propia ficha)
#   fuente  clave de `FUENTES` (por defecto, `FUENTE_MAPA`)
#   omitir  claves de mallas que no entran en la lámina (ventrículos que asoman, etc.)
#   corte   para una vista de sección: mm por debajo del extremo superior de las mallas a los
#           que se traza el plano de corte
#   capas   True: en vez de la profundidad real, cada parte tapa a las anteriores (en una
#           sección todas las piezas están en el mismo plano)
#   area_min  mm² mínimos de una isla para conservarla (por defecto, AREA_MIN)
LAMINAS = {
    'telencefalo': [
        {   # cara lateral por lóbulos: la ínsula queda bajo los opérculos y no asoma
            'eje': 'lobulos', 'vista': 'lateral',
            'partes': {
                'lobulo_frontal': ('@Frontal lobe',),
                'lobulo_parietal': ('@Parietal lobe',),
                'lobulo_temporal': ('@Temporal lobe',),
                'lobulo_occipital': ('@Occipital lobe',),
                'insula': ('@Insula',),
            },
        },
        {   # núcleos vistos a través del hemisferio (la corteza, sin ficha aquí, no oculta)
            'eje': 'nucleos', 'vista': 'lateral',
            'partes': {
                'ganglios_basales': ('Caudate', 'Putamen', 'Globus_pallidus', 'Lentiform'),
                'hipocampo': ('^Hippocampus',),
                'amigdala': ('Amygdaloid',),
            },
        },
        {   # cara medial del hemisferio derecho: corteza y cuerpo calloso
            'eje': 'interior', 'vista': 'medial',
            'partes': {
                'corteza_cerebral': ('@Neo-cortex',),
                'cuerpo_calloso': ('Corpus_callosum',),
            },
        },
    ],
    'ganglios_basales': [{
        # el pálido queda medial al putamen: en capas, para que se vea dentro del lenticular
        'eje': 'partes', 'vista': 'lateral', 'mallas': 'telencefalo', 'capas': True,
        'partes': {
            'nucleo_caudado': ('Caudate',),
            'putamen': ('Putamen',),
            'globo_palido': ('Globus_pallidus',),
        },
    }],
    'diencefalo': [{
        # hemisección: el tálamo derecho entero, el hipotálamo y el epitálamo cortados por el
        # plano medio. Z-Anatomy no trae el subtálamo. La hipófisis va en la lámina del hipotálamo.
        'eje': 'partes', 'vista': 'medial', 'area_min': 3.0, 'omitir': ('hypophysis',),
        'partes': {
            'talamo': ('^Thalamus', 'geniculate'),
            'hipotalamo': ('^Hypothalamus', 'Mamillary'),
            'epitalamo': ('Habenula', 'Pineal', 'Stria_medullaris'),
        },
    }],
    'talamo': [{
        # vista posterior: los cuerpos geniculados cuelgan de la cara inferior del pulvinar
        'eje': 'partes', 'vista': 'posterior', 'mallas': 'diencefalo', 'area_min': 2.0,
        'omitir': ('Hypothalamus', 'Mamillary', 'Optic', 'Habenula', 'Pineal', 'Stria', 'commissure',
                   'Third_ventricle', 'hypophysis'),
        'partes': {
            'cuerpo_geniculado_lateral': ('Lateral_geniculate',),
            'cuerpo_geniculado_medial': ('Medial_geniculate',),
        },
    }],
    'hipotalamo': [{
        # hemisección: el hipotálamo con el quiasma delante, los cuerpos mamilares detrás y la
        # hipófisis colgando
        'eje': 'partes', 'vista': 'medial', 'mallas': 'diencefalo', 'area_min': 2.0,
        'omitir': ('^Thalamus', 'geniculate', 'Habenula', 'Pineal', 'Stria', 'commissure', 'Third_ventricle',
                   'Optic_tract'),
        'partes': {
            'cuerpos_mamilares': ('Mamillary',),
            'hipofisis': ('hypophysis',),
        },
    }],
    'epitalamo': [{
        # hemisección: la pineal y la habénula sobre el tálamo (apagado) como referencia
        'eje': 'partes', 'vista': 'medial', 'mallas': 'diencefalo', 'area_min': 1.0,
        'omitir': ('Hypothalamus', 'Mamillary', 'Optic', 'geniculate', 'Third_ventricle', 'hypophysis'),
        'partes': {
            'glandula_pineal': ('Pineal',),
            'habenula': ('Habenula',),
        },
    }],
    'tronco_encefalico': [
        {
            'eje': 'niveles', 'vista': 'lateral', 'omitir': ('Fourth_ventricle',),
            'partes': {
                'mesencefalo': ('^Midbrain', 'colliculus', 'Aqueduct', 'Base_of_peduncle', 'Interpeduncular',
                                'Red_nucleus'),
                'puente': ('^Pons', 'Vestibular', 'salivatory'),
                'bulbo_raquideo': ('^Medulla', '^Olive', 'Pyramid', 'ambiguus', 'hypoglossal', 'solitary',
                                   'vagus', 'cochlear'),
            },
        },
        {   # núcleos con ficha vistos a través del tronco
            'eje': 'nucleos', 'vista': 'lateral', 'area_min': 3.0, 'omitir': ('Fourth_ventricle',),
            'partes': {
                'nucleo_rojo': ('Red_nucleus',),
                'nucleos_vestibulares': ('Vestibular',),
                'oliva_inferior': ('^Olive',),
            },
        },
    ],
    'cerebelo': [
        {
            # vista posterior: el vermis en medio y los hemisferios a los lados
            'eje': 'regiones', 'vista': 'posterior',
            'partes': {
                'vermis': ('Lingula', '^Central_lobule', 'Culmen', 'Declive', 'Folium', 'Tuber',
                           'Pyramis', 'Uvula', 'Nodule'),
                'hemisferios_cerebelosos': ('Wing_of_central', 'quadrangular', 'semilunar', 'Gracile',
                                            'Biventral', 'Tonsil', 'Flocculus', 'Peduncle_of_flocculus'),
                'pedunculos_cerebelosos': ('Superior_cerebellar_peduncle',),
            },
        },
        {
            # vista lateral: el lóbulo anterior arriba y delante, el posterior como masa
            # principal y el floculonodular abajo y delante; cada lóbulo reúne sus lobulillos
            # del vermis y de los hemisferios
            'eje': 'lobulos', 'vista': 'lateral',
            'partes': {
                'lobulo_anterior': ('Lingula', 'Central_lobule', 'Wing_of_central', 'Culmen',
                                    'Anterior_quadrangular'),
                'lobulo_posterior': ('Declive', 'Posterior_quadrangular', 'Folium', 'Superior_semilunar',
                                     'Tuber', 'Inferior_semilunar', 'Gracile', 'Pyramis', 'Biventral',
                                     'Uvula', 'Tonsil'),
                'lobulo_floculonodular': ('Nodule', 'Flocculus', 'Peduncle_of_flocculus'),
            },
        },
    ],
    'medula_espinal': [{
        # corte transversal cervical (donde la malla es perpendicular al plano): Z-Anatomy modela la
        # sustancia blanca por cordones y fascículos y la gris por astas y núcleos, a lo largo
        # de toda la médula
        'eje': 'interior', 'vista': 'transversal', 'corte': 45.0, 'capas': True, 'area_min': 0.5,
        'partes': {
            'sustancia_blanca_medular': ('White_matter', 'tract', 'fasciculus'),
            'sustancia_gris_medular': ('horn', 'nucleus', 'intermediate_substance', 'reticular_process'),
        },
    }],
}
LAMINAS_DIR = os.path.join(RAIZ, 'src', 'piezas', 'laminas')
TOKENS = os.path.join(RAIZ, 'src', 'estilos', 'tokens.css')
ETIQUETA_ANCHO = 100  # px del viewBox (cuerda) que necesita un nombre para ir dentro de su parte
ETIQUETA_ALTO = 22
MARGEN_ETIQUETAS = 150  # px del viewBox reservados a cada lado para los nombres de fuera

# Surcos del mapa: grupos de mallas del telencéfalo (mismas claves que en LAMINAS; la primera
# que case se queda la malla) y qué fronteras entre grupos se dibujan sobre la cara lateral.
# El surco central: frontera precentral/postcentral (el objeto «Central sulcus» de Z-Anatomy
# va con el grupo precentral para que ambos grupos se toquen). El surco lateral: frontera
# entre el lóbulo temporal y los lóbulos frontal y parietal.
GRUPOS_SURCOS = [
    ('precentral', ('^Precentral_gyrus', '^Central_sulcus')),
    ('postcentral', ('^Postcentral_gyrus',)),
    ('temporal', ('@Temporal lobe',)),
    ('frontoparietal', ('@Frontal lobe', '@Parietal lobe', 'Lat_Fis')),
]
SURCOS = [('precentral', 'postcentral'), ('frontoparietal', 'temporal'), ('precentral', 'temporal'),
          ('postcentral', 'temporal')]
SURCO_LARGO_MIN = 14.0   # mm
SURCO_TOLERANCIA = 1.2   # mm: el surco se simplifica más que el contorno
SURCOS_MAX = 2           # líneas que se conservan (las más largas): central y lateral


# --- lectura ---------------------------------------------------------------------

def leer_obj(ruta):
    v, f = [], []
    with open(ruta, encoding='utf-8', errors='ignore') as fh:
        for ln in fh:
            if ln.startswith('v '):
                a = ln.split()
                v.append((float(a[1]), float(a[2]), float(a[3])))
            elif ln.startswith('f '):
                a = [int(t.split('/')[0]) - 1 for t in ln.split()[1:]]
                for i in range(1, len(a) - 1):
                    f.append((a[0], a[i], a[i + 1]))
    return v, f


def leer_indice(ruta):
    """{archivo: [colecciones]} del `indice.tsv` de una carpeta, si existe."""
    cols = {}
    if os.path.isfile(ruta):
        with open(ruta, encoding='utf-8') as fh:
            for ln in fh.read().splitlines()[1:]:
                campos = ln.split('\t')
                if len(campos) >= 3:
                    cols[campos[0]] = [c for c in campos[2].split('|') if c]
    return cols


def casa(nombre, colecciones, claves):
    """¿Casa la malla con alguna clave? Fragmento del nombre de archivo sin distinguir
    mayúsculas; «^…» anclado al principio; «@…» por colección del índice."""
    n = nombre.lower()
    for k in claves:
        if k.startswith('@'):
            if k[1:] in colecciones:
                return True
        elif k.startswith('^'):
            if n.startswith(k[1:].lower()):
                return True
        elif k.lower() in n:
            return True
    return False


def cargar(fuente):
    """{region: [(nombre_archivo, vertices_mm, caras, colecciones)]} de una fuente de `FUENTES`."""
    cfg = FUENTES[fuente]
    carpeta = os.path.join(RAIZ, cfg['carpeta'])
    escala = cfg['escala']
    mallas = {}
    if not os.path.isdir(carpeta):
        return mallas
    for sub in sorted(os.listdir(carpeta)):
        ruta = os.path.join(carpeta, sub)
        if not os.path.isdir(ruta):
            continue
        idr = sub.split('_', 1)[1] if sub[:2].isdigit() and '_' in sub else sub
        if idr not in ORDEN:
            print('aviso: carpeta ignorada', sub, file=sys.stderr)
            continue
        indice = leer_indice(os.path.join(ruta, 'indice.tsv'))
        for nombre in sorted(os.listdir(ruta)):
            if nombre.lower().endswith('.obj'):
                v, f = leer_obj(os.path.join(ruta, nombre))
                if escala != 1.0:
                    v = [(x * escala, y * escala, z * escala) for (x, y, z) in v]
                mallas.setdefault(idr, []).append((nombre, v, f, indice.get(nombre, [])))
    return mallas


# --- raster ----------------------------------------------------------------------

class Lienzo:
    """Raster binario (bytearray) en el plano sagital: columna = y (anterior a la izquierda),
    fila = z (arriba = superior)."""

    def __init__(self, y0, z1, ancho, alto):
        self.y0, self.z1, self.W, self.H = y0, z1, ancho, alto

    def nuevo(self):
        return bytearray(self.W * self.H)

    def px(self, y, z):
        return (y - self.y0) / RES, (self.z1 - z) / RES

    def mm(self, px, py):
        return self.y0 + px * RES, self.z1 - py * RES

    def triangulo(self, mascara, p, q, r, prof=None, etq=None, valor=0, x=0.0):
        """Rellena el triángulo (coordenadas de píxel). Con `prof`/`etq`, además actualiza un
        z-buffer (x mayor = más cerca del observador, a la izquierda del cuerpo)."""
        W = self.W
        ys = (p[1], q[1], r[1])
        fila0 = max(0, int(math.floor(min(ys) - 0.5)))
        fila1 = min(self.H - 1, int(math.ceil(max(ys) - 0.5)))
        aristas = ((p, q), (q, r), (r, p))
        for fila in range(fila0, fila1 + 1):
            yc = fila + 0.5
            xs = []
            for a, b in aristas:
                if (a[1] - yc) * (b[1] - yc) <= 0 and a[1] != b[1]:
                    xs.append(a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1]))
            if len(xs) < 2:
                continue
            c0 = max(0, int(math.ceil(min(xs) - 0.5)))
            c1 = min(W - 1, int(math.floor(max(xs) - 0.5)))
            if c1 < c0:
                continue
            base = fila * W
            mascara[base + c0:base + c1 + 1] = b'\x01' * (c1 - c0 + 1)
            if prof is not None:
                for c in range(c0, c1 + 1):
                    if x > prof[base + c]:
                        prof[base + c] = x
                        etq[base + c] = valor

    def silueta(self, v, f, mascara, prof=None, etq=None, valor=0, vista='lateral', profundidad=None,
                recorte=None):
        """Proyecta la malla y rellena su silueta. `profundidad` fija una profundidad para
        toda la malla (capas) en vez de la geométrica; `recorte` añade un plano de recorte al
        de la vista."""
        cfg = VISTAS[vista]
        proy = cfg['proy']
        for plano in (cfg.get('recorte'), recorte):
            if plano:
                v, f = recortar(v, f, plano)
        T = [proy(*p) for p in v]
        P = [self.px(h, vv) for (h, vv, _) in T]
        for a, b, c in f:
            if prof is None:
                x = 0.0
            elif profundidad is not None:
                x = profundidad
            else:
                x = (T[a][2] + T[b][2] + T[c][2]) / 3.0
            self.triangulo(mascara, P[a], P[b], P[c], prof, etq, valor, x)
            for i in (a, b, c):  # un vértice siempre marca su píxel: sin huecos entre caras
                col, fila = int(P[i][0]), int(P[i][1])
                if 0 <= col < self.W and 0 <= fila < self.H:
                    mascara[fila * self.W + col] = 1

    def seccion(self, v, f, mascara, nivel, prof=None, etq=None, valor=0, vista='transversal',
                profundidad=0.0):
        """Rellena la intersección de la malla con el plano `eje = nivel` de la vista (una
        sección real, no una silueta): corta cada triángulo, encadena los segmentos en lazos y
        los rellena por paridad."""
        cfg = VISTAS[vista]
        lazos = cortar(v, f, cfg['corte'], nivel)
        P = [[self.px(*cfg['proy'](*p)[:2]) for p in lazo] for lazo in lazos]
        W = self.W
        aristas = [(l[i], l[(i + 1) % len(l)]) for l in P for i in range(len(l))]
        if not aristas:
            return 0
        filas = [a[1] for a, _ in aristas]
        for fila in range(max(0, int(min(filas))), min(self.H, int(max(filas)) + 2)):
            yc = fila + 0.5
            xs = sorted(a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1])
                        for a, b in aristas if (a[1] <= yc) != (b[1] <= yc))
            base = fila * W
            for k in range(0, len(xs) - 1, 2):
                c0 = max(0, int(math.ceil(xs[k] - 0.5)))
                c1 = min(W - 1, int(math.floor(xs[k + 1] - 0.5)))
                if c1 < c0:
                    continue
                mascara[base + c0:base + c1 + 1] = b'\x01' * (c1 - c0 + 1)
                if prof is not None:
                    for c in range(c0, c1 + 1):
                        if profundidad > prof[base + c]:
                            prof[base + c] = profundidad
                            etq[base + c] = valor
        return len(lazos)


def cortar(v, f, eje, nivel):
    """Lazos (listas de puntos 3D) de la intersección de la malla con el plano eje = nivel."""
    segmentos = {}
    puntos = {}

    def punto(i, j):
        clave = (min(i, j), max(i, j))
        if clave not in puntos:
            a, b = v[i], v[j]
            t = (nivel - a[eje]) / (b[eje] - a[eje])
            puntos[clave] = tuple(a[k] + (b[k] - a[k]) * t for k in range(3))
        return clave

    for tri in f:
        lados = [(tri[k], tri[(k + 1) % 3]) for k in range(3)]
        cruces = [punto(i, j) for i, j in lados if (v[i][eje] < nivel) != (v[j][eje] < nivel)]
        if len(cruces) == 2 and cruces[0] != cruces[1]:
            segmentos.setdefault(cruces[0], []).append(cruces[1])
            segmentos.setdefault(cruces[1], []).append(cruces[0])
    lazos, usados = [], set()
    for inicio in segmentos:
        if inicio in usados:
            continue
        lazo, actual = [inicio], inicio
        usados.add(inicio)
        while True:
            siguiente = [q for q in segmentos[actual] if q not in usados]
            if not siguiente:
                break
            actual = siguiente[0]
            usados.add(actual)
            lazo.append(actual)
        if len(lazo) >= 3:
            lazos.append([puntos[c] for c in lazo])
    return lazos


def recortar(v, f, plano):
    """Conserva lo que queda a un lado del plano `eje = valor` (`lado` +1: eje >= valor;
    -1: eje <= valor), partiendo los triángulos que lo cruzan."""
    eje, valor, lado = plano
    dentro = [(p[eje] - valor) * lado >= 0 for p in v]
    v2 = list(v)
    f2 = []
    corte = {}

    def punto_corte(i, j):
        clave = (min(i, j), max(i, j))
        if clave not in corte:
            a, b = v[i], v[j]
            t = (valor - a[eje]) / (b[eje] - a[eje])
            v2.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
            corte[clave] = len(v2) - 1
        return corte[clave]

    for tri in f:
        if all(dentro[i] for i in tri):
            f2.append(tri)
            continue
        if not any(dentro[i] for i in tri):
            continue
        poligono = []
        for k in range(3):
            i, j = tri[k], tri[(k + 1) % 3]
            if dentro[i]:
                poligono.append(i)
            if dentro[i] != dentro[j]:
                poligono.append(punto_corte(i, j))
        for k in range(1, len(poligono) - 1):
            f2.append((poligono[0], poligono[k], poligono[k + 1]))
    # solo los vértices que alguna cara usa: los de fuera no deben contar para las cajas
    usados = sorted(set(i for t in f2 for i in t))
    nuevo = dict((i, k) for k, i in enumerate(usados))
    return [v2[i] for i in usados], [tuple(nuevo[i] for i in t) for t in f2]


def unir(dest, otra):
    for i in range(len(dest)):
        if otra[i]:
            dest[i] = 1


# --- contornos (marching squares) ----------------------------------------------

def contornos(lienzo, mascara):
    """Lazos cerrados del borde de la máscara, en píxeles, como listas de puntos. Los lazos
    con área positiva son contornos exteriores; los negativos, agujeros."""
    W, H = lienzo.W, lienzo.H

    def val(c, f):
        return mascara[f * W + c] if 0 <= c < W and 0 <= f < H else 0

    segs = {}  # punto inicial -> punto final (bordes entre píxeles, a media celda)
    for f in range(-1, H):
        for c in range(-1, W):
            tl, tr, bl, br = val(c, f), val(c + 1, f), val(c, f + 1), val(c + 1, f + 1)
            caso = tl * 8 + tr * 4 + br * 2 + bl
            if caso in (0, 15):
                continue
            # puntos medios de los lados de la celda (centro de píxel = c+0.5, f+0.5)
            t, r, b, l = (c + 1.0, f + 0.5), (c + 1.5, f + 1.0), (c + 1.0, f + 1.5), (c + 0.5, f + 1.0)
            # segmentos orientados con el interior a la derecha (horario en pantalla,
            # lo que con el eje y hacia abajo da área positiva con la fórmula del cordón)
            tabla = {1: [(b, l)], 2: [(r, b)], 3: [(r, l)], 4: [(t, r)], 5: [(t, l), (b, r)],
                     6: [(t, b)], 7: [(t, l)], 8: [(l, t)], 9: [(b, t)], 10: [(l, b), (r, t)],
                     11: [(r, t)], 12: [(l, r)], 13: [(b, r)], 14: [(l, b)]}
            for a, z in tabla[caso]:
                segs.setdefault(a, []).append(z)
    lazos = []
    while segs:
        inicio = next(iter(segs))
        p = inicio
        lazo = [p]
        while True:
            sig = segs.get(p)
            if not sig:
                break
            q = sig.pop()
            if not sig:
                del segs[p]
            if q == inicio:
                break
            lazo.append(q)
            p = q
        if len(lazo) > 2:
            lazos.append(lazo)
    return lazos


def area(puntos):
    s = 0.0
    for i in range(len(puntos)):
        x0, y0 = puntos[i]
        x1, y1 = puntos[(i + 1) % len(puntos)]
        s += x0 * y1 - x1 * y0
    return -s / 2.0  # positivo = contorno exterior con la orientación de la tabla


def simplificar(puntos, tol, cerrado=True):
    """Douglas-Peucker."""
    if len(puntos) < 3:
        return puntos

    def dist(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx == dy == 0:
            return math.hypot(p[0] - a[0], p[1] - a[1])
        t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    def dp(pts):
        if len(pts) < 3:
            return pts
        a, b = pts[0], pts[-1]
        imax, dmax = 0, -1.0
        for i in range(1, len(pts) - 1):
            d = dist(pts[i], a, b)
            if d > dmax:
                imax, dmax = i, d
        if dmax > tol:
            return dp(pts[:imax + 1])[:-1] + dp(pts[imax:])
        return [a, b]

    if cerrado:
        # abre el lazo por su punto más lejano al primero para que los extremos no sean vecinos
        lejos = max(range(len(puntos)), key=lambda i: (puntos[i][0] - puntos[0][0]) ** 2 + (puntos[i][1] - puntos[0][1]) ** 2)
        a = dp(puntos[:lejos + 1])
        b = dp(puntos[lejos:] + [puntos[0]])
        return a[:-1] + b[:-1]
    return dp(puntos)


def suavizar(puntos, cerrado=True):
    """Una pasada de Chaikin: lima las esquinas del raster sin mover el contorno más de un píxel."""
    n = len(puntos)
    if n < 3:
        return puntos
    out = []
    rango = range(n) if cerrado else range(n - 1)
    for i in rango:
        a, b = puntos[i], puntos[(i + 1) % n]
        out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
        out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
    if not cerrado:
        out = [puntos[0]] + out + [puntos[-1]]
    return out


def _fmt(x):
    return ('%.1f' % x).rstrip('0').rstrip('.')


def trazado(puntos, escala, cerrado=True):
    partes = ['M%s %s' % (_fmt(puntos[0][0] * escala), _fmt(puntos[0][1] * escala))]
    partes += ['L%s %s' % (_fmt(x * escala), _fmt(y * escala)) for x, y in puntos[1:]]
    return ' '.join(partes) + (' Z' if cerrado else '')


# --- surcos ----------------------------------------------------------------------

def surcos(lienzo, etq, grupo_de, mascara_tel):
    """Líneas de frontera entre grupos de circunvoluciones visibles en la cara lateral.
    Devuelve polilíneas abiertas en píxeles."""
    W, H = lienzo.W, lienzo.H
    segs = {}
    quiero = set(SURCOS) | set((b, a) for a, b in SURCOS)
    for f in range(H):
        for c in range(W):
            i = f * W + c
            g = grupo_de.get(etq[i])
            if g is None:
                continue
            if c + 1 < W:
                g2 = grupo_de.get(etq[i + 1])
                if g2 is not None and g2 != g and (g, g2) in quiero:
                    a, b = (c + 1.0, f + 0.0), (c + 1.0, f + 1.0)
                    segs.setdefault(a, set()).add(b)
                    segs.setdefault(b, set()).add(a)
            if f + 1 < H:
                g2 = grupo_de.get(etq[i + W])
                if g2 is not None and g2 != g and (g, g2) in quiero:
                    a, b = (c + 0.0, f + 1.0), (c + 1.0, f + 1.0)
                    segs.setdefault(a, set()).add(b)
                    segs.setdefault(b, set()).add(a)
    # encadena desde los extremos (grado 1) y luego lo que quede
    lineas = []
    usados = set()

    def camina(p):
        linea = [p]
        while True:
            opciones = [q for q in segs.get(p, ()) if (p, q) not in usados]
            if not opciones:
                return linea
            q = opciones[0]
            usados.add((p, q))
            usados.add((q, p))
            linea.append(q)
            p = q

    for p in list(segs):
        if len(segs[p]) == 1:
            l = camina(p)
            if len(l) > 2:
                lineas.append(l)
    for p in list(segs):
        l = camina(p)
        if len(l) > 2:
            lineas.append(l)
    return lineas


def largo(puntos):
    return sum(math.hypot(puntos[i + 1][0] - puntos[i][0], puntos[i + 1][1] - puntos[i][1])
               for i in range(len(puntos) - 1))


# --- láminas ---------------------------------------------------------------------

def colores_region():
    """{region: '#rrggbb'} del tema claro, leído de tokens.css: un solo sitio para el color."""
    import re
    colores = {}
    with open(TOKENS, encoding='utf-8') as f:
        for m in re.finditer(r'--region-([a-z_]+):\s*(#[0-9A-Fa-f]{6})', f.read()):
            colores.setdefault(m.group(1), m.group(2))
    return colores


def tonos(hex_base, n):
    """n tonos del mismo color, del más oscuro al más claro, para distinguir las partes de una
    región sin perder su identidad."""
    import colorsys
    r, g, b = (int(hex_base[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if n == 1:
        pasos = [l]
    else:
        pasos = [l - 0.14 + (0.32 * k / (n - 1)) for k in range(n)]
    out = []
    for lk in pasos:
        lk = max(0.18, min(0.64, lk))  # ni negro ni tan claro que el nombre en blanco no se lea
        rr, gg, bb = colorsys.hls_to_rgb(h, lk, min(1.0, s * (1.08 if lk < l else 0.92)))
        out.append('#%02X%02X%02X' % (round(rr * 255), round(gg * 255), round(bb * 255)))
    return out


def centroide(l):
    A = -area(l)
    n = len(l)
    cx = sum((l[i][0] + l[(i + 1) % n][0]) * (l[i][0] * l[(i + 1) % n][1] - l[(i + 1) % n][0] * l[i][1]) for i in range(n)) / (6 * A)
    cy = sum((l[i][1] + l[(i + 1) % n][1]) * (l[i][0] * l[(i + 1) % n][1] - l[(i + 1) % n][0] * l[i][1]) for i in range(n)) / (6 * A)
    return cx, cy


def lamina(region, config, mallas, colores):
    vista = config['vista']
    cfg_vista = VISTAS[vista]
    proy = cfg_vista['proy']
    origen = config.get('mallas', region)
    piezas = [m for m in mallas[origen] if not casa(m[0], m[3], config.get('omitir', ()))]
    nivel = None
    if 'corte' in config:
        eje = cfg_vista['corte']
        nivel = max(p[eje] for (_, v, _, _) in piezas for p in v) - config['corte']
        lazos = [l for (_, v, f, _) in piezas for l in cortar(v, f, eje, nivel)]
        pts = [proy(*p) for l in lazos for p in l]
    elif cfg_vista.get('recorte'):
        eje, valor, lado = cfg_vista['recorte']
        pts = [proy(*p) for (_, v, _, _) in piezas for p in v if (p[eje] - valor) * lado >= 0]
    else:
        pts = [proy(*p) for (_, v, _, _) in piezas for p in v]
    hs = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    h0, h1 = min(hs) - MARGEN, max(hs) + MARGEN
    v0, v1 = min(vs) - MARGEN, max(vs) + MARGEN
    lienzo = Lienzo(h0, v1, int(math.ceil((h1 - h0) / RES)), int(math.ceil((v1 - v0) / RES)))
    # una lámina más alta que ancha se muestra más estrecha: el viewBox se ajusta para que el
    # texto (en unidades del viewBox) salga del mismo tamaño en pantalla en todas
    ancho_ref = ANCHO_REF if lienzo.W >= lienzo.H else max(280, int(round(ANCHO_REF * lienzo.W / float(lienzo.H))))
    escala = ancho_ref / float(lienzo.W)

    # z-buffer: cada píxel recibe la parte de la malla más cercana al observador. Las mallas
    # sin parte con ficha (sustancia blanca, ventrículos…) no ocultan: se ven las partes que
    # hay detrás, y solo donde no hay ninguna queda la zona apagada.
    prof = [-1e9] * (lienzo.W * lienzo.H)
    etq = bytearray(lienzo.W * lienzo.H)
    partes = list(config['partes'])
    codigo = dict((p, i + 1) for i, p in enumerate(partes))
    SIN = len(partes) + 1  # mallas sin parte
    mascara = lienzo.nuevo()
    for nombre, v, f, cols in piezas:
        valor = 0
        for parte, claves in config['partes'].items():
            if casa(nombre, cols, claves):
                valor = codigo[parte]
                break
        profundidad = float(valor) if config.get('capas') else None
        if nivel is not None:
            if valor:
                lienzo.seccion(v, f, mascara, nivel, prof, etq, valor, vista, profundidad or 0.0)
            else:
                lienzo.seccion(v, f, mascara, nivel, vista=vista)
        elif valor:
            lienzo.silueta(v, f, mascara, prof, etq, valor, vista, profundidad)
        else:
            lienzo.silueta(v, f, mascara, vista=vista)
    for i in range(len(etq)):
        if mascara[i] and not etq[i]:
            etq[i] = SIN

    area_min_px = config.get('area_min', AREA_MIN) / (RES * RES)
    tol_px = TOLERANCIA / RES
    trazos, cajas, centros = {}, {}, {}
    for parte, valor in list(codigo.items()) + [('_sin_ficha', SIN)]:
        m = bytearray(1 if e == valor else 0 for e in etq)
        lazos = [l for l in contornos(lienzo, m) if area(l) > area_min_px]
        lazos.sort(key=area, reverse=True)
        if not lazos:
            continue
        trazos[parte] = [trazado(suavizar(simplificar(l, tol_px)), escala) for l in lazos]
        l = lazos[0]
        ys = [p[1] for p in l]
        cx, cy = centroide(l)
        # sitio para el nombre: el tramo horizontal más largo de la parte, prefiriendo las
        # filas cercanas al centro (una parte oblicua o simétrica tiene el centroide fuera
        # de sí misma o sobre otra parte)
        mejor, tramo = None, 0
        W = lienzo.W
        for fila in range(lienzo.H):
            base = fila * W
            c = 0
            while c < W:
                if m[base + c]:
                    ini = c
                    while c < W and m[base + c]:
                        c += 1
                    puntua = (c - ini) - 0.35 * abs(fila - cy)
                    if puntua > tramo:
                        tramo, mejor = puntua, ((ini + c) / 2.0, fila + 0.5, c - ini)
                else:
                    c += 1
        cajas[parte] = ((mejor[2] if mejor else 0) * escala, (max(ys) - min(ys)) * escala)
        if mejor:
            centros[parte] = (round(mejor[0] * escala, 1), round(mejor[1] * escala, 1))
        else:
            centros[parte] = (round(cx * escala, 1), round(cy * escala, 1))

    # etiquetas: dentro si la isla mayor tiene sitio; si no, fuera a la derecha con guía
    etiquetas = {}
    fuera = []
    for parte in partes:
        if parte not in trazos:
            continue
        ancho, alto = cajas[parte]
        if ancho >= ETIQUETA_ANCHO and alto >= ETIQUETA_ALTO:
            etiquetas[parte] = {'modo': 'dentro', 'x': centros[parte][0], 'y': centros[parte][1] + 4}
        else:
            fuera.append(parte)
    # los nombres de fuera van al lado más cercano; el viewBox crece por ese lado
    izq = [p for p in fuera if centros[p][0] < ancho_ref / 2.0]
    der = [p for p in fuera if centros[p][0] >= ancho_ref / 2.0]
    # el margen crece con el nombre más largo de ese lado (el id aproxima al nombre visible)
    margen = dict((lado, max(MARGEN_ETIQUETAS, 16 + 6 * max([len(p) for p in lista] or [0])) if lista else 0)
                  for lado, lista in (('izq', izq), ('der', der)))
    desplaza = margen['izq']
    ancho_vb = ancho_ref + desplaza + margen['der']
    for lado, lista in (('izq', izq), ('der', der)):
        lista.sort(key=lambda p: centros[p][1])
        y_prev = -1e9
        for parte in lista:
            cx, cy = centros[parte]
            y = max(cy, y_prev + ETIQUETA_ALTO)  # que no se monten
            if lado == 'der':
                x_texto, ancla, fin = ancho_ref + desplaza + 14, 'start', ancho_ref + desplaza + 10
            else:
                x_texto, ancla, fin = desplaza - 14, 'end', desplaza - 10
            etiquetas[parte] = {'modo': 'fuera', 'ancla': ancla, 'x': x_texto, 'y': round(y + 4, 1),
                                'guia': 'M%s %s L%s %s' % (round(cx + desplaza, 1), cy, fin, round(y, 1))}
            y_prev = y
    if desplaza:
        # las partes se desplazan a la derecha para dejar sitio a los nombres de la izquierda
        import re as _re
        def _mueve(d):
            return _re.sub(r'([ML])(-?[\d.]+) ', lambda m: '%s%s ' % (m.group(1), _fmt(float(m.group(2)) + desplaza)), d)
        for parte in list(trazos):
            trazos[parte] = [_mueve(d) for d in trazos[parte]]
        for parte, e in etiquetas.items():
            if e['modo'] == 'dentro':
                e['x'] = round(e['x'] + desplaza, 1)

    base = colores.get(region) or colores.get(origen, '#888888')
    presentes = [p for p in partes if p in trazos]
    paleta = dict(zip(presentes, tonos(base, len(presentes))))
    salida = {
        '_nota': ('Lámina de %s (eje %s), vista %s: silueta visible de cada parte con ficha, '
                  'proyectada desde las mallas de %s con herramientas/proyectar-mapa.py. No editar a mano. '
                  '`partes` son ids de fichas; `sin_ficha` son las mallas de la región que no pertenecen a '
                  'ninguna parte con ficha (se pintan apagadas). `colores` son tonos del color de la región.'
                  % (region, config['eje'], vista, FUENTES[config.get('fuente', FUENTE_MAPA)]['fuente']['nombre'])),
        'fuente': FUENTES[config.get('fuente', FUENTE_MAPA)]['fuente'],
        'region': region,
        'eje': config['eje'],
        'vista': vista,
        'corte_mm': config.get('corte'),
        'viewBox': '0 0 %d %s' % (ancho_vb, _fmt(lienzo.H * escala)),
        'ancho_ref': ancho_ref,
        'escala_mm': round(escala / RES, 4),
        'colores': paleta,
        'orden': [p for p in partes if p in trazos],
        'partes': dict((p, trazos[p]) for p in partes if p in trazos),
        'sin_ficha': trazos.get('_sin_ficha', []),
        'etiquetas': etiquetas,
    }
    os.makedirs(LAMINAS_DIR, exist_ok=True)
    ruta = os.path.join(LAMINAS_DIR, '%s-%s.json' % (region, config['eje']))
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('  lámina %s/%s (%s): %s; sin ficha: %d islas' % (
        region, config['eje'], vista, ', '.join('%s %d' % (p, len(trazos[p])) for p in partes if p in trazos),
        len(trazos.get('_sin_ficha', []))), file=sys.stderr)
    print('escrito', os.path.relpath(ruta, RAIZ), file=sys.stderr)


# --- principal -------------------------------------------------------------------

def main():
    por_fuente = dict((nombre, cargar(nombre)) for nombre in FUENTES)
    mallas = dict(por_fuente[FUENTE_MAPA])  # copia: el mapa recorta la médula; las láminas la usan entera
    faltan = [r for r in ORDEN if r not in mallas]
    if faltan:
        sys.exit('faltan regiones: %s' % ', '.join(faltan))
    for region, claves in MALLAS_MAPA.items():
        mallas[region] = [m for m in mallas[region] if casa(m[0], m[3], claves)]
    for region, claves in OMITIR_MAPA.items():
        mallas[region] = [m for m in mallas[region] if not casa(m[0], m[3], claves)]

    # la médula sigue la columna hasta medio metro más abajo: al mapa solo entra el tramo que
    # continúa el bulbo, recortado por un plano horizontal
    z_bulbo = min(p[2] for (_, v, _, _) in mallas['tronco_encefalico'] for p in v)
    plano_medula = (2, z_bulbo - MEDULA_LARGO, 1)
    mallas['medula_espinal'] = [(n, ) + recortar(v, f, plano_medula) + (c, )
                                for (n, v, f, c) in mallas['medula_espinal']]

    ys = [p[1] for m in mallas.values() for (_, v, _, _) in m for p in v]
    zs = [p[2] for m in mallas.values() for (_, v, _, _) in m for p in v]
    y0, y1 = min(ys) - MARGEN, max(ys) + MARGEN
    z0, z1 = min(zs) - MARGEN, max(zs) + MARGEN
    lienzo = Lienzo(y0, z1, int(math.ceil((y1 - y0) / RES)), int(math.ceil((z1 - z0) / RES)))
    escala = ANCHO_REF / float(lienzo.W)
    print('raster %dx%d px, %.2f px/mm' % (lienzo.W, lienzo.H, escala / RES), file=sys.stderr)

    # siluetas por región; z-buffer de circunvoluciones solo para el telencéfalo
    mascaras = {}
    prof = [-1e9] * (lienzo.W * lienzo.H)
    etq = bytearray(lienzo.W * lienzo.H)
    grupo_de, codigo = {}, {}
    for idr in ORDEN:
        if idr not in mallas:
            continue
        m = lienzo.nuevo()
        for nombre, v, f, cols in mallas[idr]:
            valor = 0
            if idr == 'telencefalo':
                for g, claves in GRUPOS_SURCOS:
                    if casa(nombre, cols, claves):
                        valor = codigo.setdefault(nombre, len(codigo) + 1)
                        grupo_de[valor] = g
                        break
                lienzo.silueta(v, f, m, prof, etq, valor)
            else:
                lienzo.silueta(v, f, m)
        print('  %s: %d mallas, %d caras' % (idr, len(mallas[idr]), sum(len(f) for (_, _, f, _) in mallas[idr])),
              file=sys.stderr)
        mascaras[idr] = m

    # centro del tramo de médula (para su nombre): caja de su máscara
    W = lienzo.W
    med = mascaras['medula_espinal']
    filas_med = [f for f in range(lienzo.H) if any(med[f * W:(f + 1) * W])]
    cols_med = [c for c in range(W) if any(med[f * W + c] for f in filas_med[::4])]
    centro_medula = ((min(cols_med) + max(cols_med)) / 2.0, (min(filas_med) + max(filas_med)) / 2.0)

    regiones, cajas, centroides = {}, {}, {}
    area_min_px = AREA_MIN / (RES * RES)
    tol_px = TOLERANCIA / RES
    for idr in ORDEN:
        lazos = [l for l in contornos(lienzo, mascaras[idr]) if area(l) > area_min_px]
        lazos.sort(key=area, reverse=True)
        trazos = []
        for l in lazos:
            pts = suavizar(simplificar(l, tol_px))
            trazos.append(trazado(pts, escala))
        regiones[idr] = trazos
        xs = [p[0] for l in lazos for p in l]
        ys_ = [p[1] for l in lazos for p in l]
        cajas[idr] = (min(xs), min(ys_), max(xs), max(ys_))
        # centroide del lazo mayor
        l = lazos[0]
        A = -area(l)  # el cordón con el signo original
        cx = sum((l[i][0] + l[(i + 1) % len(l)][0]) * (l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1]) for i in range(len(l))) / (6 * A)
        cy = sum((l[i][1] + l[(i + 1) % len(l)][1]) * (l[i][0] * l[(i + 1) % len(l)][1] - l[(i + 1) % len(l)][0] * l[i][1]) for i in range(len(l))) / (6 * A)
        centroides[idr] = (cx, cy)
        print('  %s: %d islas, %d puntos' % (idr, len(lazos), sum(t.count('L') for t in trazos)), file=sys.stderr)

    # surcos del telencéfalo
    detalles = {}
    lineas = [l for l in surcos(lienzo, etq, grupo_de, mascaras['telencefalo'])
              if largo(l) * RES >= SURCO_LARGO_MIN]
    lineas.sort(key=largo, reverse=True)
    detalles['telencefalo'] = [trazado(suavizar(simplificar(l, SURCO_TOLERANCIA / RES, cerrado=False), cerrado=False), escala, cerrado=False)
                               for l in lineas[:SURCOS_MAX]]
    print('  surcos: %d' % len(lineas), file=sys.stderr)

    # etiquetas: dentro para las regiones grandes, fuera con guía para las demás
    def vb(p):
        return round(p[0] * escala, 1), round(p[1] * escala, 1)

    tel = cajas['telencefalo']
    ctel = vb(((tel[0] + tel[2]) / 2.0, tel[1] + (tel[3] - tel[1]) * 0.36))
    ccer = vb(centroides['cerebelo'])
    cdi = vb(centroides['diencefalo'])
    ctr = vb(((cajas['tronco_encefalico'][0] + cajas['tronco_encefalico'][2]) / 2.0,
              cajas['tronco_encefalico'][3] - (cajas['tronco_encefalico'][3] - cajas['tronco_encefalico'][1]) * 0.22))
    cme = vb(centro_medula)
    izq = round(lienzo.px(y0 + 1.0, 0)[0] * escala + 2, 1)
    alto_vb = round(lienzo.H * escala, 1)
    etiquetas = {
        'telencefalo': {'modo': 'dentro', 'x': ctel[0], 'y': ctel[1]},
        'cerebelo': {'modo': 'dentro', 'x': ccer[0], 'y': ccer[1] + 4},
        'diencefalo': {'modo': 'fuera', 'ancla': 'end', 'x': izq + 76, 'y': round(ctr[1] - 24, 1),
                       'guia': 'M%s %s L%s %s' % (cdi[0], cdi[1], izq + 80, round(ctr[1] - 28, 1))},
        'tronco_encefalico': {'modo': 'fuera', 'ancla': 'end', 'x': izq + 108, 'y': round(ctr[1] + 4, 1),
                              'guia': 'M%s %s L%s %s' % (ctr[0], ctr[1], izq + 112, ctr[1])},
        'medula_espinal': {'modo': 'fuera', 'ancla': 'start', 'x': cme[0] + 22, 'y': cme[1] + 4,
                           'guia': 'M%s %s L%s %s' % (cme[0], cme[1], cme[0] + 18, cme[1])},
    }

    salida = {
        '_nota': ('Mapa de orientación: silueta del encéfalo en vista lateral izquierda, proyectada desde las '
                  'mallas de %s con herramientas/proyectar-mapa.py. No editar a mano: cambia las '
                  'mallas o el script y vuelve a generarlo. Las claves de `regiones` son ids de fichas raíz; '
                  'cada región es una lista de trazados SVG (una isla por trazado). `detalles` son los surcos '
                  'visibles entre grupos de circunvoluciones. `recortados` lista las regiones que solo entran '
                  'en parte (la médula, cortada %s mm bajo el bulbo), pintadas con trazo discontinuo. `etiquetas` sitúa el nombre de '
                  'cada región (`dentro` = sobre la propia región; `fuera` = con línea guía).'
                  % (FUENTES[FUENTE_MAPA]['fuente']['nombre'], _fmt(MEDULA_LARGO))),
        'fuente': FUENTES[FUENTE_MAPA]['fuente'],
        'vista': 'lateral izquierda',
        'viewBox': '0 0 %d %s' % (ANCHO_REF, _fmt(alto_vb)),
        'ancho_ref': ANCHO_REF,
        'escala_mm': round(escala / RES, 4),
        'recortados': RECORTADOS,
        'regiones': regiones,
        'orden': ORDEN,
        'detalles': detalles,
        'etiquetas': etiquetas,
    }
    with open(DESTINO, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('escrito', os.path.relpath(DESTINO, RAIZ), file=sys.stderr)

    colores = colores_region()
    for region, configs in LAMINAS.items():
        for config in configs:
            fuente = config.get('fuente', FUENTE_MAPA)
            origen = por_fuente[fuente]
            if config.get('mallas', region) in origen:
                lamina(region, config, origen, colores)
            else:
                print('aviso: sin mallas de %s para la lámina %s/%s' % (fuente, region, config['eje']),
                      file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        sys.exit(__doc__)
    main()
