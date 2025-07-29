import requests
import os
import sys
from dotenv import load_dotenv

from config import Config
from api.deals import get_deals_data, get_deals_objects
from utils.db import save_to_database

sys.stdout.reconfigure(encoding='utf-8')
# Load environment variables from .env file
load_dotenv()

url = Config.API_URL

    
deals_url = Config.API_URL + Config.API_DEALS_ENDPOINT + Config.API_DEALS_PARAMS
estatus = get_deals_data(deals_url)
object_deals = []
count = 0
for deal in estatus:
    print(deal + " - " + str(count))
    count += 1
    object_deals.append(get_deals_objects(url, deal))
save_to_database(object_deals, Config.QUERY_INSERT_OBJECTS)



