from __future__ import annotations
from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud
from utils.obertka import db_handler
import re

from utils.subjects import EGE_SUBJECTS_DICT


def register_handlers(bot: AsyncTeleBot, logger: Logger = None):
    """Register this module's message and callback handlers on `bot`."""
    handler_set_subjects = db_handler(set_subjects_message_handler, logger=logger)
    if callable(handler_set_subjects):
        bot.register_message_handler(handler_set_subjects, commands=["set_subjects"], pass_bot=True)

    handler_set_subject_cb = db_handler(set_subject_callback_handler, logger=logger)
    if callable(handler_set_subject_cb):
        bot.register_callback_query_handler(
            handler_set_subject_cb,
            func=(lambda call, p=r"^set_subject_.*": bool(call.data and re.match(p, call.data))),
            pass_bot=True,
        )


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
    # callback data format: 'set_subject_<subject_id>' or 'unset_subject_<subject_id>'
    # subject ids can contain underscores, so split with max 2 parts to preserve the full id
    subject_id = call.data.split("_", 2)[-1]

    if logger:
        logger.debug(f"Callback received: {call.data!r} -> subject_id={subject_id!r}")

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

