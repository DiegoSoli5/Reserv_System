from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List



class Client(BaseModel):
    email: EmailStr
    password: str
    