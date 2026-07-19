from app import create_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio padre
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Crear la aplicación usando la función factory
app = create_app()

# Solo crear tablas si estamos usando base de datos
if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
    from utils.db import db

    with app.app_context():
        db.create_all()  # Ensure all models are created in the database

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
