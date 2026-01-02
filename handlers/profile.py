from __future__ import annotations
from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud

import datetime

from utils.subjects import EGE_SUBJECTS_DICT
from utils.obertka import make_registered_handler
from utils.validators import TelegramEvent

def register_handlers(bot: AsyncTeleBot, logger: Logger = None):
    logger.info("Registering profile handlers")
    
    handler_profile = make_registered_handler(profile_handler, bot=bot, logger=logger)
    bot.register_message_handler(handler_profile, commands=["profile", "me", "профиль"])
    
    bot.register_callback_query_handler(
        handler_profile,
        func=lambda call: call.data == "profile"
    )


async def profile_handler(event: Message | types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    if isinstance(event, types.CallbackQuery):
        await bot.delete_message(event.message.chat.id, event.message.message_id)
    event = TelegramEvent(event)
    
    user = await crud.create_or_update_user(db, **event.from_user.__dict__)
    user_id = user.id
    
    
    scores = await crud.get_all_scores_for_user(db, id=user_id, subject_id=None)
    total_tests = len(scores)
    avg_score = sum(s.score for s in scores) / total_tests if total_tests > 0 else 0
    
    subjects = []
    try:
        subjects = await crud.get_user_subjects(db, user_id)
    except:
        pass
    
    active_subjects = len(subjects)
    days_in_project = (datetime.datetime.now() - user.created_at).days
    
    profile_text = f"👤 *Профиль*\n\n"
    profile_text += f"📝 *Основное:*\n"
    profile_text += f"├ ID: `{user_id}`\n"
    profile_text += f"├ Имя: {user.first_name} {user.last_name or ''}\n"
    profile_text += f"├ Юзернейм: @{user.username}\n" if user.username else ""
    profile_text += f"└ Зарегистрирован: {user.created_at.strftime('%d.%m.%Y')}\n\n"
    
    profile_text += f"📊 *Статистика:*\n"
    profile_text += f"├ Всего пробников: {total_tests}\n"
    profile_text += f"├ Средний балл: {avg_score:.1f}\n"
    profile_text += f"├ Количество предметов: {active_subjects}\n"
    profile_text += f"└ Дней в подготовке: {days_in_project}\n\n"
    
    profile_text += f"🎯 *Предметы и цели:*\n"
    
    if subjects:
        for subject in subjects:
            subject_scores = [s for s in scores if s.subject_id == subject.id]
            subject_avg = sum(s.score for s in subject_scores) / len(subject_scores) if subject_scores else 0
            subject_max = max(s.score for s in subject_scores) if subject_scores else 0
            
            desired_score = "не установлена"
            try:
                for assoc in user.subject_associations:
                    if assoc.subject_id == subject.id:
                        desired_score = assoc.desired_score or "не установлена"
                        break
            except:
                pass
            
            profile_text += f"\n├ *{subject.name}:*\n"
            profile_text += f"│  ├ Пробников: {len(subject_scores)}\n"
            profile_text += f"│  ├ Средний результат: {subject_avg:.1f}\n"
            profile_text += f"│  ├ Максимальный балл: {subject_max}\n"
            profile_text += f"│  └ Цель: {desired_score} баллов\n"
    else:
        profile_text += f"\nℹ️ Нет выбранных предметов. Используй /subjects\n"
    
    profile_text += f"\n🛠 *Управление:*"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📊 Статистика", callback_data="profile_stats"),
        types.InlineKeyboardButton("🏆 Достижения", callback_data="profile_achievements"),
        types.InlineKeyboardButton("📈 Прогресс", callback_data="profile_progress"),
        types.InlineKeyboardButton("🔄 Обновить", callback_data="profile")
    ]
    markup.add(*buttons)
    
    await bot.send_message(
        chat_id=event.chat_id,
        text=profile_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )


