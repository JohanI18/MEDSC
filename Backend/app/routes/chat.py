from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from models.models_flask import Doctor, ChatMessage
from utils.db import db
import os
import logging
import uuid
import re

chat = Blueprint('chat', __name__)

# Configure logging
logging.basicConfig(level=logging.ERROR)
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

@chat.route('/chat')
def chat_view():
    """Display chat interface"""
    # Verificar autenticación (compatible con Supabase y login local)
    if not session.get('autenticado'):
        return redirect(url_for('clinic.index'))
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    # Get doctor information from session - Adaptado para Supabase
    doctor_info = None
    doctors = []
    
    if session.get('auth_provider') == 'supabase':
        # Para Supabase, creamos información ficticia del doctor
        email = session.get('email', 'Doctor')
        user_id = session.get('user_id', 'demo')
        name_parts = email.split('@')[0].split('.')
        
        doctor_info = {
            'id': user_id,
            'firstName': name_parts[0].capitalize() if len(name_parts) > 0 else 'Doctor',
            'lastName1': name_parts[1].capitalize() if len(name_parts) > 1 else 'Supabase',
            'speciality': 'Medicina General'
        }
        
        # Store doctor ID in session for socket authentication
        session['doctor_id'] = user_id
        session['user_id'] = user_id
        session['user_name'] = f"Dr. {doctor_info['firstName']} {doctor_info['lastName1']}"
        
        if has_database:
            try:
                # Get all doctors from database
                doctors = Doctor.query.filter(Doctor.is_deleted == False).all()
            except Exception as e:
                logger.error(f"Error fetching doctors: {str(e)}")
                doctors = []
        else:
            # Crear doctores de demo para mostrar en el chat
            doctors = [
                type('Doctor', (), {
                    'id': 'demo1',
                    'firstName': 'María',
                    'lastName1': 'González',
                    'speciality': 'Cardiología'
                }),
                type('Doctor', (), {
                    'id': 'demo2',
                    'firstName': 'Carlos',
                    'lastName1': 'Rodríguez',
                    'speciality': 'Neurología'
                }),
                type('Doctor', (), {
                    'id': 'demo3',
                    'firstName': 'Ana',
                    'lastName1': 'López',
                    'speciality': 'Pediatría'
                })
            ]
            
    elif 'cedula' in session and has_database:
        # Código original para login local (solo si hay base de datos)
        try:
            doctor = Doctor.query.filter_by(
                identifierCode=session['cedula'], 
                is_deleted=False
            ).first()
            
            if doctor:
                # Store doctor ID in session for socket authentication
                session['doctor_id'] = doctor.id
                
                doctor_info = {
                    'id': doctor.id,
                    'firstName': doctor.firstName,
                    'lastName1': doctor.lastName1,
                    'speciality': doctor.speciality
                }
                
                # Get all other doctors
                doctors = Doctor.query.filter(
                    Doctor.id != doctor.id,
                    Doctor.is_deleted == False
                ).all()
        except Exception as e:
            logger.error(f"Error fetching doctor info: {str(e)}")
    
    return render_template('chat.html', 
                          doctor_info=doctor_info, 
                          doctors=doctors,
                          view='chat')

@chat.route('/get-messages/<int:doctor_id>', methods=['GET'])
def get_messages(doctor_id):
    """Get messages between current doctor and selected doctor"""
    user_id = session.get('doctor_id') or session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if not has_database:
        # En modo demo, retornar mensajes vacíos
        return jsonify({
            'messages': [],
            'demo_mode': True
        })
    
    try:
        # Get messages between the two doctors
        messages = ChatMessage.query.filter(
            ((ChatMessage.sender_id == user_id) & 
             (ChatMessage.receiver_id == doctor_id)) |
            ((ChatMessage.sender_id == doctor_id) & 
             (ChatMessage.receiver_id == user_id))
        ).order_by(ChatMessage.timestamp).all()
        
        # Mark messages as read
        unread_messages = ChatMessage.query.filter_by(
            sender_id=doctor_id,
            receiver_id=user_id,
            is_read=False
        ).all()
        
        for msg in unread_messages:
            msg.is_read = True
        
        db.session.commit()
        
        # Format messages for JSON response
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_mine': msg.sender_id == user_id
            })
        
        return jsonify({'messages': messages_data})
    
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        return jsonify({'error': 'Error al obtener mensajes'}), 500

@chat.route('/get-messages-uuid/<receiver_id>', methods=['GET'])
def get_messages_uuid(receiver_id):
    """Get messages between current doctor and selected doctor using Supabase UUIDs"""
    logger.info(f"=== GET MESSAGES UUID REQUEST ===")
    logger.info(f"Receiver ID: {receiver_id}")
    logger.info(f"Session contents: {dict(session)}")
    
    # Obtener Supabase ID del usuario actual
    sender_supabase_id = session.get('user_id') or session.get('supabase_id')
    
    logger.info(f"Sender supabase_id: {sender_supabase_id}")
    
    if not sender_supabase_id:
        logger.error("No Supabase ID found in session")
        return jsonify({'error': 'No autorizado'}), 401
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if not has_database:
        logger.info("Database not available, returning empty messages")
        return jsonify({
            'messages': [],
            'demo_mode': True
        })
    
    try:
        # Determinar si receiver_id es un UUID o un ID numérico
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        is_uuid = bool(re.match(uuid_pattern, receiver_id, re.IGNORECASE))
        
        logger.info(f"Receiver ID is UUID: {is_uuid}")
        
        # Buscar mensajes usando los campos de Supabase ID
        if is_uuid:
            # Ambos son UUIDs - usar campos sender_supabase_id y receiver_supabase_id
            logger.info(f"Searching UUID messages between sender={sender_supabase_id} and receiver={receiver_id}")
            
            messages = ChatMessage.query.filter(
                ((ChatMessage.sender_supabase_id == sender_supabase_id) & 
                 (ChatMessage.receiver_supabase_id == receiver_id)) |
                ((ChatMessage.sender_supabase_id == receiver_id) & 
                 (ChatMessage.receiver_supabase_id == sender_supabase_id))
            ).order_by(ChatMessage.timestamp).all()
            
            logger.info(f"UUID query found {len(messages)} messages")
            
            # También buscar en mensajes antiguos que puedan usar IDs numéricos
            # Obtener el doctor_id numérico del receptor si existe
            receiver_doctor = Doctor.query.filter_by(supabase_id=receiver_id).first()
            receiver_doctor_id = receiver_doctor.id if receiver_doctor else None
            
            # Obtener el doctor_id numérico del sender si existe  
            sender_doctor = Doctor.query.filter_by(supabase_id=sender_supabase_id).first()
            sender_doctor_id = sender_doctor.id if sender_doctor else None
            
            logger.info(f"Doctor IDs - sender_doctor_id: {sender_doctor_id}, receiver_doctor_id: {receiver_doctor_id}")
            
            # Buscar mensajes antiguos con IDs numéricos
            if sender_doctor_id and receiver_doctor_id:
                numeric_messages = ChatMessage.query.filter(
                    ((ChatMessage.sender_id == sender_doctor_id) & 
                     (ChatMessage.receiver_id == receiver_doctor_id)) |
                    ((ChatMessage.sender_id == receiver_doctor_id) & 
                     (ChatMessage.receiver_id == sender_doctor_id))
                ).filter(
                    # Solo mensajes que no tengan supabase_ids (mensajes antiguos)
                    (ChatMessage.sender_supabase_id.is_(None)) | 
                    (ChatMessage.receiver_supabase_id.is_(None))
                ).order_by(ChatMessage.timestamp).all()
                
                logger.info(f"Found {len(numeric_messages)} additional numeric messages")
                messages.extend(numeric_messages)
                messages.sort(key=lambda x: x.timestamp)  # Re-ordenar por timestamp
            
            logger.info(f"Total messages found: {len(messages)}")
            
            # Marcar mensajes como leídos (tanto UUID como numéricos)
            unread_messages = []
            
            # Mensajes UUID no leídos
            unread_uuid = ChatMessage.query.filter_by(
                sender_supabase_id=receiver_id,
                receiver_supabase_id=sender_supabase_id,
                is_read=False
            ).all()
            unread_messages.extend(unread_uuid)
            
            # Mensajes numéricos no leídos (si tenemos los IDs)
            if sender_doctor_id and receiver_doctor_id:
                unread_numeric = ChatMessage.query.filter_by(
                    sender_id=receiver_doctor_id,
                    receiver_id=sender_doctor_id,
                    is_read=False
                ).filter(
                    (ChatMessage.sender_supabase_id.is_(None)) | 
                    (ChatMessage.receiver_supabase_id.is_(None))
                ).all()
                unread_messages.extend(unread_numeric)
            
        else:
            # receiver_id es numérico, sender es UUID - búsqueda mixta
            messages = ChatMessage.query.filter(
                ((ChatMessage.sender_supabase_id == sender_supabase_id) & 
                 (ChatMessage.receiver_id == int(receiver_id))) |
                ((ChatMessage.sender_id == int(receiver_id)) & 
                 (ChatMessage.receiver_supabase_id == sender_supabase_id))
            ).order_by(ChatMessage.timestamp).all()
            
            logger.info(f"Mixed query found {len(messages)} messages")
            
            # Marcar mensajes como leídos
            unread_messages = ChatMessage.query.filter_by(
                sender_id=int(receiver_id),
                receiver_supabase_id=sender_supabase_id,
                is_read=False
            ).all()
        
        for msg in unread_messages:
            msg.is_read = True
        
        db.session.commit()
        logger.info(f"Marked {len(unread_messages)} messages as read")
        
        # Formatear mensajes para respuesta JSON
        messages_data = []
        for msg in messages:
            # Determinar si el mensaje es mío comparando Supabase IDs
            is_mine = (msg.sender_supabase_id == sender_supabase_id if msg.sender_supabase_id else 
                      str(msg.sender_id) == str(session.get('doctor_id')))
            
            messages_data.append({
                'id': msg.id,
                'sender_id': msg.sender_supabase_id or str(msg.sender_id),
                'receiver_id': msg.receiver_supabase_id or str(msg.receiver_id),
                'sender_name': 'Tú' if is_mine else f'Doctor {msg.sender_supabase_id or msg.sender_id}',
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_mine': is_mine
            })
        
        logger.info(f"Returning {len(messages_data)} formatted messages")
        return jsonify({'messages': messages_data})
    
    except Exception as e:
        logger.error(f"Error getting messages with UUID: {str(e)}")
        return jsonify({'error': 'Error al obtener mensajes'}), 500

@chat.route('/send-message', methods=['POST'])
def send_message():
    """Send a message to another doctor (fallback for socket)"""
    logger.info(f"=== SEND MESSAGE REQUEST ===")
    logger.info(f"Session contents: {dict(session)}")
    
    # Obtener Supabase ID del usuario actual
    sender_supabase_id = session.get('user_id') or session.get('supabase_id')
    sender_doctor_id = session.get('doctor_id')
    
    logger.info(f"Sender - supabase_id: {sender_supabase_id}, doctor_id: {sender_doctor_id}")
    
    if not sender_supabase_id:
        logger.error("No supabase_id found in session")
        return jsonify({'error': 'No autorizado'}), 401
    
    request_data = request.get_json()
    logger.info(f"Request data: {request_data}")
    
    receiver_identifier = request_data.get('receiver_id')  # Puede ser supabase_id o doctor_id
    message_text = request_data.get('message')
    
    logger.info(f"receiver_identifier: {receiver_identifier}, message: {message_text}")
    
    if not receiver_identifier or not message_text:
        logger.error("Missing receiver_identifier or message_text")
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Determinar si el receiver_identifier es un Supabase ID (UUID) o un doctor_id
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    if re.match(uuid_pattern, receiver_identifier, re.IGNORECASE):
        # Es un UUID de Supabase - buscar el doctor por supabase_id
        receiver_supabase_id = receiver_identifier
        from models.models_flask import Doctor
        doctor_by_supabase = Doctor.query.filter_by(supabase_id=receiver_identifier, is_deleted=False).first()
        receiver_doctor_id = doctor_by_supabase.id if doctor_by_supabase else None
    else:
        # Es un doctor_id, verificar si existe en la DB
        try:
            doctor_id_int = int(receiver_identifier)
            # Verificar si el doctor existe en la base de datos
            from models.models_flask import Doctor
            doctor_exists = Doctor.query.filter_by(id=doctor_id_int, is_deleted=False).first()
            
            if doctor_exists:
                # Usar el Supabase ID real del doctor si existe, sino generar uno temporal
                receiver_supabase_id = doctor_exists.supabase_id if doctor_exists.supabase_id else str(uuid.uuid4())
                receiver_doctor_id = doctor_id_int
            else:
                # Doctor no existe, generar UUID para usuario demo
                import uuid
                receiver_supabase_id = str(uuid.uuid4())
                receiver_doctor_id = None
        except (ValueError, TypeError):
            logger.error(f"Invalid receiver_identifier: {receiver_identifier}")
            return jsonify({'error': 'Identificador de receptor inválido'}), 400
    
    # Verificar si el sender existe en la DB
    sender_doctor_id = session.get('doctor_id')
    from models.models_flask import Doctor
    if sender_doctor_id:
        sender_exists = Doctor.query.filter_by(id=sender_doctor_id, is_deleted=False).first()
        if not sender_exists:
            sender_doctor_id = None  # No existe en la DB
    
    logger.info(f"Final IDs - sender_supabase: {sender_supabase_id}, receiver_supabase: {receiver_supabase_id}")
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    logger.info(f"Has database: {has_database}")
    
    if not has_database:
        # En modo demo, simular envío exitoso
        import datetime
        logger.info("Using demo mode - returning mock response")
        return jsonify({
            'id': f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            'sender_id': sender_supabase_id,
            'receiver_id': receiver_supabase_id,
            'message': message_text,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'demo_mode': True
        })
    
    try:
        logger.info("Attempting to save message to database")
        # Save message to database usando Supabase IDs
        # Para usuarios demo, usar solo Supabase IDs y dejar doctor_id como None
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        new_message = ChatMessage(
            sender_id=None if re.match(uuid_pattern, sender_supabase_id, re.IGNORECASE) else sender_doctor_id,
            receiver_id=None if re.match(uuid_pattern, receiver_supabase_id, re.IGNORECASE) else receiver_doctor_id,
            sender_supabase_id=sender_supabase_id,
            receiver_supabase_id=receiver_supabase_id,
            message=message_text,
            created_by=sender_supabase_id  # Usar el Supabase ID del remitente como created_by
        )
        
        db.session.add(new_message)
        db.session.commit()
        logger.info(f"Message saved successfully with ID: {new_message.id}")
        
        # Return success response
        return jsonify({
            'id': new_message.id,
            'sender_id': sender_supabase_id,
            'receiver_id': receiver_supabase_id,
            'message': message_text,
            'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_mine': True
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': 'Error al enviar mensaje'}), 500

@chat.route('/get-unread-counts', methods=['GET'])
def get_unread_counts():
    """Get unread message counts for all doctors"""
    user_id = session.get('doctor_id') or session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if not has_database:
        # En modo demo, retornar conteos vacíos
        return jsonify({
            'unread_counts': {},
            'demo_mode': True
        })
    
    try:
        # Get all doctors
        doctors = Doctor.query.filter(
            Doctor.id != user_id,
            Doctor.is_deleted == False
        ).all()
        
        # Get unread counts for each doctor
        unread_counts = {}
        for doctor in doctors:
            count = ChatMessage.query.filter_by(
                sender_id=doctor.id,
                receiver_id=user_id,
                is_read=False
            ).count()
            
            unread_counts[str(doctor.id)] = count
        
        return jsonify({'unread_counts': unread_counts})
        
    except Exception as e:
        logger.error(f"Error getting unread counts: {str(e)}")
        return jsonify({'error': 'Error al obtener conteos de mensajes'}), 500

@chat.route('/demo-login', methods=['POST'])
def demo_login():
    """Login temporal para pruebas de chat"""
    try:
        # Limpiar sesión anterior
        session.clear()
        
        user_data = request.get_json()
        user_name = user_data.get('name', 'Demo User')
        
        logger.info(f"Demo login attempt for user: {user_name}")
        
        # Verificar si tenemos conexión a la base de datos
        has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
        
        if has_database:
            # Buscar un doctor real en la base de datos que tenga supabase_id
            doctor = Doctor.query.filter(
                Doctor.supabase_id.isnot(None),
                Doctor.is_deleted == False
            ).first()
            
            if doctor:
                # Usar un doctor real de la base de datos
                session['autenticado'] = True
                session['auth_provider'] = 'demo'
                session['user_id'] = doctor.supabase_id  # Usar el supabase_id real
                session['doctor_id'] = doctor.id  # ID numérico real
                session['supabase_id'] = doctor.supabase_id
                session['user_name'] = f"{doctor.firstName} {doctor.lastName1}"
                session['email'] = getattr(doctor, 'email', f"{doctor.firstName.lower()}.{doctor.lastName1.lower()}@hospital.com")
                
                logger.info(f"Demo login successful using real doctor {doctor.id}. Session: {dict(session)}")
                
                return jsonify({
                    'success': True,
                    'user_id': doctor.supabase_id,
                    'doctor_id': doctor.id,
                    'name': f"{doctor.firstName} {doctor.lastName1}"
                })
            else:
                logger.error("No doctors with supabase_id found in database for demo login")
                return jsonify({'error': 'No hay doctores disponibles para demo'}), 400
        else:
            # Sin base de datos, crear sesión básica sin UUID real
            session['autenticado'] = True
            session['auth_provider'] = 'demo_no_db'
            session['user_id'] = 'demo_user_no_db'
            session['doctor_id'] = 999  # ID demo que no conflicte
            session['user_name'] = user_name
            session['email'] = "demo@demo.com"
            
            logger.info(f"Demo login without database. Session: {dict(session)}")
            
            return jsonify({
                'success': True,
                'user_id': 'demo_user_no_db',
                'doctor_id': 999,
                'name': user_name
            })
        
    except Exception as e:
        logger.error(f"Error in demo login: {str(e)}")
        return jsonify({'error': 'Error en login demo'}), 500

@chat.route('/logout', methods=['POST'])
def logout():
    """Limpiar sesión"""
    session.clear()
    return jsonify({'success': True, 'message': 'Sesión limpiada'})

@chat.route('/get-chat-doctors', methods=['GET'])
def get_chat_doctors():
    """Get list of all doctors for chat"""
    user_id = session.get('doctor_id') or session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
    
    logger.info(f"Getting chat doctors. Session: {dict(session)}")
    
    # Verificar si tenemos conexión a la base de datos
    has_database = os.environ.get('USE_DATABASE', 'false').lower() == 'true' and check_database_connection()
    
    if not has_database:
        # En modo demo, retornar doctores demo con UUIDs reales
        import uuid
        demo_doctors = [
            {
                'id': 1,
                'supabase_id': str(uuid.uuid4()),
                'firstName': 'Juan',
                'lastName1': 'Pérez',
                'speciality': 'Cardiología',
                'email': 'juan.perez@hospital.com'
            },
            {
                'id': 2,
                'supabase_id': str(uuid.uuid4()),
                'firstName': 'María',
                'lastName1': 'González',
                'speciality': 'Neurología',
                'email': 'maria.gonzalez@hospital.com'
            },
            {
                'id': 3,
                'supabase_id': str(uuid.uuid4()),
                'firstName': 'Carlos',
                'lastName1': 'López',
                'speciality': 'Pediatría',
                'email': 'carlos.lopez@hospital.com'
            }
        ]
        return jsonify({
            'doctors': demo_doctors,
            'demo_mode': True
        })
    
    try:
        # Obtener información del usuario actual
        current_user_doctor_id = session.get('doctor_id')  # ID numérico para comparar con DB
        current_user_supabase_id = session.get('user_id') or session.get('supabase_id')  # UUID de Supabase
        
        logger.info(f"Current user - doctor_id: {current_user_doctor_id}, supabase_id: {current_user_supabase_id}")
        
        # Si no tenemos doctor_id numérico, intentar encontrarlo usando el supabase_id
        if not current_user_doctor_id and current_user_supabase_id:
            # Buscar el doctor por supabase_id
            current_doctor = Doctor.query.filter_by(supabase_id=current_user_supabase_id).first()
            if current_doctor:
                current_user_doctor_id = current_doctor.id
                session['doctor_id'] = current_user_doctor_id  # Actualizar la sesión
                logger.info(f"Found doctor_id {current_user_doctor_id} for supabase_id {current_user_supabase_id}")
        
        # Get all doctors except the current user
        if current_user_doctor_id:
            doctors = Doctor.query.filter(
                Doctor.id != current_user_doctor_id,
                Doctor.is_deleted == False
            ).all()
        else:
            # Si no podemos determinar el usuario actual, devolver todos los doctores
            doctors = Doctor.query.filter(Doctor.is_deleted == False).all()
        
        logger.info(f"Found {len(doctors)} doctors to show in chat")
        
        doctors_data = []
        
        for doctor in doctors:
            # Solo incluir doctores que YA TENGAN supabase_id en la base de datos
            if doctor.supabase_id:  # Solo si ya existe
                doctors_data.append({
                    'id': doctor.id,
                    'supabase_id': doctor.supabase_id,  # Usar el existente
                    'firstName': doctor.firstName,
                    'lastName1': doctor.lastName1,
                    'speciality': doctor.speciality,
                    'email': getattr(doctor, 'email', f"{doctor.firstName.lower()}.{doctor.lastName1.lower()}@hospital.com")
                })
                logger.info(f"Added doctor {doctor.id} with existing supabase_id: {doctor.supabase_id}")
            else:
                logger.warning(f"Skipping doctor {doctor.id} ({doctor.firstName} {doctor.lastName1}) - no supabase_id")
        
        logger.info(f"Returning {len(doctors_data)} doctors with supabase_id")
        return jsonify({'doctors': doctors_data})
        
    except Exception as e:
        logger.error(f"Error getting doctors: {str(e)}")
        return jsonify({'error': 'Error al obtener doctores'}), 500

