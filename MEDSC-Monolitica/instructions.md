# Instrucciones para ejecutar la aplicación

## 1. Crear el archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto con las siguientes variables de entorno:

```env
# Datos de conexión a MySQL
MYSQL_USER=tu_usuario_mysql
MYSQL_PASSWORD=tu_contraseña_mysql
MYSQL_HOST=localhost
MYSQL_DATABASE=nombre_de_tu_base_de_datos
MYSQL_PORT=3306
# Si usas acceso root, define también la contraseña root:
MYSQL_ROOT_PASSWORD=tu_contraseña_root_mysql
```

## 2. Ejecutar con Docker Compose (opcional)

Si prefieres usar Docker, puedes levantar los servicios con:

```bash
docker-compose up --build
```

## 3. Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
````

## 4. Instalar las dependencias

```bash
pip install -r app/requirements.txt
```


## 5. Ejecutar la aplicación

* Para ejecutar el servidor flask (según el script `index.py`):

```bash
python app/index.py
```
El servidor estará corriendo en: http://127.0.0.1:5000 