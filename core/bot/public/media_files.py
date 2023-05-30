import asyncio
import os

from aiogram.types import Message, ChatActions

from core.bot import public_bot
from core.bot.public.instructions import (
    text_for_send_data
)
from core.database.operations import DataBase

db = DataBase()


def check_media(func):
    async def wrapper(message: Message, edit_message_id, file_path):
        '''
        Декоратор загружает путь к файлу в БД со статусом wait - в ожидании пока подгрузятся остальные
        Используется небольшой костыль в виде try - except, во первых, чтобы пользователь лишний раз не тыкал на кнопки,
        пока подргужаются все медиа, изменяется тело сообщения в tg, во вторых, данное изменение помогает не реагировать
        повторно, если подгружается пачка картинок или фото

        sleep - чтобы успело подгрузиться все

        Далее файлы получают статус queue - в очереди на отправку

        :param message:
        :param edit_message_id: - сообщение которое необходимо изменить
        :param file_path:
        :return:
        '''
        path = file_path.rsplit('/', 1)[0]
        if not os.path.exists(path):
            os.mkdir(path)
        await public_bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        await db.insert_data('table_media', telegram_id=message.chat.id, path_file=file_path, status='wait',
                             type_file=message.content_type)
        try:
            await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
            await func(message, edit_message_id, file_path)
            await asyncio.sleep(2)
            await db.update_media_status(message.chat.id, new_status='queue', check_status='wait')
            text, reply_markup = await text_for_send_data(message.chat.id, media_input=True)
            result = await public_bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=reply_markup)
            await db.update_user_data('users', message.chat.id, action='send_menu', media=True,
                                      message_id=result.message_id)
        except Exception as e:
            await func(message, edit_message_id, file_path)

    return wrapper


@check_media
async def get_photo(message: Message, edit_message_id, file_path: str):
    file_info = await public_bot.get_file(message.photo[-1].file_id)
    download_file = await public_bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(download_file.read())


@check_media
async def get_video(message: Message, edit_message_id, file_path: str):
    file_info = await public_bot.get_file(message.video.file_id)
    download_file = await public_bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(download_file.read())
