import os

from dotenv import load_dotenv, find_dotenv

dotenv_file = find_dotenv('configs/.env')
load_dotenv(dotenv_file)


class Config:
    def __init__(self):
        self.bot_token = os.getenv('telegram.token')
        self.bot_private_token = os.getenv('telegram.token_private_bot')
        self.bot_admin_token = os.getenv('telegram.token_admin_bot')
        self.bot_instruction = os.getenv('telegram.token_instruction_bot')

        self.bot_moderator_1_token = os.getenv('telegram.token_moderator_1')
        self.bot_moderator_2_token = os.getenv('telegram.token_moderator_2')
        self.bot_moderator_3_token = os.getenv('telegram.token_moderator_3')
        self.bot_moderator_4_token = os.getenv('telegram.token_moderator_4')

        self.channel_id = int(os.getenv('telegram.channel'))
        self.errors_id = int(os.getenv('telegram.errors_id'))
        self.ano_chat_id = int(os.getenv('telegram.ano_chat_id'))

        self.sub_url_private_bot = os.getenv('telegram.sub_url_private_bot')

        self.db_path = os.getenv('db.path')
        self.db_name = os.getenv('db.name')
        self.db_pass = os.getenv('db.password')
        self.db_ip = os.getenv('db.ip')
        self.db_port = os.getenv('db.port')
        self.db = os.getenv('db.db')
