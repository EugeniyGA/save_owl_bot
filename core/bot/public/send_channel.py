from aiogram import Bot
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo

from core.bot import private_bot, moderator_bot_1, moderator_bot_2, moderator_bot_3, moderator_bot_4
from core.functions.geocoder import Geocode


def retry_send_message(func):
    async def wrapper(bot, *args, **kwargs):
        '''
        Ретрай отправки сообщений в канал
        Используется пачка ботов, поскольку для отправки сообщений
        в канал есть ограничение на 20 сообщений в минуту
        :param bot:
        :param args:
        :param kwargs:
        :return:
        '''
        bots = [private_bot, moderator_bot_1, moderator_bot_2,
                moderator_bot_3, moderator_bot_4]
        retry_number = 0
        while retry_number != 5:
            try:
                result = await func(bots[retry_number], *args, **kwargs)
                return result
            except Exception as e:
                retry_number += 1
                continue
    return wrapper


@retry_send_message
async def send_location(bot: Bot, chat, geodata: Geocode) -> Message:
    message = await bot.send_location(chat, latitude=geodata.latitude, longitude=geodata.longitude)
    return message


@retry_send_message
async def send_photo(bot: Bot, chat: int, photo, text, reply_markup, location_message_id):
    message = await bot.send_photo(chat, photo=photo, caption=text, parse_mode='HTML',
                                   reply_markup=reply_markup, reply_to_message_id=location_message_id)
    return message


@retry_send_message
async def send_video(bot: Bot, chat: int, video, text, reply_markup, location_message_id):
    message = await bot.send_video(chat, video=video, caption=text, parse_mode='HTML',
                                   reply_markup=reply_markup, reply_to_message_id=location_message_id)
    return message


@retry_send_message
async def send_message(bot: Bot, chat: int, text, reply_markup, location_message_id):
    message = await bot.send_message(chat, text, parse_mode='HTML', reply_markup=reply_markup,
                                     reply_to_message_id=location_message_id)
    return message


@retry_send_message
async def send_media_group(bot: Bot, chat: int, media_files, text, location_message_id):
    media_data = []
    for media_file in media_files:
        if media_file.type_file == 'photo':
            media_data.append(InputMediaPhoto(media=open(media_file.path_file, 'rb'),
                                              caption=text, parse_mode='HTML'))
        elif media_file.type_file == 'video':
            media_data.append(InputMediaVideo(media=open(media_file.path_file, 'rb'),
                                              caption=text, parse_mode='HTML'))
    message = await bot.send_media_group(chat, media_data, reply_to_message_id=location_message_id)
    return message


@retry_send_message
async def edit_message_caption(bot, chat_id, message_id, text, reply_markup):
    await bot.edit_message_caption(chat_id, message_id, caption=text, parse_mode='HTML',
                                   reply_markup=reply_markup)


@retry_send_message
async def edit_message_text(bot, chat_id, message_id, text, reply_markup):
    await bot.edit_message_text(text, chat_id, message_id=message_id, parse_mode='HTML',
                                reply_markup=reply_markup)


async def send_media_to_channel(media_file, chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    try:
        location_message_id = (await send_location(bot=private_bot, chat=chat, geodata=geodata)).message_id if geodata else None
    except:
        location_message_id = None
    with open(media_file.path_file, 'rb') as file:
        if media_file.type_file == 'photo':
            message = await send_photo(private_bot, chat, file.read(), text, reply_markup, location_message_id)
        else:
            message = await send_video(private_bot, chat, file.read(), text, reply_markup, location_message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def send_text_to_channel(chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    try:
        location_message_id = (await send_location(bot=private_bot, chat=chat, geodata=geodata)).message_id if geodata else None
    except:
        location_message_id = None
    message = await send_message(private_bot, chat, text, reply_markup, location_message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def send_media_group_to_channel(media_files: list, chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    try:
        location_message_id = (await send_location(bot=private_bot, chat=chat, geodata=geodata)).message_id if geodata else None
    except:
        location_message_id = None

    message = await send_media_group(private_bot, chat, media_files, text, location_message_id)
    message = await send_message(private_bot, chat, text, reply_markup, message[0].message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def edit_message_to_channel(chat_id, text, message_id, count_media, reply_markup=None):
    if count_media == 1:
        await edit_message_caption(private_bot, chat_id, message_id, text, reply_markup)
    else:
        await edit_message_text(private_bot, chat_id, message_id, text, reply_markup)
