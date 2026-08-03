from fastapi import APIRouter, Depends, HTTPException, status, Security
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

@router.post("/", response_model=schemas.EventResponse)
def create_event(db: Annotated[Session, Depends(get_db)],
                 event: schemas.Event,
                 current_client: Annotated[models.Client, Security(get_current_client, scopes=["events:create"])]):
    new_event = models.Event(client_id=current_client.id, **event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event