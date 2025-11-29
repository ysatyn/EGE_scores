from functools import wraps
from typing import Optional, Callable, Any
from db.database import get_async_db
from logging import Logger

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