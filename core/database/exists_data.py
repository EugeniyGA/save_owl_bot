from .base import BaseDatabase
from .insert_data import InsertData
from .update_data import UpdateData
from aiopg.sa import create_engine
from sqlalchemy import text
from typing import Union
from datetime import datetime


# 2
class ExistsData(InsertData, UpdateData, BaseDatabase):

    def __init__(self):
        super().__init__()

    # Подписан пользователь или нет (если нет, подписываем)
    def check_public_user(self, func):
        async def wrapper(message):
            # print('decorator', message)
            async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
                async with engine.acquire() as con:
                    query = text(f"""SELECT EXISTS (SELECT telegram_id FROM users WHERE telegram_id=:telegram_id)""")
                    result = await con.execute(query, {'telegram_id': message.chat.id})
                    info = await result.fetchone()
                    if info.as_tuple()[0]:
                        query = text(f"""SELECT EXISTS (SELECT chat_id FROM ban_chats WHERE chat_id=:chat_id)""")
                        result = await con.execute(query, {'chat_id': message.chat.id})
                        info = await result.fetchone()
                        if not info.as_tuple()[0]:
                            await func(message)
                    else:
                        query = text(f"""SELECT EXISTS (SELECT chat_id FROM ban_chats WHERE chat_id=:chat_id)""")
                        result = await con.execute(query, {'chat_id': message.chat.id})
                        info = await result.fetchone()
                        if not info.as_tuple()[0]:
                            date_sub = datetime.now()
                            await self.sub_user(message, 'users', date_sub=date_sub)
                            await func(message)
        return wrapper

    # Проверка на блокировку
    def check_ban_user(self, func):
        async def wrapper(call, callback_data=None):
            async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
                async with engine.acquire() as con:
                    query = text(f"""SELECT EXISTS (SELECT chat_id FROM ban_chats WHERE chat_id=:chat_id)""")
                    result = await con.execute(query, {'chat_id': call.message.chat.id})
                    info = await result.fetchone()
                    if not info.as_tuple()[0]:
                        await func(call, callback_data)
        return wrapper

    # Проверка, отключен ли оператор (супер-админ) или нет
    def check_disable_private_user(self, func):
        async def wrapper(call, callback_data=None):
            async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
                async with engine.acquire() as con:
                    query = text(f"""SELECT EXISTS (SELECT telegram_id FROM admins 
                                     WHERE telegram_id=:telegram_id AND status=:status)""")
                    result = await con.execute(query, {'telegram_id': call.message.chat.id, 'status': 'active'})
                    info = await result.fetchone()
                    if info.as_tuple()[0]:
                        await func(call, callback_data)
        return wrapper

    # Подписка оператора (супер-админа)
    def check_private_user(self, func):
        async def wrapper(message):
            async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
                async with engine.acquire() as con:
                    # query = text(f"""SELECT EXISTS (SELECT telegram_id FROM
                    #                                 private_users WHERE telegram_id=:telegram_id)""")
                    query = text(f"""SELECT status FROM admins WHERE telegram_id=:telegram_id""")
                    result = await con.execute(query, {'telegram_id': message.chat.id})
                    info = await result.fetchone()
                    status = info.as_tuple()[0] if info else None
                    # print(status)
                    if status and status != 'decline':
                        if status == 'active':
                            await func(message)
                    else:
                        if message.get_command(True) == 'start':
                            query = text(f"""SELECT role, telegram_id FROM table_sub_links WHERE key=:key AND status=:status""")
                            result = await con.execute(query, {'secret_key': message.get_args(), 'status': 'active'})
                            info = await result.fetchone()
                            # print(info)
                            if info:
                                role = info[0]
                                tg_id = info[1]
                                if not tg_id:
                                    if status:
                                        await self.update_user_data('admins', message.chat.id, status='active')
                                    else:
                                        await self.sub_user(message, table='admins', role=role, status='active')
                                    await self.update_secure_data(message.chat.id, message.get_args())
                                    await func(message)

        return wrapper

    # Статус медиа файлов
    async def check_status_media(self, telegram_id: Union[int, str], status: str):
        query = text(f"""SELECT EXISTS(SELECT path_file 
                         FROM table_media 
                         WHERE telegram_id=:telegram_id AND status=:status)""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'telegram_id': telegram_id, 'status': status})
                info = await result.fetchone()
                return info.as_tuple()[0]

