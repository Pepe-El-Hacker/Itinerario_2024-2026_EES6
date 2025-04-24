// Este script solo se carga en data.html
console.log('⚙️ script.js cargado');

const socket = io();

// Elementos del DOM
const uploadForm   = document.getElementById('uploadForm');
const archivoInput = document.getElementById('archivoInput');
const fileList     = document.getElementById('fileList');

// Al cargar la página, pedimos la lista actual
window.addEventListener('load', () => {
  socket.emit('solicitar_archivos');
});

// Recibimos la lista y la pintamos
socket.on('actualizar_lista', archivos => {
  console.log('📂 Lista de archivos actualizada:', archivos);
  if (!fileList) return;
  fileList.innerHTML = '';
  archivos.forEach(nombre => {
    const li = document.createElement('li');
    const a  = document.createElement('a');
    a.href = `/get_file/${encodeURIComponent(nombre)}`;
    a.textContent = nombre;
    a.download = nombre;
    li.appendChild(a);
    fileList.appendChild(li);
  });
});

// Manejamos la subida de archivos
if (uploadForm && archivoInput) {
  uploadForm.addEventListener('submit', async e => {
    e.preventDefault();
    if (!archivoInput.files.length) {
      return alert('Seleccioná un archivo antes de subir.');
    }
    const fd = new FormData();
    fd.append('archivo', archivoInput.files[0]);
    console.log('📤 Subiendo archivo:', archivoInput.files[0].name);
    try {
      const resp = await fetch('/upload', { method: 'POST', body: fd });
      const text = await resp.text();
      if (!resp.ok) throw new Error(text);
      archivoInput.value = '';
      // Opcional: notificar al usuario
      console.log('✅ Subida exitosa:', text);
    } catch (err) {
      console.error('❌ Error subiendo:', err);
      alert('Error subiendo: ' + err.message);
    }
  });
} else {
  console.warn('⚠️ uploadForm o archivoInput no encontrado en el DOM.');
}