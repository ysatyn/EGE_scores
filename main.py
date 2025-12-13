import logging
import asyncio 
import sys

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.asyncio_storage.memory_storage import StateMemoryStorage
from telebot.asyncio_filters import StateFilter


from config import BOT_TOKEN, DATABASE_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)


async def initiate_bot() -> AsyncTeleBot:
    bot = AsyncTeleBot(BOT_TOKEN, state_storage=StateMemoryStorage(), colorful_logs=True)
    logger.info("Bot initialized")
    return bot


async def on_startup():
    logger.info("Bot started successfully.")


async def on_shutdown():
    logger.info("Shutting down the bot...")
    pass


async def initiate_database(needs_reset: bool = False, logger: logging.Logger = logger):
    from db.database import init_models
    await init_models(needs_reset=needs_reset, logger=logger)




async def main():
    bot = await initiate_bot()
    logging.info("Registering filters...")
    bot.add_custom_filter(StateFilter(bot))
    
    await initiate_database(needs_reset=False, logger=logger)

    from handlers.register_all_handlers import register_all_handlers
    await register_all_handlers(bot, logger=logger)

    try:
        await on_startup()
        logging.info("Polling started...")
        await bot.infinity_polling(allowed_updates=[], skip_pending=True, request_timeout=30, logger_level=logging.DEBUG)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await on_shutdown()
        logger.info("Bot has been shut down.")


if __name__ == "__main__":
    asyncio.run(main())