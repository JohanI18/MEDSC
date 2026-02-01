from app import create_app, socketio
import os
from flask import session
from flask_socketio import emit, join_room, leave_room
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio padre
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Crear la aplicación usando la función factory
app = create_app()

# Solo crear tablas si estamos usando base de datos
if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
    from utils.db import db
    from models.models_flask import ChatMessage, Doctor
    
    with app.app_context():
        db.create_all()  # Ensure all models are created in the database
else:
    # Importamos los modelos pero no creamos tablas
    try:
        from models.models_flask import ChatMessage, Doctor
    except ImportError:
        pass

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"Socket.IO error: {str(e)}")
    return False

@socketio.on('connect')
def handle_connect():
    try:
        user_id = get_current_user_id()
        if user_id:
            join_room(f"user_{user_id}")
            
            # Notify others that user is online usando Supabase ID
            emit('user_status', {
                'user_id': user_id,
                'status': 'online'
            }, broadcast=True, include_self=False)
    except Exception as e:
        logger.error(f"Error in connect handler: {str(e)}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    try:
        user_id = get_current_user_id()
        if user_id:
            leave_room(f"user_{user_id}")
            
            # Notify others that user is offline usando Supabase ID
            emit('user_status', {
                'user_id': user_id,
                'status': 'offline'
            }, broadcast=True, include_self=False)
    except Exception as e:
        logger.error(f"Error in disconnect handler: {str(e)}")
        return False

def get_current_user_id():
    """Obtiene el ID del usuario actual desde la sesión"""
    return session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')


def save_message_to_db(user_id, receiver_id, message_text):
    """Guarda el mensaje en la base de datos y retorna (message_id, timestamp, sender_name)"""
    import re
    from utils.db import db
    
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    is_uuid = re.match(uuid_pattern, str(user_id), re.IGNORECASE)
    
    new_message = ChatMessage(
        sender_id=session.get('doctor_id') if not is_uuid else None,
        receiver_id=int(receiver_id) if receiver_id.isdigit() else None,
        sender_supabase_id=user_id,
        receiver_supabase_id=receiver_id,
        message=message_text,
        created_by=user_id
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    sender_name = get_sender_name_from_db()
    
    return new_message.id, new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'), sender_name


def get_sender_name_from_db():
    """Obtiene el nombre del remitente desde la base de datos"""
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return session.get('user_name', 'Usuario')
    
    sender = Doctor.query.get(doctor_id)
    if sender:
        return f"{sender.firstName} {sender.lastName1}"
    return session.get('user_name', 'Usuario')


def create_demo_message_info():
    """Crea información de mensaje para modo demo sin DB"""
    import datetime
    now = datetime.datetime.now()
    return f"demo_{now.strftime('%Y%m%d%H%M%S')}", now.strftime('%Y-%m-%d %H:%M:%S')


def emit_message_events(user_id, receiver_id, message_text, message_id, timestamp, sender_name):
    """Emite todos los eventos de Socket.IO relacionados con el mensaje"""
    message_data = {
        'id': message_id,
        'sender_id': user_id,
        'sender_name': sender_name,
        'message': message_text,
        'timestamp': timestamp,
        'is_mine': False
    }
    
    emit('new_message', message_data, room=f"user_{receiver_id}")
    
    emit('message_sent', {
        'id': message_id,
        'receiver_id': receiver_id,
        'message': message_text,
        'timestamp': timestamp,
        'success': True
    })
    
    message_preview = message_text[:50] + ('...' if len(message_text) > 50 else '')
    emit('unread_message', {
        'sender_id': user_id,
        'sender_name': sender_name,
        'message_preview': message_preview,
        'timestamp': timestamp
    }, room=f"user_{receiver_id}")


@socketio.on('send_message')
def handle_message(data):
    user_id = get_current_user_id()
    if not user_id:
        emit('message_error', {'error': 'Usuario no autenticado'})
        return
    
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    
    if not receiver_id or not message_text:
        emit('message_error', {'error': 'Datos incompletos'})
        return
    
    try:
        if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
            message_id, timestamp, sender_name = save_message_to_db(user_id, receiver_id, message_text)
        else:
            message_id, timestamp = create_demo_message_info()
            sender_name = session.get('user_name', 'Usuario')
        
        emit_message_events(user_id, receiver_id, message_text, message_id, timestamp, sender_name)
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        emit('message_error', {'error': 'Error al enviar mensaje'})

@socketio.on('typing')
def handle_typing(data):
    user_id = get_current_user_id()
    if not user_id:
        return
    
    receiver_id = data.get('receiver_id')
    is_typing = data.get('is_typing', False)
    
    if not receiver_id:
        return
    
    try:
        # Enviar indicador de typing al receptor
        emit('user_typing', {
            'user_id': user_id,
            'is_typing': is_typing
        }, room=f"user_{receiver_id}")
        
    except Exception as e:
        logger.error(f"Error sending typing indicator: {str(e)}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
