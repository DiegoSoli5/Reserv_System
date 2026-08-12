from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import schemas, utils, models
from ..oauth2 import get_current_client

router  = APIRouter(
    prefix="/booking",
    tags=["Bookings"]
)

@router.get("/{id}", response_model=schemas.BookingResponse)
def get_booking(id: int, current_client: Annotated[models.Client, Security(get_current_client, scopes=[])], db: Annotated[Session, Depends(get_db)]):
    stmt = select(models.Booking).where(models.Booking.id == id)
    booking = db.scalars(stmt).first()
    
    if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
    
    if booking.client_id != current_client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this booking"
        )
    return booking

@router.post("/", response_model=schemas.BookingResponse,status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: schemas.CreateBooking,
    db: Annotated[Session, Depends(get_db)],
    current_client: Annotated[models.Client, Security(get_current_client, scopes=["bookings:create"])]):
    stmt1 = select(models.Event).where(models.Event.id == booking.event_id).with_for_update()
    event = db.scalars(stmt1).one_or_none()
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="event not found"
        )
    
    if event.date < utils.get_current_time():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event has already passed"
        )
    
    if event.avaliable_tickets < booking.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="not enough avaliable tickets"
        )
    new_price = event.price * booking.quantity
    new_booking = models.Booking(
        client_id=current_client.id,
        event_id=booking.event_id,
        total_price=new_price,
        quantity=booking.quantity,
        status=schemas.BookingStatus.CONFIRMED)
    event.avaliable_tickets -= booking.quantity
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking
    
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def cancell_booking(id:int, db: Annotated[Session, Depends(get_db)], current_client: Annotated[models.Client, Security(get_current_client, scopes=["bookings:delete"])]):
    stmt_booking = select(models.Booking).where(models.Booking.id == id)
    booking = db.scalars(stmt_booking).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"booking with id:{id} was not found"
        )

    stmt_event = select(models.Event).where(models.Event.id == booking.event_id)
    event = db.scalars(stmt_event).first()
    
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="event not found"
        )
        
    # this is for the admin to be able to cancel another clients bookings
    if current_client.role == schemas.ClientRole.ADMIN:
        if booking.status == schemas.BookingStatus.CONFIRMED:
                event.avaliable_tickets += booking.quantity
        booking.status = schemas.BookingStatus.CANCELLED
        
        db.commit()
        db.refresh(booking)
        
        return
    if booking.client_id != current_client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform this action"
        )
    
    if booking.status == schemas.BookingStatus.CONFIRMED:
        event.avaliable_tickets += booking.quantity
    
    
    
    booking.status = schemas.BookingStatus.CANCELLED
    
    db.commit()
    db.refresh(booking)
    
    
    
    
        
    