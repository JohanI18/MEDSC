from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from models.models_flask import Patient, Allergy, FamilyBackground, PreExistingCondition, EmergencyContact
from utils.db import db
from sqlalchemy.exc import IntegrityError
import logging
import os

patients = Blueprint('patients', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Verifica si hay conexión a la base de datos"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Error de conexión a base de datos: {str(e)}")
        return False

def get_doctor_info_and_session():
    """Obtiene información del doctor y sessionID de manera compatible con Supabase"""
    from models.models_flask import Doctor
    
    doctor_info = None
    sessionID = None
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if session.get('auth_provider') == 'supabase':
        # Para Supabase, creamos información ficticia del doctor
        email = session.get('email', 'Doctor')
        user_id = session.get('user_id', 'demo')
        name_parts = email.split('@')[0].split('.')
        
        doctor_info = {
            'firstName': name_parts[0].capitalize() if len(name_parts) > 0 else 'Doctor',
            'lastName1': name_parts[1].capitalize() if len(name_parts) > 1 else 'Supabase',
            'speciality': 'Medicina General'
        }
        sessionID = user_id
        
    elif 'cedula' in session and has_database:
        # Código original para login local (solo si hay base de datos)
        try:
            doctor = Doctor.query.filter_by(identifierCode=session['cedula'], is_deleted=False).first()
            if doctor:
                doctor_info = {
                    'firstName': doctor.firstName,
                    'lastName1': doctor.lastName1,
                    'speciality': doctor.speciality
                }
                sessionID = session['cedula']
        except Exception as e:
            logger.error(f"Error fetching doctor info: {str(e)}")
    
    return doctor_info, sessionID

# Global lists for temporary storage (consider using session storage instead)
allergies = []
familyBack = []
preExistingConditions = []
emergencyContacts = []  # Add missing emergency contacts list
current_patient_id = None  # Add this to track the current patient being processed

@patients.route('/patients')
def show_patients():
    """Display all patients with proper error handling"""
    try:
        all_patients = Patient.query.filter_by(is_deleted=False).all()
        return render_template('patients_list.html', patients=all_patients)
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        flash('Error al cargar la lista de pacientes', 'error')
        return redirect(url_for('clinic.home'))

@patients.route('/api/patients', methods=['GET'])
def get_patients_api():
    """API endpoint to get all patients as JSON with all related data"""
    try:
        all_patients = Patient.query.filter_by(is_deleted=False).all()
        patients_data = []
        
        for patient in all_patients:
            # Get all related data for the patient
            allergies = Allergy.query.filter_by(idPatient=patient.id, is_deleted=False).all()
            emergency_contacts = EmergencyContact.query.filter_by(idPatient=patient.id, is_deleted=False).all()
            pre_existing_conditions = PreExistingCondition.query.filter_by(idPatient=patient.id, is_deleted=False).all()
            family_backgrounds = FamilyBackground.query.filter_by(idPatient=patient.id, is_deleted=False).all()
            
            # Format emergency contacts
            emergency_contacts_data = []
            for contact in emergency_contacts:
                emergency_contacts_data.append({
                    'id': contact.id,
                    'first_name': contact.firstName,
                    'last_name': contact.lastName,
                    'full_name': f"{contact.firstName} {contact.lastName}",
                    'relationship': contact.relationship,
                    'phone1': contact.phoneNumber1,
                    'phone2': contact.phoneNumber2,
                    'address': contact.address
                })
            
            # Format allergies
            allergies_data = []
            for allergy in allergies:
                allergies_data.append({
                    'id': allergy.id,
                    'allergy': allergy.allergies
                })
            
            # Format pre-existing conditions
            conditions_data = []
            for condition in pre_existing_conditions:
                conditions_data.append({
                    'id': condition.id,
                    'disease_name': condition.diseaseName,
                    'time': condition.time.isoformat() if condition.time else None,
                    'medicament': condition.medicament,
                    'treatment': condition.treatment
                })
            
            # Format family backgrounds
            family_backgrounds_data = []
            for background in family_backgrounds:
                family_backgrounds_data.append({
                    'id': background.id,
                    'family_background': background.familyBackground,
                    'time': background.time.isoformat() if background.time else None,
                    'degree_relationship': background.degreeRelationship
                })
            
            # Get first emergency contact for backward compatibility
            first_emergency_contact = emergency_contacts[0] if emergency_contacts else None
            
            patient_dict = {
                'id': patient.id,
                'first_name': patient.firstName,
                'middle_name': patient.middleName,
                'last_name': patient.lastName1,
                'last_name2': patient.lastName2,
                'email': patient.email,
                'phone': patient.phoneNumber,
                'address': patient.address,
                'date_of_birth': patient.birthdate.isoformat() if patient.birthdate else None,
                'gender': patient.gender,
                'sex': patient.sex,
                'civil_status': patient.civilStatus,
                'nationality': patient.nationality,
                'job': patient.job,
                'blood_type': patient.bloodType,
                'identification_type': patient.identifierType,
                'identification_number': patient.identifierCode,
                # Backward compatibility fields for first emergency contact
                'emergency_contact_name': f"{first_emergency_contact.firstName} {first_emergency_contact.lastName}" if first_emergency_contact else None,
                'emergency_contact_phone': first_emergency_contact.phoneNumber1 if first_emergency_contact else None,
                # Complete related data
                'allergies': allergies_data,
                'emergency_contacts': emergency_contacts_data,
                'pre_existing_conditions': conditions_data,
                'family_backgrounds': family_backgrounds_data,
                'created_at': patient.created_at.isoformat() if patient.created_at else None,
                'updated_at': patient.updated_at.isoformat() if patient.updated_at else None
            }
            patients_data.append(patient_dict)
        
        return jsonify({
            'success': True,
            'data': patients_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching patients API: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error al cargar la lista de pacientes'
        }), 500


# Update patient API endpoint (comprehensive)
@patients.route('/api/patients/<int:patient_id>', methods=['PUT', 'POST'])
def update_patient_api(patient_id):
    """Update patient with complete data including relationships"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()
    
    if not sessionID:
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    try:
        # Get patient
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        logger.info(f"Updating patient {patient_id} with data: {data}")
        
        # Update basic patient information
        if 'first_name' in data:
            patient.firstName = data['first_name']
        if 'middle_name' in data:
            patient.middleName = data['middle_name']
        if 'last_name' in data:
            patient.lastName1 = data['last_name']
        if 'last_name2' in data:
            patient.lastName2 = data['last_name2']
        if 'identification_type' in data:
            patient.identifierType = data['identification_type']
        if 'identification_number' in data:
            # Check for duplicate identification
            existing_patient = Patient.query.filter(
                Patient.identifierCode == data['identification_number'],
                Patient.id != patient_id,
                Patient.is_deleted == False
            ).first()
            
            if existing_patient:
                return jsonify({'success': False, 'error': 'Ya existe otro paciente con este número de identificación'}), 400
            
            patient.identifierCode = data['identification_number']
        if 'email' in data:
            patient.email = data['email']
        if 'phone' in data:
            patient.phoneNumber = data['phone']
        if 'address' in data:
            patient.address = data['address']
        if 'date_of_birth' in data:
            patient.birthdate = data['date_of_birth']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'sex' in data:
            patient.sex = data['sex']
        if 'civil_status' in data:
            patient.civilStatus = data['civil_status']
        if 'nationality' in data:
            patient.nationality = data['nationality']
        if 'job' in data:
            patient.job = data['job']
        if 'blood_type' in data:
            patient.bloodType = data['blood_type']
        
        patient.updated_by = sessionID
        
        # Handle allergies
        if 'allergies' in data:
            # Delete existing allergies
            existing_allergies = Allergy.query.filter_by(idPatient=patient_id).all()
            for allergy in existing_allergies:
                db.session.delete(allergy)
            
            # Add new allergies
            for allergy_data in data['allergies']:
                if allergy_data.get('allergy'):
                    new_allergy = Allergy(
                        idPatient=patient_id,
                        allergies=allergy_data['allergy'],
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_allergy)
        
        # Handle emergency contacts
        if 'emergency_contacts' in data:
            # Delete existing emergency contacts
            existing_contacts = EmergencyContact.query.filter_by(idPatient=patient_id).all()
            for contact in existing_contacts:
                db.session.delete(contact)
            
            # Add new emergency contacts
            for contact_data in data['emergency_contacts']:
                if contact_data.get('first_name') and contact_data.get('last_name'):
                    new_contact = EmergencyContact(
                        idPatient=patient_id,
                        firstName=contact_data['first_name'],
                        lastName=contact_data['last_name'],
                        relationship=contact_data.get('relationship', ''),
                        phoneNumber1=contact_data.get('phone1', ''),
                        phoneNumber2=contact_data.get('phone2'),
                        address=contact_data.get('address', ''),
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_contact)
        
        # Handle pre-existing conditions
        if 'pre_existing_conditions' in data:
            # Delete existing conditions
            existing_conditions = PreExistingCondition.query.filter_by(idPatient=patient_id).all()
            for condition in existing_conditions:
                db.session.delete(condition)
            
            # Add new conditions
            for condition_data in data['pre_existing_conditions']:
                if condition_data.get('disease_name'):
                    new_condition = PreExistingCondition(
                        idPatient=patient_id,
                        diseaseName=condition_data['disease_name'],
                        time=condition_data.get('time'),
                        medicament=condition_data.get('medicament'),
                        treatment=condition_data.get('treatment'),
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_condition)
        
        # Handle family backgrounds
        if 'family_backgrounds' in data:
            # Delete existing family backgrounds
            existing_backgrounds = FamilyBackground.query.filter_by(idPatient=patient_id).all()
            for background in existing_backgrounds:
                db.session.delete(background)
            
            # Add new family backgrounds
            for background_data in data['family_backgrounds']:
                if background_data.get('family_background'):
                    new_background = FamilyBackground(
                        idPatient=patient_id,
                        familyBackground=background_data['family_background'],
                        time=background_data.get('time'),
                        degreeRelationship=background_data.get('degree_relationship', '1'),
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_background)
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Patient {patient_id} updated successfully by {sessionID}")
        
        # Return updated patient data
        # Reload relationships
        updated_allergies = Allergy.query.filter_by(idPatient=patient_id).all()
        updated_contacts = EmergencyContact.query.filter_by(idPatient=patient_id).all()
        updated_conditions = PreExistingCondition.query.filter_by(idPatient=patient_id).all()
        updated_backgrounds = FamilyBackground.query.filter_by(idPatient=patient_id).all()
        
        # Format response data
        allergies_data = [{
            'id': allergy.id,
            'allergy': allergy.allergies,
            'created_at': allergy.created_at.isoformat() if allergy.created_at else None
        } for allergy in updated_allergies]
        
        emergency_contacts_data = [{
            'id': contact.id,
            'first_name': contact.firstName,
            'last_name': contact.lastName,
            'relationship': contact.relationship,
            'phone1': contact.phoneNumber1,
            'phone2': contact.phoneNumber2,
            'address': contact.address,
            'created_at': contact.created_at.isoformat() if contact.created_at else None
        } for contact in updated_contacts]
        
        conditions_data = [{
            'id': condition.id,
            'disease_name': condition.diseaseName,
            'time': condition.time,
            'medicament': condition.medicament,
            'treatment': condition.treatment,
            'created_at': condition.created_at.isoformat() if condition.created_at else None
        } for condition in updated_conditions]
        
        family_backgrounds_data = [{
            'id': background.id,
            'family_background': background.familyBackground,
            'time': background.time,
            'degree_relationship': background.degreeRelationship,
            'created_at': background.created_at.isoformat() if background.created_at else None
        } for background in updated_backgrounds]
        
        patient_data = {
            'id': patient.id,
            'first_name': patient.firstName,
            'middle_name': patient.middleName,
            'last_name': patient.lastName1,
            'last_name2': patient.lastName2,
            'identification_type': patient.identifierType,
            'identification_number': patient.identifierCode,
            'email': patient.email,
            'phone': patient.phoneNumber,
            'address': patient.address,
            'date_of_birth': patient.birthdate,
            'gender': patient.gender,
            'sex': patient.sex,
            'civil_status': patient.civilStatus,
            'nationality': patient.nationality,
            'job': patient.job,
            'blood_type': patient.bloodType,
            'allergies': allergies_data,
            'emergency_contacts': emergency_contacts_data,
            'pre_existing_conditions': conditions_data,
            'family_backgrounds': family_backgrounds_data,
            'created_at': patient.created_at.isoformat() if patient.created_at else None,
            'updated_at': patient.updated_at.isoformat() if patient.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': patient_data,
            'message': 'Paciente actualizado exitosamente'
        })
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating patient API: {str(e)}")
        return jsonify({'success': False, 'error': 'Error de integridad en los datos'}), 400
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating patient API: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500


@patients.route('/editar-paciente/<int:patient_id>', methods=['GET', 'POST'])
def editar_paciente(patient_id):
    """
    Editar un paciente existente desde la misma interfaz de agregar
    y continuar con información adicional.
    """
    global current_patient_id  # 🔴 Importante para usar la variable global

    patient = Patient.query.get_or_404(patient_id)

    # Obtener doctor_info desde la sesión usando la función helper
    doctor_info, sessionID = get_doctor_info_and_session()
    
    if not sessionID:
        flash('Sesión no válida', 'error')
        return redirect(url_for('login.index'))

    if request.method == 'POST':
        try:
            # Actualizar los campos del paciente desde el formulario
            patient.identifierType = request.form.get('identifierType')
            patient.identifierCode = request.form.get('identifierCode')
            patient.firstName = request.form.get('firstName')
            patient.middleName = request.form.get('middleName')
            patient.lastName1 = request.form.get('lastName1')
            patient.lastName2 = request.form.get('lastName2')
            patient.nationality = request.form.get('nationality')
            patient.address = request.form.get('address')
            patient.phoneNumber = request.form.get('phoneNumber')
            patient.birthdate = request.form.get('birthdate')
            patient.gender = request.form.get('gender')
            patient.sex = request.form.get('sex')
            patient.civilStatus = request.form.get('civilStatus')
            patient.job = request.form.get('job')
            patient.bloodType = request.form.get('bloodType')
            patient.email = request.form.get('email')
            patient.updated_by = session.get('cedula')

            db.session.commit()

            # 🔴 Guardar en variable global y sesión
            current_patient_id = patient.id
            session['current_patient_id'] = patient.id
            session['edit_mode'] = True

            flash('Paciente actualizado exitosamente. Puede continuar con la información adicional.', 'success')
            return redirect(url_for(
                'clinic.home',
                view='addPatient',
                sec_view='addPatientInfo',
                edit_mode='true',
                current_patient_id=patient.id
            ))


        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando paciente: {str(e)}")
            flash('Error al actualizar el paciente', 'error')

    return render_template(
        'home.html',
        view='addPatient',
        sec_view='addPatient',
        patient=patient,
        edit_mode=True,
        doctor_info=doctor_info,
        current_patient_id=patient.id
    )






@patients.route('/historial-paciente/<int:patient_id>')
def patient_details(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Consulta los datos relacionados desde la base de datos
    allergies = Allergy.query.filter_by(idPatient=patient_id).all()
    contacts = EmergencyContact.query.filter_by(idPatient=patient_id).all()
    conditions = PreExistingCondition.query.filter_by(idPatient=patient_id).all()
    backgrounds = FamilyBackground.query.filter_by(idPatient=patient_id).all()

    return render_template(
        'partials/_patient_detail.html',
        patient=patient,
        allergies=allergies,
        contacts=contacts,
        conditions=conditions,
        backgrounds=backgrounds
    )

@patients.route('/add-patients', methods=['POST'])
def add_patients():
    """Add new patient and continue to additional info step"""
    global current_patient_id, allergies, familyBack, preExistingConditions, emergencyContacts
    
    # Verificar autenticación compatible con Supabase
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    doctor_info, sessionID = get_doctor_info_and_session()
    
    if not sessionID:
        flash('Sesión no válida', 'error')
        return redirect(url_for('login.index'))
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['identifierType', 'identifierCode', 'firstName', 'lastName1', 'address', 'birthdate']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'El campo {field} es requerido', 'error')
                    return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))
            
            # Check if patient already exists
            existing_patient = Patient.query.filter_by(
                identifierCode=request.form.get('identifierCode'),
                is_deleted=False
            ).first()
            
            if existing_patient:
                flash('Ya existe un paciente con este código de identificación', 'error')
                return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))
            
            # Create new patient
            new_patient = Patient(
                identifierType=request.form.get('identifierType'),
                identifierCode=request.form.get('identifierCode'),
                firstName=request.form.get('firstName'),
                middleName=request.form.get('middleName'),
                lastName1=request.form.get('lastName1'),
                lastName2=request.form.get('lastName2'),
                nationality=request.form.get('nationality'),
                address=request.form.get('address'),
                phoneNumber=request.form.get('phoneNumber'),
                birthdate=request.form.get('birthdate'),
                gender=request.form.get('gender'),
                sex=request.form.get('sex'),
                civilStatus=request.form.get('civilStatus'),
                job=request.form.get('job'),
                bloodType=request.form.get('bloodType'),
                email=request.form.get('email'),
                created_by=sessionID,
                updated_by=sessionID
            )

            db.session.add(new_patient)
            db.session.commit()
            
            # Store the ID of the newly created patient
            current_patient_id = new_patient.id
            # Store the patient ID in the session as well
            session['current_patient_id'] = new_patient.id
            
            # Clear any existing temporary data
            allergies.clear()
            familyBack.clear()
            preExistingConditions.clear()
            emergencyContacts.clear()
            
            logger.info(f"Patient created successfully: {new_patient.identifierCode} with ID: {new_patient.id}")
            flash(f'Datos básicos de {new_patient.firstName} {new_patient.lastName1} guardados. Ahora agregue información adicional.', 'success')
            
            # Redirect to additional info step
            return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating patient: {str(e)}")
            flash('Error: Código de identificación ya existe', 'error')
            return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            flash('Error al agregar paciente', 'error')
            return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))

@patients.route('/api/patients', methods=['POST'])
def add_patient_api():
    """API endpoint to add a new patient"""
    try:
        # Verificar autenticación compatible con Supabase
        if not session.get('autenticado'):
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401

        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400

        # Debug: log received data
        logger.info(f"Received patient data: {data}")

        # Validate required fields
        required_fields = ['identification_type', 'identification_number', 'first_name', 'last_name', 'address', 'date_of_birth', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400

        # Check if patient already exists
        existing_patient = Patient.query.filter_by(
            identifierCode=data.get('identification_number'),
            is_deleted=False
        ).first()

        if existing_patient:
            return jsonify({'success': False, 'error': 'Ya existe un paciente con este número de identificación'}), 400

        # Get session info
        doctor_info, sessionID = get_doctor_info_and_session()
        if not sessionID:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401

        # Create new patient with all optional fields
        new_patient = Patient(
            identifierType=data.get('identification_type'),
            identifierCode=data.get('identification_number'),
            firstName=data.get('first_name'),
            middleName=data.get('middle_name'),
            lastName1=data.get('last_name'),
            lastName2=data.get('last_name2'),
            nationality=data.get('nationality'),
            address=data.get('address'),
            phoneNumber=data.get('phone'),
            birthdate=data.get('date_of_birth'),
            gender=data.get('gender'),
            sex=data.get('sex'),
            civilStatus=data.get('civil_status'),
            job=data.get('job'),
            bloodType=data.get('blood_type'),
            email=data.get('email'),
            created_by=sessionID,
            updated_by=sessionID
        )

        db.session.add(new_patient)
        db.session.flush()  # Flush to get the ID without committing

        # Create allergies
        if data.get('allergies'):
            logger.info(f"Processing allergies: {data.get('allergies')}")
            for allergy_text in data.get('allergies'):
                if allergy_text and str(allergy_text).strip():
                    new_allergy = Allergy(
                        allergies=str(allergy_text).strip(),
                        idPatient=new_patient.id,
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_allergy)
                    logger.info(f"Added allergy: {str(allergy_text).strip()}")

        # Create emergency contacts
        if data.get('emergency_contacts'):
            logger.info(f"Processing emergency contacts: {data.get('emergency_contacts')}")
            for contact_data in data.get('emergency_contacts'):
                if contact_data.get('first_name') and contact_data.get('last_name'):
                    new_contact = EmergencyContact(
                        idPatient=new_patient.id,
                        firstName=contact_data.get('first_name'),
                        lastName=contact_data.get('last_name'),
                        relationship=contact_data.get('relationship', 'Contacto de emergencia'),
                        phoneNumber1=contact_data.get('phone1', ''),
                        phoneNumber2=contact_data.get('phone2'),
                        address=contact_data.get('address', data.get('address', '')),
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_contact)
                    logger.info(f"Added emergency contact: {contact_data.get('first_name')} {contact_data.get('last_name')}")

        # Create pre-existing conditions
        if data.get('pre_existing_conditions'):
            logger.info(f"Processing pre-existing conditions: {data.get('pre_existing_conditions')}")
            for condition_data in data.get('pre_existing_conditions'):
                if condition_data.get('disease_name'):
                    new_condition = PreExistingCondition(
                        diseaseName=condition_data.get('disease_name'),
                        time=condition_data.get('time'),
                        medicament=condition_data.get('medicament'),
                        treatment=condition_data.get('treatment'),
                        idPatient=new_patient.id,
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_condition)
                    logger.info(f"Added pre-existing condition: {condition_data.get('disease_name')}")

        # Create family backgrounds
        if data.get('family_backgrounds'):
            logger.info(f"Processing family backgrounds: {data.get('family_backgrounds')}")
            for family_data in data.get('family_backgrounds'):
                if family_data.get('family_background'):
                    new_family_bg = FamilyBackground(
                        familyBackground=family_data.get('family_background'),
                        time=family_data.get('time'),
                        degreeRelationship=family_data.get('degree_relationship', '1'),
                        idPatient=new_patient.id,
                        created_by=sessionID,
                        updated_by=sessionID
                    )
                    db.session.add(new_family_bg)
                    logger.info(f"Added family background: {family_data.get('family_background')}")

        # Legacy support: Create emergency contact if provided in old format
        elif data.get('emergency_contact_name') or data.get('emergency_contact_phone'):
            # Split the name if provided as a single field
            emergency_name = data.get('emergency_contact_name', '')
            name_parts = emergency_name.split(' ', 1) if emergency_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            emergency_contact = EmergencyContact(
                idPatient=new_patient.id,
                firstName=first_name,
                lastName=last_name,
                phoneNumber1=data.get('emergency_contact_phone', ''),
                relationship='Contacto de emergencia',
                address=data.get('address', '')  # Use patient address as default
            )
            db.session.add(emergency_contact)

        db.session.commit()

        # Get all created related data for response
        allergies = Allergy.query.filter_by(idPatient=new_patient.id, is_deleted=False).all()
        emergency_contacts = EmergencyContact.query.filter_by(idPatient=new_patient.id, is_deleted=False).all()
        pre_existing_conditions = PreExistingCondition.query.filter_by(idPatient=new_patient.id, is_deleted=False).all()
        family_backgrounds = FamilyBackground.query.filter_by(idPatient=new_patient.id, is_deleted=False).all()

        # Format response data
        allergies_data = [{'id': a.id, 'allergy': a.allergies} for a in allergies]
        
        emergency_contacts_data = []
        for contact in emergency_contacts:
            emergency_contacts_data.append({
                'id': contact.id,
                'first_name': contact.firstName,
                'last_name': contact.lastName,
                'relationship': contact.relationship,
                'phone1': contact.phoneNumber1,
                'phone2': contact.phoneNumber2,
                'address': contact.address
            })

        conditions_data = []
        for condition in pre_existing_conditions:
            conditions_data.append({
                'id': condition.id,
                'disease_name': condition.diseaseName,
                'time': condition.time.isoformat() if condition.time else None,
                'medicament': condition.medicament,
                'treatment': condition.treatment
            })

        family_backgrounds_data = []
        for background in family_backgrounds:
            family_backgrounds_data.append({
                'id': background.id,
                'family_background': background.familyBackground,
                'time': background.time.isoformat() if background.time else None,
                'degree_relationship': background.degreeRelationship
            })

        # Get first emergency contact for backward compatibility
        first_emergency_contact = emergency_contacts[0] if emergency_contacts else None

        # Return the created patient data with all relationships
        patient_data = {
            'id': new_patient.id,
            'first_name': new_patient.firstName,
            'middle_name': new_patient.middleName,
            'last_name': new_patient.lastName1,
            'last_name2': new_patient.lastName2,
            'email': new_patient.email,
            'phone': new_patient.phoneNumber,
            'address': new_patient.address,
            'date_of_birth': new_patient.birthdate.isoformat() if new_patient.birthdate else None,
            'gender': new_patient.gender,
            'sex': new_patient.sex,
            'civil_status': new_patient.civilStatus,
            'nationality': new_patient.nationality,
            'job': new_patient.job,
            'blood_type': new_patient.bloodType,
            'identification_type': new_patient.identifierType,
            'identification_number': new_patient.identifierCode,
            # Backward compatibility fields
            'emergency_contact_name': f"{first_emergency_contact.firstName} {first_emergency_contact.lastName}" if first_emergency_contact else None,
            'emergency_contact_phone': first_emergency_contact.phoneNumber1 if first_emergency_contact else None,
            # Complete related data
            'allergies': allergies_data,
            'emergency_contacts': emergency_contacts_data,
            'pre_existing_conditions': conditions_data,
            'family_backgrounds': family_backgrounds_data,
            'created_at': new_patient.created_at.isoformat() if new_patient.created_at else None
        }

        logger.info(f"Patient created via API: {new_patient.identifierCode} with ID: {new_patient.id}")
        
        return jsonify({
            'success': True,
            'message': 'Paciente creado exitosamente',
            'data': patient_data
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        return jsonify({'success': False, 'error': 'Error: Datos duplicados o inválidos'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding patient via API: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al agregar el paciente'}), 500

# ALLERGIES ROUTES
@patients.route('/add-allergies', methods=['POST'])
def add_allergies():
    # Verificar autenticación compatible con Supabase
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))

    doctor_info, sessionID = get_doctor_info_and_session()
    
    if not sessionID:
        flash('Sesión no válida', 'error')
        return redirect(url_for('login.index'))

    if request.method == 'POST':
        try:
            new_allergy = request.form.get('allergy')
            
            if not new_allergy or not new_allergy.strip():
                flash('Por favor ingrese una alergia válida', 'error')
                return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))
            
            # Store temporarily - don't save to database yet
            if current_patient_id and new_allergy.strip() not in allergies:
                allergies.append(new_allergy.strip())
                flash('Alergia agregada temporalmente', 'info')
            elif not current_patient_id:
                flash('Error: No hay paciente activo para agregar alergia', 'error')
            else:
                flash('Esta alergia ya existe', 'warning')
            
        except Exception as e:
            logger.error(f"Error adding allergy: {str(e)}")
            flash('Error al agregar alergia', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         allergies=allergies, emergencyContacts=emergencyContacts, 
                         familyBack=familyBack, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

@patients.route('/remove-allergy', methods=['POST'])
def remove_allergy():
    """Remove allergy from temporary storage"""
    try:
        allergy_to_remove = request.form.get('allergy', '').strip()
        if allergy_to_remove in allergies:
            allergies.remove(allergy_to_remove)
            flash(f'Alergia "{allergy_to_remove}" eliminada temporalmente', 'success')
        else:
            flash('Alergia no encontrada', 'error')
    except Exception as e:
        logger.error(f"Error removing allergy: {str(e)}")
        flash('Error al eliminar alergia', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         allergies=allergies, emergencyContacts=emergencyContacts, 
                         familyBack=familyBack, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

# EMERGENCY CONTACT ROUTES
@patients.route('/add-contact', methods=['GET', 'POST'])
def add_contact():
    """Add emergency contact to temporary storage"""
    global current_patient_id, emergencyContacts
    
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    if request.method == 'POST':
        try:
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            address = request.form.get('address')
            relationship = request.form.get('relationship')
            phone_number1 = request.form.get('phoneNumber1')
            phone_number2 = request.form.get('phoneNumber2')
            
            # Validate required fields
            if not all([first_name, last_name, address, relationship, phone_number1]):
                flash('Por favor complete todos los campos requeridos del contacto de emergencia', 'error')
                return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))
            
            # Store temporarily - don't save to database yet
            if current_patient_id:
                contact_data = {
                    'firstName': first_name.strip(),
                    'lastName': last_name.strip(),
                    'address': address.strip(),
                    'relationship': relationship.strip(),
                    'phoneNumber1': phone_number1.strip(),
                    'phoneNumber2': phone_number2.strip() if phone_number2 else None
                }
                
                # Check if contact already exists
                contact_exists = any(
                    c['firstName'] == contact_data['firstName'] and 
                    c['lastName'] == contact_data['lastName'] and
                    c['phoneNumber1'] == contact_data['phoneNumber1']
                    for c in emergencyContacts
                )
                
                if not contact_exists:
                    emergencyContacts.append(contact_data)
                    flash('Contacto de emergencia agregado temporalmente', 'info')
                else:
                    flash('Este contacto ya existe', 'warning')
            else:
                flash('Error: No hay paciente activo para agregar contacto', 'error')
            
        except Exception as e:
            logger.error(f"Error adding emergency contact: {str(e)}")
            flash('Error al agregar contacto de emergencia', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         emergencyContacts=emergencyContacts, allergies=allergies, 
                         familyBack=familyBack, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

@patients.route('/remove-contact', methods=['POST'])
def remove_contact():
    """Remove emergency contact from temporary storage"""
    try:
        index = int(request.form.get('index', -1))
        if 0 <= index < len(emergencyContacts):
            removed_contact = emergencyContacts.pop(index)
            flash(f'Contacto "{removed_contact["firstName"]} {removed_contact["lastName"]}" eliminado temporalmente', 'success')
        else:
            flash('Contacto no encontrado', 'error')
    except Exception as e:
        logger.error(f"Error removing emergency contact: {str(e)}")
        flash('Error al eliminar contacto de emergencia', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         emergencyContacts=emergencyContacts, allergies=allergies, 
                         familyBack=familyBack, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

# FAMILY BACKGROUND ROUTES
@patients.route('/add-familyBack', methods=['GET', 'POST'])
def add_familyBack():
    """Add family background to temporary storage"""
    global current_patient_id, familyBack
    
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    if request.method == 'POST':
        try:
            background = request.form.get('familyBackground')
            time = request.form.get('time')
            degree_relationship = request.form.get('degreeRelationship')
            
            if not background or not background.strip():
                flash('Por favor ingrese un antecedente familiar válido', 'error')
                return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))
            
            # Store temporarily - don't save to database yet
            if current_patient_id:
                family_data = {
                    'background': background.strip(),
                    'time': time,
                    'degree': degree_relationship
                }
                
                # Check if family background already exists
                bg_exists = any(
                    f['background'] == family_data['background'] and 
                    f['time'] == family_data['time']
                    for f in familyBack
                )
                
                if not bg_exists:
                    familyBack.append(family_data)
                    flash('Antecedente familiar agregado temporalmente', 'info')
                else:
                    flash('Este antecedente familiar ya existe', 'warning')
            else:
                flash('Error: No hay paciente activo para agregar antecedente', 'error')
            
        except Exception as e:
            logger.error(f"Error adding family background: {str(e)}")
            flash('Error al agregar antecedente familiar', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         familyBack=familyBack, emergencyContacts=emergencyContacts, 
                         allergies=allergies, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

@patients.route('/remove-familyBack', methods=['POST'])
def remove_familyBack():
    """Remove family background from temporary storage"""
    try:
        index = int(request.form.get('index', -1))
        if 0 <= index < len(familyBack):
            removed_bg = familyBack.pop(index)
            flash(f'Antecedente familiar "{removed_bg["background"]}" eliminado temporalmente', 'success')
        else:
            flash('Antecedente familiar no encontrado', 'error')
    except Exception as e:
        logger.error(f"Error removing family background: {str(e)}")
        flash('Error al eliminar antecedente familiar', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         familyBack=familyBack, emergencyContacts=emergencyContacts, 
                         allergies=allergies, preExistingConditions=preExistingConditions,
                         current_patient_id=current_patient_id)

# PRE-EXISTING CONDITIONS ROUTES
@patients.route('/add-conditions', methods=['GET', 'POST'])
def add_conditions():
    """Add pre-existing conditions to temporary storage"""
    global current_patient_id, preExistingConditions
    
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    if request.method == 'POST':
        try:
            disease_name = request.form.get('diseaseName')
            time = request.form.get('time')
            medicament = request.form.get('medicament')
            treatment = request.form.get('treatment')
            
            if not disease_name or not disease_name.strip():
                flash('Por favor ingrese un nombre de enfermedad válido', 'error')
                return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))
            
            # Store temporarily - don't save to database yet
            if current_patient_id:
                condition_data = {
                    'diseaseName': disease_name.strip(),
                    'time': time,
                    'medicament': medicament.strip() if medicament else None,
                    'treatment': treatment.strip() if treatment else None
                }
                
                # Check if condition already exists
                condition_exists = any(
                    c['diseaseName'] == condition_data['diseaseName'] and 
                    c['time'] == condition_data['time']
                    for c in preExistingConditions
                )
                
                if not condition_exists:
                    preExistingConditions.append(condition_data)
                    flash('Condición preexistente agregada temporalmente', 'info')
                else:
                    flash('Esta condición ya existe', 'warning')
            else:
                flash('Error: No hay paciente activo para agregar condición', 'error')
            
        except Exception as e:
            logger.error(f"Error adding pre-existing condition: {str(e)}")
            flash('Error al agregar condición preexistente', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         preExistingConditions=preExistingConditions, emergencyContacts=emergencyContacts, 
                         allergies=allergies, familyBack=familyBack,
                         current_patient_id=current_patient_id)

@patients.route('/remove-condition', methods=['POST'])
def remove_condition():
    """Remove pre-existing condition from temporary storage"""
    try:
        index = int(request.form.get('index', -1))
        if 0 <= index < len(preExistingConditions):
            removed_condition = preExistingConditions.pop(index)
            flash(f'Condición "{removed_condition["diseaseName"]}" eliminada temporalmente', 'success')
        else:
            flash('Condición no encontrada', 'error')
    except Exception as e:
        logger.error(f"Error removing pre-existing condition: {str(e)}")
        flash('Error al eliminar condición preexistente', 'error')
    
    return render_template('home.html', view='addPatient', sec_view="addPatientInfo", 
                         preExistingConditions=preExistingConditions, emergencyContacts=emergencyContacts, 
                         allergies=allergies, familyBack=familyBack,
                         current_patient_id=current_patient_id)

# COMPLETION AND MANAGEMENT ROUTES
@patients.route('/complete-patient-registration', methods=['POST'])
def complete_patient_registration():
    """Save all temporary data to database and complete patient registration"""
    global allergies, familyBack, preExistingConditions, emergencyContacts, current_patient_id
    
    if not session.get('autenticado'):
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.index'))
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        if not current_patient_id:
            flash('No hay paciente activo para completar', 'error')
            return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))
        
        patient = Patient.query.filter_by(id=current_patient_id, is_deleted=False).first()
        if not patient:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatient'))
        
        # Save allergies
        saved_count = {'allergies': 0, 'contacts': 0, 'backgrounds': 0, 'conditions': 0}
        
        for allergy_text in allergies:
            if allergy_text.strip():
                new_allergy = Allergy(
                    allergies=allergy_text.strip(),
                    idPatient=current_patient_id,
                    created_by=sessionID,
                    updated_by=sessionID
                )
                db.session.add(new_allergy)
                saved_count['allergies'] += 1
        
        # Save emergency contacts
        for contact_data in emergencyContacts:
            new_contact = EmergencyContact(
                firstName=contact_data['firstName'],
                lastName=contact_data['lastName'],
                address=contact_data['address'],
                relationship=contact_data['relationship'],
                phoneNumber1=contact_data['phoneNumber1'],
                phoneNumber2=contact_data.get('phoneNumber2'),
                idPatient=current_patient_id,
                created_by=sessionID,
                updated_by=sessionID
            )
            db.session.add(new_contact)
            saved_count['contacts'] += 1
        
        # Save family backgrounds
        for family_data in familyBack:
            if family_data.get('background') and family_data.get('time') and family_data.get('degree'):
                new_family_bg = FamilyBackground(
                    familyBackground=family_data['background'],
                    time=family_data['time'],
                    degreeRelationship=family_data['degree'],
                    idPatient=current_patient_id,
                    created_by=sessionID,
                    updated_by=sessionID
                )
                db.session.add(new_family_bg)
                saved_count['backgrounds'] += 1
        
        # Save pre-existing conditions
        for condition_data in preExistingConditions:
            if condition_data.get('diseaseName') and condition_data.get('time'):
                new_condition = PreExistingCondition(
                    diseaseName=condition_data['diseaseName'],
                    time=condition_data['time'],
                    medicament=condition_data.get('medicament'),
                    treatment=condition_data.get('treatment'),
                    idPatient=current_patient_id,
                    created_by=sessionID,
                    updated_by=sessionID
                )
                db.session.add(new_condition)
                saved_count['conditions'] += 1
        
        # Commit all changes
        db.session.commit()
        
        # Clear temporary data and reset current patient ID
        allergies.clear()
        familyBack.clear()
        preExistingConditions.clear()
        emergencyContacts.clear()
        current_patient_id = None
        
        # Create summary message
        summary_parts = []
        if saved_count['allergies'] > 0:
            summary_parts.append(f"{saved_count['allergies']} alergia(s)")
        if saved_count['contacts'] > 0:
            summary_parts.append(f"{saved_count['contacts']} contacto(s) de emergencia")
        if saved_count['backgrounds'] > 0:
            summary_parts.append(f"{saved_count['backgrounds']} antecedente(s) familiar(es)")
        if saved_count['conditions'] > 0:
            summary_parts.append(f"{saved_count['conditions']} condición(es) preexistente(s)")
        
        if summary_parts:
            summary = " • ".join(summary_parts)
            flash(f'Registro del paciente {patient.firstName} {patient.lastName1} completado exitosamente con: {summary}', 'success')
        else:
            flash(f'Registro del paciente {patient.firstName} {patient.lastName1} completado exitosamente (sin información adicional)', 'success')
        
        logger.info(f"Patient registration completed for: {patient.identifierCode} (ID: {patient.id}) with additional data")
        
        return redirect(url_for('clinic.home'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error completing patient registration: {str(e)}")
        flash('Error al completar el registro del paciente', 'error')
        return redirect(url_for('clinic.home', view='addPatient', sec_view='addPatientInfo'))

@patients.route('/get-patient-details/<int:patient_id>')
def get_patient_details(patient_id):
    """Get detailed patient information including all related data"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    try:
        # Get patient with all related data
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        # Get all related information
        allergies = Allergy.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        emergency_contacts = EmergencyContact.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        pre_existing_conditions = PreExistingCondition.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        family_backgrounds = FamilyBackground.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        
        # Get attention history with related data
        from models.models_flask import Attention, Doctor, Diagnostic
        attentions = Attention.query.filter_by(idPatient=patient_id, is_deleted=False)\
                                  .order_by(Attention.date.desc())\
                                  .limit(10)\
                                  .all()
        
        # Render the patient details template
        html_content = render_template('partials/_patientDetails.html',
                                     patient=patient,
                                     allergies=allergies,
                                     emergency_contacts=emergency_contacts,
                                     pre_existing_conditions=pre_existing_conditions,
                                     family_backgrounds=family_backgrounds,
                                     attentions=attentions)
        
        return jsonify({'success': True, 'html': html_content})
        
    except Exception as e:
        logger.error(f"Error getting patient details: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@patients.route('/get-patient-edit-form/<int:patient_id>')
def get_patient_edit_form(patient_id):
    """Get patient edit form with all related data"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        # Get all related information for editing
        allergies = Allergy.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        emergency_contacts = EmergencyContact.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        pre_existing_conditions = PreExistingCondition.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        family_backgrounds = FamilyBackground.query.filter_by(idPatient=patient_id, is_deleted=False).all()
        
        # Render the patient edit form template
        html_content = render_template('partials/_patientEditForm.html',
                                     patient=patient,
                                     allergies=allergies,
                                     emergency_contacts=emergency_contacts,
                                     pre_existing_conditions=pre_existing_conditions,
                                     family_backgrounds=family_backgrounds)
        
        return jsonify({'success': True, 'html': html_content})
        
    except Exception as e:
        logger.error(f"Error getting patient edit form: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Update patient information
@patients.route('/update-patient/<int:patient_id>', methods=['POST'])
def update_patient(patient_id):
    """Update patient information"""
    if not session.get('autenticado'):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
        flash('Sesión no válida', 'error')
        return redirect(url_for('clinic.home', view='patients'))
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('clinic.home', view='patients'))
        
        # Validate required fields
        required_fields = ['identifierType', 'identifierCode', 'firstName', 'lastName1', 'address', 'birthdate']
        for field in required_fields:
            if not request.form.get(field):
                if request.is_json:
                    return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
                flash(f'El campo {field} es requerido', 'error')
                return redirect(url_for('clinic.home', view='patients'))
        
        # Check if identifier code is unique (excluding current patient)
        existing_patient = Patient.query.filter(
            Patient.identifierCode == request.form.get('identifierCode'),
            Patient.id != patient_id,
            Patient.is_deleted == False
        ).first()
        
        if existing_patient:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Ya existe otro paciente con este código de identificación'}), 400
            flash('Ya existe otro paciente con este código de identificación', 'error')
            return redirect(url_for('clinic.home', view='patients'))
        
        # Update patient fields
        patient.identifierType = request.form.get('identifierType')
        patient.identifierCode = request.form.get('identifierCode')
        patient.firstName = request.form.get('firstName')
        patient.middleName = request.form.get('middleName') if request.form.get('middleName') else None
        patient.lastName1 = request.form.get('lastName1')
        patient.lastName2 = request.form.get('lastName2') if request.form.get('lastName2') else None
        patient.nationality = request.form.get('nationality') if request.form.get('nationality') else None
        patient.address = request.form.get('address')
        patient.phoneNumber = request.form.get('phoneNumber') if request.form.get('phoneNumber') else None
        patient.birthdate = request.form.get('birthdate')
        patient.gender = request.form.get('gender') if request.form.get('gender') else None
        patient.sex = request.form.get('sex') if request.form.get('sex') else None
        patient.civilStatus = request.form.get('civilStatus') if request.form.get('civilStatus') else None
        patient.job = request.form.get('job') if request.form.get('job') else None
        patient.bloodType = request.form.get('bloodType') if request.form.get('bloodType') else None
        patient.email = request.form.get('email') if request.form.get('email') else None
        patient.updated_by = sessionID
        
        db.session.commit()
        
        logger.info(f"Patient {patient_id} updated successfully by {sessionID}")
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Paciente actualizado exitosamente'})
        
        flash('Paciente actualizado exitosamente', 'success')
        return redirect(url_for('clinic.home', view='patients'))
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating patient: {str(e)}")
        
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error de integridad en los datos'}), 400
        flash('Error de integridad en los datos', 'error')
        return redirect(url_for('clinic.home', view='patients'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating patient: {str(e)}")
        
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
        flash('Error interno del servidor', 'error')
        return redirect(url_for('clinic.home', view='patients'))

# Add allergy to patient
@patients.route('/patient/<int:patient_id>/add-allergy', methods=['POST'])
def add_patient_allergy(patient_id):
    """Add allergy to patient"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
            
        allergy_text = data.get('allergy', '').strip()
        
        if not allergy_text:
            return jsonify({'success': False, 'error': 'La alergia es requerida'}), 400
        
        # Check if allergy already exists
        existing = Allergy.query.filter_by(
            idPatient=patient_id, 
            allergies=allergy_text, 
            is_deleted=False
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Esta alergia ya existe'}), 400
        
        new_allergy = Allergy(
            allergies=allergy_text,
            idPatient=patient_id,
            created_by=sessionID,
            updated_by=sessionID
        )
        
        db.session.add(new_allergy)
        db.session.commit()
        
        logger.info(f"Allergy added to patient {patient_id}: {allergy_text}")
        return jsonify({'success': True, 'message': 'Alergia agregada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding allergy: {str(e)}")
        return jsonify({'success': False, 'error': f'Error interno del servidor: {str(e)}'}), 500

# Delete allergy
@patients.route('/patient/allergy/<int:allergy_id>', methods=['DELETE'])
def delete_patient_allergy(allergy_id):
    """Delete patient allergy (soft delete)"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        allergy = Allergy.query.filter_by(id=allergy_id, is_deleted=False).first()
        if not allergy:
            return jsonify({'success': False, 'error': 'Alergia no encontrada'}), 404
        
        allergy.is_deleted = True
        allergy.updated_by = sessionID
        
        db.session.commit()
        
        logger.info(f"Allergy {allergy_id} soft deleted by {sessionID}")
        return jsonify({'success': True, 'message': 'Alergia eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting allergy: {str(e)}")
        return jsonify({'success': False, 'error': f'Error interno del servidor: {str(e)}'}), 500

# Add emergency contact to patient
@patients.route('/patient/<int:patient_id>/add-contact', methods=['POST'])
def add_patient_contact(patient_id):
    """Add emergency contact to patient"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        
        required_fields = ['firstName', 'lastName', 'relationship', 'phoneNumber1', 'address']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
        
        new_contact = EmergencyContact(
            firstName=data['firstName'].strip(),
            lastName=data['lastName'].strip(),
            relationship=data['relationship'].strip(),
            phoneNumber1=data['phoneNumber1'].strip(),
            phoneNumber2=data.get('phoneNumber2', '').strip() if data.get('phoneNumber2') else None,
            address=data['address'].strip(),
            idPatient=patient_id,
            created_by=sessionID,
            updated_by=sessionID
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        logger.info(f"Emergency contact added to patient {patient_id}: {new_contact.firstName} {new_contact.lastName}")
        return jsonify({'success': True, 'message': 'Contacto agregado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding contact: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Delete emergency contact
@patients.route('/patient/contact/<int:contact_id>', methods=['DELETE'])
def delete_patient_contact(contact_id):
    """Delete patient emergency contact (soft delete)"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        contact = EmergencyContact.query.filter_by(id=contact_id, is_deleted=False).first()
        if not contact:
            return jsonify({'success': False, 'error': 'Contacto no encontrado'}), 404
        
        contact.is_deleted = True
        contact.updated_by = sessionID
        
        db.session.commit()
        
        logger.info(f"Emergency contact {contact_id} soft deleted by {sessionID}")
        return jsonify({'success': True, 'message': 'Contacto eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting contact: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Add pre-existing condition to patient
@patients.route('/patient/<int:patient_id>/add-condition', methods=['POST'])
def add_patient_condition(patient_id):
    """Add pre-existing condition to patient"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('diseaseName', '').strip() or not data.get('time'):
            return jsonify({'success': False, 'error': 'Nombre de enfermedad y fecha son requeridos'}), 400
        
        new_condition = PreExistingCondition(
            diseaseName=data['diseaseName'].strip(),
            time=data['time'],
            medicament=data.get('medicament', '').strip() if data.get('medicament') else None,
            treatment=data.get('treatment', '').strip() if data.get('treatment') else None,
            idPatient=patient_id,
            created_by=sessionID,
            updated_by=sessionID
        )
        
        db.session.add(new_condition)
        db.session.commit()
        
        logger.info(f"Pre-existing condition added to patient {patient_id}: {new_condition.diseaseName}")
        return jsonify({'success': True, 'message': 'Condición agregada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding condition: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Delete pre-existing condition
@patients.route('/patient/condition/<int:condition_id>', methods=['DELETE'])
def delete_patient_condition(condition_id):
    """Delete patient pre-existing condition (soft delete)"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        condition = PreExistingCondition.query.filter_by(id=condition_id, is_deleted=False).first()
        if not condition:
            return jsonify({'success': False, 'error': 'Condición no encontrada'}), 404
        
        condition.is_deleted = True
        condition.updated_by = sessionID
        
        db.session.commit()
        
        logger.info(f"Pre-existing condition {condition_id} soft deleted by {sessionID}")
        return jsonify({'success': True, 'message': 'Condición eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting condition: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Add family background to patient
@patients.route('/patient/<int:patient_id>/add-family-background', methods=['POST'])
def add_patient_family_background(patient_id):
    """Add family background to patient"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        
        required_fields = ['familyBackground', 'time', 'degreeRelationship']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
        
        new_background = FamilyBackground(
            familyBackground=data['familyBackground'].strip(),
            time=data['time'],
            degreeRelationship=data['degreeRelationship'],
            idPatient=patient_id,
            created_by=sessionID,
            updated_by=sessionID
        )
        
        db.session.add(new_background)
        db.session.commit()
        
        logger.info(f"Family background added to patient {patient_id}: {new_background.familyBackground}")
        return jsonify({'success': True, 'message': 'Antecedente familiar agregado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding family background: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Delete family background
@patients.route('/patient/family-background/<int:background_id>', methods=['DELETE'])
def delete_patient_family_background(background_id):
    """Delete patient family background (soft delete)"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        background = FamilyBackground.query.filter_by(id=background_id, is_deleted=False).first()
        if not background:
            return jsonify({'success': False, 'error': 'Antecedente no encontrado'}), 404
        
        background.is_deleted = True
        background.updated_by = sessionID
        
        db.session.commit()
        
        logger.info(f"Family background {background_id} soft deleted by {sessionID}")
        return jsonify({'success': True, 'message': 'Antecedente eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting family background: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# Delete patient (soft delete)
@patients.route('/patient/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    """Delete patient (soft delete)"""
    if not session.get('autenticado'):
        return jsonify({'success': False, 'error': 'Sesión no válida'}), 401
    
    doctor_info, sessionID = get_doctor_info_and_session()

    if not sessionID:
        flash('Sesi�n no v�lida', 'error')
        return redirect(url_for('login.index'))
    
    try:
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        # Soft delete patient
        patient.is_deleted = True
        patient.updated_by = sessionID
        db.session.commit()
        
        logger.info(f"Patient {patient_id} soft deleted by {sessionID}")
        return jsonify({'success': True, 'message': 'Paciente eliminado exitosamente'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting patient: {str(e)}")
        return jsonify({'success': False, 'error': f'Error interno del servidor: {str(e)}'}), 500
