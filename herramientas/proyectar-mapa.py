#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el mapa de orientación `src/piezas/mapa-sagital.json` a partir de las mallas de
BodyParts3D: proyecta cada región N1 al plano sagital (vista lateral izquierda) y traza
el contorno de la silueta. Nada se dibuja a mano: si una malla cambia, se vuelve a correr
el script y el mapa cambia con ella.

Entrada: las mallas de `fuentes-3d/` (fuera de git: son pesadas y ya están publicadas), una
carpeta por fuente según `FUENTES` y, dentro, una subcarpeta por región nombrada con el id de
la ficha raíz (con o sin prefijo numérico: `04_cerebelo` o `cerebelo`) con sus `.obj`:

- `fuentes-3d/bodyparts3d/`: BodyParts3D 4.0 (árbol PART-OF), mm; x+ = lado izquierdo,
  y- = anterior, z+ = superior. De aquí salen el mapa y las láminas del tronco y el telencéfalo.
- `fuentes-3d/zanatomy/`: objetos exportados del `Startup.blend` de Z-Anatomy con
  `herramientas/exportar-zanatomy.py` (metros, mismos ejes). De aquí sale el cerebelo, que
  BodyParts3D solo trae en dos mitades.

    python3 herramientas/proyectar-mapa.py

Salida: `src/piezas/mapa-sagital.json` (el mapa de regiones) y una lámina por región en
`src/piezas/laminas/<region>.json` (las partes con ficha de esa región, cada una con su
silueta visible en la vista elegida, según `LAMINAS`). El generador lee ambas cosas tal cual.

Limitaciones conocidas de BodyParts3D que el script compensa y el JSON declara:
- No hay malla de la médula espinal (solo del conducto central). La médula se dibuja como un
  tramo esquemático que continúa el contorno caudal del bulbo, y queda marcada en
  `esquematicos` para que el sitio la pinte con trazo discontinuo.
- En el árbol PART-OF el diencéfalo no incluye el tálamo. Su silueta sale del tercer
  ventrículo (cuyas paredes son el tálamo y el hipotálamo), el hipotálamo, la habénula y la
  pineal: en vista lateral coincide razonablemente con el perfil del diencéfalo.

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
MEDULA_LARGO = 24.0  # mm del tramo esquemático de médula por debajo del bulbo
MEDULA_SOLAPE = 5.0  # mm por encima del extremo del bulbo donde se mide su anchura
MEDULA_ESTRECHA = 0.82  # anchura final del tramo respecto a la base del bulbo

# Orden de pintado (lo de atrás primero) y qué regiones son esquemáticas.
ORDEN = ['telencefalo', 'tronco_encefalico', 'medula_espinal', 'cerebelo', 'diencefalo']
ESQUEMATICOS = ['medula_espinal']

# Vistas: (x, y, z) en mm -> (horizontal, vertical, profundidad); profundidad mayor = más
# cerca del observador. BodyParts3D: x+ = izquierda del cuerpo, y- = anterior, z+ = superior.
VISTAS = {
    'lateral': lambda x, y, z: (y, z, x),      # desde la izquierda; anterior a la izquierda
    'anterior': lambda x, y, z: (x, z, -y),    # de frente; la izquierda del cuerpo a la derecha
    'posterior': lambda x, y, z: (-x, z, y),   # desde atrás
}

# Fuentes de mallas: carpeta (relativa a la raíz), factor a mm y atribución.
FUENTES = {
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
}
FUENTE_MAPA = 'bodyparts3d'

# Láminas: por región, una lista; cada una con el eje de la ficha al que corresponde, la fuente,
# la vista (`VISTAS`) y qué mallas (por fragmento del nombre de archivo) forman cada parte con
# ficha. Una malla que no case con
# ninguna parte se dibuja apagada y sin enlace.
LAMINAS = {
    'tronco_encefalico': [{
        'eje': 'niveles', 'fuente': 'bodyparts3d', 'vista': 'lateral',
        'partes': {
            'mesencefalo': ('midbrain', 'superior_colliculus', 'inferior_colliculus', 'cerebral_aqueduct'),
            'puente': ('pons',),
            'bulbo_raquideo': ('medulla_oblongata',),
        },
    }],
    'telencefalo': [{
        'eje': 'lobulos', 'fuente': 'bodyparts3d', 'vista': 'lateral',
        'partes': {
            'lobulo_frontal': ('superior_frontal', 'middle_frontal', 'inferior_frontal', 'precentral'),
            'lobulo_parietal': ('postcentral', 'superior_parietal', 'supramarginal', 'angular'),
            'lobulo_temporal': ('middle_temporal', 'inferior_temporal', 'fusiform', 'parahippocampal'),
            'lobulo_occipital': ('occipital',),
            'insula': ('insula',),
        },
    }],
    'cerebelo': [
        {
            # vista posterior: el vermis en medio y los hemisferios a los lados
            'eje': 'regiones', 'fuente': 'zanatomy', 'vista': 'posterior',
            'partes': {
                'vermis': ('Lingula', 'Central_lobule', 'Culmen', 'Declive', 'Folium', 'Tuber',
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
            'eje': 'lobulos', 'fuente': 'zanatomy', 'vista': 'lateral',
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
}
LAMINAS_DIR = os.path.join(RAIZ, 'src', 'piezas', 'laminas')
TOKENS = os.path.join(RAIZ, 'src', 'estilos', 'tokens.css')
ETIQUETA_ANCHO = 100  # px del viewBox (cuerda) que necesita un nombre para ir dentro de su parte
ETIQUETA_ALTO = 22
MARGEN_ETIQUETAS = 150  # px del viewBox reservados a cada lado para los nombres de fuera

# Circunvoluciones que delimitan los surcos que se dibujan sobre la cara lateral.
# Solo el surco central: BodyParts3D no trae la circunvolución temporal superior, así que la
# frontera visible entre frontal/parietal y temporal sería el surco temporal superior, no el
# lateral, y dibujarlo confundiría.
GRUPOS_SURCOS = {
    'precentral': ('precentral',),
    'postcentral': ('postcentral',),
}
SURCOS = [('precentral', 'postcentral')]
SURCO_LARGO_MIN = 14.0   # mm
SURCO_TOLERANCIA = 1.2   # mm: el surco se simplifica más que el contorno




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


def cargar(fuente):
    """{region: [(nombre_archivo, vertices_mm, caras)]} de una fuente de `FUENTES`."""
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
        for nombre in sorted(os.listdir(ruta)):
            if nombre.lower().endswith('.obj'):
                v, f = leer_obj(os.path.join(ruta, nombre))
                if escala != 1.0:
                    v = [(x * escala, y * escala, z * escala) for (x, y, z) in v]
                mallas.setdefault(idr, []).append((nombre, v, f))
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

    def silueta(self, v, f, mascara, prof=None, etq=None, valor=0, vista='lateral'):
        proy = VISTAS[vista]
        T = [proy(*p) for p in v]
        P = [self.px(h, vv) for (h, vv, _) in T]
        for a, b, c in f:
            x = (T[a][2] + T[b][2] + T[c][2]) / 3.0 if prof is not None else 0.0
            self.triangulo(mascara, P[a], P[b], P[c], prof, etq, valor, x)
            for i in (a, b, c):  # un vértice siempre marca su píxel: sin huecos entre caras
                col, fila = int(P[i][0]), int(P[i][1])
                if 0 <= col < self.W and 0 <= fila < self.H:
                    mascara[fila * self.W + col] = 1


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
    proy = VISTAS[vista]
    pts = [proy(*p) for (_, v, _) in mallas[region] for p in v]
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
    for nombre, v, f in mallas[region]:
        valor = 0
        for parte, claves in config['partes'].items():
            if any(k in nombre for k in claves):
                valor = codigo[parte]
        if valor:
            lienzo.silueta(v, f, mascara, prof, etq, valor, vista)
        else:
            lienzo.silueta(v, f, mascara, vista=vista)
    for i in range(len(etq)):
        if mascara[i] and not etq[i]:
            etq[i] = SIN

    area_min_px = AREA_MIN / (RES * RES)
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
    desplaza = MARGEN_ETIQUETAS if izq else 0
    ancho_vb = ancho_ref + desplaza + (MARGEN_ETIQUETAS if der else 0)
    for lado, lista in (('izq', izq), ('der', der)):
        lista.sort(key=lambda p: centros[p][1])
        y_prev = -1e9
        for parte in lista:
            cx, cy = centros[parte]
            y = max(cy, y_prev + ETIQUETA_ALTO)  # que no se monten
            if lado == 'der':
                x_texto, ancla, fin = ancho_ref + desplaza + 14, 'start', ancho_ref + desplaza + 10
            else:
                x_texto, ancla, fin = MARGEN_ETIQUETAS - 14, 'end', MARGEN_ETIQUETAS - 10
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

    base = colores.get(region, '#888888')
    presentes = [p for p in partes if p in trazos]
    paleta = dict(zip(presentes, tonos(base, len(presentes))))
    salida = {
        '_nota': ('Lámina de %s (eje %s), vista %s: silueta visible de cada parte con ficha, '
                  'proyectada desde las mallas de %s con herramientas/proyectar-mapa.py. No editar a mano. '
                  '`partes` son ids de fichas; `sin_ficha` son las mallas de la región que no pertenecen a '
                  'ninguna parte con ficha (se pintan apagadas). `colores` son tonos del color de la región.'
                  % (region, config['eje'], vista, FUENTES[config['fuente']]['fuente']['nombre'])),
        'fuente': FUENTES[config['fuente']]['fuente'],
        'region': region,
        'eje': config['eje'],
        'vista': vista,
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
    mallas = por_fuente[FUENTE_MAPA]
    faltan = [r for r in ORDEN if r not in mallas and r not in ESQUEMATICOS]
    if faltan:
        sys.exit('faltan regiones: %s' % ', '.join(faltan))

    ys = [p[1] for m in mallas.values() for (_, v, _) in m for p in v]
    zs = [p[2] for m in mallas.values() for (_, v, _) in m for p in v]
    y0, y1 = min(ys) - MARGEN, max(ys) + MARGEN
    z0, z1 = min(zs) - MARGEN - MEDULA_LARGO, max(zs) + MARGEN
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
        for nombre, v, f in mallas[idr]:
            valor = 0
            if idr == 'telencefalo':
                for g, claves in GRUPOS_SURCOS.items():
                    if any(k in nombre for k in claves):
                        valor = codigo.setdefault(nombre, len(codigo) + 1)
                        grupo_de[valor] = g
                lienzo.silueta(v, f, m, prof, etq, valor)
            else:
                lienzo.silueta(v, f, m)
            print('  %s / %s: %d caras' % (idr, nombre, len(f)), file=sys.stderr)
        mascaras[idr] = m

    # médula espinal esquemática: continúa el borde caudal del bulbo hacia abajo
    tronco = mascaras['tronco_encefalico']
    W = lienzo.W
    fila_fin = max(f for f in range(lienzo.H) if any(tronco[f * W:(f + 1) * W]))
    # la malla del bulbo termina en un corte oblicuo: la anchura se toma unos mm más arriba,
    # donde el bulbo aún es completo, y el tramo arranca desde ahí solapando la punta
    fila_base = fila_fin - int(MEDULA_SOLAPE / RES)
    cols = [c for c in range(W) if tronco[fila_base * W + c]]
    c0, c1 = min(cols), max(cols) + 1
    cen, semi = (c0 + c1) / 2.0, (c1 - c0) / 2.0
    med = lienzo.nuevo()
    filas = int((MEDULA_LARGO + MEDULA_SOLAPE) / RES)
    for k in range(filas):
        s = semi * (1 - (1 - MEDULA_ESTRECHA) * k / float(filas))
        a, b = int(round(cen - s)), int(round(cen + s))
        f = fila_base + k
        if f < lienzo.H:
            med[f * W + a:f * W + b] = b'\x01' * (b - a)
    mascaras['medula_espinal'] = med
    centro_medula = (cen, fila_fin + (filas - (fila_fin - fila_base)) / 2.0)

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
                               for l in lineas[:1]]
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
                  'mallas de BodyParts3D con herramientas/proyectar-mapa.py. No editar a mano: cambia las '
                  'mallas o el script y vuelve a generarlo. Las claves de `regiones` son ids de fichas raíz; '
                  'cada región es una lista de trazados SVG (una isla por trazado). `detalles` son los surcos '
                  'visibles entre grupos de circunvoluciones. `esquematicos` lista las regiones sin malla, '
                  'dibujadas por continuidad y pintadas con trazo discontinuo. `etiquetas` sitúa el nombre de '
                  'cada región (`dentro` = sobre la propia región; `fuera` = con línea guía).'),
        'fuente': FUENTES[FUENTE_MAPA]['fuente'],
        'vista': 'lateral izquierda',
        'viewBox': '0 0 %d %s' % (ANCHO_REF, _fmt(alto_vb)),
        'ancho_ref': ANCHO_REF,
        'escala_mm': round(escala / RES, 4),
        'esquematicos': ESQUEMATICOS,
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
            origen = por_fuente[config['fuente']]
            if region in origen:
                lamina(region, config, origen, colores)
            else:
                print('aviso: sin mallas de %s para la lámina %s/%s' % (config['fuente'], region, config['eje']),
                      file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        sys.exit(__doc__)
    main()
