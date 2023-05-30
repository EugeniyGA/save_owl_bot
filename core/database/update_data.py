from .base import BaseDatabase
from aiopg.sa import create_engine
from sqlalchemy import text
from typing import Union


# 3
class UpdateData(BaseDatabase):

    async def update_user_data(self, table: str, telegram_id: Union[int, str], **kwargs):
        query = text(f"""UPDATE {table} SET {', '.join([f"{k}=:{k}" for k in kwargs.keys()])}
                         WHERE telegram_id=:telegram_id""")
        kwargs['telegram_id'] = telegram_id
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                await con.execute(query, kwargs)

    async def update_media_status(self, telegram_id: Union[int, str], new_status: str, check_status: str):
        query = text(f"""UPDATE table_media SET status=:new_status 
                         WHERE telegram_id=:telegram_id AND status=:check_status""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                await con.execute(query, {'new_status': new_status, 'telegram_id': telegram_id,
                                          'check_status': check_status})

    async def update_media_appeal_id(self, telegram_id: Union[int, str], appeal_id):
        query = text(f"""UPDATE table_media SET appeal_id=:appeal_id, status=:new_status
                         WHERE telegram_id=:telegram_id AND status=:check_status""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                await con.execute(query, {'appeal_id': appeal_id, 'new_status': 'done',
                                          'telegram_id': telegram_id, 'check_status': 'queue'})

    async def update_appeal_status(self, appeal_id: int, new_status: str):
        query = text(f"""UPDATE table_appeal SET status=:new_status WHERE appeal_id=:appeal_id RETURNING telegram_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                result = await con.execute(query, {'new_status': new_status, 'appeal_id': appeal_id})
                info = await result.fetchone()
                return info[0]

    async def update_animal_field(self, animal_key: str, **kwargs):
        query = text(f"""UPDATE table_animal SET {', '.join([f"{k}=:{k}" for k in kwargs.keys()])} 
                         WHERE key=:key""")
        # print(query)
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                kwargs['key'] = animal_key
                # print(kwargs)
                await con.execute(query, kwargs)

    async def update_appeal_data(self, appeal_id: int, return_telegram_id: bool = False, **kwargs):
        if return_telegram_id:
            query = text(f"""UPDATE table_appeal SET {', '.join([f"{k}=:{k}" for k in kwargs.keys()])} 
                             WHERE appeal_id=:appeal_id RETURNING telegram_id""")
        else:
            query = text(f"""UPDATE table_appeal SET {', '.join([f"{k}=:{k}" for k in kwargs.keys()])} 
                             WHERE appeal_id=:appeal_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                kwargs['appeal_id'] = appeal_id
                result = await con.execute(query, kwargs)
                if return_telegram_id:
                    info = await result.fetchone()
                    return info[0]

    async def update_secure_data(self, telegram_id, secret_key: str):
        query = text(f"""UPDATE table_sub_links SET telegram_id=:telegram_id WHERE key=:key""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                await con.execute(query, {'telegram_id': telegram_id, 'key': secret_key})

    async def update_status_secure_link(self, telegram_id: int, status: str):
        query = text(f"""UPDATE table_sub_links SET status=:status WHERE telegram_id=:telegram_id""")
        async with create_engine(self.db_uri, maxsize=self.maxsize) as engine:
            async with engine.acquire() as con:
                await con.execute(query, {'status': status, 'telegram_id': telegram_id})
