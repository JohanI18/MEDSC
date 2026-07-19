"""
Módulo de Encriptación para Datos Sensibles Médicos
====================================================
Soporta dos tipos de encriptación:

1. DETERMINÍSTICA (AES-SIV): Para campos que necesitan búsqueda
   - Mismo input = mismo output (permite WHERE campo = valor)
   - Usada para: email, identifierCode, firstName, lastName1, phoneNumber

2. NO DETERMINÍSTICA (Fernet/AES-CBC): Para datos clínicos sensibles
   - Mismo input = diferente output cada vez (máxima seguridad)
   - Usada para: diagnósticos, tratamientos, notas clínicas, etc.

IMPORTANTE: 
- Si pierdes la clave de encriptación, los datos encriptados serán irrecuperables.
- Nunca expongas la clave de encriptación en logs o mensajes de error.
- En producción, considera usar un Key Management Service (KMS).
"""

import os
import base64
import hashlib
import hmac
from typing import Optional, Union, Literal
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionError(Exception):
    """Excepción personalizada para errores de encriptación"""
    pass


# Tipo de encriptación
EncryptionType = Literal['deterministic', 'non_deterministic']


class MedicalDataEncryption:
    """
    Clase para manejar encriptación de datos médicos sensibles.
    
    Soporta dos modos:
    - Determinístico: Para campos que necesitan búsqueda (AES-SIV)
    - No Determinístico: Para datos sensibles que no necesitan búsqueda (Fernet)
    
    Uso:
        encryptor = MedicalDataEncryption()
        
        # Encriptación determinística (para búsquedas)
        encrypted = encryptor.encrypt("email@test.com", deterministic=True)
        
        # Encriptación no determinística (máxima seguridad)
        encrypted = encryptor.encrypt("Diagnóstico confidencial", deterministic=False)
    """
    
    _instance: Optional['MedicalDataEncryption'] = None
    _fernet: Optional[Fernet] = None
    _aes_siv: Optional[AESSIV] = None
    _deterministic_key: Optional[bytes] = None
    
    def __new__(cls):
        """Singleton pattern para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Inicializa las instancias de encriptación"""
        encryption_key = os.getenv('ENCRYPTION_KEY')
        encryption_salt = os.getenv('ENCRYPTION_SALT')
        
        if not encryption_key:
            raise EncryptionError(
                "ENCRYPTION_KEY no está definida en las variables de entorno. "
                "Genera una con: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        
        if not encryption_salt:
            raise EncryptionError(
                "ENCRYPTION_SALT no está definida en las variables de entorno. "
                "Genera una con: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        try:
            # Fernet para encriptación no determinística
            self._fernet = Fernet(encryption_key.encode())
            
            # Derivar clave para AES-SIV (encriptación determinística)
            # AES-SIV requiere una clave de 256 bits (32 bytes) o 512 bits (64 bytes)
            # Usamos PBKDF2 para derivar una clave consistente
            key_bytes = base64.urlsafe_b64decode(encryption_key.encode())
            
            # Convertir salt de hex string a bytes
            salt_bytes = bytes.fromhex(encryption_salt)
            
            # Derivar clave de 512 bits para AES-SIV (requiere 64 bytes)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=64,  # 512 bits para AES-256-SIV
                salt=salt_bytes,  # Salt desde variable de entorno
                iterations=100000,
            )
            self._deterministic_key = kdf.derive(key_bytes)
            self._aes_siv = AESSIV(self._deterministic_key)
            
        except Exception as e:
            raise EncryptionError(f"Error inicializando encriptación: {str(e)}")
    
    def encrypt(self, plaintext: Union[str, None], deterministic: bool = False) -> Optional[str]:
        """
        Encripta un texto plano.
        
        Args:
            plaintext: Texto a encriptar (puede ser None)
            deterministic: Si True, usa encriptación determinística (permite búsqueda)
            
        Returns:
            Texto encriptado en base64 o None si el input es None
        """
        if plaintext is None:
            return None
        
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        
        if not plaintext:  # String vacío
            return plaintext
        
        try:
            if deterministic:
                # Encriptación determinística con AES-SIV
                # Prefijo 'D:' para identificar datos encriptados de forma determinística
                encrypted_bytes = self._aes_siv.encrypt(
                    plaintext.encode('utf-8'),
                    associated_data=None
                )
                return 'D:' + base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            else:
                # Encriptación no determinística con Fernet
                # Prefijo 'N:' para identificar datos encriptados de forma no determinística
                encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
                return 'N:' + encrypted_bytes.decode('utf-8')
                
        except Exception as e:
            raise EncryptionError(f"Error al encriptar: {str(e)}")
    
    def decrypt(self, ciphertext: Union[str, None]) -> Optional[str]:
        """
        Desencripta un texto cifrado. Detecta automáticamente el tipo de encriptación.
        
        Args:
            ciphertext: Texto encriptado (puede ser None)
            
        Returns:
            Texto desencriptado o None si el input es None
        """
        if ciphertext is None:
            return None
        
        if not ciphertext:  # String vacío
            return ciphertext
        
        try:
            if ciphertext.startswith('D:'):
                # Desencriptar dato determinístico
                encrypted_data = base64.urlsafe_b64decode(ciphertext[2:].encode('utf-8'))
                decrypted_bytes = self._aes_siv.decrypt(encrypted_data, associated_data=None)
                return decrypted_bytes.decode('utf-8')
                
            elif ciphertext.startswith('N:'):
                # Desencriptar dato no determinístico (Fernet)
                decrypted_bytes = self._fernet.decrypt(ciphertext[2:].encode('utf-8'))
                return decrypted_bytes.decode('utf-8')
                
            elif ciphertext.startswith('gAAAAA'):
                # Formato Fernet legacy (sin prefijo)
                decrypted_bytes = self._fernet.decrypt(ciphertext.encode('utf-8'))
                return decrypted_bytes.decode('utf-8')
            
            else:
                # No está encriptado, retornar tal cual
                return ciphertext
                
        except InvalidToken:
            raise EncryptionError(
                "No se pudo desencriptar el dato. "
                "Posible clave incorrecta o dato corrupto."
            )
        except Exception as e:
            # Si falla la desencriptación, puede ser un dato no encriptado
            return ciphertext
    
    def is_encrypted(self, value: str) -> bool:
        """
        Verifica si un valor está encriptado.
        """
        if not isinstance(value, str):
            return False
        return (
            value.startswith('D:') or 
            value.startswith('N:') or 
            (value.startswith('gAAAAA') and len(value) > 50)
        )
    
    def encrypt_for_search(self, plaintext: Union[str, None]) -> Optional[str]:
        """
        Encripta un valor para búsqueda (determinístico).
        Útil para buscar en la base de datos.
        
        Args:
            plaintext: Texto a encriptar para búsqueda
            
        Returns:
            Texto encriptado de forma determinística
        """
        return self.encrypt(plaintext, deterministic=True)
    
    def encrypt_sensitive(self, plaintext: Union[str, None]) -> Optional[str]:
        """
        Encripta un valor sensible (no determinístico).
        Máxima seguridad para datos clínicos.
        
        Args:
            plaintext: Texto sensible a encriptar
            
        Returns:
            Texto encriptado de forma no determinística
        """
        return self.encrypt(plaintext, deterministic=False)


# ==============================================================================
# CONFIGURACIÓN DE CAMPOS Y SU TIPO DE ENCRIPTACIÓN
# ==============================================================================

# Campos con encriptación DETERMINÍSTICA (permiten búsqueda)
DETERMINISTIC_FIELDS = {
    'Patient': ['identifierCode', 'email', 'firstName', 'lastName1', 'phoneNumber'],
    'Doctor': ['identifierCode', 'email', 'firstName', 'lastName1', 'phoneNumber'],
}

# Campos con encriptación NO DETERMINÍSTICA (máxima seguridad)
NON_DETERMINISTIC_FIELDS = {
    'Patient': ['address', 'middleName', 'lastName2'],
    'Attention': ['reasonConsultation', 'currentIllness', 'evolution'],
    'Diagnostic': ['disease', 'observations'],
    'Treatment': ['medicament', 'indications', 'warning', 'frequency'],
    'Laboratory': ['exam'],
    'Imaging': ['imaging'],
    'Histopathology': ['histopathology'],
    'RegionalPhysicalExamination': ['examination'],
    'ReviewOrgansSystem': ['review'],
    'Allergy': ['allergies'],
    'FamilyBackground': ['familyBackground'],
    'PreExistingCondition': ['diseaseName', 'medicament', 'treatment'],
    'EmergencyContact': ['firstName', 'lastName', 'address', 'phoneNumber1', 'phoneNumber2'],
}

# Todos los campos sensibles combinados
SENSITIVE_FIELDS = {}
for model, fields in DETERMINISTIC_FIELDS.items():
    SENSITIVE_FIELDS[model] = SENSITIVE_FIELDS.get(model, []) + fields
for model, fields in NON_DETERMINISTIC_FIELDS.items():
    SENSITIVE_FIELDS[model] = SENSITIVE_FIELDS.get(model, []) + fields


# ==============================================================================
# FUNCIONES DE CONVENIENCIA
# ==============================================================================

_encryptor: Optional[MedicalDataEncryption] = None


def get_encryptor() -> MedicalDataEncryption:
    """Obtiene la instancia del encriptador (lazy initialization)"""
    global _encryptor
    if _encryptor is None:
        _encryptor = MedicalDataEncryption()
    return _encryptor


def encrypt_field(value: Union[str, None], model: str, field: str) -> Optional[str]:
    """
    Encripta un campo según su configuración (determinístico o no).
    
    Args:
        value: Valor a encriptar
        model: Nombre del modelo (ej: 'Patient')
        field: Nombre del campo (ej: 'email')
        
    Returns:
        Valor encriptado o None
    """
    if value is None:
        return None
    
    encryptor = get_encryptor()
    
    # Verificar si ya está encriptado
    if encryptor.is_encrypted(value):
        return value
    
    # Determinar tipo de encriptación
    if model in DETERMINISTIC_FIELDS and field in DETERMINISTIC_FIELDS[model]:
        return encryptor.encrypt(value, deterministic=True)
    elif model in NON_DETERMINISTIC_FIELDS and field in NON_DETERMINISTIC_FIELDS[model]:
        return encryptor.encrypt(value, deterministic=False)
    else:
        # Campo no configurado, no encriptar
        return value


def decrypt_field(value: Union[str, None]) -> Optional[str]:
    """
    Desencripta un campo (detecta automáticamente el tipo).
    
    Args:
        value: Valor encriptado
        
    Returns:
        Valor desencriptado o None
    """
    if value is None:
        return None
    
    return get_encryptor().decrypt(value)


def encrypt_for_search(value: Union[str, None]) -> Optional[str]:
    """
    Encripta un valor para usarlo en búsquedas WHERE.
    
    Args:
        value: Valor a buscar
        
    Returns:
        Valor encriptado de forma determinística
    """
    if value is None:
        return None
    return get_encryptor().encrypt_for_search(value)


def encrypt_model_data(model: str, data: dict) -> dict:
    """
    Encripta todos los campos sensibles de un diccionario según el modelo.
    
    Args:
        model: Nombre del modelo
        data: Diccionario con los datos
        
    Returns:
        Diccionario con campos encriptados
    """
    result = data.copy()
    
    # Campos determinísticos
    if model in DETERMINISTIC_FIELDS:
        for field in DETERMINISTIC_FIELDS[model]:
            if field in result and result[field] is not None:
                result[field] = encrypt_field(result[field], model, field)
    
    # Campos no determinísticos
    if model in NON_DETERMINISTIC_FIELDS:
        for field in NON_DETERMINISTIC_FIELDS[model]:
            if field in result and result[field] is not None:
                result[field] = encrypt_field(result[field], model, field)
    
    return result


def decrypt_model_data(model: str, data: dict) -> dict:
    """
    Desencripta todos los campos sensibles de un diccionario según el modelo.
    
    Args:
        model: Nombre del modelo
        data: Diccionario con los datos encriptados
        
    Returns:
        Diccionario con campos desencriptados
    """
    result = data.copy()
    all_fields = SENSITIVE_FIELDS.get(model, [])
    
    for field in all_fields:
        if field in result and result[field] is not None:
            result[field] = decrypt_field(result[field])
    
    return result


def generate_encryption_key() -> str:
    """
    Genera una nueva clave de encriptación Fernet.
    
    Returns:
        Clave de encriptación en formato string
    """
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Script para generar una nueva clave
    print("=" * 60)
    print("GENERADOR DE CLAVE DE ENCRIPTACIÓN PARA MEDSC")
    print("=" * 60)
    print()
    print("Nueva clave generada:")
    print(generate_encryption_key())
    print()
    print("IMPORTANTE: Copia esta clave y agrégala a tu archivo .env como:")
    print("ENCRYPTION_KEY=<tu_clave_aquí>")
    print()
    print("⚠️  NUNCA pierdas esta clave o los datos serán irrecuperables.")
    print("=" * 60)

