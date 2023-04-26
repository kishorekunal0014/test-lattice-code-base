from pymongo import MongoClient
from app.constants import DOC_DB_NAME, USER_COLLECTION_NAME, SOUTH_COLLECTION_NAME, NORTH_COLLECTION_NAME
# MONGO_URL = "mongodb://localhost:27017/"
from app.logger import get_logger
log = get_logger()
MONGO_URL = "mongodb://documentdb:document123@docdb-2023-04-24-09-52-33.cluster-c4f5vk3tgphx.ap-south-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
class DocumentDB_Manager:

    def __init__(self) -> None:
        self.doc_db_client = None

    async def init_connection(self):
        '''
        This function initiates connection with document db.
        '''
        try:
            self.doc_db_client = MongoClient(MONGO_URL)
            log.info("Connected to db")
        except Exception as e:
            log.error(f"Failed to connect to DB. {e}")
            
    async def close_connection(self):
        '''
        This function terminates document db connection.
        '''
        self.doc_db_client.close()

    async def get_user_details(self, organisation):
        '''
        This function retrieves the user details.
        '''
        log.info("retreiving user info from db")
        await self.init_connection()
        db = self.doc_db_client[DOC_DB_NAME]
        user_details_coll = db.get_collection(USER_COLLECTION_NAME)
        user_data = list(user_details_coll.find({"organization" : organisation}))
        await self.close_connection()
        log.info("successfully fetched user data from db")
        return user_data
    
    async def get_north_API_details(self, north_id):
        '''
        This function retrieves the north API details.
        '''
        await self.init_connection()
        db = self.doc_db_client[DOC_DB_NAME]
        north_details_coll = db.get_collection(NORTH_COLLECTION_NAME)
        north_data = north_details_coll.find_one({"north_id" : north_id})
        await self.close_connection()
        return north_data
    
    async def get_south_API_details(self, south_id):
        '''
        This function retrieves the south API details.
        '''
        await self.init_connection()
        db = self.doc_db_client[DOC_DB_NAME]
        south_details_coll = db.get_collection(SOUTH_COLLECTION_NAME)
        south_data = south_details_coll.find_one({"south_id" : south_id})
        await self.close_connection()
        return south_data

doc_db_manager = DocumentDB_Manager()