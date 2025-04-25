# --- 0. Cargar libs bases
import os, sys, subprocess, urllib.request, ssl, socket, importlib.util, traceback, rarfile

# --- 1. Configuración de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(BASE_DIR, 'libs')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'db')
PATCH_DIR = os.path.join(BASE_DIR, 'patches')

# Crear carpetas necesarias
for path in [LIBS_DIR, STATIC_DIR, UPLOAD_FOLDER, PATCH_DIR]:
    os.makedirs(path, exist_ok=True)

# --- 2. Descargar socket.io.min.js si no existe
SOCKETIO_JS = os.path.join(STATIC_DIR, 'socket.io.min.js')
SOCKETIO_URL = 'https://cdn.socket.io/4.7.2/socket.io.min.js'

if not os.path.exists(SOCKETIO_JS):
    print('⬇️  Descargando socket.io.min.js...')
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve(SOCKETIO_URL, SOCKETIO_JS)
        print('✔ socket.io.min.js descargado.')
    except Exception as e:
        print(f'❌ Error al descargar: {e}')
        input('Presioná Enter para cerrar...')
        sys.exit(1)
else:
    print('✔ socket.io.min.js ya existe.')

# --- 3. Verificar e instalar dependencias en ./libs
def tiene_paquete(nombre):
    return any(
        nombre in archivo for archivo in os.listdir(LIBS_DIR)
    )

REQUERIDOS = ['flask', 'flask_socketio', 'werkzeug', 'rarfile']
if not all(tiene_paquete(p) for p in REQUERIDOS):
    print('📦 Instalando dependencias en ./libs...')
    req_file = os.path.join(BASE_DIR, 'requirements.txt')
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            '--no-user', '--target', LIBS_DIR, '-r', req_file
        ])
        print('✔ Dependencias instaladas.')
    except Exception as e:
        print(f'❌ Error de instalación: {e}')
        input('Presioná Enter para cerrar...')
        sys.exit(1)

# --- 4. Añadir ./libs al sys.path
if LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

# --- 5. Importar librerías ya instaladas
try:
    from flask import Flask, render_template, request, send_file
    from flask_socketio import SocketIO, emit
    from werkzeug.utils import secure_filename
    print('✔ Módulos importados desde ./libs.')
except ImportError as e:
    print(f'❌ Error al importar: {e}')
    input('Presioná Enter para cerrar...')
    sys.exit(1)

# --- Función para descomprimir y cargar parches
def aplicar_patches():
    parches = [f for f in os.listdir(PATCH_DIR) if f.endswith('.rar')]
    
    if not parches:
        print(f'No hay parches en: {PATCH_DIR}')
        return

    print(f'Importando {len(parches)} parches desde {PATCH_DIR}')

    for parche in parches:
        parche_path = os.path.join(PATCH_DIR, parche)
        carpeta_destino = os.path.join(PATCH_DIR, parche[:-4])  # quitar ".rar"
        os.makedirs(carpeta_destino, exist_ok=True)

        try:
            with rarfile.RarFile(parche_path) as archivo_rar:
                archivo_rar.extractall(carpeta_destino)
            print(f'✔ Parche {parche} descomprimido.')

            patch_py = os.path.join(carpeta_destino, 'patch.py')
            if os.path.isfile(patch_py):
                spec = importlib.util.spec_from_file_location('patch', patch_py)
                patch_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(patch_module)
                print(f'✔ Parche {parche} ejecutado.')
            else:
                print(f'⚠ No se encontró patch.py en {carpeta_destino}')

        except Exception as e:
            print(f'❌ Error al procesar parche {parche}: {e}')
            input('Presioná Enter para cerrar...')
            sys.exit(1)

# --- Llamar función de aplicar parches
aplicar_patches()

# --- 6. Inicialización de la app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

# --- 7. Funciones auxiliares
def listar_archivos():
    return os.listdir(UPLOAD_FOLDER)

def obtener_ips_locales():
    ips = []
    try:
        ips.append(socket.gethostbyname(socket.gethostname()))
    except:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip not in ips:
            ips.append(ip)
    except:
        pass
    return ips

# --- 8. Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/upload', methods=['POST'])
def subir_archivo():
    archivo = request.files.get('archivo')
    if archivo:
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(UPLOAD_FOLDER, filename))
        socketio.emit('actualizar_lista', listar_archivos())
        return render_template('data.html')
    return render_template('data.html')

@app.route('/get_file/<filename>')
def get_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

# --- 9. Socket.IO
@socketio.on('solicitar_archivos')
def enviar_lista():
    emit('actualizar_lista', listar_archivos())

# --- 10. Ejecutar servidor
if __name__ == '__main__':
    try:
        print('🟢 Servidor corriendo en:')
        for ip in obtener_ips_locales():
            print(f'  → http://{ip}:5000')
        socketio.run(app, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f'❌ Error al ejecutar servidor: {e}')
        input('Presioná Enter para cerrar...')