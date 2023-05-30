from aiogram import executor

from core.bot import instruction_bot, instruction_dp
from core.functions.config import Config
from core.functions.generate_report import generate_report

config = Config()


async def main():
    # формируем текст для telegram бота, отчет в excel и путь к нему
    text_statistic, path_report = await generate_report()

    with open(path_report, 'rb') as doc:
        await instruction_bot.send_document(config.ano_chat_id, document=doc, caption=text_statistic, parse_mode='HTML')


if __name__ == '__main__':
    executor.start(instruction_dp, main())
