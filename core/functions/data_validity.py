import codecs
import re

from aiogram.types import Message

from core.bot import public_bot
from core.functions.logger import create_logger

logger = create_logger('check_bad_wirds.log', 'check_bad_words')

BAD_WORDS = []


PHONE_PATTERN = r"^(\+7|8)?\s?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})$"
EMAIL_PATTERN = r"^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$"
TELEGRAM_PATTERN = r"^@[a-zA-Z0-9_]{5,32}$"

FILES = [
    'bad_dict.txt',
    'dict_alibaba_badwords.uu',
    'dict_porn.uu',
    'sex_fix_list.txt',
    'bad_rus.txt'
]

for path in FILES:
    with codecs.open(f'data/{path}', 'r', 'utf_8_sig') as file:
        words = file.readlines()
        for word in words:
            BAD_WORDS.append(word.replace('\n', '').replace('\r', '').rstrip(' '))


# Декоратор, применяющийся к функциям используемых в message_handler
# Не используется по причине некорректной работы
def check_bad_words(func):
    async def wrapper(message: Message, edit_message_id):
        logger.info(f'{message.chat.id} - {message.chat.username} - {message.chat.full_name} - {message.text}')
        bad_word_pattern = r'\b(?:{})\b'.format('|'.join(re.escape(w) for w in BAD_WORDS))
        if re.search(bad_word_pattern, message.text, flags=re.IGNORECASE):
            text_reply = 'Нецензурная лексика запрещена 🤬!!!'
            await public_bot.send_message(message.chat.id, text_reply)
        else:
            await func(message, edit_message_id)
    return wrapper


def check_valid_contact(func):
    async def wrapper(message, edit_message_id):
        check_valid = [re.match(EMAIL_PATTERN, message.text), re.match(TELEGRAM_PATTERN, message.text),
                       re.match(PHONE_PATTERN, message.text)]
        if any(check_valid):
            await func(message, edit_message_id)
        else:
            text_reply = 'Проверьте, правильно ли введен email, номер телефона или ' \
                         'telegram никнейм и попробуйте еще раз!'
            await public_bot.send_message(message.chat.id, text_reply)
    return wrapper


if __name__ == '__main__':
    print(len(BAD_WORDS))
