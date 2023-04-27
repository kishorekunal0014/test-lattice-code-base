import pickle

from requests_oauthlib import OAuth1

from app.managers.redis_manager import redis_manager

class UserManager:
    # USERS_TOKENS = []
    # USERS_PO_LIST = []
    def __init__(self, user_id) -> None:
        self.user_id = user_id
        self.user_oauth1 = self.get_oauth1_token()
        self.processed_po = self.get_processed_po_list()
    
    def get_oauth1_token(self):
        '''
        Retrieve user's OAUTH1 tokens.
        '''
        user_token = pickle.loads(redis_manager.redis.get("user_data"))[0]["tokens"]["oauth1"]
        return OAuth1(
                        user_token['client_id'],
                        client_secret=user_token['client_secret'],
                        resource_owner_key=user_token['resource_owner_key'],
                        resource_owner_secret=user_token['resource_owner_secret'],
                        signature_method=user_token['signature_method'],
                        realm=user_token['realm'],
                        signature_type=user_token['signature_type'],
                    )

    def get_processed_po_list(self):
        '''
        Returns list of PO which are processed/being processed.
        '''
        try:
            return pickle.loads(redis_manager.redis.get("po_list"))[self.user_id]
        except:
            return []
        
    async def update_po_list(self):
        '''
        Updates the PO list in redis.
        '''
        new_po_list = pickle.loads(redis_manager.redis.get("po_list"))
        new_po_list[self.user_id] = self.processed_po
        redis_manager.redis.set("po_list", pickle.dumps(new_po_list))

    async def clean_up(self):
        '''
        This function clears the data from user variables.
        '''
        self.user_id = None
        self.user_oauth1 = None
        self.processed_po = None
        