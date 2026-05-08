"""
DEMAND-24 — Servicio de Autenticación (Supabase)

Gestiona el registro e inicio de sesion de usuarios delegando en Supabase Auth.
"""

import logging
from typing import Optional

from supabase import create_client, Client
from logica_negocio.config.settings import settings
from logica_negocio.api.schemas.auth_schemas import UserLogin, UserRegister, UserRead

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_ANON_KEY
        )

    def register(self, data: UserRegister):
        """Registra un nuevo usuario en Supabase."""
        try:
            response = self.supabase.auth.sign_up({
                "email": data.email,
                "password": data.password,
                "options": {
                    "data": {
                        "full_name": data.full_name
                    }
                }
            })
            return response
        except Exception as e:
            logger.error(f"Error en registro Supabase: {str(e)}")
            raise

    def login(self, data: UserLogin):
        """Inicia sesion en Supabase."""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password
            })
            return response
        except Exception as e:
            logger.error(f"Error en login Supabase: {str(e)}")
            raise

    def get_user(self, jwt_token: str) -> Optional[UserRead]:
        """Obtiene el usuario a partir de un JWT."""
        try:
            user_response = self.supabase.auth.get_user(jwt_token)
            user = user_response.user
            return UserRead(
                id=user.id,
                email=user.email,
                full_name=user.user_metadata.get("full_name") if user.user_metadata else None
            )
        except Exception as e:
            logger.error(f"Error validando token: {str(e)}")
            return None
