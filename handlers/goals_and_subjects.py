from __future__ import annotations
from telebot import Handler
from telebot.types import Message
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud

from utils.subjects import EGE_SUBJECTS_DICT
from utils.obertka import make_registered_handler
from utils.states import SpecialStates
from utils.bot_utils import del_message_from_callback
from utils.validators import TelegramEvent


pending_user_subjects: dict[int, str] = {}

def register_handlers(bot: AsyncTeleBot, logger: Logger = None):
    logger.info("Registering goals and subjects handlers")

    handler_set_subjects = make_registered_handler(set_subjects_handler, bot=bot, logger=logger)
    bot.register_message_handler(handler_set_subjects, commands=["subjects", "set_subjects"])   
    bot.register_callback_query_handler(
        handler_set_subjects,
        func=lambda call: call.data and (
            call.data.startswith("set_subject_") or 
            call.data.startswith("unset_subject_") or
            call.data == "subjects"
        )
    )
    
    handler_set_desired_score_menu = make_registered_handler(set_desired_score_menu_handler, bot=bot, logger=logger)
    bot.register_message_handler(handler_set_desired_score_menu, commands=["set_desired_score", "desired_score", "set_score"]) 
    bot.register_callback_query_handler(
        handler_set_desired_score_menu,
        func=lambda call: call.data and (
            call.data.startswith("set_desired_score_menu_") or
            call.data == "set_desired_score"
        )
    )
    
    handler_set_desired_score_callback = make_registered_handler(set_desired_score_callback_handler, bot=bot, logger=logger)
    bot.register_callback_query_handler(
        handler_set_desired_score_callback,
        func=lambda call: call.data and call.data.startswith("set_desired_score_")
    )
    
    handler_add_score_menu = make_registered_handler(add_score_menu_handler, bot=bot, logger=logger)
    bot.register_message_handler(handler_add_score_menu, commands=["add_score", "add", "score", "result"])
    bot.register_callback_query_handler(
        handler_add_score_menu,
        func=lambda call: call.data and (
            call.data.startswith("add_score_menu_") or
            call.data == "add_score"
        )
    )
    
    handler_add_score_callback = make_registered_handler(add_score_callback_handler, bot=bot, logger=logger)
    bot.register_callback_query_handler(
        handler_add_score_callback,
        func=lambda call: call.data and call.data.startswith("add_score_")
    )
    
    handler_insert_desired_score = make_registered_handler(insert_desired_score_handler, bot=bot, logger=logger)
    bot.register_message_handler(
        handler_insert_desired_score,
        state=SpecialStates.AWAITING_USER_DESIRED_SCORE
    )
    
    handler_insert_score = make_registered_handler(insert_score_handler, bot=bot, logger=logger)
    bot.register_message_handler(
        handler_insert_score,
        state=SpecialStates.WAITING_FOR_SCORE_INPUT
    )


async def set_subjects_handler(event: Message | types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    telegram_event = TelegramEvent(event)
    
    if telegram_event.is_callback:
        await del_message_from_callback(bot, telegram_event.original_event)
    
    user = await crud.create_or_update_user(db, **telegram_event.from_user.__dict__)
    user_id = user.id
    
    if telegram_event.is_callback and telegram_event.text:
        if telegram_event.text.startswith(("set_subject_", "unset_subject_")):
            subject_id = telegram_event.text.split("_", 2)[-1]
            await crud.switch_subject_for_user(db, user_id, subject_id)
    
    user_subjects = await crud.get_user_subjects(db, user_id)
    user_subject_ids = {subj.id for subj in user_subjects}
    
    message_text = "Выберите предметы, которые вы планируете сдавать на ЕГЭ.\n\n"
    if user_subjects:
        message_text += "✅ Вы уже выбрали:\n" + ", ".join([subj.name for subj in user_subjects]) + "\n\n"
    message_text += "Нажмите на предмет, чтобы добавить или убрать его из вашего списка:"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    
    for subject_id, subject_name in EGE_SUBJECTS_DICT.items():
        if subject_id in user_subject_ids:
            btn = types.InlineKeyboardButton(
                text=f"✅ {subject_name}",
                callback_data=f"unset_subject_{subject_id}"
            )
        else:
            btn = types.InlineKeyboardButton(
                text=subject_name,
                callback_data=f"set_subject_{subject_id}"
            )
        buttons.append(btn)
    
    for i in range(0, len(buttons), 2):
        markup.add(buttons[i], buttons[i+1] if i+1 < len(buttons) else None)
    
    await bot.send_message(telegram_event.chat_id, message_text, reply_markup=markup)


async def set_desired_score_menu_handler(event: Message | types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    telegram_event = TelegramEvent(event)
    
    if telegram_event.is_callback:
        await del_message_from_callback(bot, telegram_event.original_event)
    
    user = await crud.create_or_update_user(db, **telegram_event.from_user.__dict__)
    user_id = user.id
    
    if telegram_event.is_callback and telegram_event.text.startswith("set_desired_score_"):
        subject_id = telegram_event.text[len("set_desired_score_"):]
        
        subject_name = EGE_SUBJECTS_DICT.get(subject_id)
        
        await bot.set_state(user_id, SpecialStates.AWAITING_USER_DESIRED_SCORE, telegram_event.chat_id)
        pending_user_subjects[user_id] = subject_id
        
        message_text = f"Введите желаемый балл для предмета «{subject_name}» (от 0 до 100):"
        await bot.send_message(chat_id=telegram_event.chat_id, text=message_text)
        return
    
    subjects = await crud.get_user_subjects(db, user_id)
    
    if not subjects:
        message_text = "Сначала выберите предметы командой /subjects"
        await bot.send_message(chat_id=telegram_event.chat_id, text=message_text)
        return
    
    markup = types.InlineKeyboardMarkup()
    for subject in subjects:
        btn = types.InlineKeyboardButton(
            text=subject.name,
            callback_data=f"set_desired_score_{subject.id}"
        )
        markup.add(btn)
    
    message_text = "Выберите предмет, для которого хотите установить желаемый балл:\n\n"
    message_text += "Перед этим убедитесь, что предмет выбран в разделе /subjects"
    
    await bot.send_message(chat_id=telegram_event.chat_id, text=message_text, reply_markup=markup)


async def set_desired_score_callback_handler(call: types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    """Обработчик выбора предмета для желаемого балла (только callback)"""
    await del_message_from_callback(bot, call)
    user = await crud.create_or_update_user(db, **call.from_user.__dict__)
    user_id = user.id
    
    subject_id = call.data[len("set_desired_score_"):]

    if logger:
        logger.debug(f"Callback received: {call.data!r} -> subject_id={subject_id!r}")

    subject_name = EGE_SUBJECTS_DICT.get(subject_id)

    await bot.set_state(user_id, SpecialStates.AWAITING_USER_DESIRED_SCORE, call.message.chat.id)
    
    pending_user_subjects[user_id] = subject_id
    
    message_text = f"Введите желаемый балл для предмета «{subject_name}» (от 0 до 100):"
    
    await bot.send_message(chat_id=call.message.chat.id, text=message_text)


async def add_score_menu_handler(event: Message | types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    telegram_event = TelegramEvent(event)
    
    if telegram_event.is_callback:
        await del_message_from_callback(bot, telegram_event.original_event)
    
    user = await crud.create_or_update_user(db, **telegram_event.from_user.__dict__)
    user_id = user.id
    
    if telegram_event.is_callback and telegram_event.text.startswith("add_score_"):
        subject_id = telegram_event.text[len("add_score_"):]
        subject_name = EGE_SUBJECTS_DICT.get(subject_id)
        
        await bot.set_state(user_id, SpecialStates.WAITING_FOR_SCORE_INPUT, telegram_event.chat_id)
        pending_user_subjects[user_id] = subject_id
        
        message_text = f"Введите балл, который вы получили по предмету «{subject_name}» (от 0 до 100):"
        await bot.send_message(chat_id=telegram_event.chat_id, text=message_text)
        return
    
    subjects = await crud.get_user_subjects(db, user_id)
    
    if not subjects:
        message_text = "Сначала выберите предметы командой /subjects"
        await bot.send_message(chat_id=telegram_event.chat_id, text=message_text)
        return
    
    markup = types.InlineKeyboardMarkup()
    for subject in subjects:
        btn = types.InlineKeyboardButton(
            text=subject.name,
            callback_data=f"add_score_{subject.id}"
        )
        markup.add(btn)
    
    message_text = "Выберите предмет, для которого хотите добавить результат:\n\n"
    message_text += "Перед этим убедитесь, что предмет выбран в разделе /subjects"
    
    await bot.send_message(telegram_event.chat_id, message_text, reply_markup=markup)


async def add_score_callback_handler(call: types.CallbackQuery, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    """Обработчик выбора предмета для добавления балла (только callback)"""
    await del_message_from_callback(bot, call)
    user = await crud.create_or_update_user(db, **call.from_user.__dict__)
    user_id = user.id
    
    subject_id = call.data[len("add_score_"):]

    if logger:
        logger.debug(f"Callback received: {call.data!r} -> subject_id={subject_id!r}")

    subject_name = EGE_SUBJECTS_DICT.get(subject_id)

    await bot.set_state(user_id, SpecialStates.WAITING_FOR_SCORE_INPUT, call.message.chat.id)
    
    pending_user_subjects[user_id] = subject_id
    
    message_text = f"Введите балл, который вы получили по предмету «{subject_name}» (от 0 до 100):"
    
    await bot.send_message(chat_id=call.message.chat.id, text=message_text)


async def insert_desired_score_handler(message: types.Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    user_id = user.id
    
    try:
        desired_value = int(message.text)
    except ValueError:
        await bot.send_message(message.chat.id, "Пожалуйста, введите корректное число")
        return
    
    if not 0 <= desired_value <= 100:
        await bot.send_message(message.chat.id, "Пожалуйста, введите число от 0 до 100")
        return
    
    subject_id = pending_user_subjects.get(user_id)
    if not subject_id:
        await bot.send_message(message.chat.id, "Что-то пошло не так. Пожалуйста, начните процесс заново, используя команду /set_desired_score")
        return
    
    subject_name = EGE_SUBJECTS_DICT.get(subject_id)
    
    del pending_user_subjects[user_id]
    await bot.delete_state(user_id, chat_id=message.chat.id)
    
    try:
        association = await crud.set_desired_score(
            db, 
            user_id=user_id, 
            subject_id=subject_id, 
            desired_score=desired_value
        )
        
        if association:
            message_text = f"Вы установили желаемый балл {desired_value} для предмета «{subject_name}».\n\nДостойная цель! Не останавливайтесь ни перед чем и продолжайте учиться! 🚀"
        else:
            message_text = f"⚠️ Не удалось установить балл. Убедитесь, что предмет выбран в разделе /subjects"
            
        await bot.send_message(message.chat.id, text=message_text)
        
        if logger:
            logger.info(f"User {user_id} set desired score {desired_value} for subject {subject_id}")
            
    except Exception as e:
        if logger:
            logger.error(f"Error setting desired score for user {user_id}: {e}")
        await bot.send_message(message.chat.id, "Произошла ошибка при сохранении данных. Попробуйте позже.")


async def insert_score_handler(message: types.Message, db: AsyncSession, logger: Logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    user_id = user.id
    
    try:
        score_value = int(message.text)
    except ValueError:
        await bot.send_message(message.chat.id, "Пожалуйста, введите корректное число")
        return
    
    if not 0 <= score_value <= 100:
        await bot.send_message(message.chat.id, "Пожалуйста, введите число от 0 до 100")
        return
    
    subject_id = pending_user_subjects.get(user_id)
    if not subject_id:
        await bot.send_message(message.chat.id, "Что-то пошло не так. Пожалуйста, начните процесс заново, используя команду /add_score")
        return
    
    subject_name = EGE_SUBJECTS_DICT.get(subject_id)
    
    del pending_user_subjects[user_id]
    await bot.delete_state(user_id, chat_id=message.chat.id)
    
    try:
        new_score = await crud.add_score(
            db, 
            user_id=user_id,
            subject_id=subject_id,
            score=score_value,
            subject_name=subject_name
        )
        
        if new_score:
            message_text = f"✅ Балл {score_value} по предмету «{subject_name}» успешно сохранен!\n\n"
            
            scores = await crud.get_all_scores_for_user(db, id=user_id, subject_id=subject_id)
            if scores:
                message_text += f"Всего сохранено попыток: {len(scores)}\n"
                message_text += f"Средний балл: {sum(s.score for s in scores) / len(scores):.1f}\n"
                message_text += f"Максимальный балл: {max(s.score for s in scores)}"
        else:
            message_text = "⚠️ Не удалось сохранить балл. Попробуйте позже."
            
        await bot.send_message(message.chat.id, text=message_text)
        
        if logger:
            logger.info(f"User {user_id} added score {score_value} for subject {subject_id}")
            
    except Exception as e:
        if logger:
            logger.error(f"Error adding score for user {user_id}: {e}")
        await bot.send_message(message.chat.id, "Произошла ошибка при сохранении данных. Попробуйте позже.")