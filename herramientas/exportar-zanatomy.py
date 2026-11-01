#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporta a OBJ, uno por archivo y en coordenadas de mundo, los objetos del sistema nervioso
central de Z-Anatomy que lee `proyectar-mapa.py`. Z-Anatomy (CC BY-SA 4.0, derivado de
BodyParts3D) publica sus modelos como un archivo de Blender (`Startup.blend`, dentro de
`Z-Anatomy.zip` en https://github.com/Z-Anatomy/Models-of-human-anatomy), así que este script
necesita Blender o el módulo `bpy` (`pip install bpy`); es el único de `herramientas/` que sale
de la biblioteca estándar y no forma parte de la construcción del sitio.

    python3 herramientas/exportar-zanatomy.py Startup.blend fuentes-3d/zanatomy/

o, dentro de Blender:

    blender -b Startup.blend -P herramientas/exportar-zanatomy.py -- fuentes-3d/zanatomy/

Escribe una subcarpeta por región N1 (`REGIONES`, con el id de su ficha) con un `.obj` por
objeto y un `indice.tsv` (archivo, nombre del objeto, colecciones de Z-Anatomy a las que
pertenece, incluidas las colecciones madre). `proyectar-mapa.py` usa ese índice para agrupar
mallas por colección («@Frontal lobe») además de por nombre de archivo.

Las unidades de la escena son metros (`proyectar-mapa.py` las pasa a mm) y los ejes coinciden
con BodyParts3D: x+ = lado izquierdo, y- = anterior, z+ = superior. Los objetos `.g` y `.j` de
Z-Anatomy son rótulos y agrupadores sin geometría útil y se saltan. Los vértices que ninguna
cara usa (hay alguno suelto, lejos de la pieza) se descartan.
"""
import os
import re
import sys

import bpy

# Región (id de la ficha raíz) -> colecciones de Z-Anatomy cuyo árbol se exporta entero y
# objetos sueltos que van por nombre (la pineal cuelga de «Endocrine glands»; el corte
# transversal de la médula son objetos sin colección propia en la raíz del sistema nervioso).
REGIONES = {
    'telencefalo': {'colecciones': ['Telencephalon']},
    'diencefalo': {'colecciones': ['Diencephalon'], 'objetos': [r'^Pineal gland$']},
    # la mitad derecha del bulbo y varios núcleos de nervios craneales solo cuelgan de «Head»;
    # la base del pedúnculo cerebral (crus cerebri) está archivada bajo los pedúnculos cerebelosos
    'tronco_encefalico': {'colecciones': ['Brainstem'], 'objetos': [
        r'^Medulla oblongata\.r$', r'^Base of peduncle\.[lr]$',
        r'^(Nucleus ambiguus|Nucleus of (hypoglossal|trochlear|solitary)|Posterior nucleus of vagus|'
        r'(Anterior|Posterior) cochlear nucleus|Inferior salivatory nucleus)']},
    'cerebelo': {'colecciones': ['Cerebellum'], 'excluir': r'^Base of peduncle'},
    'medula_espinal': {'colecciones': ['Spinal cord'], 'objetos': [
        r'^(Anterior|Posterior) horn of spinal cord$', r'^White matter of spinal cord$',
        r'^Central canal$', r'^(Intermediolateral|Intermediomedial) nucleus$',
        r'^Nucleus proprius$', r'^Lateral intermediate substance$', r'^Spinal reticular process$',
        r' tract$', r' fasciculus( proprius)?$', r'^Posterolateral tract$']},
}
# Lo que no es sistema nervioso central aunque caiga en esas colecciones.
EXCLUIR = re.compile(r'\.(g|j)$|muscle|bone|Mandible|artery|vein|nerve\b|ganglion', re.I)


def limpio(nombre):
    return re.sub(r'[^A-Za-z0-9]+', '_', nombre.strip()).strip('_')


def madres():
    """{colección: [colecciones madre…]} (cadena completa hacia la raíz)."""
    padre = {}
    for c in bpy.data.collections:
        for h in c.children:
            padre.setdefault(h.name, c.name)
    arriba = {}
    for nombre in padre:
        cadena, n = [], padre.get(nombre)
        while n and n not in cadena:
            cadena.append(n)
            n = padre.get(n)
        arriba[nombre] = cadena
    return arriba


def colecciones_de(ob, arriba):
    todas = []
    for c in ob.users_collection:
        for n in [c.name] + arriba.get(c.name, []):
            if n not in todas:
                todas.append(n)
    return todas


def exportar(ruta_blend, salida):
    if ruta_blend:
        bpy.ops.wm.open_mainfile(filepath=ruta_blend)
    arriba = madres()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for region, cfg in REGIONES.items():
        carpeta = os.path.join(salida, region)
        os.makedirs(carpeta, exist_ok=True)
        objetos = []
        for nombre_col in cfg.get('colecciones', []):
            col = bpy.data.collections.get(nombre_col)
            if col is None:
                print('aviso: no existe la colección', nombre_col, file=sys.stderr)
                continue
            objetos.extend(col.all_objects)
        patrones = [re.compile(p) for p in cfg.get('objetos', [])]
        if patrones:
            objetos.extend(ob for ob in bpy.data.objects if any(p.search(ob.name) for p in patrones))
        vistos = set()
        filas = []
        excluir = re.compile(cfg['excluir']) if cfg.get('excluir') else None
        for ob in objetos:
            if ob.name in vistos or ob.type != 'MESH' or EXCLUIR.search(ob.name):
                continue
            if excluir and excluir.search(ob.name):
                continue
            vistos.add(ob.name)
            ev = ob.evaluated_get(depsgraph)
            malla = ev.to_mesh()
            try:
                malla.calc_loop_triangles()
                tris = [tuple(t.vertices) for t in malla.loop_triangles]
                if not tris:
                    continue
                usados = sorted(set(i for t in tris for i in t))
                nuevo = dict((i, k + 1) for k, i in enumerate(usados))
                M = ob.matrix_world
                archivo = limpio(ob.name) + '.obj'
                with open(os.path.join(carpeta, archivo), 'w', encoding='utf-8') as f:
                    f.write('# Z-Anatomy (CC BY-SA 4.0), objeto "%s", coordenadas de mundo en unidades de la escena\n'
                            % ob.name)
                    f.write('o %s\n' % limpio(ob.name))
                    for i in usados:
                        co = M @ malla.vertices[i].co
                        f.write('v %.4f %.4f %.4f\n' % (co.x, co.y, co.z))
                    for t in tris:
                        f.write('f %d %d %d\n' % tuple(nuevo[i] for i in t))
                filas.append((archivo, ob.name, '|'.join(colecciones_de(ob, arriba)), len(usados), len(tris)))
            finally:
                ev.to_mesh_clear()
        filas.sort()
        with open(os.path.join(carpeta, 'indice.tsv'), 'w', encoding='utf-8') as f:
            f.write('archivo\tobjeto\tcolecciones\tvertices\ttriangulos\n')
            for fila in filas:
                f.write('%s\t%s\t%s\t%d\t%d\n' % fila)
        print('%s: %d objetos' % (region, len(filas)))
        total += len(filas)
    print('%d objetos exportados en %s' % (total, salida))
    print('unidades de la escena:', bpy.context.scene.unit_settings.system,
          bpy.context.scene.unit_settings.scale_length)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if len(args) == 2:
        exportar(args[0], args[1])
    elif len(args) == 1:
        exportar(None, args[0])
    else:
        sys.exit(__doc__)
