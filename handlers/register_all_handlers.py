from telebot.async_telebot import AsyncTeleBot
from logging import Logger


async def register_all_handlers(bot: AsyncTeleBot, logger: Logger = None):
    from handlers.start_and_help import register_handlers as _register_start
    from handlers.goals_and_subjects import register_handlers as _register_goals
    from handlers.profile import register_handlers as _register_profile
    from handlers.simple_stats import register_handlers as _register_stats

    _register_start(bot, logger=logger)
    _register_goals(bot, logger=logger)
    _register_profile(bot, logger=logger)
    _register_stats(bot, logger=logger)
    