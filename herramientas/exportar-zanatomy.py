#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporta a OBJ, uno por archivo y en coordenadas de mundo, los objetos de Z-Anatomy que
necesita `proyectar-mapa.py`: hoy, el cerebelo por lobulillos (BodyParts3D solo lo trae en dos
mitades). Z-Anatomy (CC BY-SA 4.0) publica sus modelos como un archivo de Blender
(`Startup.blend`, dentro de `Z-Anatomy.zip` en
https://github.com/Z-Anatomy/Models-of-human-anatomy), así que este script necesita Blender o
el módulo `bpy` (`pip install bpy`); es el único de `herramientas/` que sale de la biblioteca
estándar y no forma parte de la construcción del sitio.

    python3 herramientas/exportar-zanatomy.py Startup.blend fuentes-3d/zanatomy/cerebelo/

o, dentro de Blender:

    blender -b Startup.blend -P herramientas/exportar-zanatomy.py -- fuentes-3d/zanatomy/cerebelo/

Las unidades de la escena son metros (`proyectar-mapa.py` las pasa a mm) y los ejes coinciden
con BodyParts3D: x+ = lado izquierdo, y- = anterior, z+ = superior. Los objetos `.g` y `.j` de
Z-Anatomy son rótulos y agrupadores sin geometría útil: se saltan solos porque no son mallas o
no tienen triángulos.
"""
import os
import re
import sys

import bpy

# Objetos del cerebelo de Z-Anatomy (sufijo .l/.r en los pares). Para otra región, amplía
# este patrón y crea su carpeta en fuentes-3d/zanatomy/.
PATRON = re.compile(
    r'^(Anterior quadrangular lobule|Posterior quadrangular lobule|Superior semilunar lobule|'
    r'Inferior semilunar lobule|Gracile lobule|Biventral lobule|Tonsil of cerebellum|Flocculus|'
    r'Peduncle of flocculus|Wing of central lobule|Central lobule|Culmen|Declive|Folium of vermis|'
    r'Tuber of vermis|Pyramis of vermis|Uvula of vermis|Nodule of vermis|Lingula of cerebellum|'
    r'Superior cerebellar peduncle)(\.[lr])?\s*$')


def limpio(nombre):
    return re.sub(r'[^A-Za-z0-9]+', '_', nombre.strip()).strip('_')


def exportar(ruta_blend, salida):
    if ruta_blend:
        bpy.ops.wm.open_mainfile(filepath=ruta_blend)
    os.makedirs(salida, exist_ok=True)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    n = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or not PATRON.match(ob.name):
            continue
        ev = ob.evaluated_get(depsgraph)
        malla = ev.to_mesh()
        try:
            malla.calc_loop_triangles()
            if not malla.loop_triangles:
                continue
            M = ob.matrix_world
            ruta = os.path.join(salida, limpio(ob.name) + '.obj')
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write('# Z-Anatomy (CC BY-SA 4.0), objeto "%s", coordenadas de mundo en metros\n' % ob.name)
                f.write('o %s\n' % limpio(ob.name))
                for v in malla.vertices:
                    co = M @ v.co
                    f.write('v %.4f %.4f %.4f\n' % (co.x, co.y, co.z))
                for t in malla.loop_triangles:
                    f.write('f %d %d %d\n' % tuple(i + 1 for i in t.vertices))
            print('%s: %d vértices, %d triángulos' % (ob.name, len(malla.vertices), len(malla.loop_triangles)))
            n += 1
        finally:
            ev.to_mesh_clear()
    print('%d objetos exportados en %s' % (n, salida))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if len(args) == 2:
        exportar(args[0], args[1])
    elif len(args) == 1:
        exportar(None, args[0])
    else:
        sys.exit(__doc__)
