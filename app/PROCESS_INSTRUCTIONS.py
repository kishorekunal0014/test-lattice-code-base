import yaml
import sys

from  app import actions
from app.managers.transaction_manager import transaction_manager
from app.managers.instructions_manager import instructions_manager
from app.managers.redis_manager import redis_manager
from app.logger import get_logger

log = get_logger()

async def process_file(file_path):
    '''
    This parses through the instructions file and executes the instructions.
    '''
    log.info("Reading instructions file.")
    with open(file_path, "r") as ins:
        instructions_data = yaml.safe_load(ins)

    for key in instructions_data.keys():
        # store north and south data
        if key == "INIT":
            log.info("Found instruction INIT")
            log.info("Loading north and south details")
            transaction_manager.north_details = instructions_data[key]["north_details"]
            transaction_manager.south_details = instructions_data[key]["south_details"]
            log.info("Successfully loaded north and south details")

        # initialise redis
        elif key == "REDIS":
            log.info("Found instruction REDIS")
            log.info("Setting up redis")
            await redis_manager.init_redis(instructions_data[key])

        # polling north for PO
        elif key == "POLL_PurchaseOrder":
            log.info("Found instruction POLL_PurchaseOrder")
            instructions_manager.PO_POLL_DATA = instructions_data[key]
            await actions.Poll_PurchaseOrder()

        # polling south for order status
        elif key == "POLL_OrderStatus":
            log.info("Found instruction POLL_OrderStatus")
            instructions_manager.ORDER_STATUS_POLL_DATA = instructions_data[key]
            await actions.Poll_OrderStatus()

        # undefined instruction
        else:
            log.error(f"Undefined instruction '{key}'. Please re-check the instruction file.")
            sys.exit("Terminating programs due to error in instruction file.")
