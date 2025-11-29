import re
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_helper import ApiTelegramException
from telebot.asyncio_storage import memory_storage

from logging import Logger

from utils.obertka import db_handler


async def register_all_handlers(bot: AsyncTeleBot, logger: Logger = None):
    from handlers.start_and_help import get_all_message_handlers as get_start_and_help_message_handlers
    from handlers.goals_and_subjects import get_all_message_handlers as get_goals_and_subjects_message_handlers
    all_message_handlers = []
    all_message_handlers.extend(get_start_and_help_message_handlers())
    all_message_handlers.extend(get_goals_and_subjects_message_handlers())

    for handler_func, commands in all_message_handlers:
        # Validate handler tuple
        if not callable(handler_func):
            if logger:
                logger.error(f"Skipping message handler registration: handler is not callable: {handler_func!r}")
            continue

        if isinstance(commands, str):
            commands = [commands]
        if not isinstance(commands, (list, tuple)):
            if logger:
                logger.error(f"Skipping message handler registration: commands must be list/tuple or str, got: {type(commands)!r}")
            continue

        decorated_handler = db_handler(handler_func, logger=logger)

        bot.register_message_handler(
            decorated_handler,
            pass_bot=True,
            commands=commands
        )

    from handlers.goals_and_subjects import get_all_callback_handlers as get_goals_and_subjects_callback_handlers
    all_callback_handlers = []
    all_callback_handlers.extend(get_goals_and_subjects_callback_handlers())
    for handler_func, pattern in all_callback_handlers:
        if not callable(handler_func):
            if logger:
                logger.error(f"Skipping callback handler registration: handler is not callable: {handler_func!r}")
            continue

        if not isinstance(pattern, str):
            if logger:
                logger.error(f"Skipping callback handler registration: pattern must be a str, got: {type(pattern)!r}")
            continue

        decorated_handler = db_handler(handler_func, logger=logger)

        bot.register_callback_query_handler(
            decorated_handler,
            pass_bot=True,
            func=lambda call, p=pattern: call.data and re.match(p, call.data)
        )