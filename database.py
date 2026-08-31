from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_API_KEY


#helper function that returns the supabase client

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_API_KEY)