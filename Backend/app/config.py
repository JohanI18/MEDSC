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

# En Producción, asegúrate de generar una clave secreta segura
# SECRET_KEY = secrets.token_urlsafe(32)
SECRET_KEY = "1234"