import json

import uvicorn
from fastapi import FastAPI

from app.PROCESS_INSTRUCTIONS import process_file
from app.doc_db_init import init_populate_doc_db
from app.config import INSTRUCTIONS_PATH
from app.logger import get_logger

log = get_logger()

app = FastAPI()   

@app.on_event("startup")
async def startup_event():
    # inital update to document db
    # comment the function if data is already added to DB
    # await init_populate_doc_db()
    log.info("Starting instructions processor.")
    await process_file(INSTRUCTIONS_PATH)

@app.post("/update_equinix_status")
def update_eq_status(order_id : str, status : int):
    '''
    This API is used as an alternative to the equinix API.
    It takes order id and status as input and updates the status respecitvely.
    '''
    log.info(f"Received update equinix order status.")
    if status == 1:
        status_text = "Order received"
        log.info(f"Updated order status to {status_text}.")
    elif status == 2:
        status_text = "Order in progress"
        log.info(f"Updated order status to {status_text}.")
    elif status == 3:
        status_text = "Order completed"
        log.info(f"Updated order status to {status_text}.")
    else:
        log.debug(f"Invalid status passed {status}")
        return "Invalid status"
    
    with open('db/equinix/order_status.json', 'r') as order_status_list:
        order_status_data = json.load(order_status_list)
    
    if order_id in order_status_data.keys():
        order_status_data[order_id] = status_text
        with open('db/equinix/order_status.json', 'w') as order_status_list:
            json.dump(order_status_data, order_status_list) 
            log.info("Successfully updated order status.")

    else:
        log.debug(f"Invalid order ID passed{order_id}.")
        return "Invalid order ID"


