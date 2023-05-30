from aiogram.types import Message, CallbackQuery

from core.bot import public_bot
from core.bot.public.instructions import (
    text_welcome,
    text_help,
    text_status,
    text_input_address,
    text_input_animals,
    text_input_count_animals,
    text_menu,
    text_input_media,
    text_input_contact,
    text_for_send_data
)
from core.bot.public.keyboards import new_appeal_button
from core.bot.public.message_handler import new_appeal
from core.database.operations import DataBase

db = DataBase()


async def send_message(telegram_id, edit_message_id, text, reply_markup):
    if edit_message_id:
        try:
            await public_bot.edit_message_reply_markup(telegram_id, edit_message_id)
        except:
            pass
    result = await public_bot.send_message(telegram_id, text, parse_mode='HTML', reply_markup=reply_markup)
    await db.update_user_data('users', telegram_id, message_id=result.message_id)


async def get_start(message: Message):
    action, edit_message_id = await db.get_user_data('users', message.chat.id, ['action', 'message_id'])
    if action:
        await send_current_state(message.chat.id, action, edit_message_id)
    else:
        await db.update_user_data('users', message.chat.id, action='input_address')
        text_answer = await text_welcome(message)
        await public_bot.send_message(message.chat.id, text_answer, parse_mode='HTML',
                                      reply_markup=await new_appeal_button())


async def get_help(message: Message):
    action, edit_message_id = await db.get_user_data('users', message.chat.id, ['action', 'message_id'])
    text = await text_help()
    await public_bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)

    if action:
        await send_current_state(message.chat.id, action, edit_message_id)


async def get_status(message: Message):
    edit_message_id, = await db.get_user_data('users', message.chat.id, ['message_id'])
    if edit_message_id:
        try:
            await public_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
        except: pass
    text, reply_markup = await text_status(message.chat.id)
    result = await public_bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=reply_markup)
    await db.update_user_data('users', message.chat.id, message_id=result.message_id)


async def send_current_state(telegram_id, action, edit_message_id, call: CallbackQuery = None):
    if action == 'input_address' or action == 'wait':
        await db.update_user_data('users', telegram_id, action='input_address')
        text, reply_markup = await text_input_address(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)
    elif action == 'input_animals':
        text, reply_markup = await text_input_animals(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)
    elif action == 'input_count_animals':
        text, reply_markup = await text_input_count_animals(telegram_id)
        await send_message(telegram_id, edit_message_id, text, reply_markup)

    elif action == 'send_menu':
        text, reply_markup = await text_for_send_data(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)
    elif action == 'menu':
        text, reply_markup = await text_menu(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)
    elif action == 'input_media':
        text, reply_markup = await text_input_media(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)
    elif action == 'input_contact':
        text, reply_markup = await text_input_contact(telegram_id)
        if call:
            await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await send_message(telegram_id, edit_message_id, text, reply_markup)


async def get_new_appeal(message: Message):
    edit_message_id, = await db.get_user_data('users', message.chat.id, fields=['message_id'])
    await new_appeal(message, edit_message_id)
