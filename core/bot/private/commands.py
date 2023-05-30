from aiogram.types import Message

from core.bot.private.instructions import text_welcome, text_welcome_admin, text_menu
from core.database.operations import DataBase
from .. import private_bot

db = DataBase()


async def get_start(message: Message):
    role, action, edit_message_id = await db.get_user_data('admins', message.chat.id, ['role', 'action', 'message_id'])
    if not action:
        if role == 'superadmin':
            text_answer, reply_markup = await text_welcome_admin(message)
        else:
            text_answer, reply_markup = await text_welcome(message)
        result = await private_bot.send_message(message.chat.id, text_answer, parse_mode='HTML', reply_markup=reply_markup)
        await db.update_user_data('admins', message.chat.id, action='wait', message_id=result.message_id)
    else:
        if role == 'superadmin':
            text, reply_markup = await text_menu()
            if edit_message_id:
                try:
                    await private_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
                except: pass
            result = await private_bot.send_message(message.chat.id, text, reply_markup=reply_markup)
            await db.update_user_data('admins', message.chat.id, message_id=result.message_id)
        else:
            await private_bot.send_message(message.chat.id, 'Ожидайте сообщения!', parse_mode='HTML')


async def get_help(message: Message):
    role, edit_message_id = await db.get_user_data('admins', message.chat.id, ['role', 'message_id'])
    if role == 'superadmin':
        text, reply_markup = await text_menu()
        if edit_message_id:
            await private_bot.edit_message_reply_markup(message.chat.id, edit_message_id)
        text_help = f"Бот предназначен для администрирования операторов в боте отработок.\n\n" \
                    f"<u>В боте присутствуют следующие кнопки:</u>\n" \
                    f"<b>Оператор</b> - генерирует ссылку для регистрации оператора в боте\n" \
                    f"<b>Супер-админ</b> - генерирует ссылку для регистрации супер-админа, который сможет " \
                    f"назначать операторов\n" \
                    f"<b>Отключить пользователя</b> - отключение назначенных ранее операторов и администраторов"
        await private_bot.send_message(message.chat.id, text_help, parse_mode='HTML')
        result = await private_bot.send_message(message.chat.id, text, reply_markup=reply_markup)
        await db.update_user_data('admins', message.chat.id, message_id=result.message_id)
    else:
        text_help = f"Бот предназначен для отработки обращений связанных со " \
                    f"случаями жестоко обращения с животными\n\n" \
                    f"Под каждым обращением будет две кнопки:\n" \
                    f"<b>Взять в работу</b> - ее нажатие будет говорить о том, что данное обращение взято в работу " \
                    f"(информация об этом отправляется автору обращения).\n" \
                    f"<b>Заблокировать</b> - блокировка пользователя, в случае необходимости.\n\n" \
                    f"После того, как обращение взято в работу, кнопка поменяется на <b>Готово</b>. " \
                    f"Ее нажатие будет означать, что данное обращение отработано и информация об " \
                    f"этом отправится пользователю."
        await private_bot.send_message(message.chat.id, text_help, parse_mode='HTML')
