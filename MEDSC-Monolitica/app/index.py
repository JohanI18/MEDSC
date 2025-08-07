from app import create_app, socketio
import os
from flask import session
from flask_socketio import emit, join_room, leave_room
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación usando la función factory
app = create_app()

app = create_app()

# Solo crear tablas si estamos usando base de datos
if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
    from utils.db import db
    from models.models_flask import ChatMessage, Doctor
    
    with app.app_context():
        db.create_all()  # Ensure all models are created in the database
else:
    print("🚀 Modo Supabase-only: Base de datos deshabilitada")
    # Importamos los modelos pero no creamos tablas
    try:
        from models.models_flask import ChatMessage, Doctor
    except ImportError:
        print("⚠️ Modelos no disponibles en modo Supabase-only")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
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

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
    if user_id:
        leave_room(f"user_{user_id}")
        logger.info(f"User {user_id} disconnected")
        
        # Notify others that user is offline usando Supabase ID
        emit('user_status', {
            'user_id': user_id,
            'status': 'offline'
        }, broadcast=True, include_self=False)

@socketio.on('send_message')
def handle_message(data):
    user_id = session.get('user_id') or session.get('supabase_id') or session.get('doctor_id')
    if not user_id:
        return
    
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    
    if not receiver_id or not message_text:
        return
    
    try:
        # En modo Supabase, solo manejamos mensajes en tiempo real
        if os.environ.get('USE_DATABASE', 'false').lower() == 'true':
            # Para usuarios demo, no intentar guardar en DB con FK
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            
            if re.match(uuid_pattern, str(user_id), re.IGNORECASE):
                # Modo demo con DB - usar Supabase IDs únicamente
                import datetime
                sender_name = session.get('user_name', 'Usuario Demo')
                message_id = f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Usuario real con DB
                new_message = ChatMessage(
                    sender_id=session.get('doctor_id'),  # ID numérico para FK
                    receiver_id=int(receiver_id) if receiver_id.isdigit() else None,
                    sender_supabase_id=user_id,
                    receiver_supabase_id=receiver_id,
                    message=message_text,
                    created_by=user_id
                )
                
                from utils.db import db
                db.session.add(new_message)
                db.session.commit()
                
                # Get sender info
                sender = Doctor.query.get(session.get('doctor_id'))
                sender_name = f"{sender.firstName} {sender.lastName1}" if sender else session.get('user_name', 'Usuario')
                message_id = new_message.id
                timestamp = new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Modo demo sin DB
            import datetime
            sender_name = session.get('user_name', 'Usuario Demo')
            message_id = f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Send to receiver's room usando Supabase ID
        emit('new_message', {
            'id': message_id,
            'sender_id': user_id,  # Usar Supabase ID
            'sender_name': sender_name,
            'message': message_text,
            'timestamp': timestamp,
            'is_mine': False
        }, room=f"user_{receiver_id}")
        
        # Send confirmation to sender
        emit('message_sent', {
            'id': message_id,
            'receiver_id': receiver_id,
            'message': message_text,
            'timestamp': timestamp
        })
        
        logger.info(f"Message sent from {user_id} to {receiver_id}")
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        emit('message_error', {'error': 'Error al enviar mensaje'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)