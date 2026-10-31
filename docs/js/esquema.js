/* Neuroteca — pieza `esquema`.
 *
 * Mejora progresiva sobre el diagrama que el motor ya dibujó como SVG con enlaces:
 * al señalar una estructura (en el esquema o en la lista de la derecha) se resaltan
 * sus flechas y se atenúa el resto. Sin esta pieza el esquema sigue siendo una
 * imagen con enlaces y el texto de «Circuito» cuenta lo mismo (CA-A1, CA-A2).
 */
(function () {
  'use strict';
  var esquema = document.getElementById('esquema');
  if (!esquema) return;
  var nodos = esquema.querySelectorAll('.nodo');
  var flechas = esquema.querySelectorAll('.flecha');
  var botones = document.querySelectorAll('.sistema-nav a[data-nodo]');

  function limpiar() {
    esquema.removeAttribute('data-activo');
    var i;
    for (i = 0; i < nodos.length; i++) { nodos[i].classList.remove('activo', 'vecino'); }
    for (i = 0; i < flechas.length; i++) { flechas[i].classList.remove('activa'); }
  }
  function resaltar(id) {
    limpiar();
    esquema.setAttribute('data-activo', id);
    var vecinos = {};
    var i;
    for (i = 0; i < flechas.length; i++) {
      var f = flechas[i];
      if (f.dataset.de === id || f.dataset.a === id) {
        f.classList.add('activa');
        vecinos[f.dataset.de] = true; vecinos[f.dataset.a] = true;
      }
    }
    for (i = 0; i < nodos.length; i++) {
      var n = nodos[i];
      if (n.dataset.nodo === id) n.classList.add('activo');
      else if (vecinos[n.dataset.nodo]) n.classList.add('vecino');
    }
  }
  function enganchar(el, id) {
    el.addEventListener('mouseenter', function () { resaltar(id); });
    el.addEventListener('focusin', function () { resaltar(id); });
    el.addEventListener('mouseleave', limpiar);
    el.addEventListener('focusout', limpiar);
  }
  var i;
  for (i = 0; i < nodos.length; i++) { enganchar(nodos[i], nodos[i].dataset.nodo); }
  for (i = 0; i < botones.length; i++) { enganchar(botones[i], botones[i].dataset.nodo); }
})();
