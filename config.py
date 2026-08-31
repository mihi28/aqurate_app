import os
from dotenv import load_dotenv

load_dotenv()

#url and api key for the raw data endpoint
RAW_SOURCE_URL = os.getenv("RAW_SOURCE_URL")
RAW_SOURCE_API = os.getenv("RAW_SOURCE_API")

EXCHANGE_RATES_URL = os.getenv("EXCHANGE_RATES_URL") #source of the exchange rates

#api url and key for the personal database
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")

 
if not (RAW_SOURCE_URL or SUPABASE_URL or EXCHANGE_RATES_URL):
    raise RuntimeError("Missing URL in .env file")