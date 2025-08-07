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

# Cargar variables de entorno
load_dotenv()

# Crear instancia de SocketIO
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configurar CORS para permitir requests desde el frontend
    CORS(app, 
         origins=["http://localhost:3000", "http://localhost:3001"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True)

    # Configuración para Supabase
    app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-temporal')
    
    # Solo inicializar la base de datos si estamos en modo producción con Docker
    if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
        from utils.db import db
        from config import DATABASE_CONNECTION_URI
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    app.register_blueprint(clinic)
    app.register_blueprint(login)
    app.register_blueprint(patients)
    app.register_blueprint(attention)
    app.register_blueprint(chat)  # Registrar el nuevo blueprint

    print("🚀 Aplicación iniciada con Supabase")
    print(f"🌐 Supabase URL: {os.environ.get('SUPABASE_URL', 'No configurado')}")
    print("🔑 Usando autenticación de Supabase")
    print("📝 Visita: http://localhost:5000")

    return app

# Agregar esta función para ejecutar la aplicación con SocketIO
# def run_app():
#     from app import socketio, app
#     socketio.run(app, debug=True, host='0.0.0.0')

# if __name__ == '__main__':
#     run_app()
