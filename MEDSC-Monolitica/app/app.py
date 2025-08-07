from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes.clinic import clinic
from routes.login import login
from routes.patients import patients
from routes.attention import attention
from routes.chat import chat  # Importar el nuevo blueprint

# Cargar variables de entorno desde el directorio padre
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Crear instancia de SocketIO
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configuración para Supabase
    app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-temporal')
    
    # Inicializar SQLAlchemy siempre para evitar errores de contexto
    from utils.db import db
    
    # Configurar base de datos según el modo
    if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
        from config import DATABASE_CONNECTION_URI
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        # Configuración para SQLite en memoria para evitar errores cuando no se usa MySQL
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Configurar Socket.IO primero antes de CORS
    socketio.init_app(app, 
                     cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"],
                     logger=False,
                     engineio_logger=False,
                     async_mode='threading',
                     manage_session=False,
                     transports=['polling', 'websocket'],
                     always_connect=False,
                     ping_timeout=60,
                     ping_interval=25)

    # Configurar CORS después de Socket.IO para evitar conflictos
    CORS(app, 
         origins=["http://localhost:3000", "http://localhost:3001"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True)

    # Register blueprints
    app.register_blueprint(clinic)
    app.register_blueprint(login)
    app.register_blueprint(patients)
    app.register_blueprint(attention)
    app.register_blueprint(chat)  # Registrar el nuevo blueprint

    return app

# Agregar esta función para ejecutar la aplicación con SocketIO
# def run_app():
#     from app import socketio, app
#     socketio.run(app, debug=True, host='0.0.0.0')

# if __name__ == '__main__':
#     run_app()
