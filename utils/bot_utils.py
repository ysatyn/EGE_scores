from telebot import types
from telebot.async_telebot import AsyncTeleBot

async def del_message_from_callback(bot: AsyncTeleBot, call: types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass
    return 

BOT_COMMANDS = [
    types.BotCommand("start", "Начало работы"),
    types.BotCommand("help", "Помощь"),
    types.BotCommand("subjects", "Выбрать предметы"),
    types.BotCommand("set_desired_score", "Установить цель"),
    types.BotCommand("add_score", "Добавить результат"),
    types.BotCommand("profile", "Профиль"),
]

async def register_bot_commands(bot: AsyncTeleBot) -> None:
    await bot.set_my_commands(BOT_COMMANDS)
    