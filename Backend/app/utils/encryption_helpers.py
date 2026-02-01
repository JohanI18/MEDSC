"""
Mixins y Helpers para Encriptación de Modelos SQLAlchemy
=========================================================
Proporciona funcionalidades para encriptar/desencriptar automáticamente
campos sensibles al guardar/leer de la base de datos.

Soporta:
- Encriptación Determinística: Para campos que necesitan búsqueda (WHERE campo = valor)
- Encriptación No Determinística: Para datos clínicos sensibles (máxima seguridad)
"""

from typing import List, Dict, Any, Optional
from functools import wraps
import logging

from utils.encryption import (
    encrypt_field,
    decrypt_field,
    encrypt_for_search,
    encrypt_model_data,
    decrypt_model_data,
    get_encryptor,
    DETERMINISTIC_FIELDS,
    NON_DETERMINISTIC_FIELDS,
    SENSITIVE_FIELDS,
    EncryptionError
)

logger = logging.getLogger(__name__)


class EncryptedFieldsMixin:
    """
    Mixin para modelos SQLAlchemy que tienen campos sensibles que deben encriptarse.
    
    Uso:
        class Patient(db.Model, EncryptedFieldsMixin):
            __model_name__ = 'Patient'  # Nombre del modelo para buscar configuración
            ...
            
        # Al guardar
        patient.encrypt_sensitive_data()
        db.session.commit()
        
        # Al leer (en serialización)
        data = patient.to_dict_decrypted()
    """
    
    # Nombre del modelo - sobrescribir en la clase hija
    __model_name__: str = ''
    
    def encrypt_sensitive_data(self) -> 'EncryptedFieldsMixin':
        """
        Encripta todos los campos sensibles del modelo según su configuración.
        - Campos determinísticos: Permiten búsqueda
        - Campos no determinísticos: Máxima seguridad
        
        Retorna self para permitir encadenamiento.
        """
        model_name = self.__model_name__ or self.__class__.__name__
        encryptor = get_encryptor()
        
        # Encriptar campos determinísticos
        if model_name in DETERMINISTIC_FIELDS:
            for field in DETERMINISTIC_FIELDS[model_name]:
                if hasattr(self, field):
                    value = getattr(self, field)
                    if value is not None and not encryptor.is_encrypted(str(value)):
                        try:
                            encrypted_value = encrypt_field(value, model_name, field)
                            setattr(self, field, encrypted_value)
                        except EncryptionError as e:
                            logger.warning(f"No se pudo encriptar {field}: {e}")
        
        # Encriptar campos no determinísticos
        if model_name in NON_DETERMINISTIC_FIELDS:
            for field in NON_DETERMINISTIC_FIELDS[model_name]:
                if hasattr(self, field):
                    value = getattr(self, field)
                    if value is not None and not encryptor.is_encrypted(str(value)):
                        try:
                            encrypted_value = encrypt_field(value, model_name, field)
                            setattr(self, field, encrypted_value)
                        except EncryptionError as e:
                            logger.warning(f"No se pudo encriptar {field}: {e}")
        
        return self
    
    def decrypt_sensitive_data(self) -> 'EncryptedFieldsMixin':
        """
        Desencripta todos los campos sensibles del modelo.
        Retorna self para permitir encadenamiento.
        """
        model_name = self.__model_name__ or self.__class__.__name__
        all_fields = SENSITIVE_FIELDS.get(model_name, [])
        
        for field in all_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value is not None:
                    try:
                        decrypted_value = decrypt_field(value)
                        setattr(self, field, decrypted_value)
                    except EncryptionError:
                        pass  # Mantener valor original
        
        return self
    
    def to_dict_decrypted(self, exclude: List[str] = None) -> Dict[str, Any]:
        """
        Convierte el modelo a diccionario con campos sensibles desencriptados.
        
        Args:
            exclude: Lista de campos a excluir del resultado
            
        Returns:
            Diccionario con los datos del modelo
        """
        exclude = exclude or []
        model_name = self.__model_name__ or self.__class__.__name__
        result = {}
        
        all_sensitive_fields = SENSITIVE_FIELDS.get(model_name, [])
        
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
                
            value = getattr(self, column.name)
            
            # Desencriptar si es un campo sensible
            if column.name in all_sensitive_fields and value is not None:
                try:
                    value = decrypt_field(value)
                except EncryptionError:
                    pass  # Mantener valor original
            
            result[column.name] = value
        
        return result


def encrypt_patient_data(data: dict) -> dict:
    """
    Encripta los datos de un paciente antes de guardar.
    
    Campos determinísticos (permiten búsqueda):
        - identifierCode, email, firstName, lastName1, phoneNumber
    
    Campos no determinísticos (máxima seguridad):
        - address, middleName, lastName2
    """
    return encrypt_model_data('Patient', data)


def decrypt_patient_data(data: dict) -> dict:
    """Desencripta los datos de un paciente para mostrar."""
    return decrypt_model_data('Patient', data)


def encrypt_attention_data(data: dict) -> dict:
    """
    Encripta los datos de una atención médica.
    Todos los campos clínicos usan encriptación no determinística.
    """
    return encrypt_model_data('Attention', data)


def decrypt_attention_data(data: dict) -> dict:
    """Desencripta los datos de una atención médica."""
    return decrypt_model_data('Attention', data)


def encrypt_diagnostic_data(data: dict) -> dict:
    """Encripta datos de diagnóstico (no determinístico)."""
    return encrypt_model_data('Diagnostic', data)


def decrypt_diagnostic_data(data: dict) -> dict:
    """Desencripta datos de diagnóstico."""
    return decrypt_model_data('Diagnostic', data)


def encrypt_treatment_data(data: dict) -> dict:
    """Encripta datos de tratamiento (no determinístico)."""
    return encrypt_model_data('Treatment', data)


def decrypt_treatment_data(data: dict) -> dict:
    """Desencripta datos de tratamiento."""
    return decrypt_model_data('Treatment', data)


def encrypt_allergy_data(data: dict) -> dict:
    """Encripta datos de alergias (no determinístico)."""
    return encrypt_model_data('Allergy', data)


def decrypt_allergy_data(data: dict) -> dict:
    """Desencripta datos de alergias."""
    return decrypt_model_data('Allergy', data)


def encrypt_emergency_contact_data(data: dict) -> dict:
    """Encripta datos de contacto de emergencia (no determinístico)."""
    return encrypt_model_data('EmergencyContact', data)


def decrypt_emergency_contact_data(data: dict) -> dict:
    """Desencripta datos de contacto de emergencia."""
    return decrypt_model_data('EmergencyContact', data)


def encrypt_chat_message(message: str) -> str:
    """Encripta un mensaje de chat (no determinístico)."""
    return encrypt_field(message, 'ChatMessage', 'message')


def decrypt_chat_message(encrypted_message: str) -> str:
    """Desencripta un mensaje de chat."""
    return decrypt_field(encrypted_message)


# ==============================================================================
# DECORADORES PARA RUTAS
# ==============================================================================

def encrypt_request_data(model: str, fields: List[str] = None):
    """
    Decorador para encriptar automáticamente datos del request antes de procesar.
    
    Uso:
        @app.route('/api/patients', methods=['POST'])
        @encrypt_request_data('Patient')
        def create_patient():
            data = request.get_json()  # Ya viene encriptado
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, g
            
            if request.is_json:
                original_data = request.get_json()
                if original_data:
                    # Guardar datos encriptados en g para uso posterior
                    g.encrypted_data = encrypt_model_data(model, original_data)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def decrypt_response_data(model: str):
    """
    Decorador para desencriptar automáticamente datos de respuesta.
    
    Uso:
        @app.route('/api/patients/<id>')
        @decrypt_response_data('Patient')
        def get_patient(id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            
            # Si es un dict o tiene data, desencriptar
            if isinstance(response, dict):
                if 'data' in response:
                    if isinstance(response['data'], list):
                        response['data'] = [
                            decrypt_model_data(model, item) 
                            for item in response['data']
                        ]
                    elif isinstance(response['data'], dict):
                        response['data'] = decrypt_model_data(model, response['data'])
                else:
                    response = decrypt_model_data(model, response)
            
            return response
        return wrapper
    return decorator


# ==============================================================================
# FUNCIONES DE BÚSQUEDA SEGURA
# ==============================================================================

def prepare_search_value(value: str, model: str, field: str) -> str:
    """
    Prepara un valor para búsqueda en campos encriptados.
    
    Si el campo usa encriptación determinística, encripta el valor de búsqueda.
    Si no, retorna el valor original (no se puede buscar en campos no determinísticos).
    
    Args:
        value: Valor a buscar
        model: Nombre del modelo
        field: Nombre del campo
        
    Returns:
        Valor preparado para búsqueda
    """
    if model in DETERMINISTIC_FIELDS and field in DETERMINISTIC_FIELDS[model]:
        return encrypt_for_search(value)
    return value


def search_patient_by_identifier(identifier_code: str):
    """
    Busca un paciente por código de identificación (encriptado).
    
    Args:
        identifier_code: Código de identificación en texto plano
        
    Returns:
        Query preparado para SQLAlchemy
    """
    encrypted_code = encrypt_for_search(identifier_code)
    return encrypted_code


def search_patient_by_email(email: str):
    """
    Busca un paciente por email (encriptado).
    
    Args:
        email: Email en texto plano
        
    Returns:
        Valor encriptado para usar en WHERE
    """
    return encrypt_for_search(email)


def search_patient_by_name(first_name: str = None, last_name: str = None):
    """
    Prepara valores de nombre para búsqueda.
    
    Args:
        first_name: Nombre
        last_name: Apellido
        
    Returns:
        Tupla (first_name_encrypted, last_name_encrypted)
    """
    encrypted_first = encrypt_for_search(first_name) if first_name else None
    encrypted_last = encrypt_for_search(last_name) if last_name else None
    return encrypted_first, encrypted_last

