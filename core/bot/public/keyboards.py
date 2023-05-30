from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.callback_data import CallbackData

from core.database.operations import DataBase

db = DataBase()
PAGINATE = CallbackData('paginate', 'page')
APPEALS = CallbackData('appeals', 'id')
BUTTONS_PER_PAGE = 5


async def get_appeals_buttons(appeal_ids: list, page: int = 1):
    buttons = [InlineKeyboardButton(f"Обращение №{appeal_id}", callback_data=APPEALS.new(appeal_id))
               for appeal_id in appeal_ids]
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

    keyboard.insert(InlineKeyboardButton('Продолжить обращение', callback_data='continue'))

    return keyboard


async def input_animals_buttons() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup(row_width=3)

    buttons = [InlineKeyboardButton(animal.animal_emoji, callback_data=animal.animal_key)
               for animal in await db.get_animals()]

    # back_to_input_address
    inline_bt_back = InlineKeyboardButton('Назад', callback_data='back_input_address')
    inline_kb.add(*buttons)

    inline_kb.add(inline_bt_back)

    return inline_kb


async def input_media_files_button():
    inline_bt = InlineKeyboardButton('Нет фото', callback_data='not_media')
    inline_back_bt = InlineKeyboardButton('Назад', callback_data='back_input_count_animals')
    return InlineKeyboardMarkup(row_width=2).add(inline_bt, inline_back_bt)


async def new_appeal_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Передать геопозицию',
                                                                            request_location=True))
    buttons = [KeyboardButton(text_button) for text_button in ['Новое обращение', 'Статус', 'Помощь']]
    return keyboard.add(*buttons)


async def send_button():
    inline_send_bt = InlineKeyboardButton('Отправить', callback_data='send_data')
    inline_back_bt = InlineKeyboardButton('Назад', callback_data='back_input_media')
    return InlineKeyboardMarkup(row_width=2).add(inline_send_bt, inline_back_bt)


async def menu_buttons():
    inline_kb = InlineKeyboardMarkup(row_width=2)
    inline_contact_bt = InlineKeyboardButton('Контакты', callback_data='input_contact')

    inline_kb.add(inline_contact_bt)

    inline_update_button = InlineKeyboardButton('Отправить', callback_data='update_data')
    inline_kb.add(inline_update_button)

    return inline_kb


async def next_button(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Продолжить', callback_data=callback_data))


async def back_button(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Назад', callback_data=callback_data))
