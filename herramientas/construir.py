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
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENIDO = os.path.join(RAIZ, 'contenido')
FUENTE = os.path.join(RAIZ, 'src')
SALIDA = os.path.join(RAIZ, 'docs')

IDIOMA_BASE = 'es'

NIVELES = ('N1', 'N2', 'N3', 'N4', 'N5')
TIPOS = ('estructura', 'fundacional')
ESTADOS = ('borrador', 'revisado')
ESTADOS_ACTIVO = ('provisional', 'definitivo')
ORIGENES_ACTIVO = ('propio', 'derivado', 'terceros')

# Campos obligatorios, según el tipo de ficha.
COMUNES = ('id', 'tipo', 'nombre', 'nivel_detalle', 'fuentes', 'autoria', 'estado')
PROPIOS = {
    'estructura': ('anatomia', 'fisiologia'),
    'fundacional': ('definicion', 'explicacion'),
}
# Campos de prosa donde se buscan enlaces de glosario, por tipo.
PROSA = PROPIOS
# Campos que una superposición de idioma puede traducir.
TRADUCIBLES = ('nombre', 'sinonimos', 'anatomia', 'fisiologia', 'definicion', 'explicacion')
# Campos obligatorios de un activo visual.
ACTIVO = ('id', 'nivel_detalle', 'origen', 'licencia', 'estado', 'peso_bytes',
          'equivalente_textual', 'modelo', 'esquema', 'colores')


class ErrorDeContenido(Exception):
    """Un fallo del contenido, no del generador. La construcción se detiene."""


# ---------------------------------------------------------------- carga

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
    for sub in ('estructuras', 'glosario'):
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
        return ficha, []
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
    vista['_ejes'] = trad.get('ejes', {})
    return vista, pendientes


def nombre_eje(ficha_duena, division, idioma):
    if idioma != IDIOMA_BASE:
        traducido = ficha_duena['_trad'].get(idioma, {}).get('ejes', {}).get(division['eje'])
        if traducido:
            return traducido
    return division['nombre_visible']


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


def _marcado(texto, fichas, enlace, idioma):
    """Convierte el subconjunto permitido a HTML.

    [[id|texto]] enlaza al glosario; [texto](https://…) a fuera; **negrita**, *cursiva*,
    `código`. Nada más.
    """
    salida = _esc(texto)

    def glosario(m):
        destino, visible = m.group(1), m.group(2)
        nombre = nombre_de(fichas, destino, idioma)
        return ('<a class="glos" href="%s">%s</a>'
                % (enlace('estructura/%s/' % destino), _esc(visible or nombre.lower())))

    salida = RE_ENLACE.sub(glosario, salida)
    salida = RE_EXTERNO.sub(r'<a href="\2" rel="noopener">\1</a>', salida)
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


def _navegacion(ficha, fichas, padres, enlace, colores, T, idioma):
    """Migas hasta la ficha actual, más las divisiones del padre agrupadas por eje.

    Vive en el motor, no en la pieza visor: si viviera en el visor, apagarlo la
    borraría y el atlas quedaría sin acceso a las fichas.
    """
    cadena, actual, guarda = [], ficha['id'], 0
    while actual in padres and guarda < 10:
        actual = padres[actual][0]
        cadena.insert(0, actual)
        guarda += 1

    migas = ['<p class="migas-nav">']
    for idf in cadena:
        migas.append('<a href="%s">%s <span class="nv">%s</span></a>'
                     % (enlace('estructura/%s/' % idf), _esc(nombre_de(fichas, idf, idioma)),
                        fichas[idf]['nivel_detalle']))
        migas.append('<span aria-hidden="true">&rsaquo;</span>')
    migas.append('<span class="actual">%s <span class="nv">%s</span></span>'
                 % (_esc(nombre_de(fichas, ficha['id'], idioma)), ficha['nivel_detalle']))
    migas.append('</p>')

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
    return ('<nav class="partes-nav" aria-label="%s">%s%s</nav>'
            % (_esc(T['nav_aria']), ''.join(migas), ''.join(ejes)))


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


def _ficha_html(ficha, vista, pendientes, fichas, activo, enlace, T, idioma):
    h = ['<article class="ficha">', '<h1>%s</h1>' % _esc(vista['nombre'])]
    if ficha.get('termino_latin'):
        h.append('<p class="latin" lang="la">%s</p>' % _esc(ficha['termino_latin']))
    h.append(_insignias(ficha, pendientes, T))

    def lang(campo):
        # Un campo sin traducir se marca con el idioma real del texto, por honestidad y
        # para que los lectores de pantalla lo pronuncien bien.
        return ' lang="%s"' % IDIOMA_BASE if campo in pendientes else ''

    if ficha['tipo'] == 'estructura':
        secciones = [('anatomia', 'anatomia'), ('fisiologia', 'fisiologia')]
    else:
        h.append('<h2>%s</h2>' % _esc(T['definicion']))
        h.append('<p%s>%s</p>' % (lang('definicion'),
                                 _marcado(vista['definicion'], fichas, enlace, idioma)))
        secciones = [('explicacion', 'explicacion')]

    for clave, campo in secciones:
        h.append('<h2>%s</h2>' % _esc(T[clave]))
        for parrafo in _parrafos(vista, campo):
            h.append('<p%s>%s</p>' % (lang(campo), _marcado(parrafo, fichas, enlace, idioma)))

    h.append('<h2>%s</h2><ul class="fuentes">' % _esc(T['fuentes']))
    for f in ficha['fuentes']:
        trozos = [f.get('obra', ''), f.get('edicion', ''), f.get('paginas', ''), f.get('doi', '')]
        # Se escapa cada trozo y luego se unen: al revés, el separador se escaparía a sí mismo.
        h.append('<li>%s</li>'
                 % ' &middot; '.join([_esc(t) for t in trozos if t and t not in ('-', '—')]))
    h.append('</ul>')

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


def _colores_css(activo):
    if not activo:
        return ''
    reglas = ''.join('--c-%s:%s;' % (k, v) for k, v in sorted(activo['colores'].items()))
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


def _eje_principal(ficha):
    for division in ficha.get('divisiones', []):
        if division.get('principal'):
            return division['eje']
    divisiones = ficha.get('divisiones', [])
    return divisiones[0]['eje'] if divisiones else ''


def _portada_html(fichas, padres, activos, enlace, T, idioma):
    h = ['<article class="ficha portada">']
    h.append('<h1>%s</h1>' % _esc(T['titulo_sitio']))
    h.append('<p class="lead">%s</p>' % _esc(T['portada_lead']))
    h.append('<p class="estado-proyecto">%s</p>' % _esc(T['portada_estado']))

    raices = sorted(i for i in fichas if i not in padres and fichas[i]['tipo'] == 'estructura')
    h.append('<h2>%s</h2><p class="nota">%s</p><ul class="indice">'
             % (_esc(T['regiones']), _esc(T['regiones_texto'])))
    for idf in raices:
        ficha = fichas[idf]
        vista, _p = ver(ficha, idioma)
        n = len(set(p for d in ficha.get('divisiones', []) for p in d.get('partes', [])))
        extra = ' &middot; <span class="prueba-txt">%s</span>' % _esc(T['prueba']) if ficha.get('prueba') else ''
        h.append('<li><a href="%s"><strong>%s</strong> <span class="latin-inline" lang="la">%s</span></a>'
                 '<span class="meta"><span class="nv">%s</span> &middot; %s%s</span></li>'
                 % (enlace('estructura/%s/' % idf), _esc(vista['nombre']),
                    _esc(ficha.get('termino_latin', '')), ficha['nivel_detalle'],
                    _esc(_t(T, 'partes', n=n)), extra))
    h.append('</ul>')

    fundacionales = sorted((ver(f, idioma)[0]['nombre'].lower(), i)
                           for i, f in fichas.items() if f['tipo'] == 'fundacional')
    h.append('<h2>%s <span class="nv">%s</span></h2><p class="nota">%s</p><ul class="indice glosario">'
             % (_esc(T['glosario']), _esc(_t(T, 'entradas', n=len(fundacionales))),
                _esc(T['glosario_texto'])))
    for _n, idf in fundacionales:
        vista, _p = ver(fichas[idf], idioma)
        h.append('<li><a href="%s">%s</a> <span class="meta">%s</span></li>'
                 % (enlace('estructura/%s/' % idf), _esc(vista['nombre']),
                    _marcado(vista['definicion'], fichas, enlace, idioma)))
    h.append('</ul></article>')
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

    for carpeta in ('estilos', 'js'):
        shutil.copytree(os.path.join(FUENTE, carpeta), os.path.join(SALIDA, carpeta))

    manifiesto = piezas()
    con_visor = manifiesto.get('visor', {}).get('activa', False)
    if con_visor:
        shutil.copytree(os.path.join(FUENTE, 'vendor'), os.path.join(SALIDA, 'vendor'))
        destino_activos = os.path.join(SALIDA, 'activos')
        os.makedirs(destino_activos)
        for activo in activos.values():
            shutil.copy2(os.path.join(CONTENIDO, 'activos', activo['modelo']),
                         os.path.join(destino_activos, activo['modelo']))

    plantilla = _plantilla('pagina.html')
    padres = _padres(fichas)
    codigos = orden_idiomas(idiomas)
    versiones = {
        'V_ESTILOS': version_de('estilos/sitio.css'),
        'V_TOKENS': version_de('estilos/tokens.css'),
        'V_JS': version_de('js/sitio.js'),
        'V_VISOR': version_de('js/visor.js'),
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
               aviso=False, visor_js=False, base_enlaces=None):
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
                .replace('{{COLORES}}', _colores_css(activo))
                .replace('{{T_SALTAR}}', _esc(T['saltar']))
                .replace('{{T_BAJADA}}', _esc(T['bajada']))
                .replace('{{T_TEMA}}', _esc(T['tema']))
                .replace('{{NAV_SITIO}}', cabecera_idiomas(ruta, idioma, T, base))
                .replace('{{AVISO}}', _aviso(T) if aviso else '')
                .replace('{{CUERPO}}', cuerpo)
                .replace('{{PIE}}', T['pie'])
                .replace('{{GUION_VISOR}}', guion_visor(base) if visor_js else ''))
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
            es_estructura = ficha['tipo'] == 'estructura'
            descripcion = vista.get('definicion') or _parrafos(vista, 'anatomia')[0]
            cuerpo = ['<main class="atlas" id="contenido">']
            if es_estructura and activo:
                cuerpo.append(_visor_html(ficha, vista, activo, base, enlace, con_visor, T))
            cuerpo.append('<section class="panel">')
            cuerpo.append(_navegacion(ficha, fichas, padres, enlace,
                                      activo['colores'] if activo else {}, T, idioma))
            cuerpo.append(_ficha_html(ficha, vista, pendientes, fichas,
                                      activo if es_estructura else None, enlace, T, idioma))
            cuerpo.append('</section></main>')
            guardar('%sestructura/%s/index.html' % (pre, idf),
                    pagina('estructura/%s/' % idf, idioma,
                           '%s — %s' % (vista['nombre'], T['titulo_sitio']),
                           RE_ENLACE.sub(lambda m: m.group(2) or m.group(1), descripcion),
                           base, ''.join(cuerpo), activo=activo,
                           aviso=bool(es_estructura and activo),
                           visor_js=bool(es_estructura and activo)))
            paginas_escritas += 1

        # Portada: /[idioma/]
        base = '../' * profundidad if profundidad else './'
        enlace = lambda ruta, base=base, pre=pre: base + pre + ruta
        guardar('%sindex.html' % pre,
                pagina('', idioma, '%s — %s' % (T['titulo_sitio'], T['bajada']),
                       T['meta_portada'], base,
                       '<main class="lectura" id="contenido">%s</main>'
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
