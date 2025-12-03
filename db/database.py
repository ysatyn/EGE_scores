from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from config import DATABASE_URL
from typing import AsyncGenerator
from logging import Logger
import asyncio

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
Base = declarative_base()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Получение асинхронной сессии базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_models(needs_reset: bool = False, logger: Logger = None):
    """
    Инициализация моделей базы данных - через ORM
    """
    try:
        from db.models import User, Subject, Scores, Exams, UserSubjectAssociation
        from db.crud import create_subjects
        
        async with engine.begin() as conn:
            if needs_reset:
                if logger:
                    logger.info("Dropping existing tables...")
                await conn.run_sync(Base.metadata.drop_all)
            
            await conn.run_sync(Base.metadata.create_all)
        
        if logger:
            logger.info("Database tables created successfully")

        if needs_reset:
            if logger:
                logger.info("Creating default subjects...")
            async with AsyncSessionLocal() as session:
                await create_subjects(session)

            
    except Exception as e:
        if logger:
            logger.error(f"Database initialization error: {e}")
        raise

async def show_tables():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])
        