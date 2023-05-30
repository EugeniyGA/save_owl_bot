from aiopg.sa import create_engine
from sqlalchemy import text
from aiogram.types import Message

from .base import BaseDatabase


# 1
class InsertData(BaseDatabase):

    async def insert_data(self, table: str, returning_info: str = None, **kwargs):
        placeholder = [f":{k}" for k in kwargs.keys()]
        query = f"""INSERT INTO {table} ({', '.join(kwargs.keys())}) VALUES ({', '.join(placeholder)})"""
        if returning_info:
            query += f" RETURNING {returning_info}"
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(text(query), kwargs)
                if returning_info:
                    info = await result.fetchone()
                    return info.as_tuple()[0]

    async def sub_user(self, message: Message, table: str, **kwargs):
        telegram_id = message.chat.id
        fullname = message.chat.full_name
        username = f"@{message.chat.username}"
        await self.insert_data(table, telegram_id=telegram_id, fullname=fullname,
                               username=username, **kwargs)

    # Инфа по отправленным обращениям операторам, id сообщения в tg
    # потребуется для изменения кнопок, текста в случае реагирования и тд.
    async def insert_sent_appeal_to_chats(self, data: list):
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                for row in data:
                    placeholder = [f":{k}" for k in row.keys()]
                    query = text(f"""INSERT INTO sent_appeals ({', '.join(row.keys())}) 
                                     VALUES ({', '.join(placeholder)})""")
                    await con.execute(query, row)
