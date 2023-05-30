from .base import BaseDatabase
from aiopg.sa import create_engine
from sqlalchemy import text
from typing import Union
from core.database.models import AppealModel


# 8
class SelectData(BaseDatabase):

    async def get_user_data(self, table: str, telegram_id: Union[int, str], fields: list):
        query = text(f"""SELECT {', '.join(fields)} FROM {table} WHERE telegram_id=:telegram_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'telegram_id': telegram_id})
                info = await result.fetchone()
                return info.as_tuple()

    async def get_media_files(self, telegram_id):
        query = text(f"""SELECT path_file, type_file FROM table_media WHERE telegram_id=:telegram_id AND status=:status""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'telegram_id': telegram_id, 'status': 'queue'})
                info = await result.fetchall()
                return info

    async def get_count_media_files(self, appeal_id):
        query = text(f"""SELECT COUNT(path_file) FROM table_media WHERE appeal_id=:appeal_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await (await con.execute(query, {'appeal_id': appeal_id})).fetchone()
                result = result[0] if result else result
                return result

    # Используется для кнопок с выбором вида животного
    async def check_animals(self, animal_key: str):
        query = text(f"""SELECT name FROM table_animal WHERE key=:key""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'key': animal_key})
                info = await result.fetchone()
                if info:
                    return info.as_tuple()[0]
                else:
                    return info

    # Используется для кнопок с выбором причины отклонения обращения
    async def check_reject(self, reject_key: str):
        query = text(f"""SELECT text FROM table_reject WHERE key=:key""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'key': reject_key})
                info = await result.fetchone()
                if info:
                    return info.as_tuple()[0]
                else:
                    return info

    async def get_animals(self):
        query = text(f"""SELECT key, emoji FROM table_animal""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query)
                info = await result.fetchall()
                return info

    async def get_reject(self):
        query = text(f"""SELECT key, name FROM table_reject""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query)
                info = await result.fetchall()
                return info

    async def get_chats_id(self):
        # Функция может измениться, добавится аргумент для округа, таким образом telegram_id будут записаться по округу
        query = text(f"""SELECT telegram_id FROM admins WHERE role=:role AND status=:status""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'role': 'operator', 'status': 'active'})
                info = [chat_id[0] for chat_id in await result.fetchall()]
                return info

    async def get_appeal_data(self, appeal_id: Union[int, str], fields: list) -> AppealModel:
        query = text(f"""SELECT {', '.join(fields)} FROM table_appeal WHERE appeal_id=:appeal_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'appeal_id': appeal_id})
                info = await result.fetchone()
                return AppealModel(**info)

    async def get_appeal_ids(self, telegram_id: Union[int, str]):
        query = text(f"""SELECT appeal_id FROM table_appeal WHERE telegram_id=:telegram_id ORDER BY appeal_id DESC""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'telegram_id': telegram_id})
                info = [res[0] for res in await result.fetchall()]
                return info

    async def get_secure_key(self, district: str):
        query = text(f"""SELECT key FROM table_sub_links WHERE district=:district""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'district': district})
                info = await result.fetchone()
                if info:
                    return info[0]
                return info

    async def get_chats_for_edit_appeal_message(self, appeal_id: int):
        query = text(f"""SELECT message_id, telegram_id FROM sent_appeals WHERE appeal_id=:appeal_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'appeal_id': appeal_id})
                info = await result.fetchall()
                return info

    async def get_users_by_role(self, role: str):
        query = text(f"""SELECT fullname, telegram_id FROM admins WHERE role=:role AND status=:status""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'role': role, 'status': 'active'})
                info = await result.fetchall()
                return info

    async def get_supperadmin_ids(self):
        query = text(f"""SELECT telegram_id FROM admins WHERE role='superadmin' AND status='active'""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query)
                info = await result.fetchall()
                return info

    async def get_statistic_public_users(self, date_start, date_end):
        query = text(f"""SELECT * FROM users 
                         WHERE date_sub BETWEEN :date_start AND :date_end 
                         ORDER BY user_id""")
        data = {
            'date_start': date_start,
            'date_end': date_end
        }
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, data)
                info = await result.fetchall()
                return info

    async def get_number_public_users(self, date_end):
        query = text(f"""SELECT COUNT(*) FROM users WHERE date_sub<=:date_end""")
        data = {
            'date_end': date_end
        }
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, data)
                info = await result.fetchone()
                return info.as_tuple()[0]

    async def get_statistic_appeals(self, date_start, date_end):
        query = text(f"""SELECT a.*, bc.chat_id as ban  
                         FROM (SELECT * FROM table_appeal WHERE date_create BETWEEN :date_start AND :date_end) as a
                         LEFT OUTER JOIN ban_chats bc ON a.telegram_id=bc.chat_id ORDER BY a.appeal_id""")
        data = {
            'date_start': date_start,
            'date_end': date_end
        }
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, data)
                info = await result.fetchall()
                return info
