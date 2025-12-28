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
        types.InlineKeyboardButton("📚 Выбрать предметы", callback_data="set_subjects_first"),
        types.InlineKeyboardButton("➕ Добавить балл", callback_data="quick_add_score"),
        types.InlineKeyboardButton("📊 Профиль", callback_data="profile_from_start"),
        types.InlineKeyboardButton("🆘 Помощь", callback_data="help_from_start"),
    ]
    markup.add(*buttons)
    
    message_text = f"Привет! Это бот по учёту баллов ЕГЭ.\n\n"
    message_text += f"Здесь ты можешь:\n"
    message_text += f"• Сохранять результаты тестов\n"
    message_text += f"• Смотреть статистику и прогресс\n"
    message_text += f"• Ставить цели на желаемые баллы\n"
    message_text += f"• Отслеживать подготовку к экзаменам\n\n"
    message_text += f"Используй кнопки ниже или команду /help"
    
    await bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=markup)

async def handle_help(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    
    help_text = f"🆘 Помощь по командам\n\n"
    
    help_text += f"📊 Основные команды:\n"
    help_text += f"/start — Начало работы\n"
    help_text += f"/help — Эта справка\n"
    help_text += f"/profile — Ваш профиль и статистика\n"
    help_text += f"/menu — Главное меню с кнопками\n\n"
    
    help_text += f"📚 Работа с предметами:\n"
    help_text += f"/subjects — Выбрать предметы для сдачи\n"
    help_text += f"/set_subjects — Альтернатива /subjects\n\n"
    
    help_text += f"🎯 Цели и результаты:\n"
    help_text += f"/set_desired_score — Установить желаемый балл\n"
    help_text += f"/desired_score — Альтернатива\n"
    help_text += f"/add_score — Добавить результат теста\n"
    help_text += f"/score — Альтернатива /add_score\n"
    help_text += f"/result — Альтернатива /add_score\n\n"
    
    help_text += f"📈 Быстрые действия:\n"
    help_text += f"1. Используй /menu для быстрого доступа\n"
    help_text += f"2. Или нажимай кнопки под сообщениями\n\n"
    
    help_text += f"🔧 Как пользоваться:\n"
    help_text += f"1. Сначала выбери предметы (/subjects)\n"
    help_text += f"2. Добавь первые результаты (/add_score)\n"
    help_text += f"3. Поставь цели (/set_desired_score)\n"
    help_text += f"4. Следи за прогрессом (/profile)\n\n"
    
    help_text += f"💡 Советы:\n"
    help_text += f"• Регулярно добавляй результаты\n"
    help_text += f"• Анализируй статистику\n"
    help_text += f"• Ставь реалистичные цели\n"
    help_text += f"• Сравнивай с предыдущими результатами\n\n"
    
    help_text += f"По вопросам и предложениям — пишите разработчику"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📚 Выбрать предметы", callback_data="set_subjects_first"),
        types.InlineKeyboardButton("➕ Добавить балл", callback_data="quick_add_score"),
        types.InlineKeyboardButton("📊 Мой профиль", callback_data="profile_from_help"),
        types.InlineKeyboardButton("📱 Главное меню", callback_data="menu_from_help"),
    ]
    markup.add(*buttons)
    
    await bot.send_message(chat_id=message.chat.id, text=help_text, reply_markup=markup)
    