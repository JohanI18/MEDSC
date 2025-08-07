from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app, jsonify
from utils.supabase_client import supabase_auth
from datetime import datetime, timedelta
import uuid
import re


login = Blueprint('login', __name__)

@login.route('/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    """Ruta de prueba para verificar CORS"""
    return jsonify({
        'success': True,
        'message': 'CORS funcionando correctamente',
        'method': request.method
    })

@login.route('/', methods=['GET'])
def index():
    """Default login page"""
    return render_template('login.html')

@login.route('/login', methods=['GET', 'POST'])
def new_login():
    if request.method == 'POST':
        # Check if it's a JSON request (from frontend API)
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            password = data.get('password', '')
        else:
            # HTML form request
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
        
        if not email or not password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Por favor ingrese todos los campos'}), 400
            flash('Por favor ingrese todos los campos', 'danger')
            return redirect(url_for('login.new_login'))
        
        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email inválido'}), 400
            flash('Email inválido', 'danger')
            return redirect(url_for('login.new_login'))
        
        # Authenticate with Supabase
        auth_result = supabase_auth.sign_in(email, password)
        
        if auth_result['success']:
            # Store user info in session
            session['autenticado'] = True
            session['user_id'] = auth_result['user'].id
            session['email'] = auth_result['user'].email
            session['auth_provider'] = 'supabase'
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': 'Login exitoso',
                    'user': {
                        'id': auth_result['user'].id,
                        'email': auth_result['user'].email
                    }
                })
            
            flash('Login exitoso', 'success')
            return redirect(url_for('clinic.home'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': auth_result['message']}), 401
            flash(auth_result['message'], 'danger')
            return redirect(url_for('login.new_login'))

    return render_template('login.html')

@login.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout route to clear session and redirect to login"""
    try:
        # Sign out from Supabase
        supabase_auth.sign_out()
        
        # Clear all session data
        session.clear()
        flash('Sesión cerrada exitosamente', 'success')
        
        # Log the logout action using current_app
        current_app.logger.info("User logged out successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}")
        flash('Error al cerrar sesión', 'error')
    
    return redirect(url_for('login.index'))


@login.route('/success')
def success():
    """Página de éxito después del login"""
    if not session.get('autenticado'):
        return redirect(url_for('login.index'))
    
    user_email = session.get('email', 'Usuario')
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Exitoso</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <h2 class="text-success">¡Login Exitoso! 🎉</h2>
                            <p class="lead">Bienvenido, <strong>{user_email}</strong></p>
                            <p>Has iniciado sesión correctamente con Supabase.</p>
                            <div class="mt-4">
                                <a href="{url_for('login.logout')}" class="btn btn-danger">Cerrar Sesión</a>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">
                                    Proveedor de autenticación: Supabase<br>
                                    ID de usuario: {session.get('user_id', 'N/A')}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@login.route('/home')
def home():
    """Dashboard médico principal"""
    if not session.get('autenticado'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login.index'))
    
    user_email = session.get('email', 'Usuario')
    user_id = session.get('user_id', 'N/A')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MEDSC - Dashboard Médico</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .dashboard-card {{
                transition: transform 0.2s;
                cursor: pointer;
            }}
            .dashboard-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .navbar-brand {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <!-- Navbar -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#"><i class="fas fa-hospital"></i> MEDSC</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">
                        <i class="fas fa-user"></i> {user_email}
                    </span>
                    <a href="{url_for('login.logout')}" class="btn btn-outline-light btn-sm">
                        <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                    </a>
                </div>
            </div>
        </nav>

        <!-- Main Dashboard -->
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-4"><i class="fas fa-tachometer-alt"></i> Dashboard Médico</h2>
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> 
                        Bienvenido al sistema MEDSC. Has iniciado sesión correctamente con Supabase.
                    </div>
                </div>
            </div>

            <!-- Módulos Médicos -->
            <div class="row">
                <!-- Gestión de Pacientes -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Gestión de Pacientes</h5>
                            <p class="card-text">Registrar, buscar y gestionar información de pacientes</p>
                            <button class="btn btn-primary" onclick="alert('Módulo en desarrollo - Requiere base de datos MySQL')">
                                <i class="fas fa-user-plus"></i> Acceder
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Consultas Médicas -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-stethoscope fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Consultas Médicas</h5>
                            <p class="card-text">Agendar citas y llevar historial de consultas</p>
                            <button class="btn btn-success" onclick="alert('Módulo en desarrollo - Requiere base de datos MySQL')">
                                <i class="fas fa-calendar-check"></i> Acceder
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Chat Médico -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-comments fa-3x text-info mb-3"></i>
                            <h5 class="card-title">Chat en Tiempo Real</h5>
                            <p class="card-text">Comunicación instantánea entre médicos y pacientes</p>
                            <button class="btn btn-info" onclick="alert('Módulo en desarrollo - Requiere base de datos MySQL')">
                                <i class="fas fa-comment-medical"></i> Acceder
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Reportes -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-bar fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Reportes</h5>
                            <p class="card-text">Estadísticas y reportes médicos</p>
                            <button class="btn btn-warning" onclick="alert('Módulo en desarrollo - Requiere base de datos MySQL')">
                                <i class="fas fa-file-medical-alt"></i> Acceder
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Configuración -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-cogs fa-3x text-secondary mb-3"></i>
                            <h5 class="card-title">Configuración</h5>
                            <p class="card-text">Ajustes del sistema y perfil de usuario</p>
                            <button class="btn btn-secondary" onclick="showUserInfo()">
                                <i class="fas fa-user-cog"></i> Acceder
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Base de Datos -->
                <div class="col-md-4 mb-4">
                    <div class="card dashboard-card h-100 border-danger">
                        <div class="card-body text-center">
                            <i class="fas fa-database fa-3x text-danger mb-3"></i>
                            <h5 class="card-title">Estado de la Base de Datos</h5>
                            <p class="card-text">MySQL no está conectado</p>
                            <button class="btn btn-danger" onclick="showDbInstructions()">
                                <i class="fas fa-exclamation-triangle"></i> Ver Instrucciones
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Información del Usuario -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-info-circle"></i> Información de la Sesión</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Email:</strong> {user_email}<br>
                                    <strong>ID de Usuario:</strong> {user_id}<br>
                                    <strong>Proveedor:</strong> Supabase
                                </div>
                                <div class="col-md-6">
                                    <strong>Estado:</strong> <span class="badge bg-success">Autenticado</span><br>
                                    <strong>Tipo de App:</strong> Modo Supabase-Only<br>
                                    <strong>Base de Datos:</strong> <span class="badge bg-danger">Desconectada</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function showUserInfo() {{
                alert(`Información del Usuario:
                
Email: {user_email}
ID: {user_id}
Proveedor: Supabase
Estado: Autenticado correctamente

Para acceder a todas las funcionalidades, inicia Docker con:
docker-compose up -d db`);
            }}

            function showDbInstructions() {{
                alert(`Para activar todos los módulos médicos:

1. Abre Docker Desktop
2. En terminal ejecuta: docker-compose up -d db  
3. Espera que MySQL se inicie
4. Ejecuta la aplicación completa: python index.py
5. Visita: http://localhost:5000

Actualmente estás en modo demo con solo autenticación Supabase.`);
            }}
        </script>
    </body>
    </html>
    """


# Supabase routes
@login.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user with Supabase"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not email or not password or not confirm_password:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('login.register'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('login.register'))
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return redirect(url_for('login.register'))
        
        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Email inválido', 'danger')
            return redirect(url_for('login.register'))
        
        # Register with Supabase
        metadata = {
            'full_name': full_name
        }
        
        result = supabase_auth.sign_up(email, password, metadata)
        
        if result['success']:
            flash('Registro exitoso. Revisa tu email para confirmar tu cuenta.', 'success')
            return redirect(url_for('login.new_login'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('login.register'))
    
    return render_template('register.html')


@login.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Send password reset email via Supabase"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Por favor ingrese su email', 'danger')
            return redirect(url_for('login.forgot_password'))
        
        result = supabase_auth.reset_password(email)
        
        if result['success']:
            flash('Se ha enviado un email para restablecer tu contraseña', 'success')
        else:
            flash(result['message'], 'danger')
        
        return redirect(url_for('login.forgot_password'))
    
    return render_template('forgot_password.html')



