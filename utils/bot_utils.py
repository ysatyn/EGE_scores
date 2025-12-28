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