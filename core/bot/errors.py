from core.bot.public.send_channel import retry_send_message
from aiogram import Bot
from core.functions.config import Config

config = Config()


@retry_send_message
async def send_error(bot: Bot, error: str):
    await bot.send_message(config.errors_id, error)
