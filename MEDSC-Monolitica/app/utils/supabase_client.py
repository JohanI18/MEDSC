from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en el archivo .env")
        
        logger.info(f"Conectando a Supabase: {supabase_url}")
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
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
            response = self.supabase.auth.reset_password_email(email)
            return {
                "success": True,
                "message": "Email de recuperación enviado"
            }
        except Exception as e:
            logger.error(f"Error in reset_password: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error al enviar email de recuperación"
            }

# Global instance
supabase_auth = SupabaseAuthService()
