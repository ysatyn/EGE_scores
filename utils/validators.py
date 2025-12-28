from pydantic import BaseModel, ConfigDict
from typing import Optional, Union
from telebot import types

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



class TelegramEvent:
    def __init__(self, event: Union[types.Message, types.CallbackQuery]):
        self.from_user = event.from_user
        self.original_event = event
        
        if isinstance(event, types.Message):
            self.chat_id = event.chat.id
            self.text = event.text or ''
            self.event_type = 'message'
        else: 
            self.chat_id = event.message.chat.id
            self.text = event.data or ''
            self.event_type = 'callback'
    
    @property
    def is_message(self) -> bool:
        return self.event_type == 'message'
    
    @property
    def is_callback(self) -> bool:
        return self.event_type == 'callback'