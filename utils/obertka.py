from functools import wraps
from typing import Optional, Callable, Any
from db.database import get_async_db
from logging import Logger

from typing import Coroutine
import asyncio

def db_handler(handler_func: Optional[Callable] = None, logger: Optional[Logger] = None):
    def _decorate(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db_gen = get_async_db()
            session = await anext(db_gen)
            try:
                result = await func(*args, db=session, logger=logger, **kwargs)
                return result
            except Exception as e:
                if logger:
                    logger.error(f"Error in handler: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
        return wrapper

    if callable(handler_func):
        return _decorate(handler_func)

    return _decorate


def make_registered_handler(func: Callable, bot, logger: Optional[Logger] = None):
    """Return an async wrapper that opens a DB session and calls `func` with
    signature like `func(update, db=..., logger=..., bot=...)`.

    The returned wrapper accepts a single positional argument (Message or CallbackQuery)
    so it can be registered directly with `bot.register_message_handler` or
    `bot.register_callback_query_handler`.
    """
    async def _wrapper(update):
        db_gen = get_async_db()
        session = await anext(db_gen)
        try:
            result = await func(update, db=session, logger=logger, bot=bot)
            return result
        except Exception as e:
            if logger:
                logger.error(f"Error in handler: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

    return _wrapper
