/* Neuroteca — pieza `visor`.
 *
 * Mejora progresiva sobre una página que ya funciona sin ella (RT-04). El motor
 * dibuja el esquema SVG en el servidor; esta pieza lo sustituye por el modelo 3D
 * solo si todo sale bien. Si falla cualquier cosa —WebGL, la descarga, el propio
 * módulo— el SVG se queda y el atlas sigue usable, que es `CA-A2`.
 *
 * La navegación NO vive aquí: vive en el motor (DEC-11). Apagar esta pieza no
 * puede dejar al visitante sin acceso a las fichas, que es `CA-A1`.
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const contenedor = document.getElementById('visor');
if (contenedor) {
  try {
    arrancar(JSON.parse(contenedor.dataset.visor));
  } catch (e) {
    degradar('No se pudo iniciar el visor.');
    console.error('[visor]', e);
  }
}

function degradar(motivo) {
  if (!contenedor) return;
  const svg = contenedor.querySelector('svg');
  // `hidden` NO existe como propiedad en un SVGElement: `svg.hidden = true` crea una
  // propiedad de JavaScript que no se refleja en ningun atributo y no oculta nada.
  // Hay que poner el atributo, y ademas hace falta la regla [hidden]{display:none}
  // porque .visor svg fija `display` y gana el empate de especificidad.
  if (svg) svg.removeAttribute('hidden');
  const lienzo = contenedor.querySelector('canvas');
  if (lienzo) lienzo.remove();
  const barra = contenedor.querySelector('.visor-barra .estado');
  if (barra) barra.textContent = motivo + ' Se muestra el esquema.';
  contenedor.dataset.degradado = 'si';
}

function variable(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim() || '#888888';
}

function arrancar(cfg) {
  const svg = contenedor.querySelector('svg');

  // ¿Hay WebGL? Si no, no se intenta siquiera (DEC-10).
  const prueba = document.createElement('canvas');
  if (!(prueba.getContext('webgl2') || prueba.getContext('webgl'))) {
    degradar('Este navegador no puede mostrar 3D.');
    return;
  }

  const ancho = contenedor.clientWidth || 520;
  const alto = Math.round(ancho * 400 / 520);

  const renderizador = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderizador.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderizador.setSize(ancho, alto, false);
  renderizador.domElement.style.display = 'block';
  renderizador.domElement.style.width = '100%';
  renderizador.domElement.style.height = 'auto';
  renderizador.domElement.setAttribute('aria-hidden', 'true');

  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(38, ancho / alto, 0.1, 100);
  camara.position.set(0, 0.1, 3.4);

  escena.add(new THREE.AmbientLight(0xffffff, 1.5));
  const luz = new THREE.DirectionalLight(0xffffff, 2.2);
  luz.position.set(1.2, 1.6, 2.4);
  escena.add(luz);
  const relleno = new THREE.DirectionalLight(0x88aacc, 0.7);
  relleno.position.set(-1.5, -0.8, 1.0);
  escena.add(relleno);

  const controles = new OrbitControls(camara, renderizador.domElement);
  controles.enablePan = false;
  controles.enableDamping = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  controles.dampingFactor = 0.08;
  controles.minDistance = 2.0;
  controles.maxDistance = 6.0;

  const rayo = new THREE.Raycaster();
  const puntero = new THREE.Vector2();
  const sectores = [];

  new GLTFLoader().load(cfg.modelo, function (gltf) {
    gltf.scene.traverse(function (nodo) {
      if (!nodo.isMesh) return;
      // El nombre del sector codifica los dos ejes: <region>__<lobulo>.
      // Es el modelo de grafo del esquema, bajado hasta la geometría (DC-04).
      const partes = (nodo.name || '').split('__');
      if (partes.length !== 2) return;
      nodo.userData.porEje = { regiones: partes[0], lobulos: partes[1] };
      const idColor = nodo.userData.porEje[cfg.eje] || partes[0];
      const esActual = Object.values(nodo.userData.porEje).indexOf(cfg.actual) !== -1;
      nodo.material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(variable(cfg.colores[idColor] || '--c-hemisferios')),
        roughness: 0.72,
        metalness: 0.0,
        emissive: new THREE.Color(esActual ? 0x222222 : 0x000000),
      });
      sectores.push(nodo);
    });

    if (!sectores.length) { degradar('El modelo no trae partes reconocibles.'); return; }

    // Encuadre automático: el visor se adapta al modelo, no al revés. Así el
    // modelo definitivo de Blender entra sin tocar la cámara (RT-05).
    const caja = new THREE.Box3().setFromObject(gltf.scene);
    const centro = caja.getCenter(new THREE.Vector3());
    gltf.scene.position.sub(centro);
    const radio = caja.getSize(new THREE.Vector3()).length() / 2;
    camara.position.set(0, 0, radio * 2.6);
    controles.minDistance = radio * 1.6;
    controles.maxDistance = radio * 5.0;
    controles.update();

    escena.add(gltf.scene);
    if (svg) svg.setAttribute('hidden', '');
    contenedor.insertBefore(renderizador.domElement, contenedor.firstChild);
    render();
  }, undefined, function (err) {
    degradar('No se pudo cargar el modelo.');
    console.error('[visor]', err);
  });

  function render() {
    controles.update();
    renderizador.render(escena, camara);
    requestAnimationFrame(render);
  }

  function apuntado(evento) {
    const caja = renderizador.domElement.getBoundingClientRect();
    puntero.x = ((evento.clientX - caja.left) / caja.width) * 2 - 1;
    puntero.y = -((evento.clientY - caja.top) / caja.height) * 2 + 1;
    rayo.setFromCamera(puntero, camara);
    const choques = rayo.intersectObjects(sectores, false);
    return choques.length ? choques[0].object : null;
  }

  renderizador.domElement.addEventListener('click', function (evento) {
    const nodo = apuntado(evento);
    if (!nodo) return;
    const destino = nodo.userData.porEje[cfg.eje];
    if (destino) window.location.href = cfg.base + 'estructura/' + destino + '/';
  });

  renderizador.domElement.addEventListener('pointermove', function (evento) {
    renderizador.domElement.style.cursor = apuntado(evento) ? 'pointer' : 'grab';
  });

  // DEC-14: el visor colorea por el eje principal, asi que el otro eje no se ve.
  // Al apuntar a un boton de la navegacion se resaltan sus sectores, que es lo que
  // hace visible una division que el color no representa. Funciona con raton y con
  // teclado, porque `focus` cuenta igual que `mouseenter`.
  function resaltar(idEstructura) {
    sectores.forEach(function (nodo) {
      const suyo = Object.values(nodo.userData.porEje).indexOf(idEstructura) !== -1;
      const propio = Object.values(nodo.userData.porEje).indexOf(cfg.actual) !== -1;
      nodo.material.emissive.setHex(suyo ? 0x4a4a4a : (propio ? 0x222222 : 0x000000));
    });
  }

  document.querySelectorAll('.partes-nav a[href*="/estructura/"]').forEach(function (enlace) {
    const trozos = enlace.getAttribute('href').split('/').filter(Boolean);
    const id = trozos[trozos.length - 1];
    ['mouseenter', 'focus'].forEach(function (evento) {
      enlace.addEventListener(evento, function () { resaltar(id); });
    });
    ['mouseleave', 'blur'].forEach(function (evento) {
      enlace.addEventListener(evento, function () { resaltar(cfg.actual); });
    });
  });

  const reiniciar = document.getElementById('visor-inicio');
  if (reiniciar) {
    reiniciar.hidden = false;
    reiniciar.addEventListener('click', function () { controles.reset(); });
  }

  window.addEventListener('resize', function () {
    const w = contenedor.clientWidth;
    if (!w) return;
    const h = Math.round(w * 400 / 520);
    camara.aspect = w / h;
    camara.updateProjectionMatrix();
    renderizador.setSize(w, h, false);
  });
}
