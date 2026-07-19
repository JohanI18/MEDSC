from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from models.models_flask import (
    Attention, Patient, Doctor, Diagnostic, Histopathology, Imaging, 
    Laboratory, RegionalPhysicalExamination, ReviewOrgansSystem, Treatment
)
from utils.db import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import logging
import os

attention = Blueprint('attention', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_cors_preflight():
    """Handle CORS preflight request"""
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    return None

def check_database_connection():
    """Verifica si hay conexión a la base de datos"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Error de conexión a base de datos: {str(e)}")
        return False

def is_authenticated():
    """Check if user is authenticated for both session and API requests"""
    if session.get('autenticado'):
        return True
    
    # For API requests, check if we have authorization header or basic auth
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # For now, accept any authorization header as valid
        # In production, you should validate the token properly
        return True
    
    # Check if it's a JSON request with credentials
    if request.is_json and request.content_type == 'application/json':
        # For development purposes, allow JSON requests
        # In production, implement proper API authentication
        return True
    
    return False


def _get_supabase_doctor_info():
    """Obtiene información del doctor para autenticación Supabase"""
    email = session.get('email', 'Doctor')
    user_id = session.get('user_id', 'demo')
    name_parts = email.split('@')[0].split('.')
    
    doctor_info = {
        'firstName': name_parts[0].capitalize() if name_parts else 'Doctor',
        'lastName1': name_parts[1].capitalize() if len(name_parts) > 1 else 'Supabase',
        'speciality': 'Medicina General'
    }
    return doctor_info, user_id


def _get_local_doctor_info():
    """Obtiene información del doctor desde la base de datos local"""
    from models.models_flask import Doctor
    
    try:
        doctor = Doctor.query.filter_by(identifierCode=session['cedula'], is_deleted=False).first()
        if doctor:
            return {
                'firstName': doctor.firstName,
                'lastName1': doctor.lastName1,
                'speciality': doctor.speciality
            }, session['cedula']
    except Exception as e:
        logger.error(f"Error fetching doctor info: {str(e)}")
    
    return None, None


def _get_api_doctor_info():
    """Obtiene información del doctor para peticiones API"""
    return {
        'firstName': 'API',
        'lastName1': 'Doctor',
        'speciality': 'Medicina General'
    }, 'api_user'


def _is_api_request():
    """Verifica si la petición es de tipo API"""
    return request.is_json or request.headers.get('Content-Type') == 'application/json'


def get_doctor_info_and_session():
    """Obtiene información del doctor y sessionID de manera compatible con Supabase"""
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if session.get('auth_provider') == 'supabase':
        return _get_supabase_doctor_info()
    
    if 'cedula' in session and has_database:
        return _get_local_doctor_info()
    
    if _is_api_request():
        return _get_api_doctor_info()
    
    return None, None


# =============================================================================
# HELPER FUNCTIONS FOR REDUCING COGNITIVE COMPLEXITY
# =============================================================================

def _check_auth_and_redirect():
    """
    Check authentication and return appropriate response if not authenticated.
    Returns None if authenticated, otherwise returns the appropriate response.
    """
    if is_authenticated():
        return None
    
    if request.is_json:
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    flash('Sesión no válida', 'error')
    return redirect(url_for('clinic.index'))


def _get_request_data():
    """Get data from request, handling both JSON and form data."""
    if request.is_json:
        return request.get_json()
    return request.form.to_dict()


def _get_field_from_request(field_name, default=None):
    """Get a specific field from request data."""
    if request.is_json:
        data = request.get_json()
        return data.get(field_name, default)
    return request.form.get(field_name, default)


def _json_success_response(message, data=None, status=200):
    """Create a JSON success response."""
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def _json_error_response(error, status=400):
    """Create a JSON error response."""
    return jsonify({'success': False, 'error': error}), status


def _handle_success(message, flash_suffix='', redirect_url=None, data=None):
    """Handle successful operation for both JSON and form requests."""
    if request.is_json:
        return _json_success_response(message, data)
    flash(message + flash_suffix, 'success')
    if redirect_url:
        return redirect(redirect_url)
    return None


def _handle_error(error_msg, redirect_url=None, status=500, log_msg=None):
    """Handle error for both JSON and form requests."""
    if log_msg:
        logger.error(log_msg)
    else:
        logger.error(error_msg)
    if request.is_json:
        return _json_error_response(error_msg, status)
    flash(error_msg, 'error')
    if redirect_url:
        return redirect(redirect_url)
    return None


def _add_item_to_list(item_list, item_data, item_name, success_msg, exists_msg):
    """Generic function to add an item to a temporary list."""
    if item_data not in item_list:
        item_list.append(item_data)
        return success_msg, True
    return exists_msg, False


def _remove_item_from_list(item_list, item_id=None, index=None):
    """
    Generic function to remove an item from a temporary list.
    Returns (removed_item, success).
    """
    # Try removing by ID first
    if item_id is not None:
        try:
            idx = int(item_id)
            if 0 <= idx < len(item_list):
                return item_list.pop(idx), True
        except (ValueError, IndexError):
            pass
    
    # Try removing by index
    if index is not None:
        try:
            idx = int(index) if isinstance(index, str) else index
            if 0 <= idx < len(item_list):
                return item_list.pop(idx), True
        except (ValueError, IndexError):
            pass
    
    return None, False


def _get_value_or_none(data, key):
    """Get value from dict, return None if empty or not present."""
    value = data.get(key)
    return value if value else None


def _parse_vital_signs(data):
    """Parse vital signs data from request."""
    fields = ['weight', 'height', 'temperature', 'bloodPressure', 'heartRate',
              'oxygenSaturation', 'breathingFrequency', 'glucose', 'hemoglobin']
    return {field: _get_value_or_none(data, field) for field in fields}


def _validate_attention_prerequisites(redirect_url):
    """Validate that all prerequisites for completing attention are met."""
    if not selected_patient_id:
        return _handle_error(
            'Debe seleccionar un paciente antes de finalizar la atención',
            redirect_url, 400, 'No selected patient ID'
        )

    if not evaluation_data.get('reasonConsultation') or not evaluation_data.get('currentIllness'):
        return _handle_error(
            'Debe completar la evaluación inicial (motivo de consulta y enfermedad actual) antes de finalizar',
            redirect_url, 400, 'Missing reasonConsultation or currentIllness'
        )

    if not evaluation_data.get('evolution'):
        return _handle_error(
            'Debe completar la evolución del paciente antes de finalizar',
            redirect_url, 400, 'Missing evolution'
        )
    
    return None


def _get_or_create_doctor(session_id):
    """Get doctor by session ID or create/find an API doctor."""
    doctor = None
    
    if session_id and session_id != 'api_user':
        doctor = Doctor.query.filter_by(identifierCode=session_id, is_deleted=False).first()
        if doctor:
            return doctor, None
    
    if not (request.is_json or session.get('auth_provider') == 'supabase'):
        return None, 'Doctor no encontrado'
    
    doctor = Doctor.query.filter_by(identifierCode='API001', is_deleted=False).first()
    if doctor:
        return doctor, None
    
    doctor = Doctor.query.filter_by(is_deleted=False).first()
    if doctor:
        return doctor, None
    
    return _create_api_doctor()


def _create_api_doctor():
    """Create a new API doctor record."""
    doctor = Doctor(
        identifierCode='API001',
        firstName='API',
        lastName1='Doctor',
        lastName2='',
        email='api@medsc.com',
        phoneNumber='000-000-0000',
        address='Virtual',
        gender='Otro',
        sex='Prefiero no decir',
        speciality='Medicina General',
        created_by='system',
        updated_by='system'
    )
    try:
        db.session.add(doctor)
        db.session.commit()
        logger.info("API doctor created successfully")
        return doctor, None
    except Exception as e:
        logger.error(f"Error creating API doctor: {str(e)}")
        db.session.rollback()
        fallback = Doctor.query.filter_by(is_deleted=False).first()
        if fallback:
            return fallback, None
        return None, 'Error al crear doctor API y no hay doctores disponibles'


def _create_attention_record(patient, doctor, session_id):
    """Create the main attention record."""
    return Attention(
        date=datetime.now(),
        weight=float(vital_signs_data.get('weight')) if vital_signs_data.get('weight') else None,
        height=float(vital_signs_data.get('height')) if vital_signs_data.get('height') else None,
        temperature=float(vital_signs_data.get('temperature')) if vital_signs_data.get('temperature') else None,
        bloodPressure=vital_signs_data.get('bloodPressure'),
        heartRate=int(vital_signs_data.get('heartRate')) if vital_signs_data.get('heartRate') else None,
        oxygenSaturation=int(vital_signs_data.get('oxygenSaturation')) if vital_signs_data.get('oxygenSaturation') else None,
        breathingFrequency=int(vital_signs_data.get('breathingFrequency')) if vital_signs_data.get('breathingFrequency') else None,
        glucose=float(vital_signs_data.get('glucose')) if vital_signs_data.get('glucose') else None,
        hemoglobin=float(vital_signs_data.get('hemoglobin')) if vital_signs_data.get('hemoglobin') else None,
        reasonConsultation=evaluation_data['reasonConsultation'],
        currentIllness=evaluation_data['currentIllness'],
        evolution=evaluation_data['evolution'],
        idPatient=patient.id,
        idDoctor=doctor.id,
        created_by=session_id,
        updated_by=session_id
    )


def _build_attention_success_response(patient, doctor, attention):
    """Build success response for completed attention."""
    success_msg = f'Atención registrada exitosamente para {patient.firstName} {patient.lastName1}'
    
    if request.is_json:
        return jsonify({
            'success': True,
            'message': success_msg,
            'data': {
                'attention_id': attention.id,
                'patient': {'id': patient.id, 'name': f"{patient.firstName} {patient.lastName1}"},
                'doctor': {'id': doctor.id, 'name': f"Dr. {doctor.firstName} {doctor.lastName1}"},
                'date': attention.date.isoformat()
            }
        })
    
    flash(success_msg, 'success')
    return redirect(url_for('clinic.home'))

# Global lists for temporary storage during attention creation
vital_signs_data = {}
evaluation_data = {}
physical_exams = []
organ_system_reviews = []
diagnostics = []
treatments = []
histopathologies = []
imagings = []
laboratories = []
current_attention_id = None
selected_patient_id = None

@attention.route('/add-vital-signs', methods=['POST'])
def add_vital_signs():
    """Save vital signs data temporarily - API compatible version"""
    global vital_signs_data
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='evaluacion')
    
    try:
        data = _get_request_data()
        vital_signs_data = _parse_vital_signs(data)
        
        success_msg = 'Signos vitales guardados exitosamente.'
        logger.info("Vital signs data saved temporarily")
        
        if request.is_json:
            return _json_success_response(success_msg, vital_signs_data)
        
        flash(success_msg + ' Proceda con la evaluación inicial.', 'success')
        
    except Exception as e:
        logger.error(f"Error saving vital signs: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al guardar signos vitales', 500)
        flash('Error al guardar signos vitales', 'error')
    
    return redirect(redirect_url)

@attention.route('/add-initial-evaluation', methods=['POST'])
def add_initial_evaluation():
    """Save initial evaluation data temporarily - API compatible version"""
    global evaluation_data
    
    # Check authentication
    if not is_authenticated():
        if request.is_json:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            reason_consultation = data.get('reasonConsultation')
            current_illness = data.get('currentIllness')
        else:
            reason_consultation = request.form.get('reasonConsultation')
            current_illness = request.form.get('currentIllness')
        
        # Validate required fields
        if not reason_consultation or not current_illness:
            error_msg = 'Motivo de consulta y enfermedad actual son requeridos'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('clinic.home', view='addAttention', step='evaluacion'))
        
        # Store evaluation data temporarily (these will be part of the Attention record)
        evaluation_data.update({
            'reasonConsultation': reason_consultation.strip(),
            'currentIllness': current_illness.strip()
        })
        
        success_msg = 'Evaluación inicial guardada exitosamente.'
        logger.info("Initial evaluation data saved temporarily")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'data': {
                    'reasonConsultation': evaluation_data['reasonConsultation'],
                    'currentIllness': evaluation_data['currentIllness']
                }
            })
        
        flash(success_msg + ' Proceda con el examen físico.', 'success')
        
    except Exception as e:
        logger.error(f"Error saving initial evaluation: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error al guardar evaluación inicial'}), 500
        flash('Error al guardar evaluación inicial', 'error')
    
    return redirect(url_for('clinic.home', view='addAttention', step='examen'))

@attention.route('/add-physical-exam', methods=['POST'])
def add_physical_exam():
    """Add physical examination to temporary list - API compatible version"""
    global physical_exams
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='examen')
    
    try:
        data = _get_request_data()
        type_examination = data.get('typeExamination')
        examination = data.get('examination')
        
        if not type_examination or not examination:
            error_msg = 'Tipo de examen y hallazgos son requeridos'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        exam_data = {
            'typeExamination': type_examination.strip(),
            'examination': examination.strip()
        }
        
        success_msg, is_new = _add_item_to_list(
            physical_exams, exam_data, 'examen físico',
            'Examen físico agregado exitosamente', 'Este examen ya existe'
        )
        
        if is_new:
            logger.info(f"Physical exam added: {type_examination}")
        
        if request.is_json:
            return _json_success_response(success_msg, {'exam': exam_data, 'total_exams': len(physical_exams)})
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding physical exam: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar examen físico', 500)
        flash('Error al agregar examen físico', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-physical-exam', methods=['POST'])
def remove_physical_exam():
    """Remove physical examination from temporary list - API compatible version"""
    global physical_exams
    
    redirect_url = url_for('clinic.home', view='addAttention', step='examen')
    
    try:
        data = _get_request_data()
        exam_id = data.get('exam_id')
        index = data.get('index', -1)
        
        _, removed = _remove_item_from_list(physical_exams, exam_id, index)
        
        if removed:
            if request.is_json:
                return _json_success_response('Examen físico eliminado exitosamente', {'total_exams': len(physical_exams)})
            flash('Examen físico eliminado exitosamente', 'success')
        else:
            if request.is_json:
                return _json_error_response('Examen no encontrado', 404)
            flash('Examen no encontrado', 'error')
            
    except Exception as e:
        logger.error(f"Error removing physical exam: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al eliminar examen', 500)
        flash('Error al eliminar examen', 'error')
    
    return redirect(redirect_url)

@attention.route('/add-organ-system-review', methods=['POST', 'OPTIONS'])
def add_organ_system_review():
    """Add organ system review to temporary list - API compatible version"""
    global organ_system_reviews
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='revision')
    
    try:
        data = _get_request_data()
        type_review = data.get('typeReview')
        review = data.get('review')
        
        if not type_review or not review:
            error_msg = 'Tipo de revisión y hallazgos son requeridos'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        review_data = {
            'typeReview': type_review.strip(),
            'review': review.strip()
        }
        
        success_msg, is_new = _add_item_to_list(
            organ_system_reviews, review_data, 'revisión',
            'Revisión de sistema agregada', 'Esta revisión ya existe'
        )
        
        logger.info(f"Organ system review added: {type_review}")
        
        if request.is_json:
            return _json_success_response(success_msg, review_data)
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding organ system review: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar revisión de sistema', 500)
        flash('Error al agregar revisión de sistema', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-organ-system-review', methods=['POST', 'OPTIONS'])
def remove_organ_system_review():
    """Remove organ system review from temporary list - API compatible version"""
    global organ_system_reviews
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response

    redirect_url = url_for('clinic.home', view='addAttention', step='revision')
    return _remove_item_from_list(
        organ_system_reviews, redirect_url,
        'Revisión de sistema eliminada', 'Revisión no encontrada',
        'Error al eliminar revisión'
    )

@attention.route('/add-diagnostic', methods=['POST'])
def add_diagnostic():
    """Add diagnostic to temporary list - API compatible version"""
    global diagnostics
    
    # Check authentication
    if not is_authenticated():
        if request.is_json:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            cie10_code = data.get('cie10Code')
            disease = data.get('disease')
            observations = data.get('observations')
            diagnostic_condition = data.get('diagnosticCondition')
            chronology = data.get('chronology')
        else:
            cie10_code = request.form.get('cie10Code')
            disease = request.form.get('disease')
            observations = request.form.get('observations')
            diagnostic_condition = request.form.get('diagnosticCondition')
            chronology = request.form.get('chronology')
        
        if not all([cie10_code, disease, observations, diagnostic_condition, chronology]):
            error_msg = 'Todos los campos del diagnóstico son requeridos'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('clinic.home', view='addAttention', step='diagnostico'))
        
        diagnostic_data = {
            'cie10Code': cie10_code.strip(),
            'disease': disease.strip(),
            'observations': observations.strip(),
            'diagnosticCondition': diagnostic_condition.strip(),
            'chronology': chronology.strip()
        }
        
        if diagnostic_data not in diagnostics:
            diagnostics.append(diagnostic_data)
            success_msg = 'Diagnóstico agregado exitosamente'
            logger.info(f"Diagnostic added: {cie10_code} - {disease}")
        else:
            success_msg = 'Este diagnóstico ya existe'
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'data': {
                    'diagnostic': diagnostic_data,
                    'total_diagnostics': len(diagnostics)
                }
            })
        
        flash(success_msg, 'success' if diagnostic_data not in diagnostics[:-1] else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding diagnostic: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error al agregar diagnóstico'}), 500
        flash('Error al agregar diagnóstico', 'error')
    
    return redirect(url_for('clinic.home', view='addAttention', step='diagnostico'))

@attention.route('/remove-diagnostic', methods=['POST'])
def remove_diagnostic():
    """Remove diagnostic from temporary list"""
    global diagnostics
    
    try:
        index = int(request.form.get('index', -1))
        if 0 <= index < len(diagnostics):
            removed_item = diagnostics.pop(index)
            flash('Diagnóstico eliminado', 'success')
        else:
            flash('Diagnóstico no encontrado', 'error')
    except Exception as e:
        logger.error(f"Error removing diagnostic: {str(e)}")
        flash('Error al eliminar diagnóstico', 'error')
    
    return redirect(url_for('clinic.home', view='addAttention', step='diagnostico'))

@attention.route('/add-treatment', methods=['POST', 'OPTIONS'])
def add_treatment():
    """Add treatment to temporary list - API compatible version"""
    global treatments
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='tratamiento')
    
    try:
        data = _get_request_data()
        medicament = data.get('medicament')
        via = data.get('via')
        dosage = data.get('dosage')
        unity = data.get('unity')
        frequency = data.get('frequency')
        indications = data.get('indications')
        warning = data.get('warning')
        
        if not all([medicament, via, dosage, unity, frequency, indications]):
            error_msg = 'Todos los campos requeridos del tratamiento deben completarse'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        treatment_data = {
            'medicament': medicament.strip(),
            'via': via.strip(),
            'dosage': dosage.strip(),
            'unity': unity.strip(),
            'frequency': frequency.strip(),
            'indications': indications.strip(),
            'warning': warning.strip() if warning else None
        }
        
        success_msg, is_new = _add_item_to_list(
            treatments, treatment_data, 'tratamiento',
            'Tratamiento agregado', 'Este tratamiento ya existe'
        )
        
        logger.info(f"Treatment added: {medicament}")
        
        if request.is_json:
            return _json_success_response(success_msg, treatment_data)
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding treatment: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar tratamiento', 500)
        flash('Error al agregar tratamiento', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-treatment', methods=['POST', 'OPTIONS'])
def remove_treatment():
    """Remove treatment from temporary list - API compatible version"""
    global treatments
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response

    redirect_url = url_for('clinic.home', view='addAttention', step='tratamiento')
    return _remove_item_from_list(
        treatments, redirect_url,
        'Tratamiento eliminado', 'Tratamiento no encontrado',
        'Error al eliminar tratamiento'
    )

@attention.route('/add-histopathology', methods=['POST', 'OPTIONS'])
def add_histopathology():
    """Add histopathology to temporary list - API compatible version"""
    global histopathologies
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    
    try:
        data = _get_request_data()
        histopathology = data.get('histopathology')
        
        if not histopathology or not histopathology.strip():
            error_msg = 'El resultado histopatológico es requerido'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        histo_data = {'histopathology': histopathology.strip()}
        
        success_msg, is_new = _add_item_to_list(
            histopathologies, histo_data, 'histopatología',
            'Histopatología agregada', 'Esta histopatología ya existe'
        )
        
        logger.info("Histopathology added")
        
        if request.is_json:
            return _json_success_response(success_msg, histo_data)
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding histopathology: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar histopatología', 500)
        flash('Error al agregar histopatología', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-histopathology', methods=['POST', 'OPTIONS'])
def remove_histopathology():
    """Remove histopathology from temporary list - API compatible version"""
    global histopathologies
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response

    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    return _remove_item_from_list(
        histopathologies, redirect_url,
        'Histopatología eliminada', 'Histopatología no encontrada',
        'Error al eliminar histopatología'
    )

@attention.route('/add-imaging', methods=['POST', 'OPTIONS'])
def add_imaging():
    """Add imaging to temporary list - API compatible version"""
    global imagings
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    
    try:
        data = _get_request_data()
        type_imaging = data.get('typeImaging')
        imaging = data.get('imaging')
        
        if not type_imaging or not imaging:
            error_msg = 'Tipo de imagen y resultado son requeridos'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        imaging_data = {
            'typeImaging': type_imaging.strip(),
            'imaging': imaging.strip()
        }
        
        success_msg, is_new = _add_item_to_list(
            imagings, imaging_data, 'imagen',
            'Imagen agregada', 'Esta imagen ya existe'
        )
        
        logger.info(f"Imaging added: {type_imaging}")
        
        if request.is_json:
            return _json_success_response(success_msg, imaging_data)
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding imaging: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar imagen', 500)
        flash('Error al agregar imagen', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-imaging', methods=['POST', 'OPTIONS'])
def remove_imaging():
    """Remove imaging from temporary list - API compatible version"""
    global imagings
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response

    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    return _remove_item_from_list(
        imagings, redirect_url,
        'Imagen eliminada', 'Imagen no encontrada',
        'Error al eliminar imagen'
    )

@attention.route('/add-laboratory', methods=['POST', 'OPTIONS'])
def add_laboratory():
    """Add laboratory to temporary list - API compatible version"""
    global laboratories
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    
    try:
        data = _get_request_data()
        type_exam = data.get('typeExam')
        exam = data.get('exam')
        
        if not type_exam or not exam:
            error_msg = 'Tipo de examen y resultado son requeridos'
            if request.is_json:
                return _json_error_response(error_msg, 400)
            flash(error_msg, 'error')
            return redirect(redirect_url)
        
        lab_data = {
            'typeExam': type_exam.strip(),
            'exam': exam.strip()
        }
        
        success_msg, is_new = _add_item_to_list(
            laboratories, lab_data, 'laboratorio',
            'Laboratorio agregado', 'Este laboratorio ya existe'
        )
        
        logger.info(f"Laboratory added: {type_exam}")
        
        if request.is_json:
            return _json_success_response(success_msg, lab_data)
        
        flash(success_msg, 'success' if is_new else 'warning')
        
    except Exception as e:
        logger.error(f"Error adding laboratory: {str(e)}")
        if request.is_json:
            return _json_error_response('Error al agregar laboratorio', 500)
        flash('Error al agregar laboratorio', 'error')
    
    return redirect(redirect_url)

@attention.route('/remove-laboratory', methods=['POST', 'OPTIONS'])
def remove_laboratory():
    """Remove laboratory from temporary list - API compatible version"""
    global laboratories
    
    cors_response = handle_cors_preflight()
    if cors_response:
        return cors_response

    redirect_url = url_for('clinic.home', view='addAttention', step='examenes')
    return _remove_item_from_list(
        laboratories, redirect_url,
        'Laboratorio eliminado', 'Laboratorio no encontrado',
        'Error al eliminar laboratorio'
    )

@attention.route('/continue-to-organ-systems', methods=['POST'])
def continue_to_organ_systems():
    """Continue to organ systems review step"""
    flash('Continúe con la revisión de órganos y sistemas.', 'info')
    return redirect(url_for('clinic.home', view='addAttention', step='revision'))

@attention.route('/continue-to-diagnostics', methods=['POST'])
def continue_to_diagnostics():
    """Continue to diagnostics step"""
    flash('Continúe con los diagnósticos.', 'info')
    return redirect(url_for('clinic.home', view='addAttention', step='diagnostico'))

@attention.route('/continue-to-treatments', methods=['POST'])
def continue_to_treatments():
    """Continue to treatments step"""
    flash('Continúe con los tratamientos.', 'info')
    return redirect(url_for('clinic.home', view='addAttention', step='tratamiento'))

@attention.route('/continue-to-extra-exams', methods=['POST'])
def continue_to_extra_exams():
    """Continue to extra exams step"""
    flash('Continúe con los exámenes extras.', 'info')
    return redirect(url_for('clinic.home', view='addAttention', step='examenes'))

@attention.route('/continue-to-evolution', methods=['POST'])
def continue_to_evolution():
    """Continue to evolution step"""
    flash('Continúe con la evolución del paciente.', 'info')
    return redirect(url_for('clinic.home', view='addAttention', step='evolucion'))

@attention.route('/add-evolution', methods=['POST'])
def add_evolution():
    """Save evolution data temporarily - this is the final step - API compatible version"""
    global evaluation_data
    
    # Check authentication
    if not is_authenticated():
        if request.is_json:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            evolution = data.get('evolution')
        else:
            evolution = request.form.get('evolution')
        
        if not evolution or not evolution.strip():
            error_msg = 'La evolución es requerida'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('clinic.home', view='addAttention', step='evolucion'))
        
        # Store evolution data temporarily (this will be part of the Attention record)
        evaluation_data['evolution'] = evolution.strip()
        
        success_msg = 'Evolución guardada exitosamente'
        logger.info("Evolution data saved temporarily")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'data': {
                    'evolution': evaluation_data['evolution']
                }
            })
        
        flash(success_msg + '. ¡Ya puede finalizar la atención!', 'success')
        
    except Exception as e:
        logger.error(f"Error saving evolution: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error al guardar evolución'}), 500
        flash('Error al guardar evolución', 'error')
    
    return redirect(url_for('clinic.home', view='addAttention', step='evolucion'))

@attention.route('/select-patient-for-attention', methods=['POST'])
def select_patient_for_attention():
    """Select patient for current attention - API compatible version"""
    global selected_patient_id
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention')
    
    try:
        data = _get_request_data()
        patient_id = data.get('patient_id') or data.get('selectedPatient') or data.get('preselect_patient')
        
        if not patient_id:
            return _handle_error('Debe seleccionar un paciente', redirect_url, 400)
        
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return _handle_error('Paciente no encontrado', redirect_url, 404)
        
        selected_patient_id = int(patient_id)
        logger.info(f"Patient {patient_id} selected for attention")
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'message': f'Paciente {patient.firstName} {patient.lastName1} seleccionado.',
                'data': {
                    'patient_id': patient.id,
                    'patient_name': f"{patient.firstName} {patient.lastName1}",
                    'identifier_code': patient.identifierCode
                }
            })
        
        flash(f'Paciente {patient.firstName} {patient.lastName1} seleccionado. Puede proceder con los signos vitales.', 'success')
        
    except Exception as e:
        logger.error(f"Error selecting patient: {str(e)}")
        return _handle_error('Error al seleccionar paciente', redirect_url, 500)
    
    return redirect(redirect_url)

@attention.route('/change-selected-patient', methods=['POST'])
def change_selected_patient():
    """Change selected patient for attention"""
    global selected_patient_id
    
    # Clear selected patient
    selected_patient_id = None
    flash('Selección de paciente cancelada. Seleccione un nuevo paciente', 'info')
    
    return redirect(url_for('clinic.home', view='addAttention'))

@attention.route('/complete-attention', methods=['POST'])
def complete_attention():
    """Save all attention data to database - API compatible version"""
    global current_attention_id, selected_patient_id
    
    auth_response = _check_auth_and_redirect()
    if auth_response:
        return auth_response
    
    redirect_url = url_for('clinic.home', view='addAttention')
    doctor_info, sessionID = get_doctor_info_and_session()
    
    logger.info(f"Complete attention - sessionID: {sessionID}, selected_patient_id: {selected_patient_id}")
    
    # Validate prerequisites
    validation_error = _validate_attention_prerequisites(redirect_url)
    if validation_error:
        return validation_error
    
    try:
        # Get doctor
        doctor, error = _get_or_create_doctor(sessionID)
        if error:
            return _handle_error(error, redirect_url, 500 if 'crear' in error else 404)
        
        logger.info(f"Using doctor: ID={doctor.id}, Name={doctor.firstName} {doctor.lastName1}")
        
        # Get patient
        patient = Patient.query.filter_by(id=selected_patient_id, is_deleted=False).first()
        if not patient:
            return _handle_error('Paciente seleccionado no encontrado', redirect_url, 404)
        
        logger.info(f"Using patient: ID={patient.id}, Name={patient.firstName} {patient.lastName1}")
        
        # Create and save attention
        new_attention = _create_attention_record(patient, doctor, sessionID)
        db.session.add(new_attention)
        db.session.commit()
        
        current_attention_id = new_attention.id
        logger.info(f"Attention created with ID: {new_attention.id}")
        
        # Save related data
        _save_attention_related_data(new_attention.id, sessionID)
        logger.info(f"Attention completed for patient {patient.id} by doctor {doctor.id}")
        
        # Clear temporary data
        _clear_temp_attention_data()
        
        return _build_attention_success_response(patient, doctor, new_attention)
        
    except ValueError as ve:
        db.session.rollback()
        logger.error(f"Value error: {str(ve)}")
        return _handle_error('Error en los datos numéricos ingresados. Verifique los signos vitales.', redirect_url, 400)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error completing attention: {str(e)}")
        return _handle_error('Error al completar la atención', redirect_url, 500)

def _save_attention_related_data(attention_id, session_id):
    """Helper function to save all related attention data"""
    try:
        # Save physical examinations
        for exam_data in physical_exams:
            new_exam = RegionalPhysicalExamination(
                typeExamination=exam_data['typeExamination'],
                examination=exam_data['examination'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_exam)
        
        # Save organ system reviews
        for review_data in organ_system_reviews:
            new_review = ReviewOrgansSystem(
                typeReview=review_data['typeReview'],
                review=review_data['review'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_review)
        
        # Save diagnostics
        for diagnostic_data in diagnostics:
            new_diagnostic = Diagnostic(
                cie10Code=diagnostic_data['cie10Code'],
                disease=diagnostic_data['disease'],
                observations=diagnostic_data['observations'],
                diagnosticCondition=diagnostic_data['diagnosticCondition'],
                chronology=diagnostic_data['chronology'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_diagnostic)
        
        # Save treatments
        for treatment_data in treatments:
            new_treatment = Treatment(
                medicament=treatment_data['medicament'],
                via=treatment_data['via'],
                dosage=treatment_data['dosage'],
                unity=treatment_data['unity'],
                frequency=treatment_data['frequency'],
                indications=treatment_data['indications'],
                warning=treatment_data['warning'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_treatment)
        
        # Save histopathologies
        for histo_data in histopathologies:
            new_histo = Histopathology(
                histopathology=histo_data['histopathology'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_histo)
        
        # Save imagings
        for imaging_data in imagings:
            new_imaging = Imaging(
                typeImaging=imaging_data['typeImaging'],
                imaging=imaging_data['imaging'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_imaging)
        
        # Save laboratories
        for lab_data in laboratories:
            new_lab = Laboratory(
                typeExam=lab_data['typeExam'],
                exam=lab_data['exam'],
                idAttention=attention_id,
                created_by=session_id,
                updated_by=session_id
            )
            db.session.add(new_lab)
        
        db.session.commit()
        logger.info(f"All related data saved for attention {attention_id}")
        
    except Exception as e:
        logger.error(f"Error saving related attention data: {str(e)}")
        raise e

def _clear_temp_attention_data():
    """Clear all temporary attention data"""
    global vital_signs_data, evaluation_data, physical_exams, organ_system_reviews
    global diagnostics, treatments, histopathologies, imagings, laboratories, current_attention_id
    global selected_patient_id
    
    vital_signs_data.clear()
    evaluation_data.clear()
    physical_exams.clear()
    organ_system_reviews.clear()
    diagnostics.clear()
    treatments.clear()
    histopathologies.clear()
    imagings.clear()
    laboratories.clear()
    current_attention_id = None
    selected_patient_id = None

@attention.route('/reset-attention-session', methods=['POST'])
def reset_attention_session():
    """Reset attention session when entering add attention view"""
    _clear_temp_attention_data()
    flash('Nueva sesión de atención iniciada', 'info')
    return redirect(url_for('clinic.home', view='addAttention'))

@attention.route('/clear-temp-attention-data', methods=['POST'])
def clear_temp_attention_data():
    """Clear all temporary attention data"""
    _clear_temp_attention_data()
    flash('Datos temporales de atención limpiados', 'info')
    return redirect(url_for('clinic.home', view='addAttention'))

@attention.route('/get-patients', methods=['GET'])
def get_patients():
    """Get all patients for selection in forms"""
    try:
        patients = Patient.query.filter_by(is_deleted=False).all()
        patient_list = []
        for patient in patients:
            patient_list.append({
                'id': patient.id,
                'name': f"{patient.firstName} {patient.lastName1}",
                'identifierCode': patient.identifierCode
            })
        return jsonify({'patients': patient_list})
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        return jsonify({'error': 'Error al obtener pacientes'}), 500

@attention.route('/get-doctors', methods=['GET'])
def get_doctors():
    """Get all doctors for selection in forms"""
    try:
        doctors = Doctor.query.filter_by(is_deleted=False).all()
        doctor_list = []
        for doctor in doctors:
            doctor_list.append({
                'id': doctor.id,
                'name': f"Dr. {doctor.firstName} {doctor.lastName1}",
                'speciality': doctor.speciality
            })
        return jsonify({'doctors': doctor_list})
    except Exception as e:
        logger.error(f"Error getting doctors: {str(e)}")
        return jsonify({'error': 'Error al obtener doctores'}), 500




@attention.route('/get-attention-for-patient', methods=['POST'])
def get_attention_for_patient():
    """Select patient for current attention"""
    global selected_patient_id
    
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    try:
        patient_id = request.form.get('selectedPatient')
        
        if not patient_id:
            flash('Debe seleccionar un paciente', 'error')
            return redirect(url_for('clinic.home', view='attentionHsitory'))
        
        # Validate that patient exists
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('clinic.home', view='attentionHsitory'))
        
        selected_patient_id = int(patient_id)
        flash(f'Paciente {patient.firstName} {patient.lastName1} seleccionado. Puede proceder con los signos vitales.', 'success')
        logger.info(f"Patient {patient_id} selected for attention")
        
    except Exception as e:
        logger.error(f"Error selecting patient: {str(e)}")
        flash('Error al seleccionar paciente', 'error')
    return redirect(url_for('clinic.home', view='attentionHistory'))

@attention.route('/view/<int:attention_id>', methods=['GET'])
def view(attention_id):
    """Show details for a specific attention record"""
    try:
        attention_record = Attention.query.filter_by(id=attention_id).first()
        if not attention_record:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Atención no encontrada'}), 404
            flash('Atención no encontrada', 'error')
            return redirect(url_for('clinic.home', view='attentionHistory'))

        patient = Patient.query.filter_by(id=attention_record.idPatient, is_deleted=False).first()
        doctor = Doctor.query.filter_by(id=attention_record.idDoctor, is_deleted=False).first()

        # Get related data
        physical_exams = RegionalPhysicalExamination.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        organ_reviews = ReviewOrgansSystem.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        diagnostics = Diagnostic.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        treatments = Treatment.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        histopathologies = Histopathology.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        imagings = Imaging.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        laboratories = Laboratory.query.filter_by(idAttention=attention_id, is_deleted=False).all()

        # If it's an API request, return JSON
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'data': {
                    'attention': {
                        'id': attention_record.id,
                        'date': attention_record.date.isoformat() if attention_record.date else None,
                        'reasonConsultation': attention_record.reasonConsultation,
                        'currentIllness': attention_record.currentIllness,
                        'evolution': attention_record.evolution,
                        'weight': attention_record.weight,
                        'height': attention_record.height,
                        'temperature': attention_record.temperature,
                        'bloodPressure': attention_record.bloodPressure,
                        'heartRate': attention_record.heartRate,
                        'oxygenSaturation': attention_record.oxygenSaturation,
                        'breathingFrequency': attention_record.breathingFrequency,
                        'glucose': attention_record.glucose,
                        'hemoglobin': attention_record.hemoglobin
                    },
                    'patient': {
                        'id': patient.id,
                        'firstName': patient.firstName,
                        'lastName1': patient.lastName1,
                        'identifierCode': patient.identifierCode
                    } if patient else None,
                    'doctor': {
                        'id': doctor.id,
                        'firstName': doctor.firstName,
                        'lastName1': doctor.lastName1,
                        'speciality': doctor.speciality
                    } if doctor else None,
                    'physicalExams': [
                        {
                            'id': exam.id,
                            'typeExamination': exam.typeExamination,
                            'examination': exam.examination
                        } for exam in physical_exams
                    ],
                    'organReviews': [
                        {
                            'id': review.id,
                            'typeReview': review.typeReview,
                            'review': review.review
                        } for review in organ_reviews
                    ],
                    'diagnostics': [
                        {
                            'id': diag.id,
                            'cie10Code': diag.cie10Code,
                            'disease': diag.disease,
                            'observations': diag.observations,
                            'diagnosticCondition': diag.diagnosticCondition,
                            'chronology': diag.chronology
                        } for diag in diagnostics
                    ],
                    'treatments': [
                        {
                            'id': treat.id,
                            'medicament': treat.medicament,
                            'via': treat.via,
                            'dosage': treat.dosage,
                            'unity': treat.unity,
                            'frequency': treat.frequency,
                            'indications': treat.indications,
                            'warning': treat.warning
                        } for treat in treatments
                    ],
                    'histopathologies': [
                        {
                            'id': histo.id,
                            'histopathology': histo.histopathology
                        } for histo in histopathologies
                    ],
                    'imagings': [
                        {
                            'id': img.id,
                            'typeImaging': img.typeImaging,
                            'imaging': img.imaging
                        } for img in imagings
                    ],
                    'laboratories': [
                        {
                            'id': lab.id,
                            'typeExam': lab.typeExam,
                            'exam': lab.exam
                        } for lab in laboratories
                    ]
                }
            })

        # Regular template rendering for web interface
        return render_template(
            'attention_detail.html',
            attention=attention_record,
            patient=patient,
            doctor=doctor,
            physical_exams=physical_exams,
            organ_reviews=organ_reviews,
            diagnostics=diagnostics,
            treatments=treatments,
            histopathologies=histopathologies,
            imagings=imagings,
            laboratories=laboratories
        )
        
    except Exception as e:
        logger.error(f"Error viewing attention {attention_id}: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
        flash('Error al cargar los detalles de la atención', 'error')
        return redirect(url_for('clinic.home', view='attentionHistory'))


@attention.route('/api/session-data', methods=['GET'])
def get_session_data():
    """Get current session data for attention creation"""
    try:
        global selected_patient_id, vital_signs_data, evaluation_data
        global physical_exams, organ_system_reviews, diagnostics, treatments
        global histopathologies, imagings, laboratories
        
        patient_info = None
        if selected_patient_id:
            patient = Patient.query.filter_by(id=selected_patient_id, is_deleted=False).first()
            if patient:
                patient_info = {
                    'id': patient.id,
                    'name': f"{patient.firstName} {patient.lastName1}",
                    'identifierCode': patient.identifierCode,
                    'firstName': patient.firstName,
                    'lastName1': patient.lastName1
                }
        
        return jsonify({
            'success': True,
            'data': {
                'selectedPatient': patient_info,
                'vitalSigns': vital_signs_data,
                'evaluation': evaluation_data,
                'physicalExams': physical_exams,
                'organSystemReviews': organ_system_reviews,
                'diagnostics': diagnostics,
                'treatments': treatments,
                'histopathologies': histopathologies,
                'imagings': imagings,
                'laboratories': laboratories
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session data: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener datos de sesión'}), 500

def get_all_attentions():
    """Get all attentions with pagination and filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Base query
        query = Attention.query.filter_by(is_deleted=False)
        
        # Apply filters
        if patient_id:
            query = query.filter(Attention.idPatient == patient_id)
        if doctor_id:
            query = query.filter(Attention.idDoctor == doctor_id)
        if date_from:
            query = query.filter(Attention.date >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(Attention.date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        # Order by date descending
        query = query.order_by(Attention.date.desc())
        
        # Paginate
        paginated_attentions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        attentions_data = []
        for attention in paginated_attentions.items:
            patient = Patient.query.filter_by(id=attention.idPatient).first()
            doctor = Doctor.query.filter_by(id=attention.idDoctor).first()
            
            attentions_data.append({
                'id': attention.id,
                'date': attention.date.isoformat() if attention.date else None,
                'reasonConsultation': attention.reasonConsultation,
                'currentIllness': attention.currentIllness,
                'patient': {
                    'id': patient.id,
                    'name': f"{patient.firstName} {patient.lastName1}",
                    'identifierCode': patient.identifierCode
                } if patient else None,
                'doctor': {
                    'id': doctor.id,
                    'name': f"Dr. {doctor.firstName} {doctor.lastName1}",
                    'speciality': doctor.speciality
                } if doctor else None
            })
        
        return jsonify({
            'success': True,
            'data': attentions_data,
            'pagination': {
                'page': paginated_attentions.page,
                'pages': paginated_attentions.pages,
                'per_page': paginated_attentions.per_page,
                'total': paginated_attentions.total,
                'has_next': paginated_attentions.has_next,
                'has_prev': paginated_attentions.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting attentions: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener atenciones'}), 500


@attention.route('/api/attentions/patient/<int:patient_id>', methods=['GET'])
def get_patient_attentions(patient_id):
    """Get all attentions for a specific patient"""
    try:
        # Validate patient exists
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        attentions = Attention.query.filter_by(
            idPatient=patient_id, is_deleted=False
        ).order_by(Attention.date.desc()).all()
        
        attentions_data = []
        for attention in attentions:
            doctor = Doctor.query.filter_by(id=attention.idDoctor).first()
            diagnostics = Diagnostic.query.filter_by(
                idAttention=attention.id, is_deleted=False
            ).all()

            attentions_data.append({
                'id': attention.id,
                'date': attention.date.isoformat() if attention.date else None,
                'reasonConsultation': attention.reasonConsultation,
                'currentIllness': attention.currentIllness,
                'evolution': attention.evolution,
                'doctor': {
                    'id': doctor.id,
                    'name': f"Dr. {doctor.firstName} {doctor.lastName1}",
                    'speciality': doctor.speciality
                } if doctor else None,
                'vitalSigns': {
                    'weight': attention.weight,
                    'height': attention.height,
                    'temperature': attention.temperature,
                    'bloodPressure': attention.bloodPressure,
                    'heartRate': attention.heartRate,
                    'oxygenSaturation': attention.oxygenSaturation,
                    'breathingFrequency': attention.breathingFrequency,
                    'glucose': attention.glucose,
                    'hemoglobin': attention.hemoglobin
                },
                'diagnostics': [
                    {
                        'cie10Code': d.cie10Code,
                        'disease': d.disease,
                        'diagnosticCondition': d.diagnosticCondition
                    } for d in diagnostics
                ]
            })
        
        return jsonify({
            'success': True,
            'data': {
                'patient': {
                    'id': patient.id,
                    'name': f"{patient.firstName} {patient.lastName1}",
                    'identifierCode': patient.identifierCode
                },
                'attentions': attentions_data,
                'total': len(attentions_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting patient attentions: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener atenciones del paciente'}), 500



@attention.route('/api/clear-session', methods=['POST'])
def clear_session_data():
    """Clear all session data for attention creation"""
    try:
        _clear_temp_attention_data()
        
        return jsonify({
            'success': True,
            'message': 'Datos de sesión limpiados exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error clearing session data: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al limpiar datos de sesión'}), 500


# Additional utility endpoints
@attention.route('/api/statistics', methods=['GET'])
def get_attention_statistics():
    """Get attention statistics for dashboard"""
    try:
        # Total attentions
        total_attentions = Attention.query.filter_by(is_deleted=False).count()
        
        # Attentions today
        today = datetime.now().date()
        attentions_today = Attention.query.filter(
            Attention.date >= today,
            Attention.date < today + timedelta(days=1),
            Attention.is_deleted == False
        ).count()
        
        # Attentions this month
        month_start = datetime.now().replace(day=1).date()
        attentions_this_month = Attention.query.filter(
            Attention.date >= month_start,
            Attention.is_deleted == False
        ).count()
        
        # Most active doctors (top 5)
        from sqlalchemy import func
        top_doctors = db.session.query(
            Doctor.firstName,
            Doctor.lastName1,
            func.count(Attention.id).label('attention_count')
        ).join(Attention).filter(
            Attention.is_deleted == False,
            Doctor.is_deleted == False
        ).group_by(Doctor.id).order_by(
            func.count(Attention.id).desc()
        ).limit(5).all()
        
        # Most common diagnoses (top 10)
        top_diagnoses = db.session.query(
            Diagnostic.disease,
            func.count(Diagnostic.id).label('diagnosis_count')
        ).join(Attention).filter(
            Attention.is_deleted == False,
            Diagnostic.is_deleted == False
        ).group_by(Diagnostic.disease).order_by(
            func.count(Diagnostic.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'totalAttentions': total_attentions,
                'attentionsToday': attentions_today,
                'attentionsThisMonth': attentions_this_month,
                'topDoctors': [
                    {
                        'name': f"Dr. {doctor.firstName} {doctor.lastName1}",
                        'attentionCount': doctor.attention_count
                    } for doctor in top_doctors
                ],
                'topDiagnoses': [
                    {
                        'disease': diag.disease,
                        'count': diag.diagnosis_count
                    } for diag in top_diagnoses
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting attention statistics: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener estadísticas'}), 500


@attention.route('/api/search', methods=['GET'])
def search_attentions():
    """Search attentions by patient name, doctor name, or diagnosis"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'}), 400
        
        # Search in multiple fields
        search_filter = f"%{query}%"
        
        attentions = db.session.query(Attention).join(Patient).join(Doctor).outerjoin(Diagnostic).filter(
            Attention.is_deleted == False,
            db.or_(
                Patient.firstName.ilike(search_filter),
                Patient.lastName1.ilike(search_filter),
                Doctor.firstName.ilike(search_filter),
                Doctor.lastName1.ilike(search_filter),
                Attention.reasonConsultation.ilike(search_filter),
                Attention.currentIllness.ilike(search_filter),
                Diagnostic.disease.ilike(search_filter)
            )
        ).distinct().order_by(Attention.date.desc()).limit(20).all()
        
        results = []
        for attention in attentions:
            patient = Patient.query.filter_by(id=attention.idPatient).first()
            doctor = Doctor.query.filter_by(id=attention.idDoctor).first()
            
            results.append({
                'id': attention.id,
                'date': attention.date.isoformat() if attention.date else None,
                'reasonConsultation': attention.reasonConsultation,
                'patient': {
                    'id': patient.id,
                    'name': f"{patient.firstName} {patient.lastName1}",
                    'identifierCode': patient.identifierCode
                } if patient else None,
                'doctor': {
                    'id': doctor.id,
                    'name': f"Dr. {doctor.firstName} {doctor.lastName1}"
                } if doctor else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching attentions: {str(e)}")
        return jsonify({'success': False, 'error': 'Error en la búsqueda'}), 500


@attention.route('/api/export/<int:attention_id>', methods=['GET'])
def export_attention(attention_id):
    """Export attention data in JSON format for external use"""
    try:
        attention = Attention.query.filter_by(id=attention_id, is_deleted=False).first()
        if not attention:
            return jsonify({'success': False, 'error': 'Atención no encontrada'}), 404
        
        patient = Patient.query.filter_by(id=attention.idPatient).first()
        doctor = Doctor.query.filter_by(id=attention.idDoctor).first()
        
        # Get all related data
        physical_exams = RegionalPhysicalExamination.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        organ_reviews = ReviewOrgansSystem.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        diagnostics = Diagnostic.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        treatments = Treatment.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        histopathologies = Histopathology.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        imagings = Imaging.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        laboratories = Laboratory.query.filter_by(idAttention=attention_id, is_deleted=False).all()
        
        export_data = {
            'metadata': {
                'exportDate': datetime.now().isoformat(),
                'version': '1.0',
                'system': 'MEDSC'
            },
            'attention': {
                'id': attention.id,
                'date': attention.date.isoformat() if attention.date else None,
                'reasonConsultation': attention.reasonConsultation,
                'currentIllness': attention.currentIllness,
                'evolution': attention.evolution,
                'vitalSigns': {
                    'weight': attention.weight,
                    'height': attention.height,
                    'temperature': attention.temperature,
                    'bloodPressure': attention.bloodPressure,
                    'heartRate': attention.heartRate,
                    'oxygenSaturation': attention.oxygenSaturation,
                    'breathingFrequency': attention.breathingFrequency,
                    'glucose': attention.glucose,
                    'hemoglobin': attention.hemoglobin
                }
            },
            'patient': {
                'id': patient.id,
                'firstName': patient.firstName,
                'lastName1': patient.lastName1,
                'identifierCode': patient.identifierCode,
                'birthDate': patient.birthDate.isoformat() if hasattr(patient, 'birthDate') and patient.birthDate else None,
                'gender': getattr(patient, 'gender', None)
            } if patient else None,
            'doctor': {
                'id': doctor.id,
                'firstName': doctor.firstName,
                'lastName1': doctor.lastName1,
                'speciality': doctor.speciality
            } if doctor else None,
            'clinicalData': {
                'physicalExams': [
                    {
                        'typeExamination': exam.typeExamination,
                        'examination': exam.examination
                    } for exam in physical_exams
                ],
                'organSystemReviews': [
                    {
                        'typeReview': review.typeReview,
                        'review': review.review
                    } for review in organ_reviews
                ],
                'diagnostics': [
                    {
                        'cie10Code': diag.cie10Code,
                        'disease': diag.disease,
                        'observations': diag.observations,
                        'diagnosticCondition': diag.diagnosticCondition,
                        'chronology': diag.chronology
                    } for diag in diagnostics
                ],
                'treatments': [
                    {
                        'medicament': treat.medicament,
                        'via': treat.via,
                        'dosage': treat.dosage,
                        'unity': treat.unity,
                        'frequency': treat.frequency,
                        'indications': treat.indications,
                        'warning': treat.warning
                    } for treat in treatments
                ],
                'labResults': {
                    'histopathologies': [
                        {'result': histo.histopathology} for histo in histopathologies
                    ],
                    'imagings': [
                        {
                            'type': img.typeImaging,
                            'result': img.imaging
                        } for img in imagings
                    ],
                    'laboratories': [
                        {
                            'type': lab.typeExam,
                            'result': lab.exam
                        } for lab in laboratories
                    ]
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        logger.error(f"Error exporting attention {attention_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al exportar atención'}), 500




