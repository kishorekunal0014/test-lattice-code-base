import requests
import random
import json 
import pickle

from fastapi_utils.tasks import repeat_every
from requests_oauthlib import OAuth1Session, OAuth1

from app.managers.instructions_manager import instructions_manager
from app.managers.users_manager import UserManager
from app.managers.transaction_manager import transaction_manager
from app.managers.redis_manager import redis_manager
from app.config import POLL_DURATION
from app.logger import get_logger

log = get_logger()

async def create_cross_connect(item_details):
    '''
    This function send request to the south side to order cross connect
    '''
    log.info("Sending order to equinix to create cross connect")

    # create fictitious Order ID as equinix responds NULL 
    with open('db/equinix/order_status.json', 'r') as orders_list:
            order_ids = json.load(orders_list)
    while(True):
        o_id = "CC_ORDER_ID_" + str(random.randint(1000,9999))
        if o_id in order_ids.keys():
            continue
        else:
            with open('db/equinix/order_status.json', 'w') as orders_list:
                order_ids[o_id] = ""
                json.dump(order_ids, orders_list)
                log.info("Generated order ID")
                return o_id

async def ons_mark_complete(po_id, auth):
    '''
    This function updates the PO status in ONS
    '''
    BASE_URL = transaction_manager.north_details["base_url"]
    url = f"{BASE_URL}/services/rest/record/v1/purchaseOrder/{po_id}/!transform/itemReceipt"
    return requests.post(url, auth=auth)


async def update_po_status(po_id, status, user_manager):
    data = {
                "memo" : status[:-2]
            }
    BASE_URL = transaction_manager.north_details["base_url"]
    po_url = f"{BASE_URL}/services/rest/record/v1/purchaseorder/{po_id}"
    response = requests.patch(po_url, json=data, auth=user_manager.user_oauth1)
    if response.status_code == 200:
        log.info("Successfully updated status in ONS")
    else:
        log.error(f"Failed to update status in ONS. Status code: {response.status_code}")

async def process_po_item(item_details):
    if item_details['item']['refName'] == "CrossConnect":
        log.info("Found item cross connect")
        order_id = await create_cross_connect(item_details)
        return f"Order sent to Equinix. ID: {order_id}", order_id
    else:
        return "Item '" + item_details['item']['refName'] + "' Not registered with Lattice, please check with admin.", -1

async def get_ons_details(po_url, user_auth):
    '''
    This function takes ONS endpoint as input,
    makes API call to ONS and returns the response.
    '''
    log.info(f"[{transaction_manager.transaction_id}] Making API call to ONS to get details")
    response = requests.get(po_url,auth=user_auth)
    if response.status_code == 200:
        log.info(f"[{transaction_manager.transaction_id}] API call to ONS successful")
        return response.json()
    else:
        log.error(f"[{transaction_manager.transaction_id}] API call to ONS unsuccessful.")
        log.error(f"Response code: {response.status_code}, message: {response.content}")

async def add_po_to_db(user_id, po_id, item_status):
    '''
    Add PO details to redis.
    '''
    po_details = pickle.loads(redis_manager.redis.get("po_details"))
    # if user data not in redis
    if user_id not in po_details.keys():
         po_details[user_id] = {}
         po_details[user_id][po_id] = {
                                        "items" : item_status,
                                        "transaction_id" : transaction_manager.transaction_id
                                    }
    else:
        po_details[user_id][po_id] = {
                                        "items" : item_status,
                                        "transaction_id" : transaction_manager.transaction_id
                                    }
    redis_manager.redis.set("po_details", pickle.dumps(po_details))
    
async def execute_api(api_data):
     '''
     This function takes API data as input, 
     generates the end point and body parameters and
     makes the API call.
     Return value is response from the API call.
     '''
     api_method = api_data["method"]
     url = api_data["BASE_URL"] + api_data["route"]
     if api_method == "GET":
        response = requests.get(url,auth=api_data["AUTH"])
        return response.json()
        

@repeat_every(seconds=POLL_DURATION)
async def Poll_PurchaseOrder():
    '''
    This function polls the purchase orders from north.
    '''
    log.info("Polling  PO")
    user_manager = UserManager("vidatt")
    north_id = transaction_manager.north_details["north_id"]

    # get api details from redis
    api_data = pickle.loads(redis_manager.redis.get("north_data"))[north_id]['api_details']['polling']['purchase_order']['get_details']
    api_data["BASE_URL"] = transaction_manager.north_details["base_url"]
    api_data["AUTH"] = user_manager.user_oauth1

    # get PO list
    po_list = await execute_api(api_data)
    log.info("Successfully fetched PO list.")
    new_po  = False

    # check if number of PO is more than 0
    if po_list['totalResults'] == 0:
        log.info("No purchase orders found in the list")
        return
    else:
        log.info("Iterating PO list")
        # process PO
        for po in po_list['items']:
            # if it is a new PO
            if int(po['id']) not in user_manager.processed_po:
                new_po = True
                log.info("Found new PO")
                await transaction_manager.new_transaction_id()
                log.info(f"Created new transaction {transaction_manager.transaction_id}")
                log.info(f"[{transaction_manager.transaction_id}] Get PO details")
                po_details = await get_ons_details(po['links'][0]['href'], user_manager.user_oauth1)
                log.info(f"[{transaction_manager.transaction_id}] Get items list")
                items_list = await get_ons_details(po_details['item']['links'][0]['href'], user_manager.user_oauth1)
                po_status = "Order Status: \n"
                item_count = 0
                items_status = {}
                # process items
                log.info(f"[{transaction_manager.transaction_id}] Iterating items list")
                for item in items_list['items']:
                    item_count += 1
                    log.info(f"[{transaction_manager.transaction_id}] Get item details")
                    item_details = await get_ons_details(item['links'][0]['href'], user_manager.user_oauth1)
                    log.info(f"[{transaction_manager.transaction_id}] Processing item")
                    item_status, south_order_id = await process_po_item(item_details)
                    po_status += f"Item {item_count}: " + item_status + ", \n"
                    items_status[item_count] = {
                                                    "status" : item_status,
                                                    "south_order_id" : south_order_id
                                                }
                
                (user_manager.processed_po).append(int(po['id']))
                log.info(f"[{transaction_manager.transaction_id}] Update PO status to ONS")
                await update_po_status(int(po['id']), po_status, user_manager)
                log.info(f"[{transaction_manager.transaction_id}] Add PO details to redis")
                await add_po_to_db(user_manager.user_id, int(po['id']), items_status)

        if new_po == False:
             log.info("No new PO found")
        else:
            # update PO list in redis          
            log.info("Updating user's PO list in redis")
            await user_manager.update_po_list()

    # clear user variables
    await user_manager.clean_up()
    del user_manager
    log.info("Cleared user's details.")
    log.info("Polling PO completed.")
    

@repeat_every(seconds=POLL_DURATION)
async def Poll_OrderStatus():
    '''
    This function polls the order status from south
    '''
    log.info("Polling order status")
    user_manager = UserManager('vidatt')
    log.info("Get PO details of user")
    # with open('db/po_details.json', 'r') as po_details_list:
    #         po_details_lst = json.load(po_details_list)
    #         po_details = po_details_lst[user_manager.user_id]

    with open('db/equinix/order_status.json', 'r') as order_status_list:
            order_status_data = json.load(order_status_list)
    po_details_lst = pickle.loads(redis_manager.redis.get("po_details"))
    po_details = po_details_lst[user_manager.user_id]
    log.info("Checking status of items in equinix data.")
    for po_id, po_data in po_details.items():
        status_updated = False
        po_status = "Order Status: \n"
        transaction_id = po_data["transaction_id"]
        item_count = 0
        item_completed = 0
        for item_id, item_data in po_data['items'].items():
            south_order_id = item_data['south_order_id']
            if south_order_id == -1:
                continue
            item_count += 1
            if order_status_data[south_order_id] == "Order completed":
                item_completed += 1
            if item_data['status'] == order_status_data[south_order_id] or order_status_data[south_order_id] == "":
                po_status += f"Item {item_id}: " + item_data['status'] + ', '
            else:
                po_status += f"Item {item_id}: Status in Equinix({south_order_id}) - " + order_status_data[south_order_id] + ','
                status_updated = True
                po_details_lst[user_manager.user_id][po_id]['items'][item_id]['status'] = order_status_data[south_order_id]

        # if all item orders are completed, update PO status in ONS
        if item_count == item_completed:
            log.info(f"All items for transaction {transaction_id} are completed from south")
            ons_status_code = await ons_mark_complete(po_id, user_manager.user_oauth1)
            if ons_status_code == 200:
                log.info("Updated PO status in ONS")
            else:
                log.error("Failed to update PO status in ONS. Response")

        # check if status was updated
        if status_updated:
             await update_po_status(po_id, po_status, user_manager)
             log.info(f"Updating new status in ONS for transaction {transaction_id}")
        else:
             log.info(f"No updates for transaction {transaction_id}")
    # with open('db/po_details.json', 'w') as po_detail_list:
    #             json.dump(po_details_lst, po_detail_list)    
    redis_manager.redis.set("po_details", pickle.dumps(po_details_lst))
    log.info("Polling order status completed.")

