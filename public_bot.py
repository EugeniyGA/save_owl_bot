import traceback
from datetime import datetime

from aiogram import executor
from aiogram.types import Message, CallbackQuery, ContentTypes

from core.bot import public_dp, public_bot
from core.bot.errors import send_error
from core.bot.public.callback import (
    get_call_animals,
    input_media,
    input_contact,
    input_animal,
    send_data,
    update_appeal,
    delete_files,
    paginate,
    edit_appeal_text,
    continue_appeal,
    back_to_input_address,
    back_to_input_animals,
    back_input_count_animals,
    back_to_input_media,
    back_to_menu,
    next_count_animals,
    next_input_media, next_send_menu, next_input_animals
)
from core.bot.public.commands import get_start, get_new_appeal, get_help, get_status
from core.bot.public.keyboards import PAGINATE, APPEALS
from core.bot.public.media_files import get_photo, get_video
from core.bot.public.message_handler import (
    get_address,
    get_address_location,
    get_number_animals,
    get_contact,
    new_appeal,
    get_animals
)
from core.database.operations import DataBase
from core.functions.config import Config
from core.functions.logger import create_logger

config = Config()
db = DataBase()


logger = create_logger('public_bot.log', 'public_bot_logger')


@public_dp.message_handler(commands=['start', 'new', 'help', 'status'])
@db.check_public_user
async def get_commands(message: Message):
    try:
        if message.get_command(True) == 'start':
            await get_start(message)
        elif message.get_command(True) == 'new':
            await get_new_appeal(message)
        elif message.get_command(True) == 'help':
            await get_help(message)
        elif message.get_command(True) == 'status':
            await get_status(message)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


@public_dp.message_handler(content_types=['location'])
@db.check_public_user
async def get_location(message: Message):
    try:
        action, edit_message_id = await db.get_user_data('public_users', message.chat.id, fields=['action', 'message_id'])
        if action == 'input_address':
            await get_address_location(message, edit_message_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


@public_dp.message_handler(content_types=ContentTypes.TEXT)
@db.check_public_user
async def get_message(message: Message):
    try:
        action, edit_message_id = await db.get_user_data('public_users', message.chat.id, fields=['action', 'message_id'])
        if message.text == 'Новое обращение':
            await new_appeal(message, edit_message_id)
        elif message.text == 'Статус':
            await get_status(message)
        elif message.text == 'Помощь':
            await get_help(message)
        else:
            if action == 'input_address':
                await get_address(message, edit_message_id)
            elif action == 'input_count_animals':
                await get_number_animals(message, edit_message_id)
            elif action == 'input_contact':
                await get_contact(message, edit_message_id)
            elif action == 'input_animals':
                await get_animals(message, edit_message_id)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


@public_dp.message_handler(content_types=['photo', 'video'])
@db.check_public_user
async def get_media(message: Message):
    try:
        date = datetime.now().date()
        action, edit_message_id = await db.get_user_data('public_users', message.chat.id, fields=['action', 'message_id'])
        if action == 'input_media':
            if message.content_type == 'photo':
                file_name = f'image{message.photo[-1].file_unique_id}.jpg'
                file_path = f'src/images/{date}/{file_name}'
                await get_photo(message, edit_message_id, file_path)

            elif message.content_type == 'video':
                file_name = f'video{message.video.file_unique_id}.mp4'
                file_path = f'src/videos/{date}/{file_name}'
                await get_video(message, edit_message_id, file_path)

    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


# Обрабатываем нажатие на кнопки пагинации
@public_dp.callback_query_handler(PAGINATE.filter())
@db.check_ban_user
async def process_callback_paginate(call: CallbackQuery, callback_data: dict):
    try:
        # получаем номер страницы, которая была нажата
        page = int(callback_data["page"])
        await paginate(call, page)
        # редактируем сообщение, чтобы убрать уведомление об ошибке
        await call.answer()
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


@public_dp.callback_query_handler(APPEALS.filter())
@db.check_ban_user
async def get_callback_appeals(call: CallbackQuery, callback_data: dict):
    try:
        appeal_id = int(callback_data["id"])
        await edit_appeal_text(call, appeal_id)
        await call.answer()
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


@public_dp.callback_query_handler()
@db.check_ban_user
async def get_callback(call: CallbackQuery, callback_data: dict):
    try:
        # Выбор вида животного по кнопке
        if animal_name := await db.check_animals(call.data):
            await get_call_animals(call, animal_name)

        # Дополнительные опции
        elif call.data == 'input_media':
            await input_media(call)
        elif call.data == 'input_contact':
            await input_contact(call)
        elif call.data == 'input_animals':
            await input_animal(call)
        elif call.data == 'not_media':
            await input_media(call)

        # Отправка
        elif call.data == 'send_data':
            await send_data(call)

        elif call.data == 'update_data':
            await update_appeal(call)

        elif call.data == 'delete_files':
            await delete_files(call)

        # back
        elif call.data == 'back_input_address':
            await back_to_input_address(call)

        elif call.data == 'back_input_animals':
            await back_to_input_animals(call)

        elif call.data == 'back_input_count_animals':
            await back_input_count_animals(call)
        elif call.data == 'back_input_media':
            await back_to_input_media(call)
        elif call.data == 'back_to_menu':
            await back_to_menu(call)

        elif call.data == 'continue':
            await continue_appeal(call)

        # next
        elif call.data == 'next_send_menu':
            await next_send_menu(call)
        elif call.data == 'next_input_media':
            await next_input_media(call)
        elif call.data == 'next_count_animals':
            await next_count_animals(call)
        elif call.data == 'next_input_animals':
            await next_input_animals(call)
    except Exception as e:
        error = f"{e}\n\n{traceback.format_exc(limit=3)}"
        logger.info(error)
        await send_error(public_bot, error)


if __name__ == '__main__':
    executor.start_polling(public_dp, skip_updates=True)
