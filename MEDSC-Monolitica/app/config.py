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
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vdhbgtgbxszzheftvaga.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkaGJndGdieHN6emhlZnR2YWdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDQ0NDUsImV4cCI6MjA2OTk4MDQ0NX0.LdGqI_8JONJAex3Qbn407ueNE8hRzApGkQy5JY7x3eg")

# En Producción, asegúrate de generar una clave secreta segura
# SECRET_KEY = secrets.token_urlsafe(32)
SECRET_KEY = "1234"