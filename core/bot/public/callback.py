import asyncio
import datetime

from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.utils.exceptions import MessageNotModified

from core.bot import public_bot, private_bot
from core.bot.private.keyboards import get_appeal_to_work_button, get_temp_buttons_for_operator
from core.bot.public.commands import send_current_state
from core.bot.public.instructions import (
    text_input_address,
    text_input_animals,
    text_input_count_animals,
    text_for_send_data,
    text_menu,
    text_input_media,
    text_input_contact,
    text_status
)
from core.bot.public.keyboards import (
    get_appeals_buttons
)
from core.bot.public.send_channel import (
    send_media_group_to_channel,
    send_media_to_channel,
    send_text_to_channel,
    edit_message_to_channel
)
from core.database.operations import DataBase
from core.functions.config import Config
from core.functions.geocoder import geocoder, parse_address, Geocode

db = DataBase()
config = Config()


async def get_call_animals(call: CallbackQuery, animal_name: str):
    await db.update_user_data('users', call.message.chat.id, animal=animal_name,
                              message_id=call.message.message_id,
                              action='input_count_animals')
    text, reply_markup = await text_input_count_animals(call.message.chat.id)
    await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def input_media(call: CallbackQuery):
    await db.update_media_status(call.message.chat.id, new_status='delete', check_status='queue')
    await db.update_user_data('users', call.message.chat.id, action='send_data', media=False)
    text, reply_markup = await text_for_send_data(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def input_contact(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_contact')
    text, reply_markup = await text_input_contact(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def input_animal(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_animals')
    text, reply_markup = await text_input_animals(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def send_data(call: CallbackQuery):
    fullname = call.message.chat.full_name
    username = f"@{call.message.chat.username}"
    telegram_id = call.message.chat.id
    await call.message.edit_reply_markup(reply_markup=None)
    await public_bot.send_chat_action(telegram_id, ChatActions.TYPING)

    date_now = datetime.datetime.now()

    address, animal, count_animal, media = \
        await db.get_user_data('users', telegram_id, ['address', 'animal', 'count_animal', 'media'])

    appeal_id = await db.insert_data('table_appeal', returning_info='appeal_id',
                                     fullname=fullname, username=username, telegram_id=telegram_id, animal=animal,
                                     address=address, count_animal=count_animal, media=media, date_create=date_now,
                                     status='sent')
    geodata = await parse_address(address)
    address = await geocoder(address)
    text = f'<b><u>Обращение №{appeal_id}:</u></b>\n\n' \
           f"Адрес: <b>{address}</b>\n" \
           f"Вид животного: <b>{animal}</b>\n" \
           f"Общее количество животных: <b>{count_animal}</b>"

    if 'None' not in username:
        text += f"\n\nПользователь: {username}"
    else:
        text += f"\n\nПользователь: Закрытый профиль"

    reply_markup = await get_appeal_to_work_button(appeal_id)
    chats = await db.get_chats_id()
    sent_appeal_to_chats = []
    tasks = []
    if media:
        media_files = (await db.get_media_files(telegram_id))[:5]
        if len(media_files) > 1:
            # Распараллеливаем отправку сообщений операторам (из-за возможных медиа)
            for chat in chats:
                tasks.append(asyncio.create_task(send_media_group(media_files, chat, text, reply_markup, appeal_id, geodata)))
            tasks.append(asyncio.create_task(send_media_group_to_channel(media_files, config.channel_id, text, None, appeal_id, geodata)))
            for i, task in enumerate(tasks):
                if i == len(tasks)-1:
                    result_channel = await task
                else:
                    result = await task
                    sent_appeal_to_chats.append(result)

        else:
            media_file = media_files[0]
            for chat in chats:
                tasks.append(asyncio.create_task(send_media(media_file, chat, text, reply_markup, appeal_id, geodata)))
            tasks.append(asyncio.create_task(send_media_to_channel(media_file, config.channel_id, text, None, appeal_id, geodata)))

            for i, task in enumerate(tasks):
                if i == len(tasks) - 1:
                    result_channel = await task
                else:
                    result = await task
                    sent_appeal_to_chats.append(result)

        await db.update_media_appeal_id(telegram_id, appeal_id)
    else:
        for chat in chats:
            tasks.append(asyncio.create_task(send_text(chat, text, reply_markup, appeal_id, geodata)))
        tasks.append(send_text_to_channel(config.channel_id, text, None, appeal_id, geodata))
        for i, task in enumerate(tasks):
            if i == len(tasks) - 1:
                result_channel = await task
            else:
                result = await task
                sent_appeal_to_chats.append(result)

    await db.insert_sent_appeal_to_chats(sent_appeal_to_chats)

    await db.update_user_data('users', telegram_id, action='menu', message_id=call.message.message_id,
                              appeal_id=appeal_id)
    await db.update_appeal_data(appeal_id, channel_message_id=result_channel['message_id'])
    text, reply_markup = await text_menu(telegram_id)

    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def update_appeal(call: CallbackQuery):
    telegram_id = call.message.chat.id
    username = f"@{call.message.chat.username}"
    address, count_animal, media, contact, animal, appeal_id = \
        await db.get_user_data('users', telegram_id, ['address', 'count_animal', 'media',
                                                      'contact', 'animal', 'appeal_id'])
    appeal = await db.get_appeal_data(appeal_id, ['channel_message_id', 'status'])
    address = await geocoder(address)
    if appeal.status != 'done':
        text = f'<b><u>Обращение №{appeal_id}:</u></b>\n\n' \
               f"Адрес: <b>{address}</b>\n" \
               f"Вид животного: <b>{animal}</b>\n" \
               f"Общее количество животных: <b>{count_animal}</b>"

        if contact:
            text += f'\nКонтакты для обратной связи: <b>{contact}</b>'

        if 'None' not in username:
            text += f"\n\nПользователь: {username}"
        else:
            text += f"\n\nПользователь: Закрытый профиль"
        count_media = 0
        if media:
            count_media = await db.get_count_media_files(appeal_id)
        try:
            await edit_message_to_channel(config.channel_id, text, appeal.channel_message_id, count_media)
            reply_markup = await get_temp_buttons_for_operator(appeal_id)
            sent_appeal_info = await db.get_chats_for_edit_appeal_message(appeal_id)
            for chat in sent_appeal_info:
                await edit_message(chat.telegram_id, text, chat.message_id, count_media, reply_markup)
            await db.update_appeal_data(appeal_id, animal=animal, contact=contact)
            await call.answer('Новые данные получены!✅')
        except MessageNotModified as e:
            await call.answer('Не вижу новых данных!❌')
    else:
        await call.answer('Обращение уже отработано!')


async def edit_message(chat_id, text, message_id, count_media, reply_markup=None):
    # print(count_media)
    if count_media == 1:
        await private_bot.edit_message_caption(chat_id, message_id, caption=text, parse_mode='HTML',
                                               reply_markup=reply_markup)
    else:
        await private_bot.edit_message_text(text, chat_id, message_id=message_id, parse_mode='HTML',
                                            reply_markup=reply_markup)


async def send_media_group(media_files: list, chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    media_data = []
    for media_file in media_files:
        if media_file.type_file == 'photo':
            media_data.append(InputMediaPhoto(media=open(media_file.path_file, 'rb'),
                                              caption=text, parse_mode='HTML'))
        elif media_file.type_file == 'video':
            media_data.append(InputMediaVideo(media=open(media_file.path_file, 'rb'),
                                              caption=text, parse_mode='HTML'))

    # await private_bot.send_location()
    location_message_id = (await private_bot.send_location(chat, latitude=geodata.latitude,
                                                           longitude=geodata.longitude)).message_id if geodata else None
    message = await private_bot.send_media_group(chat, media_data, reply_to_message_id=location_message_id)
    message = await private_bot.send_message(chat, text, parse_mode='HTML', reply_markup=reply_markup,
                                             reply_to_message_id=message[0].message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def send_media(media_file, chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    location_message_id = (await private_bot.send_location(chat, latitude=geodata.latitude,
                                                           longitude=geodata.longitude)).message_id if geodata else None
    with open(media_file.path_file, 'rb') as file:
        if media_file.type_file == 'photo':
            message = await private_bot.send_photo(chat, photo=file.read(), caption=text, parse_mode='HTML',
                                                   reply_markup=reply_markup, reply_to_message_id=location_message_id)
        else:
            message = await private_bot.send_video(chat, video=file.read(), caption=text, parse_mode='HTML',
                                                   reply_markup=reply_markup, reply_to_message_id=location_message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def send_text(chat: int, text: str, reply_markup, appeal_id: int, geodata: Geocode):
    location_message_id = (await private_bot.send_location(chat, latitude=geodata.latitude,
                                                           longitude=geodata.longitude)).message_id if geodata else None
    message = await private_bot.send_message(chat, text, parse_mode='HTML', reply_markup=reply_markup,
                                             reply_to_message_id=location_message_id)
    return {
        'appeal_id': appeal_id,
        'message_id': message.message_id,
        'telegram_id': chat
    }


async def delete_files(call: CallbackQuery):
    await db.update_media_status(call.message.chat.id, new_status='delete', check_status='queue')
    await db.update_user_data('public_users', call.message.chat.id, media=False)
    text, reply_markup = await text_input_media(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def paginate(call: CallbackQuery, page: int):
    appeal_ids = await db.get_appeal_ids(call.message.chat.id)
    keyboard = await get_appeals_buttons(appeal_ids, page)
    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()


async def edit_appeal_text(call: CallbackQuery, appeal_id: int):
    text = await text_status(call.message.chat.id, appeal_id)
    try:
        await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=call.message.reply_markup)
    except: pass
    await call.answer()


async def continue_appeal(call: CallbackQuery):
    action, edit_message_id = await db.get_user_data('users', call.message.chat.id, ['action', 'message_id'])
    await send_current_state(call.message.chat.id, action, edit_message_id, call=call)
    await call.answer()


async def back_to_input_address(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_address')
    text, reply_markup = await text_input_address(call.message.chat.id)
    await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def back_to_input_animals(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_animals')
    text, reply_markup = await text_input_animals(call.message.chat.id)
    await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def back_input_count_animals(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_count_animals')
    text, reply_markup = await text_input_count_animals(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def back_to_input_media(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_media')
    text, reply_markup = await text_input_media(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def back_to_menu(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='menu')
    text, reply_markup = await text_menu(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def next_input_animals(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_animals')
    text, reply_markup = await text_input_animals(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def next_count_animals(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_count_animals')
    text, reply_markup = await text_input_count_animals(call.message.chat.id)
    await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer('')


async def next_input_media(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='input_media')
    text, reply_markup = await text_input_media(call.message.chat.id)
    await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def next_send_menu(call: CallbackQuery):
    await db.update_user_data('users', call.message.chat.id, action='send_menu')
    text, reply_markup = await text_for_send_data(call.message.chat.id)
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()
