from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import schemas, utils, models


router = APIRouter(
    prefix="/client",
    tags=["Client"]
)

@router.post("/")
def create_client(client: schemas.Client, db: Session = Depends(get_db)):
    client.password = utils.get_password(client.password)
    new_client = models.Client(**client.model_dump())
    stmt = select(models.Client).where(models.Client.email == client.email)
    client_existing = db.scalars(stmt).first()
    if client_existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exist"
        )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return new_client
    
    
