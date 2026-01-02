from telebot import types
from telebot.async_telebot import AsyncTeleBot
from sqlalchemy.ext.asyncio import AsyncSession

from utils.obertka import make_registered_handler
from utils.stats import prepare_simple_chart_data, get_simple_stats
from utils.simple_charts import generate_simple_progress_chart
from db import crud

def register_handlers(bot: AsyncTeleBot, logger=None):
    handler = make_registered_handler(stats_handler, bot=bot, logger=logger)
    bot.register_message_handler(handler, commands=["stats", "график"])
    
    bot.register_callback_query_handler(
        handler,
        func=lambda call: call.data == "show_stats"
    )

async def stats_handler(message: types.Message, db: AsyncSession, logger, bot: AsyncTeleBot):
    user = await crud.create_or_update_user(db, **message.from_user.__dict__)
    
    scores = await crud.get_all_scores_for_user(db, id=user.id, subject_id=None)
    
    if not scores:
        await bot.send_message(
            message.chat.id,
            "📭 У вас пока нет сохранённых результатов.\n"
            "Добавьте первые баллы через /add_score"
        )
        return
    
    # Подготавливаем данные для графика
    chart_data = prepare_simple_chart_data(scores)
    
    # Генерируем график
    chart_buffer = generate_simple_progress_chart(chart_data)
    
    # Генерируем текст статистики для подписи
    stats_text = get_simple_stats(scores)
    
    caption = f"{stats_text}\n\n📈 *Прогресс по предметам*\n• Каждый цвет — отдельный предмет"
    
    await bot.send_photo(
        message.chat.id,
        chart_buffer,
        caption=caption,
        parse_mode="Markdown"
    )