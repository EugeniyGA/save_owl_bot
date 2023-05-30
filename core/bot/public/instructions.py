from aiogram.types import Message, InlineKeyboardButton
from core.functions.geocoder import geocoder
from core.bot.public.keyboards import (
    input_animals_buttons,
    send_button,
    input_media_files_button,
    # back_to_menu_button,
    # next_input_animals_button,
    next_button,
    menu_buttons,
    get_appeals_buttons,
    # back_to_animals_button,
    # back_to_count_animals_button,
    back_button
)
from core.database.operations import DataBase
import re

db = DataBase()


async def text_welcome(message: Message) -> str:

    text = f"<b>{message.chat.first_name}</b>, добро пожаловать в бота!\n\n" \
           f"Здесь можно оставить заявку на случаи жестокого обращения с животными в городе. " \
           f"Инспекторы Департамента природопользования и охраны окружающей среды " \
           f"Москвы оперативно отработают ситуацию и дадут обратную связь.\n\n" \
           f"Укажите точный адрес ниже или оставьте геолокацию:"

    return text


async def text_help() -> str:

    text = f"Здесь можно оставить заявку на случаи жестокого обращения с животными в городе.\n\n" \
           f"Для этого необходимо указать адрес или оставить геолокацию, " \
           f"где был замечен данный случай, общее количество замеченных животных и " \
           f"по возможности приложить фото/видео материалы.\n\n" \
           f"Как устроен процесс: получив обращение, дежурный инспектор проверяет информацию " \
           f"через доступные средства видеонаблюдения, вызывает наряд полиции и ближайшего к " \
           f"адресу инспектора. Если на животное нет документов, оно будет изъято у нарушителя и " \
           f"отправлено в Центр реабилитации диких животных, а нарушитель задержан.\n\n" \
           f"Работы по спасению незаконно эксплуатируемых животных ведутся постоянно, " \
           f"действует горячая линия: <b>+7 (495) 777-77-77.</b>\n" \
           f"Чаще всего фотографы обижают сов. В прошлом году спасли 37 этих птиц. А вот свежий " \
           f"<a href='https://ria.ru/20230208/sova-1850651469.html'>пример</a>.\n\n" \
           f"Этот бот позволит выявлять случаи нарушения ещё быстрее.\n\n" \
           f"Для того, чтобы получить обратную связь можно указать свои контакты.\n\n" \
           f"<b><u>В боте есть несколько команд:</u></b>\n" \
           f"/help - помощь\n" \
           f"/status - статус оставленных обращений\n" \
           f"/new - новое обращение"

    return text


async def text_status(telegram_id, appeal_id=None):
    status = {'sent': 'Отправлено', None: 'Отправлено', 'work': 'В работе', 'done': 'Отработано', 'reject': 'Отклонено'}
    if appeal_id:
        appeal = await db.get_appeal_data(appeal_id, ['appeal_id', 'address', 'count_animal', 'animal', 'status', 'answer'])
        address = await geocoder(appeal.address)
        text = f"<b><u>Обращение №{appeal.appeal_id}</u></b>\n\n" \
               f"Указанные данные:\n" \
               f"Адрес: <b>{address}</b>\n" \
               f"Вид животного: <b>{appeal.animal}</b>\n" \
               f"Количество животных: <b>{appeal.count_animal}</b>"

        if appeal.contact:
            text += f'\nКонтакты для обратной связи: <b>{appeal.contact}</b>'
        text += f"\n\nСтатус: <b>{status.get(appeal.status)}</b>"
        if appeal.answer:
            text += f'\nКомментарий: {appeal.answer}'

        return text
    else:
        appeal_ids = await db.get_appeal_ids(telegram_id)
        if appeal_ids:
            appeal = await db.get_appeal_data(appeal_ids[0], ['appeal_id', 'address', 'count_animal', 'animal', 'status', 'answer'])
            address = await geocoder(appeal.address)
            reply_markup = await get_appeals_buttons(appeal_ids)
            text = f"<b><u>Обращение №{appeal.appeal_id}</u></b>\n\n" \
                   f"Указанные данные:\n" \
                   f"Адрес: <b>{address}</b>\n" \
                   f"Вид животного: <b>{appeal.animal}</b>\n" \
                   f"Количество животных: <b>{appeal.count_animal}</b>"

            if appeal.contact:
                text += f'\nКонтакты для обратной связи: <b>{appeal.contact}</b>'
            text += f"\n\nСтатус: <b>{status.get(appeal.status)}</b>"
            if appeal.answer:
                text += f'\nКомментарий: {appeal.answer}'
            return text, reply_markup
        else:
            text = 'Вы еще не оставляли обращений.'
            return text, None


async def text_input_address(telegram_id):
    address, = await db.get_user_data('users', telegram_id, ['address'])
    address = await geocoder(address)
    reply_markup = await next_button('next_input_animals')
    if address:
        text = f"Указанный ранее адрес: <b>{address}</b>\n\n" \
               f"Укажите в поле для ввода точный адрес или оставьте геолокацию." \
               f"Чтобы не вносить изменения, нажмите <b><u><i>Продолжить</i></u></b>.\n"
        return text, reply_markup
    else:
        text = f"Укажите в поле для ввода точный адрес или оставьте геолокацию:"
        return text, None


async def text_input_animals(telegram_id):
    animal, = await db.get_user_data('users', telegram_id, ['animal'])
    reply_markup = await input_animals_buttons()
    if animal:
        text = f"Выбранный вами вариант: <b>{animal}</b>\n\n" \
               f"Для того, чтобы указать другого животного, воспользуйтесь кнопками ниже. " \
               f"Если необходимого варианта нет или их несколько, то <u>воспользуйтесь полем для ввода</u>.\n\n" \
               f"🦉 – Совообразные\n" \
               f"🦅 – Хищные птицы\n" \
               f"🐍 – Пресмыкающиеся\n" \
               f"🐒 – Приматы\n" \
               f"🦁 – Крупные хищники\n\n" \
               f"Чтобы не вносить изменения, нажмите <b><u><i>Продолжить</i></u></b>.\n" \
               f"Чтобы вернуться к шагу ввода адреса, нажмите <b><u><i>Назад</i></u></b>"
        reply_markup.add(InlineKeyboardButton('Продолжить', callback_data='next_count_animals'))
        return text, reply_markup
    else:
        text = f"Для того, чтобы указать животного, воспользуйтесь кнопками ниже. " \
               f"Если необходимого варианта нет или их несколько, то воспользуйтесь полем для ввода.\n\n" \
               f"🦉 – Совообразные\n" \
               f"🦅 – Хищные птицы\n" \
               f"🐍 – Пресмыкающиеся\n" \
               f"🐒 – Приматы\n" \
               f"🦁 – Крупные хищники\n\n" \
               f"Чтобы вернуться к шагу ввода адреса, нажмите <b><u><i>Назад</i></u></b>"
        return text, reply_markup


async def text_input_count_animals(telegram_id):
    count_animal, = await db.get_user_data('users', telegram_id, ['count_animal'])
    reply_markup = await back_button('back_input_animals')
    if count_animal:
        text = f"Указанное вами количество: <b>{count_animal}</b>\n\n" \
               f"Укажите в поле для ввода общее количество животных, которое было замечено.\n\n" \
               f"Чтобы не вносить изменения, нажмите <b><u><i>Продолжить</i></u></b>.\n" \
               f"Чтобы вернуться к шагу ввода адреса, нажмите <b><u><i>Назад</i></u></b>"
        reply_markup.add(InlineKeyboardButton('Продолжить', callback_data='next_input_media'))
        return text, reply_markup
    else:
        text = f"Укажите в поле для ввода общее количество животных, которое было замечено.\n\n" \
               f"Чтобы вернуться к шагу ввода адреса, нажмите <b><u><i>Назад</i></u></b>"
        return text, reply_markup


async def text_input_media(telegram_id):
    media, = await db.get_user_data('users', telegram_id, ['media'])
    reply_markup = await input_media_files_button()
    if media:
        print(await db.get_media_files(telegram_id))
        count_media = len((await db.get_media_files(telegram_id))[:5])

        text = f"Загружено фото/видео материалов: <b>{count_media}</b>\n\n" \
               f"Вы можете удалить загруженные ранее файлы и загрузить новые, для этого " \
               f"воспользуйтесь кнопкой <b><u><i>Удалить загруженные файлы</i></u></b> или добавить " \
               f"к имеющимся новые, для этого просто отправьте файлы, но помните, что их общее количество " \
               f"не должно превышать 5-ти.\n\n" \
               f"Если не хотите вносить изменений, то нажмите <b><u><i>Назад</i></u></b> или " \
               f"<b><u><i>Продолжить</i></u></b>"

        reply_markup.add(InlineKeyboardButton('Продолжить', callback_data='next_send_menu'))
        reply_markup.add(InlineKeyboardButton('Удалить загруженные файлы', callback_data='delete_files'))
    else:
        text = "Загрузите фото/видео материалы, не более 5-ти.\n\n" \
               "Если вы уже ушли, или у вас нет фото/видео, воспользуйтесь кнопкой <b><u><i>Нет фото</i></u></b>. " \
               "Помните, что у обращений без фото приоритет реагирования значительно понижается.\n\n" \
               "Чтобы вернуться назад, воспользуйтесь кнопкой ниже."
    return text, reply_markup


async def text_menu(telegram_id, contact_input=None):
    address, animal, count_animal, media, contact, appeal_id = \
        await db.get_user_data('users', telegram_id, ['address', 'animal', 'count_animal',
                                                      'media', 'contact', 'appeal_id'])
    address = await geocoder(address)
    text = f"<b>Номер вашего обращения №{appeal_id}</b>\n\n" \
           f"Указанные вами данные ранее:\n" \
           f"Адрес: <b>{address}</b>\n" \
           f"Общее количество животных: <b>{count_animal}</b>"
    if media:
        count_media = await db.get_count_media_files(appeal_id)
        if count_media > 5:
            count_media = 5
        text += f'\nКоличество предоставленных фото/видео файлов: <b>{count_media}</b>'
    if animal:
        text += f'\nВид животного: <b>{animal}</b>'
    if contact_input:
        contact = contact_input
    if contact:
        text += f'\nКонтакты для обратной связи: <b>{contact}</b>'

    text += f"\n\nВы также можете внести дополнительную информацию по данному обращению, например, " \
            f"свои контактные данные, для того, чтобы мы " \
            f"могли связаться с вами и дать полную обратную связь. Для этого воспользуйтесь клавиатурой ниже.\n\n" \
            f"Если была внесена дополнительная информация, то нажмите кнопку <b><u><i>Отправить</i></u></b>\n\n" \
            f"Чтобы создать новое обращение, посмотреть статус оставленных заявок или просто получить " \
            f"помощь по использованию бота, воспользуйтесь клавиатурой ниже."

    reply_markup = await menu_buttons()
    return text, reply_markup


async def text_for_send_data(telegram_id, media_input=False):
    address, animal, count_animal, media = \
        await db.get_user_data('users', telegram_id, ['address', 'animal', 'count_animal', 'media'])
    address = await geocoder(address)
    if media_input:
        media = media_input
    text = '<b><u>Указанные данные:</u></b>\n\n' \
           f'Адрес: <b>{address}</b>\n' \
           f'Вид животного: <b>{animal}</b>\n' \
           f'Общее количество животных: <b>{count_animal}</b>'
    if media:
        count_media = len(await db.get_media_files(telegram_id))
        if count_media > 5:
            text += f"\nЗагружены не все файлы, поскольку превышен лимит в 5 файлов"
            count_media = 5
        text += f'\nКоличество предоставленных фото/видео файлов: <b>{count_media}</b>'

    text += f"\n\nДля того, чтобы внести изменения в веденные данные " \
            f"воспользуйтесь кнопкой <b><u><i>Назад</i></u></b>\n" \
            f"Если все корректно, то отправьте первичные данные кнопкой <b><u><i>Отправить</i></u></b>"

    reply_markup = await send_button()

    return text, reply_markup


async def text_input_contact(telegram_id):
    contact, = await db.get_user_data('users', telegram_id, ['contact'])
    if contact:
        text = f"Указанные контактные данные для обратной связи: <b>{contact}</b>\n\n" \
               f"Чтобы обновить данные воспользуйтесь строкой ввода.\n\n" \
               f"Если не хотите вносить изменения, то нажмите <b><u><i>Назад</i></u></b>"
    else:
        text = f"Укажите контактные данные для обратной связи (email или telegram).\n\n" \
               f"Если не хотите ничего указывать, нажмите <b><u><i>Назад</i></u></b>"
    reply_markup = await back_button('back_to_menu')
    return text, reply_markup
