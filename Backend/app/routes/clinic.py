from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from models.models_flask import Patient, Doctor, Attention
from utils.db import db
import os

clinic = Blueprint('clinic', __name__)

def check_database_connection():
    """Verifica si hay conexión a la base de datos"""
    try:
        from sqlalchemy import text
        # Intentar hacer una consulta simple
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        return False

@clinic.route('/')
def index():
    session['autenticado'] = False
    return render_template('login.html')

@clinic.route('/home', methods=['GET', 'POST'])
def home():
    view = request.args.get('view', 'home')

    if not session.get('autenticado'):
        return redirect(url_for('login.index'))

    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()

    # Get doctor information from session - Adaptado para Supabase
    doctor_info = None
    if session.get('auth_provider') == 'supabase':
        # Para Supabase, creamos información ficticia del doctor
        email = session.get('email', 'Doctor')
        name_parts = email.split('@')[0].split('.')
        doctor_info = {
            'firstName': name_parts[0].capitalize() if len(name_parts) > 0 else 'Doctor',
            'lastName1': name_parts[1].capitalize() if len(name_parts) > 1 else 'Supabase',
            'speciality': 'Medicina General'
        }
    elif 'cedula' in session and has_database:
        # Código original para login local (solo si hay base de datos)
        try:
            doctor = Doctor.query.filter_by(
                identifierCode=session['cedula'], 
                is_deleted=False
            ).first()
            if doctor:
                doctor_info = {
                    'firstName': doctor.firstName,
                    'lastName1': doctor.lastName1,
                    'speciality': doctor.speciality
                }
        except Exception as e:
            doctor_info = None

    # Si no hay base de datos, mostrar mensaje solo para vistas que la requieren (excepto addAttention y attentionHistory)
    if not has_database and view in ['patients', 'addPatient']:
        flash('Esta funcionalidad requiere conexión a la base de datos MySQL. Inicia Docker con: docker-compose up -d db', 'warning')
        return render_template('home.html', view='home', patients=[], doctor_info=doctor_info)
    
    # Manejo de vistas
    if view == 'home':
        if has_database:
            try:
                patients = Patient.query.all()
            except Exception as e:
                patients = []
        else:
            patients = []
        sessionID = session.get('cedula', 'supabase_user')
        return render_template('home.html', view=view, patients=patients, doctor_info=doctor_info)
    
    elif view == 'patients':
        if not has_database:
            flash('Esta funcionalidad requiere conexión a la base de datos MySQL. Inicia Docker con: docker-compose up -d db', 'warning')
            return render_template('home.html', view='home', patients=[], doctor_info=doctor_info)
        
        # New patients list view
        try:
            patients = Patient.query.filter_by(is_deleted=False).order_by(Patient.firstName, Patient.lastName1).all()
            return render_template('home.html', view=view, patients=patients, doctor_info=doctor_info)
        except Exception as e:
            patients = []
            return render_template('home.html', view=view, patients=patients, doctor_info=doctor_info)
    elif view == 'addPatient':
        if not has_database:
            flash('Esta funcionalidad requiere conexión a la base de datos MySQL. Inicia Docker con: docker-compose up -d db', 'warning')
            return render_template('home.html', view='home', patients=[], doctor_info=doctor_info)
        
        sec_view = request.args.get("sec_view", "addPatient")
        if sec_view == 'addPatient':
            return render_template('home.html', view=view, sec_view=sec_view, doctor_info=doctor_info)
        elif sec_view == 'addPatientInfo':
            # Get edit mode and patient ID from request args or session
            edit_mode = request.args.get('edit_mode', 'false') == 'true'
            patient_id = request.args.get('current_patient_id') or session.get('current_patient_id')

            # Check if we have a patient ID
            if not patient_id:
                flash("Error: No hay paciente activo para agregar información adicional.", "error")
                return redirect(url_for('clinic.home', view='addPatient'))

            patient = Patient.query.get(patient_id)
            if not patient:
                flash("Error: El paciente no existe.", "error")
                return redirect(url_for('clinic.home', view='addPatient'))

            # Store in session for consistency
            session['current_patient_id'] = patient.id
            session['edit_mode'] = edit_mode

            # Get related data
            allergies = patient.allergies if patient.allergies else []
            emergencyContacts = patient.emergency_contacts if patient.emergency_contacts else []
            familyBack = patient.family_backgrounds if patient.family_backgrounds else []
            preExistingConditions = patient.pre_existing_conditions if patient.pre_existing_conditions else []

            return render_template(
                'home.html',
                view=view,
                sec_view=sec_view,
                doctor_info=doctor_info,
                edit_mode=edit_mode,
                patient=patient,
                current_patient_id=patient.id,
                allergies=allergies,
                emergencyContacts=emergencyContacts,
                familyBack=familyBack,
                preExistingConditions=preExistingConditions
            )

    elif view == 'addAttention':
        # En modo Supabase, mostrar una versión simplificada
        if not has_database:
            flash('Modo de demostración - Usando datos de ejemplo (requiere MySQL para funcionalidad completa)', 'info')
            # Crear datos de ejemplo para demostración
            available_patients = [
                type('Patient', (), {
                    'id': 1, 
                    'firstName': 'Juan', 
                    'lastName1': 'Pérez', 
                    'identifierCode': '1234567890',
                    'is_deleted': False
                })(),
                type('Patient', (), {
                    'id': 2, 
                    'firstName': 'María', 
                    'lastName1': 'González', 
                    'identifierCode': '0987654321',
                    'is_deleted': False
                })()
            ]
            current_step = request.args.get('step', 'vitales')
            return render_template('home.html', view=view,
                                 available_patients=available_patients,
                                 selected_patient=None,
                                 selected_patient_id=None,
                                 current_step=current_step,
                                 doctor_info=doctor_info,
                                 demo_mode=True)
        
        # Import here to avoid circular imports
        from routes.attention import (
            vital_signs_data, evaluation_data, physical_exams, organ_system_reviews,
            diagnostics, treatments, histopathologies, imagings, laboratories, selected_patient_id
        )
        
        # Only clear attention data when first entering (not when patient is already selected)
        if selected_patient_id is None:
            from routes.attention import _clear_temp_attention_data
            _clear_temp_attention_data()
        
        # Get available patients and selected patient info
        available_patients = Patient.query.filter_by(is_deleted=False).all()
        selected_patient = None
        if selected_patient_id:
            selected_patient = Patient.query.filter_by(id=selected_patient_id, is_deleted=False).first()
        
        # Get current step for navigation
        current_step = request.args.get('step', 'vitales')
        
        return render_template('home.html', view=view,
                             vital_signs_data=vital_signs_data,
                             evaluation_data=evaluation_data,
                             physicalExams=physical_exams,
                             organSystemReviews=organ_system_reviews,
                             diagnostics=diagnostics,
                             treatments=treatments,
                             histopathologies=histopathologies,
                             imagings=imagings,
                             laboratories=laboratories,
                             available_patients=available_patients,
                             selected_patient=selected_patient,
                             selected_patient_id=selected_patient_id,
                             current_step=current_step,
                             doctor_info=doctor_info)
    
        edit_mode = session.get('edit_mode', False)
        return render_template(
        'home.html',
        view=view,
        sec_view=sec_view,
        doctor_info=doctor_info,
        edit_mode=edit_mode,
        patient=patient,
        current_patient_id=patient.id,
        allergies=allergies,
        emergencyContacts=emergencyContacts,
        familyBack=familyBack,
        preExistingConditions=preExistingConditions
)

    elif view == 'attentionHistory':
        # En modo Supabase, mostrar una versión simplificada
        if not has_database:
            flash('Modo de demostración - Usando datos de ejemplo (requiere MySQL para funcionalidad completa)', 'info')
            # Crear datos de ejemplo para demostración
            available_patients = [
                type('Patient', (), {
                    'id': 1, 
                    'firstName': 'Juan', 
                    'lastName1': 'Pérez', 
                    'identifierCode': '1234567890',
                    'is_deleted': False
                })(),
                type('Patient', (), {
                    'id': 2, 
                    'firstName': 'María', 
                    'lastName1': 'González', 
                    'identifierCode': '0987654321',
                    'is_deleted': False
                })()
            ]
            # Crear datos de atención de ejemplo
            attentions = [
                type('Attention', (), {
                    'id': 1,
                    'date': '2025-01-15',
                    'doctor_name': 'Dr. Demo Doctor',
                    'reason': 'Consulta general de ejemplo'
                })()
            ]
            current_step = request.args.get('step', 'vitales')
            return render_template('home.html', view=view,
                                 available_patients=available_patients,
                                 selected_patient=None,
                                 selected_patient_id=None,
                                 attentions=attentions,
                                 current_step=current_step,
                                 doctor_info=doctor_info,
                                 demo_mode=True)
        
        # Import here to avoid circular imports
        from routes.attention import (
            vital_signs_data, evaluation_data, physical_exams, organ_system_reviews,
            diagnostics, treatments, histopathologies, imagings, laboratories, selected_patient_id
        )
        
        # Only clear attention data when first entering (not when patient is already selected)
        if selected_patient_id is None:
            from routes.attention import _clear_temp_attention_data
            _clear_temp_attention_data()

        # Get available patients and selected patient info
        available_patients = Patient.query.filter_by(is_deleted=False).all()
        selected_patient = None
        attentions = []
        if selected_patient_id:
            selected_patient = Patient.query.filter_by(id=selected_patient_id, is_deleted=False).first()
            if selected_patient:
                attentions = (
                    Attention.query
                    .filter_by(idPatient=selected_patient.id)
                    .order_by(Attention.date.desc())
                    .all()
                )
                # Attach doctor name to each attention
                for att in attentions:
                    doctor = Doctor.query.filter_by(id=att.idDoctor, is_deleted=False).first()
                    att.doctor_name = f"Dr. {doctor.firstName} {doctor.lastName1}" if doctor else "-"
                
                # Batch doctor lookup for all attentions
                doctor_ids = list(set(att.idDoctor for att in attentions if att.idDoctor))
                doctor_map = {}
                if doctor_ids:
                    doctors = Doctor.query.filter(Doctor.id.in_(doctor_ids), Doctor.is_deleted == False).all()
                    doctor_map = {doc.id: f"Dr. {doc.firstName} {doc.lastName1}" for doc in doctors}
                for att in attentions:
                    att.doctor_name = doctor_map.get(att.idDoctor, "-")
        
        # Get selected attention detail if requested
        selected_attention = None
        selected_attention_patient = None
        selected_attention_doctor = None
        selected_attention_id = request.args.get('selected_attention_id')
        if selected_attention_id:
            selected_attention = Attention.query.filter_by(id=selected_attention_id).first()
            if selected_attention:
                selected_attention_patient = Patient.query.filter_by(id=selected_attention.idPatient, is_deleted=False).first()
                selected_attention_doctor = Doctor.query.filter_by(id=selected_attention.idDoctor, is_deleted=False).first()
        
        current_step = request.args.get('step', 'vitales')
        return render_template('home.html', view=view,
                             vital_signs_data=vital_signs_data,
                             evaluation_data=evaluation_data,
                             physicalExams=physical_exams,
                             organSystemReviews=organ_system_reviews,
                             diagnostics=diagnostics,
                             treatments=treatments,
                             histopathologies=histopathologies,
                             imagings=imagings,
                             laboratories=laboratories,
                             available_patients=available_patients,
                             selected_patient=selected_patient,
                             selected_patient_id=selected_patient_id,
                             attentions=attentions,
                             current_step=current_step,
                             doctor_info=doctor_info,
                             selected_attention=selected_attention,
                             patient=selected_attention_patient,
                             doctor=selected_attention_doctor)
    
    return render_template('home.html', doctor_info=doctor_info)