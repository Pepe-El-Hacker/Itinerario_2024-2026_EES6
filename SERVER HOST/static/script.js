console.log('⚙️ script.js cargado');

// Socket.IO conexión
const socket = io();

// Elementos del DOM
const uploadForm   = document.getElementById('uploadForm');
const archivoInput = document.getElementById('archivoInput');
const fileList     = document.getElementById('fileList');

// ⬇️ Cargar lista al entrar
window.addEventListener('load', () => {
  socket.emit('solicitar_archivos');
});

// 🧩 Pintar lista de archivos
function renderizarLista(archivos) {
  if (!fileList) return;
  fileList.innerHTML = '';
  archivos.forEach(nombre => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `/get_file/${encodeURIComponent(nombre)}`;
    a.textContent = nombre;
    a.download = nombre;
    li.appendChild(a);
    fileList.appendChild(li);
  });
}

// 📡 Recibir lista del servidor
socket.on('actualizar_lista', archivos => {
  console.log('📂 Lista de archivos actualizada:', archivos);
  renderizarLista(archivos);
});

// 📦 Manejador de carga
function manejarSubida(form, input, endpoint = '/upload') {
  if (!form || !input) {
    return console.warn('⚠️ Formulario o input no encontrado.');
  }

  // Crear la barra de progreso
  const progreso = document.createElement('div');
  progreso.style.width = '100%';
  progreso.style.height = '20px';
  progreso.style.backgroundColor = '#e0e0e0';
  progreso.style.borderRadius = '5px';
  progreso.style.marginTop = '10px';

  const barra = document.createElement('div');
  barra.style.height = '100%';
  barra.style.width = '0';
  barra.style.backgroundColor = '#4caf50';
  barra.style.borderRadius = '5px';
  progreso.appendChild(barra);

  // Agregar la barra al DOM, debajo del formulario
  form.appendChild(progreso);

  form.addEventListener('submit', async e => {
    e.preventDefault();

    if (!input.files.length) {
      return alert('Seleccioná un archivo antes de subir.');
    }

    const archivo = input.files[0];
    const fd = new FormData();
    fd.append('archivo', archivo);

    console.log('📤 Subiendo archivo:', archivo.name);

    // Usamos XMLHttpRequest para permitir la monitorización del progreso
    const xhr = new XMLHttpRequest();
    xhr.open('POST', endpoint, true);

    const porcentajeTexto = document.createElement('span');
    porcentajeTexto.style.position = 'absolute';
    porcentajeTexto.style.width = '100%';
    porcentajeTexto.style.textAlign = 'center';
    porcentajeTexto.style.color = 'white';
    porcentajeTexto.style.fontWeight = 'bold';
    barra.appendChild(porcentajeTexto);

    // Evento para seguir el progreso de la carga
    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        const porcentaje = (e.loaded / e.total) * 100;
        barra.style.width = porcentaje + '%';
        porcentajeTexto.textContent = Math.round(porcentaje) + '%';
      }
    };

    // Evento para manejar la respuesta del servidor
    xhr.onload = function () {
      if (xhr.status === 200) {
        input.value = '';
        console.log('✅ Subida exitosa:', xhr.responseText);

        // Volver a pedir la lista actualizada
        socket.emit('solicitar_archivos');
      } else {
        console.error('❌ Error subiendo:', xhr.statusText);
        alert('Error subiendo: ' + xhr.statusText);
      }
    };

    // Evento para manejar los errores de la solicitud
    xhr.onerror = function () {
      console.error('❌ Error subiendo:', xhr.statusText);
      alert('Error subiendo: ' + xhr.statusText);
    };

    // Enviar la solicitud
    xhr.send(fd);
  });
}

// 🧠 Inicializar sistema
manejarSubida(uploadForm, archivoInput);