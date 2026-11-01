/* Neuroteca — motor.
   Solo dos cosas: el tema y el aviso de entrada. Todo lo demás lo genera el
   constructor como HTML, para que la página funcione sin JavaScript (RT-03). */

(function () {
  'use strict';

  function leer(clave) {
    try { return localStorage.getItem(clave); } catch (e) { return null; }
  }
  function guardar(clave, valor) {
    try { localStorage.setItem(clave, valor); } catch (e) { /* sin almacenamiento, se sigue */ }
  }

  // --- Tema -------------------------------------------------------------
  var btn = document.getElementById('btn-tema');
  if (btn) {
    btn.addEventListener('click', function () {
      var raiz = document.documentElement;
      var actual = raiz.getAttribute('data-tema');
      var oscuro;
      if (actual) {
        oscuro = actual === 'oscuro';
      } else {
        oscuro = window.matchMedia('(prefers-color-scheme: dark)').matches;
      }
      var nuevo = oscuro ? 'claro' : 'oscuro';
      raiz.setAttribute('data-tema', nuevo);
      guardar('neuroteca-tema', nuevo);
    });
  }

  // --- Aviso de entrada (DEC-09) ---------------------------------------
  // Se muestra una vez por navegador. Si el almacenamiento falla, se muestra
  // siempre: el fallo seguro es hacia la honestidad, no hacia ocultarlo.
  var aviso = document.getElementById('aviso-entrada');
  if (aviso) {
    if (leer('neuroteca-aviso-visto') === 'si') {
      aviso.remove();
    } else {
      var cerrar = aviso.querySelector('button');
      if (cerrar) {
        cerrar.addEventListener('click', function () {
          aviso.remove();
          guardar('neuroteca-aviso-visto', 'si');
        });
      }
    }
  }
})();

// --- Filtro del glosario en la portada -----------------------------------
// Sin JavaScript la lista completa está a la vista; con él aparece un campo que la filtra.
(function () {
  'use strict';
  var campo = document.getElementById('glosario-buscar');
  var lista = document.getElementById('glosario-lista');
  if (!campo || !lista) { return; }
  var vacio = document.querySelector('.glosario-vacio');
  var items = Array.prototype.slice.call(lista.querySelectorAll('li'));
  var textos = items.map(function (li) {
    return li.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  });
  campo.hidden = false;
  campo.addEventListener('input', function () {
    var q = campo.value.trim().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    var vistos = 0;
    items.forEach(function (li, i) {
      var ok = !q || textos[i].indexOf(q) !== -1;
      li.hidden = !ok;
      if (ok) { vistos++; }
    });
    if (vacio) { vacio.hidden = vistos > 0; }
  });
  if (location.hash === '#glosario') { campo.focus(); }
})();
