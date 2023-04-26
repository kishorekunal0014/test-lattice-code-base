import redis
import pickle

redis = redis.StrictRedis()
# b = {
#     "vidatt" : [51,54,55,62,63,64,65,66,67,68,69,70,71,75,192,196,197,198,199]
# }
# redis.set("po_list", pickle.dumps(b))
a = pickle.loads(redis.get("po_details"))
print(a)
