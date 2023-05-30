import traceback

from aiogram import executor
from aiogram.types import Message, CallbackQuery

from core.bot import private_bot, private_dp
from core.bot.errors import send_error
from core.bot.private.callback import (
    get_appeal_to_work,
    get_appeal_done,
    get_appeal_ban,
    accept_ban,
    decline_ban, generate_link,
    delete_user, back_to_menu, get_role_for_delete_user, paginate, user_deletion_confirmation, accept_delete_user,
    get_appeal_to_answer,
    get_callback_reject, send_reject_to_public_user
)
from core.bot.private.commands import get_start, get_help
from core.bot.private.keyboards import (
    APPEAL_ANSWER,
    APPEAL_WORK,
    APPEAL_DONE,
    APPEAL_BAN,
    ACCEPT_BAN,
    DECLINE_BAN,
    PAGINATE,
    USERS,
    ACCEPT_CLOSE_USER, APPEAL_REJECT
)
from core.bot.private.message_handler import get_answer
from core.database.operations import DataBase
from core.functions.config import Config
from core.functions.logger import create_logger

db = DataBase()
config = Config()

logger = create_logger('private_bot.log', 'private_bot_logger')


@private_dp.message_handler(commands=['start', 'help'])
@db.check_private_user
async def get_command(message: Message):
    try:
        if message.get_command(True) == 'start':
            await get_start(message)
        if message.get_command(True) == 'help':
            await get_help(message)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.message_handler(content_types=['text'])
@db.check_private_user
async def get_message(message: Message):
    try:
        action, appeal_id, text_appeal = await db.get_user_data('private_users', message.chat.id,
                                                                ['action', 'appeal_id', 'text_answer'])
        if action == 'answer':
            await get_answer(message, appeal_id, text_appeal)
        else:
            await private_bot.send_message(message.chat.id, 'Сперва выберите обращение, '
                                                            'для которого хотите отправить комментарий',
                                           reply_to_message_id=message.message_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(APPEAL_REJECT.filter())
@db.check_disable_private_user
async def get_callback_appeal_to_reject(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        await get_callback_reject(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(APPEAL_ANSWER.filter())
@db.check_disable_private_user
async def get_callback_appeal_to_answer(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        await get_appeal_to_answer(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(APPEAL_WORK.filter())
@db.check_disable_private_user
async def get_callback_appeal_to_work(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        # print(appeal_id)
        await get_appeal_to_work(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(APPEAL_DONE.filter())
@db.check_disable_private_user
async def get_callback_appeal_done(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        # print(appeal_id)
        await get_appeal_done(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(APPEAL_BAN.filter())
@db.check_disable_private_user
async def get_callback_appeal_ban(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        await get_appeal_ban(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(ACCEPT_BAN.filter())
@db.check_disable_private_user
async def get_callback_accept_ban(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        await accept_ban(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(DECLINE_BAN.filter())
@db.check_disable_private_user
async def get_callback_decline_ban(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data['appeal_id'])
        await decline_ban(call, appeal_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(PAGINATE.filter())
@db.check_disable_private_user
async def process_callback_paginate(call: CallbackQuery, callback_data: dict):
    try:
        page = int(callback_data["page"])
        # print(page)
        await paginate(call, page)
        await call.answer()
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(USERS.filter())
@db.check_disable_private_user
async def get_user_for_delete(call: CallbackQuery, callback_data: dict):
    try:
        telegram_id = int(callback_data['telegram_id'])
        await user_deletion_confirmation(call, telegram_id)
        await call.answer()
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler(ACCEPT_CLOSE_USER.filter())
@db.check_disable_private_user
async def accept_close_user(call: CallbackQuery, callback_data: dict):
    try:
        telegram_id = int(callback_data['telegram_id'])
        await accept_delete_user(call, telegram_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


@private_dp.callback_query_handler()
@db.check_disable_private_user
async def get_callback(call: CallbackQuery, callback_data: dict):
    try:
        print(call.data)
        if ':' in call.data:
            # 0 - reject_key, 1 - appeal_id
            parse_call_data = call.data.split(':')
            if reject_text := await db.check_reject(parse_call_data[0]):
                await send_reject_to_public_user(call, reject_text, int(parse_call_data[1]))
        else:
            if call.data in ['superadmin', 'operator']:
                await generate_link(call)
            elif call.data in ['delete_user', 'back_to_choose_role_delete']:
                await delete_user(call)
            elif call.data in ['delete_operators', 'delete_superadmins']:
                await get_role_for_delete_user(call)
            elif call.data == 'back_to_menu':
                await back_to_menu(call)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(private_bot, error)


if __name__ == '__main__':
    executor.start_polling(private_dp)
