from supabase import create_client, Client
from config import RAW_DEST_URL, SUPABASE_API_KEY, CLEAN_ORDERS_URL


#helper functions that return a client for each of the tables in the database
def raw_orders_client():
    supabase: Client = create_client(RAW_DEST_URL, SUPABASE_API_KEY)
    return Client

def clean_orders_client():
    supabase: Client = create_client(CLEAN_ORDERS_URL, SUPABASE_API_KEY)
    return Client

