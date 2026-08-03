from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime


## CLIENT SCHEMAS
class Client(BaseModel):
    email: EmailStr
    password: str
    
class ClientRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ClientResponse(BaseModel):
    id: int
    email: EmailStr
    role: ClientRole
    bookings: list
    
    model_config = ConfigDict(from_attributes=True)
    

class ClientUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, description="new password (optional)")
    role: ClientRole | None = None
    
# TOKEN SCHEMAS
    
class Token(BaseModel):
    access_token: str
    token_type: str
    role: ClientRole

class TokenData(BaseModel):
    id: int | None = None
    scopes: list[str] = []

# EVENT SCHEMAS

class Event(BaseModel):
    title: str
    description: str | None = None
    date: datetime
    location: str
    total_tickets: int = Field(gt=0)
    avaliable_tickets: int = Field(gt=0)
    price: float = Field(gt=0)
    
class EventResponse(Event):
    client: ClientResponse | None = None
    model_config = ConfigDict(from_attributes=True)