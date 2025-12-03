from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None

def validate_user_data_create(data: dict) -> dict:
    user = UserCreate(**data)
    return user.model_dump()

def validate_user_data_update(data: dict) -> dict:
    user = UserUpdate(**data)
    return user.model_dump(exclude_unset=True)
