import os
from dotenv import load_dotenv

load_dotenv()

#url and api key for the raw data endpoint
RAW_SOURCE_URL = os.getenv("RAW_SOURCE_URL")
RAW_SOURCE_API = os.getenv("RAW_SOURCE_API")

#api key for the personal database
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

#urls for the destination of the ingested data, cleaned data, exchange rates data, etc
RAW_DEST_URL = os.getenv("RAW_DEST_URL")
CLEAN_ORDERS_URL = os.getenv("CLEAN_ORDERS_URL")
EXCHANGE_RATES_URL = os.getenv("EXCHANGE_RATES_URL") #source of the exchange rates
EXCHANGE_DEST_URL = os.getenv("EXCHANGE_DEST_URL") #destination in the personal database
 
if not RAW_SOURCE_URL or CLEAN_ORDERS_URL or RAW_DEST_URL or EXCHANGE_RATES_URL:
    raise RuntimeError("Missing URL in .env file")