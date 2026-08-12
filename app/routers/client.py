from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import Annotated
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..database import get_db
from .. import schemas, utils, models
from ..oauth2 import get_current_client
from sqlalchemy import func

router = APIRouter(
    prefix="/client",
    tags=["Client"]
)

# , response_model=list[schemas.ClientBookingResponse]

@router.get("/", response_model=list[schemas.ClientFullResponse])
def get_clients(db: Session = Depends(get_db)):
    stmt = select(models.Client, func.count(models.Booking.client_id).label("num_bookings")).join(models.Booking, models.Client.id == models.Booking.client_id, isouter=True).group_by(models.Client.id)
    clients = db.execute(stmt).all()
    
    # print(clients)

    return clients

@router.post("/", status_code=status.HTTP_201_CREATED)
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
    
@router.get("/{id}", response_model=schemas.ClientFullResponse)
def get_one_client(id: int, db: Session = Depends(get_db)):
    
    stmt = select(models.Client, func.count(models.Booking.client_id).label("num_bookings")).join(models.Booking, models.Client.id == models.Booking.client_id, isouter=True).group_by(models.Client.id).where(models.Client.id == id)
    client = db.execute(stmt).first()
    
    return client


@router.patch("/{id}")
def update_client(id: int, client: schemas.ClientUpdate,
                  db: Annotated[Session, Depends(get_db)],
                  current_client: Annotated[models.Client, Security(get_current_client, scopes=["clients:write"])]):
    stmt = select(models.Client).where(models.Client.id == id)
    up_client = db.scalars(stmt).first()
    
    if not up_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    updated_data = client.model_dump(exclude_unset=True)
    
    if "password" in updated_data:
        updated_data["password"] = utils.get_password(updated_data["password"])
    
    for key, value in updated_data.items():
        setattr(up_client, key, value)
    
    
    db.commit()
    db.refresh(up_client)
    return up_client

@router.delete(
    "/{id}", 
    status_code=status.HTTP_204_NO_CONTENT)
def delete_client(id: int, db: Annotated[Session, Depends(get_db)], current_client: Annotated[models.Client, Depends(get_current_client)]):
    stmt = select(models.Client).where(models.Client.id == id)
    client = db.execute(stmt).scalar_one_or_none()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id of {id} not found "
        )
    if current_client.id != client.id and current_client.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you dont have permision to perform this action"
        )
        
    db.delete(client)
    db.commit()
    
    
    