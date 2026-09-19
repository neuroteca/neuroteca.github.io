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

import io
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


# ---------------------------------------------------------------- renderizado

COLOR = {
    'vermis': 'var(--c-vermis)',
    'hemisferios_cerebelosos': 'var(--c-hemisferios)',
    'lobulo_anterior': 'var(--c-anterior)',
    'lobulo_posterior': 'var(--c-posterior)',
    'lobulo_floculonodular': 'var(--c-floculonodular)',
}


def _esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def _plantilla(nombre):
    with open(os.path.join(FUENTE, 'plantillas', nombre), encoding='utf-8') as f:
        return f.read()


def _marcado(texto, fichas, base):
    """Convierte el subconjunto permitido a HTML: [[id|texto]], **negrita**, *cursiva*."""
    salida = _esc(texto)

    def enlace(m):
        destino, visible = m.group(1), m.group(2)
        ficha = fichas[destino]
        return ('<a class="glos" href="%sestructura/%s/">%s</a>'
                % (base, destino, _esc(visible or ficha['nombre'].lower())))

    salida = RE_ENLACE.sub(enlace, salida)
    salida = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', salida)
    salida = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', salida)
    return salida


def _padres(fichas):
    """{id_hijo: (id_padre, division)} — de quién cuelga cada ficha y por qué eje."""
    mapa = {}
    for idf, ficha in fichas.items():
        for division in ficha.get('divisiones', []):
            for parte in division.get('partes', []):
                mapa.setdefault(parte, (idf, division))
    return mapa


def _navegacion(ficha, fichas, padres, base):
    """Migas hasta la ficha actual, más las divisiones del padre agrupadas por eje.

    Vive en el motor, no en la pieza visor (DEC-11): si viviera en el visor,
    apagarlo la borraría y CA-A1 fallaría.
    """
    # Migas: se sube por el eje principal hasta la raíz.
    cadena, actual, guarda = [], ficha['id'], 0
    while actual in padres and guarda < 10:
        actual = padres[actual][0]
        cadena.insert(0, actual)
        guarda += 1

    migas = ['<p class="migas-nav">']
    for idf in cadena:
        migas.append('<a href="%sestructura/%s/">%s <span class="nv">%s</span></a>'
                     % (base, idf, _esc(fichas[idf]['nombre']), fichas[idf]['nivel_detalle']))
        migas.append('<span aria-hidden="true">&rsaquo;</span>')
    migas.append('<span class="actual">%s <span class="nv">%s</span></span>'
                 % (_esc(ficha['nombre']), ficha['nivel_detalle']))
    migas.append('</p>')

    # Divisiones a mostrar: las propias si las tiene; si no, las del padre,
    # para poder moverse entre hermanos.
    duena = ficha
    if not ficha.get('divisiones') and ficha['id'] in padres:
        duena = fichas[padres[ficha['id']][0]]

    ejes = []
    for division in duena.get('divisiones', []):
        botones = []
        for parte in division.get('partes', []):
            hijo = fichas[parte]
            aqui = ' aria-current="page"' if parte == ficha['id'] else ''
            punto = ''
            if parte in COLOR:
                punto = '<span class="punto" style="background:%s"></span>' % COLOR[parte]
            botones.append(
                '<li><a href="%sestructura/%s/"%s>%s%s <span class="nv">%s</span></a></li>'
                % (base, parte, aqui, punto, _esc(hijo['nombre']), hijo['nivel_detalle']))
        ejes.append('<div class="eje"><span class="eje-nombre">%s</span><ul>%s</ul></div>'
                    % (_esc(division['nombre_visible']), ''.join(botones)))

    if not ejes:
        return ''
    return ('<nav class="partes-nav" aria-label="Navegación por estructuras">%s%s</nav>'
            % (''.join(migas), ''.join(ejes)))


def _insignias(ficha):
    partes = ['<span class="insignia nivel">Nivel %s &middot; %s</span>'
              % (ficha['nivel_detalle'], NIVEL_ETIQUETA[ficha['nivel_detalle']])]
    if ficha.get('prueba'):
        partes.append('<span class="insignia prueba">Contenido de prueba</span>')
    partes.append('<span class="insignia">%s</span>' % ficha['estado'].capitalize())
    return '<div class="insignias">%s</div>' % ''.join(partes)


def _ficha_html(ficha, fichas, base):
    h = ['<article class="ficha">', '<h1>%s</h1>' % _esc(ficha['nombre'])]
    if ficha.get('termino_latin'):
        h.append('<p class="latin">%s</p>' % _esc(ficha['termino_latin']))
    h.append(_insignias(ficha))

    if ficha['tipo'] == 'estructura':
        secciones = [('Anatomía', 'anatomia'), ('Fisiología', 'fisiologia')]
    else:
        h.append('<h2>Definición</h2>')
        h.append('<p>%s</p>' % _marcado(ficha['definicion'], fichas, base))
        secciones = [('Explicación', 'explicacion')]

    for titulo, campo in secciones:
        h.append('<h2>%s</h2>' % titulo)
        for parrafo in _parrafos(ficha, campo):
            h.append('<p>%s</p>' % _marcado(parrafo, fichas, base))

    h.append('<h2>Fuentes</h2><ul class="fuentes">')
    for f in ficha['fuentes']:
        trozos = [f.get('obra', ''), f.get('edicion', ''), f.get('paginas', ''), f.get('doi', '')]
        # Se escapa cada trozo y luego se unen: al reves, el separador se escaparia a si mismo.
        h.append('<li>%s</li>'
                 % ' &middot; '.join([_esc(t) for t in trozos if t and t not in ('-', '—')]))
    h.append('</ul></article>')
    return ''.join(h)


AVISO = ('<div class="aviso-entrada" id="aviso-entrada"><div>'
         '<strong>Los modelos son formas aproximadas por ahora.</strong> '
         'Sirven para situar y reconocer cada estructura; el modelado definitivo está en '
         'curso. Cada ficha dice en qué estado está su modelo.'
         '</div><button type="button">Entendido</button></div>')


def _visor_html(base):
    svg = _plantilla('visor.svg').replace('{{BASE}}', base)
    barra = ('<div class="visor-barra">'
             '<span class="etiqueta-provisional">Forma aproximada</span>'
             '<span>Toca una parte para abrir su ficha</span>'
             '</div>')
    return '<section class="visor" aria-label="Visor del cerebelo">%s%s</section>' % (svg, barra)


def escribir(fichas):
    if os.path.isdir(SALIDA):
        shutil.rmtree(SALIDA)
    os.makedirs(SALIDA)
    open(os.path.join(SALIDA, '.nojekyll'), 'w').close()

    for carpeta in ('estilos', 'js'):
        shutil.copytree(os.path.join(FUENTE, carpeta), os.path.join(SALIDA, carpeta))

    plantilla = _plantilla('pagina.html')
    padres = _padres(fichas)
    paginas = 0

    for idf, ficha in sorted(fichas.items()):
        destino = os.path.join(SALIDA, 'estructura', idf)
        os.makedirs(destino)
        base = '../../'
        descripcion = ficha.get('definicion') or _parrafos(ficha, 'anatomia')[0]
        html = (plantilla
                .replace('{{ATRIBUTO_TEMA}}', '')
                .replace('{{TITULO}}', _esc('%s — Neuroteca' % ficha['nombre']))
                .replace('{{DESCRIPCION}}', _esc(RE_ENLACE.sub(r'\1', descripcion)[:160]))
                .replace('{{BASE}}', base)
                .replace('{{AVISO}}', AVISO)
                .replace('{{VISOR}}', _visor_html(base) if ficha['tipo'] == 'estructura' else '')
                .replace('{{NAVEGACION}}', _navegacion(ficha, fichas, padres, base))
                .replace('{{FICHA}}', _ficha_html(ficha, fichas, base))
                .replace('{{GUION_VISOR}}', ''))
        with io.open(os.path.join(destino, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        paginas += 1

    raiz = sorted([i for i in fichas if i not in padres and fichas[i]['tipo'] == 'estructura'])
    entrada = raiz[0] if raiz else sorted(fichas)[0]
    with io.open(os.path.join(SALIDA, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
                '<title>Neuroteca</title>'
                '<meta http-equiv="refresh" content="0; url=estructura/%s/">'
                '<link rel="canonical" href="estructura/%s/"></head>'
                '<body><p><a href="estructura/%s/">Entrar en Neuroteca</a></p></body></html>'
                % (entrada, entrada, entrada))

    with io.open(os.path.join(SALIDA, '404.html'), 'w', encoding='utf-8') as f:
        f.write(plantilla
                .replace('{{ATRIBUTO_TEMA}}', '')
                .replace('{{TITULO}}', 'Esa página no existe &mdash; Neuroteca')
                .replace('{{DESCRIPCION}}', 'Página no encontrada')
                .replace('{{BASE}}', '/')
                .replace('{{AVISO}}', '')
                .replace('{{VISOR}}', '')
                .replace('{{NAVEGACION}}', '')
                .replace('{{FICHA}}', '<article class="ficha"><h1>Esa página no existe</h1>'
                                      '<p>Puede que la estructura se llame de otra forma o que '
                                      'todavía no esté publicada.</p>'
                                      '<p><a href="/">Volver al principio</a></p></article>')
                .replace('{{GUION_VISOR}}', ''))
    return paginas


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

    paginas = escribir(fichas)
    print('%d páginas escritas en docs/' % paginas)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
