from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

client = AsyncIOMotorClient(MONGO_DB_URL)
db = client.notes

def get_user_collection():
    return db.users

def get_note_collection():
    return db.notes

def get_shared_link_collection():
    return db.shared_links