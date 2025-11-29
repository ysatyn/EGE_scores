from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_helper import ApiTelegramException
from telebot.asyncio_storage import memory_storage

from logging import Logger

from utils.obertka import db_handler


async def register_all_handlers(bot: AsyncTeleBot, logger: Logger = None):
    from handlers.start_and_help import get_all_handlers as get_start_and_help_handlers
    all_handlers = []
    all_handlers.extend(get_start_and_help_handlers())

    for handler_func, commands in all_handlers:
        # Декорируем функцию перед регистрацией
        decorated_handler = db_handler(handler_func, logger=logger)
        
        bot.register_message_handler(
            decorated_handler, 
            pass_bot=True, 
            commands=commands
        )