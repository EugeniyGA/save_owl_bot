import secrets

from aiogram.types import CallbackQuery

from core.bot import public_bot, private_bot
from core.bot.private.instructions import text_generate_link, text_delete_users, text_menu
from core.bot.private.keyboards import (
    get_appeal_to_work_button,
    get_appeal_to_done_button,
    accept_ban_user_buttons,
    get_users_button, user_deletion_confirmation_buttons,
    get_rejects_buttons
)
from core.database.operations import DataBase
from core.functions.config import Config

db = DataBase()
config = Config()


async def send_reject_to_public_user(call: CallbackQuery, reject_text: str, appeal_id: int):
    chats = await db.get_chats_for_edit_appeal_message(appeal_id)
    superadmin_ids = await db.get_supperadmin_ids()
    for chat in chats:
        await edit_text(call, chat.telegram_id, chat.message_id, call.message.entities,
                        f"\n\nОтклонено\n\n{reject_text}")

    for superadmin_id in superadmin_ids:
        await private_bot.send_message(superadmin_id.telegram_id,
                                       f'Обращение {appeal_id} - отклонено!\n\n'
                                       f'Причина: {reject_text}\n\n'
                                       f"Оператор: <a href='tg://user?id={call.message.chat.id}'>"
                                       f"{call.message.chat.full_name}</a>", parse_mode='HTML')

    await db.update_user_data('admins', call.message.chat.id, action='wait', text_answer=None, appeal_id=None)

    await db.insert_data('log_admin', appeal_id=appeal_id, telegram_id=call.message.chat.id,
                         status=f'Отклонено: {reject_text}')
    public_user_id = await db.update_appeal_data(appeal_id, return_telegram_id=True, answer=reject_text, status='reject')

    text_answer = f'Обращение №{appeal_id} отклонено!\n\nПричина: {reject_text}'
    await public_bot.send_message(public_user_id, text_answer)
    await call.answer()


async def get_callback_reject(call: CallbackQuery, appeal_id):
    reply_markup = await get_rejects_buttons(appeal_id)
    await call.message.edit_reply_markup(reply_markup)
    await call.answer()


async def get_appeal_to_answer(call: CallbackQuery, appeal_id: int):
    await db.update_user_data('admins', call.message.chat.id, action='answer',
                              appeal_id=appeal_id, text_answer=call.message.text)
    await call.message.reply(f'Укажите комментарий для пользователя с обращением №{appeal_id}\n\n'
                             f'После отправки комментария, обращение получит статус отработано.')
    await call.answer()


async def get_appeal_to_work(call: CallbackQuery, appeal_id: int):
    reply_markup = await get_appeal_to_done_button(appeal_id)
    chats = await db.get_chats_for_edit_appeal_message(appeal_id)
    superadmin_ids = await db.get_supperadmin_ids()
    for chat in chats:
        await edit_text(call, chat.telegram_id, chat.message_id, call.message.entities,
                        f"\n\nВзято в работу!", reply_markup=reply_markup)
    for superadmin_id in superadmin_ids:
        await private_bot.send_message(superadmin_id.telegram_id,
                                       f'Обращение {appeal_id} - взято в работу!\n\n'
                                       f"Оператор: <a href='tg://user?id={call.message.chat.id}'>"
                                       f"{call.message.chat.full_name}</a>", parse_mode='HTML')
    await db.insert_data('log_admin', appeal_id=appeal_id, telegram_id=call.message.chat.id,
                         status='Обращение взято в работу')
    telegram_id = await db.update_appeal_status(appeal_id, new_status='work')
    text_answer = f'Обращение №{appeal_id} взято в работу!'
    await public_bot.send_message(telegram_id, text_answer)
    await call.answer()


async def get_appeal_done(call: CallbackQuery, appeal_id: int):
    chats = await db.get_chats_for_edit_appeal_message(appeal_id)
    superadmin_ids = await db.get_supperadmin_ids()
    for chat in chats:
        await edit_text(call, chat.telegram_id, chat.message_id, call.message.entities,
                        f"\n\nОтработано!", "\n\nВзято в работу!")
    for superadmin_id in superadmin_ids:
        await private_bot.send_message(superadmin_id.telegram_id,
                                       f'Обращение {appeal_id} - отработано!\n\n'
                                       f"Оператор: <a href='tg://user?id={call.message.chat.id}'>"
                                       f"{call.message.chat.full_name}</a>", parse_mode='HTML')

    await db.update_user_data('admins', call.message.chat.id, action='wait', text_answer=None, appeal_id=None)

    await db.insert_data('log_admin', appeal_id=appeal_id, telegram_id=call.message.chat.id,
                         status='Обращение отработано')
    telegram_id = await db.update_appeal_status(appeal_id, new_status='done')
    text_answer = f'Обращение №{appeal_id} отработано!'
    await public_bot.send_message(telegram_id, text_answer)
    await call.answer()


async def get_appeal_ban(call: CallbackQuery, appeal_id: int):
    reply_markup = await accept_ban_user_buttons(appeal_id)
    await call.message.edit_reply_markup(reply_markup)
    await call.answer()


async def accept_ban(call: CallbackQuery, appeal_id: int):
    appeal = await db.get_appeal_data(appeal_id, ['telegram_id', 'fullname'])
    await db.insert_data('ban_chats', chat_id=appeal.telegram_id, chat_name=appeal.fullname)
    await db.insert_data('log_admin', appeal_id=appeal_id, telegram_id=call.message.chat.id,
                         status='Блокировка пользователя')
    superadmin_ids = await db.get_supperadmin_ids()
    for superadmin_id in superadmin_ids:
        await private_bot.send_message(superadmin_id.telegram_id,
                                       f'Пользователь с обращением {appeal_id} - заблокирован!\n\n'
                                       f"Оператор: <a href='tg://user?id={call.message.chat.id}'>"
                                       f"{call.message.chat.full_name}</a>", parse_mode='HTML')
    await public_bot.send_message(appeal.telegram_id, text='Вы заблокированы за неподобающее поведение!')
    chats = await db.get_chats_for_edit_appeal_message(appeal_id)
    for chat in chats:
        await edit_text(call, chat.telegram_id, chat.message_id, call.message.entities, f"\n\nПользователь заблокирован!")

    await call.answer()


async def decline_ban(call: CallbackQuery, appeal_id: int):
    appeal = await db.get_appeal_data(appeal_id, ['status'])
    if appeal.status == 'sent':
        reply_markup = await get_appeal_to_work_button(appeal_id)
    else:
        reply_markup = await get_appeal_to_done_button(appeal_id)
    await call.message.edit_reply_markup(reply_markup)
    await call.answer()


async def edit_text(call: CallbackQuery, chat_id, message_id, entities, new_postfix, old_postfix=None, reply_markup=None):
    if call.message.content_type in ['photo', 'video']:
        text_edit = call.message.caption
        if old_postfix:
            text_edit = text_edit.replace(old_postfix, new_postfix)
        else:
            text_edit += new_postfix
        await private_bot.edit_message_caption(chat_id, message_id, caption=text_edit, caption_entities=entities,
                                               reply_markup=reply_markup)
    else:
        text_edit = call.message.text
        if old_postfix:
            text_edit = text_edit.replace(old_postfix, new_postfix)
        else:
            text_edit += new_postfix
        await private_bot.edit_message_text(text_edit, chat_id, message_id, entities=entities,
                                            reply_markup=reply_markup)


async def generate_link(call: CallbackQuery):
    secret_key = secrets.token_urlsafe(16)
    await db.insert_data('table_sub_links', secret_key=secret_key, role=call.data, status='active')
    link = config.sub_url_private_bot + secret_key
    text, reply_markup = await text_generate_link(link)
    await call.message.edit_text(text, reply_markup=reply_markup, parse_mode='HTML')
    await call.answer()


async def delete_user(call: CallbackQuery):
    text, reply_markup = await text_delete_users()
    await call.message.edit_text(text, reply_markup=reply_markup)
    await call.answer()


async def back_to_menu(call: CallbackQuery):
    text, reply_markup = await text_menu()
    await call.message.edit_text(text, reply_markup=reply_markup)
    await call.answer()


async def get_role_for_delete_user(call: CallbackQuery):
    role = 'operator' if call.data == 'delete_operators' else 'superadmin'
    users = await db.get_users_by_role(role)
    reply_markup = await get_users_button(users)
    text = f"Используя кнопки ниже, выберите пользователя, которого хотите отключить от бота."
    await call.message.edit_text(text, reply_markup=reply_markup)
    await call.answer()


async def paginate(call: CallbackQuery, page: int):
    role = 'operator' if call.data == 'delete_operators' else 'superadmin'
    users = await db.get_users_by_role(role)
    keyboard = await get_users_button(users, page)
    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()


async def user_deletion_confirmation(call: CallbackQuery, telegram_id):
    fullname, role = await db.get_user_data('admins', telegram_id, ['fullname', 'role'])
    back = 'delete_operators' if role == 'operator' else 'delete_superadmins'
    reply_markup = await user_deletion_confirmation_buttons(telegram_id, back)
    text = f"Вы действительно хотите отключить <a href='tg://user?id={telegram_id}'>{fullname}</a> от бота?"
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await call.answer()


async def accept_delete_user(call: CallbackQuery, telegram_id):
    await db.update_user_data('admins', telegram_id, status='decline', action=None)
    await db.update_status_secure_link(telegram_id, status='decline')
    await private_bot.send_message(telegram_id, 'Администратор отключил вас от бота!')
    text, reply_markup = await text_menu()
    await call.message.edit_text(text, reply_markup=reply_markup)
    await call.answer('Пользователь отключен!')

