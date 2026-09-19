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
