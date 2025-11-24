import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    return pc.Index(index_name)

