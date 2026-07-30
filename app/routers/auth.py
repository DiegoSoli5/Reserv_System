from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta

from ..config import settings
from ..database import get_db
from .. import schemas, utils, models
from .. import oauth2



router = APIRouter(
    prefix="/login",
    tags=["Auth"]
)

@router.post("/", response_model=schemas.Token)
def login(user_creds: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    stmt = select(models.Client).where(models.Client.email == user_creds.username)
    client = db.scalars(stmt).one_or_none()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if client is None:
        raise credentials_exception
    
    if not utils.verify_password(user_creds.password, client.password):
        raise credentials_exception
    
    access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = oauth2.create_access_token(data={"sub": str(client.id)}, expires_delta=access_token_expire)
    
    return schemas.Token(access_token=access_token, token_type="bearer")