from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import schemas, utils, models
from ..oauth2 import get_current_client

router = APIRouter(
    prefix="/event",
    tags=["Events"]
)

@router.get("/", response_model=list[schemas.EventResponse])
def get_events(db: Annotated[Session, Depends(get_db)],
               limit: int = Query(default=10, ge=1, le=100),
               offset: int = Query(default=0, ge=0),
               # optional filters
               title: str | None = None,
               start_date: str | None = None,
               only_avaliable: bool = True
               ):
    stmt = select(models.Event)
    
    if title:
        stmt = stmt.where(models.Event.title.ilike(f"%{title}%"))
    if start_date:
        stmt = stmt.where(models.Event.date >= start_date)
    if only_avaliable:
        stmt = stmt.where(models.Event.avaliable_tickets > 0)
    
    stmt = stmt.limit(limit).offset(offset)
    events = db.scalars(stmt).all()
    return events
                   
@router.get("/{id}", response_model=schemas.EventResponse)
def get_one_event(id: int, db: Annotated[Session, Depends(get_db)]):
    stmt = select(models.Event).where(models.Event.id == id)
    event = db.scalars(stmt).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event not found"
        )
    return event

@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(db: Annotated[Session, Depends(get_db)],
                 event: schemas.Event,
                 current_client: Annotated[models.Client, Security(get_current_client, scopes=["events:create"])]):
    new_event = models.Event(client_id=current_client.id, **event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.patch("/{id}", response_model=schemas.EventResponse)
def update_event(id: int,
                 event: schemas.EventUpdate,
                 db: Annotated[Session, Depends(get_db)],
                 current_client: Annotated[models.Client, Security(get_current_client, scopes=["events:write"])]
                 ):
    
    stmt  = select(models.Event).where(models.Event.id == id)
    up_event = db.scalars(stmt).first()
    if not up_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    if up_event.client_id != current_client.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this event")

    updated_data = event.model_dump(exclude_unset=True)
    
    if "total_tickets" in updated_data:
        tickets_sold = up_event.total_tickets - up_event.avaliable_tickets
        if updated_data["total_tickets"] < tickets_sold:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total tickets cannot be less than tickets sold")
        
        up_event.avaliable_tickets = updated_data["total_tickets"] - tickets_sold
        
    for key, value in updated_data.items():
        setattr(up_event, key, value)
    
    db.commit()
    db.refresh(up_event)
    
    return up_event
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(id: int,
                 db: Annotated[Session, Depends(get_db)],
                 current_client: Annotated[models.Client, Security(get_current_client, scopes=["events:delete"])]):
    stmt = select(models.Event).where(models.Event.id == id)
    event = db.scalars(stmt).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Event not found")
    
    if event.client_id != current_client.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this event")
    db.delete(event)
    db.commit()
    