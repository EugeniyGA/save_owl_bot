from aiogram.types import Message

from core.bot import private_bot, public_bot
from core.database.operations import DataBase

db = DataBase()


async def get_answer(message: Message, appeal_id: int, text_appeal):
    chats = await db.get_chats_for_edit_appeal_message(appeal_id)
    superadmin_ids = await db.get_supperadmin_ids()

    new_postfix = f'Отработано. Обратная связь:\n\n{message.text}'

    for chat in chats:
        await edit_text(text_appeal, chat.telegram_id, chat.message_id,
                        f"\n\n{new_postfix}", "\n\nВзято в работу!")

    for superadmin_id in superadmin_ids:
        await private_bot.send_message(superadmin_id.telegram_id,
                                       f'Обращение {appeal_id} - отработано!\n\n'
                                       f'Комментарий: {message.text}\n\n'
                                       f"Оператор: <a href='tg://user?id={message.chat.id}'>"
                                       f"{message.chat.full_name}</a>", parse_mode='HTML')

    await db.insert_data('log_admin', appeal_id=appeal_id, telegram_id=message.chat.id,
                         status=f'Комментарий: {message.text}')

    await db.update_user_data('admins', message.chat.id, action='wait', text_answer=None, appeal_id=None)

    public_user_id = await db.update_appeal_data(appeal_id, return_telegram_id=True, answer=message.text, status='done')

    text_answer = f'Обращение №{appeal_id} отработано!\n\nКомментарий:\n{message.text}'
    await public_bot.send_message(public_user_id, text_answer)
    await private_bot.send_message(message.chat.id, 'Комментарий отправлен, обращение отработано!',
                                   reply_to_message_id=message.message_id)


async def edit_text(text_appeal, chat_id, message_id, new_postfix, old_postfix=None, reply_markup=None):
    if old_postfix:
        text_appeal = text_appeal.replace(old_postfix, new_postfix)
    else:
        text_appeal += new_postfix
    await private_bot.edit_message_text(text_appeal, chat_id, message_id, reply_markup=reply_markup)
