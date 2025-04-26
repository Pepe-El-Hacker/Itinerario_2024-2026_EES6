ESTRUCTURA BASICA DE PARCHES:

Nombre-del-Parche/

├── patch.py

├── templates/

│   └── nueva_pagina.html

├── static/

│   ├── css/

│   │   └── estilos.css

│   ├── js/

│   │   └── script.js

│   └── img/

│       └── imagen.png

└── otros_archivos/
    └── datos.json


EJEMPLO DE patch.py:

from flask import render_template

def init_patch(app, socketio):

    @app.route('/nueva_pagina')
    def nueva_pagina():
        return render_template('nueva_pagina.html')
    print('✅ Ruta /nueva_pagina agregada desde el parche.')


patch.py minimo:

def init_patch(app, socketio):

    @app.route('/nueva_pagina')
    def nueva_pagina():
        return render_template('nueva_pagina.html')
