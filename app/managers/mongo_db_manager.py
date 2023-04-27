from pymongo import MongoClient
MONGO_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URL)

'''
using AUTH
client = MongoClient('example.com',
                     username='user',
                     password='password',
                     authSource='the_database',
                     authMechanism='SCRAM-SHA-256')
'''

db = client['LATTICE']

# test_dict  = {
#     "first_name" : "Vidatt",
#     "last_name" : "Lattice",
#     "organization" : "Vidatt",
#     "tokens" : {
#         "oauth1" : {
#             "client_id" : "5f8cbd0592f7bae7965c05c7ea804548dafdd4dd25065b0f8a71dfedabf637de",
#             "client_secret" : "aac9a3aa923f6e5aab1b41d259ba5318b9edc3d7fb4096f687ffdb89bb237cfe",
#             "token_key" : "bfc150b2497cb9ff610fdbecce560a008111b67cb80fee9cc17dba4c7937eebd",
#             "token_secret" : "1c5dac787dd405d3d3304c32806e0431723f97f8094ea45a715a8649cc1f4dad"
#         }
#     }
# }

test_dict = {
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
post_id = user_details_db.insert_one(test_dict)

# user_details_db = db.get_collection("USER_DETAILS")
# a = user_details_db.find({"organization" : "Vidatt_test123"})
# # for a1 in a:
# #     print(a1)
# print(list(a))
