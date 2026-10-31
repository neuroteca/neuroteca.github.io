# Neuroteca

*Atlas vivo del sistema nervioso.* Atlas interactivo de neuroanatomía y neurofisiología, de acceso
libre, publicado en GitHub Pages (https://neuroteca.github.io) y usable sin conocimientos de
programación.

## Si eres un agente, empieza aquí

**Lee [`GUIA.md`](GUIA.md) completa.** Es la única guía: dice cómo está hecho el atlas, cómo se
trabaja (una rama y un pull request por cambio, Max revisa y aprueba) y qué reglas no cambian.
No hay reporte de orientación ni ritual de cierre; el pull request es el reporte.

## Reglas que no se negocian

- **Lo que no está escrito no está decidido.** No asumas ni completes huecos: pregunta en el PR
  o abre un issue.
- **Ninguna afirmación neurocientífica sin fuente localizable.** Un agente no es una fuente.
- **`revisado` lo pone Max**, nunca el agente.
- **`_referencia/` nunca entra a git.** Contiene datos personales y este repositorio es público.
- **El contenido vive como datos** en `contenido/`; la aplicación en `src/`; `docs/` se genera,
  no se edita.

## Estructura

| Carpeta | Qué contiene |
|---|---|
| `contenido/` | Los datos del atlas: fichas neuro y activos visuales |
| `src/` | La aplicación |
| `herramientas/` | El generador y las herramientas de geometría |
| `docs/` | El sitio generado que publica GitHub Pages |
| `archivo/` | Material retirado, incluido el método anterior. No rige |
| `_referencia/` | Material privado, **excluido de git**. No se lee salvo que Max lo pida |
