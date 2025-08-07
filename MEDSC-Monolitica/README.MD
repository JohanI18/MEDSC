# MEDSC

**Gestor de Pacientes y Consultas Médicas**

Proyecto monolítico de aplicación web para la gestión de pacientes y consultas médicas, desarrollado por Johan Illicachi, Johanna Huaraca, Adrian Paguay y Kevin Asimbaya.

---

## 🚀 Descripción

MEDSC es una aplicación web monolítica que permite:

- **Registrar y gestionar pacientes** (CRUD).
- **Agendar y llevar el historial** de consultas médicas.
- **Chat en tiempo real** entre médicos y pacientes mediante WebSocket.
- Renderizado de vistas HTML desde el servidor y routing completo del lado servidor.
- Persistencia de datos en base de datos relacional (MYSQL).

---

## 🛠️ Características principales

1. **Monolito completo**  
   - Lógica de negocio, persistencia y presentación en un solo proyecto.

2. **Renderizado de vistas HTML**  
   - Uso de EJS para plantillas del lado servidor.

3. **Routing del lado servidor**  
   - Organización de rutas para pacientes, consultas, autenticación y chat.

4. **Base de datos relacional**  
   - PostgreSQL como motor de datos.

5. **Chat en tiempo real**  
   - Socket.IO para comunicación en WebSocket dentro del mismo stack.

---

## 📦 Tecnologías

Flask(Python) + Jinja2 + SQLAlchemy + Flask-SocketIO

---