# 🏥 MEDSC Backend

Backend robusto desarrollado con **Flask** y **Python** para el sistema médico MEDSC.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-black?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?logo=sqlalchemy)
![Socket.IO](https://img.shields.io/badge/Socket.IO-5.0+-green?logo=socket.io)

---

## 🚀 Características Principales

- 🌐 **API RESTful** completa
- 🔒 **Autenticación JWT** segura
- 💬 **Chat en tiempo real** con Socket.IO
- 🗄️ **Base de datos híbrida** (MySQL + Supabase)
- 📊 **ORM avanzado** con SQLAlchemy
- 🔄 **CORS configurado** para frontend
- 🛡️ **Validación robusta** de datos
- 📝 **Documentación automática** de API

---

## 🛠️ Stack Tecnológico

### Backend Core
- **Flask 3.1+** - Framework web minimalista
- **Python 3.8+** - Lenguaje de programación
- **SQLAlchemy 2.0+** - ORM avanzado

### Base de Datos
- **MySQL** - Base de datos principal
- **Supabase** - Backend as a Service
- **PyMySQL** - Conector MySQL

### Comunicación en Tiempo Real
- **Flask-SocketIO** - WebSocket para Flask
- **Socket.IO** - Protocolo de comunicación bidireccional

### Seguridad & Utilidades
- **Flask-JWT-Extended** - Autenticación JWT
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Bcrypt** - Hashing de contraseñas
- **python-dotenv** - Variables de entorno

---

## 📋 Prerequisitos

- **Python 3.8+**
- **MySQL** (o Docker)
- **Cuenta Supabase** (opcional pero recomendado)
- **pip** o **pipenv**

---

## 🚀 Instalación y Configuración

### 1. Configuración del Entorno

```bash
# Clonar repositorio y navegar al backend
cd MEDSC-Monolitica

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r app/requirements.txt
```

### 2. Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# Base de datos MySQL
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_HOST=localhost
MYSQL_DATABASE=medsc_db
MYSQL_PORT=3306

# Supabase (recomendado)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key

# JWT Secret
JWT_SECRET_KEY=tu_clave_secreta_muy_segura

# Configuración Flask
FLASK_ENV=development
FLASK_DEBUG=true
```

### 3. Configuración de Base de Datos

#### Opción A: MySQL Local
```bash
# Instalar MySQL y crear base de datos
mysql -u root -p
CREATE DATABASE medsc_db;
```

#### Opción B: MySQL con Docker
```bash
# Ejecutar MySQL en Docker
docker-compose up -d db
```

#### Opción C: Solo Supabase
```bash
# El sistema funciona completamente con Supabase
# Solo configurar las variables SUPABASE_*
```

### 4. Ejecutar la Aplicación

```bash
# Desde la carpeta MEDSC-Monolitica
python app/index.py
```

El servidor estará disponible en: **http://localhost:5000**

---

## 🏗️ Estructura del Proyecto

```
MEDSC-Monolitica/
├── app/
│   ├── routes/                 # Endpoints de la API
│   │   ├── login.py           # Autenticación
│   │   ├── clinic.py          # Rutas principales
│   │   ├── patients.py        # Gestión de pacientes
│   │   ├── attention.py       # Atención médica
│   │   └── chat.py            # Chat en tiempo real
│   │
│   ├── models/                # Modelos de base de datos
│   │   └── models_flask.py    # Definición de tablas
│   │
│   ├── utils/                 # Utilidades
│   │   ├── db.py              # Configuración de DB
│   │   └── supabase_client.py # Cliente Supabase
│   │
│   ├── templates/             # Templates HTML (legado)
│   ├── static/                # Archivos estáticos
│   │
│   ├── app.py                 # Aplicación Flask principal
│   ├── index.py               # Punto de entrada
│   ├── config.py              # Configuraciones
│   └── requirements.txt       # Dependencias Python
│
├── docker-compose.yml         # Configuración Docker
└── README.md                  # Este archivo
```

---

## 🌐 API Endpoints

### 🔐 Autenticación
- `POST /login` - Iniciar sesión
- `POST /logout` - Cerrar sesión
- `GET /verify-token` - Verificar JWT

### 👥 Pacientes
- `GET /patients` - Listar pacientes
- `POST /patients` - Crear paciente
- `PUT /patients/{id}` - Actualizar paciente
- `DELETE /patients/{id}` - Eliminar paciente
- `GET /patients/{id}` - Obtener paciente específico

### 🏥 Atención Médica
- `POST /add-attention` - Crear nueva atención
- `POST /add-vital-signs` - Agregar signos vitales
- `POST /add-evaluation` - Agregar evaluación inicial
- `POST /add-physical-exam` - Agregar examen físico
- `POST /add-diagnostic` - Agregar diagnóstico
- `POST /add-treatment` - Agregar tratamiento
- `GET /get-attentions/{patient_id}` - Historial de atenciones

### 💬 Chat
- `POST /send-message` - Enviar mensaje HTTP
- `GET /get-messages/{user_id}` - Obtener mensajes
- `GET /get-chat-doctors` - Listar doctores disponibles
- `WebSocket /socket.io/` - Chat en tiempo real

### 📊 Dashboard
- `GET /dashboard-stats` - Estadísticas generales
- `GET /recent-activity` - Actividad reciente

---

## 🔧 Modelos de Base de Datos

### Principales Entidades
- **Patient** - Información de pacientes
- **Doctor** - Información de médicos
- **Attention** - Consultas médicas
- **ChatMessage** - Mensajes del chat
- **Diagnostic** - Diagnósticos médicos
- **Treatment** - Tratamientos aplicados
- **Laboratory** - Exámenes de laboratorio
- **Imaging** - Estudios de imagen

### Relaciones
- Un paciente puede tener múltiples atenciones
- Una atención puede tener múltiples diagnósticos
- Los doctores pueden chatear con pacientes
- Historial completo de todas las interacciones

---

## 💬 Chat en Tiempo Real

### Características
- **WebSocket** con Socket.IO
- **Fallback HTTP** automático
- **Notificaciones** en tiempo real
- **Estado de conectividad** de usuarios
- **Persistencia** de mensajes en BD

### Eventos WebSocket
```python
# Eventos del servidor
@socketio.on('connect')
@socketio.on('disconnect')
@socketio.on('send_message')
@socketio.on('join_room')

# Eventos emitidos al cliente
emit('new_message', message_data)
emit('user_status', status_data)
emit('message_sent', confirmation)
```

---

## 🔒 Seguridad Implementada

- ✅ **JWT Authentication** en todas las rutas protegidas
- ✅ **CORS configurado** específicamente para el frontend
- ✅ **Bcrypt hashing** para contraseñas
- ✅ **Validación de entrada** en todos los endpoints
- ✅ **Sanitización** de datos SQL
- ✅ **Headers de seguridad** configurados

---

## 📊 Monitoreo y Logs

### Logging
```python
# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs de eventos importantes
logger.info('User logged in')
logger.error('Database connection failed')
```

### Métricas (Futuro)
- Tiempo de respuesta de APIs
- Conectividad de WebSocket
- Uso de base de datos
- Errores y excepciones

---

## 🐳 Docker Support

```bash
# Ejecutar solo la base de datos
docker-compose up -d db

# Ejecutar toda la aplicación (futuro)
docker-compose up --build
```

---

## 🧪 Testing

### Estructura de Tests
```bash
# Ejecutar tests unitarios
python -m pytest app/test_models.py

# Tests de modelos de base de datos
python app/test_models.py
```

---

## 🔧 Desarrollo y Debugging

### Modo Debug
```bash
# Ejecutar en modo desarrollo
export FLASK_ENV=development
export FLASK_DEBUG=true
python app/index.py
```

### Herramientas Útiles
- **Flask Debug Toolbar** (desarrollo)
- **SQLAlchemy logging** para consultas
- **SocketIO debug** para WebSocket
- **Postman collection** para testing APIs

---

## 📈 Performance & Optimizaciones

- ⚡ **Connection pooling** en SQLAlchemy
- 🗄️ **Query optimization** con índices
- 📦 **Lazy loading** de relaciones
- 🔄 **Async operations** con SocketIO
- 💾 **Caching** estratégico (futuro)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea feature branch: `git checkout -b feature/nueva-api`
3. Commit cambios: `git commit -am 'Agrega nueva API'`
4. Push branch: `git push origin feature/nueva-api`
5. Crea Pull Request

---

## 📄 Licencia

Este proyecto es parte del sistema MEDSC bajo licencia MIT.

---

**Backend potente y escalable para el futuro de la medicina digital** 🚀
