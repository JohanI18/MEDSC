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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"Socket.IO error: {str(e)}")
    return False

@socketio.on('connect')
def handle_connect():
    try:
        # Priorizar Supabase ID sobre doctor_id
        user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
        if user_id:
            join_room(f"user_{user_id}")
            logger.info(f"User {user_id} connected")
            
            # Notify others that user is online usando Supabase ID
            emit('user_status', {
                'user_id': user_id,
                'status': 'online'
            }, broadcast=True, include_self=False)
        else:
            logger.warning("User connected without valid session")
    except Exception as e:
        logger.error(f"Error in connect handler: {str(e)}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    try:
        user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
        if user_id:
            leave_room(f"user_{user_id}")
            logger.info(f"User {user_id} disconnected")
            
            # Notify others that user is offline usando Supabase ID
            emit('user_status', {
                'user_id': user_id,
                'status': 'offline'
            }, broadcast=True, include_self=False)
        else:
            logger.warning("User disconnected without valid session")
    except Exception as e:
        logger.error(f"Error in disconnect handler: {str(e)}")
        return False

@socketio.on('send_message')
def handle_message(data):
    user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
    if not user_id:
        emit('message_error', {'error': 'Usuario no autenticado'})
        return
    
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    
    if not receiver_id or not message_text:
        emit('message_error', {'error': 'Datos incompletos'})
        return
    
    try:
        # Obtener información del usuario actual
        sender_name = session.get('user_name', 'Usuario')
        message_id = None
        timestamp = None
        
        # En modo Supabase, guardar mensaje en DB si está disponible
        if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            
            # Crear mensaje en base de datos
            new_message = ChatMessage(
                sender_id=session.get('doctor_id') if not re.match(uuid_pattern, str(user_id), re.IGNORECASE) else None,
                receiver_id=None,  # Lo establecemos después si es numérico
                sender_supabase_id=user_id,
                receiver_supabase_id=receiver_id,
                message=message_text,
                created_by=user_id
            )
            
            # Si el receiver_id es numérico, intentar establecerlo
            if receiver_id.isdigit():
                new_message.receiver_id = int(receiver_id)
            
            from utils.db import db
            db.session.add(new_message)
            db.session.commit()
            
            # Obtener información del remitente si existe
            if session.get('doctor_id'):
                sender = Doctor.query.get(session.get('doctor_id'))
                if sender:
                    sender_name = f"{sender.firstName} {sender.lastName1}"
            
            message_id = new_message.id
            timestamp = new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Modo demo sin DB
            import datetime
            message_id = f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Crear objeto de mensaje para enviar
        message_data = {
            'id': message_id,
            'sender_id': user_id,
            'sender_name': sender_name,
            'message': message_text,
            'timestamp': timestamp,
            'is_mine': False
        }
        
        # Enviar a la sala del receptor
        emit('new_message', message_data, room=f"user_{receiver_id}")
        
        # Notificar al remitente que el mensaje fue enviado
        emit('message_sent', {
            'id': message_id,
            'receiver_id': receiver_id,
            'message': message_text,
            'timestamp': timestamp,
            'success': True
        })
        
        # Emitir notificación de mensaje no leído al receptor
        emit('unread_message', {
            'sender_id': user_id,
            'sender_name': sender_name,
            'message_preview': message_text[:50] + ('...' if len(message_text) > 50 else ''),
            'timestamp': timestamp
        }, room=f"user_{receiver_id}")
        
        logger.info(f"Message sent from {user_id} to {receiver_id}")
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        emit('message_error', {'error': 'Error al enviar mensaje'})

@socketio.on('typing')
def handle_typing(data):
    user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
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
        
        logger.info(f"Typing indicator: {user_id} -> {receiver_id} (typing: {is_typing})")
        
    except Exception as e:
        logger.error(f"Error sending typing indicator: {str(e)}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
