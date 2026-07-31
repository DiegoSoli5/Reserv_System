from .config import settings
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes)


from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.scopes import ROLE_SCOPES
from app.schemas import TokenData, ClientRole
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import select
from . import models

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        "profile:read": "See data of own profile",
        "profile:write": "Edit own data",
        "clients:read": "See other client's data",
        "clients:write": "edit other client's data",
        "clients:delete": "delete clients"
    })

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def create_access_token(data:dict, role: ClientRole, expires_delta: timedelta | None):
    to_encode = data.copy()
    
    scopes = ROLE_SCOPES.get(role, [])
    to_encode.update({"scopes": scopes, "role":role})
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes):
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope ="{security_scopes.scopes}"'
    else:
        authenticate_value = "Bearer"
    
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        scope: list[str] = payload.get("scopes", [])
        token_data = TokenData(id=(id),scopes=scope)
        print(token_data.scopes)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough Permissions. Required: {scope}",
                headers={"WWW-Authenticate": authenticate_value}
            )
    return token_data


async def get_current_client(token_data: Annotated[TokenData, Depends(verify_token)], db: Annotated[Session, Depends(get_db)]) -> models.Client:
    stmt = select(models.Client).where(models.Client.id == token_data.id)
    client = db.execute(stmt).scalar_one_or_none()
    if client is None:
        raise credentials_exception
    return client