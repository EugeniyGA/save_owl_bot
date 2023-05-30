from core.functions.config import Config
import sys, asyncio

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = Config()


class BaseDatabase(object):
    def __init__(self, maxsize: int = 5):
        self.name = config.db_name
        self.password = config.db_pass
        self.ip = config.db_ip
        self.port = config.db_port
        self.db = config.db

        self.db_uri = f'postgresql://{self.name}:{self.password}@{self.ip}:{self.port}/{self.db}'
        self.maxsize = maxsize
