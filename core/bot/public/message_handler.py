from aiogram.types import Message

from core.bot import public_bot
from core.bot.public.instructions import (
    text_input_media,
    text_input_count_animals,
    text_input_address,
    text_menu, text_input_animals
)
from core.bot.public.keyboards import new_appeal_button
from core.database.operations import DataBase
from core.functions.data_validity import check_bad_words, check_valid_contact

db = DataBase()


async def new_appeal(message: Message, edit_message_id):
    media, = await db.get_user_data('users', message.chat.id, ['media'])
    if media:
        await db.update_media_status(message.chat.id, new_status='delete', check_status='queue')
    await db.update_user_data('users', message.chat.id, action='input_address', message_id=None, address=None,
                              animal=None, count_animal=None, contact=None, media=None)
    text, reply_markup = await text_input_address(message.chat.id)
    if not reply_markup:
        reply_markup = await new_appeal_button()
    if edit_message_id:
        try:
            await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
        except: pass
    await public_bot.send_message(message.chat.id, text, reply_markup=reply_markup, parse_mode='HTML')


async def get_address(message: Message, edit_message_id):
    text, reply_markup = await text_input_animals(message.chat.id)
    if edit_message_id:
        try:
            await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
        except:
            pass
    result = await public_bot.send_message(message.chat.id, text, reply_markup=reply_markup, parse_mode='HTML')
    await db.update_user_data('users', message.chat.id, address=message.text, action='input_animals',
                              message_id=result.message_id)


async def get_address_location(message: Message, edit_message_id):
    text, reply_markup = await text_input_animals(message.chat.id)
    if edit_message_id:
        try:
            await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
        except:
            pass
    result = await public_bot.send_message(message.chat.id, text, reply_markup=reply_markup, parse_mode='HTML')
    location = f"geo:{message.location.latitude}:{message.location.longitude}"
    await db.update_user_data('users', message.chat.id, address=location, action='input_animals',
                              message_id=result.message_id)


@check_bad_words
async def get_animals(message: Message, edit_message_id):
    text, reply_markup = await text_input_count_animals(message.chat.id)
    if edit_message_id:
        await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
    result = await public_bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode='HTML')
    await db.update_user_data('users', message.chat.id, animal=message.text[:95], message_id=result.message_id,
                              action='input_count_animals')


async def get_number_animals(message: Message, edit_message_id):
    # Загрузка медиа
    text, reply_markup = await text_input_media(message.chat.id)
    if edit_message_id:
        await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
    result = await public_bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode='HTML')
    await db.update_user_data('users', message.chat.id, count_animal=message.text, message_id=result.message_id,
                              action='input_media')


@check_valid_contact
async def get_contact(message: Message, edit_message_id):
    text, reply_markup = await text_menu(message.chat.id, contact_input=message.text)
    if edit_message_id:
        await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
    result = await public_bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode='HTML')
    await db.update_user_data('users', message.chat.id, contact=message.text[:145], message_id=result.message_id,
                              action='menu')
