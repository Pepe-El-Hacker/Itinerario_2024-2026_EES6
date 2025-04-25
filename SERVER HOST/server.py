import os, sys, subprocess, urllib.request

# 0) Defino y creo ./libs
current_path = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.expanduser(f"{current_path}/libs/")
os.makedirs(libs_path, exist_ok=True)

# 1) Descargar socket.io.min.js si no está
static_libs_path = os.path.join(current_path, "static", "libs")
os.makedirs(static_libs_path, exist_ok=True)

socketio_js_path = os.path.join(static_libs_path, "socket.io.min.js")
socketio_js_url = "https://cdn.socket.io/4.7.2/socket.io.min.js"

if not os.path.exists(socketio_js_path):
    print("Descargando socket.io.min.js…")
    try:
        urllib.request.urlretrieve(socketio_js_url, socketio_js_path)
        print("✔ socket.io.min.js descargado en static/libs/")
    except Exception as e:
        print(f"❌ Error al descargar socket.io.min.js: {e}")
        input("Presioná Enter para cerrar…")
        sys.exit(1)
else:
    print("✔ socket.io.min.js ya está presente.")

# 2) Compruebo si ya están los paquetes en ./libs
def libs_contiene(paquete_nombre):
    # busca carpeta o egg/wheel del paquete
    base = os.path.join(libs_path, paquete_nombre)
    return os.path.isdir(base) or any(fn.startswith(paquete_nombre) for fn in os.listdir(libs_path))

# si falta alguno, lo instalo
necesarios = ["flask", "flask_socketio", "werkzeug"]
if not all(libs_contiene(p) for p in necesarios):
    print("No están todos los paquetes en ./libs → instalando…")
    requirements = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--no-user", "--target", libs_path,
            "-r", requirements
        ])
        print("Instalación en ./libs completada.")
    except Exception as e:
        print(f'Error al instalar las librerias: {e}')
        input("Presioná Enter para cerrar...")
        sys.exit(1)

# 3) Ahora sí añado ./libs al path *antes* de importar
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)
try: 
    # 4) Importo (ya obligatoriamente vendrán de ./libs)
    from flask import Flask, render_template, request, send_file
    from flask_socketio import SocketIO, emit
    from werkzeug.utils import secure_filename

    print("Módulos importados correctamente desde ./libs.")
except ImportError as e:
    print(f'Error al importar las librerias desde ./libs: {e}')
    input("Presioná Enter para cerrar...")
    sys.exit(1)

UPLOAD_FOLDER = os.path.expanduser(f"{current_path}/db/")  # Carpeta de subida de archivos

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

# Asegúrate de que exista la carpeta
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def listar_archivos():
    return os.listdir(UPLOAD_FOLDER)

import socket

def obtener_ips_locales():
    ips = []
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        ips.append(local_ip)
    except:
        pass
    try:
        # Usar UDP para descubrir la IP externa de la interfaz predeterminada
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        external_ip = s.getsockname()[0]
        s.close()
        if external_ip not in ips:
            ips.append(external_ip)
    except:
        pass
    return ips

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/upload', methods=['POST', 'GET'])
def subir_archivo():
    archivo = request.files.get('archivo')
    if archivo:
        filename = secure_filename(archivo.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta)
        # Avisamos a todos los clientes que la lista cambió
        socketio.emit('actualizar_lista', listar_archivos(), namespace='/', to=None)
        return render_template('data.html')
    return render_template('data.html')

@app.route('/get_file/<filename>')
def get_file(filename):
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(ruta, as_attachment=True)

@socketio.on('solicitar_archivos')
def enviar_lista():
    emit('actualizar_lista', listar_archivos())

if __name__ == '__main__':
    try:
        print("Servidor escuchando en las siguientes IPs de red local:")
        for ip in obtener_ips_locales():
            print(f"  -> http://{ip}:5000")
        socketio.run(app, host='0.0.0.0', port=5000)
        input("Servidor finalizado. Presioná Enter para cerrar...")
    except Exception as e:
        print(f"Error: {e}")
        input("Presioná Enter para cerrar...")