import json

from app.config import TRANSACTION_ID_PATH

class TransactionManager:
    def __init__(self) -> None:
        self.north_details = {}
        self.south_details = {}
        self.transaction_id = self.get_last_transaction_id()

    def get_last_transaction_id(self):
        '''
        This function gets the last transaction id from config file.
        '''
        with open(TRANSACTION_ID_PATH, 'r') as t_id:
            return 'T' + str(json.load(t_id)["id"])
        
    async def new_transaction_id(self):
        '''
        This function creates new transaction id for new PO.
        '''
        with open(TRANSACTION_ID_PATH, 'r') as t_id:
            id = int(json.load(t_id)["id"])
        id += 1
        id_data = {"id" : id}
        with open(TRANSACTION_ID_PATH, 'w') as t_id:
                json.dump(id_data, t_id)
        self.transaction_id = "T" + str(id)


transaction_manager = TransactionManager()
