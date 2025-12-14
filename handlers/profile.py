from __future__ import annotations
from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import get_chat
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud

from utils.subjects import EGE_SUBJECTS_DICT
from utils.obertka import make_registered_handler
from utils.states import SpecialStates


def register_handlers(bot: AsyncTeleBot, logger: Logger = None):
    pass


async def view_profile_handler(message: types.Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__) 
    user_id = user.id 
    
    user