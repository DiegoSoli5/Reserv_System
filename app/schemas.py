from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum



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
    
class Token(BaseModel):
    access_token: str
    token_type: str
    role: ClientRole

class TokenData(BaseModel):
    id: int | None = None
    scopes: list[str] = []