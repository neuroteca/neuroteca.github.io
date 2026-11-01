#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Neuroteca.

Lee el contenido de `contenido/`, lo valida contra el esquema y escribe el sitio
estático en `docs/`, que es lo que publica GitHub Pages.

Solo biblioteca estándar: este script debe seguir funcionando dentro de diez años sin
instalar nada.

Uso:
    python3 herramientas/construir.py            construye
    python3 herramientas/construir.py --validar  solo valida, no escribe

Convenciones que este archivo hace cumplir (ver GUIA.md):

- Una ficha por archivo JSON; el `id` coincide con el nombre del archivo y es la URL.
- `contenido/<carpeta>/<id>.<idioma>.json` es una superposición: traduce los campos
  que quiera de la ficha `<id>`. Lo que falte se muestra en español y la página lo dice.
- Los textos de la interfaz viven en `src/idiomas/<idioma>.json`. El español es el
  idioma base y vive en la raíz del sitio; los demás, bajo `/<idioma>/`.
- Cada activo visual declara en `contenido/activos/<id>.json` su modelo, su esquema de
  respaldo, sus colores por estructura y su eje principal. El generador no sabe nada del
  cerebelo.
"""

import hashlib
import io
import json
import os
import re
import textwrap
import unicodedata
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENIDO = os.path.join(RAIZ, 'contenido')
FUENTE = os.path.join(RAIZ, 'src')
SALIDA = os.path.join(RAIZ, 'docs')

IDIOMA_BASE = 'es'

NIVELES = ('N1', 'N2', 'N3', 'N4', 'N5')
TIPOS = ('estructura', 'fundacional', 'sistema')
ESTADOS = ('borrador', 'revisado')
ESTADOS_ACTIVO = ('provisional', 'definitivo')
ORIGENES_ACTIVO = ('propio', 'derivado', 'terceros')

# Campos obligatorios, según el tipo de ficha.
COMUNES = ('id', 'tipo', 'nombre', 'nivel_detalle', 'fuentes', 'autoria', 'estado')
PROPIOS = {
    'estructura': ('anatomia', 'fisiologia'),
    'fundacional': ('definicion', 'explicacion'),
    'sistema': ('funcion', 'circuito', 'estructuras', 'esquema'),
}
# Campos de prosa donde se buscan enlaces de glosario, por tipo.
PROSA = {'estructura': PROPIOS['estructura'], 'fundacional': PROPIOS['fundacional'],
         'sistema': ('funcion', 'circuito')}
# Campos que una superposición de idioma puede traducir.
TRADUCIBLES = ('nombre', 'sinonimos', 'anatomia', 'fisiologia', 'definicion', 'explicacion',
               'funcion', 'circuito', 'nodos', 'vistazo')
# «De un vistazo»: frases cortas, opcionales, cada una con su referencia. Solo estas claves.
VISTAZO = ('que_hace', 'si_falla', 'conexiones', 'neurotransmisores')
# Campos obligatorios de un activo visual.
ACTIVO = ('id', 'nivel_detalle', 'origen', 'licencia', 'estado', 'peso_bytes',
          'equivalente_textual', 'modelo', 'esquema', 'colores')


class ErrorDeContenido(Exception):
    """Un fallo del contenido, no del generador. La construcción se detiene."""


# ---------------------------------------------------------------- carga


def _clave(nombre):
    """Clave de ordenación alfabética que ignora tildes y mayúsculas (Área junto a Aferente)."""
    return ''.join(c for c in unicodedata.normalize('NFD', nombre.lower()) if not unicodedata.combining(c))

def _leer_json(ruta):
    with open(ruta, encoding='utf-8') as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise ErrorDeContenido('%s no es JSON válido: %s' % (_rel(ruta), e))


def _rel(ruta):
    return os.path.relpath(ruta, RAIZ).replace('\\', '/')


def cargar_idiomas():
    """{codigo: textos}. El español va primero; los demás, en orden alfabético."""
    carpeta = os.path.join(FUENTE, 'idiomas')
    idiomas = {}
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith('.json'):
            codigo = nombre[:-5]
            idiomas[codigo] = _leer_json(os.path.join(carpeta, nombre))
    if IDIOMA_BASE not in idiomas:
        raise ErrorDeContenido('falta src/idiomas/%s.json' % IDIOMA_BASE)
    return idiomas


def orden_idiomas(idiomas):
    return [IDIOMA_BASE] + sorted(c for c in idiomas if c != IDIOMA_BASE)


def cargar_fichas(idiomas):
    """Devuelve {id: ficha}. Cada ficha lleva `_trad` = {idioma: superposición}."""
    fichas = {}
    superposiciones = []
    for sub in ('estructuras', 'glosario', 'sistemas'):
        carpeta = os.path.join(CONTENIDO, sub)
        if not os.path.isdir(carpeta):
            continue
        for nombre in sorted(os.listdir(carpeta)):
            if not nombre.endswith('.json'):
                continue
            ruta = os.path.join(carpeta, nombre)
            partes = nombre[:-5].split('.')
            if len(partes) == 2:
                superposiciones.append((partes[0], partes[1], ruta))
                continue
            ficha = _leer_json(ruta)
            ficha['_ruta'] = _rel(ruta)
            ficha['_trad'] = {}
            idf = ficha.get('id')
            if not idf:
                raise ErrorDeContenido('%s no declara `id`' % ficha['_ruta'])
            if idf in fichas:
                raise ErrorDeContenido(
                    'id repetido «%s»: %s y %s' % (idf, fichas[idf]['_ruta'], ficha['_ruta']))
            if idf != partes[0]:
                raise ErrorDeContenido(
                    '%s: el `id` («%s») debe coincidir con el nombre del archivo'
                    % (ficha['_ruta'], idf))
            fichas[idf] = ficha

    for idf, idioma, ruta in superposiciones:
        donde = _rel(ruta)
        if idf not in fichas:
            raise ErrorDeContenido('%s traduce la ficha «%s», que no existe' % (donde, idf))
        if idioma not in idiomas or idioma == IDIOMA_BASE:
            raise ErrorDeContenido(
                '%s: «%s» no es un idioma declarado en src/idiomas/' % (donde, idioma))
        trad = _leer_json(ruta)
        if trad.get('id') != idf:
            raise ErrorDeContenido('%s: el `id` debe ser «%s»' % (donde, idf))
        for campo in trad:
            if campo not in TRADUCIBLES + ('id', 'idioma', 'ejes'):
                raise ErrorDeContenido(
                    '%s: una superposición no puede traducir `%s`' % (donde, campo))
        trad['_ruta'] = donde
        fichas[idf]['_trad'][idioma] = trad
    return fichas


def cargar_activos():
    """{id: activo}, leídos de contenido/activos/*.json."""
    carpeta = os.path.join(CONTENIDO, 'activos')
    activos = {}
    if not os.path.isdir(carpeta):
        return activos
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith('.json'):
            activo = _leer_json(os.path.join(carpeta, nombre))
            activo['_ruta'] = _rel(os.path.join(carpeta, nombre))
            if activo.get('id') != nombre[:-5]:
                raise ErrorDeContenido(
                    '%s: el `id` debe coincidir con el nombre del archivo' % activo['_ruta'])
            activos[activo['id']] = activo
    return activos


def cargar_paginas():
    """Páginas sueltas (acerca…): contenido/paginas/<id>.json con un bloque por idioma."""
    carpeta = os.path.join(CONTENIDO, 'paginas')
    paginas = {}
    if not os.path.isdir(carpeta):
        return paginas
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith('.json'):
            pagina = _leer_json(os.path.join(carpeta, nombre))
            pagina['_ruta'] = _rel(os.path.join(carpeta, nombre))
            paginas[nombre[:-5]] = pagina
    return paginas


# ---------------------------------------------------------------- validación

RE_ENLACE = re.compile(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]')
# [^3] al final de una frase: la afirmación se apoya en la fuente número 3 de la ficha.
RE_REF = re.compile(r'\[\^(\d+)\]')


def _parrafos(ficha, campo):
    valor = ficha.get(campo)
    if isinstance(valor, str):
        return [valor]
    return list(valor or [])


def validar(fichas, activos, paginas, idiomas):
    """Comprueba el esquema y los enlaces. Lanza ErrorDeContenido con todos los fallos."""
    problemas = []

    def enlaces(ficha, donde):
        tipo = ficha.get('tipo')
        for campo in PROSA.get(tipo, ()):
            for parrafo in _parrafos(ficha, campo):
                for destino, _texto in RE_ENLACE.findall(parrafo):
                    if destino not in fichas:
                        problemas.append(
                            '%s: el enlace [[%s]] en `%s` no tiene destino' % (donde, destino, campo))
                for n in RE_REF.findall(parrafo):
                    if not 1 <= int(n) <= len(ficha.get('fuentes') or ()):
                        problemas.append(
                            '%s: la referencia [^%s] en `%s` no corresponde a ninguna fuente'
                            % (donde, n, campo))

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
        if not ficha.get('fuentes'):
            problemas.append('%s: ninguna ficha se publica sin al menos una fuente' % donde)

        enlaces(ficha, donde)
        for idioma, trad in ficha['_trad'].items():
            enlaces(dict(trad, tipo=tipo), trad['_ruta'])

        def vistazo_ok(bloque, donde_v, n_fuentes):
            if not isinstance(bloque, dict) or not bloque:
                problemas.append('%s: `vistazo` debe ser un objeto con alguna de las claves %s'
                                 % (donde_v, ', '.join(VISTAZO)))
                return
            for clave, frase in bloque.items():
                if clave not in VISTAZO:
                    problemas.append('%s: `vistazo.%s` no es una clave admitida (%s)'
                                     % (donde_v, clave, ', '.join(VISTAZO)))
                    continue
                if not isinstance(frase, str) or not RE_REF.search(frase):
                    problemas.append('%s: `vistazo.%s` necesita al menos una referencia [^n]' % (donde_v, clave))
                    continue
                for destino, _texto in RE_ENLACE.findall(frase):
                    if destino not in fichas:
                        problemas.append('%s: el enlace [[%s]] en `vistazo.%s` no tiene destino'
                                         % (donde_v, destino, clave))
                for n in RE_REF.findall(frase):
                    if not 1 <= int(n) <= n_fuentes:
                        problemas.append('%s: la referencia [^%s] en `vistazo.%s` no corresponde a ninguna fuente'
                                         % (donde_v, n, clave))
        if 'vistazo' in ficha:
            vistazo_ok(ficha['vistazo'], donde, len(ficha.get('fuentes') or ()))
        for idioma, trad in ficha['_trad'].items():
            if 'vistazo' in trad:
                vistazo_ok(trad['vistazo'], trad['_ruta'], len(ficha.get('fuentes') or ()))
                if isinstance(trad['vistazo'], dict) and set(trad['vistazo']) - set(ficha.get('vistazo') or {}):
                    problemas.append('%s: traduce claves de `vistazo` que la ficha no tiene' % trad['_ruta'])

        ejes_vistos = set()
        for division in ficha.get('divisiones', []):
            if not division.get('eje') or not division.get('nombre_visible'):
                problemas.append('%s: una división no declara `eje` o `nombre_visible`' % donde)
            ejes_vistos.add(division.get('eje'))
            for parte in division.get('partes', []):
                if parte not in fichas:
                    problemas.append(
                        '%s: la división «%s» apunta a «%s», que no existe'
                        % (donde, division.get('eje'), parte))
        for idioma, trad in ficha['_trad'].items():
            for eje in trad.get('ejes', {}):
                if eje not in ejes_vistos:
                    problemas.append(
                        '%s: traduce el eje «%s», que la ficha no tiene' % (trad['_ruta'], eje))

        for ida in ficha.get('activos', []):
            if ida not in activos:
                problemas.append('%s: el activo «%s» no existe en contenido/activos/' % (donde, ida))

        if tipo == 'sistema':
            for ide in ficha.get('estructuras', []):
                if ide not in fichas or fichas[ide]['tipo'] != 'estructura':
                    problemas.append('%s: `estructuras` nombra «%s», que no es una estructura'
                                     % (donde, ide))
            esquema = ficha.get('esquema') or {}
            nodos = {}
            for columna in esquema.get('columnas', []):
                if not columna.get('titulo'):
                    problemas.append('%s: una columna del esquema no tiene `titulo`' % donde)
                for nodo in columna.get('nodos', []):
                    if not nodo.get('id') or not nodo.get('nombre'):
                        problemas.append('%s: un nodo del esquema no tiene `id` o `nombre`' % donde)
                    elif nodo['id'] in nodos:
                        problemas.append('%s: nodo repetido «%s» en el esquema' % (donde, nodo['id']))
                    nodos[nodo.get('id')] = nodo
            for flecha in esquema.get('flechas', []):
                for extremo in ('de', 'a'):
                    if flecha.get(extremo) not in nodos:
                        problemas.append('%s: la flecha %s → %s apunta a un nodo que no existe'
                                         % (donde, flecha.get('de'), flecha.get('a')))
            for idioma, trad in ficha['_trad'].items():
                for idn in trad.get('nodos', {}):
                    if idn not in nodos:
                        problemas.append('%s: traduce el nodo «%s», que el esquema no tiene'
                                         % (trad['_ruta'], idn))

    for ida, activo in sorted(activos.items()):
        donde = activo['_ruta']
        for campo in ACTIVO:
            if campo not in activo or activo[campo] in ('', None):
                problemas.append('%s: falta el campo obligatorio `%s`' % (donde, campo))
        if activo.get('estado') not in ESTADOS_ACTIVO:
            problemas.append('%s: `estado` debe ser uno de %s' % (donde, ', '.join(ESTADOS_ACTIVO)))
        if activo.get('origen') not in ORIGENES_ACTIVO:
            problemas.append('%s: `origen` debe ser uno de %s' % (donde, ', '.join(ORIGENES_ACTIVO)))
        if activo.get('origen') in ('derivado', 'terceros') and not activo.get('atribucion'):
            problemas.append('%s: un activo derivado o de terceros necesita `atribucion`' % donde)
        for campo in ('modelo', 'esquema'):
            if activo.get(campo) and not os.path.isfile(
                    os.path.join(CONTENIDO, 'activos', activo[campo])):
                problemas.append('%s: `%s` apunta a %s, que no existe'
                                 % (donde, campo, activo[campo]))
        for parte in activo.get('colores', {}):
            if parte not in fichas:
                problemas.append('%s: `colores` nombra «%s», que no es una ficha' % (donde, parte))

    for region, lams in _laminas()[0].items():
        if region not in fichas:
            problemas.append('lámina %s: la región no es una ficha' % region)
        for lam in lams:
            for parte in list(lam['partes']) + list(lam['colores']) + list(lam['etiquetas']):
                if parte not in fichas:
                    problemas.append('lámina %s/%s: «%s» no es una ficha' % (region, lam.get('eje'), parte))

    for idp, pagina in sorted(paginas.items()):
        for idioma in idiomas:
            if idioma not in pagina:
                problemas.append('%s: falta el bloque del idioma «%s»' % (pagina['_ruta'], idioma))

    if problemas:
        raise ErrorDeContenido('\n  - '.join(['%d problema(s):' % len(problemas)] + problemas))


# ---------------------------------------------------------------- vistas por idioma

def ver(ficha, idioma):
    """La ficha tal como se muestra en un idioma, más la lista de campos sin traducir.

    En el idioma base devuelve la ficha misma. En otro idioma, superpone lo traducido;
    lo que falta se queda en español y se declara en `pendientes`, para que la página
    lo diga en vez de disimularlo.
    """
    if idioma == IDIOMA_BASE:
        return dict(ficha, _ejes={}, _nodos={}), []
    trad = ficha['_trad'].get(idioma, {})
    vista = dict(ficha)
    pendientes = []
    for campo in ('nombre',) + PROPIOS.get(ficha.get('tipo'), ()):
        if campo in trad:
            vista[campo] = trad[campo]
        else:
            pendientes.append(campo)
    if 'sinonimos' in trad:
        vista['sinonimos'] = trad['sinonimos']
    if ficha.get('vistazo'):
        if 'vistazo' in trad:
            vista['vistazo'] = trad['vistazo']
        else:
            pendientes.append('vistazo')
    vista['_ejes'] = trad.get('ejes', {})
    vista['_nodos'] = trad.get('nodos', {})
    return vista, pendientes


def nombre_eje(ficha_duena, division, idioma):
    if idioma != IDIOMA_BASE:
        traducido = ficha_duena['_trad'].get(idioma, {}).get('ejes', {}).get(division['eje'])
        if traducido:
            return traducido
    return division['nombre_visible']


def ruta_de(fichas, idf):
    """Ruta relativa de la página de una ficha. Los sistemas viven aparte de las estructuras."""
    if fichas[idf]['tipo'] == 'sistema':
        return 'sistema/%s/' % idf
    return 'estructura/%s/' % idf


def nombre_de(fichas, idf, idioma):
    return ver(fichas[idf], idioma)[0]['nombre']


# ---------------------------------------------------------------- renderizado

def piezas():
    """Manifiesto de piezas del motor. Apagar una aquí es lo que prueba el aislamiento."""
    ruta = os.path.join(FUENTE, 'piezas.json')
    if not os.path.isfile(ruta):
        return {}
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def _esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def _t(T, clave, **kw):
    texto = T[clave]
    for k, v in kw.items():
        texto = texto.replace('{%s}' % k, str(v))
    return texto


def version_de(ruta_relativa):
    """Sello corto del contenido de un archivo, para versionar su URL y vencer la caché."""
    ruta = os.path.join(FUENTE, ruta_relativa)
    if not os.path.isfile(ruta):
        return '0'
    with open(ruta, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def _plantilla(nombre):
    with open(os.path.join(FUENTE, 'plantillas', nombre), encoding='utf-8') as f:
        return f.read()


RE_EXTERNO = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')
RE_CODIGO = re.compile(r'`([^`]+)`')


RE_REFS = re.compile(r'(?:\[\^\d+\])+')


def _refs(m):
    """[^2][^4] → un solo superíndice «2, 4», cada número enlazado a su fuente."""
    numeros = RE_REF.findall(m.group(0))
    return '<sup class="ref">%s</sup>' % ', '.join(
        '<a href="#fuente-%s">%s</a>' % (n, n) for n in numeros)


def _marcado(texto, fichas, enlace, idioma):
    """Convierte el subconjunto permitido a HTML.

    [[id|texto]] enlaza al glosario; [texto](https://…) a fuera; [^n] a la fuente n de la
    ficha; **negrita**, *cursiva*, `código`. Nada más.
    """
    salida = _esc(texto)

    def glosario(m):
        destino, visible = m.group(1), m.group(2)
        nombre = nombre_de(fichas, destino, idioma)
        return ('<a class="glos" href="%s">%s</a>'
                % (enlace(ruta_de(fichas, destino)), _esc(visible or nombre.lower())))

    salida = RE_ENLACE.sub(glosario, salida)
    salida = RE_EXTERNO.sub(r'<a href="\2" rel="noopener">\1</a>', salida)
    salida = RE_REFS.sub(_refs, salida)
    salida = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', salida)
    salida = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', salida)
    salida = RE_CODIGO.sub(r'<code>\1</code>', salida)
    return salida


def _padres(fichas):
    """{id_hijo: (id_padre, division)}: de quién cuelga cada ficha y por qué eje."""
    mapa = {}
    for idf, ficha in fichas.items():
        for division in ficha.get('divisiones', []):
            for parte in division.get('partes', []):
                mapa.setdefault(parte, (idf, division))
    return mapa


def _migas_html(ficha, fichas, padres, enlace, idioma):
    """Camino desde la región hasta la ficha actual."""
    cadena, actual, guarda = [], ficha['id'], 0
    while actual in padres and guarda < 10:
        actual = padres[actual][0]
        cadena.insert(0, actual)
        guarda += 1
    if not cadena:
        return ''
    migas = ['<p class="migas-nav">']
    for idf in cadena:
        migas.append('<a href="%s">%s <span class="nv">%s</span></a>'
                     % (enlace('estructura/%s/' % idf), _esc(nombre_de(fichas, idf, idioma)),
                        fichas[idf]['nivel_detalle']))
        migas.append('<span aria-hidden="true">&rsaquo;</span>')
    migas.append('<span class="actual">%s <span class="nv">%s</span></span>'
                 % (_esc(nombre_de(fichas, ficha['id'], idioma)), ficha['nivel_detalle']))
    migas.append('</p>')
    return ''.join(migas)


def _navegacion(ficha, fichas, padres, enlace, colores, T, idioma):
    """Las divisiones de la ficha (o de su dueña) agrupadas por eje, debajo de la cabecera.

    Vive en el motor, no en la pieza visor: si viviera en el visor, apagarlo la
    borraría y el atlas quedaría sin acceso a las fichas.
    """
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
            if parte in colores:
                punto = '<span class="punto" style="background:var(--c-%s)"></span>' % parte
            botones.append(
                '<li><a href="%s"%s>%s%s <span class="nv">%s</span></a></li>'
                % (enlace('estructura/%s/' % parte), aqui, punto,
                   _esc(nombre_de(fichas, parte, idioma)), hijo['nivel_detalle']))
        ejes.append('<div class="eje"><span class="eje-nombre">%s</span><ul>%s</ul></div>'
                    % (_esc(nombre_eje(duena, division, idioma)), ''.join(botones)))

    if not ejes:
        return ''
    return ('<nav class="partes-nav" aria-label="%s"><h2>%s</h2>%s</nav>'
            % (_esc(T['nav_aria']), _esc(_t(T, 'partes_titulo', nombre=nombre_de(fichas, duena['id'], idioma))),
               ''.join(ejes)))


def _insignias(ficha, pendientes, T):
    partes = ['<span class="insignia nivel">%s %s &middot; %s</span>'
              % (_esc(T['nivel']), ficha['nivel_detalle'],
                 _esc(T['niveles'][ficha['nivel_detalle']]))]
    if ficha.get('prueba'):
        partes.append('<span class="insignia prueba">%s</span>' % _esc(T['prueba']))
    partes.append('<span class="insignia">%s</span>' % _esc(T['estados'][ficha['estado']]))
    if pendientes:
        partes.append('<span class="insignia pendiente">%s</span>' % _esc(T['sin_traducir']))
    return '<div class="insignias">%s</div>' % ''.join(partes)


def _vistazo_html(ficha, vista, pendientes, fichas, enlace, T, idioma):
    """«De un vistazo»: las frases cortas de la ficha, cada una con su referencia."""
    bloque = vista.get('vistazo') or {}
    if not bloque:
        return ''
    lang = ' lang="%s"' % IDIOMA_BASE if 'vistazo' in pendientes else ''
    h = ['<dl class="vistazo"%s>' % lang]
    for clave in VISTAZO:
        if clave in bloque:
            h.append('<div><dt>%s</dt><dd>%s</dd></div>'
                     % (_esc(T['vistazo_' + clave]), _marcado(bloque[clave], fichas, enlace, idioma)))
    h.append('</dl>')
    return ''.join(h)


def _cabecera_html(ficha, vista, pendientes, fichas, padres, mapa, enlace, T, idioma):
    """Cabecera de toda ficha: migas, localizador en el mapa, nombre, latín, insignias y
    «de un vistazo». Va antes que las partes y que el esquema: quien llega debe saber
    qué mira y dónde está antes de leer."""
    tipo = ficha['tipo']
    h = ['<header class="cabecera cabecera-%s">' % tipo]
    if tipo == 'estructura':
        h.append(_migas_html(ficha, fichas, padres, enlace, idioma))
    regiones = []
    if tipo == 'estructura':
        regiones = [_region_de(ficha['id'], padres)]
    elif tipo == 'sistema':
        regiones = sorted(set(_region_de(e, padres) for e in ficha.get('estructuras', [])))
    regiones = [r for r in regiones if r in mapa['regiones']]
    localizador = ''
    if regiones:
        etiqueta = _t(T, 'mapa_localizador', nombre=', '.join(nombre_de(fichas, r, idioma) for r in regiones))
        localizador = ('<div class="localizador-caja" style="--rc: var(--region-%s)">%s%s<small>%s</small></div>'
                       % (regiones[0], _mapa_simbolo(mapa), _mapa_localizador(mapa, regiones, etiqueta),
                          _esc(T['mapa_localizador_pie'])))
    h.append('<div class="cabecera-grid%s">%s<div class="cabecera-texto">' % (' con-mapa' if localizador else '', localizador))
    h.append('<h1>%s</h1>' % _esc(vista['nombre']))
    if ficha.get('termino_latin'):
        h.append('<p class="latin" lang="la">%s</p>' % _esc(ficha['termino_latin']))
    h.append(_insignias(ficha, pendientes, T))
    if tipo == 'fundacional':
        lang = ' lang="%s"' % IDIOMA_BASE if 'definicion' in pendientes else ''
        h.append('<p class="entradilla definicion"%s>%s</p>'
                 % (lang, _marcado(vista['definicion'], fichas, enlace, idioma)))
    h.append(_vistazo_html(ficha, vista, pendientes, fichas, enlace, T, idioma))
    h.append('</div></div></header>')
    return ''.join(h)


def _ficha_html(ficha, vista, pendientes, fichas, activo, enlace, T, idioma):
    """Cuerpo de la ficha: la prosa por secciones, los sistemas, las fuentes y el modelo.
    La cabecera (nombre, localizador, vistazo) la pone _cabecera_html."""
    h = ['<article class="ficha">']

    def lang(campo):
        # Un campo sin traducir se marca con el idioma real del texto, por honestidad y
        # para que los lectores de pantalla lo pronuncien bien.
        return ' lang="%s"' % IDIOMA_BASE if campo in pendientes else ''

    if ficha['tipo'] == 'estructura':
        secciones = [('anatomia', 'anatomia'), ('fisiologia', 'fisiologia')]
    elif ficha['tipo'] == 'sistema':
        secciones = [('funcion', 'funcion'), ('circuito', 'circuito')]
    else:
        # La definición va en la cabecera, como entradilla.
        secciones = [('explicacion', 'explicacion')]

    primero = ficha['tipo'] != 'fundacional'
    for clave, campo in secciones:
        h.append('<h2>%s</h2>' % _esc(T[clave]))
        for parrafo in _parrafos(vista, campo):
            clase = ' class="entradilla"' if primero else ''
            primero = False
            h.append('<p%s%s>%s</p>' % (clase, lang(campo), _marcado(parrafo, fichas, enlace, idioma)))

    if ficha['tipo'] == 'estructura':
        sistemas = sorted(i for i, f in fichas.items()
                          if f['tipo'] == 'sistema' and ficha['id'] in f.get('estructuras', []))
        if sistemas:
            h.append('<h2>%s</h2><ul class="sistemas-de">' % _esc(T['sistemas_de']))
            for ids in sistemas:
                h.append('<li><a href="%s">%s <span class="nv">%s</span></a></li>'
                         % (enlace(ruta_de(fichas, ids)), _esc(nombre_de(fichas, ids, idioma)),
                            fichas[ids]['nivel_detalle']))
            h.append('</ul>')

    # Plegadas: son la credencial de la ficha, no su lectura. Una nota [^n] las abre.
    h.append('<details class="fuentes-caja" id="fuentes"><summary><h2>%s</h2></summary><ol class="fuentes">'
             % _esc(_t(T, 'fuentes_n', n=len(ficha['fuentes']))))
    for n, f in enumerate(ficha['fuentes'], 1):
        trozos = [_esc(t) for t in (f.get('obra', ''), f.get('edicion', ''), f.get('paginas', ''))
                  if t and t not in ('-', '—')]
        # Se escapa cada trozo y luego se unen: al revés, el separador se escaparía a sí mismo.
        if f.get('doi'):
            trozos.append('<a href="https://doi.org/%s" rel="noopener">doi:%s</a>'
                          % (_esc(f['doi']), _esc(f['doi'])))
        if f.get('url'):
            trozos.append('<a href="%s" rel="noopener">%s</a>' % (_esc(f['url']), _esc(f['url'])))
        h.append('<li id="fuente-%d">%s</li>' % (n, ' &middot; '.join(trozos)))
    h.append('</ol></details>')

    if activo:
        h.append('<h2>%s</h2><p class="modelo-info">%s' % (
            _esc(T['modelo']),
            _esc(_t(T, 'modelo_linea',
                    estado=T['modelo_estados'][activo['estado']],
                    origen=T['modelo_origenes'][activo['origen']],
                    licencia=activo['licencia']))))
        if activo.get('atribucion'):
            h.append(' %s %s' % (_esc(T['modelo_atribucion']), _esc(activo['atribucion'])))
        h.append('</p><p class="modelo-info" lang="%s">%s %s</p>'
                 % (IDIOMA_BASE, _esc(T['modelo_descripcion']), _esc(activo['equivalente_textual'])))
    h.append('</article>')
    return ''.join(h)


def _aviso(T):
    return ('<div class="aviso-entrada" id="aviso-entrada"><div><strong>%s</strong> %s</div>'
            '<button type="button">%s</button></div>'
            % (_esc(T['aviso_titulo']), _esc(T['aviso_texto']), _esc(T['entendido'])))


def _colores_css(colores):
    """Un color por parte (`--c-<id>`): los del activo y los de la lámina de la región."""
    if not colores:
        return ''
    reglas = ''.join('--c-%s:%s;' % (k, v) for k, v in sorted(colores.items()))
    return '<style>:root{%s}</style>' % reglas


def _visor_html(ficha, vista, activo, base, enlace, con_pieza, T):
    """El SVG lo dibuja siempre el motor. La pieza `visor` lo sustituye por 3D si puede.

    Si la pieza está apagada o falla, el SVG se queda: el aislamiento se resuelve por
    diseño, no con código defensivo.
    """
    with open(os.path.join(CONTENIDO, 'activos', activo['esquema']), encoding='utf-8') as f:
        svg = f.read().replace('{{BASE}}', enlace(''))
    if con_pieza:
        # Con la pieza activa el esquema nace oculto: si nace visible, se ve un destello
        # del SVG antes de que cargue el modelo. `degradar()` lo devuelve si algo falla,
        # y el <noscript> lo devuelve si no hay JavaScript.
        svg = svg.replace('<svg ', '<svg hidden ', 1)
        svg = ('<noscript><style>#visor svg[hidden]{display:block !important}</style>'
               '</noscript>' + svg)
    etiqueta = T['forma_aproximada'] if activo['estado'] == 'provisional' else T['modelo_definitivo']
    barra = ('<div class="visor-barra">'
             '<span class="etiqueta-provisional">%s</span>'
             '<span class="estado">%s</span>'
             '<span class="controles">'
             '<button type="button" id="visor-inicio" hidden>%s</button>'
             '</span></div>'
             % (_esc(etiqueta),
                _esc(T['visor_instrucciones'] if con_pieza else T['visor_apagado']),
                _esc(T['vista_inicial'])))

    datos = ''
    if con_pieza:
        cfg = {
            'modelo': base + 'activos/' + activo['modelo'],
            'base': enlace(''),
            'eje': activo.get('eje_visor') or _eje_principal(ficha),
            'actual': ficha['id'],
            'colores': dict((k, '--c-%s' % k) for k in activo['colores']),
            'textos': {
                'sin3d': T['visor_sin_3d'],
                'falloInicio': T['visor_fallo_inicio'],
                'falloModelo': T['visor_fallo_modelo'],
                'sinPartes': T['visor_sin_partes'],
                'esquema': T['visor_se_muestra_esquema'],
            },
        }
        datos = " data-visor='%s'" % json.dumps(cfg, ensure_ascii=True).replace("'", '&#39;')

    return ('<section class="visor" id="visor" aria-label="%s"%s>%s%s</section>'
            % (_esc(_t(T, 'visor_aria', nombre=vista['nombre'])), datos, svg, barra))


def _sistema_nav(ficha, fichas, padres, mapa, enlace, T, idioma):
    """Estructuras implicadas en un sistema, agrupadas por región y plegadas: el esquema ya
    las muestra; la lista es el acceso alternativo. Vive en el motor, no en la pieza."""
    grupos = {}
    for ide in ficha.get('estructuras', []):
        grupos.setdefault(_region_de(ide, padres), []).append(ide)
    orden = sorted(grupos, key=lambda r: mapa['orden'].index(r) if r in mapa['orden'] else 99)
    ejes = []
    for region in orden:
        botones = []
        for ide in grupos[region]:
            punto = ('<span class="punto" style="background:var(--region-%s)"></span>' % region
                     if region in mapa['regiones'] else '')
            botones.append('<li><a href="%s" data-nodo="%s">%s%s <span class="nv">%s</span></a></li>'
                           % (enlace(ruta_de(fichas, ide)), _esc(ide), punto,
                              _esc(nombre_de(fichas, ide, idioma)), fichas[ide]['nivel_detalle']))
        ejes.append('<div class="eje"><span class="eje-nombre">%s</span><ul>%s</ul></div>'
                    % (_esc(nombre_de(fichas, region, idioma)), ''.join(botones)))
    n = len(ficha.get('estructuras', []))
    return ('<details class="partes-nav sistema-nav" id="estructuras"><summary><h2>%s</h2></summary>'
            '<nav aria-label="%s">%s</nav></details>'
            % (_esc(_t(T, 'estructuras_implicadas_n', n=n)), _esc(T['nav_aria']), ''.join(ejes)))


def _esquema_svg(ficha, vista, fichas, padres, mapa, enlace, T, idioma):
    """Diagrama del circuito, generado desde `esquema`. Un nodo con ficha es un enlace,
    coloreado con la región a la que pertenece, para que el recorrido se lea sin texto."""
    esq = ficha['esquema']
    regiones_vistas = []
    nombres = vista.get('_nodos', {})
    ANCHO, LINEA, RELLENO, SEP_Y, SEP_X, MARGEN = 160, 15, 11, 18, 132, 16
    columnas = esq.get('columnas', [])
    flechas = esq.get('flechas', [])
    columna_de = {}
    for ci, col in enumerate(columnas):
        for nodo in col.get('nodos', []):
            columna_de[nodo['id']] = ci
    hay_vuelta = any(columna_de[f['a']] <= columna_de[f['de']] for f in flechas)
    arriba = 92 if hay_vuelta else 40

    pos = {}
    alto = 0
    for ci, col in enumerate(columnas):
        x = MARGEN + ci * (ANCHO + SEP_X)
        y = arriba
        for nodo in col.get('nodos', []):
            lineas = textwrap.wrap(nombres.get(nodo['id'], nodo['nombre']), 23)[:3]
            h = RELLENO * 2 + LINEA * len(lineas)
            pos[nodo['id']] = (x, y, h, lineas, nodo)
            y += h + SEP_Y
        alto = max(alto, y)
    ancho_total = MARGEN * 2 + len(columnas) * ANCHO + (len(columnas) - 1) * SEP_X
    alto_total = alto + 8

    out = ['<svg class="circuito" viewBox="0 0 %d %d" role="img" aria-label="%s" '
           'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
           % (ancho_total, alto_total, _esc(_t(T, 'esquema_alt', nombre=vista['nombre'])))]
    out.append('<title>%s</title>' % _esc(_t(T, 'esquema_alt', nombre=vista['nombre'])))
    out.append('<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" '
               'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
               '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>')
    for ci, col in enumerate(columnas):
        x = MARGEN + ci * (ANCHO + SEP_X)
        out.append('<text class="columna" x="%d" y="%d">%s</text>'
                   % (x, arriba - 12, _esc(col['titulo'])))

    def centro(idn):
        x, y, h, _l, _n = pos[idn]
        return x, y, h

    for f in flechas:
        sx, sy, sh = centro(f['de'])
        tx, ty, th = centro(f['a'])
        atras = columna_de[f['a']] <= columna_de[f['de']]
        if not atras:
            x1, y1 = sx + ANCHO, sy + sh / 2
            x2, y2 = tx, ty + th / 2
            cx = (x1 + x2) / 2
            d = 'M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (x1, y1, cx, y1, cx, y2, x2, y2)
            lx, ly = cx, (y1 + y2) / 2 - 5
        else:
            x1, y1 = sx + ANCHO / 2, sy
            x2, y2 = tx + ANCHO / 2, ty
            techo = 22
            d = 'M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (x1, y1, x1, techo, x2, techo, x2, y2)
            lx, ly = (x1 + x2) / 2, techo + 6
        out.append('<g class="flecha" data-de="%s" data-a="%s"><path d="%s" marker-end="url(#punta)"/>'
                   % (_esc(f['de']), _esc(f['a']), d))
        if f.get('texto'):
            out.append('<text x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (lx, ly, _esc(f['texto'])))
        out.append('</g>')

    for idn, (x, y, h, lineas, nodo) in pos.items():
        con_ficha = idn in fichas
        clase = 'nodo con-ficha' if con_ficha else 'nodo sin-ficha'
        texto = ''.join('<tspan x="%d" dy="%s">%s</tspan>'
                        % (x + ANCHO / 2, '0' if i == 0 else LINEA, _esc(l)) for i, l in enumerate(lineas))
        caja = ('<rect x="%d" y="%d" width="%d" height="%d" rx="7"/>'
                '<text x="%d" y="%.1f" text-anchor="middle">%s</text>'
                % (x, y, ANCHO, h, x + ANCHO / 2, y + RELLENO + LINEA - 4, texto))
        if con_ficha:
            region = _region_de(idn, padres) if fichas[idn]['tipo'] == 'estructura' else None
            estilo = ''
            if region in mapa['regiones']:
                estilo = ' style="--rc: var(--region-%s); --rs: var(--region-%s-suave)"' % (region, region)
                if region not in regiones_vistas:
                    regiones_vistas.append(region)
            out.append('<g class="%s" data-nodo="%s"%s><a href="%s"><title>%s</title>%s</a></g>'
                       % (clase, _esc(idn), estilo, enlace(ruta_de(fichas, idn)),
                          _esc(_t(T, 'esquema_abrir', nombre=nombre_de(fichas, idn, idioma))), caja))
        else:
            out.append('<g class="%s" data-nodo="%s"><title>%s</title>%s</g>'
                       % (clase, _esc(idn), _esc(T['esquema_sin_ficha']), caja))
    out.append('</svg>')
    items = ['<span class="item"><span class="muestra region" style="--rc: var(--region-%s); --rs: var(--region-%s-suave)"></span>%s</span>'
             % (r, r, _esc(nombre_de(fichas, r, idioma))) for r in sorted(regiones_vistas, key=mapa['orden'].index)]
    items.append('<span class="item"><span class="muestra con-ficha"></span>%s</span>' % _esc(T['esquema_leyenda_con']))
    items.append('<span class="item"><span class="muestra sin-ficha"></span>%s</span>' % _esc(T['esquema_leyenda_sin']))
    leyenda = '<p class="esquema-leyenda">%s</p>' % ''.join(items)
    return '<div class="esquema" id="esquema">%s%s</div>' % (''.join(out), leyenda)


def _eje_principal(ficha):
    for division in ficha.get('divisiones', []):
        if division.get('principal'):
            return division['eje']
    divisiones = ficha.get('divisiones', [])
    return divisiones[0]['eje'] if divisiones else ''


def _mapa():
    """Mapa de orientación (src/piezas/mapa-sagital.json): regiones N1 como trazados SVG."""
    with open(os.path.join(FUENTE, 'piezas', 'mapa-sagital.json'), encoding='utf-8') as f:
        return json.load(f)


def _laminas():
    """Láminas por región (src/piezas/laminas/<region>.json): las partes con ficha de una región,
    proyectadas desde las mallas. Devuelve (por región, por parte)."""
    carpeta = os.path.join(FUENTE, 'piezas', 'laminas')
    por_region, por_parte = {}, {}
    if not os.path.isdir(carpeta):
        return por_region, por_parte
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.endswith('.json'):
            continue
        with open(os.path.join(carpeta, nombre), encoding='utf-8') as f:
            lam = json.load(f)
        por_region.setdefault(lam['region'], []).append(lam)
        for parte in lam['partes']:
            por_parte.setdefault(parte, []).append(lam)
    return por_region, por_parte


def _laminas_html(lams, actual, fichas, enlace, T, idioma):
    if not lams:
        return ''
    return '<div class="laminas">%s</div>' % ''.join(_lamina_html(l, actual, fichas, enlace, T, idioma) for l in lams)


def _lamina_html(lam, actual, fichas, enlace, T, idioma):
    """Figura con la lámina de una región: cada parte es un enlace a su ficha; la ficha actual,
    si es una parte, queda resaltada y las demás atenuadas."""
    region = lam['region']
    vista = _esc(T.get('vista_' + lam['vista'], lam['vista']))
    titulo = _esc(_t(T, 'lamina_titulo', nombre=nombre_de(fichas, region, idioma), vista=vista))
    con_actual = actual in lam['partes']
    idl = 'lamina-%s-%s' % (region, lam.get('eje', 'partes'))
    h = ['<figure class="lamina%s" style="max-width:min(100%%, %dpx)">'
         % (' con-actual' if con_actual else '', int(float(lam['viewBox'].split()[2])) + 24),
         '<div class="lamina-caja"><svg viewBox="%s" role="img" aria-labelledby="%s">'
         '<title id="%s">%s</title>' % (lam['viewBox'], idl, idl, titulo)]
    for d in lam.get('sin_ficha', []):
        h.append('<path class="apagado" d="%s"><title>%s</title></path>' % (d, _esc(T['lamina_sin_ficha'])))
    for parte in lam['orden']:
        if parte not in fichas:
            continue
        aqui = ' aria-current="page"' if parte == actual else ''
        h.append('<a href="%s" class="parte"%s style="--f: var(--c-%s)"><title>%s</title>'
                 % (enlace('estructura/%s/' % parte), aqui, parte, _esc(nombre_de(fichas, parte, idioma))))
        for d in lam['partes'][parte]:
            h.append('<path d="%s"/>' % d)
        h.append('</a>')
    for parte, et in lam['etiquetas'].items():
        if parte not in fichas:
            continue
        nombre = _esc(nombre_de(fichas, parte, idioma))
        if et['modo'] == 'dentro':
            h.append('<text class="dentro" text-anchor="middle" x="%s" y="%s">%s</text>' % (et['x'], et['y'], nombre))
        else:
            h.append('<path class="guia" d="%s"/><text text-anchor="%s" x="%s" y="%s">%s</text>'
                     % (et['guia'], et.get('ancla', 'start'), et['x'], et['y'], nombre))
    h.append('</svg></div>')
    fuente = lam.get('fuente')
    credito = ''
    if fuente:
        credito = ' · <a href="%s" rel="license">%s</a>' % (_esc(fuente['url']), _esc(fuente['nombre']))
    h.append('<figcaption>%s%s</figcaption></figure>' % (_esc(_t(T, 'lamina_pie', vista=vista)), credito))
    return ''.join(h)


def _region_de(idf, padres):
    """Id de la ficha raíz (región N1) de la que cuelga `idf`; la propia si no cuelga de nadie."""
    actual, guarda = idf, 0
    while actual in padres and guarda < 10:
        actual = padres[actual][0]
        guarda += 1
    return actual


def _mapa_simbolo(mapa):
    """Definición única del mapa para los localizadores (<use>). El color de cada región
    entra por la variable --f-<id>: los selectores no atraviesan un <use>, las variables sí."""
    h = ['<svg class="mapa-def" width="0" height="0" aria-hidden="true" focusable="false">'
         '<symbol id="mapa-sagital" viewBox="%s">' % mapa['viewBox']]
    for idr in mapa['orden']:
        raya = ' stroke-dasharray="5 4"' if idr in mapa.get('esquematicos', []) else ''
        for d in mapa['regiones'][idr]:
            h.append('<path d="%s" fill="var(--f-%s, var(--mapa-apagado))" stroke="var(--papel)" '
                     'stroke-width="2" stroke-linejoin="round"%s/>' % (d, idr, raya))
        for d in mapa.get('detalles', {}).get(idr, []):
            h.append('<path d="%s" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="1.4" '
                     'stroke-linecap="round"/>' % d)
    h.append('</symbol></svg>')
    return ''.join(h)


def _mapa_localizador(mapa, ids, etiqueta):
    """Mapa apagado salvo las regiones `ids` (un id o una lista), para tarjetas y cabeceras."""
    if isinstance(ids, str):
        ids = [ids]
    ids = [i for i in ids if i in mapa['regiones']]
    if not ids:
        return ''
    estilo = ' '.join('--f-%s: var(--region-%s);' % (i, i) for i in ids)
    return ('<svg class="mapa localizador" viewBox="%s" role="img" aria-label="%s" '
            'style="%s"><use href="#mapa-sagital"/></svg>'
            % (mapa['viewBox'], _esc(etiqueta), estilo))


def _mapa_credito(mapa, T):
    """Atribución de las mallas de las que se proyecta el mapa (su licencia la exige)."""
    fuente = mapa.get('fuente')
    if not fuente:
        return ''
    enlace_fuente = '<a href="%s" rel="license">%s</a> (© %s, %s)' % (
        _esc(fuente['url']), _esc(fuente['nombre']), _esc(fuente['titular']), _esc(fuente['licencia']))
    return '<p class="mapa-credito">%s</p>' % _esc(T['mapa_credito']).replace('{fuente}', enlace_fuente)


def _mapa_interactivo(mapa, fichas, enlace, T, idioma):
    """Mapa de la portada: cada región es un enlace a su ficha y lleva su nombre."""
    h = ['<svg class="mapa interactivo" viewBox="%s" role="img" aria-labelledby="mapa-titulo">'
         '<title id="mapa-titulo">%s</title>' % (mapa['viewBox'], _esc(T['mapa_titulo']))]
    for idr in mapa['orden']:
        if idr not in fichas:
            continue
        h.append('<a href="%s" class="region%s" style="--f: var(--region-%s)"><title>%s</title>'
                 % (enlace('estructura/%s/' % idr), ' esquematico' if idr in mapa.get('esquematicos', []) else '',
                    idr, _esc(nombre_de(fichas, idr, idioma))))
        for d in mapa['regiones'][idr]:
            h.append('<path d="%s"/>' % d)
        for d in mapa.get('detalles', {}).get(idr, []):
            h.append('<path class="detalle" d="%s"/>' % d)
        h.append('</a>')
    for idr, et in mapa['etiquetas'].items():
        if idr not in fichas:
            continue
        nombre = _esc(nombre_de(fichas, idr, idioma))
        if et['modo'] == 'dentro':
            h.append('<text class="dentro" text-anchor="middle" x="%s" y="%s">%s</text>'
                     % (et['x'], et['y'], nombre))
        else:
            h.append('<path class="guia" d="%s"/><text text-anchor="%s" x="%s" y="%s">%s</text>'
                     % (et['guia'], et.get('ancla', 'start'), et['x'], et['y'], nombre))
    h.append('</svg>')
    return ''.join(h)


def _portada_html(fichas, padres, activos, enlace, T, idioma):
    mapa = _mapa()
    h = ['<article class="portada">', _mapa_simbolo(mapa)]

    # Entrada: título, texto, recorridos y el mapa.
    h.append('<section class="entrada"><div class="entrada-texto">')
    h.append('<h1>%s</h1>' % _esc(T['portada_titulo']))
    h.append('<p class="lead">%s</p>' % _esc(T['portada_lead']))
    h.append('<p class="estado-proyecto">%s</p>' % _esc(T['portada_estado']))
    h.append('<nav class="recorridos" aria-label="%s">' % _esc(T['recorridos']))
    for i, rec in enumerate(T['portada_recorridos']):
        ruta = rec['ruta']
        href = ruta if ruta.startswith('#') else enlace(ruta)
        h.append('<a href="%s"%s>%s</a>' % (href, ' class="principal"' if i == 0 else '', _esc(rec['texto'])))
    h.append('</nav></div>')
    h.append('<div class="entrada-mapa"><div class="mapa-caja">%s</div><p class="mapa-pie">%s</p>%s</div></section>'
             % (_mapa_interactivo(mapa, fichas, enlace, T, idioma), _esc(T['mapa_pie']), _mapa_credito(mapa, T)))

    # Regiones: una tarjeta por ficha raíz, con su localizador y su color.
    raices = [i for _n, i in sorted((_clave(ver(f, idioma)[0]['nombre']), i) for i, f in fichas.items()
                                    if i not in padres and f['tipo'] == 'estructura')]
    h.append('<section class="bloque" id="regiones"><h2>%s</h2><p class="nota">%s</p><ul class="regiones">'
             % (_esc(T['regiones']), _esc(T['regiones_texto'])))
    for idf in raices:
        ficha = fichas[idf]
        vista, _p = ver(ficha, idioma)
        divisiones = ficha.get('divisiones', [])
        n = len(set(p for d in divisiones for p in d.get('partes', [])))
        ejes = ' · '.join(_esc(nombre_eje(ficha, d, idioma).lower()) for d in divisiones)
        extra = ' · <span class="prueba-txt">%s</span>' % _esc(T['prueba']) if ficha.get('prueba') else ''
        en_mapa = idf in mapa['regiones']
        color = ('--rc: var(--region-%s); --rs: var(--region-%s-suave)' % (idf, idf)) if en_mapa else ''
        h.append('<li><a class="region-tarjeta" href="%s" style="%s">'
                 '<span class="mini">%s</span>'
                 '<span class="texto"><strong>%s</strong> <span class="latin-inline" lang="la">%s</span>'
                 '<span class="meta">%s<span class="nv">%s</span> · %s%s</span></span></a></li>'
                 % (enlace('estructura/%s/' % idf), color,
                    _mapa_localizador(mapa, idf, _t(T, 'mapa_localizador', nombre=vista['nombre'])),
                    _esc(vista['nombre']), _esc(ficha.get('termino_latin', '')),
                    ('<span class="ejes">%s</span>' % ejes) if ejes else '', ficha['nivel_detalle'],
                    _esc(_t(T, 'partes', n=n)), extra))
    h.append('</ul></section>')

    # Sistemas: nombre, tamaño y el recorrido en miniatura (primer nodo de cada columna, por color de región).
    sistemas = sorted((_clave(ver(f, idioma)[0]['nombre']), i)
                      for i, f in fichas.items() if f['tipo'] == 'sistema')
    if sistemas:
        h.append('<section class="bloque" id="sistemas"><h2>%s</h2><p class="nota">%s</p><ul class="sistemas">'
                 % (_esc(T['sistemas']), _esc(T['sistemas_texto'])))
        for _n, ids in sistemas:
            ficha = fichas[ids]
            vista, _p = ver(ficha, idioma)
            nombres = vista.get('_nodos', {})
            pasos = []
            for columna in ficha.get('esquema', {}).get('columnas', [])[:7]:
                nodos = columna.get('nodos', [])
                if not nodos:
                    continue
                nodo = nodos[0]
                idn = nodo.get('id', '')
                if idn in fichas:
                    region = _region_de(idn, padres)
                    estilo = (' style="--rc: var(--region-%s); --rs: var(--region-%s-suave)"' % (region, region)
                              if region in mapa['regiones'] else '')
                    pasos.append('<li%s>%s</li>' % (estilo, _esc(nombres.get(idn, nodo['nombre']))))
                else:
                    pasos.append('<li class="sin-ficha">%s</li>' % _esc(nombres.get(idn, nodo['nombre'])))
            h.append('<li><a class="sistema-tarjeta" href="%s"><strong>%s</strong>'
                     '<ol class="recorrido-mini" aria-hidden="true">%s</ol>'
                     '<span class="meta"><span class="nv">%s</span> · %s</span></a></li>'
                     % (enlace(ruta_de(fichas, ids)), _esc(vista['nombre']), ''.join(pasos),
                        ficha['nivel_detalle'],
                        _esc(_t(T, 'estructuras_n', n=len(ficha.get('estructuras', []))))))
        h.append('</ul></section>')

    # Glosario: filtro (con JavaScript) y la lista completa (sin él).
    fundacionales = sorted((_clave(ver(f, idioma)[0]['nombre']), i)
                           for i, f in fichas.items() if f['tipo'] == 'fundacional')
    h.append('<section class="bloque" id="glosario"><h2>%s <span class="nv">%s</span></h2><p class="nota">%s</p>'
             % (_esc(T['glosario']), _esc(_t(T, 'entradas', n=len(fundacionales))), _esc(T['glosario_texto'])))
    h.append('<p class="glosario-filtro"><label class="sr" for="glosario-buscar">%s</label>'
             '<input type="search" id="glosario-buscar" placeholder="%s" autocomplete="off" hidden></p>'
             % (_esc(T['glosario_filtro_aria']), _esc(T['glosario_buscar'])))
    h.append('<ul class="indice glosario" id="glosario-lista">')
    for _n, idf in fundacionales:
        vista, _p = ver(fichas[idf], idioma)
        h.append('<li><a href="%s">%s</a> <span class="meta">%s</span></li>'
                 % (enlace('estructura/%s/' % idf), _esc(vista['nombre']),
                    _marcado(vista['definicion'], fichas, enlace, idioma)))
    h.append('</ul><p class="glosario-vacio" hidden>%s</p></section></article>' % _esc(T['glosario_sin_resultados']))
    return ''.join(h)


def _pagina_suelta_html(pagina, fichas, enlace, idioma):
    bloque = pagina[idioma]
    h = ['<article class="ficha texto">', '<h1>%s</h1>' % _esc(bloque['titulo'])]
    for seccion in bloque['secciones']:
        h.append('<h2>%s</h2>' % _esc(seccion['titulo']))
        for parrafo in seccion['parrafos']:
            h.append('<p>%s</p>' % _marcado(parrafo, fichas, enlace, idioma))
    h.append('</article>')
    return ''.join(h)


# ---------------------------------------------------------------- escritura

def escribir(fichas, activos, paginas, idiomas):
    if os.path.isdir(SALIDA):
        shutil.rmtree(SALIDA)
    os.makedirs(SALIDA)
    open(os.path.join(SALIDA, '.nojekyll'), 'w').close()

    for carpeta in ('estilos', 'js', 'fuentes'):
        shutil.copytree(os.path.join(FUENTE, carpeta), os.path.join(SALIDA, carpeta))

    manifiesto = piezas()
    con_visor = manifiesto.get('visor', {}).get('activa', False)
    con_esquema = manifiesto.get('esquema', {}).get('activa', False)
    if con_visor:
        shutil.copytree(os.path.join(FUENTE, 'vendor'), os.path.join(SALIDA, 'vendor'))
        destino_activos = os.path.join(SALIDA, 'activos')
        os.makedirs(destino_activos)
        for activo in activos.values():
            shutil.copy2(os.path.join(CONTENIDO, 'activos', activo['modelo']),
                         os.path.join(destino_activos, activo['modelo']))

    plantilla = _plantilla('pagina.html')
    padres = _padres(fichas)
    mapa = _mapa()
    laminas_region, laminas_parte = _laminas()
    codigos = orden_idiomas(idiomas)
    versiones = {
        'V_ESTILOS': version_de('estilos/sitio.css'),
        'V_TOKENS': version_de('estilos/tokens.css'),
        'V_FUENTES': version_de('estilos/fuentes.css'),
        'V_JS': version_de('js/sitio.js'),
        'V_VISOR': version_de('js/visor.js'),
        'V_ESQUEMA': version_de('js/esquema.js'),
    }

    def guion_visor(base):
        if not con_visor:
            return ''
        mapa = json.dumps({'imports': {
            'three': base + 'vendor/three/three.module.min.js',
            'three/addons/': base + 'vendor/three/jsm/',
        }})
        return ('<script type="importmap">%s</script>\n'
                '<script type="module" src="%sjs/visor.js?v=%s"></script>'
                % (mapa, base, versiones['V_VISOR']))

    def guion_esquema(base):
        if not con_esquema:
            return ''
        return '<script src="%sjs/esquema.js?v=%s" defer></script>' % (base, versiones['V_ESQUEMA'])

    def prefijo(idioma):
        return '' if idioma == IDIOMA_BASE else idioma + '/'

    def cabecera_idiomas(ruta, idioma, T, base):
        """Inicio y Acerca de en este idioma, más la misma página en los demás idiomas.

        Rutas relativas a la raíz del sitio, como todo lo demás: el sitio debe poder
        servirse desde cualquier carpeta.
        """
        partes = []
        for otro in codigos:
            if otro == idioma:
                continue
            partes.append('<a href="%s%s%s" lang="%s" hreflang="%s">%s</a>'
                          % (base, prefijo(otro), ruta, otro, otro, _esc(idiomas[otro]['nombre'])))
        return ('<nav class="sitio-nav" aria-label="%s"><a href="%s%s">%s</a>'
                '<a href="%s%sacerca/">%s</a>%s</nav>'
                % (_esc(T['idioma']), base, prefijo(idioma), _esc(T['inicio']),
                   base, prefijo(idioma), _esc(T['acerca']), ''.join(partes)))

    def alternas(ruta):
        etiquetas = ['<link rel="alternate" hreflang="%s" href="https://neuroteca.github.io/%s%s">'
                     % (c, prefijo(c), ruta) for c in codigos]
        etiquetas.append('<link rel="alternate" hreflang="x-default" '
                         'href="https://neuroteca.github.io/%s">' % ruta)
        return '\n'.join(etiquetas)

    def pagina(ruta, idioma, titulo, descripcion, base, cuerpo, activo=None,
               aviso=False, visor_js=False, base_enlaces=None, esquema_js=False, colores=None):
        T = idiomas[idioma]
        html = plantilla
        for k, v in versiones.items():
            html = html.replace('{{%s}}' % k, v)
        html = (html
                .replace('{{IDIOMA}}', idioma)
                .replace('{{TITULO}}', _esc(titulo))
                .replace('{{DESCRIPCION}}', _esc(descripcion[:160]))
                .replace('{{BASE}}', base)
                .replace('{{INICIO}}', base_enlaces if base_enlaces is not None else base + prefijo(idioma))
                .replace('{{ALTERNAS}}', alternas(ruta))
                .replace('{{COLORES}}', _colores_css(colores))
                .replace('{{T_SALTAR}}', _esc(T['saltar']))
                .replace('{{T_BAJADA}}', _esc(T['bajada']))
                .replace('{{T_TEMA}}', _esc(T['tema']))
                .replace('{{NAV_SITIO}}', cabecera_idiomas(ruta, idioma, T, base))
                .replace('{{AVISO}}', _aviso(T) if aviso else '')
                .replace('{{CUERPO}}', cuerpo)
                .replace('{{PIE}}', T['pie'])
                .replace('{{GUION_VISOR}}', (guion_visor(base) if visor_js else '')
                         + (guion_esquema(base) if esquema_js else '')))
        return html

    def guardar(ruta_relativa, html):
        destino = os.path.join(SALIDA, ruta_relativa)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with io.open(destino, 'w', encoding='utf-8') as f:
            f.write(html)

    paginas_escritas = 0
    for idioma in codigos:
        T = idiomas[idioma]
        pre = prefijo(idioma)
        profundidad = 1 if pre else 0

        # Fichas: /[idioma/]estructura/<id>/
        for idf, ficha in sorted(fichas.items()):
            base = '../../' + '../' * profundidad
            enlace = lambda ruta, base=base, pre=pre: base + pre + ruta
            vista, pendientes = ver(ficha, idioma)
            activo = activos.get((ficha.get('activos') or [None])[0])
            # Un modelo provisional ya no se muestra (decisión D3, 2026-10-31): el visor
            # vuelve con mallas definitivas. Sus colores sí sirven para marcar las partes.
            activo_visor = activo if activo and activo.get('estado') == 'definitivo' else None
            es_estructura = ficha['tipo'] == 'estructura'
            es_sistema = ficha['tipo'] == 'sistema'
            descripcion = (vista.get('definicion') or _parrafos(vista, 'anatomia' if es_estructura
                                                                 else 'funcion')[0])
            # Sin modelo (fundacionales, regiones aún sin activo) la ficha ocupa una sola
            # columna legible en vez de dejar vacía la zona del visor.
            clase = ' sistema' if es_sistema else ('' if activo_visor else ' sin-visor')
            cuerpo = ['<main class="atlas%s" id="contenido">' % clase]
            if es_estructura and activo_visor:
                cuerpo.append(_visor_html(ficha, vista, activo_visor, base, enlace, con_visor, T))
            cabecera = _cabecera_html(ficha, vista, pendientes, fichas, padres, mapa, enlace, T, idioma)
            if es_sistema:
                # El nombre va antes del esquema: quien llega debe saber qué circuito mira
                # antes de verlo dibujado.
                cuerpo.append('<div class="cabecera-sistema">%s</div>' % cabecera)
                cuerpo.append(_esquema_svg(ficha, vista, fichas, padres, mapa, enlace, T, idioma))
            lams = (laminas_region.get(idf) or laminas_parte.get(idf) or []) if es_estructura else []
            colores = {}
            for lam in lams:
                colores.update(lam['colores'])
            if activo:
                colores.update(activo['colores'])
            cuerpo.append('<section class="panel">')
            if es_sistema:
                cuerpo.append(_sistema_nav(ficha, fichas, padres, mapa, enlace, T, idioma))
            else:
                cuerpo.append(cabecera)
                cuerpo.append(_navegacion(ficha, fichas, padres, enlace, colores, T, idioma))
                cuerpo.append(_laminas_html(lams, idf, fichas, enlace, T, idioma))
            cuerpo.append(_ficha_html(ficha, vista, pendientes, fichas,
                                      activo_visor if es_estructura else None, enlace, T, idioma))
            cuerpo.append('</section></main>')
            ruta = ruta_de(fichas, idf)
            guardar('%s%sindex.html' % (pre, ruta),
                    pagina(ruta, idioma,
                           '%s — %s' % (vista['nombre'], T['titulo_sitio']),
                           RE_REF.sub('', RE_ENLACE.sub(lambda m: m.group(2) or m.group(1),
                                                        descripcion)),
                           base, ''.join(cuerpo), activo=activo, colores=colores,
                           aviso=bool(es_estructura and activo_visor),
                           visor_js=bool(es_estructura and activo_visor), esquema_js=es_sistema))
            paginas_escritas += 1

        # Portada: /[idioma/]
        base = '../' * profundidad if profundidad else './'
        enlace = lambda ruta, base=base, pre=pre: base + pre + ruta
        guardar('%sindex.html' % pre,
                pagina('', idioma, '%s — %s' % (T['titulo_sitio'], T['bajada']),
                       T['meta_portada'], base,
                       '<main class="lectura ancha" id="contenido">%s</main>'
                       % _portada_html(fichas, padres, activos, enlace, T, idioma)))
        paginas_escritas += 1

        # Páginas sueltas: /[idioma/]<id>/
        for idp, suelta in sorted(paginas.items()):
            base = '../' + '../' * profundidad
            enlace = lambda ruta, base=base, pre=pre: base + pre + ruta
            guardar('%s%s/index.html' % (pre, idp),
                    pagina('%s/' % idp, idioma,
                           '%s — %s' % (suelta[idioma]['titulo'], T['titulo_sitio']),
                           suelta[idioma].get('descripcion', ''), base,
                           '<main class="lectura" id="contenido">%s</main>'
                           % _pagina_suelta_html(suelta, fichas, enlace, idioma)))
            paginas_escritas += 1

    # 404 única, en la raíz (es la que sirve Pages), con todos los idiomas.
    T = idiomas[IDIOMA_BASE]
    cuerpo = ['<main class="lectura" id="contenido"><article class="ficha texto">']
    for idioma in codigos:
        Ti = idiomas[idioma]
        cuerpo.append('<section lang="%s"><h1>%s</h1><p>%s</p><p><a href="/%s">%s</a></p></section>'
                      % (idioma, _esc(Ti['no_encontrada_titulo']), _esc(Ti['no_encontrada_texto']),
                         prefijo(idioma), _esc(Ti['no_encontrada_volver'])))
    cuerpo.append('</article></main>')
    guardar('404.html', pagina('', IDIOMA_BASE, '%s — %s' % (T['no_encontrada_titulo'], T['titulo_sitio']),
                               T['no_encontrada_texto'], '/', ''.join(cuerpo), base_enlaces='/'))
    return paginas_escritas


def main(argv):
    solo_validar = '--validar' in argv
    try:
        idiomas = cargar_idiomas()
        fichas = cargar_fichas(idiomas)
        if not fichas:
            raise ErrorDeContenido('no hay ninguna ficha en contenido/')
        activos = cargar_activos()
        paginas = cargar_paginas()
        validar(fichas, activos, paginas, idiomas)
    except ErrorDeContenido as e:
        sys.stderr.write('\nLa construcción se detuvo.\n\n  %s\n\n' % e)
        return 1

    traducidas = sum(len(f['_trad']) for f in fichas.values())
    print('%d fichas válidas, %d superposiciones de idioma, %d activos, %d páginas sueltas; idiomas: %s.'
          % (len(fichas), traducidas, len(activos), len(paginas), ', '.join(orden_idiomas(idiomas))))
    if solo_validar:
        return 0

    paginas_escritas = escribir(fichas, activos, paginas, idiomas)
    print('%d páginas escritas en docs/' % paginas_escritas)
    total = sum(os.path.getsize(os.path.join(d, f))
                for d, _s, fs in os.walk(SALIDA) for f in fs)
    print('peso del sitio: %.1f KB' % (total / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
