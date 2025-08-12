from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
import requests

# Cargar variables de entorno
# Cargar variables de entorno desde el directorio padre
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL', "https://vdhbgtgbxszzheftvaga.supabase.co")
        supabase_key = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkaGJndGdieHN6emhlZnR2YWdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDQ0NDUsImV4cCI6MjA2OTk4MDQ0NX0.LdGqI_8JONJAex3Qbn407ueNE8hRzApGkQy5JY7x3eg")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados")
        
        logger.info(f"Conectando a Supabase: {supabase_url}")
        
        # Test connectivity first
        try:
            test_response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
            logger.info(f"Connectivity test response: {test_response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Connectivity test failed: {str(e)}")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    def sign_up(self, email: str, password: str, metadata: dict = None):
        """Register a new user"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {},
                    "email_confirm": False  # Desactivar confirmación por email para pruebas
                }
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session,
                "message": "Usuario registrado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error in sign_up: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error al registrar usuario"
            }
    
    def sign_in(self, email: str, password: str):
        """Sign in user with email and password"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session,
                "message": "Login exitoso"
            }
        except Exception as e:
            logger.error(f"Error in sign_in: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Credenciales inválidas"
            }
    
    def sign_out(self):
        """Sign out current user"""
        try:
            self.supabase.auth.sign_out()
            return {
                "success": True,
                "message": "Logout exitoso"
            }
        except Exception as e:
            logger.error(f"Error in sign_out: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error al cerrar sesión"
            }
    
    def get_user(self):
        """Get current user"""
        try:
            user = self.supabase.auth.get_user()
            return {
                "success": True,
                "user": user.user if user else None
            }
        except Exception as e:
            logger.error(f"Error in get_user: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user": None
            }
    
    def reset_password(self, email: str):
        """Send password reset email"""
        try:
            # Configurar la URL de redirect correctamente
            redirect_to = "http://localhost:3000/auth/callback"
            
            logger.info(f"Attempting to send reset password email to: {email}")
            logger.info(f"Redirect URL configured as: {redirect_to}")
            
            # Intentar con el cliente de Supabase primero
            try:
                response = self.supabase.auth.reset_password_email(
                    email,
                    {
                        "redirect_to": redirect_to
                    }
                )
                
                logger.info(f"Supabase client response: {response}")
                
                return {
                    "success": True,
                    "message": "Email de recuperación enviado exitosamente. Revisa tu bandeja de entrada."
                }
                
            except Exception as supabase_error:
                logger.warning(f"Supabase client failed: {str(supabase_error)}")
                logger.info("Trying direct API call...")
                
                # Método de respaldo usando requests directamente
                headers = {
                    'apikey': self.supabase_key,
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'email': email,
                    'options': {
                        'redirect_to': redirect_to
                    }
                }
                
                api_response = requests.post(
                    f'{self.supabase_url}/auth/v1/recover',
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                logger.info(f"Direct API response: {api_response.status_code} - {api_response.text}")
                
                if api_response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Email de recuperación enviado exitosamente. Revisa tu bandeja de entrada."
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API Error: {api_response.status_code}",
                        "message": f"Error del servidor: {api_response.text}"
                    }
            
        except Exception as e:
            logger.error(f"Error in reset_password: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            
            error_msg = str(e).lower()
            if "user not found" in error_msg or "email not found" in error_msg or "invalid" in error_msg:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Si el email está registrado en el sistema, recibirás un enlace de recuperación. Verifica que el email esté correcto."
                }
            
            # Si es un error de conectividad, dar una respuesta más específica
            if "getaddrinfo failed" in error_msg or "connection" in error_msg.lower():
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Error de conectividad. Verifica tu conexión a internet y vuelve a intentarlo."
                }
                
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al procesar la solicitud: {str(e)}"
            }

    def update_password(self, access_token: str, new_password: str):
        """Update user password with access token"""
        try:
            # Crear una nueva instancia de cliente con el token de acceso
            from supabase import create_client
            import os
            
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            temp_client = create_client(supabase_url, supabase_key)
            
            # Establecer la sesión con el token de acceso
            temp_client.auth.set_session(access_token, refresh_token="")
            
            # Actualizar la contraseña
            update_response = temp_client.auth.update_user({
                "password": new_password
            })
            
            return {
                "success": True,
                "user": update_response.user,
                "message": "Contraseña actualizada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error in update_password: {str(e)}")
            # Intentar método alternativo con API directa
            try:
                # Método alternativo usando la API REST de Supabase
                import requests
                import json
                
                supabase_url = os.environ.get('SUPABASE_URL')
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'apikey': os.environ.get('SUPABASE_KEY')
                }
                
                data = {
                    'password': new_password
                }
                
                response = requests.put(
                    f'{supabase_url}/auth/v1/user',
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "user": response.json(),
                        "message": "Contraseña actualizada exitosamente"
                    }
                else:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API Error: {response.status_code}",
                        "message": "Error al actualizar la contraseña. El token puede haber expirado."
                    }
                    
            except Exception as api_error:
                logger.error(f"API method also failed: {str(api_error)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Error al actualizar la contraseña. El token puede haber expirado o ser inválido."
                }

# Global instance
supabase_auth = SupabaseAuthService()
