from telebot.async_telebot import AsyncTeleBot
from logging import Logger


async def register_all_handlers(bot: AsyncTeleBot, logger: Logger = None):
    """Call each module's local `register_handlers` in order."""
    from handlers.start_and_help import register_handlers as _register_start
    from handlers.goals_and_subjects import register_handlers as _register_goals
    from handlers.profile import register_handlers as _register_profile

    _register_start(bot, logger=logger)
    _register_goals(bot, logger=logger)
    _register_profile(bot, logger=logger)
    