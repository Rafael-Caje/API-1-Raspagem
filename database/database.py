import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_job_data(data):
    response = supabase_client.table('vagas').insert(data).execute()
    return response
