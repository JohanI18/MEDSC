from flask import Blueprint, request, jsonify, session
from utils.supabase_client import supabase_auth
from models.models_flask import Doctor
from utils.db import db
import logging
import re
import os

logger = logging.getLogger(__name__)

admin = Blueprint('admin', __name__, url_prefix='/api/admin')

# Clave secreta para crear el primer admin (cambiar en producción)
BOOTSTRAP_SECRET = os.environ.get('ADMIN_BOOTSTRAP_SECRET', 'medsc-admin-setup-2026')


@admin.route('/bootstrap', methods=['POST'])
def bootstrap_admin():
    """
    Endpoint de inicialización para crear el primer administrador.
    Requiere una clave secreta y solo funciona si no hay admins en el sistema.
    """
    try:
        data = request.get_json()
        
        # Verificar clave secreta
        if data.get('bootstrap_secret') != BOOTSTRAP_SECRET:
            return jsonify({
                'success': False,
                'error': 'Clave de inicialización inválida'
            }), 403
        
        # Verificar si ya existe un admin
        existing_admin = Doctor.query.filter_by(role='admin', is_deleted=False).first()
        if existing_admin:
            return jsonify({
                'success': False,
                'error': 'Ya existe un administrador en el sistema. Use el panel de admin para crear más usuarios.'
            }), 400
        
        # Validar datos requeridos
        required_fields = [
            'email', 'password', 'firstName', 'lastName1', 'identifierCode',
            'phoneNumber', 'address', 'gender', 'sex', 'speciality'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return jsonify({'success': False, 'error': 'Email inválido'}), 400
        
        # Validar contraseña
        if len(data['password']) < 6:
            return jsonify({
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Crear usuario en Supabase
        full_name = f"{data['firstName']} {data.get('middleName', '')} {data['lastName1']} {data.get('lastName2', '')}".strip()
        metadata = {
            'full_name': full_name,
            'first_name': data['firstName'],
            'last_name': data['lastName1'],
            'speciality': data['speciality'],
            'role': 'admin'
        }
        
        supabase_result = supabase_auth.sign_up(data['email'], data['password'], metadata)
        
        if not supabase_result['success']:
            return jsonify({
                'success': False,
                'error': f'Error en Supabase: {supabase_result["message"]}'
            }), 400
        
        # Obtener Supabase UID
        supabase_user = supabase_result.get('user')
        if not supabase_user or not hasattr(supabase_user, 'id') or not supabase_user.id:
            return jsonify({'success': False, 'error': 'No se pudo obtener el UID de Supabase'}), 400
            
        supabase_uid = supabase_user.id
        
        # Crear admin en la base de datos local
        new_admin = Doctor(
            identifierCode=data['identifierCode'],
            supabase_id=supabase_uid,
            firstName=data['firstName'],
            middleName=data.get('middleName'),
            lastName1=data['lastName1'],
            lastName2=data.get('lastName2'),
            phoneNumber=data['phoneNumber'],
            address=data['address'],
            gender=data['gender'],
            sex=data['sex'],
            speciality=data['speciality'],
            email=data['email'],
            role='admin',  # Rol de administrador
            status='active',
            created_by=supabase_uid,
            updated_by=supabase_uid,
            is_deleted=False
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        logger.info(f"Bootstrap admin created: {data['email']} with Supabase ID: {supabase_uid}")
        
        return jsonify({
            'success': True,
            'message': 'Administrador creado exitosamente. Ahora puede iniciar sesión y crear más usuarios desde el panel de admin.',
            'admin': {
                'id': new_admin.id,
                'email': new_admin.email,
                'firstName': new_admin.firstName,
                'lastName1': new_admin.lastName1
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in bootstrap: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def require_admin(f):
    """Decorator to require admin role for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        
        # Get doctor role from database
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Usuario no identificado'}), 401
        
        doctor = Doctor.query.filter_by(supabase_id=user_id, is_deleted=False).first()
        if not doctor:
            return jsonify({'success': False, 'error': 'Doctor no encontrado'}), 404
        
        if doctor.role != 'admin':
            return jsonify({'success': False, 'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_auth(f):
    """Decorator to require authentication for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('autenticado'):
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/doctors', methods=['GET'])
@require_admin
def list_doctors():
    """List all doctors (admin only)"""
    try:
        doctors = Doctor.query.filter_by(is_deleted=False).all()
        
        doctors_list = []
        for doc in doctors:
            doctors_list.append({
                'id': doc.id,
                'supabase_id': doc.supabase_id,
                'identifierCode': doc.identifierCode,
                'firstName': doc.firstName,
                'middleName': doc.middleName,
                'lastName1': doc.lastName1,
                'lastName2': doc.lastName2,
                'email': doc.email,
                'phoneNumber': doc.phoneNumber,
                'address': doc.address,
                'gender': doc.gender,
                'sex': doc.sex,
                'speciality': doc.speciality,
                'role': doc.role,
                'status': doc.status,
                'created_at': doc.created_at.isoformat() if doc.created_at else None
            })
        
        return jsonify({
            'success': True,
            'doctors': doctors_list,
            'total': len(doctors_list)
        })
        
    except Exception as e:
        logger.error(f"Error listing doctors: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin.route('/doctors', methods=['POST'])
@require_admin
def create_doctor():
    """Create a new doctor (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'email', 'password', 'firstName', 'lastName1', 'identifierCode',
            'phoneNumber', 'address', 'gender', 'sex', 'speciality'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return jsonify({'success': False, 'error': 'Email inválido'}), 400
        
        # Validate password
        if len(data['password']) < 6:
            return jsonify({
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        # Check if email or identifier already exists
        existing_email = Doctor.query.filter_by(email=data['email'], is_deleted=False).first()
        if existing_email:
            return jsonify({'success': False, 'error': 'El email ya está registrado'}), 400
            
        existing_identifier = Doctor.query.filter_by(identifierCode=data['identifierCode'], is_deleted=False).first()
        if existing_identifier:
            return jsonify({
                'success': False,
                'error': 'El número de identificación ya está registrado'
            }), 400
        
        # Create user in Supabase
        full_name = f"{data['firstName']} {data.get('middleName', '')} {data['lastName1']} {data.get('lastName2', '')}".strip()
        metadata = {
            'full_name': full_name,
            'first_name': data['firstName'],
            'last_name': data['lastName1'],
            'speciality': data['speciality']
        }
        
        supabase_result = supabase_auth.sign_up(data['email'], data['password'], metadata)
        
        if not supabase_result['success']:
            return jsonify({
                'success': False,
                'error': f'Error en Supabase: {supabase_result["message"]}'
            }), 400
        
        # Get Supabase UID
        supabase_user = supabase_result.get('user')
        if not supabase_user or not hasattr(supabase_user, 'id') or not supabase_user.id:
            return jsonify({'success': False, 'error': 'No se pudo obtener el UID de Supabase'}), 400
            
        supabase_uid = supabase_user.id
        admin_id = session.get('user_id')
        
        # Create doctor in local database
        new_doctor = Doctor(
            identifierCode=data['identifierCode'],
            supabase_id=supabase_uid,
            firstName=data['firstName'],
            middleName=data.get('middleName'),
            lastName1=data['lastName1'],
            lastName2=data.get('lastName2'),
            phoneNumber=data['phoneNumber'],
            address=data['address'],
            gender=data['gender'],
            sex=data['sex'],
            speciality=data['speciality'],
            email=data['email'],
            role=data.get('role', 'medico'),  # Allow setting role
            status='active',
            created_by=admin_id,
            updated_by=admin_id,
            is_deleted=False
        )
        
        db.session.add(new_doctor)
        db.session.commit()
        
        logger.info(f"Doctor created by admin: {data['email']} with Supabase ID: {supabase_uid}")
        
        return jsonify({
            'success': True,
            'message': 'Doctor creado exitosamente',
            'doctor': {
                'id': new_doctor.id,
                'email': new_doctor.email,
                'firstName': new_doctor.firstName,
                'lastName1': new_doctor.lastName1,
                'role': new_doctor.role
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating doctor: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin.route('/doctors/<int:doctor_id>', methods=['PUT'])
@require_admin
def update_doctor(doctor_id):
    """Update a doctor (admin only)"""
    try:
        doctor = Doctor.query.filter_by(id=doctor_id, is_deleted=False).first()
        if not doctor:
            return jsonify({'success': False, 'error': 'Doctor no encontrado'}), 404
        
        data = request.get_json()
        admin_id = session.get('user_id')
        
        # Update fields if provided
        if data.get('firstName'):
            doctor.firstName = data['firstName']
        if data.get('middleName') is not None:
            doctor.middleName = data['middleName']
        if data.get('lastName1'):
            doctor.lastName1 = data['lastName1']
        if data.get('lastName2') is not None:
            doctor.lastName2 = data['lastName2']
        if data.get('phoneNumber'):
            doctor.phoneNumber = data['phoneNumber']
        if data.get('address'):
            doctor.address = data['address']
        if data.get('speciality'):
            doctor.speciality = data['speciality']
        if data.get('role'):
            doctor.role = data['role']
        if data.get('status'):
            doctor.status = data['status']
        
        doctor.updated_by = admin_id
        
        db.session.commit()
        
        logger.info(f"Doctor updated by admin: {doctor.email}")
        
        return jsonify({
            'success': True,
            'message': 'Doctor actualizado exitosamente',
            'doctor': {
                'id': doctor.id,
                'email': doctor.email,
                'firstName': doctor.firstName,
                'lastName1': doctor.lastName1,
                'role': doctor.role,
                'status': doctor.status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating doctor: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@require_admin
def delete_doctor(doctor_id):
    """Soft delete a doctor (admin only)"""
    try:
        doctor = Doctor.query.filter_by(id=doctor_id, is_deleted=False).first()
        if not doctor:
            return jsonify({'success': False, 'error': 'Doctor no encontrado'}), 404
        
        # Prevent deleting yourself
        current_doctor = Doctor.query.filter_by(supabase_id=session.get('user_id'), is_deleted=False).first()
        if current_doctor and current_doctor.id == doctor_id:
            return jsonify({'success': False, 'error': 'No puedes eliminarte a ti mismo'}), 400
        
        admin_id = session.get('user_id')
        
        # Soft delete
        doctor.is_deleted = True
        doctor.status = 'inactive'
        doctor.updated_by = admin_id
        
        db.session.commit()
        
        logger.info(f"Doctor soft deleted by admin: {doctor.email}")
        
        return jsonify({
            'success': True,
            'message': 'Doctor eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting doctor: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info including role"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Usuario no identificado'}), 401
        
        doctor = Doctor.query.filter_by(supabase_id=user_id, is_deleted=False).first()
        if not doctor:
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'email': session.get('email'),
                    'role': 'user',
                    'isAdmin': False
                }
            })
        
        return jsonify({
            'success': True,
            'user': {
                'id': doctor.id,
                'supabase_id': doctor.supabase_id,
                'email': doctor.email,
                'firstName': doctor.firstName,
                'lastName1': doctor.lastName1,
                'speciality': doctor.speciality,
                'role': doctor.role,
                'isAdmin': doctor.role == 'admin'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
