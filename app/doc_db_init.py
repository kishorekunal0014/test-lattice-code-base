from pymongo import MongoClient
from app.constants import DOC_DB_NAME, USER_COLLECTION_NAME, SOUTH_COLLECTION_NAME, NORTH_COLLECTION_NAME
# MONGO_URL = "mongodb://localhost:27017/"
MONGO_URL = "mongodb://documentdb:document123@docdb-2023-04-24-09-52-33.cluster-c4f5vk3tgphx.ap-south-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

async def init_populate_doc_db():
    doc_db_client = MongoClient(MONGO_URL)
    dbnames = doc_db_client.list_database_names()
    if 'LATTICE' in dbnames:
        return
    db = doc_db_client['LATTICE']
    dict_data1  = {
                    "first_name" : "Vidatt",
                    "last_name" : "Lattice",
                    "organization" : "Vidatt",
                    "tokens" : {
                        "oauth1" : {
                            "client_id" : "5f8cbd0592f7bae7965c05c7ea804548dafdd4dd25065b0f8a71dfedabf637de",
                            "client_secret" : "aac9a3aa923f6e5aab1b41d259ba5318b9edc3d7fb4096f687ffdb89bb237cfe",
                            "resource_owner_key" : "bfc150b2497cb9ff610fdbecce560a008111b67cb80fee9cc17dba4c7937eebd",
                            "resource_owner_secret" : "1c5dac787dd405d3d3304c32806e0431723f97f8094ea45a715a8649cc1f4dad",
                            "signature_method" : 'HMAC-SHA256',
                            "realm" : '8147918',
                            "signature_type" : 'auth_header'
                        }
                    }
                }
    dict_data2 = {
                    "north_id" : "ONS",
                    "api_details" : {
                        "polling" : {
                            "purchase_order" : {
                                "get_details" : {
                                    "method" : "GET",
                                    "route" : "/services/rest/record/v1/purchaseorder"
                                }
                            }
                        }
                    }
                }
    
    user_details_db = db.get_collection("NORTH_DETAILS")
    user_details_db.insert_one(dict_data2)
    user_details_db = db.get_collection("USER_DETAILS")
    user_details_db.insert_one(dict_data1)
    

    doc_db_client.close()