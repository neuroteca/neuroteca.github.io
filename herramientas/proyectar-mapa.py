#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el mapa de orientación `src/piezas/mapa-sagital.json` a partir de las mallas de
BodyParts3D: proyecta cada región N1 al plano sagital (vista lateral izquierda) y traza
el contorno de la silueta. Nada se dibuja a mano: si una malla cambia, se vuelve a correr
el script y el mapa cambia con ella.

Entrada: una carpeta con una subcarpeta por región, nombrada con el id de la ficha raíz
(con o sin prefijo numérico: `04_cerebelo` o `cerebelo`), y dentro los `.obj` de
BodyParts3D (árbol PART-OF, versión 4.0, coordenadas en mm; x positiva = lado izquierdo,
y negativa = anterior, z = superior). Las mallas no entran al repositorio (son pesadas y
ya están publicadas): viven en `fuentes-3d/bodyparts3d/`, que `.gitignore` excluye.

    python3 herramientas/proyectar-mapa.py fuentes-3d/bodyparts3d/

Salida: `src/piezas/mapa-sagital.json`, que el generador lee tal cual.

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

FUENTE = {
    'nombre': 'BodyParts3D',
    'version': '4.0 (árbol PART-OF)',
    'titular': 'The Database Center for Life Science',
    'licencia': 'CC BY-SA 2.1 JP',
    'url': 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html',
    'atribucion': 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan',
}


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


def cargar(carpeta):
    """{region: [(nombre_archivo, vertices, caras)]}"""
    mallas = {}
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

    def silueta(self, v, f, mascara, prof=None, etq=None, valor=0):
        P = [self.px(y, z) for (_, y, z) in v]
        for a, b, c in f:
            x = (v[a][0] + v[b][0] + v[c][0]) / 3.0 if prof is not None else 0.0
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


# --- principal -------------------------------------------------------------------

def main(carpeta):
    mallas = cargar(carpeta)
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
        'fuente': FUENTE,
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
