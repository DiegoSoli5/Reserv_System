from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List



class Client(BaseModel):
    email: EmailStr
    password: str
    
class ClientResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    bookings: list
    
    model_config = ConfigDict(from_attributes=True)

class ClientUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, description="new password (optional)")
    role: str | None = None
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None