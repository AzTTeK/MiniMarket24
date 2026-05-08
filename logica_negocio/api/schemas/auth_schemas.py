from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserLogin(BaseModel):
    """Schema para inicio de sesion."""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """Schema para registro de usuario."""
    email: EmailStr
    password: str
    full_name: Optional[str] = Field(None, description="Nombre completo del usuario")


class UserRead(BaseModel):
    """Schema para leer datos de usuario."""
    id: str
    email: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Respuesta con el token de acceso."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead
