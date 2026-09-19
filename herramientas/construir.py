#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Neuroteca.

Lee el contenido de `contenido/`, lo valida contra el esquema y escribe el sitio
estático en `docs/`, que es lo que publica GitHub Pages.

Solo biblioteca estándar (DEC-01, RT-02): este script debe seguir funcionando dentro
de diez años sin instalar nada.

Uso:
    python herramientas/construir.py            construye
    python herramientas/construir.py --validar  solo valida, no escribe
"""

import json
import os
import re
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENIDO = os.path.join(RAIZ, 'contenido')
FUENTE = os.path.join(RAIZ, 'src')
SALIDA = os.path.join(RAIZ, 'docs')

NIVELES = ('N1', 'N2', 'N3', 'N4', 'N5')
TIPOS = ('estructura', 'fundacional')
ESTADOS = ('borrador', 'revisado')

# Campos obligatorios, segun el tipo de ficha (esquema-contenido.md v0.3 + DC-01).
COMUNES = ('id', 'tipo', 'nombre', 'nivel_detalle', 'fuentes', 'autoria', 'estado')
PROPIOS = {
    'estructura': ('anatomia', 'fisiologia'),
    'fundacional': ('definicion', 'explicacion'),
}
# Campos de prosa donde se buscan enlaces de glosario, por tipo.
PROSA = {
    'estructura': ('anatomia', 'fisiologia'),
    'fundacional': ('definicion', 'explicacion'),
}

NIVEL_ETIQUETA = {
    'N1': 'forma general',
    'N2': 'subdivisiones',
    'N3': 'núcleos',
    'N4': 'vías y fibras',
    'N5': 'circuito',
}


class ErrorDeContenido(Exception):
    """Un fallo del contenido, no del generador.

    La construcción se detiene: nunca se publica una ficha incompleta ni un enlace
    de glosario sin destino (RT-12).
    """


# ---------------------------------------------------------------- carga

def _leer_json(ruta):
    with open(ruta, encoding='utf-8') as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise ErrorDeContenido('%s no es JSON válido: %s' % (_rel(ruta), e))


def _rel(ruta):
    return os.path.relpath(ruta, RAIZ).replace('\\', '/')


def cargar_fichas():
    """Devuelve {id: ficha} con todas las fichas de estructura y de glosario."""
    fichas = {}
    for sub in ('estructuras', 'glosario'):
        carpeta = os.path.join(CONTENIDO, sub)
        if not os.path.isdir(carpeta):
            continue
        for nombre in sorted(os.listdir(carpeta)):
            if not nombre.endswith('.json'):
                continue
            ruta = os.path.join(carpeta, nombre)
            ficha = _leer_json(ruta)
            ficha['_ruta'] = _rel(ruta)
            idf = ficha.get('id')
            if not idf:
                raise ErrorDeContenido('%s no declara `id`' % ficha['_ruta'])
            if idf in fichas:
                raise ErrorDeContenido(
                    'id repetido «%s»: %s y %s' % (idf, fichas[idf]['_ruta'], ficha['_ruta']))
            if idf != os.path.splitext(nombre)[0]:
                raise ErrorDeContenido(
                    '%s: el `id` («%s») debe coincidir con el nombre del archivo'
                    % (ficha['_ruta'], idf))
            fichas[idf] = ficha
    return fichas


# ---------------------------------------------------------------- validación

RE_ENLACE = re.compile(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]')


def _parrafos(ficha, campo):
    valor = ficha.get(campo)
    if isinstance(valor, str):
        return [valor]
    return list(valor or [])


def validar(fichas):
    """Comprueba el esquema y los enlaces. Lanza ErrorDeContenido al primer fallo."""
    problemas = []

    for idf, ficha in sorted(fichas.items()):
        donde = ficha['_ruta']

        tipo = ficha.get('tipo')
        if tipo not in TIPOS:
            problemas.append('%s: `tipo` debe ser uno de %s' % (donde, ', '.join(TIPOS)))

        for campo in COMUNES + PROPIOS.get(tipo, ()):
            if not ficha.get(campo):
                problemas.append('%s: falta el campo obligatorio `%s`' % (donde, campo))
        if ficha.get('nivel_detalle') not in NIVELES:
            problemas.append('%s: `nivel_detalle` debe ser uno de %s' % (donde, ', '.join(NIVELES)))
        if ficha.get('estado') not in ESTADOS:
            problemas.append('%s: `estado` debe ser uno de %s' % (donde, ', '.join(ESTADOS)))

        # Fuente obligatoria por ficha, sin excepción (P-01 / compuerta V).
        if not ficha.get('fuentes'):
            problemas.append('%s: ninguna ficha se publica sin al menos una fuente' % donde)

        # RT-12: un enlace de glosario sin destino detiene la construcción.
        for campo in PROSA.get(tipo, ()):
            for parrafo in _parrafos(ficha, campo):
                for destino, _texto in RE_ENLACE.findall(parrafo):
                    if destino not in fichas:
                        problemas.append(
                            '%s: el enlace [[%s]] en `%s` no tiene destino' % (donde, destino, campo))

        # Las divisiones apuntan a fichas que existen.
        for division in ficha.get('divisiones', []):
            if not division.get('eje') or not division.get('nombre_visible'):
                problemas.append('%s: una división no declara `eje` o `nombre_visible`' % donde)
            for parte in division.get('partes', []):
                if parte not in fichas:
                    problemas.append(
                        '%s: la división «%s» apunta a «%s», que no existe'
                        % (donde, division.get('eje'), parte))

    if problemas:
        raise ErrorDeContenido('\n  - '.join(['%d problema(s):' % len(problemas)] + problemas))


def main(argv):
    solo_validar = '--validar' in argv
    try:
        fichas = cargar_fichas()
        if not fichas:
            raise ErrorDeContenido('no hay ninguna ficha en contenido/')
        validar(fichas)
    except ErrorDeContenido as e:
        sys.stderr.write('\nLa construcción se detuvo.\n\n  %s\n\n' % e)
        return 1

    print('%d fichas válidas.' % len(fichas))
    if solo_validar:
        return 0

    # El renderizado llega en el paso 3 del plan.
    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, '.nojekyll'), 'w') as f:
        f.write('')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
