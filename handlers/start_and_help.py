from __future__ import annotations

from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession

from db import crud
from utils.obertka import make_registered_handler


def register_handlers(bot: AsyncTeleBot, logger: Logger = None):
    if logger:
        logger.info("Registering start and help handlers")

    handler_start = make_registered_handler(handle_start, bot=bot, logger=logger)
    bot.register_message_handler(handler_start, commands=["start"])

    handler_help = make_registered_handler(handle_help, bot=bot, logger=logger)
    bot.register_message_handler(handler_help, commands=["help", "помощь", "commands"])


async def handle_start(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    await crud.create_or_update_user(db, **message.from_user.__dict__)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📚 Выбрать предметы", callback_data="subjects"),
        types.InlineKeyboardButton("➕ Добавить балл", callback_data="add_score"),
        types.InlineKeyboardButton("🎯 Установить цель", callback_data="set_desired_score"),
        types.InlineKeyboardButton("📊 Профиль", callback_data="profile"),
    ]
    markup.add(*buttons)
    
    message_text = f"👋 Привет, {message.from_user.first_name}!\n\n"
    message_text += f"📚 **Это бот для учёта баллов ЕГЭ**\n\n"
    message_text += f"✨ **Что можно делать:**\n"
    message_text += f"• 📝 Сохранять результаты пробных тестов\n"
    message_text += f"• 🎯 Ставить цели по предметам\n"
    message_text += f"• 📊 Отслеживать прогресс подготовки\n"
    message_text += f"• 📈 Анализировать статистику\n"
    message_text += f"• 🏆 Достигать учебных целей\n\n"
    message_text += f"🚀 **Начни с выбора предметов** или используй кнопки ниже!\n"
    message_text += f"ℹ️ Подробнее — /help"
    
    await bot.send_message(
        chat_id=message.chat.id, 
        text=message_text, 
        reply_markup=markup,
        parse_mode="Markdown"
    )


async def handle_help(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    await crud.create_or_update_user(db, **message.from_user.__dict__)
    
    help_text = f"📚 **Помощь по боту для подготовки к ЕГЭ**\n\n"
    
    help_text += f"🎯 **Основные команды:**\n"
    help_text += f"`/start` — Начало работы, главное меню\n"
    help_text += f"`/help` — Эта справка\n"
    help_text += f"`/profile` — Ваш профиль и статистика\n\n"
    
    help_text += f"📖 **Работа с предметами:**\n"
    help_text += f"`/subjects` — Выбрать предметы для сдачи\n"
    help_text += f"`/set_subjects` — То же самое\n\n"
    
    help_text += f"🏆 **Цели и результаты:**\n"
    help_text += f"`/set_desired_score` — Установить желаемый балл\n"
    help_text += f"`/add_score` — Добавить результат теста\n\n"
    
    help_text += f"🔄 **Рабочий процесс:**\n"
    help_text += f"1️⃣ **Выбери предметы** → `/subjects`\n"
    help_text += f"2️⃣ **Добавь первый результат** → `/add_score`\n"
    help_text += f"3️⃣ **Поставь цели** → `/set_desired_score`\n"
    help_text += f"4️⃣ **Следи за прогрессом** → `/profile`\n\n"
        
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📚 Выбрать предметы", callback_data="subjects"),
        types.InlineKeyboardButton("➕ Добавить балл", callback_data="add_score"),
        types.InlineKeyboardButton("🎯 Установить цель", callback_data="set_desired_score"),
        types.InlineKeyboardButton("📊 Профиль", callback_data="profile"),
    ]
    markup.add(*buttons)
    
    await bot.send_message(
        chat_id=message.chat.id, 
        text=help_text, 
        reply_markup=markup,
        parse_mode="Markdown"
    )