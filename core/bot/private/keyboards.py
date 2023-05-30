from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.callback_data import CallbackData

from core.database.operations import DataBase

db = DataBase()


APPEAL_ANSWER = CallbackData('appeal_answer', 'appeal_id')
APPEAL_WORK = CallbackData('appeal_work', 'appeal_id')
APPEAL_DONE = CallbackData('appeal_done', 'appeal_id')
APPEAL_BAN = CallbackData('appeal_ban', 'appeal_id')
ACCEPT_BAN = CallbackData('accept_ban', 'appeal_id')
DECLINE_BAN = CallbackData('decline_ban', 'appeal_id')
APPEAL_REJECT = CallbackData('appeal_reject', 'appeal_id')


USERS = CallbackData('delete_user', 'telegram_id')
PAGINATE = CallbackData('paginate', 'page')
ACCEPT_CLOSE_USER = CallbackData('accept_close_user', 'telegram_id')

BUTTONS_PER_PAGE = 5


async def get_rejects_buttons(appeal_id: int):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(reject.name, callback_data=f"{reject.key}:{appeal_id}")
               for reject in await db.get_reject()]

    inline_bt_back = InlineKeyboardButton('Назад', callback_data=DECLINE_BAN.new(appeal_id))
    inline_kb.add(*buttons)

    inline_kb.add(inline_bt_back)
    return inline_kb


async def get_appeal_to_work_button(appeal_id: int):
    inline_get_to_work = InlineKeyboardButton('Взять в работу', callback_data=APPEAL_WORK.new(appeal_id))
    inline_ban = InlineKeyboardButton('Заблокировать', callback_data=APPEAL_BAN.new(appeal_id))
    inline_reject_bt = InlineKeyboardButton('Отклонить', callback_data=APPEAL_REJECT.new(appeal_id))
    return InlineKeyboardMarkup(row_width=2).add(inline_get_to_work, inline_ban, inline_reject_bt)


async def get_appeal_to_done_button(appeal_id: int):
    inline_done_bt = InlineKeyboardButton('Готово', callback_data=APPEAL_DONE.new(appeal_id))
    inline_answer_bt = InlineKeyboardButton('Отправить комментарий', callback_data=APPEAL_ANSWER.new(appeal_id))
    inline_ban = InlineKeyboardButton('Заблокировать', callback_data=APPEAL_BAN.new(appeal_id))
    return InlineKeyboardMarkup(row_width=2).add(inline_done_bt, inline_ban, inline_answer_bt)


async def accept_ban_user_buttons(appeal_id: int):
    inline_accept_bt = InlineKeyboardButton('Подтвердить', callback_data=ACCEPT_BAN.new(appeal_id))
    inline_decline_bt = InlineKeyboardButton('Назад', callback_data=DECLINE_BAN.new(appeal_id))
    return InlineKeyboardMarkup(row_width=2).add(inline_accept_bt, inline_decline_bt)


async def get_temp_buttons_for_operator(appeal_id: int):
    appeal = await db.get_appeal_data(appeal_id, ['status'])
    if appeal.status == 'sent':
        return await get_appeal_to_work_button(appeal_id)
    else:
        return await get_appeal_to_done_button(appeal_id)


async def generate_secure_links():
    inline_admin_bt = InlineKeyboardButton('Супер-админ', callback_data='superadmin')
    inline_operator_bt = InlineKeyboardButton('Оператор', callback_data='operator')
    inline_delete_user = InlineKeyboardButton('Отключить пользователя', callback_data='delete_user')
    return InlineKeyboardMarkup(row_width=2).add(inline_operator_bt, inline_admin_bt, inline_delete_user)


async def delete_users_buttons():
    inline_delete_admin_bt = InlineKeyboardButton('Супер-админы', callback_data='delete_superadmins')
    inline_delete_operator_bt = InlineKeyboardButton('Операторы', callback_data='delete_operators')
    inline_back_to_menu_bt = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    return InlineKeyboardMarkup(row_width=2).add(inline_delete_operator_bt, inline_delete_admin_bt,
                                                 inline_back_to_menu_bt)


async def get_users_button(users: list, page: int = 1):
    buttons = [InlineKeyboardButton(user.fullname, callback_data=USERS.new(user.telegram_id))
               for user in users]
    # смещаемся на одну страницу вперед или назад в зависимости от принятой страницы
    start = (page - 1) * BUTTONS_PER_PAGE
    end = start + BUTTONS_PER_PAGE

    # создаем новый список кнопок для вывода
    buttons_to_show = buttons[start:end]

    # создаем новый InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(*buttons_to_show)

    # Добавляем кнопку следующей страницы
    if len(buttons) > end:
        keyboard.insert(InlineKeyboardButton("Следующие", callback_data=PAGINATE.new(page=page + 1)))
    # Добавляем кнопку предыдущей страницы
    if page > 1:
        keyboard.insert(InlineKeyboardButton("Предыдущие", callback_data=PAGINATE.new(page=page - 1)))

    keyboard.insert(InlineKeyboardButton('Назад', callback_data='back_to_choose_role_delete'))

    return keyboard


async def user_deletion_confirmation_buttons(telegram_id: int, back: str):
    inline_accept_bt = InlineKeyboardButton('Подтвердить', callback_data=ACCEPT_CLOSE_USER.new(telegram_id))
    inline_decline_bt = InlineKeyboardButton('Отмена', callback_data=back)
    return InlineKeyboardMarkup(row_width=2).add(inline_accept_bt, inline_decline_bt)
