from aiogram.types import Message

from core.bot.private.keyboards import generate_secure_links, delete_users_buttons


async def text_welcome(message: Message):
    text = f"<b>{message.chat.first_name}</b>, добро пожаловать в бота отработок!\n\n" \
           f"Данный бот предназначен для отработок входящих обращений от жителей города. " \
           f"Под каждым обращением будет кнопка для того, чтобы взять его в работу.\n\n" \
           f"Используя команду /help можно получить инструкцию по использованию."
    return text, None


async def text_welcome_admin(message: Message):
    reply_markup = await generate_secure_links()
    text = f"<b>{message.chat.first_name}</b>, добро пожаловать в админ-бота!\n\n" \
           f"Данный бот предназначен для назначения/отстранения операторов в бота отработок.\n" \
           f"Для этого воспользуйтесь кнопками ниже, которые сгенерируют ссылку для подписки на бота. " \
           f"Полученную ссылку необходимо передать назначенному оператору.\n\n" \
           f"Используя команду /help можно получить инструкцию по использованию."
    return text, reply_markup


async def text_generate_link(link: str):
    reply_markup = await generate_secure_links()
    text = f'Передайте ссылку для подписки: {link}\n\n' \
           f'Чтобы сгенерировать новую ссылку или удалить пользователя из бота, воспользуйтесь кнопками ниже'
    return text, reply_markup


async def text_menu():
    reply_markup = await generate_secure_links()
    text = f"Чтобы сгенерировать новую ссылку или удалить пользователя из бота, воспользуйтесь кнопками ниже"
    return text, reply_markup


async def text_delete_users():
    reply_markup = await delete_users_buttons()
    text = f"Выберите роль пользователя, которого хотите отключить."
    return text, reply_markup

