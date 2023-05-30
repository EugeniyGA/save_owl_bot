from aiogram import Bot, Dispatcher

from core.functions.config import Config

config = Config()

public_bot = Bot(config.bot_token)
public_dp = Dispatcher(public_bot)

private_bot = Bot(config.bot_private_token)
private_dp = Dispatcher(private_bot)

moderator_bot_1 = Bot(config.bot_moderator_1_token)
moderator_bot_2 = Bot(config.bot_moderator_2_token)
moderator_bot_3 = Bot(config.bot_moderator_3_token)
moderator_bot_4 = Bot(config.bot_moderator_4_token)

instruction_bot = Bot(config.bot_instruction)
instruction_dp = Dispatcher(instruction_bot)
