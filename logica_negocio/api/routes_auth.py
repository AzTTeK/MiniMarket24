"""
DEMAND-24 — API Router: Autenticación

Endpoints para gestionar usuarios y sesiones via Supabase.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from logica_negocio.auth.auth_service import AuthService
from logica_negocio.api.schemas.auth_schemas import UserLogin, UserRegister, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["Autenticación"])
auth_service = AuthService()

@router.post("/register", response_model=UserRead)
def register(data: UserRegister):
    """Registra un nuevo usuario."""
    try:
        res = auth_service.register(data)
        if not res.user:
            raise HTTPException(status_code=400, detail="Error al crear usuario")
        
        return UserRead(
            id=res.user.id,
            email=res.user.email,
            full_name=data.full_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    """Inicia sesion y retorna token JWT."""
    try:
        res = auth_service.login(data)
        if not res.session:
            raise HTTPException(status_code=401, detail="Credenciales invalidas")
        
        user_data = UserRead(
            id=res.user.id,
            email=res.user.email,
            full_name=res.user.user_metadata.get("full_name") if res.user.user_metadata else None
        )
        
        return TokenResponse(
            access_token=res.session.access_token,
            user=user_data
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Error en autenticacion")

@router.get("/me", response_model=UserRead)
def get_me(authorization: str = Header(None)):
    """Obtiene el perfil del usuario actual a partir del token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.split(" ")[1]
    user = auth_service.get_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
    
    return user
