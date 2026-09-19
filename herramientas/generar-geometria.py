#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la geometría PROVISIONAL del cerebelo: `contenido/activos/cerebelo.glb`.

Esto **no es el modelo definitivo**. Es una aproximación por código que cumple el
listón acordado en C-04: silueta reconocible, las cinco divisiones diferenciadas y
posiciones relativas correctas, sin folia ni detalle de superficie. El modelo real lo
está haciendo Max en Blender, que exporta glTF de forma nativa: cuando esté listo,
sustituye a este archivo y no hay que tocar una línea de código (RT-05, DEC-06).

**La malla se parte en seis sectores, no en cinco piezas.** Una estructura pertenece a
varios ejes a la vez —el nódulo es vermis y es floculonodular—, así que partirla por un
solo eje obligaría a elegir cuál de los dos se representa mal. Los seis sectores son
{vermis, hemisferios} × {anterior, posterior, floculonodular}, y cada división del
esquema se compone uniendo los que le corresponden.

Solo biblioteca estándar. Uso:
    python herramientas/generar-geometria.py
"""

import json
import math
import os
import struct

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'contenido', 'activos')

# Semiejes del elipsoide base, en unidades arbitrarias (el visor encuadra solo).
A = 1.00   # anchura, de hemisferio a hemisferio
B = 0.62   # altura, del lóbulo anterior al floculonodular
C = 0.50   # profundidad

ANCHO_VERMIS = 0.16      # fracción del ancho local que ocupa el vermis
CORTE_ANTERIOR = 0.34    # y por encima de esto es lóbulo anterior
CORTE_FLOCULO = -0.46    # y por debajo de esto es lóbulo floculonodular

FILAS = 56      # subdivisiones en y
COLUMNAS = 96   # subdivisiones alrededor


def _profundidad(x):
    """Los hemisferios abultan; el vermis queda hundido entre ellos.

    Es lo que hace que la franja medial se reconozca como tal en la silueta, que es
    justo lo que exige un N2 de divisiones.
    """
    hundido = math.exp(-(x / (ANCHO_VERMIS * 1.15)) ** 2)
    return C * (1.0 - 0.24 * hundido)


def superficie():
    """Rejilla de vértices sobre un elipsoide deformado, cerrada en los polos."""
    vertices = []
    for i in range(FILAS + 1):
        phi = math.pi * i / FILAS              # 0 arriba (anterior), pi abajo
        y = B * math.cos(phi)
        radio = math.sin(phi)
        for j in range(COLUMNAS):
            theta = 2.0 * math.pi * j / COLUMNAS
            x = A * radio * math.cos(theta)
            z = _profundidad(x) * radio * math.sin(theta)
            vertices.append((x, y, z))
    return vertices


def sector_de(x, y):
    """A qué sector pertenece un punto: (region, lobulo).

    El ancho del vermis es **proporcional al ancho local**, no fijo: con un umbral fijo,
    cerca de los polos superior e inferior la malla se estrecha por debajo de ese umbral
    y el casquete entero acababa clasificado como vermis. El vermis es una franja medial
    estrecha a cualquier altura, no un cono.
    """
    radio = math.sqrt(max(0.0, 1.0 - (y / B) ** 2))
    umbral = ANCHO_VERMIS * A * max(radio, 0.45)
    region = 'vermis' if abs(x) < umbral else 'hemisferios_cerebelosos'
    if y > CORTE_ANTERIOR:
        lobulo = 'lobulo_anterior'
    elif y < CORTE_FLOCULO:
        lobulo = 'lobulo_floculonodular'
    else:
        lobulo = 'lobulo_posterior'
    return region, lobulo


def triangulos(vertices):
    """Triángulos de la rejilla, agrupados por sector."""
    grupos = {}
    for i in range(FILAS):
        for j in range(COLUMNAS):
            j2 = (j + 1) % COLUMNAS
            a = i * COLUMNAS + j
            b = i * COLUMNAS + j2
            c = (i + 1) * COLUMNAS + j
            d = (i + 1) * COLUMNAS + j2
            for tri in ((a, c, d), (a, d, b)):
                # El sector se decide por el centro del triángulo, para que un mismo
                # triángulo no quede repartido entre dos.
                cx = sum(vertices[k][0] for k in tri) / 3.0
                cy = sum(vertices[k][1] for k in tri) / 3.0
                grupos.setdefault(sector_de(cx, cy), []).append(tri)
    return grupos


def normales(vertices, todos_los_triangulos):
    acum = [[0.0, 0.0, 0.0] for _ in vertices]
    for tri in todos_los_triangulos:
        p, q, r = (vertices[k] for k in tri)
        u = (q[0] - p[0], q[1] - p[1], q[2] - p[2])
        v = (r[0] - p[0], r[1] - p[1], r[2] - p[2])
        n = (u[1] * v[2] - u[2] * v[1],
             u[2] * v[0] - u[0] * v[2],
             u[0] * v[1] - u[1] * v[0])
        for k in tri:
            acum[k][0] += n[0]
            acum[k][1] += n[1]
            acum[k][2] += n[2]
    salida = []
    for n in acum:
        largo = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        salida.append((n[0] / largo, n[1] / largo, n[2] / largo))
    return salida


def _alinear(datos, relleno=b'\x00'):
    resto = len(datos) % 4
    return datos + relleno * (4 - resto) if resto else datos


def escribir_glb(ruta, sectores):
    """sectores: lista de (nombre, vertices, normales, indices)."""
    binario = bytearray()
    vistas, accesores, mallas, nodos = [], [], [], []

    for nombre, verts, norms, indices in sectores:
        # POSICIÓN
        desplazamiento = len(binario)
        for v in verts:
            binario.extend(struct.pack('<3f', *v))
        vistas.append({'buffer': 0, 'byteOffset': desplazamiento,
                       'byteLength': len(binario) - desplazamiento, 'target': 34962})
        accesores.append({
            'bufferView': len(vistas) - 1, 'componentType': 5126, 'count': len(verts),
            'type': 'VEC3',
            'min': [min(v[k] for v in verts) for k in range(3)],
            'max': [max(v[k] for v in verts) for k in range(3)],
        })
        acc_pos = len(accesores) - 1

        # NORMAL
        desplazamiento = len(binario)
        for n in norms:
            binario.extend(struct.pack('<3f', *n))
        vistas.append({'buffer': 0, 'byteOffset': desplazamiento,
                       'byteLength': len(binario) - desplazamiento, 'target': 34962})
        accesores.append({'bufferView': len(vistas) - 1, 'componentType': 5126,
                          'count': len(norms), 'type': 'VEC3'})
        acc_nor = len(accesores) - 1

        # ÍNDICES
        binario.extend(b'\x00' * ((4 - len(binario) % 4) % 4))
        desplazamiento = len(binario)
        for idx in indices:
            binario.extend(struct.pack('<I', idx))
        vistas.append({'buffer': 0, 'byteOffset': desplazamiento,
                       'byteLength': len(binario) - desplazamiento, 'target': 34963})
        accesores.append({'bufferView': len(vistas) - 1, 'componentType': 5125,
                          'count': len(indices), 'type': 'SCALAR'})
        acc_idx = len(accesores) - 1

        mallas.append({'name': nombre, 'primitives': [
            {'attributes': {'POSITION': acc_pos, 'NORMAL': acc_nor}, 'indices': acc_idx}]})
        nodos.append({'name': nombre, 'mesh': len(mallas) - 1})

    gltf = {
        'asset': {'version': '2.0',
                  'generator': 'Neuroteca generar-geometria.py — forma aproximada, no definitiva'},
        'scene': 0,
        'scenes': [{'nodes': list(range(len(nodos)))}],
        'nodes': nodos,
        'meshes': mallas,
        'accessors': accesores,
        'bufferViews': vistas,
        'buffers': [{'byteLength': len(binario)}],
    }

    json_chunk = _alinear(json.dumps(gltf, separators=(',', ':')).encode('utf-8'), b' ')
    bin_chunk = _alinear(bytes(binario))
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)

    with open(ruta, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(json_chunk), 0x4E4F534A))
        f.write(json_chunk)
        f.write(struct.pack('<II', len(bin_chunk), 0x004E4942))
        f.write(bin_chunk)
    return total


def main():
    os.makedirs(DESTINO, exist_ok=True)
    verts = superficie()
    grupos = triangulos(verts)
    todos = [t for tris in grupos.values() for t in tris]
    norms = normales(verts, todos)

    sectores = []
    for (region, lobulo), tris in sorted(grupos.items()):
        # Cada sector lleva solo sus vértices, renumerados.
        usados, mapa = [], {}
        indices = []
        for tri in tris:
            for k in tri:
                if k not in mapa:
                    mapa[k] = len(usados)
                    usados.append(k)
                indices.append(mapa[k])
        sectores.append((
            '%s__%s' % (region, lobulo),
            [verts[k] for k in usados],
            [norms[k] for k in usados],
            indices,
        ))

    ruta = os.path.join(DESTINO, 'cerebelo.glb')
    total = escribir_glb(ruta, sectores)

    metadatos = {
        'id': 'cerebelo',
        'nivel_detalle': 'N2',
        'origen': 'propio',
        'licencia': 'CC BY-SA 4.0',
        'estado': 'provisional',
        'peso_bytes': total,
        'equivalente_textual': (
            'Esquema del cerebelo en vista posterior: dos hemisferios abultados a los '
            'lados, separados por la franja más estrecha y hundida del vermis, y '
            'recorridos de arriba abajo por los lóbulos anterior, posterior y '
            'floculonodular.'),
        'sectores': [s[0] for s in sectores],
        'nota': ('Forma aproximada generada por código, no modelado definitivo. Cumple el '
                 'listón de C-04: silueta reconocible y divisiones diferenciadas, sin folia. '
                 'Lo más débil de la aproximación son los extremos superior e inferior, donde '
                 'la malla se estrecha más de lo que lo hace un cerebelo real.'),
    }
    with open(os.path.join(DESTINO, 'cerebelo.json'), 'w', encoding='utf-8') as f:
        json.dump(metadatos, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print('cerebelo.glb: %d sectores, %.1f KB' % (len(sectores), total / 1024.0))
    for nombre, v, _n, i in sectores:
        print('  %-44s %5d vértices  %5d triángulos' % (nombre, len(v), len(i) // 3))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
