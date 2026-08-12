from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime,  timezone, timedelta

# OTHER SCHEMAS
class BookingInClient(BaseModel):
    id: int
    event_id: int
    quantity: int
    total_price: float
    status: BookingStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


## CLIENT SCHEMAS

class ClientRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class Client(BaseModel):
    email: EmailStr
    password: str
    role: ClientRole = ClientRole.USER
    
    
class ClientResponse(BaseModel):
    id: int
    email: EmailStr
    role: ClientRole
    
    model_config = ConfigDict(from_attributes=True)
    

class ClientUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, description="new password (optional)")
    role: ClientRole | None = None

class ClientBookingResponse(BaseModel):
    id: int
    email: EmailStr
    role: ClientRole
    bookings: list[BookingInClient]
    
    model_config = ConfigDict(from_attributes=True)
   
class ClientFullResponse(BaseModel):
    num_bookings: int
    Client: ClientBookingResponse
    
    model_config = ConfigDict(from_attributes=True)
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
    date: datetime | None = datetime.now(timezone.utc) + timedelta(minutes=10)
    location: str
    total_tickets: int = Field(gt=0)
    price: float = Field(gt=0)
    
class EventResponse(Event):
    id: int
    avaliable_tickets: int
    client: ClientResponse
    
    model_config = ConfigDict(from_attributes=True)

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: datetime | None = None
    location: str | None = None
    total_tickets: int | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, gt=0)
    
# BOOKING SCHEMAS
class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class CreateBooking(BaseModel):
    event_id: int | None = None
    quantity: int = Field(gt=0)
    
class BookingResponse(BaseModel):
    id: int
    total_price: float
    status: BookingStatus   
    created_at: datetime
    client: ClientResponse
    event: EventResponse
    
    
    model_config = ConfigDict(from_attributes=True)
