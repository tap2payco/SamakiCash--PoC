from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    FISHER = "fisher"
    SELLER = "seller"   # seller = dagaa vendor / landing site seller
    BUYER = "buyer"     # buyer = wholesaler / hotel / processor / trader
    SUPERUSER = "superuser"

class UserCreate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    user_type: UserType = Field(default=UserType.FISHER)
    name: Optional[str] = None
    organization: Optional[str] = None  # useful for buyers
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
