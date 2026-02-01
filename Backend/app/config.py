from dotenv import load_dotenv
import os
import secrets

# Cargar variables de entorno desde el directorio padre o actual
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # Directorio padre
    os.path.join(os.path.dirname(__file__), '.env'),  # Directorio actual
    '.env'  # Directorio de trabajo actual
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Para la conexión Python, usaremos root
user = "root"
password = os.getenv("MYSQL_ROOT_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
database = os.getenv("MYSQL_DATABASE")

DATABASE_CONNECTION_URI = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL y SUPABASE_KEY deben estar definidos en las variables de entorno (.env)")

# Secret Key para Flask (sesiones, CSRF, etc.)
# Generada de forma segura y almacenada en .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY debe estar definida en las variables de entorno (.env)")

# Configuración de Encriptación de Datos Sensibles
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError(
        "ENCRYPTION_KEY debe estar definida en las variables de entorno (.env). "
        "Genera una con: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )

# Configuración de entorno
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"