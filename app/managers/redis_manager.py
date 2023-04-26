import pickle

# from rediscluster import RedisCluster
import redis
from app.managers.document_db_manager import doc_db_manager
from app.logger import get_logger

log = get_logger()

class RedisManager:
    def __init__(self) -> None:
        # create connection to redis instance
        self.host = "clustercfg.elastic-cache-1.0owaz2.aps1.cache.amazonaws.com"
        self.port = "6379"
        startup_nodes = [{"host": self.host, "port": self.port}]
        # self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True,skip_full_coverage_check=True, ssl=True)
        self.redis = redis.Redis()
        if self.redis.ping():
            log.info("Initialized redis connection")
        else:
            log.error("Failed to initialize redis")
        

    async def init_redis(self, redis_data):
        '''
        This function fetches the necessary data from the master DB and populates into redis.
        '''
        self.organisation = redis_data["ORGANISATION"]
        self.north_list = redis_data["NORTH"]
        self.south_list = redis_data["SOUTH"]

        # update redis data
        log.info(f"Fetching user details for {self.organisation} organisation")
        await self.update_user_details()
        log.info(f"Fetching API details for {self.north_list}")
        await self.update_north_api_details()
        log.info(f"Fetching API details for {self.south_list}")
        await self.update_south_api_details()
        # initialise PO list
        if self.redis.get("po_list") is None:
            self.redis.set("po_list", pickle.dumps({}))

        #initialise PO details dict
        if self.redis.get("po_details") is None:
            self.redis.set("po_details", pickle.dumps({}))

    async def update_user_details(self):
        '''
        This function fetches user details from master DB and loads to redis.
        '''
        user_data = await doc_db_manager.get_user_details(self.organisation)
        self.redis.set('user_data', pickle.dumps(user_data))
        log.info("Loaded user details to redis")
        
    async def update_north_api_details(self):
        '''
        This function fetches API details of north side from master DB and loads to redis.
        '''
        north_data = {}
        for north in self.north_list:
            north_api_data = await doc_db_manager.get_north_API_details(north)
            north_data[north] = north_api_data
        self.redis.set('north_data', pickle.dumps(north_data))
        log.info("Loaded north API details to redis")

    async def update_south_api_details(self):
        '''
        This function fetches API details of south side from master DB and loads to redis.
        '''
        south_data = {}
        for south in self.south_list:
            south_api_data = await doc_db_manager.get_south_API_details(south)
            south_data[south] = south_api_data
        self.redis.set('south_data', pickle.dumps(south_data))
        log.info("Loaded south API details to redis")

    async def save_po_list(self, po_list):
        '''
        This function saves the PO list to redis.
        '''
        self.redis.set("po_list", pickle.dumps(po_list))

redis_manager = RedisManager()