from .insert_data import InsertData
from .exists_data import ExistsData
from .select_data import SelectData
from .update_data import UpdateData


class DataBase(ExistsData, InsertData, SelectData, UpdateData):
    def __init__(self):
        super().__init__()
