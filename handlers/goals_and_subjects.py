from __future__ import annotations
from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud

from utils.subjects import EGE_SUBJECTS_DICT

def get_all_message_handlers() -> list[(Handler, list[str])]:
    return [(set_subjects_message_handler, ["set_subjects"])]

def get_all_callback_handlers() -> list[(Handler, str)]:
    return [(set_subject_callback_handler, r"^set_subject_.*")]


async def set_subjects_message_handler(message: Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    user_id = user.id

    message_text = "Здесь вы можете отметить предметы, которые вы хотитет сдавать. Выберите предметы из списка ниже"
    markup = types.InlineKeyboardMarkup(row_width=2)

    user_subjects_ids = await crud.get_user_subjects_ids(db, user_id)
    if user_subjects_ids:
        subjects = await crud.get_user_subjects(db, user_id)
        message_text = "Вы выбрали следующие предметы для сдачи:\n" + ", ".join([subj.name for subj in subjects]) + "\n\n" + message_text
    for subj_id, subject_name in EGE_SUBJECTS_DICT.items():
        if subj_id in user_subjects_ids:
            button = types.InlineKeyboardButton(text=f"✅ {subject_name}", callback_data=f"unset_subject_{subj_id}")
        else:
            button = types.InlineKeyboardButton(text=subject_name, callback_data=f"set_subject_{subj_id}")
        markup.add(button)
    await bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=markup)


async def set_subject_callback_handler(call: types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **call.from_user.__dict__)
    user_id = user.id
    subject_id = call.data.split("_")[-1]

    await crud.switch_subject_for_user(db, user_id, subject_id)

    message_text = "Здесь вы можете отметить предметы, которые вы хотитет сдавать. Выберите предметы из списка ниже"
    markup = types.InlineKeyboardMarkup(row_width=2)

    user_subjects_ids = await crud.get_user_subjects_ids(db, user_id)
    if user_subjects_ids:
        subjects = await crud.get_user_subjects(db, user_id)
        message_text = "Вы выбрали следующие предметы для сдачи:\n" + ", ".join([subj.name for subj in subjects]) + "\n\n" + message_text
    for subj_id, subject_name in EGE_SUBJECTS_DICT.items():
        if subj_id in user_subjects_ids:
            button = types.InlineKeyboardButton(text=f"✅ {subject_name}", callback_data=f"unset_subject_{subj_id}")
        else:
            button = types.InlineKeyboardButton(text=subject_name, callback_data=f"set_subject_{subj_id}")
        markup.add(button)
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

