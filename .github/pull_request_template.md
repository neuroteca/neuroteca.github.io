## Qué cambia

<!-- Una o dos frases. Si es un lote de contenido: qué fichas entran y a qué nivel. -->

## Tipo

- [ ] Contenido (lote de fichas o activos)
- [ ] Software (generador, aplicación, estilos)
- [ ] Documentación o proceso

## Lista de revisión · contenido

- [ ] Cada afirmación tiene fuente citada y localizable, y la fuente dice lo que la ficha dice
- [ ] Correcto al nivel de detalle declarado (`N1`…`N5`)
- [ ] Lo establecido y lo discutido están diferenciados donde aplica
- [ ] Ningún término técnico sin enlace `[[id]]` al glosario; nada explicado en línea en más de media frase
- [ ] Término en latín en la primera mención; sinónimos en su campo, no en el cuerpo
- [ ] Activos nuevos: origen, licencia, atribución, nivel, estado y peso registrados
- [ ] Al aprobar, Max cambia `estado` a `revisado` o pide que se cambie

## Lista de revisión · software

- [ ] Las páginas siguen funcionando sin JavaScript y por URL directa
- [ ] Probado en móvil (375 px) y con teclado
- [ ] Sin dependencias nuevas de gestor de paquetes ni CDN
- [ ] Si cambia cómo se trabaja, `GUIA.md` cambia en este mismo PR

## Verificación

- [ ] `python3 herramientas/construir.py --validar` pasa
- [ ] `docs/` regenerado y comiteado (si cambia el sitio)
