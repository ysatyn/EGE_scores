from __future__ import annotations

from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession

from db import crud




def get_all_message_handlers() -> list[(Handler, list[str])]:
    return [(handle_start, ['start']), (handle_help, ["help", "помощь", "commands"])]

async def handle_start(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    await crud.create_or_update_user(db, **message.from_user.__dict__)
    message_text = ("Привет! Это бот по учёту баллов ЕГЭ. Здесь ты можешь сохранять свои результаты, смотреть статистику и ставить цели на желаемое количество баллов.\n" \
                    "Используй команду /help, чтобы узнать больше о доступных функциях.\n" \
                    "Удачи в подготовке к экзаменам!")
    await bot.send_message(chat_id=message.chat.id, text=message_text)

async def handle_help(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    user_id = user.id
    message_text = ("Список команд пока что в разработке. Потом прокину через гпт и внесу сюда список команд")
    await bot.send_message(chat_id=user_id, text=message_text)