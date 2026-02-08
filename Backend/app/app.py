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
from routes.icd11 import icd11  # Blueprint para CIE-11 / ICD-11
from routes.admin import admin  # Blueprint para administración

# Cargar variables de entorno desde el directorio padre
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Crear instancia de SocketIO
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configuración para Supabase
    app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-temporal')
    
    # Configuración de cookies de sesión para funcionar con HTTPS y cross-site
    app.config['SESSION_COOKIE_SECURE'] = True  # Solo HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Permitir cross-site
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
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
                     cors_allowed_origins="*",
                     logger=False,
                     engineio_logger=False,
                     async_mode='threading',
                     manage_session=False,
                     transports=['polling', 'websocket'],
                     always_connect=False,
                     ping_timeout=60,
                     ping_interval=25)

    # Configurar CORS después de Socket.IO para evitar conflictos
    # URLs permitidas desde variables de entorno
    cors_origins = ["http://localhost:3000", "http://localhost:3001"]
    frontend_url = os.environ.get('FRONTEND_URL')
    backend_url = os.environ.get('BACKEND_URL')
    if frontend_url:
        cors_origins.append(frontend_url)
    if backend_url:
        cors_origins.append(backend_url)
    
    CORS(app, 
         origins=cors_origins, 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True)

    # Register blueprints
    app.register_blueprint(clinic)
    app.register_blueprint(login)
    app.register_blueprint(patients)
    app.register_blueprint(attention)
    app.register_blueprint(chat)  # Registrar el nuevo blueprint
    app.register_blueprint(icd11)  # Registrar blueprint de CIE-11
    app.register_blueprint(admin)  # Registrar blueprint de administración

    return app

# Agregar esta función para ejecutar la aplicación con SocketIO
# def run_app():
#     from app import socketio, app
#     socketio.run(app, debug=True, host='0.0.0.0')

# if __name__ == '__main__':
#     run_app()
